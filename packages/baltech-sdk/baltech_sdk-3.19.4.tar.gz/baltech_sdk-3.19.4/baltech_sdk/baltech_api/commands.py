
import abc
from io import BytesIO
from typing import Optional, NamedTuple, Union, Literal, TypedDict, Dict, List, ClassVar, Type as _Type

from typing_extensions import Self, NotRequired

from .common import safe_read_int_from_buffer, LiteralParser, FrameExecutor, BaltechApiError, PayloadTooLongError, PayloadTooShortError, InvalidPayloadError
from .typedefs import *
from .baltech_script import BaltechScript
from .template import Template
class AR_GetMessage_Result(NamedTuple):
    MsgType: 'MessageType'
    MsgData: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'MsgType={ repr(self.MsgType) }')
        non_default_args.append(f'MsgData={ repr(self.MsgData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class BlePeriph_GetEvents_Result(NamedTuple):
    ConnectionStatusChanged: 'bool'
    ValueChangedCharacteristicNdx4: 'bool'
    ValueChangedCharacteristicNdx3: 'bool'
    ValueChangedCharacteristicNdx2: 'bool'
    ValueChangedCharacteristicNdx1: 'bool'
    ValueChangedCharacteristicNdx0: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ConnectionStatusChanged={ repr(self.ConnectionStatusChanged) }')
        non_default_args.append(f'ValueChangedCharacteristicNdx4={ repr(self.ValueChangedCharacteristicNdx4) }')
        non_default_args.append(f'ValueChangedCharacteristicNdx3={ repr(self.ValueChangedCharacteristicNdx3) }')
        non_default_args.append(f'ValueChangedCharacteristicNdx2={ repr(self.ValueChangedCharacteristicNdx2) }')
        non_default_args.append(f'ValueChangedCharacteristicNdx1={ repr(self.ValueChangedCharacteristicNdx1) }')
        non_default_args.append(f'ValueChangedCharacteristicNdx0={ repr(self.ValueChangedCharacteristicNdx0) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class BlePeriph_IsConnected_Result(NamedTuple):
    Address: 'bytes'
    AddressType: 'BlePeriph_IsConnected_AddressType'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Address={ repr(self.Address) }')
        non_default_args.append(f'AddressType={ repr(self.AddressType) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Crypto_EncryptBuffer_Result(NamedTuple):
    NextInitialVector: 'bytes'
    EncryptedBuffer: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'NextInitialVector={ repr(self.NextInitialVector) }')
        non_default_args.append(f'EncryptedBuffer={ repr(self.EncryptedBuffer) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Crypto_DecryptBuffer_Result(NamedTuple):
    NextInitialVector: 'bytes'
    UnencryptedBuffer: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'NextInitialVector={ repr(self.NextInitialVector) }')
        non_default_args.append(f'UnencryptedBuffer={ repr(self.UnencryptedBuffer) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Crypto_BalKeyEncryptBuffer_Result(NamedTuple):
    EncryptedBuffer: 'bytes'
    NextInitialVector: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'EncryptedBuffer={ repr(self.EncryptedBuffer) }')
        non_default_args.append(f'NextInitialVector={ repr(self.NextInitialVector) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Desfire_VirtualCardSelect_Result(NamedTuple):
    FciType: 'int'
    Fci: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FciType={ repr(self.FciType) }')
        non_default_args.append(f'Fci={ repr(self.Fci) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Eth_GetNetworkStatus_Result(NamedTuple):
    PortStatus: 'int'
    StaticIPAdr: 'bytes'
    StaticIPNetmask: 'bytes'
    StaticIPGateway: 'bytes'
    DHCPAdr: 'bytes'
    DHCPNetmask: 'bytes'
    DHCPGateway: 'bytes'
    LinkLocalAdr: 'bytes'
    LinkLocalNetmask: 'bytes'
    LinkLocalGateway: 'bytes'
    DNSAdr: 'bytes'
    HostAdr: 'bytes'
    HostPort: 'int'
    AutocloseTimeout: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'PortStatus={ repr(self.PortStatus) }')
        non_default_args.append(f'StaticIPAdr={ repr(self.StaticIPAdr) }')
        non_default_args.append(f'StaticIPNetmask={ repr(self.StaticIPNetmask) }')
        non_default_args.append(f'StaticIPGateway={ repr(self.StaticIPGateway) }')
        non_default_args.append(f'DHCPAdr={ repr(self.DHCPAdr) }')
        non_default_args.append(f'DHCPNetmask={ repr(self.DHCPNetmask) }')
        non_default_args.append(f'DHCPGateway={ repr(self.DHCPGateway) }')
        non_default_args.append(f'LinkLocalAdr={ repr(self.LinkLocalAdr) }')
        non_default_args.append(f'LinkLocalNetmask={ repr(self.LinkLocalNetmask) }')
        non_default_args.append(f'LinkLocalGateway={ repr(self.LinkLocalGateway) }')
        non_default_args.append(f'DNSAdr={ repr(self.DNSAdr) }')
        non_default_args.append(f'HostAdr={ repr(self.HostAdr) }')
        non_default_args.append(f'HostPort={ repr(self.HostPort) }')
        non_default_args.append(f'AutocloseTimeout={ repr(self.AutocloseTimeout) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Felica_Request_Result(NamedTuple):
    ColFlag: 'int'
    Labels: 'List[bytes]'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ColFlag={ repr(self.ColFlag) }')
        non_default_args.append(f'Labels={ repr(self.Labels) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class FlashFS_GetMemoryInfo_Result(NamedTuple):
    TotalMem: 'int'
    FreeMem: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'TotalMem={ repr(self.TotalMem) }')
        non_default_args.append(f'FreeMem={ repr(self.FreeMem) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class HID_PyramidRead_Result(NamedTuple):
    Len: 'int'
    Data: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'Data={ repr(self.Data) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso14a_RequestLegacy_Result(NamedTuple):
    UIDSize: 'Iso14a_RequestLegacy_UIDSize'
    Coll: 'int'
    ProprietaryCoding: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'UIDSize={ repr(self.UIDSize) }')
        non_default_args.append(f'Coll={ repr(self.Coll) }')
        non_default_args.append(f'ProprietaryCoding={ repr(self.ProprietaryCoding) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso14a_Select_Result(NamedTuple):
    SAK: 'int'
    Serial: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SAK={ repr(self.SAK) }')
        non_default_args.append(f'Serial={ repr(self.Serial) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso14a_Request_Result(NamedTuple):
    ATQA: 'bytes'
    Collision: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ATQA={ repr(self.ATQA) }')
        non_default_args.append(f'Collision={ repr(self.Collision) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso14a_RequestVasup_Result(NamedTuple):
    ATQA: 'bytes'
    Collision: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ATQA={ repr(self.ATQA) }')
        non_default_args.append(f'Collision={ repr(self.Collision) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso14a_TransparentCmdBitlen_Result(NamedTuple):
    RecvDataLen: 'int'
    CollisionPosition: 'int'
    RecvData: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'RecvDataLen={ repr(self.RecvDataLen) }')
        non_default_args.append(f'CollisionPosition={ repr(self.CollisionPosition) }')
        non_default_args.append(f'RecvData={ repr(self.RecvData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso14b_Attrib_Result(NamedTuple):
    AssignedCID: 'Optional[int]' = None
    MBLI: 'Optional[int]' = None
    HLR: 'Optional[bytes]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.AssignedCID != None:
            non_default_args.append(f'AssignedCID={ repr(self.AssignedCID) }')
        if self.MBLI != None:
            non_default_args.append(f'MBLI={ repr(self.MBLI) }')
        if self.HLR != None:
            non_default_args.append(f'HLR={ repr(self.HLR) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_GetParam_Result(NamedTuple):
    ModulationIndex: 'int'
    TXMode: 'int'
    HighDataRate: 'int'
    DualSubcarrier: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ModulationIndex={ repr(self.ModulationIndex) }')
        non_default_args.append(f'TXMode={ repr(self.TXMode) }')
        non_default_args.append(f'HighDataRate={ repr(self.HighDataRate) }')
        non_default_args.append(f'DualSubcarrier={ repr(self.DualSubcarrier) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_GetUIDList_Result(NamedTuple):
    More: 'int'
    Labels: 'List[Iso15_GetUIDList_Labels_Entry]'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'More={ repr(self.More) }')
        non_default_args.append(f'Labels={ repr(self.Labels) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_ReadBlock_Result(NamedTuple):
    LabelStat: 'int'
    BlockLen: 'Optional[int]' = None
    Data: 'Optional[List[Iso15_ReadBlock_Data_Entry]]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LabelStat={ repr(self.LabelStat) }')
        if self.BlockLen != None:
            non_default_args.append(f'BlockLen={ repr(self.BlockLen) }')
        if self.Data != None:
            non_default_args.append(f'Data={ repr(self.Data) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_GetSystemInformation_Result(NamedTuple):
    LabelStat: 'int'
    EnICRef: 'Optional[bool]' = None
    EnMemSize: 'Optional[bool]' = None
    EnAFI: 'Optional[bool]' = None
    EnDSFID: 'Optional[bool]' = None
    SNR: 'Optional[bytes]' = None
    DSFID: 'Optional[int]' = None
    AFI: 'Optional[int]' = None
    BlockNum: 'Optional[int]' = None
    BlockSize: 'Optional[int]' = None
    ICRef: 'Optional[int]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LabelStat={ repr(self.LabelStat) }')
        if self.EnICRef != None:
            non_default_args.append(f'EnICRef={ repr(self.EnICRef) }')
        if self.EnMemSize != None:
            non_default_args.append(f'EnMemSize={ repr(self.EnMemSize) }')
        if self.EnAFI != None:
            non_default_args.append(f'EnAFI={ repr(self.EnAFI) }')
        if self.EnDSFID != None:
            non_default_args.append(f'EnDSFID={ repr(self.EnDSFID) }')
        if self.SNR != None:
            non_default_args.append(f'SNR={ repr(self.SNR) }')
        if self.DSFID != None:
            non_default_args.append(f'DSFID={ repr(self.DSFID) }')
        if self.AFI != None:
            non_default_args.append(f'AFI={ repr(self.AFI) }')
        if self.BlockNum != None:
            non_default_args.append(f'BlockNum={ repr(self.BlockNum) }')
        if self.BlockSize != None:
            non_default_args.append(f'BlockSize={ repr(self.BlockSize) }')
        if self.ICRef != None:
            non_default_args.append(f'ICRef={ repr(self.ICRef) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_GetSecurityStatus_Result(NamedTuple):
    LabelStat: 'int'
    BlockStat: 'List[int]'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LabelStat={ repr(self.LabelStat) }')
        non_default_args.append(f'BlockStat={ repr(self.BlockStat) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_CustomCommand_Result(NamedTuple):
    LabelStat: 'int'
    ResponseData: 'Optional[bytes]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LabelStat={ repr(self.LabelStat) }')
        if self.ResponseData != None:
            non_default_args.append(f'ResponseData={ repr(self.ResponseData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_ReadSingleBlock_Result(NamedTuple):
    LabelStat: 'int'
    Payload: 'Optional[bytes]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LabelStat={ repr(self.LabelStat) }')
        if self.Payload != None:
            non_default_args.append(f'Payload={ repr(self.Payload) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso15_ReadMultipleBlocks_Result(NamedTuple):
    LabelStat: 'int'
    RecvBlocks: 'List[bytes]'
    BlocksSecData: 'List[int]'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LabelStat={ repr(self.LabelStat) }')
        non_default_args.append(f'RecvBlocks={ repr(self.RecvBlocks) }')
        non_default_args.append(f'BlocksSecData={ repr(self.BlocksSecData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Iso78_OpenSam_Result(NamedTuple):
    SamHandle: 'int'
    ATR: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SamHandle={ repr(self.SamHandle) }')
        non_default_args.append(f'ATR={ repr(self.ATR) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Legic_TransparentCommand4000_Result(NamedTuple):
    Status: 'int'
    Resp: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Status={ repr(self.Status) }')
        non_default_args.append(f'Resp={ repr(self.Resp) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Legic_TransparentCommand6000_Result(NamedTuple):
    Status: 'int'
    Resp: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Status={ repr(self.Status) }')
        non_default_args.append(f'Resp={ repr(self.Resp) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Lg_Select_Result(NamedTuple):
    MediaType: 'Lg_Select_MediaType'
    FuncLevel: 'int'
    OrgLevel: 'int'
    EvStat: 'Lg_Select_EvStat'
    ActSegID: 'int'
    ActAdr: 'int'
    Data: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'MediaType={ repr(self.MediaType) }')
        non_default_args.append(f'FuncLevel={ repr(self.FuncLevel) }')
        non_default_args.append(f'OrgLevel={ repr(self.OrgLevel) }')
        non_default_args.append(f'EvStat={ repr(self.EvStat) }')
        non_default_args.append(f'ActSegID={ repr(self.ActSegID) }')
        non_default_args.append(f'ActAdr={ repr(self.ActAdr) }')
        non_default_args.append(f'Data={ repr(self.Data) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Lg_GenSetRead_Result(NamedTuple):
    GenSetNum: 'int'
    Stamp: 'bytes'
    StampLen: 'int'
    WriteExLen: 'int'
    WriteExShad: 'bool'
    WriteExMode: 'Lg_GenSetRead_WriteExMode'
    WriteExStart: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'GenSetNum={ repr(self.GenSetNum) }')
        non_default_args.append(f'Stamp={ repr(self.Stamp) }')
        non_default_args.append(f'StampLen={ repr(self.StampLen) }')
        non_default_args.append(f'WriteExLen={ repr(self.WriteExLen) }')
        non_default_args.append(f'WriteExShad={ repr(self.WriteExShad) }')
        non_default_args.append(f'WriteExMode={ repr(self.WriteExMode) }')
        non_default_args.append(f'WriteExStart={ repr(self.WriteExStart) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Lg_ReadMIM_Result(NamedTuple):
    DataAdr: 'int'
    Data: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DataAdr={ repr(self.DataAdr) }')
        non_default_args.append(f'Data={ repr(self.Data) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Lg_ReadMIMCRC_Result(NamedTuple):
    DataAdr: 'int'
    Data: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DataAdr={ repr(self.DataAdr) }')
        non_default_args.append(f'Data={ repr(self.Data) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Lg_ReadSMStatus_Result(NamedTuple):
    RFU: 'bytes'
    SWV: 'int'
    SmStat: 'int'
    HfPow: 'int'
    NoMIM: 'bool'
    MIMVersion: 'Lg_ReadSMStatus_MIMVersion'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'RFU={ repr(self.RFU) }')
        non_default_args.append(f'SWV={ repr(self.SWV) }')
        non_default_args.append(f'SmStat={ repr(self.SmStat) }')
        non_default_args.append(f'HfPow={ repr(self.HfPow) }')
        non_default_args.append(f'NoMIM={ repr(self.NoMIM) }')
        non_default_args.append(f'MIMVersion={ repr(self.MIMVersion) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Lga_TransparentCommand_Result(NamedTuple):
    Status: 'int'
    Resp: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Status={ repr(self.Status) }')
        non_default_args.append(f'Resp={ repr(self.Resp) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Main_Bf2Upload_Result(NamedTuple):
    ResultCode: 'Main_Bf2Upload_ResultCode'
    InvertedResultCode: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ResultCode={ repr(self.ResultCode) }')
        non_default_args.append(f'InvertedResultCode={ repr(self.InvertedResultCode) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Main_Bf3UploadStart_Result(NamedTuple):
    ReqDataAdr: 'int'
    ReqDataLen: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ReqDataAdr={ repr(self.ReqDataAdr) }')
        non_default_args.append(f'ReqDataLen={ repr(self.ReqDataLen) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Main_Bf3UploadContinue_Result(NamedTuple):
    Reconnect: 'bool'
    Continue: 'bool'
    ReqDataAdr: 'int'
    ReqDataLen: 'int'
    ContainsEstimation: 'bool'
    ContainsReconnectRetryTimeout: 'bool'
    ReconnectRetryTimeout: 'Optional[int]' = None
    EstimatedNumberOfBytes: 'Optional[int]' = None
    EstimatedTimeOverhead: 'Optional[int]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Reconnect={ repr(self.Reconnect) }')
        non_default_args.append(f'Continue={ repr(self.Continue) }')
        non_default_args.append(f'ReqDataAdr={ repr(self.ReqDataAdr) }')
        non_default_args.append(f'ReqDataLen={ repr(self.ReqDataLen) }')
        non_default_args.append(f'ContainsEstimation={ repr(self.ContainsEstimation) }')
        non_default_args.append(f'ContainsReconnectRetryTimeout={ repr(self.ContainsReconnectRetryTimeout) }')
        if self.ReconnectRetryTimeout != None:
            non_default_args.append(f'ReconnectRetryTimeout={ repr(self.ReconnectRetryTimeout) }')
        if self.EstimatedNumberOfBytes != None:
            non_default_args.append(f'EstimatedNumberOfBytes={ repr(self.EstimatedNumberOfBytes) }')
        if self.EstimatedTimeOverhead != None:
            non_default_args.append(f'EstimatedTimeOverhead={ repr(self.EstimatedTimeOverhead) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Mif_VirtualCardSelect_Result(NamedTuple):
    FciType: 'int'
    Fci: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FciType={ repr(self.FciType) }')
        non_default_args.append(f'Fci={ repr(self.Fci) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Pki_Tunnel2_Result(NamedTuple):
    RspHMAC: 'bytes'
    EncryptedRsp: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'RspHMAC={ repr(self.RspHMAC) }')
        non_default_args.append(f'EncryptedRsp={ repr(self.EncryptedRsp) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sec_AuthPhase1_Result(NamedTuple):
    EncRndA: 'bytes'
    RndB: 'bytes'
    ContinuousIV: 'bool'
    Encrypted: 'bool'
    MACed: 'bool'
    SessionKey: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'EncRndA={ repr(self.EncRndA) }')
        non_default_args.append(f'RndB={ repr(self.RndB) }')
        non_default_args.append(f'ContinuousIV={ repr(self.ContinuousIV) }')
        non_default_args.append(f'Encrypted={ repr(self.Encrypted) }')
        non_default_args.append(f'MACed={ repr(self.MACed) }')
        non_default_args.append(f'SessionKey={ repr(self.SessionKey) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_GetBufferSize_Result(NamedTuple):
    MaxSendSize: 'int'
    MaxRecvSize: 'int'
    TotalSize: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'MaxSendSize={ repr(self.MaxSendSize) }')
        non_default_args.append(f'MaxRecvSize={ repr(self.MaxRecvSize) }')
        non_default_args.append(f'TotalSize={ repr(self.TotalSize) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_CfgCheck_Result(NamedTuple):
    TotalSize: 'int'
    FreeSize: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'TotalSize={ repr(self.TotalSize) }')
        non_default_args.append(f'FreeSize={ repr(self.FreeSize) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_GetPlatformId_Result(NamedTuple):
    PlatformId: 'bytes'
    BootloaderId: 'int'
    BootloaderMajor: 'int'
    BootloaderMinor: 'int'
    BootloaderBuild: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'PlatformId={ repr(self.PlatformId) }')
        non_default_args.append(f'BootloaderId={ repr(self.BootloaderId) }')
        non_default_args.append(f'BootloaderMajor={ repr(self.BootloaderMajor) }')
        non_default_args.append(f'BootloaderMinor={ repr(self.BootloaderMinor) }')
        non_default_args.append(f'BootloaderBuild={ repr(self.BootloaderBuild) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_CfgGetId_Result(NamedTuple):
    ConfigId: 'str'
    ConfigName: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ConfigId={ repr(self.ConfigId) }')
        non_default_args.append(f'ConfigName={ repr(self.ConfigName) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_CfgGetDeviceSettingsId_Result(NamedTuple):
    ConfigId: 'str'
    ConfigName: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ConfigId={ repr(self.ConfigId) }')
        non_default_args.append(f'ConfigName={ repr(self.ConfigName) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_GetFeatures_Result(NamedTuple):
    FeatureList: 'List[FeatureID]'
    MaxFeatureID: 'FeatureID'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FeatureList={ repr(self.FeatureList) }')
        non_default_args.append(f'MaxFeatureID={ repr(self.MaxFeatureID) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_GetPartNumber_Result(NamedTuple):
    PartNo: 'str'
    HwRevNo: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'PartNo={ repr(self.PartNo) }')
        non_default_args.append(f'HwRevNo={ repr(self.HwRevNo) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class EpcUid_UidReplyRound_Result(NamedTuple):
    MemStatusFlag: 'int'
    LabelNr: 'int'
    LabelLength: 'int'
    LabelData: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'MemStatusFlag={ repr(self.MemStatusFlag) }')
        non_default_args.append(f'LabelNr={ repr(self.LabelNr) }')
        non_default_args.append(f'LabelLength={ repr(self.LabelLength) }')
        non_default_args.append(f'LabelData={ repr(self.LabelData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class EpcUid_EpcInventory_Result(NamedTuple):
    MemStatusFlag: 'int'
    LabelNr: 'int'
    LabelData: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'MemStatusFlag={ repr(self.MemStatusFlag) }')
        non_default_args.append(f'LabelNr={ repr(self.LabelNr) }')
        non_default_args.append(f'LabelData={ repr(self.LabelData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class UlRdr_SendAuth1_Result(NamedTuple):
    SendDevCode: 'int'
    SendCmdCode: 'int'
    SendParams: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SendDevCode={ repr(self.SendDevCode) }')
        non_default_args.append(f'SendCmdCode={ repr(self.SendCmdCode) }')
        non_default_args.append(f'SendParams={ repr(self.SendParams) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class UlRdr_SendAuth2_Result(NamedTuple):
    SendDevCode: 'int'
    SendCmdCode: 'int'
    SendParams: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SendDevCode={ repr(self.SendDevCode) }')
        non_default_args.append(f'SendCmdCode={ repr(self.SendCmdCode) }')
        non_default_args.append(f'SendParams={ repr(self.SendParams) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class UlRdr_SendEncryptedCmd_Result(NamedTuple):
    SendDevCode: 'int'
    SendCmdCode: 'int'
    SendParams: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SendDevCode={ repr(self.SendDevCode) }')
        non_default_args.append(f'SendCmdCode={ repr(self.SendCmdCode) }')
        non_default_args.append(f'SendParams={ repr(self.SendParams) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VHL_ExchangeLongAPDU_Result(NamedTuple):
    ContinueResp: 'bool'
    Resp: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ContinueResp={ repr(self.ContinueResp) }')
        non_default_args.append(f'Resp={ repr(self.Resp) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VHL_GetFileInfo_Result(NamedTuple):
    Len: 'int'
    BlockSize: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Len={ repr(self.Len) }')
        non_default_args.append(f'BlockSize={ repr(self.BlockSize) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class DHWCtrl_DataflashGetSize_Result(NamedTuple):
    PageCount: 'int'
    PageSize: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'PageCount={ repr(self.PageCount) }')
        non_default_args.append(f'PageSize={ repr(self.PageSize) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class DHWCtrl_Run_Result(NamedTuple):
    Status: 'int'
    Response: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Status={ repr(self.Status) }')
        non_default_args.append(f'Response={ repr(self.Response) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class DHWCtrl_GetStartupRun_Result(NamedTuple):
    Status: 'int'
    Response: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Status={ repr(self.Status) }')
        non_default_args.append(f'Response={ repr(self.Response) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LT_ReadWord_Result(NamedTuple):
    DataLo: 'int'
    DataHi: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DataLo={ repr(self.DataLo) }')
        non_default_args.append(f'DataHi={ repr(self.DataHi) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LT_Test_Result(NamedTuple):
    Teststatus: 'int'
    Snr: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Teststatus={ repr(self.Teststatus) }')
        non_default_args.append(f'Snr={ repr(self.Snr) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LT_GetBootStatus_Result(NamedTuple):
    BootStatusLo: 'int'
    BootStatusHi: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'BootStatusLo={ repr(self.BootStatusLo) }')
        non_default_args.append(f'BootStatusHi={ repr(self.BootStatusHi) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LT_TransparentCmd_Result(NamedTuple):
    ReturnLenLo: 'int'
    ReturnLenHi: 'int'
    ColPos: 'int'
    ReturnData: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ReturnLenLo={ repr(self.ReturnLenLo) }')
        non_default_args.append(f'ReturnLenHi={ repr(self.ReturnLenHi) }')
        non_default_args.append(f'ColPos={ repr(self.ColPos) }')
        non_default_args.append(f'ReturnData={ repr(self.ReturnData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LT_ReadWordExtended_Result(NamedTuple):
    DataLo: 'int'
    DataHi: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DataLo={ repr(self.DataLo) }')
        non_default_args.append(f'DataHi={ repr(self.DataHi) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Command:
    def __init__(self, executor: FrameExecutor) -> None:
        self.executor = executor
    def execute(self, frame: bytes) -> bytes:
        return self.executor.execute(frame)
class ASK_SecuraKeyRead(Command):
    CommandGroupId = 0x36
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x36\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class ASK_GproxRead(Command):
    CommandGroupId = 0x36
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x36\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class ASK_CotagRead(Command):
    CommandGroupId = 0x36
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x36\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class AR_SetMode(Command):
    CommandGroupId = 0x05
    CommandId = 0x00
    def build_frame(self, Mode: AutoReadMode, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x05\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AutoReadMode_Parser.as_value(Mode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: AutoReadMode, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class AR_GetMessage(Command):
    CommandGroupId = 0x05
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x05\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> AR_GetMessage_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MsgType = MessageType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _MsgData_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _MsgData = _recv_buffer.read(_MsgData_len)
        if len(_MsgData) != _MsgData_len:
            raise PayloadTooShortError(_MsgData_len - len(_MsgData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return AR_GetMessage_Result(_MsgType, _MsgData)
class AR_RunScript(Command):
    CommandGroupId = 0x05
    CommandId = 0x03
    def build_frame(self, Script: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x05\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Script)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Script)
        return _send_buffer.getvalue()
    def __call__(self, Script: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Script=Script, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class AR_RestrictScanCardFamilies(Command):
    CommandGroupId = 0x05
    CommandId = 0x04
    def build_frame(self, CardFamiliesFilter: Union[CardFamilies, CardFamilies_Dict] = CardFamilies.All(), BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x05\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if isinstance(CardFamiliesFilter, dict):
            CardFamiliesFilter = CardFamilies(**CardFamiliesFilter)
        CardFamiliesFilter_int = 0
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.LEGICPrime) & 0b1) << 11
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.BluetoothMce) & 0b1) << 10
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Khz125Part2) & 0b1) << 9
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Srix) & 0b1) << 8
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Khz125Part1) & 0b1) << 7
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Felica) & 0b1) << 6
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.IClass) & 0b1) << 5
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.IClassIso14B) & 0b1) << 4
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Iso14443B) & 0b1) << 3
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Iso15693) & 0b1) << 2
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Iso14443A) & 0b1) << 0
        _send_buffer.write(CardFamiliesFilter_int.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CardFamiliesFilter: Union[CardFamilies, CardFamilies_Dict] = CardFamilies.All(), BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CardFamiliesFilter=CardFamiliesFilter, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Bat_Run(Command):
    CommandGroupId = 0x46
    CommandId = 0x00
    def build_frame(self, SubCmds: List[Bat_Run_SubCmds_Entry], BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x46\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SubCmds)).to_bytes(1, byteorder='big'))
        for _SubCmds_Entry in SubCmds:
            _ConditionBits, _DevCode, _CmdCode, _Params = _SubCmds_Entry
            _send_buffer.write(_ConditionBits.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(_DevCode.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_CmdCode.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(int(len(_Params)).to_bytes(2, byteorder='big'))
            _send_buffer.write(_Params)
        return _send_buffer.getvalue()
    def __call__(self, SubCmds: List[Bat_Run_SubCmds_Entry], BrpTimeout: int = 1000) -> List[Bat_Run_Rsps_Entry]:
        request_frame = self.build_frame(SubCmds=SubCmds, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Rsps_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Rsps = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_Rsps) >= _Rsps_len:
            _Status = safe_read_int_from_buffer(_recv_buffer, 1)
            _Resp_len = safe_read_int_from_buffer(_recv_buffer, 2)
            _Resp = _recv_buffer.read(_Resp_len)
            if len(_Resp) != _Resp_len:
                raise PayloadTooShortError(_Resp_len - len(_Resp))
            _Rsps_Entry = Bat_Run_Rsps_Entry(_Status, _Resp)
            _Rsps.append(_Rsps_Entry)
        if len(_Rsps) != _Rsps_len:
            raise PayloadTooShortError(_Rsps_len - len(_Rsps))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Rsps
class Bat_CheckStatus(Command):
    CommandGroupId = 0x46
    CommandId = 0x10
    def build_frame(self, CondBitNdx: int, StatusCodes: List[int], Invert: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x46\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CondBitNdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(StatusCodes)).to_bytes(1, byteorder='big'))
        for _StatusCodes_Entry in StatusCodes:
            _StatusCode = _StatusCodes_Entry
            _send_buffer.write(_StatusCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Invert.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CondBitNdx: int, StatusCodes: List[int], Invert: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CondBitNdx=CondBitNdx, StatusCodes=StatusCodes, Invert=Invert, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Bat_CheckAny(Command):
    CommandGroupId = 0x46
    CommandId = 0x11
    def build_frame(self, CondBitNdx: int, CondBits: int, Invert: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x46\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CondBitNdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CondBits.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Invert.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CondBitNdx: int, CondBits: int, Invert: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CondBitNdx=CondBitNdx, CondBits=CondBits, Invert=Invert, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Bat_CheckTemplate(Command):
    CommandGroupId = 0x46
    CommandId = 0x12
    def build_frame(self, CondBitNdx: int, Template: bytes, FieldBitLens: List[int], Invert: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x46\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CondBitNdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Template)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Template)
        _send_buffer.write(int(len(FieldBitLens)).to_bytes(1, byteorder='big'))
        for _FieldBitLens_Entry in FieldBitLens:
            _FieldLen = _FieldBitLens_Entry
            _send_buffer.write(_FieldLen.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Invert.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CondBitNdx: int, Template: bytes, FieldBitLens: List[int], Invert: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CondBitNdx=CondBitNdx, Template=Template, FieldBitLens=FieldBitLens, Invert=Invert, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Bat_Delay(Command):
    CommandGroupId = 0x46
    CommandId = 0x20
    def build_frame(self, DelayTime: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x46\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DelayTime.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DelayTime: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(DelayTime=DelayTime, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class BlePeriph_DefineService(Command):
    CommandGroupId = 0x4B
    CommandId = 0x01
    def build_frame(self, ServiceUUID: bytes, Characteristics: List[BlePeriph_DefineService_Characteristics_Entry], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(b'\x00')
        _send_buffer.write(int(len(ServiceUUID)).to_bytes(1, byteorder='big'))
        _send_buffer.write(ServiceUUID)
        _send_buffer.write(int(len(Characteristics)).to_bytes(1, byteorder='big'))
        for _Characteristics_Entry in Characteristics:
            _CharacteristicUUID, _SupportsIndicate, _SupportsNotify, _SupportsWrite, _SupportsWriteNoResponse, _SupportsRead, _VariableSize, _Size = _Characteristics_Entry
            _send_buffer.write(int(len(_CharacteristicUUID)).to_bytes(1, byteorder='big'))
            _send_buffer.write(_CharacteristicUUID)
            _var_0000_int = 0
            _var_0000_int |= (int(_SupportsIndicate) & 0b1) << 5
            _var_0000_int |= (int(_SupportsNotify) & 0b1) << 4
            _var_0000_int |= (int(_SupportsWrite) & 0b1) << 3
            _var_0000_int |= (int(_SupportsWriteNoResponse) & 0b1) << 2
            _var_0000_int |= (int(_SupportsRead) & 0b1) << 1
            _send_buffer.write(_var_0000_int.to_bytes(length=2, byteorder='big'))
            _var_0001_int = 0
            _var_0001_int |= (int(_VariableSize) & 0b1) << 0
            _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_Size.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ServiceUUID: bytes, Characteristics: List[BlePeriph_DefineService_Characteristics_Entry], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ServiceUUID=ServiceUUID, Characteristics=Characteristics, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class BlePeriph_Enable(Command):
    CommandGroupId = 0x4B
    CommandId = 0x02
    def build_frame(self, Activate: bool, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Activate.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Activate: bool, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Activate=Activate, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class BlePeriph_SetAdvertisingData(Command):
    CommandGroupId = 0x4B
    CommandId = 0x03
    def build_frame(self, AdvertisingData: bytes, ScanResponseData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(AdvertisingData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(AdvertisingData)
        _send_buffer.write(int(len(ScanResponseData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(ScanResponseData)
        return _send_buffer.getvalue()
    def __call__(self, AdvertisingData: bytes, ScanResponseData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AdvertisingData=AdvertisingData, ScanResponseData=ScanResponseData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class BlePeriph_WriteCharacteristic(Command):
    CommandGroupId = 0x4B
    CommandId = 0x04
    def build_frame(self, CharacteristicNdx: int, WriteValue: bytes, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CharacteristicNdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(WriteValue)).to_bytes(2, byteorder='big'))
        _send_buffer.write(WriteValue)
        return _send_buffer.getvalue()
    def __call__(self, CharacteristicNdx: int, WriteValue: bytes, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(CharacteristicNdx=CharacteristicNdx, WriteValue=WriteValue, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class BlePeriph_ReadCharacteristic(Command):
    CommandGroupId = 0x4B
    CommandId = 0x05
    def build_frame(self, CharacteristicNdx: int, ReadLength: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CharacteristicNdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ReadLength.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CharacteristicNdx: int, ReadLength: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(CharacteristicNdx=CharacteristicNdx, ReadLength=ReadLength, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadValue_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _ReadValue = _recv_buffer.read(_ReadValue_len)
        if len(_ReadValue) != _ReadValue_len:
            raise PayloadTooShortError(_ReadValue_len - len(_ReadValue))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadValue
class BlePeriph_GetEvents(Command):
    CommandGroupId = 0x4B
    CommandId = 0x06
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> BlePeriph_GetEvents_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EventMask_int = safe_read_int_from_buffer(_recv_buffer, 4)
        _ConnectionStatusChanged = bool((_EventMask_int >> 31) & 0b1)
        _ValueChangedCharacteristicNdx4 = bool((_EventMask_int >> 4) & 0b1)
        _ValueChangedCharacteristicNdx3 = bool((_EventMask_int >> 3) & 0b1)
        _ValueChangedCharacteristicNdx2 = bool((_EventMask_int >> 2) & 0b1)
        _ValueChangedCharacteristicNdx1 = bool((_EventMask_int >> 1) & 0b1)
        _ValueChangedCharacteristicNdx0 = bool((_EventMask_int >> 0) & 0b1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return BlePeriph_GetEvents_Result(_ConnectionStatusChanged, _ValueChangedCharacteristicNdx4, _ValueChangedCharacteristicNdx3, _ValueChangedCharacteristicNdx2, _ValueChangedCharacteristicNdx1, _ValueChangedCharacteristicNdx0)
class BlePeriph_IsConnected(Command):
    CommandGroupId = 0x4B
    CommandId = 0x07
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> BlePeriph_IsConnected_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Address = _recv_buffer.read(6)
        if len(_Address) != 6:
            raise PayloadTooShortError(6 - len(_Address))
        _AddressType = BlePeriph_IsConnected_AddressType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return BlePeriph_IsConnected_Result(_Address, _AddressType)
class BlePeriph_GetRSSI(Command):
    CommandGroupId = 0x4B
    CommandId = 0x08
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _AbsRSSI = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _AbsRSSI
class BlePeriph_CloseConnection(Command):
    CommandGroupId = 0x4B
    CommandId = 0x09
    def build_frame(self, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4B\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class CardEmu_GetMaxFrameSize(Command):
    CommandGroupId = 0x47
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x47\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MaxFrameSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _MaxFrameSize
class CardEmu_StartEmu(Command):
    CommandGroupId = 0x47
    CommandId = 0x01
    def build_frame(self, Snr: bytes, ATQA: int, SAK: int, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x47\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(b'\x00')
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        _send_buffer.write(ATQA.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(SAK.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Snr: bytes, ATQA: int, SAK: int, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        request_frame = self.build_frame(Snr=Snr, ATQA=ATQA, SAK=SAK, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FirstCmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _FirstCmd = _recv_buffer.read(_FirstCmd_len)
        if len(_FirstCmd) != _FirstCmd_len:
            raise PayloadTooShortError(_FirstCmd_len - len(_FirstCmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _FirstCmd
class CardEmu_TransparentCmd(Command):
    CommandGroupId = 0x47
    CommandId = 0x02
    def build_frame(self, Rsp: bytes, Timeout: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x47\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Rsp)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Rsp)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Rsp: bytes, Timeout: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Rsp=Rsp, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Cmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Cmd = _recv_buffer.read(_Cmd_len)
        if len(_Cmd) != _Cmd_len:
            raise PayloadTooShortError(_Cmd_len - len(_Cmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Cmd
class CardEmu_GetExternalHfStatus(Command):
    CommandGroupId = 0x47
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x47\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ExtFieldStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ExtFieldStat
class CardEmu_StartNfc(Command):
    CommandGroupId = 0x47
    CommandId = 0x04
    def build_frame(self, NfcAPassiv: bool = True, *, Snr: bytes, ATQA: int, SAK: int, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x47\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(NfcAPassiv) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        _send_buffer.write(ATQA.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(SAK.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, NfcAPassiv: bool = True, *, Snr: bytes, ATQA: int, SAK: int, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        request_frame = self.build_frame(NfcAPassiv=NfcAPassiv, Snr=Snr, ATQA=ATQA, SAK=SAK, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FirstCmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _FirstCmd = _recv_buffer.read(_FirstCmd_len)
        if len(_FirstCmd) != _FirstCmd_len:
            raise PayloadTooShortError(_FirstCmd_len - len(_FirstCmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _FirstCmd
class Crypto_EncryptBlock(Command):
    CommandGroupId = 0x02
    CommandId = 0x00
    def build_frame(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, Block: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIndex.to_bytes(length=1, byteorder='big'))
        if KeyIndex == 0:
            if KeyValue is None:
                raise TypeError("missing a required argument: 'KeyValue'")
            if len(KeyValue) != 10:
                raise ValueError(KeyValue)
            _send_buffer.write(KeyValue)
        if len(Block) != 8:
            raise ValueError(Block)
        _send_buffer.write(Block)
        return _send_buffer.getvalue()
    def __call__(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, Block: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(KeyIndex=KeyIndex, KeyValue=KeyValue, Block=Block, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EncryptedBlock = _recv_buffer.read(8)
        if len(_EncryptedBlock) != 8:
            raise PayloadTooShortError(8 - len(_EncryptedBlock))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _EncryptedBlock
class Crypto_DecryptBlock(Command):
    CommandGroupId = 0x02
    CommandId = 0x01
    def build_frame(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, Block: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIndex.to_bytes(length=1, byteorder='big'))
        if KeyIndex == 0:
            if KeyValue is None:
                raise TypeError("missing a required argument: 'KeyValue'")
            if len(KeyValue) != 10:
                raise ValueError(KeyValue)
            _send_buffer.write(KeyValue)
        if len(Block) != 8:
            raise ValueError(Block)
        _send_buffer.write(Block)
        return _send_buffer.getvalue()
    def __call__(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, Block: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(KeyIndex=KeyIndex, KeyValue=KeyValue, Block=Block, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _UnencryptedBlock = _recv_buffer.read(8)
        if len(_UnencryptedBlock) != 8:
            raise PayloadTooShortError(8 - len(_UnencryptedBlock))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _UnencryptedBlock
class Crypto_EncryptBuffer(Command):
    CommandGroupId = 0x02
    CommandId = 0x02
    def build_frame(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, InitialVector: bytes, Buffer: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIndex.to_bytes(length=1, byteorder='big'))
        if KeyIndex == 0:
            if KeyValue is None:
                raise TypeError("missing a required argument: 'KeyValue'")
            if len(KeyValue) != 10:
                raise ValueError(KeyValue)
            _send_buffer.write(KeyValue)
        if len(InitialVector) != 8:
            raise ValueError(InitialVector)
        _send_buffer.write(InitialVector)
        _send_buffer.write(int(len(Buffer)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Buffer)
        return _send_buffer.getvalue()
    def __call__(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, InitialVector: bytes, Buffer: bytes, BrpTimeout: int = 100) -> Crypto_EncryptBuffer_Result:
        request_frame = self.build_frame(KeyIndex=KeyIndex, KeyValue=KeyValue, InitialVector=InitialVector, Buffer=Buffer, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _NextInitialVector = _recv_buffer.read(8)
        if len(_NextInitialVector) != 8:
            raise PayloadTooShortError(8 - len(_NextInitialVector))
        _EncryptedBuffer_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _EncryptedBuffer = _recv_buffer.read(_EncryptedBuffer_len)
        if len(_EncryptedBuffer) != _EncryptedBuffer_len:
            raise PayloadTooShortError(_EncryptedBuffer_len - len(_EncryptedBuffer))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Crypto_EncryptBuffer_Result(_NextInitialVector, _EncryptedBuffer)
class Crypto_DecryptBuffer(Command):
    CommandGroupId = 0x02
    CommandId = 0x03
    def build_frame(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, InitialVector: bytes, Buffer: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIndex.to_bytes(length=1, byteorder='big'))
        if KeyIndex == 0:
            if KeyValue is None:
                raise TypeError("missing a required argument: 'KeyValue'")
            if len(KeyValue) != 10:
                raise ValueError(KeyValue)
            _send_buffer.write(KeyValue)
        if len(InitialVector) != 8:
            raise ValueError(InitialVector)
        _send_buffer.write(InitialVector)
        _send_buffer.write(int(len(Buffer)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Buffer)
        return _send_buffer.getvalue()
    def __call__(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, *, InitialVector: bytes, Buffer: bytes, BrpTimeout: int = 100) -> Crypto_DecryptBuffer_Result:
        request_frame = self.build_frame(KeyIndex=KeyIndex, KeyValue=KeyValue, InitialVector=InitialVector, Buffer=Buffer, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _NextInitialVector = _recv_buffer.read(8)
        if len(_NextInitialVector) != 8:
            raise PayloadTooShortError(8 - len(_NextInitialVector))
        _UnencryptedBuffer_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _UnencryptedBuffer = _recv_buffer.read(_UnencryptedBuffer_len)
        if len(_UnencryptedBuffer) != _UnencryptedBuffer_len:
            raise PayloadTooShortError(_UnencryptedBuffer_len - len(_UnencryptedBuffer))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Crypto_DecryptBuffer_Result(_NextInitialVector, _UnencryptedBuffer)
class Crypto_BalKeyEncryptBuffer(Command):
    CommandGroupId = 0x02
    CommandId = 0x04
    def build_frame(self, KeyVersion: int = 2, EmbeddedKeyIndex: int = 0, EmbeddedKeyPos: int = 255, *, Buffer: bytes, InitialVector: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyVersion.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EmbeddedKeyIndex.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EmbeddedKeyPos.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Buffer)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Buffer)
        _send_buffer.write(int(len(InitialVector)).to_bytes(1, byteorder='big'))
        _send_buffer.write(InitialVector)
        return _send_buffer.getvalue()
    def __call__(self, KeyVersion: int = 2, EmbeddedKeyIndex: int = 0, EmbeddedKeyPos: int = 255, *, Buffer: bytes, InitialVector: bytes, BrpTimeout: int = 100) -> Crypto_BalKeyEncryptBuffer_Result:
        request_frame = self.build_frame(KeyVersion=KeyVersion, EmbeddedKeyIndex=EmbeddedKeyIndex, EmbeddedKeyPos=EmbeddedKeyPos, Buffer=Buffer, InitialVector=InitialVector, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EncryptedBuffer_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _EncryptedBuffer = _recv_buffer.read(_EncryptedBuffer_len)
        if len(_EncryptedBuffer) != _EncryptedBuffer_len:
            raise PayloadTooShortError(_EncryptedBuffer_len - len(_EncryptedBuffer))
        _NextInitialVector_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _NextInitialVector = _recv_buffer.read(_NextInitialVector_len)
        if len(_NextInitialVector) != _NextInitialVector_len:
            raise PayloadTooShortError(_NextInitialVector_len - len(_NextInitialVector))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Crypto_BalKeyEncryptBuffer_Result(_EncryptedBuffer, _NextInitialVector)
class Crypto_GetKeySig(Command):
    CommandGroupId = 0x02
    CommandId = 0x10
    def build_frame(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIndex.to_bytes(length=1, byteorder='big'))
        if KeyIndex == 0:
            if KeyValue is None:
                raise TypeError("missing a required argument: 'KeyValue'")
            if len(KeyValue) != 10:
                raise ValueError(KeyValue)
            _send_buffer.write(KeyValue)
        return _send_buffer.getvalue()
    def __call__(self, KeyIndex: int = 0, KeyValue: Optional[bytes] = None, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(KeyIndex=KeyIndex, KeyValue=KeyValue, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _KeySignature = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _KeySignature
class Crypto_CopyConfigKey(Command):
    CommandGroupId = 0x02
    CommandId = 0x11
    def build_frame(self, KeyIndex: int, ForceDefaultKey: bool = False, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x02\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIndex.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ForceDefaultKey.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, KeyIndex: int, ForceDefaultKey: bool = False, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(KeyIndex=KeyIndex, ForceDefaultKey=ForceDefaultKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Dbg_ReadLogs(Command):
    CommandGroupId = 0xF3
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF3\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> str:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LogData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _LogData_bytes = _recv_buffer.read(_LogData_len)
        _LogData = _LogData_bytes.decode('ascii')
        if len(_LogData) != _LogData_len:
            raise PayloadTooShortError(_LogData_len - len(_LogData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LogData
class Dbg_RunCmd(Command):
    CommandGroupId = 0xF3
    CommandId = 0x01
    def build_frame(self, Cmd: str, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF3\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Cmd) != 1:
            raise ValueError(Cmd)
        _send_buffer.write(Cmd.encode("ascii"))
        return _send_buffer.getvalue()
    def __call__(self, Cmd: str, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Cmd=Cmd, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_ExecCommand(Command):
    CommandGroupId = 0x1B
    CommandId = 0x00
    def build_frame(self, Cmd: int, Header: bytes, Param: bytes, CryptoMode: Desfire_ExecCommand_CryptoMode = "Plain", ResponseLen: int = 65535, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Cmd.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Header)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Header)
        _send_buffer.write(int(len(Param)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Param)
        _send_buffer.write(Desfire_ExecCommand_CryptoMode_Parser.as_value(CryptoMode).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ResponseLen.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Cmd: int, Header: bytes, Param: bytes, CryptoMode: Desfire_ExecCommand_CryptoMode = "Plain", ResponseLen: int = 65535, BrpTimeout: int = 2000) -> bytes:
        request_frame = self.build_frame(Cmd=Cmd, Header=Header, Param=Param, CryptoMode=CryptoMode, ResponseLen=ResponseLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Resp
class Desfire_Authenticate(Command):
    CommandGroupId = 0x1B
    CommandId = 0x01
    def build_frame(self, SecureMessaging: Desfire_Authenticate_SecureMessaging = "EV1", DesKeynr: int = 0, KeyId: int = 128, KeyHasDivData: bool = False, KeyDivMode: Desfire_Authenticate_KeyDivMode = "NoDiv", KeyHasExtIdx: bool = False, KeyDivData: Optional[bytes] = None, KeyExtIdx: Optional[int] = None, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Desfire_Authenticate_SecureMessaging_Parser.as_value(SecureMessaging).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DesKeynr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(KeyId.to_bytes(length=1, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(KeyHasDivData) & 0b1) << 4
        _var_0000_int |= (Desfire_Authenticate_KeyDivMode_Parser.as_value(KeyDivMode) & 0b111) << 1
        _var_0000_int |= (int(KeyHasExtIdx) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if KeyHasDivData:
            if KeyDivData is None:
                raise TypeError("missing a required argument: 'KeyDivData'")
            _send_buffer.write(int(len(KeyDivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(KeyDivData)
        if KeyHasExtIdx:
            if KeyExtIdx is None:
                raise TypeError("missing a required argument: 'KeyExtIdx'")
            _send_buffer.write(KeyExtIdx.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SecureMessaging: Desfire_Authenticate_SecureMessaging = "EV1", DesKeynr: int = 0, KeyId: int = 128, KeyHasDivData: bool = False, KeyDivMode: Desfire_Authenticate_KeyDivMode = "NoDiv", KeyHasExtIdx: bool = False, KeyDivData: Optional[bytes] = None, KeyExtIdx: Optional[int] = None, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(SecureMessaging=SecureMessaging, DesKeynr=DesKeynr, KeyId=KeyId, KeyHasDivData=KeyHasDivData, KeyDivMode=KeyDivMode, KeyHasExtIdx=KeyHasExtIdx, KeyDivData=KeyDivData, KeyExtIdx=KeyExtIdx, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_AuthExtKey(Command):
    CommandGroupId = 0x1B
    CommandId = 0x02
    def build_frame(self, SecureMessaging: Desfire_AuthExtKey_SecureMessaging = "EV1", DesKeyNr: int = 0, CryptoMode: Desfire_AuthExtKey_CryptoMode = "AES", *, Key: bytes, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Desfire_AuthExtKey_SecureMessaging_Parser.as_value(SecureMessaging).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DesKeyNr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Desfire_AuthExtKey_CryptoMode_Parser.as_value(CryptoMode).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Key)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, SecureMessaging: Desfire_AuthExtKey_SecureMessaging = "EV1", DesKeyNr: int = 0, CryptoMode: Desfire_AuthExtKey_CryptoMode = "AES", *, Key: bytes, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(SecureMessaging=SecureMessaging, DesKeyNr=DesKeyNr, CryptoMode=CryptoMode, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_SelectApplication(Command):
    CommandGroupId = 0x1B
    CommandId = 0x03
    def build_frame(self, AppId: int = 0, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AppId.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AppId: int = 0, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(AppId=AppId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_ReadData(Command):
    CommandGroupId = 0x1B
    CommandId = 0x04
    def build_frame(self, FileId: int, Adr: int = 0, Len: int = 0, Mode: Desfire_ReadData_Mode = "Plain", BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Desfire_ReadData_Mode_Parser.as_value(Mode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, Adr: int = 0, Len: int = 0, Mode: Desfire_ReadData_Mode = "Plain", BrpTimeout: int = 3000) -> bytes:
        request_frame = self.build_frame(FileId=FileId, Adr=Adr, Len=Len, Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class Desfire_WriteData(Command):
    CommandGroupId = 0x1B
    CommandId = 0x05
    def build_frame(self, FileId: int, Adr: int = 0, *, Data: bytes, Mode: Desfire_WriteData_Mode = "Plain", BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        _send_buffer.write(Desfire_WriteData_Mode_Parser.as_value(Mode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, Adr: int = 0, *, Data: bytes, Mode: Desfire_WriteData_Mode = "Plain", BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(FileId=FileId, Adr=Adr, Data=Data, Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_ChangeExtKey(Command):
    CommandGroupId = 0x1B
    CommandId = 0x06
    def build_frame(self, MasterKeyType: Desfire_ChangeExtKey_MasterKeyType = "DESorTripleDES", IsKeySet: bool = False, IsAesKey: bool = False, IsVersion: bool = False, IsChangeKey: bool = True, *, KeyNo: int, KeyVersion: Optional[int] = 0, NewKey: bytes, OldKey: bytes, KeySet: Optional[int] = None, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (Desfire_ChangeExtKey_MasterKeyType_Parser.as_value(MasterKeyType) & 0b11) << 6
        _var_0000_int |= (int(IsKeySet) & 0b1) << 3
        _var_0000_int |= (int(IsAesKey) & 0b1) << 2
        _var_0000_int |= (int(IsVersion) & 0b1) << 1
        _var_0000_int |= (int(IsChangeKey) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(KeyNo.to_bytes(length=1, byteorder='big'))
        if IsVersion:
            if KeyVersion is None:
                raise TypeError("missing a required argument: 'KeyVersion'")
            _send_buffer.write(KeyVersion.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(NewKey)).to_bytes(1, byteorder='big'))
        _send_buffer.write(NewKey)
        _send_buffer.write(int(len(OldKey)).to_bytes(1, byteorder='big'))
        _send_buffer.write(OldKey)
        if IsKeySet:
            if KeySet is None:
                raise TypeError("missing a required argument: 'KeySet'")
            _send_buffer.write(KeySet.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, MasterKeyType: Desfire_ChangeExtKey_MasterKeyType = "DESorTripleDES", IsKeySet: bool = False, IsAesKey: bool = False, IsVersion: bool = False, IsChangeKey: bool = True, *, KeyNo: int, KeyVersion: Optional[int] = 0, NewKey: bytes, OldKey: bytes, KeySet: Optional[int] = None, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(MasterKeyType=MasterKeyType, IsKeySet=IsKeySet, IsAesKey=IsAesKey, IsVersion=IsVersion, IsChangeKey=IsChangeKey, KeyNo=KeyNo, KeyVersion=KeyVersion, NewKey=NewKey, OldKey=OldKey, KeySet=KeySet, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_ChangeKey(Command):
    CommandGroupId = 0x1B
    CommandId = 0x07
    def build_frame(self, IsKeySet: bool = False, IsMasterKey: bool = False, IsChangeKey: bool = False, *, KeyNr: int, NewKeyDivMode: Desfire_ChangeKey_NewKeyDivMode = "SamAv1OneRound", NewKeyHasDivData: bool = False, NewKeyHasExtIdx: bool = False, NewKeyIdx: int, CurKeyDivMode: Desfire_ChangeKey_CurKeyDivMode = "SamAv1OneRound", CurKeyHasDivData: bool = False, CurKeyHasExtIdx: bool = False, CurKeyIdx: int, NewKeyDivData: Optional[bytes] = None, CurKeyDivData: Optional[bytes] = None, NewKeyExtIdx: Optional[int] = None, CurKeyExtIdx: Optional[int] = None, KeySet: Optional[int] = None, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(IsKeySet) & 0b1) << 2
        _var_0000_int |= (int(IsMasterKey) & 0b1) << 1
        _var_0000_int |= (int(IsChangeKey) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(KeyNr.to_bytes(length=1, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (Desfire_ChangeKey_NewKeyDivMode_Parser.as_value(NewKeyDivMode) & 0b11) << 3
        _var_0001_int |= (int(NewKeyHasDivData) & 0b1) << 1
        _var_0001_int |= (int(NewKeyHasExtIdx) & 0b1) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(NewKeyIdx.to_bytes(length=1, byteorder='big'))
        _var_0002_int = 0
        _var_0002_int |= (Desfire_ChangeKey_CurKeyDivMode_Parser.as_value(CurKeyDivMode) & 0b11) << 3
        _var_0002_int |= (int(CurKeyHasDivData) & 0b1) << 1
        _var_0002_int |= (int(CurKeyHasExtIdx) & 0b1) << 0
        _send_buffer.write(_var_0002_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CurKeyIdx.to_bytes(length=1, byteorder='big'))
        if NewKeyHasDivData:
            if NewKeyDivData is None:
                raise TypeError("missing a required argument: 'NewKeyDivData'")
            _send_buffer.write(int(len(NewKeyDivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(NewKeyDivData)
        if CurKeyHasDivData:
            if CurKeyDivData is None:
                raise TypeError("missing a required argument: 'CurKeyDivData'")
            _send_buffer.write(int(len(CurKeyDivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(CurKeyDivData)
        if NewKeyHasExtIdx:
            if NewKeyExtIdx is None:
                raise TypeError("missing a required argument: 'NewKeyExtIdx'")
            _send_buffer.write(NewKeyExtIdx.to_bytes(length=1, byteorder='big'))
        if CurKeyHasExtIdx:
            if CurKeyExtIdx is None:
                raise TypeError("missing a required argument: 'CurKeyExtIdx'")
            _send_buffer.write(CurKeyExtIdx.to_bytes(length=1, byteorder='big'))
        if IsKeySet:
            if KeySet is None:
                raise TypeError("missing a required argument: 'KeySet'")
            _send_buffer.write(KeySet.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, IsKeySet: bool = False, IsMasterKey: bool = False, IsChangeKey: bool = False, *, KeyNr: int, NewKeyDivMode: Desfire_ChangeKey_NewKeyDivMode = "SamAv1OneRound", NewKeyHasDivData: bool = False, NewKeyHasExtIdx: bool = False, NewKeyIdx: int, CurKeyDivMode: Desfire_ChangeKey_CurKeyDivMode = "SamAv1OneRound", CurKeyHasDivData: bool = False, CurKeyHasExtIdx: bool = False, CurKeyIdx: int, NewKeyDivData: Optional[bytes] = None, CurKeyDivData: Optional[bytes] = None, NewKeyExtIdx: Optional[int] = None, CurKeyExtIdx: Optional[int] = None, KeySet: Optional[int] = None, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(IsKeySet=IsKeySet, IsMasterKey=IsMasterKey, IsChangeKey=IsChangeKey, KeyNr=KeyNr, NewKeyDivMode=NewKeyDivMode, NewKeyHasDivData=NewKeyHasDivData, NewKeyHasExtIdx=NewKeyHasExtIdx, NewKeyIdx=NewKeyIdx, CurKeyDivMode=CurKeyDivMode, CurKeyHasDivData=CurKeyHasDivData, CurKeyHasExtIdx=CurKeyHasExtIdx, CurKeyIdx=CurKeyIdx, NewKeyDivData=NewKeyDivData, CurKeyDivData=CurKeyDivData, NewKeyExtIdx=NewKeyExtIdx, CurKeyExtIdx=CurKeyExtIdx, KeySet=KeySet, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_SetFraming(Command):
    CommandGroupId = 0x1B
    CommandId = 0x10
    def build_frame(self, CommMode: Desfire_SetFraming_CommMode = "DESFireNative", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Desfire_SetFraming_CommMode_Parser.as_value(CommMode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CommMode: Desfire_SetFraming_CommMode = "DESFireNative", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CommMode=CommMode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_ResetAuthentication(Command):
    CommandGroupId = 0x1B
    CommandId = 0x11
    def build_frame(self, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_CreateDam(Command):
    CommandGroupId = 0x1B
    CommandId = 0x08
    def build_frame(self, AppId: int = 0, *, AppParams: bytes, EncryptedDefaultDamKey: bytes, DamMacKey: bytes, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AppId.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(int(len(AppParams)).to_bytes(1, byteorder='big'))
        _send_buffer.write(AppParams)
        _send_buffer.write(int(len(EncryptedDefaultDamKey)).to_bytes(1, byteorder='big'))
        _send_buffer.write(EncryptedDefaultDamKey)
        _send_buffer.write(int(len(DamMacKey)).to_bytes(1, byteorder='big'))
        _send_buffer.write(DamMacKey)
        return _send_buffer.getvalue()
    def __call__(self, AppId: int = 0, *, AppParams: bytes, EncryptedDefaultDamKey: bytes, DamMacKey: bytes, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(AppId=AppId, AppParams=AppParams, EncryptedDefaultDamKey=EncryptedDefaultDamKey, DamMacKey=DamMacKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_GetOriginalitySignature(Command):
    CommandGroupId = 0x1B
    CommandId = 0x0A
    def build_frame(self, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 2000) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Signature_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Signature = _recv_buffer.read(_Signature_len)
        if len(_Signature) != _Signature_len:
            raise PayloadTooShortError(_Signature_len - len(_Signature))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Signature
class Desfire_VirtualCardSelect(Command):
    CommandGroupId = 0x1B
    CommandId = 0x0B
    def build_frame(self, ForceVcsAuthentication: bool = False, UseExtVcSelectKeys: bool = False, DiversifyMacKey: int = 0, DiversifyEncKey: bool = False, UseVcSelectKeys: bool = False, *, IID: bytes, EncKeyIdx: Optional[int] = None, MacKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, EncKey: Optional[bytes] = None, MacKey: Optional[bytes] = None, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x0B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ForceVcsAuthentication) & 0b1) << 5
        _var_0000_int |= (int(UseExtVcSelectKeys) & 0b1) << 4
        _var_0000_int |= (DiversifyMacKey & 0b11) << 2
        _var_0000_int |= (int(DiversifyEncKey) & 0b1) << 1
        _var_0000_int |= (int(UseVcSelectKeys) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(IID)).to_bytes(1, byteorder='big'))
        _send_buffer.write(IID)
        if UseVcSelectKeys:
            if EncKeyIdx is None:
                raise TypeError("missing a required argument: 'EncKeyIdx'")
            if MacKeyIdx is None:
                raise TypeError("missing a required argument: 'MacKeyIdx'")
            _send_buffer.write(EncKeyIdx.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(MacKeyIdx.to_bytes(length=2, byteorder='big'))
        if DiversifyMacKey == 1 or DiversifyMacKey == 2 or DiversifyMacKey == 3 or DiversifyEncKey:
            if DivData is None:
                raise TypeError("missing a required argument: 'DivData'")
            _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(DivData)
        if UseExtVcSelectKeys:
            if EncKey is None:
                raise TypeError("missing a required argument: 'EncKey'")
            if MacKey is None:
                raise TypeError("missing a required argument: 'MacKey'")
            _send_buffer.write(int(len(EncKey)).to_bytes(1, byteorder='big'))
            _send_buffer.write(EncKey)
            _send_buffer.write(int(len(MacKey)).to_bytes(1, byteorder='big'))
            _send_buffer.write(MacKey)
        return _send_buffer.getvalue()
    def __call__(self, ForceVcsAuthentication: bool = False, UseExtVcSelectKeys: bool = False, DiversifyMacKey: int = 0, DiversifyEncKey: bool = False, UseVcSelectKeys: bool = False, *, IID: bytes, EncKeyIdx: Optional[int] = None, MacKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, EncKey: Optional[bytes] = None, MacKey: Optional[bytes] = None, BrpTimeout: int = 2000) -> Desfire_VirtualCardSelect_Result:
        request_frame = self.build_frame(ForceVcsAuthentication=ForceVcsAuthentication, UseExtVcSelectKeys=UseExtVcSelectKeys, DiversifyMacKey=DiversifyMacKey, DiversifyEncKey=DiversifyEncKey, UseVcSelectKeys=UseVcSelectKeys, IID=IID, EncKeyIdx=EncKeyIdx, MacKeyIdx=MacKeyIdx, DivData=DivData, EncKey=EncKey, MacKey=MacKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FciType = safe_read_int_from_buffer(_recv_buffer, 1)
        _Fci_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Fci = _recv_buffer.read(_Fci_len)
        if len(_Fci) != _Fci_len:
            raise PayloadTooShortError(_Fci_len - len(_Fci))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Desfire_VirtualCardSelect_Result(_FciType, _Fci)
class Desfire_ProxCheck(Command):
    CommandGroupId = 0x1B
    CommandId = 0x0C
    def build_frame(self, M: int = 4, UseExtProxKey: bool = False, DiversifyProxKey: bool = False, UseProxKey: bool = False, ProxKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, ProxKey: Optional[bytes] = None, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x0C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (M & 0b111) << 4
        _var_0000_int |= (int(UseExtProxKey) & 0b1) << 2
        _var_0000_int |= (int(DiversifyProxKey) & 0b1) << 1
        _var_0000_int |= (int(UseProxKey) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if UseProxKey:
            if ProxKeyIdx is None:
                raise TypeError("missing a required argument: 'ProxKeyIdx'")
            _send_buffer.write(ProxKeyIdx.to_bytes(length=2, byteorder='big'))
        if DiversifyProxKey and UseProxKey:
            if DivData is None:
                raise TypeError("missing a required argument: 'DivData'")
            _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(DivData)
        if UseExtProxKey:
            if ProxKey is None:
                raise TypeError("missing a required argument: 'ProxKey'")
            _send_buffer.write(int(len(ProxKey)).to_bytes(1, byteorder='big'))
            _send_buffer.write(ProxKey)
        return _send_buffer.getvalue()
    def __call__(self, M: int = 4, UseExtProxKey: bool = False, DiversifyProxKey: bool = False, UseProxKey: bool = False, ProxKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, ProxKey: Optional[bytes] = None, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(M=M, UseExtProxKey=UseExtProxKey, DiversifyProxKey=DiversifyProxKey, UseProxKey=UseProxKey, ProxKeyIdx=ProxKeyIdx, DivData=DivData, ProxKey=ProxKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Desfire_GetDfNames(Command):
    CommandGroupId = 0x1B
    CommandId = 0x0D
    def build_frame(self, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1B\x0D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 3000) -> List[Desfire_GetDfNames_AppNr_Entry]:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _AppNr_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _AppNr = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_AppNr) >= _AppNr_len:
            _AppId = safe_read_int_from_buffer(_recv_buffer, 4)
            _IsoFileId = safe_read_int_from_buffer(_recv_buffer, 2)
            _IsoDfName_len = safe_read_int_from_buffer(_recv_buffer, 1)
            _IsoDfName = _recv_buffer.read(_IsoDfName_len)
            if len(_IsoDfName) != _IsoDfName_len:
                raise PayloadTooShortError(_IsoDfName_len - len(_IsoDfName))
            _AppNr_Entry = Desfire_GetDfNames_AppNr_Entry(_AppId, _IsoFileId, _IsoDfName)
            _AppNr.append(_AppNr_Entry)
        if len(_AppNr) != _AppNr_len:
            raise PayloadTooShortError(_AppNr_len - len(_AppNr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _AppNr
class Disp_Enable(Command):
    CommandGroupId = 0x41
    CommandId = 0x00
    def build_frame(self, Enable: bool, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x41\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Disp_SetContrast(Command):
    CommandGroupId = 0x41
    CommandId = 0x01
    def build_frame(self, Contrast: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x41\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Contrast.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Contrast: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Contrast=Contrast, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Disp_EnableBacklight(Command):
    CommandGroupId = 0x41
    CommandId = 0x02
    def build_frame(self, EnableLight: bool, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x41\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(EnableLight.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, EnableLight: bool, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(EnableLight=EnableLight, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Disp_Clear(Command):
    CommandGroupId = 0x41
    CommandId = 0x10
    def build_frame(self, DelPermanentDefines: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x41\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DelPermanentDefines.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DelPermanentDefines: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(DelPermanentDefines=DelPermanentDefines, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Disp_Load(Command):
    CommandGroupId = 0x41
    CommandId = 0x11
    def build_frame(self, PageDesc: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x41\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PageDesc)
        return _send_buffer.getvalue()
    def __call__(self, PageDesc: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PageDesc=PageDesc, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Disp_Extend(Command):
    CommandGroupId = 0x41
    CommandId = 0x12
    def build_frame(self, PageDesc: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x41\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PageDesc)
        return _send_buffer.getvalue()
    def __call__(self, PageDesc: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PageDesc=PageDesc, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_DecodeCfg(Command):
    CommandGroupId = 0x31
    CommandId = 0x00
    def build_frame(self, RxMod: EM_DecodeCfg_RxMod = "Unknown", RxBaud: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(EM_DecodeCfg_RxMod_Parser.as_value(RxMod).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(RxBaud.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, RxMod: EM_DecodeCfg_RxMod = "Unknown", RxBaud: int = 0, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(RxMod=RxMod, RxBaud=RxBaud, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Read4100(Command):
    CommandGroupId = 0x31
    CommandId = 0x08
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class EM_Read4205(Command):
    CommandGroupId = 0x31
    CommandId = 0x10
    def build_frame(self, Address: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(Address=Address, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Page = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Page
class EM_Write4205(Command):
    CommandGroupId = 0x31
    CommandId = 0x11
    def build_frame(self, Address: int, Page: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Page.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, Page: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Address=Address, Page=Page, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Halt4205(Command):
    CommandGroupId = 0x31
    CommandId = 0x12
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Login4205(Command):
    CommandGroupId = 0x31
    CommandId = 0x13
    def build_frame(self, Password: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x13")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Password.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Password: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Password=Password, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Protect4205(Command):
    CommandGroupId = 0x31
    CommandId = 0x14
    def build_frame(self, ProtectMask: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x14")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ProtectMask.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ProtectMask: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ProtectMask=ProtectMask, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Read4469(Command):
    CommandGroupId = 0x31
    CommandId = 0x18
    def build_frame(self, Address: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x18")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(Address=Address, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Page = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Page
class EM_Write4469(Command):
    CommandGroupId = 0x31
    CommandId = 0x19
    def build_frame(self, Address: int, Page: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x19")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Page.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, Page: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Address=Address, Page=Page, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Halt4469(Command):
    CommandGroupId = 0x31
    CommandId = 0x1A
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x1A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Login4469(Command):
    CommandGroupId = 0x31
    CommandId = 0x1B
    def build_frame(self, Password: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x1B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Password.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Password: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Password=Password, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EM_Read4450(Command):
    CommandGroupId = 0x31
    CommandId = 0x20
    def build_frame(self, StartAdr: int, EndAdr: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x31\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EndAdr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, StartAdr: int, EndAdr: int, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(StartAdr=StartAdr, EndAdr=EndAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PageNr_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _PageNr = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_PageNr) >= _PageNr_len:
            _Page = safe_read_int_from_buffer(_recv_buffer, 4)
            _PageNr.append(_Page)
        if len(_PageNr) != _PageNr_len:
            raise PayloadTooShortError(_PageNr_len - len(_PageNr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PageNr
class Eth_GetMacAdr(Command):
    CommandGroupId = 0x45
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MAC = _recv_buffer.read(6)
        if len(_MAC) != 6:
            raise PayloadTooShortError(6 - len(_MAC))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _MAC
class Eth_GetConnDevIP(Command):
    CommandGroupId = 0x45
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _IP = _recv_buffer.read(4)
        if len(_IP) != 4:
            raise PayloadTooShortError(4 - len(_IP))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _IP
class Eth_CreateRecoveryPoint(Command):
    CommandGroupId = 0x45
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Eth_DelRecoveryPoint(Command):
    CommandGroupId = 0x45
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Eth_GetNetworkStatus(Command):
    CommandGroupId = 0x45
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Eth_GetNetworkStatus_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PortStatus = safe_read_int_from_buffer(_recv_buffer, 1)
        _StaticIPAdr = _recv_buffer.read(4)
        if len(_StaticIPAdr) != 4:
            raise PayloadTooShortError(4 - len(_StaticIPAdr))
        _StaticIPNetmask = _recv_buffer.read(4)
        if len(_StaticIPNetmask) != 4:
            raise PayloadTooShortError(4 - len(_StaticIPNetmask))
        _StaticIPGateway = _recv_buffer.read(4)
        if len(_StaticIPGateway) != 4:
            raise PayloadTooShortError(4 - len(_StaticIPGateway))
        _DHCPAdr = _recv_buffer.read(4)
        if len(_DHCPAdr) != 4:
            raise PayloadTooShortError(4 - len(_DHCPAdr))
        _DHCPNetmask = _recv_buffer.read(4)
        if len(_DHCPNetmask) != 4:
            raise PayloadTooShortError(4 - len(_DHCPNetmask))
        _DHCPGateway = _recv_buffer.read(4)
        if len(_DHCPGateway) != 4:
            raise PayloadTooShortError(4 - len(_DHCPGateway))
        _LinkLocalAdr = _recv_buffer.read(4)
        if len(_LinkLocalAdr) != 4:
            raise PayloadTooShortError(4 - len(_LinkLocalAdr))
        _LinkLocalNetmask = _recv_buffer.read(4)
        if len(_LinkLocalNetmask) != 4:
            raise PayloadTooShortError(4 - len(_LinkLocalNetmask))
        _LinkLocalGateway = _recv_buffer.read(4)
        if len(_LinkLocalGateway) != 4:
            raise PayloadTooShortError(4 - len(_LinkLocalGateway))
        _DNSAdr = _recv_buffer.read(4)
        if len(_DNSAdr) != 4:
            raise PayloadTooShortError(4 - len(_DNSAdr))
        _HostAdr = _recv_buffer.read(4)
        if len(_HostAdr) != 4:
            raise PayloadTooShortError(4 - len(_HostAdr))
        _HostPort = safe_read_int_from_buffer(_recv_buffer, 2)
        _AutocloseTimeout = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Eth_GetNetworkStatus_Result(_PortStatus, _StaticIPAdr, _StaticIPNetmask, _StaticIPGateway, _DHCPAdr, _DHCPNetmask, _DHCPGateway, _LinkLocalAdr, _LinkLocalNetmask, _LinkLocalGateway, _DNSAdr, _HostAdr, _HostPort, _AutocloseTimeout)
class Eth_GetMIBCounters(Command):
    CommandGroupId = 0x45
    CommandId = 0x05
    def build_frame(self, Port: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(Port=Port, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MIBCounterList_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _MIBCounterList = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_MIBCounterList) >= _MIBCounterList_len:
            _Value = safe_read_int_from_buffer(_recv_buffer, 4)
            _MIBCounterList.append(_Value)
        if len(_MIBCounterList) != _MIBCounterList_len:
            raise PayloadTooShortError(_MIBCounterList_len - len(_MIBCounterList))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _MIBCounterList
class Eth_GetTcpConnectionStatus(Command):
    CommandGroupId = 0x45
    CommandId = 0x06
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Eth_GetTcpConnectionStatus_Status:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = Eth_GetTcpConnectionStatus_Status_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Status
class Eth_OpenTcpConnection(Command):
    CommandGroupId = 0x45
    CommandId = 0x07
    def build_frame(self, ConnectionReason: Eth_OpenTcpConnection_ConnectionReason, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Eth_OpenTcpConnection_ConnectionReason_Parser.as_value(ConnectionReason).to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ConnectionReason: Eth_OpenTcpConnection_ConnectionReason, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ConnectionReason=ConnectionReason, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Eth_CloseTcpConnection(Command):
    CommandGroupId = 0x45
    CommandId = 0x08
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x45\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Felica_GenericCmd(Command):
    CommandGroupId = 0x1C
    CommandId = 0x02
    def build_frame(self, FastBaud: Felica_GenericCmd_FastBaud = "Kbps424", *, Cmd: int, Param: bytes, Timeout: int = 20, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1C\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Felica_GenericCmd_FastBaud_Parser.as_value(FastBaud).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Cmd.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Param)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Param)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FastBaud: Felica_GenericCmd_FastBaud = "Kbps424", *, Cmd: int, Param: bytes, Timeout: int = 20, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(FastBaud=FastBaud, Cmd=Cmd, Param=Param, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Resp
class Felica_SetUID2(Command):
    CommandGroupId = 0x1C
    CommandId = 0x01
    def build_frame(self, UID2: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1C\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(UID2) != 8:
            raise ValueError(UID2)
        _send_buffer.write(UID2)
        return _send_buffer.getvalue()
    def __call__(self, UID2: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(UID2=UID2, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Felica_Request(Command):
    CommandGroupId = 0x1C
    CommandId = 0x00
    def build_frame(self, FastBaud: Felica_Request_FastBaud = "Kbps212", SystemCode: int = 65535, RequestCode: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1C\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Felica_Request_FastBaud_Parser.as_value(FastBaud).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SystemCode.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(RequestCode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FastBaud: Felica_Request_FastBaud = "Kbps212", SystemCode: int = 65535, RequestCode: int = 0, BrpTimeout: int = 100) -> Felica_Request_Result:
        request_frame = self.build_frame(FastBaud=FastBaud, SystemCode=SystemCode, RequestCode=RequestCode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ColFlag = safe_read_int_from_buffer(_recv_buffer, 1)
        _Labels_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Labels = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_Labels) >= _Labels_len:
            _NFCID_len = safe_read_int_from_buffer(_recv_buffer, 1)
            _NFCID = _recv_buffer.read(_NFCID_len)
            if len(_NFCID) != _NFCID_len:
                raise PayloadTooShortError(_NFCID_len - len(_NFCID))
            _Labels.append(_NFCID)
        if len(_Labels) != _Labels_len:
            raise PayloadTooShortError(_Labels_len - len(_Labels))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Felica_Request_Result(_ColFlag, _Labels)
class FlashFS_GetMemoryInfo(Command):
    CommandGroupId = 0x49
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> FlashFS_GetMemoryInfo_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _TotalMem = safe_read_int_from_buffer(_recv_buffer, 4)
        _FreeMem = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return FlashFS_GetMemoryInfo_Result(_TotalMem, _FreeMem)
class FlashFS_Format(Command):
    CommandGroupId = 0x49
    CommandId = 0x02
    def build_frame(self, QuickFormat: bool, BrpTimeout: int = 5000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(QuickFormat.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, QuickFormat: bool, BrpTimeout: int = 5000) -> None:
        request_frame = self.build_frame(QuickFormat=QuickFormat, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class FlashFS_CreateFile(Command):
    CommandGroupId = 0x49
    CommandId = 0x03
    def build_frame(self, FileId: int, RecordSize: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(RecordSize.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, RecordSize: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FileId=FileId, RecordSize=RecordSize, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class FlashFS_DeleteFile(Command):
    CommandGroupId = 0x49
    CommandId = 0x04
    def build_frame(self, FileId: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FileId=FileId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class FlashFS_RenameFile(Command):
    CommandGroupId = 0x49
    CommandId = 0x05
    def build_frame(self, FileId: int, NewFileId: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(NewFileId.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, NewFileId: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FileId=FileId, NewFileId=NewFileId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class FlashFS_GetRecordSize(Command):
    CommandGroupId = 0x49
    CommandId = 0x06
    def build_frame(self, FileId: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(FileId=FileId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecordSize = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecordSize
class FlashFS_GetFileSize(Command):
    CommandGroupId = 0x49
    CommandId = 0x07
    def build_frame(self, FileId: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(FileId=FileId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FileSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _FileSize
class FlashFS_ReadRecords(Command):
    CommandGroupId = 0x49
    CommandId = 0x08
    def build_frame(self, FileId: int, StartRecord: int, RecordCount: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(StartRecord.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(RecordCount.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, StartRecord: int, RecordCount: int, BrpTimeout: int = 100) -> List[bytes]:
        request_frame = self.build_frame(FileId=FileId, StartRecord=StartRecord, RecordCount=RecordCount, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecordList_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecordList = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_RecordList) >= _RecordList_len:
            _Record_len = safe_read_int_from_buffer(_recv_buffer, 1)
            _Record = _recv_buffer.read(_Record_len)
            if len(_Record) != _Record_len:
                raise PayloadTooShortError(_Record_len - len(_Record))
            _RecordList.append(_Record)
        if len(_RecordList) != _RecordList_len:
            raise PayloadTooShortError(_RecordList_len - len(_RecordList))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecordList
class FlashFS_WriteRecords(Command):
    CommandGroupId = 0x49
    CommandId = 0x09
    def build_frame(self, FileId: int, StartRecord: int, RecordList: List[bytes], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x49\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileId.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(StartRecord.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(RecordList)).to_bytes(2, byteorder='big'))
        for _RecordList_Entry in RecordList:
            _Record = _RecordList_Entry
            _send_buffer.write(int(len(_Record)).to_bytes(1, byteorder='big'))
            _send_buffer.write(_Record)
        return _send_buffer.getvalue()
    def __call__(self, FileId: int, StartRecord: int, RecordList: List[bytes], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FileId=FileId, StartRecord=StartRecord, RecordList=RecordList, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Ftob_OpenReadFile(Command):
    CommandGroupId = 0x03
    CommandId = 0x00
    def build_frame(self, Filename: bytes, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x03\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Filename)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Filename)
        return _send_buffer.getvalue()
    def __call__(self, Filename: bytes, BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(Filename=Filename, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Ftob_OpenWriteFile(Command):
    CommandGroupId = 0x03
    CommandId = 0x01
    def build_frame(self, Filename: bytes, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x03\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Filename)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Filename)
        return _send_buffer.getvalue()
    def __call__(self, Filename: bytes, BrpTimeout: int = 3000) -> int:
        request_frame = self.build_frame(Filename=Filename, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MaxBlockLen = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _MaxBlockLen
class Ftob_ReadFileBlock(Command):
    CommandGroupId = 0x03
    CommandId = 0x02
    def build_frame(self, ToggleBit: bool, MaxBlockLength: int = 128, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x03\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ToggleBit.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(MaxBlockLength.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ToggleBit: bool, MaxBlockLength: int = 128, BrpTimeout: int = 3000) -> bytes:
        request_frame = self.build_frame(ToggleBit=ToggleBit, MaxBlockLength=MaxBlockLength, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BlockData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _BlockData = _recv_buffer.read(_BlockData_len)
        if len(_BlockData) != _BlockData_len:
            raise PayloadTooShortError(_BlockData_len - len(_BlockData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _BlockData
class Ftob_WriteFileBlock(Command):
    CommandGroupId = 0x03
    CommandId = 0x03
    def build_frame(self, ToggleBit: bool, BlockData: bytes, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x03\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ToggleBit.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(BlockData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(BlockData)
        return _send_buffer.getvalue()
    def __call__(self, ToggleBit: bool, BlockData: bytes, BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(ToggleBit=ToggleBit, BlockData=BlockData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Ftob_CloseFile(Command):
    CommandGroupId = 0x03
    CommandId = 0x04
    def build_frame(self, Success: bool = True, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x03\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Success.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Success: bool = True, BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(Success=Success, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class HID_IndalaRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class HID_ProxRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class HID_AwidRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class HID_IoProxRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class HID_Prox32Read(Command):
    CommandGroupId = 0x33
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class HID_PyramidRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x05
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> HID_PyramidRead_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return HID_PyramidRead_Result(_Len, _Data)
class HID_IndalaSecureRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x06
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class HID_IdteckRead(Command):
    CommandGroupId = 0x33
    CommandId = 0x07
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x33\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class Hitag_Request(Command):
    CommandGroupId = 0x30
    CommandId = 0x00
    def build_frame(self, TagType: Hitag_Request_TagType = "HitagS", Mode: Hitag_Request_Mode = "StdHtg12S", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x30\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Hitag_Request_TagType_Parser.as_value(TagType).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Hitag_Request_Mode_Parser.as_value(Mode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, TagType: Hitag_Request_TagType = "HitagS", Mode: Hitag_Request_Mode = "StdHtg12S", BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(TagType=TagType, Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Snr = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Snr
class Hitag_Select(Command):
    CommandGroupId = 0x30
    CommandId = 0x01
    def build_frame(self, SelMode: Hitag_Select_SelMode = "Select", Pwd: Optional[int] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x30\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Hitag_Select_SelMode_Parser.as_value(SelMode).to_bytes(length=1, byteorder='big'))
        if SelMode == "H2AuthOnlyPwd":
            if Pwd is None:
                raise TypeError("missing a required argument: 'Pwd'")
            _send_buffer.write(Pwd.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SelMode: Hitag_Select_SelMode = "Select", Pwd: Optional[int] = None, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(SelMode=SelMode, Pwd=Pwd, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Page1 = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Page1
class Hitag_Halt(Command):
    CommandGroupId = 0x30
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x30\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Hitag_Read(Command):
    CommandGroupId = 0x30
    CommandId = 0x03
    def build_frame(self, Address: int, InvRead: bool = False, KeyB: bool = False, Encrypt: bool = False, BlockRead: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x30\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(InvRead) & 0b1) << 3
        _var_0000_int |= (int(KeyB) & 0b1) << 2
        _var_0000_int |= (int(Encrypt) & 0b1) << 1
        _var_0000_int |= (int(BlockRead) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, InvRead: bool = False, KeyB: bool = False, Encrypt: bool = False, BlockRead: bool = False, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(Address=Address, InvRead=InvRead, KeyB=KeyB, Encrypt=Encrypt, BlockRead=BlockRead, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PageNr_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _PageNr = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_PageNr) >= _PageNr_len:
            _Page = safe_read_int_from_buffer(_recv_buffer, 4)
            _PageNr.append(_Page)
        if len(_PageNr) != _PageNr_len:
            raise PayloadTooShortError(_PageNr_len - len(_PageNr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PageNr
class Hitag_Write(Command):
    CommandGroupId = 0x30
    CommandId = 0x04
    def build_frame(self, Address: int, KeyB: bool = False, Encrypt: bool = False, BlockWrite: bool = False, *, PageNr: List[int], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x30\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(KeyB) & 0b1) << 2
        _var_0000_int |= (int(Encrypt) & 0b1) << 1
        _var_0000_int |= (int(BlockWrite) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(PageNr)).to_bytes(1, byteorder='big'))
        for _PageNr_Entry in PageNr:
            _Page = _PageNr_Entry
            _send_buffer.write(_Page.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, KeyB: bool = False, Encrypt: bool = False, BlockWrite: bool = False, *, PageNr: List[int], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Address=Address, KeyB=KeyB, Encrypt=Encrypt, BlockWrite=BlockWrite, PageNr=PageNr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Hitag_PersonaliseHtg(Command):
    CommandGroupId = 0x30
    CommandId = 0x10
    def build_frame(self, Reset: bool = False, HtgS: bool = False, *, Len: List[int], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x30\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(Reset) & 0b1) << 1
        _var_0000_int |= (int(HtgS) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Len)).to_bytes(1, byteorder='big'))
        for _Len_Entry in Len:
            _Data = _Len_Entry
            _send_buffer.write(_Data.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Reset: bool = False, HtgS: bool = False, *, Len: List[int], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Reset=Reset, HtgS=HtgS, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class I2c_SetSpeed(Command):
    CommandGroupId = 0x08
    CommandId = 0x01
    def build_frame(self, FastMode: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x08\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FastMode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FastMode: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FastMode=FastMode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class I2c_Read(Command):
    CommandGroupId = 0x08
    CommandId = 0x02
    def build_frame(self, Address: int, ReadLen: int = 5, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x08\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ReadLen.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, ReadLen: int = 5, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Address=Address, ReadLen=ReadLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadData_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ReadData = _recv_buffer.read(_ReadData_len)
        if len(_ReadData) != _ReadData_len:
            raise PayloadTooShortError(_ReadData_len - len(_ReadData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadData
class I2c_Write(Command):
    CommandGroupId = 0x08
    CommandId = 0x03
    def build_frame(self, Address: int, WriteData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x08\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(WriteData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(WriteData)
        return _send_buffer.getvalue()
    def __call__(self, Address: int, WriteData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Address=Address, WriteData=WriteData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class I2c_TxRx(Command):
    CommandGroupId = 0x08
    CommandId = 0x04
    def build_frame(self, Address: int, CmdData: bytes, ReadLen: int = 5, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x08\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(CmdData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(CmdData)
        _send_buffer.write(ReadLen.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int, CmdData: bytes, ReadLen: int = 5, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Address=Address, CmdData=CmdData, ReadLen=ReadLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadData_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ReadData = _recv_buffer.read(_ReadData_len)
        if len(_ReadData) != _ReadData_len:
            raise PayloadTooShortError(_ReadData_len - len(_ReadData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadData
class Iso14a_RequestLegacy(Command):
    CommandGroupId = 0x13
    CommandId = 0x02
    def build_frame(self, ReqAll: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ReqAll) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ReqAll: bool = False, BrpTimeout: int = 100) -> Iso14a_RequestLegacy_Result:
        request_frame = self.build_frame(ReqAll=ReqAll, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATQA_int = safe_read_int_from_buffer(_recv_buffer, 2)
        _UIDSize = Iso14a_RequestLegacy_UIDSize_Parser.as_literal((_ATQA_int >> 14) & 0b11)
        _Coll = (_ATQA_int >> 8) & 0b11111
        _ProprietaryCoding = (_ATQA_int >> 0) & 0b1111
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso14a_RequestLegacy_Result(_UIDSize, _Coll, _ProprietaryCoding)
class Iso14a_Select(Command):
    CommandGroupId = 0x13
    CommandId = 0x03
    def build_frame(self, CascLev: int = 0, BitCount: int = 0, *, PreSelSer: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CascLev.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BitCount.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(PreSelSer)
        return _send_buffer.getvalue()
    def __call__(self, CascLev: int = 0, BitCount: int = 0, *, PreSelSer: bytes, BrpTimeout: int = 100) -> Iso14a_Select_Result:
        request_frame = self.build_frame(CascLev=CascLev, BitCount=BitCount, PreSelSer=PreSelSer, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SAK = safe_read_int_from_buffer(_recv_buffer, 1)
        _Serial_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Serial = _recv_buffer.read(_Serial_len)
        if len(_Serial) != _Serial_len:
            raise PayloadTooShortError(_Serial_len - len(_Serial))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso14a_Select_Result(_SAK, _Serial)
class Iso14a_Halt(Command):
    CommandGroupId = 0x13
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso14a_RequestATS(Command):
    CommandGroupId = 0x13
    CommandId = 0x05
    def build_frame(self, FSDI: Iso14a_RequestATS_FSDI = "Bytes64", CID: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (Iso14a_RequestATS_FSDI_Parser.as_value(FSDI) & 0b1111) << 4
        _var_0000_int |= (CID & 0b1111) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FSDI: Iso14a_RequestATS_FSDI = "Bytes64", CID: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(FSDI=FSDI, CID=CID, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATS = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ATS
class Iso14a_PerformPPS(Command):
    CommandGroupId = 0x13
    CommandId = 0x06
    def build_frame(self, CID: int = 0, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CID.to_bytes(length=1, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (DivisorInteger_Parser.as_value(DSI) & 0b11) << 2
        _var_0000_int |= (DivisorInteger_Parser.as_value(DRI) & 0b11) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CID: int = 0, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CID=CID, DSI=DSI, DRI=DRI, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso14a_Request(Command):
    CommandGroupId = 0x13
    CommandId = 0x07
    def build_frame(self, ReqAll: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ReqAll) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ReqAll: bool = False, BrpTimeout: int = 100) -> Iso14a_Request_Result:
        request_frame = self.build_frame(ReqAll=ReqAll, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATQA = _recv_buffer.read(2)
        if len(_ATQA) != 2:
            raise PayloadTooShortError(2 - len(_ATQA))
        _Collision = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso14a_Request_Result(_ATQA, _Collision)
class Iso14a_RequestVasup(Command):
    CommandGroupId = 0x13
    CommandId = 0x0A
    def build_frame(self, ReqAll: bool = False, FormatVersion: int = 2, VasSupported: bool = True, AuthUserRequested: bool = True, TerminalTypeDataLength: int = 3, *, TerminalType: int, TCI: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ReqAll) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(FormatVersion.to_bytes(length=1, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (int(VasSupported) & 0b1) << 7
        _var_0001_int |= (int(AuthUserRequested) & 0b1) << 6
        _var_0001_int |= (TerminalTypeDataLength & 0b1111) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(TerminalType.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(TCI)
        return _send_buffer.getvalue()
    def __call__(self, ReqAll: bool = False, FormatVersion: int = 2, VasSupported: bool = True, AuthUserRequested: bool = True, TerminalTypeDataLength: int = 3, *, TerminalType: int, TCI: bytes, BrpTimeout: int = 100) -> Iso14a_RequestVasup_Result:
        request_frame = self.build_frame(ReqAll=ReqAll, FormatVersion=FormatVersion, VasSupported=VasSupported, AuthUserRequested=AuthUserRequested, TerminalTypeDataLength=TerminalTypeDataLength, TerminalType=TerminalType, TCI=TCI, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATQA = _recv_buffer.read(2)
        if len(_ATQA) != 2:
            raise PayloadTooShortError(2 - len(_ATQA))
        _Collision = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso14a_RequestVasup_Result(_ATQA, _Collision)
class Iso14a_Anticoll(Command):
    CommandGroupId = 0x13
    CommandId = 0x18
    def build_frame(self, BitCount: int = 0, *, PreSelectedSnr: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x18")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BitCount.to_bytes(length=1, byteorder='big'))
        if len(PreSelectedSnr) != 4:
            raise ValueError(PreSelectedSnr)
        _send_buffer.write(PreSelectedSnr)
        return _send_buffer.getvalue()
    def __call__(self, BitCount: int = 0, *, PreSelectedSnr: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BitCount=BitCount, PreSelectedSnr=PreSelectedSnr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SelectedSnr = _recv_buffer.read(4)
        if len(_SelectedSnr) != 4:
            raise PayloadTooShortError(4 - len(_SelectedSnr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _SelectedSnr
class Iso14a_SelectOnly(Command):
    CommandGroupId = 0x13
    CommandId = 0x19
    def build_frame(self, Snr: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x19")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        return _send_buffer.getvalue()
    def __call__(self, Snr: bytes, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(Snr=Snr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SAK = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _SAK
class Iso14a_TransparentCmd(Command):
    CommandGroupId = 0x13
    CommandId = 0x20
    def build_frame(self, EnMifBwProt: bool = False, EnBitmode: bool = False, EnCRCRX: bool = True, EnCRCTX: bool = True, ParityMode: bool = True, EnParity: bool = True, *, SendDataLen: int, Timeout: int = 26, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", SendData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EnMifBwProt) & 0b1) << 7
        _var_0000_int |= (int(EnBitmode) & 0b1) << 4
        _var_0000_int |= (int(EnCRCRX) & 0b1) << 3
        _var_0000_int |= (int(EnCRCTX) & 0b1) << 2
        _var_0000_int |= (int(ParityMode) & 0b1) << 1
        _var_0000_int |= (int(EnParity) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SendDataLen.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (DivisorInteger_Parser.as_value(DSI) & 0b11) << 2
        _var_0001_int |= (DivisorInteger_Parser.as_value(DRI) & 0b11) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, EnMifBwProt: bool = False, EnBitmode: bool = False, EnCRCRX: bool = True, EnCRCTX: bool = True, ParityMode: bool = True, EnParity: bool = True, *, SendDataLen: int, Timeout: int = 26, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", SendData: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(EnMifBwProt=EnMifBwProt, EnBitmode=EnBitmode, EnCRCRX=EnCRCRX, EnCRCTX=EnCRCTX, ParityMode=ParityMode, EnParity=EnParity, SendDataLen=SendDataLen, Timeout=Timeout, DSI=DSI, DRI=DRI, SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RcvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RcvData = _recv_buffer.read(_RcvData_len)
        if len(_RcvData) != _RcvData_len:
            raise PayloadTooShortError(_RcvData_len - len(_RcvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RcvData
class Iso14a_TransparentCmdBitlen(Command):
    CommandGroupId = 0x13
    CommandId = 0x23
    def build_frame(self, EnHighBaudOld: bool = False, *, EnParTx: bool, SendDataLen: int, Timeout: int = 26, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", SendData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x13\x23")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EnHighBaudOld) & 0b1) << 6
        _var_0000_int |= (int(EnParTx) & 0b1) << 5
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SendDataLen.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (DivisorInteger_Parser.as_value(DSI) & 0b11) << 2
        _var_0001_int |= (DivisorInteger_Parser.as_value(DRI) & 0b11) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, EnHighBaudOld: bool = False, *, EnParTx: bool, SendDataLen: int, Timeout: int = 26, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", SendData: bytes, BrpTimeout: int = 100) -> Iso14a_TransparentCmdBitlen_Result:
        request_frame = self.build_frame(EnHighBaudOld=EnHighBaudOld, EnParTx=EnParTx, SendDataLen=SendDataLen, Timeout=Timeout, DSI=DSI, DRI=DRI, SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvDataLen = safe_read_int_from_buffer(_recv_buffer, 2)
        _CollisionPosition = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso14a_TransparentCmdBitlen_Result(_RecvDataLen, _CollisionPosition, _RecvData)
class Iso14b_Request(Command):
    CommandGroupId = 0x14
    CommandId = 0x02
    def build_frame(self, ExtendedATQB: bool = False, ReqAll: bool = False, TimeSlots: Iso14b_Request_TimeSlots = "TimeSlots1", AFI: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x14\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ExtendedATQB) & 0b1) << 4
        _var_0000_int |= (int(ReqAll) & 0b1) << 3
        _var_0000_int |= (Iso14b_Request_TimeSlots_Parser.as_value(TimeSlots) & 0b111) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AFI.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ExtendedATQB: bool = False, ReqAll: bool = False, TimeSlots: Iso14b_Request_TimeSlots = "TimeSlots1", AFI: int = 0, BrpTimeout: int = 100) -> List[Iso14b_Request_ValueList_Entry]:
        request_frame = self.build_frame(ExtendedATQB=ExtendedATQB, ReqAll=ReqAll, TimeSlots=TimeSlots, AFI=AFI, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ValueList_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ValueList = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_ValueList) >= _ValueList_len:
            _PUPI = _recv_buffer.read(4)
            if len(_PUPI) != 4:
                raise PayloadTooShortError(4 - len(_PUPI))
            _AppData = _recv_buffer.read(4)
            if len(_AppData) != 4:
                raise PayloadTooShortError(4 - len(_AppData))
            _var_0001_int = safe_read_int_from_buffer(_recv_buffer, 1)
            _Synced = (_var_0001_int >> 7) & 0b1
            _Send848 = (_var_0001_int >> 6) & 0b1
            _Send424 = (_var_0001_int >> 5) & 0b1
            _Send212 = (_var_0001_int >> 4) & 0b1
            _Recv848 = (_var_0001_int >> 2) & 0b1
            _Recv424 = (_var_0001_int >> 1) & 0b1
            _Recv212 = (_var_0001_int >> 0) & 0b1
            _var_0002_int = safe_read_int_from_buffer(_recv_buffer, 2)
            _FSCI = Iso14b_Request_FSCI_Parser.as_literal((_var_0002_int >> 12) & 0b1111)
            _ProtType = Iso14b_Request_ProtType_Parser.as_literal((_var_0002_int >> 8) & 0b1111)
            _FWI = Iso14b_Request_FWI_Parser.as_literal((_var_0002_int >> 4) & 0b1111)
            _ADC = (_var_0002_int >> 2) & 0b11
            _NAD = (_var_0002_int >> 1) & 0b1
            _CID = (_var_0002_int >> 0) & 0b1
            if ExtendedATQB:
                _var_0004_int = safe_read_int_from_buffer(_recv_buffer, 1)
                _SFGI = Iso14b_Request_SFGI_Parser.as_literal((_var_0004_int >> 4) & 0b1111)
            else:
                _SFGI = None
            _ValueList_Entry = Iso14b_Request_ValueList_Entry(_PUPI, _AppData, _Synced, _Send848, _Send424, _Send212, _Recv848, _Recv424, _Recv212, _FSCI, _ProtType, _FWI, _ADC, _NAD, _CID, _SFGI)
            _ValueList.append(_ValueList_Entry)
        if len(_ValueList) != _ValueList_len:
            raise PayloadTooShortError(_ValueList_len - len(_ValueList))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ValueList
class Iso14b_Attrib(Command):
    CommandGroupId = 0x14
    CommandId = 0x03
    def build_frame(self, PUPI: bytes, TR0: Iso14b_Attrib_TR0 = "Numerator64", TR1: Iso14b_Attrib_TR1 = "Numerator80", EOF: Iso14b_Attrib_EOF = "EOFrequired", SOF: Iso14b_Attrib_SOF = "SOFrequired", DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", FSDI: Iso14b_Attrib_FSDI = "Bytes64", *, ProtocolType: int, CID: int = 0, EnHLR: bool = False, EnMBLI: bool = False, EnCID: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x14\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(PUPI) != 4:
            raise ValueError(PUPI)
        _send_buffer.write(PUPI)
        _var_0000_int = 0
        _var_0000_int |= (Iso14b_Attrib_TR0_Parser.as_value(TR0) & 0b11) << 22
        _var_0000_int |= (Iso14b_Attrib_TR1_Parser.as_value(TR1) & 0b11) << 20
        _var_0000_int |= (Iso14b_Attrib_EOF_Parser.as_value(EOF) & 0b1) << 19
        _var_0000_int |= (Iso14b_Attrib_SOF_Parser.as_value(SOF) & 0b1) << 18
        _var_0000_int |= (DivisorInteger_Parser.as_value(DSI) & 0b11) << 14
        _var_0000_int |= (DivisorInteger_Parser.as_value(DRI) & 0b11) << 12
        _var_0000_int |= (Iso14b_Attrib_FSDI_Parser.as_value(FSDI) & 0b1111) << 8
        _var_0000_int |= (ProtocolType & 0b1111) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=3, byteorder='big'))
        _send_buffer.write(CID.to_bytes(length=1, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (int(EnHLR) & 0b1) << 2
        _var_0001_int |= (int(EnMBLI) & 0b1) << 1
        _var_0001_int |= (int(EnCID) & 0b1) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PUPI: bytes, TR0: Iso14b_Attrib_TR0 = "Numerator64", TR1: Iso14b_Attrib_TR1 = "Numerator80", EOF: Iso14b_Attrib_EOF = "EOFrequired", SOF: Iso14b_Attrib_SOF = "SOFrequired", DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", FSDI: Iso14b_Attrib_FSDI = "Bytes64", *, ProtocolType: int, CID: int = 0, EnHLR: bool = False, EnMBLI: bool = False, EnCID: bool = False, BrpTimeout: int = 100) -> Iso14b_Attrib_Result:
        request_frame = self.build_frame(PUPI=PUPI, TR0=TR0, TR1=TR1, EOF=EOF, SOF=SOF, DSI=DSI, DRI=DRI, FSDI=FSDI, ProtocolType=ProtocolType, CID=CID, EnHLR=EnHLR, EnMBLI=EnMBLI, EnCID=EnCID, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        if EnCID:
            _AssignedCID = safe_read_int_from_buffer(_recv_buffer, 1)
        else:
            _AssignedCID = None
        if EnMBLI:
            _MBLI = safe_read_int_from_buffer(_recv_buffer, 1)
        else:
            _MBLI = None
        if EnHLR:
            _HLR_len = safe_read_int_from_buffer(_recv_buffer, 1)
            _HLR = _recv_buffer.read(_HLR_len)
            if len(_HLR) != _HLR_len:
                raise PayloadTooShortError(_HLR_len - len(_HLR))
        else:
            _HLR = None
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso14b_Attrib_Result(_AssignedCID, _MBLI, _HLR)
class Iso14b_Halt(Command):
    CommandGroupId = 0x14
    CommandId = 0x04
    def build_frame(self, PUPI: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x14\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(PUPI) != 4:
            raise ValueError(PUPI)
        _send_buffer.write(PUPI)
        return _send_buffer.getvalue()
    def __call__(self, PUPI: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PUPI=PUPI, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso14b_SetTransparentSettings(Command):
    CommandGroupId = 0x14
    CommandId = 0x21
    def build_frame(self, Tags: List[Iso14b_SetTransparentSettings_Tags_Entry], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x14\x21")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        for _Tags_Entry in Tags:
            _ID, _Value = _Tags_Entry
            _send_buffer.write(_ID.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_Value.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Tags: List[Iso14b_SetTransparentSettings_Tags_Entry], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Tags=Tags, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso14b_GetTransparentSettings(Command):
    CommandGroupId = 0x14
    CommandId = 0x22
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x14\x22")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> List[Iso14b_GetTransparentSettings_Tags_Entry]:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Tags = []  # type: ignore[var-annotated,unused-ignore]
        while not _recv_buffer.tell() >= len(_recv_buffer.getvalue()):
            _ID = safe_read_int_from_buffer(_recv_buffer, 1)
            _Value = safe_read_int_from_buffer(_recv_buffer, 1)
            _Tags_Entry = Iso14b_GetTransparentSettings_Tags_Entry(_ID, _Value)
            _Tags.append(_Tags_Entry)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Tags
class Iso14b_TransparentCmd(Command):
    CommandGroupId = 0x14
    CommandId = 0x20
    def build_frame(self, EnCRCRX: int = 1, EnCRCTX: int = 1, *, SendDataLen: int, Timeout: int = 10, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", SendData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x14\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (EnCRCRX & 0b1) << 1
        _var_0000_int |= (EnCRCTX & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SendDataLen.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (DivisorInteger_Parser.as_value(DSI) & 0b11) << 2
        _var_0001_int |= (DivisorInteger_Parser.as_value(DRI) & 0b11) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, EnCRCRX: int = 1, EnCRCTX: int = 1, *, SendDataLen: int, Timeout: int = 10, DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", SendData: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(EnCRCRX=EnCRCRX, EnCRCTX=EnCRCTX, SendDataLen=SendDataLen, Timeout=Timeout, DSI=DSI, DRI=DRI, SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(_RecvData_len)
        if len(_RecvData) != _RecvData_len:
            raise PayloadTooShortError(_RecvData_len - len(_RecvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvData
class Iso14L4_SetupAPDU(Command):
    CommandGroupId = 0x16
    CommandId = 0x00
    def build_frame(self, EnDefault: bool = True, ToggleAB: int = 0, EnNAD: bool = False, EnCID: bool = False, CID: int = 0, NAD: int = 0, FSCI: Iso14L4_SetupAPDU_FSCI = "Bytes64", FWI: Iso14L4_SetupAPDU_FWI = "Us4832", DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x16\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EnDefault) & 0b1) << 3
        _var_0000_int |= (ToggleAB & 0b1) << 2
        _var_0000_int |= (int(EnNAD) & 0b1) << 1
        _var_0000_int |= (int(EnCID) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(NAD.to_bytes(length=1, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (Iso14L4_SetupAPDU_FSCI_Parser.as_value(FSCI) & 0b1111) << 12
        _var_0001_int |= (Iso14L4_SetupAPDU_FWI_Parser.as_value(FWI) & 0b1111) << 8
        _var_0001_int |= (DivisorInteger_Parser.as_value(DSI) & 0b11) << 2
        _var_0001_int |= (DivisorInteger_Parser.as_value(DRI) & 0b11) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, EnDefault: bool = True, ToggleAB: int = 0, EnNAD: bool = False, EnCID: bool = False, CID: int = 0, NAD: int = 0, FSCI: Iso14L4_SetupAPDU_FSCI = "Bytes64", FWI: Iso14L4_SetupAPDU_FWI = "Us4832", DSI: DivisorInteger = "Kbps106", DRI: DivisorInteger = "Kbps106", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(EnDefault=EnDefault, ToggleAB=ToggleAB, EnNAD=EnNAD, EnCID=EnCID, CID=CID, NAD=NAD, FSCI=FSCI, FWI=FWI, DSI=DSI, DRI=DRI, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso14L4_ExchangeAPDU(Command):
    CommandGroupId = 0x16
    CommandId = 0x01
    def build_frame(self, SendData: bytes, BrpTimeout: int = 60000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x16\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SendData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, SendData: bytes, BrpTimeout: int = 60000) -> bytes:
        request_frame = self.build_frame(SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(_RecvData_len)
        if len(_RecvData) != _RecvData_len:
            raise PayloadTooShortError(_RecvData_len - len(_RecvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvData
class Iso14L4_Deselect(Command):
    CommandGroupId = 0x16
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x16\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class I4CE_StartEmu(Command):
    CommandGroupId = 0x48
    CommandId = 0x01
    def build_frame(self, Snr: bytes, FWT: int = 0, TimeoutPCD: int = 750, TimeoutAPDU: int = 50, *, ATS: bytes, AutoWTX: int = 0, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x48\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        _send_buffer.write(FWT.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(TimeoutPCD.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(TimeoutAPDU.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(ATS)).to_bytes(1, byteorder='big'))
        _send_buffer.write(ATS)
        _send_buffer.write(AutoWTX.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Snr: bytes, FWT: int = 0, TimeoutPCD: int = 750, TimeoutAPDU: int = 50, *, ATS: bytes, AutoWTX: int = 0, BrpTimeout: int = 1000) -> bytes:
        request_frame = self.build_frame(Snr=Snr, FWT=FWT, TimeoutPCD=TimeoutPCD, TimeoutAPDU=TimeoutAPDU, ATS=ATS, AutoWTX=AutoWTX, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FirstCmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _FirstCmd = _recv_buffer.read(_FirstCmd_len)
        if len(_FirstCmd) != _FirstCmd_len:
            raise PayloadTooShortError(_FirstCmd_len - len(_FirstCmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _FirstCmd
class I4CE_ExchangeInverseAPDU(Command):
    CommandGroupId = 0x48
    CommandId = 0x02
    def build_frame(self, Rsp: bytes, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x48\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Rsp)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Rsp)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Rsp: bytes, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        request_frame = self.build_frame(Rsp=Rsp, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Cmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Cmd = _recv_buffer.read(_Cmd_len)
        if len(_Cmd) != _Cmd_len:
            raise PayloadTooShortError(_Cmd_len - len(_Cmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Cmd
class I4CE_ExtendWaitingTime(Command):
    CommandGroupId = 0x48
    CommandId = 0x03
    def build_frame(self, WaitingTimeout: int = 65535, WTXM: int = 1, RefreshTimeRatio: int = 90, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x48\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(WaitingTimeout.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(WTXM.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(RefreshTimeRatio.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, WaitingTimeout: int = 65535, WTXM: int = 1, RefreshTimeRatio: int = 90, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(WaitingTimeout=WaitingTimeout, WTXM=WTXM, RefreshTimeRatio=RefreshTimeRatio, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class I4CE_GetExternalHfStatus(Command):
    CommandGroupId = 0x48
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x48\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ExtFieldStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ExtFieldStat
class Iso14CE_ActivateCardAPDU(Command):
    CommandGroupId = 0x4A
    CommandId = 0x01
    def build_frame(self, SpecifyTimeoutApdu: bool = False, AutoWTX: bool = False, *, ATQA: int, Snr: bytes, DSEqualToDR: bool = False, DS8: bool = False, DS4: bool = False, DS2: bool = False, DR8: bool = False, DR4: bool = False, DR2: bool = False, FWT: int = 0, TimeoutPCD: int = 750, TimeoutApdu: Optional[int] = None, ATS: bytes, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4A\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(SpecifyTimeoutApdu) & 0b1) << 1
        _var_0000_int |= (int(AutoWTX) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ATQA.to_bytes(length=2, byteorder='big'))
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        _var_0001_int = 0
        _var_0001_int |= (int(DSEqualToDR) & 0b1) << 7
        _var_0001_int |= (int(DS8) & 0b1) << 6
        _var_0001_int |= (int(DS4) & 0b1) << 5
        _var_0001_int |= (int(DS2) & 0b1) << 4
        _var_0001_int |= (int(DR8) & 0b1) << 2
        _var_0001_int |= (int(DR4) & 0b1) << 1
        _var_0001_int |= (int(DR2) & 0b1) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(FWT.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(TimeoutPCD.to_bytes(length=2, byteorder='big'))
        if SpecifyTimeoutApdu:
            if TimeoutApdu is None:
                raise TypeError("missing a required argument: 'TimeoutApdu'")
            _send_buffer.write(TimeoutApdu.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(ATS)).to_bytes(1, byteorder='big'))
        _send_buffer.write(ATS)
        return _send_buffer.getvalue()
    def __call__(self, SpecifyTimeoutApdu: bool = False, AutoWTX: bool = False, *, ATQA: int, Snr: bytes, DSEqualToDR: bool = False, DS8: bool = False, DS4: bool = False, DS2: bool = False, DR8: bool = False, DR4: bool = False, DR2: bool = False, FWT: int = 0, TimeoutPCD: int = 750, TimeoutApdu: Optional[int] = None, ATS: bytes, BrpTimeout: int = 2000) -> bytes:
        request_frame = self.build_frame(SpecifyTimeoutApdu=SpecifyTimeoutApdu, AutoWTX=AutoWTX, ATQA=ATQA, Snr=Snr, DSEqualToDR=DSEqualToDR, DS8=DS8, DS4=DS4, DS2=DS2, DR8=DR8, DR4=DR4, DR2=DR2, FWT=FWT, TimeoutPCD=TimeoutPCD, TimeoutApdu=TimeoutApdu, ATS=ATS, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FirstCmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _FirstCmd = _recv_buffer.read(_FirstCmd_len)
        if len(_FirstCmd) != _FirstCmd_len:
            raise PayloadTooShortError(_FirstCmd_len - len(_FirstCmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _FirstCmd
class Iso14CE_ExchangeCardAPDU(Command):
    CommandGroupId = 0x4A
    CommandId = 0x02
    def build_frame(self, Rsp: bytes, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4A\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Rsp)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Rsp)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Rsp: bytes, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        request_frame = self.build_frame(Rsp=Rsp, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Cmd_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Cmd = _recv_buffer.read(_Cmd_len)
        if len(_Cmd) != _Cmd_len:
            raise PayloadTooShortError(_Cmd_len - len(_Cmd))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Cmd
class Iso14CE_ExtendWaitingTime(Command):
    CommandGroupId = 0x4A
    CommandId = 0x03
    def build_frame(self, WaitingTimeout: int = 65535, WTXM: int = 1, RefreshTimeRatio: int = 90, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4A\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(WaitingTimeout.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(WTXM.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(RefreshTimeRatio.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, WaitingTimeout: int = 65535, WTXM: int = 1, RefreshTimeRatio: int = 90, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(WaitingTimeout=WaitingTimeout, WTXM=WTXM, RefreshTimeRatio=RefreshTimeRatio, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso14CE_GetExternalHfStatus(Command):
    CommandGroupId = 0x4A
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4A\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ExtFieldStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ExtFieldStat
class Iso15_SetParam(Command):
    CommandGroupId = 0x21
    CommandId = 0x00
    def build_frame(self, ModulationIndex: bool = False, TXMode: bool = True, HighDataRate: bool = True, DualSubcarrier: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ModulationIndex) & 0b1) << 3
        _var_0000_int |= (int(TXMode) & 0b1) << 2
        _var_0000_int |= (int(HighDataRate) & 0b1) << 1
        _var_0000_int |= (int(DualSubcarrier) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ModulationIndex: bool = False, TXMode: bool = True, HighDataRate: bool = True, DualSubcarrier: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ModulationIndex=ModulationIndex, TXMode=TXMode, HighDataRate=HighDataRate, DualSubcarrier=DualSubcarrier, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso15_GetParam(Command):
    CommandGroupId = 0x21
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Iso15_GetParam_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Mode_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _ModulationIndex = (_Mode_int >> 3) & 0b1
        _TXMode = (_Mode_int >> 2) & 0b1
        _HighDataRate = (_Mode_int >> 1) & 0b1
        _DualSubcarrier = (_Mode_int >> 0) & 0b1
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_GetParam_Result(_ModulationIndex, _TXMode, _HighDataRate, _DualSubcarrier)
class Iso15_GetUIDList(Command):
    CommandGroupId = 0x21
    CommandId = 0x02
    def build_frame(self, EnAFI: bool = False, NextBlock: bool = False, AutoQuiet: bool = False, EnDSFID: bool = False, En16Slots: bool = False, AFI: Optional[int] = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EnAFI) & 0b1) << 4
        _var_0000_int |= (int(NextBlock) & 0b1) << 3
        _var_0000_int |= (int(AutoQuiet) & 0b1) << 2
        _var_0000_int |= (int(EnDSFID) & 0b1) << 1
        _var_0000_int |= (int(En16Slots) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if EnAFI:
            if AFI is None:
                raise TypeError("missing a required argument: 'AFI'")
            _send_buffer.write(AFI.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, EnAFI: bool = False, NextBlock: bool = False, AutoQuiet: bool = False, EnDSFID: bool = False, En16Slots: bool = False, AFI: Optional[int] = 0, BrpTimeout: int = 100) -> Iso15_GetUIDList_Result:
        request_frame = self.build_frame(EnAFI=EnAFI, NextBlock=NextBlock, AutoQuiet=AutoQuiet, EnDSFID=EnDSFID, En16Slots=En16Slots, AFI=AFI, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _More = safe_read_int_from_buffer(_recv_buffer, 1)
        _Labels_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Labels = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_Labels) >= _Labels_len:
            _UID = _recv_buffer.read(8)
            if len(_UID) != 8:
                raise PayloadTooShortError(8 - len(_UID))
            if EnDSFID:
                _DSFID = safe_read_int_from_buffer(_recv_buffer, 1)
            else:
                _DSFID = None
            _Labels_Entry = Iso15_GetUIDList_Labels_Entry(_UID, _DSFID)
            _Labels.append(_Labels_Entry)
        if len(_Labels) != _Labels_len:
            raise PayloadTooShortError(_Labels_len - len(_Labels))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_GetUIDList_Result(_More, _Labels)
class Iso15_SetMode(Command):
    CommandGroupId = 0x21
    CommandId = 0x03
    def build_frame(self, Mode: int = 1, UID: Optional[bytes] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        if Mode != 0:
            if UID is None:
                raise TypeError("missing a required argument: 'UID'")
            if len(UID) != 8:
                raise ValueError(UID)
            _send_buffer.write(UID)
        return _send_buffer.getvalue()
    def __call__(self, Mode: int = 1, UID: Optional[bytes] = None, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Mode=Mode, UID=UID, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso15_StayQuiet(Command):
    CommandGroupId = 0x21
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso15_ReadBlock(Command):
    CommandGroupId = 0x21
    CommandId = 0x05
    def build_frame(self, BlockID: int = 0, BlockNum: int = 0, EnBlockSec: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockNum.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EnBlockSec.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockID: int = 0, BlockNum: int = 0, EnBlockSec: bool = True, BrpTimeout: int = 100) -> Iso15_ReadBlock_Result:
        request_frame = self.build_frame(BlockID=BlockID, BlockNum=BlockNum, EnBlockSec=EnBlockSec, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        if _LabelStat == 0:
            _BlockLen = safe_read_int_from_buffer(_recv_buffer, 1)
            _Data = []  # type: ignore[var-annotated,unused-ignore]
            while not _recv_buffer.tell() >= len(_recv_buffer.getvalue()):
                _BlockData = _recv_buffer.read(0)
                if len(_BlockData) != 0:
                    raise PayloadTooShortError(0 - len(_BlockData))
                if EnBlockSec:
                    _BlockSecData = safe_read_int_from_buffer(_recv_buffer, 1)
                else:
                    _BlockSecData = None
                _Data_Entry = Iso15_ReadBlock_Data_Entry(_BlockData, _BlockSecData)
                _Data.append(_Data_Entry)
        else:
            _BlockLen = None
            _Data = None
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_ReadBlock_Result(_LabelStat, _BlockLen, _Data)
class Iso15_WriteBlock(Command):
    CommandGroupId = 0x21
    CommandId = 0x06
    def build_frame(self, BlockID: int = 0, *, BlockNum: int, BlockLen: int, OptionFlag: bool = False, Data: List[bytes], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockNum.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockLen.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        for _Data_Entry in Data:
            _SingleBlock = _Data_Entry
            if len(_SingleBlock) != 0:
                raise ValueError(_SingleBlock)
            _send_buffer.write(_SingleBlock)
        return _send_buffer.getvalue()
    def __call__(self, BlockID: int = 0, *, BlockNum: int, BlockLen: int, OptionFlag: bool = False, Data: List[bytes], BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BlockID=BlockID, BlockNum=BlockNum, BlockLen=BlockLen, OptionFlag=OptionFlag, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_LockBlock(Command):
    CommandGroupId = 0x21
    CommandId = 0x07
    def build_frame(self, BlockID: int = 0, OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockID: int = 0, OptionFlag: bool = False, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BlockID=BlockID, OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_ResetToReady(Command):
    CommandGroupId = 0x21
    CommandId = 0x08
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_WriteAFI(Command):
    CommandGroupId = 0x21
    CommandId = 0x09
    def build_frame(self, AFI: int, OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AFI.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AFI: int, OptionFlag: bool = False, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(AFI=AFI, OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_LockAFI(Command):
    CommandGroupId = 0x21
    CommandId = 0x0A
    def build_frame(self, OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, OptionFlag: bool = False, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_WriteDSFID(Command):
    CommandGroupId = 0x21
    CommandId = 0x0B
    def build_frame(self, DSFID: int, OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x0B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DSFID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DSFID: int, OptionFlag: bool = False, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(DSFID=DSFID, OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_LockDSFID(Command):
    CommandGroupId = 0x21
    CommandId = 0x0C
    def build_frame(self, OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x0C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, OptionFlag: bool = False, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_GetSystemInformation(Command):
    CommandGroupId = 0x21
    CommandId = 0x0D
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x0D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Iso15_GetSystemInformation_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        if _LabelStat == 0:
            _Info_int = safe_read_int_from_buffer(_recv_buffer, 1)
            _EnICRef = bool((_Info_int >> 3) & 0b1)
            _EnMemSize = bool((_Info_int >> 2) & 0b1)
            _EnAFI = bool((_Info_int >> 1) & 0b1)
            _EnDSFID = bool((_Info_int >> 0) & 0b1)
            _SNR = _recv_buffer.read(8)
            if len(_SNR) != 8:
                raise PayloadTooShortError(8 - len(_SNR))
        else:
            _EnICRef = None
            _EnMemSize = None
            _EnAFI = None
            _EnDSFID = None
            _SNR = None
        if _LabelStat == 0 and _EnDSFID:
            _DSFID = safe_read_int_from_buffer(_recv_buffer, 1)
        else:
            _DSFID = None
        if _LabelStat == 0 and _EnAFI:
            _AFI = safe_read_int_from_buffer(_recv_buffer, 1)
        else:
            _AFI = None
        if _LabelStat == 0 and _EnMemSize:
            _BlockNum = safe_read_int_from_buffer(_recv_buffer, 1)
            _BlockSize = safe_read_int_from_buffer(_recv_buffer, 1)
        else:
            _BlockNum = None
            _BlockSize = None
        if _LabelStat == 0 and _EnICRef:
            _ICRef = safe_read_int_from_buffer(_recv_buffer, 1)
        else:
            _ICRef = None
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_GetSystemInformation_Result(_LabelStat, _EnICRef, _EnMemSize, _EnAFI, _EnDSFID, _SNR, _DSFID, _AFI, _BlockNum, _BlockSize, _ICRef)
class Iso15_GetSecurityStatus(Command):
    CommandGroupId = 0x21
    CommandId = 0x0E
    def build_frame(self, BlockID: int = 0, BlockNum: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x0E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockNum.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockID: int = 0, BlockNum: int = 0, BrpTimeout: int = 100) -> Iso15_GetSecurityStatus_Result:
        request_frame = self.build_frame(BlockID=BlockID, BlockNum=BlockNum, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _BlockStat = []  # type: ignore[var-annotated,unused-ignore]
        while not _recv_buffer.tell() >= len(_recv_buffer.getvalue()):
            _Status = safe_read_int_from_buffer(_recv_buffer, 1)
            _BlockStat.append(_Status)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_GetSecurityStatus_Result(_LabelStat, _BlockStat)
class Iso15_CustomCommand(Command):
    CommandGroupId = 0x21
    CommandId = 0x0F
    def build_frame(self, Cmd: int, Opt: int, MFC: int, TO: int, RequestData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x0F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Cmd.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Opt.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(MFC.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(TO.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(RequestData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(RequestData)
        return _send_buffer.getvalue()
    def __call__(self, Cmd: int, Opt: int, MFC: int, TO: int, RequestData: bytes, BrpTimeout: int = 100) -> Iso15_CustomCommand_Result:
        request_frame = self.build_frame(Cmd=Cmd, Opt=Opt, MFC=MFC, TO=TO, RequestData=RequestData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        if _LabelStat == 0:
            _ResponseData_len = safe_read_int_from_buffer(_recv_buffer, 2)
            _ResponseData = _recv_buffer.read(_ResponseData_len)
            if len(_ResponseData) != _ResponseData_len:
                raise PayloadTooShortError(_ResponseData_len - len(_ResponseData))
        else:
            _ResponseData = None
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_CustomCommand_Result(_LabelStat, _ResponseData)
class Iso15_ReadSingleBlock(Command):
    CommandGroupId = 0x21
    CommandId = 0x11
    def build_frame(self, BlockID: int = 0, EnBlockSec: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EnBlockSec.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockID: int = 0, EnBlockSec: bool = False, BrpTimeout: int = 100) -> Iso15_ReadSingleBlock_Result:
        request_frame = self.build_frame(BlockID=BlockID, EnBlockSec=EnBlockSec, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        if _LabelStat == 0:
            _Payload_len = safe_read_int_from_buffer(_recv_buffer, 1)
            _Payload = _recv_buffer.read(_Payload_len)
            if len(_Payload) != _Payload_len:
                raise PayloadTooShortError(_Payload_len - len(_Payload))
        else:
            _Payload = None
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_ReadSingleBlock_Result(_LabelStat, _Payload)
class Iso15_WriteSingleBlock(Command):
    CommandGroupId = 0x21
    CommandId = 0x12
    def build_frame(self, BlockID: int = 0, *, BlockLen: int, OptionFlag: bool = False, SingleBlockData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockLen.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SingleBlockData)
        return _send_buffer.getvalue()
    def __call__(self, BlockID: int = 0, *, BlockLen: int, OptionFlag: bool = False, SingleBlockData: bytes, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BlockID=BlockID, BlockLen=BlockLen, OptionFlag=OptionFlag, SingleBlockData=SingleBlockData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_TransparentCmdLegacy(Command):
    CommandGroupId = 0x21
    CommandId = 0x20
    def build_frame(self, EnRxWait: bool = False, EnCRCRX: bool = True, EnCRCTX: bool = True, *, Len: int, Timeout: int = 26, Data: bytes, RxWait: Optional[int] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EnRxWait) & 0b1) << 4
        _var_0000_int |= (int(EnCRCRX) & 0b1) << 3
        _var_0000_int |= (int(EnCRCTX) & 0b1) << 2
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        if len(Data) != 0:
            raise ValueError(Data)
        _send_buffer.write(Data)
        if EnRxWait:
            if RxWait is None:
                raise TypeError("missing a required argument: 'RxWait'")
            _send_buffer.write(RxWait.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, EnRxWait: bool = False, EnCRCRX: bool = True, EnCRCTX: bool = True, *, Len: int, Timeout: int = 26, Data: bytes, RxWait: Optional[int] = None, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(EnRxWait=EnRxWait, EnCRCRX=EnCRCRX, EnCRCTX=EnCRCTX, Len=Len, Timeout=Timeout, Data=Data, RxWait=RxWait, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _LabelData = _recv_buffer.read(_LabelData_len)
        if len(_LabelData) != _LabelData_len:
            raise PayloadTooShortError(_LabelData_len - len(_LabelData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelData
class Iso15_WriteMultipleBlocks(Command):
    CommandGroupId = 0x21
    CommandId = 0x21
    def build_frame(self, FirstBlockId: int = 0, *, WriteBlocks: List[bytes], OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x21")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FirstBlockId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(WriteBlocks)).to_bytes(2, byteorder='big'))
        for _WriteBlocks_Entry in WriteBlocks:
            _WriteBlock = _WriteBlocks_Entry
            _send_buffer.write(int(len(_WriteBlock)).to_bytes(1, byteorder='big'))
            _send_buffer.write(_WriteBlock)
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FirstBlockId: int = 0, *, WriteBlocks: List[bytes], OptionFlag: bool = False, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(FirstBlockId=FirstBlockId, WriteBlocks=WriteBlocks, OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LabelStat
class Iso15_ReadMultipleBlocks(Command):
    CommandGroupId = 0x21
    CommandId = 0x22
    def build_frame(self, FirstBlockId: int, BlockCount: int = 1, EnBlockSec: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x22")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FirstBlockId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockCount.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(EnBlockSec.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FirstBlockId: int, BlockCount: int = 1, EnBlockSec: bool = False, BrpTimeout: int = 100) -> Iso15_ReadMultipleBlocks_Result:
        request_frame = self.build_frame(FirstBlockId=FirstBlockId, BlockCount=BlockCount, EnBlockSec=EnBlockSec, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LabelStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _RecvBlocks_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvBlocks = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_RecvBlocks) >= _RecvBlocks_len:
            _RecvBlock_len = safe_read_int_from_buffer(_recv_buffer, 1)
            _RecvBlock = _recv_buffer.read(_RecvBlock_len)
            if len(_RecvBlock) != _RecvBlock_len:
                raise PayloadTooShortError(_RecvBlock_len - len(_RecvBlock))
            _RecvBlocks.append(_RecvBlock)
        if len(_RecvBlocks) != _RecvBlocks_len:
            raise PayloadTooShortError(_RecvBlocks_len - len(_RecvBlocks))
        _BlocksSecData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _BlocksSecData = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_BlocksSecData) >= _BlocksSecData_len:
            _BlockSecData = safe_read_int_from_buffer(_recv_buffer, 1)
            _BlocksSecData.append(_BlockSecData)
        if len(_BlocksSecData) != _BlocksSecData_len:
            raise PayloadTooShortError(_BlocksSecData_len - len(_BlocksSecData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso15_ReadMultipleBlocks_Result(_LabelStat, _RecvBlocks, _BlocksSecData)
class Iso15_TransparentCmd(Command):
    CommandGroupId = 0x21
    CommandId = 0x23
    def build_frame(self, SendData: bytes, Timeout: int = 26, EnCrcRx: bool = True, EnCrcTx: bool = True, RxWait: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x21\x23")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SendData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendData)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(EnCrcRx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EnCrcTx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(RxWait.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SendData: bytes, Timeout: int = 26, EnCrcRx: bool = True, EnCrcTx: bool = True, RxWait: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(SendData=SendData, Timeout=Timeout, EnCrcRx=EnCrcRx, EnCrcTx=EnCrcTx, RxWait=RxWait, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(_RecvData_len)
        if len(_RecvData) != _RecvData_len:
            raise PayloadTooShortError(_RecvData_len - len(_RecvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvData
class Iso78_SelectSlot(Command):
    CommandGroupId = 0x40
    CommandId = 0x00
    def build_frame(self, SlotIndex: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SlotIndex.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SlotIndex: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(SlotIndex=SlotIndex, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso78_OpenSamLegacy(Command):
    CommandGroupId = 0x40
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 1200) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 1200) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATR_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ATR = _recv_buffer.read(_ATR_len)
        if len(_ATR) != _ATR_len:
            raise PayloadTooShortError(_ATR_len - len(_ATR))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ATR
class Iso78_CloseSamLegacy(Command):
    CommandGroupId = 0x40
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso78_ExchangeApduLegacy(Command):
    CommandGroupId = 0x40
    CommandId = 0x03
    def build_frame(self, SendData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SendData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, SendData: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(_RecvData_len)
        if len(_RecvData) != _RecvData_len:
            raise PayloadTooShortError(_RecvData_len - len(_RecvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvData
class Iso78_OpenSam(Command):
    CommandGroupId = 0x40
    CommandId = 0x04
    def build_frame(self, LID: Iso78_OpenSam_LID, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Iso78_OpenSam_LID_Parser.as_value(LID).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, LID: Iso78_OpenSam_LID, BrpTimeout: int = 100) -> Iso78_OpenSam_Result:
        request_frame = self.build_frame(LID=LID, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SamHandle = safe_read_int_from_buffer(_recv_buffer, 1)
        _ATR_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ATR = _recv_buffer.read(_ATR_len)
        if len(_ATR) != _ATR_len:
            raise PayloadTooShortError(_ATR_len - len(_ATR))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Iso78_OpenSam_Result(_SamHandle, _ATR)
class Iso78_CloseSam(Command):
    CommandGroupId = 0x40
    CommandId = 0x05
    def build_frame(self, SamHandle: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SamHandle.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SamHandle: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(SamHandle=SamHandle, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Iso78_ExchangeApdu(Command):
    CommandGroupId = 0x40
    CommandId = 0x06
    def build_frame(self, SamHandle: int, SendData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x40\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SamHandle.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(SendData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, SamHandle: int, SendData: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(SamHandle=SamHandle, SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(_RecvData_len)
        if len(_RecvData) != _RecvData_len:
            raise PayloadTooShortError(_RecvData_len - len(_RecvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvData
class Keyboard_Exist(Command):
    CommandGroupId = 0x42
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x42\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bool:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _KeyboardConnected = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _KeyboardConnected
class Keyboard_CurrentKey(Command):
    CommandGroupId = 0x42
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x42\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Key = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Key
class Keyboard_EnableWakeup(Command):
    CommandGroupId = 0x42
    CommandId = 0x02
    def build_frame(self, Enable: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x42\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Keyboard_WaitForKey(Command):
    CommandGroupId = 0x42
    CommandId = 0x03
    def build_frame(self, Timeout: int = 65535, BrpTimeout: int = 66000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x42\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Timeout: int = 65535, BrpTimeout: int = 66000) -> int:
        request_frame = self.build_frame(Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Key = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Key
class Legic_TransparentCommand4000(Command):
    CommandGroupId = 0x1E
    CommandId = 0x20
    def build_frame(self, CmdCode: int, CmdParams: bytes, Timeout: int = 100, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1E\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(CmdParams)).to_bytes(1, byteorder='big'))
        _send_buffer.write(CmdParams)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCode: int, CmdParams: bytes, Timeout: int = 100, BrpTimeout: int = 3000) -> Legic_TransparentCommand4000_Result:
        request_frame = self.build_frame(CmdCode=CmdCode, CmdParams=CmdParams, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Legic_TransparentCommand4000_Result(_Status, _Resp)
class Legic_TransparentCommand6000(Command):
    CommandGroupId = 0x1E
    CommandId = 0x21
    def build_frame(self, CmdCode: int, CmdParams: bytes, Timeout: int = 100, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1E\x21")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(CmdParams)).to_bytes(1, byteorder='big'))
        _send_buffer.write(CmdParams)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCode: int, CmdParams: bytes, Timeout: int = 100, BrpTimeout: int = 3000) -> Legic_TransparentCommand6000_Result:
        request_frame = self.build_frame(CmdCode=CmdCode, CmdParams=CmdParams, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Legic_TransparentCommand6000_Result(_Status, _Resp)
class Lg_Select(Command):
    CommandGroupId = 0x11
    CommandId = 0x01
    def build_frame(self, TO: int = 5, Adr: int = 7, Len: int = 4, PollTime: int = 1, CRCAdr: int = 0, SafeDat: int = 0, ChgSeg: int = 0, ProtHead: int = 1, CRCCalc: int = 0, CRCChk: int = 0, SegID: int = 1, *, Stamp: bytes, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(TO.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(PollTime.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CRCAdr.to_bytes(length=2, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (SafeDat & 0b1) << 4
        _var_0000_int |= (ChgSeg & 0b1) << 3
        _var_0000_int |= (ProtHead & 0b1) << 2
        _var_0000_int |= (CRCCalc & 0b1) << 1
        _var_0000_int |= (CRCChk & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SegID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Stamp)
        return _send_buffer.getvalue()
    def __call__(self, TO: int = 5, Adr: int = 7, Len: int = 4, PollTime: int = 1, CRCAdr: int = 0, SafeDat: int = 0, ChgSeg: int = 0, ProtHead: int = 1, CRCCalc: int = 0, CRCChk: int = 0, SegID: int = 1, *, Stamp: bytes, BrpTimeout: int = 2000) -> Lg_Select_Result:
        request_frame = self.build_frame(TO=TO, Adr=Adr, Len=Len, PollTime=PollTime, CRCAdr=CRCAdr, SafeDat=SafeDat, ChgSeg=ChgSeg, ProtHead=ProtHead, CRCCalc=CRCCalc, CRCChk=CRCChk, SegID=SegID, Stamp=Stamp, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MediaType = Lg_Select_MediaType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _FuncLevel = safe_read_int_from_buffer(_recv_buffer, 1)
        _OrgLevel = safe_read_int_from_buffer(_recv_buffer, 1)
        _EvStat = Lg_Select_EvStat_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _ActSegID = safe_read_int_from_buffer(_recv_buffer, 1)
        _ActAdr = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Lg_Select_Result(_MediaType, _FuncLevel, _OrgLevel, _EvStat, _ActSegID, _ActAdr, _Data)
class Lg_Idle(Command):
    CommandGroupId = 0x11
    CommandId = 0x03
    def build_frame(self, PowOff: Lg_Idle_PowOff = "Off", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Lg_Idle_PowOff_Parser.as_value(PowOff).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PowOff: Lg_Idle_PowOff = "Off", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PowOff=PowOff, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Lg_GenSetRead(Command):
    CommandGroupId = 0x11
    CommandId = 0x04
    def build_frame(self, DesiredGenSetNum: int = 1, BrpTimeout: int = 500) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DesiredGenSetNum.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DesiredGenSetNum: int = 1, BrpTimeout: int = 500) -> Lg_GenSetRead_Result:
        request_frame = self.build_frame(DesiredGenSetNum=DesiredGenSetNum, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _GenSetNum = safe_read_int_from_buffer(_recv_buffer, 1)
        _Stamp = _recv_buffer.read(7)
        if len(_Stamp) != 7:
            raise PayloadTooShortError(7 - len(_Stamp))
        _StampLen = safe_read_int_from_buffer(_recv_buffer, 1)
        _var_0000_int = safe_read_int_from_buffer(_recv_buffer, 3)
        _WriteExLen = (_var_0000_int >> 16) & 0b11111111
        _WriteExShad = bool((_var_0000_int >> 15) & 0b1)
        _WriteExMode = Lg_GenSetRead_WriteExMode_Parser.as_literal((_var_0000_int >> 13) & 0b11)
        _WriteExStart = (_var_0000_int >> 0) & 0b111111111111
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Lg_GenSetRead_Result(_GenSetNum, _Stamp, _StampLen, _WriteExLen, _WriteExShad, _WriteExMode, _WriteExStart)
class Lg_GenSetDelete(Command):
    CommandGroupId = 0x11
    CommandId = 0x05
    def build_frame(self, GenSetNum: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(GenSetNum.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, GenSetNum: int = 1, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(GenSetNum=GenSetNum, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _DeletedGenSetNum = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _DeletedGenSetNum
class Lg_ReadMIM(Command):
    CommandGroupId = 0x11
    CommandId = 0x06
    def build_frame(self, Adr: int = 7, Len: int = 4, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 7, Len: int = 4, BrpTimeout: int = 100) -> Lg_ReadMIM_Result:
        request_frame = self.build_frame(Adr=Adr, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _DataAdr = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Lg_ReadMIM_Result(_DataAdr, _Data)
class Lg_ReadMIMCRC(Command):
    CommandGroupId = 0x11
    CommandId = 0x07
    def build_frame(self, Adr: int = 7, Len: int = 4, CRCAdr: int = 11, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CRCAdr.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 7, Len: int = 4, CRCAdr: int = 11, BrpTimeout: int = 100) -> Lg_ReadMIMCRC_Result:
        request_frame = self.build_frame(Adr=Adr, Len=Len, CRCAdr=CRCAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _DataAdr = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Lg_ReadMIMCRC_Result(_DataAdr, _Data)
class Lg_WriteMIM(Command):
    CommandGroupId = 0x11
    CommandId = 0x08
    def build_frame(self, Adr: int, Data: bytes, BrpTimeout: int = 1500) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, Data: bytes, BrpTimeout: int = 1500) -> None:
        request_frame = self.build_frame(Adr=Adr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Lg_WriteMIMCRC(Command):
    CommandGroupId = 0x11
    CommandId = 0x09
    def build_frame(self, Adr: int, DataLen: int, CRCAdr: int, Data: bytes, BrpTimeout: int = 1500) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(DataLen.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CRCAdr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, DataLen: int, CRCAdr: int, Data: bytes, BrpTimeout: int = 1500) -> None:
        request_frame = self.build_frame(Adr=Adr, DataLen=DataLen, CRCAdr=CRCAdr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Lg_MakeMIMCRC(Command):
    CommandGroupId = 0x11
    CommandId = 0x0A
    def build_frame(self, Adr: int, Len: int, CRCAdr: int, BrpTimeout: int = 1500) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CRCAdr.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, Len: int, CRCAdr: int, BrpTimeout: int = 1500) -> None:
        request_frame = self.build_frame(Adr=Adr, Len=Len, CRCAdr=CRCAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Lg_ReadSMStatus(Command):
    CommandGroupId = 0x11
    CommandId = 0x0D
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x0D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Lg_ReadSMStatus_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RFU = _recv_buffer.read(3)
        if len(_RFU) != 3:
            raise PayloadTooShortError(3 - len(_RFU))
        _SWV = safe_read_int_from_buffer(_recv_buffer, 1)
        _SmStat = safe_read_int_from_buffer(_recv_buffer, 1)
        _HfPow = safe_read_int_from_buffer(_recv_buffer, 1)
        _MIMStat_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _NoMIM = bool((_MIMStat_int >> 4) & 0b1)
        _MIMVersion = Lg_ReadSMStatus_MIMVersion_Parser.as_literal((_MIMStat_int >> 0) & 0b11)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Lg_ReadSMStatus_Result(_RFU, _SWV, _SmStat, _HfPow, _NoMIM, _MIMVersion)
class Lg_SetPassword(Command):
    CommandGroupId = 0x11
    CommandId = 0x0E
    def build_frame(self, Password: bytes, BrpTimeout: int = 2500) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x0E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Password) != 4:
            raise ValueError(Password)
        _send_buffer.write(Password)
        return _send_buffer.getvalue()
    def __call__(self, Password: bytes, BrpTimeout: int = 2500) -> Lg_SetPassword_PwdStat:
        request_frame = self.build_frame(Password=Password, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PwdStat = Lg_SetPassword_PwdStat_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PwdStat
class Lg_Lock(Command):
    CommandGroupId = 0x11
    CommandId = 0x0F
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x0F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Lg_Lock_PwdStat:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PwdStat = Lg_Lock_PwdStat_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PwdStat
class Lg_Unlock(Command):
    CommandGroupId = 0x11
    CommandId = 0x10
    def build_frame(self, Password: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x11\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Password) != 4:
            raise ValueError(Password)
        _send_buffer.write(Password)
        return _send_buffer.getvalue()
    def __call__(self, Password: bytes, BrpTimeout: int = 100) -> Lg_Unlock_PwdStat:
        request_frame = self.build_frame(Password=Password, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PwdStat = Lg_Unlock_PwdStat_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PwdStat
class Lga_TransparentCommand(Command):
    CommandGroupId = 0x12
    CommandId = 0x20
    def build_frame(self, CmdCode: int, CmdParams: bytes, Timeout: int = 100, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x12\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(CmdParams)).to_bytes(1, byteorder='big'))
        _send_buffer.write(CmdParams)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCode: int, CmdParams: bytes, Timeout: int = 100, BrpTimeout: int = 3000) -> Lga_TransparentCommand_Result:
        request_frame = self.build_frame(CmdCode=CmdCode, CmdParams=CmdParams, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Lga_TransparentCommand_Result(_Status, _Resp)
class Lic_GetLicenses(Command):
    CommandGroupId = 0x0B
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0B\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> LicenseBitMask:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LicenseBitMask_int = safe_read_int_from_buffer(_recv_buffer, 4)
        _Ble = bool((_LicenseBitMask_int >> 3) & 0b1)
        _BleLicRequired = bool((_LicenseBitMask_int >> 2) & 0b1)
        _HidOnlyForSE = bool((_LicenseBitMask_int >> 1) & 0b1)
        _Hid = bool((_LicenseBitMask_int >> 0) & 0b1)
        _LicenseBitMask = LicenseBitMask(_Ble, _BleLicRequired, _HidOnlyForSE, _Hid)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LicenseBitMask
class Lic_ReadLicCard(Command):
    CommandGroupId = 0x0B
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0B\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Main_Bf2Upload(Command):
    CommandGroupId = 0xF0
    CommandId = 0x01
    def build_frame(self, Bf2Line: bytes, BrpTimeout: int = 5000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF0\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Bf2Line)
        return _send_buffer.getvalue()
    def __call__(self, Bf2Line: bytes, BrpTimeout: int = 5000) -> Main_Bf2Upload_Result:
        request_frame = self.build_frame(Bf2Line=Bf2Line, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ResultCode = Main_Bf2Upload_ResultCode_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _InvertedResultCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Main_Bf2Upload_Result(_ResultCode, _InvertedResultCode)
class Main_SwitchFW(Command):
    CommandGroupId = 0xF0
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF0\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Main_MatchPlatformId2(Command):
    CommandGroupId = 0xF0
    CommandId = 0x04
    def build_frame(self, Filter: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF0\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Filter)
        return _send_buffer.getvalue()
    def __call__(self, Filter: bytes, BrpTimeout: int = 100) -> bool:
        request_frame = self.build_frame(Filter=Filter, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Matches = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Matches
class Main_IsFirmwareUpToDate(Command):
    CommandGroupId = 0xF0
    CommandId = 0x05
    def build_frame(self, VersionDesc: bytes, BrpTimeout: int = 5000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF0\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(VersionDesc)).to_bytes(1, byteorder='big'))
        _send_buffer.write(VersionDesc)
        return _send_buffer.getvalue()
    def __call__(self, VersionDesc: bytes, BrpTimeout: int = 5000) -> None:
        request_frame = self.build_frame(VersionDesc=VersionDesc, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Main_Bf3UploadStart(Command):
    CommandGroupId = 0xF0
    CommandId = 0x10
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF0\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Main_Bf3UploadStart_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReqDataAdr = safe_read_int_from_buffer(_recv_buffer, 4)
        _ReqDataLen = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Main_Bf3UploadStart_Result(_ReqDataAdr, _ReqDataLen)
class Main_Bf3UploadContinue(Command):
    CommandGroupId = 0xF0
    CommandId = 0x11
    def build_frame(self, DataAdr: int, Data: bytes, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xF0\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DataAdr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, DataAdr: int, Data: bytes, BrpTimeout: int = 1000) -> Main_Bf3UploadContinue_Result:
        request_frame = self.build_frame(DataAdr=DataAdr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RequiredAction_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _Reconnect = bool((_RequiredAction_int >> 1) & 0b1)
        _Continue = bool((_RequiredAction_int >> 0) & 0b1)
        _ReqDataAdr = safe_read_int_from_buffer(_recv_buffer, 4)
        _ReqDataLen = safe_read_int_from_buffer(_recv_buffer, 2)
        _AdditionalFields_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _ContainsEstimation = bool((_AdditionalFields_int >> 1) & 0b1)
        _ContainsReconnectRetryTimeout = bool((_AdditionalFields_int >> 0) & 0b1)
        if _ContainsReconnectRetryTimeout:
            _ReconnectRetryTimeout = safe_read_int_from_buffer(_recv_buffer, 4)
        else:
            _ReconnectRetryTimeout = None
        if _ContainsEstimation:
            _EstimatedNumberOfBytes = safe_read_int_from_buffer(_recv_buffer, 4)
            _EstimatedTimeOverhead = safe_read_int_from_buffer(_recv_buffer, 4)
        else:
            _EstimatedNumberOfBytes = None
            _EstimatedTimeOverhead = None
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Main_Bf3UploadContinue_Result(_Reconnect, _Continue, _ReqDataAdr, _ReqDataLen, _ContainsEstimation, _ContainsReconnectRetryTimeout, _ReconnectRetryTimeout, _EstimatedNumberOfBytes, _EstimatedTimeOverhead)
class Mce_Enable(Command):
    CommandGroupId = 0x4D
    CommandId = 0x01
    def build_frame(self, Mode: Mce_Enable_Mode, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4D\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mce_Enable_Mode_Parser.as_value(Mode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: Mce_Enable_Mode, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mce_Request(Command):
    CommandGroupId = 0x4D
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4D\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Snr_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Snr = _recv_buffer.read(_Snr_len)
        if len(_Snr) != _Snr_len:
            raise PayloadTooShortError(_Snr_len - len(_Snr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Snr
class Mif_LoadKey(Command):
    CommandGroupId = 0x10
    CommandId = 0x00
    def build_frame(self, KeyIdx: int, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(KeyIdx.to_bytes(length=1, byteorder='big'))
        if len(Key) != 6:
            raise ValueError(Key)
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, KeyIdx: int, Key: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(KeyIdx=KeyIdx, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_Request(Command):
    CommandGroupId = 0x10
    CommandId = 0x01
    def build_frame(self, ReqAll: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (ReqAll & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ReqAll: int = 0, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(ReqAll=ReqAll, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATQA = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ATQA
class Mif_Anticoll(Command):
    CommandGroupId = 0x10
    CommandId = 0x02
    def build_frame(self, BitCount: int = 0, *, PreSelSer: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BitCount.to_bytes(length=1, byteorder='big'))
        if len(PreSelSer) != 4:
            raise ValueError(PreSelSer)
        _send_buffer.write(PreSelSer)
        return _send_buffer.getvalue()
    def __call__(self, BitCount: int = 0, *, PreSelSer: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BitCount=BitCount, PreSelSer=PreSelSer, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Snr = _recv_buffer.read(4)
        if len(_Snr) != 4:
            raise PayloadTooShortError(4 - len(_Snr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Snr
class Mif_Select(Command):
    CommandGroupId = 0x10
    CommandId = 0x03
    def build_frame(self, Snr: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        return _send_buffer.getvalue()
    def __call__(self, Snr: bytes, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(Snr=Snr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SAK = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _SAK
class Mif_AuthE2(Command):
    CommandGroupId = 0x10
    CommandId = 0x04
    def build_frame(self, AuthMode: int = 96, *, Block: int, KeyIdx: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AuthMode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(KeyIdx.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AuthMode: int = 96, *, Block: int, KeyIdx: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AuthMode=AuthMode, Block=Block, KeyIdx=KeyIdx, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_AuthUser(Command):
    CommandGroupId = 0x10
    CommandId = 0x05
    def build_frame(self, AuthMode: int = 96, *, Block: int, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AuthMode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        if len(Key) != 6:
            raise ValueError(Key)
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, AuthMode: int = 96, *, Block: int, Key: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AuthMode=AuthMode, Block=Block, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_Read(Command):
    CommandGroupId = 0x10
    CommandId = 0x06
    def build_frame(self, Block: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Block: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Block=Block, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BlockData = _recv_buffer.read(16)
        if len(_BlockData) != 16:
            raise PayloadTooShortError(16 - len(_BlockData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _BlockData
class Mif_Write(Command):
    CommandGroupId = 0x10
    CommandId = 0x07
    def build_frame(self, Block: int, BlockData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        if len(BlockData) != 16:
            raise ValueError(BlockData)
        _send_buffer.write(BlockData)
        return _send_buffer.getvalue()
    def __call__(self, Block: int, BlockData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Block=Block, BlockData=BlockData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_ChangeValue(Command):
    CommandGroupId = 0x10
    CommandId = 0x08
    def build_frame(self, Mode: int, Block: int, Value: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Value.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: int, Block: int, Value: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Mode=Mode, Block=Block, Value=Value, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_ChangeValueBackup(Command):
    CommandGroupId = 0x10
    CommandId = 0x09
    def build_frame(self, Mode: int, Block: int, Value: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Value.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: int, Block: int, Value: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Mode=Mode, Block=Block, Value=Value, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_TransferBlock(Command):
    CommandGroupId = 0x10
    CommandId = 0x0A
    def build_frame(self, Block: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Block: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Block=Block, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_Halt(Command):
    CommandGroupId = 0x10
    CommandId = 0x0B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x0B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_AuthE2Extended(Command):
    CommandGroupId = 0x10
    CommandId = 0x10
    def build_frame(self, AuthLevel: int = 2, KeyHasExtIdx: bool = False, EV1Mode: int = 0, IsKeyB: bool = False, Block: int = 16384, *, KeyIdx: int, KeyExtIdx: Optional[int] = 0, DivData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (AuthLevel & 0b11) << 6
        _var_0000_int |= (int(KeyHasExtIdx) & 0b1) << 2
        _var_0000_int |= (EV1Mode & 0b1) << 1
        _var_0000_int |= (int(IsKeyB) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(KeyIdx.to_bytes(length=1, byteorder='big'))
        if KeyHasExtIdx:
            if KeyExtIdx is None:
                raise TypeError("missing a required argument: 'KeyExtIdx'")
            _send_buffer.write(KeyExtIdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(DivData)
        return _send_buffer.getvalue()
    def __call__(self, AuthLevel: int = 2, KeyHasExtIdx: bool = False, EV1Mode: int = 0, IsKeyB: bool = False, Block: int = 16384, *, KeyIdx: int, KeyExtIdx: Optional[int] = 0, DivData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AuthLevel=AuthLevel, KeyHasExtIdx=KeyHasExtIdx, EV1Mode=EV1Mode, IsKeyB=IsKeyB, Block=Block, KeyIdx=KeyIdx, KeyExtIdx=KeyExtIdx, DivData=DivData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_AuthUserExtended(Command):
    CommandGroupId = 0x10
    CommandId = 0x11
    def build_frame(self, AuthLevel: int = 2, EV1Mode: int = 0, KeyB: int = 0, Block: int = 16384, *, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (AuthLevel & 0b11) << 6
        _var_0000_int |= (EV1Mode & 0b1) << 1
        _var_0000_int |= (KeyB & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, AuthLevel: int = 2, EV1Mode: int = 0, KeyB: int = 0, Block: int = 16384, *, Key: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AuthLevel=AuthLevel, EV1Mode=EV1Mode, KeyB=KeyB, Block=Block, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_ResetAuth(Command):
    CommandGroupId = 0x10
    CommandId = 0x12
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_ReadSL3(Command):
    CommandGroupId = 0x10
    CommandId = 0x13
    def build_frame(self, NoMacOnCmd: int = 0, PlainData: int = 0, NoMacOnResp: int = 0, *, Block: int, BlockNr: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x13")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (NoMacOnCmd & 0b1) << 2
        _var_0000_int |= (PlainData & 0b1) << 1
        _var_0000_int |= (NoMacOnResp & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(BlockNr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, NoMacOnCmd: int = 0, PlainData: int = 0, NoMacOnResp: int = 0, *, Block: int, BlockNr: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(NoMacOnCmd=NoMacOnCmd, PlainData=PlainData, NoMacOnResp=NoMacOnResp, Block=Block, BlockNr=BlockNr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BlockData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _BlockData = _recv_buffer.read(_BlockData_len)
        if len(_BlockData) != _BlockData_len:
            raise PayloadTooShortError(_BlockData_len - len(_BlockData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _BlockData
class Mif_WriteSL3(Command):
    CommandGroupId = 0x10
    CommandId = 0x14
    def build_frame(self, PlainData: int = 0, NoMacOnResp: int = 0, *, Block: int, BlockData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x14")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (PlainData & 0b1) << 1
        _var_0000_int |= (NoMacOnResp & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(BlockData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(BlockData)
        return _send_buffer.getvalue()
    def __call__(self, PlainData: int = 0, NoMacOnResp: int = 0, *, Block: int, BlockData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PlainData=PlainData, NoMacOnResp=NoMacOnResp, Block=Block, BlockData=BlockData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_ChangeAESKey(Command):
    CommandGroupId = 0x10
    CommandId = 0x15
    def build_frame(self, KeyHasExtIdx: bool = False, NoMacOnResp: int = 0, *, Block: int, KeyIdx: int, KeyExtIdx: Optional[int] = 0, DivData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x15")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(KeyHasExtIdx) & 0b1) << 3
        _var_0000_int |= (NoMacOnResp & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(KeyIdx.to_bytes(length=1, byteorder='big'))
        if KeyHasExtIdx:
            if KeyExtIdx is None:
                raise TypeError("missing a required argument: 'KeyExtIdx'")
            _send_buffer.write(KeyExtIdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(DivData)
        return _send_buffer.getvalue()
    def __call__(self, KeyHasExtIdx: bool = False, NoMacOnResp: int = 0, *, Block: int, KeyIdx: int, KeyExtIdx: Optional[int] = 0, DivData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(KeyHasExtIdx=KeyHasExtIdx, NoMacOnResp=NoMacOnResp, Block=Block, KeyIdx=KeyIdx, KeyExtIdx=KeyExtIdx, DivData=DivData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_ValueSL3(Command):
    CommandGroupId = 0x10
    CommandId = 0x16
    def build_frame(self, NoMacOnResp: int = 0, *, Cmd: int, Block: int, DestBlock: Optional[int] = None, Value: Optional[int] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x16")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (NoMacOnResp & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Cmd.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        if Cmd == 3 or Cmd == 4:
            if DestBlock is None:
                raise TypeError("missing a required argument: 'DestBlock'")
            _send_buffer.write(DestBlock.to_bytes(length=2, byteorder='big'))
        if Cmd == 0 or Cmd == 1 or Cmd == 3 or Cmd == 4:
            if Value is None:
                raise TypeError("missing a required argument: 'Value'")
            _send_buffer.write(Value.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, NoMacOnResp: int = 0, *, Cmd: int, Block: int, DestBlock: Optional[int] = None, Value: Optional[int] = None, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(NoMacOnResp=NoMacOnResp, Cmd=Cmd, Block=Block, DestBlock=DestBlock, Value=Value, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _TMCounterTMValue_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _TMCounterTMValue = _recv_buffer.read(_TMCounterTMValue_len)
        if len(_TMCounterTMValue) != _TMCounterTMValue_len:
            raise PayloadTooShortError(_TMCounterTMValue_len - len(_TMCounterTMValue))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _TMCounterTMValue
class Mif_ProxCheck(Command):
    CommandGroupId = 0x10
    CommandId = 0x17
    def build_frame(self, M: int = 4, DisableIsoWrapping: int = 0, UseExtProxKey: bool = False, DiversifyProxKey: bool = False, UseProxKey: bool = False, ProxKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, ProxKey: Optional[bytes] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x17")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (M & 0b111) << 4
        _var_0000_int |= (DisableIsoWrapping & 0b1) << 3
        _var_0000_int |= (int(UseExtProxKey) & 0b1) << 2
        _var_0000_int |= (int(DiversifyProxKey) & 0b1) << 1
        _var_0000_int |= (int(UseProxKey) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if UseProxKey:
            if ProxKeyIdx is None:
                raise TypeError("missing a required argument: 'ProxKeyIdx'")
            _send_buffer.write(ProxKeyIdx.to_bytes(length=2, byteorder='big'))
        if DiversifyProxKey and UseProxKey:
            if DivData is None:
                raise TypeError("missing a required argument: 'DivData'")
            _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(DivData)
        if UseExtProxKey:
            if ProxKey is None:
                raise TypeError("missing a required argument: 'ProxKey'")
            _send_buffer.write(int(len(ProxKey)).to_bytes(1, byteorder='big'))
            _send_buffer.write(ProxKey)
        return _send_buffer.getvalue()
    def __call__(self, M: int = 4, DisableIsoWrapping: int = 0, UseExtProxKey: bool = False, DiversifyProxKey: bool = False, UseProxKey: bool = False, ProxKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, ProxKey: Optional[bytes] = None, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(M=M, DisableIsoWrapping=DisableIsoWrapping, UseExtProxKey=UseExtProxKey, DiversifyProxKey=DiversifyProxKey, UseProxKey=UseProxKey, ProxKeyIdx=ProxKeyIdx, DivData=DivData, ProxKey=ProxKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_GetCardVersion(Command):
    CommandGroupId = 0x10
    CommandId = 0x18
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x18")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _CardVersion_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _CardVersion = _recv_buffer.read(_CardVersion_len)
        if len(_CardVersion) != _CardVersion_len:
            raise PayloadTooShortError(_CardVersion_len - len(_CardVersion))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _CardVersion
class Mif_ReadSig(Command):
    CommandGroupId = 0x10
    CommandId = 0x19
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x19")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _NxpSignature_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _NxpSignature = _recv_buffer.read(_NxpSignature_len)
        if len(_NxpSignature) != _NxpSignature_len:
            raise PayloadTooShortError(_NxpSignature_len - len(_NxpSignature))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _NxpSignature
class Mif_VirtualCardSelect(Command):
    CommandGroupId = 0x10
    CommandId = 0x1A
    def build_frame(self, ForceVcsAuthentication: bool = False, UseExtVcSelectKeys: bool = False, DiversifyMacKey: int = 0, DiversifyEncKey: bool = False, UseVcSelectKeys: bool = False, *, IID: bytes, EncKeyIdx: Optional[int] = None, MacKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, EncKey: Optional[bytes] = None, MacKey: Optional[bytes] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x1A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ForceVcsAuthentication) & 0b1) << 5
        _var_0000_int |= (int(UseExtVcSelectKeys) & 0b1) << 4
        _var_0000_int |= (DiversifyMacKey & 0b11) << 2
        _var_0000_int |= (int(DiversifyEncKey) & 0b1) << 1
        _var_0000_int |= (int(UseVcSelectKeys) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(IID)).to_bytes(1, byteorder='big'))
        _send_buffer.write(IID)
        if UseVcSelectKeys:
            if EncKeyIdx is None:
                raise TypeError("missing a required argument: 'EncKeyIdx'")
            if MacKeyIdx is None:
                raise TypeError("missing a required argument: 'MacKeyIdx'")
            _send_buffer.write(EncKeyIdx.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(MacKeyIdx.to_bytes(length=2, byteorder='big'))
        if DiversifyMacKey == 1 or DiversifyMacKey == 2 or DiversifyMacKey == 3 or DiversifyEncKey:
            if DivData is None:
                raise TypeError("missing a required argument: 'DivData'")
            _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
            _send_buffer.write(DivData)
        if UseExtVcSelectKeys:
            if EncKey is None:
                raise TypeError("missing a required argument: 'EncKey'")
            if MacKey is None:
                raise TypeError("missing a required argument: 'MacKey'")
            _send_buffer.write(int(len(EncKey)).to_bytes(1, byteorder='big'))
            _send_buffer.write(EncKey)
            _send_buffer.write(int(len(MacKey)).to_bytes(1, byteorder='big'))
            _send_buffer.write(MacKey)
        return _send_buffer.getvalue()
    def __call__(self, ForceVcsAuthentication: bool = False, UseExtVcSelectKeys: bool = False, DiversifyMacKey: int = 0, DiversifyEncKey: bool = False, UseVcSelectKeys: bool = False, *, IID: bytes, EncKeyIdx: Optional[int] = None, MacKeyIdx: Optional[int] = None, DivData: Optional[bytes] = None, EncKey: Optional[bytes] = None, MacKey: Optional[bytes] = None, BrpTimeout: int = 100) -> Mif_VirtualCardSelect_Result:
        request_frame = self.build_frame(ForceVcsAuthentication=ForceVcsAuthentication, UseExtVcSelectKeys=UseExtVcSelectKeys, DiversifyMacKey=DiversifyMacKey, DiversifyEncKey=DiversifyEncKey, UseVcSelectKeys=UseVcSelectKeys, IID=IID, EncKeyIdx=EncKeyIdx, MacKeyIdx=MacKeyIdx, DivData=DivData, EncKey=EncKey, MacKey=MacKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FciType = safe_read_int_from_buffer(_recv_buffer, 1)
        _Fci_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Fci = _recv_buffer.read(_Fci_len)
        if len(_Fci) != _Fci_len:
            raise PayloadTooShortError(_Fci_len - len(_Fci))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Mif_VirtualCardSelect_Result(_FciType, _Fci)
class Mif_SectorSwitch(Command):
    CommandGroupId = 0x10
    CommandId = 0x1B
    def build_frame(self, L3SectorSwitch: bool = True, *, SectorSwitchKeyIdx: int, SectorSwitchKeyDivData: bytes, SectorSpec: List[Mif_SectorSwitch_SectorSpec_Entry], SectorKeysDivData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x1B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(L3SectorSwitch) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SectorSwitchKeyIdx.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(SectorSwitchKeyDivData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(SectorSwitchKeyDivData)
        _send_buffer.write(int(len(SectorSpec)).to_bytes(1, byteorder='big'))
        for _SectorSpec_Entry in SectorSpec:
            _BlockAddress, _SectorKeyIdx = _SectorSpec_Entry
            _send_buffer.write(_BlockAddress.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(_SectorKeyIdx.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(SectorKeysDivData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(SectorKeysDivData)
        return _send_buffer.getvalue()
    def __call__(self, L3SectorSwitch: bool = True, *, SectorSwitchKeyIdx: int, SectorSwitchKeyDivData: bytes, SectorSpec: List[Mif_SectorSwitch_SectorSpec_Entry], SectorKeysDivData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(L3SectorSwitch=L3SectorSwitch, SectorSwitchKeyIdx=SectorSwitchKeyIdx, SectorSwitchKeyDivData=SectorSwitchKeyDivData, SectorSpec=SectorSpec, SectorKeysDivData=SectorKeysDivData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Mif_CommitReaderID(Command):
    CommandGroupId = 0x10
    CommandId = 0x1D
    def build_frame(self, Block: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x1D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Block.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Block: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Block=Block, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EncTRI_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _EncTRI = _recv_buffer.read(_EncTRI_len)
        if len(_EncTRI) != _EncTRI_len:
            raise PayloadTooShortError(_EncTRI_len - len(_EncTRI))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _EncTRI
class Mif_SetFraming(Command):
    CommandGroupId = 0x10
    CommandId = 0x1C
    def build_frame(self, CommMode: Mif_SetFraming_CommMode = "MifareNative", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x10\x1C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mif_SetFraming_CommMode_Parser.as_value(CommMode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CommMode: Mif_SetFraming_CommMode = "MifareNative", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CommMode=CommMode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class MobileId_Enable(Command):
    CommandGroupId = 0x4C
    CommandId = 0x01
    def build_frame(self, Mode: MobileId_Enable_Mode, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4C\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(MobileId_Enable_Mode_Parser.as_value(Mode).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: MobileId_Enable_Mode, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class MobileId_GetVirtualCredentialId(Command):
    CommandGroupId = 0x4C
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x4C\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _CredentialId_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _CredentialId = _recv_buffer.read(_CredentialId_len)
        if len(_CredentialId) != _CredentialId_len:
            raise PayloadTooShortError(_CredentialId_len - len(_CredentialId))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _CredentialId
class MsgQueue_GetMsgSize(Command):
    CommandGroupId = 0xA6
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA6\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BufferSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _BufferSize
class MsgQueue_Receive(Command):
    CommandGroupId = 0xA6
    CommandId = 0x01
    def build_frame(self, Timeout: int = 5000, BrpTimeout: int = 5000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA6\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Timeout: int = 5000, BrpTimeout: int = 5000) -> bytes:
        request_frame = self.build_frame(Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvMsg_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvMsg = _recv_buffer.read(_RecvMsg_len)
        if len(_RecvMsg) != _RecvMsg_len:
            raise PayloadTooShortError(_RecvMsg_len - len(_RecvMsg))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvMsg
class MsgQueue_Send(Command):
    CommandGroupId = 0xA6
    CommandId = 0x02
    def build_frame(self, SendMsg: bytes, Timeout: int = 5000, BrpTimeout: int = 5000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA6\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SendMsg)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendMsg)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SendMsg: bytes, Timeout: int = 5000, BrpTimeout: int = 5000) -> None:
        request_frame = self.build_frame(SendMsg=SendMsg, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class MsgQueue_SendReceive(Command):
    CommandGroupId = 0xA6
    CommandId = 0x03
    def build_frame(self, SendMsg: bytes, Timeout: int = 5000, BrpTimeout: int = 5000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA6\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SendMsg)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendMsg)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SendMsg: bytes, Timeout: int = 5000, BrpTimeout: int = 5000) -> bytes:
        request_frame = self.build_frame(SendMsg=SendMsg, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvMsg_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvMsg = _recv_buffer.read(_RecvMsg_len)
        if len(_RecvMsg) != _RecvMsg_len:
            raise PayloadTooShortError(_RecvMsg_len - len(_RecvMsg))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvMsg
class Pico_SetHfMode(Command):
    CommandGroupId = 0x1A
    CommandId = 0x00
    def build_frame(self, HfMode: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(HfMode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, HfMode: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(HfMode=HfMode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Pico_RequestAnticoll(Command):
    CommandGroupId = 0x1A
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ASNB_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ASNB = _recv_buffer.read(_ASNB_len)
        if len(_ASNB) != _ASNB_len:
            raise PayloadTooShortError(_ASNB_len - len(_ASNB))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ASNB
class Pico_Select(Command):
    CommandGroupId = 0x1A
    CommandId = 0x02
    def build_frame(self, ASNB: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(ASNB)).to_bytes(1, byteorder='big'))
        _send_buffer.write(ASNB)
        return _send_buffer.getvalue()
    def __call__(self, ASNB: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(ASNB=ASNB, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Serial_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Serial = _recv_buffer.read(_Serial_len)
        if len(_Serial) != _Serial_len:
            raise PayloadTooShortError(_Serial_len - len(_Serial))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Serial
class Pico_Halt(Command):
    CommandGroupId = 0x1A
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Pico_SelectBookPage(Command):
    CommandGroupId = 0x1A
    CommandId = 0x04
    def build_frame(self, Book: int = 0, Page: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Book.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Page.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Book: int = 0, Page: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Book=Book, Page=Page, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Page1_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Page1 = _recv_buffer.read(_Page1_len)
        if len(_Page1) != _Page1_len:
            raise PayloadTooShortError(_Page1_len - len(_Page1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Page1
class Pico_Authenticate(Command):
    CommandGroupId = 0x1A
    CommandId = 0x05
    def build_frame(self, IsDebitKey: bool = False, KeyIdx: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(IsDebitKey.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(KeyIdx.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, IsDebitKey: bool = False, KeyIdx: int = 0, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(IsDebitKey=IsDebitKey, KeyIdx=KeyIdx, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Pico_Read(Command):
    CommandGroupId = 0x1A
    CommandId = 0x06
    def build_frame(self, PageAdr: int = 0, PageNr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PageAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(PageNr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PageAdr: int = 0, PageNr: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(PageAdr=PageAdr, PageNr=PageNr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PageData_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _PageData = _recv_buffer.read(_PageData_len)
        if len(_PageData) != _PageData_len:
            raise PayloadTooShortError(_PageData_len - len(_PageData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PageData
class Pico_Write(Command):
    CommandGroupId = 0x1A
    CommandId = 0x07
    def build_frame(self, PageAdr: int = 0, *, PageData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x1A\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PageAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(PageData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(PageData)
        return _send_buffer.getvalue()
    def __call__(self, PageAdr: int = 0, *, PageData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PageAdr=PageAdr, PageData=PageData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Pki_PfsGenKey(Command):
    CommandGroupId = 0x09
    CommandId = 0x01
    def build_frame(self, TmpHostPubKey: bytes, BrpTimeout: int = 16000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(TmpHostPubKey)).to_bytes(2, byteorder='big'))
        _send_buffer.write(TmpHostPubKey)
        return _send_buffer.getvalue()
    def __call__(self, TmpHostPubKey: bytes, BrpTimeout: int = 16000) -> bytes:
        request_frame = self.build_frame(TmpHostPubKey=TmpHostPubKey, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _TmpRdrPubKey_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _TmpRdrPubKey = _recv_buffer.read(_TmpRdrPubKey_len)
        if len(_TmpRdrPubKey) != _TmpRdrPubKey_len:
            raise PayloadTooShortError(_TmpRdrPubKey_len - len(_TmpRdrPubKey))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _TmpRdrPubKey
class Pki_PfsAuthHostCert(Command):
    CommandGroupId = 0x09
    CommandId = 0x02
    def build_frame(self, EncryptedPayload: bytes, BrpTimeout: int = 16000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(EncryptedPayload)).to_bytes(2, byteorder='big'))
        _send_buffer.write(EncryptedPayload)
        return _send_buffer.getvalue()
    def __call__(self, EncryptedPayload: bytes, BrpTimeout: int = 16000) -> None:
        request_frame = self.build_frame(EncryptedPayload=EncryptedPayload, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Pki_PfsAuthRdrCert(Command):
    CommandGroupId = 0x09
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 16000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 16000) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EncryptedResponse_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _EncryptedResponse = _recv_buffer.read(_EncryptedResponse_len)
        if len(_EncryptedResponse) != _EncryptedResponse_len:
            raise PayloadTooShortError(_EncryptedResponse_len - len(_EncryptedResponse))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _EncryptedResponse
class Pki_Tunnel2(Command):
    CommandGroupId = 0x09
    CommandId = 0x04
    def build_frame(self, SequenceCounter: int, CmdHMAC: bytes, EncryptedCmd: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SequenceCounter.to_bytes(length=4, byteorder='big'))
        if len(CmdHMAC) != 16:
            raise ValueError(CmdHMAC)
        _send_buffer.write(CmdHMAC)
        _send_buffer.write(int(len(EncryptedCmd)).to_bytes(2, byteorder='big'))
        _send_buffer.write(EncryptedCmd)
        return _send_buffer.getvalue()
    def __call__(self, SequenceCounter: int, CmdHMAC: bytes, EncryptedCmd: bytes, BrpTimeout: int = 100) -> Pki_Tunnel2_Result:
        request_frame = self.build_frame(SequenceCounter=SequenceCounter, CmdHMAC=CmdHMAC, EncryptedCmd=EncryptedCmd, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RspHMAC = _recv_buffer.read(16)
        if len(_RspHMAC) != 16:
            raise PayloadTooShortError(16 - len(_RspHMAC))
        _EncryptedRsp_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _EncryptedRsp = _recv_buffer.read(_EncryptedRsp_len)
        if len(_EncryptedRsp) != _EncryptedRsp_len:
            raise PayloadTooShortError(_EncryptedRsp_len - len(_EncryptedRsp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Pki_Tunnel2_Result(_RspHMAC, _EncryptedRsp)
class Pki_GetX509Csr(Command):
    CommandGroupId = 0x09
    CommandId = 0x10
    def build_frame(self, BrpTimeout: int = 16000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 16000) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Csr_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Csr = _recv_buffer.read(_Csr_len)
        if len(_Csr) != _Csr_len:
            raise PayloadTooShortError(_Csr_len - len(_Csr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Csr
class Pki_StoreX509Cert(Command):
    CommandGroupId = 0x09
    CommandId = 0x11
    def build_frame(self, SecLevel: int, Cert: bytes, BrpTimeout: int = 16000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SecLevel.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Cert)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Cert)
        return _send_buffer.getvalue()
    def __call__(self, SecLevel: int, Cert: bytes, BrpTimeout: int = 16000) -> None:
        request_frame = self.build_frame(SecLevel=SecLevel, Cert=Cert, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Pki_StoreX509RootCert(Command):
    CommandGroupId = 0x09
    CommandId = 0x12
    def build_frame(self, SecLevel: int, Cert: bytes, BrpTimeout: int = 16000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x09\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SecLevel.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Cert)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Cert)
        return _send_buffer.getvalue()
    def __call__(self, SecLevel: int, Cert: bytes, BrpTimeout: int = 16000) -> None:
        request_frame = self.build_frame(SecLevel=SecLevel, Cert=Cert, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class QKey_Read(Command):
    CommandGroupId = 0x35
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x35\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class Rtc_GetTime(Command):
    CommandGroupId = 0x04
    CommandId = 0x00
    def build_frame(self, ClockId: int = 255, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x04\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ClockId.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ClockId: int = 255, BrpTimeout: int = 100) -> Time:
        request_frame = self.build_frame(ClockId=ClockId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Now = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Now
class Rtc_SetTime(Command):
    CommandGroupId = 0x04
    CommandId = 0x01
    def build_frame(self, ClockId: int = 255, *, Now: Time, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x04\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ClockId.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Now.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ClockId: int = 255, *, Now: Time, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ClockId=ClockId, Now=Now, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sec_GetAcMask(Command):
    CommandGroupId = 0x07
    CommandId = 0x01
    def build_frame(self, SecLevel: int = 255, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SecLevel.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SecLevel: int = 255, BrpTimeout: int = 100) -> HostSecurityAccessConditionBits:
        request_frame = self.build_frame(SecLevel=SecLevel, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _AcMask_int = safe_read_int_from_buffer(_recv_buffer, 4)
        _EthernetAccess = bool((_AcMask_int >> 28) & 0b1)
        _AutoreadAccess = bool((_AcMask_int >> 27) & 0b1)
        _CryptoAccess = bool((_AcMask_int >> 26) & 0b1)
        _Bf2Upload = bool((_AcMask_int >> 25) & 0b1)
        _ExtendedAccess = bool((_AcMask_int >> 24) & 0b1)
        _FlashFileSystemWrite = bool((_AcMask_int >> 23) & 0b1)
        _FlashFileSystemRead = bool((_AcMask_int >> 22) & 0b1)
        _RtcWrite = bool((_AcMask_int >> 21) & 0b1)
        _VhlExchangeapdu = bool((_AcMask_int >> 20) & 0b1)
        _VhlFormat = bool((_AcMask_int >> 19) & 0b1)
        _VhlWrite = bool((_AcMask_int >> 18) & 0b1)
        _VhlRead = bool((_AcMask_int >> 17) & 0b1)
        _VhlSelect = bool((_AcMask_int >> 16) & 0b1)
        _ExtSamAccess = bool((_AcMask_int >> 15) & 0b1)
        _HfLowlevelAccess = bool((_AcMask_int >> 14) & 0b1)
        _GuiAccess = bool((_AcMask_int >> 13) & 0b1)
        _IoPortWrite = bool((_AcMask_int >> 12) & 0b1)
        _IoPortRead = bool((_AcMask_int >> 11) & 0b1)
        _ConfigReset = bool((_AcMask_int >> 10) & 0b1)
        _ConfigWrite = bool((_AcMask_int >> 9) & 0b1)
        _ConfigRead = bool((_AcMask_int >> 8) & 0b1)
        _SysReset = bool((_AcMask_int >> 7) & 0b1)
        _SetAccessConditionMask2 = bool((_AcMask_int >> 6) & 0b1)
        _SetAccessConditionMask1 = bool((_AcMask_int >> 5) & 0b1)
        _SetAccessConditionMask0 = bool((_AcMask_int >> 4) & 0b1)
        _SetKey3 = bool((_AcMask_int >> 3) & 0b1)
        _SetKey2 = bool((_AcMask_int >> 2) & 0b1)
        _SetKey1 = bool((_AcMask_int >> 1) & 0b1)
        _FactoryReset = bool((_AcMask_int >> 0) & 0b1)
        _AcMask = HostSecurityAccessConditionBits(_EthernetAccess, _AutoreadAccess, _CryptoAccess, _Bf2Upload, _ExtendedAccess, _FlashFileSystemWrite, _FlashFileSystemRead, _RtcWrite, _VhlExchangeapdu, _VhlFormat, _VhlWrite, _VhlRead, _VhlSelect, _ExtSamAccess, _HfLowlevelAccess, _GuiAccess, _IoPortWrite, _IoPortRead, _ConfigReset, _ConfigWrite, _ConfigRead, _SysReset, _SetAccessConditionMask2, _SetAccessConditionMask1, _SetAccessConditionMask0, _SetKey3, _SetKey2, _SetKey1, _FactoryReset)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _AcMask
class Sec_SetAcMask(Command):
    CommandGroupId = 0x07
    CommandId = 0x02
    def build_frame(self, SecLevel: int = 255, *, AcMask: Union[HostSecurityAccessConditionBits, HostSecurityAccessConditionBits_Dict], BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SecLevel.to_bytes(length=1, byteorder='big'))
        if isinstance(AcMask, dict):
            AcMask = HostSecurityAccessConditionBits(**AcMask)
        AcMask_int = 0
        AcMask_int |= (int(AcMask.EthernetAccess) & 0b1) << 28
        AcMask_int |= (int(AcMask.AutoreadAccess) & 0b1) << 27
        AcMask_int |= (int(AcMask.CryptoAccess) & 0b1) << 26
        AcMask_int |= (int(AcMask.Bf2Upload) & 0b1) << 25
        AcMask_int |= (int(AcMask.ExtendedAccess) & 0b1) << 24
        AcMask_int |= (int(AcMask.FlashFileSystemWrite) & 0b1) << 23
        AcMask_int |= (int(AcMask.FlashFileSystemRead) & 0b1) << 22
        AcMask_int |= (int(AcMask.RtcWrite) & 0b1) << 21
        AcMask_int |= (int(AcMask.VhlExchangeapdu) & 0b1) << 20
        AcMask_int |= (int(AcMask.VhlFormat) & 0b1) << 19
        AcMask_int |= (int(AcMask.VhlWrite) & 0b1) << 18
        AcMask_int |= (int(AcMask.VhlRead) & 0b1) << 17
        AcMask_int |= (int(AcMask.VhlSelect) & 0b1) << 16
        AcMask_int |= (int(AcMask.ExtSamAccess) & 0b1) << 15
        AcMask_int |= (int(AcMask.HfLowlevelAccess) & 0b1) << 14
        AcMask_int |= (int(AcMask.GuiAccess) & 0b1) << 13
        AcMask_int |= (int(AcMask.IoPortWrite) & 0b1) << 12
        AcMask_int |= (int(AcMask.IoPortRead) & 0b1) << 11
        AcMask_int |= (int(AcMask.ConfigReset) & 0b1) << 10
        AcMask_int |= (int(AcMask.ConfigWrite) & 0b1) << 9
        AcMask_int |= (int(AcMask.ConfigRead) & 0b1) << 8
        AcMask_int |= (int(AcMask.SysReset) & 0b1) << 7
        AcMask_int |= (int(AcMask.SetAccessConditionMask2) & 0b1) << 6
        AcMask_int |= (int(AcMask.SetAccessConditionMask1) & 0b1) << 5
        AcMask_int |= (int(AcMask.SetAccessConditionMask0) & 0b1) << 4
        AcMask_int |= (int(AcMask.SetKey3) & 0b1) << 3
        AcMask_int |= (int(AcMask.SetKey2) & 0b1) << 2
        AcMask_int |= (int(AcMask.SetKey1) & 0b1) << 1
        AcMask_int |= (int(AcMask.FactoryReset) & 0b1) << 0
        _send_buffer.write(AcMask_int.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SecLevel: int = 255, *, AcMask: Union[HostSecurityAccessConditionBits, HostSecurityAccessConditionBits_Dict], BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(SecLevel=SecLevel, AcMask=AcMask, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sec_SetKey(Command):
    CommandGroupId = 0x07
    CommandId = 0x03
    def build_frame(self, ContinuousIV: int = 0, Encrypted: int = 0, MACed: int = 0, SessionKey: int = 0, DeriveKey: int = 0, *, SecLevel: int, Key: bytes, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (ContinuousIV & 0b1) << 7
        _var_0000_int |= (Encrypted & 0b1) << 6
        _var_0000_int |= (MACed & 0b1) << 5
        _var_0000_int |= (SessionKey & 0b1) << 4
        _var_0000_int |= (DeriveKey & 0b11) << 2
        _var_0000_int |= (SecLevel & 0b11) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if len(Key) != 16:
            raise ValueError(Key)
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, ContinuousIV: int = 0, Encrypted: int = 0, MACed: int = 0, SessionKey: int = 0, DeriveKey: int = 0, *, SecLevel: int, Key: bytes, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(ContinuousIV=ContinuousIV, Encrypted=Encrypted, MACed=MACed, SessionKey=SessionKey, DeriveKey=DeriveKey, SecLevel=SecLevel, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sec_AuthPhase1(Command):
    CommandGroupId = 0x07
    CommandId = 0x04
    def build_frame(self, SecLevel: int, RndA: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SecLevel.to_bytes(length=1, byteorder='big'))
        if len(RndA) != 16:
            raise ValueError(RndA)
        _send_buffer.write(RndA)
        return _send_buffer.getvalue()
    def __call__(self, SecLevel: int, RndA: bytes, BrpTimeout: int = 100) -> Sec_AuthPhase1_Result:
        request_frame = self.build_frame(SecLevel=SecLevel, RndA=RndA, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EncRndA = _recv_buffer.read(16)
        if len(_EncRndA) != 16:
            raise PayloadTooShortError(16 - len(_EncRndA))
        _RndB = _recv_buffer.read(16)
        if len(_RndB) != 16:
            raise PayloadTooShortError(16 - len(_RndB))
        _ReqAuthModes_int = safe_read_int_from_buffer(_recv_buffer, 1)
        _ContinuousIV = bool((_ReqAuthModes_int >> 7) & 0b1)
        _Encrypted = bool((_ReqAuthModes_int >> 6) & 0b1)
        _MACed = bool((_ReqAuthModes_int >> 5) & 0b1)
        _SessionKey = bool((_ReqAuthModes_int >> 4) & 0b1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sec_AuthPhase1_Result(_EncRndA, _RndB, _ContinuousIV, _Encrypted, _MACed, _SessionKey)
class Sec_AuthPhase2(Command):
    CommandGroupId = 0x07
    CommandId = 0x05
    def build_frame(self, EncRndB: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(EncRndB) != 16:
            raise ValueError(EncRndB)
        _send_buffer.write(EncRndB)
        return _send_buffer.getvalue()
    def __call__(self, EncRndB: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(EncRndB=EncRndB, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sec_Tunnel(Command):
    CommandGroupId = 0x07
    CommandId = 0x06
    def build_frame(self, ContinuousIV: bool = True, Encrypted: bool = True, MACed: bool = False, SessionKey: bool = True, *, SecLevel: int, TunnelledCmd: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ContinuousIV) & 0b1) << 7
        _var_0000_int |= (int(Encrypted) & 0b1) << 6
        _var_0000_int |= (int(MACed) & 0b1) << 5
        _var_0000_int |= (int(SessionKey) & 0b1) << 4
        _var_0000_int |= (SecLevel & 0b11) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(TunnelledCmd)
        return _send_buffer.getvalue()
    def __call__(self, ContinuousIV: bool = True, Encrypted: bool = True, MACed: bool = False, SessionKey: bool = True, *, SecLevel: int, TunnelledCmd: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(ContinuousIV=ContinuousIV, Encrypted=Encrypted, MACed=MACed, SessionKey=SessionKey, SecLevel=SecLevel, TunnelledCmd=TunnelledCmd, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _TunnelledResp = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _TunnelledResp
class Sec_Reset(Command):
    CommandGroupId = 0x07
    CommandId = 0x08
    def build_frame(self, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sec_LockReset(Command):
    CommandGroupId = 0x07
    CommandId = 0x09
    def build_frame(self, SecLevel: int = 255, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SecLevel.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SecLevel: int = 255, BrpTimeout: int = 1000) -> None:
        request_frame = self.build_frame(SecLevel=SecLevel, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sec_GetCurAcMask(Command):
    CommandGroupId = 0x07
    CommandId = 0x0A
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x07\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> HostSecurityAccessConditionBits:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _AcMask_int = safe_read_int_from_buffer(_recv_buffer, 4)
        _EthernetAccess = bool((_AcMask_int >> 28) & 0b1)
        _AutoreadAccess = bool((_AcMask_int >> 27) & 0b1)
        _CryptoAccess = bool((_AcMask_int >> 26) & 0b1)
        _Bf2Upload = bool((_AcMask_int >> 25) & 0b1)
        _ExtendedAccess = bool((_AcMask_int >> 24) & 0b1)
        _FlashFileSystemWrite = bool((_AcMask_int >> 23) & 0b1)
        _FlashFileSystemRead = bool((_AcMask_int >> 22) & 0b1)
        _RtcWrite = bool((_AcMask_int >> 21) & 0b1)
        _VhlExchangeapdu = bool((_AcMask_int >> 20) & 0b1)
        _VhlFormat = bool((_AcMask_int >> 19) & 0b1)
        _VhlWrite = bool((_AcMask_int >> 18) & 0b1)
        _VhlRead = bool((_AcMask_int >> 17) & 0b1)
        _VhlSelect = bool((_AcMask_int >> 16) & 0b1)
        _ExtSamAccess = bool((_AcMask_int >> 15) & 0b1)
        _HfLowlevelAccess = bool((_AcMask_int >> 14) & 0b1)
        _GuiAccess = bool((_AcMask_int >> 13) & 0b1)
        _IoPortWrite = bool((_AcMask_int >> 12) & 0b1)
        _IoPortRead = bool((_AcMask_int >> 11) & 0b1)
        _ConfigReset = bool((_AcMask_int >> 10) & 0b1)
        _ConfigWrite = bool((_AcMask_int >> 9) & 0b1)
        _ConfigRead = bool((_AcMask_int >> 8) & 0b1)
        _SysReset = bool((_AcMask_int >> 7) & 0b1)
        _SetAccessConditionMask2 = bool((_AcMask_int >> 6) & 0b1)
        _SetAccessConditionMask1 = bool((_AcMask_int >> 5) & 0b1)
        _SetAccessConditionMask0 = bool((_AcMask_int >> 4) & 0b1)
        _SetKey3 = bool((_AcMask_int >> 3) & 0b1)
        _SetKey2 = bool((_AcMask_int >> 2) & 0b1)
        _SetKey1 = bool((_AcMask_int >> 1) & 0b1)
        _FactoryReset = bool((_AcMask_int >> 0) & 0b1)
        _AcMask = HostSecurityAccessConditionBits(_EthernetAccess, _AutoreadAccess, _CryptoAccess, _Bf2Upload, _ExtendedAccess, _FlashFileSystemWrite, _FlashFileSystemRead, _RtcWrite, _VhlExchangeapdu, _VhlFormat, _VhlWrite, _VhlRead, _VhlSelect, _ExtSamAccess, _HfLowlevelAccess, _GuiAccess, _IoPortWrite, _IoPortRead, _ConfigReset, _ConfigWrite, _ConfigRead, _SysReset, _SetAccessConditionMask2, _SetAccessConditionMask1, _SetAccessConditionMask0, _SetKey3, _SetKey2, _SetKey1, _FactoryReset)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _AcMask
class Srix_Select(Command):
    CommandGroupId = 0x24
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x24\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Snr_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Snr = _recv_buffer.read(_Snr_len)
        if len(_Snr) != _Snr_len:
            raise PayloadTooShortError(_Snr_len - len(_Snr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Snr
class Srix_Read(Command):
    CommandGroupId = 0x24
    CommandId = 0x01
    def build_frame(self, Adr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x24\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class Srix_Write(Command):
    CommandGroupId = 0x24
    CommandId = 0x02
    def build_frame(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x24\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_GetBufferSize(Command):
    CommandGroupId = 0x00
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 50) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 50) -> Sys_GetBufferSize_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MaxSendSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _MaxRecvSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _TotalSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_GetBufferSize_Result(_MaxSendSize, _MaxRecvSize, _TotalSize)
class Sys_HFReset(Command):
    CommandGroupId = 0x00
    CommandId = 0x01
    def build_frame(self, OffDuration: int = 1, BrpTimeout: int = 2000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(OffDuration.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, OffDuration: int = 1, BrpTimeout: int = 2000) -> None:
        request_frame = self.build_frame(OffDuration=OffDuration, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_Reset(Command):
    CommandGroupId = 0x00
    CommandId = 0x03
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_GetInfo(Command):
    CommandGroupId = 0x00
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 50) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 50) -> str:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Info_bytes = b''
        _Info_next_byte = _recv_buffer.read(1)
        while _Info_next_byte and _Info_next_byte != b'\x00':
            _Info_bytes += _Info_next_byte
            _Info_next_byte = _recv_buffer.read(1)
        if not _Info_next_byte:
            raise InvalidPayloadError('missing zero-terminator in field Info')
        _Info = _Info_bytes.decode('ascii')
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Info
class Sys_GetBootStatus(Command):
    CommandGroupId = 0x00
    CommandId = 0x05
    def build_frame(self, BrpTimeout: int = 50) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 50) -> Sys_GetBootStatus_BootStatus:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BootStatus_int = safe_read_int_from_buffer(_recv_buffer, 4)
        _NewerReaderChipFirmware = bool((_BootStatus_int >> 31) & 0b1)
        _UnexpectedRebootsLegacy = bool((_BootStatus_int >> 30) & 0b1)
        _FactorySettings = bool((_BootStatus_int >> 29) & 0b1)
        _ConfigurationInconsistent = bool((_BootStatus_int >> 28) & 0b1)
        _FirmwareVersionBlocked = bool((_BootStatus_int >> 27) & 0b1)
        _Bluetooth = bool((_BootStatus_int >> 23) & 0b1)
        _WiFi = bool((_BootStatus_int >> 22) & 0b1)
        _Tamper = bool((_BootStatus_int >> 21) & 0b1)
        _BatteryManagement = bool((_BootStatus_int >> 20) & 0b1)
        _Keyboard = bool((_BootStatus_int >> 19) & 0b1)
        _FirmwareVersionBlockedLegacy = bool((_BootStatus_int >> 18) & 0b1)
        _Display = bool((_BootStatus_int >> 17) & 0b1)
        _ConfCardPresented = bool((_BootStatus_int >> 16) & 0b1)
        _Ethernet = bool((_BootStatus_int >> 15) & 0b1)
        _ExtendedLED = bool((_BootStatus_int >> 14) & 0b1)
        _Rf125kHz = bool((_BootStatus_int >> 12) & 0b1)
        _Rf13MHz = bool((_BootStatus_int >> 10) & 0b1)
        _Rf13MHzLegic = bool((_BootStatus_int >> 9) & 0b1)
        _Rf13MHzLegacy = bool((_BootStatus_int >> 8) & 0b1)
        _HWoptions = bool((_BootStatus_int >> 7) & 0b1)
        _RTC = bool((_BootStatus_int >> 5) & 0b1)
        _Dataflash = bool((_BootStatus_int >> 4) & 0b1)
        _Configuration = bool((_BootStatus_int >> 2) & 0b1)
        _CorruptFirmware = bool((_BootStatus_int >> 1) & 0b1)
        _IncompleteFirmware = bool((_BootStatus_int >> 0) & 0b1)
        _BootStatus = Sys_GetBootStatus_BootStatus(_NewerReaderChipFirmware, _UnexpectedRebootsLegacy, _FactorySettings, _ConfigurationInconsistent, _FirmwareVersionBlocked, _Bluetooth, _WiFi, _Tamper, _BatteryManagement, _Keyboard, _FirmwareVersionBlockedLegacy, _Display, _ConfCardPresented, _Ethernet, _ExtendedLED, _Rf125kHz, _Rf13MHz, _Rf13MHzLegic, _Rf13MHzLegacy, _HWoptions, _RTC, _Dataflash, _Configuration, _CorruptFirmware, _IncompleteFirmware)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _BootStatus
class Sys_GetPort(Command):
    CommandGroupId = 0x00
    CommandId = 0x06
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> IoPortBitmask:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PortMask_int = safe_read_int_from_buffer(_recv_buffer, 2)
        _Gpio7 = bool((_PortMask_int >> 15) & 0b1)
        _Gpio6 = bool((_PortMask_int >> 14) & 0b1)
        _Gpio5 = bool((_PortMask_int >> 13) & 0b1)
        _Gpio4 = bool((_PortMask_int >> 12) & 0b1)
        _Gpio3 = bool((_PortMask_int >> 11) & 0b1)
        _Gpio2 = bool((_PortMask_int >> 10) & 0b1)
        _Gpio1 = bool((_PortMask_int >> 9) & 0b1)
        _Gpio0 = bool((_PortMask_int >> 8) & 0b1)
        _TamperAlarm = bool((_PortMask_int >> 7) & 0b1)
        _BlueLed = bool((_PortMask_int >> 6) & 0b1)
        _Input1 = bool((_PortMask_int >> 5) & 0b1)
        _Input0 = bool((_PortMask_int >> 4) & 0b1)
        _Relay = bool((_PortMask_int >> 3) & 0b1)
        _Beeper = bool((_PortMask_int >> 2) & 0b1)
        _RedLed = bool((_PortMask_int >> 1) & 0b1)
        _GreenLed = bool((_PortMask_int >> 0) & 0b1)
        _PortMask = IoPortBitmask(_Gpio7, _Gpio6, _Gpio5, _Gpio4, _Gpio3, _Gpio2, _Gpio1, _Gpio0, _TamperAlarm, _BlueLed, _Input1, _Input0, _Relay, _Beeper, _RedLed, _GreenLed)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PortMask
class Sys_SetPort(Command):
    CommandGroupId = 0x00
    CommandId = 0x07
    def build_frame(self, PortMask: Union[IoPortBitmask, IoPortBitmask_Dict], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if isinstance(PortMask, dict):
            PortMask = IoPortBitmask(**PortMask)
        PortMask_int = 0
        PortMask_int |= (int(PortMask.Gpio7) & 0b1) << 15
        PortMask_int |= (int(PortMask.Gpio6) & 0b1) << 14
        PortMask_int |= (int(PortMask.Gpio5) & 0b1) << 13
        PortMask_int |= (int(PortMask.Gpio4) & 0b1) << 12
        PortMask_int |= (int(PortMask.Gpio3) & 0b1) << 11
        PortMask_int |= (int(PortMask.Gpio2) & 0b1) << 10
        PortMask_int |= (int(PortMask.Gpio1) & 0b1) << 9
        PortMask_int |= (int(PortMask.Gpio0) & 0b1) << 8
        PortMask_int |= (int(PortMask.TamperAlarm) & 0b1) << 7
        PortMask_int |= (int(PortMask.BlueLed) & 0b1) << 6
        PortMask_int |= (int(PortMask.Input1) & 0b1) << 5
        PortMask_int |= (int(PortMask.Input0) & 0b1) << 4
        PortMask_int |= (int(PortMask.Relay) & 0b1) << 3
        PortMask_int |= (int(PortMask.Beeper) & 0b1) << 2
        PortMask_int |= (int(PortMask.RedLed) & 0b1) << 1
        PortMask_int |= (int(PortMask.GreenLed) & 0b1) << 0
        _send_buffer.write(PortMask_int.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PortMask: Union[IoPortBitmask, IoPortBitmask_Dict], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PortMask=PortMask, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgGetValue(Command):
    CommandGroupId = 0x00
    CommandId = 0x08
    def build_frame(self, Key: int, Value: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Key.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Value.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Key: int, Value: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Key=Key, Value=Value, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Content_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Content = _recv_buffer.read(_Content_len)
        if len(_Content) != _Content_len:
            raise PayloadTooShortError(_Content_len - len(_Content))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Content
class Sys_CfgSetValue(Command):
    CommandGroupId = 0x00
    CommandId = 0x09
    def build_frame(self, Key: int, Value: int, Content: bytes, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Key.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Value.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Content)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Content)
        return _send_buffer.getvalue()
    def __call__(self, Key: int, Value: int, Content: bytes, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(Key=Key, Value=Value, Content=Content, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgDelValues(Command):
    CommandGroupId = 0x00
    CommandId = 0x0A
    def build_frame(self, Key: int = 65535, Value: int = 255, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Key.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Value.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Key: int = 65535, Value: int = 255, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(Key=Key, Value=Value, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgGetKeyList(Command):
    CommandGroupId = 0x00
    CommandId = 0x0B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x0B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _KeyList_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _KeyList = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_KeyList) >= _KeyList_len:
            _Key = safe_read_int_from_buffer(_recv_buffer, 2)
            _KeyList.append(_Key)
        if len(_KeyList) != _KeyList_len:
            raise PayloadTooShortError(_KeyList_len - len(_KeyList))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _KeyList
class Sys_CfgGetValueList(Command):
    CommandGroupId = 0x00
    CommandId = 0x0C
    def build_frame(self, Key: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x0C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Key.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Key: int, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ValueList_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ValueList = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_ValueList) >= _ValueList_len:
            _Value = safe_read_int_from_buffer(_recv_buffer, 1)
            _ValueList.append(_Value)
        if len(_ValueList) != _ValueList_len:
            raise PayloadTooShortError(_ValueList_len - len(_ValueList))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ValueList
class Sys_CfgWriteTlvSector(Command):
    CommandGroupId = 0x00
    CommandId = 0x0D
    def build_frame(self, TlvBlock: bytes, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x0D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(TlvBlock)
        return _send_buffer.getvalue()
    def __call__(self, TlvBlock: bytes, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(TlvBlock=TlvBlock, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgCheck(Command):
    CommandGroupId = 0x00
    CommandId = 0x13
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x13")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Sys_CfgCheck_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _TotalSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _FreeSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_CfgCheck_Result(_TotalSize, _FreeSize)
class Sys_ConfigPort(Command):
    CommandGroupId = 0x00
    CommandId = 0x0E
    def build_frame(self, InpOutp: Union[IoPortBitmask, IoPortBitmask_Dict], DefaultState: Union[IoPortBitmask, IoPortBitmask_Dict], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x0E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if isinstance(InpOutp, dict):
            InpOutp = IoPortBitmask(**InpOutp)
        InpOutp_int = 0
        InpOutp_int |= (int(InpOutp.Gpio7) & 0b1) << 15
        InpOutp_int |= (int(InpOutp.Gpio6) & 0b1) << 14
        InpOutp_int |= (int(InpOutp.Gpio5) & 0b1) << 13
        InpOutp_int |= (int(InpOutp.Gpio4) & 0b1) << 12
        InpOutp_int |= (int(InpOutp.Gpio3) & 0b1) << 11
        InpOutp_int |= (int(InpOutp.Gpio2) & 0b1) << 10
        InpOutp_int |= (int(InpOutp.Gpio1) & 0b1) << 9
        InpOutp_int |= (int(InpOutp.Gpio0) & 0b1) << 8
        InpOutp_int |= (int(InpOutp.TamperAlarm) & 0b1) << 7
        InpOutp_int |= (int(InpOutp.BlueLed) & 0b1) << 6
        InpOutp_int |= (int(InpOutp.Input1) & 0b1) << 5
        InpOutp_int |= (int(InpOutp.Input0) & 0b1) << 4
        InpOutp_int |= (int(InpOutp.Relay) & 0b1) << 3
        InpOutp_int |= (int(InpOutp.Beeper) & 0b1) << 2
        InpOutp_int |= (int(InpOutp.RedLed) & 0b1) << 1
        InpOutp_int |= (int(InpOutp.GreenLed) & 0b1) << 0
        _send_buffer.write(InpOutp_int.to_bytes(length=2, byteorder='big'))
        if isinstance(DefaultState, dict):
            DefaultState = IoPortBitmask(**DefaultState)
        DefaultState_int = 0
        DefaultState_int |= (int(DefaultState.Gpio7) & 0b1) << 15
        DefaultState_int |= (int(DefaultState.Gpio6) & 0b1) << 14
        DefaultState_int |= (int(DefaultState.Gpio5) & 0b1) << 13
        DefaultState_int |= (int(DefaultState.Gpio4) & 0b1) << 12
        DefaultState_int |= (int(DefaultState.Gpio3) & 0b1) << 11
        DefaultState_int |= (int(DefaultState.Gpio2) & 0b1) << 10
        DefaultState_int |= (int(DefaultState.Gpio1) & 0b1) << 9
        DefaultState_int |= (int(DefaultState.Gpio0) & 0b1) << 8
        DefaultState_int |= (int(DefaultState.TamperAlarm) & 0b1) << 7
        DefaultState_int |= (int(DefaultState.BlueLed) & 0b1) << 6
        DefaultState_int |= (int(DefaultState.Input1) & 0b1) << 5
        DefaultState_int |= (int(DefaultState.Input0) & 0b1) << 4
        DefaultState_int |= (int(DefaultState.Relay) & 0b1) << 3
        DefaultState_int |= (int(DefaultState.Beeper) & 0b1) << 2
        DefaultState_int |= (int(DefaultState.RedLed) & 0b1) << 1
        DefaultState_int |= (int(DefaultState.GreenLed) & 0b1) << 0
        _send_buffer.write(DefaultState_int.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, InpOutp: Union[IoPortBitmask, IoPortBitmask_Dict], DefaultState: Union[IoPortBitmask, IoPortBitmask_Dict], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(InpOutp=InpOutp, DefaultState=DefaultState, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_SetRegister(Command):
    CommandGroupId = 0x00
    CommandId = 0x0F
    def build_frame(self, ResetRegister: bool = False, *, RegisterAssignments: List[Sys_SetRegister_RegisterAssignments_Entry], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x0F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ResetRegister.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(RegisterAssignments)).to_bytes(1, byteorder='big'))
        for _RegisterAssignments_Entry in RegisterAssignments:
            _ID, _Value = _RegisterAssignments_Entry
            _send_buffer.write(_ID.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(_Value.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ResetRegister: bool = False, *, RegisterAssignments: List[Sys_SetRegister_RegisterAssignments_Entry], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ResetRegister=ResetRegister, RegisterAssignments=RegisterAssignments, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_GetRegister(Command):
    CommandGroupId = 0x00
    CommandId = 0x10
    def build_frame(self, ID: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ID.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ID: int, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(ID=ID, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Value = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Value
class Sys_PowerDown(Command):
    CommandGroupId = 0x00
    CommandId = 0x11
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_SelectProtocol(Command):
    CommandGroupId = 0x00
    CommandId = 0x12
    def build_frame(self, Protocol: ProtocolID, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ProtocolID_Parser.as_value(Protocol).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Protocol: ProtocolID, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Protocol=Protocol, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_SetCommParam(Command):
    CommandGroupId = 0x00
    CommandId = 0x14
    def build_frame(self, NewBaudrate: Baudrate = "Baud115200", *, NewParity: Parity, CWT: int = 20, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x14")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Baudrate_Parser.as_value(NewBaudrate).to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Parity_Parser.as_value(NewParity).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CWT.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, NewBaudrate: Baudrate = "Baud115200", *, NewParity: Parity, CWT: int = 20, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(NewBaudrate=NewBaudrate, NewParity=NewParity, CWT=CWT, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgLoadBlock(Command):
    CommandGroupId = 0x00
    CommandId = 0x16
    def build_frame(self, Version: int = 0, *, Data: bytes, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x16")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Version.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Version: int = 0, *, Data: bytes, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(Version=Version, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_GetPlatformId(Command):
    CommandGroupId = 0x00
    CommandId = 0x17
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x17")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Sys_GetPlatformId_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PlatformId = _recv_buffer.read(5)
        if len(_PlatformId) != 5:
            raise PayloadTooShortError(5 - len(_PlatformId))
        _BootloaderId = safe_read_int_from_buffer(_recv_buffer, 1)
        _BootloaderMajor = safe_read_int_from_buffer(_recv_buffer, 1)
        _BootloaderMinor = safe_read_int_from_buffer(_recv_buffer, 1)
        _BootloaderBuild = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_GetPlatformId_Result(_PlatformId, _BootloaderId, _BootloaderMajor, _BootloaderMinor, _BootloaderBuild)
class Sys_CfgReset(Command):
    CommandGroupId = 0x00
    CommandId = 0x18
    def build_frame(self, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x18")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_StopProtocol(Command):
    CommandGroupId = 0x00
    CommandId = 0x19
    def build_frame(self, Protocol: ProtocolID, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x19")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(ProtocolID_Parser.as_value(Protocol).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Protocol: ProtocolID, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Protocol=Protocol, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgGetId(Command):
    CommandGroupId = 0x00
    CommandId = 0x20
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Sys_CfgGetId_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ConfigId_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ConfigId_bytes = _recv_buffer.read(_ConfigId_len)
        _ConfigId = _ConfigId_bytes.decode('ascii')
        if len(_ConfigId) != _ConfigId_len:
            raise PayloadTooShortError(_ConfigId_len - len(_ConfigId))
        _ConfigName_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ConfigName_bytes = _recv_buffer.read(_ConfigName_len)
        _ConfigName = _ConfigName_bytes.decode('ascii')
        if len(_ConfigName) != _ConfigName_len:
            raise PayloadTooShortError(_ConfigName_len - len(_ConfigName))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_CfgGetId_Result(_ConfigId, _ConfigName)
class Sys_CfgGetDeviceSettingsId(Command):
    CommandGroupId = 0x00
    CommandId = 0x21
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x21")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Sys_CfgGetDeviceSettingsId_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ConfigId_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ConfigId_bytes = _recv_buffer.read(_ConfigId_len)
        _ConfigId = _ConfigId_bytes.decode('ascii')
        if len(_ConfigId) != _ConfigId_len:
            raise PayloadTooShortError(_ConfigId_len - len(_ConfigId))
        _ConfigName_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ConfigName_bytes = _recv_buffer.read(_ConfigName_len)
        _ConfigName = _ConfigName_bytes.decode('ascii')
        if len(_ConfigName) != _ConfigName_len:
            raise PayloadTooShortError(_ConfigName_len - len(_ConfigName))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_CfgGetDeviceSettingsId_Result(_ConfigId, _ConfigName)
class Sys_FactoryResetLegacy(Command):
    CommandGroupId = 0x00
    CommandId = 0x22
    def build_frame(self, BrpTimeout: int = 30000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x22")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 30000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_GetStatistics(Command):
    CommandGroupId = 0x00
    CommandId = 0x23
    def build_frame(self, DeleteCounters: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x23")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DeleteCounters.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DeleteCounters: bool = False, BrpTimeout: int = 100) -> List[Sys_GetStatistics_CounterTuple_Entry]:
        request_frame = self.build_frame(DeleteCounters=DeleteCounters, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _CounterTuple_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _CounterTuple = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_CounterTuple) >= _CounterTuple_len:
            _ID = safe_read_int_from_buffer(_recv_buffer, 1)
            _Value = safe_read_int_from_buffer(_recv_buffer, 1)
            _CounterTuple_Entry = Sys_GetStatistics_CounterTuple_Entry(_ID, _Value)
            _CounterTuple.append(_CounterTuple_Entry)
        if len(_CounterTuple) != _CounterTuple_len:
            raise PayloadTooShortError(_CounterTuple_len - len(_CounterTuple))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _CounterTuple
class Sys_GetFeatures(Command):
    CommandGroupId = 0x00
    CommandId = 0x24
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x24")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Sys_GetFeatures_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _FeatureList_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _FeatureList = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_FeatureList) >= _FeatureList_len:
            _SupportedFeatureID = FeatureID_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 2))
            _FeatureList.append(_SupportedFeatureID)
        if len(_FeatureList) != _FeatureList_len:
            raise PayloadTooShortError(_FeatureList_len - len(_FeatureList))
        _MaxFeatureID = FeatureID_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 2))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_GetFeatures_Result(_FeatureList, _MaxFeatureID)
class Sys_GetPartNumber(Command):
    CommandGroupId = 0x00
    CommandId = 0x25
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x25")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> Sys_GetPartNumber_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PartNo_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _PartNo_bytes = _recv_buffer.read(_PartNo_len)
        _PartNo = _PartNo_bytes.decode('ascii')
        if len(_PartNo) != _PartNo_len:
            raise PayloadTooShortError(_PartNo_len - len(_PartNo))
        _HwRevNo_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _HwRevNo_bytes = _recv_buffer.read(_HwRevNo_len)
        _HwRevNo = _HwRevNo_bytes.decode('ascii')
        if len(_HwRevNo) != _HwRevNo_len:
            raise PayloadTooShortError(_HwRevNo_len - len(_HwRevNo))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return Sys_GetPartNumber_Result(_PartNo, _HwRevNo)
class Sys_CfgLoadPrepare(Command):
    CommandGroupId = 0x00
    CommandId = 0x26
    def build_frame(self, AuthReq: AuthReqUpload = "Default", BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x26")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AuthReqUpload_Parser.as_value(AuthReq).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AuthReq: AuthReqUpload = "Default", BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(AuthReq=AuthReq, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_CfgLoadFinish(Command):
    CommandGroupId = 0x00
    CommandId = 0x27
    def build_frame(self, FinalizeAction: Sys_CfgLoadFinish_FinalizeAction, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x27")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Sys_CfgLoadFinish_FinalizeAction_Parser.as_value(FinalizeAction).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FinalizeAction: Sys_CfgLoadFinish_FinalizeAction, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(FinalizeAction=FinalizeAction, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_FactoryReset(Command):
    CommandGroupId = 0x00
    CommandId = 0x28
    def build_frame(self, PerformReboot: bool = True, BrpTimeout: int = 30000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x28")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PerformReboot.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PerformReboot: bool = True, BrpTimeout: int = 30000) -> None:
        request_frame = self.build_frame(PerformReboot=PerformReboot, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Sys_GetLicenses(Command):
    CommandGroupId = 0x00
    CommandId = 0x29
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x29")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> LicenseBitMask:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LicenseBitMask_int = safe_read_int_from_buffer(_recv_buffer, 4)
        _Ble = bool((_LicenseBitMask_int >> 3) & 0b1)
        _BleLicRequired = bool((_LicenseBitMask_int >> 2) & 0b1)
        _HidOnlyForSE = bool((_LicenseBitMask_int >> 1) & 0b1)
        _Hid = bool((_LicenseBitMask_int >> 0) & 0b1)
        _LicenseBitMask = LicenseBitMask(_Ble, _BleLicRequired, _HidOnlyForSE, _Hid)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LicenseBitMask
class Sys_GetFwCrc(Command):
    CommandGroupId = 0x00
    CommandId = 0x7F
    def build_frame(self, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x00\x7F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 1000) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _CRC = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _CRC
class TTF_ReadByteStream(Command):
    CommandGroupId = 0x34
    CommandId = 0x02
    def build_frame(self, ResetDataPtr: bool = False, SamplingTime: int = 0, Rxlen: int = 256, RxMod: TTF_ReadByteStream_RxMod = "SMPL", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x34\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ResetDataPtr) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SamplingTime.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Rxlen.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(TTF_ReadByteStream_RxMod_Parser.as_value(RxMod).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ResetDataPtr: bool = False, SamplingTime: int = 0, Rxlen: int = 256, RxMod: TTF_ReadByteStream_RxMod = "SMPL", BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(ResetDataPtr=ResetDataPtr, SamplingTime=SamplingTime, Rxlen=Rxlen, RxMod=RxMod, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class TTF_IdteckRead(Command):
    CommandGroupId = 0x34
    CommandId = 0x10
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x34\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class EpcUid_UidReplyRound(Command):
    CommandGroupId = 0x22
    CommandId = 0x00
    def build_frame(self, EPC: bool = False, FixSlot: bool = False, SlotCoding: int = 0, MaskLength: int = 0, *, SelectionMask: bytes, HashValue: Optional[int] = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x22\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EPC) & 0b1) << 1
        _var_0000_int |= (int(FixSlot) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SlotCoding.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(MaskLength.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(SelectionMask)).to_bytes(1, byteorder='big'))
        _send_buffer.write(SelectionMask)
        if EPC:
            if HashValue is None:
                raise TypeError("missing a required argument: 'HashValue'")
            _send_buffer.write(HashValue.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, EPC: bool = False, FixSlot: bool = False, SlotCoding: int = 0, MaskLength: int = 0, *, SelectionMask: bytes, HashValue: Optional[int] = 0, BrpTimeout: int = 100) -> EpcUid_UidReplyRound_Result:
        request_frame = self.build_frame(EPC=EPC, FixSlot=FixSlot, SlotCoding=SlotCoding, MaskLength=MaskLength, SelectionMask=SelectionMask, HashValue=HashValue, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MemStatusFlag = safe_read_int_from_buffer(_recv_buffer, 1)
        _LabelNr = safe_read_int_from_buffer(_recv_buffer, 2)
        _LabelLength = safe_read_int_from_buffer(_recv_buffer, 1)
        _LabelData = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return EpcUid_UidReplyRound_Result(_MemStatusFlag, _LabelNr, _LabelLength, _LabelData)
class EpcUid_UidWrite(Command):
    CommandGroupId = 0x22
    CommandId = 0x01
    def build_frame(self, EPC: bool = False, *, BlockAdr: int, BlockData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x22\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(EPC) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(BlockData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(BlockData)
        return _send_buffer.getvalue()
    def __call__(self, EPC: bool = False, *, BlockAdr: int, BlockData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(EPC=EPC, BlockAdr=BlockAdr, BlockData=BlockData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EpcUid_UidDestroy(Command):
    CommandGroupId = 0x22
    CommandId = 0x02
    def build_frame(self, EpcUidData: bytes, DestroyCode: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x22\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(EpcUidData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(EpcUidData)
        _send_buffer.write(int(len(DestroyCode)).to_bytes(1, byteorder='big'))
        _send_buffer.write(DestroyCode)
        return _send_buffer.getvalue()
    def __call__(self, EpcUidData: bytes, DestroyCode: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(EpcUidData=EpcUidData, DestroyCode=DestroyCode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EpcUid_EpcSetMode(Command):
    CommandGroupId = 0x22
    CommandId = 0x10
    def build_frame(self, DR848: int = 0, Coding: EpcUid_EpcSetMode_Coding = "Man2", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x22\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (DR848 & 0b1) << 2
        _var_0000_int |= (EpcUid_EpcSetMode_Coding_Parser.as_value(Coding) & 0b11) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DR848: int = 0, Coding: EpcUid_EpcSetMode_Coding = "Man2", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(DR848=DR848, Coding=Coding, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EpcUid_EpcSelect(Command):
    CommandGroupId = 0x22
    CommandId = 0x11
    def build_frame(self, Truncate: int = 0, Target: int = 0, Action: int = 0, MemBank: EpcUid_EpcSelect_MemBank = "EPC", MaskPointerLength: int = 8, *, MaskPointer: bytes, MaskLength: int = 0, SelectionMask: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x22\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (Truncate & 0b1) << 6
        _var_0000_int |= (Target & 0b111) << 3
        _var_0000_int |= (Action & 0b111) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(EpcUid_EpcSelect_MemBank_Parser.as_value(MemBank).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(MaskPointerLength.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(MaskPointer)).to_bytes(1, byteorder='big'))
        _send_buffer.write(MaskPointer)
        _send_buffer.write(MaskLength.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SelectionMask)
        return _send_buffer.getvalue()
    def __call__(self, Truncate: int = 0, Target: int = 0, Action: int = 0, MemBank: EpcUid_EpcSelect_MemBank = "EPC", MaskPointerLength: int = 8, *, MaskPointer: bytes, MaskLength: int = 0, SelectionMask: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Truncate=Truncate, Target=Target, Action=Action, MemBank=MemBank, MaskPointerLength=MaskPointerLength, MaskPointer=MaskPointer, MaskLength=MaskLength, SelectionMask=SelectionMask, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class EpcUid_EpcInventory(Command):
    CommandGroupId = 0x22
    CommandId = 0x12
    def build_frame(self, Sel: int = 0, Session: int = 0, SlotCoding: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x22\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (Sel & 0b11) << 2
        _var_0000_int |= (Session & 0b11) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(SlotCoding.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Sel: int = 0, Session: int = 0, SlotCoding: int = 0, BrpTimeout: int = 100) -> EpcUid_EpcInventory_Result:
        request_frame = self.build_frame(Sel=Sel, Session=Session, SlotCoding=SlotCoding, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MemStatusFlag = safe_read_int_from_buffer(_recv_buffer, 1)
        _LabelNr = safe_read_int_from_buffer(_recv_buffer, 2)
        _LabelData = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return EpcUid_EpcInventory_Result(_MemStatusFlag, _LabelNr, _LabelData)
class Ultralight_ExecCmd(Command):
    CommandGroupId = 0x25
    CommandId = 0x00
    def build_frame(self, Cmd: int, Param: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x25\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Cmd.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Param)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Param)
        return _send_buffer.getvalue()
    def __call__(self, Cmd: int, Param: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Cmd=Cmd, Param=Param, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Response_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Response = _recv_buffer.read(_Response_len)
        if len(_Response) != _Response_len:
            raise PayloadTooShortError(_Response_len - len(_Response))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Response
class Ultralight_Read(Command):
    CommandGroupId = 0x25
    CommandId = 0x01
    def build_frame(self, PageAdr: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x25\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PageAdr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PageAdr: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(PageAdr=PageAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PageData = _recv_buffer.read(16)
        if len(_PageData) != 16:
            raise PayloadTooShortError(16 - len(_PageData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PageData
class Ultralight_Write(Command):
    CommandGroupId = 0x25
    CommandId = 0x02
    def build_frame(self, PageAdr: int, PageData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x25\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PageAdr.to_bytes(length=1, byteorder='big'))
        if len(PageData) != 4:
            raise ValueError(PageData)
        _send_buffer.write(PageData)
        return _send_buffer.getvalue()
    def __call__(self, PageAdr: int, PageData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(PageAdr=PageAdr, PageData=PageData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Ultralight_AuthE2(Command):
    CommandGroupId = 0x25
    CommandId = 0x03
    def build_frame(self, DivMode: Ultralight_AuthE2_DivMode = "NoDiv", HasExtIdx: bool = False, *, KeyIdx: int, DivData: bytes, KeyExtIdx: Optional[int] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x25\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (Ultralight_AuthE2_DivMode_Parser.as_value(DivMode) & 0b11) << 1
        _var_0000_int |= (int(HasExtIdx) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(KeyIdx.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(DivData)).to_bytes(1, byteorder='big'))
        _send_buffer.write(DivData)
        if HasExtIdx:
            if KeyExtIdx is None:
                raise TypeError("missing a required argument: 'KeyExtIdx'")
            _send_buffer.write(KeyExtIdx.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, DivMode: Ultralight_AuthE2_DivMode = "NoDiv", HasExtIdx: bool = False, *, KeyIdx: int, DivData: bytes, KeyExtIdx: Optional[int] = None, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(DivMode=DivMode, HasExtIdx=HasExtIdx, KeyIdx=KeyIdx, DivData=DivData, KeyExtIdx=KeyExtIdx, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Ultralight_AuthUser(Command):
    CommandGroupId = 0x25
    CommandId = 0x04
    def build_frame(self, CryptoMode: Ultralight_AuthUser_CryptoMode = "TripleDES", *, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x25\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (Ultralight_AuthUser_CryptoMode_Parser.as_value(CryptoMode) & 0b11) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Key)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, CryptoMode: Ultralight_AuthUser_CryptoMode = "TripleDES", *, Key: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CryptoMode=CryptoMode, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class Ultralight_SectorSwitch(Command):
    CommandGroupId = 0x25
    CommandId = 0x05
    def build_frame(self, SectorNumber: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x25\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SectorNumber.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SectorNumber: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(SectorNumber=SectorNumber, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UlRdr_SendAuth1(Command):
    CommandGroupId = 0xA5
    CommandId = 0x00
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA5\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> UlRdr_SendAuth1_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SendDevCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _SendCmdCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _SendParams_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _SendParams = _recv_buffer.read(_SendParams_len)
        if len(_SendParams) != _SendParams_len:
            raise PayloadTooShortError(_SendParams_len - len(_SendParams))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return UlRdr_SendAuth1_Result(_SendDevCode, _SendCmdCode, _SendParams)
class UlRdr_RecvAuth1(Command):
    CommandGroupId = 0xA5
    CommandId = 0x01
    def build_frame(self, RecvStatus: int, RecvResult: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA5\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(RecvStatus.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(RecvResult)).to_bytes(2, byteorder='big'))
        _send_buffer.write(RecvResult)
        return _send_buffer.getvalue()
    def __call__(self, RecvStatus: int, RecvResult: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(RecvStatus=RecvStatus, RecvResult=RecvResult, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UlRdr_SendAuth2(Command):
    CommandGroupId = 0xA5
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA5\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> UlRdr_SendAuth2_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SendDevCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _SendCmdCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _SendParams_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _SendParams = _recv_buffer.read(_SendParams_len)
        if len(_SendParams) != _SendParams_len:
            raise PayloadTooShortError(_SendParams_len - len(_SendParams))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return UlRdr_SendAuth2_Result(_SendDevCode, _SendCmdCode, _SendParams)
class UlRdr_RecvAuth2(Command):
    CommandGroupId = 0xA5
    CommandId = 0x03
    def build_frame(self, RecvStatus: int, RecvResult: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA5\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(RecvStatus.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(RecvResult)).to_bytes(2, byteorder='big'))
        _send_buffer.write(RecvResult)
        return _send_buffer.getvalue()
    def __call__(self, RecvStatus: int, RecvResult: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(RecvStatus=RecvStatus, RecvResult=RecvResult, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UlRdr_SendEncryptedCmd(Command):
    CommandGroupId = 0xA5
    CommandId = 0x04
    def build_frame(self, Signature: bytes, DevCode: int, CmdCode: int, Params: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA5\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Signature) != 16:
            raise ValueError(Signature)
        _send_buffer.write(Signature)
        _send_buffer.write(DevCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CmdCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Params)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Params)
        return _send_buffer.getvalue()
    def __call__(self, Signature: bytes, DevCode: int, CmdCode: int, Params: bytes, BrpTimeout: int = 100) -> UlRdr_SendEncryptedCmd_Result:
        request_frame = self.build_frame(Signature=Signature, DevCode=DevCode, CmdCode=CmdCode, Params=Params, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SendDevCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _SendCmdCode = safe_read_int_from_buffer(_recv_buffer, 1)
        _SendParams_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _SendParams = _recv_buffer.read(_SendParams_len)
        if len(_SendParams) != _SendParams_len:
            raise PayloadTooShortError(_SendParams_len - len(_SendParams))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return UlRdr_SendEncryptedCmd_Result(_SendDevCode, _SendCmdCode, _SendParams)
class UlRdr_RecvEncryptedCmd(Command):
    CommandGroupId = 0xA5
    CommandId = 0x05
    def build_frame(self, RecvStatus: int, RecvResult: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA5\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(RecvStatus.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(RecvResult)).to_bytes(2, byteorder='big'))
        _send_buffer.write(RecvResult)
        return _send_buffer.getvalue()
    def __call__(self, RecvStatus: int, RecvResult: bytes, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(RecvStatus=RecvStatus, RecvResult=RecvResult, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Status
class UsbHost_Enable(Command):
    CommandGroupId = 0x44
    CommandId = 0x01
    def build_frame(self, Enable: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_IsConnected(Command):
    CommandGroupId = 0x44
    CommandId = 0x02
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bool:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Connected = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Connected
class UsbHost_SetupPipes(Command):
    CommandGroupId = 0x44
    CommandId = 0x03
    def build_frame(self, Pipes: List[UsbHost_SetupPipes_Pipes_Entry], BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Pipes)).to_bytes(1, byteorder='big'))
        for _Pipes_Entry in Pipes:
            _No, _Type, _FrameSize = _Pipes_Entry
            _send_buffer.write(_No.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(UsbHost_SetupPipes_Type_Parser.as_value(_Type).to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_FrameSize.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Pipes: List[UsbHost_SetupPipes_Pipes_Entry], BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Pipes=Pipes, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_SetAddr(Command):
    CommandGroupId = 0x44
    CommandId = 0x04
    def build_frame(self, Address: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Address: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Address=Address, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_Reset(Command):
    CommandGroupId = 0x44
    CommandId = 0x05
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_TransRawSetup(Command):
    CommandGroupId = 0x44
    CommandId = 0x06
    def build_frame(self, SetupData: bytes, PipeNo: int = 0, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(SetupData) != 8:
            raise ValueError(SetupData)
        _send_buffer.write(SetupData)
        _send_buffer.write(PipeNo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SetupData: bytes, PipeNo: int = 0, Timeout: int = 100, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(SetupData=SetupData, PipeNo=PipeNo, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_TransSetupIn(Command):
    CommandGroupId = 0x44
    CommandId = 0x07
    def build_frame(self, SetupData: bytes, PipeNo: int = 0, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(SetupData) != 8:
            raise ValueError(SetupData)
        _send_buffer.write(SetupData)
        _send_buffer.write(PipeNo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SetupData: bytes, PipeNo: int = 0, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(SetupData=SetupData, PipeNo=PipeNo, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _InData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _InData = _recv_buffer.read(_InData_len)
        if len(_InData) != _InData_len:
            raise PayloadTooShortError(_InData_len - len(_InData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _InData
class UsbHost_TransSetupOut(Command):
    CommandGroupId = 0x44
    CommandId = 0x08
    def build_frame(self, SetupData: bytes, OutData: bytes, PipeNo: int = 0, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(SetupData) != 8:
            raise ValueError(SetupData)
        _send_buffer.write(SetupData)
        _send_buffer.write(int(len(OutData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(OutData)
        _send_buffer.write(PipeNo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SetupData: bytes, OutData: bytes, PipeNo: int = 0, Timeout: int = 100, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(SetupData=SetupData, OutData=OutData, PipeNo=PipeNo, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_TransIn(Command):
    CommandGroupId = 0x44
    CommandId = 0x09
    def build_frame(self, PipeNo: int, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(PipeNo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, PipeNo: int, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(PipeNo=PipeNo, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _InData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _InData = _recv_buffer.read(_InData_len)
        if len(_InData) != _InData_len:
            raise PayloadTooShortError(_InData_len - len(_InData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _InData
class UsbHost_TransOut(Command):
    CommandGroupId = 0x44
    CommandId = 0x0A
    def build_frame(self, OutData: bytes, PipeNo: int, Continue: bool = False, Timeout: int = 100, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(OutData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(OutData)
        _send_buffer.write(PipeNo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Continue.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, OutData: bytes, PipeNo: int, Continue: bool = False, Timeout: int = 100, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(OutData=OutData, PipeNo=PipeNo, Continue=Continue, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_Suspend(Command):
    CommandGroupId = 0x44
    CommandId = 0x0B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x0B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UsbHost_Resume(Command):
    CommandGroupId = 0x44
    CommandId = 0x0C
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x44\x0C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UI_Enable(Command):
    CommandGroupId = 0x0A
    CommandId = 0x01
    def build_frame(self, Port: IoPort, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0A\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(IoPort_Parser.as_value(Port).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: IoPort, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Port=Port, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UI_Disable(Command):
    CommandGroupId = 0x0A
    CommandId = 0x02
    def build_frame(self, Port: IoPort, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0A\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(IoPort_Parser.as_value(Port).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: IoPort, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Port=Port, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UI_Toggle(Command):
    CommandGroupId = 0x0A
    CommandId = 0x03
    def build_frame(self, Port: IoPort, ToggleCount: int, Timespan1: int, Timespan2: int, Polarity: UI_Toggle_Polarity, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0A\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(IoPort_Parser.as_value(Port).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ToggleCount.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timespan1.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Timespan2.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(UI_Toggle_Polarity_Parser.as_value(Polarity).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: IoPort, ToggleCount: int, Timespan1: int, Timespan2: int, Polarity: UI_Toggle_Polarity, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Port=Port, ToggleCount=ToggleCount, Timespan1=Timespan1, Timespan2=Timespan2, Polarity=Polarity, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UI_SetRgbLed(Command):
    CommandGroupId = 0x0A
    CommandId = 0x20
    def build_frame(self, LedState: Union[LedBitMask, LedBitMask_Dict], RgbColor: int, TransitionTime: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0A\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if isinstance(LedState, dict):
            LedState = LedBitMask(**LedState)
        LedState_int = 0
        LedState_int |= (int(LedState.LeftLed) & 0b1) << 2
        LedState_int |= (int(LedState.RightLed) & 0b1) << 1
        LedState_int |= (int(LedState.SingleLed) & 0b1) << 0
        _send_buffer.write(LedState_int.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(RgbColor.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(TransitionTime.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, LedState: Union[LedBitMask, LedBitMask_Dict], RgbColor: int, TransitionTime: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(LedState=LedState, RgbColor=RgbColor, TransitionTime=TransitionTime, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class UI_PulseRgbLed(Command):
    CommandGroupId = 0x0A
    CommandId = 0x21
    def build_frame(self, LedState: Union[LedBitMask, LedBitMask_Dict], RgbColor1: int, RgbColor2: int, TransitionTime: int, Period: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x0A\x21")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if isinstance(LedState, dict):
            LedState = LedBitMask(**LedState)
        LedState_int = 0
        LedState_int |= (int(LedState.LeftLed) & 0b1) << 2
        LedState_int |= (int(LedState.RightLed) & 0b1) << 1
        LedState_int |= (int(LedState.SingleLed) & 0b1) << 0
        _send_buffer.write(LedState_int.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(RgbColor1.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(RgbColor2.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(TransitionTime.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Period.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, LedState: Union[LedBitMask, LedBitMask_Dict], RgbColor1: int, RgbColor2: int, TransitionTime: int, Period: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(LedState=LedState, RgbColor1=RgbColor1, RgbColor2=RgbColor2, TransitionTime=TransitionTime, Period=Period, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_Select(Command):
    CommandGroupId = 0x01
    CommandId = 0x00
    def build_frame(self, CardFamiliesFilter: Union[CardFamilies, CardFamilies_Dict] = CardFamilies.All(), Reselect: bool = False, AcceptConfCard: bool = False, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if isinstance(CardFamiliesFilter, dict):
            CardFamiliesFilter = CardFamilies(**CardFamiliesFilter)
        CardFamiliesFilter_int = 0
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.LEGICPrime) & 0b1) << 11
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.BluetoothMce) & 0b1) << 10
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Khz125Part2) & 0b1) << 9
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Srix) & 0b1) << 8
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Khz125Part1) & 0b1) << 7
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Felica) & 0b1) << 6
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.IClass) & 0b1) << 5
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.IClassIso14B) & 0b1) << 4
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Iso14443B) & 0b1) << 3
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Iso15693) & 0b1) << 2
        CardFamiliesFilter_int |= (int(CardFamiliesFilter.Iso14443A) & 0b1) << 0
        _send_buffer.write(CardFamiliesFilter_int.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Reselect.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AcceptConfCard.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CardFamiliesFilter: Union[CardFamilies, CardFamilies_Dict] = CardFamilies.All(), Reselect: bool = False, AcceptConfCard: bool = False, BrpTimeout: int = 3000) -> CardType:
        request_frame = self.build_frame(CardFamiliesFilter=CardFamiliesFilter, Reselect=Reselect, AcceptConfCard=AcceptConfCard, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SelectedCardType = CardType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _SelectedCardType
class VHL_GetSnr(Command):
    CommandGroupId = 0x01
    CommandId = 0x01
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Snr = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Snr
class VHL_Read(Command):
    CommandGroupId = 0x01
    CommandId = 0x02
    def build_frame(self, Id: int = 255, Adr: int = 0, *, Len: int, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Id.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Id: int = 255, Adr: int = 0, *, Len: int, BrpTimeout: int = 3000) -> bytes:
        request_frame = self.build_frame(Id=Id, Adr=Adr, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class VHL_Write(Command):
    CommandGroupId = 0x01
    CommandId = 0x03
    def build_frame(self, Id: int = 255, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Id.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Id: int = 255, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(Id=Id, Adr=Adr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_IsSelected(Command):
    CommandGroupId = 0x01
    CommandId = 0x04
    def build_frame(self, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_GetLegacyATR(Command):
    CommandGroupId = 0x01
    CommandId = 0x05
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATR_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ATR = _recv_buffer.read(_ATR_len)
        if len(_ATR) != _ATR_len:
            raise PayloadTooShortError(_ATR_len - len(_ATR))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ATR
class VHL_ExchangeAPDU(Command):
    CommandGroupId = 0x01
    CommandId = 0x06
    def build_frame(self, AssumedCardType: CardType = "Default", *, Cmd: bytes, BrpTimeout: int = 60000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CardType_Parser.as_value(AssumedCardType).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Cmd)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Cmd)
        return _send_buffer.getvalue()
    def __call__(self, AssumedCardType: CardType = "Default", *, Cmd: bytes, BrpTimeout: int = 60000) -> bytes:
        request_frame = self.build_frame(AssumedCardType=AssumedCardType, Cmd=Cmd, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Resp
class VHL_Setup(Command):
    CommandGroupId = 0x01
    CommandId = 0x07
    def build_frame(self, ConsideredCardType: CardType = "Default", MifareKey: Optional[bytes] = b'\xff\xff\xff\xff\xff\xff', AsKeyA: Optional[bool] = True, MadId: Optional[int] = None, AppId: Optional[int] = 0, DesfireFileDesc: Optional[Union[DesfireFileDescription, DesfireFileDescription_Dict]] = None, Key: Optional[bytes] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', SegmentInfo: Optional[bytes] = b'\x01', EnStamp: Optional[bool] = False, AdrMode: Optional[VHL_Setup_AdrMode] = "ProtocolHeader", FirstBlock: Optional[int] = None, BlockCount: Optional[int] = None, OptionFlag: Optional[VHL_Setup_OptionFlag] = None, BlockSize: Optional[int] = None, SelectFileCmdListLen: Optional[int] = None, SelectFileCmdList: Optional[List[VHL_Setup_SelectFileCmdList_Entry]] = None, FileLen: Optional[int] = 4294967295, ApduTimeout: Optional[int] = 2500, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CardType_Parser.as_value(ConsideredCardType).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(b'\x00')
        if ConsideredCardType == "MifareClassic":
            if MifareKey is None:
                raise TypeError("missing a required argument: 'MifareKey'")
            if AsKeyA is None:
                raise TypeError("missing a required argument: 'AsKeyA'")
            if MadId is None:
                raise TypeError("missing a required argument: 'MadId'")
            _send_buffer.write(b'\x06')
            if len(MifareKey) != 6:
                raise ValueError(MifareKey)
            _send_buffer.write(MifareKey)
            _send_buffer.write(b'\x01')
            _send_buffer.write(AsKeyA.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(b'\x02')
            _send_buffer.write(MadId.to_bytes(length=2, byteorder='big'))
        if ConsideredCardType == "MifareDesfire":
            if AppId is None:
                raise TypeError("missing a required argument: 'AppId'")
            if DesfireFileDesc is None:
                raise TypeError("missing a required argument: 'DesfireFileDesc'")
            if Key is None:
                raise TypeError("missing a required argument: 'Key'")
            _send_buffer.write(b'\x04')
            _send_buffer.write(AppId.to_bytes(length=4, byteorder='big'))
            _send_buffer.write(b'\x10')
            if isinstance(DesfireFileDesc, dict):
                DesfireFileDesc = DesfireFileDescription(**DesfireFileDesc)
            _FileNo, _FileCommunicationSecurity, _FileType, _ReadKeyNo, _WriteKeyNo, _Offset, _Length, _ReadKeyIdx, _WriteKeyIdx, _AccessRightsLowByte, _ChangeKeyIdx, _FileSize, _IsoFid = DesfireFileDesc
            _send_buffer.write(_FileNo.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(DesfireFileDescription_FileCommunicationSecurity_Parser.as_value(_FileCommunicationSecurity).to_bytes(length=1, byteorder='big'))
            _send_buffer.write(DesfireFileDescription_FileType_Parser.as_value(_FileType).to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_ReadKeyNo.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_WriteKeyNo.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_Offset.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(_Length.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(_ReadKeyIdx.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_WriteKeyIdx.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_AccessRightsLowByte.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_ChangeKeyIdx.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(_FileSize.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(_IsoFid.to_bytes(length=2, byteorder='big'))
            _send_buffer.write(int(len(Key)).to_bytes(1, byteorder='big'))
            _send_buffer.write(Key)
        if ConsideredCardType == "LEGICPrimeLegacy" or ConsideredCardType == "LEGICAdvantLegacy" or ConsideredCardType == "LEGICPrime" or ConsideredCardType == "LEGICAdvantIso14443a" or ConsideredCardType == "LEGICAdvantIso15693":
            if SegmentInfo is None:
                raise TypeError("missing a required argument: 'SegmentInfo'")
            if EnStamp is None:
                raise TypeError("missing a required argument: 'EnStamp'")
            if AdrMode is None:
                raise TypeError("missing a required argument: 'AdrMode'")
            _send_buffer.write(int(len(SegmentInfo)).to_bytes(1, byteorder='big'))
            _send_buffer.write(SegmentInfo)
            _send_buffer.write(b'\x01')
            _send_buffer.write(EnStamp.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(b'\x01')
            _send_buffer.write(VHL_Setup_AdrMode_Parser.as_value(AdrMode).to_bytes(length=1, byteorder='big'))
        if ConsideredCardType == "Iso15693":
            if FirstBlock is None:
                raise TypeError("missing a required argument: 'FirstBlock'")
            if BlockCount is None:
                raise TypeError("missing a required argument: 'BlockCount'")
            if OptionFlag is None:
                raise TypeError("missing a required argument: 'OptionFlag'")
            if BlockSize is None:
                raise TypeError("missing a required argument: 'BlockSize'")
            _send_buffer.write(b'\x01')
            _send_buffer.write(FirstBlock.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(b'\x01')
            _send_buffer.write(BlockCount.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(b'\x01')
            _send_buffer.write(VHL_Setup_OptionFlag_Parser.as_value(OptionFlag).to_bytes(length=1, byteorder='big'))
            _send_buffer.write(b'\x01')
            _send_buffer.write(BlockSize.to_bytes(length=1, byteorder='big'))
        if ConsideredCardType == "Iso14443aInterIndustry" or ConsideredCardType == "Iso14443aIntIndustryMif":
            if SelectFileCmdListLen is None:
                raise TypeError("missing a required argument: 'SelectFileCmdListLen'")
            if SelectFileCmdList is None:
                raise TypeError("missing a required argument: 'SelectFileCmdList'")
            if FileLen is None:
                raise TypeError("missing a required argument: 'FileLen'")
            if ApduTimeout is None:
                raise TypeError("missing a required argument: 'ApduTimeout'")
            _send_buffer.write(SelectFileCmdListLen.to_bytes(length=1, byteorder='big'))
            _send_buffer.write(int(len(SelectFileCmdList)).to_bytes(1, byteorder='big'))
            for _SelectFileCmdList_Entry in SelectFileCmdList:
                _FileSpecifier, _Name, _Path, _ApduCommand = _SelectFileCmdList_Entry
                _send_buffer.write(VHL_Setup_FileSpecifier_Parser.as_value(_FileSpecifier).to_bytes(length=1, byteorder='big'))
                if _FileSpecifier == "SelectByName":
                    if _Name is None:
                        raise TypeError("missing a required argument: '_Name'")
                    _send_buffer.write(int(len(_Name)).to_bytes(1, byteorder='big'))
                    _send_buffer.write(_Name)
                if _FileSpecifier == "SelectByPath":
                    if _Path is None:
                        raise TypeError("missing a required argument: '_Path'")
                    _send_buffer.write(int(len(_Path)).to_bytes(1, byteorder='big'))
                    _send_buffer.write(_Path)
                if _FileSpecifier == "SelectByAPDU":
                    if _ApduCommand is None:
                        raise TypeError("missing a required argument: '_ApduCommand'")
                    _send_buffer.write(int(len(_ApduCommand)).to_bytes(1, byteorder='big'))
                    _send_buffer.write(_ApduCommand)
            _send_buffer.write(b'\x04')
            _send_buffer.write(FileLen.to_bytes(length=4, byteorder='big'))
            _send_buffer.write(b'\x02')
            _send_buffer.write(ApduTimeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ConsideredCardType: CardType = "Default", MifareKey: Optional[bytes] = b'\xff\xff\xff\xff\xff\xff', AsKeyA: Optional[bool] = True, MadId: Optional[int] = None, AppId: Optional[int] = 0, DesfireFileDesc: Optional[Union[DesfireFileDescription, DesfireFileDescription_Dict]] = None, Key: Optional[bytes] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', SegmentInfo: Optional[bytes] = b'\x01', EnStamp: Optional[bool] = False, AdrMode: Optional[VHL_Setup_AdrMode] = "ProtocolHeader", FirstBlock: Optional[int] = None, BlockCount: Optional[int] = None, OptionFlag: Optional[VHL_Setup_OptionFlag] = None, BlockSize: Optional[int] = None, SelectFileCmdListLen: Optional[int] = None, SelectFileCmdList: Optional[List[VHL_Setup_SelectFileCmdList_Entry]] = None, FileLen: Optional[int] = 4294967295, ApduTimeout: Optional[int] = 2500, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ConsideredCardType=ConsideredCardType, MifareKey=MifareKey, AsKeyA=AsKeyA, MadId=MadId, AppId=AppId, DesfireFileDesc=DesfireFileDesc, Key=Key, SegmentInfo=SegmentInfo, EnStamp=EnStamp, AdrMode=AdrMode, FirstBlock=FirstBlock, BlockCount=BlockCount, OptionFlag=OptionFlag, BlockSize=BlockSize, SelectFileCmdListLen=SelectFileCmdListLen, SelectFileCmdList=SelectFileCmdList, FileLen=FileLen, ApduTimeout=ApduTimeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_SetupMifare(Command):
    CommandGroupId = 0x01
    CommandId = 0x08
    def build_frame(self, CustomKey: bool = False, KeyA: bool = True, Key: Optional[bytes] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(CustomKey) & 0b1) << 1
        _var_0000_int |= (int(KeyA) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        if CustomKey:
            if Key is None:
                raise TypeError("missing a required argument: 'Key'")
            if len(Key) != 6:
                raise ValueError(Key)
            _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, CustomKey: bool = False, KeyA: bool = True, Key: Optional[bytes] = None, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CustomKey=CustomKey, KeyA=KeyA, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_SetupLegic(Command):
    CommandGroupId = 0x01
    CommandId = 0x09
    def build_frame(self, StampLen: int = 0, SegmentID: Optional[int] = 1, Stamp: Optional[bytes] = None, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x09")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StampLen.to_bytes(length=1, byteorder='big'))
        if StampLen == 0:
            if SegmentID is None:
                raise TypeError("missing a required argument: 'SegmentID'")
            _send_buffer.write(SegmentID.to_bytes(length=1, byteorder='big'))
        if StampLen > 0:
            if Stamp is None:
                raise TypeError("missing a required argument: 'Stamp'")
            _send_buffer.write(Stamp)
        return _send_buffer.getvalue()
    def __call__(self, StampLen: int = 0, SegmentID: Optional[int] = 1, Stamp: Optional[bytes] = None, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(StampLen=StampLen, SegmentID=SegmentID, Stamp=Stamp, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_SetupISO15(Command):
    CommandGroupId = 0x01
    CommandId = 0x0A
    def build_frame(self, FirstBlock: int = 0, BlockCount: int = 255, OptionFlag: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x0A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FirstBlock.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockCount.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OptionFlag.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, FirstBlock: int = 0, BlockCount: int = 255, OptionFlag: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FirstBlock=FirstBlock, BlockCount=BlockCount, OptionFlag=OptionFlag, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_CheckReconfigErr(Command):
    CommandGroupId = 0x01
    CommandId = 0x0B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x0B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bool:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Failed = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Failed
class VHL_ExchangeLongAPDU(Command):
    CommandGroupId = 0x01
    CommandId = 0x0C
    def build_frame(self, AssumedCardType: CardType = "Default", Reset: bool = False, ContinueCmd: bool = False, *, Cmd: bytes, BrpTimeout: int = 60000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x0C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CardType_Parser.as_value(AssumedCardType).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Reset.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(ContinueCmd.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Cmd)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Cmd)
        return _send_buffer.getvalue()
    def __call__(self, AssumedCardType: CardType = "Default", Reset: bool = False, ContinueCmd: bool = False, *, Cmd: bytes, BrpTimeout: int = 60000) -> VHL_ExchangeLongAPDU_Result:
        request_frame = self.build_frame(AssumedCardType=AssumedCardType, Reset=Reset, ContinueCmd=ContinueCmd, Cmd=Cmd, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ContinueResp = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _Resp_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Resp = _recv_buffer.read(_Resp_len)
        if len(_Resp) != _Resp_len:
            raise PayloadTooShortError(_Resp_len - len(_Resp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return VHL_ExchangeLongAPDU_Result(_ContinueResp, _Resp)
class VHL_GetFileInfo(Command):
    CommandGroupId = 0x01
    CommandId = 0x0D
    def build_frame(self, Id: int = 255, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x0D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Id.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Id: int = 255, BrpTimeout: int = 100) -> VHL_GetFileInfo_Result:
        request_frame = self.build_frame(Id=Id, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Len = safe_read_int_from_buffer(_recv_buffer, 2)
        _BlockSize = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return VHL_GetFileInfo_Result(_Len, _BlockSize)
class VHL_GetATR(Command):
    CommandGroupId = 0x01
    CommandId = 0x0E
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x0E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATR_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ATR = _recv_buffer.read(_ATR_len)
        if len(_ATR) != _ATR_len:
            raise PayloadTooShortError(_ATR_len - len(_ATR))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ATR
class VHL_Format(Command):
    CommandGroupId = 0x01
    CommandId = 0x0F
    def build_frame(self, Id: int, BrpTimeout: int = 4000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x0F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Id.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Id: int, BrpTimeout: int = 4000) -> None:
        request_frame = self.build_frame(Id=Id, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class VHL_ResolveFilename(Command):
    CommandGroupId = 0x01
    CommandId = 0x10
    def build_frame(self, FileName: str, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(FileName)).to_bytes(1, byteorder='big'))
        _send_buffer.write(FileName.encode("ascii"))
        return _send_buffer.getvalue()
    def __call__(self, FileName: str, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(FileName=FileName, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Id = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Id
class VHL_GetCardType(Command):
    CommandGroupId = 0x01
    CommandId = 0x11
    def build_frame(self, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\x01\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 3000) -> CardType:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SelectedCardType = CardType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _SelectedCardType
class DHWCtrl_PortConfig(Command):
    CommandGroupId = 0xE0
    CommandId = 0x00
    def build_frame(self, Port: int, Mode: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x00")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, Mode: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Port=Port, Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PortGet(Command):
    CommandGroupId = 0xE0
    CommandId = 0x01
    def build_frame(self, Port: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x01")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, BrpTimeout: int = 100) -> bool:
        request_frame = self.build_frame(Port=Port, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Level = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Level
class DHWCtrl_PortSet(Command):
    CommandGroupId = 0xE0
    CommandId = 0x02
    def build_frame(self, Port: int, Level: bool, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x02")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Level.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, Level: bool, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Port=Port, Level=Level, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PortWait(Command):
    CommandGroupId = 0xE0
    CommandId = 0x05
    def build_frame(self, Port: int, Level: bool, Timeout: int = 65535, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x05")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Level.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, Level: bool, Timeout: int = 65535, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(Port=Port, Level=Level, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReactionTime = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReactionTime
class DHWCtrl_GetResetCause(Command):
    CommandGroupId = 0xE0
    CommandId = 0x06
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x06")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ResetCause = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ResetCause
class DHWCtrl_APortMeasure(Command):
    CommandGroupId = 0xE0
    CommandId = 0x07
    def build_frame(self, Port: int, Count: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x07")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Count.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, Count: int, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(Port=Port, Count=Count, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Voltages = []  # type: ignore[var-annotated,unused-ignore]
        while not _recv_buffer.tell() >= len(_recv_buffer.getvalue()):
            _Voltage = safe_read_int_from_buffer(_recv_buffer, 2)
            _Voltages.append(_Voltage)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Voltages
class DHWCtrl_SRAMTest(Command):
    CommandGroupId = 0xE0
    CommandId = 0x04
    def build_frame(self, SramSize: int, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x04")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(SramSize.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, SramSize: int, BrpTimeout: int = 1000) -> bool:
        request_frame = self.build_frame(SramSize=SramSize, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Success = bool(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Success
class DHWCtrl_SetBaudrate(Command):
    CommandGroupId = 0xE0
    CommandId = 0x03
    def build_frame(self, NewBaudrate: Baudrate = "Baud115200", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x03")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Baudrate_Parser.as_value(NewBaudrate).to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, NewBaudrate: Baudrate = "Baud115200", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(NewBaudrate=NewBaudrate, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_MirrorData(Command):
    CommandGroupId = 0xE0
    CommandId = 0x08
    def build_frame(self, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x08")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Data: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _MirroredData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _MirroredData = _recv_buffer.read(_MirroredData_len)
        if len(_MirroredData) != _MirroredData_len:
            raise PayloadTooShortError(_MirroredData_len - len(_MirroredData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _MirroredData
class DHWCtrl_DispEnable(Command):
    CommandGroupId = 0xE0
    CommandId = 0x10
    def build_frame(self, Enable: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x10")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_DispBacklight(Command):
    CommandGroupId = 0xE0
    CommandId = 0x11
    def build_frame(self, Backlight: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x11")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Backlight.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Backlight: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Backlight=Backlight, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_DispColor(Command):
    CommandGroupId = 0xE0
    CommandId = 0x12
    def build_frame(self, Color: int = 255, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x12")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Color.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Color: int = 255, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Color=Color, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_DispContrast(Command):
    CommandGroupId = 0xE0
    CommandId = 0x13
    def build_frame(self, Contrast: int = 128, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x13")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Contrast.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Contrast: int = 128, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Contrast=Contrast, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_DispBox(Command):
    CommandGroupId = 0xE0
    CommandId = 0x14
    def build_frame(self, X: int = 0, Y: int = 0, Width: int = 128, Height: int = 64, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x14")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(X.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Y.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Width.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Height.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, X: int = 0, Y: int = 0, Width: int = 128, Height: int = 64, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(X=X, Y=Y, Width=Width, Height=Height, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_Ser2Ctrl(Command):
    CommandGroupId = 0xE0
    CommandId = 0x15
    def build_frame(self, InterfaceID: int = 0, *, Enable: bool, NewBaudrate: Baudrate = "Baud115200", NewParity: Parity, Stopbits: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x15")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(InterfaceID.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Baudrate_Parser.as_value(NewBaudrate).to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Parity_Parser.as_value(NewParity).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Stopbits.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, InterfaceID: int = 0, *, Enable: bool, NewBaudrate: Baudrate = "Baud115200", NewParity: Parity, Stopbits: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(InterfaceID=InterfaceID, Enable=Enable, NewBaudrate=NewBaudrate, NewParity=NewParity, Stopbits=Stopbits, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_Ser2WriteRead(Command):
    CommandGroupId = 0xE0
    CommandId = 0x16
    def build_frame(self, MaxReadCount: int = 1, Timeout: int = 10, *, WriteData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x16")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(MaxReadCount.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(WriteData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(WriteData)
        return _send_buffer.getvalue()
    def __call__(self, MaxReadCount: int = 1, Timeout: int = 10, *, WriteData: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(MaxReadCount=MaxReadCount, Timeout=Timeout, WriteData=WriteData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _ReadData = _recv_buffer.read(_ReadData_len)
        if len(_ReadData) != _ReadData_len:
            raise PayloadTooShortError(_ReadData_len - len(_ReadData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadData
class DHWCtrl_Ser2Flush(Command):
    CommandGroupId = 0xE0
    CommandId = 0x20
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x20")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_Delay1ms(Command):
    CommandGroupId = 0xE0
    CommandId = 0x17
    def build_frame(self, Delay: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x17")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Delay.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Delay: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Delay=Delay, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_Delay10us(Command):
    CommandGroupId = 0xE0
    CommandId = 0x18
    def build_frame(self, Delay: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x18")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Delay.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Delay: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Delay=Delay, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PowermgrSuspend(Command):
    CommandGroupId = 0xE0
    CommandId = 0x19
    def build_frame(self, Delay: int = 65535, KeyboardWakeup: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x19")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Delay.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(KeyboardWakeup.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Delay: int = 65535, KeyboardWakeup: bool = False, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Delay=Delay, KeyboardWakeup=KeyboardWakeup, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_ScanMatrix(Command):
    CommandGroupId = 0xE0
    CommandId = 0x1A
    def build_frame(self, Bitmask: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x1A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Bitmask.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Bitmask: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Bitmask=Bitmask, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_GetReaderChipType(Command):
    CommandGroupId = 0xE0
    CommandId = 0x1B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x1B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> DHWCtrl_GetReaderChipType_ChipType:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ChipType = DHWCtrl_GetReaderChipType_ChipType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ChipType
class DHWCtrl_SelectAntenna(Command):
    CommandGroupId = 0xE0
    CommandId = 0x1C
    def build_frame(self, Ant: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x1C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Ant.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Ant: int = 0, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Ant=Ant, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_GetSamType(Command):
    CommandGroupId = 0xE0
    CommandId = 0x1D
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x1D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> DHWCtrl_GetSamType_ChipType:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ChipType = DHWCtrl_GetSamType_ChipType_Parser.as_literal(safe_read_int_from_buffer(_recv_buffer, 1))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ChipType
class DHWCtrl_HfAcquire(Command):
    CommandGroupId = 0xE0
    CommandId = 0x1E
    def build_frame(self, ModuleId: DHWCtrl_HfAcquire_ModuleId = "No", BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x1E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DHWCtrl_HfAcquire_ModuleId_Parser.as_value(ModuleId).to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ModuleId: DHWCtrl_HfAcquire_ModuleId = "No", BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(ModuleId=ModuleId, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_EepromWrite(Command):
    CommandGroupId = 0xE0
    CommandId = 0x21
    def build_frame(self, Address: int, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x21")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Address: int, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Address=Address, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_DataflashGetSize(Command):
    CommandGroupId = 0xE0
    CommandId = 0x22
    def build_frame(self, Device: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x22")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Device.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Device: int = 0, BrpTimeout: int = 100) -> DHWCtrl_DataflashGetSize_Result:
        request_frame = self.build_frame(Device=Device, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PageCount = safe_read_int_from_buffer(_recv_buffer, 2)
        _PageSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return DHWCtrl_DataflashGetSize_Result(_PageCount, _PageSize)
class DHWCtrl_DataflashErasePages(Command):
    CommandGroupId = 0xE0
    CommandId = 0x23
    def build_frame(self, Device: int = 0, StartPage: int = 0, Len: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x23")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Device.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(StartPage.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Device: int = 0, StartPage: int = 0, Len: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Device=Device, StartPage=StartPage, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_DataflashRead(Command):
    CommandGroupId = 0xE0
    CommandId = 0x24
    def build_frame(self, Device: int = 0, Page: int = 0, StartAdr: int = 0, Len: int = 5, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x24")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Device.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Page.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Device: int = 0, Page: int = 0, StartAdr: int = 0, Len: int = 5, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Device=Device, Page=Page, StartAdr=StartAdr, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class DHWCtrl_DataflashWrite(Command):
    CommandGroupId = 0xE0
    CommandId = 0x25
    def build_frame(self, Device: int = 0, Mode: int = 1, Page: int = 0, StartAdr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x25")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Device.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Page.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Device: int = 0, Mode: int = 1, Page: int = 0, StartAdr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Device=Device, Mode=Mode, Page=Page, StartAdr=StartAdr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_EepromRead(Command):
    CommandGroupId = 0xE0
    CommandId = 0x26
    def build_frame(self, StartAdr: int = 0, Len: int = 5, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x26")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, StartAdr: int = 0, Len: int = 5, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(StartAdr=StartAdr, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class DHWCtrl_SecurityAndConfigReset(Command):
    CommandGroupId = 0xE0
    CommandId = 0x27
    def build_frame(self, BrpTimeout: int = 10000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x27")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 10000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PulseGenerate(Command):
    CommandGroupId = 0xE0
    CommandId = 0x28
    def build_frame(self, Port: int, Frequency: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x28")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Port.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Frequency.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Port: int, Frequency: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Port=Port, Frequency=Frequency, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitSer2(Command):
    CommandGroupId = 0xE0
    CommandId = 0x31
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x31")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitRtc(Command):
    CommandGroupId = 0xE0
    CommandId = 0x32
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x32")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitLcdDrv(Command):
    CommandGroupId = 0xE0
    CommandId = 0x33
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x33")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitRc(Command):
    CommandGroupId = 0xE0
    CommandId = 0x34
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x34")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitMf(Command):
    CommandGroupId = 0xE0
    CommandId = 0x35
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x35")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitIso14A(Command):
    CommandGroupId = 0xE0
    CommandId = 0x36
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x36")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitIso14B(Command):
    CommandGroupId = 0xE0
    CommandId = 0x37
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x37")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitIso15(Command):
    CommandGroupId = 0xE0
    CommandId = 0x38
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x38")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitLg(Command):
    CommandGroupId = 0xE0
    CommandId = 0x39
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x39")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitLga(Command):
    CommandGroupId = 0xE0
    CommandId = 0x3A
    def build_frame(self, BrpTimeout: int = 3000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x3A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 3000) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitDf(Command):
    CommandGroupId = 0xE0
    CommandId = 0x3B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x3B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitRc125(Command):
    CommandGroupId = 0xE0
    CommandId = 0x3C
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x3C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitCc(Command):
    CommandGroupId = 0xE0
    CommandId = 0x3D
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x3D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitUsbHost(Command):
    CommandGroupId = 0xE0
    CommandId = 0x3E
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x3E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_InitNic(Command):
    CommandGroupId = 0xE0
    CommandId = 0x3F
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x3F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_BohEnable(Command):
    CommandGroupId = 0xE0
    CommandId = 0x41
    def build_frame(self, Enable: bool = True, Bug6WorkaroundEnabled: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x41")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Bug6WorkaroundEnabled.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, Bug6WorkaroundEnabled: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, Bug6WorkaroundEnabled=Bug6WorkaroundEnabled, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_NicEnable(Command):
    CommandGroupId = 0xE0
    CommandId = 0x42
    def build_frame(self, Enable: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x42")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_NicGetChipType(Command):
    CommandGroupId = 0xE0
    CommandId = 0x43
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x43")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ChipType_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ChipType = _recv_buffer.read(_ChipType_len)
        if len(_ChipType) != _ChipType_len:
            raise PayloadTooShortError(_ChipType_len - len(_ChipType))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ChipType
class DHWCtrl_NicGetLinkStatus(Command):
    CommandGroupId = 0xE0
    CommandId = 0x44
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x44")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LinkStatus = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LinkStatus
class DHWCtrl_NicSend(Command):
    CommandGroupId = 0xE0
    CommandId = 0x45
    def build_frame(self, SendData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x45")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(SendData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(SendData)
        return _send_buffer.getvalue()
    def __call__(self, SendData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(SendData=SendData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_NicReceive(Command):
    CommandGroupId = 0xE0
    CommandId = 0x46
    def build_frame(self, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x46")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Timeout: int, BrpTimeout: int = 1000) -> bytes:
        request_frame = self.build_frame(Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RecvData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _RecvData = _recv_buffer.read(_RecvData_len)
        if len(_RecvData) != _RecvData_len:
            raise PayloadTooShortError(_RecvData_len - len(_RecvData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RecvData
class DHWCtrl_NicSetMAC(Command):
    CommandGroupId = 0xE0
    CommandId = 0x47
    def build_frame(self, MAC: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x47")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(MAC) != 6:
            raise ValueError(MAC)
        _send_buffer.write(MAC)
        return _send_buffer.getvalue()
    def __call__(self, MAC: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(MAC=MAC, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_ApspiSetSpeed(Command):
    CommandGroupId = 0xE0
    CommandId = 0x50
    def build_frame(self, Speed: int = 3390, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x50")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Speed.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Speed: int = 3390, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Speed=Speed, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_ApspiEnable(Command):
    CommandGroupId = 0xE0
    CommandId = 0x51
    def build_frame(self, Enable: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x51")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_ApspiSingleSend(Command):
    CommandGroupId = 0xE0
    CommandId = 0x52
    def build_frame(self, CmdCode: int, Address: int, CmdData: int, Delay: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x52")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(CmdData.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Delay.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCode: int, Address: int, CmdData: int, Delay: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CmdCode=CmdCode, Address=Address, CmdData=CmdData, Delay=Delay, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_ApspiSingleRecv(Command):
    CommandGroupId = 0xE0
    CommandId = 0x53
    def build_frame(self, CmdCode: int, Address: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x53")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCode: int, Address: int, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(CmdCode=CmdCode, Address=Address, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _CmdData = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _CmdData
class DHWCtrl_ApspiAlternateSend(Command):
    CommandGroupId = 0xE0
    CommandId = 0x54
    def build_frame(self, CmdCodeA: int, CmdCodeB: int, Address: int, CmdData: bytes, Delay: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x54")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCodeA.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CmdCodeB.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(int(len(CmdData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(CmdData)
        _send_buffer.write(Delay.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCodeA: int, CmdCodeB: int, Address: int, CmdData: bytes, Delay: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(CmdCodeA=CmdCodeA, CmdCodeB=CmdCodeB, Address=Address, CmdData=CmdData, Delay=Delay, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_ApspiAlternateRecv(Command):
    CommandGroupId = 0xE0
    CommandId = 0x55
    def build_frame(self, CmdCodeA: int, CmdCodeB: int, Address: int, CmdDataLen: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x55")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CmdCodeA.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(CmdCodeB.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Address.to_bytes(length=2, byteorder='big'))
        _send_buffer.write(CmdDataLen.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, CmdCodeA: int, CmdCodeB: int, Address: int, CmdDataLen: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(CmdCodeA=CmdCodeA, CmdCodeB=CmdCodeB, Address=Address, CmdDataLen=CmdDataLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _CmdData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _CmdData = _recv_buffer.read(_CmdData_len)
        if len(_CmdData) != _CmdData_len:
            raise PayloadTooShortError(_CmdData_len - len(_CmdData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _CmdData
class DHWCtrl_PdiEnable(Command):
    CommandGroupId = 0xE0
    CommandId = 0x56
    def build_frame(self, Enable: bool = True, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x56")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Enable.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Enable: bool = True, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Enable=Enable, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PdiEraseDevice(Command):
    CommandGroupId = 0xE0
    CommandId = 0x57
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x57")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PdiReadFlash(Command):
    CommandGroupId = 0xE0
    CommandId = 0x58
    def build_frame(self, Adr: int, ReadLen: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x58")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(ReadLen.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, ReadLen: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, ReadLen=ReadLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _ReadData = _recv_buffer.read(_ReadData_len)
        if len(_ReadData) != _ReadData_len:
            raise PayloadTooShortError(_ReadData_len - len(_ReadData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadData
class DHWCtrl_PdiEraseFlashPage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x59
    def build_frame(self, Adr: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x59")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PdiWriteFlashPage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x5A
    def build_frame(self, Adr: int, WriteData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x5A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(int(len(WriteData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(WriteData)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, WriteData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, WriteData=WriteData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PdiProgramFlashPage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x5B
    def build_frame(self, Adr: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x5B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PdiReadEeprom(Command):
    CommandGroupId = 0xE0
    CommandId = 0x5C
    def build_frame(self, Adr: int, ReadLen: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x5C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(ReadLen.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, ReadLen: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, ReadLen=ReadLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _ReadData = _recv_buffer.read(_ReadData_len)
        if len(_ReadData) != _ReadData_len:
            raise PayloadTooShortError(_ReadData_len - len(_ReadData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadData
class DHWCtrl_PdiProgramEepromPage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x5D
    def build_frame(self, Adr: int, WriteData: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x5D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(int(len(WriteData)).to_bytes(2, byteorder='big'))
        _send_buffer.write(WriteData)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, WriteData: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, WriteData=WriteData, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_PdiReadFuses(Command):
    CommandGroupId = 0xE0
    CommandId = 0x5E
    def build_frame(self, Adr: int, ReadLen: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x5E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(ReadLen.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, ReadLen: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, ReadLen=ReadLen, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReadData_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _ReadData = _recv_buffer.read(_ReadData_len)
        if len(_ReadData) != _ReadData_len:
            raise PayloadTooShortError(_ReadData_len - len(_ReadData))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ReadData
class DHWCtrl_PdiWriteFuse(Command):
    CommandGroupId = 0xE0
    CommandId = 0x5F
    def build_frame(self, Adr: int, Fuse: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x5F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(Fuse.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int, Fuse: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, Fuse=Fuse, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_FlashGetPageSize(Command):
    CommandGroupId = 0xE0
    CommandId = 0x60
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x60")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _PageSize = safe_read_int_from_buffer(_recv_buffer, 2)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _PageSize
class DHWCtrl_FlashErasePage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x61
    def build_frame(self, StartAdr: int = 0, *, Len: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x61")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, StartAdr: int = 0, *, Len: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(StartAdr=StartAdr, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_FlashRead(Command):
    CommandGroupId = 0xE0
    CommandId = 0x62
    def build_frame(self, StartAdr: int = 0, Len: int = 5, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x62")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(Len.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, StartAdr: int = 0, Len: int = 5, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(StartAdr=StartAdr, Len=Len, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Data = _recv_buffer.read(_Data_len)
        if len(_Data) != _Data_len:
            raise PayloadTooShortError(_Data_len - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class DHWCtrl_FlashWritePage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x63
    def build_frame(self, StartAdr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x63")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(int(len(Data)).to_bytes(2, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, StartAdr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(StartAdr=StartAdr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_FlashProgramPage(Command):
    CommandGroupId = 0xE0
    CommandId = 0x64
    def build_frame(self, StartAdr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x64")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(StartAdr.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, StartAdr: int = 0, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(StartAdr=StartAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_RegisterRead(Command):
    CommandGroupId = 0xE0
    CommandId = 0x65
    def build_frame(self, RegAdr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x65")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(RegAdr.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, RegAdr: int = 0, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(RegAdr=RegAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _RegValue = safe_read_int_from_buffer(_recv_buffer, 4)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _RegValue
class DHWCtrl_RegisterWrite(Command):
    CommandGroupId = 0xE0
    CommandId = 0x66
    def build_frame(self, RegAdr: int = 0, RegValue: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x66")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(RegAdr.to_bytes(length=4, byteorder='big'))
        _send_buffer.write(RegValue.to_bytes(length=4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, RegAdr: int = 0, RegValue: int = 0, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(RegAdr=RegAdr, RegValue=RegValue, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_AesWrapKey(Command):
    CommandGroupId = 0xE0
    CommandId = 0x68
    def build_frame(self, WrappedKeyNr: DHWCtrl_AesWrapKey_WrappedKeyNr, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x68")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DHWCtrl_AesWrapKey_WrappedKeyNr_Parser.as_value(WrappedKeyNr).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Key)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, WrappedKeyNr: DHWCtrl_AesWrapKey_WrappedKeyNr, Key: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(WrappedKeyNr=WrappedKeyNr, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _WrappedKey_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _WrappedKey = _recv_buffer.read(_WrappedKey_len)
        if len(_WrappedKey) != _WrappedKey_len:
            raise PayloadTooShortError(_WrappedKey_len - len(_WrappedKey))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _WrappedKey
class DHWCtrl_AesEncrypt(Command):
    CommandGroupId = 0xE0
    CommandId = 0x69
    def build_frame(self, WrappedKeyNr: DHWCtrl_AesEncrypt_WrappedKeyNr, Block: bytes, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x69")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DHWCtrl_AesEncrypt_WrappedKeyNr_Parser.as_value(WrappedKeyNr).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(Block)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Block)
        _send_buffer.write(int(len(Key)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, WrappedKeyNr: DHWCtrl_AesEncrypt_WrappedKeyNr, Block: bytes, Key: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(WrappedKeyNr=WrappedKeyNr, Block=Block, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EncBlock_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _EncBlock = _recv_buffer.read(_EncBlock_len)
        if len(_EncBlock) != _EncBlock_len:
            raise PayloadTooShortError(_EncBlock_len - len(_EncBlock))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _EncBlock
class DHWCtrl_AesDecrypt(Command):
    CommandGroupId = 0xE0
    CommandId = 0x6A
    def build_frame(self, WrappedKeyNr: DHWCtrl_AesDecrypt_WrappedKeyNr, EncBlock: bytes, Key: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x6A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(DHWCtrl_AesDecrypt_WrappedKeyNr_Parser.as_value(WrappedKeyNr).to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(EncBlock)).to_bytes(1, byteorder='big'))
        _send_buffer.write(EncBlock)
        _send_buffer.write(int(len(Key)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Key)
        return _send_buffer.getvalue()
    def __call__(self, WrappedKeyNr: DHWCtrl_AesDecrypt_WrappedKeyNr, EncBlock: bytes, Key: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(WrappedKeyNr=WrappedKeyNr, EncBlock=EncBlock, Key=Key, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Block_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Block = _recv_buffer.read(_Block_len)
        if len(_Block) != _Block_len:
            raise PayloadTooShortError(_Block_len - len(_Block))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Block
class DHWCtrl_GetPlatformId2(Command):
    CommandGroupId = 0xE0
    CommandId = 0x7B
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x7B")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> List[int]:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _HWCIdLst_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _HWCIdLst = []  # type: ignore[var-annotated,unused-ignore]
        while not len(_HWCIdLst) >= _HWCIdLst_len:
            _HWCId = safe_read_int_from_buffer(_recv_buffer, 2)
            _HWCIdLst.append(_HWCId)
        if len(_HWCIdLst) != _HWCIdLst_len:
            raise PayloadTooShortError(_HWCIdLst_len - len(_HWCIdLst))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _HWCIdLst
class DHWCtrl_GetProdLoader(Command):
    CommandGroupId = 0xE0
    CommandId = 0x7C
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x7C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> int:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _LoaderBaudrate = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _LoaderBaudrate
class DHWCtrl_StartProdLoader(Command):
    CommandGroupId = 0xE0
    CommandId = 0x7D
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x7D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_Run(Command):
    CommandGroupId = 0xE0
    CommandId = 0x7F
    def build_frame(self, CommandList: bytes, BrpTimeout: int = 20000) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x7F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(CommandList)
        return _send_buffer.getvalue()
    def __call__(self, CommandList: bytes, BrpTimeout: int = 20000) -> DHWCtrl_Run_Result:
        request_frame = self.build_frame(CommandList=CommandList, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = safe_read_int_from_buffer(_recv_buffer, 1)
        _Response_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Response = _recv_buffer.read(_Response_len)
        if len(_Response) != _Response_len:
            raise PayloadTooShortError(_Response_len - len(_Response))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return DHWCtrl_Run_Result(_Status, _Response)
class DHWCtrl_GetStartupRun(Command):
    CommandGroupId = 0xE0
    CommandId = 0x7E
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x7E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> DHWCtrl_GetStartupRun_Result:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Status = safe_read_int_from_buffer(_recv_buffer, 1)
        _Response_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Response = _recv_buffer.read(_Response_len)
        if len(_Response) != _Response_len:
            raise PayloadTooShortError(_Response_len - len(_Response))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return DHWCtrl_GetStartupRun_Result(_Status, _Response)
class DHWCtrl_InitBgm(Command):
    CommandGroupId = 0xE0
    CommandId = 0x80
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x80")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_BgmExec(Command):
    CommandGroupId = 0xE0
    CommandId = 0x81
    def build_frame(self, Cmd: bytes, Timeout: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x81")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(int(len(Cmd)).to_bytes(1, byteorder='big'))
        _send_buffer.write(Cmd)
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Cmd: bytes, Timeout: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Cmd=Cmd, Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Rsp_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _Rsp = _recv_buffer.read(_Rsp_len)
        if len(_Rsp) != _Rsp_len:
            raise PayloadTooShortError(_Rsp_len - len(_Rsp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Rsp
class DHWCtrl_Sm4x00BootloaderStart(Command):
    CommandGroupId = 0xE0
    CommandId = 0x82
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x82")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BootloaderString_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _BootloaderString = _recv_buffer.read(_BootloaderString_len)
        if len(_BootloaderString) != _BootloaderString_len:
            raise PayloadTooShortError(_BootloaderString_len - len(_BootloaderString))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _BootloaderString
class DHWCtrl_Sm4x00EraseFlash(Command):
    CommandGroupId = 0xE0
    CommandId = 0x83
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x83")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class DHWCtrl_Sm4x00WaitForFlashErase(Command):
    CommandGroupId = 0xE0
    CommandId = 0x84
    def build_frame(self, Timeout: int, BrpTimeout: int = 1500) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x84")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Timeout: int, BrpTimeout: int = 1500) -> bytes:
        request_frame = self.build_frame(Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _EraseResponse_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _EraseResponse = _recv_buffer.read(_EraseResponse_len)
        if len(_EraseResponse) != _EraseResponse_len:
            raise PayloadTooShortError(_EraseResponse_len - len(_EraseResponse))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _EraseResponse
class DHWCtrl_Sm4x00ProgramBlock(Command):
    CommandGroupId = 0xE0
    CommandId = 0x85
    def build_frame(self, IsLast: bool, FwBlock: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x85")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(IsLast.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(int(len(FwBlock)).to_bytes(1, byteorder='big'))
        _send_buffer.write(FwBlock)
        return _send_buffer.getvalue()
    def __call__(self, IsLast: bool, FwBlock: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(IsLast=IsLast, FwBlock=FwBlock, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ProgramResponse_len = safe_read_int_from_buffer(_recv_buffer, 1)
        _ProgramResponse = _recv_buffer.read(_ProgramResponse_len)
        if len(_ProgramResponse) != _ProgramResponse_len:
            raise PayloadTooShortError(_ProgramResponse_len - len(_ProgramResponse))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ProgramResponse
class DHWCtrl_BgmRead(Command):
    CommandGroupId = 0xE0
    CommandId = 0x86
    def build_frame(self, Timeout: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xE0\x86")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Timeout.to_bytes(length=2, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Timeout: int, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Timeout=Timeout, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Rsp_len = safe_read_int_from_buffer(_recv_buffer, 2)
        _Rsp = _recv_buffer.read(_Rsp_len)
        if len(_Rsp) != _Rsp_len:
            raise PayloadTooShortError(_Rsp_len - len(_Rsp))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Rsp
class LT_Request(Command):
    CommandGroupId = 0xA0
    CommandId = 0x41
    def build_frame(self, ReqAll: bool = False, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x41")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (int(ReqAll) & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, ReqAll: bool = False, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(ReqAll=ReqAll, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ATQA = _recv_buffer.read(2)
        if len(_ATQA) != 2:
            raise PayloadTooShortError(2 - len(_ATQA))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _ATQA
class LT_Anticoll(Command):
    CommandGroupId = 0xA0
    CommandId = 0x42
    def build_frame(self, BitCount: int = 0, *, PreSelectedSnr: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x42")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BitCount.to_bytes(length=1, byteorder='big'))
        if len(PreSelectedSnr) != 4:
            raise ValueError(PreSelectedSnr)
        _send_buffer.write(PreSelectedSnr)
        return _send_buffer.getvalue()
    def __call__(self, BitCount: int = 0, *, PreSelectedSnr: bytes, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(BitCount=BitCount, PreSelectedSnr=PreSelectedSnr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _SelectedSnr = _recv_buffer.read(4)
        if len(_SelectedSnr) != 4:
            raise PayloadTooShortError(4 - len(_SelectedSnr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _SelectedSnr
class LT_Select(Command):
    CommandGroupId = 0xA0
    CommandId = 0x43
    def build_frame(self, Snr: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x43")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        if len(Snr) != 4:
            raise ValueError(Snr)
        _send_buffer.write(Snr)
        return _send_buffer.getvalue()
    def __call__(self, Snr: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Snr=Snr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_Halt(Command):
    CommandGroupId = 0xA0
    CommandId = 0x45
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x45")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_ReadBlock(Command):
    CommandGroupId = 0xA0
    CommandId = 0x70
    def build_frame(self, Adr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x70")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(32)
        if len(_Data) != 32:
            raise PayloadTooShortError(32 - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class LT_ReadMultipleBlocks(Command):
    CommandGroupId = 0xA0
    CommandId = 0x76
    def build_frame(self, Adr: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x76")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(NumBlocks.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, NumBlocks=NumBlocks, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class LT_WriteBlock(Command):
    CommandGroupId = 0xA0
    CommandId = 0x71
    def build_frame(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x71")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        if len(Data) != 32:
            raise ValueError(Data)
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_ReadWord(Command):
    CommandGroupId = 0xA0
    CommandId = 0x72
    def build_frame(self, BlockAdr: int = 0, WordAdr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x72")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(WordAdr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockAdr: int = 0, WordAdr: int = 0, BrpTimeout: int = 100) -> LT_ReadWord_Result:
        request_frame = self.build_frame(BlockAdr=BlockAdr, WordAdr=WordAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _DataLo = safe_read_int_from_buffer(_recv_buffer, 1)
        _DataHi = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return LT_ReadWord_Result(_DataLo, _DataHi)
class LT_WriteWord(Command):
    CommandGroupId = 0xA0
    CommandId = 0x73
    def build_frame(self, BlockAdr: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x73")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(WordAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataHi.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockAdr: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BlockAdr=BlockAdr, WordAdr=WordAdr, DataLo=DataLo, DataHi=DataHi, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_WriteFile(Command):
    CommandGroupId = 0xA0
    CommandId = 0x74
    def build_frame(self, FileNr: int = 0, Mode: int = 0, *, BlockAdr: int, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x74")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(FileNr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockAdr.to_bytes(length=1, byteorder='big'))
        if len(Data) != 32:
            raise ValueError(Data)
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, FileNr: int = 0, Mode: int = 0, *, BlockAdr: int, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(FileNr=FileNr, Mode=Mode, BlockAdr=BlockAdr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_Test(Command):
    CommandGroupId = 0xA0
    CommandId = 0x75
    def build_frame(self, Mode: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x75")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: int = 0, BrpTimeout: int = 100) -> LT_Test_Result:
        request_frame = self.build_frame(Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Teststatus = safe_read_int_from_buffer(_recv_buffer, 1)
        _Snr = _recv_buffer.read(4)
        if len(_Snr) != 4:
            raise PayloadTooShortError(4 - len(_Snr))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return LT_Test_Result(_Teststatus, _Snr)
class LT_FastWriteBlock(Command):
    CommandGroupId = 0xA0
    CommandId = 0x7C
    def build_frame(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x7C")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        if len(Data) != 32:
            raise ValueError(Data)
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_FastWriteWord(Command):
    CommandGroupId = 0xA0
    CommandId = 0x7D
    def build_frame(self, BlockAdr: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x7D")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(WordAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataHi.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockAdr: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BlockAdr=BlockAdr, WordAdr=WordAdr, DataLo=DataLo, DataHi=DataHi, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_HighSpeedWriteBlock(Command):
    CommandGroupId = 0xA0
    CommandId = 0x60
    def build_frame(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x60")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        if len(Data) != 32:
            raise ValueError(Data)
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Adr=Adr, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_GetBootStatus(Command):
    CommandGroupId = 0xA0
    CommandId = 0x34
    def build_frame(self, Mode: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x34")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: int = 0, BrpTimeout: int = 100) -> LT_GetBootStatus_Result:
        request_frame = self.build_frame(Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _BootStatusLo = safe_read_int_from_buffer(_recv_buffer, 1)
        _BootStatusHi = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return LT_GetBootStatus_Result(_BootStatusLo, _BootStatusHi)
class LT_ContinousReadBlocks(Command):
    CommandGroupId = 0xA0
    CommandId = 0x61
    def build_frame(self, Adr: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x61")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Adr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(NumBlocks.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Adr: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(Adr=Adr, NumBlocks=NumBlocks, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class LT_SetReturnLink(Command):
    CommandGroupId = 0xA0
    CommandId = 0x7F
    def build_frame(self, Mode: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x7F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Mode.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Mode: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Mode=Mode, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_HFReset(Command):
    CommandGroupId = 0xA0
    CommandId = 0x4E
    def build_frame(self, OffDurationLo: int = 1, OffDurationHi: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x4E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(OffDurationLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(OffDurationHi.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, OffDurationLo: int = 1, OffDurationHi: int = 1, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(OffDurationLo=OffDurationLo, OffDurationHi=OffDurationHi, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_Reset(Command):
    CommandGroupId = 0xA0
    CommandId = 0x36
    def build_frame(self, Quit: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x36")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(Quit.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, Quit: int = 0, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(Quit=Quit, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_GetInfo(Command):
    CommandGroupId = 0xA0
    CommandId = 0x4F
    def build_frame(self, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x4F")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BrpTimeout: int = 100) -> str:
        request_frame = self.build_frame(BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Info_bytes = b''
        _Info_next_byte = _recv_buffer.read(1)
        while _Info_next_byte and _Info_next_byte != b'\x00':
            _Info_bytes += _Info_next_byte
            _Info_next_byte = _recv_buffer.read(1)
        if not _Info_next_byte:
            raise InvalidPayloadError('missing zero-terminator in field Info')
        _Info = _Info_bytes.decode('ascii')
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Info
class LT_TransparentCmd(Command):
    CommandGroupId = 0xA0
    CommandId = 0x7E
    def build_frame(self, EnBitMode: int = 0, EnCRCRX: int = 1, EnCRCTX: int = 1, ParityMode: int = 1, EnParity: int = 1, *, LenLo: int, LenHi: int, TimeoutLo: int = 26, TimeoutHi: int = 26, DSI: int = 0, DRI: int = 0, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x7E")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _var_0000_int = 0
        _var_0000_int |= (EnBitMode & 0b1) << 4
        _var_0000_int |= (EnCRCRX & 0b1) << 3
        _var_0000_int |= (EnCRCTX & 0b1) << 2
        _var_0000_int |= (ParityMode & 0b1) << 1
        _var_0000_int |= (EnParity & 0b1) << 0
        _send_buffer.write(_var_0000_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(LenLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(LenHi.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(TimeoutLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(TimeoutHi.to_bytes(length=1, byteorder='big'))
        _var_0001_int = 0
        _var_0001_int |= (DSI & 0b11) << 2
        _var_0001_int |= (DRI & 0b11) << 0
        _send_buffer.write(_var_0001_int.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, EnBitMode: int = 0, EnCRCRX: int = 1, EnCRCTX: int = 1, ParityMode: int = 1, EnParity: int = 1, *, LenLo: int, LenHi: int, TimeoutLo: int = 26, TimeoutHi: int = 26, DSI: int = 0, DRI: int = 0, Data: bytes, BrpTimeout: int = 100) -> LT_TransparentCmd_Result:
        request_frame = self.build_frame(EnBitMode=EnBitMode, EnCRCRX=EnCRCRX, EnCRCTX=EnCRCTX, ParityMode=ParityMode, EnParity=EnParity, LenLo=LenLo, LenHi=LenHi, TimeoutLo=TimeoutLo, TimeoutHi=TimeoutHi, DSI=DSI, DRI=DRI, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _ReturnLenLo = safe_read_int_from_buffer(_recv_buffer, 1)
        _ReturnLenHi = safe_read_int_from_buffer(_recv_buffer, 1)
        _ColPos = safe_read_int_from_buffer(_recv_buffer, 2)
        _ReturnData = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return LT_TransparentCmd_Result(_ReturnLenLo, _ReturnLenHi, _ColPos, _ReturnData)
class LT_ReadBlockExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x80
    def build_frame(self, AdrLo: int = 0, AdrHi: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x80")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AdrHi.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AdrLo: int = 0, AdrHi: int = 0, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(AdrLo=AdrLo, AdrHi=AdrHi, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(32)
        if len(_Data) != 32:
            raise PayloadTooShortError(32 - len(_Data))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class LT_WriteBlockExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x81
    def build_frame(self, AdrLo: int = 0, AdrHi: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x81")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AdrHi.to_bytes(length=1, byteorder='big'))
        if len(Data) != 32:
            raise ValueError(Data)
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, AdrLo: int = 0, AdrHi: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AdrLo=AdrLo, AdrHi=AdrHi, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_ReadWordExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x82
    def build_frame(self, AdrLo: int = 0, AdrHi: int = 0, WordAdr: int = 0, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x82")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AdrHi.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(WordAdr.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AdrLo: int = 0, AdrHi: int = 0, WordAdr: int = 0, BrpTimeout: int = 100) -> LT_ReadWordExtended_Result:
        request_frame = self.build_frame(AdrLo=AdrLo, AdrHi=AdrHi, WordAdr=WordAdr, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _DataLo = safe_read_int_from_buffer(_recv_buffer, 1)
        _DataHi = safe_read_int_from_buffer(_recv_buffer, 1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return LT_ReadWordExtended_Result(_DataLo, _DataHi)
class LT_WriteWordExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x83
    def build_frame(self, BlockAdrLo: int = 0, BlockAdrHi: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x83")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockAdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockAdrHi.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(WordAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataHi.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockAdrLo: int = 0, BlockAdrHi: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BlockAdrLo=BlockAdrLo, BlockAdrHi=BlockAdrHi, WordAdr=WordAdr, DataLo=DataLo, DataHi=DataHi, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_ReadMultipleBlocksExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x84
    def build_frame(self, AdrLo: int = 0, AdrHi: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x84")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AdrHi.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(NumBlocks.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AdrLo: int = 0, AdrHi: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(AdrLo=AdrLo, AdrHi=AdrHi, NumBlocks=NumBlocks, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class LT_FastWriteWordExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x88
    def build_frame(self, BlockAdrLo: int = 0, BlockAdrHi: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x88")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(BlockAdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(BlockAdrHi.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(WordAdr.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(DataHi.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, BlockAdrLo: int = 0, BlockAdrHi: int = 0, WordAdr: int = 0, *, DataLo: int, DataHi: int, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(BlockAdrLo=BlockAdrLo, BlockAdrHi=BlockAdrHi, WordAdr=WordAdr, DataLo=DataLo, DataHi=DataHi, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None
class LT_ContinousReadBlocksExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x89
    def build_frame(self, AdrLo: int = 0, AdrHi: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x89")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AdrHi.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(NumBlocks.to_bytes(length=1, byteorder='big'))
        return _send_buffer.getvalue()
    def __call__(self, AdrLo: int = 0, AdrHi: int = 0, NumBlocks: int = 1, BrpTimeout: int = 100) -> bytes:
        request_frame = self.build_frame(AdrLo=AdrLo, AdrHi=AdrHi, NumBlocks=NumBlocks, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _Data = _recv_buffer.read(-1)
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return _Data
class LT_HighSpeedWriteBlockExtended(Command):
    CommandGroupId = 0xA0
    CommandId = 0x8A
    def build_frame(self, AdrLo: int = 0, AdrHi: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> bytes:
        _send_buffer = BytesIO()
        _send_buffer.write(b"\x00\xA0\x8A")
        _send_buffer.write(int(BrpTimeout).to_bytes(4, byteorder='big'))
        _send_buffer.write(AdrLo.to_bytes(length=1, byteorder='big'))
        _send_buffer.write(AdrHi.to_bytes(length=1, byteorder='big'))
        if len(Data) != 32:
            raise ValueError(Data)
        _send_buffer.write(Data)
        return _send_buffer.getvalue()
    def __call__(self, AdrLo: int = 0, AdrHi: int = 0, *, Data: bytes, BrpTimeout: int = 100) -> None:
        request_frame = self.build_frame(AdrLo=AdrLo, AdrHi=AdrHi, Data=Data, BrpTimeout=BrpTimeout)
        _recv_buffer = BytesIO(self.execute(request_frame))
        _additional_data = _recv_buffer.read()
        if _additional_data:
            raise PayloadTooLongError(_additional_data)
        return None