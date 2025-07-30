
import abc
from io import BytesIO
from typing import Optional, NamedTuple, Union, Literal, TypedDict, Dict, List, ClassVar, Type as _Type

from typing_extensions import Self, NotRequired

from .common import safe_read_int_from_buffer, LiteralParser, FrameExecutor, BaltechApiError, PayloadTooLongError, PayloadTooShortError, InvalidPayloadError
class ASKError(BaltechApiError):
    ErrorCode = 0x00013600
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html"
class ASK_ErrAskNoTag(ASKError):
    """
    No Tag.
    """
    ErrorCode = 0x00013601
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskNoTag"
class ASK_ErrAskRxdata(ASKError):
    """
    Wrong length or wrong data.
    """
    ErrorCode = 0x00013603
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskRxdata"
class ASK_ErrAskParity(ASKError):
    """
    Parity error.
    """
    ErrorCode = 0x00013605
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskParity"
class ASK_ErrAskParam(ASKError):
    """
    Wrong command param (on HF).
    """
    ErrorCode = 0x00013607
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskParam"
class ASK_ErrAskHfreqctrl(ASKError):
    """
    Another task requested control over HF via hf_request_control.
    """
    ErrorCode = 0x00013608
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskHfreqctrl"
class ASK_ErrAskHw(ASKError):
    """
    Missing Platform ID or Readerchip error.
    """
    ErrorCode = 0x00013609
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskHw"
class ASK_ErrAskHwNotSupported(ASKError):
    """
    Hardware not supported.
    """
    ErrorCode = 0x0001360B
    URL = "https://docs.baltech.de/refman/cmds/ask/index.html#ASK.ErrAskHwNotSupported"
class ARError(BaltechApiError):
    ErrorCode = 0x00010500
    URL = "https://docs.baltech.de/refman/cmds/ar/index.html"
class AR_ErrNoMessage(ARError):
    """
    No valid card has been presented to the reader so far.
    """
    ErrorCode = 0x00010501
    URL = "https://docs.baltech.de/refman/cmds/ar/index.html#AR.ErrNoMessage"
class AR_ErrScriptRuntime(ARError):
    """
    A runtime error occurred when executing the script.
    """
    ErrorCode = 0x00010502
    URL = "https://docs.baltech.de/refman/cmds/ar/index.html#AR.ErrScriptRuntime"
class AR_ErrScriptSyntax(ARError):
    """
    There's a syntax error in the script code.
    """
    ErrorCode = 0x00010503
    URL = "https://docs.baltech.de/refman/cmds/ar/index.html#AR.ErrScriptSyntax"
class AR_ErrScriptNotImplemented(ARError):
    """
    The script ran the command
    [DefaultAction](../cfg/baltechscript.xml#BaltechScript.DefaultAction).
    """
    ErrorCode = 0x00010504
    URL = "https://docs.baltech.de/refman/cmds/ar/index.html#AR.ErrScriptNotImplemented"
class AR_ErrArDisabled(ARError):
    """
    Autoread is disabled.
    """
    ErrorCode = 0x00010510
    URL = "https://docs.baltech.de/refman/cmds/ar/index.html#AR.ErrArDisabled"
class BatError(BaltechApiError):
    ErrorCode = 0x00014600
    URL = "https://docs.baltech.de/refman/cmds/bat/index.html"
class Bat_ErrSkipped(BatError):
    """
    This command was skipped, since condition bits did not match.
    """
    ErrorCode = 0x00014690
    URL = "https://docs.baltech.de/refman/cmds/bat/index.html#Bat.ErrSkipped"
class BlePeriphError(BaltechApiError):
    ErrorCode = 0x00014B00
    URL = "https://docs.baltech.de/refman/cmds/bleperiph/index.html"
class BlePeriph_ErrNotEnabled(BlePeriphError):
    """
    The command could not be executed because BLE is currently not
    [enabled](.#BlePeriph.Enable).
    """
    ErrorCode = 0x00014B01
    URL = "https://docs.baltech.de/refman/cmds/bleperiph/index.html#BlePeriph.ErrNotEnabled"
class BlePeriph_ErrNotConnected(BlePeriphError):
    """
    The reader is currently not connected with a BLE central.
    """
    ErrorCode = 0x00014B02
    URL = "https://docs.baltech.de/refman/cmds/bleperiph/index.html#BlePeriph.ErrNotConnected"
class BlePeriph_ErrInvalidCharacteristicNdx(BlePeriphError):
    """
    The given characteristic index is invalid.
    """
    ErrorCode = 0x00014B03
    URL = "https://docs.baltech.de/refman/cmds/bleperiph/index.html#BlePeriph.ErrInvalidCharacteristicNdx"
class BlePeriph_ErrWriteCharacteristic(BlePeriphError):
    """
    The characteristic value could not be written because the given offset or
    length exceeds the characteristic size.
    """
    ErrorCode = 0x00014B04
    URL = "https://docs.baltech.de/refman/cmds/bleperiph/index.html#BlePeriph.ErrWriteCharacteristic"
class CardEmuError(BaltechApiError):
    ErrorCode = 0x00014700
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html"
class CardEmu_CardemuErrNoTag(CardEmuError):
    """
    No tag error.
    """
    ErrorCode = 0x00014701
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrNoTag"
class CardEmu_CardemuErrCollision(CardEmuError):
    """
    Collision occurred (status value will be stored with bit position of collision
    in high nibble).
    """
    ErrorCode = 0x00014702
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrCollision"
class CardEmu_CardemuErrHf(CardEmuError):
    """
    General HF error.
    """
    ErrorCode = 0x00014704
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrHf"
class CardEmu_CardemuErrFrame(CardEmuError):
    """
    Bit error, parity error or frame error (start /stop bit).
    """
    ErrorCode = 0x00014707
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrFrame"
class CardEmu_CardemuErrCrc(CardEmuError):
    """
    CRC checksum error.
    """
    ErrorCode = 0x00014708
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrCrc"
class CardEmu_CardemuErrCom(CardEmuError):
    """
    Communication error uC - reader chip.
    """
    ErrorCode = 0x00014710
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrCom"
class CardEmu_CardemuErrBuflen(CardEmuError):
    """
    Remaining data in FIFO / FIFO overflow.
    """
    ErrorCode = 0x00014711
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrBuflen"
class CardEmu_CardemuErrTimeout(CardEmuError):
    """
    Timeout occurred while waiting for card / APDU command.
    """
    ErrorCode = 0x0001473F
    URL = "https://docs.baltech.de/refman/cmds/cardemu/index.html#CardEmu.CardemuErrTimeout"
class CryptoError(BaltechApiError):
    ErrorCode = 0x00010200
    URL = "https://docs.baltech.de/refman/cmds/crypto/index.html"
class Crypto_CrptErrInvalidBlock(CryptoError):
    """
    Encrypted block format is invalid.
    """
    ErrorCode = 0x00010201
    URL = "https://docs.baltech.de/refman/cmds/crypto/index.html#Crypto.CrptErrInvalidBlock"
class Crypto_CrptErrAuth(CryptoError):
    """
    Internal key cannot be accessed for the specified action due to the access
    condition flags settings.
    """
    ErrorCode = 0x00010202
    URL = "https://docs.baltech.de/refman/cmds/crypto/index.html#Crypto.CrptErrAuth"
class Crypto_CrptErrKeyNotFound(CryptoError):
    """
    Specified key not available in the internal key list.
    """
    ErrorCode = 0x00010203
    URL = "https://docs.baltech.de/refman/cmds/crypto/index.html#Crypto.CrptErrKeyNotFound"
class Crypto_CrptErrWriteConfigkey(CryptoError):
    """
    Configuration key cannot be stored in the reader's configuration.
    """
    ErrorCode = 0x00010204
    URL = "https://docs.baltech.de/refman/cmds/crypto/index.html#Crypto.CrptErrWriteConfigkey"
class Crypto_CrptErrInvalidKey(CryptoError):
    """
    No valid configuration card key. Since no key is present, the reader is forced
    to work unencrypted.
    
    **This status code is not supported by Crypto.Encrypt/Crypto.Decrypt commands
    due to legacy reasons.**
    """
    ErrorCode = 0x00010205
    URL = "https://docs.baltech.de/refman/cmds/crypto/index.html#Crypto.CrptErrInvalidKey"
class DbgError(BaltechApiError):
    ErrorCode = 0x0001F300
    URL = "https://docs.baltech.de/refman/cmds/dbg/index.html"
class Dbg_DbgErrBusy(DbgError):
    """
    Still processing last command.
    """
    ErrorCode = 0x0001F301
    URL = "https://docs.baltech.de/refman/cmds/dbg/index.html#Dbg.DbgErrBusy"
class DesfireError(BaltechApiError):
    ErrorCode = 0x00011B00
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html"
class Desfire_ErrIso14NoTag(DesfireError):
    """
    There's no card in the HF field, or the card doesn't respond.
    """
    ErrorCode = 0x00011B01
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIso14NoTag"
class Desfire_ErrBreak(DesfireError):
    """
    The command has been aborted because the HF interface has been requested by
    another task or command. Please reselect the card.
    
    **This error only occurs when you combine VHL and low-level commands. We
    highly recommend you avoid that combination as these 2 command sets will
    interfere with each other's card states.**
    """
    ErrorCode = 0x00011B03
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrBreak"
class Desfire_ErrIso14Hf(DesfireError):
    """
    The response frame received from the PICC is invalid, e.g. it may contain an
    invalid number of bits. Please rerun the command.
    """
    ErrorCode = 0x00011B04
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIso14Hf"
class Desfire_ErrIso14CardInvalid(DesfireError):
    """
    The card behaves in an unspecified way or is corrupted. Please rerun the
    command or reselect the card.
    """
    ErrorCode = 0x00011B05
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIso14CardInvalid"
class Desfire_ErrReaderChipCommunication(DesfireError):
    """
    Communication with the reader's HF interface has failed. Please reset the HF
    interface with [Sys.HFReset](system.xml#Sys.HFReset) and check the reader
    status with [Sys.GetBootStatus](system.xml#Sys.GetBootStatus).
    """
    ErrorCode = 0x00011B06
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrReaderChipCommunication"
class Desfire_ErrIso14ApduCmd(DesfireError):
    """
    ISO 14443-4 error: The command or parameters are invalid.
    """
    ErrorCode = 0x00011B07
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIso14ApduCmd"
class Desfire_ErrIso14InvalidResponse(DesfireError):
    """
    ISO 14443-4 error: The card returned an invalid response, e.g. data with an
    invalid length. This may have several reasons, e.g. a wrong card type.
    """
    ErrorCode = 0x00011B08
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIso14InvalidResponse"
class Desfire_ErrPcdAuthentication(DesfireError):
    """
    Authentication with the PICC has failed, e.g. because the encryption algorithm
    or key is wrong.
    """
    ErrorCode = 0x00011B09
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrPcdAuthentication"
class Desfire_ErrIntegrity(DesfireError):
    """
    Secure messaging error: The CRC or MAC checksum doesn't match the transmitted
    data. Authentication has been lost. Please reauthenticate and rerun the
    commands.
    """
    ErrorCode = 0x00011B0A
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIntegrity"
class Desfire_ErrPcdKey(DesfireError):
    """
    The key in the SAM/crypto memory is invalid or missing.
    """
    ErrorCode = 0x00011B0B
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrPcdKey"
class Desfire_ErrNoChanges(DesfireError):
    """
    Card error as per DESFire specification: No changes done to backup files,
    CommitTransaction / AbortTransaction not necessary.
    """
    ErrorCode = 0x00011B0C
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrNoChanges"
class Desfire_ErrPcdParam(DesfireError):
    """
    The BRP command contains an invalid parameter.
    """
    ErrorCode = 0x00011B0D
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrPcdParam"
class Desfire_VcsAndProxCheckError(DesfireError):
    """
    The proximity check has timed out. Please reselect the card.
    """
    ErrorCode = 0x00011B0F
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.VcsAndProxCheckError"
class Desfire_ErrFirmwareNotSupported(DesfireError):
    """
    This command or parameter isn't supported by the reader firmware.
    """
    ErrorCode = 0x00011B10
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrFirmwareNotSupported"
class Desfire_ErrSamCommunication(DesfireError):
    """
    Communication with the SAM has failed. This may have several reasons, e.g. the
    wrong SAM type or a failure to activate the SAM. Please check the SAM status
    and reset the reader with [Sys.Reset](system.xml#Sys.Reset).
    """
    ErrorCode = 0x00011B11
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrSamCommunication"
class Desfire_ErrSamUnlock(DesfireError):
    """
    Unlocking/authenticating with the SAM has failed. Please check the
    [SamAVx](../cfg/base.xml#Project.SamAVx) configuration values.
    """
    ErrorCode = 0x00011B12
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrSamUnlock"
class Desfire_ErrHardwareNotSupported(DesfireError):
    """
    This command isn't supported by the reader hardware.
    
    **This error may refer to any hardware component.**
    """
    ErrorCode = 0x00011B13
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrHardwareNotSupported"
class Desfire_ErrIllegalCmdLegacy(DesfireError):
    """
    Card error as per DESFire specification: Command code not supported by card.
    This status code is identical to ErrIllegalCmd (0x33) und returned be older
    firmware versions.
    """
    ErrorCode = 0x00011B1C
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIllegalCmdLegacy"
class Desfire_ErrLength(DesfireError):
    """
    Card error as per DESFire specification: Length of command string invalid.
    """
    ErrorCode = 0x00011B20
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrLength"
class Desfire_ErrPermissionDenied(DesfireError):
    """
    Card error as per DESFire specification: Current configuration/state does not
    allow the requested command.
    """
    ErrorCode = 0x00011B21
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrPermissionDenied"
class Desfire_ErrParameter(DesfireError):
    """
    Card error as per DESFire specification: Value of the parameter invalid.
    """
    ErrorCode = 0x00011B22
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrParameter"
class Desfire_ErrAppNotFound(DesfireError):
    """
    Card error as per DESFire specification: Requested AID not present on PICC.
    """
    ErrorCode = 0x00011B23
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrAppNotFound"
class Desfire_ErrAppIntegrity(DesfireError):
    """
    Card error as per DESFire specification: Unrecoverable error in application.
    Application will be disabled.
    """
    ErrorCode = 0x00011B24
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrAppIntegrity"
class Desfire_ErrAuthentication(DesfireError):
    """
    Card error as per DESFire specification: Current authentication status does
    not allow execution of requested command.
    """
    ErrorCode = 0x00011B25
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrAuthentication"
class Desfire_ErrBoundary(DesfireError):
    """
    Card error as per DESFire specification: Attempted to read/write beyond the
    limits of the file.
    """
    ErrorCode = 0x00011B27
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrBoundary"
class Desfire_ErrPiccIntegrity(DesfireError):
    """
    Card error as per DESFire specification: Unrecoverable error within PICC, PICC
    will be disabled.
    """
    ErrorCode = 0x00011B28
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrPiccIntegrity"
class Desfire_ErrCommandAborted(DesfireError):
    """
    Card error as per DESFire specification: Previous command was not fully
    completed. Not all frames were requested or provided by the reader.
    """
    ErrorCode = 0x00011B29
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrCommandAborted"
class Desfire_ErrPiccDisabled(DesfireError):
    """
    Card error as per DESFire specification: PICC was disabled by an unrecoverable
    error.
    """
    ErrorCode = 0x00011B2A
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrPiccDisabled"
class Desfire_ErrCount(DesfireError):
    """
    Card error as per DESFire specification: Number of applications limited to 28,
    no additional CreateApplication possible.
    """
    ErrorCode = 0x00011B2B
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrCount"
class Desfire_ErrDuplicate(DesfireError):
    """
    Card error as per DESFire specification: Creation of file/application failed
    because file/application with same number already exists.
    """
    ErrorCode = 0x00011B2C
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrDuplicate"
class Desfire_ErrEeprom(DesfireError):
    """
    Card error as per DESFire specification: Could not complete NV-write operation
    due to loss of power, internal backup/rollback mechanism activated.
    """
    ErrorCode = 0x00011B2D
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrEeprom"
class Desfire_ErrFileNotFound(DesfireError):
    """
    Card error as per DESFire specification: Specified file number does not exist.
    """
    ErrorCode = 0x00011B2E
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrFileNotFound"
class Desfire_ErrFileIntegrity(DesfireError):
    """
    Card error as per DESFire specification: Unrecoverable error within file, file
    will be disabled.
    """
    ErrorCode = 0x00011B2F
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrFileIntegrity"
class Desfire_ErrNoSuchKey(DesfireError):
    """
    Card error as per DESFire specification: Invalid key number specified.
    """
    ErrorCode = 0x00011B30
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrNoSuchKey"
class Desfire_ErrOutOfMemory(DesfireError):
    """
    Card error as per DESFire specification: Insufficient NV-Memory to complete
    command .
    """
    ErrorCode = 0x00011B32
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrOutOfMemory"
class Desfire_ErrIllegalCmd(DesfireError):
    """
    Card error as per DESFire specification: Command code not supported by card.
    """
    ErrorCode = 0x00011B33
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrIllegalCmd"
class Desfire_ErrCmdOverflow(DesfireError):
    """
    Card error as per DESFire specification: Too many commands in the session or
    transaction.
    """
    ErrorCode = 0x00011B34
    URL = "https://docs.baltech.de/refman/cmds/desfire/index.html#Desfire.ErrCmdOverflow"
class DispError(BaltechApiError):
    ErrorCode = 0x00014100
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html"
class Disp_DispPageNotFound(DispError):
    """
    Page was neither found in configuration nor in flash
    """
    ErrorCode = 0x00014101
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispPageNotFound"
class Disp_DispUnexpectedEop(DispError):
    """
    Unexpected end of page
    """
    ErrorCode = 0x00014102
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispUnexpectedEop"
class Disp_DispOutOfMem(DispError):
    """
    Too much defines, too much frames or too much strings used by this page
    """
    ErrorCode = 0x00014103
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispOutOfMem"
class Disp_DispFrameNotFound(DispError):
    """
    The specified frame is not defined
    """
    ErrorCode = 0x00014104
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispFrameNotFound"
class Disp_DispUnknownCommand(DispError):
    """
    The render command is not known
    """
    ErrorCode = 0x00014105
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispUnknownCommand"
class Disp_DispStringTooLong(DispError):
    """
    String is too long
    """
    ErrorCode = 0x00014106
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispStringTooLong"
class Disp_DispInvalidFont(DispError):
    """
    invalid font
    """
    ErrorCode = 0x00014107
    URL = "https://docs.baltech.de/refman/cmds/disp/index.html#Disp.DispInvalidFont"
class EMError(BaltechApiError):
    ErrorCode = 0x00013100
    URL = "https://docs.baltech.de/refman/cmds/em/index.html"
class EM_ErrEmNoTag(EMError):
    """
    No tag error.
    """
    ErrorCode = 0x00013101
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmNoTag"
class EM_ErrEmRxdata(EMError):
    """
    Wrong length or wrong data.
    """
    ErrorCode = 0x00013103
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmRxdata"
class EM_ErrEmChecksum(EMError):
    """
    Receive checksum error.
    """
    ErrorCode = 0x00013104
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmChecksum"
class EM_ErrEmParity(EMError):
    """
    Receive parity error.
    """
    ErrorCode = 0x00013105
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmParity"
class EM_EmCmdError(EMError):
    """
    Error detected during command execution.
    """
    ErrorCode = 0x00013106
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.EmCmdError"
class EM_EmTagtypeNotDetected(EMError):
    """
    Unknown tag type or modulation not detected.
    """
    ErrorCode = 0x00013107
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.EmTagtypeNotDetected"
class EM_ErrEmOvTo(EMError):
    """
    ISR buffer overflow during send/receive, TO during send.
    """
    ErrorCode = 0x00013108
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmOvTo"
class EM_EmParamError(EMError):
    """
    Host command parameter error.
    """
    ErrorCode = 0x00013109
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.EmParamError"
class EM_ErrEmHfreqctrl(EMError):
    """
    Another task requested control over HF via hf_request_control.
    """
    ErrorCode = 0x0001310A
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmHfreqctrl"
class EM_ErrEmHw(EMError):
    """
    Missing Platform ID or Readerchip error.
    """
    ErrorCode = 0x0001310B
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmHw"
class EM_ErrEmHwNotSupported(EMError):
    """
    Hardware not supported.
    """
    ErrorCode = 0x0001310D
    URL = "https://docs.baltech.de/refman/cmds/em/index.html#EM.ErrEmHwNotSupported"
class EthError(BaltechApiError):
    ErrorCode = 0x00014500
    URL = "https://docs.baltech.de/refman/cmds/eth/index.html"
class Eth_ErrNoResultYet(EthError):
    """
    No result yet.
    """
    ErrorCode = 0x00014501
    URL = "https://docs.baltech.de/refman/cmds/eth/index.html#Eth.ErrNoResultYet"
class Eth_ErrNotConnected(EthError):
    """
    Port is not connected.
    """
    ErrorCode = 0x00014502
    URL = "https://docs.baltech.de/refman/cmds/eth/index.html#Eth.ErrNotConnected"
class Eth_ErrDisabled(EthError):
    """
    Detection is disabled.
    """
    ErrorCode = 0x00014503
    URL = "https://docs.baltech.de/refman/cmds/eth/index.html#Eth.ErrDisabled"
class FelicaError(BaltechApiError):
    ErrorCode = 0x00011C00
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html"
class Felica_ErrFelicaNoTag(FelicaError):
    """
    No PICC in HF field.
    """
    ErrorCode = 0x00011C01
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html#Felica.ErrFelicaNoTag"
class Felica_ErrFelicaHf(FelicaError):
    """
    PICC-reader communication error.
    """
    ErrorCode = 0x00011C04
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html#Felica.ErrFelicaHf"
class Felica_ErrFelicaFrame(FelicaError):
    """
    Bit error, parity error or frame error.
    """
    ErrorCode = 0x00011C07
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html#Felica.ErrFelicaFrame"
class Felica_ErrFelicaCom(FelicaError):
    """
    Communication error uC - reader chip.
    """
    ErrorCode = 0x00011C10
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html#Felica.ErrFelicaCom"
class Felica_ErrFelicaCardNotSupported(FelicaError):
    """
    Reader chip does not support cardtype-selected baud rate.
    """
    ErrorCode = 0x00011C22
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html#Felica.ErrFelicaCardNotSupported"
class Felica_ErrFelicaHwNotSupported(FelicaError):
    """
    Command not supported by hardware.
    """
    ErrorCode = 0x00011C23
    URL = "https://docs.baltech.de/refman/cmds/felica/index.html#Felica.ErrFelicaHwNotSupported"
class FlashFSError(BaltechApiError):
    ErrorCode = 0x00014900
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html"
class FlashFS_ErrFsCorrupt(FlashFSError):
    """
    The file system is corrupt: Format required.
    """
    ErrorCode = 0x00014901
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrFsCorrupt"
class FlashFS_ErrRecordCorrupt(FlashFSError):
    """
    The current record is corrupt.
    """
    ErrorCode = 0x00014902
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrRecordCorrupt"
class FlashFS_ErrFlashAccess(FlashFSError):
    """
    Dataflash cannot be accessed: Hardware error.
    """
    ErrorCode = 0x00014903
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrFlashAccess"
class FlashFS_ErrDirectoryFull(FlashFSError):
    """
    The File cannot be created, since there are no more free entries.
    """
    ErrorCode = 0x00014904
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrDirectoryFull"
class FlashFS_ErrFileNotFound(FlashFSError):
    """
    The file is not created yet.
    """
    ErrorCode = 0x00014905
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrFileNotFound"
class FlashFS_ErrEndOfFile(FlashFSError):
    """
    The end of the file is reached: no more records available.
    """
    ErrorCode = 0x00014906
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrEndOfFile"
class FlashFS_ErrFull(FlashFSError):
    """
    There is no more space on the Dataflash.
    """
    ErrorCode = 0x00014907
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrFull"
class FlashFS_ErrFileExist(FlashFSError):
    """
    The file cannot be created, since it already exists.
    """
    ErrorCode = 0x00014908
    URL = "https://docs.baltech.de/refman/cmds/flashfs/index.html#FlashFS.ErrFileExist"
class FtobError(BaltechApiError):
    ErrorCode = 0x00010300
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html"
class Ftob_ErrInvalidFilename(FtobError):
    """
    The specified file name is not supported by the reader.
    """
    ErrorCode = 0x00010301
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrInvalidFilename"
class Ftob_ErrFileAccessDenied(FtobError):
    """
    Permission missing to read/write file.
    """
    ErrorCode = 0x00010302
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrFileAccessDenied"
class Ftob_ErrWriteBlock(FtobError):
    """
    Cannot write data.
    """
    ErrorCode = 0x00010303
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrWriteBlock"
class Ftob_ErrReadBlock(FtobError):
    """
    Cannot read data.
    """
    ErrorCode = 0x00010304
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrReadBlock"
class Ftob_ErrNoFileActive(FtobError):
    """
    Cannot transfer data without opening a file.
    """
    ErrorCode = 0x00010305
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrNoFileActive"
class Ftob_ErrOutOfMemory(FtobError):
    """
    Filesystem ran out of memory.
    """
    ErrorCode = 0x00010306
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrOutOfMemory"
class Ftob_ErrBroken(FtobError):
    """
    Transfer was broken prematurely with FinishTransfer.
    """
    ErrorCode = 0x00010307
    URL = "https://docs.baltech.de/refman/cmds/ftob/index.html#Ftob.ErrBroken"
class HIDError(BaltechApiError):
    ErrorCode = 0x00013300
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html"
class HID_ErrHidNoTag(HIDError):
    """
    No tag error.
    """
    ErrorCode = 0x00013301
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidNoTag"
class HID_ErrHidRxdata(HIDError):
    """
    Wrong length or wrong data.
    """
    ErrorCode = 0x00013303
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidRxdata"
class HID_ErrHidParity(HIDError):
    """
    Parity error.
    """
    ErrorCode = 0x00013305
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidParity"
class HID_ErrHidParam(HIDError):
    """
    Wrong command param (on HF).
    """
    ErrorCode = 0x00013307
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidParam"
class HID_ErrHidHfreqctrl(HIDError):
    """
    Another task requested control over HF via hf_request_control.
    """
    ErrorCode = 0x00013308
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidHfreqctrl"
class HID_ErrHidHw(HIDError):
    """
    Reader chip hardware error.
    """
    ErrorCode = 0x00013309
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidHw"
class HID_ErrHidHwNotSupported(HIDError):
    """
    Hardware not supported.
    """
    ErrorCode = 0x0001330B
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrHidHwNotSupported"
class HID_ErrLicense(HIDError):
    """
    You use an HID Prox/Indala/Keri card, but the reader doesn't have the
    [required Prox license](https://docs.baltech.de/project-setup/get-prox-
    license-for-hid-prox-indala-keri.html).
    """
    ErrorCode = 0x0001330C
    URL = "https://docs.baltech.de/refman/cmds/hid/index.html#HID.ErrLicense"
class HitagError(BaltechApiError):
    ErrorCode = 0x00013000
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html"
class Hitag_ErrHtgNoTag(HitagError):
    """
    No tag error.
    """
    ErrorCode = 0x00013001
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgNoTag"
class Hitag_ErrHtgCollision(HitagError):
    """
    Collision occurred.
    """
    ErrorCode = 0x00013002
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgCollision"
class Hitag_ErrHtgRxdata(HitagError):
    """
    Wrong length or wrong data.
    """
    ErrorCode = 0x00013003
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgRxdata"
class Hitag_HtgChecksum(HitagError):
    """
    Receive checksum error.
    """
    ErrorCode = 0x00013004
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.HtgChecksum"
class Hitag_HtgWrongParam(HitagError):
    """
    Wrong command parameter.
    """
    ErrorCode = 0x00013007
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.HtgWrongParam"
class Hitag_ErrHtgAuth(HitagError):
    """
    Authentication error.
    """
    ErrorCode = 0x00013009
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgAuth"
class Hitag_ErrHtgOvTo(HitagError):
    """
    ISR buffer overflow during send/receive, TO during send.
    """
    ErrorCode = 0x00013008
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgOvTo"
class Hitag_ErrHtgHw(HitagError):
    """
    Reader chip HW error.
    """
    ErrorCode = 0x0001300A
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgHw"
class Hitag_ErrHtgCr(HitagError):
    """
    Crypt processor HW error.
    """
    ErrorCode = 0x0001300B
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgCr"
class Hitag_ErrHtgCfg(HitagError):
    """
    Update of configuration not successful.
    """
    ErrorCode = 0x0001300C
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgCfg"
class Hitag_ErrHtgHfreqctrl(HitagError):
    """
    Another task requested control over HF via hf_request_control.
    """
    ErrorCode = 0x0001300D
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgHfreqctrl"
class Hitag_ErrHtgHwNotSupported(HitagError):
    """
    Hardware not supported.
    """
    ErrorCode = 0x0001300F
    URL = "https://docs.baltech.de/refman/cmds/hitag/index.html#Hitag.ErrHtgHwNotSupported"
class I2cError(BaltechApiError):
    ErrorCode = 0x00010800
    URL = "https://docs.baltech.de/refman/cmds/i2c/index.html"
class I2c_ErrI2CRead(I2cError):
    """
    Error reading from I2C interface.
    """
    ErrorCode = 0x00010801
    URL = "https://docs.baltech.de/refman/cmds/i2c/index.html#I2c.ErrI2CRead"
class I2c_ErrI2CWrite(I2cError):
    """
    Error writing to I2C interface.
    """
    ErrorCode = 0x00010802
    URL = "https://docs.baltech.de/refman/cmds/i2c/index.html#I2c.ErrI2CWrite"
class Iso14aError(BaltechApiError):
    ErrorCode = 0x00011300
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html"
class Iso14a_ErrNoTag(Iso14aError):
    """
    No card in field of antenna or card in field of antenna does not match the
    given VHL-file.
    """
    ErrorCode = 0x00011301
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrNoTag"
class Iso14a_ErrCollision(Iso14aError):
    """
    More than one PICC answered in the same time slot and none of them could
    therefore be requested correctly.
    
    **In case this status code is returned by the[
    Iso14a.Request](.#Iso14a.Request) command, when two or more ISO 14443 Type A
    PICCs of different types (e.g. one Mifare Classic card and one Mifare DESFire
    card) are present in the HF field of the reader, the AQTA response will still
    be returned and the card selection procedure can be continued normally with
    the[ Iso14a.Select](.#Iso14a.Select) command.**
    """
    ErrorCode = 0x00011302
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrCollision"
class Iso14a_ErrHf(Iso14aError):
    """
    General HF error.
    """
    ErrorCode = 0x00011304
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrHf"
class Iso14a_ErrKey(Iso14aError):
    """
    Key error (Only triggered by Mifare authentication).
    """
    ErrorCode = 0x00011306
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrKey"
class Iso14a_ErrFrame(Iso14aError):
    """
    Bit error, Parity error or Frame error (start/stop bit).
    """
    ErrorCode = 0x00011307
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrFrame"
class Iso14a_ErrCrc(Iso14aError):
    """
    CRC checksum error.
    """
    ErrorCode = 0x00011308
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrCrc"
class Iso14a_ErrCom(Iso14aError):
    """
    Error in communication with reader chip.
    """
    ErrorCode = 0x00011310
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrCom"
class Iso14a_ErrEeprom(Iso14aError):
    """
    Error accessing EEPROM of the reader chip.
    """
    ErrorCode = 0x00011321
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrEeprom"
class Iso14a_ErrCardNotSupported(Iso14aError):
    """
    Reader chip does not support card type.
    """
    ErrorCode = 0x00011322
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrCardNotSupported"
class Iso14a_ErrHwNotSupported(Iso14aError):
    """
    Command not supported by hardware.
    """
    ErrorCode = 0x00011323
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.ErrHwNotSupported"
class Iso14a_BreakErr(Iso14aError):
    """
    Command has been interrupted.
    """
    ErrorCode = 0x00011330
    URL = "https://docs.baltech.de/refman/cmds/iso14a/index.html#Iso14a.BreakErr"
class Iso14bError(BaltechApiError):
    ErrorCode = 0x00011400
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html"
class Iso14b_ErrNoTag(Iso14bError):
    """
    No card in field of antenna or card in field of antenna does not match given
    VHL-file.
    """
    ErrorCode = 0x00011401
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrNoTag"
class Iso14b_ErrCollision(Iso14bError):
    """
    More than one PICC answered in the same time slot and none of them could
    therefore be requested correctly. The [Iso14b.Request](.#Iso14b.Request)
    command needs to be called again, maybe with more time slots.
    """
    ErrorCode = 0x00011402
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrCollision"
class Iso14b_ErrAuth(Iso14bError):
    """
    Authentication error.
    """
    ErrorCode = 0x00011403
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrAuth"
class Iso14b_ErrHf(Iso14bError):
    """
    General HF error.
    """
    ErrorCode = 0x00011404
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrHf"
class Iso14b_ErrFrame(Iso14bError):
    """
    Bit error, parity error or frame error (start/stop bit).
    """
    ErrorCode = 0x00011407
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrFrame"
class Iso14b_ErrCrc(Iso14bError):
    """
    CRC checksum error.
    """
    ErrorCode = 0x00011408
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrCrc"
class Iso14b_ErrCom(Iso14bError):
    """
    Error in communication with reader chip.
    """
    ErrorCode = 0x00011410
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrCom"
class Iso14b_ErrEeprom(Iso14bError):
    """
    Error accessing EEPROM of the reader chip.
    """
    ErrorCode = 0x00011421
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrEeprom"
class Iso14b_ErrCardNotSupported(Iso14bError):
    """
    Reader chip does not support card type.
    """
    ErrorCode = 0x00011422
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrCardNotSupported"
class Iso14b_ErrMem(Iso14bError):
    """
    Either internal list of labels or response buffer full.
    """
    ErrorCode = 0x00011423
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrMem"
class Iso14b_ErrHwNotSupported(Iso14bError):
    """
    Command not supported by hardware.
    """
    ErrorCode = 0x00011424
    URL = "https://docs.baltech.de/refman/cmds/iso14b/index.html#Iso14b.ErrHwNotSupported"
class Iso14L4Error(BaltechApiError):
    ErrorCode = 0x00011600
    URL = "https://docs.baltech.de/refman/cmds/iso14l4/index.html"
class Iso14L4_ErrNoTag(Iso14L4Error):
    """
    No card in field of antenna or card in field of antenna does not match given
    VHL-file.
    """
    ErrorCode = 0x00011601
    URL = "https://docs.baltech.de/refman/cmds/iso14l4/index.html#Iso14L4.ErrNoTag"
class Iso14L4_ErrHf(Iso14L4Error):
    """
    General HF error.
    """
    ErrorCode = 0x00011604
    URL = "https://docs.baltech.de/refman/cmds/iso14l4/index.html#Iso14L4.ErrHf"
class Iso14L4_ErrCard(Iso14L4Error):
    """
    PICC corrupt or behaves unspecified.
    """
    ErrorCode = 0x00011605
    URL = "https://docs.baltech.de/refman/cmds/iso14l4/index.html#Iso14L4.ErrCard"
class Iso14L4_ErrCom(Iso14L4Error):
    """
    Error in communication to reader chip.
    """
    ErrorCode = 0x00011610
    URL = "https://docs.baltech.de/refman/cmds/iso14l4/index.html#Iso14L4.ErrCom"
class Iso14L4_ErrCmd(Iso14L4Error):
    """
    Command and/or parameters invalid.
    """
    ErrorCode = 0x00011623
    URL = "https://docs.baltech.de/refman/cmds/iso14l4/index.html#Iso14L4.ErrCmd"
class I4CEError(BaltechApiError):
    ErrorCode = 0x00014800
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html"
class I4CE_ErrIso144State(I4CEError):
    """
    Emulated PICC currently not in the proper state to exchange ISO14443-4 APDUs
    (PCD didn't activate the protocol or PICC has been deselected).
    
    Card emulation has to be restarted.
    """
    ErrorCode = 0x00014801
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html#I4CE.ErrIso144State"
class I4CE_ErrCom(I4CEError):
    """
    Communication problem between microcontroller and reader chip.
    """
    ErrorCode = 0x00014802
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html#I4CE.ErrCom"
class I4CE_ErrTransmission(I4CEError):
    """
    HF transmission error (e.g. CRC, framing,...).
    """
    ErrorCode = 0x00014803
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html#I4CE.ErrTransmission"
class I4CE_ErrTimeout(I4CEError):
    """
    Timeout: no APDU was received from the PCD within the specified time.
    """
    ErrorCode = 0x00014804
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html#I4CE.ErrTimeout"
class I4CE_ErrOverflow(I4CEError):
    """
    Buffer overflow: the PCD sent more data than the receive buffer of the
    emulated PICC can handle.
    """
    ErrorCode = 0x00014805
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html#I4CE.ErrOverflow"
class I4CE_ErrInternal(I4CEError):
    """
    Internal error - should never occur.
    """
    ErrorCode = 0x00014806
    URL = "https://docs.baltech.de/refman/cmds/i4ce/index.html#I4CE.ErrInternal"
class Iso14CEError(BaltechApiError):
    ErrorCode = 0x00014A00
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html"
class Iso14CE_ErrIso144State(Iso14CEError):
    """
    Emulated PICC currently not in the proper state to exchange ISO14443-4 APDUs
    (PCD didn't activate the protocol)
    
    Card emulation has to be restarted.
    """
    ErrorCode = 0x00014A01
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrIso144State"
class Iso14CE_ErrCom(Iso14CEError):
    """
    Communication problem between microcontroller and reader chip.
    """
    ErrorCode = 0x00014A02
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrCom"
class Iso14CE_ErrTransmission(Iso14CEError):
    """
    HF transmission error (e.g. CRC, framing,...).
    """
    ErrorCode = 0x00014A03
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrTransmission"
class Iso14CE_ErrTimeout(Iso14CEError):
    """
    Timeout: no APDU was received from the PCD within the specified time.
    """
    ErrorCode = 0x00014A04
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrTimeout"
class Iso14CE_ErrOverflow(Iso14CEError):
    """
    Buffer overflow: the PCD sent more data than the receive buffer of the
    emulated PICC can handle.
    """
    ErrorCode = 0x00014A05
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrOverflow"
class Iso14CE_ErrInternal(Iso14CEError):
    """
    Internal error - should never occur.
    """
    ErrorCode = 0x00014A06
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrInternal"
class Iso14CE_ErrDeselect(Iso14CEError):
    """
    PICC has been deselected.
    """
    ErrorCode = 0x00014A07
    URL = "https://docs.baltech.de/refman/cmds/iso14ce/index.html#Iso14CE.ErrDeselect"
class Iso15Error(BaltechApiError):
    ErrorCode = 0x00012100
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html"
class Iso15_ErrNoTag(Iso15Error):
    """
    No label in field of antenna.
    """
    ErrorCode = 0x00012101
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrNoTag"
class Iso15_ErrCollision(Iso15Error):
    """
    This status code is triggered by two events:
    
      * A collision between two or more labels occurred. 
      * DSFID different - cannot resolve collision.
    """
    ErrorCode = 0x00012102
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrCollision"
class Iso15_ErrHf(Iso15Error):
    """
    General HF Error.
    """
    ErrorCode = 0x00012104
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrHf"
class Iso15_ErrLabel(Iso15Error):
    """
    Label status error.
    """
    ErrorCode = 0x00012105
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrLabel"
class Iso15_ErrCom(Iso15Error):
    """
    Error in communication to reader chip.
    """
    ErrorCode = 0x00012110
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrCom"
class Iso15_ErrCmd(Iso15Error):
    """
    Command and/or parameters invalid.
    """
    ErrorCode = 0x00012120
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrCmd"
class Iso15_ErrParamNotSupported(Iso15Error):
    """
    Reader chip does not support label type parameters.
    """
    ErrorCode = 0x00012123
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrParamNotSupported"
class Iso15_ErrMem(Iso15Error):
    """
    Either internal list of labels or response buffer full.
    """
    ErrorCode = 0x00012124
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrMem"
class Iso15_ErrLabelBlocksize(Iso15Error):
    """
    The blocks requested are not equal in size (Read multiple blocks).
    """
    ErrorCode = 0x00012125
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrLabelBlocksize"
class Iso15_ErrHwNotSupported(Iso15Error):
    """
    Command not supported by hardware.
    """
    ErrorCode = 0x00012126
    URL = "https://docs.baltech.de/refman/cmds/iso15/index.html#Iso15.ErrHwNotSupported"
class Iso78Error(BaltechApiError):
    ErrorCode = 0x00014000
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html"
class Iso78_ErrInvalidSlot(Iso78Error):
    """
    The specified slot index is not supported.
    """
    ErrorCode = 0x00014002
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html#Iso78.ErrInvalidSlot"
class Iso78_ErrAbort(Iso78Error):
    """
    SAM aborted command execution by sending an abort command.
    """
    ErrorCode = 0x00014010
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html#Iso78.ErrAbort"
class Iso78_ErrProtNotSupported(Iso78Error):
    """
    The specified protocol is not supported.
    """
    ErrorCode = 0x00014020
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html#Iso78.ErrProtNotSupported"
class Iso78_ErrCom(Iso78Error):
    """
    Communication error.
    """
    ErrorCode = 0x00014021
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html#Iso78.ErrCom"
class Iso78_ErrHw(Iso78Error):
    """
    Hardware error.
    """
    ErrorCode = 0x00014022
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html#Iso78.ErrHw"
class Iso78_ErrInvalid7816Cmd(Iso78Error):
    """
    The command/parameter(s) is/are not supported by the SAM.
    """
    ErrorCode = 0x00014031
    URL = "https://docs.baltech.de/refman/cmds/iso78/index.html#Iso78.ErrInvalid7816Cmd"
class KeyboardError(BaltechApiError):
    ErrorCode = 0x00014200
    URL = "https://docs.baltech.de/refman/cmds/keyboard/index.html"
class LegicError(BaltechApiError):
    ErrorCode = 0x00011E00
    URL = "https://docs.baltech.de/refman/cmds/legic/index.html"
class Legic_ErrCommunication(LegicError):
    """
    Communication error.
    
    Command could not be executed successfully due to a error in the communication
    of the reader controller with the LEGIC chip (e.g. checksum error, internal
    timeout error). It is recommended to repeat the command.
    """
    ErrorCode = 0x00011E01
    URL = "https://docs.baltech.de/refman/cmds/legic/index.html#Legic.ErrCommunication"
class Legic_ErrNotInitialized(LegicError):
    """
    LEGIC support is not initialized yet.
    
    After powering up, the LEGIC chip normally needs several 100 milliseconds
    until it is ready to execute commands. As long as the reader returns this
    status code the command needs to be repeated.
    
    If the LEGIC chip is still not available 3.5 seconds after the reader has
    powered up, usually due to a hardware defect, the _Rf13MHzLegic_ boot status
    of the Baltech reader will be set (The Baltech reader boot status can be read
    using the [Sys.GetBootStatus](system.xml#Sys.GetBootStatus) command).
    """
    ErrorCode = 0x00011E02
    URL = "https://docs.baltech.de/refman/cmds/legic/index.html#Legic.ErrNotInitialized"
class Legic_ErrNotAssembled(LegicError):
    """
    No appropriate LEGIC reader chip is assembled on this hardware.
    
    This reader device doesn't support LEGIC or doesn't contain the required LEGIC
    reader chip to execute the called command. Please check the model number.
    """
    ErrorCode = 0x00011E03
    URL = "https://docs.baltech.de/refman/cmds/legic/index.html#Legic.ErrNotAssembled"
class LgError(BaltechApiError):
    ErrorCode = 0x00011100
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html"
class Lg_ErrNomim(LgError):
    """
    No LEGIC Prime card detected.
    """
    ErrorCode = 0x00011101
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrNomim"
class Lg_ErrInvalidCmd(LgError):
    """
    Either the desired command is impossible to execute because no card is
    currently selected, or the specified parameters are invalid (e.g. wrong
    address, to many Bytes specified for reading/writing, ...). This status code
    may also come up when the [Lg.Select](.#Lg.Select) command is executed when
    less than 5 Bytes to read are specified and access has been denied.
    
    A card that was already selected before execution of the command triggering
    this status code will stay selected.
    """
    ErrorCode = 0x00011102
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrInvalidCmd"
class Lg_ErrAccessDenied(LgError):
    """
    Read/write not allowed due to the access conditions flags of the selected
    card/segment.
    
    A card that was already selected before execution of the command triggering
    this status code will stay selected.
    """
    ErrorCode = 0x00011103
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrAccessDenied"
class Lg_ErrHf(LgError):
    """
    Error occurred while transferring data via the HF field.
    
    An occurrence of this error makes it necessary to reselect the card with the
    [Lg.Select](.#Lg.Select) command for further communication.
    """
    ErrorCode = 0x00011104
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrHf"
class Lg_ErrDataCorrupt(LgError):
    """
    Data has been corrupted during transmission between the reader and the card.
    
    **In case this error is generated by the[ Lg.WriteMIM](.#Lg.WriteMIM) command
    or by the[ Lg.WriteMIMCRC](.#Lg.WriteMIMCRC) command, corrupted data may have
    been written to the card. Please make sure to rewrite the data correctly to
    ensure consistency.**
    
    An occurrence of this error makes it necessary to reselect the card with the
    [Lg.Select](.#Lg.Select) command for further communication.
    """
    ErrorCode = 0x00011105
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrDataCorrupt"
class Lg_ErrCrc(LgError):
    """
    CRC checksum invalid.
    
    A card that was already selected before execution of the command triggering
    this status code will stay selected.
    """
    ErrorCode = 0x00011106
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrCrc"
class Lg_ErrCommunication(LgError):
    """
    Checksum error most likely occurred in internal communication. It is
    recommended to repeat the command.
    
    A card that was already selected before execution of the command triggering
    this status code will stay selected.
    """
    ErrorCode = 0x00011107
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrCommunication"
class Lg_ErrMimCorrupt(LgError):
    """
    Card is corrupted and may not longer be used.
    """
    ErrorCode = 0x00011108
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrMimCorrupt"
class Lg_ErrBusy(LgError):
    """
    The SM05 is busy and cannot process the command. Please wait until
    communication with the SM05 is finished.
    """
    ErrorCode = 0x00011109
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.ErrBusy"
class Lg_NotInitialized(LgError):
    """
    The SC-2560 is still powering up and is not available yet.
    """
    ErrorCode = 0x0001110A
    URL = "https://docs.baltech.de/refman/cmds/lg/index.html#Lg.NotInitialized"
class LgaError(BaltechApiError):
    ErrorCode = 0x00011200
    URL = "https://docs.baltech.de/refman/cmds/lga/index.html"
class Lga_ErrNotag(LgaError):
    """
    No LEGIC Advant/Prime card found in the reader's HF field or communication
    with card lost.
    """
    ErrorCode = 0x00011201
    URL = "https://docs.baltech.de/refman/cmds/lga/index.html#Lga.ErrNotag"
class Lga_ErrLegic(LgaError):
    """
    The LEGIC reader chip returned an error code.
    
    The LEGIC reader reported an error that occurred during command execution. The
    actual LEGIC status code appears in the response parameter.
    """
    ErrorCode = 0x00011202
    URL = "https://docs.baltech.de/refman/cmds/lga/index.html#Lga.ErrLegic"
class Lga_ErrCommunication(LgaError):
    """
    Communication error.
    
    Command could not be executed successfully due to a error in the communication
    of the reader controller with the LEGIC chip (e.g. checksum error, internal
    timeout error). It is recommended to repeat the command.
    """
    ErrorCode = 0x00011203
    URL = "https://docs.baltech.de/refman/cmds/lga/index.html#Lga.ErrCommunication"
class Lga_ErrNotInitialized(LgaError):
    """
    LEGIC support is not initialized yet.
    
    After powering up, the LEGIC chip normally needs several 100 milliseconds
    until it is ready to execute commands. As long as the reader returns this
    status code the command needs to be repeated.
    
    If the LEGIC chip is still not available 3.5 seconds after the reader has
    powered up, usually due to a hardware defect, the _Rf13MHzLegic_ boot status
    of the Baltech reader will be set (The Baltech reader boot status can be read
    using the [Sys.GetBootStatus](system.xml#Sys.GetBootStatus) command).
    """
    ErrorCode = 0x00011204
    URL = "https://docs.baltech.de/refman/cmds/lga/index.html#Lga.ErrNotInitialized"
class Lga_ErrNotAssembled(LgaError):
    """
    No LEGIC reader chip is assembled on this hardware.
    
    This reader device doesn't support LEGIC. Please check the model number.
    """
    ErrorCode = 0x00011205
    URL = "https://docs.baltech.de/refman/cmds/lga/index.html#Lga.ErrNotAssembled"
class LicError(BaltechApiError):
    ErrorCode = 0x00010B00
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html"
class Lic_ErrNoLicCard(LicError):
    """
    No valid LicenseCard detected.
    """
    ErrorCode = 0x00010B01
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html#Lic.ErrNoLicCard"
class Lic_ErrAccess(LicError):
    """
    Card cannot be accessed (e.g. card was removed too early).
    """
    ErrorCode = 0x00010B02
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html#Lic.ErrAccess"
class Lic_ErrNotSupported(LicError):
    """
    The license type of the presented LicenseCard isn't supported by the reader
    hardware or firmware.  
    _Example:_ Readers without 125 kHz interface don't support LicenseCards
    containing [Prox licenses](https://docs.baltech.de/installation/deploy-
    license.html).
    """
    ErrorCode = 0x00010B03
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html#Lic.ErrNotSupported"
class Lic_ErrAlreadyActive(LicError):
    """
    A license of this type is already activated on the reader.
    """
    ErrorCode = 0x00010B04
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html#Lic.ErrAlreadyActive"
class Lic_ErrNoFreeLicense(LicError):
    """
    The LicenseCard contains no free license.
    """
    ErrorCode = 0x00010B05
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html#Lic.ErrNoFreeLicense"
class Lic_ErrActivation(LicError):
    """
    The license couldn't be activated on the reader.  
    
    **Please[ get in touch](https://docs.baltech.de/support/contact-support.html)
    with us.**
    """
    ErrorCode = 0x00010B06
    URL = "https://docs.baltech.de/refman/cmds/lic/index.html#Lic.ErrActivation"
class MainError(BaltechApiError):
    ErrorCode = 0x0001F000
    URL = "https://docs.baltech.de/refman/cmds/main/index.html"
class Main_ErrOutdatedFirmware(MainError):
    """
    Is returned by isFirmwareUpToDate() if the following piece of firmware is not
    up to date.
    """
    ErrorCode = 0x0001F001
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrOutdatedFirmware"
class Main_ErrUnknownVersion(MainError):
    """
    Is returned by isFirmwareUpToDate() if it's unknown whether the following
    piece of firmware is outdated or not.
    """
    ErrorCode = 0x0001F002
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrUnknownVersion"
class Main_ErrInvalidState(MainError):
    """
    Is returned by Bf3UploadStart if an upload process is already running or by
    Bf3UploadContinue if an upload process is currently not active.
    """
    ErrorCode = 0x0001F010
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidState"
class Main_ErrReadFile(MainError):
    """
    Is returned by Bf3UploadContinue if BF3/BEC2 file data couldn't be retrieved
    from the host.
    """
    ErrorCode = 0x0001F011
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrReadFile"
class Main_ErrInvalidFormat(MainError):
    """
    Is returned by Bf3UploadContinue if the BF3/BEC2 file has an invalid format.
    """
    ErrorCode = 0x0001F012
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidFormat"
class Main_ErrInvalidCustomerKey(MainError):
    """
    Is returned by Bf3UploadContinue if the customer key of the BEC2 file doesn't
    match the customer key stored in the reader.
    """
    ErrorCode = 0x0001F013
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidCustomerKey"
class Main_ErrInvalidConfigSecurityCode(MainError):
    """
    Is returned by Bf3UploadContinue if the Config Security Code of the BEC2 file
    doesn't match the Config Security Code stored in the reader ([ learn
    more](https://docs.baltech.de/project-setup/security.html#config-security-
    code)).
    """
    ErrorCode = 0x0001F014
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidConfigSecurityCode"
class Main_ErrInvalidConfigVersion(MainError):
    """
    Is returned by Bf3UploadContinue if the configuration version of the BEC2 file
    is older than the configuration version stored in the reader.
    """
    ErrorCode = 0x0001F015
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidConfigVersion"
class Main_ErrInvalidCmac(MainError):
    """
    Is returned by Bf3UploadContinue if the Message Authentication Code (CMAC) of
    the BF3/BEC2 file is incorrect.
    """
    ErrorCode = 0x0001F016
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidCmac"
class Main_ErrUpload(MainError):
    """
    Is returned by Bf3UploadContinue if a component of the current BF3/BEC2 file
    couldn't be written to the reader memory.
    """
    ErrorCode = 0x0001F017
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrUpload"
class Main_ErrUnsupportedFirmware(MainError):
    """
    Is returned by Bf3UploadContinue if the BF3/BEC2 file contains a firmware
    which is not supported by the reader hardware.
    """
    ErrorCode = 0x0001F018
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrUnsupportedFirmware"
class Main_ErrAlreadyUpToDate(MainError):
    """
    Is returned by Bf3UploadContinue if all relevant components of the current
    BF3/BEC2 file are already up to date.
    """
    ErrorCode = 0x0001F019
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrAlreadyUpToDate"
class Main_ErrMissingConfigSecurityCode(MainError):
    """
    Is returned by Bf3UploadContinue if the reader was not able to decode the
    current BEC2 file, because there is no Config Security Code stored in the
    reader yet.
    """
    ErrorCode = 0x0001F01A
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrMissingConfigSecurityCode"
class Main_ErrInvalidEccKey(MainError):
    """
    The elliptic curve key that is used to encrypt the configuration is wrong.
    """
    ErrorCode = 0x0001F01B
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrInvalidEccKey"
class Main_ErrVerify(MainError):
    """
    Is returned by SwitchFW and Bf3UploadContinue if the cryptographic signature
    of the firmware cannot be verified successfully.
    """
    ErrorCode = 0x0001F01C
    URL = "https://docs.baltech.de/refman/cmds/main/index.html#Main.ErrVerify"
class MceError(BaltechApiError):
    ErrorCode = 0x00014D00
    URL = "https://docs.baltech.de/refman/cmds/mce/index.html"
class Mce_ErrNoTag(MceError):
    """
    No valid MCE device is currently presented to the reader.
    """
    ErrorCode = 0x00014D01
    URL = "https://docs.baltech.de/refman/cmds/mce/index.html#Mce.ErrNoTag"
class Mce_ErrDisabled(MceError):
    """
    MCE functionality is currently disabled.
    """
    ErrorCode = 0x00014D03
    URL = "https://docs.baltech.de/refman/cmds/mce/index.html#Mce.ErrDisabled"
class Mce_ErrLicense(MceError):
    """
    A valid BLE license is required, but not available.
    """
    ErrorCode = 0x00014D04
    URL = "https://docs.baltech.de/refman/cmds/mce/index.html#Mce.ErrLicense"
class MifError(BaltechApiError):
    ErrorCode = 0x00011000
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html"
class Mif_ErrNoTag(MifError):
    """
    There's no card in the HF field, or the card doesn't respond.
    """
    ErrorCode = 0x00011001
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrNoTag"
class Mif_ErrCrc(MifError):
    """
    The response frame is invalid, e.g. it may contain an invalid CRC checksum.
    Please rerun the command.
    """
    ErrorCode = 0x00011002
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrCrc"
class Mif_ErrAuth(MifError):
    """
    Card authentication has failed.
    """
    ErrorCode = 0x00011004
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrAuth"
class Mif_ErrParity(MifError):
    """
    Legacy error code: The parity bits don't match the transmitted data.
    Authentication has been lost. Please reauthenticate and rerun the commands.
    """
    ErrorCode = 0x00011005
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrParity"
class Mif_ErrCode(MifError):
    """
    The card behaves in an unspecified way. Please rerun the command or reselect
    the card.
    """
    ErrorCode = 0x00011006
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrCode"
class Mif_ErrSnr(MifError):
    """
    Legacy error code: The serial number is wrong.
    """
    ErrorCode = 0x00011008
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrSnr"
class Mif_ErrKey(MifError):
    """
    The key in the SAM/crypto memory is invalid or missing.
    """
    ErrorCode = 0x00011009
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrKey"
class Mif_ErrNotauth(MifError):
    """
    Card authentication has failed. The current configuration/state doesn't allow
    the requested command.
    """
    ErrorCode = 0x0001100A
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrNotauth"
class Mif_ErrBitcount(MifError):
    """
    Legacy error code: HF data transition error. The number of received bits is
    invalid.
    """
    ErrorCode = 0x0001100B
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrBitcount"
class Mif_ErrBytecount(MifError):
    """
    Legacy error code: HF data transition error. The number of received bytes is
    invalid.
    """
    ErrorCode = 0x0001100C
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrBytecount"
class Mif_VcsAndProxCheckError(MifError):
    """
    The proximity check has timed out. Please reselect the card.
    """
    ErrorCode = 0x0001100E
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.VcsAndProxCheckError"
class Mif_ErrWrite(MifError):
    """
    Writing to the card has failed. Please rerun the command or check the access
    conditions.
    """
    ErrorCode = 0x0001100F
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrWrite"
class Mif_ErrInc(MifError):
    """
    Legacy error code: Increment couldn't be performed.
    """
    ErrorCode = 0x00011010
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrInc"
class Mif_ErrDecr(MifError):
    """
    Legacy error code: Decrement couldn't be performed.
    """
    ErrorCode = 0x00011011
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrDecr"
class Mif_ErrRead(MifError):
    """
    Reading data from the card has failed. Please rerun the command or check the
    access conditions.
    """
    ErrorCode = 0x00011012
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrRead"
class Mif_ErrOvfl(MifError):
    """
    Legacy error code: An overflow occurred during decrement or increment.
    """
    ErrorCode = 0x00011013
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrOvfl"
class Mif_ErrFraming(MifError):
    """
    The response frame is invalid, e.g. it may contain an invalid number of bits.
    Please rerun the command.
    """
    ErrorCode = 0x00011015
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrFraming"
class Mif_ErrBreak(MifError):
    """
    The command has been aborted because the HF interface has been requested by
    another task or command. Please reselect the card.
    
    **This error only occurs when you combine VHL and low-level commands. We
    highly recommend you avoid that combination as these 2 command sets will
    interfere with each other's card states.**
    """
    ErrorCode = 0x00011016
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrBreak"
class Mif_ErrCmd(MifError):
    """
    The specified command or parameters are unknown.
    """
    ErrorCode = 0x00011017
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrCmd"
class Mif_ErrColl(MifError):
    """
    An error occurred in the anti-collision sequence. Please reselect the card.
    """
    ErrorCode = 0x00011018
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrColl"
class Mif_ErrReaderChipCommunication(MifError):
    """
    Communication with the reader's HF interface has failed. Please reset the HF
    interface with [Sys.HFReset](system.xml#Sys.HFReset) and check the reader
    status with [Sys.GetBootStatus](system.xml#Sys.GetBootStatus).
    """
    ErrorCode = 0x0001101A
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrReaderChipCommunication"
class Mif_ErrFirmwareNotSupported(MifError):
    """
    This command isn't supported by the reader firmware.
    """
    ErrorCode = 0x0001101D
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrFirmwareNotSupported"
class Mif_ErrVal(MifError):
    """
    A value operation, e.g. increment or decrement, has failed. This may have
    several reasons, e.g. an invalid value format, or the value to manipulate
    doesn't exist on the card.
    """
    ErrorCode = 0x0001101E
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrVal"
class Mif_ErrIntegrity(MifError):
    """
    Secure messaging error: The CRC or MAC checksum doesn't match the transmitted
    data. Authentication has been lost. Please reauthenticate and rerun the
    commands, or check the security conditions.
    """
    ErrorCode = 0x0001101F
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrIntegrity"
class Mif_CondNotvalid(MifError):
    """
    Card error as per MIFARE specification: Condition of use not satisfied.
    """
    ErrorCode = 0x00011020
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.CondNotvalid"
class Mif_ErrHwNotSupported(MifError):
    """
    This command isn't supported by the reader hardware, i.e. by the SAM or reader
    chip.
    """
    ErrorCode = 0x00011021
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrHwNotSupported"
class Mif_ErrSamUnlock(MifError):
    """
    Unlocking/authenticating with the SAM has failed. Please check the
    [SamAVx](../cfg/base.xml#Project.SamAVx) configuration values.
    """
    ErrorCode = 0x00011022
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrSamUnlock"
class Mif_ErrSamCommunication(MifError):
    """
    Communication with the SAM has failed. This may have several reasons, e.g. the
    wrong SAM type or a failure to activate the SAM. Please check the SAM status
    and reset the reader with [Sys.Reset](system.xml#Sys.Reset).
    """
    ErrorCode = 0x00011023
    URL = "https://docs.baltech.de/refman/cmds/mif/index.html#Mif.ErrSamCommunication"
class MobileIdError(BaltechApiError):
    ErrorCode = 0x00014C00
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html"
class MobileId_ErrNoCredential(MobileIdError):
    """
    No valid credential has been presented to the reader so far.
    """
    ErrorCode = 0x00014C01
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html#MobileId.ErrNoCredential"
class MobileId_ErrProtocol(MobileIdError):
    """
    The credential is trying to perform an action that doesn't comply with the
    BALTECH Mobile ID protocol. (For details, please refer to the protocol
    specification, available on request.)
    """
    ErrorCode = 0x00014C02
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html#MobileId.ErrProtocol"
class MobileId_ErrAuthentication(MobileIdError):
    """
    An authentication error occured, e.g. invalid encryption key or authentication
    tag.
    """
    ErrorCode = 0x00014C03
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html#MobileId.ErrAuthentication"
class MobileId_ErrCredentialVersion(MobileIdError):
    """
    The version of the presented credential is not compatible with the current
    reader firmware.
    """
    ErrorCode = 0x00014C04
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html#MobileId.ErrCredentialVersion"
class MobileId_ErrCredentialCmac(MobileIdError):
    """
    The presented credential is rejected due to an invalid CMAC.
    """
    ErrorCode = 0x00014C05
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html#MobileId.ErrCredentialCmac"
class MobileId_ErrDisabled(MobileIdError):
    """
    Mobile ID functionality is currently disabled.
    """
    ErrorCode = 0x00014C10
    URL = "https://docs.baltech.de/refman/cmds/mobileid/index.html#MobileId.ErrDisabled"
class MsgQueueError(BaltechApiError):
    ErrorCode = 0x0001A600
    URL = "https://docs.baltech.de/refman/cmds/msgqueue/index.html"
class MsgQueue_ErrMsgqRecvTimeout(MsgQueueError):
    """
    Timeout: no message received within the specified time interval
    """
    ErrorCode = 0x0001A601
    URL = "https://docs.baltech.de/refman/cmds/msgqueue/index.html#MsgQueue.ErrMsgqRecvTimeout"
class MsgQueue_ErrMsgqNotackedTimeout(MsgQueueError):
    """
    Timeout: the message was not picked up within the specified time interval
    """
    ErrorCode = 0x0001A602
    URL = "https://docs.baltech.de/refman/cmds/msgqueue/index.html#MsgQueue.ErrMsgqNotackedTimeout"
class MsgQueue_ErrMsgqCollision(MsgQueueError):
    """
    Collision: there is already a message in the queue - pick up this data first
    """
    ErrorCode = 0x0001A603
    URL = "https://docs.baltech.de/refman/cmds/msgqueue/index.html#MsgQueue.ErrMsgqCollision"
class MsgQueue_ErrMsgqBufoverflow(MsgQueueError):
    """
    Buffer Overflow: the message is too large and can not be processed
    """
    ErrorCode = 0x0001A604
    URL = "https://docs.baltech.de/refman/cmds/msgqueue/index.html#MsgQueue.ErrMsgqBufoverflow"
class PicoError(BaltechApiError):
    ErrorCode = 0x00011A00
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html"
class Pico_ErrNoTag(PicoError):
    """
    No PICC
    """
    ErrorCode = 0x00011A01
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrNoTag"
class Pico_ErrCollision(PicoError):
    """
    Collision occurred (value will be ordered with bit position of collision in
    high nibble!)
    """
    ErrorCode = 0x00011A02
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrCollision"
class Pico_ErrHf(PicoError):
    """
    General HF error
    """
    ErrorCode = 0x00011A04
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrHf"
class Pico_ErrFrame(PicoError):
    """
    Bit error, parity error or frame error (start/stop-bit)
    """
    ErrorCode = 0x00011A07
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrFrame"
class Pico_ErrCrc(PicoError):
    """
    CRC checksum error
    """
    ErrorCode = 0x00011A08
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrCrc"
class Pico_ErrCom(PicoError):
    """
    Communication error UC - reader chip
    """
    ErrorCode = 0x00011A10
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrCom"
class Pico_ErrCardNotSupported(PicoError):
    """
    Reader chip does not support card type
    """
    ErrorCode = 0x00011A22
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrCardNotSupported"
class Pico_ErrHwNotSupported(PicoError):
    """
    Command not supported by hardware
    """
    ErrorCode = 0x00011A23
    URL = "https://docs.baltech.de/refman/cmds/pico/index.html#Pico.ErrHwNotSupported"
class PkiError(BaltechApiError):
    ErrorCode = 0x00010900
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html"
class Pki_ErrCrypto(PkiError):
    """
    Invalid Key used for encryption/MACing or MAC is invalid.
    """
    ErrorCode = 0x00010901
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html#Pki.ErrCrypto"
class Pki_ErrTunnel(PkiError):
    """
    It is not possible to tunnel this command.
    """
    ErrorCode = 0x00010902
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html#Pki.ErrTunnel"
class Pki_ErrCert(PkiError):
    """
    The certificate (or key) has invalid format or signature.
    """
    ErrorCode = 0x00010903
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html#Pki.ErrCert"
class Pki_ErrSeqctr(PkiError):
    """
    The sequence counter was too low.
    """
    ErrorCode = 0x00010904
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html#Pki.ErrSeqctr"
class Pki_ErrSeclevelUnsupported(PkiError):
    """
    This security level has no key for authentication.
    """
    ErrorCode = 0x00010905
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html#Pki.ErrSeclevelUnsupported"
class Pki_ErrSessionTimeout(PkiError):
    """
    The security session timed out.
    """
    ErrorCode = 0x00010906
    URL = "https://docs.baltech.de/refman/cmds/pki/index.html#Pki.ErrSessionTimeout"
class QKeyError(BaltechApiError):
    ErrorCode = 0x00013500
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html"
class QKey_ErrQkeyNoTag(QKeyError):
    """
    No tag error.
    """
    ErrorCode = 0x00013501
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyNoTag"
class QKey_ErrQkeyRxdata(QKeyError):
    """
    Wrong length or wrong data.
    """
    ErrorCode = 0x00013503
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyRxdata"
class QKey_ErrQkeyParity(QKeyError):
    """
    Parity error.
    """
    ErrorCode = 0x00013505
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyParity"
class QKey_ErrQkeyParam(QKeyError):
    """
    Wrong command param (on HF).
    """
    ErrorCode = 0x00013507
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyParam"
class QKey_ErrQkeyHfreqctrl(QKeyError):
    """
    Another task requested control over HF via hf_request_control.
    """
    ErrorCode = 0x00013508
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyHfreqctrl"
class QKey_ErrQkeyHw(QKeyError):
    """
    Missing Platform ID or Readerchip error.
    """
    ErrorCode = 0x00013509
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyHw"
class QKey_ErrQkeyHwNotSupported(QKeyError):
    """
    Hardware not supported.
    """
    ErrorCode = 0x0001350B
    URL = "https://docs.baltech.de/refman/cmds/qkey/index.html#QKey.ErrQkeyHwNotSupported"
class RtcError(BaltechApiError):
    ErrorCode = 0x00010400
    URL = "https://docs.baltech.de/refman/cmds/rtc/index.html"
class Rtc_ErrHardware(RtcError):
    """
    The RTC hardware is defect.
    """
    ErrorCode = 0x00010401
    URL = "https://docs.baltech.de/refman/cmds/rtc/index.html#Rtc.ErrHardware"
class Rtc_ErrVoltageLow(RtcError):
    """
    The battery of the RTC is low. The time may be invalid.
    """
    ErrorCode = 0x00010402
    URL = "https://docs.baltech.de/refman/cmds/rtc/index.html#Rtc.ErrVoltageLow"
class SecError(BaltechApiError):
    ErrorCode = 0x00010700
    URL = "https://docs.baltech.de/refman/cmds/sec/index.html"
class Sec_ErrCrypto(SecError):
    """
    Invalid key used for encryption/MACing, MAC address invalid, or decrypted data
    invalid.
    """
    ErrorCode = 0x00010701
    URL = "https://docs.baltech.de/refman/cmds/sec/index.html#Sec.ErrCrypto"
class Sec_ErrTunnel(SecError):
    """
    It is not possible to tunnel this command.
    """
    ErrorCode = 0x00010702
    URL = "https://docs.baltech.de/refman/cmds/sec/index.html#Sec.ErrTunnel"
class SrixError(BaltechApiError):
    ErrorCode = 0x00012400
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html"
class Srix_ErrNoTag(SrixError):
    """
    No Tag
    """
    ErrorCode = 0x00012401
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrNoTag"
class Srix_ErrFrame(SrixError):
    """
    Frame Error (CRC, parity...)
    """
    ErrorCode = 0x00012403
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrFrame"
class Srix_ErrHf(SrixError):
    """
    General hf error
    """
    ErrorCode = 0x00012404
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrHf"
class Srix_ErrCom(SrixError):
    """
    Hardware error
    """
    ErrorCode = 0x00012405
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrCom"
class Srix_ErrSrixCardtypeNotSupported(SrixError):
    """
    Chip type not supported by reader chip
    """
    ErrorCode = 0x00012406
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrSrixCardtypeNotSupported"
class Srix_ErrHwNotSupported(SrixError):
    """
    Hardware does not support reader chip
    """
    ErrorCode = 0x00012407
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrHwNotSupported"
class Srix_ErrCmdBreak(SrixError):
    """
    Command has been interrupted
    """
    ErrorCode = 0x00012408
    URL = "https://docs.baltech.de/refman/cmds/srix/index.html#Srix.ErrCmdBreak"
class SysError(BaltechApiError):
    ErrorCode = 0x00010000
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html"
class Sys_ErrCfgFull(SysError):
    """
    There's not enough space to store the reader's configuration values.
    """
    ErrorCode = 0x00010001
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgFull"
class Sys_ErrCfgAccess(SysError):
    """
    Reading/writing to the internal memory failed.  
    
    **Please[ get in touch](https://docs.baltech.de/support/contact-support.html)
    with us.**
    """
    ErrorCode = 0x00010002
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgAccess"
class Sys_ErrCfgNotFound(SysError):
    """
    The meaning of this status code varies depending on the access mode:
    
      * _Read access:_ The desired key/value couldn't be found in the configuration. 
      * _Write access:_ The key/value ID is invalid. The value couldn't be set.
    """
    ErrorCode = 0x00010003
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgNotFound"
class Sys_ErrInvalidCfgBlock(SysError):
    """
    The format of the configuration file (BEC file) is invalid.
    """
    ErrorCode = 0x00010004
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrInvalidCfgBlock"
class Sys_ErrCfgAccessDenied(SysError):
    """
    Memory access denied. The configuration value ID is too high (> 0x80).
    """
    ErrorCode = 0x00010005
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgAccessDenied"
class Sys_ErrRegAccess(SysError):
    """
    Register cannot be modified or doesn't exist.
    """
    ErrorCode = 0x00010006
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrRegAccess"
class Sys_ErrInvalidProtocol(SysError):
    """
    The selected protocol isn't supported by the current firmware.
    """
    ErrorCode = 0x00010007
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrInvalidProtocol"
class Sys_ErrNotSupportedByHardware(SysError):
    """
    This feature isn't supported by the reader hardware.
    """
    ErrorCode = 0x00010008
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrNotSupportedByHardware"
class Sys_ErrFactsetRestore(SysError):
    """
    Restoring the reader's factory settings failed.
    """
    ErrorCode = 0x00010009
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrFactsetRestore"
class Sys_ErrCfgConfigSecurityCode(SysError):
    """
    [Sys.CfgLoadBlock](.#Sys.CfgLoadBlock) was run with an invalid Config Security
    Code, i.e. the configuration you're trying to deploy is not a new version of
    the existing configuration, but a completely different configuration ([ learn
    more](https://docs.baltech.de/project-setup/security.html#config-security-
    code)).
    """
    ErrorCode = 0x0001000A
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgConfigSecurityCode"
class Sys_ErrCfgVersion(SysError):
    """
    [Sys.CfgLoadBlock](.#Sys.CfgLoadBlock) was run with a configuration version
    that is older than the one currently deployed ([ learn
    more](https://docs.baltech.de/project-setup/security.html#configuration-
    updates-with-rollback-prevention)).
    """
    ErrorCode = 0x0001000B
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgVersion"
class Sys_ErrCfgLoadWrongState(SysError):
    """
    The command can't be run in the current (CfgLoadBlock) state, i.e. [
    Sys.CfgLoadFinish](.#Sys.CfgLoadFinish) must be run after [
    Sys.CfgLoadPrepare](.#Sys.CfgLoadPrepare).
    """
    ErrorCode = 0x0001000C
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrCfgLoadWrongState"
class Sys_ErrInvalidFwCrc(SysError):
    """
    The CRC of the firmware is invalid. This error can only be returned by the
    [Sys.GetFwCrc](.#Sys.GetFwCrc) command.
    """
    ErrorCode = 0x0001007F
    URL = "https://docs.baltech.de/refman/cmds/sys/index.html#Sys.ErrInvalidFwCrc"
class TTFError(BaltechApiError):
    ErrorCode = 0x00013400
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html"
class TTF_ErrTtfNoTag(TTFError):
    """
    No tag error.
    """
    ErrorCode = 0x00013401
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfNoTag"
class TTF_ErrTtfRxdata(TTFError):
    """
    Wrong length or wrong data.
    """
    ErrorCode = 0x00013403
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfRxdata"
class TTF_ErrTtfParam(TTFError):
    """
    Wrong cmd param.
    """
    ErrorCode = 0x00013407
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfParam"
class TTF_ErrTtfOvTo(TTFError):
    """
    ISR buffer overflow during receive.
    """
    ErrorCode = 0x00013408
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfOvTo"
class TTF_ErrTtfHfreqctrl(TTFError):
    """
    Another task requested control over HF via hf_request_control.
    """
    ErrorCode = 0x00013409
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfHfreqctrl"
class TTF_ErrTtfHw(TTFError):
    """
    Platform ID missing or hardware error.
    """
    ErrorCode = 0x0001340A
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfHw"
class TTF_ErrTtfHwNotSupported(TTFError):
    """
    Hardware not supported.
    """
    ErrorCode = 0x0001340C
    URL = "https://docs.baltech.de/refman/cmds/ttf/index.html#TTF.ErrTtfHwNotSupported"
class EpcUidError(BaltechApiError):
    ErrorCode = 0x00012200
    URL = "https://docs.baltech.de/refman/cmds/epcuid/index.html"
class EpcUid_ErrNoTag(EpcUidError):
    """
    No label in field of antenna.
    """
    ErrorCode = 0x00012201
    URL = "https://docs.baltech.de/refman/cmds/epcuid/index.html#EpcUid.ErrNoTag"
class EpcUid_ErrHf(EpcUidError):
    """
    General HF error.
    """
    ErrorCode = 0x00012204
    URL = "https://docs.baltech.de/refman/cmds/epcuid/index.html#EpcUid.ErrHf"
class EpcUid_ErrCom(EpcUidError):
    """
    Error in communication to reader chip.
    """
    ErrorCode = 0x00012210
    URL = "https://docs.baltech.de/refman/cmds/epcuid/index.html#EpcUid.ErrCom"
class EpcUid_ErrCmd(EpcUidError):
    """
    Command and/or parameters invalid.
    """
    ErrorCode = 0x00012220
    URL = "https://docs.baltech.de/refman/cmds/epcuid/index.html#EpcUid.ErrCmd"
class UltralightError(BaltechApiError):
    ErrorCode = 0x00012500
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html"
class Ultralight_ErrNoTag(UltralightError):
    """
    There's no card in the HF field, or the card doesn't respond.
    """
    ErrorCode = 0x00012501
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrNoTag"
class Ultralight_ErrAuth(UltralightError):
    """
    Authentication with the card has failed.
    """
    ErrorCode = 0x00012502
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrAuth"
class Ultralight_ErrHf(UltralightError):
    """
    The response frame is invalid, e.g. it may contain an invalid number of bits
    or an invalid CRC checksum. Please rerun the command.
    """
    ErrorCode = 0x00012503
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrHf"
class Ultralight_ErrKey(UltralightError):
    """
    The encryption key is undefined or inaccessible.
    """
    ErrorCode = 0x00012504
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrKey"
class Ultralight_ErrNack(UltralightError):
    """
    The card didn't accept the command. Please check the conditions and rerun the
    command.
    """
    ErrorCode = 0x00012505
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrNack"
class Ultralight_ErrInterface(UltralightError):
    """
    Communication with the reader chip has failed. Please reset the reader with
    [Sys.Reset](system.xml#Sys.Reset) and check the reader chip status with
    [Sys.GetBootStatus](system.xml#Sys.GetBootStatus).
    """
    ErrorCode = 0x00012518
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrInterface"
class Ultralight_ErrCmd(UltralightError):
    """
    The specified command or parameters are unknown.
    """
    ErrorCode = 0x00012519
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrCmd"
class Ultralight_ErrHwNotSupported(UltralightError):
    """
    This command isn't supported by the reader hardware.
    """
    ErrorCode = 0x00012520
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrHwNotSupported"
class Ultralight_ErrFirmwareNotSupported(UltralightError):
    """
    This command isn't supported by the reader firmware.
    """
    ErrorCode = 0x00012521
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.ErrFirmwareNotSupported"
class Ultralight_BreakErr(UltralightError):
    """
    The command has been aborted because the HF interface has been requested by
    another task or command. Please reselect the card.
    
    **This error only occurs when you combine VHL and low-level commands. We
    highly recommend you avoid that combination as these 2 command sets will
    interfere with each other's card states.**
    """
    ErrorCode = 0x00012528
    URL = "https://docs.baltech.de/refman/cmds/ultralight/index.html#Ultralight.BreakErr"
class UlRdrError(BaltechApiError):
    ErrorCode = 0x0001A500
    URL = "https://docs.baltech.de/refman/cmds/ulrdr/index.html"
class UlRdr_ErrResponse(UlRdrError):
    """
    Response received from reader is unexpected.
    """
    ErrorCode = 0x0001A501
    URL = "https://docs.baltech.de/refman/cmds/ulrdr/index.html#UlRdr.ErrResponse"
class UlRdr_ErrSequence(UlRdrError):
    """
    Command sequence was not kept.
    """
    ErrorCode = 0x0001A502
    URL = "https://docs.baltech.de/refman/cmds/ulrdr/index.html#UlRdr.ErrSequence"
class UlRdr_ErrSignature(UlRdrError):
    """
    Signature of SEND_ENCRYPTED is invalid.
    """
    ErrorCode = 0x0001A503
    URL = "https://docs.baltech.de/refman/cmds/ulrdr/index.html#UlRdr.ErrSignature"
class UsbHostError(BaltechApiError):
    ErrorCode = 0x00014400
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html"
class UsbHost_UsbhstErrNotconnected(UsbHostError):
    """
    No device connected.
    """
    ErrorCode = 0x00014401
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrNotconnected"
class UsbHost_UsbhstErrTimeout(UsbHostError):
    """
    Device did not respond within Timeout.
    """
    ErrorCode = 0x00014402
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrTimeout"
class UsbHost_UsbhstErrNack(UsbHostError):
    """
    Device responded only with NACK within Timeout.
    """
    ErrorCode = 0x00014403
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrNack"
class UsbHost_UsbhstErrStall(UsbHostError):
    """
    Device responded with STALL.
    """
    ErrorCode = 0x00014404
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrStall"
class UsbHost_UsbhstErrTransfer(UsbHostError):
    """
    Error on transferring data (CRC, Invalid PID, ...).
    """
    ErrorCode = 0x00014405
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrTransfer"
class UsbHost_UsbhstErrUnexpectedPkt(UsbHostError):
    """
    Device sent unexpected data.
    """
    ErrorCode = 0x00014406
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrUnexpectedPkt"
class UsbHost_UsbhstErrBufferoverflow(UsbHostError):
    """
    Received too much data.
    """
    ErrorCode = 0x00014407
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrBufferoverflow"
class UsbHost_UsbhstErrSetupPipes(UsbHostError):
    """
    Failure on setting up pipes.
    """
    ErrorCode = 0x00014420
    URL = "https://docs.baltech.de/refman/cmds/usbhost/index.html#UsbHost.UsbhstErrSetupPipes"
class UIError(BaltechApiError):
    ErrorCode = 0x00010A00
    URL = "https://docs.baltech.de/refman/cmds/ui/index.html"
class UI_ErrInvalidPort(UIError):
    """
    The specified port isn't available or it doesn't support the desired
    operation.
    """
    ErrorCode = 0x00010A01
    URL = "https://docs.baltech.de/refman/cmds/ui/index.html#UI.ErrInvalidPort"
class VHLError(BaltechApiError):
    ErrorCode = 0x00010100
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html"
class VHL_ErrNoTag(VHLError):
    """
    This status code occurs in the following cases:
    
      * There's no card in the antenna field.
      * The card doesn't respond, i.e. it doesn't match the given VHL file.
      * You use an HID Prox/Indala/Keri card, but the reader doesn't have the [required Prox license](https://docs.baltech.de/project-setup/get-prox-license-for-hid-prox-indala-keri.html). 
    
    This status code is the only one that requires a reselection of the card with
    [VHL.Select](.#VHL.Select).
    """
    ErrorCode = 0x00010101
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrNoTag"
class VHL_ErrCardNotSelected(VHLError):
    """
    The command can't be run because no card is selected.
    """
    ErrorCode = 0x00010102
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrCardNotSelected"
class VHL_ErrHf(VHLError):
    """
    Communication problems with the card occurred. Data may have been corrupted.
    """
    ErrorCode = 0x00010103
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrHf"
class VHL_ErrConfig(VHLError):
    """
    The VHL file structure in the reader configuration is invalid or the specified
    VHL file isn't available.
    """
    ErrorCode = 0x00010104
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrConfig"
class VHL_ErrAuth(VHLError):
    """
    An authentication error occurred. Data may have been written partially. This
    may occur if the specified VHL file uses invalid keys (MIFARE) or the
    specified stamp is not in the reader's EEPROM (LEGIC).
    """
    ErrorCode = 0x00010105
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrAuth"
class VHL_ErrRead(VHLError):
    """
    The communication sequence was OK, but reading failed. The card remains
    selected. This may occur if the specified VHL file is too long for the
    physical card storage.
    """
    ErrorCode = 0x00010106
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrRead"
class VHL_ErrWrite(VHLError):
    """
    The communication sequence was OK, but writing failed. Data may have been
    written partially. The card remains selected. This may occur if the specified
    VHL file is too long for the physical card storage.
    """
    ErrorCode = 0x00010107
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrWrite"
class VHL_ConfcardRead(VHLError):
    """
    A BALTECH ConfigCard has been detected successfully and will be read after
    this command.
    """
    ErrorCode = 0x00010108
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ConfcardRead"
class VHL_ErrInvalidCardType(VHLError):
    """
    The desired card type doesn't match the card family of the currently selected
    card.
    """
    ErrorCode = 0x00010109
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrInvalidCardType"
class VHL_ErrNotSupported(VHLError):
    """
    The command is currently not supported. Future releases may support the
    command.
    """
    ErrorCode = 0x0001010A
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrNotSupported"
class VHL_ErrFormat(VHLError):
    """
    The communication sequence was OK, but formatting failed. Data may have been
    written partially. The card remains selected.
    """
    ErrorCode = 0x0001010B
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrFormat"
class VHL_ErrHw(VHLError):
    """
    An error occurred while communicating with the reader chip/SAM.
    """
    ErrorCode = 0x0001010C
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrHw"
class VHL_ErrApdu(VHLError):
    """
    Card communication error: The command has been aborted, or the response hasn't
    been read completely.
    """
    ErrorCode = 0x0001010D
    URL = "https://docs.baltech.de/refman/cmds/vhl/index.html#VHL.ErrApdu"
class DHWCtrlError(BaltechApiError):
    ErrorCode = 0x0001E000
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html"
class DHWCtrl_ErrUnknownPort(DHWCtrlError):
    """
    This port is not available on this hardware platform.
    """
    ErrorCode = 0x0001E001
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrUnknownPort"
class DHWCtrl_ErrMarshall(DHWCtrlError):
    """
    The structure of a StartupRun-block is wrong or the command
    [DHWCtrl.GetStartupRun](.#DHWCtrl.GetStartupRun) has not properly been called.
    """
    ErrorCode = 0x0001E002
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrMarshall"
class DHWCtrl_ErrNoStartupRun(DHWCtrlError):
    """
    There was no StartupRun-block, or the
    [DHWCtrl.GetStartupRun](.#DHWCtrl.GetStartupRun) command was not executed.
    """
    ErrorCode = 0x0001E003
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrNoStartupRun"
class DHWCtrl_ErrNoPowermgr(DHWCtrlError):
    """
    The Power Manager was unable to take the module into suspend mode.
    """
    ErrorCode = 0x0001E004
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrNoPowermgr"
class DHWCtrl_ErrNoProdloader(DHWCtrlError):
    """
    No production loader is present in the reader's flash memory.
    """
    ErrorCode = 0x0001E005
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrNoProdloader"
class DHWCtrl_ErrPfid2NotAvailable(DHWCtrlError):
    """
    No PlatformID2 available.
    """
    ErrorCode = 0x0001E006
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrPfid2NotAvailable"
class DHWCtrl_ErrEepIndex(DHWCtrlError):
    """
    Specified EEPROM address and amount of Bytes to write are not compatible.
    """
    ErrorCode = 0x0001E011
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrEepIndex"
class DHWCtrl_ErrEepVerify(DHWCtrlError):
    """
    Data written to EEPROM could not be verified.
    """
    ErrorCode = 0x0001E012
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrEepVerify"
class DHWCtrl_ErrEepTimeout(DHWCtrlError):
    """
    Data could not be written within timeout.
    """
    ErrorCode = 0x0001E013
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrEepTimeout"
class DHWCtrl_ErrDataflash(DHWCtrlError):
    """
    Dataflash could not be found.
    """
    ErrorCode = 0x0001E020
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrDataflash"
class DHWCtrl_ErrDataflashTimeout(DHWCtrlError):
    """
    Timeout occurred.
    """
    ErrorCode = 0x0001E021
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrDataflashTimeout"
class DHWCtrl_ErrDataflashVerify(DHWCtrlError):
    """
    Verification failed after writing data.
    """
    ErrorCode = 0x0001E022
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrDataflashVerify"
class DHWCtrl_ErrDataflashParam(DHWCtrlError):
    """
    Parameter(s)/address(es) are not valid.
    """
    ErrorCode = 0x0001E023
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrDataflashParam"
class DHWCtrl_ErrDataflashSpi(DHWCtrlError):
    """
    Communication via SPI interface failed.
    """
    ErrorCode = 0x0001E024
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrDataflashSpi"
class DHWCtrl_ErrDataflashFlash(DHWCtrlError):
    """
    Flash device behaves in an unspecified manner.
    """
    ErrorCode = 0x0001E025
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrDataflashFlash"
class DHWCtrl_ErrAvrProgSpi(DHWCtrlError):
    """
    SPI programming instruction couldn't be executed successfully.
    """
    ErrorCode = 0x0001E030
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrAvrProgSpi"
class DHWCtrl_ErrAvrProgPdi(DHWCtrlError):
    """
    PDI operation couldn't be executed successfully.
    """
    ErrorCode = 0x0001E031
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrAvrProgPdi"
class DHWCtrl_ErrNicNoData(DHWCtrlError):
    """
    No data was received by NIC.
    """
    ErrorCode = 0x0001E050
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrNicNoData"
class DHWCtrl_ErrNicBufferFlow(DHWCtrlError):
    """
    Received data was to big for buffer.
    """
    ErrorCode = 0x0001E051
    URL = "https://docs.baltech.de/refman/cmds/dhwctrl/index.html#DHWCtrl.ErrNicBufferFlow"
class LTError(BaltechApiError):
    ErrorCode = 0x0001A000
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html"
class LT_ErrLtNoTag(LTError):
    """
    No tag present in the reader's RFID field.
    """
    ErrorCode = 0x0001A001
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtNoTag"
class LT_ErrLtCrc(LTError):
    """
    CRC checksum error.
    """
    ErrorCode = 0x0001A002
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtCrc"
class LT_ErrLtParity(LTError):
    """
    Parity error.
    """
    ErrorCode = 0x0001A005
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtParity"
class LT_LtNackReceived(LTError):
    """
    NACK received, command not accepted.
    """
    ErrorCode = 0x0001A006
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.LtNackReceived"
class LT_ErrLtHf(LTError):
    """
    General HF error.
    """
    ErrorCode = 0x0001A007
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtHf"
class LT_ErrLtSnr(LTError):
    """
    Collision occurred.
    """
    ErrorCode = 0x0001A008
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtSnr"
class LT_ErrLtBitcount(LTError):
    """
    Wrong number of bits received from the transponder.
    """
    ErrorCode = 0x0001A00B
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtBitcount"
class LT_ErrLtFileov(LTError):
    """
    To many blocks written to file.
    """
    ErrorCode = 0x0001A00C
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtFileov"
class LT_ErrLtCom(LTError):
    """
    Communication error uC - reader chip.
    """
    ErrorCode = 0x0001A00D
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtCom"
class LT_ErrLtCmd(LTError):
    """
    Command syntax error.
    """
    ErrorCode = 0x0001A013
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtCmd"
class LT_ErrLtEepRead(LTError):
    """
    Error reading EEPROM of the reader.
    """
    ErrorCode = 0x0001A015
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtEepRead"
class LT_ErrLtEepWrite(LTError):
    """
    Error writing EEPROM of the reader.
    """
    ErrorCode = 0x0001A016
    URL = "https://docs.baltech.de/refman/cmds/lt/index.html#LT.ErrLtEepWrite"
FeatureID = Literal["GreenLed", "RedLed", "Beeper", "Relay", "MHz13", "Khz125", "Iso14443A", "Iso14443AUidOnly", "Iso14443B", "Iso14443BUidOnly", "Iso15693", "Iso15693UidOnly", "Felica", "FelicaUidOnly", "Legic", "Sam", "SamAv2", "SamHid", "Picopass", "MifareClassic", "MifarePlusEv0", "MifareDESFireEv1", "Srix", "Jewel", "ISO14443L4", "InterIndustry", "EM4205", "EM4100", "EM4450", "FarpointePyramid", "HidProx32", "HidAwid", "HidProx", "HidIoProx", "Indala", "Keri", "IndalaSecure", "Quadrakey", "SecuraKey", "GProx", "Hitag1S", "Hitag2M", "Hitag2B", "BlueLed", "Cotag", "PicopassUidOnly", "IdTeck", "Tamper", "MaxHfBaudrate106kbps", "MaxHfBaudrate212kbps", "MaxHfBaudrate424kbps", "FirmwareLoader", "FwUploadViaBrpOverSer", "AesHostProtocolEncryption", "PkiHostProtocolEncryption", "HidIClass", "HidIClassSr", "HidIClassSeAndSeos", "MifareUltralight", "CardEmulationISO14443L4", "MifareDESFireEv2", "MifarePlusEv1", "SamAv3", "OsdpV217", "Bluetooth", "RgbLed", "RgbLedLimited", "Bec2Upload", "MifareDESFireEv3", "MobileId", "MobileCardEmulation", "BleHci", "BlePeripheral", "undefined"]
FeatureID_Parser = LiteralParser[FeatureID, int](
    name='FeatureID',
    literal_map={
        'GreenLed': 1,
        'RedLed': 2,
        'Beeper': 3,
        'Relay': 4,
        'MHz13': 5,
        'Khz125': 6,
        'Iso14443A': 7,
        'Iso14443AUidOnly': 8,
        'Iso14443B': 9,
        'Iso14443BUidOnly': 10,
        'Iso15693': 11,
        'Iso15693UidOnly': 12,
        'Felica': 13,
        'FelicaUidOnly': 14,
        'Legic': 15,
        'Sam': 16,
        'SamAv2': 17,
        'SamHid': 18,
        'Picopass': 19,
        'MifareClassic': 35,
        'MifarePlusEv0': 36,
        'MifareDESFireEv1': 37,
        'Srix': 38,
        'Jewel': 39,
        'ISO14443L4': 40,
        'InterIndustry': 41,
        'EM4205': 42,
        'EM4100': 43,
        'EM4450': 44,
        'FarpointePyramid': 45,
        'HidProx32': 46,
        'HidAwid': 47,
        'HidProx': 48,
        'HidIoProx': 49,
        'Indala': 50,
        'Keri': 51,
        'IndalaSecure': 52,
        'Quadrakey': 53,
        'SecuraKey': 54,
        'GProx': 55,
        'Hitag1S': 56,
        'Hitag2M': 57,
        'Hitag2B': 58,
        'BlueLed': 59,
        'Cotag': 60,
        'PicopassUidOnly': 61,
        'IdTeck': 62,
        'Tamper': 63,
        'MaxHfBaudrate106kbps': 64,
        'MaxHfBaudrate212kbps': 65,
        'MaxHfBaudrate424kbps': 66,
        'FirmwareLoader': 67,
        'FwUploadViaBrpOverSer': 68,
        'AesHostProtocolEncryption': 69,
        'PkiHostProtocolEncryption': 70,
        'HidIClass': 71,
        'HidIClassSr': 72,
        'HidIClassSeAndSeos': 73,
        'MifareUltralight': 74,
        'CardEmulationISO14443L4': 75,
        'MifareDESFireEv2': 76,
        'MifarePlusEv1': 77,
        'SamAv3': 78,
        'OsdpV217': 79,
        'Bluetooth': 80,
        'RgbLed': 81,
        'RgbLedLimited': 82,
        'Bec2Upload': 83,
        'MifareDESFireEv3': 84,
        'MobileId': 85,
        'MobileCardEmulation': 86,
        'BleHci': 87,
        'BlePeripheral': 88,
        'undefined': -1,
    },
    undefined_literal='undefined',
)
class Protocols_KeyboardEmulation_ScancodesMap_Value_Entry(NamedTuple):
    AsciiCode: 'int'
    ScanCode: 'int'
    Shift: 'bool'
    Ctrl: 'bool'
    AltGr: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'AsciiCode={ repr(self.AsciiCode) }')
        non_default_args.append(f'ScanCode={ repr(self.ScanCode) }')
        non_default_args.append(f'Shift={ repr(self.Shift) }')
        non_default_args.append(f'Ctrl={ repr(self.Ctrl) }')
        non_default_args.append(f'AltGr={ repr(self.AltGr) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Mif_SetFraming_CommMode = Literal["MifareNative", "MifareISO"]
Mif_SetFraming_CommMode_Parser = LiteralParser[Mif_SetFraming_CommMode, int](
    name='Mif_SetFraming_CommMode',
    literal_map={
        'MifareNative': 1,
        'MifareISO': 2,
    },
)
class MifareClassicVhlKeyAssignment(NamedTuple):
    """
    This bitmask can be combined with a reference to a key index in the readers
    keylist and specifies more details.
    """
    Secure: 'bool'
    KeyB: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Secure={ repr(self.Secure) }')
        non_default_args.append(f'KeyB={ repr(self.KeyB) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class MifareClassicVhlKeyAssignment_Dict(TypedDict):
    """
    This bitmask can be combined with a reference to a key index in the readers
    keylist and specifies more details.
    """
    Secure: 'NotRequired[bool]'
    KeyB: 'NotRequired[bool]'
class VhlCfg_File_MifarePlusFormatOriginalKeyIdx_Value_Entry(NamedTuple):
    """
    Every entry is build of a 1 byte Bool and a 2 byte key index.
    """
    FormatWithKeyB: 'bool'
    OriginalKeyMemoryType: 'MifarePlusKeyMemoryType'
    OriginalKeyIdx: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FormatWithKeyB={ repr(self.FormatWithKeyB) }')
        non_default_args.append(f'OriginalKeyMemoryType={ repr(self.OriginalKeyMemoryType) }')
        non_default_args.append(f'OriginalKeyIdx={ repr(self.OriginalKeyIdx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
DesfireKeyIdx = int
Autoread_Rule_OnMatchAction_Action = Literal["AcceptCard", "DenyCard"]
Autoread_Rule_OnMatchAction_Action_Parser = LiteralParser[Autoread_Rule_OnMatchAction_Action, int](
    name='Autoread_Rule_OnMatchAction_Action',
    literal_map={
        'AcceptCard': 0,
        'DenyCard': 1,
    },
)
class VirtualLedDefinition_Mode(NamedTuple):
    """
    This byte is required to enable additional fields for the characterization of
    the desired LED behavior.
    """
    ContainsTransitionTime: 'bool'
    IsPulse: 'bool'
    ContainsPhysicalLedSelection: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ContainsTransitionTime={ repr(self.ContainsTransitionTime) }')
        non_default_args.append(f'IsPulse={ repr(self.IsPulse) }')
        non_default_args.append(f'ContainsPhysicalLedSelection={ repr(self.ContainsPhysicalLedSelection) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VirtualLedDefinition_Mode_Dict(TypedDict):
    """
    This byte is required to enable additional fields for the characterization of
    the desired LED behavior.
    """
    ContainsTransitionTime: 'NotRequired[bool]'
    IsPulse: 'NotRequired[bool]'
    ContainsPhysicalLedSelection: 'NotRequired[bool]'
class LedBitMask(NamedTuple):
    """
    A bitmask containing the physical LEDs you want to switch.
    """
    LeftLed: 'bool'
    RightLed: 'bool'
    SingleLed: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'LeftLed={ repr(self.LeftLed) }')
        non_default_args.append(f'RightLed={ repr(self.RightLed) }')
        non_default_args.append(f'SingleLed={ repr(self.SingleLed) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LedBitMask_Dict(TypedDict):
    """
    A bitmask containing the physical LEDs you want to switch.
    """
    LeftLed: 'NotRequired[bool]'
    RightLed: 'NotRequired[bool]'
    SingleLed: 'NotRequired[bool]'
DesfireFileDescription_FileCommunicationSecurity = Literal["Plain", "Mac", "Encrypted"]
DesfireFileDescription_FileCommunicationSecurity_Parser = LiteralParser[DesfireFileDescription_FileCommunicationSecurity, int](
    name='DesfireFileDescription_FileCommunicationSecurity',
    literal_map={
        'Plain': 0,
        'Mac': 1,
        'Encrypted': 3,
    },
)
class Iso14b_Request_ValueList_Entry(NamedTuple):
    PUPI: 'bytes'
    AppData: 'bytes'
    Synced: 'int'
    Send848: 'int'
    Send424: 'int'
    Send212: 'int'
    Recv848: 'int'
    Recv424: 'int'
    Recv212: 'int'
    FSCI: 'FSCI'
    ProtType: 'ProtType'
    FWI: 'FWI'
    ADC: 'int'
    NAD: 'int'
    CID: 'int'
    SFGI: 'Optional[SFGI]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'PUPI={ repr(self.PUPI) }')
        non_default_args.append(f'AppData={ repr(self.AppData) }')
        non_default_args.append(f'Synced={ repr(self.Synced) }')
        non_default_args.append(f'Send848={ repr(self.Send848) }')
        non_default_args.append(f'Send424={ repr(self.Send424) }')
        non_default_args.append(f'Send212={ repr(self.Send212) }')
        non_default_args.append(f'Recv848={ repr(self.Recv848) }')
        non_default_args.append(f'Recv424={ repr(self.Recv424) }')
        non_default_args.append(f'Recv212={ repr(self.Recv212) }')
        non_default_args.append(f'FSCI={ repr(self.FSCI) }')
        non_default_args.append(f'ProtType={ repr(self.ProtType) }')
        non_default_args.append(f'FWI={ repr(self.FWI) }')
        non_default_args.append(f'ADC={ repr(self.ADC) }')
        non_default_args.append(f'NAD={ repr(self.NAD) }')
        non_default_args.append(f'CID={ repr(self.CID) }')
        if self.SFGI != None:
            non_default_args.append(f'SFGI={ repr(self.SFGI) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_Network_RecoveryPointStatus_Value = Literal["RecoveryPointSet", "RecoveryPointRestored"]
Protocols_Network_RecoveryPointStatus_Value_Parser = LiteralParser[Protocols_Network_RecoveryPointStatus_Value, int](
    name='Protocols_Network_RecoveryPointStatus_Value',
    literal_map={
        'RecoveryPointSet': 1,
        'RecoveryPointRestored': 2,
    },
)
Protocols_Osdp_SecureInstallMode_Value = Literal["Insecure", "Install", "Secure", "SecureInstall", "V1"]
Protocols_Osdp_SecureInstallMode_Value_Parser = LiteralParser[Protocols_Osdp_SecureInstallMode_Value, int](
    name='Protocols_Osdp_SecureInstallMode_Value',
    literal_map={
        'Insecure': 0,
        'Install': 1,
        'Secure': 2,
        'SecureInstall': 3,
        'V1': 4,
    },
)
Protocols_Network_DhcpMode_Value = Literal["Disabled", "Enabled", "Auto"]
Protocols_Network_DhcpMode_Value_Parser = LiteralParser[Protocols_Network_DhcpMode_Value, int](
    name='Protocols_Network_DhcpMode_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
        'Auto': 2,
    },
)
Protocols_Wiegand_PinMessageFormat_Value = Literal["MultiDigit", "SingleDigit", "SingleDigitWithBcc", "SingleDigitWithSwappedBcc", "SingleDigit4Bit"]
Protocols_Wiegand_PinMessageFormat_Value_Parser = LiteralParser[Protocols_Wiegand_PinMessageFormat_Value, int](
    name='Protocols_Wiegand_PinMessageFormat_Value',
    literal_map={
        'MultiDigit': 0,
        'SingleDigit': 1,
        'SingleDigitWithBcc': 2,
        'SingleDigitWithSwappedBcc': 3,
        'SingleDigit4Bit': 4,
    },
)
VhlCfg_File_IntIndOnReadSelectOnly_Value = Literal["False", "True"]
VhlCfg_File_IntIndOnReadSelectOnly_Value_Parser = LiteralParser[VhlCfg_File_IntIndOnReadSelectOnly_Value, int](
    name='VhlCfg_File_IntIndOnReadSelectOnly_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
class VhlCfg_File_LegicApplicationSegmentList_Value_Entry(NamedTuple):
    SegmentIdAndAdr: 'SegmentIdentificationAndAddressing'
    SegmentInformation: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SegmentIdAndAdr={ repr(self.SegmentIdAndAdr) }')
        non_default_args.append(f'SegmentInformation={ repr(self.SegmentInformation) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Project_VhlSettings125Khz_PyramidSerialNrFormat_Value = Literal["BaltechStandard", "MXCompatible"]
Project_VhlSettings125Khz_PyramidSerialNrFormat_Value_Parser = LiteralParser[Project_VhlSettings125Khz_PyramidSerialNrFormat_Value, int](
    name='Project_VhlSettings125Khz_PyramidSerialNrFormat_Value',
    literal_map={
        'BaltechStandard': 0,
        'MXCompatible': 1,
    },
)
class VhlCfg_File_IntIndFileDescList_Value_Entry(NamedTuple):
    FileSpecifier: 'FileType'
    FileId: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FileSpecifier={ repr(self.FileSpecifier) }')
        non_default_args.append(f'FileId={ repr(self.FileId) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Desfire_ChangeKey_CurKeyDivMode = Literal["SamAv1OneRound", "SamAv1TwoRounds", "SamAv2"]
Desfire_ChangeKey_CurKeyDivMode_Parser = LiteralParser[Desfire_ChangeKey_CurKeyDivMode, int](
    name='Desfire_ChangeKey_CurKeyDivMode',
    literal_map={
        'SamAv1OneRound': 0,
        'SamAv1TwoRounds': 1,
        'SamAv2': 2,
    },
)
DHWCtrl_HfAcquire_ModuleId = Literal["No", "RC", "Legic", "PN", "LegicAdvant", "RC125", "PN2", "RC663", "HTRC110"]
DHWCtrl_HfAcquire_ModuleId_Parser = LiteralParser[DHWCtrl_HfAcquire_ModuleId, int](
    name='DHWCtrl_HfAcquire_ModuleId',
    literal_map={
        'No': 0,
        'RC': 1,
        'Legic': 3,
        'PN': 17,
        'LegicAdvant': 19,
        'RC125': 24,
        'PN2': 26,
        'RC663': 34,
        'HTRC110': 36,
    },
)
AutoReadMode = Literal["Disabled", "Enabled", "EnableOnce", "EnableIfDefinedRules"]
AutoReadMode_Parser = LiteralParser[AutoReadMode, int](
    name='AutoReadMode',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
        'EnableOnce': 2,
        'EnableIfDefinedRules': 255,
    },
)
Protocols_KeyboardEmulation_RegisterInterface_Value = Literal["AutoDetect", "Disabled", "Enabled"]
Protocols_KeyboardEmulation_RegisterInterface_Value_Parser = LiteralParser[Protocols_KeyboardEmulation_RegisterInterface_Value, int](
    name='Protocols_KeyboardEmulation_RegisterInterface_Value',
    literal_map={
        'AutoDetect': 0,
        'Disabled': 1,
        'Enabled': 2,
    },
)
Felica_Request_FastBaud = Literal["Kbps212", "Kbps424"]
Felica_Request_FastBaud_Parser = LiteralParser[Felica_Request_FastBaud, int](
    name='Felica_Request_FastBaud',
    literal_map={
        'Kbps212': 0,
        'Kbps424': 1,
    },
)
Project_VhlSettings125Khz_HidProxSerialNrFormat_Value = Literal["NoConversion", "WithParityBits", "McmCompatible", "CardNumberRightAdjusted", "CardNumberLeftAdjusted"]
Project_VhlSettings125Khz_HidProxSerialNrFormat_Value_Parser = LiteralParser[Project_VhlSettings125Khz_HidProxSerialNrFormat_Value, int](
    name='Project_VhlSettings125Khz_HidProxSerialNrFormat_Value',
    literal_map={
        'NoConversion': 0,
        'WithParityBits': 1,
        'McmCompatible': 2,
        'CardNumberRightAdjusted': 3,
        'CardNumberLeftAdjusted': 4,
    },
)
DesfireFileDescription_FileType = Literal["Standard", "Backup", "BackupManualCommit"]
DesfireFileDescription_FileType_Parser = LiteralParser[DesfireFileDescription_FileType, int](
    name='DesfireFileDescription_FileType',
    literal_map={
        'Standard': 0,
        'Backup': 1,
        'BackupManualCommit': 2,
    },
)
class SegmentIdentificationAndAddressing(NamedTuple):
    """
    This byte defines how a Legic segment shall be accessed.
    
    There are two possibilities to select a certain segment on a Legic card:
    
      * ID: The reader selects the segment with the desired number. 
      * Stamp: The reader selects the first segment that matches the desired stamp. 
    
    **If possible always stamp search should be used for segment identification to
    guarantee that only genuine cards are processed!**
    
    Legic advant compatible readers support two addressing modes:
    
      * Protocol Header: Stamp data (read-only) can be accessed starting with address 18 (data below address 18 is undefined). Application data follows directly after the stamp. 
      * Advant: Application data stored in S_DATA can be accessed starting with address 0. Stamp data is not accessible in this case.
    """
    AdvantAddressMode: 'bool'
    StampSearch: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'AdvantAddressMode={ repr(self.AdvantAddressMode) }')
        non_default_args.append(f'StampSearch={ repr(self.StampSearch) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class SegmentIdentificationAndAddressing_Dict(TypedDict):
    """
    This byte defines how a Legic segment shall be accessed.
    
    There are two possibilities to select a certain segment on a Legic card:
    
      * ID: The reader selects the segment with the desired number. 
      * Stamp: The reader selects the first segment that matches the desired stamp. 
    
    **If possible always stamp search should be used for segment identification to
    guarantee that only genuine cards are processed!**
    
    Legic advant compatible readers support two addressing modes:
    
      * Protocol Header: Stamp data (read-only) can be accessed starting with address 18 (data below address 18 is undefined). Application data follows directly after the stamp. 
      * Advant: Application data stored in S_DATA can be accessed starting with address 0. Stamp data is not accessible in this case.
    """
    AdvantAddressMode: 'NotRequired[bool]'
    StampSearch: 'NotRequired[bool]'
Protocols_Wiegand_BitOrder_Value = Literal["LsbFirst", "MsbFirst"]
Protocols_Wiegand_BitOrder_Value_Parser = LiteralParser[Protocols_Wiegand_BitOrder_Value, int](
    name='Protocols_Wiegand_BitOrder_Value',
    literal_map={
        'LsbFirst': 255,
        'MsbFirst': 0,
    },
)
Protocols_Osdp_DataMode_Value = Literal["Ascii", "BitstreamRaw", "BitstreamWiegand"]
Protocols_Osdp_DataMode_Value_Parser = LiteralParser[Protocols_Osdp_DataMode_Value, int](
    name='Protocols_Osdp_DataMode_Value',
    literal_map={
        'Ascii': 0,
        'BitstreamRaw': 1,
        'BitstreamWiegand': 2,
    },
)
class VhlCfg_File_MifarePlusKeyAssignment_Value_Entry(NamedTuple):
    WriteWithKeyB: 'bool'
    ReadWithKeyB: 'bool'
    KeyAMemoryType: 'MifarePlusKeyMemoryType'
    KeyAIdx: 'int'
    KeyBMemoryType: 'MifarePlusKeyMemoryType'
    KeyBIdx: 'int'
    ACBytes: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'WriteWithKeyB={ repr(self.WriteWithKeyB) }')
        non_default_args.append(f'ReadWithKeyB={ repr(self.ReadWithKeyB) }')
        non_default_args.append(f'KeyAMemoryType={ repr(self.KeyAMemoryType) }')
        non_default_args.append(f'KeyAIdx={ repr(self.KeyAIdx) }')
        non_default_args.append(f'KeyBMemoryType={ repr(self.KeyBMemoryType) }')
        non_default_args.append(f'KeyBIdx={ repr(self.KeyBIdx) }')
        non_default_args.append(f'ACBytes={ repr(self.ACBytes) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_GetBootStatus_BootStatus(NamedTuple):
    NewerReaderChipFirmware: 'bool'
    UnexpectedRebootsLegacy: 'bool'
    FactorySettings: 'bool'
    ConfigurationInconsistent: 'bool'
    FirmwareVersionBlocked: 'bool'
    Bluetooth: 'bool'
    WiFi: 'bool'
    Tamper: 'bool'
    BatteryManagement: 'bool'
    Keyboard: 'bool'
    FirmwareVersionBlockedLegacy: 'bool'
    Display: 'bool'
    ConfCardPresented: 'bool'
    Ethernet: 'bool'
    ExtendedLED: 'bool'
    Rf125kHz: 'bool'
    Rf13MHz: 'bool'
    Rf13MHzLegic: 'bool'
    Rf13MHzLegacy: 'bool'
    HWoptions: 'bool'
    RTC: 'bool'
    Dataflash: 'bool'
    Configuration: 'bool'
    CorruptFirmware: 'bool'
    IncompleteFirmware: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'NewerReaderChipFirmware={ repr(self.NewerReaderChipFirmware) }')
        non_default_args.append(f'UnexpectedRebootsLegacy={ repr(self.UnexpectedRebootsLegacy) }')
        non_default_args.append(f'FactorySettings={ repr(self.FactorySettings) }')
        non_default_args.append(f'ConfigurationInconsistent={ repr(self.ConfigurationInconsistent) }')
        non_default_args.append(f'FirmwareVersionBlocked={ repr(self.FirmwareVersionBlocked) }')
        non_default_args.append(f'Bluetooth={ repr(self.Bluetooth) }')
        non_default_args.append(f'WiFi={ repr(self.WiFi) }')
        non_default_args.append(f'Tamper={ repr(self.Tamper) }')
        non_default_args.append(f'BatteryManagement={ repr(self.BatteryManagement) }')
        non_default_args.append(f'Keyboard={ repr(self.Keyboard) }')
        non_default_args.append(f'FirmwareVersionBlockedLegacy={ repr(self.FirmwareVersionBlockedLegacy) }')
        non_default_args.append(f'Display={ repr(self.Display) }')
        non_default_args.append(f'ConfCardPresented={ repr(self.ConfCardPresented) }')
        non_default_args.append(f'Ethernet={ repr(self.Ethernet) }')
        non_default_args.append(f'ExtendedLED={ repr(self.ExtendedLED) }')
        non_default_args.append(f'Rf125kHz={ repr(self.Rf125kHz) }')
        non_default_args.append(f'Rf13MHz={ repr(self.Rf13MHz) }')
        non_default_args.append(f'Rf13MHzLegic={ repr(self.Rf13MHzLegic) }')
        non_default_args.append(f'Rf13MHzLegacy={ repr(self.Rf13MHzLegacy) }')
        non_default_args.append(f'HWoptions={ repr(self.HWoptions) }')
        non_default_args.append(f'RTC={ repr(self.RTC) }')
        non_default_args.append(f'Dataflash={ repr(self.Dataflash) }')
        non_default_args.append(f'Configuration={ repr(self.Configuration) }')
        non_default_args.append(f'CorruptFirmware={ repr(self.CorruptFirmware) }')
        non_default_args.append(f'IncompleteFirmware={ repr(self.IncompleteFirmware) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Sys_GetBootStatus_BootStatus_Dict(TypedDict):
    NewerReaderChipFirmware: 'NotRequired[bool]'
    UnexpectedRebootsLegacy: 'NotRequired[bool]'
    FactorySettings: 'NotRequired[bool]'
    ConfigurationInconsistent: 'NotRequired[bool]'
    FirmwareVersionBlocked: 'NotRequired[bool]'
    Bluetooth: 'NotRequired[bool]'
    WiFi: 'NotRequired[bool]'
    Tamper: 'NotRequired[bool]'
    BatteryManagement: 'NotRequired[bool]'
    Keyboard: 'NotRequired[bool]'
    FirmwareVersionBlockedLegacy: 'NotRequired[bool]'
    Display: 'NotRequired[bool]'
    ConfCardPresented: 'NotRequired[bool]'
    Ethernet: 'NotRequired[bool]'
    ExtendedLED: 'NotRequired[bool]'
    Rf125kHz: 'NotRequired[bool]'
    Rf13MHz: 'NotRequired[bool]'
    Rf13MHzLegic: 'NotRequired[bool]'
    Rf13MHzLegacy: 'NotRequired[bool]'
    HWoptions: 'NotRequired[bool]'
    RTC: 'NotRequired[bool]'
    Dataflash: 'NotRequired[bool]'
    Configuration: 'NotRequired[bool]'
    CorruptFirmware: 'NotRequired[bool]'
    IncompleteFirmware: 'NotRequired[bool]'
Protocols_Network_ResolverEnable_Value = Literal["Yes", "No"]
Protocols_Network_ResolverEnable_Value_Parser = LiteralParser[Protocols_Network_ResolverEnable_Value, int](
    name='Protocols_Network_ResolverEnable_Value',
    literal_map={
        'Yes': 1,
        'No': 0,
    },
)
Autoread_Rule_PrioritizationMode_PrioMode = Literal["NoPrio", "PrioReturnInOrder", "PrioSuppressOthers"]
Autoread_Rule_PrioritizationMode_PrioMode_Parser = LiteralParser[Autoread_Rule_PrioritizationMode_PrioMode, int](
    name='Autoread_Rule_PrioritizationMode_PrioMode',
    literal_map={
        'NoPrio': 0,
        'PrioReturnInOrder': 1,
        'PrioSuppressOthers': 2,
    },
)
Device_Run_AccessRightsOfBAC_Value = Literal["Disabled", "ReadOnly", "EnabledOnTamper", "Enabled"]
Device_Run_AccessRightsOfBAC_Value_Parser = LiteralParser[Device_Run_AccessRightsOfBAC_Value, int](
    name='Device_Run_AccessRightsOfBAC_Value',
    literal_map={
        'Disabled': 0,
        'ReadOnly': 1,
        'EnabledOnTamper': 2,
        'Enabled': 3,
    },
)
Project_VhlSettings125Khz_TTFBaudrate_TTFBaud = Literal["Baud32", "Baud64"]
Project_VhlSettings125Khz_TTFBaudrate_TTFBaud_Parser = LiteralParser[Project_VhlSettings125Khz_TTFBaudrate_TTFBaud, int](
    name='Project_VhlSettings125Khz_TTFBaudrate_TTFBaud',
    literal_map={
        'Baud32': 32,
        'Baud64': 64,
    },
)
VhlCfg_File_DesfireEv2FormatAppKeysetParams_MaxKeySize = Literal["Len16", "Len24"]
VhlCfg_File_DesfireEv2FormatAppKeysetParams_MaxKeySize_Parser = LiteralParser[VhlCfg_File_DesfireEv2FormatAppKeysetParams_MaxKeySize, int](
    name='VhlCfg_File_DesfireEv2FormatAppKeysetParams_MaxKeySize',
    literal_map={
        'Len16': 16,
        'Len24': 24,
    },
)
Protocols_KeyboardEmulation_UsbInterfaceOrder_Value = Literal["First", "Second"]
Protocols_KeyboardEmulation_UsbInterfaceOrder_Value_Parser = LiteralParser[Protocols_KeyboardEmulation_UsbInterfaceOrder_Value, int](
    name='Protocols_KeyboardEmulation_UsbInterfaceOrder_Value',
    literal_map={
        'First': 0,
        'Second': 1,
    },
)
Device_Run_UsbSuspendMode_SuspendMode = Literal["Disabled", "Enabled"]
Device_Run_UsbSuspendMode_SuspendMode_Parser = LiteralParser[Device_Run_UsbSuspendMode_SuspendMode, int](
    name='Device_Run_UsbSuspendMode_SuspendMode',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
Protocols_Network_SlpUseBroadcast_Value = Literal["Yes", "No"]
Protocols_Network_SlpUseBroadcast_Value_Parser = LiteralParser[Protocols_Network_SlpUseBroadcast_Value, int](
    name='Protocols_Network_SlpUseBroadcast_Value',
    literal_map={
        'Yes': 1,
        'No': 0,
    },
)
Felica_GenericCmd_FastBaud = Literal["Kbps212", "Kbps424"]
Felica_GenericCmd_FastBaud_Parser = LiteralParser[Felica_GenericCmd_FastBaud, int](
    name='Felica_GenericCmd_FastBaud',
    literal_map={
        'Kbps212': 0,
        'Kbps424': 1,
    },
)
CardType = Literal["Default", "MifareClassic", "Iso14443aGeneric", "Iso14443aInterIndustry", "MifareUltraLight", "MifareDesfire", "InfineonSle55", "Iso14443aIntIndustryMif", "MifarePlusL2", "LEGICAdvantIso14443a", "MifarePlusL3", "LEGICPrimeLegacy", "LEGICAdvantLegacy", "Iso15693", "LEGICAdvantIso15693", "Iso14443bUnknown", "Iso14443bIntIndustry", "IClassIso14B", "IClassIso14B2", "IClass", "Felica", "EM4205", "EM4100", "EM4450", "Pyramid", "HidProx32", "Keri", "Quadrakey", "HidIndala", "HidAwid", "HidProx", "HidIoprox", "Hitag1S", "Hitag2M", "Hitag2B", "TTF", "STSRIX", "SecuraKey", "GProx", "HidIndalaSecure", "Cotag", "Idteck", "BluetoothMce", "LEGICPrime", "HidSio", "Fido", "Piv", "undefined"]
CardType_Parser = LiteralParser[CardType, int](
    name='CardType',
    literal_map={
        'Default': 0,
        'MifareClassic': 16,
        'Iso14443aGeneric': 17,
        'Iso14443aInterIndustry': 18,
        'MifareUltraLight': 19,
        'MifareDesfire': 20,
        'InfineonSle55': 21,
        'Iso14443aIntIndustryMif': 22,
        'MifarePlusL2': 23,
        'LEGICAdvantIso14443a': 24,
        'MifarePlusL3': 25,
        'LEGICPrimeLegacy': 32,
        'LEGICAdvantLegacy': 33,
        'Iso15693': 48,
        'LEGICAdvantIso15693': 50,
        'Iso14443bUnknown': 64,
        'Iso14443bIntIndustry': 65,
        'IClassIso14B': 66,
        'IClassIso14B2': 80,
        'IClass': 96,
        'Felica': 112,
        'EM4205': 128,
        'EM4100': 129,
        'EM4450': 131,
        'Pyramid': 132,
        'HidProx32': 133,
        'Keri': 134,
        'Quadrakey': 135,
        'HidIndala': 136,
        'HidAwid': 137,
        'HidProx': 138,
        'HidIoprox': 139,
        'Hitag1S': 140,
        'Hitag2M': 141,
        'Hitag2B': 142,
        'TTF': 143,
        'STSRIX': 144,
        'SecuraKey': 160,
        'GProx': 161,
        'HidIndalaSecure': 162,
        'Cotag': 163,
        'Idteck': 164,
        'BluetoothMce': 176,
        'LEGICPrime': 192,
        'HidSio': 224,
        'Fido': 228,
        'Piv': 229,
        'undefined': -1,
    },
    undefined_literal='undefined',
)
class Sys_GetStatistics_CounterTuple_Entry(NamedTuple):
    ID: 'int'
    Value: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ID={ repr(self.ID) }')
        non_default_args.append(f'Value={ repr(self.Value) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Iso14L4_SetupAPDU_FSCI = Literal["Bytes16", "Bytes24", "Bytes32", "Bytes40", "Bytes48", "Bytes64", "Bytes96", "Bytes128", "Bytes256"]
Iso14L4_SetupAPDU_FSCI_Parser = LiteralParser[Iso14L4_SetupAPDU_FSCI, int](
    name='Iso14L4_SetupAPDU_FSCI',
    literal_map={
        'Bytes16': 0,
        'Bytes24': 1,
        'Bytes32': 2,
        'Bytes40': 3,
        'Bytes48': 4,
        'Bytes64': 5,
        'Bytes96': 6,
        'Bytes128': 7,
        'Bytes256': 8,
    },
)
VhlCfg_File_Iso15WriteOptFlag_Value = Literal["WriteOptFlagZero", "WriteOptFlagOne", "WriteOptFlagAuto"]
VhlCfg_File_Iso15WriteOptFlag_Value_Parser = LiteralParser[VhlCfg_File_Iso15WriteOptFlag_Value, int](
    name='VhlCfg_File_Iso15WriteOptFlag_Value',
    literal_map={
        'WriteOptFlagZero': 0,
        'WriteOptFlagOne': 1,
        'WriteOptFlagAuto': 2,
    },
)
Desfire_SetFraming_CommMode = Literal["DESFireNative", "ISO7816Compatible"]
Desfire_SetFraming_CommMode_Parser = LiteralParser[Desfire_SetFraming_CommMode, int](
    name='Desfire_SetFraming_CommMode',
    literal_map={
        'DESFireNative': 1,
        'ISO7816Compatible': 2,
    },
)
Time = int
Protocols_Network_LinkLocalMode_Value = Literal["Disabled", "Enabled", "Auto"]
Protocols_Network_LinkLocalMode_Value_Parser = LiteralParser[Protocols_Network_LinkLocalMode_Value, int](
    name='Protocols_Network_LinkLocalMode_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
        'Auto': 2,
    },
)
class VirtualLedDefinition(NamedTuple):
    Mode: 'VirtualLedDefinition_Mode'
    RgbColor: 'int'
    PhysicalLedSelection: 'Optional[VirtualLedDefinition_PhysicalLedSelection]' = None
    RgbColor2: 'Optional[int]' = None
    TransitionTime: 'Optional[int]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Mode={ repr(self.Mode) }')
        non_default_args.append(f'RgbColor={ repr(self.RgbColor) }')
        if self.PhysicalLedSelection != None:
            non_default_args.append(f'PhysicalLedSelection={ repr(self.PhysicalLedSelection) }')
        if self.RgbColor2 != None:
            non_default_args.append(f'RgbColor2={ repr(self.RgbColor2) }')
        if self.TransitionTime != None:
            non_default_args.append(f'TransitionTime={ repr(self.TransitionTime) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VirtualLedDefinition_Dict(TypedDict):
    Mode: 'VirtualLedDefinition_Mode'
    RgbColor: 'NotRequired[int]'
    PhysicalLedSelection: 'NotRequired[VirtualLedDefinition_PhysicalLedSelection]'
    RgbColor2: 'NotRequired[int]'
    TransitionTime: 'NotRequired[int]'
Protocols_Ccid_InterfaceMode_Value = Literal["Autodetect", "Single", "Compound"]
Protocols_Ccid_InterfaceMode_Value_Parser = LiteralParser[Protocols_Ccid_InterfaceMode_Value, int](
    name='Protocols_Ccid_InterfaceMode_Value',
    literal_map={
        'Autodetect': 0,
        'Single': 1,
        'Compound': 2,
    },
)
DHWCtrl_AesEncrypt_WrappedKeyNr = Literal["WrapNone", "WrapDHUK"]
DHWCtrl_AesEncrypt_WrappedKeyNr_Parser = LiteralParser[DHWCtrl_AesEncrypt_WrappedKeyNr, int](
    name='DHWCtrl_AesEncrypt_WrappedKeyNr',
    literal_map={
        'WrapNone': 0,
        'WrapDHUK': 1,
    },
)
class VhlCfg_File_MifareKeyList_Value_Entry(NamedTuple):
    DenyTransferToSecureMemory: 'bool'
    DenyChangeKey: 'bool'
    DenyWrite: 'bool'
    DenyRead: 'bool'
    Key: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DenyTransferToSecureMemory={ repr(self.DenyTransferToSecureMemory) }')
        non_default_args.append(f'DenyChangeKey={ repr(self.DenyChangeKey) }')
        non_default_args.append(f'DenyWrite={ repr(self.DenyWrite) }')
        non_default_args.append(f'DenyRead={ repr(self.DenyRead) }')
        non_default_args.append(f'Key={ repr(self.Key) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Bat_Run_Rsps_Entry(NamedTuple):
    Status: 'int'
    Resp: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Status={ repr(self.Status) }')
        non_default_args.append(f'Resp={ repr(self.Resp) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LicenseBitMask(NamedTuple):
    """
    License bit mask
    """
    Ble: 'bool'
    BleLicRequired: 'bool'
    HidOnlyForSE: 'bool'
    Hid: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Ble={ repr(self.Ble) }')
        non_default_args.append(f'BleLicRequired={ repr(self.BleLicRequired) }')
        non_default_args.append(f'HidOnlyForSE={ repr(self.HidOnlyForSE) }')
        non_default_args.append(f'Hid={ repr(self.Hid) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class LicenseBitMask_Dict(TypedDict):
    """
    License bit mask
    """
    Ble: 'NotRequired[bool]'
    BleLicRequired: 'NotRequired[bool]'
    HidOnlyForSE: 'NotRequired[bool]'
    Hid: 'NotRequired[bool]'
VHL_Setup_AdrMode = Literal["ProtocolHeader", "Advant"]
VHL_Setup_AdrMode_Parser = LiteralParser[VHL_Setup_AdrMode, int](
    name='VHL_Setup_AdrMode',
    literal_map={
        'ProtocolHeader': 0,
        'Advant': 1,
    },
)
VhlCfg_File_MifareClassicFormatOriginalKeyList_AuthenticationKeyAssignment = Literal["UseKeyA", "UseKeyB"]
VhlCfg_File_MifareClassicFormatOriginalKeyList_AuthenticationKeyAssignment_Parser = LiteralParser[VhlCfg_File_MifareClassicFormatOriginalKeyList_AuthenticationKeyAssignment, int](
    name='VhlCfg_File_MifareClassicFormatOriginalKeyList_AuthenticationKeyAssignment',
    literal_map={
        'UseKeyA': 0,
        'UseKeyB': 1,
    },
)
DHWCtrl_GetReaderChipType_ChipType = Literal["RC500", "RC632", "RC663", "PN512"]
DHWCtrl_GetReaderChipType_ChipType_Parser = LiteralParser[DHWCtrl_GetReaderChipType_ChipType, int](
    name='DHWCtrl_GetReaderChipType_ChipType',
    literal_map={
        'RC500': 1,
        'RC632': 4,
        'RC663': 5,
        'PN512': 33,
    },
)
class CardFamilies(NamedTuple):
    LEGICPrime: 'bool' = False
    BluetoothMce: 'bool' = False
    Khz125Part2: 'bool' = False
    Srix: 'bool' = False
    Khz125Part1: 'bool' = False
    Felica: 'bool' = False
    IClass: 'bool' = False
    IClassIso14B: 'bool' = False
    Iso14443B: 'bool' = False
    Iso15693: 'bool' = False
    Iso14443A: 'bool' = False
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.LEGICPrime != False:
            non_default_args.append(f'LEGICPrime={ repr(self.LEGICPrime) }')
        if self.BluetoothMce != False:
            non_default_args.append(f'BluetoothMce={ repr(self.BluetoothMce) }')
        if self.Khz125Part2 != False:
            non_default_args.append(f'Khz125Part2={ repr(self.Khz125Part2) }')
        if self.Srix != False:
            non_default_args.append(f'Srix={ repr(self.Srix) }')
        if self.Khz125Part1 != False:
            non_default_args.append(f'Khz125Part1={ repr(self.Khz125Part1) }')
        if self.Felica != False:
            non_default_args.append(f'Felica={ repr(self.Felica) }')
        if self.IClass != False:
            non_default_args.append(f'IClass={ repr(self.IClass) }')
        if self.IClassIso14B != False:
            non_default_args.append(f'IClassIso14B={ repr(self.IClassIso14B) }')
        if self.Iso14443B != False:
            non_default_args.append(f'Iso14443B={ repr(self.Iso14443B) }')
        if self.Iso15693 != False:
            non_default_args.append(f'Iso15693={ repr(self.Iso15693) }')
        if self.Iso14443A != False:
            non_default_args.append(f'Iso14443A={ repr(self.Iso14443A) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
    @classmethod
    def All(cls, LEGICPrime: bool = True, BluetoothMce: bool = True, Khz125Part2: bool = True, Srix: bool = True, Khz125Part1: bool = True, Felica: bool = True, IClass: bool = True, IClassIso14B: bool = True, Iso14443B: bool = True, Iso15693: bool = True, Iso14443A: bool = True) -> Self:
        return cls(LEGICPrime, BluetoothMce, Khz125Part2, Srix, Khz125Part1, Felica, IClass, IClassIso14B, Iso14443B, Iso15693, Iso14443A)
    @classmethod
    def Khz125(cls, LEGICPrime: bool = False, BluetoothMce: bool = False, Khz125Part2: bool = True, Srix: bool = False, Khz125Part1: bool = True, Felica: bool = False, IClass: bool = False, IClassIso14B: bool = False, Iso14443B: bool = False, Iso15693: bool = False, Iso14443A: bool = False) -> Self:
        return cls(LEGICPrime, BluetoothMce, Khz125Part2, Srix, Khz125Part1, Felica, IClass, IClassIso14B, Iso14443B, Iso15693, Iso14443A)
class CardFamilies_Dict(TypedDict):
    LEGICPrime: 'NotRequired[bool]'
    BluetoothMce: 'NotRequired[bool]'
    Khz125Part2: 'NotRequired[bool]'
    Srix: 'NotRequired[bool]'
    Khz125Part1: 'NotRequired[bool]'
    Felica: 'NotRequired[bool]'
    IClass: 'NotRequired[bool]'
    IClassIso14B: 'NotRequired[bool]'
    Iso14443B: 'NotRequired[bool]'
    Iso15693: 'NotRequired[bool]'
    Iso14443A: 'NotRequired[bool]'
Protocols_Network_SlpEnable_Value = Literal["Yes", "No"]
Protocols_Network_SlpEnable_Value_Parser = LiteralParser[Protocols_Network_SlpEnable_Value, int](
    name='Protocols_Network_SlpEnable_Value',
    literal_map={
        'Yes': 1,
        'No': 0,
    },
)
DivisorInteger = Literal["Kbps106", "Kbps212", "Kbps424", "Kbps848"]
DivisorInteger_Parser = LiteralParser[DivisorInteger, int](
    name='DivisorInteger',
    literal_map={
        'Kbps106': 0,
        'Kbps212': 1,
        'Kbps424': 2,
        'Kbps848': 3,
    },
)
AutoRunCommand_RunMode = Literal["Standard", "Continuous", "Repeat"]
AutoRunCommand_RunMode_Parser = LiteralParser[AutoRunCommand_RunMode, int](
    name='AutoRunCommand_RunMode',
    literal_map={
        'Standard': 0,
        'Continuous': 1,
        'Repeat': 2,
    },
)
EpcUid_EpcSetMode_Coding = Literal["FM0", "Miller8", "Man2", "Man4"]
EpcUid_EpcSetMode_Coding_Parser = LiteralParser[EpcUid_EpcSetMode_Coding, int](
    name='EpcUid_EpcSetMode_Coding',
    literal_map={
        'FM0': 0,
        'Miller8': 1,
        'Man2': 2,
        'Man4': 3,
    },
)
Desfire_Authenticate_KeyDivMode = Literal["NoDiv", "SamAV1OneRound", "SamAV1TwoRounds", "SamAV2"]
Desfire_Authenticate_KeyDivMode_Parser = LiteralParser[Desfire_Authenticate_KeyDivMode, int](
    name='Desfire_Authenticate_KeyDivMode',
    literal_map={
        'NoDiv': 0,
        'SamAV1OneRound': 1,
        'SamAV1TwoRounds': 2,
        'SamAV2': 3,
    },
)
Project_MobileId_DetectionRssiFilter_Value = Literal["Disabled", "Enabled"]
Project_MobileId_DetectionRssiFilter_Value_Parser = LiteralParser[Project_MobileId_DetectionRssiFilter_Value, int](
    name='Project_MobileId_DetectionRssiFilter_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
DHWCtrl_GetSamType_ChipType = Literal["TDA8007C2", "TDA8007C3"]
DHWCtrl_GetSamType_ChipType_Parser = LiteralParser[DHWCtrl_GetSamType_ChipType, int](
    name='DHWCtrl_GetSamType_ChipType',
    literal_map={
        'TDA8007C2': 1,
        'TDA8007C3': 2,
    },
)
Project_SamAVx_SecureMessaging_Value = Literal["Plain", "Mac", "Encrypted"]
Project_SamAVx_SecureMessaging_Value_Parser = LiteralParser[Project_SamAVx_SecureMessaging_Value, int](
    name='Project_SamAVx_SecureMessaging_Value',
    literal_map={
        'Plain': 0,
        'Mac': 1,
        'Encrypted': 2,
    },
)
MifarePlusKeyMemoryType = Literal["CryptoKey", "SamKey", "ReaderChipKey", "VhlKey"]
MifarePlusKeyMemoryType_Parser = LiteralParser[MifarePlusKeyMemoryType, int](
    name='MifarePlusKeyMemoryType',
    literal_map={
        'CryptoKey': 0,
        'SamKey': 1,
        'ReaderChipKey': 2,
        'VhlKey': 3,
    },
)
class Project_SamAVxKeySettings_Index_KeySettingsList_Entry(NamedTuple):
    """
    This value consists of a list (array) with a maximum of 3 entries (for SamKey
    A / B / C). 8-bit key indexes refer automatically to entry 0, the MSB of a
    16-bit key index refers to entry 0..2.
    """
    KeyVersion: 'int'
    DiversificationMode: 'DiversificationMode'
    DivIdx: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'KeyVersion={ repr(self.KeyVersion) }')
        non_default_args.append(f'DiversificationMode={ repr(self.DiversificationMode) }')
        non_default_args.append(f'DivIdx={ repr(self.DivIdx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_Network_SlpPassiveDiscovery_Value = Literal["Disabled", "Enabled"]
Protocols_Network_SlpPassiveDiscovery_Value_Parser = LiteralParser[Protocols_Network_SlpPassiveDiscovery_Value, int](
    name='Protocols_Network_SlpPassiveDiscovery_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
Iso14b_Attrib_FSDI = Literal["Bytes16", "Bytes24", "Bytes32", "Bytes40", "Bytes48", "Bytes64", "Bytes96", "Bytes128", "Bytes256"]
Iso14b_Attrib_FSDI_Parser = LiteralParser[Iso14b_Attrib_FSDI, int](
    name='Iso14b_Attrib_FSDI',
    literal_map={
        'Bytes16': 0,
        'Bytes24': 1,
        'Bytes32': 2,
        'Bytes40': 3,
        'Bytes48': 4,
        'Bytes64': 5,
        'Bytes96': 6,
        'Bytes128': 7,
        'Bytes256': 8,
    },
)
class VhlCfg_File_MifareClassicFormatOriginalKeyList_Value_Entry(NamedTuple):
    """
    List of key entries
    """
    AuthenticationKeyAssignment: 'AuthenticationKeyAssignment'
    Key: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'AuthenticationKeyAssignment={ repr(self.AuthenticationKeyAssignment) }')
        non_default_args.append(f'Key={ repr(self.Key) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Iso14a_RequestLegacy_UIDSize = Literal["SingleSize", "DoubleSize", "TripleSize"]
Iso14a_RequestLegacy_UIDSize_Parser = LiteralParser[Iso14a_RequestLegacy_UIDSize, int](
    name='Iso14a_RequestLegacy_UIDSize',
    literal_map={
        'SingleSize': 0,
        'DoubleSize': 1,
        'TripleSize': 2,
    },
)
Main_Bf2Upload_ResultCode = Literal["Success", "InvalidChecksum", "ProgrammingTimeout", "VerifyTimeout", "UnsupportedCodeType", "ProtocolError", "SecuredByConfigSecurityCode", "undefined"]
Main_Bf2Upload_ResultCode_Parser = LiteralParser[Main_Bf2Upload_ResultCode, int](
    name='Main_Bf2Upload_ResultCode',
    literal_map={
        'Success': 0,
        'InvalidChecksum': 1,
        'ProgrammingTimeout': 2,
        'VerifyTimeout': 3,
        'UnsupportedCodeType': 4,
        'ProtocolError': 5,
        'SecuredByConfigSecurityCode': 6,
        'undefined': -1,
    },
    undefined_literal='undefined',
)
Project_Mce_Mode_Value = Literal["Disabled", "Enabled"]
Project_Mce_Mode_Value_Parser = LiteralParser[Project_Mce_Mode_Value, int](
    name='Project_Mce_Mode_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
VhlCfg_File_Iso15ReadCmd_Value = Literal["ReadAuto", "ReadMultipleBlocks", "ReadSingleBlock", "FastMultipleBlock26kbit", "FastMultipleBlock52kbit", "FastMultipleBlock105kbit", "FastMultipleBlock211kbit"]
VhlCfg_File_Iso15ReadCmd_Value_Parser = LiteralParser[VhlCfg_File_Iso15ReadCmd_Value, int](
    name='VhlCfg_File_Iso15ReadCmd_Value',
    literal_map={
        'ReadAuto': 0,
        'ReadMultipleBlocks': 1,
        'ReadSingleBlock': 2,
        'FastMultipleBlock26kbit': 4,
        'FastMultipleBlock52kbit': 5,
        'FastMultipleBlock105kbit': 6,
        'FastMultipleBlock211kbit': 7,
    },
)
Project_MobileId_AdvertisementFilter_Value = Literal["Disabled", "Enabled"]
Project_MobileId_AdvertisementFilter_Value_Parser = LiteralParser[Project_MobileId_AdvertisementFilter_Value, int](
    name='Project_MobileId_AdvertisementFilter_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
Project_Bluetooth_DiscoveryMode_Value = Literal["NonDiscoverable", "LimitedDiscoverable", "GeneralDiscoverable"]
Project_Bluetooth_DiscoveryMode_Value_Parser = LiteralParser[Project_Bluetooth_DiscoveryMode_Value, int](
    name='Project_Bluetooth_DiscoveryMode_Value',
    literal_map={
        'NonDiscoverable': 0,
        'LimitedDiscoverable': 1,
        'GeneralDiscoverable': 2,
    },
)
class VhlCfg_File_MifarePlusAesKeyList_Value_Entry(NamedTuple):
    DenyChangeKey: 'bool'
    DenyWrite: 'bool'
    DenyRead: 'bool'
    Key: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'DenyChangeKey={ repr(self.DenyChangeKey) }')
        non_default_args.append(f'DenyWrite={ repr(self.DenyWrite) }')
        non_default_args.append(f'DenyRead={ repr(self.DenyRead) }')
        non_default_args.append(f'Key={ repr(self.Key) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
VhlCfg_File_DesfireEv2FormatAppKeysetKeylist_KeysetType = Literal["TripleDESKey", "ThreeKeyTripleDESKey", "AESKey"]
VhlCfg_File_DesfireEv2FormatAppKeysetKeylist_KeysetType_Parser = LiteralParser[VhlCfg_File_DesfireEv2FormatAppKeysetKeylist_KeysetType, int](
    name='VhlCfg_File_DesfireEv2FormatAppKeysetKeylist_KeysetType',
    literal_map={
        'TripleDESKey': 0,
        'ThreeKeyTripleDESKey': 1,
        'AESKey': 2,
    },
)
Lg_SetPassword_PwdStat = Literal["Deactivated", "Activated", "AlreadySet"]
Lg_SetPassword_PwdStat_Parser = LiteralParser[Lg_SetPassword_PwdStat, int](
    name='Lg_SetPassword_PwdStat',
    literal_map={
        'Deactivated': 0,
        'Activated': 1,
        'AlreadySet': 2,
    },
)
Iso14b_Attrib_TR0 = Literal["Numerator64", "Numerator48", "Numerator16"]
Iso14b_Attrib_TR0_Parser = LiteralParser[Iso14b_Attrib_TR0, int](
    name='Iso14b_Attrib_TR0',
    literal_map={
        'Numerator64': 0,
        'Numerator48': 1,
        'Numerator16': 2,
    },
)
FSCI = Literal["Bytes16", "Bytes24", "Bytes32", "Bytes40", "Bytes48", "Bytes64", "Bytes96", "Bytes128", "Bytes256"]
FSCI_Parser = LiteralParser[FSCI, int](
    name='FSCI',
    literal_map={
        'Bytes16': 0,
        'Bytes24': 1,
        'Bytes32': 2,
        'Bytes40': 3,
        'Bytes48': 4,
        'Bytes64': 5,
        'Bytes96': 6,
        'Bytes128': 7,
        'Bytes256': 8,
    },
)
Eth_GetTcpConnectionStatus_Status = Literal["NotConnected", "ConnectionTrialRunning", "Connected"]
Eth_GetTcpConnectionStatus_Status_Parser = LiteralParser[Eth_GetTcpConnectionStatus_Status, int](
    name='Eth_GetTcpConnectionStatus_Status',
    literal_map={
        'NotConnected': 0,
        'ConnectionTrialRunning': 1,
        'Connected': 2,
    },
)
Desfire_ChangeKey_NewKeyDivMode = Literal["SamAv1OneRound", "SamAv1TwoRounds", "SamAv2"]
Desfire_ChangeKey_NewKeyDivMode_Parser = LiteralParser[Desfire_ChangeKey_NewKeyDivMode, int](
    name='Desfire_ChangeKey_NewKeyDivMode',
    literal_map={
        'SamAv1OneRound': 0,
        'SamAv1TwoRounds': 1,
        'SamAv2': 2,
    },
)
Iso14b_Request_TimeSlots = Literal["TimeSlots1", "TimeSlots2", "TimeSlots4", "TimeSlots8", "TimeSlots16"]
Iso14b_Request_TimeSlots_Parser = LiteralParser[Iso14b_Request_TimeSlots, int](
    name='Iso14b_Request_TimeSlots',
    literal_map={
        'TimeSlots1': 0,
        'TimeSlots2': 1,
        'TimeSlots4': 2,
        'TimeSlots8': 3,
        'TimeSlots16': 4,
    },
)
Project_MobileId_ConvenientAccess_Value = Literal["Disabled", "Enabled"]
Project_MobileId_ConvenientAccess_Value_Parser = LiteralParser[Project_MobileId_ConvenientAccess_Value, int](
    name='Project_MobileId_ConvenientAccess_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
class DesfireFileDescription(NamedTuple):
    FileNo: 'int' = 0
    FileCommunicationSecurity: 'DesfireFileDescription_FileCommunicationSecurity' = "Plain"
    FileType: 'DesfireFileDescription_FileType' = "Standard"
    ReadKeyNo: 'int' = 0
    WriteKeyNo: 'int' = 0
    Offset: 'int' = 0
    Length: 'int' = 32767
    ReadKeyIdx: 'int' = 192
    WriteKeyIdx: 'int' = 192
    AccessRightsLowByte: 'int' = 0
    ChangeKeyIdx: 'int' = 0
    FileSize: 'int' = 256
    IsoFid: 'int' = 16128
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.FileNo != 0:
            non_default_args.append(f'FileNo={ repr(self.FileNo) }')
        if self.FileCommunicationSecurity != "Plain":
            non_default_args.append(f'FileCommunicationSecurity={ repr(self.FileCommunicationSecurity) }')
        if self.FileType != "Standard":
            non_default_args.append(f'FileType={ repr(self.FileType) }')
        if self.ReadKeyNo != 0:
            non_default_args.append(f'ReadKeyNo={ repr(self.ReadKeyNo) }')
        if self.WriteKeyNo != 0:
            non_default_args.append(f'WriteKeyNo={ repr(self.WriteKeyNo) }')
        if self.Offset != 0:
            non_default_args.append(f'Offset={ repr(self.Offset) }')
        if self.Length != 32767:
            non_default_args.append(f'Length={ repr(self.Length) }')
        if self.ReadKeyIdx != 192:
            non_default_args.append(f'ReadKeyIdx={ repr(self.ReadKeyIdx) }')
        if self.WriteKeyIdx != 192:
            non_default_args.append(f'WriteKeyIdx={ repr(self.WriteKeyIdx) }')
        if self.AccessRightsLowByte != 0:
            non_default_args.append(f'AccessRightsLowByte={ repr(self.AccessRightsLowByte) }')
        if self.ChangeKeyIdx != 0:
            non_default_args.append(f'ChangeKeyIdx={ repr(self.ChangeKeyIdx) }')
        if self.FileSize != 256:
            non_default_args.append(f'FileSize={ repr(self.FileSize) }')
        if self.IsoFid != 16128:
            non_default_args.append(f'IsoFid={ repr(self.IsoFid) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class DesfireFileDescription_Dict(TypedDict):
    FileNo: 'NotRequired[int]'
    FileCommunicationSecurity: 'NotRequired[DesfireFileDescription_FileCommunicationSecurity]'
    FileType: 'NotRequired[DesfireFileDescription_FileType]'
    ReadKeyNo: 'NotRequired[int]'
    WriteKeyNo: 'NotRequired[int]'
    Offset: 'NotRequired[int]'
    Length: 'NotRequired[int]'
    ReadKeyIdx: 'NotRequired[int]'
    WriteKeyIdx: 'NotRequired[int]'
    AccessRightsLowByte: 'NotRequired[int]'
    ChangeKeyIdx: 'NotRequired[int]'
    FileSize: 'NotRequired[int]'
    IsoFid: 'NotRequired[int]'
KeyAccessRights_DiversificationMode = Literal["NoDiversification", "ModeAv2"]
KeyAccessRights_DiversificationMode_Parser = LiteralParser[KeyAccessRights_DiversificationMode, int](
    name='KeyAccessRights_DiversificationMode',
    literal_map={
        'NoDiversification': 0,
        'ModeAv2': 2,
    },
)
Hitag_Request_Mode = Literal["StdHtg12S", "AdvHtg1S", "FAdvHS"]
Hitag_Request_Mode_Parser = LiteralParser[Hitag_Request_Mode, int](
    name='Hitag_Request_Mode',
    literal_map={
        'StdHtg12S': 0,
        'AdvHtg1S': 1,
        'FAdvHS': 2,
    },
)
FWI = Literal["Us302", "Us604", "Us1208", "Us2416", "Us4832", "Us9664", "Ms19", "Ms39", "Ms77", "Ms155", "Ms309", "Ms618", "Ms1237", "Ms2474", "Ms4948"]
FWI_Parser = LiteralParser[FWI, int](
    name='FWI',
    literal_map={
        'Us302': 0,
        'Us604': 1,
        'Us1208': 2,
        'Us2416': 3,
        'Us4832': 4,
        'Us9664': 5,
        'Ms19': 6,
        'Ms39': 7,
        'Ms77': 8,
        'Ms155': 9,
        'Ms309': 10,
        'Ms618': 11,
        'Ms1237': 12,
        'Ms2474': 13,
        'Ms4948': 14,
    },
)
VHL_Setup_OptionFlag = Literal["OptFlagZero", "OptFlagOne", "OptFlagAuto"]
VHL_Setup_OptionFlag_Parser = LiteralParser[VHL_Setup_OptionFlag, int](
    name='VHL_Setup_OptionFlag',
    literal_map={
        'OptFlagZero': 0,
        'OptFlagOne': 1,
        'OptFlagAuto': 2,
    },
)
UsbHost_SetupPipes_Type = Literal["Control", "Interrupt", "Bulk", "Isochronous"]
UsbHost_SetupPipes_Type_Parser = LiteralParser[UsbHost_SetupPipes_Type, int](
    name='UsbHost_SetupPipes_Type',
    literal_map={
        'Control': 0,
        'Interrupt': 1,
        'Bulk': 2,
        'Isochronous': 3,
    },
)
ProtType = Literal["NoISO14443L4Support", "ISO14443L4Support", "undefined"]
ProtType_Parser = LiteralParser[ProtType, int](
    name='ProtType',
    literal_map={
        'NoISO14443L4Support': 0,
        'ISO14443L4Support': 1,
        'undefined': -1,
    },
    undefined_literal='undefined',
)
Protocols_Network_UdpIntrospecEnable_Value = Literal["Yes", "No"]
Protocols_Network_UdpIntrospecEnable_Value_Parser = LiteralParser[Protocols_Network_UdpIntrospecEnable_Value, int](
    name='Protocols_Network_UdpIntrospecEnable_Value',
    literal_map={
        'Yes': 1,
        'No': 0,
    },
)
class CRCAddressAndCRCType(NamedTuple):
    """
    This word defines the CRC address according to the addressing mode selected in
    [SegmentIdentificationAndAddressing](.#VhlCfg.File.LegicApplicationSegmentList).
    There must be an entry for every fragment that has enabled the CRC check in
    AddressAndEnableCRC.
    
    The MSB determines the CRC type.
    """
    CRC16bit: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'CRC16bit={ repr(self.CRC16bit) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CRCAddressAndCRCType_Dict(TypedDict):
    """
    This word defines the CRC address according to the addressing mode selected in
    [SegmentIdentificationAndAddressing](.#VhlCfg.File.LegicApplicationSegmentList).
    There must be an entry for every fragment that has enabled the CRC check in
    AddressAndEnableCRC.
    
    The MSB determines the CRC type.
    """
    CRC16bit: 'NotRequired[bool]'
class Bat_Run_SubCmds_Entry(NamedTuple):
    ConditionBits: 'int'
    DevCode: 'int'
    CmdCode: 'int'
    Params: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ConditionBits={ repr(self.ConditionBits) }')
        non_default_args.append(f'DevCode={ repr(self.DevCode) }')
        non_default_args.append(f'CmdCode={ repr(self.CmdCode) }')
        non_default_args.append(f'Params={ repr(self.Params) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_Osdp_SCBKey_DiversifyFlag = Literal["IsAlreadyDiversified", "WillBeDiversified"]
Protocols_Osdp_SCBKey_DiversifyFlag_Parser = LiteralParser[Protocols_Osdp_SCBKey_DiversifyFlag, int](
    name='Protocols_Osdp_SCBKey_DiversifyFlag',
    literal_map={
        'IsAlreadyDiversified': 0,
        'WillBeDiversified': 1,
    },
)
Baudrate = Literal["Baud300", "Baud600", "Baud1200", "Baud2400", "Baud4800", "Baud9600", "Baud14400", "Baud19200", "Baud28800", "Baud38400", "Baud57600", "Baud115200", "Baud500000", "Baud576000", "Baud921600"]
Baudrate_Parser = LiteralParser[Baudrate, int](
    name='Baudrate',
    literal_map={
        'Baud300': 3,
        'Baud600': 6,
        'Baud1200': 12,
        'Baud2400': 24,
        'Baud4800': 48,
        'Baud9600': 96,
        'Baud14400': 144,
        'Baud19200': 192,
        'Baud28800': 288,
        'Baud38400': 384,
        'Baud57600': 576,
        'Baud115200': 1152,
        'Baud500000': 5000,
        'Baud576000': 5760,
        'Baud921600': 9216,
    },
)
VhlCfg_File_LegicSegmentTypeList_Value = Literal["Any", "GAM", "SAM", "IAM", "XAM1", "Data", "Access", "Biometric", "AMPlus"]
VhlCfg_File_LegicSegmentTypeList_Value_Parser = LiteralParser[VhlCfg_File_LegicSegmentTypeList_Value, int](
    name='VhlCfg_File_LegicSegmentTypeList_Value',
    literal_map={
        'Any': 0,
        'GAM': 1,
        'SAM': 2,
        'IAM': 3,
        'XAM1': 4,
        'Data': 64,
        'Access': 80,
        'Biometric': 112,
        'AMPlus': 192,
    },
)
Lg_Select_MediaType = Literal["GAM", "SAM", "IAM", "IM", "NM", "XAM1"]
Lg_Select_MediaType_Parser = LiteralParser[Lg_Select_MediaType, int](
    name='Lg_Select_MediaType',
    literal_map={
        'GAM': 1,
        'SAM': 2,
        'IAM': 3,
        'IM': 4,
        'NM': 5,
        'XAM1': 6,
    },
)
Device_VhlSettings125Khz_IndaspParityCheck_ParityDisable = Literal["Enable", "Disable"]
Device_VhlSettings125Khz_IndaspParityCheck_ParityDisable_Parser = LiteralParser[Device_VhlSettings125Khz_IndaspParityCheck_ParityDisable, int](
    name='Device_VhlSettings125Khz_IndaspParityCheck_ParityDisable',
    literal_map={
        'Enable': 0,
        'Disable': 1,
    },
)
Protocols_RawSerial_Channel_Value = Literal["Channel0", "Channel1"]
Protocols_RawSerial_Channel_Value_Parser = LiteralParser[Protocols_RawSerial_Channel_Value, int](
    name='Protocols_RawSerial_Channel_Value',
    literal_map={
        'Channel0': 0,
        'Channel1': 1,
    },
)
class HostSecurityAccessConditionBits(NamedTuple):
    """
    Every Feature in this list can be disabled by not setting the corresponding
    bit.
    """
    EthernetAccess: 'bool'
    AutoreadAccess: 'bool'
    CryptoAccess: 'bool'
    Bf2Upload: 'bool'
    ExtendedAccess: 'bool'
    FlashFileSystemWrite: 'bool'
    FlashFileSystemRead: 'bool'
    RtcWrite: 'bool'
    VhlExchangeapdu: 'bool'
    VhlFormat: 'bool'
    VhlWrite: 'bool'
    VhlRead: 'bool'
    VhlSelect: 'bool'
    ExtSamAccess: 'bool'
    HfLowlevelAccess: 'bool'
    GuiAccess: 'bool'
    IoPortWrite: 'bool'
    IoPortRead: 'bool'
    ConfigReset: 'bool'
    ConfigWrite: 'bool'
    ConfigRead: 'bool'
    SysReset: 'bool'
    SetAccessConditionMask2: 'bool'
    SetAccessConditionMask1: 'bool'
    SetAccessConditionMask0: 'bool'
    SetKey3: 'bool'
    SetKey2: 'bool'
    SetKey1: 'bool'
    FactoryReset: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'EthernetAccess={ repr(self.EthernetAccess) }')
        non_default_args.append(f'AutoreadAccess={ repr(self.AutoreadAccess) }')
        non_default_args.append(f'CryptoAccess={ repr(self.CryptoAccess) }')
        non_default_args.append(f'Bf2Upload={ repr(self.Bf2Upload) }')
        non_default_args.append(f'ExtendedAccess={ repr(self.ExtendedAccess) }')
        non_default_args.append(f'FlashFileSystemWrite={ repr(self.FlashFileSystemWrite) }')
        non_default_args.append(f'FlashFileSystemRead={ repr(self.FlashFileSystemRead) }')
        non_default_args.append(f'RtcWrite={ repr(self.RtcWrite) }')
        non_default_args.append(f'VhlExchangeapdu={ repr(self.VhlExchangeapdu) }')
        non_default_args.append(f'VhlFormat={ repr(self.VhlFormat) }')
        non_default_args.append(f'VhlWrite={ repr(self.VhlWrite) }')
        non_default_args.append(f'VhlRead={ repr(self.VhlRead) }')
        non_default_args.append(f'VhlSelect={ repr(self.VhlSelect) }')
        non_default_args.append(f'ExtSamAccess={ repr(self.ExtSamAccess) }')
        non_default_args.append(f'HfLowlevelAccess={ repr(self.HfLowlevelAccess) }')
        non_default_args.append(f'GuiAccess={ repr(self.GuiAccess) }')
        non_default_args.append(f'IoPortWrite={ repr(self.IoPortWrite) }')
        non_default_args.append(f'IoPortRead={ repr(self.IoPortRead) }')
        non_default_args.append(f'ConfigReset={ repr(self.ConfigReset) }')
        non_default_args.append(f'ConfigWrite={ repr(self.ConfigWrite) }')
        non_default_args.append(f'ConfigRead={ repr(self.ConfigRead) }')
        non_default_args.append(f'SysReset={ repr(self.SysReset) }')
        non_default_args.append(f'SetAccessConditionMask2={ repr(self.SetAccessConditionMask2) }')
        non_default_args.append(f'SetAccessConditionMask1={ repr(self.SetAccessConditionMask1) }')
        non_default_args.append(f'SetAccessConditionMask0={ repr(self.SetAccessConditionMask0) }')
        non_default_args.append(f'SetKey3={ repr(self.SetKey3) }')
        non_default_args.append(f'SetKey2={ repr(self.SetKey2) }')
        non_default_args.append(f'SetKey1={ repr(self.SetKey1) }')
        non_default_args.append(f'FactoryReset={ repr(self.FactoryReset) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class HostSecurityAccessConditionBits_Dict(TypedDict):
    """
    Every Feature in this list can be disabled by not setting the corresponding
    bit.
    """
    EthernetAccess: 'NotRequired[bool]'
    AutoreadAccess: 'NotRequired[bool]'
    CryptoAccess: 'NotRequired[bool]'
    Bf2Upload: 'NotRequired[bool]'
    ExtendedAccess: 'NotRequired[bool]'
    FlashFileSystemWrite: 'NotRequired[bool]'
    FlashFileSystemRead: 'NotRequired[bool]'
    RtcWrite: 'NotRequired[bool]'
    VhlExchangeapdu: 'NotRequired[bool]'
    VhlFormat: 'NotRequired[bool]'
    VhlWrite: 'NotRequired[bool]'
    VhlRead: 'NotRequired[bool]'
    VhlSelect: 'NotRequired[bool]'
    ExtSamAccess: 'NotRequired[bool]'
    HfLowlevelAccess: 'NotRequired[bool]'
    GuiAccess: 'NotRequired[bool]'
    IoPortWrite: 'NotRequired[bool]'
    IoPortRead: 'NotRequired[bool]'
    ConfigReset: 'NotRequired[bool]'
    ConfigWrite: 'NotRequired[bool]'
    ConfigRead: 'NotRequired[bool]'
    SysReset: 'NotRequired[bool]'
    SetAccessConditionMask2: 'NotRequired[bool]'
    SetAccessConditionMask1: 'NotRequired[bool]'
    SetAccessConditionMask0: 'NotRequired[bool]'
    SetKey3: 'NotRequired[bool]'
    SetKey2: 'NotRequired[bool]'
    SetKey1: 'NotRequired[bool]'
    FactoryReset: 'NotRequired[bool]'
VhlCfg_File_DesfireFormatPiccConfig_ConfigurationSettings = Literal["Default", "DisableFormat", "EnableRandomUID"]
VhlCfg_File_DesfireFormatPiccConfig_ConfigurationSettings_Parser = LiteralParser[VhlCfg_File_DesfireFormatPiccConfig_ConfigurationSettings, int](
    name='VhlCfg_File_DesfireFormatPiccConfig_ConfigurationSettings',
    literal_map={
        'Default': 0,
        'DisableFormat': 1,
        'EnableRandomUID': 2,
    },
)
class VhlCfg_File_AreaList125_Value_Entry(NamedTuple):
    PageAddress: 'int'
    PageNr: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'PageAddress={ repr(self.PageAddress) }')
        non_default_args.append(f'PageNr={ repr(self.PageNr) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class VhlCfg_File_Iso15BlockList_Value_Entry(NamedTuple):
    StartBlock: 'int'
    NumberOfBlocks: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartBlock={ repr(self.StartBlock) }')
        non_default_args.append(f'NumberOfBlocks={ repr(self.NumberOfBlocks) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Iso14b_Request_FWI = Literal["Us302", "Us604", "Us1208", "Us2416", "Us4832", "Us9664", "Ms19", "Ms39", "Ms77", "Ms155", "Ms309", "Ms618", "Ms1237", "Ms2474", "Ms4948"]
Iso14b_Request_FWI_Parser = LiteralParser[Iso14b_Request_FWI, int](
    name='Iso14b_Request_FWI',
    literal_map={
        'Us302': 0,
        'Us604': 1,
        'Us1208': 2,
        'Us2416': 3,
        'Us4832': 4,
        'Us9664': 5,
        'Ms19': 6,
        'Ms39': 7,
        'Ms77': 8,
        'Ms155': 9,
        'Ms309': 10,
        'Ms618': 11,
        'Ms1237': 12,
        'Ms2474': 13,
        'Ms4948': 14,
    },
)
Protocols_Osdp_SCBKeyDefault_DiversifyFlag = Literal["IsAlreadyDiversified", "WillBeDiversified"]
Protocols_Osdp_SCBKeyDefault_DiversifyFlag_Parser = LiteralParser[Protocols_Osdp_SCBKeyDefault_DiversifyFlag, int](
    name='Protocols_Osdp_SCBKeyDefault_DiversifyFlag',
    literal_map={
        'IsAlreadyDiversified': 0,
        'WillBeDiversified': 1,
    },
)
class Iso15_ReadBlock_Data_Entry(NamedTuple):
    BlockData: 'bytes'
    BlockSecData: 'Optional[int]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'BlockData={ repr(self.BlockData) }')
        if self.BlockSecData != None:
            non_default_args.append(f'BlockSecData={ repr(self.BlockSecData) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Project_VhlSettings125Khz_BaudRate_Baud = Literal["Baud32", "Baud64"]
Project_VhlSettings125Khz_BaudRate_Baud_Parser = LiteralParser[Project_VhlSettings125Khz_BaudRate_Baud, int](
    name='Project_VhlSettings125Khz_BaudRate_Baud',
    literal_map={
        'Baud32': 32,
        'Baud64': 64,
    },
)
class VhlCfg_File_UltralightKeyList_Value_Entry(NamedTuple):
    AccessRights: 'KeyAccessRights'
    Algorithm: 'CryptoAlgorithm'
    TripleDesAesKey: 'Optional[bytes]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'AccessRights={ repr(self.AccessRights) }')
        non_default_args.append(f'Algorithm={ repr(self.Algorithm) }')
        if self.TripleDesAesKey != None:
            non_default_args.append(f'TripleDesAesKey={ repr(self.TripleDesAesKey) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Device_Boot_FirmwareCrcCheck_Value = Literal["Enabled", "Disabled"]
Device_Boot_FirmwareCrcCheck_Value_Parser = LiteralParser[Device_Boot_FirmwareCrcCheck_Value, int](
    name='Device_Boot_FirmwareCrcCheck_Value',
    literal_map={
        'Enabled': 255,
        'Disabled': 0,
    },
)
class KeyAccessRights(NamedTuple):
    KeySettings: 'KeyAccessRights_KeySettings'
    Version: 'Optional[int]' = None
    DiversificationMode: 'Optional[KeyAccessRights_DiversificationMode]' = None
    DivIdx: 'Optional[int]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'KeySettings={ repr(self.KeySettings) }')
        if self.Version != None:
            non_default_args.append(f'Version={ repr(self.Version) }')
        if self.DiversificationMode != None:
            non_default_args.append(f'DiversificationMode={ repr(self.DiversificationMode) }')
        if self.DivIdx != None:
            non_default_args.append(f'DivIdx={ repr(self.DivIdx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class KeyAccessRights_Dict(TypedDict):
    KeySettings: 'KeyAccessRights_KeySettings'
    Version: 'NotRequired[int]'
    DiversificationMode: 'NotRequired[KeyAccessRights_DiversificationMode]'
    DivIdx: 'NotRequired[int]'
AuthenticationKeyAssignment = Literal["UseKeyA", "UseKeyB"]
AuthenticationKeyAssignment_Parser = LiteralParser[AuthenticationKeyAssignment, int](
    name='AuthenticationKeyAssignment',
    literal_map={
        'UseKeyA': 0,
        'UseKeyB': 1,
    },
)
Device_Run_DebugInterfaceSecurityLevel_SecurityLevel = Literal["None", "EncryptKey", "EncryptKeyAndConfigSecurityCode"]
Device_Run_DebugInterfaceSecurityLevel_SecurityLevel_Parser = LiteralParser[Device_Run_DebugInterfaceSecurityLevel_SecurityLevel, int](
    name='Device_Run_DebugInterfaceSecurityLevel_SecurityLevel',
    literal_map={
        'None': 0,
        'EncryptKey': 1,
        'EncryptKeyAndConfigSecurityCode': 2,
    },
)
Protocols_Wiegand_Mode_Value = Literal["Standard", "Raw"]
Protocols_Wiegand_Mode_Value_Parser = LiteralParser[Protocols_Wiegand_Mode_Value, int](
    name='Protocols_Wiegand_Mode_Value',
    literal_map={
        'Standard': 0,
        'Raw': 1,
    },
)
Project_VhlSettings125Khz_EM4100SerialNrFormat_Value = Literal["BaltechStandard", "MXCompatible"]
Project_VhlSettings125Khz_EM4100SerialNrFormat_Value_Parser = LiteralParser[Project_VhlSettings125Khz_EM4100SerialNrFormat_Value, int](
    name='Project_VhlSettings125Khz_EM4100SerialNrFormat_Value',
    literal_map={
        'BaltechStandard': 0,
        'MXCompatible': 1,
    },
)
Iso14b_Request_SFGI = Literal["Us302", "Us604", "Us1208", "Us2416", "Us4832", "Us9664", "Ms19", "Ms39", "Ms77", "Ms155", "Ms309", "Ms618", "Ms1237", "Ms2474", "Ms4948"]
Iso14b_Request_SFGI_Parser = LiteralParser[Iso14b_Request_SFGI, int](
    name='Iso14b_Request_SFGI',
    literal_map={
        'Us302': 0,
        'Us604': 1,
        'Us1208': 2,
        'Us2416': 3,
        'Us4832': 4,
        'Us9664': 5,
        'Ms19': 6,
        'Ms39': 7,
        'Ms77': 8,
        'Ms155': 9,
        'Ms309': 10,
        'Ms618': 11,
        'Ms1237': 12,
        'Ms2474': 13,
        'Ms4948': 14,
    },
)
Desfire_ReadData_Mode = Literal["Plain", "MAC", "Encrypted"]
Desfire_ReadData_Mode_Parser = LiteralParser[Desfire_ReadData_Mode, int](
    name='Desfire_ReadData_Mode',
    literal_map={
        'Plain': 0,
        'MAC': 1,
        'Encrypted': 3,
    },
)
Device_Run_DenyReaderInfoViaIso14443_Value = Literal["False", "True"]
Device_Run_DenyReaderInfoViaIso14443_Value_Parser = LiteralParser[Device_Run_DenyReaderInfoViaIso14443_Value, int](
    name='Device_Run_DenyReaderInfoViaIso14443_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
VHL_Setup_FileSpecifier = Literal["SelectByName", "SelectByPath", "SelectByAPDU"]
VHL_Setup_FileSpecifier_Parser = LiteralParser[VHL_Setup_FileSpecifier, int](
    name='VHL_Setup_FileSpecifier',
    literal_map={
        'SelectByName': 0,
        'SelectByPath': 1,
        'SelectByAPDU': 2,
    },
)
class VhlCfg_File_DesfireEv2FormatAppKeysetKeylist_KeysetList_Entry(NamedTuple):
    Keyset: 'int'
    KeysetVersion: 'int'
    KeysetType: 'KeysetType'
    KeyList: 'List[DesfireKeyIdx]'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Keyset={ repr(self.Keyset) }')
        non_default_args.append(f'KeysetVersion={ repr(self.KeysetVersion) }')
        non_default_args.append(f'KeysetType={ repr(self.KeysetType) }')
        non_default_args.append(f'KeyList={ repr(self.KeyList) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Device_VhlSettings_ForceReselect_Value = Literal["False", "True"]
Device_VhlSettings_ForceReselect_Value_Parser = LiteralParser[Device_VhlSettings_ForceReselect_Value, int](
    name='Device_VhlSettings_ForceReselect_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
Project_VhlSettingsLegic_TxpType_LegicTxpTypes = Literal["LegicPrimeMim256", "LegicPrimeMim1024", "LegicAdvantAtc128Mv210", "LegicAdvantAtc256Mv210", "LegicAdvantAtc512Mp110", "LegicAdvantAtc1024Mv110", "LegicAdvantAtc2048Mp110", "LegicAdvantAtc4096Mp310", "LegicAdvantAtc4096Mp311", "LegicAdvantAfs4096Jp10", "LegicPrimeMim22", "LegicCrossCtc4096Mp410", "LegicCrossCtc4096Mm410", "LegicAdvantAtc1024Mv010", "LegicAdvantAtc256Mp410"]
Project_VhlSettingsLegic_TxpType_LegicTxpTypes_Parser = LiteralParser[Project_VhlSettingsLegic_TxpType_LegicTxpTypes, int](
    name='Project_VhlSettingsLegic_TxpType_LegicTxpTypes',
    literal_map={
        'LegicPrimeMim256': 1,
        'LegicPrimeMim1024': 2,
        'LegicAdvantAtc128Mv210': 3,
        'LegicAdvantAtc256Mv210': 4,
        'LegicAdvantAtc512Mp110': 6,
        'LegicAdvantAtc1024Mv110': 7,
        'LegicAdvantAtc2048Mp110': 8,
        'LegicAdvantAtc4096Mp310': 9,
        'LegicAdvantAtc4096Mp311': 10,
        'LegicAdvantAfs4096Jp10': 11,
        'LegicPrimeMim22': 12,
        'LegicCrossCtc4096Mp410': 13,
        'LegicCrossCtc4096Mm410': 16,
        'LegicAdvantAtc1024Mv010': 14,
        'LegicAdvantAtc256Mp410': 15,
    },
)
Project_VhlSettings125Khz_AwidSerialNrFormat_Value = Literal["BaltechStandard", "MXCompatible"]
Project_VhlSettings125Khz_AwidSerialNrFormat_Value_Parser = LiteralParser[Project_VhlSettings125Khz_AwidSerialNrFormat_Value, int](
    name='Project_VhlSettings125Khz_AwidSerialNrFormat_Value',
    literal_map={
        'BaltechStandard': 0,
        'MXCompatible': 1,
    },
)
class VhlCfg_File_LegicSegmentListLegacy_Value_Entry(NamedTuple):
    SegmentIdAndAdr: 'SegmentIdentificationAndAddressing'
    SegmentInformation: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'SegmentIdAndAdr={ repr(self.SegmentIdAndAdr) }')
        non_default_args.append(f'SegmentInformation={ repr(self.SegmentInformation) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
AuthReqUpload = Literal["Default", "None", "CustomerKey", "ConfigSecurityCode", "Version", "GreaterVersion"]
AuthReqUpload_Parser = LiteralParser[AuthReqUpload, int](
    name='AuthReqUpload',
    literal_map={
        'Default': 0,
        'None': 1,
        'CustomerKey': 2,
        'ConfigSecurityCode': 3,
        'Version': 4,
        'GreaterVersion': 5,
    },
)
Project_VhlSettings125Khz_IoProxSerialNrFormat_Value = Literal["BaltechStandard", "MXCompatible"]
Project_VhlSettings125Khz_IoProxSerialNrFormat_Value_Parser = LiteralParser[Project_VhlSettings125Khz_IoProxSerialNrFormat_Value, int](
    name='Project_VhlSettings125Khz_IoProxSerialNrFormat_Value',
    literal_map={
        'BaltechStandard': 0,
        'MXCompatible': 1,
    },
)
Lg_Select_EvStat = Literal["OKNoEvent", "EEPROMFull", "StampToEEPROM", "SamOutOfHF", "NoStampOnSAM", "StampDeleted", "StampDeletionAborted", "StampAlreadyInEEPROM", "StampNotStoredToEEPROM", "NewStampExtended"]
Lg_Select_EvStat_Parser = LiteralParser[Lg_Select_EvStat, int](
    name='Lg_Select_EvStat',
    literal_map={
        'OKNoEvent': 0,
        'EEPROMFull': 1,
        'StampToEEPROM': 2,
        'SamOutOfHF': 3,
        'NoStampOnSAM': 4,
        'StampDeleted': 5,
        'StampDeletionAborted': 6,
        'StampAlreadyInEEPROM': 7,
        'StampNotStoredToEEPROM': 8,
        'NewStampExtended': 9,
    },
)
Device_Run_AutoreadWaitForCardRemoval_WaitForCardRemoval = Literal["Disabled", "Enabled"]
Device_Run_AutoreadWaitForCardRemoval_WaitForCardRemoval_Parser = LiteralParser[Device_Run_AutoreadWaitForCardRemoval_WaitForCardRemoval, int](
    name='Device_Run_AutoreadWaitForCardRemoval_WaitForCardRemoval',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
Ultralight_AuthE2_DivMode = Literal["NoDiv", "SamAv1OneRound", "SamAv1TwoRounds", "SamAv2"]
Ultralight_AuthE2_DivMode_Parser = LiteralParser[Ultralight_AuthE2_DivMode, int](
    name='Ultralight_AuthE2_DivMode',
    literal_map={
        'NoDiv': 0,
        'SamAv1OneRound': 1,
        'SamAv1TwoRounds': 2,
        'SamAv2': 3,
    },
)
Device_Boot_LegicAdvantInitialization_Value = Literal["DelaysPowerup", "AfterPowerup"]
Device_Boot_LegicAdvantInitialization_Value_Parser = LiteralParser[Device_Boot_LegicAdvantInitialization_Value, int](
    name='Device_Boot_LegicAdvantInitialization_Value',
    literal_map={
        'DelaysPowerup': 1,
        'AfterPowerup': 0,
    },
)
VirtualLedDefinition_PhysicalLedSelection = Literal["Right", "Left", "All"]
VirtualLedDefinition_PhysicalLedSelection_Parser = LiteralParser[VirtualLedDefinition_PhysicalLedSelection, int](
    name='VirtualLedDefinition_PhysicalLedSelection',
    literal_map={
        'Right': 1,
        'Left': 2,
        'All': 3,
    },
)
class BlePeriph_DefineService_Characteristics_Entry(NamedTuple):
    """
    List of characteristics (max. 5)
    """
    CharacteristicUUID: 'bytes'
    SupportsIndicate: 'bool'
    SupportsNotify: 'bool'
    SupportsWrite: 'bool'
    SupportsWriteNoResponse: 'bool'
    SupportsRead: 'bool'
    VariableSize: 'bool'
    Size: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'CharacteristicUUID={ repr(self.CharacteristicUUID) }')
        non_default_args.append(f'SupportsIndicate={ repr(self.SupportsIndicate) }')
        non_default_args.append(f'SupportsNotify={ repr(self.SupportsNotify) }')
        non_default_args.append(f'SupportsWrite={ repr(self.SupportsWrite) }')
        non_default_args.append(f'SupportsWriteNoResponse={ repr(self.SupportsWriteNoResponse) }')
        non_default_args.append(f'SupportsRead={ repr(self.SupportsRead) }')
        non_default_args.append(f'VariableSize={ repr(self.VariableSize) }')
        non_default_args.append(f'Size={ repr(self.Size) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Device_Run_AutoreadPulseHf_PulseHf = Literal["Disabled", "Enabled"]
Device_Run_AutoreadPulseHf_PulseHf_Parser = LiteralParser[Device_Run_AutoreadPulseHf_PulseHf, int](
    name='Device_Run_AutoreadPulseHf_PulseHf',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
Custom_BlackWhiteList_ListMode_BlackWhiteListMode = Literal["Blacklist", "Whitelist"]
Custom_BlackWhiteList_ListMode_BlackWhiteListMode_Parser = LiteralParser[Custom_BlackWhiteList_ListMode_BlackWhiteListMode, int](
    name='Custom_BlackWhiteList_ListMode_BlackWhiteListMode',
    literal_map={
        'Blacklist': 1,
        'Whitelist': 0,
    },
)
FireEventAtPowerup = Literal["Never", "IfClear", "IfSet", "Always"]
FireEventAtPowerup_Parser = LiteralParser[FireEventAtPowerup, int](
    name='FireEventAtPowerup',
    literal_map={
        'Never': 0,
        'IfClear': 1,
        'IfSet': 2,
        'Always': 3,
    },
)
Project_SamAVx_PowerUpState_Value = Literal["Idle", "Powered", "Force"]
Project_SamAVx_PowerUpState_Value_Parser = LiteralParser[Project_SamAVx_PowerUpState_Value, int](
    name='Project_SamAVx_PowerUpState_Value',
    literal_map={
        'Idle': 0,
        'Powered': 1,
        'Force': 2,
    },
)
class VhlCfg_File_DesfireKeyList_Value_Entry(NamedTuple):
    AccessRights: 'KeyAccessRights'
    Algorithm: 'CryptoAlgorithm'
    DesKey: 'Optional[bytes]' = None
    ThreeKeyTripleDESKey: 'Optional[bytes]' = None
    TripleDesAesKey: 'Optional[bytes]' = None
    MifareClassicKey: 'Optional[bytes]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'AccessRights={ repr(self.AccessRights) }')
        non_default_args.append(f'Algorithm={ repr(self.Algorithm) }')
        if self.DesKey != None:
            non_default_args.append(f'DesKey={ repr(self.DesKey) }')
        if self.ThreeKeyTripleDESKey != None:
            non_default_args.append(f'ThreeKeyTripleDESKey={ repr(self.ThreeKeyTripleDESKey) }')
        if self.TripleDesAesKey != None:
            non_default_args.append(f'TripleDesAesKey={ repr(self.TripleDesAesKey) }')
        if self.MifareClassicKey != None:
            non_default_args.append(f'MifareClassicKey={ repr(self.MifareClassicKey) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
EpcUid_EpcSelect_MemBank = Literal["EPC", "TID", "User"]
EpcUid_EpcSelect_MemBank_Parser = LiteralParser[EpcUid_EpcSelect_MemBank, int](
    name='EpcUid_EpcSelect_MemBank',
    literal_map={
        'EPC': 1,
        'TID': 2,
        'User': 3,
    },
)
Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder_Value = Literal["False", "True"]
Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder_Value_Parser = LiteralParser[Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder_Value, int](
    name='Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
Project_VhlSettingsLegic_TxpFamily_LegicTxpFamilies = Literal["LegicTxpFamAtc128Mim1024", "LegicTxpFamAtc4096Mp310", "LegicTxpFamAfs4096Jp", "LegicTxpFamAtc4096Mp311", "LegicTxpFamCtc4096Mp410", "LegicTxpFamCtc4096Mm410", "LegicTxpFamAtc1024Mv010", "LegicTxpFamAtc256Mv410"]
Project_VhlSettingsLegic_TxpFamily_LegicTxpFamilies_Parser = LiteralParser[Project_VhlSettingsLegic_TxpFamily_LegicTxpFamilies, int](
    name='Project_VhlSettingsLegic_TxpFamily_LegicTxpFamilies',
    literal_map={
        'LegicTxpFamAtc128Mim1024': 0,
        'LegicTxpFamAtc4096Mp310': 1,
        'LegicTxpFamAfs4096Jp': 2,
        'LegicTxpFamAtc4096Mp311': 3,
        'LegicTxpFamCtc4096Mp410': 5,
        'LegicTxpFamCtc4096Mm410': 6,
        'LegicTxpFamAtc1024Mv010': 7,
        'LegicTxpFamAtc256Mv410': 15,
    },
)
ProtocolID = Literal["All", "BrpSerial", "BrpRs485", "BrpHid", "BrpTcp", "DebugInterface", "RawSerial", "Wiegand", "KeyboardEmulation", "LowLevelIoPorts", "ClkData", "Omron", "Snet", "Bpa9", "Ccid", "RawSerial2", "Osdp", "BleHci", "HttpsClient"]
ProtocolID_Parser = LiteralParser[ProtocolID, int](
    name='ProtocolID',
    literal_map={
        'All': 0,
        'BrpSerial': 3,
        'BrpRs485': 4,
        'BrpHid': 5,
        'BrpTcp': 134,
        'DebugInterface': 9,
        'RawSerial': 35,
        'Wiegand': 32,
        'KeyboardEmulation': 43,
        'LowLevelIoPorts': 36,
        'ClkData': 34,
        'Omron': 33,
        'Snet': 16,
        'Bpa9': 17,
        'Ccid': 54,
        'RawSerial2': 55,
        'Osdp': 56,
        'BleHci': 59,
        'HttpsClient': 60,
    },
)
Iso14b_Attrib_EOF = Literal["EOFrequired", "EOFoptional"]
Iso14b_Attrib_EOF_Parser = LiteralParser[Iso14b_Attrib_EOF, int](
    name='Iso14b_Attrib_EOF',
    literal_map={
        'EOFrequired': 0,
        'EOFoptional': 1,
    },
)
class VhlCfg_File_DesfireEV2FormatFileMultAccessCond_FileList_Entry(NamedTuple):
    FileNr: 'int'
    AccessCondList: 'List[int]'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FileNr={ repr(self.FileNr) }')
        non_default_args.append(f'AccessCondList={ repr(self.AccessCondList) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
SFGI = Literal["Us302", "Us604", "Us1208", "Us2416", "Us4832", "Us9664", "Ms19", "Ms39", "Ms77", "Ms155", "Ms309", "Ms618", "Ms1237", "Ms2474", "Ms4948"]
SFGI_Parser = LiteralParser[SFGI, int](
    name='SFGI',
    literal_map={
        'Us302': 0,
        'Us604': 1,
        'Us1208': 2,
        'Us2416': 3,
        'Us4832': 4,
        'Us9664': 5,
        'Ms19': 6,
        'Ms39': 7,
        'Ms77': 8,
        'Ms155': 9,
        'Ms309': 10,
        'Ms618': 11,
        'Ms1237': 12,
        'Ms2474': 13,
        'Ms4948': 14,
    },
)
VhlCfg_File_ForceCardSM_MinimumSM = Literal["Native", "EV1", "EV2AES128"]
VhlCfg_File_ForceCardSM_MinimumSM_Parser = LiteralParser[VhlCfg_File_ForceCardSM_MinimumSM, int](
    name='VhlCfg_File_ForceCardSM_MinimumSM',
    literal_map={
        'Native': 0,
        'EV1': 1,
        'EV2AES128': 2,
    },
)
class RunSequenceCmd(NamedTuple):
    CmdCode: 'RunSequenceCmd_CmdCode'
    RepeatCnt: 'Optional[int]' = None
    Param: 'Optional[int]' = None
    SwitchIoPort: 'Optional[IoPort]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'CmdCode={ repr(self.CmdCode) }')
        if self.RepeatCnt != None:
            non_default_args.append(f'RepeatCnt={ repr(self.RepeatCnt) }')
        if self.Param != None:
            non_default_args.append(f'Param={ repr(self.Param) }')
        if self.SwitchIoPort != None:
            non_default_args.append(f'SwitchIoPort={ repr(self.SwitchIoPort) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class RunSequenceCmd_Dict(TypedDict):
    CmdCode: 'NotRequired[RunSequenceCmd_CmdCode]'
    RepeatCnt: 'NotRequired[int]'
    Param: 'NotRequired[int]'
    SwitchIoPort: 'NotRequired[IoPort]'
Device_Run_CardReadFailureLogging_Value = Literal["Disabled", "Enabled"]
Device_Run_CardReadFailureLogging_Value_Parser = LiteralParser[Device_Run_CardReadFailureLogging_Value, int](
    name='Device_Run_CardReadFailureLogging_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
EM_DecodeCfg_RxMod = Literal["Unknown", "Manchester", "Biphase", "NRZ"]
EM_DecodeCfg_RxMod_Parser = LiteralParser[EM_DecodeCfg_RxMod, int](
    name='EM_DecodeCfg_RxMod',
    literal_map={
        'Unknown': 0,
        'Manchester': 16,
        'Biphase': 32,
        'NRZ': 48,
    },
)
MobileId_Enable_Mode = Literal["Disable", "Enable"]
MobileId_Enable_Mode_Parser = LiteralParser[MobileId_Enable_Mode, int](
    name='MobileId_Enable_Mode',
    literal_map={
        'Disable': 0,
        'Enable': 1,
    },
)
class CardTypes125KhzPart2(NamedTuple):
    Idteck: 'bool'
    Cotag: 'bool'
    HidIndalaSecure: 'bool'
    GProx: 'bool'
    SecuraKey: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Idteck={ repr(self.Idteck) }')
        non_default_args.append(f'Cotag={ repr(self.Cotag) }')
        non_default_args.append(f'HidIndalaSecure={ repr(self.HidIndalaSecure) }')
        non_default_args.append(f'GProx={ repr(self.GProx) }')
        non_default_args.append(f'SecuraKey={ repr(self.SecuraKey) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CardTypes125KhzPart2_Dict(TypedDict):
    Idteck: 'NotRequired[bool]'
    Cotag: 'NotRequired[bool]'
    HidIndalaSecure: 'NotRequired[bool]'
    GProx: 'NotRequired[bool]'
    SecuraKey: 'NotRequired[bool]'
class Desfire_GetDfNames_AppNr_Entry(NamedTuple):
    AppId: 'int'
    IsoFileId: 'int'
    IsoDfName: 'bytes'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'AppId={ repr(self.AppId) }')
        non_default_args.append(f'IsoFileId={ repr(self.IsoFileId) }')
        non_default_args.append(f'IsoDfName={ repr(self.IsoDfName) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_Network_WlanEncryptionMode_Value = Literal["Open", "WPA", "WPA2", "WEP", "LEAP", "PEAP"]
Protocols_Network_WlanEncryptionMode_Value_Parser = LiteralParser[Protocols_Network_WlanEncryptionMode_Value, int](
    name='Protocols_Network_WlanEncryptionMode_Value',
    literal_map={
        'Open': 0,
        'WPA': 1,
        'WPA2': 2,
        'WEP': 3,
        'LEAP': 4,
        'PEAP': 5,
    },
)
Iso14L4_SetupAPDU_FWI = Literal["Us302", "Us604", "Us1208", "Us2416", "Us4832", "Us9664", "Ms19", "Ms39", "Ms77", "Ms155", "Ms309", "Ms618", "Ms1237", "Ms2474", "Ms4948"]
Iso14L4_SetupAPDU_FWI_Parser = LiteralParser[Iso14L4_SetupAPDU_FWI, int](
    name='Iso14L4_SetupAPDU_FWI',
    literal_map={
        'Us302': 0,
        'Us604': 1,
        'Us1208': 2,
        'Us2416': 3,
        'Us4832': 4,
        'Us9664': 5,
        'Ms19': 6,
        'Ms39': 7,
        'Ms77': 8,
        'Ms155': 9,
        'Ms309': 10,
        'Ms618': 11,
        'Ms1237': 12,
        'Ms2474': 13,
        'Ms4948': 14,
    },
)
Lg_Idle_PowOff = Literal["On", "Off", "OffPowerReduced"]
Lg_Idle_PowOff_Parser = LiteralParser[Lg_Idle_PowOff, int](
    name='Lg_Idle_PowOff',
    literal_map={
        'On': 0,
        'Off': 1,
        'OffPowerReduced': 2,
    },
)
Protocols_Network_NicNetworkPortSpeedDuplexMode_Value = Literal["Autonegotiation", "HalfDuplex10Mbit", "FullDuplex10Mbit", "HalfDuplex100Mbit", "FullDuplex100Mbit"]
Protocols_Network_NicNetworkPortSpeedDuplexMode_Value_Parser = LiteralParser[Protocols_Network_NicNetworkPortSpeedDuplexMode_Value, int](
    name='Protocols_Network_NicNetworkPortSpeedDuplexMode_Value',
    literal_map={
        'Autonegotiation': 0,
        'HalfDuplex10Mbit': 1,
        'FullDuplex10Mbit': 2,
        'HalfDuplex100Mbit': 3,
        'FullDuplex100Mbit': 4,
    },
)
Device_Run_DenyUnauthFwUploadViaBrp_Value = Literal["False", "True"]
Device_Run_DenyUnauthFwUploadViaBrp_Value_Parser = LiteralParser[Device_Run_DenyUnauthFwUploadViaBrp_Value, int](
    name='Device_Run_DenyUnauthFwUploadViaBrp_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
Device_Keypad_SpecialKeySettings_Settings = Literal["StarSharpCorrect", "StarSharpTerminate", "Raw", "StarClearSharpTerminate", "DipSwitch"]
Device_Keypad_SpecialKeySettings_Settings_Parser = LiteralParser[Device_Keypad_SpecialKeySettings_Settings, int](
    name='Device_Keypad_SpecialKeySettings_Settings',
    literal_map={
        'StarSharpCorrect': 0,
        'StarSharpTerminate': 1,
        'Raw': 2,
        'StarClearSharpTerminate': 3,
        'DipSwitch': 255,
    },
)
MessageType = Literal["Card", "AlarmOn", "AlarmOff", "Keyboard", "CardRemoval", "FunctionKey", "Logs"]
MessageType_Parser = LiteralParser[MessageType, int](
    name='MessageType',
    literal_map={
        'Card': 0,
        'AlarmOn': 1,
        'AlarmOff': 2,
        'Keyboard': 3,
        'CardRemoval': 4,
        'FunctionKey': 5,
        'Logs': 6,
    },
)
class AutoRunCommand(NamedTuple):
    RunMode: 'AutoRunCommand_RunMode'
    DeviceCode: 'int'
    CommandCode: 'int'
    Parameter: 'str'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'RunMode={ repr(self.RunMode) }')
        non_default_args.append(f'DeviceCode={ repr(self.DeviceCode) }')
        non_default_args.append(f'CommandCode={ repr(self.CommandCode) }')
        non_default_args.append(f'Parameter={ repr(self.Parameter) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class AutoRunCommand_Dict(TypedDict):
    RunMode: 'NotRequired[AutoRunCommand_RunMode]'
    DeviceCode: 'NotRequired[int]'
    CommandCode: 'NotRequired[int]'
    Parameter: 'str'
Desfire_ExecCommand_CryptoMode = Literal["Plain", "MAC", "Encrypted"]
Desfire_ExecCommand_CryptoMode_Parser = LiteralParser[Desfire_ExecCommand_CryptoMode, int](
    name='Desfire_ExecCommand_CryptoMode',
    literal_map={
        'Plain': 0,
        'MAC': 1,
        'Encrypted': 3,
    },
)
TTF_ReadByteStream_RxMod = Literal["Manchester", "Biphase", "Ind", "HIDP", "PSK", "SMPL"]
TTF_ReadByteStream_RxMod_Parser = LiteralParser[TTF_ReadByteStream_RxMod, int](
    name='TTF_ReadByteStream_RxMod',
    literal_map={
        'Manchester': 16,
        'Biphase': 32,
        'Ind': 48,
        'HIDP': 80,
        'PSK': 96,
        'SMPL': 112,
    },
)
Project_SamAVxKeySettings_Index_DiversificationMode = Literal["NoDiversification", "ModeAv1", "ModeAv2", "ModeAv1Des1Round"]
Project_SamAVxKeySettings_Index_DiversificationMode_Parser = LiteralParser[Project_SamAVxKeySettings_Index_DiversificationMode, int](
    name='Project_SamAVxKeySettings_Index_DiversificationMode',
    literal_map={
        'NoDiversification': 0,
        'ModeAv1': 1,
        'ModeAv2': 2,
        'ModeAv1Des1Round': 17,
    },
)
class Iso14b_GetTransparentSettings_Tags_Entry(NamedTuple):
    ID: 'int'
    Value: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ID={ repr(self.ID) }')
        non_default_args.append(f'Value={ repr(self.Value) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Device_VhlSettings125Khz_Baud_Baud = Literal["ModUnknown", "Baud32", "Baud64"]
Device_VhlSettings125Khz_Baud_Baud_Parser = LiteralParser[Device_VhlSettings125Khz_Baud_Baud, int](
    name='Device_VhlSettings125Khz_Baud_Baud',
    literal_map={
        'ModUnknown': 0,
        'Baud32': 32,
        'Baud64': 64,
    },
)
Project_VhlSettings125Khz_ModType_Mod = Literal["ModManchester", "ModBiphase", "ModNRZ", "ModHID"]
Project_VhlSettings125Khz_ModType_Mod_Parser = LiteralParser[Project_VhlSettings125Khz_ModType_Mod, int](
    name='Project_VhlSettings125Khz_ModType_Mod',
    literal_map={
        'ModManchester': 16,
        'ModBiphase': 32,
        'ModNRZ': 48,
        'ModHID': 80,
    },
)
Lg_Lock_PwdStat = Literal["Activated", "Deactivated"]
Lg_Lock_PwdStat_Parser = LiteralParser[Lg_Lock_PwdStat, int](
    name='Lg_Lock_PwdStat',
    literal_map={
        'Activated': 0,
        'Deactivated': 1,
    },
)
Device_Run_DenyUploadViaIso14443_Value = Literal["False", "True"]
Device_Run_DenyUploadViaIso14443_Value_Parser = LiteralParser[Device_Run_DenyUploadViaIso14443_Value, int](
    name='Device_Run_DenyUploadViaIso14443_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
class CryptoMemoryIndex(NamedTuple):
    Page: 'int'
    Idx: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Page={ repr(self.Page) }')
        non_default_args.append(f'Idx={ repr(self.Idx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CryptoMemoryIndex_Dict(TypedDict):
    Page: 'NotRequired[int]'
    Idx: 'NotRequired[int]'
Iso14b_Attrib_SOF = Literal["SOFrequired", "SOFoptional"]
Iso14b_Attrib_SOF_Parser = LiteralParser[Iso14b_Attrib_SOF, int](
    name='Iso14b_Attrib_SOF',
    literal_map={
        'SOFrequired': 0,
        'SOFoptional': 1,
    },
)
Project_Bluetooth_ConnectionMode_Value = Literal["NonConnectable", "Connectable"]
Project_Bluetooth_ConnectionMode_Value_Parser = LiteralParser[Project_Bluetooth_ConnectionMode_Value, int](
    name='Project_Bluetooth_ConnectionMode_Value',
    literal_map={
        'NonConnectable': 0,
        'Connectable': 1,
    },
)
VhlCfg_File_MifareTransferToSecureMemory_TransferKeys = Literal["Yes", "No"]
VhlCfg_File_MifareTransferToSecureMemory_TransferKeys_Parser = LiteralParser[VhlCfg_File_MifareTransferToSecureMemory_TransferKeys, int](
    name='VhlCfg_File_MifareTransferToSecureMemory_TransferKeys',
    literal_map={
        'Yes': 255,
        'No': 254,
    },
)
RunSequenceCmd_CmdCode = Literal["EnablePort", "DisablePort", "RepeatLoop", "WaitMs", "WaitSec", "EndOfSequence", "StartLoop", "OnStop", "EnablePortGreenLed", "EnablePortRedLed", "EnablePortBeeper", "EnablePortRelay", "EnablePortBlue", "DisablePortGreenLed", "DisablePortRedLed", "DisablePortBeeper", "DisablePortRelay", "DisablePortBlue", "InvertPortGreenLed", "InvertPortRedLed", "InvertPortBeeper", "InvertPortRelay", "InvertPortBlue", "Repeat1Times", "RepeatLoop2Times", "RepeatLoop3Times", "RepeatLoop4Times", "RepeatLoop5Times", "RepeatLoop6Times", "RepeatLoop7Times", "RepeatLoop8Times", "RepeatLoop9Times", "RepeatLoop10Times", "RepeatLoop11Times", "RepeatLoop12Times", "RepeatLoop13Times", "RepeatLoop14Times", "RepeatLoop15Times", "Wait100Ms", "Wait200Ms", "Wait300Ms", "Wait400Ms", "Wait500Ms", "Wait600Ms", "Wait700Ms", "Wait800Ms", "Wait900Ms", "Wait1000Ms", "Wait1100Ms", "Wait1200Ms", "Wait1300Ms", "Wait1400Ms", "Wait1500Ms", "Wait1600Ms", "Wait1700Ms", "Wait1800Ms", "Wait1900Ms", "Wait2000Ms", "Wait2100Ms", "Wait2200Ms", "Wait2300Ms", "Wait2400Ms", "Wait2500Ms", "Wait2600Ms", "Wait2700Ms", "Wait2800Ms", "Wait2900Ms", "Wait3000Ms", "Wait3100Ms", "Wait3200Ms", "Wait3300Ms", "Wait3400Ms", "Wait3500Ms", "Wait3600Ms", "Wait3700Ms", "Wait3800Ms", "Wait3900Ms", "Wait4000Ms", "Wait4100Ms", "Wait4200Ms", "Wait4300Ms", "Wait4400Ms", "Wait4500Ms", "Wait4600Ms", "Wait4700Ms", "Wait4800Ms", "Wait4900Ms", "Wait5000Ms", "Wait5100Ms", "Wait5200Ms", "Wait5300Ms", "Wait5400Ms", "Wait5500Ms", "Wait5600Ms", "Wait5700Ms", "Wait5800Ms", "Wait5900Ms", "Wait6000Ms", "Wait6100Ms", "Wait6200Ms", "Wait6300Ms"]
RunSequenceCmd_CmdCode_Parser = LiteralParser[RunSequenceCmd_CmdCode, int](
    name='RunSequenceCmd_CmdCode',
    literal_map={
        'EnablePort': 1,
        'DisablePort': 2,
        'RepeatLoop': 5,
        'WaitMs': 8,
        'WaitSec': 9,
        'EndOfSequence': 241,
        'StartLoop': 242,
        'OnStop': 243,
        'EnablePortGreenLed': 16,
        'EnablePortRedLed': 17,
        'EnablePortBeeper': 18,
        'EnablePortRelay': 19,
        'EnablePortBlue': 22,
        'DisablePortGreenLed': 32,
        'DisablePortRedLed': 33,
        'DisablePortBeeper': 34,
        'DisablePortRelay': 35,
        'DisablePortBlue': 38,
        'InvertPortGreenLed': 48,
        'InvertPortRedLed': 49,
        'InvertPortBeeper': 50,
        'InvertPortRelay': 51,
        'InvertPortBlue': 54,
        'Repeat1Times': 81,
        'RepeatLoop2Times': 82,
        'RepeatLoop3Times': 83,
        'RepeatLoop4Times': 84,
        'RepeatLoop5Times': 85,
        'RepeatLoop6Times': 86,
        'RepeatLoop7Times': 87,
        'RepeatLoop8Times': 88,
        'RepeatLoop9Times': 89,
        'RepeatLoop10Times': 90,
        'RepeatLoop11Times': 91,
        'RepeatLoop12Times': 92,
        'RepeatLoop13Times': 93,
        'RepeatLoop14Times': 94,
        'RepeatLoop15Times': 95,
        'Wait100Ms': 129,
        'Wait200Ms': 130,
        'Wait300Ms': 131,
        'Wait400Ms': 132,
        'Wait500Ms': 133,
        'Wait600Ms': 134,
        'Wait700Ms': 135,
        'Wait800Ms': 136,
        'Wait900Ms': 137,
        'Wait1000Ms': 138,
        'Wait1100Ms': 139,
        'Wait1200Ms': 140,
        'Wait1300Ms': 141,
        'Wait1400Ms': 142,
        'Wait1500Ms': 143,
        'Wait1600Ms': 144,
        'Wait1700Ms': 145,
        'Wait1800Ms': 146,
        'Wait1900Ms': 147,
        'Wait2000Ms': 148,
        'Wait2100Ms': 149,
        'Wait2200Ms': 150,
        'Wait2300Ms': 151,
        'Wait2400Ms': 152,
        'Wait2500Ms': 153,
        'Wait2600Ms': 154,
        'Wait2700Ms': 155,
        'Wait2800Ms': 156,
        'Wait2900Ms': 157,
        'Wait3000Ms': 158,
        'Wait3100Ms': 159,
        'Wait3200Ms': 160,
        'Wait3300Ms': 161,
        'Wait3400Ms': 162,
        'Wait3500Ms': 163,
        'Wait3600Ms': 164,
        'Wait3700Ms': 165,
        'Wait3800Ms': 166,
        'Wait3900Ms': 167,
        'Wait4000Ms': 168,
        'Wait4100Ms': 169,
        'Wait4200Ms': 170,
        'Wait4300Ms': 171,
        'Wait4400Ms': 172,
        'Wait4500Ms': 173,
        'Wait4600Ms': 174,
        'Wait4700Ms': 175,
        'Wait4800Ms': 176,
        'Wait4900Ms': 177,
        'Wait5000Ms': 178,
        'Wait5100Ms': 179,
        'Wait5200Ms': 180,
        'Wait5300Ms': 181,
        'Wait5400Ms': 182,
        'Wait5500Ms': 183,
        'Wait5600Ms': 184,
        'Wait5700Ms': 185,
        'Wait5800Ms': 186,
        'Wait5900Ms': 187,
        'Wait6000Ms': 188,
        'Wait6100Ms': 189,
        'Wait6200Ms': 190,
        'Wait6300Ms': 191,
    },
)
DHWCtrl_AesWrapKey_WrappedKeyNr = Literal["WrapNone", "WrapDHUK"]
DHWCtrl_AesWrapKey_WrappedKeyNr_Parser = LiteralParser[DHWCtrl_AesWrapKey_WrappedKeyNr, int](
    name='DHWCtrl_AesWrapKey_WrappedKeyNr',
    literal_map={
        'WrapNone': 0,
        'WrapDHUK': 1,
    },
)
VhlCfg_File_MifareMode_AccessMode = Literal["Absolute", "Mad", "AbsoluteFullS0"]
VhlCfg_File_MifareMode_AccessMode_Parser = LiteralParser[VhlCfg_File_MifareMode_AccessMode, int](
    name='VhlCfg_File_MifareMode_AccessMode',
    literal_map={
        'Absolute': 0,
        'Mad': 1,
        'AbsoluteFullS0': 2,
    },
)
UI_Toggle_Polarity = Literal["Normal", "Inverted"]
UI_Toggle_Polarity_Parser = LiteralParser[UI_Toggle_Polarity, int](
    name='UI_Toggle_Polarity',
    literal_map={
        'Normal': 0,
        'Inverted': 1,
    },
)
class AddressAndEnableCRC(NamedTuple):
    """
    This word defines the start address according to the addressing mode selected
    in
    [SegmentIdentificationAndAddressing](.#VhlCfg.File.LegicApplicationSegmentList)
    for every fragment.
    
    The MSB determines if a CRC check shall be applied for accessing this segment.
    """
    EnableCRC: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'EnableCRC={ repr(self.EnableCRC) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class AddressAndEnableCRC_Dict(TypedDict):
    """
    This word defines the start address according to the addressing mode selected
    in
    [SegmentIdentificationAndAddressing](.#VhlCfg.File.LegicApplicationSegmentList)
    for every fragment.
    
    The MSB determines if a CRC check shall be applied for accessing this segment.
    """
    EnableCRC: 'NotRequired[bool]'
class VhlCfg_File_UltralightExtendedBlockList_Value_Entry(NamedTuple):
    StartBlock: 'int'
    NumberOfBlocks: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartBlock={ repr(self.StartBlock) }')
        non_default_args.append(f'NumberOfBlocks={ repr(self.NumberOfBlocks) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IoPortBitmask(NamedTuple):
    Gpio7: 'bool'
    Gpio6: 'bool'
    Gpio5: 'bool'
    Gpio4: 'bool'
    Gpio3: 'bool'
    Gpio2: 'bool'
    Gpio1: 'bool'
    Gpio0: 'bool'
    TamperAlarm: 'bool'
    BlueLed: 'bool'
    Input1: 'bool'
    Input0: 'bool'
    Relay: 'bool'
    Beeper: 'bool'
    RedLed: 'bool'
    GreenLed: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Gpio7={ repr(self.Gpio7) }')
        non_default_args.append(f'Gpio6={ repr(self.Gpio6) }')
        non_default_args.append(f'Gpio5={ repr(self.Gpio5) }')
        non_default_args.append(f'Gpio4={ repr(self.Gpio4) }')
        non_default_args.append(f'Gpio3={ repr(self.Gpio3) }')
        non_default_args.append(f'Gpio2={ repr(self.Gpio2) }')
        non_default_args.append(f'Gpio1={ repr(self.Gpio1) }')
        non_default_args.append(f'Gpio0={ repr(self.Gpio0) }')
        non_default_args.append(f'TamperAlarm={ repr(self.TamperAlarm) }')
        non_default_args.append(f'BlueLed={ repr(self.BlueLed) }')
        non_default_args.append(f'Input1={ repr(self.Input1) }')
        non_default_args.append(f'Input0={ repr(self.Input0) }')
        non_default_args.append(f'Relay={ repr(self.Relay) }')
        non_default_args.append(f'Beeper={ repr(self.Beeper) }')
        non_default_args.append(f'RedLed={ repr(self.RedLed) }')
        non_default_args.append(f'GreenLed={ repr(self.GreenLed) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class IoPortBitmask_Dict(TypedDict):
    Gpio7: 'NotRequired[bool]'
    Gpio6: 'NotRequired[bool]'
    Gpio5: 'NotRequired[bool]'
    Gpio4: 'NotRequired[bool]'
    Gpio3: 'NotRequired[bool]'
    Gpio2: 'NotRequired[bool]'
    Gpio1: 'NotRequired[bool]'
    Gpio0: 'NotRequired[bool]'
    TamperAlarm: 'NotRequired[bool]'
    BlueLed: 'NotRequired[bool]'
    Input1: 'NotRequired[bool]'
    Input0: 'NotRequired[bool]'
    Relay: 'NotRequired[bool]'
    Beeper: 'NotRequired[bool]'
    RedLed: 'NotRequired[bool]'
    GreenLed: 'NotRequired[bool]'
class HostSecurityAuthenticationMode(NamedTuple):
    """
    Specifies a minimum of security requirements, when working in this security
    level
    """
    RequireContinuousIv: 'bool'
    RequireEncrypted: 'bool'
    RequireMac: 'bool'
    RequireSessionKey: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'RequireContinuousIv={ repr(self.RequireContinuousIv) }')
        non_default_args.append(f'RequireEncrypted={ repr(self.RequireEncrypted) }')
        non_default_args.append(f'RequireMac={ repr(self.RequireMac) }')
        non_default_args.append(f'RequireSessionKey={ repr(self.RequireSessionKey) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class HostSecurityAuthenticationMode_Dict(TypedDict):
    """
    Specifies a minimum of security requirements, when working in this security
    level
    """
    RequireContinuousIv: 'NotRequired[bool]'
    RequireEncrypted: 'NotRequired[bool]'
    RequireMac: 'NotRequired[bool]'
    RequireSessionKey: 'NotRequired[bool]'
class Iso15_GetUIDList_Labels_Entry(NamedTuple):
    UID: 'bytes'
    DSFID: 'Optional[int]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'UID={ repr(self.UID) }')
        if self.DSFID != None:
            non_default_args.append(f'DSFID={ repr(self.DSFID) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_Ccid_LedControl_Value = Literal["Disabled", "Enabled"]
Protocols_Ccid_LedControl_Value_Parser = LiteralParser[Protocols_Ccid_LedControl_Value, int](
    name='Protocols_Ccid_LedControl_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
class Sys_SetRegister_RegisterAssignments_Entry(NamedTuple):
    ID: 'int'
    Value: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ID={ repr(self.ID) }')
        non_default_args.append(f'Value={ repr(self.Value) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Project_MobileId_Mode_Value = Literal["Disabled", "Enabled"]
Project_MobileId_Mode_Value_Parser = LiteralParser[Project_MobileId_Mode_Value, int](
    name='Project_MobileId_Mode_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
Desfire_WriteData_Mode = Literal["Plain", "MAC", "Encrypted"]
Desfire_WriteData_Mode_Parser = LiteralParser[Desfire_WriteData_Mode, int](
    name='Desfire_WriteData_Mode',
    literal_map={
        'Plain': 0,
        'MAC': 1,
        'Encrypted': 3,
    },
)
Protocols_SNet_DeviceType_Value = Literal["Mkr", "DkrKeyPinMode", "DkrStandardMode"]
Protocols_SNet_DeviceType_Value_Parser = LiteralParser[Protocols_SNet_DeviceType_Value, int](
    name='Protocols_SNet_DeviceType_Value',
    literal_map={
        'Mkr': 0,
        'DkrKeyPinMode': 1,
        'DkrStandardMode': 2,
    },
)
Protocols_Network_SlpActiveDiscovery_Value = Literal["Disabled", "Enabled"]
Protocols_Network_SlpActiveDiscovery_Value_Parser = LiteralParser[Protocols_Network_SlpActiveDiscovery_Value, int](
    name='Protocols_Network_SlpActiveDiscovery_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
class VhlCfg_File_DesfireFormatAppChangeKeys_Value_Entry(NamedTuple):
    KeyNo: 'int'
    CurrentKeyIdx: 'DesfireKeyIdx'
    NewKeyIdx: 'DesfireKeyIdx'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'KeyNo={ repr(self.KeyNo) }')
        non_default_args.append(f'CurrentKeyIdx={ repr(self.CurrentKeyIdx) }')
        non_default_args.append(f'NewKeyIdx={ repr(self.NewKeyIdx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_Network_NicPrinterPortSpeedDuplexMode_Value = Literal["Autonegotiation", "HalfDuplex10Mbit", "FullDuplex10Mbit", "HalfDuplex100Mbit", "FullDuplex100Mbit", "Disabled"]
Protocols_Network_NicPrinterPortSpeedDuplexMode_Value_Parser = LiteralParser[Protocols_Network_NicPrinterPortSpeedDuplexMode_Value, int](
    name='Protocols_Network_NicPrinterPortSpeedDuplexMode_Value',
    literal_map={
        'Autonegotiation': 0,
        'HalfDuplex10Mbit': 1,
        'FullDuplex10Mbit': 2,
        'HalfDuplex100Mbit': 3,
        'FullDuplex100Mbit': 4,
        'Disabled': 255,
    },
)
VhlCfg_File_DesfireProtocol_ProtocolMode = Literal["Auto", "Native", "IsoCompatible"]
VhlCfg_File_DesfireProtocol_ProtocolMode_Parser = LiteralParser[VhlCfg_File_DesfireProtocol_ProtocolMode, int](
    name='VhlCfg_File_DesfireProtocol_ProtocolMode',
    literal_map={
        'Auto': 0,
        'Native': 1,
        'IsoCompatible': 2,
    },
)
Lg_Unlock_PwdStat = Literal["Unlocked", "NotActivated", "AlreadyUnlocked"]
Lg_Unlock_PwdStat_Parser = LiteralParser[Lg_Unlock_PwdStat, int](
    name='Lg_Unlock_PwdStat',
    literal_map={
        'Unlocked': 0,
        'NotActivated': 1,
        'AlreadyUnlocked': 2,
    },
)
class VhlCfg_File_DesfireMapKeyidx_KeyidxMapList_Entry(NamedTuple):
    """
    Entry has to be a sorted list, sorted by keyidx in ascending order.
    """
    Keyidx: 'int'
    KeyidxMsb: 'int'
    KeyidxLsb: 'DesfireKeyIdx'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Keyidx={ repr(self.Keyidx) }')
        non_default_args.append(f'KeyidxMsb={ repr(self.KeyidxMsb) }')
        non_default_args.append(f'KeyidxLsb={ repr(self.KeyidxLsb) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Iso14b_Request_ProtType = Literal["NoISO14443L4Support", "ISO14443L4Support", "undefined"]
Iso14b_Request_ProtType_Parser = LiteralParser[Iso14b_Request_ProtType, int](
    name='Iso14b_Request_ProtType',
    literal_map={
        'NoISO14443L4Support': 0,
        'ISO14443L4Support': 1,
        'undefined': -1,
    },
    undefined_literal='undefined',
)
Project_VhlSettings125Khz_IndaspParityCheck_ParityDisable = Literal["Enable", "Disable"]
Project_VhlSettings125Khz_IndaspParityCheck_ParityDisable_Parser = LiteralParser[Project_VhlSettings125Khz_IndaspParityCheck_ParityDisable, int](
    name='Project_VhlSettings125Khz_IndaspParityCheck_ParityDisable',
    literal_map={
        'Enable': 0,
        'Disable': 1,
    },
)
Desfire_ChangeExtKey_MasterKeyType = Literal["DESorTripleDES", "ThreeKeyTripleDES", "AES"]
Desfire_ChangeExtKey_MasterKeyType_Parser = LiteralParser[Desfire_ChangeExtKey_MasterKeyType, int](
    name='Desfire_ChangeExtKey_MasterKeyType',
    literal_map={
        'DESorTripleDES': 0,
        'ThreeKeyTripleDES': 1,
        'AES': 2,
    },
)
class FirmwareVersion(NamedTuple):
    FirmwareID: 'int'
    SmallestBlockedFwVersionMajor: 'int'
    SmallestBlockedFwVersionMinor: 'int'
    SmallestBlockedFwVersionBuild: 'int'
    GreatestBlockedFwVersionMajor: 'int'
    GreatestBlockedFwVersionMinor: 'int'
    GreatestBlockedFwVersionBuild: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FirmwareID={ repr(self.FirmwareID) }')
        non_default_args.append(f'SmallestBlockedFwVersionMajor={ repr(self.SmallestBlockedFwVersionMajor) }')
        non_default_args.append(f'SmallestBlockedFwVersionMinor={ repr(self.SmallestBlockedFwVersionMinor) }')
        non_default_args.append(f'SmallestBlockedFwVersionBuild={ repr(self.SmallestBlockedFwVersionBuild) }')
        non_default_args.append(f'GreatestBlockedFwVersionMajor={ repr(self.GreatestBlockedFwVersionMajor) }')
        non_default_args.append(f'GreatestBlockedFwVersionMinor={ repr(self.GreatestBlockedFwVersionMinor) }')
        non_default_args.append(f'GreatestBlockedFwVersionBuild={ repr(self.GreatestBlockedFwVersionBuild) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class FirmwareVersion_Dict(TypedDict):
    FirmwareID: 'NotRequired[int]'
    SmallestBlockedFwVersionMajor: 'NotRequired[int]'
    SmallestBlockedFwVersionMinor: 'NotRequired[int]'
    SmallestBlockedFwVersionBuild: 'NotRequired[int]'
    GreatestBlockedFwVersionMajor: 'NotRequired[int]'
    GreatestBlockedFwVersionMinor: 'NotRequired[int]'
    GreatestBlockedFwVersionBuild: 'NotRequired[int]'
Iso78_OpenSam_LID = Literal["AV2", "HID", "Gen1", "Gen2"]
Iso78_OpenSam_LID_Parser = LiteralParser[Iso78_OpenSam_LID, int](
    name='Iso78_OpenSam_LID',
    literal_map={
        'AV2': 0,
        'HID': 1,
        'Gen1': 16,
        'Gen2': 17,
    },
)
KeysetType = Literal["TripleDESKey", "ThreeKeyTripleDESKey", "AESKey"]
KeysetType_Parser = LiteralParser[KeysetType, int](
    name='KeysetType',
    literal_map={
        'TripleDESKey': 0,
        'ThreeKeyTripleDESKey': 1,
        'AESKey': 2,
    },
)
BlePeriph_IsConnected_AddressType = Literal["Public", "RandomStatic", "RandomResolvable", "RandomNonResolvable"]
BlePeriph_IsConnected_AddressType_Parser = LiteralParser[BlePeriph_IsConnected_AddressType, int](
    name='BlePeriph_IsConnected_AddressType',
    literal_map={
        'Public': 0,
        'RandomStatic': 1,
        'RandomResolvable': 2,
        'RandomNonResolvable': 3,
    },
)
VhlCfg_File_Iso15WriteCmd_Value = Literal["WriteAuto", "WriteMultipleBlocksCmd", "WriteSingleBlockCmd"]
VhlCfg_File_Iso15WriteCmd_Value_Parser = LiteralParser[VhlCfg_File_Iso15WriteCmd_Value, int](
    name='VhlCfg_File_Iso15WriteCmd_Value',
    literal_map={
        'WriteAuto': 0,
        'WriteMultipleBlocksCmd': 1,
        'WriteSingleBlockCmd': 2,
    },
)
class Template_Scramble_BitMap_Entry(NamedTuple):
    """
    This array contains mapping, that maps every bits in the destination block to
    a bit in the source block or a constant value.
    """
    Invert: 'bool'
    SrcBitPos: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'Invert={ repr(self.Invert) }')
        non_default_args.append(f'SrcBitPos={ repr(self.SrcBitPos) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Template_IsEqual_ActionOnSuccess = Literal["Cut", "Keep"]
Template_IsEqual_ActionOnSuccess_Parser = LiteralParser[Template_IsEqual_ActionOnSuccess, int](
    name='Template_IsEqual_ActionOnSuccess',
    literal_map={
        'Cut': 1,
        'Keep': 2,
    },
)
Template_Encrypt_CryptoMode = Literal["Ecb", "Cbc"]
Template_Encrypt_CryptoMode_Parser = LiteralParser[Template_Encrypt_CryptoMode, int](
    name='Template_Encrypt_CryptoMode',
    literal_map={
        'Ecb': 0,
        'Cbc': 1,
    },
)
Alignment = Literal["Right", "Left"]
Alignment_Parser = LiteralParser[Alignment, int](
    name='Alignment',
    literal_map={
        'Right': 1,
        'Left': 0,
    },
)
Project_VhlSettings125Khz_TTFModType_TTFMod = Literal["ModManchester", "ModBiphase", "ModNRZ", "ModHID"]
Project_VhlSettings125Khz_TTFModType_TTFMod_Parser = LiteralParser[Project_VhlSettings125Khz_TTFModType_TTFMod, int](
    name='Project_VhlSettings125Khz_TTFModType_TTFMod',
    literal_map={
        'ModManchester': 16,
        'ModBiphase': 32,
        'ModNRZ': 48,
        'ModHID': 80,
    },
)
Protocols_KeyboardEmulation_UsbInterfaceSubClass_Value = Literal["NoBoot", "Boot"]
Protocols_KeyboardEmulation_UsbInterfaceSubClass_Value_Parser = LiteralParser[Protocols_KeyboardEmulation_UsbInterfaceSubClass_Value, int](
    name='Protocols_KeyboardEmulation_UsbInterfaceSubClass_Value',
    literal_map={
        'NoBoot': 0,
        'Boot': 1,
    },
)
Lg_ReadSMStatus_MIMVersion = Literal["MIM022", "MIM256", "MIM1024"]
Lg_ReadSMStatus_MIMVersion_Parser = LiteralParser[Lg_ReadSMStatus_MIMVersion, int](
    name='Lg_ReadSMStatus_MIMVersion',
    literal_map={
        'MIM022': 0,
        'MIM256': 2,
        'MIM1024': 3,
    },
)
class Custom_AdminData_FactoryResetFirmwareVersion_Value_Entry(NamedTuple):
    FirmwareId: 'int'
    FwVersionMajor: 'int'
    FwVersionMinor: 'int'
    FwVersionBuild: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FirmwareId={ repr(self.FirmwareId) }')
        non_default_args.append(f'FwVersionMajor={ repr(self.FwVersionMajor) }')
        non_default_args.append(f'FwVersionMinor={ repr(self.FwVersionMinor) }')
        non_default_args.append(f'FwVersionBuild={ repr(self.FwVersionBuild) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Desfire_Authenticate_SecureMessaging = Literal["Native", "EV1", "EV2"]
Desfire_Authenticate_SecureMessaging_Parser = LiteralParser[Desfire_Authenticate_SecureMessaging, int](
    name='Desfire_Authenticate_SecureMessaging',
    literal_map={
        'Native': 1,
        'EV1': 0,
        'EV2': 2,
    },
)
Project_MobileId_TriggerFromDistance_Value = Literal["Disabled", "Enabled"]
Project_MobileId_TriggerFromDistance_Value_Parser = LiteralParser[Project_MobileId_TriggerFromDistance_Value, int](
    name='Project_MobileId_TriggerFromDistance_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
    },
)
DiversificationMode = Literal["NoDiversification", "ModeAv1", "ModeAv2", "ModeAv1Des1Round"]
DiversificationMode_Parser = LiteralParser[DiversificationMode, int](
    name='DiversificationMode',
    literal_map={
        'NoDiversification': 0,
        'ModeAv1': 1,
        'ModeAv2': 2,
        'ModeAv1Des1Round': 17,
    },
)
class Iso14b_SetTransparentSettings_Tags_Entry(NamedTuple):
    ID: 'int'
    Value: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'ID={ repr(self.ID) }')
        non_default_args.append(f'Value={ repr(self.Value) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Protocols_MagstripeEmulation_Encoding_Value = Literal["Numeric", "Alphanumeric"]
Protocols_MagstripeEmulation_Encoding_Value_Parser = LiteralParser[Protocols_MagstripeEmulation_Encoding_Value, int](
    name='Protocols_MagstripeEmulation_Encoding_Value',
    literal_map={
        'Numeric': 4,
        'Alphanumeric': 6,
    },
)
Mce_Enable_Mode = Literal["Disable", "Enable"]
Mce_Enable_Mode_Parser = LiteralParser[Mce_Enable_Mode, int](
    name='Mce_Enable_Mode',
    literal_map={
        'Disable': 0,
        'Enable': 1,
    },
)
class CardTypes125KhzPart1(NamedTuple):
    TTF: 'bool'
    Hitag2B: 'bool'
    Hitag2M: 'bool'
    Hitag1S: 'bool'
    HidIoprox: 'bool'
    HidProx: 'bool'
    HidAwid: 'bool'
    HidIndala: 'bool'
    Quadrakey: 'bool'
    Keri: 'bool'
    HidProx32: 'bool'
    Pyramid: 'bool'
    EM4450: 'bool'
    EM4100: 'bool'
    EM4205: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'TTF={ repr(self.TTF) }')
        non_default_args.append(f'Hitag2B={ repr(self.Hitag2B) }')
        non_default_args.append(f'Hitag2M={ repr(self.Hitag2M) }')
        non_default_args.append(f'Hitag1S={ repr(self.Hitag1S) }')
        non_default_args.append(f'HidIoprox={ repr(self.HidIoprox) }')
        non_default_args.append(f'HidProx={ repr(self.HidProx) }')
        non_default_args.append(f'HidAwid={ repr(self.HidAwid) }')
        non_default_args.append(f'HidIndala={ repr(self.HidIndala) }')
        non_default_args.append(f'Quadrakey={ repr(self.Quadrakey) }')
        non_default_args.append(f'Keri={ repr(self.Keri) }')
        non_default_args.append(f'HidProx32={ repr(self.HidProx32) }')
        non_default_args.append(f'Pyramid={ repr(self.Pyramid) }')
        non_default_args.append(f'EM4450={ repr(self.EM4450) }')
        non_default_args.append(f'EM4100={ repr(self.EM4100) }')
        non_default_args.append(f'EM4205={ repr(self.EM4205) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class CardTypes125KhzPart1_Dict(TypedDict):
    TTF: 'NotRequired[bool]'
    Hitag2B: 'NotRequired[bool]'
    Hitag2M: 'NotRequired[bool]'
    Hitag1S: 'NotRequired[bool]'
    HidIoprox: 'NotRequired[bool]'
    HidProx: 'NotRequired[bool]'
    HidAwid: 'NotRequired[bool]'
    HidIndala: 'NotRequired[bool]'
    Quadrakey: 'NotRequired[bool]'
    Keri: 'NotRequired[bool]'
    HidProx32: 'NotRequired[bool]'
    Pyramid: 'NotRequired[bool]'
    EM4450: 'NotRequired[bool]'
    EM4100: 'NotRequired[bool]'
    EM4205: 'NotRequired[bool]'
class VhlCfg_File_Iso15ExtendedBlockList_Value_Entry(NamedTuple):
    StartBlock: 'int'
    NumberOfBlocks: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'StartBlock={ repr(self.StartBlock) }')
        non_default_args.append(f'NumberOfBlocks={ repr(self.NumberOfBlocks) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Project_VhlSettingsLegic_RfStdList_RfStds = Literal["RfStdLegic", "RfStdIso15693", "RfStdIso14443A"]
Project_VhlSettingsLegic_RfStdList_RfStds_Parser = LiteralParser[Project_VhlSettingsLegic_RfStdList_RfStds, int](
    name='Project_VhlSettingsLegic_RfStdList_RfStds',
    literal_map={
        'RfStdLegic': 0,
        'RfStdIso15693': 1,
        'RfStdIso14443A': 2,
    },
)
Ultralight_AuthUser_CryptoMode = Literal["TripleDES", "AES"]
Ultralight_AuthUser_CryptoMode_Parser = LiteralParser[Ultralight_AuthUser_CryptoMode, int](
    name='Ultralight_AuthUser_CryptoMode',
    literal_map={
        'TripleDES': 0,
        'AES': 1,
    },
)
Device_Run_SetBusAdrOnUploadViaIso14443_Value = Literal["Disabled", "Enabled", "Auto"]
Device_Run_SetBusAdrOnUploadViaIso14443_Value_Parser = LiteralParser[Device_Run_SetBusAdrOnUploadViaIso14443_Value, int](
    name='Device_Run_SetBusAdrOnUploadViaIso14443_Value',
    literal_map={
        'Disabled': 0,
        'Enabled': 1,
        'Auto': 2,
    },
)
Sys_CfgLoadFinish_FinalizeAction = Literal["CancelCfgLoad", "FinalizeCfgLoadWithoutReboot", "FinalizeCfgLoadWithReboot"]
Sys_CfgLoadFinish_FinalizeAction_Parser = LiteralParser[Sys_CfgLoadFinish_FinalizeAction, int](
    name='Sys_CfgLoadFinish_FinalizeAction',
    literal_map={
        'CancelCfgLoad': 0,
        'FinalizeCfgLoadWithoutReboot': 1,
        'FinalizeCfgLoadWithReboot': 2,
    },
)
MaxBaudrateIso14443 = Literal["Dri106Dsi106", "Dri212Dsi106", "Dri424Dsi106", "Dri848Dsi106", "Dri106Dsi212", "Dri212Dsi212", "Dri424Dsi212", "Dri848Dsi212", "Dri106Dsi424", "Dri212Dsi424", "Dri424Dsi424", "Dri848Dsi424", "Dri106Dsi848", "Dri212Dsi848", "Dri424Dsi848", "Dri848Dsi848"]
MaxBaudrateIso14443_Parser = LiteralParser[MaxBaudrateIso14443, int](
    name='MaxBaudrateIso14443',
    literal_map={
        'Dri106Dsi106': 0,
        'Dri212Dsi106': 1,
        'Dri424Dsi106': 2,
        'Dri848Dsi106': 3,
        'Dri106Dsi212': 4,
        'Dri212Dsi212': 5,
        'Dri424Dsi212': 6,
        'Dri848Dsi212': 7,
        'Dri106Dsi424': 8,
        'Dri212Dsi424': 9,
        'Dri424Dsi424': 10,
        'Dri848Dsi424': 11,
        'Dri106Dsi848': 12,
        'Dri212Dsi848': 13,
        'Dri424Dsi848': 14,
        'Dri848Dsi848': 15,
    },
)
Hitag_Select_SelMode = Literal["Select", "Quiet", "AuthPwd", "H2AuthOnlyPwd"]
Hitag_Select_SelMode_Parser = LiteralParser[Hitag_Select_SelMode, int](
    name='Hitag_Select_SelMode',
    literal_map={
        'Select': 0,
        'Quiet': 1,
        'AuthPwd': 2,
        'H2AuthOnlyPwd': 3,
    },
)
class VhlCfg_File_DesfireEv2FormatPiccKeys_PiccLevelKeylist_Entry(NamedTuple):
    KeyNo: 'int'
    PiccCurKeyIdx: 'DesfireKeyIdx'
    PiccNewKeyIdx: 'DesfireKeyIdx'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'KeyNo={ repr(self.KeyNo) }')
        non_default_args.append(f'PiccCurKeyIdx={ repr(self.PiccCurKeyIdx) }')
        non_default_args.append(f'PiccNewKeyIdx={ repr(self.PiccNewKeyIdx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
CryptoAlgorithm = Literal["DES", "TripleDES", "ThreeKeyTripleDES", "AES", "MifareClassic"]
CryptoAlgorithm_Parser = LiteralParser[CryptoAlgorithm, int](
    name='CryptoAlgorithm',
    literal_map={
        'DES': 1,
        'TripleDES': 2,
        'ThreeKeyTripleDES': 3,
        'AES': 4,
        'MifareClassic': 5,
    },
)
Protocols_Network_DetectIpEnable_Value = Literal["Yes", "No"]
Protocols_Network_DetectIpEnable_Value_Parser = LiteralParser[Protocols_Network_DetectIpEnable_Value, int](
    name='Protocols_Network_DetectIpEnable_Value',
    literal_map={
        'Yes': 1,
        'No': 0,
    },
)
TemplateBitorder = Literal["Lsb", "Msb"]
TemplateBitorder_Parser = LiteralParser[TemplateBitorder, int](
    name='TemplateBitorder',
    literal_map={
        'Lsb': 0,
        'Msb': 1,
    },
)
Device_Boot_ConfigCardState_Value = Literal["None", "Ok", "ReadFailure", "InvalidConfigSecurityCode", "InvalidCustomerKey"]
Device_Boot_ConfigCardState_Value_Parser = LiteralParser[Device_Boot_ConfigCardState_Value, int](
    name='Device_Boot_ConfigCardState_Value',
    literal_map={
        'None': 0,
        'Ok': 1,
        'ReadFailure': 2,
        'InvalidConfigSecurityCode': 3,
        'InvalidCustomerKey': 4,
    },
)
class UsbHost_SetupPipes_Pipes_Entry(NamedTuple):
    No: 'int'
    Type: 'Type'
    FrameSize: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'No={ repr(self.No) }')
        non_default_args.append(f'Type={ repr(self.Type) }')
        non_default_args.append(f'FrameSize={ repr(self.FrameSize) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Desfire_AuthExtKey_SecureMessaging = Literal["Native", "EV1", "EV2"]
Desfire_AuthExtKey_SecureMessaging_Parser = LiteralParser[Desfire_AuthExtKey_SecureMessaging, int](
    name='Desfire_AuthExtKey_SecureMessaging',
    literal_map={
        'Native': 1,
        'EV1': 0,
        'EV2': 2,
    },
)
DHWCtrl_AesDecrypt_WrappedKeyNr = Literal["WrapNone", "WrapDHUK"]
DHWCtrl_AesDecrypt_WrappedKeyNr_Parser = LiteralParser[DHWCtrl_AesDecrypt_WrappedKeyNr, int](
    name='DHWCtrl_AesDecrypt_WrappedKeyNr',
    literal_map={
        'WrapNone': 0,
        'WrapDHUK': 1,
    },
)
Project_VhlSettings_ForceReselect_Value = Literal["False", "True"]
Project_VhlSettings_ForceReselect_Value_Parser = LiteralParser[Project_VhlSettings_ForceReselect_Value, int](
    name='Project_VhlSettings_ForceReselect_Value',
    literal_map={
        'False': 0,
        'True': 1,
    },
)
class TemplateFilter(NamedTuple):
    """
    For every of these filter bits, a specific data conversion mechanism is
    specified. This mechanism is applied to a TemplateCommand if the filterbit is
    set.
    
    The activated filters are applied ordered by there value. Starting with the
    smallest value.
    """
    BcdToBin: 'bool' = False
    BinToAscii: 'bool' = False
    Unpack: 'bool' = False
    BinToBcd: 'bool' = False
    SwapNibbles: 'bool' = False
    Pack: 'bool' = False
    AsciiToBin: 'bool' = False
    Reverse: 'bool' = False
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        if self.BcdToBin != False:
            non_default_args.append(f'BcdToBin={ repr(self.BcdToBin) }')
        if self.BinToAscii != False:
            non_default_args.append(f'BinToAscii={ repr(self.BinToAscii) }')
        if self.Unpack != False:
            non_default_args.append(f'Unpack={ repr(self.Unpack) }')
        if self.BinToBcd != False:
            non_default_args.append(f'BinToBcd={ repr(self.BinToBcd) }')
        if self.SwapNibbles != False:
            non_default_args.append(f'SwapNibbles={ repr(self.SwapNibbles) }')
        if self.Pack != False:
            non_default_args.append(f'Pack={ repr(self.Pack) }')
        if self.AsciiToBin != False:
            non_default_args.append(f'AsciiToBin={ repr(self.AsciiToBin) }')
        if self.Reverse != False:
            non_default_args.append(f'Reverse={ repr(self.Reverse) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
    @classmethod
    def NoFilter(cls, BcdToBin: bool = False, BinToAscii: bool = False, Unpack: bool = False, BinToBcd: bool = False, SwapNibbles: bool = False, Pack: bool = False, AsciiToBin: bool = False, Reverse: bool = False) -> Self:
        return cls(BcdToBin, BinToAscii, Unpack, BinToBcd, SwapNibbles, Pack, AsciiToBin, Reverse)
class TemplateFilter_Dict(TypedDict):
    """
    For every of these filter bits, a specific data conversion mechanism is
    specified. This mechanism is applied to a TemplateCommand if the filterbit is
    set.
    
    The activated filters are applied ordered by there value. Starting with the
    smallest value.
    """
    BcdToBin: 'NotRequired[bool]'
    BinToAscii: 'NotRequired[bool]'
    Unpack: 'NotRequired[bool]'
    BinToBcd: 'NotRequired[bool]'
    SwapNibbles: 'NotRequired[bool]'
    Pack: 'NotRequired[bool]'
    AsciiToBin: 'NotRequired[bool]'
    Reverse: 'NotRequired[bool]'
Desfire_AuthExtKey_CryptoMode = Literal["DES", "TripleDES", "ThreeKeyTripleDES", "AES"]
Desfire_AuthExtKey_CryptoMode_Parser = LiteralParser[Desfire_AuthExtKey_CryptoMode, int](
    name='Desfire_AuthExtKey_CryptoMode',
    literal_map={
        'DES': 1,
        'TripleDES': 2,
        'ThreeKeyTripleDES': 3,
        'AES': 4,
    },
)
FileType = Literal["FileByDfName", "FileByFileId", "FileByApduCmd"]
FileType_Parser = LiteralParser[FileType, int](
    name='FileType',
    literal_map={
        'FileByDfName': 0,
        'FileByFileId': 1,
        'FileByApduCmd': 2,
    },
)
class VHL_Setup_SelectFileCmdList_Entry(NamedTuple):
    FileSpecifier: 'FileSpecifier'
    Name: 'Optional[bytes]' = None
    Path: 'Optional[bytes]' = None
    ApduCommand: 'Optional[bytes]' = None
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'FileSpecifier={ repr(self.FileSpecifier) }')
        if self.Name != None:
            non_default_args.append(f'Name={ repr(self.Name) }')
        if self.Path != None:
            non_default_args.append(f'Path={ repr(self.Path) }')
        if self.ApduCommand != None:
            non_default_args.append(f'ApduCommand={ repr(self.ApduCommand) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Iso14b_Request_FSCI = Literal["Bytes16", "Bytes24", "Bytes32", "Bytes40", "Bytes48", "Bytes64", "Bytes96", "Bytes128", "Bytes256"]
Iso14b_Request_FSCI_Parser = LiteralParser[Iso14b_Request_FSCI, int](
    name='Iso14b_Request_FSCI',
    literal_map={
        'Bytes16': 0,
        'Bytes24': 1,
        'Bytes32': 2,
        'Bytes40': 3,
        'Bytes48': 4,
        'Bytes64': 5,
        'Bytes96': 6,
        'Bytes128': 7,
        'Bytes256': 8,
    },
)
Device_VhlSettings125Khz_ModulationType_TTFMod = Literal["ModManchester", "ModBiphase", "ModNRZ", "ModHID"]
Device_VhlSettings125Khz_ModulationType_TTFMod_Parser = LiteralParser[Device_VhlSettings125Khz_ModulationType_TTFMod, int](
    name='Device_VhlSettings125Khz_ModulationType_TTFMod',
    literal_map={
        'ModManchester': 16,
        'ModBiphase': 32,
        'ModNRZ': 48,
        'ModHID': 80,
    },
)
IoPort = Literal["GreenLed", "RedLed", "Beeper", "Relay", "Input0", "Input1", "BlueLed", "TamperAlarm", "Gpio0", "Gpio1", "Gpio2", "Gpio3", "Gpio4", "Gpio5", "Gpio6", "Gpio7", "CustomVled0", "CustomVled1", "CustomVled2", "CustomVled3", "CustomVled4", "CustomVled5", "CustomVled6", "CustomVled7", "CustomVled8", "CustomVled9", "CustomVled10", "CustomVled11", "CustomVled12", "CustomVled13", "CustomVled14", "CustomVled15"]
IoPort_Parser = LiteralParser[IoPort, int](
    name='IoPort',
    literal_map={
        'GreenLed': 0,
        'RedLed': 1,
        'Beeper': 2,
        'Relay': 3,
        'Input0': 4,
        'Input1': 5,
        'BlueLed': 6,
        'TamperAlarm': 7,
        'Gpio0': 8,
        'Gpio1': 9,
        'Gpio2': 10,
        'Gpio3': 11,
        'Gpio4': 12,
        'Gpio5': 13,
        'Gpio6': 14,
        'Gpio7': 15,
        'CustomVled0': 64,
        'CustomVled1': 65,
        'CustomVled2': 66,
        'CustomVled3': 67,
        'CustomVled4': 68,
        'CustomVled5': 69,
        'CustomVled6': 70,
        'CustomVled7': 71,
        'CustomVled8': 72,
        'CustomVled9': 73,
        'CustomVled10': 74,
        'CustomVled11': 75,
        'CustomVled12': 76,
        'CustomVled13': 77,
        'CustomVled14': 78,
        'CustomVled15': 79,
    },
)
Lg_GenSetRead_WriteExMode = Literal["ArbitraryWriting", "DecrementOnly", "IncrementOnly", "InvalidMode"]
Lg_GenSetRead_WriteExMode_Parser = LiteralParser[Lg_GenSetRead_WriteExMode, int](
    name='Lg_GenSetRead_WriteExMode',
    literal_map={
        'ArbitraryWriting': 0,
        'DecrementOnly': 1,
        'IncrementOnly': 2,
        'InvalidMode': 3,
    },
)
FileSpecifier = Literal["SelectByName", "SelectByPath", "SelectByAPDU"]
FileSpecifier_Parser = LiteralParser[FileSpecifier, int](
    name='FileSpecifier',
    literal_map={
        'SelectByName': 0,
        'SelectByPath': 1,
        'SelectByAPDU': 2,
    },
)
class KeyAccessRights_KeySettings(NamedTuple):
    """
    Access rights and key info
    
    Access rights: By default, all operations are allowed. With this bitmask,
    however, this key can be locked for certain operations.
    """
    IsVersion: 'bool'
    IsDivInfo: 'bool'
    IsDivInfoVhl: 'bool'
    DenyFormat: 'bool'
    DenyWrite: 'bool'
    DenyRead: 'bool'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'IsVersion={ repr(self.IsVersion) }')
        non_default_args.append(f'IsDivInfo={ repr(self.IsDivInfo) }')
        non_default_args.append(f'IsDivInfoVhl={ repr(self.IsDivInfoVhl) }')
        non_default_args.append(f'DenyFormat={ repr(self.DenyFormat) }')
        non_default_args.append(f'DenyWrite={ repr(self.DenyWrite) }')
        non_default_args.append(f'DenyRead={ repr(self.DenyRead) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class KeyAccessRights_KeySettings_Dict(TypedDict):
    """
    Access rights and key info
    
    Access rights: By default, all operations are allowed. With this bitmask,
    however, this key can be locked for certain operations.
    """
    IsVersion: 'NotRequired[bool]'
    IsDivInfo: 'NotRequired[bool]'
    IsDivInfoVhl: 'NotRequired[bool]'
    DenyFormat: 'NotRequired[bool]'
    DenyWrite: 'NotRequired[bool]'
    DenyRead: 'NotRequired[bool]'
Eth_OpenTcpConnection_ConnectionReason = Literal["Powerup", "LinkChange", "SessionkeyTimeout", "Message", "UdpIntrospection", "Reset", "FailedConnectionTrials"]
Eth_OpenTcpConnection_ConnectionReason_Parser = LiteralParser[Eth_OpenTcpConnection_ConnectionReason, int](
    name='Eth_OpenTcpConnection_ConnectionReason',
    literal_map={
        'Powerup': 1,
        'LinkChange': 2,
        'SessionkeyTimeout': 4,
        'Message': 8,
        'UdpIntrospection': 16,
        'Reset': 32,
        'FailedConnectionTrials': 32768,
    },
)
class VhlCfg_File_FelicaAreaList_Value_Entry(NamedTuple):
    BlockAddress: 'int'
    BlockNr: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'BlockAddress={ repr(self.BlockAddress) }')
        non_default_args.append(f'BlockNr={ repr(self.BlockNr) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
class Mif_SectorSwitch_SectorSpec_Entry(NamedTuple):
    BlockAddress: 'int'
    SectorKeyIdx: 'int'
    def __repr__(self) -> str:
        non_default_args: List[str] = []
        non_default_args.append(f'BlockAddress={ repr(self.BlockAddress) }')
        non_default_args.append(f'SectorKeyIdx={ repr(self.SectorKeyIdx) }')
        return f'{type(self).__name__}({", ".join(non_default_args)})'
Hitag_Request_TagType = Literal["HitagS", "Hitag1", "Hitag2Manchester", "Hitag2Biphase"]
Hitag_Request_TagType_Parser = LiteralParser[Hitag_Request_TagType, int](
    name='Hitag_Request_TagType',
    literal_map={
        'HitagS': 0,
        'Hitag1': 1,
        'Hitag2Manchester': 2,
        'Hitag2Biphase': 3,
    },
)
Type = Literal["Control", "Interrupt", "Bulk", "Isochronous"]
Type_Parser = LiteralParser[Type, int](
    name='Type',
    literal_map={
        'Control': 0,
        'Interrupt': 1,
        'Bulk': 2,
        'Isochronous': 3,
    },
)
Iso14a_RequestATS_FSDI = Literal["Bytes16", "Bytes24", "Bytes32", "Bytes40", "Bytes48", "Bytes64", "Bytes96", "Bytes128", "Bytes256"]
Iso14a_RequestATS_FSDI_Parser = LiteralParser[Iso14a_RequestATS_FSDI, int](
    name='Iso14a_RequestATS_FSDI',
    literal_map={
        'Bytes16': 0,
        'Bytes24': 1,
        'Bytes32': 2,
        'Bytes40': 3,
        'Bytes48': 4,
        'Bytes64': 5,
        'Bytes96': 6,
        'Bytes128': 7,
        'Bytes256': 8,
    },
)
Parity = Literal["None", "Even", "Odd"]
Parity_Parser = LiteralParser[Parity, int](
    name='Parity',
    literal_map={
        'None': 78,
        'Even': 69,
        'Odd': 79,
    },
)
Device_Keypad_KeyPressSignal_SignalType = Literal["ShortBeep", "LongBeep"]
Device_Keypad_KeyPressSignal_SignalType_Parser = LiteralParser[Device_Keypad_KeyPressSignal_SignalType, int](
    name='Device_Keypad_KeyPressSignal_SignalType',
    literal_map={
        'ShortBeep': 0,
        'LongBeep': 1,
    },
)
VhlCfg_File_DesfireFormatResetPicc_ResetPicc = Literal["EncodeAppOnly", "Reset"]
VhlCfg_File_DesfireFormatResetPicc_ResetPicc_Parser = LiteralParser[VhlCfg_File_DesfireFormatResetPicc_ResetPicc, int](
    name='VhlCfg_File_DesfireFormatResetPicc_ResetPicc',
    literal_map={
        'EncodeAppOnly': 0,
        'Reset': 1,
    },
)
Iso14b_Attrib_TR1 = Literal["Numerator80", "Numerator64", "Numerator16"]
Iso14b_Attrib_TR1_Parser = LiteralParser[Iso14b_Attrib_TR1, int](
    name='Iso14b_Attrib_TR1',
    literal_map={
        'Numerator80': 0,
        'Numerator64': 1,
        'Numerator16': 2,
    },
)
Protocols_Network_NicFlowControl_Value = Literal["Enabled", "Disabled"]
Protocols_Network_NicFlowControl_Value_Parser = LiteralParser[Protocols_Network_NicFlowControl_Value, int](
    name='Protocols_Network_NicFlowControl_Value',
    literal_map={
        'Enabled': 1,
        'Disabled': 0,
    },
)