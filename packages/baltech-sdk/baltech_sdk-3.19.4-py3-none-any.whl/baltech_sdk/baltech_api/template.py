
import abc
from io import BytesIO
from typing import Optional, NamedTuple, Union, Literal, TypedDict, Dict, List, ClassVar, Type as _Type

from typing_extensions import Self, NotRequired

from .common import safe_read_int_from_buffer, LiteralParser, FrameExecutor, BaltechApiError, PayloadTooLongError, PayloadTooShortError, InvalidPayloadError
from .common import ProtocolFrame, ProtocolBase
from .typedefs import *

class TemplateFrame(ProtocolFrame, metaclass=abc.ABCMeta):
    Code: Optional[int] = None

class Static(TemplateFrame):
    def __init__(self, Data: bytes) -> None:
        self.Data = Data

    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        data = b''
        while True:
            next_byte = frame.read(1)
            if not next_byte:
                break
            if next_byte == b"\x1B":
                frame.seek(frame.tell()-1)
                break
            data += next_byte
        return cls(data)

    def __bytes__(self) -> bytes:
        return self.Data
    
    def __repr__(self) -> str:
        return f"Static(Data={ repr(self.Data) })"
class EscChar(TemplateFrame):
    Code = 0x1B1B
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        return cls()
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VarData(TemplateFrame):
    Code = 0x1B01
    def __init__(self, StartPos: int, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.StartPos = StartPos
        self.Len = Len
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StartPos = safe_read_int_from_buffer(_recv_buffer, 2)
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(StartPos=_StartPos, Len=_Len, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StartPos.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartPos={ repr(self.StartPos) }')
        non_default_args.append(f'Len={ repr(self.Len) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VarDataClip(TemplateFrame):
    Code = 0x1B03
    def __init__(self, StartPos: int, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.StartPos = StartPos
        self.Len = Len
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StartPos = safe_read_int_from_buffer(_recv_buffer, 2)
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(StartPos=_StartPos, Len=_Len, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StartPos.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartPos={ repr(self.StartPos) }')
        non_default_args.append(f'Len={ repr(self.Len) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VarDataAlign(TemplateFrame):
    Code = 0x1B05
    def __init__(self, FillByte: int, StartPos: int, Len: int, Alignment: Alignment, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.FillByte = FillByte
        self.StartPos = StartPos
        self.Len = Len
        self.Alignment = Alignment
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _FillByte = safe_read_int_from_buffer(_recv_buffer, 1)
        _StartPos = safe_read_int_from_buffer(_recv_buffer, 1)
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Alignment = Alignment_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(FillByte=_FillByte, StartPos=_StartPos, Len=_Len, Alignment=_Alignment, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.FillByte.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.StartPos.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Alignment_Parser.as_value(self.Alignment).to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FillByte={ repr(self.FillByte) }')
        non_default_args.append(f'StartPos={ repr(self.StartPos) }')
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'Alignment={ repr(self.Alignment) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Serialnr(TemplateFrame):
    Code = 0x1B02
    def __init__(self, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class SerialnrAlign(TemplateFrame):
    Code = 0x1B06
    def __init__(self, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.Len = Len
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(Len=_Len, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Reconvert(TemplateFrame):
    Code = 0x1B07
    def __init__(self, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.Len = Len
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(Len=_Len, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CutNibbles(TemplateFrame):
    Code = 0x1B04
    def __init__(self, StartNibble: int, NibbleCount: int) -> None:
        self.StartNibble = StartNibble
        self.NibbleCount = NibbleCount
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StartNibble = safe_read_int_from_buffer(_recv_buffer, 2)
        _NibbleCount = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(StartNibble=_StartNibble, NibbleCount=_NibbleCount)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StartNibble.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.NibbleCount.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartNibble={ repr(self.StartNibble) }')
        non_default_args.append(f'NibbleCount={ repr(self.NibbleCount) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CutBits(TemplateFrame):
    Code = 0x1B09
    def __init__(self, StartBit: int, BitCount: int, Bitorder: TemplateBitorder) -> None:
        self.StartBit = StartBit
        self.BitCount = BitCount
        self.Bitorder = Bitorder
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StartBit = safe_read_int_from_buffer(_recv_buffer, 2)
        _BitCount = safe_read_int_from_buffer(_recv_buffer, 1)
        _Bitorder = TemplateBitorder_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(StartBit=_StartBit, BitCount=_BitCount, Bitorder=_Bitorder)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StartBit.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.BitCount.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(TemplateBitorder_Parser.as_value(self.Bitorder).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartBit={ repr(self.StartBit) }')
        non_default_args.append(f'BitCount={ repr(self.BitCount) }')
        non_default_args.append(f'Bitorder={ repr(self.Bitorder) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Bcc(TemplateFrame):
    Code = 0x1B08
    def __init__(self, StartPos: int, Len: int, InitValue: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.StartPos = StartPos
        self.Len = Len
        self.InitValue = InitValue
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StartPos = safe_read_int_from_buffer(_recv_buffer, 2)
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _InitValue = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(StartPos=_StartPos, Len=_Len, InitValue=_InitValue, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StartPos.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.InitValue.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartPos={ repr(self.StartPos) }')
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'InitValue={ repr(self.InitValue) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class ContinueTmpl(TemplateFrame):
    Code = 0x1B10
    def __init__(self, TemplateValueId: int) -> None:
        self.TemplateValueId = TemplateValueId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _TemplateValueId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(TemplateValueId=_TemplateValueId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.TemplateValueId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'TemplateValueId={ repr(self.TemplateValueId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Encrypt(TemplateFrame):
    Code = 0x1B0A
    def __init__(self, Len: int, CryptoMode: Template_Encrypt_CryptoMode, Key: int) -> None:
        self.Len = Len
        self.CryptoMode = CryptoMode
        self.Key = Key
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _CryptoMode = Template_Encrypt_CryptoMode_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _Key = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(Len=_Len, CryptoMode=_CryptoMode, Key=_Key)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Template_Encrypt_CryptoMode_Parser.as_value(self.CryptoMode).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.Key.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'CryptoMode={ repr(self.CryptoMode) }')
        non_default_args.append(f'Key={ repr(self.Key) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class ReaderSerialnr(TemplateFrame):
    Code = 0x1B0B
    def __init__(self, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CardCounter(TemplateFrame):
    Code = 0x1B0C
    def __init__(self, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Scramble(TemplateFrame):
    Code = 0x1B0D
    def __init__(self, Len: int, NoRepeat: bool, PadZero: bool, AlignRight: bool, SourceSubBlockBits: int, BitMap: List[Template_Scramble_BitMap_Entry], Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.Len = Len
        self.NoRepeat = NoRepeat
        self.PadZero = PadZero
        self.AlignRight = AlignRight
        self.SourceSubBlockBits = SourceSubBlockBits
        self.BitMap = BitMap
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ScrambleOptions_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _NoRepeat = bool((_ScrambleOptions_int >> 2) & 0b1)
        _PadZero = bool((_ScrambleOptions_int >> 1) & 0b1)
        _AlignRight = bool((_ScrambleOptions_int >> 0) & 0b1)
        _SourceSubBlockBits = safe_read_int_from_buffer(_recv_buffer, 1)
        _BitMap_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _BitMap = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_BitMap) >= _BitMap_len:
            _var_0000_int = safe_read_int_from_buffer(_recv_buffer, 1)
            _Invert = bool((_var_0000_int >> 7) & 0b1)
            _SrcBitPos = (_var_0000_int >> 0) & 0b1111111
            _BitMap_Entry = Template_Scramble_BitMap_Entry(_Invert, _SrcBitPos)
            _BitMap.append(_BitMap_Entry)
        if len(_BitMap) != _BitMap_len:
            raise PayloadTooShortError(_BitMap_len - len(_BitMap))
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(Len=_Len, NoRepeat=_NoRepeat, PadZero=_PadZero, AlignRight=_AlignRight, SourceSubBlockBits=_SourceSubBlockBits, BitMap=_BitMap, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(self.NoRepeat) & 0b1) << 2
        _var_0000_int |= (int(self.PadZero) & 0b1) << 1
        _var_0000_int |= (int(self.AlignRight) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.SourceSubBlockBits.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(self.BitMap)).to_bytes(1, byteorder='big'))
        for _BitMap_Entry in self.BitMap:
            _Invert, _SrcBitPos = _BitMap_Entry
            _var_0001_int = 0
            _var_0001_int |= (int(_Invert) & 0b1) << 7
            _var_0001_int |= (_SrcBitPos & 0b1111111) << 0
            _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'NoRepeat={ repr(self.NoRepeat) }')
        non_default_args.append(f'PadZero={ repr(self.PadZero) }')
        non_default_args.append(f'AlignRight={ repr(self.AlignRight) }')
        non_default_args.append(f'SourceSubBlockBits={ repr(self.SourceSubBlockBits) }')
        non_default_args.append(f'BitMap={ repr(self.BitMap) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Mark(TemplateFrame):
    Code = 0x1B0E
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        return cls()
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Strip(TemplateFrame):
    Code = 0x1B0F
    def __init__(self, Len: int, Leading: bool, Middle: bool, Trailing: bool, RemoveChar: int) -> None:
        self.Len = Len
        self.Leading = Leading
        self.Middle = Middle
        self.Trailing = Trailing
        self.RemoveChar = RemoveChar
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _StripOptions_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _Leading = bool((_StripOptions_int >> 2) & 0b1)
        _Middle = bool((_StripOptions_int >> 1) & 0b1)
        _Trailing = bool((_StripOptions_int >> 0) & 0b1)
        _RemoveChar = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(Len=_Len, Leading=_Leading, Middle=_Middle, Trailing=_Trailing, RemoveChar=_RemoveChar)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(self.Leading) & 0b1) << 2
        _var_0000_int |= (int(self.Middle) & 0b1) << 1
        _var_0000_int |= (int(self.Trailing) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.RemoveChar.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'Leading={ repr(self.Leading) }')
        non_default_args.append(f'Middle={ repr(self.Middle) }')
        non_default_args.append(f'Trailing={ repr(self.Trailing) }')
        non_default_args.append(f'RemoveChar={ repr(self.RemoveChar) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IsEqual(TemplateFrame):
    Code = 0x1B12
    def __init__(self, ActionOnSuccess: Template_IsEqual_ActionOnSuccess, ConstData: str) -> None:
        self.ActionOnSuccess = ActionOnSuccess
        self.ConstData = ConstData
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _ActionOnSuccess = Template_IsEqual_ActionOnSuccess_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _ConstData_bytes = b''
        _ConstData_next_byte = _recv_buffer.read(1)
        while _ConstData_next_byte and _ConstData_next_byte != b'\x00':
            _ConstData_bytes += _ConstData_next_byte
            _ConstData_next_byte = _recv_buffer.read(1)
        if not _ConstData_next_byte:
            raise InvalidPayloadError('missing zero-terminator in field ConstData')
        _ConstData = _ConstData_bytes.decode('ascii')
        return cls(ActionOnSuccess=_ActionOnSuccess, ConstData=_ConstData)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(Template_IsEqual_ActionOnSuccess_Parser.as_value(self.ActionOnSuccess).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.ConstData.encode("ascii"))
        _send_buffer.write(b'\x00')
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ActionOnSuccess={ repr(self.ActionOnSuccess) }')
        non_default_args.append(f'ConstData={ repr(self.ConstData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class BitDataEnd(TemplateFrame):
    Code = 0x1B13
    def __init__(self, SrcDataBitOrder: TemplateBitorder) -> None:
        self.SrcDataBitOrder = SrcDataBitOrder
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _SrcDataBitOrder = TemplateBitorder_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(SrcDataBitOrder=_SrcDataBitOrder)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(TemplateBitorder_Parser.as_value(self.SrcDataBitOrder).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SrcDataBitOrder={ repr(self.SrcDataBitOrder) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class ExtractBitField(TemplateFrame):
    Code = 0x1B14
    def __init__(self, SrcFieldStartBit: int, SrcFieldBits: int, Filter: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter(), *, DstFieldBytes: int) -> None:
        self.SrcFieldStartBit = SrcFieldStartBit
        self.SrcFieldBits = SrcFieldBits
        self.Filter = Filter
        self.DstFieldBytes = DstFieldBytes
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _SrcFieldStartBit = safe_read_int_from_buffer(_recv_buffer, 2)
        _SrcFieldBits = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filter_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filter_int >> 7) & 0b1)
        _BinToAscii = bool((_Filter_int >> 6) & 0b1)
        _Unpack = bool((_Filter_int >> 5) & 0b1)
        _BinToBcd = bool((_Filter_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filter_int >> 3) & 0b1)
        _Pack = bool((_Filter_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filter_int >> 1) & 0b1)
        _Reverse = bool((_Filter_int >> 0) & 0b1)
        _Filter = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        _DstFieldBytes = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(SrcFieldStartBit=_SrcFieldStartBit, SrcFieldBits=_SrcFieldBits, Filter=_Filter, DstFieldBytes=_DstFieldBytes)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.SrcFieldStartBit.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.SrcFieldBits.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filter, dict):
            self.Filter = TemplateFilter(**self.Filter)
        self.Filter_int = 0
        self.Filter_int |= (int(self.Filter.BcdToBin) & 0b1) << 7
        self.Filter_int |= (int(self.Filter.BinToAscii) & 0b1) << 6
        self.Filter_int |= (int(self.Filter.Unpack) & 0b1) << 5
        self.Filter_int |= (int(self.Filter.BinToBcd) & 0b1) << 4
        self.Filter_int |= (int(self.Filter.SwapNibbles) & 0b1) << 3
        self.Filter_int |= (int(self.Filter.Pack) & 0b1) << 2
        self.Filter_int |= (int(self.Filter.AsciiToBin) & 0b1) << 1
        self.Filter_int |= (int(self.Filter.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filter_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.DstFieldBytes.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SrcFieldStartBit={ repr(self.SrcFieldStartBit) }')
        non_default_args.append(f'SrcFieldBits={ repr(self.SrcFieldBits) }')
        if self.Filter != TemplateFilter.NoFilter():
            non_default_args.append(f'Filter={ repr(self.Filter) }')
        non_default_args.append(f'DstFieldBytes={ repr(self.DstFieldBytes) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sum(TemplateFrame):
    Code = 0x1B15
    def __init__(self, StartPos: int, Len: int, InitValue: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> None:
        self.StartPos = StartPos
        self.Len = Len
        self.InitValue = InitValue
        self.Filters = Filters
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StartPos = safe_read_int_from_buffer(_recv_buffer, 2)
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _InitValue = safe_read_int_from_buffer(_recv_buffer, 1)
        _Filters_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _BcdToBin = bool((_Filters_int >> 7) & 0b1)
        _BinToAscii = bool((_Filters_int >> 6) & 0b1)
        _Unpack = bool((_Filters_int >> 5) & 0b1)
        _BinToBcd = bool((_Filters_int >> 4) & 0b1)
        _SwapNibbles = bool((_Filters_int >> 3) & 0b1)
        _Pack = bool((_Filters_int >> 2) & 0b1)
        _AsciiToBin = bool((_Filters_int >> 1) & 0b1)
        _Reverse = bool((_Filters_int >> 0) & 0b1)
        _Filters = TemplateFilter(_BcdToBin, _BinToAscii, _Unpack, _BinToBcd, _SwapNibbles, _Pack, _AsciiToBin, _Reverse)
        return cls(StartPos=_StartPos, Len=_Len, InitValue=_InitValue, Filters=_Filters)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StartPos.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(self.Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.InitValue.to_bytes(length=1, byteorder='big'))
        if isinstance(self.Filters, dict):
            self.Filters = TemplateFilter(**self.Filters)
        self.Filters_int = 0
        self.Filters_int |= (int(self.Filters.BcdToBin) & 0b1) << 7
        self.Filters_int |= (int(self.Filters.BinToAscii) & 0b1) << 6
        self.Filters_int |= (int(self.Filters.Unpack) & 0b1) << 5
        self.Filters_int |= (int(self.Filters.BinToBcd) & 0b1) << 4
        self.Filters_int |= (int(self.Filters.SwapNibbles) & 0b1) << 3
        self.Filters_int |= (int(self.Filters.Pack) & 0b1) << 2
        self.Filters_int |= (int(self.Filters.AsciiToBin) & 0b1) << 1
        self.Filters_int |= (int(self.Filters.Reverse) & 0b1) << 0
        _send_buffer.write(self.Filters_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartPos={ repr(self.StartPos) }')
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'InitValue={ repr(self.InitValue) }')
        if self.Filters != TemplateFilter.NoFilter():
            non_default_args.append(f'Filters={ repr(self.Filters) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Align(TemplateFrame):
    Code = 0x1B16
    def __init__(self, FillByte: int, DestLen: int, Alignment: Alignment) -> None:
        self.FillByte = FillByte
        self.DestLen = DestLen
        self.Alignment = Alignment
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _FillByte = safe_read_int_from_buffer(_recv_buffer, 1)
        _DestLen = safe_read_int_from_buffer(_recv_buffer, 1)
        _Alignment = Alignment_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(FillByte=_FillByte, DestLen=_DestLen, Alignment=_Alignment)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.FillByte.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.DestLen.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Alignment_Parser.as_value(self.Alignment).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FillByte={ repr(self.FillByte) }')
        non_default_args.append(f'DestLen={ repr(self.DestLen) }')
        non_default_args.append(f'Alignment={ repr(self.Alignment) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Template(ProtocolBase[TemplateFrame]):
    """
    A Template defines a conversation rule how source data (i.e. VHL file) is
    converted to destination data. It consists of static data, which is copied 1:1
    to the destination data and command which are replaced by variable data.
    
    A TemplateCommand defines an area of variable content within a
    [Template](.#Template) (the rest of the Template is static content, except the
    byte 0x1B, see _EscChar_ ).
    
    variable content is fetched from one of the following sources:
    
      * Part of the Source Data 
      * Serialnumber of the currently presented card (only available on Autoread Rules) 
      * Part of the already generated destination Buffer 
    
    The variable data that is inserted at the TemplateCommands location depends on
    the commandbyte that starts the TemplateCommand defintion and the command
    specific parameter that are following the command. The available commands are
    listed below (including a description of their parameters).
    
    ` Template: "HDR" VarData 0001 02 NoFilter "TAIL" Sourcedata: "12345"
    Destinationdata: "HDR23TAIL" `
    """
    CodeMap: Dict[int, _Type[TemplateFrame]] = {
        0x1B1B: EscChar,
        0x1B01: VarData,
        0x1B03: VarDataClip,
        0x1B05: VarDataAlign,
        0x1B02: Serialnr,
        0x1B06: SerialnrAlign,
        0x1B07: Reconvert,
        0x1B04: CutNibbles,
        0x1B09: CutBits,
        0x1B08: Bcc,
        0x1B10: ContinueTmpl,
        0x1B0A: Encrypt,
        0x1B0B: ReaderSerialnr,
        0x1B0C: CardCounter,
        0x1B0D: Scramble,
        0x1B0E: Mark,
        0x1B0F: Strip,
        0x1B12: IsEqual,
        0x1B13: BitDataEnd,
        0x1B14: ExtractBitField,
        0x1B15: Sum,
        0x1B16: Align,
    }
    
    def frame_header(self, frame: TemplateFrame) -> bytes:
        if frame.Code is not None:
            return frame.Code.to_bytes(length=2, byteorder='big')
        return b''
    
    @classmethod
    def parse_frames(cls, data: bytes) -> List[TemplateFrame]:
        buffer = BytesIO(data)
        frames: List[TemplateFrame] = []
        while True:
            next_byte = buffer.read(1)
            if not next_byte:
                break
            if next_byte != b'\x1B':
                buffer.seek(buffer.tell()-1)
                frames.append(Static.read_from(buffer))
            else:
                code = int.from_bytes(next_byte + buffer.read(1), byteorder="big")
                frame_class = cls.CodeMap.get(code)
                if frame_class is None:
                    raise InvalidPayloadError(f'Invalid Template code 0x{code:04X}')
                frames.append(frame_class.read_from(buffer))
                
        return frames
    
    def Static(self, Data: bytes) -> Self:
        self.frames.append(Static(Data))
        return self
    def EscChar(self, ) -> Self:
        """
        To include the Bytecode 0x1B into the static part of the template, this
        command has to be used.
        
        ` Template: 12 EscChar 34 Destination data: 12 1B 34 `
        """
        self.frames.append(EscChar())
        return self
    def VarData(self, StartPos: int, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        Copies _exactly Len_ bytes from source data beginning at _StartPos_ to the
        TemplateCommands location.
        
        Before inserting the data finally it will be converted using the Filters
        specified in _Filters_.
        
        **If source data's length is lesser than _StartPos_ +_Len_ the conversion with
        this Template will fail. See also[ VarDataClip](.#Template.VarDataClip) and[
        VarDataAlign](.#Template.VarDataAlign)**
        """
        self.frames.append(VarData(StartPos=StartPos, Len=Len, Filters=Filters))
        return self
    def VarDataClip(self, StartPos: int, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        Is identical to the _VarData_ TemplateCommand, except that it inserts the data
        also if the source data's length is shorter than _StartPos_ \+ _Len_. In this
        case the inserted data will be shorter than _Len_
        """
        self.frames.append(VarDataClip(StartPos=StartPos, Len=Len, Filters=Filters))
        return self
    def VarDataAlign(self, FillByte: int, StartPos: int, Len: int, Alignment: Alignment, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        Copies _Len_ bytes from source data, beginning at _StartPos_ , to the
        TemplateCommands location.
        
        Is identical to the _VarData_ TemplateCommand, except that it accepts source
        data of variable length. It will extend/cut the source data depending on its
        length.
        
        ` Template: VarDataAlign "_" 01 04 Right NoFilter Sourcedata: "1234"
        Destination data: "_234" `
        """
        self.frames.append(VarDataAlign(FillByte=FillByte, StartPos=StartPos, Len=Len, Alignment=Alignment, Filters=Filters))
        return self
    def Serialnr(self, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        This command inserts the serialnumber of the currently processed card at the
        TemplateCommands location. Before inserting it, the filters in _Filters_ are
        applied.
        
        **This command works only in[ Autoread
        Templates](autoread.xml#Autoread.Rule.Template) .**
        
        **The length of this field depends on the cardtype of the card that is
        presented.**
        """
        self.frames.append(Serialnr(Filters=Filters))
        return self
    def SerialnrAlign(self, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        This command is identical to _Serialnr_ , except that it extends/cuts the
        serialnumber's length to match exactly _Len_ before applying the filter.
        """
        self.frames.append(SerialnrAlign(Len=Len, Filters=Filters))
        return self
    def Reconvert(self, Len: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        Using this command, _Filters_ can be applied again to the last generated
        Bytes. The size of the block to convert again can be spcified via _Len_ either
        by specifiying the number of Bytes or by setting it to _0xFF_ and set a marker
        (see command _Mark_ ). In the latter case all bytes from the marker to the end
        are reconverted.
        
        ` Template: "xy15" Reconvert 2 AsciiToBin|BcdToHex|BinToAscii Destination
        data: "xy0F" `
        """
        self.frames.append(Reconvert(Len=Len, Filters=Filters))
        return self
    def CutNibbles(self, StartNibble: int, NibbleCount: int) -> Self:
        """
        **This command is deprecated. Please use[
        ExtractBitField](.#Template.ExtractBitField) .**
        
        this command can remove data from the already generated Bytes. It works on
        nibble (half-byte) level. Thus all parameters are addressing nibbles not
        bytes.
        
        _StartNibble_ specifies the address (beginning from the start of the
        destination data) of the first nibble to remove. _NibbleCount_ specifies the
        number of nibbles to remove. If an odd number of nibbles is removed, a
        0-nibble is inserted into the Least-significant-nibble at the end of
        destination data.
        
        ` Template: 12 34 56 CutNibbles 0001 3 Destination data: 15 60 `
        """
        self.frames.append(CutNibbles(StartNibble=StartNibble, NibbleCount=NibbleCount))
        return self
    def CutBits(self, StartBit: int, BitCount: int, Bitorder: TemplateBitorder) -> Self:
        """
        **This command is deprecated. Please use[
        ExtractBitField](.#Template.ExtractBitField) .**
        
        This command is identical to _CutNibbles_ , but works on bit level instead of
        nibble level.
        
        Depending on _Bitorder_ all values are considered as MSB-values or LSB values.
        In case they are are considered as MSB this means bit position 0 corresponds
        to byte value 0x80 and bit position 7 corresponds to byte value 0x01.
        
        **If the number of remaining bits is not multiple of eight, the template will
        be filled with 0-bits at the end to ensure that the it matches the next byte
        boundary.**
        
        ` Template: FF 01 CutNibbles 0006 7 Destination data: FC 80 `
        """
        self.frames.append(CutBits(StartBit=StartBit, BitCount=BitCount, Bitorder=Bitorder))
        return self
    def Bcc(self, StartPos: int, Len: int, InitValue: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        This Command calculates a XOR-8bit-BCC over some bytes of the already
        generated destination data. The bytes to include into this calculation are
        specified by _StartPos_ and _Len_ , which are specifying the first byte
        beginning from the destination data and the number of bytes.
        
        After all bytes are XORed the InitValue will be XORed to the result. Then all
        filters specified in _Filters_ will be applied and the result stored at the
        TemplateCommand location.
        
        **If a marker is set,_StartPos_ will be ignored and the marker position will
        be used as start instead (without removing the marker from the marker stack).
        If furthermore _Len_ is 0xFF, all data up to the end of the destination data
        will be included in the BCC calculation and the marker will be removed from
        the marker stack.**
        
        ` Template: 0xFF 0x08 0x10 0xFF Bcc 0001 2 0x40 NoFilter Destination data:
        0xFF 0x08 0x10 0xFF 0x58 `
        """
        self.frames.append(Bcc(StartPos=StartPos, Len=Len, InitValue=InitValue, Filters=Filters))
        return self
    def ContinueTmpl(self, TemplateValueId: int) -> Self:
        """
        Since configuration values must not exceed 128 Bytes very complex Templates
        might not fit within a single value. To overcome this limitation this command
        allows to extend this template by another one within the same subkey. The
        valueid of the extension template must be specified in _TemplateValueId_.
        
        Theoretically an arbitrary number of values may be concatenated to a single
        template this way. In practice the only limitation is the maximum size of
        destination data supported by the firmware.
        """
        self.frames.append(ContinueTmpl(TemplateValueId=TemplateValueId))
        return self
    def Encrypt(self, Len: int, CryptoMode: Template_Encrypt_CryptoMode, Key: int) -> Self:
        """
        This command encrypts the last generated bytes of the destination data. The
        number of concerned bytes is specified in _Len_ and has to be either the count
        of bytes or 0xFF, in which case all bytes from the last _Mark_ Command to the
        end are encrypted.
        
        The used Cryptoalgorithm is TripleDES. The _Cryptomode_ specifies the used
        cryptomode. If the number of bytes to encrypt is not a multiple of 8, the
        missing bytes will be filled with 0 at the end.
        
        The _Key_ Key specifies a valueid within the subkey where the template is
        stored. This value contains a 16byte Key, that shall be used for encryption.
        
        **The _Key_ should be > 0x80 to ensure security (values < 0x80 can be read
        out)**
        """
        self.frames.append(Encrypt(Len=Len, CryptoMode=CryptoMode, Key=Key))
        return self
    def ReaderSerialnr(self, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        Inserts the reader serialnumber as 8 byte decimal ASCII number. Before finally
        inserting the data, filters specified in _Filters_ will be applied.
        """
        self.frames.append(ReaderSerialnr(Filters=Filters))
        return self
    def CardCounter(self, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        Inserts a [counter](autoread.xml#Autoread.Rule.Counter) that increases
        everytime the template is used to convert data (i.e. everytime a card is
        presented in autoread mode). The counter is inserted as 4 byte binary number
        that is converted by the specified filters in _Filters_.
        """
        self.frames.append(CardCounter(Filters=Filters))
        return self
    def Scramble(self, Len: int, NoRepeat: bool, PadZero: bool, AlignRight: bool, SourceSubBlockBits: int, BitMap: List[Template_Scramble_BitMap_Entry], Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        **This command should only be required in very rare cases. Usually[
        ExtractBitField](.#Template.ExtractBitField) is a better and much more simpler
        option.**
        
        Using this command, the bits of the last generated Bytes can be
        scrambled/inverted in any fashion. The main steps of this command are:
        
          1. Determine the data that shall be scrambled. Either the last _Len_ bytes are used, or (if _Len_ is 0xFF) all bytes from the last marker (see _Mark_ command) to the end are used. This data is used as source data and will be replaced. 
          2. Split the resulting block into sub-blocks, that all are of length _SourceSubBlockBits_. If _Len_ * 8 is not multiple of _SourceSubBlockBits_ the remaining bits in the source data are ignored by default. Alternatively the ScrambleOptions can be used to set "PadZero". In this case the remaining bits of the source data are extended by 0-bits until the length of the remaining block is _SourceSubBlockBits_ and thus can be processed. 
          3. Every source block is scrambled by generating a destination block. This destination block is of the same size as the _BitMap_ array. _BitMap_ specifies a mapping of source bits to destination bits. This mapping is applied to every source block and results in a corresponding destination block 
          4. The scrambled destination blocks are concatenated again. If the total number of bits in all destination blocks is not a multiple of 8, padding zero bits are appended, until the number of bits is exactly a multiple of 8. 
          5. The filters specified in _Filters_ are applied to the resulting content. 
        
        The most regular use case of this command is cutting a bitfield out of the
        source data without the requirement of repetitions. The following command
        shows a sample, that cuts a field of 4 bits starting at bit index 6 from the
        source data and converts it to a 4 digit ASCII decimal number.
        
        ` {optionally some data before scramble} Mark {template to be scrambled}
        Scramble 0xFF 'scramble all data between Mark and Scramble' NoRepeat 'Do a
        simple scramble without multiple blocks' 16 'scramble the first 16 bits of
        {variable-data}' 8 'the scrambled data should be a multiple of 8!' 0x7F 0x7F
        0x7F 0x7F 6 7 8 9 '4 leading zeros, then bytes 6-9 of source data'
        Bin2Bcd|Unpack|Bin2Ascii 'convert data to ASCII decimal' `
        """
        self.frames.append(Scramble(Len=Len, NoRepeat=NoRepeat, PadZero=PadZero, AlignRight=AlignRight, SourceSubBlockBits=SourceSubBlockBits, BitMap=BitMap, Filters=Filters))
        return self
    def Mark(self, ) -> Self:
        """
        This is used as position marker for the commands _Reconvert_ , _Encrypt_ ,
        _Bcc_ , _Strip_ , _Scramble_ , and _Sum_ when they have no _Len_ parameter
        specified but use 0xFF as length.
        
        Mark pushes the current position within the destination data onto a internal
        stack. When one of the above commands (with _Len_ parameter is 0xFF) is
        detected, it removes the top position from the stack. Then all data from this
        removed position to the end of the destination data is processed.
        
        **If one the above commands (with _Len_ parameter is 0xFF) is detected and the
        internal position stack is empty (No matching _Mark_ command found), all
        destination data (from byte 0 to the current end) will be processed.**
        
        **The stack size for Mark commands is 4. If more than 4 positions are pushed
        by Mark commands without removing one from the top of the stack the "oldest"
        position gets lost. On 12.06.18 the stack size was increased from 2 to 4!**
        
        ` Template: 12 Mark 34 Mark 56 Reconvert UnPack Reconvert Unpack 78
        Destination data before first Reconvert: 12 34 56 Destination data after first
        Reconvert: 12 34 05 06 Destination data after second Reconvert: 12 03 04 00 05
        00 06 Destination data after finish: 12 03 04 00 05 00 06 78 `
        """
        self.frames.append(Mark())
        return self
    def Strip(self, Len: int, Leading: bool, Middle: bool, Trailing: bool, RemoveChar: int) -> Self:
        """
        This command removes characters of a specific value. The area to strip is
        defined by _Len_. Either the last _Len_ bytes are stripped, or (if _Len_ is
        0xFF) all bytes from the last marker (see _Mark_ command) to the end are
        stripped.
        
        The character to remove can be specfied by RemoveChar (is usually "0").
        StripOptions specify if leading or trailing characters shall be removed
        """
        self.frames.append(Strip(Len=Len, Leading=Leading, Middle=Middle, Trailing=Trailing, RemoveChar=RemoveChar))
        return self
    def IsEqual(self, ActionOnSuccess: Template_IsEqual_ActionOnSuccess, ConstData: str) -> Self:
        """
        This command checks if the last converted bytes are equal to _ConstData_. If
        this is not the case, the conversion of the template is cancelled.
        
        The number of compared bytes is determined by the length of _ConstData_. This
        means that the comparing operation is done until _ConstData_ ends with a zero
        byte.
        
        **It is strongly recommended to convert the data always to ASCII before
        comparing it with IsEqual. Otherwise the user had to ensure that "ConstData"
        contains no zero byte, as it would be interpreted as String terminator.**
        
        If the number of bytes already converted is lower than the length of
        _ConstData_ , the conversion is cancelled.
        """
        self.frames.append(IsEqual(ActionOnSuccess=ActionOnSuccess, ConstData=ConstData))
        return self
    def BitDataEnd(self, SrcDataBitOrder: TemplateBitorder) -> Self:
        """
        If the source data (i.e. the data to be read from the card) is bitwise
        organized the Template rendering is split into two phases:
        
          1. The first phase retrieves the bit data from the data source (i.e. card; usually done by [VarData](.#Template.VarData) or [Serialnr](.#Template.Serialnr)) 
          2. The second phase converts the bit data returned by the first phase into ASCII data (Usually done by [ExtractBitField](.#Template.ExtractBitField)) 
        
        This command delimits the template for phase one (the template-description
        before this command) from the template for the second phase (the template-
        description after this command). The returned result is only the result from
        phase 2!
        
        For the rare case that this command does not fulfil your requirements please
        use [Scramble](.#Template.Scramble).
        
        **This commmand must occur at maximum once per template.**
        """
        self.frames.append(BitDataEnd(SrcDataBitOrder=SrcDataBitOrder))
        return self
    def ExtractBitField(self, SrcFieldStartBit: int, SrcFieldBits: int, Filter: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter(), *, DstFieldBytes: int) -> Self:
        """
        This command includes a bit field from the source data (phase 1) and converts
        it into an ASCII number. It can only be used after a preceding phase 1, see
        [BitDataEnd](.#Template.BitDataEnd).
        
        **The resulting number is returned with the most significant digits first.
        LSB-encoded source data will be converted automatically.**
        
        The following sample cuts bits 1-6, converts them to ASCII, and extends the
        number to 4 digits. This results in "0016".
        
        ` 0x5A BitDataEnd Msb ExtractBitField 0001 5 Unpack|BinToAscii 4 `
        
        The next sample shows the difference between the MSB- and the LSB-first
        encoding. This command outputs "3456" as it is, but by specifying _BitDataEnd
        Lsb_ instead, we would obtain "5634", since the input is interpreted as
        "0x78563412".
        
        ` 0x12345678 BitDataEnd Msb ExtractBitField 0008 16 Unpack|BinToAscii 0 `
        """
        self.frames.append(ExtractBitField(SrcFieldStartBit=SrcFieldStartBit, SrcFieldBits=SrcFieldBits, Filter=Filter, DstFieldBytes=DstFieldBytes))
        return self
    def Sum(self, StartPos: int, Len: int, InitValue: int, Filters: Union[TemplateFilter, TemplateFilter_Dict] = TemplateFilter.NoFilter()) -> Self:
        """
        This command calculates the 8-bit sum over some bytes of the already generated
        destination data. The bytes to include into this calculation are specified by
        _StartPos_ and _Len_ , which specify the first byte beginning from the
        destination data and the number of bytes.
        
        InitValue will be added to the sum of the specified bytes. Then all filters
        specified in _Filters_ will be applied and the result will be stored at the
        TemplateCommand location.
        
        **If a marker is set,_StartPos_ will be ignored and the marker position will
        be used as start instead (without removing the marker from the marker stack).
        If furthermore _Len_ is 0xFF, all data up to the end of the destination data
        will be included in the calculation and the marker will be removed from the
        marker stack.**
        
        ` Template: 0xFF 0x08 0x19 0xFF Sum 0001 2 0x40 NoFilter Destination data:
        0xFF 0x08 0x19 0xFF 0x61 `
        """
        self.frames.append(Sum(StartPos=StartPos, Len=Len, InitValue=InitValue, Filters=Filters))
        return self
    def Align(self, FillByte: int, DestLen: int, Alignment: Alignment) -> Self:
        """
        This command aligns the last generated bytes of destination data. Depending on
        the required destination length, data is clipped or extended.
        
        **If a marker is set, the marker position will be used as the start position
        for the data to be aligned. Otherwise, all available data will be aligned.**
        
        ` Template: 0x12 0x34 Align 0x00 5 Right Destination data: 0x00 0x00 0x00 0x12
        0x34 `
        """
        self.frames.append(Align(FillByte=FillByte, DestLen=DestLen, Alignment=Alignment))
        return self