import ctypes
import typing
import functools
from pathlib import Path
from typing import Any, Protocol, TypeVar, Callable, Union, Optional
from typing_extensions import Annotated, ParamSpec

from ..errors import StatusCodeError


buf = ctypes.POINTER(ctypes.c_char)
time = ctypes.c_ulong
errcode = ctypes.c_uint
layer_id = ctypes.c_int
socket = ctypes.c_int


class protocol_t(ctypes.Structure):
    pass


protocol = ctypes.POINTER(protocol_t)


class frame_t(ctypes.Structure):
    _fields_ = [
        ("ptr", buf),  # type is brp_buf, but in python
        # buf is defined in the scope of
        # this class definition...
        ("act_size", ctypes.c_size_t),
        ("total_size", ctypes.c_size_t),
    ]  # last read/write of frame failed


frame = ctypes.POINTER(frame_t)


class frame_reader_t(ctypes.Structure):
    _fields_ = [("frame", frame), ("ptr", buf), ("err", ctypes.c_bool)]


frame_reader = ctypes.POINTER(frame_reader_t)


class mempool_object_t(ctypes.Structure):
    pass


mempool = ctypes.POINTER(mempool_object_t)

mempool_object_t._fields_ = [
    ("prev", ctypes.POINTER(mempool_object_t)),
    ("next", ctypes.POINTER(mempool_object_t)),
    ("buf", ctypes.c_char_p),
]


cb_generic_t = ctypes.CFUNCTYPE(errcode, protocol)
cb_recv_any_frame_t = ctypes.CFUNCTYPE(errcode, protocol, time)
cb_fmt_spec_t = ctypes.CFUNCTYPE(ctypes.c_int, frame, ctypes.c_void_p)
cb_recv_frame_t = ctypes.CFUNCTYPE(
    errcode, protocol, time, cb_fmt_spec_t, ctypes.c_void_p
)
cb_get_id_t = ctypes.CFUNCTYPE(
    errcode, protocol, ctypes.POINTER(ctypes.c_char_p), frame
)

protocol_t._fields_ = [
    ("protocol_id", ctypes.c_int),
    ("layer_id", layer_id),
    ("base_protocol", protocol),
    ("cb_open", cb_generic_t),
    ("cb_close", cb_generic_t),
    ("cb_send_frame", cb_generic_t),
    ("cb_recv_any_frame", cb_recv_any_frame_t),
    ("cb_recv_frame", cb_recv_frame_t),
    ("cb_flush", cb_generic_t),
    ("cb_destroy", cb_generic_t),
    ("cb_get_id", cb_get_id_t),
    ("opened", ctypes.c_bool),
    ("send_frame", frame_t),
    ("recv_frame", frame_t),
    ("recv_delay", time),
    ("mempool", mempool_object_t),
]


R = TypeVar("R", covariant=True)
P = ParamSpec("P")
C = TypeVar("C", bound=type)


class CBrpLibFunction(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


CharP = Annotated[ctypes.Array[ctypes.c_char], ctypes.c_char_p]
CInt = Annotated[int, ctypes.c_int]
CSize = Annotated[int, ctypes.c_size_t]
CSizeP = Annotated[Any, ctypes.POINTER(ctypes.c_size_t)]
CChar = Annotated[bytes, ctypes.c_char]
CBool = Annotated[bool, ctypes.c_bool]
CBuf = Annotated[bytes, buf]
CLongLong = Annotated[int, ctypes.c_longlong]
CTime = Annotated[int, ctypes.c_ulong]
CProtocol = Annotated[Any, protocol]
CFrame = Annotated[Any, frame]
CFrameReader = Annotated[Any, frame_reader]
CSocket = Annotated[int, socket]

ErrorCode = Annotated[None, errcode]


def _to_ctype(t: Any) -> Any:
    if t is type(None):
        return None

    args = typing.get_args(t)
    if args:
        return args[1]

    return t


def with_error_handling(fn: Callable[P, int]) -> Callable[P, None]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        result = fn(*args, **kwargs)
        if result:
            raise StatusCodeError.create(result)

    return wrapper


class CBrpLib:
    brp_create: CBrpLibFunction[[], CProtocol]
    brp_set_io: CBrpLibFunction[[CProtocol, CProtocol], ErrorCode]
    brp_open: CBrpLibFunction[[CProtocol], ErrorCode]
    brp_close: CBrpLibFunction[[CProtocol], ErrorCode]
    brp_suppress_monitoring: CBrpLibFunction[[CProtocol], ErrorCode]
    brp_create_usb_hid: CBrpLibFunction[[CLongLong], CProtocol]
    brp_create_rs232: CBrpLibFunction[[CharP, CInt, CChar], CProtocol]
    brp_create_tcpip: CBrpLibFunction[[CharP], CProtocol]
    brp_create_tcpip_by_socket: CBrpLibFunction[[CSocket], CProtocol]
    brp_create_secure_channel: CBrpLibFunction[[CInt, CBuf, CInt], CProtocol]
    brp_create_pki: CBrpLibFunction[[CInt, CBuf, CSize, CBuf, CSize, CBuf, CSize, CTime], CProtocol]
    brp_append_host_certs: CBrpLibFunction[[CProtocol, CBuf, CSize], ErrorCode]
    brp_append_dev_ca_certs: CBrpLibFunction[[CProtocol, CBuf, CSize], ErrorCode]
    brp_set_crypto: CBrpLibFunction[[CProtocol, CProtocol], ErrorCode]
    brp_set_monitor: CBrpLibFunction[[CProtocol, CInt], ErrorCode]
    brp_pki_save_session: CBrpLibFunction[[CProtocol, CBuf, CSize, CSizeP], ErrorCode]
    brp_pki_restore_session: CBrpLibFunction[[CProtocol, CBuf, CSize], ErrorCode]
    brp_send_frame: CBrpLibFunction[[CProtocol], ErrorCode]
    brp_recv_any_frame: CBrpLibFunction[[CProtocol, CInt], ErrorCode]
    brp_frame_rest: CBrpLibFunction[[CFrameReader], CSize]
    brp_frame_init: CBrpLibFunction[[CFrame], None]
    brp_frame_write_start: CBrpLibFunction[[CFrame], None]
    brp_frame_write: CBrpLibFunction[[CFrame, CBuf, CSize], None]
    brp_frame_write_err: CBrpLibFunction[[CFrame], CBool]
    brp_frame_read_start: CBrpLibFunction[[CFrameReader, CFrame], None]
    brp_frame_read: CBrpLibFunction[[CFrameReader, CBuf, CSize], None]
    brp_frame_read_err: CBrpLibFunction[[CFrameReader], CBool]
    brp_frame_read_eof: CBrpLibFunction[[CFrameReader], CBool]
    brp_annotation_start: CBrpLibFunction[[CProtocol], None]
    brp_annotation_end: CBrpLibFunction[[CProtocol, CBool, CharP], None]

    def __init__(self) -> None:
        self.__dll_path: Optional[Path] = None

    @property
    def dll_path(self) -> Optional[Path]:
        return self.__dll_path

    @dll_path.setter
    def dll_path(self, dll_path: Path) -> None:
        self.__dll_path = dll_path.absolute()
        dll = ctypes.CDLL(str(self.__dll_path))
        for name, annotation in self.__annotations__.items():
            if typing.get_origin(annotation) == CBrpLibFunction:
                argtypes, restype = typing.get_args(annotation)
                fn = getattr(dll, name)
                fn.restype = _to_ctype(restype)
                fn.argtypes = tuple(map(_to_ctype, argtypes))
                if restype == ErrorCode:
                    fn = with_error_handling(fn)
                setattr(self, name, fn)

    def __getattr__(self, item: str) -> Any:
        if item in self.__annotations__:
            raise RuntimeError("Please initialize the brp_lib path calling `baltechsdk.set_brp_lib_path`.")
        return super().__getattribute__(item)


c_brp_lib = CBrpLib()
