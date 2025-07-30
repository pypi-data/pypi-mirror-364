import abc
from typing import Dict, Type, Optional


class BaltechSDKError(Exception):
    pass


class StatusCodeError(Exception, metaclass=abc.ABCMeta):
    StatusCodeMap: Dict[int, Type["StatusCodeError"]] = {}

    ErrorCode: Optional[int] = None
    URL: Optional[str] = None

    def __init_subclass__(cls) -> None:
        if cls.ErrorCode:
            already_registered_error = cls.StatusCodeMap.get(cls.ErrorCode)
            if already_registered_error:
                raise TypeError(f"multiple exceptions defined for same status code {hex(cls.ErrorCode)} ({cls} and {already_registered_error})")
            cls.StatusCodeMap[cls.ErrorCode] = cls

    @classmethod
    def create(cls, ec: int) -> "StatusCodeError":
        return cls.StatusCodeMap.get(ec, cls)()

    def __str__(self) -> str:
        return "\n".join(
            map(str,
                filter(
                    lambda i: i is not None,
                    [hex(self.ErrorCode) if self.ErrorCode else None, self.URL, self.__doc__]
                )
            )
        )


class CBrpLibError(StatusCodeError, metaclass=abc.ABCMeta):
    URL = "https://docs.baltech.de/api-docs/c/group__brp__lib.html"


class ComError(CBrpLibError, metaclass=abc.ABCMeta):
    pass


class ComUnsupported(ComError, metaclass=abc.ABCMeta):
    pass


class ComAccessDeniedError(ComError, metaclass=abc.ABCMeta):
    pass


class ComTimeoutError(ComError, metaclass=abc.ABCMeta):
    pass


class ComFrameFormatError(ComError, metaclass=abc.ABCMeta):
    pass


class ComUndefined(ComError, metaclass=abc.ABCMeta):
    pass


class LibError(CBrpLibError, metaclass=abc.ABCMeta):
    pass


class LibInvalidCallError(LibError, metaclass=abc.ABCMeta):
    pass


class LibNonRecoverableError(LibError, metaclass=abc.ABCMeta):
    pass


class LibOsError(LibError, metaclass=abc.ABCMeta):
    pass


class LibUndefinedError(LibError, metaclass=abc.ABCMeta):
    pass


class InternalError(LibNonRecoverableError):
    ErrorCode = 0x20000001


class CommandTimeoutError(ComTimeoutError):
    ErrorCode = 0x02000002


class FrameFormatError(ComFrameFormatError):
    ErrorCode = 0x04000003


class InvalidApiCallError(LibInvalidCallError):
    ErrorCode = 0x10000004


class OutOfMemoryError(LibNonRecoverableError):
    ErrorCode = 0x20000005


class BrpNotImplementedError(LibInvalidCallError):
    ErrorCode = 0x10000006


class BusyError(LibInvalidCallError):
    ErrorCode = 0x10000007


class ClosedError(LibInvalidCallError):
    ErrorCode = 0x10000008


class BufferOverflowError(ComFrameFormatError):
    ErrorCode = 0x04000009


class OpenIOError(LibOsError):
    ErrorCode = 0x4000000A


class WriteIOError(LibOsError):
    ErrorCode = 0x4000000B


class WaitIOError(LibOsError):
    ErrorCode = 0x4000000C


class ReadIOError(LibOsError):
    ErrorCode = 0x4000000D


class CloseIOError(LibOsError):
    ErrorCode = 0x4000000E


class PayloadFormatError(ComFrameFormatError):
    ErrorCode = 0x0400000F


class CryptoFormatError(ComFrameFormatError):
    ErrorCode = 0x04000010


class DeviceCertificateFormatError(ComFrameFormatError):
    ErrorCode = 0x04000011


class HostCertificateFormatError(ComFrameFormatError):
    ErrorCode = 0x040000012


class PkiOperationFailed(LibNonRecoverableError):
    ErrorCode = 0x20000013


class DeviceCertificateInvalidSignature(ComAccessDeniedError):
    ErrorCode = 0x01000014


class HostCertificateInvalidSignatureError(ComAccessDeniedError):
    ErrorCode = 0x01000015


class SecurityLevelNotSupportedError(ComAccessDeniedError):
    ErrorCode = 0x01000016


class SequenceCounterNotInSyncError(ComAccessDeniedError):
    ErrorCode = 0x01000017


class InvalidHMACError(ComAccessDeniedError):
    ErrorCode = 0x01000018


class CryptoRecvDevError(ComAccessDeniedError):
    ErrorCode = 0x01000019


class UnsupportedCommandError(ComUnsupported):
    ErrorCode = 0x00800020


class CommandDeniedError(ComAccessDeniedError):
    ErrorCode = 0x01000021


class UnexpectedFrameError(ComFrameFormatError):
    ErrorCode = 0x04000022


class BrpTimeoutError(ComTimeoutError):
    ErrorCode = 0x02000023


class CalledInvalidFrameError(LibInvalidCallError):
    ErrorCode = 0x10000024


class ExistingLayerError(LibInvalidCallError):
    ErrorCode = 0x10000025


class GenRandomDataError(LibOsError):
    ErrorCode = 0x40000026


class InvalidKeyError(ComAccessDeniedError):
    ErrorCode = 0x01000027
