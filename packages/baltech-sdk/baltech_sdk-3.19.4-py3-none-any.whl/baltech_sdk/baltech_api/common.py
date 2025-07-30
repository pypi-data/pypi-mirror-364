
import abc
from io import BytesIO
from typing import Generic, TypeVar, Dict, Optional, List, Iterable, Any, Union
from typing_extensions import Self

from baltech_sdk.errors import BaltechSDKError, StatusCodeError


class PayloadError(BaltechSDKError):
    pass


class PayloadTooLongError(PayloadError):
    def __init__(self, additional_data: bytes) -> None:
        super().__init__()
        self.additional_data = additional_data

    def __str__(self) -> str:
        return f'{len(self.additional_data)} bytes of unexpected data'


class PayloadTooShortError(PayloadError):
    def __init__(self, missing_bytes: int) -> None:
        super().__init__()
        self.missing_bytes = missing_bytes

    def __str__(self) -> str:
        return f'{self.missing_bytes} bytes are missing'


class InvalidPayloadError(PayloadError):
    pass


class BaltechApiError(StatusCodeError, metaclass=abc.ABCMeta):
    pass


def safe_read_int_from_buffer(buffer: BytesIO, field_len: int) -> int:
    raw_data = buffer.read(field_len)
    if len(raw_data) != field_len:
        raise PayloadTooShortError(field_len - len(raw_data))
    else:
        return int.from_bytes(raw_data, byteorder='big')


class FrameExecutor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, frame: bytes) -> bytes: ...


class ProtocolFrame(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def read_from(cls, buffer: BytesIO) -> Self: ...
    
    @abc.abstractmethod
    def __bytes__(self) -> bytes: ...

F = TypeVar("F", bound=ProtocolFrame)

class ProtocolBase(Generic[F], metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def parse_frames(cls, data: bytes) -> List[F]: ...
    
    def __init__(self, frames: Optional[Union[Iterable[F], bytes]] = None) -> None:
        if frames is None:
            self.frames: List[F] = []
        elif isinstance(frames, bytes):
            self.frames = self.parse_frames(frames)
        else:
            self.frames = list(frames)
    
    @abc.abstractmethod
    def frame_header(self, frame: F) -> bytes: ...
    
    def __bytes__(self) -> bytes:
        return b''.join(map(lambda f: self.frame_header(f) + bytes(f), self.frames))
    
    def __add__(self, other: Self) -> Self:
        return type(self)([*self.frames, *other.frames])
    
    def __iadd__(self, other: Self) -> Self:
        self.frames += other.frames
        return self
    
    def _as_string(self, *, sep: str) -> str:
        constructor = f"{ type(self).__name__ }()"
        if not self.frames:
            return constructor
        parts = [constructor, *map(repr, self.frames)]
        return f"{sep.join(parts)}"
    
    def __repr__(self) -> str:
        return self._as_string(sep=".")
    
    def __str__(self) -> str:
        return self._as_string(sep="\n    .")


L = TypeVar("L")
V = TypeVar("V")


class LiteralParser(Generic[L, V], metaclass=abc.ABCMeta):
    def __init__(
            self,
            name: str,
            literal_map: Dict[L, V],
            undefined_literal: Optional[L] = None
    ) -> None:
        self.name = name
        self.literal_map = literal_map
        self.value_map = {v: k for k, v in literal_map.items()}
        self.undefined_literal = undefined_literal

    def as_value(self, literal: L) -> V:
        if literal not in self.literal_map:
            if self.undefined_literal is not None:
                literal = self.undefined_literal
            else:
                raise ValueError(f"'{ literal }' is not a valid literal for type {self.name}")
        return self.literal_map[literal]

    def as_literal(self, value: V) -> L:
        if value not in self.value_map:
            if self.undefined_literal is not None:
                value = self.literal_map[self.undefined_literal]
            else:
                raise ValueError(f"'{ value }' is not a valid value for type {self.name}")
        return self.value_map[value]