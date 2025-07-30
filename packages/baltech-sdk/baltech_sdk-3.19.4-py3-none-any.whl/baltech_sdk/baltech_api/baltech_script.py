
import abc
from io import BytesIO
from typing import Optional, NamedTuple, Union, Literal, TypedDict, Dict, List, ClassVar, Type as _Type

from typing_extensions import Self, NotRequired

from .common import safe_read_int_from_buffer, LiteralParser, FrameExecutor, BaltechApiError, PayloadTooLongError, PayloadTooShortError, InvalidPayloadError
from .common import ProtocolFrame, ProtocolBase
from .typedefs import *

class BaltechScriptFrame(ProtocolFrame, metaclass=abc.ABCMeta):
    Code: int
class Enable(BaltechScriptFrame):
    Code = 0x1
    def __init__(self, EnabledIoPort: IoPort) -> None:
        self.EnabledIoPort = EnabledIoPort
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _EnabledIoPort = IoPort_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(EnabledIoPort=_EnabledIoPort)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(IoPort_Parser.as_value(self.EnabledIoPort).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'EnabledIoPort={ repr(self.EnabledIoPort) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Disable(BaltechScriptFrame):
    Code = 0x2
    def __init__(self, DisabledIoPort: IoPort) -> None:
        self.DisabledIoPort = DisabledIoPort
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _DisabledIoPort = IoPort_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(DisabledIoPort=_DisabledIoPort)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(IoPort_Parser.as_value(self.DisabledIoPort).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DisabledIoPort={ repr(self.DisabledIoPort) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Toggle(BaltechScriptFrame):
    Code = 0x3
    def __init__(self, ToggledIoPort: IoPort, RepeatCount: int, Delay: int) -> None:
        self.ToggledIoPort = ToggledIoPort
        self.RepeatCount = RepeatCount
        self.Delay = Delay
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _ToggledIoPort = IoPort_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _RepeatCount = safe_read_int_from_buffer(_recv_buffer, 1)
        _Delay = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(ToggledIoPort=_ToggledIoPort, RepeatCount=_RepeatCount, Delay=_Delay)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(IoPort_Parser.as_value(self.ToggledIoPort).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.RepeatCount.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.Delay.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ToggledIoPort={ repr(self.ToggledIoPort) }')
        non_default_args.append(f'RepeatCount={ repr(self.RepeatCount) }')
        non_default_args.append(f'Delay={ repr(self.Delay) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class ToggleInverted(BaltechScriptFrame):
    Code = 0x6
    def __init__(self, InvertedToggledIoPort: IoPort, RepeatCount: int, Delay: int) -> None:
        self.InvertedToggledIoPort = InvertedToggledIoPort
        self.RepeatCount = RepeatCount
        self.Delay = Delay
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _InvertedToggledIoPort = IoPort_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _RepeatCount = safe_read_int_from_buffer(_recv_buffer, 1)
        _Delay = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(InvertedToggledIoPort=_InvertedToggledIoPort, RepeatCount=_RepeatCount, Delay=_Delay)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(IoPort_Parser.as_value(self.InvertedToggledIoPort).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.RepeatCount.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.Delay.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'InvertedToggledIoPort={ repr(self.InvertedToggledIoPort) }')
        non_default_args.append(f'RepeatCount={ repr(self.RepeatCount) }')
        non_default_args.append(f'Delay={ repr(self.Delay) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class DefaultAction(BaltechScriptFrame):
    Code = 0x4
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
class SendCardMsg(BaltechScriptFrame):
    Code = 0x5
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
class SendMsg(BaltechScriptFrame):
    Code = 0x7
    def __init__(self, MsgType: MessageType, MsgId: int, Protocol: ProtocolID) -> None:
        self.MsgType = MsgType
        self.MsgId = MsgId
        self.Protocol = Protocol
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _MsgType = MessageType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _MsgId = safe_read_int_from_buffer(_recv_buffer, 1)
        _Protocol = ProtocolID_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(MsgType=_MsgType, MsgId=_MsgId, Protocol=_Protocol)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(MessageType_Parser.as_value(self.MsgType).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.MsgId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ProtocolID_Parser.as_value(self.Protocol).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'MsgType={ repr(self.MsgType) }')
        non_default_args.append(f'MsgId={ repr(self.MsgId) }')
        non_default_args.append(f'Protocol={ repr(self.Protocol) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class SetTimer(BaltechScriptFrame):
    Code = 0xB
    def __init__(self, TimerId: int, TimerValue: int) -> None:
        self.TimerId = TimerId
        self.TimerValue = TimerValue
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _TimerId = safe_read_int_from_buffer(_recv_buffer, 1)
        _TimerValue = safe_read_int_from_buffer(_recv_buffer, 2)
        return cls(TimerId=_TimerId, TimerValue=_TimerValue)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.TimerId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(self.TimerValue.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'TimerId={ repr(self.TimerId) }')
        non_default_args.append(f'TimerValue={ repr(self.TimerValue) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class SetVar(BaltechScriptFrame):
    Code = 0x8
    def __init__(self, VarId: int) -> None:
        self.VarId = VarId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _VarId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(VarId=_VarId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.VarId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'VarId={ repr(self.VarId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class ClearVar(BaltechScriptFrame):
    Code = 0x9
    def __init__(self, VarId: int) -> None:
        self.VarId = VarId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _VarId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(VarId=_VarId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.VarId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'VarId={ repr(self.VarId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class AssignVar(BaltechScriptFrame):
    Code = 0xA
    def __init__(self, VarId: int) -> None:
        self.VarId = VarId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _VarId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(VarId=_VarId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.VarId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'VarId={ repr(self.VarId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IfIoPort(BaltechScriptFrame):
    Code = 0x44
    def __init__(self, CheckedIoPort: IoPort) -> None:
        self.CheckedIoPort = CheckedIoPort
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _CheckedIoPort = IoPort_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(CheckedIoPort=_CheckedIoPort)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(IoPort_Parser.as_value(self.CheckedIoPort).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'CheckedIoPort={ repr(self.CheckedIoPort) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IfVar(BaltechScriptFrame):
    Code = 0x45
    def __init__(self, VarId: int) -> None:
        self.VarId = VarId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _VarId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(VarId=_VarId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.VarId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'VarId={ repr(self.VarId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IfProtocolEnabled(BaltechScriptFrame):
    Code = 0x41
    def __init__(self, Protocol: ProtocolID) -> None:
        self.Protocol = Protocol
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Protocol = ProtocolID_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        return cls(Protocol=_Protocol)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(ProtocolID_Parser.as_value(self.Protocol).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Protocol={ repr(self.Protocol) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IfDip(BaltechScriptFrame):
    Code = 0x42
    def __init__(self, DipId: int) -> None:
        self.DipId = DipId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _DipId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(DipId=_DipId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.DipId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DipId={ repr(self.DipId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IfState(BaltechScriptFrame):
    Code = 0x40
    def __init__(self, StateId: int) -> None:
        self.StateId = StateId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _StateId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(StateId=_StateId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.StateId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StateId={ repr(self.StateId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Not(BaltechScriptFrame):
    Code = 0x80
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
class Or(BaltechScriptFrame):
    Code = 0x81
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
class And(BaltechScriptFrame):
    Code = 0x82
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
class IfTrue(BaltechScriptFrame):
    Code = 0x43
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
class Trace(BaltechScriptFrame):
    Code = 0xC
    def __init__(self, LogCode: int) -> None:
        self.LogCode = LogCode
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _LogCode = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(LogCode=_LogCode)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.LogCode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LogCode={ repr(self.LogCode) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Run(BaltechScriptFrame):
    Code = 0xD
    def __init__(self, EventId: int) -> None:
        self.EventId = EventId
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _EventId = safe_read_int_from_buffer(_recv_buffer, 1)
        return cls(EventId=_EventId)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(self.EventId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'EventId={ repr(self.EventId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class RunSequence(BaltechScriptFrame):
    Code = 0x13
    def __init__(self, Cmds: List[RunSequenceCmd]) -> None:
        self.Cmds = Cmds
    @classmethod
    def read_from(cls, frame: BytesIO) -> Self:
        _recv_buffer = frame
        _Cmds = []  # type: ignore[var-annotated,unused-ignore]
        while not False:
            _CmdCode = RunSequenceCmd_CmdCode_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
            if _CmdCode == "RepeatLoop":
                _RepeatCnt = safe_read_int_from_buffer(_recv_buffer, 1)
            else:
                _RepeatCnt = None
            if _CmdCode == "WaitMs" or _CmdCode == "WaitSec":
                _Param = safe_read_int_from_buffer(_recv_buffer, 1)
            else:
                _Param = None
            if _CmdCode == "EnablePort" or _CmdCode == "DisablePort":
                _SwitchIoPort = IoPort_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
            else:
                _SwitchIoPort = None
            _Cmd = RunSequenceCmd(_CmdCode, _RepeatCnt, _Param, _SwitchIoPort)
            _Cmds.append(_Cmd)
            if _CmdCode == "EndOfSequence":
                break
        return cls(Cmds=_Cmds)
    def __bytes__(self) -> bytes:
        _send_buffer = BytesIO()
        for _Cmds_Entry in self.Cmds:
            _Cmd = _Cmds_Entry
            if isinstance(_Cmd, dict):
                _Cmd = RunSequenceCmd(**_Cmd)
            _CmdCode, _RepeatCnt, _Param, _SwitchIoPort = _Cmd
            _send_buffer.write(RunSequenceCmd_CmdCode_Parser.as_value(_CmdCode).to_bytes(length=1, byteorder='big'))
            if _CmdCode == "RepeatLoop":
                if _RepeatCnt is None:
                    raise TypeError("missing a required argument: '_RepeatCnt'")
                _send_buffer.write(_RepeatCnt.to_bytes(length=1, byteorder='big'))
            if _CmdCode == "WaitMs" or _CmdCode == "WaitSec":
                if _Param is None:
                    raise TypeError("missing a required argument: '_Param'")
                _send_buffer.write(_Param.to_bytes(length=1, byteorder='big'))
            if _CmdCode == "EnablePort" or _CmdCode == "DisablePort":
                if _SwitchIoPort is None:
                    raise TypeError("missing a required argument: '_SwitchIoPort'")
                _send_buffer.write(IoPort_Parser.as_value(_SwitchIoPort).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Cmds={ repr(self.Cmds) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class BaltechScript(ProtocolBase[BaltechScriptFrame]):
    """
    Baltech Script is a small language to define simple actions the reader should
    execute. A Baltech Script consists of one or more commands processed
    sequentially when the script is run. Usually these actions are assigned to
    events such as ''card presentation'' or ''I/O port set to low'' in Autoread
    Mode based readers. Alternatively, the host can execute such a script via
    protocol using the [AR.RunScript](../cmds/autoread.xml#AR.RunScript) command.
    
    A script has to be stored as a configuration value within the [Scripts /
    Events](autoread.xml#Scripts.Events) Key, if it shall be assigned to an event.
    This configuration Key contains a list of all available configuration Values
    and the events assigned to them.
    
    **Script commands are never waiting or delaying execution. If they start a
    long running process (i.e.[ Toggle](.#BaltechScript.Toggle) ), this process
    will be started asynchronously. This means that the script is not waiting
    until the corresponding command has finished.**
    
    _Example_
    
    The following example describes a scenario in which the Baltech reader runs in
    Autoread Mode.
    
      * As long as the reader is waiting for cards, the green LED should be enabled. 
      * On card presentation, the reader should read the card number and send it to the host. 
      * One of the input pins (Input0) shall be used as ''lock signal''. If this pin is set to ''low'', the reader will not send the card number to the host but beep three times (at 1 Hz frequency) and disable the green led while beeping. 
      * As soon as this pin is high again, the ID-engine will continue sending the card number to the host without beeping when detecting a valid card. 
    
    The script to be executed in case a presented card is deemed valid by the
    Baltech reader is stored in the [Scripts / Events /
    OnAccepted](autoread.xml#Scripts.Events.OnAccepted) configuration Value.
    
    The desired script needs to decide if the pin labeled _Input0_ is low (logical
    false) or not:
    
      * If _Input0_ is high (logical true), the script should be stopped and the default action should be executed. The default action for the _OnAccepted_ event is to send the card number to the host. 
      * If _Input0_ is low, the script should toggle the beeper 3 times where the beeper shall be enabled for 500 ms on every beep. Furthermore the red led should be enabled for 3000 ms. 
    
    This script takes the following form:
    
      1. [IfIoPort](.#BaltechScript.IfIoPort) Input0 (hex code 44 04) 
      2. [DefaultAction](.#BaltechScript.DefaultAction) (hex code 04) 
      3. [IfIoPort](.#BaltechScript.IfIoPort) Input0 [Not](.#BaltechScript.Not) (hex code 44 04 80) 
      4. [Toggle](.#BaltechScript.Toggle) Beeper 3 5 (hex code 03 02 03 05) 
      5. [ToggleInverted](.#BaltechScript.ToggleInverted) GreenLed 1 30 (hex code 06 00 01 1E) 
    
    A second script is needed to ensure that the green LED is enabled after the
    reader powers up. As soon as the reader is initialized completely, the host
    protocol is activated. Thus the [Scripts / Events /
    OnEnabledProtocol](autoread.xml#Scripts.Events.OnEnabledProtocol) event can be
    used to trigger the second script:
    
      * [Enable](.#BaltechScript.Enable) GreenLed (hex code 01 00) 
    
    _Condition Stack_
    
    A condition stack, necessary for conditional execution of parts of a script,
    is included as a feature of the Baltech Script language. It consists of a list
    of flags which may be either _false_ (=0) or _true_ (=1). If the topmost flag
    is _true_ , all subsequent commands will be executed. If the topmost flag is
    _false_ , none of the subsequent commands is executed, except commands
    modifying the stack. When a script is started, the condition stack is always
    empty. Thus, all commands are executed. The following list summarizes all
    commands modifying the condition stack:
    
      * All commands starting with _If_ push a new flag onto the top of the stack ([IfIoPort](.#BaltechScript.IfIoPort), [IfVar](.#BaltechScript.IfVar), [IfProtocolEnabled](.#BaltechScript.IfProtocolEnabled), [IfDip](.#BaltechScript.IfDip), [IfState](.#BaltechScript.IfState), [IfTrue](.#BaltechScript.IfTrue)). 
      * Some commands modify the top of the stack ([Not](.#BaltechScript.Not), [Or](.#BaltechScript.Or), [And](.#BaltechScript.And)) 
      * The [AssignVar](.#BaltechScript.AssignVar) command removes the topmost flag from the stack. 
    
    The architecture allows an inverse polish notation for complex boolean
    expressions such as:
    
    ` If "global state variable 8" is true and "dip switch 3" is off do X `
    
    _Global State Variables_
    
    To save a script's state, 16 so-called global state variables are available.
    These variables are flags which can be set or cleared within a script. They
    keep their state even after the execution of a script. Thus, the next script
    can access the flags set by the previous script.
    
    Initially, all 16 global state variables are cleared (=0).
    
    It is possible to modify these global variables via a script or to copy a
    variable onto the top of the Condition Stack and vice-versa. Please refer to
    the description of the [SetVar](.#BaltechScript.SetVar),
    [ClearVar](.#BaltechScript.ClearVar), [AssignVar](.#BaltechScript.AssignVar)
    and [IfVar](.#BaltechScript.IfVar) functions for detailed information.
    """
    CodeMap: Dict[int, _Type[BaltechScriptFrame]] = {
        0x0001: Enable,
        0x0002: Disable,
        0x0003: Toggle,
        0x0006: ToggleInverted,
        0x0004: DefaultAction,
        0x0005: SendCardMsg,
        0x0007: SendMsg,
        0x000B: SetTimer,
        0x0008: SetVar,
        0x0009: ClearVar,
        0x000A: AssignVar,
        0x0044: IfIoPort,
        0x0045: IfVar,
        0x0041: IfProtocolEnabled,
        0x0042: IfDip,
        0x0040: IfState,
        0x0080: Not,
        0x0081: Or,
        0x0082: And,
        0x0043: IfTrue,
        0x000C: Trace,
        0x000D: Run,
        0x0013: RunSequence,
    }
    
    def frame_header(self, frame: BaltechScriptFrame) -> bytes:
        return frame.Code.to_bytes(length=1, byteorder='big')
    
    @classmethod
    def parse_frames(cls, data: bytes) -> List[BaltechScriptFrame]:
        buffer = BytesIO(data)
        frames: List[BaltechScriptFrame] = []
        while True:
            code_byte = buffer.read(1)
            if not code_byte:
                break
            else:
                code = int.from_bytes(code_byte, byteorder="big")
                frame_class = cls.CodeMap.get(code)
                if frame_class is None:
                    raise InvalidPayloadError(f'Invalid BaltechScript code 0x{code:04X}')
                frames.append(frame_class.read_from(buffer))
                
        return frames
    def Enable(self, EnabledIoPort: IoPort) -> Self:
        """
        Sets an IoPort to high permanently.
        
        See also [Disable](.#BaltechScript.Disable), [Toggle](.#BaltechScript.Toggle)
        or [ToggleInverted](.#BaltechScript.ToggleInverted).
        """
        self.frames.append(Enable(EnabledIoPort=EnabledIoPort))
        return self
    def Disable(self, DisabledIoPort: IoPort) -> Self:
        """
        Sets an IoPort to low permanently.
        
        See also [Enable](.#BaltechScript.Enable), [Toggle](.#BaltechScript.Toggle) or
        [ToggleInverted](.#BaltechScript.ToggleInverted).
        """
        self.frames.append(Disable(DisabledIoPort=DisabledIoPort))
        return self
    def Toggle(self, ToggledIoPort: IoPort, RepeatCount: int, Delay: int) -> Self:
        """
        Set _IoPort_ to high, wait Delay/10 seconds, set _IoPort_ to low and wait
        Delay/10 seconds again. Repeat this _RepeatCount_ times.
        
        See also [Enable](.#BaltechScript.Enable), [Disable](.#BaltechScript.Disable)
        or [ToggleInverted](.#BaltechScript.ToggleInverted).
        """
        self.frames.append(Toggle(ToggledIoPort=ToggledIoPort, RepeatCount=RepeatCount, Delay=Delay))
        return self
    def ToggleInverted(self, InvertedToggledIoPort: IoPort, RepeatCount: int, Delay: int) -> Self:
        """
        Set _IoPort_ to low, wait Delay/10 seconds. Then set _IoPort_ to high and wait
        Delay/10 seconds again. Repeat this _RepeatCount_ times. This is exactly the
        inverse behaviour of [Toggle](.#BaltechScript.Toggle) and is mainly used to
        ensure that the IoPort is set to high after finishing toggling.
        
        See also [Enable](.#BaltechScript.Enable), [Disable](.#BaltechScript.Disable)
        or [Toggle](.#BaltechScript.Toggle).
        """
        self.frames.append(ToggleInverted(InvertedToggledIoPort=InvertedToggledIoPort, RepeatCount=RepeatCount, Delay=Delay))
        return self
    def DefaultAction(self, ) -> Self:
        """
        Most events have a "default action", i.e. the action that the firmware
        performs by default. If you configure a custom action, it will replace the
        default action. To perform the default action _in addition_ to your custom
        action, you need to run the _DefaultAction_ command.
        
        To find out the default action for each event, please see the [event
        value](autoread.xml#Scripts.Events) descriptions.
        """
        self.frames.append(DefaultAction())
        return self
    def SendCardMsg(self, ) -> Self:
        """
        **Deprecated! Use[ SendMsg](.#BaltechScript.SendMsg) instead.**
        """
        self.frames.append(SendCardMsg())
        return self
    def SendMsg(self, MsgType: MessageType, MsgId: int, Protocol: ProtocolID) -> Self:
        """
        Sends the message which is stored in [Scripts / StaticMessages /
        SendMsg](autoread.xml#Scripts.StaticMessages.SendMsg) with Value ID _MsgId_ to
        the host(s). The message is handled like an event of kind _MsgType_.
        
        **The _MsgId_ parameter starts counting from 3. I.e., to send
        SendMsg[2],_MsgId_ has to be 5.**
        
        If _Protocol_ is 0, the message is sent to _all_ active protocols. Furthermore
        it will be transformed by the corresponding PostConvertTemplates.
        
        If _Protocol_ is a protocol id, the message will be sent to this protocol only
        and _no_ (PostConvertTemplate-) conversion will be initiated.
        """
        self.frames.append(SendMsg(MsgType=MsgType, MsgId=MsgId, Protocol=Protocol))
        return self
    def SetTimer(self, TimerId: int, TimerValue: int) -> Self:
        """
        Activate/deactivate one of the three Timers. _TimerId_ is the ID of the timer
        to setup. The reader will wait _TimerValue_ / 10 seconds before starting the
        corresponding [timer event](autoread.xml#Scripts.Events.OnTimer).
        
        If _TimerValue_ is 0, the timer will be deactivated. This means that the timer
        event will never be started.
        """
        self.frames.append(SetTimer(TimerId=TimerId, TimerValue=TimerValue))
        return self
    def SetVar(self, VarId: int) -> Self:
        """
        Set the global variable _VarId_ to True. _VarId_ has to be between 0 and 15.
        """
        self.frames.append(SetVar(VarId=VarId))
        return self
    def ClearVar(self, VarId: int) -> Self:
        """
        Set the global variable _VarId_ to False. _VarId_ has to be between 0 and 15.
        """
        self.frames.append(ClearVar(VarId=VarId))
        return self
    def AssignVar(self, VarId: int) -> Self:
        """
        Set the global variable _VarId_ to the top of the condition stack. _VarId_ has
        to be between 0 and 15. The top of the condition stack will be removed after
        assignment.
        
        **Unlike all other commands, this command is executed in dependency of the
        second topmost flag on the condition stack, since the topmost flag is needed
        for the assignment.**
        """
        self.frames.append(AssignVar(VarId=VarId))
        return self
    def IfIoPort(self, CheckedIoPort: IoPort) -> Self:
        """
        Check if the input I/O-port _IoPort_ is currently high. If so, _true_ will be
        pushed into the top of the condition stack. Otherwise, _false_ will be pushed.
        """
        self.frames.append(IfIoPort(CheckedIoPort=CheckedIoPort))
        return self
    def IfVar(self, VarId: int) -> Self:
        """
        Push the state of global variable _VarId_ onto the top of the condition stack.
        """
        self.frames.append(IfVar(VarId=VarId))
        return self
    def IfProtocolEnabled(self, Protocol: ProtocolID) -> Self:
        """
        Check if _Protocol_ is currently active. If this is the case, True is pushed
        into the top of the condition stack. Otherwise False is pushed into the top of
        the condition stack.
        """
        self.frames.append(IfProtocolEnabled(Protocol=Protocol))
        return self
    def IfDip(self, DipId: int) -> Self:
        """
        Reads the state of the dip switch _DipId_ and pushes it into the top of the
        condition stack.
        """
        self.frames.append(IfDip(DipId=DipId))
        return self
    def IfState(self, StateId: int) -> Self:
        """
        Pushes _StateId_ , onto the top of the Condition Stack. _StateId_ is firmware-
        dependent if it is a number between 0 and 7. If _StateId_ is between 8 and 15,
        this command is identical to [IfVar](.#BaltechScript.IfVar).
        """
        self.frames.append(IfState(StateId=StateId))
        return self
    def Not(self, ) -> Self:
        """
        Inverts the top of the condition stack.
        
        **This command can also be used as ELSE-replacement: "IfVar 1 / Enable
        GreenLed / Not / Enable RedLed"**
        """
        self.frames.append(Not())
        return self
    def Or(self, ) -> Self:
        """
        Merges the two topmost flags on the condition stack into a single one by OR-
        ing them.
        """
        self.frames.append(Or())
        return self
    def And(self, ) -> Self:
        """
        Merges the two topmost flags on the condition stack into a single one by AND-
        ing them.
        """
        self.frames.append(And())
        return self
    def IfTrue(self, ) -> Self:
        """
        Pushes _true_ onto the top of the condition stack.
        """
        self.frames.append(IfTrue())
        return self
    def Trace(self, LogCode: int) -> Self:
        """
        This command can be used for debugging purposes. It outputs _LogCode_ as a
        2-digit hex code on the debug interface.
        """
        self.frames.append(Trace(LogCode=LogCode))
        return self
    def Run(self, EventId: int) -> Self:
        """
        Can be used to stop the execution of the currently running script and continue
        with another script. The _ScriptId_ is the target Value ID within the [Scripts
        / Events](autoread.xml#Scripts.Events) Key.
        """
        self.frames.append(Run(EventId=EventId))
        return self
    def RunSequence(self, Cmds: List[RunSequenceCmd]) -> Self:
        """
        This command allows to run complex switch sequences for IO-Ports. A switch
        sequence can be one or multiple (nested) loops (with separate timing each)
        that are controlling one or multiple different LEDs.
        
        A sample for a switch sequence is:
        
          1. toggle green LED 3 times with 10 Hz frequency
          2. enable red LED for 2 sec
          3. repeat from step 1 four times.
        
        **Currently it is not possible to run more than one switch sequence at the
        same time.**
        
        **All parameters of switch sequences (=frequencies, LED ids and repeat count)
        are static.**
        """
        self.frames.append(RunSequence(Cmds=Cmds))
        return self