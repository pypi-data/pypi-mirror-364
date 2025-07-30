import abc
import ctypes
import socket
from pathlib import Path
from zipfile import ZipFile
from configparser import ConfigParser
from typing import Any, Optional, TypeVar, Literal, Type, Union, Iterator
from contextlib import contextmanager

from .dll_wrapper import c_brp_lib, buf, frame_reader_t

T = TypeVar("T")


class CProtocolWrapper(metaclass=abc.ABCMeta):
    def __init__(self, c_protocol: Any) -> None:
        self.__c_protocol__ = c_protocol

    @property
    def closed(self) -> bool:
        return not self.__c_protocol__.contents.opened

    def open(self) -> None:
        c_brp_lib.brp_open(self.__c_protocol__)

    def close(self) -> None:
        c_brp_lib.brp_close(self.__c_protocol__)

    def __enter__(self) -> Any:
        if self.closed:
            self.open()
        return self

    def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: Any) -> None:
        if not self.closed:
            self.close()


class IoProtocol(CProtocolWrapper, metaclass=abc.ABCMeta):
    pass


class UsbHid(IoProtocol):
    def __init__(self, serialnumber: Optional[int] = None) -> None:
        self.serialnumber = serialnumber
        super().__init__(c_brp_lib.brp_create_usb_hid(serialnumber or 0))


class RS232(IoProtocol):
    def __init__(self, comport: str, baudrate: int = 115200, parity: Literal[b"O", b"E", b"N"] = b"N") -> None:
        self.comport = comport
        comport_cstr = ctypes.create_string_buffer(comport.encode("ascii"))
        super().__init__(c_brp_lib.brp_create_rs232(comport_cstr, baudrate, parity))


class Tcp(IoProtocol):
    def __init__(self, ipaddr: Optional[str] = None, *, sock: Optional[Union[socket.socket, int]] = None):
        if sock and ipaddr:
            raise TypeError("only one of ipaddr and sock parameter is allowed")

        self.socket = sock
        self.ipaddr = ipaddr

        if sock:
            socket_fileno = sock.fileno() if isinstance(sock, socket.socket) else sock
            cprotocol = c_brp_lib.brp_create_tcpip_by_socket(socket_fileno)
        elif ipaddr:
            ipaddr_cstr = ctypes.create_string_buffer(ipaddr.encode('ascii'))
            cprotocol = c_brp_lib.brp_create_tcpip(ipaddr_cstr)
        else:
            raise TypeError("parameter ipaddr or sock required")

        super().__init__(cprotocol)


class CryptoProtocol(CProtocolWrapper, metaclass=abc.ABCMeta):
    pass


class SecureChannel(CryptoProtocol):
    def __init__(self, *, security_level: int, key: bytes, security_mode: Literal["std", "plain", "stateless"] = "std") -> None:
        secmode = dict(std=0, plain=1, stateless=2).get(security_mode, 0)
        super().__init__(c_brp_lib.brp_create_secure_channel(security_level, key, secmode))


class PKI(CryptoProtocol):
    def __init__(self, certificates_path: Path, *, session_key: Optional[bytes] = None, session_timeout: Optional[int] = None) -> None:
        with ZipFile(str(certificates_path)) as pkizip:
            keypair = pkizip.read("keypair.key")

            config = ConfigParser()
            config.read_string(pkizip.read("settings.cfg").decode("utf-8"))
            security_level = int(config["settings"]["security_level"])

            cprotocol = c_brp_lib.brp_create_pki(
                security_level,
                b"", 0,
                b"", 0,
                keypair, len(keypair),
                session_timeout or 0,
                )

            for zipinfo in sorted(pkizip.filelist, key=lambda zi: zi.filename):
                if not zipinfo.is_dir():
                    if zipinfo.filename.startswith("host_chain"):
                        host_cert = pkizip.read(zipinfo)
                        c_brp_lib.brp_append_host_certs(cprotocol, host_cert, len(host_cert))
                    elif zipinfo.filename.startswith("reader_chain"):
                        reader_cert = pkizip.read(zipinfo)
                        c_brp_lib.brp_append_dev_ca_certs(cprotocol, reader_cert, len(reader_cert))

        if session_key:
            c_brp_lib.brp_pki_restore_session(cprotocol, session_key, len(session_key))

        super().__init__(cprotocol)
        self.certifcates_path = certificates_path
        self.session_timoeut = session_timeout

    @property
    def session_key(self) -> bytes:
        max_session_key_length = 1024
        session_key = buf(ctypes.create_string_buffer(max_session_key_length))  # type: ignore[call-overload]
        actual_len = ctypes.c_size_t()
        c_brp_lib.brp_pki_save_session(
            self.__c_protocol__, session_key, max_session_key_length, ctypes.pointer(actual_len)
        )
        return bytes(session_key[:int(actual_len)])


MonitorMode = Union[Literal["disabled", "enabled", "plaintext"], bool]


class AnnotationLogger:

    def __init__(self) -> None:
        self._message = ""
        self._fail = False

    def info(self, message: str) -> None:
        self._message += message

    def fail(self, message: str = "") -> None:
        self._fail = True
        self._message += message


class BrpStack(CProtocolWrapper):
    def __init__(
            self,
            io: IoProtocol,
            *,
            crypto: Optional[CryptoProtocol] = None,
            monitor:MonitorMode = "enabled",
            open: bool = False,
    ) -> None:
        super().__init__(c_brp_lib.brp_create())

        c_brp_lib.brp_set_io(self.__c_protocol__, io.__c_protocol__)

        if crypto:
            c_brp_lib.brp_set_crypto(self.__c_protocol__, crypto.__c_protocol__)

        if monitor not in (True, "enabled"):
            self.monitor = monitor

        if open:
            self.open()

    def execute(self, frame: bytes) -> bytes:
        send_frame = ctypes.pointer(self.__c_protocol__.contents.send_frame)

        c_brp_lib.brp_frame_write_start(send_frame)
        c_brp_lib.brp_frame_write(send_frame, frame, len(frame))
        c_brp_lib.brp_frame_write_err(send_frame)
        c_brp_lib.brp_send_frame(self.__c_protocol__)

        reader = frame_reader_t()
        c_brp_lib.brp_recv_any_frame(self.__c_protocol__, 0xFFFFFFFF)
        c_brp_lib.brp_frame_read_start(
            ctypes.pointer(reader), ctypes.pointer(self.__c_protocol__.contents.recv_frame)
        )
        rest = c_brp_lib.brp_frame_rest(ctypes.pointer(reader))

        result = ctypes.create_string_buffer(rest)
        c_brp_lib.brp_frame_read(ctypes.pointer(reader), buf(result), rest)  # type: ignore[call-overload]
        c_brp_lib.brp_frame_read_err(ctypes.pointer(reader))

        eof = c_brp_lib.brp_frame_read_eof(ctypes.pointer(reader))
        if not eof:
            raise RuntimeError("UnexpectedData")

        return result.raw

    def set_monitor(self, new_val: MonitorMode) -> None:
        map = {"disabled": 0, "enabled": 1, "plaintext": 2, False:0, True:1}
        c_brp_lib.brp_set_monitor(self.__c_protocol__, map[new_val])

    @contextmanager
    def annotate_log(self, comment:str="") -> Iterator[AnnotationLogger]:
        """
        Adds an annotations/comment to all brplogs that are executed within
        this context.

        Returns a contextmanager that allows to add further log-messages
        (log.info(...) or log.fail(...)). if at least one failure message is
        send the whole block is marked as failed.

        If an exception occurs the block will be marked as failed, too.
        If no log.fail() was called the exception text will be added to
        the log annotation.

        :param comment: A string that shall be added as annotation to the logs
        :return: a contextmanager of type AnnotationLogger()
        """
        annotation_logger = AnnotationLogger()
        annotation_logger.info(comment)
        try:
            c_brp_lib.brp_annotation_start(self.__c_protocol__)
            yield annotation_logger
        except Exception as exc:
            if not annotation_logger._fail:
                exc_text = f"{type(exc).__name__}: {str(exc)}"
                annotation_logger.fail(exc_text.splitlines()[0])
            raise
        finally:
            message_utf8 = annotation_logger._message.encode('utf8')
            message_cstr = ctypes.create_string_buffer(message_utf8)
            fail = annotation_logger._fail
            c_brp_lib.brp_annotation_end(
                self.__c_protocol__, not fail, message_cstr)

    monitor = property(fset=set_monitor)