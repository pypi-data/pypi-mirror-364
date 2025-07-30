
from .commands import *
from .configuration import *
from .common import FrameExecutor
from .baltech_script import BaltechScript
from .template import Template
class Commands(FrameExecutor):
    @property
    def ASK_SecuraKeyRead(self) -> ASK_SecuraKeyRead:
        """
        Returns data of SecuraKey tags (read only tag).
        """
        return ASK_SecuraKeyRead(self)
    @property
    def ASK_GproxRead(self) -> ASK_GproxRead:
        """
        Returns data of G-Prox tags (read only tag).
        """
        return ASK_GproxRead(self)
    @property
    def ASK_CotagRead(self) -> ASK_CotagRead:
        """
        Returns data of Cotag tags (read only tag).
        """
        return ASK_CotagRead(self)
    @property
    def AR_SetMode(self) -> AR_SetMode:
        """
        This command controls Autoread mode at runtime. Usually, the Autoread
        subsystem will be stared at boot time if the reader is [ configured to work
        autonomously](../cfg/autoread.xml#Device.Boot.StartAutoreadAtPowerup).
        However, you can still enable and disable Autoread at runtime. This is e.g.
        needed if you use [ VHL & Autoread](https://docs.baltech.de/developers/map-
        vhl-autoread.html) in combination, so you can interrupt Autoread to run VHL
        commands.
        
        **_AR.SetMode_ automatically empties the reader's message buffer. This ensures
        that the next[ AR.GetMessage](.#AR.GetMessage) you run doesn't return "old"
        data from a card detected before running _AR.SetMode_ .**
        """
        return AR_SetMode(self)
    @property
    def AR_GetMessage(self) -> AR_GetMessage:
        """
        This command checks if a card has been presented to the reader since the last
        _AR.GetMessage_ execution. If yes, the card identification will be returned in
        _MsgData_. If no, the [AR.ErrNoMessage](.#AR.ErrNoMessage) status code will be
        returned.
        
        Apart from card identifications, some readers support additional types of
        messages, e.g. PINs entered via the keyboard. This information is returned in
        _MsgType_.
        
        **Read results are buffered in the reader's memory for 5 seconds, i.e. that's
        the time frame you have to execute this command.**
        """
        return AR_GetMessage(self)
    @property
    def AR_RunScript(self) -> AR_RunScript:
        """
        This command runs a [BaltechScript](../cfg/baltechscript.xml). This is a small
        sequence of instructions for the reader to execute. Typically, it's used to
        control reader feedback, i.e. LEDs, beeper, relay, and other I/O ports when
        you have highly specific requirements and/or want to store the script on the
        reader.
        
        **Instead of _AR.RunScript_ , we recommend the[ UI command
        set](userinterface.xml) as it's easier to implement and sufficient for the
        majority of use cases.**
        
        ## Script structure
        
        A script consists of the following parts:
        
          * _Frame value_ (e.g. 0x01 for Enable)
          * _Port_ (e.g. 0x00 for the green LED)
          * _Parameters_ if applicable (e.g. number of repetitions and delay after each change of state)
        
        ## Examples
        
        Here are a few examples of how to create a script. We'll use the following
        script commands as they're the most important ones:
        
          * [Enable](../cfg/baltechscript.xml#BaltechScript.Enable)
          * [Disable](../cfg/baltechscript.xml#BaltechScript.Disable)
          * [Toggle](../cfg/baltechscript.xml#BaltechScript.Toggle)
          * [ToggleInverted](../cfg/baltechscript.xml#BaltechScript.ToggleInverted)
        
        ### Single script to control 1 port
        
        In this example, we'll switch on the green LED permanently. To do so, we need
        to run the [Enable](../cfg/baltechscript.xml#BaltechScript.Enable) script as
        follows:
        
        `01 00`
        
          * _01_ is the frame value for _Enable_.
          * _00_ is the parameter value for the _green LED_.
        
        ### Sequence of scripts
        
        You can run a sequence of scripts in parallel by concatenating them.
        
        #### Simultaneous feedback sequence
        
        In this example, we'll switch on the green LED permanently. At the same time,
        we have the beeper beep 3 times for 200 ms. To do so, we extend the _Enable_
        script from the above example with a
        [Toggle](../cfg/baltechscript.xml#BaltechScript.Toggle) script:
        
        `01 00 03 02 03 02`
        
        The _Toggle_ script in this sequence is composed as follows:
        
          * _03_ is the frame value for _Toggle_.
          * _02_ is the parameter for the _beeper_.
          * _03_ is the _repeat count_.
          * _02_ is the _delay_ : 
        
        The unit of this value is 1/10 sec, i.e. it's 200 ms in this example. This
        time period applies to the length of the beep and the delay afterwards, i.e.
        you have a duration of 2x200 ms per beep and a duration of 1200 ms for the
        entire sequence.
        
        #### Consecutive feedback sequence
        
        Concatenated scripts are always executed in parallel. However, you can still
        produce a consecutive feedback sequence using
        [ToggleInverted](../cfg/baltechscript.xml#BaltechScript.ToggleInverted) and an
        appropriate delay. In this example, we'll use the toggle script from the above
        example to have the beeper beep 3 times for 200 ms. After the third beep, the
        red LED is enabled:
        
        `03 02 03 02 06 01 01 0C`
        
        The _ToggleInverted_ script in this sequence is composed as follows:
        
          * _06_ is the frame value for _ToggleInverted_.
          * _01_ is the parameter for the _red LED_.
          * _01_ is the _repeat count_.
          * _0C_ is the _delay_ : 
        
        The unit of this value is 1/10 sec, i.e. it's 1200 ms in this example. This
        corresponds to the duration of the _Toggle_ script that runs in parallel (see
        also previous example). Thus the LED (controlled by the _ToggleInverted_
        script) turns on after the beeper sequence (controlled by the _Toggle_ script)
        is completed.
        """
        return AR_RunScript(self)
    @property
    def AR_RestrictScanCardFamilies(self) -> AR_RestrictScanCardFamilies:
        """
        This command restricts the card families that Autoread will scan for. By
        selecting only the required card families, the detection time on card
        presentation will be minimized.
        """
        return AR_RestrictScanCardFamilies(self)
    @property
    def Bat_Run(self) -> Bat_Run:
        """
        Run a batch of BRP commands Via condition bits, it is possible to run sub-
        commands selectively. When this command is started, all condition bits are
        reset to 0. Currently, there are no commands that support setting condition
        bits!
        """
        return Bat_Run(self)
    @property
    def Bat_CheckStatus(self) -> Bat_CheckStatus:
        """
        This command checks the status of the last action-sub-command (i.e. sub-
        command that did not start with "Check..."). Depending on the result it sets
        (or clears, if _Invert_ is _true_) a condition bit.
        """
        return Bat_CheckStatus(self)
    @property
    def Bat_CheckAny(self) -> Bat_CheckAny:
        """
        This command checks if one or more of a list of condition bits is set.
        """
        return Bat_CheckAny(self)
    @property
    def Bat_CheckTemplate(self) -> Bat_CheckTemplate:
        """
        This command checks if the result of the last action-sub-command (i.e. sub-
        command that did not start with "Check...") matches a template. Depending on
        the result it sets (or clears, if _Invert_ is _true_) a condition bit.
        """
        return Bat_CheckTemplate(self)
    @property
    def Bat_Delay(self) -> Bat_Delay:
        """
        Delays execution for a specified amount of ms. This command must only be
        executed within a batch command. Batch commands including the Bat.Delay
        command cannot be cancelled by sending data to the reader.
        """
        return Bat_Delay(self)
    @property
    def BlePeriph_DefineService(self) -> BlePeriph_DefineService:
        """
        This command registers a new BLE service. When a BLE Central tries to discover
        services, this service will be amongst the available ones.
        
        If currently enabled, this method disables BLE implicitly. To start the
        service, call [BlePeriph.Enable(true)](.#BlePeriph.Enable) afterwards.
        
        **A maximum of 5 characteristics may be defined for the BLE service. The total
        size of all characteristics may not exceed 1536 bytes.**
        """
        return BlePeriph_DefineService(self)
    @property
    def BlePeriph_Enable(self) -> BlePeriph_Enable:
        """
        This command starts/stops the advertisement of the reader as a BLE Peripheral,
        so you can respond to connection and other requests.
        """
        return BlePeriph_Enable(self)
    @property
    def BlePeriph_SetAdvertisingData(self) -> BlePeriph_SetAdvertisingData:
        """
        This command defines the data to be advertised by the reader. If advertisement
        is currently [enabled](.#BlePeriph.Enable), the new data will be used
        immediately.
        """
        return BlePeriph_SetAdvertisingData(self)
    @property
    def BlePeriph_WriteCharacteristic(self) -> BlePeriph_WriteCharacteristic:
        """
        This command changes the value of a characteristic. All future reads from the
        Central or [BlePeriph.ReadCharacteristic](.#BlePeriph.ReadCharacteristic) from
        the BRP host will return the new value.
        
        If the Central has registered a notification/indication for this
        characteristic, the reader will automatically send a corresponding message to
        the Central.
        
        **A characteristic can only be written when BLE is[
        enabled](.#BlePeriph.Enable) .**
        """
        return BlePeriph_WriteCharacteristic(self)
    @property
    def BlePeriph_ReadCharacteristic(self) -> BlePeriph_ReadCharacteristic:
        """
        This command retrieves the current value of a characteristic. A characteristic
        will be initialized to _00 00 ... 00_ when calling
        [BlePeriph.Enable](.#BlePeriph.Enable) and will be modified by either the BRP
        host ([BlePeriph.WriteCharacteristic](.#BlePeriph.WriteCharacteristic)) or the
        BLE Central (via a write to the characteristic).
        
        **A characteristic can only be read when BLE is[ enabled](.#BlePeriph.Enable)
        .**
        """
        return BlePeriph_ReadCharacteristic(self)
    @property
    def BlePeriph_GetEvents(self) -> BlePeriph_GetEvents:
        """
        This command returns a bitmask of all events that have occurred since the last
        call of _BlePeriph.GetEvents_.
        """
        return BlePeriph_GetEvents(self)
    @property
    def BlePeriph_IsConnected(self) -> BlePeriph_IsConnected:
        """
        This command is used to check the current connection status. If connected, it
        returns the device address of the connected BLE central.
        """
        return BlePeriph_IsConnected(self)
    @property
    def BlePeriph_GetRSSI(self) -> BlePeriph_GetRSSI:
        """
        This command returns the RSSI value of the connected BLE Central.
        """
        return BlePeriph_GetRSSI(self)
    @property
    def BlePeriph_CloseConnection(self) -> BlePeriph_CloseConnection:
        """
        This command closes the active connection with a BLE Central.
        """
        return BlePeriph_CloseConnection(self)
    @property
    def CardEmu_GetMaxFrameSize(self) -> CardEmu_GetMaxFrameSize:
        """
        This command returns the maximum size of a single ISO14443-3 frame that may be
        sent/received via [CardEmu.StartEmu](.#CardEmu.StartEmu) or
        [CardEmu.TransparentCmd](.#CardEmu.TransparentCmd).
        """
        return CardEmu_GetMaxFrameSize(self)
    @property
    def CardEmu_StartEmu(self) -> CardEmu_StartEmu:
        """
        Switch to Passive mode and wait for a ISO1443-3a Request/Anticoll/Select
        sequence and receive the first frame.
        """
        return CardEmu_StartEmu(self)
    @property
    def CardEmu_TransparentCmd(self) -> CardEmu_TransparentCmd:
        """
        Sends a response to the command returned by
        [CardEmu.StartEmu](.#CardEmu.StartEmu) or to the command returned by the last
        [CardEmu.TransparentCmd](.#CardEmu.TransparentCmd).
        """
        return CardEmu_TransparentCmd(self)
    @property
    def CardEmu_GetExternalHfStatus(self) -> CardEmu_GetExternalHfStatus:
        """
        Returns _true_ if an external HF field is detected.
        """
        return CardEmu_GetExternalHfStatus(self)
    @property
    def CardEmu_StartNfc(self) -> CardEmu_StartNfc:
        """
        Switch to Passive mode and wait for an NFC powerup sequence
        """
        return CardEmu_StartNfc(self)
    @property
    def Crypto_EncryptBlock(self) -> Crypto_EncryptBlock:
        """
        This command encrypts an 8-Byte data block given in the _Block_ parameter
        using the SkipJack algorithm. If _KeyIndex_ is set to 0x00, _KeyValue_ will be
        used as encryption key. Otherwise, _KeyIndex_ is interpreted as the index of
        the corresponding entry in the internal key list. _KeyIndex_ = 0x01 denotes
        configuration value 0x81, _KeyIndex_ = 0x02 denotes configuration value 0x82,
        etc.
        """
        return Crypto_EncryptBlock(self)
    @property
    def Crypto_DecryptBlock(self) -> Crypto_DecryptBlock:
        """
        This command decrypts an 8-Byte data block given in the _Block_ parameter
        using the SkipJack algorithm. If _KeyIndex_ is set to 0x00, _KeyValue_ will be
        used as encryption key. Otherwise, _KeyIndex_ is interpreted as the index of
        the corresponding entry in the internal key list. _KeyIndex_ = 0x01 denotes
        configuration value 0x81, _KeyIndex_ = 0x02 denotes configuration value 0x82,
        etc.
        """
        return Crypto_DecryptBlock(self)
    @property
    def Crypto_EncryptBuffer(self) -> Crypto_EncryptBuffer:
        """
        This command encrypts a variable length buffer given in the _Buffer_ parameter
        using the SkipJack algorithm. If _KeyIndex_ is set to 0x00, _KeyValue_ will be
        used as encryption key. Otherwise, _KeyIndex_ is interpreted as the index of
        the corresponding entry in the internal key list. _KeyIndex_ = 0x01 denotes
        configuration value 0x81, _KeyIndex_ = 0x02 denotes configuration value 0x82,
        etc.
        
        The value returned in the _InitialVector_ variable is necessary for CBC
        encryption. If large amounts of data must be encrypted, this command has to be
        called more than once. In this case, the returned _InitialVector_ variable of
        call _i_ of the command has to be specified as the _InitialVector_ parameter
        of call _i+1_.
        """
        return Crypto_EncryptBuffer(self)
    @property
    def Crypto_DecryptBuffer(self) -> Crypto_DecryptBuffer:
        """
        This command decrypts a variable length buffer given in the _Buffer_ parameter
        using the SkipJack algorithm. If _KeyIndex_ is set to 0x00, _KeyValue_ will be
        used as encryption key. Otherwise, _KeyIndex_ is interpreted as the index of
        the corresponding entry in the internal key list. _KeyIndex_ = 0x01 denotes
        configuration value 0x81, _KeyIndex_ = 0x02 denotes configuration value 0x82,
        etc.
        
        The value returned in the _InitialVector_ variable is necessary for CBC
        encryption. If large amounts of data must be encrypted, this command has to be
        called more than once. In this case, the returned _InitialVector_ variable of
        call _i_ of the command has to be specified as the _InitialVector_ parameter
        of call _i+1_.
        """
        return Crypto_DecryptBuffer(self)
    @property
    def Crypto_BalKeyEncryptBuffer(self) -> Crypto_BalKeyEncryptBuffer:
        """
        This command is a special version of the
        [Crypto.EncryptBuffer](.#Crypto.EncryptBuffer) command which always uses a
        customer key to encrypt a buffer of data and inserts a Crypto-Key at a desired
        position before encryption.
        
        The key to insert has to be specified in the _EmbeddedKeyIndex_ parameter. In
        this case, the 10 Byte Key will, on the one hand, replace the data at the
        _EmbeddedKeyPos_ position, and on the other hand, replace the last two Bytes
        by a CRC (16-bit, 8404B, MSB encoded) that is generated on the data contained
        in _Buffer_.
        """
        return Crypto_BalKeyEncryptBuffer(self)
    @property
    def Crypto_GetKeySig(self) -> Crypto_GetKeySig:
        """
        Returns a signature of the ConfigurationKey to identify the MasterCard needed
        for this reader.
        """
        return Crypto_GetKeySig(self)
    @property
    def Crypto_CopyConfigKey(self) -> Crypto_CopyConfigKey:
        """
        Copies the configuration card key 0x0202/0x85
        (_Device/Run/ConfigCardEncryptKey_) to the _Custom/Crypto/Key[x]_ area of the
        Baltech reader's configuration, where _x_ is the index of the target key,
        specified in the _KeyIndex_ parameter.
        
        When a key does not exist, a Baltech standard key is used instead.
        """
        return Crypto_CopyConfigKey(self)
    @property
    def Dbg_ReadLogs(self) -> Dbg_ReadLogs:
        """
        Get next available block of debug data.
        """
        return Dbg_ReadLogs(self)
    @property
    def Dbg_RunCmd(self) -> Dbg_RunCmd:
        """
        Run a command by emulating the corresponding keypress in
        DebugCommandInterface.
        """
        return Dbg_RunCmd(self)
    @property
    def Desfire_ExecCommand(self) -> Desfire_ExecCommand:
        """
        Generic command to communicate to a DESFire card. Depending on the value of
        the _CryptoMode_ parameter, data will be transmitted plain, MACed or
        encrypted.
        
        The DESFire command frame has to be split into two parts, header and data. The
        data block will be encrypted whereas the header block is left unencrypted.
        
        Example: in the Desfire _ChangeKeySettings_ command, the header is empty. The
        encrypted key settings will be transferred in the data block.
        """
        return Desfire_ExecCommand(self)
    @property
    def Desfire_Authenticate(self) -> Desfire_Authenticate:
        """
        This command authenticates a card with the reader. All authentication modes of
        DESFire cards are supported. Subsequent commands, such as
        [Desfire.ExecCommand](.#Desfire.ExecCommand), take the authentication mode
        into account when communicating with a card.
        
        The key used for authentication is specified in the [Device /
        CryptoKey](../cfg/base.xml#Project.CryptoKey) key of the reader's
        configuration.
        """
        return Desfire_Authenticate(self)
    @property
    def Desfire_AuthExtKey(self) -> Desfire_AuthExtKey:
        """
        This command authenticates a card with the reader, similarly to the
        [Desfire.Authenticate](.#Desfire.Authenticate) command, but uses an external
        authentication key provided as a parameter. Allowed are keys with a length of
        8, 16 and 24 Byte.
        
          * 8 Byte keys are always DES keys. 
          * 16 Byte keys can be DES and AES keys. 
          * 24 Byte keys are only used for 3K3DES encryption.
        """
        return Desfire_AuthExtKey(self)
    @property
    def Desfire_SelectApplication(self) -> Desfire_SelectApplication:
        """
        Selects an application of the DESFire card. Has to be called before any file
        specific command.
        """
        return Desfire_SelectApplication(self)
    @property
    def Desfire_ReadData(self) -> Desfire_ReadData:
        """
        Reads data from a Standard or Backup data file.
        """
        return Desfire_ReadData(self)
    @property
    def Desfire_WriteData(self) -> Desfire_WriteData:
        """
        Writes data to a Standard or a Backup data file.
        """
        return Desfire_WriteData(self)
    @property
    def Desfire_ChangeExtKey(self) -> Desfire_ChangeExtKey:
        """
        This command allows to change any key stored on the card.
        
        The key length has to be set according to the desired encryption algorithm:
        
          * DES encryption uses keys of 8 Byte. 
          * 3DES and AES encryption uses keys of 16 Byte. 
          * 3K3DES encryption uses keys of 24 Byte.
        """
        return Desfire_ChangeExtKey(self)
    @property
    def Desfire_ChangeKey(self) -> Desfire_ChangeKey:
        """
        Modifies a DESFire card key defined in the SAM or crypto memory.
        """
        return Desfire_ChangeKey(self)
    @property
    def Desfire_SetFraming(self) -> Desfire_SetFraming:
        """
        This command switches the DESFire communication protocol mode to use (std,
        iso_wrapping). Please refer to the [DESFire
        specification](http://www.nxp.com/products/identification-and-security/smart-
        card-ics/mifare-ics/mifare-desfire:MC_53450) for more information.
        """
        return Desfire_SetFraming(self)
    @property
    def Desfire_ResetAuthentication(self) -> Desfire_ResetAuthentication:
        """
        This command resets the reader's authentication state until the next call of
        the [Desfire.Authenticate](.#Desfire.Authenticate) or
        [Desfire.AuthExtKey](.#Desfire.AuthExtKey) commands. All following DESFire
        commands will be sent and received in plain text without MAC.
        
        It is not possible to run the [Desfire.ExecCommand](.#Desfire.ExecCommand)
        with _CryptoMode_ set to any other value than PLAIN after the execution of
        this command, until the card is reauthenticated.
        """
        return Desfire_ResetAuthentication(self)
    @property
    def Desfire_CreateDam(self) -> Desfire_CreateDam:
        """
        This command creates a delegated application
        """
        return Desfire_CreateDam(self)
    @property
    def Desfire_GetOriginalitySignature(self) -> Desfire_GetOriginalitySignature:
        """
        This command returns the NXP originality signature of a desfire card.
        """
        return Desfire_GetOriginalitySignature(self)
    @property
    def Desfire_VirtualCardSelect(self) -> Desfire_VirtualCardSelect:
        """
        This command selects a virtual card
        """
        return Desfire_VirtualCardSelect(self)
    @property
    def Desfire_ProxCheck(self) -> Desfire_ProxCheck:
        """
        This command executes a proximity check of the card
        """
        return Desfire_ProxCheck(self)
    @property
    def Desfire_GetDfNames(self) -> Desfire_GetDfNames:
        """
        This command returns the application identifiers together with file IDs and
        (optionally) DF names of all applications with ISO7816-4 support.
        """
        return Desfire_GetDfNames(self)
    @property
    def Disp_Enable(self) -> Disp_Enable:
        """
        Enable/Disable Display.
        """
        return Disp_Enable(self)
    @property
    def Disp_SetContrast(self) -> Disp_SetContrast:
        """
        Set contrast of display
        """
        return Disp_SetContrast(self)
    @property
    def Disp_EnableBacklight(self) -> Disp_EnableBacklight:
        """
        Enable/Disable display backlight
        """
        return Disp_EnableBacklight(self)
    @property
    def Disp_Clear(self) -> Disp_Clear:
        """
        Clear Page description.
        """
        return Disp_Clear(self)
    @property
    def Disp_Load(self) -> Disp_Load:
        """
        Load page description.
        """
        return Disp_Load(self)
    @property
    def Disp_Extend(self) -> Disp_Extend:
        """
        Extend page description
        """
        return Disp_Extend(self)
    @property
    def EM_DecodeCfg(self) -> EM_DecodeCfg:
        """
        Configures Mod and Baudtype of receiver. When _RxMod_ is set to _unknown_ ,
        the Mod is automatically scanned. When _RxBaud_ is set to _unknown_ , the
        baudtype is automatically detected.
        """
        return EM_DecodeCfg(self)
    @property
    def EM_Read4100(self) -> EM_Read4100:
        """
        Reads the UID from EM4100/4102 labels.
        """
        return EM_Read4100(self)
    @property
    def EM_Read4205(self) -> EM_Read4205:
        """
        Reads a page from EM4205/4305 labels.
        """
        return EM_Read4205(self)
    @property
    def EM_Write4205(self) -> EM_Write4205:
        """
        Writes a page to EM4205/4305 labels.
        """
        return EM_Write4205(self)
    @property
    def EM_Halt4205(self) -> EM_Halt4205:
        """
        Disables a 4205 tag until next power on.
        """
        return EM_Halt4205(self)
    @property
    def EM_Login4205(self) -> EM_Login4205:
        """
        Login to a 4205 tag with data has to match block 1.
        """
        return EM_Login4205(self)
    @property
    def EM_Protect4205(self) -> EM_Protect4205:
        """
        Protects data from being modified.
        """
        return EM_Protect4205(self)
    @property
    def EM_Read4469(self) -> EM_Read4469:
        """
        Reads a page from EM4469/4569 labels.
        """
        return EM_Read4469(self)
    @property
    def EM_Write4469(self) -> EM_Write4469:
        """
        Writes a page to EM4469/4569 labels.
        """
        return EM_Write4469(self)
    @property
    def EM_Halt4469(self) -> EM_Halt4469:
        """
        Disables a EM4469/4569 tag until next power on.
        """
        return EM_Halt4469(self)
    @property
    def EM_Login4469(self) -> EM_Login4469:
        """
        Login to a EM4469/4569 tag with data has to match block 1.
        """
        return EM_Login4469(self)
    @property
    def EM_Read4450(self) -> EM_Read4450:
        """
        Reads pages from a EM4450 tag (start to end address).
        """
        return EM_Read4450(self)
    @property
    def Eth_GetMacAdr(self) -> Eth_GetMacAdr:
        """
        Retrieve the MAC address of the device.
        """
        return Eth_GetMacAdr(self)
    @property
    def Eth_GetConnDevIP(self) -> Eth_GetConnDevIP:
        """
        Retrieve the IP address of the directly connected network device.
        """
        return Eth_GetConnDevIP(self)
    @property
    def Eth_CreateRecoveryPoint(self) -> Eth_CreateRecoveryPoint:
        """
        Create a _Recovery Point_ , backing up all relevant Ethernet- and TCP/IP-
        settings.
        """
        return Eth_CreateRecoveryPoint(self)
    @property
    def Eth_DelRecoveryPoint(self) -> Eth_DelRecoveryPoint:
        """
        Remove a Recovery Point which was created via the
        [Eth.CreateRecoveryPoint](.#Eth.CreateRecoveryPoint) command.
        """
        return Eth_DelRecoveryPoint(self)
    @property
    def Eth_GetNetworkStatus(self) -> Eth_GetNetworkStatus:
        """
        Retrieve current network status.
        """
        return Eth_GetNetworkStatus(self)
    @property
    def Eth_GetMIBCounters(self) -> Eth_GetMIBCounters:
        """
        Retrieve current MIB counters.
        """
        return Eth_GetMIBCounters(self)
    @property
    def Eth_GetTcpConnectionStatus(self) -> Eth_GetTcpConnectionStatus:
        """
        Retrieve the BRP over TCP connection status. Checks if there is an open TCP
        connection.
        """
        return Eth_GetTcpConnectionStatus(self)
    @property
    def Eth_OpenTcpConnection(self) -> Eth_OpenTcpConnection:
        """
        Open a BRP over TCP connection to the configured host.
        """
        return Eth_OpenTcpConnection(self)
    @property
    def Eth_CloseTcpConnection(self) -> Eth_CloseTcpConnection:
        """
        Close the BRP over TCP connection.
        """
        return Eth_CloseTcpConnection(self)
    @property
    def Felica_GenericCmd(self) -> Felica_GenericCmd:
        """
        Generic command for FeliCa.
        """
        return Felica_GenericCmd(self)
    @property
    def Felica_SetUID2(self) -> Felica_SetUID2:
        """
        Sets UID2 used by generic command.
        """
        return Felica_SetUID2(self)
    @property
    def Felica_Request(self) -> Felica_Request:
        """
        Polls for tags with number of time slots, returns NFCID2 list of detected tags
        (maximum 16 / length 8).
        """
        return Felica_Request(self)
    @property
    def FlashFS_GetMemoryInfo(self) -> FlashFS_GetMemoryInfo:
        """
        This command checks the consistency of the file system and retrieves
        information about the available dataflash memory space.
        """
        return FlashFS_GetMemoryInfo(self)
    @property
    def FlashFS_Format(self) -> FlashFS_Format:
        """
        This command resets the complete file system. All data - managment structures,
        files and records - gets lost.
        
        A format is required before the first use.
        """
        return FlashFS_Format(self)
    @property
    def FlashFS_CreateFile(self) -> FlashFS_CreateFile:
        """
        This command creates a new empty file, if the file doesn't exist yet. All
        records of this file that may be created with the
        [FlashFS.WriteRecords](.#FlashFS.WriteRecords) command later have the
        specified record size.
        """
        return FlashFS_CreateFile(self)
    @property
    def FlashFS_DeleteFile(self) -> FlashFS_DeleteFile:
        """
        This command deletes a file and all its contained records. The file will be
        removed from the file system directory and the memory space allocated by its
        records will be freed, so that other files can use this space.
        """
        return FlashFS_DeleteFile(self)
    @property
    def FlashFS_RenameFile(self) -> FlashFS_RenameFile:
        """
        This command changes the File ID of a file from _FileId_ to _NewFileId_ ,
        provided the file with ID _FileId_ exists and a file with ID _NewFileId_
        doesn't exist yet.
        """
        return FlashFS_RenameFile(self)
    @property
    def FlashFS_GetRecordSize(self) -> FlashFS_GetRecordSize:
        """
        This command retrieves the size of a single record of a certain file. Every
        file has a fix record size, which was specified at file creation.
        """
        return FlashFS_GetRecordSize(self)
    @property
    def FlashFS_GetFileSize(self) -> FlashFS_GetFileSize:
        """
        This command retrieves the number of records a certain file contains.
        """
        return FlashFS_GetFileSize(self)
    @property
    def FlashFS_ReadRecords(self) -> FlashFS_ReadRecords:
        """
        This command reads one or more records from a file. If the file contains less
        records than specified, the response only returns the available number of
        records.
        """
        return FlashFS_ReadRecords(self)
    @property
    def FlashFS_WriteRecords(self) -> FlashFS_WriteRecords:
        """
        This command writes one or more records to a file. By selecting an appropriate
        _StartRecord_ parameter new records may be appended to the end of the file or
        may overwrite existing records.
        """
        return FlashFS_WriteRecords(self)
    @property
    def Ftob_OpenReadFile(self) -> Ftob_OpenReadFile:
        """
        This commands starts reading a file from the reader. After executing this
        command successfully, you may execute only FToB commands until finishing
        transfer.
        """
        return Ftob_OpenReadFile(self)
    @property
    def Ftob_OpenWriteFile(self) -> Ftob_OpenWriteFile:
        """
        This commands starts writing a file to the reader. After executing this
        command successfully, you may execute only FToB commands until finishing
        transfer.
        """
        return Ftob_OpenWriteFile(self)
    @property
    def Ftob_ReadFileBlock(self) -> Ftob_ReadFileBlock:
        """
        Use this command to receive a file block by block.
        """
        return Ftob_ReadFileBlock(self)
    @property
    def Ftob_WriteFileBlock(self) -> Ftob_WriteFileBlock:
        """
        This command writes a file block by block.
        """
        return Ftob_WriteFileBlock(self)
    @property
    def Ftob_CloseFile(self) -> Ftob_CloseFile:
        """
        This commands quits transferring a file.
        """
        return Ftob_CloseFile(self)
    @property
    def HID_IndalaRead(self) -> HID_IndalaRead:
        """
        Returns data of Indala tags (read only tag).
        """
        return HID_IndalaRead(self)
    @property
    def HID_ProxRead(self) -> HID_ProxRead:
        """
        Returns raw data of HID prox tag (read only tag / 44 bit).
        """
        return HID_ProxRead(self)
    @property
    def HID_AwidRead(self) -> HID_AwidRead:
        """
        Returns number of a AWID tag (read only tag / 44 bit).
        """
        return HID_AwidRead(self)
    @property
    def HID_IoProxRead(self) -> HID_IoProxRead:
        """
        Returns number of a IoProx tag (read only tag / 64 bit).
        """
        return HID_IoProxRead(self)
    @property
    def HID_Prox32Read(self) -> HID_Prox32Read:
        """
        Returns raw data of HID prox 32 (orange) tag (read only tag / 32bit).
        """
        return HID_Prox32Read(self)
    @property
    def HID_PyramidRead(self) -> HID_PyramidRead:
        """
        Returns number of Farpointe Pyramid cards (variable bitlength).
        """
        return HID_PyramidRead(self)
    @property
    def HID_IndalaSecureRead(self) -> HID_IndalaSecureRead:
        """
        Returns data of indala tags (read only tag).
        """
        return HID_IndalaSecureRead(self)
    @property
    def HID_IdteckRead(self) -> HID_IdteckRead:
        """
        Returns data of idteck tags (read only tag).
        """
        return HID_IdteckRead(self)
    @property
    def Hitag_Request(self) -> Hitag_Request:
        """
        Request and AC / according to Mode byte you can request Hitag-1 and Hitag-S
        tags.
        """
        return Hitag_Request(self)
    @property
    def Hitag_Select(self) -> Hitag_Select:
        """
        Selects a Hitag-1 or Hitag-S tag and returns page 1.
        """
        return Hitag_Select(self)
    @property
    def Hitag_Halt(self) -> Hitag_Halt:
        """
        Sets a Hitag1/S label in halt mode.
        """
        return Hitag_Halt(self)
    @property
    def Hitag_Read(self) -> Hitag_Read:
        """
        Reads a Hitag1/S label.
        """
        return Hitag_Read(self)
    @property
    def Hitag_Write(self) -> Hitag_Write:
        """
        Writes data to a Hitag1/S label.
        """
        return Hitag_Write(self)
    @property
    def Hitag_PersonaliseHtg(self) -> Hitag_PersonaliseHtg:
        """
        Writes personalization data for Hitag1/2 to coprocessor.
        """
        return Hitag_PersonaliseHtg(self)
    @property
    def I2c_SetSpeed(self) -> I2c_SetSpeed:
        """
        Set speed of I2C interface.
        """
        return I2c_SetSpeed(self)
    @property
    def I2c_Read(self) -> I2c_Read:
        """
        Read data from I2C interface.
        """
        return I2c_Read(self)
    @property
    def I2c_Write(self) -> I2c_Write:
        """
        Write data to I2C interface.
        """
        return I2c_Write(self)
    @property
    def I2c_TxRx(self) -> I2c_TxRx:
        """
        Write data and directly after that read from I2C interface.
        """
        return I2c_TxRx(self)
    @property
    def Iso14a_RequestLegacy(self) -> Iso14a_RequestLegacy:
        """
        This commands scans for ISO 14443-3 (Type A) compliant PICCs in the field of
        the antenna.
        
        If the _ReqAll_ parameter flag is set, both PICCs in idle state and PICCs in
        halt state will be switched to ready state. If this flag is not set, only
        PICCs in idle state will be switched to ready state.
        
        **Only PICCs in ready state may be selected via the[
        Iso14a.Select](.#Iso14a.Select) command.**
        
        **This command may return the[ Iso14a.ErrCollision](.#Iso14a.ErrCollision)
        status code when executed successfully, in case two or more PICCs of different
        types are present in the HF field of the reader. In this case, the selection
        PICC procedure can be carried out normally with the[
        Iso14a.Select](.#Iso14a.Select) command.**
        
        This command covers the commands REQA and WAKE-UP as specified by the ISO
        14443-3 standard.
        
        **For new applications, the command[ Iso14a.Request](.#Iso14a.Request) should
        be used instead.**
        """
        return Iso14a_RequestLegacy(self)
    @property
    def Iso14a_Select(self) -> Iso14a_Select:
        """
        This command Performs the anti-collision and selection sequence of a PICC in
        the field of the antenna. The PICC has to be in ready state (see
        [Iso14a.Request](.#Iso14a.Request) command) for this command to succeed.
        
        PICCs exist with three different lengths of serial numbers:
        
          * Four bytes (single size) 
          * Seven bytes (double size) 
          * Ten bytes (triple size) 
        
        In manual anti-collision mode, the Iso14a.Select command can only return 4
        Bytes of the serial number at a time, in the _Serial_ returned variable.
        Iso14a.Select therefore needs to be called one, two or three times to read
        serial numbers of single, double or triple size, respectively. Each call of
        the Iso14a.Select command is associated to a specific _cascade level_ ,
        specified by the _CascLev_ parameter. The first call of Iso14a.Select is
        associated to cascade level 1, the second call to cascade level 2, and the
        third call to cascade level 3.
        
        The fact that a serial number has not been completely returned by the
        Iso14a.Select command is indicated by a _cascade tag_ (CT, 0x88), in the first
        byte of the returned _Serial_ variable. In this case, the Iso14a.Select
        command needs to be called with the next higher cascade level (for instance
        _CascLev_ = 2 if Iso14a.Select was called with _CascLev_ = 1). The complete
        serial number of a PICC consists then of the concatenation of the (up to 3)
        returned values of _Serial_ , after removing the cascade tags(s) from these
        values. A completed selection flow is signaled by the _Casc_ flag in the _SAK_
        byte and by the missing cascade tag in the returned serial number.
        
        Using the _PreSelSer_ parameter, the serial number (or an initial part of it)
        of a given PICC can be specified to be selected within a specific cascade
        level (up to four bytes) in order to speed up the anti-collision sequence. The
        CT must be included in _PreSelSer_ if it belongs to non-final parts of the
        serial number.
        
        For convenience reasons, an automatic anti-collision mode has been
        implemented. This mode can be activated by setting the _CascLev_ parameter to
        0. In this case, the PICC can be selected with a single call of Iso14a.Select
        and the returned _Serial_ variable contains the complete serial number,
        without cascade tag(s).
        
        **In this case, cascade tags must be manually added to the _PreSelSer_
        parameter to be able to use the preselection feature.**
        
        This command combines the commands ANTICOLL and SELECT as specified in the ISO
        14443-3 (Type A) standard.
        """
        return Iso14a_Select(self)
    @property
    def Iso14a_Halt(self) -> Iso14a_Halt:
        """
        Switch PICC to halt state.
        
        The PICC has to be selected before it may be switched to halt state.
        
        **This command only works for PICCs that are, though in active state, not in
        ISO 14443-4 mode. For such PICCs, the[ Iso14L4.Deselect](.#Iso14L4.Deselect)
        command should be used instead.**
        """
        return Iso14a_Halt(self)
    @property
    def Iso14a_RequestATS(self) -> Iso14a_RequestATS:
        """
        This command requests the Answer to Select (ATS) of the PICC according to the
        ISO 14443-3 (Type A) standard.
        
        RequestATS has to be called by the PCD (reader) directly after a successful
        call of the [Iso14a.Select](.#Iso14a.Select) command if
        
          1. The selected PICC is ISO 14443-4 compliant (according to _SAK_ byte) and 
          2. communication as specified by ISO 14443-4 shall be performed via the [Iso14L4.ExchangeAPDU](iso14443_4.xml#Iso14L4.ExchangeAPDU) command. 
        
        Since it is possible to keep several PICCs in active state at the same time
        according to ISO 14443-4, a unique CID has to be assigned to each of them.
        However, if you only want to communicate with a single label at a given time,
        the value 0 should be assigned to the _CID_ variable. In this case, it is
        possible to call the
        [Iso14L4.ExchangeAPDU](iso14443_4.xml#Iso14L4.ExchangeAPDU) command without
        bothering about CIDs.
        
        Please refer to the [Iso14a.PerformPPS](.#Iso14a.PerformPPS) and
        [Iso14L4.ExchangeAPDU](iso14443_4.xml#Iso14L4.ExchangeAPDU) command
        descriptions for more information about frame sizes and timing issues.
        
        After successful execution of this command, the communication parameters can
        be tuned with the [Iso14a.PerformPPS](.#Iso14a.PerformPPS) command.
        """
        return Iso14a_RequestATS(self)
    @property
    def Iso14a_PerformPPS(self) -> Iso14a_PerformPPS:
        """
        This command sets up the communication parameters for ISO 14443-4 commands.
        
        Iso14a.PerformPPS may be used to change the default communication parameters
        in order to achieve faster HF communication. This command has to be executed
        directly after the [Iso14a.RequestATS](.#Iso14a.RequestATS) command but it is
        not necessary to execute it at all.
        
        This command covers the PPS command as specified by ISO 14443-3 (type A).
        
        The _PPS1_ bit mask is only sent to the PICC if DSI or DRI differ from the
        current settings.
        """
        return Iso14a_PerformPPS(self)
    @property
    def Iso14a_Request(self) -> Iso14a_Request:
        """
        This commands scans for ISO 14443-3 (Type A) compliant PICCs in the field of
        the antenna.
        
        If the _ReqAll_ parameter flag is set, both PICCs in idle state and PICCs in
        halt state will be switched to ready state. If this flag is not set, only
        PICCs in idle state will be switched to ready state.
        
        **Only PICCs in ready state may be selected via the[
        Iso14a.Select](.#Iso14a.Select) command.**
        
        This command covers the commands REQA and WAKE-UP as specified by the ISO
        14443-3 standard.
        """
        return Iso14a_Request(self)
    @property
    def Iso14a_RequestVasup(self) -> Iso14a_RequestVasup:
        """
        This commands scans for ISO 14443-3 (Type A) compliant PICCs in the field of
        the antenna and enhances polling with the VASUP-A command (required for ECP
        support).
        
        If the _ReqAll_ parameter flag is set, both PICCs in idle state and PICCs in
        halt state will be switched to ready state. If this flag is not set, only
        PICCs in idle state will be switched to ready state.
        
        **Only PICCs in ready state may be selected via the[
        Iso14a.Select](.#Iso14a.Select) command.**
        
        This command covers the commands REQA and WAKE-UP as specified by the ISO
        14443-3 standard.
        """
        return Iso14a_RequestVasup(self)
    @property
    def Iso14a_Anticoll(self) -> Iso14a_Anticoll:
        """
        This command performs an anti-collision sequence.
        """
        return Iso14a_Anticoll(self)
    @property
    def Iso14a_SelectOnly(self) -> Iso14a_SelectOnly:
        """
        This command selects a PICC with a 4 Byte serial number.
        """
        return Iso14a_SelectOnly(self)
    @property
    def Iso14a_TransparentCmd(self) -> Iso14a_TransparentCmd:
        """
        This command sends a data stream to a card and returns the communication
        status and the received card data stream to the host.
        """
        return Iso14a_TransparentCmd(self)
    @property
    def Iso14a_TransparentCmdBitlen(self) -> Iso14a_TransparentCmdBitlen:
        """
        This command is similar to _Iso14a.TransparentCmd_. The difference is that the
        length of data to send is given in bits instead of bytes.
        """
        return Iso14a_TransparentCmdBitlen(self)
    @property
    def Iso14b_Request(self) -> Iso14b_Request:
        """
        Scan for ISO 14443 (Type B) compliant PICCs in the field of the antenna.
        
        If a collision occurred in at least one time slot (signaled by status code
        ISO14B_COLLISION_ERR), this command needs to be called again with an increased
        number of time slots so that more PICCs can be detected.
        
        The ISO14B_MEM_ERR status code signals that more PICCs are available than can
        be handled with the buffer provided by the reader for BRP communication. The
        [Iso14b.Halt](.#Iso14b.Halt) command can be used to disable undesired PICCs
        before calling the Iso14b.Request command again.
        
        PICCs that have been returned by this command may subsequently be switched to
        the active state via the [Iso14b.Attrib](.#Iso14b.Attrib) command.
        """
        return Iso14b_Request(self)
    @property
    def Iso14b_Attrib(self) -> Iso14b_Attrib:
        """
        Select the PICC with given _PUPI_ serial number for further communication. The
        desired PICC must have been reported by the [Iso14b.Request](.#Iso14b.Request)
        command before.
        
        The parameters given in the _Param_ bit mask have to match both the supported
        communication parameters of the reader and of the current PICC, according to
        the _ProtInfo_ bit mask returned by the [Iso14b.Request](.#Iso14b.Request)
        command. These parameters will be applied for all ISO 14443-4 APDUs that will
        be exchanged via the [Iso14L4.ExchangeAPDU](.#Iso14L4.ExchangeAPDU) command.
        
        Furthermore, a unique communication channel ID (CID) has to be assigned, which
        identifies the PICC and which will also be needed by the ISO 14443-4 commands.
        
        Normally, there may be up to 14 PICCs in active state at the same time and
        each PICC will be uniquely identified by its CID. However, there are exist
        PICCs which do no support being assigned a CID. Only one of these PICCs may be
        in active state at the same time (along with other PICCs supporting the CID
        feature). The same restriction also holds for PICCs which are assigned a CID
        of 0x00 with this command.
        """
        return Iso14b_Attrib(self)
    @property
    def Iso14b_Halt(self) -> Iso14b_Halt:
        """
        Switch the PICC with the given _PUPI_ serial number into halt state, so that
        it will not answer to further [Iso14b.Request](.#Iso14b.Request) commands,
        except when the _ReqAll_ flag parameter of the
        [Iso14b.Request](.#Iso14b.Request) command is set. The memory occupied by this
        PICC's information will also be freed, which makes it is available for future
        calls of the [Iso14b.Request](.#Iso14b.Request) command. Use this command in
        order to deactivate some of the PICCs in case the
        [Iso14b.ErrMem](.#Iso14b.ErrMem) status code has been returned by the last
        call of [Iso14b.Request](.#Iso14b.Request).
        
        **This command only works for PICCs in ready state. For PICCs in active state,
        the[ Iso14L4.Deselect](iso14443_4.xml#Iso14L4.Deselect) command should be used
        instead.**
        """
        return Iso14b_Halt(self)
    @property
    def Iso14b_SetTransparentSettings(self) -> Iso14b_SetTransparentSettings:
        """
        **This command is obsolete and included here only for compatibility reasons.
        Please use the[ Iso14b.TransparentCmd](.#Iso14b.TransparentCmd) command
        instead.**
        
        Sets reader chip configuration. If this command is not called, default
        parameters will be used.
        """
        return Iso14b_SetTransparentSettings(self)
    @property
    def Iso14b_GetTransparentSettings(self) -> Iso14b_GetTransparentSettings:
        """
        **This command is obsolete and included here only for compatibility reasons.
        Please use the[ Iso14b.TransparentCmd](.#Iso14b.TransparentCmd) command
        instead.**
        
        Gets reader chip configuration.
        """
        return Iso14b_GetTransparentSettings(self)
    @property
    def Iso14b_TransparentCmd(self) -> Iso14b_TransparentCmd:
        """
        This command sends a data stream to a card and returns the communication
        status and the received card data stream to the host.
        """
        return Iso14b_TransparentCmd(self)
    @property
    def Iso14L4_SetupAPDU(self) -> Iso14L4_SetupAPDU:
        """
        Setup communication parameters and select a certain PICC for APDU exchange.
        The chosen settings will be applied to all subsequent calls of the
        [Iso14L4.ExchangeAPDU](.#Iso14L4.ExchangeAPDU) and
        [Iso14L4.Deselect](.#Iso14L4.Deselect) commands.
        
        The _FrameParam_ and _Bitrate_ parameters have to be chosen according to the
        PICC's capabilities.
        
        In some cases, the _CID_ of the label to select has to be passed as a
        parameter. This is the case if the label supports the feature of being
        assigned a CID, and if a CID value has been previously assigned to the PICC
        using the [Iso14a.RequestATS](iso14443a_3.xml#Iso14a.RequestATS) command (for
        ISO 14443 Type A labels) or by the or the
        [Iso14b.Attrib](iso14443b_3.xml#Iso14b.Attrib) command (for ISO 14443 Type B
        labels). Otherwise, the CID functionality should be disabled, by clearing the
        _EnCID_ flag.
        
        PICCs which do not support a CID (for which the returned _CID_ value from the
        [Iso14a.RequestATS](iso14443a_3.xml#Iso14a.RequestATS) command, or from the
        [Iso14b.Request](iso14443b_3.xml#Iso14b.Request) command, is 0x00) will only
        respond to the [Iso14L4.ExchangeAPDU](.#Iso14L4.ExchangeAPDU) and
        [Iso14L4.Deselect](.#Iso14L4.Deselect) commands if the CID functionality is
        disabled.
        
        A PICC, which supports a CID, will
        
          1. respond to the [Iso14L4.ExchangeAPDU](.#Iso14L4.ExchangeAPDU) and [Iso14L4.Deselect](.#Iso14L4.Deselect) commands only if the CID functionality is enabled and if the specified CID value matches the PICC's own CID value. 
          2. ignore the [Iso14L4.ExchangeAPDU](.#Iso14L4.ExchangeAPDU) and [Iso14L4.Deselect](.#Iso14L4.Deselect) commands if a different CID value is specified. 
          3. also respond to [Iso14L4.ExchangeAPDU](.#Iso14L4.ExchangeAPDU) and [Iso14L4.Deselect](.#Iso14L4.Deselect) commands with a disabled CID functionality, if its own CID value is 0. 
        
        The _NAD_ parameter may be used to select a certain logical application (node)
        on the target PICC, if these are supported by this PICC.
        """
        return Iso14L4_SetupAPDU(self)
    @property
    def Iso14L4_ExchangeAPDU(self) -> Iso14L4_ExchangeAPDU:
        """
        This command allows to transmit/receive _Application Protocol Data Units_
        (APDUs) according to the ISO 14443-4 standard.
        
        The [Iso14L4.SetupAPDU](.#Iso14L4.SetupAPDU) command must be run before
        Iso14L4.ExchangeAPDU in order to select the required PICC and set the
        appropriate communication parameters. If an error occurs during the execution
        of Iso14L4.ExchangeAPDU, it is mandatory to reselect the PICC. The
        [Iso14L4.SetupAPDU](.#Iso14L4.SetupAPDU) command can be called anew if
        communication parameters with the PICC should be changed.
        """
        return Iso14L4_ExchangeAPDU(self)
    @property
    def Iso14L4_Deselect(self) -> Iso14L4_Deselect:
        """
        This command switches one or multiple PICC(s) to halt state.
        
        **This command only works for certain types of PICCs (see command group
        description above). For other types of PICCs, the[
        Iso14a.Halt](iso14443a_3.xml#Iso14a.Halt) command or the[
        Iso14b.Halt](iso14443b_3.xml#Iso14b.Halt) command should be used instead.**
        """
        return Iso14L4_Deselect(self)
    @property
    def I4CE_StartEmu(self) -> I4CE_StartEmu:
        """
        **This command is marked as deprecated as it is not supported by Baltech's
        SDK. There is currently no alternative for this command.**
        
        This command starts the reader's passive mode, emulating an ISO14443-4
        compatible card, and returns the first APDU request received.
        
        The emulated PICC answers all ISO14443-3 request, anticollision and select
        commands. It utilizes the 4-Byte serial number specified in the _Snr_
        parameter. The Byte order corresponds to ISO14443-3: The first Byte (uid0)
        will be transmitted first to the reader. It has to be 0x08 as this indicates a
        random serial number.
        
        To identify potential errors, the PCD starts a timer within which the PICC has
        to respond, after sending out each frame. This time duration is the so-called
        _frame waiting time_ (FWT). FWT is determined by the PICC during protocol
        activation and is valid for all further communication. This parameter should
        be chosen as large as required, but as small as possible. The communication
        speed between card emulator and host and the processing speed of the host
        should be taken into consideration. It is possible to increase the FWT
        temporarily for a single frame by calling the
        [I4CE.ExtendWaitingTime](.#I4CE.ExtendWaitingTime) command. Since the ISO14443
        protocol specification only allows discrete FWT values, the firmware
        calculates the lowest value that meets the specified waiting time according to
        the equation
        
        FWI = (256 * 16 / fc) * 2 ^ FWT,
        
        where fc is the RFID carrier frequency. The highest possible FWT value is 4949
        ms.
        
        Two timeout parameters triggering two timers have to be specified for this
        command. The first timer, associated to the _TimeoutPCD_ parameter, stops as
        soon as the first PCD command frame after the card selection as defined in
        ISO14443-3 is received. If the emulated PICC does not receive anything within
        _TimeoutPCD_ , this command will return an
        [I4CE.ErrIso144State](.#I4CE.ErrIso144State) status code, which indicates that
        the PICC did not receive the required protocol activation sequence to exchange
        ISO14443-4 APDUs. If a PCD frame is received before _TimeoutPCD_ elapses, the
        second timer, associated to the _TimeoutAPDU_ variable, is started. If this
        timer elapses before the reader receives the first protocol activation
        sequence and the first APDU, the [I4CE.ErrTimeout](.#I4CE.ErrTimeout) status
        code is returned. Otherwise, the first APDU request is returned in the
        command's response.
        
        The ATS (historical bytes) the card emulation shall use may be specified by
        the _ATS_ parameter if required. This parameter may also be left out, in which
        case no historical bytes are sent.
        
        As already mentioned, ISO14443-4 specifies that a card has to send a response
        within _FWT_ ms. The command
        [I4CE.ExtendWaitingTime](.#I4CE.ExtendWaitingTime) can be called to extend
        this time temporarily if the host cannot prepare the APDU within the defined
        FWT time. A more convenient way to perform this action is to use the
        _automatic WTX mode_ : If the parameter _AutoWTX_ is set to 1, the card
        emulation will automatically transmit WTX requests periodically every 0.9 *
        FWT ms after the successful execution of the I4CE.StartEmu command and of all
        subsequent [I4CE.ExchangeInverseAPDU](.#I4CE.ExchangeInverseAPDU) commands. In
        practice, this allows to ignore the FWT limits, since the card emulation
        itself keeps the communication with the PCD alive.
        """
        return I4CE_StartEmu(self)
    @property
    def I4CE_ExchangeInverseAPDU(self) -> I4CE_ExchangeInverseAPDU:
        """
        **This command is marked as deprecated as it is not supported by Baltech's
        SDK. There is currently no alternative for this command.**
        
        Send an APDU response to the APDU request received during the last call of
        I4CE.ExchangeInverseAPDU or [I4CE.StartEmu](.#I4CE.StartEmu), and receive the
        next PCD APDU request.
        
        The _Timeout_ parameter specifies the maximum time in ms to wait for the next
        APDU. If no request could be received from the PCD, I4CE.ExchangeInverseAPDU
        returns the [I4CE.ErrTimeout](.#I4CE.ErrTimeout) status code.
        
        In case the received APDU does not fit into the internal buffer of the
        emulated PICC, the part of the frame which could be processed is returned
        together with an [I4CE.ErrOverflow](.#I4CE.ErrOverflow) status code. The
        buffer size is firmware dependent and can be retrieved via the
        [Sys.GetBufferSize](system.xml#Sys.GetBufferSize) command.
        
        The command returns the [I4CE.ErrIso144State](.#I4CE.ErrIso144State) status
        code if the PICC is not in the proper state to exchange ISO14443-4 APDUs. This
        is the case if [I4CE.StartEmu](.#I4CE.StartEmu) has not previously been
        successfully executed, or if the PCD has terminated the communication by e.g.
        executing the [Iso14L4.Deselect](iso14443_4.xml#Iso14L4.Deselect) command.
        """
        return I4CE_ExchangeInverseAPDU(self)
    @property
    def I4CE_ExtendWaitingTime(self) -> I4CE_ExtendWaitingTime:
        """
        This command enables to extend the waiting time for the response from the PCD.
        This command is required in case the host needs a longer time than FWT (see
        description of the [I4CE.StartEmu](.#I4CE.StartEmu) command) to prepare a
        response APDU to the last request APDU from the PCD. After calling this
        command, the PICC repeatedly sends WTX requests to the PCD for
        _WaitingTimeout_ ms.
        
        **This command should be run in BRP _Continuous Mode_ , since it can
        explicitly be stopped by the host by executing the _Break_ command. If this
        command is not run in BRP Continuous Mode, the reader has to wait for the
        _WaitingTimeout_ duration before finalizing the execution of the command.**
        
        The WTX request refresh interval may be accommodated with the _WTXM_ and
        _RefreshRatio_ parameters according to the formula:
        
        t(refresh) = FWT * WTXM * RefreshRatio / 100.
        
        By default, the waiting time is renewed every (0.9 * FWT) ms (WTXM = 1,
        RefreshRatio = 90).
        
        Please note that according to the [ISO/IEC
        14443-4:2008](https://www.iso.org/standard/50648.html) specification, the
        maximum allowed value for FWT and for the extension FWT * WTXM is 4949 ms.
        
        **This command should only be used if the _AutoWTX_ parameter in the[
        I4CE.StartEmu](.#I4CE.StartEmu) command is set to 0. Otherwise, the card
        emulation automatically takes care of extending the frame waiting time.**
        """
        return I4CE_ExtendWaitingTime(self)
    @property
    def I4CE_GetExternalHfStatus(self) -> I4CE_GetExternalHfStatus:
        """
        Polls for an external HF field and returns the status in the _ExtFieldStat_
        variable.
        """
        return I4CE_GetExternalHfStatus(self)
    @property
    def Iso14CE_ActivateCardAPDU(self) -> Iso14CE_ActivateCardAPDU:
        """
        This command starts the reader's passive mode, emulating an ISO14443-4
        compatible card, and returns the first APDU request received.
        
        The emulated PICC answers all ISO14443-3 request, anticollision and select
        commands. It utilizes the 4-Byte serial number specified in the _Snr_
        parameter. The Byte order corresponds to ISO14443-3: The first Byte (uid0)
        will be transmitted first to the reader. It has to be 0x08 as this indicates a
        random serial number.
        
        To identify potential errors, the PCD starts a timer within which the PICC has
        to respond, after sending out each frame. This time duration is the so-called
        _frame waiting time_ (FWT). FWT is determined by the PICC during protocol
        activation and is valid for all further communication. This parameter should
        be chosen as large as required, but as small as possible. The communication
        speed between card emulator and host and the processing speed of the host
        should be taken into consideration. It is possible to increase the FWT
        temporarily for a single frame by calling the
        [Iso14CE.ExtendWaitingTime](.#Iso14CE.ExtendWaitingTime) command. Since the
        ISO14443 protocol specification only allows discrete FWT values, the firmware
        calculates the lowest value that meets the specified waiting time according to
        the equation
        
        FWI = (256 * 16 / fc) * 2 ^ FWT,
        
        where fc is the RFID carrier frequency. The highest possible FWT value is 4949
        ms.
        
        2 timeout parameters triggering a timer have to be specified for this command:
        
          * The first timer, associated with the _TimeoutPCD_ parameter, is used for the card activation sequence. Card activation is complete once the emulated PICC has received the RATS command. If the emulated PICC doesn't receive the required protocol activation sequence within _TimeoutPCD_ , this command will return an [Iso14CE.ErrIso144State](.#Iso14CE.ErrIso144State) status code. For _TimeoutPCD_ , we recommend a value of 1000 ms - this provides the best results for the protocol activation sequence. 
          * The second timer is optional (default value: 100 ms) and associated with the _TimeoutApdu_ parameter. It stops as soon as the emulated PICC has received an optional PPS command frame or an APDU Exchange command after the RATS command as defined in ISO14443-4. If the emulated PICC doesn't receive anything within _TimeoutApdu_ , this command will return an [Iso14CE.ErrIso144State](.#Iso14CE.ErrIso144State) status code. Otherwise, the first APDU request is returned in the command's response. 
        
        The ATS (historical bytes) the card emulation shall use may be specified by
        the _ATS_ parameter if required. This parameter may also be left out, in which
        case no historical bytes are sent.
        
        As already mentioned, ISO14443-4 specifies that a card has to send a response
        within _FWT_ ms. The command
        [I4CE.ExtendWaitingTime](.#Iso14CE.ExtendWaitingTime) can be called to extend
        this time temporarily if the host cannot prepare the APDU within the defined
        FWT time. A more convenient way to perform this action is to use the
        _automatic WTX mode_ : If the parameter _AutoWTX_ is set to 1, the card
        emulation will automatically transmit WTX requests periodically every 0.9 *
        FWT ms after the successful execution of the Iso14CE.StartEmu command and of
        all subsequent [Iso14CE.ExchangeCardAPDU](.#Iso14CE.ExchangeCardAPDU)
        commands. In practice, this allows to ignore the FWT limits, since the card
        emulation itself keeps the communication with the PCD alive.
        """
        return Iso14CE_ActivateCardAPDU(self)
    @property
    def Iso14CE_ExchangeCardAPDU(self) -> Iso14CE_ExchangeCardAPDU:
        """
        Send an APDU response to the APDU request received during the last call of
        Iso14CE.ExchangeInverseAPDU or
        [Iso14CE.ActivateCardAPDU](.#Iso14CE.ActivateCardAPDU), and receive the next
        PCD APDU request.
        
        The _Timeout_ parameter specifies the maximum time in ms to wait for the next
        APDU. If no request could be received from the PCD,
        Iso14CE.ExchangeInverseAPDU returns the
        [Iso14CE.ErrTimeout](.#Iso14CE.ErrTimeout) status code.
        
        In case the received APDU does not fit into the internal buffer of the
        emulated PICC, the part of the frame which could be processed is returned
        together with an [I4CE.ErrOverflow](.#Iso14CE.ErrOverflow) status code. The
        buffer size is firmware dependent and can be retrieved via the
        [Sys.GetBufferSize](system.xml#Sys.GetBufferSize) command.
        
        The command returns the [Iso14CE.ErrIso144State](.#Iso14CE.ErrIso144State)
        status code if the PICC is not in the proper state to exchange ISO14443-4
        APDUs. This is the case if
        [Iso14CE.ActivateCardAPDU](.#Iso14CE.ActivateCardAPDU) has not previously been
        successfully executed, or if the PCD has terminated the communication by e.g.
        executing the [Iso14L4.Deselect](iso14443_4.xml#Iso14L4.Deselect) command.
        """
        return Iso14CE_ExchangeCardAPDU(self)
    @property
    def Iso14CE_ExtendWaitingTime(self) -> Iso14CE_ExtendWaitingTime:
        """
        This command enables to extend the waiting time for the response from the PCD.
        This command is required in case the host needs a longer time than FWT (see
        description of the [Iso14CE.ActivateCardAPDU](.#Iso14CE.ActivateCardAPDU)
        command) to prepare a response APDU to the last request APDU from the PCD.
        After calling this command, the PICC repeatedly sends WTX requests to the PCD
        for _WaitingTimeout_ ms.
        
        **This command should be run in BRP _Continuous Mode_ , since it can
        explicitly be stopped by the host by executing the _Break_ command. If this
        command is not run in BRP Continuous Mode, the reader has to wait for the
        _WaitingTimeout_ duration before finalizing the execution of the command.**
        
        The WTX request refresh interval may be accommodated with the _WTXM_ and
        _RefreshRatio_ parameters according to the formula:
        
        t(refresh) = FWT * WTXM * RefreshRatio / 100.
        
        By default, the waiting time is renewed every (0.9 * FWT) ms (WTXM = 1,
        RefreshRatio = 90).
        
        Please note that according to the [ISO/IEC
        14443-4:2008](https://www.iso.org/standard/50648.html) specification, the
        maximum allowed value for FWT and for the extension FWT * WTXM is 4949 ms.
        
        **This command should only be used if the _AutoWTX_ parameter in the[
        Iso14CE.ActivateCardAPDU](.#Iso14CE.ActivateCardAPDU) command is set to 0.
        Otherwise, the card emulation automatically takes care of extending the frame
        waiting time.**
        """
        return Iso14CE_ExtendWaitingTime(self)
    @property
    def Iso14CE_GetExternalHfStatus(self) -> Iso14CE_GetExternalHfStatus:
        """
        Polls for an external HF field and returns the status in the _ExtFieldStat_
        variable.
        """
        return Iso14CE_GetExternalHfStatus(self)
    @property
    def Iso15_SetParam(self) -> Iso15_SetParam:
        """
        This command configures the reader chip. If a parameter is not supported, a
        status message is returned.
        """
        return Iso15_SetParam(self)
    @property
    def Iso15_GetParam(self) -> Iso15_GetParam:
        """
        This command reads the configuration of the reader chip.
        """
        return Iso15_GetParam(self)
    @property
    def Iso15_GetUIDList(self) -> Iso15_GetUIDList:
        """
        This command scans for ISO 15693 labels which are in the field of the readers
        antenna and which are not in _quiet-state_. The list of UIDs is returned in
        the response frame. Furthermore, the DSFID is send back if the _DSFID_ flag in
        _Mode_ is set.
        
        If the _More_ response value is different from zero, there are more tags to
        scan, and Iso15.GetUIDList has to be called again with the _NextBlock_ flag
        set to get the rest of the labels which have not been transferred within this
        frame.
        
        To optimize the label scanning time, the reader should be told if there are
        many labels (more than 2 or 3) in the antenna's field. In this case, the
        _En16Slots_ flag should be set. This bit will tell Iso15.GetUIDList to send
        the inventory with 16 time slots instead of one.
        
        Furthermore the _Autoquiet_ flag can be set to put every label into _quiet-
        state_ after a successful scan. This will result in a kind of incremental
        behaviour from Iso15.GetUIDList since after the first successful
        Iso15.GetUIDList call, all following Iso15.GetUIDList calls will only return
        labels which came into the field of the antenna after the last call.
        """
        return Iso15_GetUIDList(self)
    @property
    def Iso15_SetMode(self) -> Iso15_SetMode:
        """
        This command configures the mode to address a label.
        
          * _Unaddressed mode_ : The following label commands are sent to the label without an UID (broadcast). This implies that not more than one label should be in the antenna's field because every label is responding in this mode which would result in a collision. 
          * _Addressed mode_ : The following label commands are sent to the label including the UID given in _UID_. To talk to one distinct label among others, the Iso15.SetMode command has to be called with a value of 0x01 in the _Mode_ byte before execution of other label commands. 
          * _Selected mode_ : Useful if a lot of operations need to be performed with the same label since the UID is not transferred to the label over and over again. A Iso15.SetMode command with _Mode_ 0x02 implicitly executes a _Select_ command with the corresponding UID as parameter (see the [ISO 1593-3 standard](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467) for details). A previously selected label will be deselected automatically if a Iso15.SetMode command with Mode 0x02 and a different UID or a Iso15.SetMode command with Mode unequal 0x02 is executed. If a Iso15.SetMode command with Mode 0x02 fails, the reader remains in the unaddressed mode. 
        
        **Please be aware that not all label types support all modes.**
        """
        return Iso15_SetMode(self)
    @property
    def Iso15_StayQuiet(self) -> Iso15_StayQuiet:
        """
        This command puts a label into the _quiet-state_. This command shall always be
        executed in addressed mode (see the [Iso15.SetMode](.#Iso15.SetMode) command).
        After executing this command, the label will not response to any
        [Iso15.GetUIDList](.#Iso15.GetUIDList) command until its state machine is
        reset (either by a physical HF-reset (i.e. switching off the field of the
        antenna or taking the label out of the field) or by executing the commands
        [Iso15.ResetToReady](.#Iso15.ResetToReady) or [Iso15.SetMode](.#Iso15.SetMode)
        (using selected mode).
        """
        return Iso15_StayQuiet(self)
    @property
    def Iso15_ReadBlock(self) -> Iso15_ReadBlock:
        """
        **For new applications please use[
        Iso15.WriteMultipleBlocks](.#Iso15.ReadMultipleBlocks) as this command is
        deprecated and may be removed in future.**
        
        This command reads one or multiple blocks from a label.
        
        This command implements the "read single block" and "read multiple blocks"
        optional commands from the [ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        """
        return Iso15_ReadBlock(self)
    @property
    def Iso15_WriteBlock(self) -> Iso15_WriteBlock:
        """
        **For new applications please use[
        Iso15.WriteMultipleBlocks](.#Iso15.WriteMultipleBlocks) as this command is
        deprecated and may be removed in future.**
        
        This command writes one or multiple blocks to a label.
        
        This command implements the "write multiple blocks" optional commands from the
        [ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        """
        return Iso15_WriteBlock(self)
    @property
    def Iso15_LockBlock(self) -> Iso15_LockBlock:
        """
        This command permanently locks the block with ID _BlockID_.
        
        **This command is an _optional command_ .**
        """
        return Iso15_LockBlock(self)
    @property
    def Iso15_ResetToReady(self) -> Iso15_ResetToReady:
        """
        This command puts a label into _ready-state_ , according to the VICC state
        transition diagram from the [ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        
        **This command is an _optional command_ .**
        """
        return Iso15_ResetToReady(self)
    @property
    def Iso15_WriteAFI(self) -> Iso15_WriteAFI:
        """
        This commands writes the _AFI_ value into the label's memory.
        
        **This commands is an _optional command_ .**
        """
        return Iso15_WriteAFI(self)
    @property
    def Iso15_LockAFI(self) -> Iso15_LockAFI:
        """
        This command locks the _AFI_ value permanently into the reader's memory.
        
        **This commands is an _optional command_ .**
        """
        return Iso15_LockAFI(self)
    @property
    def Iso15_WriteDSFID(self) -> Iso15_WriteDSFID:
        """
        This commands writes the _DSFID_ value into the label's memory.
        
        **This commands is an _optional command_ .**
        """
        return Iso15_WriteDSFID(self)
    @property
    def Iso15_LockDSFID(self) -> Iso15_LockDSFID:
        """
        This command locks the _DSFID_ value permanently into the reader's memory.
        
        **This commands is an _optional command_ .**
        """
        return Iso15_LockDSFID(self)
    @property
    def Iso15_GetSystemInformation(self) -> Iso15_GetSystemInformation:
        """
        This command gets the system information of a VICC.
        
        **This commands is an _optional command_ .**
        """
        return Iso15_GetSystemInformation(self)
    @property
    def Iso15_GetSecurityStatus(self) -> Iso15_GetSecurityStatus:
        """
        This command retrieves the block security status of a label.
        
        **This command is an _optional command_ .**
        """
        return Iso15_GetSecurityStatus(self)
    @property
    def Iso15_CustomCommand(self) -> Iso15_CustomCommand:
        """
        This command executes any ISO 15693 manufacturer proprietary commands, so-
        called _custom-commands_.
        
        By default, the same label is addressed as in the last regular ISO 15693
        command.
        """
        return Iso15_CustomCommand(self)
    @property
    def Iso15_ReadSingleBlock(self) -> Iso15_ReadSingleBlock:
        """
        This command reads a single block from a label.
        
        This command implements the "read single block" optional command from the [ISO
        15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        """
        return Iso15_ReadSingleBlock(self)
    @property
    def Iso15_WriteSingleBlock(self) -> Iso15_WriteSingleBlock:
        """
        This command writes a single block to a label.
        
        This command implements the "write single block" optional command from the
        [ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        """
        return Iso15_WriteSingleBlock(self)
    @property
    def Iso15_TransparentCmdLegacy(self) -> Iso15_TransparentCmdLegacy:
        """
        **For new applications please use[
        Iso15.TransparentCmd](.#Iso15.TransparentCmd) as this command is deprecated
        and may be removed in future.**
        
        This command sends a data stream to a label and returns the communication
        status and the received label data stream to the host. If no bytes are sent
        and the CRC check is disabled, only an EOF is sent to the label. After
        execution of this command, the _Mode_ parameter is reset to default.
        
        **Please be aware that the _flag_ Byte (see the[ ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467) ,
        2001 p.9) is not generated by the reader. This flag has to be transmitted as
        part of the _data_ string.**
        """
        return Iso15_TransparentCmdLegacy(self)
    @property
    def Iso15_WriteMultipleBlocks(self) -> Iso15_WriteMultipleBlocks:
        """
        Sends the "WriteMultipleBlocks" to the card to store the data passed in
        _WriteBlocks_ to the data blocks of the presented card starting at block with
        id _Blockid_. For more information about this command please refer to the [ISO
        15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        """
        return Iso15_WriteMultipleBlocks(self)
    @property
    def Iso15_ReadMultipleBlocks(self) -> Iso15_ReadMultipleBlocks:
        """
        This command reads one or multiple blocks from a label.
        
        This command implements the (optional) "ReadMultipleBlocks" command from the
        [ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467).
        """
        return Iso15_ReadMultipleBlocks(self)
    @property
    def Iso15_TransparentCmd(self) -> Iso15_TransparentCmd:
        """
        This command sends a data stream to a label and returns the communication
        status and the received label data stream to the host. If no bytes are sent
        and the CRC check is disabled, only an EOF is sent to the label. After
        execution of this command, the _Mode_ parameter is reset to default.
        
        **Please be aware that the _flag_ Byte (see the[ ISO 15693-3
        specification](http://www.iso.org/iso/catalogue_detail.htm?csnumber=43467) ,
        2001 p.9) is not generated by the reader. This flag has to be transmitted as
        part of the _data_ string.**
        """
        return Iso15_TransparentCmd(self)
    @property
    def Iso78_SelectSlot(self) -> Iso78_SelectSlot:
        """
        This command can be used for readers with more than one SAM slot to switch
        between the slots. The slots are indexed starting at 0. At power up, slot 0 is
        selected. All following commands are routed to the SAM in the selected slot.
        
        It is possible to switch the slots after opening a SAM.
        """
        return Iso78_SelectSlot(self)
    @property
    def Iso78_OpenSamLegacy(self) -> Iso78_OpenSamLegacy:
        """
        This command sets up a communication channel to the SAM in the currently
        selected slot. If Iso78.OpenSAM was executed successfully,
        [Iso78.ExchangeApdu](.#Iso78.ExchangeApdu) can then be used to communicate
        with the SAM.
        
        To close the communication channel after data exchange, the
        [Iso78.CloseSam](.#Iso78.CloseSam) command has to be called.
        """
        return Iso78_OpenSamLegacy(self)
    @property
    def Iso78_CloseSamLegacy(self) -> Iso78_CloseSamLegacy:
        """
        This command closes a communication channel previously opened via the
        [Iso78.OpenSAM](.#Iso78.OpenSam) command. It is recommended to call this
        command before physically removing the SAM from its slot since it also powers
        down the SAM module.
        """
        return Iso78_CloseSamLegacy(self)
    @property
    def Iso78_ExchangeApduLegacy(self) -> Iso78_ExchangeApduLegacy:
        """
        This command sends an APDU command on the currently selected and opened SAM.
        Please note that the complete APDU command including the CLA, INS, P1, P2, Lc
        and Le values need part of the _SendData_ parameter.
        """
        return Iso78_ExchangeApduLegacy(self)
    @property
    def Iso78_OpenSam(self) -> Iso78_OpenSam:
        """
        This command sets up a communication channel to a Secure Access Module (SAM)
        inserted into the reader. To select the SAM, you specify it using the _LID_
        parameter as described below. Once you've run this command successfully, you
        can run [Iso78.ExchangeApdu](.#Iso78.ExchangeApdu) to communicate with the
        SAM.
        
        To close the communication channel after data exchange, run
        [Iso78.CloseSam](.#Iso78.CloseSam).
        """
        return Iso78_OpenSam(self)
    @property
    def Iso78_CloseSam(self) -> Iso78_CloseSam:
        """
        This command closes a communication channel previously opened via the
        [Iso78.OpenSam](.#Iso78.OpenSam) command. It is recommended to call this
        command before physically removing the SAM from its slot since it also powers
        down the SAM module.
        """
        return Iso78_CloseSam(self)
    @property
    def Iso78_ExchangeApdu(self) -> Iso78_ExchangeApdu:
        """
        This command sends an APDU command on the currently selected and opened SAM
        module using a logical ID. Please note that the complete APDU command
        including the CLA, INS, P1, P2, Lc and Le values need part of the _SendData_
        parameter.
        """
        return Iso78_ExchangeApdu(self)
    @property
    def Keyboard_Exist(self) -> Keyboard_Exist:
        """
        Checks if a keyboard is connected. Returns _true_ if this is the case.
        """
        return Keyboard_Exist(self)
    @property
    def Keyboard_CurrentKey(self) -> Keyboard_CurrentKey:
        """
        Returns the keycode of the currently pressed key. This function does not
        perform any key buffering or key repeating avoidance operation.
        """
        return Keyboard_CurrentKey(self)
    @property
    def Keyboard_EnableWakeup(self) -> Keyboard_EnableWakeup:
        """
        Enables the keyboard wake-up feature. When this function is enabled, the
        device will be woken up when it is in power down mode and a key is pressed.
        """
        return Keyboard_EnableWakeup(self)
    @property
    def Keyboard_WaitForKey(self) -> Keyboard_WaitForKey:
        """
        Waits until a key press is detected.
        """
        return Keyboard_WaitForKey(self)
    @property
    def Legic_TransparentCommand4000(self) -> Legic_TransparentCommand4000:
        """
        Transparent command to directly access the LEGIC reader chip modules from the
        4000 series, e.g. the SM-4200 or SM-4500.
        
        Every command which is defined in the LEGIC documentation for the SM-4x00 chip
        may be executed using this pass-through command.
        
        For the direct communication with the SM-4x00 LEGIC defines a protocol frame
        that consists of the following fields (refer also to LEGIC documentation):
        
        LEN  |  CMD  |  DATA[]  |  CRC   
        ---|---|---|---  
          
        The reader firmware handles this frame protocol internally by calculating and
        appending the LEN and CRC fields automatically. The host application only
        specifies the fields CMD and DATA in the transparent command parameters.
        
        The protocol frame for the response consists of the following fields:
        
        LEN  |  CMD  |  STAT  |  DATA[]  |  CRC   
        ---|---|---|---|---  
          
        Similar to the command frame protocol also the response frame protocol is
        handled by the reader firmware. It verifies the CRC checksum and removes the
        LEN, CMD and CRC fields. Only STAT and DATA are returned to the host.
        """
        return Legic_TransparentCommand4000(self)
    @property
    def Legic_TransparentCommand6000(self) -> Legic_TransparentCommand6000:
        """
        Transparent command to directly access the LEGIC reader chip modules from the
        6000 series, e.g. the SM-6300.
        
        Every command which is defined in the LEGIC documentation for the SM-6x00 chip
        may be executed using this pass-through command.
        
        For the direct communication with the SM-6x00 LEGIC defines a protocol frame
        that consists of the following fields (refer also to LEGIC documentation):
        
        LEN  |  CMD  |  DATA[]  |  CRC   
        ---|---|---|---  
          
        The reader firmware handles this frame protocol internally by calculating and
        appending the LEN and CRC fields automatically. The host application only
        specifies the fields CMD and DATA in the transparent command parameters.
        
        The protocol frame for the response consists of the following fields:
        
        LEN  |  CMD  |  STAT  |  DATA[]  |  CRC   
        ---|---|---|---|---  
          
        Similar to the command frame protocol also the response frame protocol is
        handled by the reader firmware. It verifies the CRC checksum and removes the
        LEN, CMD and CRC fields. Only STAT and DATA are returned to the host.
        """
        return Legic_TransparentCommand6000(self)
    @property
    def Lg_Select(self) -> Lg_Select:
        """
        This command selects a specific segment of a LEGIC Prime card and reads some
        data from it.
        
        This command can both access IM cards (standard LEGIC Prime cards containing
        user data) and SAM cards (used for security purposes).
        
        If no label can be detected, the [Lg.Idle](.#Lg.Idle) command is implicitly
        called in order to switch off the HF field. Otherwise, the selected label will
        stay selected until either a new call of the Lg.Select command is performed,
        until the [Lg.Idle](.#Lg.Idle) command is called, if the selected MIM gets out
        of the HF field, or if the [Lg.ErrDataCorrupt](.#Lg.ErrDataCorrupt) error
        occurs.
        
        If several segments are present on the card, only the first segment is
        directly accessible by the reader. All other segments have to be found by
        "jumping" from segment to segment. Therefore the time for selecting a certain
        segment is:
        
        t = 80 ms + SegID * 22 ms
        
        If several segments on the selected card must be accessed, it is recommended
        to always start with the segment which has the lowest ID.
        
        The protocol header-based addressing mode should always be used. The physical
        addressing mode is only applicable for unsegmented MIMs and is therefore
        deprecated.
        
        If the desired data is protected against reading, then the first 5 Bytes of
        the segment, according to the protocol header addressing, will be returned in
        the _Data_ variable instead of the requested data. It is recommended to check
        that the returned value of _Data_ has a length unequal to 5 or to check the
        value of the returned address in the _ActAdr_ variable to make sure that the
        requested data has been properly returned.
        
        If an error status code is returned by this command, no card will be selected.
        
        If [Lg.ErrBusy](.#Lg.ErrBusy) is returned, the reader is still busy with
        reading a SAM card. This occurs when the _TO_ parameter for this command is to
        small to wait for the end of this operation. In this case, the reader will
        reject any LEGIC command by returning the [Lg.ErrBusy](.#Lg.ErrBusy) status
        code until the operation is finished and the stamp is stored in the reader's
        EEPROM.
        
        **To prevent unauthorized writing of stamp data to the reader's EEPROM, it is
        advisable to use a _TO_ value below 0xA0 in your application software.**
        """
        return Lg_Select(self)
    @property
    def Lg_Idle(self) -> Lg_Idle:
        """
        Switch power supply of HF field to the level specified in the _PowOff_
        parameter. Any selected label will no longer be selected.
        """
        return Lg_Idle(self)
    @property
    def Lg_GenSetRead(self) -> Lg_GenSetRead:
        """
        Read stamp data with ID specified in the _GenSetNum_ parameter from the
        reader's EEPROM.
        
        **Responses after _StampLen_ are only transmitted when StatusCode is OK and
        the response length is > 9!**
        """
        return Lg_GenSetRead(self)
    @property
    def Lg_GenSetDelete(self) -> Lg_GenSetDelete:
        """
        Delete stamp data with ID specified in the _GenSetNum_ parameter from the
        reader's EEPROM.
        """
        return Lg_GenSetDelete(self)
    @property
    def Lg_ReadMIM(self) -> Lg_ReadMIM:
        """
        Read _Len_ Bytes from the currently selected card/segment, starting at address
        _Adr_.
        """
        return Lg_ReadMIM(self)
    @property
    def Lg_ReadMIMCRC(self) -> Lg_ReadMIMCRC:
        """
        This command is similar to the [Lg.ReadMIM](.#Lg.ReadMIM) command, except that
        a CRC checksum is calculated over the read Bytes and compared to the CRC
        checksum given in the _CRCAdr_ parameter. If these checksums differ, the
        [Lg.ErrCrc](.#Lg.ErrCrc) status code will be returned. Depending on the value
        of the _CRCCalc_ flag given as a parameter in the [Lg.Select](.#Lg.Select)
        command, either 8-bit or 16-bit checksums will be used.
        """
        return Lg_ReadMIMCRC(self)
    @property
    def Lg_WriteMIM(self) -> Lg_WriteMIM:
        """
        Write data to selected card/segment.
        """
        return Lg_WriteMIM(self)
    @property
    def Lg_WriteMIMCRC(self) -> Lg_WriteMIMCRC:
        """
        This command is similar to the [Lg.WriteMIM](.#Lg.WriteMIM) command, except
        that a CRC checksum is calculated over the data to write and compared to the
        CRC checksum given in the _CRCAdr_ parameter. If these checksums differ, the
        [Lg.ErrCrc](.#Lg.ErrCrc) status code will be returned. Depending on the value
        of the _CRCCalc_ flag given as a parameter in the [Lg.Select](.#Lg.Select)
        command, either 8-bit or 16-bit checksums will be used.
        """
        return Lg_WriteMIMCRC(self)
    @property
    def Lg_MakeMIMCRC(self) -> Lg_MakeMIMCRC:
        """
        Create CRC checksum at _CRCAdr_ for a data block of length _Len_ present at
        address _Adr_. Depending on the value of the _CRCCalc_ flag given as a
        parameter in the [Lg.Select](.#Lg.Select) command, either an 8-bit or 16-bit
        checksum will be created.
        """
        return Lg_MakeMIMCRC(self)
    @property
    def Lg_ReadSMStatus(self) -> Lg_ReadSMStatus:
        """
        Retrieve status information from LEGIC prime SM 05 chip as well as information
        from the currently selected MIM.
        """
        return Lg_ReadSMStatus(self)
    @property
    def Lg_SetPassword(self) -> Lg_SetPassword:
        """
        Activates password protection for the SC-2560.
        """
        return Lg_SetPassword(self)
    @property
    def Lg_Lock(self) -> Lg_Lock:
        """
        Locks the SC-2560.
        """
        return Lg_Lock(self)
    @property
    def Lg_Unlock(self) -> Lg_Unlock:
        """
        Unlocks the SC-2560 with a password.
        """
        return Lg_Unlock(self)
    @property
    def Lga_TransparentCommand(self) -> Lga_TransparentCommand:
        """
        Transparent command to directly access the Legic reader chip module.
        
        Every command which is defined in the LEGIC documentation for the SC-2560
        module or the SM-4x00 chip may be executed using this pass-through command.
        
        For the direct communication with the reader chips SC-2560 or SM-4x00 LEGIC
        defines a protocol frame that consists of the following fields (refer also to
        LEGIC documentation):
        
        NUMBER OF BYTES/LEN  |  CMD  |  DATA[]  |  LRC/CRC   
        ---|---|---|---  
          
        The reader firmware handles this frame protocol internally by calculating and
        appending the NUMBER OF BYTES/LEN and LRC/CRC fields automatically. The host
        application only specifies the fields CMD and DATA in the transparent command
        parameters.
        
        The protocol frame for the response consists of the following fields:
        
        NUMBER OF BYTES/LEN  |  CMD  |  STAT  |  DATA[]  |  LRC/CRC   
        ---|---|---|---|---  
          
        Similar to the command frame protocol also the response frame protocol is
        handled by the reader firmware. It verifies the CRC checksum and removes the
        NUMBER OF BYTES/LEN, CMD and LRC/CRC fields. Only STAT and DATA are returned
        to the host.
        """
        return Lga_TransparentCommand(self)
    @property
    def Lic_GetLicenses(self) -> Lic_GetLicenses:
        """
        This command retrieves a bit mask of the licenses that are activated on the
        reader.
        """
        return Lic_GetLicenses(self)
    @property
    def Lic_ReadLicCard(self) -> Lic_ReadLicCard:
        """
        This command reads and evaluates a LicenseCard.
        
        A license is debited from the card and activated on the reader if the
        following applies:
        
          * The presented card is a valid LicenseCard.
          * This license type is supported by the reader.
          * A license of this type is not yet activated on the reader.
        """
        return Lic_ReadLicCard(self)
    @property
    def Main_Bf2Upload(self) -> Main_Bf2Upload:
        """
        This command transfers a single line of a BF2 file starting with a colon to
        the reader (needed for firmware upload).
        """
        return Main_Bf2Upload(self)
    @property
    def Main_SwitchFW(self) -> Main_SwitchFW:
        """
        After uploading the complete firmware with [Main.Bf2Upload](.#Main.Bf2Upload),
        this command is needed to activate the new firmware and reboot the reader.
        """
        return Main_SwitchFW(self)
    @property
    def Main_MatchPlatformId2(self) -> Main_MatchPlatformId2:
        """
        This command checks if the PlatformID2 of the reader matches the PlatformID2
        provided in the _Filter_ parameter.
        
        **If this command is not available, the[
        Sys.GetPlatformId](system.xml#Sys.GetPlatformId) command can be used as a
        fallback.**
        """
        return Main_MatchPlatformId2(self)
    @property
    def Main_IsFirmwareUpToDate(self) -> Main_IsFirmwareUpToDate:
        """
        This command checks if the following part of the firmware is already up to
        date. It must be called exactly in the order it occurs in the BF2 file: If the
        firmware is split in 2 parts and this command is in between them, it has to be
        called after transferring the first part and before loading the second part.
        Otherwise it is not guaranteed that it works correctly.
        """
        return Main_IsFirmwareUpToDate(self)
    @property
    def Main_Bf3UploadStart(self) -> Main_Bf3UploadStart:
        """
        This command starts the upload of a BEC2/BF3 file to update the reader's
        configuration and/or firmware.  
        The reader responds by requesting the first data block within the BEC2/BF3
        file. To transfer this data block, run the
        [Main.Bf3UploadContinue](.#Main.Bf3UploadContinue) command afterwards.
        
        **For more details about implementation, please refer to the help topic[
        Implement wired upload via the
        host](https://docs.baltech.de/developers/implement-wired-upload.html) .**
        """
        return Main_Bf3UploadStart(self)
    @property
    def Main_Bf3UploadContinue(self) -> Main_Bf3UploadContinue:
        """
        This command is used to transfer the data of a BEC2/BF3 file block by block to
        the reader.  
        The host transfers the data block of the BEC2/BF3 file which has been
        requested by the reader previously. The response parameter _RequiredAction_
        indicates how the host has to proceed afterwards:
        
          * Transfer the next data block. 
          * Disconnect and reconnect to the reader. 
          * Upload completed - no more data to transfer. 
        
        **For more details about implementation, please refer to the help topic[
        Implement wired upload via the
        host](https://docs.baltech.de/developers/implement-wired-upload.html) .**
        """
        return Main_Bf3UploadContinue(self)
    @property
    def Mce_Enable(self) -> Mce_Enable:
        """
        This command enables/disables Mobile Card Emulation (MCE).
        """
        return Mce_Enable(self)
    @property
    def Mce_Request(self) -> Mce_Request:
        """
        This command is used to check if a Mobile Card Emulation (MCE) device (usually
        a smartphone running a particular app) is currently presented to the reader.
        As long as an MCE device is detected, the command returns the serial number
        that has been transferred from the device to the reader.
        
        If no MCE device is detected, the status code [Mce.ErrNoTag](.#Mce.ErrNoTag)
        will be returned. In case MCE is not enabled on the reader,
        [Mce.ErrDisabled](.#Mce.ErrDisabled) will be returned.
        """
        return Mce_Request(self)
    @property
    def Mif_LoadKey(self) -> Mif_LoadKey:
        """
        This command writes a MIFARE Classic key to the reader's secure key memory.
        The reader can store 32 different keys so the key index must not exceed 31.
        These keys will be used for the authentication of certain sectors.
        """
        return Mif_LoadKey(self)
    @property
    def Mif_Request(self) -> Mif_Request:
        """
        Request labels in the field of the antenna.
        
        _ATQA_ is a two byte value (MSB first). This value is called _tagtype_ and for
        MIFARE 1 CSCs, it is expected to be equal to 0x0004.
        
        **For new applications, the[ Iso14a.Request](iso14443a_3.xml#Iso14a.Request)
        command should be used instead.**
        """
        return Mif_Request(self)
    @property
    def Mif_Anticoll(self) -> Mif_Anticoll:
        """
        This command performs an anti-collision sequence.
        
        A number of bits equal to the _BitCount_ value will be used in _PreSelSer_ for
        preselection of cards in the HF field of the antenna. This means that only
        cards with a serial number matching the first _BitCount_ bits of _PreSelSer_
        will be taken into consideration. The command returns an unambiguous serial
        number in the _Snr_ value which may be used for the card selection procedure,
        using the [Mif.Select](.#Mif.Select) command.
        
        **For new applications, the[ Iso14a.Anticoll](iso14443a_3.xml#Iso14a.Anticoll)
        command should be used instead.**
        """
        return Mif_Anticoll(self)
    @property
    def Mif_Select(self) -> Mif_Select:
        """
        This command selects a card with a 4 Byte serial number specified in the _Snr_
        parameter.
        
        **This command is deprecated. For new applications, the[
        Iso14a.Select](iso14443a_3.xml#Iso14a.Select) command should be used
        instead.**
        """
        return Mif_Select(self)
    @property
    def Mif_AuthE2(self) -> Mif_AuthE2:
        """
        This command authenticates a certain sector of a card using a key from the
        secure EEPROM of the Baltech reader chip.
        
        Depending on the value of the _AuthMode_ variable, either key A or key B of
        the sector specified by the _Block_ variable will be compared to the key
        specified in _KeyIdx_.
        
        It is only possible to authenticate one sector at a time.
        """
        return Mif_AuthE2(self)
    @property
    def Mif_AuthUser(self) -> Mif_AuthUser:
        """
        This command authenticates a certain sector of a card using the key specified
        in the _Key_ variable.
        
        Depending on the value of the _AuthMode_ variable, either key A or key B of
        the sector specified by the _Block_ variable will be compared to the key
        specified in _KeyIdx_.
        
        It is only possible to authenticate one sector at a time.
        """
        return Mif_AuthUser(self)
    @property
    def Mif_Read(self) -> Mif_Read:
        """
        This command reads data from a specified block of the currently selected card,
        providing authentication has been performed beforehand.
        """
        return Mif_Read(self)
    @property
    def Mif_Write(self) -> Mif_Write:
        """
        This command write data to a specified block of the currently selected card,
        providing authentication has been performed beforehand.
        """
        return Mif_Write(self)
    @property
    def Mif_ChangeValue(self) -> Mif_ChangeValue:
        """
        This command uses the value block specified by the _Block_ parameter and
        performs an operation given by the _Mode_ parameter. The result is stored in
        the card's Transfer Buffer.
        
        _Mode_ = 1 increments the _value_ , _Mode_ = 0 decrements the value, _Mode_ =
        0x02 simply transfers the value to the Transfer Buffer - the _Value_ parameter
        is ignored.
        
        In order to persistently store the calculated value on the card, a _transfer_
        operation, using the [Mif.TransferBlock](.#Mif.TransferBlock) command, has to
        be performed directly after the completion of this command.
        
        This command can be used for MIFARE Classic cards and only works on value
        sectors.
        
        **This command is not supported by LEGIC readers.**
        """
        return Mif_ChangeValue(self)
    @property
    def Mif_ChangeValueBackup(self) -> Mif_ChangeValueBackup:
        """
        This command is identical to [Mif.ChangeValue](.#Mif.ChangeValue), but can
        only be used for MIFARE cards which support automatic transfer, such as _Pro_
        or _Light_ MIFARE variants.
        
        **This command is not supported by LEGIC readers.**
        """
        return Mif_ChangeValueBackup(self)
    @property
    def Mif_TransferBlock(self) -> Mif_TransferBlock:
        """
        This command transfers data from the card's internal Transfer Buffer to a
        specified block.
        
        This command needs to be called directly after any operation on the internal
        data register performed by [Mif.ChangeValue](.#Mif.ChangeValue) or
        [Mif.ChangeValueBackup](.#Mif.ChangeValueBackup) in order to make the results
        of these commands persistent.
        
        **This command is not supported by LEGIC readers.**
        """
        return Mif_TransferBlock(self)
    @property
    def Mif_Halt(self) -> Mif_Halt:
        """
        Switch card to halt state. The card has to be selected before it may be
        switched to halt state.
        """
        return Mif_Halt(self)
    @property
    def Mif_AuthE2Extended(self) -> Mif_AuthE2Extended:
        """
        This command is identical to the [Mif.AuthE2](.#Mif.AuthE2) command with the
        exception that it supports stronger authentication methods (MIFARE and AES),
        supported by MIFARE Pro cards.
        
        **MIFARE Plus SL2 support was deprecated and removed in firmware 2.12.00. It
        is unsupported in this and all later versions.**
        """
        return Mif_AuthE2Extended(self)
    @property
    def Mif_AuthUserExtended(self) -> Mif_AuthUserExtended:
        """
        This command is identical to the [Mif.AuthUser](.#Mif.AuthUser) command with
        the exception that it supports stronger authentication methods (MIFARE and
        AES), supported by MIFARE Pro cards.
        
        **MIFARE Plus SL2 support was deprecated and removed in firmware 2.12.00. It
        is unsupported in this and all later versions.**
        """
        return Mif_AuthUserExtended(self)
    @property
    def Mif_ResetAuth(self) -> Mif_ResetAuth:
        """
        This command resets the reader's authentication state (used for MIFARE Pro
        specific Read/Write counters.
        """
        return Mif_ResetAuth(self)
    @property
    def Mif_ReadSL3(self) -> Mif_ReadSL3:
        """
        This command reads blocks from an SL3-authenticated MIFARE Pro card.
        """
        return Mif_ReadSL3(self)
    @property
    def Mif_WriteSL3(self) -> Mif_WriteSL3:
        """
        This command writes blocks to an SL3-authenticated MIFARE Pro card.
        """
        return Mif_WriteSL3(self)
    @property
    def Mif_ChangeAESKey(self) -> Mif_ChangeAESKey:
        """
        This command changes an AES key on a MIFARE Plus card.
        """
        return Mif_ChangeAESKey(self)
    @property
    def Mif_ValueSL3(self) -> Mif_ValueSL3:
        """
        This command performs an operation on a value block.
        
        It can be used for MIFARE Plus cards in security level 3.
        """
        return Mif_ValueSL3(self)
    @property
    def Mif_ProxCheck(self) -> Mif_ProxCheck:
        """
        This command performs a proximity check. The key-related parameters are only
        used if no authentication has been performed before this command is called.
        """
        return Mif_ProxCheck(self)
    @property
    def Mif_GetCardVersion(self) -> Mif_GetCardVersion:
        """
        This command returns HW- / SW- / Production-Information. (only MIFARE+ EV1 and
        newer)
        """
        return Mif_GetCardVersion(self)
    @property
    def Mif_ReadSig(self) -> Mif_ReadSig:
        return Mif_ReadSig(self)
    @property
    def Mif_VirtualCardSelect(self) -> Mif_VirtualCardSelect:
        """
        Command is only supported by MIFARE Plus EV1 cards. Selected in ISO14443-3
        mode the VCSupportLastISOL3 command is executed. Selected in ISO14443-4 mode
        the IsoSelect command is executed If the card answers in the latter case with
        a Payload (UID does not match or authentication with VCSelection is mandatory)
        the reader executes an additional ISOExternalAuthentication command
        """
        return Mif_VirtualCardSelect(self)
    @property
    def Mif_SectorSwitch(self) -> Mif_SectorSwitch:
        """
        This command performs a sector switch command (only for EV1 cards). Prior the
        card has to be set in 14443-4 mode, all sectors are addressed with sector Key
        B.
        """
        return Mif_SectorSwitch(self)
    @property
    def Mif_CommitReaderID(self) -> Mif_CommitReaderID:
        """
        This commands commits a reader ID from a card and returns the encrypted TMRI
        to the host. Authentication must take place before using this command.
        """
        return Mif_CommitReaderID(self)
    @property
    def Mif_SetFraming(self) -> Mif_SetFraming:
        """
        This command switches the communication protocol mode for MIFARE Plus EV1
        cards.
        """
        return Mif_SetFraming(self)
    @property
    def MobileId_Enable(self) -> MobileId_Enable:
        """
        This command enables/disables Mobile ID.
        """
        return MobileId_Enable(self)
    @property
    def MobileId_GetVirtualCredentialId(self) -> MobileId_GetVirtualCredentialId:
        """
        This command checks if a Mobile ID credential has been presented to the reader
        since the last _MobileId.GetVirtualCredentialId_ execution.
        
          * If a valid credential is detected, the credential identification will be returned in _CredentialId_. 
          * If no credential is detected, the [MobileId.ErrNoCredential](.#MobileId.ErrNoCredential) status code will be returned. 
          * If an invalid credential is detected, one of the other status codes will be returned. 
        
        **If you use Autoread, run[ AR.GetMessage](../cmds/autoread.xml#AR.GetMessage)
        instead of this command to retrieve the ID of a presented credential.**
        """
        return MobileId_GetVirtualCredentialId(self)
    @property
    def MsgQueue_GetMsgSize(self) -> MsgQueue_GetMsgSize:
        """
        Retrieve the maximum message size the reader supports. If a message exceeds
        this value the commands Send and SendReceive return the status code
        MSGQ_BUFOVERFLOW_ERR.
        """
        return MsgQueue_GetMsgSize(self)
    @property
    def MsgQueue_Receive(self) -> MsgQueue_Receive:
        """
        Wait for a message and return its content. If no message is received within
        Timeout ms MSGQ_RECV_TIMEOUT_ERR is returned. If a previously sent message has
        not been picked up by another host within Timeout ms MSGQ_NOTACKED_TIMEOUT_ERR
        is returned.
        """
        return MsgQueue_Receive(self)
    @property
    def MsgQueue_Send(self) -> MsgQueue_Send:
        """
        Put a message into the Message Queue and wait a maximum time of Timeout ms
        until the message has been picked up. If the queue already contains a message
        that originates from another host MSGQ_COLLISION_ERR is returned; the message
        must be removed from the queue first with the Receive command. If the message
        is not picked up from another host within Timeout ms MSGQ_NOTACKED_TIMEOUT_ERR
        is returned.
        """
        return MsgQueue_Send(self)
    @property
    def MsgQueue_SendReceive(self) -> MsgQueue_SendReceive:
        """
        This command combines Send and Receive to a single command. It sends a message
        and then waits for the reception of a new message.
        """
        return MsgQueue_SendReceive(self)
    @property
    def Pico_SetHfMode(self) -> Pico_SetHfMode:
        """
        Specify HF communication mode that should be used by the commands in this
        command-set.
        """
        return Pico_SetHfMode(self)
    @property
    def Pico_RequestAnticoll(self) -> Pico_RequestAnticoll:
        """
        Request PICCs and perform anticollision.
        """
        return Pico_RequestAnticoll(self)
    @property
    def Pico_Select(self) -> Pico_Select:
        """
        Select PICC.
        """
        return Pico_Select(self)
    @property
    def Pico_Halt(self) -> Pico_Halt:
        """
        Set PICC to halt mode.
        """
        return Pico_Halt(self)
    @property
    def Pico_SelectBookPage(self) -> Pico_SelectBookPage:
        """
        Selects book and page of a selected picopass label
        """
        return Pico_SelectBookPage(self)
    @property
    def Pico_Authenticate(self) -> Pico_Authenticate:
        """
        Authenticates a previously selected picopass label
        """
        return Pico_Authenticate(self)
    @property
    def Pico_Read(self) -> Pico_Read:
        """
        Reads a picopass label
        """
        return Pico_Read(self)
    @property
    def Pico_Write(self) -> Pico_Write:
        """
        Writes to picopass label
        """
        return Pico_Write(self)
    @property
    def Pki_PfsGenKey(self) -> Pki_PfsGenKey:
        """
        This command prepares a perfect forward secrecy (PFS) session by exchanging
        the public part of temporary elliptic curve cryptography (ECC) keys generated
        by host and reader. These are needed by the
        [Pki.PfsAuthHostCert](.#Pki.PfsAuthHostCert) and
        [Pki.PfsAuthRdrCert](.#Pki.PfsAuthRdrCert) commands.
        
        The next step in negotiating a session key can be performed by running the
        [Pki.PfsAuthHostCert](.#Pki.PfsAuthHostCert) command.
        
        If a session key was negotiated before running this command, it will be
        invalidated. For this reason, it is not possible to exchange encrypted
        commands until finalizing the session setup sequence.
        
        The temporary keys generated by the host (_TmpHostPubKey_ parameter) and by
        the reader (_TmpRdrPubKey_ response variable) follow the Abstract Syntax
        Notation One (ASN.1) Distinguished Encoding Rules (DER) format. An example of
        the format for such keys is as follows:
        
        30 59 30 13 06 07 2A 86 48 CE 3D 02 01 06 08 2A 86 48 CE 3D 03 01 07 03 42 00
        04 0C C2 D2 24 16 47 4B DC A1 39 52 08 73 B7 6E A1 32 40 34 7B 8D 70 2F E1 FC
        CC 93 81 ED EF 65 8E 0C 49 A8 63 0F 23 65 07 5F C1 19 3A 3B 90 4F CA 35 E7 18
        52 F7 95 AA CF FB FE 96 66 3D 44 0A BA
        
        Please not that the initial part of the key (30 59 30 13 06 07 2A 86 48 CE 3D
        02 01 06 08 2A 86 48 CE 3D 03 01 07) is the ASN.1 DER-specific header and must
        always be identical.
        
        **This command needs a long timeout, since the ECC operations may take up to
        15 seconds.**
        """
        return Pki_PfsGenKey(self)
    @property
    def Pki_PfsAuthHostCert(self) -> Pki_PfsAuthHostCert:
        """
        This command authenticates the host's certificate chain to the reader. If the
        certificate chain is longer than one certificate, this command has to be
        called multiple times with the _IsEndCert_ flag of the _EncryptedPayload_
        parameter set to 0, until the last certificate has been reached in which case
        it must be set to 1.
        
        The certificates must comply with the following limitations:
        
          * Certificates have to be X.509 v3 certificates. 
          * As signing algorithms, only ECC P-256 and SHA256 are allowed. 
          * The only allowed extensions are _basicConstraints_ (indicating the certificate is a CA certificate) and the (optional) Baltech proprietary certificate _acMask_ using the ASN.1 object identifier (OID) _1.3.6.1.4.1.44885.1_. 
        
        The 32-bit _acMask_ extension makes it possible to further restrict the
        allowed operations by the reader in the Security Level corresponding to the
        certificate since it will be combined with the reader's internal 32-bit
        _Access Condition Mask_ , using a logical _AND_ operator.
        
        If this command is called multiple times (since the certificate chain contains
        multiple entries), it is required that the _SecLevel_ and _SessionTimeout_
        field always have the same value.
        
        If the format of _HostCert_ is invalid or if the signature verification fails,
        the ERR_CERT status code is returned.
        
        **This command needs a long timeout, since the ECC operations may take up to
        15 seconds.**
        """
        return Pki_PfsAuthHostCert(self)
    @property
    def Pki_PfsAuthRdrCert(self) -> Pki_PfsAuthRdrCert:
        """
        After successfully authenticating the host against the reader using the
        [Pki.PfsAuthHostCert](.#Pki.PfsAuthHostCert) command, the reader must return
        its own certificate to the host in order the host to verify it.
        
        This command will finalize the PFS session setup and calculate the new AES-128
        session key. This session key has to be used for all following calls of the
        [Pki.Tunnel2](.#Pki.Tunnel2) command.
        
        **This command needs a long timeout, since the ECC operations may take up to
        15 seconds.**
        """
        return Pki_PfsAuthRdrCert(self)
    @property
    def Pki_Tunnel2(self) -> Pki_Tunnel2:
        """
        Runs a command in the Security Level authenticated by the
        [Pki.PfsGenKey](.#Pki.PfsGenKey),
        [Pki.PfsAuthHostCert](.#Pki.PfsAuthHostCert),
        [Pki.PfsAuthRdrCert](.#Pki.PfsAuthRdrCert) commands sequence. The command is
        encrypted with the session key calculated by
        [Pki.PfsAuthRdrCert](.#Pki.PfsAuthRdrCert).
        
        After the reader decrypts the received tunnelled command, it checks whether
        this command is blocked by the _Access Condition Mask_ assigned to the
        Security Level or by one of the Access Condition Masks of the certificates in
        the host certificate chain. If this command is blocked by one of these Access
        Condition Masks, it is not allowed to be executed in the given Security Level
        and the [ErrAccessDenied](protocol_errors.xml#ErrAccessDenied) status code is
        returned.
        """
        return Pki_Tunnel2(self)
    @property
    def Pki_GetX509Csr(self) -> Pki_GetX509Csr:
        """
        Every reader is shipped with a unique ECC P-256 key, generated at the time of
        manufacturing. This command returns a certificate signing request (CSR) over
        the public part of the reader's key, which can be signed by a certificate
        authority. To store the signed certificate on the reader, run the
        [Pki.StoreX509Cert](.#Pki.StoreX509Cert) command afterwards.
        """
        return Pki_GetX509Csr(self)
    @property
    def Pki_StoreX509Cert(self) -> Pki_StoreX509Cert:
        """
        After signing a CSR using the [Pki.GetX509Csr](.#Pki.GetX509Csr) command, run
        this command to store the resulting in the reader's certificate store. The
        certificate store provides up to 3 slots (for security level 1-3). This means
        up to 3 different certificate authorities can store their certificates in a
        reader.
        
        The certificates must comply with the following limitations:
        
          * Only ECC P-256 and SHA256 are allowed as signing algorithms. 
          * The length of the tag containing the issuer distinguished name must not exceed 128 Bytes. 
          * No extensions are allowed. 
        
        A sample certificate matching all these limitations is the following:
        
        30 82 01 6C 30 82 01 11 A0 03 02 01 02 02 01 01 30 0A 06 08 2A 86 48 CE 3D 04
        03 02 30 3C 31 23 30 21 06 03 55 04 03 0C 1A 49 6E 74 65 72 6D 65 64 69 61 74
        65 20 43 41 20 66 6F 72 20 52 65 61 64 65 72 31 15 30 13 06 03 55 04 0A 0C 0C
        43 75 73 74 6F 6D 65 72 20 4F 6E 65 30 1E 17 0D 30 30 30 31 30 31 30 30 30 30
        30 30 5A 17 0D 33 38 30 31 31 39 30 32 31 34 30 37 5A 30 42 31 14 30 12 06 03
        55 04 03 0C 0B 53 23 20 31 31 31 31 31 31 31 31 31 13 30 11 06 03 55 04 0A 0C
        0A 42 61 6C 74 65 63 68 20 41 47 31 15 30 13 06 03 55 04 07 0C 0C 48 61 6C 6C
        62 65 72 67 6D 6F 6F 73 30 59 30 13 06 07 2A 86 48 CE 3D 02 01 06 08 2A 86 48
        CE 3D 03 01 07 03 42 00 04 C3 4D 0E D2 EA 8F 94 88 93 E0 16 75 06 78 67 BB 96
        14 5A A9 24 F8 95 02 4F 47 87 C7 1C B3 1F D5 83 CD 8C A3 FB B2 57 51 38 BF 81
        AA 9C 26 DC CA 71 A6 FE 83 1B 2C 88 60 86 69 D3 53 93 08 39 D7 30 0A 06 08 2A
        86 48 CE 3D 04 03 02 03 49 00 30 46 02 21 00 90 6F 97 EF C0 95 1C 9C FC 60 4C
        1F F7 12 00 F4 C8 2C EA FE 4E 9D C9 F0 BE 29 75 C6 E6 42 3C 1B 02 21 00 BB 22
        42 56 13 5A B5 BF D1 19 B7 40 EA 44 30 2B 14 3B 86 4E 0C 48 24 96 8F FB 49 69
        24 71 CA DF
        
        This sample certificate can be decoded using the following online tool:
        <https://redkestrel.co.uk/products/decoder/>
        
        Furthermore, the access conditions mask of the security level running the
        Pki.StoreX509Cert command has to allow setting the corresponding key
        (SEC_SETKEY1, SEC_SETKEY2 or SEC_SETKEY3 bit of the access condition mask must
        be set).
        
        **This command needs a long timeout, since the ECC operations may take up to
        15 seconds.**
        """
        return Pki_StoreX509Cert(self)
    @property
    def Pki_StoreX509RootCert(self) -> Pki_StoreX509RootCert:
        """
        Every security level that should be usable with the PKI must be provided with
        a root certificate. The certificate chain provided in the
        [Pki.PfsAuthHostCert](.#Pki.PfsAuthHostCert) command will be verified against
        this root certificate.
        
        The root certificates must comply with the following limitations:
        
          * Certificates have to be X.509 v3 certificates. 
          * Only ECC P-256 and SHA256 are allowed as signing algorithms. 
          * The length of the tags containing the Issuer Unique Identifier and the Subject Unique Identifier must not exceed 128 Bytes. 
          * The only allowed extension is _basicConstraints_ (indicating the certificate is a CA certificate) 
          * The validity period always has to be from "Jan 1 00:00:00 2000 GMT" to "Jan 19 02:14:07 2038 GMT". 
        
        A sample certificate matching all these limitations is the following:
        
        30 82 01 9D 30 82 01 43 A0 03 02 01 02 02 01 01 30 0A 06 08 2A 86 48 CE 3D 04
        03 02 30 41 31 19 30 17 06 03 55 04 03 0C 10 52 6F 6F 74 20 43 65 72 74 69 66
        69 63 61 74 65 31 11 30 0F 06 03 55 04 0A 0C 08 45 71 75 69 74 72 61 63 31 11
        30 0F 06 03 55 04 07 0C 08 57 61 74 65 72 6C 6F 6F 30 1E 17 0D 30 30 30 31 30
        31 30 30 30 30 30 30 5A 17 0D 33 38 30 31 31 39 30 32 31 34 30 37 5A 30 41 31
        19 30 17 06 03 55 04 03 0C 10 52 6F 6F 74 20 43 65 72 74 69 66 69 63 61 74 65
        31 11 30 0F 06 03 55 04 0A 0C 08 45 71 75 69 74 72 61 63 31 11 30 0F 06 03 55
        04 07 0C 08 57 61 74 65 72 6C 6F 6F 30 59 30 13 06 07 2A 86 48 CE 3D 02 01 06
        08 2A 86 48 CE 3D 03 01 07 03 42 00 04 B0 13 B7 1F A6 61 47 8E 8D 2F FC C0 36
        17 C0 51 5D 2A 39 C5 67 15 1A E3 85 2A 3B 9C 2E 93 FA 41 0A B5 F3 66 62 6A F8
        04 D7 0E D1 DB 7A 2D 36 26 0A A5 77 D2 9C D4 65 24 70 DF 9A 74 40 C2 A7 B1 A3
        2C 30 2A 30 0F 06 03 55 1D 13 01 01 FF 04 05 30 03 01 01 FF 30 17 06 09 2B 06
        01 04 01 82 DE 55 01 01 01 FF 04 07 03 05 00 08 00 10 80 30 0A 06 08 2A 86 48
        CE 3D 04 03 02 03 48 00 30 45 02 21 00 BB 42 BB 32 8C D5 68 39 E9 40 28 10 5F
        63 E1 52 9A 63 06 BF B2 69 03 0A F8 9D A5 56 95 CF 0F B2 02 20 35 D6 FF 5C 9A
        42 D9 85 5E F3 16 DA 7A 53 19 F7 74 81 A4 54 B3 D4 C9 74 26 78 D2 1D 11 52 2D
        2A
        
        This sample certificate can be decoded using the following online tool:
        <https://redkestrel.co.uk/products/decoder/>
        
        Furthermore, the access conditions mask of the security llevel running the
        Pki.StoreX509RootCert command has to allow setting the corresponding key
        (SEC_SETKEY1, SEC_SETKEY2 or SEC_SETKEY3 bit of the access condition mask must
        be set).
        
        **This command needs a long timeout, since the ECC operations may take up to
        15 seconds.**
        """
        return Pki_StoreX509RootCert(self)
    @property
    def QKey_Read(self) -> QKey_Read:
        """
        Returns data of quadrakey tags (read only tag).
        """
        return QKey_Read(self)
    @property
    def Rtc_GetTime(self) -> Rtc_GetTime:
        """
        Retrieve current time of on-board RTC.
        """
        return Rtc_GetTime(self)
    @property
    def Rtc_SetTime(self) -> Rtc_SetTime:
        """
        Set the time of the on-board RTC.
        """
        return Rtc_SetTime(self)
    @property
    def Sec_GetAcMask(self) -> Sec_GetAcMask:
        """
        This command retrieves the Access Condition Mask of a specified security
        level.
        
        The Access Condition Mask can be set using the command
        [Sec.SetAcMask](.#Sec.SetAcMask) or by loading a reader configuration file
        which defines the respective configuration values
        [Device/HostSecurity/AccessConditionMask](../cfg/base.xml#Device.HostSecurity.AccessConditionMask).
        
        **In case of security level 0 (plain access) the actual Access Condition Mask
        that is applied by the reader may deviate from the value which is returned by
        this command. Refer to[ Sec.GetCurAcMask](.#Sec.GetCurAcMask) .**
        
        **It is _not_ possible to deny the retrieval of the Access Condition Mask via
        the "Encryption and Authorization" settings in the configuration. This means
        that this command will never return the ERR_ACCESS_DENIED status code.**
        """
        return Sec_GetAcMask(self)
    @property
    def Sec_SetAcMask(self) -> Sec_SetAcMask:
        """
        This command sets the Access Condition Mask of the security level specified in
        the _SecurityLevel_ parameter to the _AcMask_ value.
        
        Alternatively Access Condition Masks may also be set via reader configuration,
        refer to
        [Device/HostSecurity/AccessConditionMask](../cfg/base.xml#Device.HostSecurity.AccessConditionMask).
        
        **The Access Condition Mask of security level 3 is by definition 0xFFFFFFFF.
        It can not be restricted.**
        """
        return Sec_SetAcMask(self)
    @property
    def Sec_SetKey(self) -> Sec_SetKey:
        """
        Sets a key and the appropriate Authorization Mode bits for a specified
        Security Level.
        
        Please note that if _DeriveKey_ is not 0, Sec.SetKey will not use the _Key_
        parameter as a new key value for the authentication of security level
        _SecLevel_ directly. Instead, it encrypts the key specified in _DeriveKey_
        with the key specified in _Key_ (via AES), and uses this encrypted key as a
        new key value for the authentication of security level _SecLevel_.
        
        If one or more of the _SessionKey_ , _MACed_ , _Encrypted_ or _ContinuousIV_
        bits are set, it is not possible to authenticate without the corresponding
        authentication mode setting.
        """
        return Sec_SetKey(self)
    @property
    def Sec_AuthPhase1(self) -> Sec_AuthPhase1:
        """
        This command initiates a 2-phase authentication. The 2-phase authentication is
        required for entering a security level, if its Authorization Mode enforces a
        session key.
        
        In the first phase of the 2-phase authentication, the host sends a random
        number (_RndA_) to the reader. The reader encrypts this number two times,
        using AES128 encryption, with the key of the Security Level specified in
        _SecLevel_ , and sends the result back to the host as _EncRndA_. The host then
        has to check if the reader encrypted the number correctly. If this is the
        case, the reader returns the OK status code and the
        [Sec.AuthPhase2](.#Sec.AuthPhase2) command can be called to initiate the
        second phase of the 2-phase authentication procedure.
        
        If _EncRndA_ is invalid, the reader is configured with an invalid key,
        different from the one expected by the host. In this case, an error status
        code is returned.
        """
        return Sec_AuthPhase1(self)
    @property
    def Sec_AuthPhase2(self) -> Sec_AuthPhase2:
        """
        This command finishes the 2-phase authentication procedure started by the
        [Sec.AuthPhase1](.#Sec.AuthPhase1) command. The host has to encrypt the
        parameter _RndB_ returned by [Sec.AuthPhase1](.#Sec.AuthPhase1) two times,
        using AES128 encryption, with the key of the Security Level specified by the
        _SecLevel_ parameter of [Sec.AuthPhase1](.#Sec.AuthPhase1). The host then
        sends the result back to the reader as _EncRndB_.
        
        If _RndB_ was encrypted correctly, the reader returns the OK status code and
        enters the security level specified in [Sec.AuthPhase1](.#Sec.AuthPhase1) as
        parameter _SecLevel_. Depending on the Authentication Mode, the reader enters
        this Security Level permanently (all subsequent commands are executed in this
        Security Level) or temporarily (only encrypted/MACed commands are executed in
        this Security Level). To ensure that the reader enters the Security Level
        temporarily, one of the _Encrypted_ /_MACed_ flags of the Authentication Mode
        has to be set. Please refer to the [Sec.SetKey](.#Sec.SetKey) command for
        details.
        
        Additionally, the Sec.AuthPhase2 command generates a session key by encrypting
        the _RndA_ parameter of [Sec.AuthPhase1](.#Sec.AuthPhase1) and the _RndB_
        value returned by [Sec.AuthPhase1](.#Sec.AuthPhase1), _each only once_. The
        resulting 16 Byte session key is the result of the encryption of the
        concatenated _RndA_ (first 8 Bytes) and _RndB_ (last 8 Bytes).
        """
        return Sec_AuthPhase2(self)
    @property
    def Sec_Tunnel(self) -> Sec_Tunnel:
        """
        This command enables to send a specific command, called the _tunnelled_
        command, to the reader (and to receive its response) in an encrypted and/or
        MACed fashion.
        
        Depending on the values of the _AuthModeAndSecLevel_ bit mask, the tunnelled
        command will either be encrypted, MACed or both. The structure of the
        _TunnelledCmd_ parameter and of the _TunnelledResp_ response vary depending on
        the encryption/MACing behaviour:
        
          * _Encrypted only_ : 
            * The data has to be padded to the next 16 Byte boundary by appending "00"-Bytes. 
            * The initial vector (IV) has to be reset to all zeros (00 00 ... 00) if if the _ContinuousIV_ flag is not set. If _ContinuousIV_ is set, Cipher Block Chaining (CBC) will be used in the encryption process. In this case, the result from the last block encryption will be used as IV. 
        
            * The padded data is encrypted using AES128 in CBC mode. The key for encryption is either the key assigned to the currently selected Security Level or, if the _SessionKey_ flag is set, the session key derived from the values _RndA_ and _RndB_ of the [Sec.AuthPhase1](.#Sec.AuthPhase1) command: 
        
        _SessionKey = encrypt(RndA[0..7] + RndB[8..15])_
        
          * _Encrypted and MACed_ : Same as the _encrypted only_ variant, but a number of padding Bytes (at least 8) are appended to the encrypted data before transmission. The receiver always has to check whether the padding Bytes have the 0x00 value. If not, the frame is considered invalid. 
          * _MACed only_ : The encryption process is applied to the data which has to be MACed, but unlike in the _encryption only_ mode, the data is not modified. The first 8 Bytes of the hash value resulting from the encryption process (normally used as an IV for the next data block) are simply appended to the original data block to get the MACed data block. 
        
        **This command must not be used in BRP _Repeat Mode_ .**
        """
        return Sec_Tunnel(self)
    @property
    def Sec_Reset(self) -> Sec_Reset:
        """
        This command resets the Baltech ID engine's security system. After its
        execution, all security features will be disabled and the whole memory (i.e.
        the whole configuration) will be deleted.
        
        Unless a [Sec.LockReset](.#Sec.LockReset) was executed beforehand, this
        command runs in every security level. If available, factory settings as well
        as "Encryption and Authorization" settings are restored.
        """
        return Sec_Reset(self)
    @property
    def Sec_LockReset(self) -> Sec_LockReset:
        """
        This command prevents, that a [Sys.FactoryReset](system.xml#Sys.FactoryReset)
        is run for the Security Level specified in the _SecLevel_ command. See also
        [Sec.SetAcMask](.#Sec.SetAcMask).
        """
        return Sec_LockReset(self)
    @property
    def Sec_GetCurAcMask(self) -> Sec_GetCurAcMask:
        """
        This command retrieves the Access Condition Mask, which is applied by the
        reader in the current context (i.e. security level, protocol).
        
        If this command is executed in security level 1-3 the actual Access Condition
        Mask is defined by the value which has been set for the particular security
        level before via [Sec.SetAcMask](.#Sec.SetAcMask) command respectively the
        configuration value
        [Device/HostSecurity/AccessConditionMask](../cfg/base.xml#Device.HostSecurity.AccessConditionMask).
        In this case this command is identical to [Sec.GetAcMask](.#Sec.GetAcMask) for
        the respective security level.
        
        In case of security level 0 (plain access) the applied Access Condition Mask
        is determined by the protocol-specific Access Condition Mask (
        [Protocols/AccessConditionsBitsStd](../cfg/protocols.xml#Protocols.AccessConditionBitsStd),
        [Protocols/AccessConditionsBitsAlt](../cfg/protocols.xml#Protocols.AccessConditionBitsAlt)).
        If this value is not available for the particular protocol the reader uses the
        value that has been set with [Sec.SetAcMask](.#Sec.SetAcMask) respectively
        [Device/HostSecurity/AccessConditionMask[0]](../cfg/base.xml#Device.HostSecurity.AccessConditionMask)
        before in combination (bitwise AND) with a hard-coded default value as
        fallback; in most cases this default value corresponds to all access rights -
        for BRP over TCP it is zero.
        
        **It is _not_ possible to deny the retrieval of the Access Condition Mask via
        the "Encryption and Authorization" settings in the configuration. This means
        that this command will never return the ERR_ACCESS_DENIED status code.**
        """
        return Sec_GetCurAcMask(self)
    @property
    def Srix_Select(self) -> Srix_Select:
        """
        This command selects a label including anticollision.
        """
        return Srix_Select(self)
    @property
    def Srix_Read(self) -> Srix_Read:
        """
        This command reads a secure data page
        """
        return Srix_Read(self)
    @property
    def Srix_Write(self) -> Srix_Write:
        """
        This command writes data to a page address of a label.
        """
        return Srix_Write(self)
    @property
    def Sys_GetBufferSize(self) -> Sys_GetBufferSize:
        """
        This command returns the maximum sizes of
        [command](https://docs.baltech.de/developers/brp-command-frame.html) and
        [response](https://docs.baltech.de/developers/brp-response-frame.html) frames
        that the reader can send and receive. This information is indicated by 3
        return values: _MaxSendSize_ , _MaxRecvSize_ , and _TotalSize_. They're
        determined by the firmware.
        
        **You need to comply with _all_ 3 values in your application: It's not enough
        if the command frame size and the expected response frame size are each
        smaller than or equal to _MaxSendSize_ and _MaxRecvSize_ , respectively. Their
        combined frame size must not exceed _TotalSize_ either. If _all_ 3 values are
        < 128 bytes, you don't need to use _Sys_GetBufferSize_ because this is the
        minimum size that all BALTECH readers support.**
        """
        return Sys_GetBufferSize(self)
    @property
    def Sys_HFReset(self) -> Sys_HFReset:
        """
        This command turns the HF antenna off or on.
        
        **You cannot use it in combination with[ VHL commands](vhl.xml) .**
        
        The behavior is as follows:
        
          * When the antenna is _on_ , the command turns it off for the time defined in _OffDuration_. To turn it off permanently, set the value to 0. 
          * When the antenna is _off_ , the command turns it on. To do so, set _OffDuration_ > 0\. 
        
        **The HF antenna is turned _off_ after booting. If, however, the reader is
        configured for[ Autoread](https://docs.baltech.de/developers/map-
        autoread.html) , the HF antenna is turned on automatically during
        initialization, so you don't need to actively turn it on. This is the default
        behavior as of ID-engine Z.**
        """
        return Sys_HFReset(self)
    @property
    def Sys_Reset(self) -> Sys_Reset:
        """
        This command reboots the reader. Its main purpose is to apply configuration
        changes made e.g. with [Sys.CfgSetValue](.#Sys.CfgSetValue).
        
        ## Close and reopen the connection after running Sys.Reset
        
        Close the connection to the reader immediately after running _Sys.Reset_.
        Depending on the protocol, the connection may be lost. In this case, you need
        to reconnect.
        
        ### When to reconnect?
        
        The reset takes about 500 to 1000 ms to complete. Thus, we recommend you wait
        about 100 ms after closing the connection. Then try to reconnect every 100 ms.
        
        ### When is a reconnect successful?
        
        Consider a reconnect successful as soon as the reader executes a command.
        Opening a port is not a guarantee that you've reconnected.
        """
        return Sys_Reset(self)
    @property
    def Sys_GetInfo(self) -> Sys_GetInfo:
        """
        This command retrieves the firmware string of the reader, which holds
        information about the reader firmware and serial number. It has the following
        format:
        
        _1xxx nnnnnnnnn r.rr.rr dd/dd/dd ssssssss_
        
        _1xxx_ |  ID of firmware (4 digits)   
        ---|---  
        _nnnnnnnnn_ |  Name of firmware (9 alphanumeric characters/spaces)   
        _r.rr.rr_ |  Release of firmware (major release, minor release, build ID)   
        _dd/dd/dd_ |  Date of release   
        _ssssssss_ |  Serial number of reader (8 digits)   
          
        **The combination of ID and release uniquely identifies any firmware version.
        You can use this information e.g. to retrieve the firmware in our download
        area.**
        """
        return Sys_GetInfo(self)
    @property
    def Sys_GetBootStatus(self) -> Sys_GetBootStatus:
        """
        This command retrieves the boot status of the reader, i.e. it describes the
        state of each component of the reader's hardware. Every bit in the returned
        value corresponds to a reader-internal component or a system error. If the
        component couldn't be initialized or the system error is triggered, the
        related bit is set.
        
          * _Error bits (0-23):_ You have to solve these issues before you can use the reader. 
          * _Warning bits (24-31):_ The reader may still work properly. However, we highly recommend you solve these issues as well.
        """
        return Sys_GetBootStatus(self)
    @property
    def Sys_GetPort(self) -> Sys_GetPort:
        """
        This command retrieves the logic state for the custom I/O ports of the module.
        Each module can have up to 16 ports, with each bit of the returned _PortMask_
        value corresponding to a port. _1_ corresponds to high state (VCC), while _0_
        corresponds to low state (GND).
        """
        return Sys_GetPort(self)
    @property
    def Sys_SetPort(self) -> Sys_SetPort:
        """
        **Please use[ UI.Enable](userinterface.xml#UI.Enable) and[
        UI.Disable](userinterface.xml#UI.Disable) instead of this command for new
        applications.**
        
        Sets/clears custom I/O ports of the module. Every bit in _PortMask_ is
        assigned to an I/O port. By calling this command all output ports are set.
        Some ports need to be configured as output ports before being set via this
        command.
        """
        return Sys_SetPort(self)
    @property
    def Sys_CfgGetValue(self) -> Sys_CfgGetValue:
        """
        This command retrieves a desired value of the reader's configuration,
        specified by the _Key_ and _Value_ parameters.
        """
        return Sys_CfgGetValue(self)
    @property
    def Sys_CfgSetValue(self) -> Sys_CfgSetValue:
        """
        This command stores a value in the reader's configuration. The _Content_
        parameter will be stored to the desired configuration value specified by the
        _Key_ and _Value_ parameters. If the value is already stored in the
        configuration, it will be replaced.
        """
        return Sys_CfgSetValue(self)
    @property
    def Sys_CfgDelValues(self) -> Sys_CfgDelValues:
        """
        This command deletes a key or a value from the reader's configuration.
        
          * It is possible to use the wildcard character (0xFF). 
          * If 0xFF is used as _Value_ , all values of the given _Key_ will be deleted. For instance, setting 0x0101 as _Key_ and 0xFF as _Value_ will delete all configuration values within the key 0x0101. 
          * If 0xFF is used as SubKey (low order byte of the _Key_ variable), all SubKeys from a specified MasterKey will be deleted. For instance, setting 0x01FF as _Key_ delete all SubKeys and thus also all values contained in MasterKey 0x01. The content of the _Value_ variable is irrelevant in this case. 
          * If 0xFF is used as MasterKey (high order byte of the _Key_ variable), the complete configuration will be deleted. The contents of the low order byte of the _Key_ variable and of the _Value_ variable are irrelevant in this case. 
          * This command is subject to potential restrictions . Specifically, SubKeys >= 0x80 are not deleted when the 0xFF wildcard is used. Deletion of these SubKeys must be performed explicitly.
        """
        return Sys_CfgDelValues(self)
    @property
    def Sys_CfgGetKeyList(self) -> Sys_CfgGetKeyList:
        """
        Retrieves a list of all keys stored in the reader's configuration.
        """
        return Sys_CfgGetKeyList(self)
    @property
    def Sys_CfgGetValueList(self) -> Sys_CfgGetValueList:
        """
        Returns a list of all configuration values within a specified _Key_.
        """
        return Sys_CfgGetValueList(self)
    @property
    def Sys_CfgWriteTlvSector(self) -> Sys_CfgWriteTlvSector:
        """
        **Please use[ Sys.CfgLoadBlock](.#Sys.CfgLoadBlock) instead of this command
        for new applications.**
        
        This command parses the given TLV block and stores all its keys and values
        into the reader's configuration memory.
        """
        return Sys_CfgWriteTlvSector(self)
    @property
    def Sys_CfgCheck(self) -> Sys_CfgCheck:
        """
        This command checks the consistency of the reader's internal configuration.
        Additionally, it returns the overall configuration data size as well as the
        amount of free space for further configuration data. Please keep in mind that
        each value (including empty values) requires a few extra bytes of overhead for
        data management purposes.
        
        **Starting with reader generation ID-engine Z, configuration consistency is
        always checked during powerup. That's why this command is no longer needed and
        always returns 0 (for _TotalSize_ and _FreeSize_ ) without any further
        checks.**
        """
        return Sys_CfgCheck(self)
    @property
    def Sys_ConfigPort(self) -> Sys_ConfigPort:
        """
        Configures generic I/O ports for input/output.
        
        **Some ports are unidirectional (only usable either as an input or as an
        output). Only bidirectional ports can be reconfigured via this command.**
        
        **I/O Port configuration can also be performed via scripts in the
        configuration editor. See the[ BaltechScript
        documentation](../cfg/baltechscript.xml#BaltechScript) for further details.**
        """
        return Sys_ConfigPort(self)
    @property
    def Sys_SetRegister(self) -> Sys_SetRegister:
        """
        Sets one or multiple of the reader's internal registers.
        
        **To reset a register, its _Value_ should be set to 0xFFFF.**
        
        **If the parameter _ResetRegister_ is set to _True_ , all registers of the
        reader will be reset.**
        
        **Register setting operations are usually performed by changing the relevant
        configuration values.**
        """
        return Sys_SetRegister(self)
    @property
    def Sys_GetRegister(self) -> Sys_GetRegister:
        """
        Retrieves one of the reader's internal registers.
        
        **Register setting operations are usually performed by changing the relevant
        configuration values.**
        """
        return Sys_GetRegister(self)
    @property
    def Sys_PowerDown(self) -> Sys_PowerDown:
        """
        Powers off the device.
        
        This command is only supported by Baltech devices with special hardware
        support.
        
        **_WARNING:_ This function has the wrong name. It does not put the device into
        _power down_ mode (low power sleep) but turns it off completely.**
        """
        return Sys_PowerDown(self)
    @property
    def Sys_SelectProtocol(self) -> Sys_SelectProtocol:
        """
        This command starts a host protocol.
        
        Depending on the reader's hardware and firmware, multiple protocols may be
        supported. For most reader-to-host interfaces (e.g. USB, Ethernet), an
        unlimited number of protocols can be used on the physical channel, but in some
        cases only a single protocol per physical channel can be used at a time. This
        is for example the case when using a serial (RS-232/UART) interface, offering
        two physical channels, in which case each physical channel must be shared by
        several protocols.
        
        **After power-up, the reader activates all protocols specified in the[ Device
        / Run / EnabledProtocols](../cfg/base.xml#Device.Run.EnabledProtocols)
        configuration value. To change the activated protocols at runtime, this
        command has to be used.**
        
        In case only a single protocol is allowed to run per physical channel, calling
        this command when a channel is already in use by another protocol will stop
        the currently running protocol.
        
        _Example:_ the protocol is currently running on a serial interface (physical
        channel CH0) when Sys.SelectProtocol is called with _ProtocolID_ = 0x09 (Debug
        Interface). Since the Debug Interface protocol uses the same physical channel
        (CH0), it will be disabled.
        """
        return Sys_SelectProtocol(self)
    @property
    def Sys_SetCommParam(self) -> Sys_SetCommParam:
        """
        This command is only required when the _serial_ host-to-reader interface is in
        use. In case the protocol is running, this command can be used to change the
        settings of the serial line:
        
          * Baud rate 
          * Parity 
          * Character Waiting Time (CWT) 
        
        Usually the reader uses the settings specified in the configuration of the
        reader under the
        [Protocols/BrpSerial](../cfg/protocols.xml#Protocols.BrpSerial) Key. If the
        corresponding configuration values do not exist, the default settings are used
        (Baud rate 115200; no parity; CWT 20 ms).
        
        **The BRP response frame to this command is received according to the _old_
        serial settings. The new serial settings are only in effect starting with the
        next BRP command frame.**
        
        **The parameters set by this command are lost when the reader is powered off
        or reset.**
        
        **CWT must never be smaller than the time needed for transferring a single
        byte. This is especially important when using baud rates smaller than 9600. It
        is good practice to adapt the CWT according to the following equation: CWT =
        10 / baud rate + 10.**
        """
        return Sys_SetCommParam(self)
    @property
    def Sys_CfgLoadBlock(self) -> Sys_CfgLoadBlock:
        """
        This command transfers the configuration from a BEC file into the reader. You
        have to call it for every _block_ tag in the BEC file.
        
        **All _Sys.CfgLoad_ commands only work with the legacy file format BEC. For
        the current[ default format BEC2](https://docs.baltech.de/deployable-file-
        formats) , please use[
        Main.Bf3UploadStart](maintenance.xml#Main.Bf3UploadStart) and[
        Main.Bf3UploadContinue](maintenance.xml#Main.Bf3UploadContinue) as explained
        in this[ overview](https://docs.baltech.de/developers/implement-wired-
        upload.html) .**
        
        ## Commands to run before and after
        
        To initiate the transfer, run [Sys.CfgLoadPrepare](.#Sys.CfgLoadPrepare)
        before the first _Sys.CfgLoadBlock_.  
        For legacy reasons, you can ommit _Sys.CfgLoadPrepare_ because it's not
        supported by readers older than our current product lines based on ID-engine
        Z. In this case, ensure that the _Sys.CfgLoadBlock_ transferring the first
        block of the BEC file is the first _Sys.CfgLoadBlock_ after powerup.
        
        To complete the operation once all _block_ tags are transferred, run
        [Sys.CfgLoadFinish](.#Sys.CfgLoadFinish).  
        If you omit _Sys.CfgLoadPrepare_ for legacy reasons, omit _Sys.CfgLoadFinish_
        as well. In this case, do a [a manual reset](.#Sys.Reset) to activate the
        configuration changes.
        """
        return Sys_CfgLoadBlock(self)
    @property
    def Sys_GetPlatformId(self) -> Sys_GetPlatformId:
        """
        Maintenance command only needed for Baltech internal use to get detailed
        information about the actually used hardware.
        
        **This command must only be used if the[
        Main.MatchPlatformId2](maintenance.xml#Main.MatchPlatformId2) command is not
        supported by the current firmware.**
        """
        return Sys_GetPlatformId(self)
    @property
    def Sys_CfgReset(self) -> Sys_CfgReset:
        """
        Deletes the complete configuration. This command has the same effect as the
        [Sys.CfgDelValues](.#Sys.CfgDelValues) command using 0xFF as MasterKey.
        
        **Like[ Sys.CfgDelValues](.#Sys.CfgDelValues) , this command is subject to
        potential restrictions . Specifically, SubKeys > = 0x80 are not deleted by
        this command. Deletion of these SubKeys must be performed explicitly using[
        Sys.CfgDelValues](.#Sys.CfgDelValues) .**
        """
        return Sys_CfgReset(self)
    @property
    def Sys_StopProtocol(self) -> Sys_StopProtocol:
        """
        This command stops a host protocol. No reaction is expected after the protocol
        has been stopped. More details on protocols can be found in the
        [Sys.SelectProtocol](.#Sys.SelectProtocol) command reference.
        """
        return Sys_StopProtocol(self)
    @property
    def Sys_CfgGetId(self) -> Sys_CfgGetId:
        """
        This command returns the identifier of the reader configuration. The
        prerequisite is that the configuration contains a valid host interface
        component and/or RFID interface component.
        
        **If the RFID interface component(s) are stored in one configuration and other
        components (typically the host interface component) in another configuration,
        this command will only return the ID for the configuration with the RFID
        interface component(s). To get the ID for the configuration with the host
        interface component, run[
        Sys.CfgGetDeviceSettingsId](.#Sys.CfgGetDeviceSettingsId) .**
        """
        return Sys_CfgGetId(self)
    @property
    def Sys_CfgGetDeviceSettingsId(self) -> Sys_CfgGetDeviceSettingsId:
        """
        This command retrieves the ID of the reader configuration containing the
        device settings.
        
        **Use this command if the RFID interface component(s) are stored in one
        configuration and other components (typically the host interface component) in
        another configuration. If you have no RFID interface component or a
        configuration containing all components, run[ Sys.CfgGetId](.#Sys.CfgGetId) to
        get the configuration ID.**
        """
        return Sys_CfgGetDeviceSettingsId(self)
    @property
    def Sys_FactoryResetLegacy(self) -> Sys_FactoryResetLegacy:
        """
        **This is a legacy command! For new developments please use[
        Sys.FactoryReset](.#Sys.FactoryReset) .**
        
        This command resets the device's configuration to the state it had, when
        leaving the factory.
        
        A factory reset is only available on newer devices (about 2017 and later).
        When running it on a older Hardware
        [Sys.ErrNotSupportedByHardware](.#Sys.ErrNotSupportedByHardware) is returned.
        
        **After a factory reset a[ Sys.Reset](.#Sys.Reset) has to be done to ensure
        that the factory settings are fully activated.**
        """
        return Sys_FactoryResetLegacy(self)
    @property
    def Sys_GetStatistics(self) -> Sys_GetStatistics:
        """
        This command retrieves all available statistics counters from the reader's
        configuration. The statistics counters are stored in the [Device /
        Statistics](../cfg/base.xml#Device.Statistics) configuration key.
        
        **This command is designed for Baltech internal use only.**
        """
        return Sys_GetStatistics(self)
    @property
    def Sys_GetFeatures(self) -> Sys_GetFeatures:
        """
        This command retrieves the list of features supported by the reader, so you
        can find out if the reader meets your requirements. The list of features
        includes e.g. supported card types, LEDs, encryption methods, and maintenance
        options. It depends both on the reader hardware and firmware.
        """
        return Sys_GetFeatures(self)
    @property
    def Sys_GetPartNumber(self) -> Sys_GetPartNumber:
        """
        This command returns the part number and the hardware revision number of the
        device. This information, which is usually also printed on the label, allows
        you to identify the reader model type for e.g. reorder purposes.
        
        **Don't use this command to distinguish the device features in your
        application! Use[ Sys.GetFeatures](.#Sys.GetFeatures) instead. The reason is:
        Baltech may offer (replacement) products with the same or a similar feature
        set, which have different part numbers. If the application would stick to a
        certain part number these devices would not be deployable.**
        """
        return Sys_GetPartNumber(self)
    @property
    def Sys_CfgLoadPrepare(self) -> Sys_CfgLoadPrepare:
        """
        This command initiates the transfer of a BEC file via
        [Sys.CfgLoadBlock](.#Sys.CfgLoadBlock). It will cancel any running BEC
        transfer and start loading a new one.
        
        **All _Sys.CfgLoad_ commands only work with the legacy file format BEC. For
        the current[ default format BEC2](https://docs.baltech.de/deployable-file-
        formats) , please use[
        Main.Bf3UploadStart](maintenance.xml#Main.Bf3UploadStart) and[
        Main.Bf3UploadContinue](maintenance.xml#Main.Bf3UploadContinue) as explained
        in this[ overview](https://docs.baltech.de/developers/implement-wired-
        upload.html) .**
        """
        return Sys_CfgLoadPrepare(self)
    @property
    def Sys_CfgLoadFinish(self) -> Sys_CfgLoadFinish:
        """
        This command has to be called after transferring a BEC file with
        [Sys.CfgLoadBlock](.#Sys.CfgLoadBlock). Depending on how you set the parameter
        _FinalizeAction_ , this command will do one of the following:
        
          * Complete the transfer; this requires all _Sys.CfgLoadBlock_ calls to have succeeded. 
          * Cancel the transfer and undo all configuration changes since [Sys.CfgLoadPrepare](.#Sys.CfgLoadPrepare). 
        
        **All _Sys.CfgLoad_ commands only work with the legacy file format BEC. For
        the current[ default format BEC2](https://docs.baltech.de/deployable-file-
        formats) , please use[
        Main.Bf3UploadStart](maintenance.xml#Main.Bf3UploadStart) and[
        Main.Bf3UploadContinue](maintenance.xml#Main.Bf3UploadContinue) as explained
        in this[ overview](https://docs.baltech.de/developers/implement-wired-
        upload.html) .**
        """
        return Sys_CfgLoadFinish(self)
    @property
    def Sys_FactoryReset(self) -> Sys_FactoryReset:
        """
        This command restores the reader's [ factory
        settings](https://docs.baltech.de/project-setup/factory-settings.html).
        """
        return Sys_FactoryReset(self)
    @property
    def Sys_GetLicenses(self) -> Sys_GetLicenses:
        """
        This command retrieves a bit mask of the licenses that are activated in the
        reader.
        """
        return Sys_GetLicenses(self)
    @property
    def Sys_GetFwCrc(self) -> Sys_GetFwCrc:
        """
        Maintenance command only needed for Baltech internal use to get the CRC of the
        firmware.
        """
        return Sys_GetFwCrc(self)
    @property
    def TTF_ReadByteStream(self) -> TTF_ReadByteStream:
        """
        Returns raw data of the 125 kHz HF interface.
        """
        return TTF_ReadByteStream(self)
    @property
    def TTF_IdteckRead(self) -> TTF_IdteckRead:
        """
        Returns data of idteck tags (read only tag).
        """
        return TTF_IdteckRead(self)
    @property
    def EpcUid_UidReplyRound(self) -> EpcUid_UidReplyRound:
        """
        This command scans for labels in the field using time slots. All labels with
        consistent data according to _SelectionMask_ bits are responding in time
        slots. If the _FixSlot_ flag is set, a successfully recognized label (CRC OK)
        will be set to the FIXED SLOT state. All successfully recognized label data
        will be transferred to the host. If the internal reader buffer is to small,
        _MemStatusFlag_ will be set.
        """
        return EpcUid_UidReplyRound(self)
    @property
    def EpcUid_UidWrite(self) -> EpcUid_UidWrite:
        """
        This command writes data Bytes to a label. The address of the data to write is
        specified in the _BlockAdr_ parameter. As an enhancement to the specification,
        multiple Bytes can be written.
        """
        return EpcUid_UidWrite(self)
    @property
    def EpcUid_UidDestroy(self) -> EpcUid_UidDestroy:
        """
        This command will render the label permanently unable to give any replies. The
        command can be used for both EPC and UID labels.
        """
        return EpcUid_UidDestroy(self)
    @property
    def EpcUid_EpcSetMode(self) -> EpcUid_EpcSetMode:
        """
        This command specifies HF coding.
        """
        return EpcUid_EpcSetMode(self)
    @property
    def EpcUid_EpcSelect(self) -> EpcUid_EpcSelect:
        """
        This command selects a particular tag population.
        """
        return EpcUid_EpcSelect(self)
    @property
    def EpcUid_EpcInventory(self) -> EpcUid_EpcInventory:
        """
        This command executes an inventory command.
        """
        return EpcUid_EpcInventory(self)
    @property
    def Ultralight_ExecCmd(self) -> Ultralight_ExecCmd:
        """
        Generic command to communicate to a Mifare Ultralight card.
        """
        return Ultralight_ExecCmd(self)
    @property
    def Ultralight_Read(self) -> Ultralight_Read:
        """
        Standard read command for Ultralight cards. Command returns 4 pages of a card
        (16 byte).
        """
        return Ultralight_Read(self)
    @property
    def Ultralight_Write(self) -> Ultralight_Write:
        """
        Standard write command for Ultralight cards. 1 page (4 bytes) is writen to a
        card.
        """
        return Ultralight_Write(self)
    @property
    def Ultralight_AuthE2(self) -> Ultralight_AuthE2:
        """
        Authenticates to a Ultralight-c card.
        
        The key used for authentication is specified in the [Device /
        CryptoKey](../cfg/base.xml#Device.CryptoKey) key of the reader's
        configuration. Key has to be of type 3DES (16 bytes).
        """
        return Ultralight_AuthE2(self)
    @property
    def Ultralight_AuthUser(self) -> Ultralight_AuthUser:
        """
        Authenticates to an Ultralight-C/EV1 card.
        """
        return Ultralight_AuthUser(self)
    @property
    def Ultralight_SectorSwitch(self) -> Ultralight_SectorSwitch:
        """
        Selects a sector of an Ultralight-C/EV1 card.
        """
        return Ultralight_SectorSwitch(self)
    @property
    def UlRdr_SendAuth1(self) -> UlRdr_SendAuth1:
        """
        Retrieves the command that has to be sent to the reader to unlock, to initiate
        authentication.
        """
        return UlRdr_SendAuth1(self)
    @property
    def UlRdr_RecvAuth1(self) -> UlRdr_RecvAuth1:
        """
        Passes the response of the reader to unlock.
        """
        return UlRdr_RecvAuth1(self)
    @property
    def UlRdr_SendAuth2(self) -> UlRdr_SendAuth2:
        """
        Retrieves the command that has to be send to the reader to unlock, to continue
        authentication.
        """
        return UlRdr_SendAuth2(self)
    @property
    def UlRdr_RecvAuth2(self) -> UlRdr_RecvAuth2:
        """
        Passes the response of the reader to unlock.
        """
        return UlRdr_RecvAuth2(self)
    @property
    def UlRdr_SendEncryptedCmd(self) -> UlRdr_SendEncryptedCmd:
        """
        Encrypts the given command with the session key generated in the previous
        3-pass-authentication. Before doing so, the signature is checked.
        """
        return UlRdr_SendEncryptedCmd(self)
    @property
    def UlRdr_RecvEncryptedCmd(self) -> UlRdr_RecvEncryptedCmd:
        """
        Check the response received by the command
        [UlRdr.SendEncryptedCmd](.#UlRdr.SendEncryptedCmd).
        """
        return UlRdr_RecvEncryptedCmd(self)
    @property
    def UsbHost_Enable(self) -> UsbHost_Enable:
        """
        Enable/Disable the USB-Host-Interface of the uC.
        """
        return UsbHost_Enable(self)
    @property
    def UsbHost_IsConnected(self) -> UsbHost_IsConnected:
        """
        Check if a device is connected.
        """
        return UsbHost_IsConnected(self)
    @property
    def UsbHost_SetupPipes(self) -> UsbHost_SetupPipes:
        """
        Setup all Pipes Definitions (uC's internal configuration).
        """
        return UsbHost_SetupPipes(self)
    @property
    def UsbHost_SetAddr(self) -> UsbHost_SetAddr:
        """
        Set Address of device.
        """
        return UsbHost_SetAddr(self)
    @property
    def UsbHost_Reset(self) -> UsbHost_Reset:
        """
        Send a Reset via USB interface, Remove all Pipes Definitions and reset address
        of device to 0.
        """
        return UsbHost_Reset(self)
    @property
    def UsbHost_TransRawSetup(self) -> UsbHost_TransRawSetup:
        """
        Transfers a raw SETUP packet. Has to be combined with a call of
        [UsbHost.TransSetupIn](.#UsbHost.TransSetupIn) or
        [UsbHost.TransSetupOut](.#UsbHost.TransSetupOut).
        """
        return UsbHost_TransRawSetup(self)
    @property
    def UsbHost_TransSetupIn(self) -> UsbHost_TransSetupIn:
        """
        Transfers a SETUP transaction with a IN DATA stage.
        """
        return UsbHost_TransSetupIn(self)
    @property
    def UsbHost_TransSetupOut(self) -> UsbHost_TransSetupOut:
        """
        Transfers a SETUP transaction with a OUT DATA stage.
        """
        return UsbHost_TransSetupOut(self)
    @property
    def UsbHost_TransIn(self) -> UsbHost_TransIn:
        """
        Transfers an IN transaction.
        """
        return UsbHost_TransIn(self)
    @property
    def UsbHost_TransOut(self) -> UsbHost_TransOut:
        """
        Transfers an OUT transaction.
        """
        return UsbHost_TransOut(self)
    @property
    def UsbHost_Suspend(self) -> UsbHost_Suspend:
        """
        Send a Suspend via USB interface.
        """
        return UsbHost_Suspend(self)
    @property
    def UsbHost_Resume(self) -> UsbHost_Resume:
        """
        Send a Resume via USB interface.
        """
        return UsbHost_Resume(self)
    @property
    def UI_Enable(self) -> UI_Enable:
        """
        This command enables a specific port of the reader.
        
        Depending on the type of the selected port, it does one of the following:
        
          * Drive an output pin high (GPIO)
          * Activate a peripheral component (beeper, relay)
          * Switch an LED to a certain color
        """
        return UI_Enable(self)
    @property
    def UI_Disable(self) -> UI_Disable:
        """
        This command disables a specific port of the reader.
        
        Depending on the type of the selected port, it does one the following:
        
          * Drive an output pin low (GPIO)
          * Deactivate a peripheral component (beeper, relay)
          * Switch an LED off
        """
        return UI_Disable(self)
    @property
    def UI_Toggle(self) -> UI_Toggle:
        """
        This command toggles the output state of a specific port.
        
        A single toggle consists of 2 state changes: From the initial state to the
        inverse state and back. The initial state is defined by the _Polarity_
        parameter. This is also the state of the port at the end of the toggling
        operation.
        
        To stop the toggling, call [UI.Enable](.#UI.Enable) or
        [UI.Disable](.#UI.Disable) for this port.
        """
        return UI_Toggle(self)
    @property
    def UI_SetRgbLed(self) -> UI_SetRgbLed:
        """
        This command changes the RGB color of a single LED or a group of LEDs. The
        color may be activated instantly or smoothly by a sine-wave approximated
        fading transition.
        
        If the addressed LEDs are already active when this command is called, the
        color first fades to black (off), before the transition to the new color
        starts.
        
        **This command gives you direct control of the reader's LEDs. It competes with
        the command[ UI.Enable](.#UI.Enable) , which can be used to switch LEDs via
        Virtual LED port definitions (VLEDs)._UI.Enable_ operates on a higher
        abstraction level. Don't mix the 2 commands as this may result in inconsistent
        behavior.**
        """
        return UI_SetRgbLed(self)
    @property
    def UI_PulseRgbLed(self) -> UI_PulseRgbLed:
        """
        This command starts to pulse a single LED or a group of multiple LEDs
        continuously by performing smooth sine-wave approximated transitions between 2
        RGB colors.
        
        To stop the pulsing, call the command [UI.SetRgbLed](.#UI.SetRgbLed).
        
        **This command gives you direct control of the reader's LEDs. It competes with
        the command[ UI.Enable](.#UI.Enable) , which can be used to switch LEDs via
        Virtual LED port definitions (VLEDs)._UI.Enable_ operates on a higher
        abstraction level. Don't mix the 2 commands as this may result in inconsistent
        behavior.**
        """
        return UI_PulseRgbLed(self)
    @property
    def VHL_Select(self) -> VHL_Select:
        """
        This command selects a card or tag in the antenna field for further
        operations. You need to run it successfully before you can use the following
        VHL commands:
        
          * [VHL.GetSnr](.#VHL.GetSnr)
          * [VHL.GetATR](.#VHL.GetATR)
          * [VHL.Read](.#VHL.Read)
          * [VHL.Write](.#VHL.Write)
          * [VHL.ExchangeAPDU](.#VHL.ExchangeAPDU)
          * [VHL.GetCardType](.#VHL.GetCardType)
        
        ## Handling multiple cards in the antenna field
        
        Using the _Reselect_ parameter, you can interact with a card that you've
        already processed before (learn more in the _Parameters_ section below).
        
        **Certain cards return[ random
        IDs](https://docs.baltech.de/glossary.html#random-id) . If 2 or more cards
        with random IDs _AND_ the same card family are present in the antenna field at
        the same time,_VHL.Select_ detects these cards more than once.**
        
        ## Potential error cases after selection
        
        After running _VHL.Select_ successfully, the above commands will usually be
        executed successfully, even if the card temporarily leaves the antenna field.
        Communication parameters such as _bit rate_ and _frame size_ are automatically
        chosen to optimize performance.
        
        However, problems with certain cards (e.g. MIFARE proX/DESFire) may occur when
        they're in the border area of the antenna field and brought in very slowly. In
        these cases, _VHL.Select_ may be executed successful, but the subsequent
        command may fail.
        
        **In this case, make sure your application guarantees a suitable card
        distance, either by user guidance or by repetition of the[
        VHL.IsSelected](.#VHL.IsSelected) command until its success. This is
        especially important in conjunction with the[
        VHL.ExchangeAPDU](.#VHL.ExchangeAPDU) command since it doesn't perform retries
        internally.**
        """
        return VHL_Select(self)
    @property
    def VHL_GetSnr(self) -> VHL_GetSnr:
        """
        This command returns the serial number (UID) of the currently selected card.
        The UID is the number sent when the card is selected; this may also be a
        random ID.
        
        If [VHL.Select](.#VHL.Select) hasn't been executed successfully before, the
        reader will return [VHL.ErrCardNotSelected](.#VHL.ErrCardNotSelected). If the
        last selected card is no longer available in the antenna field, or a
        read/write operation failed previous to this command, the returned serial
        number is undefined.
        
        **Don't make security-critical decisions by only examining the card's serial
        number.**
        """
        return VHL_GetSnr(self)
    @property
    def VHL_Read(self) -> VHL_Read:
        """
        This command reads data from a card based on a VHL file. In this file, you
        specify the card-specific memory structure. You can either [add the VHL file
        to your reader configuration](https://docs.baltech.de/developers/configure-
        rfid-interface.html#add-a-vhl-file) or create it dynamically using
        [VHL.Setup](.#VHL.Setup).
        """
        return VHL_Read(self)
    @property
    def VHL_Write(self) -> VHL_Write:
        """
        This command writes data to a card based on a VHL file. In this file, you
        specify the card-specific memory structure. You can either [add the VHL file
        to your reader configuration](https://docs.baltech.de/developers/configure-
        rfid-interface.html#add-a-vhl-file) or create it dynamically using
        [VHL.Setup](.#VHL.Setup).
        """
        return VHL_Write(self)
    @property
    def VHL_IsSelected(self) -> VHL_IsSelected:
        """
        This command checks if the card/label selected by the last execution of the
        [VHL.Select](.#VHL.Select) command is still in the HF field of the antenna. If
        the card/label has been taken away from the reader and put back on it _after_
        the last execution of [VHL.Select](.#VHL.Select), or if
        [VHL.Select](.#VHL.Select) has not been called after a card has been put on
        the reader, this command will return the
        [VHL.ErrCardNotSelected](.#VHL.ErrCardNotSelected) status code.
        
        **For 125 kHz cards, a retry is automatically performed in case of a misread
        to improve reliability. Please note that this may increase reaction time for
        125 kHz cards to a maximum of 100 ms.**
        """
        return VHL_IsSelected(self)
    @property
    def VHL_GetLegacyATR(self) -> VHL_GetLegacyATR:
        """
        This command is deprecated and should only be used for compatibility purposes
        with older firmware version. It returns the Answer To Reset (ATR) of the
        currently selected card in a legacy format, i.e. not conform with the [PC/SC
        specification, version
        2](http://pcscworkgroup.com/Download/Specifications/pcsc3_v2.01.09.pdf). For
        new projects it is recommended to use the [VHL.GetATR](.#VHL.GetATR) command
        instead.
        
        If the [VHL.Select](.#VHL.Select) command has not been successfully executed
        before this command, the [VHL.ErrCardNotSelected](.#VHL.ErrCardNotSelected)
        status code will be returned. If the last selected card is no longer available
        in the field of the antenna, or if a read/write operation failed before
        executing this command, the returned ATR is undefined.
        
        The returned _ATR_ variable always has the following format:
        
          * 0x3B 
          * Length of card UID (in bytes) 
          * Card UID
        """
        return VHL_GetLegacyATR(self)
    @property
    def VHL_ExchangeAPDU(self) -> VHL_ExchangeAPDU:
        """
        This command sends APDUs to the currently selected card. APDUs are the
        communication units between a reader and an ISO 14443-4 card. They're defined
        in the [ISO/IEC 7816-4
        standard](http://www.iso.org/iso/catalogue_detail.htm?csnumber=54550).
        _VHL.ExchangeAPDU_ transmits the actual APDU command via the _Cmd_ parameter
        and returns the APDU response as _Resp_.
        
        ## Keep an eye on the frame size
        
        The combined size of transmitted and received APDU data (i.e. the combined
        size of _Cmd_ and _Resp_) must not exceed the maximum frame size supported by
        your reader's firmware version. To check the maximum frame size, run
        [Sys.GetBufferSize](system.xml#Sys.GetBufferSize) and refer to the _TotalSize_
        response value.
        
        **For larger amount of data, please use[
        VHL.ExchangeLongAPDU](.#VHL.ExchangeLongAPDU) instead.**
        
        ## No error correction or retry mechanisms
        
        The reader firmware does _not_ perform any error handling operations with
        ISO/IEC 7816-4 inter-industry commands. Errors will be directly reported as
        part of the _Resp_ value without further action, so you have to take care of
        error handling in your application.
        """
        return VHL_ExchangeAPDU(self)
    @property
    def VHL_Setup(self) -> VHL_Setup:
        """
        This command creates a VHL file dynamically and transfers it to the reader's
        RAM. The VHL file specifies the card-specific memory structure required to
        call [VHL.Read](.#VHL.Read) or [VHL.Write](.#VHL.Write). You need to run
        _VHL.Setup_ if you don't want to configure the readers with a static VHL file
        ( [ learn more](https://docs.baltech.de/developers/map-vhl-without-
        config.html)).
        
        **To run[ VHL.Format](.#VHL.Format) , you cannot use a dynamic VHL file. In
        this case, you have to follow the[ standard VHL
        implementation](https://docs.baltech.de/developers/map-vhl.html) with a static
        VHL file.**
        
        ## What to specify
        
        To describe the memory structure, provide a list of parameters depending on
        the card type (see optional fields in the _Parameters_ table below). If you
        omit a parameter, the reader will use the default value. To fill in the
        parameter values, please refer to the card specification. For LEGIC or MIFARE
        cards, you can also [analyze the card
        structure](https://docs.baltech.de/project-setup/analyze-card-structure.html)
        using BALTECH ID-engine Explorer.
        
        ## Mixing dynamic and static VHL files
        
        In principle, it is possible to mix dynamic VHL files and static VHL files (as
        part of the reader configuration for the [ VHL &
        Autoread](https://docs.baltech.de/developers/map-vhl-autoread.html)). However,
        please note that the dynamic VHL file is lost as soon as you run
        [VHL.Read](.#VHL.Read) or [VHL.Write](.#VHL.Write) with a static VHL file.
        Thus, if you later want to run _VHL.Read_ or _VHL.Write_ with the dynamic VHL
        file again, you first need to rerun _VHL.Setup_ to recreate the dynamic VHL
        file.
        """
        return VHL_Setup(self)
    @property
    def VHL_SetupMifare(self) -> VHL_SetupMifare:
        """
        This commands prepares the reader to access Mifare cards with the given Mifare
        key settings. It can be called before using [VHL.Read](.#VHL.Read) and
        [VHL.Write](.#VHL.Write) with Mifare cards without configuring the reader with
        a VHL-file, i.e. when the _ID_ parameter of [VHL.Read](.#VHL.Read) or
        [VHL.Write](.#VHL.Write) is set to 0xFF.
        
        All data blocks of the card starting from sector 1 will be included in the ad
        hoc VHL-file. This only makes sense if all blocks can be accessed using the
        same key. If this assumption is too simplistic for your application, please
        use a normal VHL-file to set up the reader.
        
        **After calling[ VHL.Select](.#VHL.Select) ,[ VHL.Read](.#VHL.Read) or[
        VHL.Write](.#VHL.Write) with an _ID_ parameter other than 0xFF, or after a
        reboot, the settings made by this command are lost.**
        
        **For new applications, the command[ VHL.Setup](.#VHL.Setup) should be used
        instead.**
        """
        return VHL_SetupMifare(self)
    @property
    def VHL_SetupLegic(self) -> VHL_SetupLegic:
        """
        This commands prepares the reader to access LEGIC cards with the given
        settings. It can be called before using [VHL.Read](.#VHL.Read) and
        [VHL.Write](.#VHL.Write) with LEGIC cards without configuring the reader with
        a VHL-file, i.e. when the _ID_ parameter of [VHL.Read](.#VHL.Read) or
        [VHL.Write](.#VHL.Write) is set to 0xFF.
        
        A distinct segment of the LEGIC card to access may be specified, either
        according to its fixed segment ID (through the _SegmentID_ parameter) or
        according to its stamp (through the _Stamp_ parameter).
        
        This command works with a fixed address mapping for the application data: VHL
        address 0 corresponds to Protocol Header address 25, the first data byte after
        the longest possible LEGIC Prime stamp. If this assumption is too simplistic
        for your application, please use [VHL.Setup](.#VHL.Setup) or a normal VHL-file
        to set up the reader.
        
        **After calling[ VHL.Select](.#VHL.Select) ,[ VHL.Read](.#VHL.Read) or[
        VHL.Write](.#VHL.Write) with an _ID_ parameter other than 0xFF, or after a
        reboot, the settings made by this command are lost.**
        
        **For new applications, the command[ VHL.Setup](.#VHL.Setup) should be used
        instead.**
        """
        return VHL_SetupLegic(self)
    @property
    def VHL_SetupISO15(self) -> VHL_SetupISO15:
        """
        This commands prepares the reader to access ISO15693 cards with the given
        settings. It can be called before using [VHL.Read](.#VHL.Read) and
        [VHL.Write](.#VHL.Write) with ISO15693 cards without configuring the reader
        with a VHL-file, i.e. when the _ID_ parameter of [VHL.Read](.#VHL.Read) or
        [VHL.Write](.#VHL.Write) is set to 0xFF.
        
        **After calling[ VHL.Select](.#VHL.Select) ,[ VHL.Read](.#VHL.Read) or[
        VHL.Write](.#VHL.Write) with an _ID_ parameter other than 0xFF, or after a
        reboot, the settings made by this command are lost.**
        
        **Firmware versions 1100 2.07.00 and above also support 16-bit length values
        for the FirstBlock and BlockCount parameters. This is not explicitly
        documented.**
        
        **For new applications, the command[ VHL.Setup](.#VHL.Setup) should be used
        instead.**
        """
        return VHL_SetupISO15(self)
    @property
    def VHL_CheckReconfigErr(self) -> VHL_CheckReconfigErr:
        """
        This command returns the status of the last reconfiguration with a ConfigCard
        using the [VHL.Select](.#VHL.Select) command.
        
        **The _Failed_ status flag is cleared with the next reader reboot.**
        """
        return VHL_CheckReconfigErr(self)
    @property
    def VHL_ExchangeLongAPDU(self) -> VHL_ExchangeLongAPDU:
        """
        This command sends basic Inter-Industry commands to the currently selected
        card in accordance with the [ISO/IEC 7816-4
        standard](http://www.iso.org/iso/catalogue_detail.htm?csnumber=54550). This
        command has the same functionality as [VHL.ExchangeAPDU](.#VHL.ExchangeAPDU),
        but it allows the application to send commands and receive responses larger
        than the reader's internal protocol buffers by splitting the command. See the
        [Sys.GetBufferSize](system.xml#Sys.GetBufferSize) command documentation for
        more details about the reader's internal buffers.
        
        When splitting a command into multiple blocks, this command has to be repeated
        to transfer the APDU as _Cmd_ parameter block by block. As long as the
        _ContinueCmd_ parameter is set to _true_ , the reader will wait for further
        output before transmitting the APDU. The last block of the APDU can be sent by
        setting _ContinueCmd_ to _false_. The reader will only start transferring the
        response once the last block of the APDU command has been sent. If the
        response is bigger than one communication frame, it is split in the same
        manner as the command with the _ContinueResp_ flag set to _true_ as long as
        the response has not been completely received. The command is completely
        exchanged when the _ContinueResp_ flag is set to _false_.
        
        A command transfer can be broken if the reader returns an error status code or
        by starting a new VHL.ExchangeLongAPDU sequence. When starting a new APDU the
        _Reset_ parameter of the first VHL.ExchangeLongAPDU call always has to be set
        to _true_ (it does not matter if the command breaks a preceding
        VHL.ExchangeLongAPDU or not).
        
        The splitting of a command into blocks is determined by the size of the
        reader's sending and receiving buffers. The size of these buffers can be
        obtained by the [Sys.GetBufferSize](system.xml#Sys.GetBufferSize) command. A
        frame must not exceed _MaxSendSize_ \- 4 or _TotalSize_ \- 8.
        
        **The sum of the amount of data transmitted and received through _Cmd_ and
        _Resp_ has to be smaller than or equal to _TotalSize_ .**
        
        The following example shows how a 1000 Byte APDU Command which returns a 500
        Byte response is transferred to a reader having a buffer of 400 Bytes (i.e.
        for which [Sys.GetBufferSize](system.xml#Sys.GetBufferSize) returns a 400 Byte
        _MaxSendSize_ and a 400 Byte _TotalSize_ ):
        
          1. ExchangeLongAPDU(Reset=True, ContinueCmd=True, Cmd=bytes 0..391) >= ContinueResp=True, Resp=empty 
          2. ExchangeLongAPDU(Reset=False, ContinueCmd=True, Cmd=bytes 392..783) >= ContinueResp=True, Resp=empty 
          3. ExchangeLongAPDU(Reset=False, ContinueCmd=False, Cmd=bytes 784..999) >= ContinueResp=True, Resp=0..175 
          4. ExchangeLongAPDU(Reset=False, ContinueCmd=False, Cmd=empty) >= ContinueResp=False, Resp=176..499
        """
        return VHL_ExchangeLongAPDU(self)
    @property
    def VHL_GetFileInfo(self) -> VHL_GetFileInfo:
        """
        This command returns the available size of the VHL-file whose ID is specified
        by the _ID_ parameter. Two values are returned: the length of the VHL-file
        (_Len_) and the size of a single block (_BlockSize_).
        
        **The size of the returned value _Len_ indicates the maximum number of bytes
        which can be read/written with the[ VHL.Read](.#VHL.Read) or[
        VHL.Write](.#VHL.Write) commands. Attempting to read or write a larger amount
        of Bytes with[ VHL.Read](.#VHL.Read) or[ VHL.Write](.#VHL.Write) will generate
        an error status code ([ VHL.ErrRead](.#VHL.ErrRead) or[
        VHL.ErrWrite](.#VHL.ErrWrite) ).**
        
        If the card system organizes its memory in blocks, _BlockSize_ returns the
        size of a single block. If the memory is not organized in blocks, 1 will be
        returned. 0 will be returned if the block sizes are not unique (currently,
        there is no such card system in existence).
        
        **This command can only be executed if a card is selected, e.g. with a
        previous call of[ VHL.Select](.#VHL.Select) .**
        
        **The returned VHL-file size corresponds to the reader's configuration values.
        It does not necessarily guarantee that a file of the returned sized can be
        read on the card. In some cases, the actual size of the card may be smaller
        than the returned VHL-file size.**
        """
        return VHL_GetFileInfo(self)
    @property
    def VHL_GetATR(self) -> VHL_GetATR:
        """
        This command returns the Answer to Reset (ATR) of the currently selected card
        as defined in the [PC/SC specification, version
        2](http://pcscworkgroup.com/Download/Specifications/pcsc3_v2.01.09.pdf). If
        [VHL.Select](.#VHL.Select) hasn't been executed successfully before, the
        [VHL.ErrCardNotSelected](.#VHL.ErrCardNotSelected) status code will be
        returned. If the last selected card is no longer available in the antenna
        field, or a read/write operation failed previous to this command, the returned
        ATR is undefined.
        """
        return VHL_GetATR(self)
    @property
    def VHL_Format(self) -> VHL_Format:
        """
        This command formats a blank card based on a VHL file. In this file, you
        specify the card-specific memory structure.
        
        **_VHL.Format_ only works with the[ standard VHL
        implementation](https://docs.baltech.de/developers/map-vhl.html) using a
        static VHL file. You cannot use a dynamic VHL file created with[
        VHL.Setup](.#VHL.Setup) .**
        """
        return VHL_Format(self)
    @property
    def VHL_ResolveFilename(self) -> VHL_ResolveFilename:
        """
        This command returns the ID of a VHL file based on its filename. To to do, the
        command searches for a file whose configuration value
        [VhlCfg.File.Filename](../cfg/vhl.xml#VhlCfg.File.Filename) matches the passed
        _Filename_ exactly.
        
        Use this ID to reference the VHL file in the following commands:
        
          * [VHL.Read](.#VHL.Read)
          * [VHL.Write](.#VHL.Write)
          * [VHL.Format](.#VHL.Format)
          * [VHL.GetFileInfo](.#VHL.GetFileInfo)
        
        **We strongly recommend you don't hardcode file IDs, but always resolve them
        via this command. Otherwise, your application won't work anymore if e.g. a
        project manager later merges VHL files into a different configuration using
        BALTECH ConfigEditor. This process may result in a new ID, but not in a new
        name.**
        """
        return VHL_ResolveFilename(self)
    @property
    def VHL_GetCardType(self) -> VHL_GetCardType:
        """
        This command returns the card type of the currently selected card.
        
        If no card is selected or the last selected card is no longer available in the
        antenna field, the reader will return
        [VHL.ErrCardNotSelected](.#VHL.ErrCardNotSelected).
        """
        return VHL_GetCardType(self)
    @property
    def DHWCtrl_PortConfig(self) -> DHWCtrl_PortConfig:
        """
        Configures a port.
        """
        return DHWCtrl_PortConfig(self)
    @property
    def DHWCtrl_PortGet(self) -> DHWCtrl_PortGet:
        """
        Reads the current input of a port.
        """
        return DHWCtrl_PortGet(self)
    @property
    def DHWCtrl_PortSet(self) -> DHWCtrl_PortSet:
        """
        Sets the state of a port.
        """
        return DHWCtrl_PortSet(self)
    @property
    def DHWCtrl_PortWait(self) -> DHWCtrl_PortWait:
        """
        Waits until a port has reached the specified level, or until timeout.
        """
        return DHWCtrl_PortWait(self)
    @property
    def DHWCtrl_GetResetCause(self) -> DHWCtrl_GetResetCause:
        """
        Returns the cause of the microcontroller's last reset.
        """
        return DHWCtrl_GetResetCause(self)
    @property
    def DHWCtrl_APortMeasure(self) -> DHWCtrl_APortMeasure:
        """
        The selected ADC Clock is MCU Clock / 128 (i.e. 13.56 Mhz / 128)
        
        After 13 ADC Clock Ticks the first sample will measured. 13 ADC Clock Ticks
        are needed for one sample:
        
        (1 / 13.56 Mhz) * 128 * 13 = 0.123 ms
        
        So we have each 0.123ms one sample. As reference voltage the AVR internal
        2.56V is used, the results are 10 bit values, so to get the voltage in Volt
        use the following formula:
        
        Vin = float(result) / 1024 * 2.56V = float(result) / 400V
        """
        return DHWCtrl_APortMeasure(self)
    @property
    def DHWCtrl_SRAMTest(self) -> DHWCtrl_SRAMTest:
        """
        Tests the external SRAM.
        """
        return DHWCtrl_SRAMTest(self)
    @property
    def DHWCtrl_SetBaudrate(self) -> DHWCtrl_SetBaudrate:
        """
        Changes the baudrate. This command should not be called over BRP.
        """
        return DHWCtrl_SetBaudrate(self)
    @property
    def DHWCtrl_MirrorData(self) -> DHWCtrl_MirrorData:
        """
        Sends the exact same data back.
        """
        return DHWCtrl_MirrorData(self)
    @property
    def DHWCtrl_DispEnable(self) -> DHWCtrl_DispEnable:
        """
        Enables the Display.
        """
        return DHWCtrl_DispEnable(self)
    @property
    def DHWCtrl_DispBacklight(self) -> DHWCtrl_DispBacklight:
        """
        Enables the Baltech reader display's backlight.
        """
        return DHWCtrl_DispBacklight(self)
    @property
    def DHWCtrl_DispColor(self) -> DHWCtrl_DispColor:
        """
        Set the drawing color
        """
        return DHWCtrl_DispColor(self)
    @property
    def DHWCtrl_DispContrast(self) -> DHWCtrl_DispContrast:
        """
        Changes the display contrast.
        """
        return DHWCtrl_DispContrast(self)
    @property
    def DHWCtrl_DispBox(self) -> DHWCtrl_DispBox:
        """
        Draws a filled box.
        """
        return DHWCtrl_DispBox(self)
    @property
    def DHWCtrl_Ser2Ctrl(self) -> DHWCtrl_Ser2Ctrl:
        """
        Enable/Disable and setup the reader's 2nd RS-232/UART interface.
        """
        return DHWCtrl_Ser2Ctrl(self)
    @property
    def DHWCtrl_Ser2WriteRead(self) -> DHWCtrl_Ser2WriteRead:
        """
        Write/Read data to/from the reader's 2nd RS-232/UART interface.
        """
        return DHWCtrl_Ser2WriteRead(self)
    @property
    def DHWCtrl_Ser2Flush(self) -> DHWCtrl_Ser2Flush:
        """
        Wait until output to 2nd RS-232/UART interface is sent out.
        """
        return DHWCtrl_Ser2Flush(self)
    @property
    def DHWCtrl_Delay1ms(self) -> DHWCtrl_Delay1ms:
        """
        Sleeps for some milliseconds.
        """
        return DHWCtrl_Delay1ms(self)
    @property
    def DHWCtrl_Delay10us(self) -> DHWCtrl_Delay10us:
        """
        Sleeps for some microseconds.
        """
        return DHWCtrl_Delay10us(self)
    @property
    def DHWCtrl_PowermgrSuspend(self) -> DHWCtrl_PowermgrSuspend:
        """
        Takes the board into suspend mode, i.e. energy saving mode.
        """
        return DHWCtrl_PowermgrSuspend(self)
    @property
    def DHWCtrl_ScanMatrix(self) -> DHWCtrl_ScanMatrix:
        """
        Writes a bitmask to the 573, which is used for keyboard scanning.
        """
        return DHWCtrl_ScanMatrix(self)
    @property
    def DHWCtrl_GetReaderChipType(self) -> DHWCtrl_GetReaderChipType:
        """
        Returns the RC reader chip type.
        """
        return DHWCtrl_GetReaderChipType(self)
    @property
    def DHWCtrl_SelectAntenna(self) -> DHWCtrl_SelectAntenna:
        """
        Switch external antenna.
        """
        return DHWCtrl_SelectAntenna(self)
    @property
    def DHWCtrl_GetSamType(self) -> DHWCtrl_GetSamType:
        """
        Returns the RC reader chip type
        """
        return DHWCtrl_GetSamType(self)
    @property
    def DHWCtrl_HfAcquire(self) -> DHWCtrl_HfAcquire:
        """
        Acquire specific HF Subsystem.
        """
        return DHWCtrl_HfAcquire(self)
    @property
    def DHWCtrl_EepromWrite(self) -> DHWCtrl_EepromWrite:
        """
        Writes data to an arbitrary address in the EEPROM.
        """
        return DHWCtrl_EepromWrite(self)
    @property
    def DHWCtrl_DataflashGetSize(self) -> DHWCtrl_DataflashGetSize:
        """
        Retrieves the flash size.
        """
        return DHWCtrl_DataflashGetSize(self)
    @property
    def DHWCtrl_DataflashErasePages(self) -> DHWCtrl_DataflashErasePages:
        """
        Erase a group of pages.
        """
        return DHWCtrl_DataflashErasePages(self)
    @property
    def DHWCtrl_DataflashRead(self) -> DHWCtrl_DataflashRead:
        """
        Read data within a certain page.
        """
        return DHWCtrl_DataflashRead(self)
    @property
    def DHWCtrl_DataflashWrite(self) -> DHWCtrl_DataflashWrite:
        """
        Write data to a certain page.
        """
        return DHWCtrl_DataflashWrite(self)
    @property
    def DHWCtrl_EepromRead(self) -> DHWCtrl_EepromRead:
        """
        Reads data from the EEPROM.
        """
        return DHWCtrl_EepromRead(self)
    @property
    def DHWCtrl_SecurityAndConfigReset(self) -> DHWCtrl_SecurityAndConfigReset:
        """
        Reset configuration incl. "Encryption and Authorization" settings.
        """
        return DHWCtrl_SecurityAndConfigReset(self)
    @property
    def DHWCtrl_PulseGenerate(self) -> DHWCtrl_PulseGenerate:
        """
        Generates a pulse of specified frequency on a certain pin.
        """
        return DHWCtrl_PulseGenerate(self)
    @property
    def DHWCtrl_InitSer2(self) -> DHWCtrl_InitSer2:
        """
        Initializes the serial2 module.
        """
        return DHWCtrl_InitSer2(self)
    @property
    def DHWCtrl_InitRtc(self) -> DHWCtrl_InitRtc:
        """
        Initializes the rtc module.
        """
        return DHWCtrl_InitRtc(self)
    @property
    def DHWCtrl_InitLcdDrv(self) -> DHWCtrl_InitLcdDrv:
        """
        Initializes the display module.
        """
        return DHWCtrl_InitLcdDrv(self)
    @property
    def DHWCtrl_InitRc(self) -> DHWCtrl_InitRc:
        """
        Initializes the rc module.
        """
        return DHWCtrl_InitRc(self)
    @property
    def DHWCtrl_InitMf(self) -> DHWCtrl_InitMf:
        """
        Initializes the Mifare module.
        """
        return DHWCtrl_InitMf(self)
    @property
    def DHWCtrl_InitIso14A(self) -> DHWCtrl_InitIso14A:
        """
        Initializes the ISO14443A module.
        """
        return DHWCtrl_InitIso14A(self)
    @property
    def DHWCtrl_InitIso14B(self) -> DHWCtrl_InitIso14B:
        """
        Initializes the ISO14443B module.
        """
        return DHWCtrl_InitIso14B(self)
    @property
    def DHWCtrl_InitIso15(self) -> DHWCtrl_InitIso15:
        """
        Initializes the ISO15693 module.
        """
        return DHWCtrl_InitIso15(self)
    @property
    def DHWCtrl_InitLg(self) -> DHWCtrl_InitLg:
        """
        Initializes the Legic module.
        """
        return DHWCtrl_InitLg(self)
    @property
    def DHWCtrl_InitLga(self) -> DHWCtrl_InitLga:
        """
        Initializes the Legic Advant module.
        """
        return DHWCtrl_InitLga(self)
    @property
    def DHWCtrl_InitDf(self) -> DHWCtrl_InitDf:
        """
        Initializes the dataflash module.
        """
        return DHWCtrl_InitDf(self)
    @property
    def DHWCtrl_InitRc125(self) -> DHWCtrl_InitRc125:
        """
        Initializes the RC125 module.
        """
        return DHWCtrl_InitRc125(self)
    @property
    def DHWCtrl_InitCc(self) -> DHWCtrl_InitCc:
        """
        Initializes the TDA8007 or CCUART module.
        """
        return DHWCtrl_InitCc(self)
    @property
    def DHWCtrl_InitUsbHost(self) -> DHWCtrl_InitUsbHost:
        """
        Initializes the USB-Host module.
        """
        return DHWCtrl_InitUsbHost(self)
    @property
    def DHWCtrl_InitNic(self) -> DHWCtrl_InitNic:
        """
        Initializes the Network Interface (NIC) module.
        """
        return DHWCtrl_InitNic(self)
    @property
    def DHWCtrl_BohEnable(self) -> DHWCtrl_BohEnable:
        """
        Enables the BRP over HID interface.
        """
        return DHWCtrl_BohEnable(self)
    @property
    def DHWCtrl_NicEnable(self) -> DHWCtrl_NicEnable:
        """
        Enables the Network Interface.
        """
        return DHWCtrl_NicEnable(self)
    @property
    def DHWCtrl_NicGetChipType(self) -> DHWCtrl_NicGetChipType:
        """
        Returns the chip type of the Network Interface.
        """
        return DHWCtrl_NicGetChipType(self)
    @property
    def DHWCtrl_NicGetLinkStatus(self) -> DHWCtrl_NicGetLinkStatus:
        """
        Retrieve the Link status of the Network Interface.
        """
        return DHWCtrl_NicGetLinkStatus(self)
    @property
    def DHWCtrl_NicSend(self) -> DHWCtrl_NicSend:
        """
        Sends a frame via the Network Interface.
        """
        return DHWCtrl_NicSend(self)
    @property
    def DHWCtrl_NicReceive(self) -> DHWCtrl_NicReceive:
        """
        Receives a frame from the Network Interface.
        """
        return DHWCtrl_NicReceive(self)
    @property
    def DHWCtrl_NicSetMAC(self) -> DHWCtrl_NicSetMAC:
        """
        Set the MAC address of the Network Interface.
        """
        return DHWCtrl_NicSetMAC(self)
    @property
    def DHWCtrl_ApspiSetSpeed(self) -> DHWCtrl_ApspiSetSpeed:
        """
        Set the speed of SPI programming mode.
        """
        return DHWCtrl_ApspiSetSpeed(self)
    @property
    def DHWCtrl_ApspiEnable(self) -> DHWCtrl_ApspiEnable:
        """
        Enables/disables the SPI programming mode of a connected slave AVR.
        """
        return DHWCtrl_ApspiEnable(self)
    @property
    def DHWCtrl_ApspiSingleSend(self) -> DHWCtrl_ApspiSingleSend:
        """
        Send a single SPI programming instruction.
        """
        return DHWCtrl_ApspiSingleSend(self)
    @property
    def DHWCtrl_ApspiSingleRecv(self) -> DHWCtrl_ApspiSingleRecv:
        """
        Send a single SPI programming instruction and receive one data byte.
        """
        return DHWCtrl_ApspiSingleRecv(self)
    @property
    def DHWCtrl_ApspiAlternateSend(self) -> DHWCtrl_ApspiAlternateSend:
        """
        Send alternately SPI programming instructions. First CmdCodeA with address adr
        and the first byte in the data buffer, then CmdCodeB with the same address and
        the second byte in the buffer is sent. After that the address will be
        incremented. This is repeated as long as data bytes are in the buffer.
        """
        return DHWCtrl_ApspiAlternateSend(self)
    @property
    def DHWCtrl_ApspiAlternateRecv(self) -> DHWCtrl_ApspiAlternateRecv:
        """
        Send alternately SPI programming instructions and receive data bytes. Works
        similar to ApspiAlternateSend.
        """
        return DHWCtrl_ApspiAlternateRecv(self)
    @property
    def DHWCtrl_PdiEnable(self) -> DHWCtrl_PdiEnable:
        """
        Enables/disables the PDI programming mode of a connected target AVR.
        """
        return DHWCtrl_PdiEnable(self)
    @property
    def DHWCtrl_PdiEraseDevice(self) -> DHWCtrl_PdiEraseDevice:
        """
        Erases the target chip device.
        """
        return DHWCtrl_PdiEraseDevice(self)
    @property
    def DHWCtrl_PdiReadFlash(self) -> DHWCtrl_PdiReadFlash:
        """
        Read flash memory from target device.
        """
        return DHWCtrl_PdiReadFlash(self)
    @property
    def DHWCtrl_PdiEraseFlashPage(self) -> DHWCtrl_PdiEraseFlashPage:
        """
        Erase flash page.
        """
        return DHWCtrl_PdiEraseFlashPage(self)
    @property
    def DHWCtrl_PdiWriteFlashPage(self) -> DHWCtrl_PdiWriteFlashPage:
        """
        Write to internal flash page buffer.
        """
        return DHWCtrl_PdiWriteFlashPage(self)
    @property
    def DHWCtrl_PdiProgramFlashPage(self) -> DHWCtrl_PdiProgramFlashPage:
        """
        Program flash page. Page must be written with PdiWriteFlashPage before.
        """
        return DHWCtrl_PdiProgramFlashPage(self)
    @property
    def DHWCtrl_PdiReadEeprom(self) -> DHWCtrl_PdiReadEeprom:
        """
        Read eeprom memory from target device.
        """
        return DHWCtrl_PdiReadEeprom(self)
    @property
    def DHWCtrl_PdiProgramEepromPage(self) -> DHWCtrl_PdiProgramEepromPage:
        """
        Write an eeprom page to target device.
        """
        return DHWCtrl_PdiProgramEepromPage(self)
    @property
    def DHWCtrl_PdiReadFuses(self) -> DHWCtrl_PdiReadFuses:
        """
        Read fuse memory from target device.
        """
        return DHWCtrl_PdiReadFuses(self)
    @property
    def DHWCtrl_PdiWriteFuse(self) -> DHWCtrl_PdiWriteFuse:
        """
        Write a fuse byte to target device.
        """
        return DHWCtrl_PdiWriteFuse(self)
    @property
    def DHWCtrl_FlashGetPageSize(self) -> DHWCtrl_FlashGetPageSize:
        """
        Retrieves the page size of the program flash.
        """
        return DHWCtrl_FlashGetPageSize(self)
    @property
    def DHWCtrl_FlashErasePage(self) -> DHWCtrl_FlashErasePage:
        """
        Erases one or several consecutive program flash pages.
        """
        return DHWCtrl_FlashErasePage(self)
    @property
    def DHWCtrl_FlashRead(self) -> DHWCtrl_FlashRead:
        """
        Read data from program flash.
        """
        return DHWCtrl_FlashRead(self)
    @property
    def DHWCtrl_FlashWritePage(self) -> DHWCtrl_FlashWritePage:
        """
        Write to a temporary page buffer. Can be executed several times until the page
        buffer is filled.
        """
        return DHWCtrl_FlashWritePage(self)
    @property
    def DHWCtrl_FlashProgramPage(self) -> DHWCtrl_FlashProgramPage:
        """
        Program a page to program flash. The data has to be written to the temporary
        page buffer with FlashWritePage before.
        """
        return DHWCtrl_FlashProgramPage(self)
    @property
    def DHWCtrl_RegisterRead(self) -> DHWCtrl_RegisterRead:
        """
        Read processor register.
        """
        return DHWCtrl_RegisterRead(self)
    @property
    def DHWCtrl_RegisterWrite(self) -> DHWCtrl_RegisterWrite:
        """
        Write processor register.
        """
        return DHWCtrl_RegisterWrite(self)
    @property
    def DHWCtrl_AesWrapKey(self) -> DHWCtrl_AesWrapKey:
        """
        Wraps an AES key for secure storage
        """
        return DHWCtrl_AesWrapKey(self)
    @property
    def DHWCtrl_AesEncrypt(self) -> DHWCtrl_AesEncrypt:
        """
        Encrypts a block
        """
        return DHWCtrl_AesEncrypt(self)
    @property
    def DHWCtrl_AesDecrypt(self) -> DHWCtrl_AesDecrypt:
        """
        Decrypts a block
        """
        return DHWCtrl_AesDecrypt(self)
    @property
    def DHWCtrl_GetPlatformId2(self) -> DHWCtrl_GetPlatformId2:
        """
        This command retrieves the PlatformId2. A list of all supported
        HardwareComponents is returned.
        """
        return DHWCtrl_GetPlatformId2(self)
    @property
    def DHWCtrl_GetProdLoader(self) -> DHWCtrl_GetProdLoader:
        """
        Returns the baudrate Byte of the production-loader.
        """
        return DHWCtrl_GetProdLoader(self)
    @property
    def DHWCtrl_StartProdLoader(self) -> DHWCtrl_StartProdLoader:
        """
        Starts the production-loader.
        """
        return DHWCtrl_StartProdLoader(self)
    @property
    def DHWCtrl_Run(self) -> DHWCtrl_Run:
        """
        Executes a list of commands. The commands are stored sequentially in the
        buffer. Every command has as a header the command code and the length of the
        following parameters. Both are given in bytes. It is possible to execute every
        DHWCtrl command through this interface.
        """
        return DHWCtrl_Run(self)
    @property
    def DHWCtrl_GetStartupRun(self) -> DHWCtrl_GetStartupRun:
        """
        Returns the result of the execution of DHWCtrl-commands at the startup.
        """
        return DHWCtrl_GetStartupRun(self)
    @property
    def DHWCtrl_InitBgm(self) -> DHWCtrl_InitBgm:
        """
        Initializes the Bluetooth BGM12X chip.
        """
        return DHWCtrl_InitBgm(self)
    @property
    def DHWCtrl_BgmExec(self) -> DHWCtrl_BgmExec:
        """
        Execute a Bgm12X API command.
        """
        return DHWCtrl_BgmExec(self)
    @property
    def DHWCtrl_Sm4x00BootloaderStart(self) -> DHWCtrl_Sm4x00BootloaderStart:
        """
        Start SM4x00 Bootloader.
        """
        return DHWCtrl_Sm4x00BootloaderStart(self)
    @property
    def DHWCtrl_Sm4x00EraseFlash(self) -> DHWCtrl_Sm4x00EraseFlash:
        """
        Erase SM4x00 Flash. Must be issued directly after
        DHWCtrl.Sm4x00BootloaderStart. Erasing lasts about 20-30 seconds. Use
        DHWCtrl.Sm4x00WaitForFlashErase to find out when it has been finished.
        """
        return DHWCtrl_Sm4x00EraseFlash(self)
    @property
    def DHWCtrl_Sm4x00WaitForFlashErase(self) -> DHWCtrl_Sm4x00WaitForFlashErase:
        """
        Check if flash erasing has been finished.
        """
        return DHWCtrl_Sm4x00WaitForFlashErase(self)
    @property
    def DHWCtrl_Sm4x00ProgramBlock(self) -> DHWCtrl_Sm4x00ProgramBlock:
        """
        Program one 128 byte block of SM4x00 firmware.
        """
        return DHWCtrl_Sm4x00ProgramBlock(self)
    @property
    def DHWCtrl_BgmRead(self) -> DHWCtrl_BgmRead:
        """
        Read from Bgm12X.
        """
        return DHWCtrl_BgmRead(self)
    @property
    def LT_Request(self) -> LT_Request:
        """
        According to the _ReqAll_ flag, either only PICCs in idle state or also PICCs
        in halt state will be switched to ready state. Only PICCs in ready state may
        be selected via the [LT.Select](.#LT.Select) command.
        """
        return LT_Request(self)
    @property
    def LT_Anticoll(self) -> LT_Anticoll:
        """
        This command performs an anticollision sequence.
        """
        return LT_Anticoll(self)
    @property
    def LT_Select(self) -> LT_Select:
        """
        This command selects a PICC with 4-Byte serial number.
        """
        return LT_Select(self)
    @property
    def LT_Halt(self) -> LT_Halt:
        """
        Switch PICC to halt state. The PICC has to be selected before it may be
        switched to halt state.
        """
        return LT_Halt(self)
    @property
    def LT_ReadBlock(self) -> LT_ReadBlock:
        """
        Reads a block (32 Byte) from the transponder.
        """
        return LT_ReadBlock(self)
    @property
    def LT_ReadMultipleBlocks(self) -> LT_ReadMultipleBlocks:
        """
        Reads several blocks (32 Byte) from the transponder.
        """
        return LT_ReadMultipleBlocks(self)
    @property
    def LT_WriteBlock(self) -> LT_WriteBlock:
        """
        Writes a block (32 Byte) to the transponder.
        """
        return LT_WriteBlock(self)
    @property
    def LT_ReadWord(self) -> LT_ReadWord:
        """
        Reads a word (2 Byte) from the transponder.
        """
        return LT_ReadWord(self)
    @property
    def LT_WriteWord(self) -> LT_WriteWord:
        """
        Writes a word to the transponder.
        """
        return LT_WriteWord(self)
    @property
    def LT_WriteFile(self) -> LT_WriteFile:
        """
        Writes a test file to the reader.
        """
        return LT_WriteFile(self)
    @property
    def LT_Test(self) -> LT_Test:
        """
        Writes a test file to the reader.
        """
        return LT_Test(self)
    @property
    def LT_FastWriteBlock(self) -> LT_FastWriteBlock:
        """
        Writes a block (32 Byte) to the transponder, write time is reduced (LT5).
        """
        return LT_FastWriteBlock(self)
    @property
    def LT_FastWriteWord(self) -> LT_FastWriteWord:
        """
        Writes a word to the transponder, write time is reduced (LT5).
        """
        return LT_FastWriteWord(self)
    @property
    def LT_HighSpeedWriteBlock(self) -> LT_HighSpeedWriteBlock:
        """
        Writes a block (32 Byte) to the transponder, write time is reduced (LT5),
        block 1 has to be unprotected.
        """
        return LT_HighSpeedWriteBlock(self)
    @property
    def LT_GetBootStatus(self) -> LT_GetBootStatus:
        """
        Retrieves the boot status of the reader, which describes the state of the
        readers hardware. If a defect is detected during the self-test of the reader,
        a bit will be set.
        """
        return LT_GetBootStatus(self)
    @property
    def LT_ContinousReadBlocks(self) -> LT_ContinousReadBlocks:
        """
        Reads several blocks (32 Byte) from the transponder. Faster read because
        transponder protocol has been optimized (LT5).
        """
        return LT_ContinousReadBlocks(self)
    @property
    def LT_SetReturnLink(self) -> LT_SetReturnLink:
        """
        Sets the transponder baud rate after selection.
        """
        return LT_SetReturnLink(self)
    @property
    def LT_HFReset(self) -> LT_HFReset:
        """
        This command controls the antenna of the reader. It can be powered off and on
        permanently or for a limited time.
        """
        return LT_HFReset(self)
    @property
    def LT_Reset(self) -> LT_Reset:
        """
        This command reboots the reader. After this command you have to wait some time
        until the reader reacts to requests.
        """
        return LT_Reset(self)
    @property
    def LT_GetInfo(self) -> LT_GetInfo:
        """
        Retrieves the firmware string, which provides information regarding the
        firmware release of the reader and the reader's serial number.
        """
        return LT_GetInfo(self)
    @property
    def LT_TransparentCmd(self) -> LT_TransparentCmd:
        return LT_TransparentCmd(self)
    @property
    def LT_ReadBlockExtended(self) -> LT_ReadBlockExtended:
        """
        Reads a block (32 Byte) from the transponder using a 16-bit block address.
        """
        return LT_ReadBlockExtended(self)
    @property
    def LT_WriteBlockExtended(self) -> LT_WriteBlockExtended:
        """
        Writes a block (32 Byte) to the transponder using a 16-bit block address.
        """
        return LT_WriteBlockExtended(self)
    @property
    def LT_ReadWordExtended(self) -> LT_ReadWordExtended:
        """
        Reads a word (2 Byte) from the transponder using a 16-bit address.
        """
        return LT_ReadWordExtended(self)
    @property
    def LT_WriteWordExtended(self) -> LT_WriteWordExtended:
        """
        Writes a word to the transponder using a 16-bit block address.
        """
        return LT_WriteWordExtended(self)
    @property
    def LT_ReadMultipleBlocksExtended(self) -> LT_ReadMultipleBlocksExtended:
        """
        Reads several blocks (32 Byte) from the transponder.
        """
        return LT_ReadMultipleBlocksExtended(self)
    @property
    def LT_FastWriteWordExtended(self) -> LT_FastWriteWordExtended:
        """
        Writes a word to the transponder using a 16-bit block address + fast mode.
        """
        return LT_FastWriteWordExtended(self)
    @property
    def LT_ContinousReadBlocksExtended(self) -> LT_ContinousReadBlocksExtended:
        """
        Reads several blocks (32 Byte) from the transponder using fast mode.
        """
        return LT_ContinousReadBlocksExtended(self)
    @property
    def LT_HighSpeedWriteBlockExtended(self) -> LT_HighSpeedWriteBlockExtended:
        """
        Writes a block (32 Byte) to the transponder using a 16-bit address, write time
        is reduced (LT6).
        """
        return LT_HighSpeedWriteBlockExtended(self)
class ConfigAccessor(FrameExecutor):
    @property
    def Autoread(self) -> Autoread:
        """
        The Autoread masterkey contains a set of rules that describes how cards have
        to be read. When a card is presented it starts processing Rule0. On failure it
        will go on with the next rule until a rule succeeds reading the card or no
        more rules are available.
        
        To activate the autoread mode at least the
        [Template](.#Autoread.Rule.Template) of Rule0 has to be defined or the
        autoread mode has to be forced to autorun by the
        [AutoreadMode](../cmds/autoread.xml#AR.SetMode) value.
        
        The resulting data is send to the host depending on the [active host
        protocols](base.xml#Device.Run.EnabledProtocols). Each protocol driver may
        convert the data to a protocol specific format before sending it.
        """
        return Autoread(self)
    @property
    def Autoread_Rule(self) -> Autoread_Rule:
        """
        When processing a rule the following steps are checked within this order:
        
          1. the cardtype of the detected card is within [CardTypes](.#Autoread.Rule.CardTypes)
          2. the constant area required by [ConstArea](.#Autoread.Rule.ConstArea) is found on the card 
          3. the [Template](.#Autoread.Rule.Template) can be processed successfully 
          4. the BaltechScript in [CheckScript](.#Autoread.Rule.CheckScriptId) is runs successfully (returns with _DefaultAction_ or is not defined 
          5. the data return by the template is in the whitelist / not in the blacklist (see [Custom/BlackWhiteList](.#Custom.BlackWhiteList)).
        """
        return Autoread_Rule(self)
    @property
    def Autoread_Rule_Template(self) -> Autoread_Rule_Template:
        """
        This template describes which parts of the [VHL
        file](.#Autoread.Rule.VhlFileIndex) (see
        [VarData](dataconverter.xml#Template.VarData)) or the card's serial number
        (see [Serialnr](dataconverter.xml#Template.Serialnr)) to read and how to
        convert them to ASCII format.
        
        **A default value reading the card's serial number was introduced with
        firmware 2.11.00. For all previous versions, this value has to be defined
        explicitly; otherwise no data will be processed by Autoread.**
        """
        return Autoread_Rule_Template(self)
    @property
    def Autoread_Rule_VhlFileIndex(self) -> Autoread_Rule_VhlFileIndex:
        """
        Specifies the index of the VHL file (0-0x3F), that shall be used as source
        data for the [Template](.#Autoread.Rule.Template). Commands like
        [VarData](dataconverter.xml#Template.VarData) are reading this vhlfile.
        
        If this value is omitted implicitly 1 is assumed as default.
        """
        return Autoread_Rule_VhlFileIndex(self)
    @property
    def Autoread_Rule_ConstArea(self) -> Autoread_Rule_ConstArea:
        """
        With this value, an Autoread rule requires fix data at a specific position
        within the VHL file. _Position_ define the position from where the fix data
        area is starting. The rest of this field constant data VHL file has to match.
        """
        return Autoread_Rule_ConstArea(self)
    @property
    def Autoread_Rule_CardTypes(self) -> Autoread_Rule_CardTypes:
        """
        With this value the autoread rule can be enforced to accept only one of the
        cardtypes specified in this list.
        """
        return Autoread_Rule_CardTypes(self)
    @property
    def Autoread_Rule_CheckScriptId(self) -> Autoread_Rule_CheckScriptId:
        """
        **This value is obsolete. It is only supported for legacy configurations.
        Please use[ Autoread.Rule.CheckScript](.#Autoread.Rule.CheckScript) instead.**
        
        When a card matches an autoread rule, this value allows to do additional
        script based checks that can deny the card. If this value is not set, the card
        will always be accepted.
        """
        return Autoread_Rule_CheckScriptId(self)
    @property
    def Autoread_Rule_MsgType(self) -> Autoread_Rule_MsgType:
        """
        This value defines the message type that the command
        [AR.GetMessage](../cmds/autoread.xml#AR.GetMessage) returns. For each message
        type, you can define how to format the message and how to transmit it to the
        host system. To do so, use the _HostMsgFormatTemplate_ value of your protocol.
        You can find in the [Protocols](protocols.xml#Protocols) MasterKey, under the
        Subkey for your protocol.
        """
        return Autoread_Rule_MsgType(self)
    @property
    def Autoread_Rule_WiegandInputBitLen(self) -> Autoread_Rule_WiegandInputBitLen:
        """
        Only needed for readers, that provides a Wiegand Input port and which process
        this wiegand input like a card presentation (i.e. with the Autoread
        functionality). If defined, reader accepts only wiegand frames with this
        bitlen. If 0xFF any bitlen is accepted.
        """
        return Autoread_Rule_WiegandInputBitLen(self)
    @property
    def Autoread_Rule_CardFamilies(self) -> Autoread_Rule_CardFamilies:
        """
        With this value the autoread rule can be enforced to accept only one of the
        card families specified in this bitmask.
        
        If the [prioritization](.#Autoread.Rule.PrioritizationMode) feature is enabled
        this value defines the card families to be handled prioritized. In this
        respect this value corresponds to
        [VhlSettings.PrioritizeCardFamilies](vhl.xml#Project.VhlSettings.PrioritizeCardFamilies).
        Be aware that if the VhlSettings value is set the Autoread rule value is
        ignored!
        """
        return Autoread_Rule_CardFamilies(self)
    @property
    def Autoread_Rule_PrioritizationMode(self) -> Autoread_Rule_PrioritizationMode:
        """
        This value allows enabling a prioritization scheme which is applied when
        multiple cards are presented to the reader simultaneously. The prioritization
        guarantees that the reader always returns the prioritized card families
        first/only.
        
        If prioritization is enabled the card families which shall pe prioritized are
        defined in [Card Families](.#Autoread.Rule.CardFamilies). By default the
        prioritization is applied to any detected card. The configuration value
        [PrioritizationTriggeringCardFamilies](.#Autoread.Rule.PrioritizationTriggeringCardFamilies)
        allows restricting the prioritization to certain card families in order to
        optimize the processing speed.
        """
        return Autoread_Rule_PrioritizationMode(self)
    @property
    def Autoread_Rule_PrioritizationTriggeringCardFamilies(self) -> Autoread_Rule_PrioritizationTriggeringCardFamilies:
        """
        This value defines the card families which trigger the [prioritization
        mechanism](.#Autoread.Rule.PrioritizationMode). Only if the reader detects a
        card which belongs to one of the specified card families, it checks for a
        [prioritized card](.#Autoread.Rule.CardFamilies) which it would return instead
        of the originally detected card.
        
        If this value is not set, the reader applies the [prioritization
        mechanism](.#Autoread.Rule.PrioritizationMode) to every detected card. Because
        the prioritization consumes additional time the processing speed can be
        optimized by defining this value and restricting the prioritization to the
        relevant cards only.
        
        **This value corresponds to[
        VhlSettings.PrioritizeCardFamilies](vhl.xml#Project.VhlSettings.PrioritizeCardFamilies)
        . If the VhlSettings value is set it overwrites the Autoread rule value!**
        """
        return Autoread_Rule_PrioritizationTriggeringCardFamilies(self)
    @property
    def Autoread_Rule_OnMatchAction(self) -> Autoread_Rule_OnMatchAction:
        """
        This value allows defining an inverse rule which suppresses the output if the
        rule can be applied successfully (see _DenyCard_). This feature can be used to
        filter out cards with certain properties.
        """
        return Autoread_Rule_OnMatchAction(self)
    @property
    def Autoread_Rule_AllowRandomSerialNumbers(self) -> Autoread_Rule_AllowRandomSerialNumbers:
        """
        This value allows Autoread to be forced to return random card serial numbers.
        
        Random card serial numbers, changing with every card presentation, are useless
        for identification purposes. This is why random serial numbers are ignored by
        rules which process the card serial number by default. This value allows
        changing this behaviour.
        """
        return Autoread_Rule_AllowRandomSerialNumbers(self)
    @property
    def Autoread_Rule_OnMatchEvent(self) -> Autoread_Rule_OnMatchEvent:
        """
        This event is fired when the surrounding rule is matching. If the script that
        is executed on this event contains a _DefaultAction_ , one of the following
        events will be fired subsequently:
        
          * [OnAccepted](autoread.xml#Scripts.Events.OnAccepted)
          * [OnMatchMsg[X]](autoread.xml#Scripts.Events.OnMatchMsg)
          * [OnInvalidCard](autoread.xml#Scripts.Events.OnInvalidCard)
        
        **If the script contains no _DefaultAction_ , the events listed above will be
        omitted.**
        """
        return Autoread_Rule_OnMatchEvent(self)
    @property
    def Autoread_Rule_VhlFileName(self) -> Autoread_Rule_VhlFileName:
        """
        Specifies the name of the VHL file to be used as source data for the
        [template](.#Autoread.Rule.Template). This VHL file is read by commands such
        as [VarData](dataconverter.xml#Template.VarData).
        
        If this value is omitted, [VhlFileIdx](.#Autoread.Rule.Template) is used as
        default.
        """
        return Autoread_Rule_VhlFileName(self)
    @property
    def Autoread_Rule_CheckScript(self) -> Autoread_Rule_CheckScript:
        """
        When a card matches an autoread rule, this value allows to do additional
        script based checks that can deny the card.
        
        The card will always be accepted if this configuration value is not set or if
        the script within this value contains a
        [DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.
        Otherwise, Autoread will assume that this rule has failed and will progress
        with the remaining rules.
        """
        return Autoread_Rule_CheckScript(self)
    @property
    def Autoread_Rule_BlackWhiteListTemplate(self) -> Autoread_Rule_BlackWhiteListTemplate:
        """
        If this template is set, it is used to generate a number that is compared
        against a black-/whitelist instead of the number that is returned by Autoread
        (see [Template](.#Autoread.Rule.Template)).
        """
        return Autoread_Rule_BlackWhiteListTemplate(self)
    @property
    def Autoread_Rule_SendProtocol(self) -> Autoread_Rule_SendProtocol:
        """
        If this value is set, the number returned by Autoread will not be sent to all
        activated protocols, but only to the specified protocol.
        """
        return Autoread_Rule_SendProtocol(self)
    @property
    def Autoread_Rule_TemplateExt1(self) -> Autoread_Rule_TemplateExt1:
        """
        This value can be used as an extension for the
        [Template](.#Autoread.Rule.Template) value, in case the Autoread template to
        use is longer than 128 Bytes. In this case, the previous part of the template
        must end with the [TemplateCommand](dataconverter.xml#Template.ContinueTmpl)
        command.
        """
        return Autoread_Rule_TemplateExt1(self)
    @property
    def Autoread_Rule_TemplateExt2(self) -> Autoread_Rule_TemplateExt2:
        """
        This value can be used as an extension for the
        [Template](.#Autoread.Rule.Template) and
        [TemplateExt1](.#Autoread.Rule.TemplateExt1) values, in case the Autoread
        template to use is longer than 256 Bytes. In this case, the previous part of
        the template must end with the
        [TemplateCommand](dataconverter.xml#Template.ContinueTmpl) command.
        """
        return Autoread_Rule_TemplateExt2(self)
    @property
    def Autoread_Rule_Counter(self) -> Autoread_Rule_Counter:
        """
        This is an internal storage for saving the current counter state that is
        needed when a [CardCounter](dataconverter.xml#Template.CardCounter) command is
        processed and need to retrieve/increment the current value.
        """
        return Autoread_Rule_Counter(self)
    @property
    def Autoread_Rule_OnMatchSendApdu(self) -> Autoread_Rule_OnMatchSendApdu:
        """
        _OnMatchSendApdu_ consists of an APDU. The APDU is sent to the card when the
        rule has been successfully applied and the VHL commands have been executed in
        EnableOnce mode if necessary.
        """
        return Autoread_Rule_OnMatchSendApdu(self)
    @property
    def Scripts(self) -> Scripts:
        """
        The autoread functionality of the reader is highly customizable with the help
        of [BaltechScripts](baltechscript.xml#BaltechScript). These scripts and their
        helper values are stored in this masterkey.
        """
        return Scripts(self)
    @property
    def Scripts_StaticMessages(self) -> Scripts_StaticMessages:
        """
        Contains constant messages that are needed by scripts
        """
        return Scripts_StaticMessages(self)
    @property
    def Scripts_StaticMessages_MatchMsg(self) -> Scripts_StaticMessages_MatchMsg:
        """
        Autoread compares every returned message to one of these constant messages. On
        match the corresponding [OnMatchMsg Event](.#Scripts.Events.OnMatchMsg) will
        be fired.
        """
        return Scripts_StaticMessages_MatchMsg(self)
    @property
    def Scripts_StaticMessages_SendMsg(self) -> Scripts_StaticMessages_SendMsg:
        """
        This constant Messages are for use by _SendMsg_ (see [BaltechScripts
        Commands](baltechscript.xml#BaltechScript) ).
        
        **The maximum allowed size of a message is 30 bytes!**
        """
        return Scripts_StaticMessages_SendMsg(self)
    @property
    def Scripts_Events(self) -> Scripts_Events:
        """
        The Autoread functionality defines a number of events, each of which
        corresponds to a configuration value within this subkey. At each event, you
        can perform a custom action. To do so, you need to load the code for the
        action onto the reader as the respective configuration value.
        
        **Most events have a _default action_ , i.e. the action that the firmware
        performs by default. If you configure a custom action, it will replace the
        default action. To perform the default action _in addition_ to your custom
        action, you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        
        For more details about the events and their default actions, please refer to
        the configuration value descriptions.
        """
        return Scripts_Events(self)
    @property
    def Scripts_Events_OnSetState(self) -> Scripts_Events_OnSetState:
        """
        A state switched from cleared to set. This event can define a custom action.
        The meaning of the state depends on the firmware.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnSetState(self)
    @property
    def Scripts_Events_OnSetInput(self) -> Scripts_Events_OnSetInput:
        """
        The _InputX_ I/O-port changed its state from low to high. This event can
        define a custom action.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnSetInput(self)
    @property
    def Scripts_Events_OnSetTamperAlarm(self) -> Scripts_Events_OnSetTamperAlarm:
        """
        The _TamperAlarm_ I/O-port changed its state from off to on. This event can
        define a custom action.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnSetTamperAlarm(self)
    @property
    def Scripts_Events_OnSetGpio(self) -> Scripts_Events_OnSetGpio:
        """
        The _GpioX_ I/O-port changed its state from low to high. This event can define
        a custom action.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnSetGpio(self)
    @property
    def Scripts_Events_OnClearState(self) -> Scripts_Events_OnClearState:
        """
        A state switched from set to cleared. This event can define a custom action.
        The meaning of the state depends on the firmware.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnClearState(self)
    @property
    def Scripts_Events_OnClearInput(self) -> Scripts_Events_OnClearInput:
        """
        The _InputX_ I/O-port changed its state from high to low. This event can
        define a custom action.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnClearInput(self)
    @property
    def Scripts_Events_OnClearTamperAlarm(self) -> Scripts_Events_OnClearTamperAlarm:
        """
        The _TamperAlarm_ I/O port has changed its state from on to off.  
        The initial state is defined in
        [Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup).
        
        The _default action_ for this event is to send an AlarmOff message to the
        host.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnClearTamperAlarm(self)
    @property
    def Scripts_Events_OnClearGpio(self) -> Scripts_Events_OnClearGpio:
        """
        The _GpioX_ I/O-port changed its state from high to low. This event can define
        a custom action.
        
        **The initial state is defined in[
        Device/Boot/FireInputEventAtPowerup](.#Device.Boot.FireInputEventAtPowerup)**
        """
        return Scripts_Events_OnClearGpio(self)
    @property
    def Scripts_Events_OnKeypressF(self) -> Scripts_Events_OnKeypressF:
        """
        A function key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressF(self)
    @property
    def Scripts_Events_OnKeypressEsc(self) -> Scripts_Events_OnKeypressEsc:
        """
        The Escape key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressEsc(self)
    @property
    def Scripts_Events_OnKeypressClear(self) -> Scripts_Events_OnKeypressClear:
        """
        The C (clear) key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressClear(self)
    @property
    def Scripts_Events_OnKeypressMenu(self) -> Scripts_Events_OnKeypressMenu:
        """
        The menu key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressMenu(self)
    @property
    def Scripts_Events_OnKeypressOk(self) -> Scripts_Events_OnKeypressOk:
        """
        The Ok key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressOk(self)
    @property
    def Scripts_Events_OnKeypressStar(self) -> Scripts_Events_OnKeypressStar:
        """
        The '*' key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressStar(self)
    @property
    def Scripts_Events_OnKeypressSharp(self) -> Scripts_Events_OnKeypressSharp:
        """
        The '#' key on the keyboard (if present) was pressed.
        """
        return Scripts_Events_OnKeypressSharp(self)
    @property
    def Scripts_Events_OnPinEntry(self) -> Scripts_Events_OnPinEntry:
        """
        A PIN code has been entered via the keypad.
        
        The _default action_ for this event is to send a message with the PIN code to
        the host.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnPinEntry(self)
    @property
    def Scripts_Events_OnDetectedCard(self) -> Scripts_Events_OnDetectedCard:
        """
        The Autoread scan (see [Scripts/Events/OnScan](.#Scripts.Events.OnScan)) has
        detected a card that is not a ConfigCard.
        
        The _default action_ for this event is to continue Autoread, i.e. to read the
        card based on the Autoread rules. Depending on the data stored on the card and
        the Autoread rules/blacklist/whitelist/match messages, one of the following
        scripts will be fired:
        
          * [Scripts/Events/OnAccepted](.#Scripts.Events.OnAccepted)
          * [Scripts/Events/OnInvalidCard](.#Scripts.Events.OnInvalidCard)
          * [Scripts/Events/OnBlackWhiteListDenied](.#Scripts.Events.OnBlackWhiteListDenied)
          * [Scripts/Events/OnMatchMsg](.#Scripts.Events.OnMatchMsg)
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnDetectedCard(self)
    @property
    def Scripts_Events_OnMatchMsg(self) -> Scripts_Events_OnMatchMsg:
        """
        A card has been read by the Autoread functionality and the returned message
        matches one of the values stored in
        [Scripts/StaticMessages/MatchMsg](.#Scripts.StaticMessages.MatchMsg).
        
        The _default action_ for this event is to send the message to the host.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnMatchMsg(self)
    @property
    def Scripts_Events_OnAccepted(self) -> Scripts_Events_OnAccepted:
        """
        A card has been read by the Autoread functionality and the returned message
        matches none of the values stored in
        [Scripts/StaticMessages/MatchMsg](.#Scripts.StaticMessages.MatchMsg).
        
        The _default action_ for this event is to send the message to the host.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnAccepted(self)
    @property
    def Scripts_Events_OnInvalidCard(self) -> Scripts_Events_OnInvalidCard:
        """
        The detected card cannot be read by any of the Autoread rules.
        """
        return Scripts_Events_OnInvalidCard(self)
    @property
    def Scripts_Events_OnEnabledProtocol(self) -> Scripts_Events_OnEnabledProtocol:
        """
        If a host protocol is enabled (see
        [Device/Run/EnabldeProtocols](base.xml#Device.Run.EnabledProtocols)) this
        event is fired.
        """
        return Scripts_Events_OnEnabledProtocol(self)
    @property
    def Scripts_Events_OnBlackWhiteListDenied(self) -> Scripts_Events_OnBlackWhiteListDenied:
        """
        A card is denied by the blacklist or whitelist stored in the reader
        configuration (see [Custom/BlackWhiteList subkey](.#Custom.BlackWhiteList)).
        
        The _default action_ for this event is to deny the card.
        
        **If you configure a custom action, it will replace the default action, i.e.
        the card will be accepted and sent to the host ([
        Scripts/Events/OnAccepted](.#Scripts.Events.OnAccepted) will be called). To
        perform the custom action _and_ deny the card, you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnBlackWhiteListDenied(self)
    @property
    def Scripts_Events_OnSetGreenLed(self) -> Scripts_Events_OnSetGreenLed:
        """
        The green LED has been enabled by a custom protocol command.
        
        The _default action_ for this event is to physically enable the green LED.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnSetGreenLed(self)
    @property
    def Scripts_Events_OnSetRedLed(self) -> Scripts_Events_OnSetRedLed:
        """
        The red LED has been enabled by a custom protocol command.
        
        The _default action_ for this event is to physically enable the red LED.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnSetRedLed(self)
    @property
    def Scripts_Events_OnSetBeeper(self) -> Scripts_Events_OnSetBeeper:
        """
        The beeper has been enabled by a custom protocol command.
        
        The _default action_ for this event is to physically enable the beeper.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnSetBeeper(self)
    @property
    def Scripts_Events_OnSetRelay(self) -> Scripts_Events_OnSetRelay:
        """
        The relay has been enabled by a custom protocol command.
        
        The _default action_ for this event is to physically enable the relay.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnSetRelay(self)
    @property
    def Scripts_Events_OnClearGreenLed(self) -> Scripts_Events_OnClearGreenLed:
        """
        The green LED has been disabled by a custom protocol command.
        
        The _default action_ for this event is to physically disable the green LED.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnClearGreenLed(self)
    @property
    def Scripts_Events_OnClearRedLed(self) -> Scripts_Events_OnClearRedLed:
        """
        The red LED has been disabled by a custom protocol command.
        
        The _default action_ for this event is to physically disable the red LED.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnClearRedLed(self)
    @property
    def Scripts_Events_OnClearBeeper(self) -> Scripts_Events_OnClearBeeper:
        """
        The beeper has been disabled by a custom protocol command.
        
        The _default action_ for this event is to physically disable the beeper.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnClearBeeper(self)
    @property
    def Scripts_Events_OnClearRelay(self) -> Scripts_Events_OnClearRelay:
        """
        The relay has been disabled by a custom protocol command.
        
        The _default action_ for this event is to physically disable the relay.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnClearRelay(self)
    @property
    def Scripts_Events_OnTimer(self) -> Scripts_Events_OnTimer:
        """
        Is fired when a timer that was setup by _SetTimer_ (see [BaltechScripts
        Commands](baltechscript.xml#BaltechScript)) expired. Before firing the timer
        it will be deleted. To run a timer continuously it has to be setup again
        within this event.
        """
        return Scripts_Events_OnTimer(self)
    @property
    def Scripts_Events_OnConfigCardSucceeded(self) -> Scripts_Events_OnConfigCardSucceeded:
        """
        The reader has been reconfigured with a ConfigCard and reset.
        
        The _default action_ for this event is to emit the following feedback to the
        card holder:
        
          * Beeper beeps for 0.7 seconds.
          * Green LED is on for 6 seconds.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnConfigCardSucceeded(self)
    @property
    def Scripts_Events_OnConfigCardFailed(self) -> Scripts_Events_OnConfigCardFailed:
        """
        Reconfiguring the reader with a ConfigCard has failed.
        
        The _default action_ for this event is to emit the following feedback to the
        card holder:
        
          * Beeper beeps 7-9 times depending on error type, 0.1 seconds each. 
          * Red LED is on for 6 seconds.
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnConfigCardFailed(self)
    @property
    def Scripts_Events_OnPowerup(self) -> Scripts_Events_OnPowerup:
        """
        If the reader was powered or got any kind of reset it will emit this event
        after everything is initialized.
        """
        return Scripts_Events_OnPowerup(self)
    @property
    def Scripts_Events_OnAutoreadEnabled(self) -> Scripts_Events_OnAutoreadEnabled:
        """
        When the autoread is enabled (either on powerup via configuration or during
        runtime via host command AR.SetMode() ) this event is triggered.
        """
        return Scripts_Events_OnAutoreadEnabled(self)
    @property
    def Scripts_Events_OnAutoreadDisabled(self) -> Scripts_Events_OnAutoreadDisabled:
        """
        When the autoread is disabled via host command AR.SetMode() this event is
        triggered.
        """
        return Scripts_Events_OnAutoreadDisabled(self)
    @property
    def Scripts_Events_OnScan(self) -> Scripts_Events_OnScan:
        """
        This event is fired _before_ every card scan. Autoread waits at least 50 ms
        between 2 card scans; however, depending on the card system, this delay may
        increase up to a multiple of 100 ms.
        
        The _default action_ for this event is to scan the card. Depending on the scan
        result, one of the following events will be fired afterwards:
        
          * [Scripts/Events/OnDetectedNoCard](.#Scripts.Events.OnDetectedNoCard)
          * [Scripts/Events/OnConfigCardSucceeded](.#Scripts.Events.OnConfigCardSucceeded)
          * [Scripts/Events/OnConfigCardFailed](.#Scripts.Events.OnConfigCardFailed)
          * [Scripts/Events/OnDetectedCard](.#Scripts.Events.OnDetectedCard)
        
        **If you configure a custom action, it will replace the default action. To
        perform _both actions_ , you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnScan(self)
    @property
    def Scripts_Events_OnDetectedNoCard(self) -> Scripts_Events_OnDetectedNoCard:
        """
        Once all cards detected by the reader have been processed, this event is fired
        to indicate that there are no more cards.
        
        **This event does not indicate that there are no cards _in front of the
        reader_ . It only means that there are no more _unprocessed cards_ .**
        """
        return Scripts_Events_OnDetectedNoCard(self)
    @property
    def Scripts_Events_OnCheckSuppressRepeat(self) -> Scripts_Events_OnCheckSuppressRepeat:
        """
        The reader has detected the same card again during the
        [RepeatMessageDelay](base.xml#Device.Run.RepeatMessageDelay) interval, while
        [RepeatMessageMode](base.xml#Device.Run.RepeatMessageMode) is set to
        _Suppress_.
        
        The _default action_ for this event is to suppress a message from being sent
        to the host. As a result, the host will only be notified about the first
        detection of the card.
        
        **If you configure a custom action, it will replace the default action: You'll
        override _Suppress_ mode for this card presentation, i.e. the reader will send
        a message each time it detects the card. To perform the custom action _and_
        keep _Suppress_ mode enabled, you need to run the[
        DefaultAction](baltechscript.xml#BaltechScript.DefaultAction) command.**
        """
        return Scripts_Events_OnCheckSuppressRepeat(self)
    @property
    def Scripts_Events_OnBrpCommand(self) -> Scripts_Events_OnBrpCommand:
        """
        This event will be fired when the host sends any BRP command to the reader. It
        is usually used to ensure that the user is informed if the host communication
        gets lost.
        """
        return Scripts_Events_OnBrpCommand(self)
    @property
    def Scripts_Events_OnCardRemoved(self) -> Scripts_Events_OnCardRemoved:
        """
        This event will be fired when Autoread detects that a presented card has been
        removed.
        
        **This event is only triggered if[
        Device/Run/AutoreadWaitForCardRemoval](base.xml#Device.Run.AutoreadWaitForCardRemoval)
        is activated.**
        """
        return Scripts_Events_OnCardRemoved(self)
    @property
    def Scripts_Events_OnCardProcessed(self) -> Scripts_Events_OnCardProcessed:
        """
        This event will be fired by Autoread when a post-processing firmware module
        has processed the card successfully.
        """
        return Scripts_Events_OnCardProcessed(self)
    @property
    def Scripts_Events_OnCardAcceptedByHost(self) -> Scripts_Events_OnCardAcceptedByHost:
        """
        If the host has accepted the card number read in the last Autoread loop, the
        host may trigger this event via
        [AR.RunScript](../cmds/autoread.xml#AR.RunScript). This indicates that the
        card number is included in the host's whitelist. The reader firmware, however,
        never directly executes this script.
        
        In contrary to directly switching LEDs/beeper, using this event allows you to
        keep the UI definition in the reader configuration. See also
        [Scripts.Events.OnCardDeniedByHost](../cmds/autoread.xml#Scripts.Events.OnCardDeniedByHost).
        """
        return Scripts_Events_OnCardAcceptedByHost(self)
    @property
    def Scripts_Events_OnCardDeniedByHost(self) -> Scripts_Events_OnCardDeniedByHost:
        """
        If the host has denied the card number read in the last Autoread loop, the
        host may trigger this event via
        [AR.RunScript](../cmds/autoread.xml#AR.RunScript). This indicates that the
        card is not included in the host's whitelist. The reader firmware, however,
        never directly executes this script.
        
        In contrary to directly switching LEDs/beeper, using this event allows you to
        keep the UI definition in the reader configuration. See also
        [Scripts.Events.OnCardAcceptedByHost](../cmds/autoread.xml#Scripts.Events.OnCardAcceptedByHost).
        """
        return Scripts_Events_OnCardDeniedByHost(self)
    @property
    def Scripts_Events_OnNetworkBooted(self) -> Scripts_Events_OnNetworkBooted:
        """
        This event will be fired when the network stack has been booted.
        """
        return Scripts_Events_OnNetworkBooted(self)
    @property
    def Scripts_Events_OnLinkedNoPort(self) -> Scripts_Events_OnLinkedNoPort:
        """
        This event will be fired when the ethernet reader has no links on its network
        interfaces.
        """
        return Scripts_Events_OnLinkedNoPort(self)
    @property
    def Scripts_Events_OnLinkedNetworkPort(self) -> Scripts_Events_OnLinkedNetworkPort:
        """
        This event will be fired when the ethernet reader has established a link on
        port 1 while port 2 is not linked or not available in hardware.
        """
        return Scripts_Events_OnLinkedNetworkPort(self)
    @property
    def Scripts_Events_OnLinkedDevicePort(self) -> Scripts_Events_OnLinkedDevicePort:
        """
        This event will be fired when the ethernet reader has established a link on
        port 2 while port 1 is not linked.
        """
        return Scripts_Events_OnLinkedDevicePort(self)
    @property
    def Scripts_Events_OnLinkedAllPorts(self) -> Scripts_Events_OnLinkedAllPorts:
        """
        This event will be fired when the ethernet reader has established a link on
        all available ports.
        """
        return Scripts_Events_OnLinkedAllPorts(self)
    @property
    def Scripts_Events_OnWaitingForDHCP(self) -> Scripts_Events_OnWaitingForDHCP:
        """
        This event will be fired when the ethernet reader has started the DHCP client.
        """
        return Scripts_Events_OnWaitingForDHCP(self)
    @property
    def Scripts_Events_OnSearchingForHost(self) -> Scripts_Events_OnSearchingForHost:
        """
        This event will be fired when the ethernet reader has acquired an IP address
        starting to search for a host.
        """
        return Scripts_Events_OnSearchingForHost(self)
    @property
    def Scripts_Events_OnUDPConnectFailure(self) -> Scripts_Events_OnUDPConnectFailure:
        """
        This event will be fired when the ethernet reader has received an UDP
        introspection packet, but the connection trial to the received host failed.
        """
        return Scripts_Events_OnUDPConnectFailure(self)
    @property
    def Scripts_Events_OnHostConnectFailure(self) -> Scripts_Events_OnHostConnectFailure:
        """
        This event will be fired when a connection trial to the configured host
        failed.
        """
        return Scripts_Events_OnHostConnectFailure(self)
    @property
    def Scripts_Events_OnStaticIPFailure(self) -> Scripts_Events_OnStaticIPFailure:
        """
        This event will be fired when the ethernet reader has detected an IP conflict:
        the assigned IP address is already in use by another network device.
        """
        return Scripts_Events_OnStaticIPFailure(self)
    @property
    def Scripts_Events_OnHostFound(self) -> Scripts_Events_OnHostFound:
        """
        This event will be fired when the ethernet reader has connected to the host
        successfully for the first time.
        """
        return Scripts_Events_OnHostFound(self)
    @property
    def Device(self) -> Device:
        """
        This masterkey contains settings that influence the behaviour of the device.
        """
        return Device(self)
    @property
    def Device_VhlSettings(self) -> Device_VhlSettings:
        """
        **These values should not be used any more! They were replaced by[
        Project/VhlSettings](.#Project.VhlSettings) .**
        
        These value are usually set implicitly when activating the corresponding
        ConfigEditor Filter. For details see EQT-368.
        """
        return Device_VhlSettings(self)
    @property
    def Device_VhlSettings_ScanCardFamilies(self) -> Device_VhlSettings_ScanCardFamilies:
        """
        This value is replaced by
        [Project/VhlSettings/ScanCardFamilies](.#Project.VhlSettings.ScanCardFamilies).
        Please refer to that value for further details.
        """
        return Device_VhlSettings_ScanCardFamilies(self)
    @property
    def Device_VhlSettings_ForceReselect(self) -> Device_VhlSettings_ForceReselect:
        """
        Setting this value to True enforces a Reselect on every VHLSelect.
        """
        return Device_VhlSettings_ForceReselect(self)
    @property
    def Device_VhlSettings_DelayRequestATS(self) -> Device_VhlSettings_DelayRequestATS:
        """
        Specifies the delay in ms that shall be waited after detecting an ISO14443
        card and before requesting its ATS (Answer To Select).
        """
        return Device_VhlSettings_DelayRequestATS(self)
    @property
    def Device_VhlSettings_DelayPerformPPS(self) -> Device_VhlSettings_DelayPerformPPS:
        """
        Specifies the delay in ms that shall be waited after receiving the ATS of an
        ISO14443 card and before performing its PPS.
        """
        return Device_VhlSettings_DelayPerformPPS(self)
    @property
    def Device_VhlSettings_MaxBaudrateIso14443A(self) -> Device_VhlSettings_MaxBaudrateIso14443A:
        """
        When VHLSelect / autoread detects a Iso14443/A card it negotiates the send and
        the receive baudrate automatically. Usually it tries to communicate as fast as
        possible (that means as fast as the card is supporting). If the performance
        shall be limited (i.e. due to HF instabilities) this value can be used to set
        a Maximum value for DSI (=reader to card baudrate) and DRI (=card to reader
        baudrate).
        """
        return Device_VhlSettings_MaxBaudrateIso14443A(self)
    @property
    def Device_VhlSettings_MaxBaudrateIso14443B(self) -> Device_VhlSettings_MaxBaudrateIso14443B:
        """
        When VHLSelect / autoread detects a Iso14443/B card it negotiates the send and
        the receive baudrate automatically. Usually it tries to communicate as fast as
        possible (that means as fast as the card is supporting). If the performance
        shall be limited (i.e. due to HF instabilities) this value can be used to set
        a Maximum value for DSI (=reader to card baudrate) and DRI (=card to reader
        baudrate).
        """
        return Device_VhlSettings_MaxBaudrateIso14443B(self)
    @property
    def Device_VhlSettings125Khz(self) -> Device_VhlSettings125Khz:
        """
        **These values should not be used any more! They were replaced by[
        Project/VhlSettings125Khz](.#Project.VhlSettings125Khz) .**
        
        These value are usually set implicitly when activating the corresponding
        ConfigEditor Filter. For details see EQT-368.
        """
        return Device_VhlSettings125Khz(self)
    @property
    def Device_VhlSettings125Khz_ScanCardTypes(self) -> Device_VhlSettings125Khz_ScanCardTypes:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/ScanCardTypesPart1](.#Project.VhlSettings125Khz.ScanCardTypesPart1)
        and
        [Project/VhlSettings125Khz/ScanCardTypesPart2](.#Project.VhlSettings125Khz.ScanCardTypesPart2)
        instead.
        """
        return Device_VhlSettings125Khz_ScanCardTypes(self)
    @property
    def Device_VhlSettings125Khz_ModulationType(self) -> Device_VhlSettings125Khz_ModulationType:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/TTFModType](.#Project.VhlSettings125Khz.TTFModType)
        instead.
        """
        return Device_VhlSettings125Khz_ModulationType(self)
    @property
    def Device_VhlSettings125Khz_Baud(self) -> Device_VhlSettings125Khz_Baud:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/TTFBaudrate](.#Project.VhlSettings125Khz.TTFBaudrate)
        instead.
        """
        return Device_VhlSettings125Khz_Baud(self)
    @property
    def Device_VhlSettings125Khz_TTFHeaderLength(self) -> Device_VhlSettings125Khz_TTFHeaderLength:
        """
        Specifies the pattern length in bit, the reader searches for. Legacy value,
        please use
        [Project/VhlSettings125Khz/TTFHeaderLength](.#Project.VhlSettings125Khz.TTFHeaderLength)
        instead.
        """
        return Device_VhlSettings125Khz_TTFHeaderLength(self)
    @property
    def Device_VhlSettings125Khz_TTFHeader(self) -> Device_VhlSettings125Khz_TTFHeader:
        """
        Pattern which has to match. Legacy value, please use
        [Project/VhlSettings125Khz/TTFHeader](.#Project.VhlSettings125Khz.TTFHeader)
        instead.
        """
        return Device_VhlSettings125Khz_TTFHeader(self)
    @property
    def Device_VhlSettings125Khz_TTFDataLength(self) -> Device_VhlSettings125Khz_TTFDataLength:
        """
        Card data length (includes also Pattern Length). Legacy value, please use
        [Project/VhlSettings125Khz/TTFDataLength](.#Project.VhlSettings125Khz.TTFDataLength)
        instead.
        """
        return Device_VhlSettings125Khz_TTFDataLength(self)
    @property
    def Device_VhlSettings125Khz_TTFOkCounter(self) -> Device_VhlSettings125Khz_TTFOkCounter:
        """
        Number of consecutive successfully reads until a card searched by a pattern is
        reported as detected by VHL. Legacy value, please use
        [Project/VhlSettings125Khz/TTFOkCounter](.#Project.VhlSettings125Khz.TTFOkCounter)
        instead.
        """
        return Device_VhlSettings125Khz_TTFOkCounter(self)
    @property
    def Device_VhlSettings125Khz_IndaspDecode(self) -> Device_VhlSettings125Khz_IndaspDecode:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/IndaspDecode](.#Project.VhlSettings125Khz.IndaspDecode)
        instead.
        """
        return Device_VhlSettings125Khz_IndaspDecode(self)
    @property
    def Device_VhlSettings125Khz_IndaspParityCheck(self) -> Device_VhlSettings125Khz_IndaspParityCheck:
        """
        Legacy value, please use
        [Project/VhlSettings125kHz/IndaspParityCheck](.#Project.VhlSettings125Khz.IndaspParityCheck)
        instead.
        """
        return Device_VhlSettings125Khz_IndaspParityCheck(self)
    @property
    def Device_VhlSettings125Khz_IndaspOkCounter(self) -> Device_VhlSettings125Khz_IndaspOkCounter:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/IndaspDecode](.#Project.VhlSettings125Khz.IndaspDecode)
        instead.
        """
        return Device_VhlSettings125Khz_IndaspOkCounter(self)
    @property
    def Device_VhlSettings125Khz_AwidOkCounter(self) -> Device_VhlSettings125Khz_AwidOkCounter:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/AwidOkCounter](.#Project.VhlSettings125Khz.AwidOkCounter)
        instead.
        """
        return Device_VhlSettings125Khz_AwidOkCounter(self)
    @property
    def Device_VhlSettings125Khz_HidProxOkCounter(self) -> Device_VhlSettings125Khz_HidProxOkCounter:
        """
        Legacy value, please use
        [Project/VhlSettings125Khz/HidProxOkCounter](.#Project.VhlSettings125Khz.HidProxOkCounter)
        instead.
        """
        return Device_VhlSettings125Khz_HidProxOkCounter(self)
    @property
    def Device_Keypad(self) -> Device_Keypad:
        """
        When autoread functionality is activated the keyboard is used to enter PINs.
        Therefore an internal character buffer is available which collects all entered
        pins. This internal buffer will be send to the host as message of Messagetype
        "Keyboard" as soon as one of the following events occurs:
        
          * A [predefined number](.#Device.Keypad.PinLength) of digits was entered 
          * A [special key](.#Device.Keypad.SpecialKeySettings) that terminate keyboard entry was pressed 
          * A [Timeout](.#Device.Keypad.Timeout) was exceeded during pin entry
        """
        return Device_Keypad(self)
    @property
    def Device_Keypad_SpecialKeySettings(self) -> Device_Keypad_SpecialKeySettings:
        """
        This value describes the behaviour of special keys like the star ('*') and the
        sharp ('#') keys.
        """
        return Device_Keypad_SpecialKeySettings(self)
    @property
    def Device_Keypad_Timeout(self) -> Device_Keypad_Timeout:
        """
        When pressing the first key of a PIN a timer is started. After "Timeout"
        seconds the internal character buffer will be transmitted to host and reset.
        If Timeout is 0xFF (which is not recommended) there is not timeout for pin
        entry. If this value is not defined 2 seconds will be used as default.
        """
        return Device_Keypad_Timeout(self)
    @property
    def Device_Keypad_PinLength(self) -> Device_Keypad_PinLength:
        """
        When more digits than specified in this value are entered within
        [Device/Keypad/Timeout](.#Device.Keypad.Timeout) seconds the internal
        character buffer is send to the host and reset. If this value is not defined a
        6 digits are used as default.
        """
        return Device_Keypad_PinLength(self)
    @property
    def Device_Keypad_KeyPressSignal(self) -> Device_Keypad_KeyPressSignal:
        """
        Specify the user feedback when a key is pressed.
        """
        return Device_Keypad_KeyPressSignal(self)
    @property
    def Device_Boot(self) -> Device_Boot:
        """
        This subkey configures how the devices shall behave during powerup.
        """
        return Device_Boot(self)
    @property
    def Device_Boot_ConfigCardState(self) -> Device_Boot_ConfigCardState:
        """
        When a ConfigCard is presented, the reader stores the result of the
        reconfiguration process in this variable. After resetting the device this
        variable is checked by firmware and the corresponding user feedback is done.
        """
        return Device_Boot_ConfigCardState(self)
    @property
    def Device_Boot_FireInputEventAtPowerup(self) -> Device_Boot_FireInputEventAtPowerup:
        """
        Specifies under which condition the InputX line shall be fired at powerup.
        """
        return Device_Boot_FireInputEventAtPowerup(self)
    @property
    def Device_Boot_FireTamperEventAtPowerup(self) -> Device_Boot_FireTamperEventAtPowerup:
        """
        Specifies under which condition the Tamperalarm shall be fired at powerup.
        """
        return Device_Boot_FireTamperEventAtPowerup(self)
    @property
    def Device_Boot_FireGpioEventAtPowerup(self) -> Device_Boot_FireGpioEventAtPowerup:
        """
        Specifies under which condition the GpioX line shall be fired at powerup.
        """
        return Device_Boot_FireGpioEventAtPowerup(self)
    @property
    def Device_Boot_StartAutoreadAtPowerup(self) -> Device_Boot_StartAutoreadAtPowerup:
        """
        This value defines if Autoread functionality shall be started automatically at
        powerup of reader.
        """
        return Device_Boot_StartAutoreadAtPowerup(self)
    @property
    def Device_Boot_FirmwareCrcCheck(self) -> Device_Boot_FirmwareCrcCheck:
        """
        Every firmware is protected by a CRC. By default the firmware does a self test
        by calculating the CRC and verifying that it is correct. If the readers
        program memory is defect or the firwmare was not loaded completely/correctly
        this test will fail and the BootStatus bit 1 (=0x00000002) will be set.
        """
        return Device_Boot_FirmwareCrcCheck(self)
    @property
    def Device_Boot_LegicAdvantInitialization(self) -> Device_Boot_LegicAdvantInitialization:
        """
        Specify if powerup of legic advant firmware shall be delayed until the legic
        advant functionality is completely initialized. This may take up to 2 seconds
        in worst case (depending on hardware).
        """
        return Device_Boot_LegicAdvantInitialization(self)
    @property
    def Device_Run(self) -> Device_Run:
        """
        Contains basic settings for operation of the device
        """
        return Device_Run(self)
    @property
    def Device_Run_ConfigCardAcceptTime(self) -> Device_Run_ConfigCardAcceptTime:
        """
        It is possible to restrict the acceptance of Configuration Cards in [autoread
        mode](autoread.xml#Autoread) to a defined time window after powerup. This
        value specifies the length of this time window in seconds. If it is set to 0,
        reconfiguration via Configuration Cards is disabled. If it is set to 255 (=the
        default value) reconfiguration via Configuraton Cards is not limited at all.
        """
        return Device_Run_ConfigCardAcceptTime(self)
    @property
    def Device_Run_EnabledProtocols(self) -> Device_Run_EnabledProtocols:
        """
        This is a list of all protocols that shall be active on powerup. Depending on
        the firmware variant there may be more activated protocols than listed here.
        If 2 protocols use the same physical interface, the latter one is the actual
        activated one.
        
        **The protocols that are actually activated on powerup are not only determined
        by this configuration value, but also by[
        Device/Run/EnableProtocolOnBAC](.#Device.Run.EnableProtocolOnBAC) , which
        defines the protocol that is enabled when a bus address has been set up via
        BALTECH AdCard ([ Device.Run.BusAdressByBAC](.#Device.Run.BusAdressByBAC) ).
        This protocol overrides all competing protocols in the EnabledProtocols list
        which are running on the same physical interface.**
        """
        return Device_Run_EnabledProtocols(self)
    @property
    def Device_Run_AutoreadPulseHf(self) -> Device_Run_AutoreadPulseHf:
        """
        Specifies if HF shall be disabled between two scan cycles of the [autoread
        functionality](autoread.xml#Autoread).
        """
        return Device_Run_AutoreadPulseHf(self)
    @property
    def Device_Run_RepeatMessageDelay(self) -> Device_Run_RepeatMessageDelay:
        """
        If [RepeatMessageMode](.#Device.Run.RepeatMessageMode) is set to another value
        than default, this time specifies the (minimum/maximum) delay between
        repeating a message in ms.
        
        **Internally this value is handled as a multiple of[
        AutoreadPollTime](.#Device.Run.AutoreadPollTime) respectively the time one
        single poll cycle requires. As this value depends on the activated card types,
        the observed delay may deviate from the selected time value.**
        """
        return Device_Run_RepeatMessageDelay(self)
    @property
    def Device_Run_DeviceName(self) -> Device_Run_DeviceName:
        """
        This value was used to store the name of the device settings (is replaced by
        [Custom/AdminData/DeviceSettingsName](.#Custom.AdminData.DeviceSettingsName))
        """
        return Device_Run_DeviceName(self)
    @property
    def Device_Run_ProjectName(self) -> Device_Run_ProjectName:
        """
        This value was used to store the name of the project settings (is replaced by
        [Custom/AdminData/DeviceSettingsName](.#Custom.AdminData.DeviceSettingsName))
        """
        return Device_Run_ProjectName(self)
    @property
    def Device_Run_DebugInterfaceSecurityLevel(self) -> Device_Run_DebugInterfaceSecurityLevel:
        """
        In earlier firmware versions this value specified the keys that had to be
        known if a configuration should be transferred via debug interface.
        """
        return Device_Run_DebugInterfaceSecurityLevel(self)
    @property
    def Device_Run_RepeatMessageMode(self) -> Device_Run_RepeatMessageMode:
        """
        In [Autoread mode](autoread.xml#Autoread), the reader usually sends _one_
        message per detected card to the host. However, you can change that behavior
        using this configuration value. You may want to do so in the following cases:
        
          * In difficult environments, the reader may erroneously detect the same card several times during one presentation. In this case, you can _suppress_ additional messages from being sent to the host. 
          * If a card is presented longer, you may want more than one message to be sent to the host. In this case, you can _enforce_ a minimum amount of messages. 
        
        \-
        """
        return Device_Run_RepeatMessageMode(self)
    @property
    def Device_Run_RestrictFirmwareRelease(self) -> Device_Run_RestrictFirmwareRelease:
        """
        In earlier firmware builds this value was used to restrict the firmware
        version that works with this configuration. Is replaced by
        [Device/Run/FirmwareVersionBlacklist](.#Device.Run.FirmwareVersionBlacklist).
        """
        return Device_Run_RestrictFirmwareRelease(self)
    @property
    def Device_Run_EnableProtocolOnBAC(self) -> Device_Run_EnableProtocolOnBAC:
        """
        Specifies a (Bus-)protocol, that will be started as soon as a Baltech Address
        Card (BAC) is used to setup a bus address (see
        [Device/Run/BusAdressByBAC](.#Device.Run.BusAdressByBAC))
        """
        return Device_Run_EnableProtocolOnBAC(self)
    @property
    def Device_Run_AccessRightsOfBAC(self) -> Device_Run_AccessRightsOfBAC:
        """
        Specifies the behavior of the reader if a BALTECH AdrCard (BAC) or an NFC
        device enabled for bus address setup is presented.
        
        **When setting a bus address via NFC, also set the configuration value[
        RequiresBusAddress](.#Custom.AdminData.RequiresBusAddress) to ensure a correct
        workflow of the upload software tool.**
        """
        return Device_Run_AccessRightsOfBAC(self)
    @property
    def Device_Run_FirmwareVersionBlacklist(self) -> Device_Run_FirmwareVersionBlacklist:
        """
        This value contains a list of blocked firmware versions. Every entry consists
        of the entries specified below and corresponds to a range of versions of a
        specific a firmware id.
        """
        return Device_Run_FirmwareVersionBlacklist(self)
    @property
    def Device_Run_DefaultBusAdrForBAC(self) -> Device_Run_DefaultBusAdrForBAC:
        """
        If a bus protocol is active and no bus address was set up via BALTECH AdrCard,
        this value indicates the address which is currently used by the protocol due
        to a protocol-specific address or a firmware default value.
        
        **This value doesn't allow to configure a bus address. It is used internally
        by the firmware to report the bus address correctly when a BALTECH AdrCard is
        presented and should not be changed! Use[
        Device/Run/BusAdressByBAC](.#Device.Run.BusAdressByBAC) or the protocol-
        specific address configuration value to set up a bus address.**
        """
        return Device_Run_DefaultBusAdrForBAC(self)
    @property
    def Device_Run_CardReadFailureLogging(self) -> Device_Run_CardReadFailureLogging:
        """
        To get more information about the cause of failed card reads in autoread mode
        this value can be set. The reader will then collect internal data and report
        it via [AR.GetMessage](../cmds/autoread.xml#AR.GetMessage). This data can be
        used by Baltech to analyze the reason of failure.
        """
        return Device_Run_CardReadFailureLogging(self)
    @property
    def Device_Run_MessageExpireTimeout(self) -> Device_Run_MessageExpireTimeout:
        """
        Specifies the time messages (i.e. card read) are retained for retrieval by
        host before they are thrown away (in 1/10 Seconds).
        
        This timeout prevents ghost reads if the host fails to poll the reader for
        some time.
        
        Setting this value to 0 will disable the timeout (message will not be thrown
        away automatically then)
        """
        return Device_Run_MessageExpireTimeout(self)
    @property
    def Device_Run_AutoreadPollTime(self) -> Device_Run_AutoreadPollTime:
        """
        This value specifies the minimum polling cycle time of the [autoread
        functionality](autoread.xml#Autoread) in ms. It defaults to 100 ms.
        
        Along with [Pulse Mode](.#Device.Run.AutoreadPulseHf) this value can be used
        to save energy by reducing the average power consumption of the reader.
        
        **This value only guarantees a lower limit of the polling cycle time! The
        actual cycle time depends on number and type of the[ activated card
        systems](vhl.xml#Project.VhlSettings.ScanCardFamilies) and may be larger if no
        restrictions are configured. In case of a multi-frequency reader scanning for
        all supported card systems a single poll cycle may take around 500 ms.**
        """
        return Device_Run_AutoreadPollTime(self)
    @property
    def Device_Run_AuthReqUploadViaBrp(self) -> Device_Run_AuthReqUploadViaBrp:
        """
        Specifies the authentication level a BEC, BEC2, or BF3 file has to fulfill if
        the file is uploaded via BRP commands.
        
        When uploading a BEC file, this value is a fallback if the parameter of
        [Sys.CfgLoadPrepare](../cmds/system.xml#Sys.CfgLoadPrepare) is "Default".
        """
        return Device_Run_AuthReqUploadViaBrp(self)
    @property
    def Device_Run_AuthReqUploadViaIso14443(self) -> Device_Run_AuthReqUploadViaIso14443:
        """
        Specifies the authentication level a configuration, BEC2 or BF3 file has to
        fulfill if the file is uploaded via the reader's contactless radio interface
        using a ConfigCard or an NFC device.
        """
        return Device_Run_AuthReqUploadViaIso14443(self)
    @property
    def Device_Run_AutoreadWaitForCardRemoval(self) -> Device_Run_AutoreadWaitForCardRemoval:
        """
        Specifies if [Autoread](autoread.xml#Autoread) waits until a presented card
        has been removed before it continues scanning for further cards.
        
        If this mode is enabled, the reader triggers the event
        [Scripts/Events/OnCardRemoved](autoread.xml#Scripts.Events.OnCardRemoved)
        whenever Autoread detects that a card has been removed. You can use this mode
        in combination with [RepeatMessageMode
        Suppress](.#Device.Run.RepeatMessageMode) to avoid that this event is
        triggered in case of short-term card removals of less than
        [RepeatMessageDelay](.#Device.Run.RepeatMessageDelay) ms.
        
        **You can't use this mode in combination with[ RepeatMessageMode
        Force](.#Device.Run.RepeatMessageMode) .**
        """
        return Device_Run_AutoreadWaitForCardRemoval(self)
    @property
    def Device_Run_UsbVendorId(self) -> Device_Run_UsbVendorId:
        """
        Set this value to modify the VendorID of USB devices.
        
        **Setting this value is very dangerous: Neither BALTECH ToolSuite nor the SDK
        can connect to a device via USB once its VendorID has been modified.**
        
        If you use firmware 1100, you need version 1.25.00 or above.
        """
        return Device_Run_UsbVendorId(self)
    @property
    def Device_Run_UsbProductId(self) -> Device_Run_UsbProductId:
        """
        Set this value to modify the ProductID of USB devices.
        
        If you use firmware 1100, you need version 1.25.00 or above.
        """
        return Device_Run_UsbProductId(self)
    @property
    def Device_Run_DenyUploadViaIso14443(self) -> Device_Run_DenyUploadViaIso14443:
        """
        Deny/allow upload of BEC2 files via the reader's wireless RFID interface (ISO
        14443-4) using a ConfigCard or an NFC device.
        """
        return Device_Run_DenyUploadViaIso14443(self)
    @property
    def Device_Run_DenyReaderInfoViaIso14443(self) -> Device_Run_DenyReaderInfoViaIso14443:
        """
        Deny/allow retrieval of general reader information via the reader's wireless
        RFID interface using an NFC device.
        
        The reader information contains the reader's serial number, firmware version,
        boot status, and identifier as well as the name of the loaded project/device
        settings.
        """
        return Device_Run_DenyReaderInfoViaIso14443(self)
    @property
    def Device_Run_DenyUnauthFwUploadViaBrp(self) -> Device_Run_DenyUnauthFwUploadViaBrp:
        """
        Deny/allow firmware upload of BF2 and BF3 files via BRP.
        
        If this value is set to "True", the upload of BF2 or BF3 files is denied as
        soon as the reader is secured by a Config Security Code. In this case, a
        firmware update can only be deployed when packaged with a configuration in a
        BEC2 file. Alternatively, a factory reset can be performed to reset the Config
        Security Code.
        """
        return Device_Run_DenyUnauthFwUploadViaBrp(self)
    @property
    def Device_Run_SetBusAdrOnUploadViaIso14443(self) -> Device_Run_SetBusAdrOnUploadViaIso14443:
        """
        Enable/disable the setup of a bus address along with a BEC2 file upload via
        the reader's wireless RFID interface.
        
        If this feature is enabled, the reader requests the bus address from the host
        via APDU after a successful BEC2 file upload. The BEC2 file serves as an
        authorization for address setup.
        
        **If you enable this feature, also set the configuration value[
        RequiresBusAddress](.#Custom.AdminData.RequiresBusAddress) to ensure a correct
        workflow of the upload software tool.**
        """
        return Device_Run_SetBusAdrOnUploadViaIso14443(self)
    @property
    def Device_Run_MaintenanceFunctionFilter(self) -> Device_Run_MaintenanceFunctionFilter:
        """
        Disable individual maintenance functions that are triggered when the reader
        operates in Autoread mode and a maintenance function card (e.g. ConfigCard or
        LicenseCard) or an NFC device is presented.
        """
        return Device_Run_MaintenanceFunctionFilter(self)
    @property
    def Device_Run_FirstVhlRc500Key(self) -> Device_Run_FirstVhlRc500Key:
        """
        Usually Mifare Classic VHL files are transferring their keys from the
        configuration into the RC500 eeprom for security reasons. This value specifies
        the begin of the key address range the VHL subsystem may occupy in the RC.
        """
        return Device_Run_FirstVhlRc500Key(self)
    @property
    def Device_Run_ConfigCardMifareKey(self) -> Device_Run_ConfigCardMifareKey:
        """
        This value has to be set only if:
        
          * The reader shall _not_ be configurable via Mifare Classic Configuration Cards (has to be set to empty value then) 
          * The reader shall be reconfigurable with Mifare Configuration Cards that is non-standard, but with a custom configuration card. 
        
        **This is a factory loaded key that will be restored automatically on reader
        reboot if deleted accidentally (see[
        Device/Run/ConfigCardMifareKeyBackup](.#Device.Run.ConfigCardMifareKeyBackup)
        ).**
        """
        return Device_Run_ConfigCardMifareKey(self)
    @property
    def Device_Run_ConfigSecurityCode(self) -> Device_Run_ConfigSecurityCode:
        """
        This value specifies the security code that is needed to reconfigure the
        reader via BALTECH ConfigCard or via an encrypted configuration file (BEC,
        BEC2).
        
        **If this value is not set, the reader can be reconfigured by every
        configuration card.**
        """
        return Device_Run_ConfigSecurityCode(self)
    @property
    def Device_Run_CustomerKey(self) -> Device_Run_CustomerKey:
        """
        This value has to be set only if:
        
          * The reader shall _not_ encrypt the content of the Configuration Card additionally to the cards crypto system (has to be set to empty value then) 
          * The reader shall be reconfigurable with Mifare Configuration Cards that are not created with configurator pack 001 (=Baltech Standard), but with a custom configurator pack. 
        
        **This is a factory loaded key that will be restored automatically on reader
        reboot if deleted accidentally (see[
        Device/Run/CustomerKeyBackup](.#Device.Run.CustomerKeyBackup) ).**
        """
        return Device_Run_CustomerKey(self)
    @property
    def Device_Run_AltConfigSecurityCode(self) -> Device_Run_AltConfigSecurityCode:
        """
        This is an alternative [ConfigSecurityCode](.#Device.Run.ConfigSecurityCode).
        The reader will accept Configuration Cards with either of both values.
        """
        return Device_Run_AltConfigSecurityCode(self)
    @property
    def Device_Run_ConfigCardDesfireKey(self) -> Device_Run_ConfigCardDesfireKey:
        """
        This value has to be set only if:
        
          * The reader shall _not_ be configurable via Mifare Desfire Configuration Cards (has to be set to empty value then) 
          * The reader shall be reconfigurable with Mifare Desfire Configuration Cards that are non-standard, but with a custom configuration card. 
        
        **This is a factory loaded key that will be retored automatically on reader
        reboot if deleted accidentally (see[
        Device/Run/ConfigCardDesfireKeyBackup](.#Device.Run.ConfigCardDesfireKeyBackup)**
        """
        return Device_Run_ConfigCardDesfireKey(self)
    @property
    def Device_Run_BusAdressByBAC(self) -> Device_Run_BusAdressByBAC:
        """
        If a BAC (Baltech Address Card) was used to set the bus address of a reader,
        the bus address is stored within this value. This value works protocol
        independent (i.e. it works on ALL bus protocols that would needs a dip switch
        otherwise). This value is only for internal use.
        """
        return Device_Run_BusAdressByBAC(self)
    @property
    def Device_Run_ConfigCardMifareKeyBackup(self) -> Device_Run_ConfigCardMifareKeyBackup:
        """
        Internal Backup of
        [Device/Run/ConfigCardMifareKey](.#Device.Run.ConfigCardMifareKey).
        """
        return Device_Run_ConfigCardMifareKeyBackup(self)
    @property
    def Device_Run_CustomerKeyBackup(self) -> Device_Run_CustomerKeyBackup:
        """
        Internal Backup of
        [Device/Run/ConfigCardEncryptKey](.#Device.Run.CustomerKey).
        """
        return Device_Run_CustomerKeyBackup(self)
    @property
    def Device_Run_ConfigCardDesfireKeyBackup(self) -> Device_Run_ConfigCardDesfireKeyBackup:
        """
        Internal Backup of
        [Device/Run/ConfigCardDesfireKey](.#Device.Run.ConfigCardDesfireKey).
        """
        return Device_Run_ConfigCardDesfireKeyBackup(self)
    @property
    def Device_Run_UsbSuspendMode(self) -> Device_Run_UsbSuspendMode:
        """
        Enables or disables USB suspend mode.
        """
        return Device_Run_UsbSuspendMode(self)
    @property
    def Device_CryptoKey(self) -> Device_CryptoKey:
        """
        Keys container used by the crypto manager for crypto operations.
        """
        return Device_CryptoKey(self)
    @property
    def Device_CryptoKey_Entry(self) -> Device_CryptoKey_Entry:
        """
        Key entry which contains a key and its according CryptoAlgorithm with
        KeyAccessRights used by the crypto manager.
        """
        return Device_CryptoKey_Entry(self)
    @property
    def Device_HostSecurity(self) -> Device_HostSecurity:
        """
        These values can be used to change the reader's security settings. They
        address both AES and PKI authentication and encryption. When the reader is
        rebooted the next time, the settings will be applied.
        
        **These values are not only written to configuration memory but also extracted
        from ConfigEditor to be loaded via TLV block directly into security memory.**
        """
        return Device_HostSecurity(self)
    @property
    def Device_HostSecurity_AccessConditionMask(self) -> Device_HostSecurity_AccessConditionMask:
        """
        Defines an Access Condition Mask for every security Level. If the config value
        of a security Level is not set, it is not restricted at all.
        
        **Level 3 has _always_ all access rights. No matter if there is a limitation
        via AcMask[3] or not.**
        """
        return Device_HostSecurity_AccessConditionMask(self)
    @property
    def Device_HostSecurity_Key(self) -> Device_HostSecurity_Key:
        """
        Defines a Key for every security Level. This key has to be used when working
        encrypted.
        
        **Level 0 will never use keys, since it always works unencrypted.**
        """
        return Device_HostSecurity_Key(self)
    @property
    def Device_HostSecurity_PrivateKey(self) -> Device_HostSecurity_PrivateKey:
        """
        Private key of the reader (PKI).
        """
        return Device_HostSecurity_PrivateKey(self)
    @property
    def Device_HostSecurity_PublicKey(self) -> Device_HostSecurity_PublicKey:
        """
        Public key of the reader (PKI).
        """
        return Device_HostSecurity_PublicKey(self)
    @property
    def Device_HostSecurity_HostRootCertSubjectName(self) -> Device_HostSecurity_HostRootCertSubjectName:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the distuingished subject name of the
        X503 host root certificate. The reader creates the host root certificate from
        this value, [HostRootCertPubKey](.#Device.HostSecurity.HostRootCertPubKey) and
        [HostRootCertSnr](.#Device.HostSecurity.HostRootCertSnr) to verify the host
        certificate chain.
        
        Please keep in mind, that the issuer name is the same as the subject name of
        the certificate. Thus the issuer name needs not to be stored separately in the
        configuration.
        
        **RootCertSubjectName[0] must not be used, since security level 0 works
        unencrypted.**
        """
        return Device_HostSecurity_HostRootCertSubjectName(self)
    @property
    def Device_HostSecurity_HostRootCertPubKey(self) -> Device_HostSecurity_HostRootCertPubKey:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the public key of the X503 host root
        certificate. The reader creates the host root certificate from this value,
        [HostRootCertSubjectName](.#Device.HostSecurity.HostRootCertSubjectName) and
        [HostRootCertSnr](.#Device.HostSecurity.HostRootCertSnr) to verify the host
        certificate chain.
        
        **Only the raw bits are stored in this field. The crypto algorithms have to be
        always ECC-P256 with SHA256.**
        
        **RootCertPubKey[0] must not be used, since security level 0 works
        unencrypted.**
        """
        return Device_HostSecurity_HostRootCertPubKey(self)
    @property
    def Device_HostSecurity_HostRootCertSnr(self) -> Device_HostSecurity_HostRootCertSnr:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the serial number of the X503 host root
        certificate. The reader creates the host root certificate from this value,
        [HostRootCertSubjectName](.#Device.HostSecurity.HostRootCertSubjectName) and
        [HostRootCertPubKey](.#Device.HostSecurity.HostRootCertPubKey) to verify the
        host certificate chain.
        
        **RootCertSnr[0] must not be used, since security level 0 works unencrypted.**
        """
        return Device_HostSecurity_HostRootCertSnr(self)
    @property
    def Device_HostSecurity_ReaderCertSnr(self) -> Device_HostSecurity_ReaderCertSnr:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the serial number of the X503
        certificate of the reader.
        
        **ReaderCertSnr[0] must not be used, since security level 0 works
        unencrypted.**
        """
        return Device_HostSecurity_ReaderCertSnr(self)
    @property
    def Device_HostSecurity_ReaderCertIssuer(self) -> Device_HostSecurity_ReaderCertIssuer:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the distinguished issuer name of the
        X503 certificate of the reader.
        
        **ReaderCertIssuer[0] must not be used, since security level 0 works
        unencrypted.**
        """
        return Device_HostSecurity_ReaderCertIssuer(self)
    @property
    def Device_HostSecurity_ReaderCertValidity(self) -> Device_HostSecurity_ReaderCertValidity:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the time range, in which this
        certificate is valid.
        
        **ReaderCertValidity[0] must not be used, since security level 0 works
        unencrypted.**
        """
        return Device_HostSecurity_ReaderCertValidity(self)
    @property
    def Device_HostSecurity_ReaderCertSignature(self) -> Device_HostSecurity_ReaderCertSignature:
        """
        If PKI is enabled for a specific security level, this value must contain the
        ASN.1 DER encoded tag, that represents the signature created by the issuer
        over the whole reader certificate.
        
        **ReaderCertValidity[0] must not be used, since security level 0 works
        unencrypted.**
        """
        return Device_HostSecurity_ReaderCertSignature(self)
    @property
    def Device_VirtualLeds(self) -> Device_VirtualLeds:
        """
        This key contains all settings related to Virtual LEDs (VLEDs).
        
        A Virtual LED is a description for the behavior of one or more reader LEDs
        when being enabled via [UI.Enable](../cmds/userinterface.xml#UI.Enable) or
        [BaltechScript](baltechscript.xml#BaltechScript).
        
        You can enable VLEDs instantly without any delay. Alternatively, you can
        activate them gradually: In this case, the RGB color is increased in several
        steps until the desired color is obtained. When you deactivate a VLED, the
        inverse fading behavior is applied. You can configure this transition time
        globally for all VLEDs or define a certain value for each VLED individually.
        
        There are static and dynamic VLEDs. A static VLED preserves a certain color
        until it is deactivated or a different VLED is activated. A dynamic or pulsing
        VLED continuously fades the RGB color between 2 values.
        """
        return Device_VirtualLeds(self)
    @property
    def Device_VirtualLeds_TransitionTime(self) -> Device_VirtualLeds_TransitionTime:
        """
        This value defines the default transition time in ms from off to the target
        RGB color or vice versa, when a VLED port is enabled or disabled. The value 0
        enables/disables LEDs instantly.
        
        This value is applied to every VLED if no individual transition time is
        specified in the corresponding [VLED
        definition](.#Device.VirtualLeds.CustomVledDefinition).
        
        **This value is not applied to legacy LED ports (GreenLed/RedLed/BlueLed). To
        maintain backwards compatibility, these ports use transition time 0 as
        default. To override this value, define an individual transition time within
        the[ VLED definition](.#Device.VirtualLeds.CustomVledDefinition) .**
        """
        return Device_VirtualLeds_TransitionTime(self)
    @property
    def Device_VirtualLeds_PulsePeriod(self) -> Device_VirtualLeds_PulsePeriod:
        """
        This value defines the period in ms for pulsing VLEDs. This is the time to
        transition from the first to the second RGB color and back.
        
        This value applies to any dynamic VLED definition.
        """
        return Device_VirtualLeds_PulsePeriod(self)
    @property
    def Device_VirtualLeds_CustomVledDefinition(self) -> Device_VirtualLeds_CustomVledDefinition:
        """
        Virtual LED (VLED) definitions describe how one or more LEDs are to be
        activated when the corresponding VLED port is enabled via
        [UI.Enable](../cmds/userinterface.xml#UI.Enable) or
        [BaltechScript](baltechscript.xml#BaltechScript).
        
        **The first 8 VLED definitions (0x40 - 0x47) are also used to maintain legacy
        compatibility. They're evaluated by the firmware in case a legacy LED port
        (GreenLed/RedLed/BlueLed) is switched. To avoid an undesired behavior, use
        either legacy _or_ VLED ports, but not both.**
        """
        return Device_VirtualLeds_CustomVledDefinition(self)
    @property
    def Device_Statistics(self) -> Device_Statistics:
        """
        This key contains values that are only for Baltech internal use. They will be
        set on firmware failure to log unexpected states. Must not be set/cleared by
        customers.
        
        Device/Statistics/FirmwareId & Device/Statistics/FirmwareRelease are
        identifing the Firmware that was the cause of the failure (may be different
        from current firmware)
        """
        return Device_Statistics(self)
    @property
    def Device_Statistics_FirmwareId(self) -> Device_Statistics_FirmwareId:
        """
        Contains the ID of the firmware (e.g. 1100 for ID-engine Z) that produced the
        logged errors. When an error is detected and this value does not correspond to
        the current firwmare ID, all statistics counters are reset.
        """
        return Device_Statistics_FirmwareId(self)
    @property
    def Device_Statistics_FirmwareRelease(self) -> Device_Statistics_FirmwareRelease:
        """
        Contains the firmware version that produced the logged errors. When an error
        is detected and this value does not correspond to the current firwmare ID, all
        statistics counters are reset.
        """
        return Device_Statistics_FirmwareRelease(self)
    @property
    def Device_Statistics_WatchdogResetCount(self) -> Device_Statistics_WatchdogResetCount:
        """
        Contains the number of watchdog resets caused by the firmware that is
        specified in the [FirmwareId](.#Device.Statistics.FirmwareId) and
        [FirmwareRelease](.#Device.Statistics.FirmwareRelease) values.
        """
        return Device_Statistics_WatchdogResetCount(self)
    @property
    def Device_Statistics_StackOverflowCount(self) -> Device_Statistics_StackOverflowCount:
        """
        Contains the number of stack overflows caused by the firmware that is
        specified in the [FirmwareId](.#Device.Statistics.FirmwareId) and
        [FirmwareRelease](.#Device.Statistics.FirmwareRelease) values.
        """
        return Device_Statistics_StackOverflowCount(self)
    @property
    def Device_Statistics_StackOverflowTaskAddress(self) -> Device_Statistics_StackOverflowTaskAddress:
        """
        Contains the address of the Task that caused the last stackoverflow. To assign
        this address to a name simply search for this hexvalue in the listingfile.
        """
        return Device_Statistics_StackOverflowTaskAddress(self)
    @property
    def Device_Statistics_BrownoutResetCount(self) -> Device_Statistics_BrownoutResetCount:
        """
        Contains the number of brownouts registered by the firmware that is specified
        in the [FirmwareId](.#Device.Statistics.FirmwareId) and
        [FirmwareRelease](.#Device.Statistics.FirmwareRelease) values.
        """
        return Device_Statistics_BrownoutResetCount(self)
    @property
    def Device_Statistics_KeypadResetCount(self) -> Device_Statistics_KeypadResetCount:
        """
        Contains the number of unintended keypad controller resets registered by the
        firmware that is specified in the [FirmwareId](.#Device.Statistics.FirmwareId)
        and [FirmwareRelease](.#Device.Statistics.FirmwareRelease) values.
        """
        return Device_Statistics_KeypadResetCount(self)
    @property
    def Device_Statistics_AccessRestrictedTaskOverflowResetCount(self) -> Device_Statistics_AccessRestrictedTaskOverflowResetCount:
        """
        Contains the number of resets caused due to an overflow of access-restricted
        tasks registered by the firmware that is specified in the
        [FirmwareId](.#Device.Statistics.FirmwareId) and
        [FirmwareRelease](.#Device.Statistics.FirmwareRelease) values.
        """
        return Device_Statistics_AccessRestrictedTaskOverflowResetCount(self)
    @property
    def Custom(self) -> Custom:
        """
        This value contains configuration values for customer specific applications.
        Due to historical reasons some non-customer specific subkeys are nonetheless
        part of this masterkey.
        """
        return Custom(self)
    @property
    def Custom_BlackWhiteList(self) -> Custom_BlackWhiteList:
        """
        This subkey defines either whitelist or a blacklist for the autoread
        functionality. Every value read by autoread functionality will be checked
        against this list. It will be denied if it part of the list (blacklist) or not
        part of the list (whitelist). In the case of denial the
        [Scripts/Events/OnBlackWhiteListDenied
        Event](.#Scripts.Events.OnBlackWhiteListDenied) will be emitted.
        """
        return Custom_BlackWhiteList(self)
    @property
    def Custom_BlackWhiteList_ListMode(self) -> Custom_BlackWhiteList_ListMode:
        """
        Specifies if the list within this subkey shall be used as Black- or as
        Whitelist.
        """
        return Custom_BlackWhiteList_ListMode(self)
    @property
    def Custom_BlackWhiteList_RangeStart(self) -> Custom_BlackWhiteList_RangeStart:
        """
        If this value is specified, it defines a lower limit of accepted/denied values
        read by autoread functionality. It is intended mainly for Blacklistmode, where
        all values below this value are denied (In Whitelistmode all values below this
        value are accepted).
        """
        return Custom_BlackWhiteList_RangeStart(self)
    @property
    def Custom_BlackWhiteList_RangeEnd(self) -> Custom_BlackWhiteList_RangeEnd:
        """
        If this value is specified, it defines an upper limit of accepted/denied
        values read by autoread functionality. It is intended mainly for
        Blacklistmode, where all values higher than this value are denied (In
        Whitelistmode all values higher than this value are accepted).
        """
        return Custom_BlackWhiteList_RangeEnd(self)
    @property
    def Custom_BlackWhiteList_EntrySize(self) -> Custom_BlackWhiteList_EntrySize:
        """
        This value specifies the length of a entry in the
        [Black-/Whitelist](.#Custom.BlackWhiteList.List). All entries in this list
        have to be of the length specified here. Although this value can be omitted
        (in which case the length of the message returned by Autoread is assumed as
        entrysize), we strongly recommend you specify the size explicitly.
        
        If the length of the value returned by Autoread does not match this value the
        smaller one is used as "comparison length". Only "comparson length" bytes
        (starting from the right) from the autoread number and the black-/whitelist
        entry are compared then.
        """
        return Custom_BlackWhiteList_EntrySize(self)
    @property
    def Custom_BlackWhiteList_List(self) -> Custom_BlackWhiteList_List:
        """
        This is a list of all values returned by autoread functionality that shall be
        denied (in Blacklistmode) or accepted (in Whitelistmode).
        
        Every configuration value may contain multiple, concatenated autoread values.
        All autoread values stored in this list must be sorted ascending (the values
        within a configuration value as the values between configuration values).
        
        ` If the autoread functionality returns a value of 4 byte length this would be
        a valid list: List[0] = "1111" "2222" "3333" List[1] = "4444" List[2] = "5555"
        "6666" `
        """
        return Custom_BlackWhiteList_List(self)
    @property
    def Custom_Crypto(self) -> Custom_Crypto:
        """
        List of skipjack keys that can be used by the Crypto commands to
        encrypt-/decrypt user data. The primary purpose of these keys is to encode
        configurations.
        
        **Must not be mixed up with Host Interface Security or with Desfire Crypto /
        Mifare Plus Crypto.**
        """
        return Custom_Crypto(self)
    @property
    def Custom_Crypto_Key(self) -> Custom_Crypto_Key:
        """
        Specifies a list of keys that can be referred by the crypro commands via
        index.
        """
        return Custom_Crypto_Key(self)
    @property
    def Custom_AdminData(self) -> Custom_AdminData:
        """
        Contains only values that are identifying and describing the rest of the
        configuration. These values do not have direct impact on the reader firmware
        behaviour. They are only used as storage for allowing configuration management
        software to set/get administrative information about the project/reader.
        
        The configuration is split into two logical parts which are identifies by
        different fields:
        
          * DeviceSettings: includes all configuration settings needed for host/user interaction 
          * ProjectSettings: includes all configuration settings describing the project card(s) like crypto-key, format of data, ... 
          * MasterCard: Mastercards are identified by these values. _Attention:_ non-mastercards will refer to a mastercard, too. The corresponding Values are called _MasterCardRef_ / _MasterCardNameRef_.
        """
        return Custom_AdminData(self)
    @property
    def Custom_AdminData_CustomerNo(self) -> Custom_AdminData_CustomerNo:
        """
        A unique Customer's ID. This are the first 5 digits of the ConfigID (12345-xxxx-xxxx-xx). The following ID ranges may be used  Range  |  Meaning   
        ---|---  
        00000  |  Only for standard configurations created by Baltech   
        0xxxx  |  Only for custom configurations created by Baltech   
        5xxxx  |  configurations created by Baltech's customers. The customers may use _xxxx_ to store their customers' id.   
        99999  |  ???
        """
        return Custom_AdminData_CustomerNo(self)
    @property
    def Custom_AdminData_DeviceSettingsNo(self) -> Custom_AdminData_DeviceSettingsNo:
        """
        Contains an ID that identifies the device settings in an unique manner. This are the 4 digits in the third block of the ConfigID (xxxxx-xxxx-1234-xx). The following ranges may be used  Range  |  Meaning   
        ---|---  
        00000  |  This value means, that _no_ device settings are stored in this configuration at all.   
        1000 - 4999  |  The device settings were created by Baltech   
        5xxx  |  The device settings were created by the customer. This implies that Baltech does not guarantee uniqueness of this value.   
        91xx  |  Dummybaseconfigurations (only for legacyprojects). They are not needed when working with ConfigEditor.   
        9999  |  ???
        """
        return Custom_AdminData_DeviceSettingsNo(self)
    @property
    def Custom_AdminData_DeviceSettingsName(self) -> Custom_AdminData_DeviceSettingsName:
        """
        A human readable description of the DeviceSettings
        """
        return Custom_AdminData_DeviceSettingsName(self)
    @property
    def Custom_AdminData_DeviceSettingsVersion(self) -> Custom_AdminData_DeviceSettingsVersion:
        """
        The version of the Devicesettings. Has to be incremented on every change on
        device specific settings by one.
        """
        return Custom_AdminData_DeviceSettingsVersion(self)
    @property
    def Custom_AdminData_ProjectSettingsNo(self) -> Custom_AdminData_ProjectSettingsNo:
        """
        Contains an ID that identifies the device settings in an unique manner. This
        are the 4 digits in the second block of the ConfigID (xxxxx-1234-xxxx-xx).
        This ID has to be unique within the same
        [CustomerNo](.#Custom.AdminData.CustomerNo). By convention Value < 0500 are
        used by Baltech and Values > 0500 are used by Baltech's Customers.
        """
        return Custom_AdminData_ProjectSettingsNo(self)
    @property
    def Custom_AdminData_ProjectName(self) -> Custom_AdminData_ProjectName:
        """
        A human readable description of the ProjectSettings
        """
        return Custom_AdminData_ProjectName(self)
    @property
    def Custom_AdminData_ProjectSettingsVersion(self) -> Custom_AdminData_ProjectSettingsVersion:
        """
        The version of the Projectsettings. Has to be incremented on every change on
        project specific settings by one.
        """
        return Custom_AdminData_ProjectSettingsVersion(self)
    @property
    def Custom_AdminData_MasterCardNoRef(self) -> Custom_AdminData_MasterCardNoRef:
        """
        This Mastercardnumber refers to a MasterCard that has to be used to create
        configuration cards (or encrypted .bec files) from this configuration. The
        default value of 1 means that no custom Mastercard is used but the Baltech
        standard mastercard.
        """
        return Custom_AdminData_MasterCardNoRef(self)
    @property
    def Custom_AdminData_MasterCardNameRef(self) -> Custom_AdminData_MasterCardNameRef:
        """
        This field contains the corresponding name of the mastercard (see
        [MasterCardNoRef](.#Custom.AdminData.MasterCardNoRef))
        """
        return Custom_AdminData_MasterCardNameRef(self)
    @property
    def Custom_AdminData_DataLen(self) -> Custom_AdminData_DataLen:
        """
        This Value is not used any more
        """
        return Custom_AdminData_DataLen(self)
    @property
    def Custom_AdminData_DummyDeviceSettingsNo(self) -> Custom_AdminData_DummyDeviceSettingsNo:
        """
        This value is needed only for legacy configurations. In newer configuration it
        is simply a indicator if the current configuration was build from two
        configurations (a DeviceSettings Config and an independent ProjectSettings
        Config) or from a single one (if does not exist).
        """
        return Custom_AdminData_DummyDeviceSettingsNo(self)
    @property
    def Custom_AdminData_DummyDeviceSettingsName(self) -> Custom_AdminData_DummyDeviceSettingsName:
        """
        This value is needed only for legacy configurations
        """
        return Custom_AdminData_DummyDeviceSettingsName(self)
    @property
    def Custom_AdminData_DummyDeviceSettingsVersion(self) -> Custom_AdminData_DummyDeviceSettingsVersion:
        """
        This value is needed only for legacy configurations
        """
        return Custom_AdminData_DummyDeviceSettingsVersion(self)
    @property
    def Custom_AdminData_AddCustomerKeyInProduction(self) -> Custom_AdminData_AddCustomerKeyInProduction:
        """
        **This is a deprecated value. Since 28.05.2014 it is completely ignored.
        Before deprecation it was used as indicator to load the CustomerKey during
        production (by setting it to 1).**
        """
        return Custom_AdminData_AddCustomerKeyInProduction(self)
    @property
    def Custom_AdminData_MasterCardNo(self) -> Custom_AdminData_MasterCardNo:
        """
        Must only be set if this _is_ a MasterCard. It must not contain any
        configuration components other than a VHL file with ID #240 and crypto keys
        for encrypting the configuration. This ID is the unique identification of the
        mastercard and has to be referred by configurations via
        [MasterCardNoRef](.#Custom.AdminData.MasterCardNoRef))
        """
        return Custom_AdminData_MasterCardNo(self)
    @property
    def Custom_AdminData_MasterCardName(self) -> Custom_AdminData_MasterCardName:
        """
        This field contains the corresponding name of the mastercard (see
        [MasterCardNo](.#Custom.AdminData.MasterCardNo))
        """
        return Custom_AdminData_MasterCardName(self)
    @property
    def Custom_AdminData_DeviceSettingsTemplateBased(self) -> Custom_AdminData_DeviceSettingsTemplateBased:
        """
        This value is not used any more
        """
        return Custom_AdminData_DeviceSettingsTemplateBased(self)
    @property
    def Custom_AdminData_ProjectSettingsTemplateBased(self) -> Custom_AdminData_ProjectSettingsTemplateBased:
        """
        This value is not used any more
        """
        return Custom_AdminData_ProjectSettingsTemplateBased(self)
    @property
    def Custom_AdminData_UniqueDeviceName(self) -> Custom_AdminData_UniqueDeviceName:
        """
        This value contains a unique ASCII-string that identifies the device
        containing this value. It is currently only used for Ethernet devices that
        support SLP. This name can be retrieved as SLP attribute.
        """
        return Custom_AdminData_UniqueDeviceName(self)
    @property
    def Custom_AdminData_DraftFlag(self) -> Custom_AdminData_DraftFlag:
        """
        The ConfigEditor sets this value (without any content) for configurations that
        are in draft mode. If this value is not defined, the configuration is
        released.
        """
        return Custom_AdminData_DraftFlag(self)
    @property
    def Custom_AdminData_BaltechConfigID(self) -> Custom_AdminData_BaltechConfigID:
        """
        This value contains a 18 byte string formatted like "aaaaa-bbbb-cccc-dd"
        (without zero-terminator!). If this configuration was created at Baltech this
        value is the configuration id. If the configuration was modified at a customer
        this value refers to the baltech configuration id, which the customer used as
        base for his modifications.
        """
        return Custom_AdminData_BaltechConfigID(self)
    @property
    def Custom_AdminData_DeviceSettingsCustomerNo(self) -> Custom_AdminData_DeviceSettingsCustomerNo:
        """
        The unique Customer's ID of the device settings. see also
        [CustomerNo](.#Custom.AdminData.CustomerNo). As this value was introduced much
        later than CustomerNo a lot of configurations do not contain this value. In
        this case the reader has to fallback to the value of CustomerNo.
        """
        return Custom_AdminData_DeviceSettingsCustomerNo(self)
    @property
    def Custom_AdminData_FactoryResetFirmwareVersion(self) -> Custom_AdminData_FactoryResetFirmwareVersion:
        """
        This value contains information to pinpoint exactly which firmware should be
        loaded upon a factory reset: - the firmware ID (like 1055) - the firmware
        version (like 1.16.17), where each of the numbers is stored separately in BCD
        encoding.
        """
        return Custom_AdminData_FactoryResetFirmwareVersion(self)
    @property
    def Custom_AdminData_BleFirmwareVersion(self) -> Custom_AdminData_BleFirmwareVersion:
        """
        This value contains information about the version of the firmware, which is
        currently active in the BLE communication chip.
        
        **This value is used internally by the firmware and should not be changed!**
        """
        return Custom_AdminData_BleFirmwareVersion(self)
    @property
    def Custom_AdminData_RequiresBusAddress(self) -> Custom_AdminData_RequiresBusAddress:
        """
        This value indicates if the upload software tool must request the user to
        specify a bus address. It's not used by the firmware.
        
        Use this value in combination with
        [SetBusAdrOnUploadViaIso14443](.#Device.Run.SetBusAdrOnUploadViaIso14443)
        and/or [AccessRightsOfBAC](.#Device.Run.AccessRightsOfBAC) when you want to
        enable an NFC-based addressing mechanism.
        """
        return Custom_AdminData_RequiresBusAddress(self)
    @property
    def Custom_AdminData_V2eFormatIndicator(self) -> Custom_AdminData_V2eFormatIndicator:
        """
        This value is not used by firmware. It should even never occur in a real
        configuration. It is needed internally for implementing v2e configuration
        format.
        """
        return Custom_AdminData_V2eFormatIndicator(self)
    @property
    def Registers(self) -> Registers:
        """
        This masterkey contains baltech internal values for the register manager.
        """
        return Registers(self)
    @property
    def Registers_Rc(self) -> Registers_Rc:
        """
        This value contains HF Settings (Register Settings) of the RC500 / RC400 /
        RC632 reader chip.
        """
        return Registers_Rc(self)
    @property
    def Registers_Rc_TxControl14A848(self) -> Registers_Rc_TxControl14A848:
        """
        Specifies settings of the TxControl register for 14A_848.
        """
        return Registers_Rc_TxControl14A848(self)
    @property
    def Registers_Rc_TxControl14A424(self) -> Registers_Rc_TxControl14A424:
        """
        Specifies settings of the TxControl register for 14A_424.
        """
        return Registers_Rc_TxControl14A424(self)
    @property
    def Registers_Rc_TxControl14A212(self) -> Registers_Rc_TxControl14A212:
        """
        Specifies settings of the TxControl register for 14A_212.
        """
        return Registers_Rc_TxControl14A212(self)
    @property
    def Registers_Rc_TxControl14A106(self) -> Registers_Rc_TxControl14A106:
        """
        Specifies settings of the TxControl register for 14A_106.
        """
        return Registers_Rc_TxControl14A106(self)
    @property
    def Registers_Rc_TxControl14B848(self) -> Registers_Rc_TxControl14B848:
        """
        Specifies settings of the TxControl register for 14B_848.
        """
        return Registers_Rc_TxControl14B848(self)
    @property
    def Registers_Rc_TxControl14B424(self) -> Registers_Rc_TxControl14B424:
        """
        Specifies settings of the TxControl register for 14B_424.
        """
        return Registers_Rc_TxControl14B424(self)
    @property
    def Registers_Rc_TxControl14B212(self) -> Registers_Rc_TxControl14B212:
        """
        Specifies settings of the TxControl register for 14B_212.
        """
        return Registers_Rc_TxControl14B212(self)
    @property
    def Registers_Rc_TxControl14B106(self) -> Registers_Rc_TxControl14B106:
        """
        Specifies settings of the TxControl register for 14B_106.
        """
        return Registers_Rc_TxControl14B106(self)
    @property
    def Registers_Rc_TxControl15Standard(self) -> Registers_Rc_TxControl15Standard:
        """
        Specifies settings of the TxControl register for 15Standard.
        """
        return Registers_Rc_TxControl15Standard(self)
    @property
    def Registers_Rc_TxControl15Fast(self) -> Registers_Rc_TxControl15Fast:
        """
        Specifies settings of the TxControl register for 15Fast.
        """
        return Registers_Rc_TxControl15Fast(self)
    @property
    def Registers_Rc_TxControl14A(self) -> Registers_Rc_TxControl14A:
        """
        Specifies settings of the TxControl register for 14A.
        """
        return Registers_Rc_TxControl14A(self)
    @property
    def Registers_Rc_TxControl14B(self) -> Registers_Rc_TxControl14B:
        """
        Specifies settings of the TxControl register for 14B.
        """
        return Registers_Rc_TxControl14B(self)
    @property
    def Registers_Rc_TxControl15(self) -> Registers_Rc_TxControl15:
        """
        Specifies settings of the TxControl register for 15.
        """
        return Registers_Rc_TxControl15(self)
    @property
    def Registers_Rc_TxControlALL(self) -> Registers_Rc_TxControlALL:
        """
        Specifies settings of the TxControl register for ALL.
        """
        return Registers_Rc_TxControlALL(self)
    @property
    def Registers_Rc_TxControlVOLATILE(self) -> Registers_Rc_TxControlVOLATILE:
        """
        Specifies settings of the TxControl register for VOLATILE.
        """
        return Registers_Rc_TxControlVOLATILE(self)
    @property
    def Registers_Rc_CwConductance14A848(self) -> Registers_Rc_CwConductance14A848:
        """
        Specifies settings of the CwConductance register for 14A_848.
        """
        return Registers_Rc_CwConductance14A848(self)
    @property
    def Registers_Rc_CwConductance14A424(self) -> Registers_Rc_CwConductance14A424:
        """
        Specifies settings of the CwConductance register for 14A_424.
        """
        return Registers_Rc_CwConductance14A424(self)
    @property
    def Registers_Rc_CwConductance14A212(self) -> Registers_Rc_CwConductance14A212:
        """
        Specifies settings of the CwConductance register for 14A_212.
        """
        return Registers_Rc_CwConductance14A212(self)
    @property
    def Registers_Rc_CwConductance14A106(self) -> Registers_Rc_CwConductance14A106:
        """
        Specifies settings of the CwConductance register for 14A_106.
        """
        return Registers_Rc_CwConductance14A106(self)
    @property
    def Registers_Rc_CwConductance14B848(self) -> Registers_Rc_CwConductance14B848:
        """
        Specifies settings of the CwConductance register for 14B_848.
        """
        return Registers_Rc_CwConductance14B848(self)
    @property
    def Registers_Rc_CwConductance14B424(self) -> Registers_Rc_CwConductance14B424:
        """
        Specifies settings of the CwConductance register for 14B_424.
        """
        return Registers_Rc_CwConductance14B424(self)
    @property
    def Registers_Rc_CwConductance14B212(self) -> Registers_Rc_CwConductance14B212:
        """
        Specifies settings of the CwConductance register for 14B_212.
        """
        return Registers_Rc_CwConductance14B212(self)
    @property
    def Registers_Rc_CwConductance14B106(self) -> Registers_Rc_CwConductance14B106:
        """
        Specifies settings of the CwConductance register for 14B_106.
        """
        return Registers_Rc_CwConductance14B106(self)
    @property
    def Registers_Rc_CwConductance15Standard(self) -> Registers_Rc_CwConductance15Standard:
        """
        Specifies settings of the CwConductance register for 15Standard.
        """
        return Registers_Rc_CwConductance15Standard(self)
    @property
    def Registers_Rc_CwConductance15Fast(self) -> Registers_Rc_CwConductance15Fast:
        """
        Specifies settings of the CwConductance register for 15Fast.
        """
        return Registers_Rc_CwConductance15Fast(self)
    @property
    def Registers_Rc_CwConductance14A(self) -> Registers_Rc_CwConductance14A:
        """
        Specifies settings of the CwConductance register for 14A.
        """
        return Registers_Rc_CwConductance14A(self)
    @property
    def Registers_Rc_CwConductance14B(self) -> Registers_Rc_CwConductance14B:
        """
        Specifies settings of the CwConductance register for 14B.
        """
        return Registers_Rc_CwConductance14B(self)
    @property
    def Registers_Rc_CwConductance15(self) -> Registers_Rc_CwConductance15:
        """
        Specifies settings of the CwConductance register for 15.
        """
        return Registers_Rc_CwConductance15(self)
    @property
    def Registers_Rc_CwConductanceALL(self) -> Registers_Rc_CwConductanceALL:
        """
        Specifies settings of the CwConductance register for ALL.
        """
        return Registers_Rc_CwConductanceALL(self)
    @property
    def Registers_Rc_CwConductanceVOLATILE(self) -> Registers_Rc_CwConductanceVOLATILE:
        """
        Specifies settings of the CwConductance register for VOLATILE.
        """
        return Registers_Rc_CwConductanceVOLATILE(self)
    @property
    def Registers_Rc_ModConductance14A848(self) -> Registers_Rc_ModConductance14A848:
        """
        Specifies settings of the ModConductance register for 14A_848.
        """
        return Registers_Rc_ModConductance14A848(self)
    @property
    def Registers_Rc_ModConductance14A424(self) -> Registers_Rc_ModConductance14A424:
        """
        Specifies settings of the ModConductance register for 14A_424.
        """
        return Registers_Rc_ModConductance14A424(self)
    @property
    def Registers_Rc_ModConductance14A212(self) -> Registers_Rc_ModConductance14A212:
        """
        Specifies settings of the ModConductance register for 14A_212.
        """
        return Registers_Rc_ModConductance14A212(self)
    @property
    def Registers_Rc_ModConductance14A106(self) -> Registers_Rc_ModConductance14A106:
        """
        Specifies settings of the ModConductance register for 14A_106.
        """
        return Registers_Rc_ModConductance14A106(self)
    @property
    def Registers_Rc_ModConductance14B848(self) -> Registers_Rc_ModConductance14B848:
        """
        Specifies settings of the ModConductance register for 14B_848.
        """
        return Registers_Rc_ModConductance14B848(self)
    @property
    def Registers_Rc_ModConductance14B424(self) -> Registers_Rc_ModConductance14B424:
        """
        Specifies settings of the ModConductance register for 14B_424.
        """
        return Registers_Rc_ModConductance14B424(self)
    @property
    def Registers_Rc_ModConductance14B212(self) -> Registers_Rc_ModConductance14B212:
        """
        Specifies settings of the ModConductance register for 14B_212.
        """
        return Registers_Rc_ModConductance14B212(self)
    @property
    def Registers_Rc_ModConductance14B106(self) -> Registers_Rc_ModConductance14B106:
        """
        Specifies settings of the ModConductance register for 14B_106.
        """
        return Registers_Rc_ModConductance14B106(self)
    @property
    def Registers_Rc_ModConductance15Standard(self) -> Registers_Rc_ModConductance15Standard:
        """
        Specifies settings of the ModConductance register for 15Standard.
        """
        return Registers_Rc_ModConductance15Standard(self)
    @property
    def Registers_Rc_ModConductance15Fast(self) -> Registers_Rc_ModConductance15Fast:
        """
        Specifies settings of the ModConductance register for 15Fast.
        """
        return Registers_Rc_ModConductance15Fast(self)
    @property
    def Registers_Rc_ModConductance14A(self) -> Registers_Rc_ModConductance14A:
        """
        Specifies settings of the ModConductance register for 14A.
        """
        return Registers_Rc_ModConductance14A(self)
    @property
    def Registers_Rc_ModConductance14B(self) -> Registers_Rc_ModConductance14B:
        """
        Specifies settings of the ModConductance register for 14B.
        """
        return Registers_Rc_ModConductance14B(self)
    @property
    def Registers_Rc_ModConductance15(self) -> Registers_Rc_ModConductance15:
        """
        Specifies settings of the ModConductance register for 15.
        """
        return Registers_Rc_ModConductance15(self)
    @property
    def Registers_Rc_ModConductanceALL(self) -> Registers_Rc_ModConductanceALL:
        """
        Specifies settings of the ModConductance register for ALL.
        """
        return Registers_Rc_ModConductanceALL(self)
    @property
    def Registers_Rc_ModConductanceVOLATILE(self) -> Registers_Rc_ModConductanceVOLATILE:
        """
        Specifies settings of the ModConductance register for VOLATILE.
        """
        return Registers_Rc_ModConductanceVOLATILE(self)
    @property
    def Registers_Rc_ModWidth14A848(self) -> Registers_Rc_ModWidth14A848:
        """
        Specifies settings of the ModWidth register for 14A_848.
        """
        return Registers_Rc_ModWidth14A848(self)
    @property
    def Registers_Rc_ModWidth14A424(self) -> Registers_Rc_ModWidth14A424:
        """
        Specifies settings of the ModWidth register for 14A_424.
        """
        return Registers_Rc_ModWidth14A424(self)
    @property
    def Registers_Rc_ModWidth14A212(self) -> Registers_Rc_ModWidth14A212:
        """
        Specifies settings of the ModWidth register for 14A_212.
        """
        return Registers_Rc_ModWidth14A212(self)
    @property
    def Registers_Rc_ModWidth14A106(self) -> Registers_Rc_ModWidth14A106:
        """
        Specifies settings of the ModWidth register for 14A_106.
        """
        return Registers_Rc_ModWidth14A106(self)
    @property
    def Registers_Rc_ModWidth14B848(self) -> Registers_Rc_ModWidth14B848:
        """
        Specifies settings of the ModWidth register for 14B_848.
        """
        return Registers_Rc_ModWidth14B848(self)
    @property
    def Registers_Rc_ModWidth14B424(self) -> Registers_Rc_ModWidth14B424:
        """
        Specifies settings of the ModWidth register for 14B_424.
        """
        return Registers_Rc_ModWidth14B424(self)
    @property
    def Registers_Rc_ModWidth14B212(self) -> Registers_Rc_ModWidth14B212:
        """
        Specifies settings of the ModWidth register for 14B_212.
        """
        return Registers_Rc_ModWidth14B212(self)
    @property
    def Registers_Rc_ModWidth14B106(self) -> Registers_Rc_ModWidth14B106:
        """
        Specifies settings of the ModWidth register for 14B_106.
        """
        return Registers_Rc_ModWidth14B106(self)
    @property
    def Registers_Rc_ModWidth15Standard(self) -> Registers_Rc_ModWidth15Standard:
        """
        Specifies settings of the ModWidth register for 15Standard.
        """
        return Registers_Rc_ModWidth15Standard(self)
    @property
    def Registers_Rc_ModWidth15Fast(self) -> Registers_Rc_ModWidth15Fast:
        """
        Specifies settings of the ModWidth register for 15Fast.
        """
        return Registers_Rc_ModWidth15Fast(self)
    @property
    def Registers_Rc_ModWidth14A(self) -> Registers_Rc_ModWidth14A:
        """
        Specifies settings of the ModWidth register for 14A.
        """
        return Registers_Rc_ModWidth14A(self)
    @property
    def Registers_Rc_ModWidth14B(self) -> Registers_Rc_ModWidth14B:
        """
        Specifies settings of the ModWidth register for 14B.
        """
        return Registers_Rc_ModWidth14B(self)
    @property
    def Registers_Rc_ModWidth15(self) -> Registers_Rc_ModWidth15:
        """
        Specifies settings of the ModWidth register for 15.
        """
        return Registers_Rc_ModWidth15(self)
    @property
    def Registers_Rc_ModWidthALL(self) -> Registers_Rc_ModWidthALL:
        """
        Specifies settings of the ModWidth register for ALL.
        """
        return Registers_Rc_ModWidthALL(self)
    @property
    def Registers_Rc_ModWidthVOLATILE(self) -> Registers_Rc_ModWidthVOLATILE:
        """
        Specifies settings of the ModWidth register for VOLATILE.
        """
        return Registers_Rc_ModWidthVOLATILE(self)
    @property
    def Registers_Rc_ModWidthSOF14A848(self) -> Registers_Rc_ModWidthSOF14A848:
        """
        Specifies settings of the ModWidthSOF register for 14A_848.
        """
        return Registers_Rc_ModWidthSOF14A848(self)
    @property
    def Registers_Rc_ModWidthSOF14A424(self) -> Registers_Rc_ModWidthSOF14A424:
        """
        Specifies settings of the ModWidthSOF register for 14A_424.
        """
        return Registers_Rc_ModWidthSOF14A424(self)
    @property
    def Registers_Rc_ModWidthSOF14A212(self) -> Registers_Rc_ModWidthSOF14A212:
        """
        Specifies settings of the ModWidthSOF register for 14A_212.
        """
        return Registers_Rc_ModWidthSOF14A212(self)
    @property
    def Registers_Rc_ModWidthSOF14A106(self) -> Registers_Rc_ModWidthSOF14A106:
        """
        Specifies settings of the ModWidthSOF register for 14A_106.
        """
        return Registers_Rc_ModWidthSOF14A106(self)
    @property
    def Registers_Rc_ModWidthSOF14B848(self) -> Registers_Rc_ModWidthSOF14B848:
        """
        Specifies settings of the ModWidthSOF register for 14B_848.
        """
        return Registers_Rc_ModWidthSOF14B848(self)
    @property
    def Registers_Rc_ModWidthSOF14B424(self) -> Registers_Rc_ModWidthSOF14B424:
        """
        Specifies settings of the ModWidthSOF register for 14B_424.
        """
        return Registers_Rc_ModWidthSOF14B424(self)
    @property
    def Registers_Rc_ModWidthSOF14B212(self) -> Registers_Rc_ModWidthSOF14B212:
        """
        Specifies settings of the ModWidthSOF register for 14B_212.
        """
        return Registers_Rc_ModWidthSOF14B212(self)
    @property
    def Registers_Rc_ModWidthSOF14B106(self) -> Registers_Rc_ModWidthSOF14B106:
        """
        Specifies settings of the ModWidthSOF register for 14B_106.
        """
        return Registers_Rc_ModWidthSOF14B106(self)
    @property
    def Registers_Rc_ModWidthSOF15Standard(self) -> Registers_Rc_ModWidthSOF15Standard:
        """
        Specifies settings of the ModWidthSOF register for 15Standard.
        """
        return Registers_Rc_ModWidthSOF15Standard(self)
    @property
    def Registers_Rc_ModWidthSOF15Fast(self) -> Registers_Rc_ModWidthSOF15Fast:
        """
        Specifies settings of the ModWidthSOF register for 15Fast.
        """
        return Registers_Rc_ModWidthSOF15Fast(self)
    @property
    def Registers_Rc_ModWidthSOF14A(self) -> Registers_Rc_ModWidthSOF14A:
        """
        Specifies settings of the ModWidthSOF register for 14A.
        """
        return Registers_Rc_ModWidthSOF14A(self)
    @property
    def Registers_Rc_ModWidthSOF14B(self) -> Registers_Rc_ModWidthSOF14B:
        """
        Specifies settings of the ModWidthSOF register for 14B.
        """
        return Registers_Rc_ModWidthSOF14B(self)
    @property
    def Registers_Rc_ModWidthSOF15(self) -> Registers_Rc_ModWidthSOF15:
        """
        Specifies settings of the ModWidthSOF register for 15.
        """
        return Registers_Rc_ModWidthSOF15(self)
    @property
    def Registers_Rc_ModWidthSOFALL(self) -> Registers_Rc_ModWidthSOFALL:
        """
        Specifies settings of the ModWidthSOF register for ALL.
        """
        return Registers_Rc_ModWidthSOFALL(self)
    @property
    def Registers_Rc_ModWidthSOFVOLATILE(self) -> Registers_Rc_ModWidthSOFVOLATILE:
        """
        Specifies settings of the ModWidthSOF register for VOLATILE.
        """
        return Registers_Rc_ModWidthSOFVOLATILE(self)
    @property
    def Registers_Rc_TypeBFraming14A848(self) -> Registers_Rc_TypeBFraming14A848:
        """
        Specifies settings of the TypeBFraming register for 14A_848.
        """
        return Registers_Rc_TypeBFraming14A848(self)
    @property
    def Registers_Rc_TypeBFraming14A424(self) -> Registers_Rc_TypeBFraming14A424:
        """
        Specifies settings of the TypeBFraming register for 14A_424.
        """
        return Registers_Rc_TypeBFraming14A424(self)
    @property
    def Registers_Rc_TypeBFraming14A212(self) -> Registers_Rc_TypeBFraming14A212:
        """
        Specifies settings of the TypeBFraming register for 14A_212.
        """
        return Registers_Rc_TypeBFraming14A212(self)
    @property
    def Registers_Rc_TypeBFraming14A106(self) -> Registers_Rc_TypeBFraming14A106:
        """
        Specifies settings of the TypeBFraming register for 14A_106.
        """
        return Registers_Rc_TypeBFraming14A106(self)
    @property
    def Registers_Rc_TypeBFraming14B848(self) -> Registers_Rc_TypeBFraming14B848:
        """
        Specifies settings of the TypeBFraming register for 14B_848.
        """
        return Registers_Rc_TypeBFraming14B848(self)
    @property
    def Registers_Rc_TypeBFraming14B424(self) -> Registers_Rc_TypeBFraming14B424:
        """
        Specifies settings of the TypeBFraming register for 14B_424.
        """
        return Registers_Rc_TypeBFraming14B424(self)
    @property
    def Registers_Rc_TypeBFraming14B212(self) -> Registers_Rc_TypeBFraming14B212:
        """
        Specifies settings of the TypeBFraming register for 14B_212.
        """
        return Registers_Rc_TypeBFraming14B212(self)
    @property
    def Registers_Rc_TypeBFraming14B106(self) -> Registers_Rc_TypeBFraming14B106:
        """
        Specifies settings of the TypeBFraming register for 14B_106.
        """
        return Registers_Rc_TypeBFraming14B106(self)
    @property
    def Registers_Rc_TypeBFraming15Standard(self) -> Registers_Rc_TypeBFraming15Standard:
        """
        Specifies settings of the TypeBFraming register for 15Standard.
        """
        return Registers_Rc_TypeBFraming15Standard(self)
    @property
    def Registers_Rc_TypeBFraming15Fast(self) -> Registers_Rc_TypeBFraming15Fast:
        """
        Specifies settings of the TypeBFraming register for 15Fast.
        """
        return Registers_Rc_TypeBFraming15Fast(self)
    @property
    def Registers_Rc_TypeBFraming14A(self) -> Registers_Rc_TypeBFraming14A:
        """
        Specifies settings of the TypeBFraming register for 14A.
        """
        return Registers_Rc_TypeBFraming14A(self)
    @property
    def Registers_Rc_TypeBFraming14B(self) -> Registers_Rc_TypeBFraming14B:
        """
        Specifies settings of the TypeBFraming register for 14B.
        """
        return Registers_Rc_TypeBFraming14B(self)
    @property
    def Registers_Rc_TypeBFraming15(self) -> Registers_Rc_TypeBFraming15:
        """
        Specifies settings of the TypeBFraming register for 15.
        """
        return Registers_Rc_TypeBFraming15(self)
    @property
    def Registers_Rc_TypeBFramingALL(self) -> Registers_Rc_TypeBFramingALL:
        """
        Specifies settings of the TypeBFraming register for ALL.
        """
        return Registers_Rc_TypeBFramingALL(self)
    @property
    def Registers_Rc_TypeBFramingVOLATILE(self) -> Registers_Rc_TypeBFramingVOLATILE:
        """
        Specifies settings of the TypeBFraming register for VOLATILE.
        """
        return Registers_Rc_TypeBFramingVOLATILE(self)
    @property
    def Registers_Rc_RxControl114A848(self) -> Registers_Rc_RxControl114A848:
        """
        Specifies settings of the RxControl1 register for 14A_848.
        """
        return Registers_Rc_RxControl114A848(self)
    @property
    def Registers_Rc_RxControl114A424(self) -> Registers_Rc_RxControl114A424:
        """
        Specifies settings of the RxControl1 register for 14A_424.
        """
        return Registers_Rc_RxControl114A424(self)
    @property
    def Registers_Rc_RxControl114A212(self) -> Registers_Rc_RxControl114A212:
        """
        Specifies settings of the RxControl1 register for 14A_212.
        """
        return Registers_Rc_RxControl114A212(self)
    @property
    def Registers_Rc_RxControl114A106(self) -> Registers_Rc_RxControl114A106:
        """
        Specifies settings of the RxControl1 register for 14A_106.
        """
        return Registers_Rc_RxControl114A106(self)
    @property
    def Registers_Rc_RxControl114B848(self) -> Registers_Rc_RxControl114B848:
        """
        Specifies settings of the RxControl1 register for 14B_848.
        """
        return Registers_Rc_RxControl114B848(self)
    @property
    def Registers_Rc_RxControl114B424(self) -> Registers_Rc_RxControl114B424:
        """
        Specifies settings of the RxControl1 register for 14B_424.
        """
        return Registers_Rc_RxControl114B424(self)
    @property
    def Registers_Rc_RxControl114B212(self) -> Registers_Rc_RxControl114B212:
        """
        Specifies settings of the RxControl1 register for 14B_212.
        """
        return Registers_Rc_RxControl114B212(self)
    @property
    def Registers_Rc_RxControl114B106(self) -> Registers_Rc_RxControl114B106:
        """
        Specifies settings of the RxControl1 register for 14B_106.
        """
        return Registers_Rc_RxControl114B106(self)
    @property
    def Registers_Rc_RxControl115Standard(self) -> Registers_Rc_RxControl115Standard:
        """
        Specifies settings of the RxControl1 register for 15Standard.
        """
        return Registers_Rc_RxControl115Standard(self)
    @property
    def Registers_Rc_RxControl115Fast(self) -> Registers_Rc_RxControl115Fast:
        """
        Specifies settings of the RxControl1 register for 15Fast.
        """
        return Registers_Rc_RxControl115Fast(self)
    @property
    def Registers_Rc_RxControl114A(self) -> Registers_Rc_RxControl114A:
        """
        Specifies settings of the RxControl1 register for 14A.
        """
        return Registers_Rc_RxControl114A(self)
    @property
    def Registers_Rc_RxControl114B(self) -> Registers_Rc_RxControl114B:
        """
        Specifies settings of the RxControl1 register for 14B.
        """
        return Registers_Rc_RxControl114B(self)
    @property
    def Registers_Rc_RxControl115(self) -> Registers_Rc_RxControl115:
        """
        Specifies settings of the RxControl1 register for 15.
        """
        return Registers_Rc_RxControl115(self)
    @property
    def Registers_Rc_RxControl1ALL(self) -> Registers_Rc_RxControl1ALL:
        """
        Specifies settings of the RxControl1 register for ALL.
        """
        return Registers_Rc_RxControl1ALL(self)
    @property
    def Registers_Rc_RxControl1VOLATILE(self) -> Registers_Rc_RxControl1VOLATILE:
        """
        Specifies settings of the RxControl1 register for VOLATILE.
        """
        return Registers_Rc_RxControl1VOLATILE(self)
    @property
    def Registers_Rc_BitPhase14A848(self) -> Registers_Rc_BitPhase14A848:
        """
        Specifies settings of the BitPhase register for 14A_848.
        """
        return Registers_Rc_BitPhase14A848(self)
    @property
    def Registers_Rc_BitPhase14A424(self) -> Registers_Rc_BitPhase14A424:
        """
        Specifies settings of the BitPhase register for 14A_424.
        """
        return Registers_Rc_BitPhase14A424(self)
    @property
    def Registers_Rc_BitPhase14A212(self) -> Registers_Rc_BitPhase14A212:
        """
        Specifies settings of the BitPhase register for 14A_212.
        """
        return Registers_Rc_BitPhase14A212(self)
    @property
    def Registers_Rc_BitPhase14A106(self) -> Registers_Rc_BitPhase14A106:
        """
        Specifies settings of the BitPhase register for 14A_106.
        """
        return Registers_Rc_BitPhase14A106(self)
    @property
    def Registers_Rc_BitPhase14B848(self) -> Registers_Rc_BitPhase14B848:
        """
        Specifies settings of the BitPhase register for 14B_848.
        """
        return Registers_Rc_BitPhase14B848(self)
    @property
    def Registers_Rc_BitPhase14B424(self) -> Registers_Rc_BitPhase14B424:
        """
        Specifies settings of the BitPhase register for 14B_424.
        """
        return Registers_Rc_BitPhase14B424(self)
    @property
    def Registers_Rc_BitPhase14B212(self) -> Registers_Rc_BitPhase14B212:
        """
        Specifies settings of the BitPhase register for 14B_212.
        """
        return Registers_Rc_BitPhase14B212(self)
    @property
    def Registers_Rc_BitPhase14B106(self) -> Registers_Rc_BitPhase14B106:
        """
        Specifies settings of the BitPhase register for 14B_106.
        """
        return Registers_Rc_BitPhase14B106(self)
    @property
    def Registers_Rc_BitPhase15Standard(self) -> Registers_Rc_BitPhase15Standard:
        """
        Specifies settings of the BitPhase register for 15Standard.
        """
        return Registers_Rc_BitPhase15Standard(self)
    @property
    def Registers_Rc_BitPhase15Fast(self) -> Registers_Rc_BitPhase15Fast:
        """
        Specifies settings of the BitPhase register for 15Fast.
        """
        return Registers_Rc_BitPhase15Fast(self)
    @property
    def Registers_Rc_BitPhase14A(self) -> Registers_Rc_BitPhase14A:
        """
        Specifies settings of the BitPhase register for 14A.
        """
        return Registers_Rc_BitPhase14A(self)
    @property
    def Registers_Rc_BitPhase14B(self) -> Registers_Rc_BitPhase14B:
        """
        Specifies settings of the BitPhase register for 14B.
        """
        return Registers_Rc_BitPhase14B(self)
    @property
    def Registers_Rc_BitPhase15(self) -> Registers_Rc_BitPhase15:
        """
        Specifies settings of the BitPhase register for 15.
        """
        return Registers_Rc_BitPhase15(self)
    @property
    def Registers_Rc_BitPhaseALL(self) -> Registers_Rc_BitPhaseALL:
        """
        Specifies settings of the BitPhase register for ALL.
        """
        return Registers_Rc_BitPhaseALL(self)
    @property
    def Registers_Rc_BitPhaseVOLATILE(self) -> Registers_Rc_BitPhaseVOLATILE:
        """
        Specifies settings of the BitPhase register for VOLATILE.
        """
        return Registers_Rc_BitPhaseVOLATILE(self)
    @property
    def Registers_Rc_RxThreshold14A848(self) -> Registers_Rc_RxThreshold14A848:
        """
        Specifies settings of the RxThreshold register for 14A_848.
        """
        return Registers_Rc_RxThreshold14A848(self)
    @property
    def Registers_Rc_RxThreshold14A424(self) -> Registers_Rc_RxThreshold14A424:
        """
        Specifies settings of the RxThreshold register for 14A_424.
        """
        return Registers_Rc_RxThreshold14A424(self)
    @property
    def Registers_Rc_RxThreshold14A212(self) -> Registers_Rc_RxThreshold14A212:
        """
        Specifies settings of the RxThreshold register for 14A_212.
        """
        return Registers_Rc_RxThreshold14A212(self)
    @property
    def Registers_Rc_RxThreshold14A106(self) -> Registers_Rc_RxThreshold14A106:
        """
        Specifies settings of the RxThreshold register for 14A_106.
        """
        return Registers_Rc_RxThreshold14A106(self)
    @property
    def Registers_Rc_RxThreshold14B848(self) -> Registers_Rc_RxThreshold14B848:
        """
        Specifies settings of the RxThreshold register for 14B_848.
        """
        return Registers_Rc_RxThreshold14B848(self)
    @property
    def Registers_Rc_RxThreshold14B424(self) -> Registers_Rc_RxThreshold14B424:
        """
        Specifies settings of the RxThreshold register for 14B_424.
        """
        return Registers_Rc_RxThreshold14B424(self)
    @property
    def Registers_Rc_RxThreshold14B212(self) -> Registers_Rc_RxThreshold14B212:
        """
        Specifies settings of the RxThreshold register for 14B_212.
        """
        return Registers_Rc_RxThreshold14B212(self)
    @property
    def Registers_Rc_RxThreshold14B106(self) -> Registers_Rc_RxThreshold14B106:
        """
        Specifies settings of the RxThreshold register for 14B_106.
        """
        return Registers_Rc_RxThreshold14B106(self)
    @property
    def Registers_Rc_RxThreshold15Standard(self) -> Registers_Rc_RxThreshold15Standard:
        """
        Specifies settings of the RxThreshold register for 15Standard.
        """
        return Registers_Rc_RxThreshold15Standard(self)
    @property
    def Registers_Rc_RxThreshold15Fast(self) -> Registers_Rc_RxThreshold15Fast:
        """
        Specifies settings of the RxThreshold register for 15Fast.
        """
        return Registers_Rc_RxThreshold15Fast(self)
    @property
    def Registers_Rc_RxThreshold14A(self) -> Registers_Rc_RxThreshold14A:
        """
        Specifies settings of the RxThreshold register for 14A.
        """
        return Registers_Rc_RxThreshold14A(self)
    @property
    def Registers_Rc_RxThreshold14B(self) -> Registers_Rc_RxThreshold14B:
        """
        Specifies settings of the RxThreshold register for 14B.
        """
        return Registers_Rc_RxThreshold14B(self)
    @property
    def Registers_Rc_RxThreshold15(self) -> Registers_Rc_RxThreshold15:
        """
        Specifies settings of the RxThreshold register for 15.
        """
        return Registers_Rc_RxThreshold15(self)
    @property
    def Registers_Rc_RxThresholdALL(self) -> Registers_Rc_RxThresholdALL:
        """
        Specifies settings of the RxThreshold register for ALL.
        """
        return Registers_Rc_RxThresholdALL(self)
    @property
    def Registers_Rc_RxThresholdVOLATILE(self) -> Registers_Rc_RxThresholdVOLATILE:
        """
        Specifies settings of the RxThreshold register for VOLATILE.
        """
        return Registers_Rc_RxThresholdVOLATILE(self)
    @property
    def Registers_Rc_BPSKDemControl14A848(self) -> Registers_Rc_BPSKDemControl14A848:
        """
        Specifies settings of the BPSKDemControl register for 14A_848.
        """
        return Registers_Rc_BPSKDemControl14A848(self)
    @property
    def Registers_Rc_BPSKDemControl14A424(self) -> Registers_Rc_BPSKDemControl14A424:
        """
        Specifies settings of the BPSKDemControl register for 14A_424.
        """
        return Registers_Rc_BPSKDemControl14A424(self)
    @property
    def Registers_Rc_BPSKDemControl14A212(self) -> Registers_Rc_BPSKDemControl14A212:
        """
        Specifies settings of the BPSKDemControl register for 14A_212.
        """
        return Registers_Rc_BPSKDemControl14A212(self)
    @property
    def Registers_Rc_BPSKDemControl14A106(self) -> Registers_Rc_BPSKDemControl14A106:
        """
        Specifies settings of the BPSKDemControl register for 14A_106.
        """
        return Registers_Rc_BPSKDemControl14A106(self)
    @property
    def Registers_Rc_BPSKDemControl14B848(self) -> Registers_Rc_BPSKDemControl14B848:
        """
        Specifies settings of the BPSKDemControl register for 14B_848.
        """
        return Registers_Rc_BPSKDemControl14B848(self)
    @property
    def Registers_Rc_BPSKDemControl14B424(self) -> Registers_Rc_BPSKDemControl14B424:
        """
        Specifies settings of the BPSKDemControl register for 14B_424.
        """
        return Registers_Rc_BPSKDemControl14B424(self)
    @property
    def Registers_Rc_BPSKDemControl14B212(self) -> Registers_Rc_BPSKDemControl14B212:
        """
        Specifies settings of the BPSKDemControl register for 14B_212.
        """
        return Registers_Rc_BPSKDemControl14B212(self)
    @property
    def Registers_Rc_BPSKDemControl14B106(self) -> Registers_Rc_BPSKDemControl14B106:
        """
        Specifies settings of the BPSKDemControl register for 14B_106.
        """
        return Registers_Rc_BPSKDemControl14B106(self)
    @property
    def Registers_Rc_BPSKDemControl15Standard(self) -> Registers_Rc_BPSKDemControl15Standard:
        """
        Specifies settings of the BPSKDemControl register for 15Standard.
        """
        return Registers_Rc_BPSKDemControl15Standard(self)
    @property
    def Registers_Rc_BPSKDemControl15Fast(self) -> Registers_Rc_BPSKDemControl15Fast:
        """
        Specifies settings of the BPSKDemControl register for 15Fast.
        """
        return Registers_Rc_BPSKDemControl15Fast(self)
    @property
    def Registers_Rc_BPSKDemControl14A(self) -> Registers_Rc_BPSKDemControl14A:
        """
        Specifies settings of the BPSKDemControl register for 14A.
        """
        return Registers_Rc_BPSKDemControl14A(self)
    @property
    def Registers_Rc_BPSKDemControl14B(self) -> Registers_Rc_BPSKDemControl14B:
        """
        Specifies settings of the BPSKDemControl register for 14B.
        """
        return Registers_Rc_BPSKDemControl14B(self)
    @property
    def Registers_Rc_BPSKDemControl15(self) -> Registers_Rc_BPSKDemControl15:
        """
        Specifies settings of the BPSKDemControl register for 15.
        """
        return Registers_Rc_BPSKDemControl15(self)
    @property
    def Registers_Rc_BPSKDemControlALL(self) -> Registers_Rc_BPSKDemControlALL:
        """
        Specifies settings of the BPSKDemControl register for ALL.
        """
        return Registers_Rc_BPSKDemControlALL(self)
    @property
    def Registers_Rc_BPSKDemControlVOLATILE(self) -> Registers_Rc_BPSKDemControlVOLATILE:
        """
        Specifies settings of the BPSKDemControl register for VOLATILE.
        """
        return Registers_Rc_BPSKDemControlVOLATILE(self)
    @property
    def Registers_Rc_RxWait14A848(self) -> Registers_Rc_RxWait14A848:
        """
        Specifies settings of the RxWait register for 14A_848.
        """
        return Registers_Rc_RxWait14A848(self)
    @property
    def Registers_Rc_RxWait14A424(self) -> Registers_Rc_RxWait14A424:
        """
        Specifies settings of the RxWait register for 14A_424.
        """
        return Registers_Rc_RxWait14A424(self)
    @property
    def Registers_Rc_RxWait14A212(self) -> Registers_Rc_RxWait14A212:
        """
        Specifies settings of the RxWait register for 14A_212.
        """
        return Registers_Rc_RxWait14A212(self)
    @property
    def Registers_Rc_RxWait14A106(self) -> Registers_Rc_RxWait14A106:
        """
        Specifies settings of the RxWait register for 14A_106.
        """
        return Registers_Rc_RxWait14A106(self)
    @property
    def Registers_Rc_RxWait14B848(self) -> Registers_Rc_RxWait14B848:
        """
        Specifies settings of the RxWait register for 14B_848.
        """
        return Registers_Rc_RxWait14B848(self)
    @property
    def Registers_Rc_RxWait14B424(self) -> Registers_Rc_RxWait14B424:
        """
        Specifies settings of the RxWait register for 14B_424.
        """
        return Registers_Rc_RxWait14B424(self)
    @property
    def Registers_Rc_RxWait14B212(self) -> Registers_Rc_RxWait14B212:
        """
        Specifies settings of the RxWait register for 14B_212.
        """
        return Registers_Rc_RxWait14B212(self)
    @property
    def Registers_Rc_RxWait14B106(self) -> Registers_Rc_RxWait14B106:
        """
        Specifies settings of the RxWait register for 14B_106.
        """
        return Registers_Rc_RxWait14B106(self)
    @property
    def Registers_Rc_RxWait15Standard(self) -> Registers_Rc_RxWait15Standard:
        """
        Specifies settings of the RxWait register for 15Standard.
        """
        return Registers_Rc_RxWait15Standard(self)
    @property
    def Registers_Rc_RxWait15Fast(self) -> Registers_Rc_RxWait15Fast:
        """
        Specifies settings of the RxWait register for 15Fast.
        """
        return Registers_Rc_RxWait15Fast(self)
    @property
    def Registers_Rc_RxWait14A(self) -> Registers_Rc_RxWait14A:
        """
        Specifies settings of the RxWait register for 14A.
        """
        return Registers_Rc_RxWait14A(self)
    @property
    def Registers_Rc_RxWait14B(self) -> Registers_Rc_RxWait14B:
        """
        Specifies settings of the RxWait register for 14B.
        """
        return Registers_Rc_RxWait14B(self)
    @property
    def Registers_Rc_RxWait15(self) -> Registers_Rc_RxWait15:
        """
        Specifies settings of the RxWait register for 15.
        """
        return Registers_Rc_RxWait15(self)
    @property
    def Registers_Rc_RxWaitALL(self) -> Registers_Rc_RxWaitALL:
        """
        Specifies settings of the RxWait register for ALL.
        """
        return Registers_Rc_RxWaitALL(self)
    @property
    def Registers_Rc_RxWaitVOLATILE(self) -> Registers_Rc_RxWaitVOLATILE:
        """
        Specifies settings of the RxWait register for VOLATILE.
        """
        return Registers_Rc_RxWaitVOLATILE(self)
    @property
    def Registers_Pn(self) -> Registers_Pn:
        """
        This value contains HF Settings (Register Settings) of the PN512 reader chip.
        """
        return Registers_Pn(self)
    @property
    def Registers_Pn_TxMode14A848(self) -> Registers_Pn_TxMode14A848:
        """
        Specifies settings of the TxMode register for 14A_848.
        """
        return Registers_Pn_TxMode14A848(self)
    @property
    def Registers_Pn_TxMode14A424(self) -> Registers_Pn_TxMode14A424:
        """
        Specifies settings of the TxMode register for 14A_424.
        """
        return Registers_Pn_TxMode14A424(self)
    @property
    def Registers_Pn_TxMode14A212(self) -> Registers_Pn_TxMode14A212:
        """
        Specifies settings of the TxMode register for 14A_212.
        """
        return Registers_Pn_TxMode14A212(self)
    @property
    def Registers_Pn_TxMode14A106(self) -> Registers_Pn_TxMode14A106:
        """
        Specifies settings of the TxMode register for 14A_106.
        """
        return Registers_Pn_TxMode14A106(self)
    @property
    def Registers_Pn_TxMode14B848(self) -> Registers_Pn_TxMode14B848:
        """
        Specifies settings of the TxMode register for 14B_848.
        """
        return Registers_Pn_TxMode14B848(self)
    @property
    def Registers_Pn_TxMode14B424(self) -> Registers_Pn_TxMode14B424:
        """
        Specifies settings of the TxMode register for 14B_424.
        """
        return Registers_Pn_TxMode14B424(self)
    @property
    def Registers_Pn_TxMode14B212(self) -> Registers_Pn_TxMode14B212:
        """
        Specifies settings of the TxMode register for 14B_212.
        """
        return Registers_Pn_TxMode14B212(self)
    @property
    def Registers_Pn_TxMode14B106(self) -> Registers_Pn_TxMode14B106:
        """
        Specifies settings of the TxMode register for 14B_106.
        """
        return Registers_Pn_TxMode14B106(self)
    @property
    def Registers_Pn_TxMode14A(self) -> Registers_Pn_TxMode14A:
        """
        Specifies settings of the TxMode register for 14A.
        """
        return Registers_Pn_TxMode14A(self)
    @property
    def Registers_Pn_TxMode14B(self) -> Registers_Pn_TxMode14B:
        """
        Specifies settings of the TxMode register for 14B.
        """
        return Registers_Pn_TxMode14B(self)
    @property
    def Registers_Pn_TxModeALL(self) -> Registers_Pn_TxModeALL:
        """
        Specifies settings of the TxMode register for ALL.
        """
        return Registers_Pn_TxModeALL(self)
    @property
    def Registers_Pn_TxModeVOLATILE(self) -> Registers_Pn_TxModeVOLATILE:
        """
        Specifies settings of the TxMode register for VOLATILE.
        """
        return Registers_Pn_TxModeVOLATILE(self)
    @property
    def Registers_Pn_RxMode14A848(self) -> Registers_Pn_RxMode14A848:
        """
        Specifies settings of the RxMode register for 14A_848.
        """
        return Registers_Pn_RxMode14A848(self)
    @property
    def Registers_Pn_RxMode14A424(self) -> Registers_Pn_RxMode14A424:
        """
        Specifies settings of the RxMode register for 14A_424.
        """
        return Registers_Pn_RxMode14A424(self)
    @property
    def Registers_Pn_RxMode14A212(self) -> Registers_Pn_RxMode14A212:
        """
        Specifies settings of the RxMode register for 14A_212.
        """
        return Registers_Pn_RxMode14A212(self)
    @property
    def Registers_Pn_RxMode14A106(self) -> Registers_Pn_RxMode14A106:
        """
        Specifies settings of the RxMode register for 14A_106.
        """
        return Registers_Pn_RxMode14A106(self)
    @property
    def Registers_Pn_RxMode14B848(self) -> Registers_Pn_RxMode14B848:
        """
        Specifies settings of the RxMode register for 14B_848.
        """
        return Registers_Pn_RxMode14B848(self)
    @property
    def Registers_Pn_RxMode14B424(self) -> Registers_Pn_RxMode14B424:
        """
        Specifies settings of the RxMode register for 14B_424.
        """
        return Registers_Pn_RxMode14B424(self)
    @property
    def Registers_Pn_RxMode14B212(self) -> Registers_Pn_RxMode14B212:
        """
        Specifies settings of the RxMode register for 14B_212.
        """
        return Registers_Pn_RxMode14B212(self)
    @property
    def Registers_Pn_RxMode14B106(self) -> Registers_Pn_RxMode14B106:
        """
        Specifies settings of the RxMode register for 14B_106.
        """
        return Registers_Pn_RxMode14B106(self)
    @property
    def Registers_Pn_RxMode14A(self) -> Registers_Pn_RxMode14A:
        """
        Specifies settings of the RxMode register for 14A.
        """
        return Registers_Pn_RxMode14A(self)
    @property
    def Registers_Pn_RxMode14B(self) -> Registers_Pn_RxMode14B:
        """
        Specifies settings of the RxMode register for 14B.
        """
        return Registers_Pn_RxMode14B(self)
    @property
    def Registers_Pn_RxModeALL(self) -> Registers_Pn_RxModeALL:
        """
        Specifies settings of the RxMode register for ALL.
        """
        return Registers_Pn_RxModeALL(self)
    @property
    def Registers_Pn_RxModeVOLATILE(self) -> Registers_Pn_RxModeVOLATILE:
        """
        Specifies settings of the RxMode register for VOLATILE.
        """
        return Registers_Pn_RxModeVOLATILE(self)
    @property
    def Registers_Pn_RxSel14A848(self) -> Registers_Pn_RxSel14A848:
        """
        Specifies settings of the RxSel register for 14A_848.
        """
        return Registers_Pn_RxSel14A848(self)
    @property
    def Registers_Pn_RxSel14A424(self) -> Registers_Pn_RxSel14A424:
        """
        Specifies settings of the RxSel register for 14A_424.
        """
        return Registers_Pn_RxSel14A424(self)
    @property
    def Registers_Pn_RxSel14A212(self) -> Registers_Pn_RxSel14A212:
        """
        Specifies settings of the RxSel register for 14A_212.
        """
        return Registers_Pn_RxSel14A212(self)
    @property
    def Registers_Pn_RxSel14A106(self) -> Registers_Pn_RxSel14A106:
        """
        Specifies settings of the RxSel register for 14A_106.
        """
        return Registers_Pn_RxSel14A106(self)
    @property
    def Registers_Pn_RxSel14B848(self) -> Registers_Pn_RxSel14B848:
        """
        Specifies settings of the RxSel register for 14B_848.
        """
        return Registers_Pn_RxSel14B848(self)
    @property
    def Registers_Pn_RxSel14B424(self) -> Registers_Pn_RxSel14B424:
        """
        Specifies settings of the RxSel register for 14B_424.
        """
        return Registers_Pn_RxSel14B424(self)
    @property
    def Registers_Pn_RxSel14B212(self) -> Registers_Pn_RxSel14B212:
        """
        Specifies settings of the RxSel register for 14B_212.
        """
        return Registers_Pn_RxSel14B212(self)
    @property
    def Registers_Pn_RxSel14B106(self) -> Registers_Pn_RxSel14B106:
        """
        Specifies settings of the RxSel register for 14B_106.
        """
        return Registers_Pn_RxSel14B106(self)
    @property
    def Registers_Pn_RxSel14A(self) -> Registers_Pn_RxSel14A:
        """
        Specifies settings of the RxSel register for 14A.
        """
        return Registers_Pn_RxSel14A(self)
    @property
    def Registers_Pn_RxSel14B(self) -> Registers_Pn_RxSel14B:
        """
        Specifies settings of the RxSel register for 14B.
        """
        return Registers_Pn_RxSel14B(self)
    @property
    def Registers_Pn_RxSelALL(self) -> Registers_Pn_RxSelALL:
        """
        Specifies settings of the RxSel register for ALL.
        """
        return Registers_Pn_RxSelALL(self)
    @property
    def Registers_Pn_RxSelVOLATILE(self) -> Registers_Pn_RxSelVOLATILE:
        """
        Specifies settings of the RxSel register for VOLATILE.
        """
        return Registers_Pn_RxSelVOLATILE(self)
    @property
    def Registers_Pn_RxThreshold14A848(self) -> Registers_Pn_RxThreshold14A848:
        """
        Specifies settings of the RxThreshold register for 14A_848.
        """
        return Registers_Pn_RxThreshold14A848(self)
    @property
    def Registers_Pn_RxThreshold14A424(self) -> Registers_Pn_RxThreshold14A424:
        """
        Specifies settings of the RxThreshold register for 14A_424.
        """
        return Registers_Pn_RxThreshold14A424(self)
    @property
    def Registers_Pn_RxThreshold14A212(self) -> Registers_Pn_RxThreshold14A212:
        """
        Specifies settings of the RxThreshold register for 14A_212.
        """
        return Registers_Pn_RxThreshold14A212(self)
    @property
    def Registers_Pn_RxThreshold14A106(self) -> Registers_Pn_RxThreshold14A106:
        """
        Specifies settings of the RxThreshold register for 14A_106.
        """
        return Registers_Pn_RxThreshold14A106(self)
    @property
    def Registers_Pn_RxThreshold14B848(self) -> Registers_Pn_RxThreshold14B848:
        """
        Specifies settings of the RxThreshold register for 14B_848.
        """
        return Registers_Pn_RxThreshold14B848(self)
    @property
    def Registers_Pn_RxThreshold14B424(self) -> Registers_Pn_RxThreshold14B424:
        """
        Specifies settings of the RxThreshold register for 14B_424.
        """
        return Registers_Pn_RxThreshold14B424(self)
    @property
    def Registers_Pn_RxThreshold14B212(self) -> Registers_Pn_RxThreshold14B212:
        """
        Specifies settings of the RxThreshold register for 14B_212.
        """
        return Registers_Pn_RxThreshold14B212(self)
    @property
    def Registers_Pn_RxThreshold14B106(self) -> Registers_Pn_RxThreshold14B106:
        """
        Specifies settings of the RxThreshold register for 14B_106.
        """
        return Registers_Pn_RxThreshold14B106(self)
    @property
    def Registers_Pn_RxThreshold14A(self) -> Registers_Pn_RxThreshold14A:
        """
        Specifies settings of the RxThreshold register for 14A.
        """
        return Registers_Pn_RxThreshold14A(self)
    @property
    def Registers_Pn_RxThreshold14B(self) -> Registers_Pn_RxThreshold14B:
        """
        Specifies settings of the RxThreshold register for 14B.
        """
        return Registers_Pn_RxThreshold14B(self)
    @property
    def Registers_Pn_RxThresholdALL(self) -> Registers_Pn_RxThresholdALL:
        """
        Specifies settings of the RxThreshold register for ALL.
        """
        return Registers_Pn_RxThresholdALL(self)
    @property
    def Registers_Pn_RxThresholdVOLATILE(self) -> Registers_Pn_RxThresholdVOLATILE:
        """
        Specifies settings of the RxThreshold register for VOLATILE.
        """
        return Registers_Pn_RxThresholdVOLATILE(self)
    @property
    def Registers_Pn_Demod14A848(self) -> Registers_Pn_Demod14A848:
        """
        Specifies settings of the Demod register for 14A_848.
        """
        return Registers_Pn_Demod14A848(self)
    @property
    def Registers_Pn_Demod14A424(self) -> Registers_Pn_Demod14A424:
        """
        Specifies settings of the Demod register for 14A_424.
        """
        return Registers_Pn_Demod14A424(self)
    @property
    def Registers_Pn_Demod14A212(self) -> Registers_Pn_Demod14A212:
        """
        Specifies settings of the Demod register for 14A_212.
        """
        return Registers_Pn_Demod14A212(self)
    @property
    def Registers_Pn_Demod14A106(self) -> Registers_Pn_Demod14A106:
        """
        Specifies settings of the Demod register for 14A_106.
        """
        return Registers_Pn_Demod14A106(self)
    @property
    def Registers_Pn_Demod14B848(self) -> Registers_Pn_Demod14B848:
        """
        Specifies settings of the Demod register for 14B_848.
        """
        return Registers_Pn_Demod14B848(self)
    @property
    def Registers_Pn_Demod14B424(self) -> Registers_Pn_Demod14B424:
        """
        Specifies settings of the Demod register for 14B_424.
        """
        return Registers_Pn_Demod14B424(self)
    @property
    def Registers_Pn_Demod14B212(self) -> Registers_Pn_Demod14B212:
        """
        Specifies settings of the Demod register for 14B_212.
        """
        return Registers_Pn_Demod14B212(self)
    @property
    def Registers_Pn_Demod14B106(self) -> Registers_Pn_Demod14B106:
        """
        Specifies settings of the Demod register for 14B_106.
        """
        return Registers_Pn_Demod14B106(self)
    @property
    def Registers_Pn_Demod14A(self) -> Registers_Pn_Demod14A:
        """
        Specifies settings of the Demod register for 14A.
        """
        return Registers_Pn_Demod14A(self)
    @property
    def Registers_Pn_Demod14B(self) -> Registers_Pn_Demod14B:
        """
        Specifies settings of the Demod register for 14B.
        """
        return Registers_Pn_Demod14B(self)
    @property
    def Registers_Pn_DemodALL(self) -> Registers_Pn_DemodALL:
        """
        Specifies settings of the Demod register for ALL.
        """
        return Registers_Pn_DemodALL(self)
    @property
    def Registers_Pn_DemodVOLATILE(self) -> Registers_Pn_DemodVOLATILE:
        """
        Specifies settings of the Demod register for VOLATILE.
        """
        return Registers_Pn_DemodVOLATILE(self)
    @property
    def Registers_Pn_MifNFC14A848(self) -> Registers_Pn_MifNFC14A848:
        """
        Specifies settings of the MifNFC register for 14A_848.
        """
        return Registers_Pn_MifNFC14A848(self)
    @property
    def Registers_Pn_MifNFC14A424(self) -> Registers_Pn_MifNFC14A424:
        """
        Specifies settings of the MifNFC register for 14A_424.
        """
        return Registers_Pn_MifNFC14A424(self)
    @property
    def Registers_Pn_MifNFC14A212(self) -> Registers_Pn_MifNFC14A212:
        """
        Specifies settings of the MifNFC register for 14A_212.
        """
        return Registers_Pn_MifNFC14A212(self)
    @property
    def Registers_Pn_MifNFC14A106(self) -> Registers_Pn_MifNFC14A106:
        """
        Specifies settings of the MifNFC register for 14A_106.
        """
        return Registers_Pn_MifNFC14A106(self)
    @property
    def Registers_Pn_MifNFC14B848(self) -> Registers_Pn_MifNFC14B848:
        """
        Specifies settings of the MifNFC register for 14B_848.
        """
        return Registers_Pn_MifNFC14B848(self)
    @property
    def Registers_Pn_MifNFC14B424(self) -> Registers_Pn_MifNFC14B424:
        """
        Specifies settings of the MifNFC register for 14B_424.
        """
        return Registers_Pn_MifNFC14B424(self)
    @property
    def Registers_Pn_MifNFC14B212(self) -> Registers_Pn_MifNFC14B212:
        """
        Specifies settings of the MifNFC register for 14B_212.
        """
        return Registers_Pn_MifNFC14B212(self)
    @property
    def Registers_Pn_MifNFC14B106(self) -> Registers_Pn_MifNFC14B106:
        """
        Specifies settings of the MifNFC register for 14B_106.
        """
        return Registers_Pn_MifNFC14B106(self)
    @property
    def Registers_Pn_MifNFC14A(self) -> Registers_Pn_MifNFC14A:
        """
        Specifies settings of the MifNFC register for 14A.
        """
        return Registers_Pn_MifNFC14A(self)
    @property
    def Registers_Pn_MifNFC14B(self) -> Registers_Pn_MifNFC14B:
        """
        Specifies settings of the MifNFC register for 14B.
        """
        return Registers_Pn_MifNFC14B(self)
    @property
    def Registers_Pn_MifNFCALL(self) -> Registers_Pn_MifNFCALL:
        """
        Specifies settings of the MifNFC register for ALL.
        """
        return Registers_Pn_MifNFCALL(self)
    @property
    def Registers_Pn_MifNFCVOLATILE(self) -> Registers_Pn_MifNFCVOLATILE:
        """
        Specifies settings of the MifNFC register for VOLATILE.
        """
        return Registers_Pn_MifNFCVOLATILE(self)
    @property
    def Registers_Pn_ManualRCV14A848(self) -> Registers_Pn_ManualRCV14A848:
        """
        Specifies settings of the ManualRCV register for 14A_848.
        """
        return Registers_Pn_ManualRCV14A848(self)
    @property
    def Registers_Pn_ManualRCV14A424(self) -> Registers_Pn_ManualRCV14A424:
        """
        Specifies settings of the ManualRCV register for 14A_424.
        """
        return Registers_Pn_ManualRCV14A424(self)
    @property
    def Registers_Pn_ManualRCV14A212(self) -> Registers_Pn_ManualRCV14A212:
        """
        Specifies settings of the ManualRCV register for 14A_212.
        """
        return Registers_Pn_ManualRCV14A212(self)
    @property
    def Registers_Pn_ManualRCV14A106(self) -> Registers_Pn_ManualRCV14A106:
        """
        Specifies settings of the ManualRCV register for 14A_106.
        """
        return Registers_Pn_ManualRCV14A106(self)
    @property
    def Registers_Pn_ManualRCV14B848(self) -> Registers_Pn_ManualRCV14B848:
        """
        Specifies settings of the ManualRCV register for 14B_848.
        """
        return Registers_Pn_ManualRCV14B848(self)
    @property
    def Registers_Pn_ManualRCV14B424(self) -> Registers_Pn_ManualRCV14B424:
        """
        Specifies settings of the ManualRCV register for 14B_424.
        """
        return Registers_Pn_ManualRCV14B424(self)
    @property
    def Registers_Pn_ManualRCV14B212(self) -> Registers_Pn_ManualRCV14B212:
        """
        Specifies settings of the ManualRCV register for 14B_212.
        """
        return Registers_Pn_ManualRCV14B212(self)
    @property
    def Registers_Pn_ManualRCV14B106(self) -> Registers_Pn_ManualRCV14B106:
        """
        Specifies settings of the ManualRCV register for 14B_106.
        """
        return Registers_Pn_ManualRCV14B106(self)
    @property
    def Registers_Pn_ManualRCV14A(self) -> Registers_Pn_ManualRCV14A:
        """
        Specifies settings of the ManualRCV register for 14A.
        """
        return Registers_Pn_ManualRCV14A(self)
    @property
    def Registers_Pn_ManualRCV14B(self) -> Registers_Pn_ManualRCV14B:
        """
        Specifies settings of the ManualRCV register for 14B.
        """
        return Registers_Pn_ManualRCV14B(self)
    @property
    def Registers_Pn_ManualRCVALL(self) -> Registers_Pn_ManualRCVALL:
        """
        Specifies settings of the ManualRCV register for ALL.
        """
        return Registers_Pn_ManualRCVALL(self)
    @property
    def Registers_Pn_ManualRCVVOLATILE(self) -> Registers_Pn_ManualRCVVOLATILE:
        """
        Specifies settings of the ManualRCV register for VOLATILE.
        """
        return Registers_Pn_ManualRCVVOLATILE(self)
    @property
    def Registers_Pn_TypeB14A848(self) -> Registers_Pn_TypeB14A848:
        """
        Specifies settings of the TypeB register for 14A_848.
        """
        return Registers_Pn_TypeB14A848(self)
    @property
    def Registers_Pn_TypeB14A424(self) -> Registers_Pn_TypeB14A424:
        """
        Specifies settings of the TypeB register for 14A_424.
        """
        return Registers_Pn_TypeB14A424(self)
    @property
    def Registers_Pn_TypeB14A212(self) -> Registers_Pn_TypeB14A212:
        """
        Specifies settings of the TypeB register for 14A_212.
        """
        return Registers_Pn_TypeB14A212(self)
    @property
    def Registers_Pn_TypeB14A106(self) -> Registers_Pn_TypeB14A106:
        """
        Specifies settings of the TypeB register for 14A_106.
        """
        return Registers_Pn_TypeB14A106(self)
    @property
    def Registers_Pn_TypeB14B848(self) -> Registers_Pn_TypeB14B848:
        """
        Specifies settings of the TypeB register for 14B_848.
        """
        return Registers_Pn_TypeB14B848(self)
    @property
    def Registers_Pn_TypeB14B424(self) -> Registers_Pn_TypeB14B424:
        """
        Specifies settings of the TypeB register for 14B_424.
        """
        return Registers_Pn_TypeB14B424(self)
    @property
    def Registers_Pn_TypeB14B212(self) -> Registers_Pn_TypeB14B212:
        """
        Specifies settings of the TypeB register for 14B_212.
        """
        return Registers_Pn_TypeB14B212(self)
    @property
    def Registers_Pn_TypeB14B106(self) -> Registers_Pn_TypeB14B106:
        """
        Specifies settings of the TypeB register for 14B_106.
        """
        return Registers_Pn_TypeB14B106(self)
    @property
    def Registers_Pn_TypeB14A(self) -> Registers_Pn_TypeB14A:
        """
        Specifies settings of the TypeB register for 14A.
        """
        return Registers_Pn_TypeB14A(self)
    @property
    def Registers_Pn_TypeB14B(self) -> Registers_Pn_TypeB14B:
        """
        Specifies settings of the TypeB register for 14B.
        """
        return Registers_Pn_TypeB14B(self)
    @property
    def Registers_Pn_TypeBALL(self) -> Registers_Pn_TypeBALL:
        """
        Specifies settings of the TypeB register for ALL.
        """
        return Registers_Pn_TypeBALL(self)
    @property
    def Registers_Pn_TypeBVOLATILE(self) -> Registers_Pn_TypeBVOLATILE:
        """
        Specifies settings of the TypeB register for VOLATILE.
        """
        return Registers_Pn_TypeBVOLATILE(self)
    @property
    def Registers_Pn_GsNOff14A848(self) -> Registers_Pn_GsNOff14A848:
        """
        Specifies settings of the GsNOff register for 14A_848.
        """
        return Registers_Pn_GsNOff14A848(self)
    @property
    def Registers_Pn_GsNOff14A424(self) -> Registers_Pn_GsNOff14A424:
        """
        Specifies settings of the GsNOff register for 14A_424.
        """
        return Registers_Pn_GsNOff14A424(self)
    @property
    def Registers_Pn_GsNOff14A212(self) -> Registers_Pn_GsNOff14A212:
        """
        Specifies settings of the GsNOff register for 14A_212.
        """
        return Registers_Pn_GsNOff14A212(self)
    @property
    def Registers_Pn_GsNOff14A106(self) -> Registers_Pn_GsNOff14A106:
        """
        Specifies settings of the GsNOff register for 14A_106.
        """
        return Registers_Pn_GsNOff14A106(self)
    @property
    def Registers_Pn_GsNOff14B848(self) -> Registers_Pn_GsNOff14B848:
        """
        Specifies settings of the GsNOff register for 14B_848.
        """
        return Registers_Pn_GsNOff14B848(self)
    @property
    def Registers_Pn_GsNOff14B424(self) -> Registers_Pn_GsNOff14B424:
        """
        Specifies settings of the GsNOff register for 14B_424.
        """
        return Registers_Pn_GsNOff14B424(self)
    @property
    def Registers_Pn_GsNOff14B212(self) -> Registers_Pn_GsNOff14B212:
        """
        Specifies settings of the GsNOff register for 14B_212.
        """
        return Registers_Pn_GsNOff14B212(self)
    @property
    def Registers_Pn_GsNOff14B106(self) -> Registers_Pn_GsNOff14B106:
        """
        Specifies settings of the GsNOff register for 14B_106.
        """
        return Registers_Pn_GsNOff14B106(self)
    @property
    def Registers_Pn_GsNOff14A(self) -> Registers_Pn_GsNOff14A:
        """
        Specifies settings of the GsNOff register for 14A.
        """
        return Registers_Pn_GsNOff14A(self)
    @property
    def Registers_Pn_GsNOff14B(self) -> Registers_Pn_GsNOff14B:
        """
        Specifies settings of the GsNOff register for 14B.
        """
        return Registers_Pn_GsNOff14B(self)
    @property
    def Registers_Pn_GsNOffALL(self) -> Registers_Pn_GsNOffALL:
        """
        Specifies settings of the GsNOff register for ALL.
        """
        return Registers_Pn_GsNOffALL(self)
    @property
    def Registers_Pn_GsNOffVOLATILE(self) -> Registers_Pn_GsNOffVOLATILE:
        """
        Specifies settings of the GsNOff register for VOLATILE.
        """
        return Registers_Pn_GsNOffVOLATILE(self)
    @property
    def Registers_Pn_ModWith14A848(self) -> Registers_Pn_ModWith14A848:
        """
        Specifies settings of the ModWith register for 14A_848.
        """
        return Registers_Pn_ModWith14A848(self)
    @property
    def Registers_Pn_ModWith14A424(self) -> Registers_Pn_ModWith14A424:
        """
        Specifies settings of the ModWith register for 14A_424.
        """
        return Registers_Pn_ModWith14A424(self)
    @property
    def Registers_Pn_ModWith14A212(self) -> Registers_Pn_ModWith14A212:
        """
        Specifies settings of the ModWith register for 14A_212.
        """
        return Registers_Pn_ModWith14A212(self)
    @property
    def Registers_Pn_ModWith14A106(self) -> Registers_Pn_ModWith14A106:
        """
        Specifies settings of the ModWith register for 14A_106.
        """
        return Registers_Pn_ModWith14A106(self)
    @property
    def Registers_Pn_ModWith14B848(self) -> Registers_Pn_ModWith14B848:
        """
        Specifies settings of the ModWith register for 14B_848.
        """
        return Registers_Pn_ModWith14B848(self)
    @property
    def Registers_Pn_ModWith14B424(self) -> Registers_Pn_ModWith14B424:
        """
        Specifies settings of the ModWith register for 14B_424.
        """
        return Registers_Pn_ModWith14B424(self)
    @property
    def Registers_Pn_ModWith14B212(self) -> Registers_Pn_ModWith14B212:
        """
        Specifies settings of the ModWith register for 14B_212.
        """
        return Registers_Pn_ModWith14B212(self)
    @property
    def Registers_Pn_ModWith14B106(self) -> Registers_Pn_ModWith14B106:
        """
        Specifies settings of the ModWith register for 14B_106.
        """
        return Registers_Pn_ModWith14B106(self)
    @property
    def Registers_Pn_ModWith14A(self) -> Registers_Pn_ModWith14A:
        """
        Specifies settings of the ModWith register for 14A.
        """
        return Registers_Pn_ModWith14A(self)
    @property
    def Registers_Pn_ModWith14B(self) -> Registers_Pn_ModWith14B:
        """
        Specifies settings of the ModWith register for 14B.
        """
        return Registers_Pn_ModWith14B(self)
    @property
    def Registers_Pn_ModWithALL(self) -> Registers_Pn_ModWithALL:
        """
        Specifies settings of the ModWith register for ALL.
        """
        return Registers_Pn_ModWithALL(self)
    @property
    def Registers_Pn_ModWithVOLATILE(self) -> Registers_Pn_ModWithVOLATILE:
        """
        Specifies settings of the ModWith register for VOLATILE.
        """
        return Registers_Pn_ModWithVOLATILE(self)
    @property
    def Registers_Pn_TxBitPhase14A848(self) -> Registers_Pn_TxBitPhase14A848:
        """
        Specifies settings of the TxBitPhase register for 14A_848.
        """
        return Registers_Pn_TxBitPhase14A848(self)
    @property
    def Registers_Pn_TxBitPhase14A424(self) -> Registers_Pn_TxBitPhase14A424:
        """
        Specifies settings of the TxBitPhase register for 14A_424.
        """
        return Registers_Pn_TxBitPhase14A424(self)
    @property
    def Registers_Pn_TxBitPhase14A212(self) -> Registers_Pn_TxBitPhase14A212:
        """
        Specifies settings of the TxBitPhase register for 14A_212.
        """
        return Registers_Pn_TxBitPhase14A212(self)
    @property
    def Registers_Pn_TxBitPhase14A106(self) -> Registers_Pn_TxBitPhase14A106:
        """
        Specifies settings of the TxBitPhase register for 14A_106.
        """
        return Registers_Pn_TxBitPhase14A106(self)
    @property
    def Registers_Pn_TxBitPhase14B848(self) -> Registers_Pn_TxBitPhase14B848:
        """
        Specifies settings of the TxBitPhase register for 14B_848.
        """
        return Registers_Pn_TxBitPhase14B848(self)
    @property
    def Registers_Pn_TxBitPhase14B424(self) -> Registers_Pn_TxBitPhase14B424:
        """
        Specifies settings of the TxBitPhase register for 14B_424.
        """
        return Registers_Pn_TxBitPhase14B424(self)
    @property
    def Registers_Pn_TxBitPhase14B212(self) -> Registers_Pn_TxBitPhase14B212:
        """
        Specifies settings of the TxBitPhase register for 14B_212.
        """
        return Registers_Pn_TxBitPhase14B212(self)
    @property
    def Registers_Pn_TxBitPhase14B106(self) -> Registers_Pn_TxBitPhase14B106:
        """
        Specifies settings of the TxBitPhase register for 14B_106.
        """
        return Registers_Pn_TxBitPhase14B106(self)
    @property
    def Registers_Pn_TxBitPhase14A(self) -> Registers_Pn_TxBitPhase14A:
        """
        Specifies settings of the TxBitPhase register for 14A.
        """
        return Registers_Pn_TxBitPhase14A(self)
    @property
    def Registers_Pn_TxBitPhase14B(self) -> Registers_Pn_TxBitPhase14B:
        """
        Specifies settings of the TxBitPhase register for 14B.
        """
        return Registers_Pn_TxBitPhase14B(self)
    @property
    def Registers_Pn_TxBitPhaseALL(self) -> Registers_Pn_TxBitPhaseALL:
        """
        Specifies settings of the TxBitPhase register for ALL.
        """
        return Registers_Pn_TxBitPhaseALL(self)
    @property
    def Registers_Pn_TxBitPhaseVOLATILE(self) -> Registers_Pn_TxBitPhaseVOLATILE:
        """
        Specifies settings of the TxBitPhase register for VOLATILE.
        """
        return Registers_Pn_TxBitPhaseVOLATILE(self)
    @property
    def Registers_Pn_RFCfg14A848(self) -> Registers_Pn_RFCfg14A848:
        """
        Specifies settings of the RFCfg register for 14A_848.
        """
        return Registers_Pn_RFCfg14A848(self)
    @property
    def Registers_Pn_RFCfg14A424(self) -> Registers_Pn_RFCfg14A424:
        """
        Specifies settings of the RFCfg register for 14A_424.
        """
        return Registers_Pn_RFCfg14A424(self)
    @property
    def Registers_Pn_RFCfg14A212(self) -> Registers_Pn_RFCfg14A212:
        """
        Specifies settings of the RFCfg register for 14A_212.
        """
        return Registers_Pn_RFCfg14A212(self)
    @property
    def Registers_Pn_RFCfg14A106(self) -> Registers_Pn_RFCfg14A106:
        """
        Specifies settings of the RFCfg register for 14A_106.
        """
        return Registers_Pn_RFCfg14A106(self)
    @property
    def Registers_Pn_RFCfg14B848(self) -> Registers_Pn_RFCfg14B848:
        """
        Specifies settings of the RFCfg register for 14B_848.
        """
        return Registers_Pn_RFCfg14B848(self)
    @property
    def Registers_Pn_RFCfg14B424(self) -> Registers_Pn_RFCfg14B424:
        """
        Specifies settings of the RFCfg register for 14B_424.
        """
        return Registers_Pn_RFCfg14B424(self)
    @property
    def Registers_Pn_RFCfg14B212(self) -> Registers_Pn_RFCfg14B212:
        """
        Specifies settings of the RFCfg register for 14B_212.
        """
        return Registers_Pn_RFCfg14B212(self)
    @property
    def Registers_Pn_RFCfg14B106(self) -> Registers_Pn_RFCfg14B106:
        """
        Specifies settings of the RFCfg register for 14B_106.
        """
        return Registers_Pn_RFCfg14B106(self)
    @property
    def Registers_Pn_RFCfg14A(self) -> Registers_Pn_RFCfg14A:
        """
        Specifies settings of the RFCfg register for 14A.
        """
        return Registers_Pn_RFCfg14A(self)
    @property
    def Registers_Pn_RFCfg14B(self) -> Registers_Pn_RFCfg14B:
        """
        Specifies settings of the RFCfg register for 14B.
        """
        return Registers_Pn_RFCfg14B(self)
    @property
    def Registers_Pn_RFCfgALL(self) -> Registers_Pn_RFCfgALL:
        """
        Specifies settings of the RFCfg register for ALL.
        """
        return Registers_Pn_RFCfgALL(self)
    @property
    def Registers_Pn_RFCfgVOLATILE(self) -> Registers_Pn_RFCfgVOLATILE:
        """
        Specifies settings of the RFCfg register for VOLATILE.
        """
        return Registers_Pn_RFCfgVOLATILE(self)
    @property
    def Registers_Pn_GsNOn14A848(self) -> Registers_Pn_GsNOn14A848:
        """
        Specifies settings of the GsNOn register for 14A_848.
        """
        return Registers_Pn_GsNOn14A848(self)
    @property
    def Registers_Pn_GsNOn14A424(self) -> Registers_Pn_GsNOn14A424:
        """
        Specifies settings of the GsNOn register for 14A_424.
        """
        return Registers_Pn_GsNOn14A424(self)
    @property
    def Registers_Pn_GsNOn14A212(self) -> Registers_Pn_GsNOn14A212:
        """
        Specifies settings of the GsNOn register for 14A_212.
        """
        return Registers_Pn_GsNOn14A212(self)
    @property
    def Registers_Pn_GsNOn14A106(self) -> Registers_Pn_GsNOn14A106:
        """
        Specifies settings of the GsNOn register for 14A_106.
        """
        return Registers_Pn_GsNOn14A106(self)
    @property
    def Registers_Pn_GsNOn14B848(self) -> Registers_Pn_GsNOn14B848:
        """
        Specifies settings of the GsNOn register for 14B_848.
        """
        return Registers_Pn_GsNOn14B848(self)
    @property
    def Registers_Pn_GsNOn14B424(self) -> Registers_Pn_GsNOn14B424:
        """
        Specifies settings of the GsNOn register for 14B_424.
        """
        return Registers_Pn_GsNOn14B424(self)
    @property
    def Registers_Pn_GsNOn14B212(self) -> Registers_Pn_GsNOn14B212:
        """
        Specifies settings of the GsNOn register for 14B_212.
        """
        return Registers_Pn_GsNOn14B212(self)
    @property
    def Registers_Pn_GsNOn14B106(self) -> Registers_Pn_GsNOn14B106:
        """
        Specifies settings of the GsNOn register for 14B_106.
        """
        return Registers_Pn_GsNOn14B106(self)
    @property
    def Registers_Pn_GsNOn14A(self) -> Registers_Pn_GsNOn14A:
        """
        Specifies settings of the GsNOn register for 14A.
        """
        return Registers_Pn_GsNOn14A(self)
    @property
    def Registers_Pn_GsNOn14B(self) -> Registers_Pn_GsNOn14B:
        """
        Specifies settings of the GsNOn register for 14B.
        """
        return Registers_Pn_GsNOn14B(self)
    @property
    def Registers_Pn_GsNOnALL(self) -> Registers_Pn_GsNOnALL:
        """
        Specifies settings of the GsNOn register for ALL.
        """
        return Registers_Pn_GsNOnALL(self)
    @property
    def Registers_Pn_GsNOnVOLATILE(self) -> Registers_Pn_GsNOnVOLATILE:
        """
        Specifies settings of the GsNOn register for VOLATILE.
        """
        return Registers_Pn_GsNOnVOLATILE(self)
    @property
    def Registers_Pn_CWGsP14A848(self) -> Registers_Pn_CWGsP14A848:
        """
        Specifies settings of the CWGsP register for 14A_848.
        """
        return Registers_Pn_CWGsP14A848(self)
    @property
    def Registers_Pn_CWGsP14A424(self) -> Registers_Pn_CWGsP14A424:
        """
        Specifies settings of the CWGsP register for 14A_424.
        """
        return Registers_Pn_CWGsP14A424(self)
    @property
    def Registers_Pn_CWGsP14A212(self) -> Registers_Pn_CWGsP14A212:
        """
        Specifies settings of the CWGsP register for 14A_212.
        """
        return Registers_Pn_CWGsP14A212(self)
    @property
    def Registers_Pn_CWGsP14A106(self) -> Registers_Pn_CWGsP14A106:
        """
        Specifies settings of the CWGsP register for 14A_106.
        """
        return Registers_Pn_CWGsP14A106(self)
    @property
    def Registers_Pn_CWGsP14B848(self) -> Registers_Pn_CWGsP14B848:
        """
        Specifies settings of the CWGsP register for 14B_848.
        """
        return Registers_Pn_CWGsP14B848(self)
    @property
    def Registers_Pn_CWGsP14B424(self) -> Registers_Pn_CWGsP14B424:
        """
        Specifies settings of the CWGsP register for 14B_424.
        """
        return Registers_Pn_CWGsP14B424(self)
    @property
    def Registers_Pn_CWGsP14B212(self) -> Registers_Pn_CWGsP14B212:
        """
        Specifies settings of the CWGsP register for 14B_212.
        """
        return Registers_Pn_CWGsP14B212(self)
    @property
    def Registers_Pn_CWGsP14B106(self) -> Registers_Pn_CWGsP14B106:
        """
        Specifies settings of the CWGsP register for 14B_106.
        """
        return Registers_Pn_CWGsP14B106(self)
    @property
    def Registers_Pn_CWGsP14A(self) -> Registers_Pn_CWGsP14A:
        """
        Specifies settings of the CWGsP register for 14A.
        """
        return Registers_Pn_CWGsP14A(self)
    @property
    def Registers_Pn_CWGsP14B(self) -> Registers_Pn_CWGsP14B:
        """
        Specifies settings of the CWGsP register for 14B.
        """
        return Registers_Pn_CWGsP14B(self)
    @property
    def Registers_Pn_CWGsPALL(self) -> Registers_Pn_CWGsPALL:
        """
        Specifies settings of the CWGsP register for ALL.
        """
        return Registers_Pn_CWGsPALL(self)
    @property
    def Registers_Pn_CWGsPVOLATILE(self) -> Registers_Pn_CWGsPVOLATILE:
        """
        Specifies settings of the CWGsP register for VOLATILE.
        """
        return Registers_Pn_CWGsPVOLATILE(self)
    @property
    def Registers_Pn_ModGsP14A848(self) -> Registers_Pn_ModGsP14A848:
        """
        Specifies settings of the ModGsP register for 14A_848.
        """
        return Registers_Pn_ModGsP14A848(self)
    @property
    def Registers_Pn_ModGsP14A424(self) -> Registers_Pn_ModGsP14A424:
        """
        Specifies settings of the ModGsP register for 14A_424.
        """
        return Registers_Pn_ModGsP14A424(self)
    @property
    def Registers_Pn_ModGsP14A212(self) -> Registers_Pn_ModGsP14A212:
        """
        Specifies settings of the ModGsP register for 14A_212.
        """
        return Registers_Pn_ModGsP14A212(self)
    @property
    def Registers_Pn_ModGsP14A106(self) -> Registers_Pn_ModGsP14A106:
        """
        Specifies settings of the ModGsP register for 14A_106.
        """
        return Registers_Pn_ModGsP14A106(self)
    @property
    def Registers_Pn_ModGsP14B848(self) -> Registers_Pn_ModGsP14B848:
        """
        Specifies settings of the ModGsP register for 14B_848.
        """
        return Registers_Pn_ModGsP14B848(self)
    @property
    def Registers_Pn_ModGsP14B424(self) -> Registers_Pn_ModGsP14B424:
        """
        Specifies settings of the ModGsP register for 14B_424.
        """
        return Registers_Pn_ModGsP14B424(self)
    @property
    def Registers_Pn_ModGsP14B212(self) -> Registers_Pn_ModGsP14B212:
        """
        Specifies settings of the ModGsP register for 14B_212.
        """
        return Registers_Pn_ModGsP14B212(self)
    @property
    def Registers_Pn_ModGsP14B106(self) -> Registers_Pn_ModGsP14B106:
        """
        Specifies settings of the ModGsP register for 14B_106.
        """
        return Registers_Pn_ModGsP14B106(self)
    @property
    def Registers_Pn_ModGsP14A(self) -> Registers_Pn_ModGsP14A:
        """
        Specifies settings of the ModGsP register for 14A.
        """
        return Registers_Pn_ModGsP14A(self)
    @property
    def Registers_Pn_ModGsP14B(self) -> Registers_Pn_ModGsP14B:
        """
        Specifies settings of the ModGsP register for 14B.
        """
        return Registers_Pn_ModGsP14B(self)
    @property
    def Registers_Pn_ModGsPALL(self) -> Registers_Pn_ModGsPALL:
        """
        Specifies settings of the ModGsP register for ALL.
        """
        return Registers_Pn_ModGsPALL(self)
    @property
    def Registers_Pn_ModGsPVOLATILE(self) -> Registers_Pn_ModGsPVOLATILE:
        """
        Specifies settings of the ModGsP register for VOLATILE.
        """
        return Registers_Pn_ModGsPVOLATILE(self)
    @property
    def Registers_Rc663(self) -> Registers_Rc663:
        """
        This value contains HF Settings (Register Settings) of the RC663 reader chip.
        """
        return Registers_Rc663(self)
    @property
    def Registers_Rc663_TxAmpReg14A848(self) -> Registers_Rc663_TxAmpReg14A848:
        """
        Specifies settings of the TxAmpReg register for 14A_848.
        """
        return Registers_Rc663_TxAmpReg14A848(self)
    @property
    def Registers_Rc663_TxAmpReg14A424(self) -> Registers_Rc663_TxAmpReg14A424:
        """
        Specifies settings of the TxAmpReg register for 14A_424.
        """
        return Registers_Rc663_TxAmpReg14A424(self)
    @property
    def Registers_Rc663_TxAmpReg14A212(self) -> Registers_Rc663_TxAmpReg14A212:
        """
        Specifies settings of the TxAmpReg register for 14A_212.
        """
        return Registers_Rc663_TxAmpReg14A212(self)
    @property
    def Registers_Rc663_TxAmpReg14A106(self) -> Registers_Rc663_TxAmpReg14A106:
        """
        Specifies settings of the TxAmpReg register for 14A_106.
        """
        return Registers_Rc663_TxAmpReg14A106(self)
    @property
    def Registers_Rc663_TxAmpReg14B848(self) -> Registers_Rc663_TxAmpReg14B848:
        """
        Specifies settings of the TxAmpReg register for 14B_848.
        """
        return Registers_Rc663_TxAmpReg14B848(self)
    @property
    def Registers_Rc663_TxAmpReg14B424(self) -> Registers_Rc663_TxAmpReg14B424:
        """
        Specifies settings of the TxAmpReg register for 14B_424.
        """
        return Registers_Rc663_TxAmpReg14B424(self)
    @property
    def Registers_Rc663_TxAmpReg14B212(self) -> Registers_Rc663_TxAmpReg14B212:
        """
        Specifies settings of the TxAmpReg register for 14B_212.
        """
        return Registers_Rc663_TxAmpReg14B212(self)
    @property
    def Registers_Rc663_TxAmpReg14B106(self) -> Registers_Rc663_TxAmpReg14B106:
        """
        Specifies settings of the TxAmpReg register for 14B_106.
        """
        return Registers_Rc663_TxAmpReg14B106(self)
    @property
    def Registers_Rc663_TxAmpReg15(self) -> Registers_Rc663_TxAmpReg15:
        """
        Specifies settings of the TxAmpReg register for 15.
        """
        return Registers_Rc663_TxAmpReg15(self)
    @property
    def Registers_Rc663_TxAmpReg14A(self) -> Registers_Rc663_TxAmpReg14A:
        """
        Specifies settings of the TxAmpReg register for 14A.
        """
        return Registers_Rc663_TxAmpReg14A(self)
    @property
    def Registers_Rc663_TxAmpReg14B(self) -> Registers_Rc663_TxAmpReg14B:
        """
        Specifies settings of the TxAmpReg register for 14B.
        """
        return Registers_Rc663_TxAmpReg14B(self)
    @property
    def Registers_Rc663_TxAmpRegALL(self) -> Registers_Rc663_TxAmpRegALL:
        """
        Specifies settings of the TxAmpReg register for ALL.
        """
        return Registers_Rc663_TxAmpRegALL(self)
    @property
    def Registers_Rc663_TxAmpRegVOLATILE(self) -> Registers_Rc663_TxAmpRegVOLATILE:
        """
        Specifies settings of the TxAmpReg register for VOLATILE.
        """
        return Registers_Rc663_TxAmpRegVOLATILE(self)
    @property
    def Registers_Rc663_TxDataModWithReg14A848(self) -> Registers_Rc663_TxDataModWithReg14A848:
        """
        Specifies settings of the TxDataModWithReg register for 14A_848.
        """
        return Registers_Rc663_TxDataModWithReg14A848(self)
    @property
    def Registers_Rc663_TxDataModWithReg14A424(self) -> Registers_Rc663_TxDataModWithReg14A424:
        """
        Specifies settings of the TxDataModWithReg register for 14A_424.
        """
        return Registers_Rc663_TxDataModWithReg14A424(self)
    @property
    def Registers_Rc663_TxDataModWithReg14A212(self) -> Registers_Rc663_TxDataModWithReg14A212:
        """
        Specifies settings of the TxDataModWithReg register for 14A_212.
        """
        return Registers_Rc663_TxDataModWithReg14A212(self)
    @property
    def Registers_Rc663_TxDataModWithReg14A106(self) -> Registers_Rc663_TxDataModWithReg14A106:
        """
        Specifies settings of the TxDataModWithReg register for 14A_106.
        """
        return Registers_Rc663_TxDataModWithReg14A106(self)
    @property
    def Registers_Rc663_TxDataModWithReg14B848(self) -> Registers_Rc663_TxDataModWithReg14B848:
        """
        Specifies settings of the TxDataModWithReg register for 14B_848.
        """
        return Registers_Rc663_TxDataModWithReg14B848(self)
    @property
    def Registers_Rc663_TxDataModWithReg14B424(self) -> Registers_Rc663_TxDataModWithReg14B424:
        """
        Specifies settings of the TxDataModWithReg register for 14B_424.
        """
        return Registers_Rc663_TxDataModWithReg14B424(self)
    @property
    def Registers_Rc663_TxDataModWithReg14B212(self) -> Registers_Rc663_TxDataModWithReg14B212:
        """
        Specifies settings of the TxDataModWithReg register for 14B_212.
        """
        return Registers_Rc663_TxDataModWithReg14B212(self)
    @property
    def Registers_Rc663_TxDataModWithReg14B106(self) -> Registers_Rc663_TxDataModWithReg14B106:
        """
        Specifies settings of the TxDataModWithReg register for 14B_106.
        """
        return Registers_Rc663_TxDataModWithReg14B106(self)
    @property
    def Registers_Rc663_TxDataModWithReg15(self) -> Registers_Rc663_TxDataModWithReg15:
        """
        Specifies settings of the TxDataModWithReg register for 15.
        """
        return Registers_Rc663_TxDataModWithReg15(self)
    @property
    def Registers_Rc663_TxDataModWithReg14A(self) -> Registers_Rc663_TxDataModWithReg14A:
        """
        Specifies settings of the TxDataModWithReg register for 14A.
        """
        return Registers_Rc663_TxDataModWithReg14A(self)
    @property
    def Registers_Rc663_TxDataModWithReg14B(self) -> Registers_Rc663_TxDataModWithReg14B:
        """
        Specifies settings of the TxDataModWithReg register for 14B.
        """
        return Registers_Rc663_TxDataModWithReg14B(self)
    @property
    def Registers_Rc663_TxDataModWithRegALL(self) -> Registers_Rc663_TxDataModWithRegALL:
        """
        Specifies settings of the TxDataModWithReg register for ALL.
        """
        return Registers_Rc663_TxDataModWithRegALL(self)
    @property
    def Registers_Rc663_TxDataModWithRegVOLATILE(self) -> Registers_Rc663_TxDataModWithRegVOLATILE:
        """
        Specifies settings of the TxDataModWithReg register for VOLATILE.
        """
        return Registers_Rc663_TxDataModWithRegVOLATILE(self)
    @property
    def Registers_Rc663_RxThresholdReg14A848(self) -> Registers_Rc663_RxThresholdReg14A848:
        """
        Specifies settings of the RxThresholdReg register for 14A_848.
        """
        return Registers_Rc663_RxThresholdReg14A848(self)
    @property
    def Registers_Rc663_RxThresholdReg14A424(self) -> Registers_Rc663_RxThresholdReg14A424:
        """
        Specifies settings of the RxThresholdReg register for 14A_424.
        """
        return Registers_Rc663_RxThresholdReg14A424(self)
    @property
    def Registers_Rc663_RxThresholdReg14A212(self) -> Registers_Rc663_RxThresholdReg14A212:
        """
        Specifies settings of the RxThresholdReg register for 14A_212.
        """
        return Registers_Rc663_RxThresholdReg14A212(self)
    @property
    def Registers_Rc663_RxThresholdReg14A106(self) -> Registers_Rc663_RxThresholdReg14A106:
        """
        Specifies settings of the RxThresholdReg register for 14A_106.
        """
        return Registers_Rc663_RxThresholdReg14A106(self)
    @property
    def Registers_Rc663_RxThresholdReg14B848(self) -> Registers_Rc663_RxThresholdReg14B848:
        """
        Specifies settings of the RxThresholdReg register for 14B_848.
        """
        return Registers_Rc663_RxThresholdReg14B848(self)
    @property
    def Registers_Rc663_RxThresholdReg14B424(self) -> Registers_Rc663_RxThresholdReg14B424:
        """
        Specifies settings of the RxThresholdReg register for 14B_424.
        """
        return Registers_Rc663_RxThresholdReg14B424(self)
    @property
    def Registers_Rc663_RxThresholdReg14B212(self) -> Registers_Rc663_RxThresholdReg14B212:
        """
        Specifies settings of the RxThresholdReg register for 14B_212.
        """
        return Registers_Rc663_RxThresholdReg14B212(self)
    @property
    def Registers_Rc663_RxThresholdReg14B106(self) -> Registers_Rc663_RxThresholdReg14B106:
        """
        Specifies settings of the RxThresholdReg register for 14B_106.
        """
        return Registers_Rc663_RxThresholdReg14B106(self)
    @property
    def Registers_Rc663_RxThresholdReg15(self) -> Registers_Rc663_RxThresholdReg15:
        """
        Specifies settings of the RxThresholdReg register for 15.
        """
        return Registers_Rc663_RxThresholdReg15(self)
    @property
    def Registers_Rc663_RxThresholdReg14A(self) -> Registers_Rc663_RxThresholdReg14A:
        """
        Specifies settings of the RxThresholdReg register for 14A.
        """
        return Registers_Rc663_RxThresholdReg14A(self)
    @property
    def Registers_Rc663_RxThresholdReg14B(self) -> Registers_Rc663_RxThresholdReg14B:
        """
        Specifies settings of the RxThresholdReg register for 14B.
        """
        return Registers_Rc663_RxThresholdReg14B(self)
    @property
    def Registers_Rc663_RxThresholdRegALL(self) -> Registers_Rc663_RxThresholdRegALL:
        """
        Specifies settings of the RxThresholdReg register for ALL.
        """
        return Registers_Rc663_RxThresholdRegALL(self)
    @property
    def Registers_Rc663_RxThresholdRegVOLATILE(self) -> Registers_Rc663_RxThresholdRegVOLATILE:
        """
        Specifies settings of the RxThresholdReg register for VOLATILE.
        """
        return Registers_Rc663_RxThresholdRegVOLATILE(self)
    @property
    def Registers_Rc663_RxAnaReg14A848(self) -> Registers_Rc663_RxAnaReg14A848:
        """
        Specifies settings of the RxAnaReg register for 14A_848.
        """
        return Registers_Rc663_RxAnaReg14A848(self)
    @property
    def Registers_Rc663_RxAnaReg14A424(self) -> Registers_Rc663_RxAnaReg14A424:
        """
        Specifies settings of the RxAnaReg register for 14A_424.
        """
        return Registers_Rc663_RxAnaReg14A424(self)
    @property
    def Registers_Rc663_RxAnaReg14A212(self) -> Registers_Rc663_RxAnaReg14A212:
        """
        Specifies settings of the RxAnaReg register for 14A_212.
        """
        return Registers_Rc663_RxAnaReg14A212(self)
    @property
    def Registers_Rc663_RxAnaReg14A106(self) -> Registers_Rc663_RxAnaReg14A106:
        """
        Specifies settings of the RxAnaReg register for 14A_106.
        """
        return Registers_Rc663_RxAnaReg14A106(self)
    @property
    def Registers_Rc663_RxAnaReg14B848(self) -> Registers_Rc663_RxAnaReg14B848:
        """
        Specifies settings of the RxAnaReg register for 14B_848.
        """
        return Registers_Rc663_RxAnaReg14B848(self)
    @property
    def Registers_Rc663_RxAnaReg14B424(self) -> Registers_Rc663_RxAnaReg14B424:
        """
        Specifies settings of the RxAnaReg register for 14B_424.
        """
        return Registers_Rc663_RxAnaReg14B424(self)
    @property
    def Registers_Rc663_RxAnaReg14B212(self) -> Registers_Rc663_RxAnaReg14B212:
        """
        Specifies settings of the RxAnaReg register for 14B_212.
        """
        return Registers_Rc663_RxAnaReg14B212(self)
    @property
    def Registers_Rc663_RxAnaReg14B106(self) -> Registers_Rc663_RxAnaReg14B106:
        """
        Specifies settings of the RxAnaReg register for 14B_106.
        """
        return Registers_Rc663_RxAnaReg14B106(self)
    @property
    def Registers_Rc663_RxAnaReg15(self) -> Registers_Rc663_RxAnaReg15:
        """
        Specifies settings of the RxAnaReg register for 15.
        """
        return Registers_Rc663_RxAnaReg15(self)
    @property
    def Registers_Rc663_RxAnaReg14A(self) -> Registers_Rc663_RxAnaReg14A:
        """
        Specifies settings of the RxAnaReg register for 14A.
        """
        return Registers_Rc663_RxAnaReg14A(self)
    @property
    def Registers_Rc663_RxAnaReg14B(self) -> Registers_Rc663_RxAnaReg14B:
        """
        Specifies settings of the RxAnaReg register for 14B.
        """
        return Registers_Rc663_RxAnaReg14B(self)
    @property
    def Registers_Rc663_RxAnaRegALL(self) -> Registers_Rc663_RxAnaRegALL:
        """
        Specifies settings of the RxAnaReg register for ALL.
        """
        return Registers_Rc663_RxAnaRegALL(self)
    @property
    def Registers_Rc663_RxAnaRegVOLATILE(self) -> Registers_Rc663_RxAnaRegVOLATILE:
        """
        Specifies settings of the RxAnaReg register for VOLATILE.
        """
        return Registers_Rc663_RxAnaRegVOLATILE(self)
    @property
    def Registers_Rc663_TxModeReg14A848(self) -> Registers_Rc663_TxModeReg14A848:
        """
        Specifies settings of the TxModeReg register for 14A_848.
        """
        return Registers_Rc663_TxModeReg14A848(self)
    @property
    def Registers_Rc663_TxModeReg14A424(self) -> Registers_Rc663_TxModeReg14A424:
        """
        Specifies settings of the TxModeReg register for 14A_424.
        """
        return Registers_Rc663_TxModeReg14A424(self)
    @property
    def Registers_Rc663_TxModeReg14A212(self) -> Registers_Rc663_TxModeReg14A212:
        """
        Specifies settings of the TxModeReg register for 14A_212.
        """
        return Registers_Rc663_TxModeReg14A212(self)
    @property
    def Registers_Rc663_TxModeReg14A106(self) -> Registers_Rc663_TxModeReg14A106:
        """
        Specifies settings of the TxModeReg register for 14A_106.
        """
        return Registers_Rc663_TxModeReg14A106(self)
    @property
    def Registers_Rc663_TxModeReg14B848(self) -> Registers_Rc663_TxModeReg14B848:
        """
        Specifies settings of the TxModeReg register for 14B_848.
        """
        return Registers_Rc663_TxModeReg14B848(self)
    @property
    def Registers_Rc663_TxModeReg14B424(self) -> Registers_Rc663_TxModeReg14B424:
        """
        Specifies settings of the TxModeReg register for 14B_424.
        """
        return Registers_Rc663_TxModeReg14B424(self)
    @property
    def Registers_Rc663_TxModeReg14B212(self) -> Registers_Rc663_TxModeReg14B212:
        """
        Specifies settings of the TxModeReg register for 14B_212.
        """
        return Registers_Rc663_TxModeReg14B212(self)
    @property
    def Registers_Rc663_TxModeReg14B106(self) -> Registers_Rc663_TxModeReg14B106:
        """
        Specifies settings of the TxModeReg register for 14B_106.
        """
        return Registers_Rc663_TxModeReg14B106(self)
    @property
    def Registers_Rc663_TxModeReg15(self) -> Registers_Rc663_TxModeReg15:
        """
        Specifies settings of the TxModeReg register for 15.
        """
        return Registers_Rc663_TxModeReg15(self)
    @property
    def Registers_Rc663_TxModeReg14A(self) -> Registers_Rc663_TxModeReg14A:
        """
        Specifies settings of the TxModeReg register for 14A.
        """
        return Registers_Rc663_TxModeReg14A(self)
    @property
    def Registers_Rc663_TxModeReg14B(self) -> Registers_Rc663_TxModeReg14B:
        """
        Specifies settings of the TxModeReg register for 14B.
        """
        return Registers_Rc663_TxModeReg14B(self)
    @property
    def Registers_Rc663_TxModeRegALL(self) -> Registers_Rc663_TxModeRegALL:
        """
        Specifies settings of the TxModeReg register for ALL.
        """
        return Registers_Rc663_TxModeRegALL(self)
    @property
    def Registers_Rc663_TxModeRegVOLATILE(self) -> Registers_Rc663_TxModeRegVOLATILE:
        """
        Specifies settings of the TxModeReg register for VOLATILE.
        """
        return Registers_Rc663_TxModeRegVOLATILE(self)
    @property
    def Registers_Rc663_TxConReg14A848(self) -> Registers_Rc663_TxConReg14A848:
        """
        Specifies settings of the TxConReg register for 14A_848.
        """
        return Registers_Rc663_TxConReg14A848(self)
    @property
    def Registers_Rc663_TxConReg14A424(self) -> Registers_Rc663_TxConReg14A424:
        """
        Specifies settings of the TxConReg register for 14A_424.
        """
        return Registers_Rc663_TxConReg14A424(self)
    @property
    def Registers_Rc663_TxConReg14A212(self) -> Registers_Rc663_TxConReg14A212:
        """
        Specifies settings of the TxConReg register for 14A_212.
        """
        return Registers_Rc663_TxConReg14A212(self)
    @property
    def Registers_Rc663_TxConReg14A106(self) -> Registers_Rc663_TxConReg14A106:
        """
        Specifies settings of the TxConReg register for 14A_106.
        """
        return Registers_Rc663_TxConReg14A106(self)
    @property
    def Registers_Rc663_TxConReg14B848(self) -> Registers_Rc663_TxConReg14B848:
        """
        Specifies settings of the TxConReg register for 14B_848.
        """
        return Registers_Rc663_TxConReg14B848(self)
    @property
    def Registers_Rc663_TxConReg14B424(self) -> Registers_Rc663_TxConReg14B424:
        """
        Specifies settings of the TxConReg register for 14B_424.
        """
        return Registers_Rc663_TxConReg14B424(self)
    @property
    def Registers_Rc663_TxConReg14B212(self) -> Registers_Rc663_TxConReg14B212:
        """
        Specifies settings of the TxConReg register for 14B_212.
        """
        return Registers_Rc663_TxConReg14B212(self)
    @property
    def Registers_Rc663_TxConReg14B106(self) -> Registers_Rc663_TxConReg14B106:
        """
        Specifies settings of the TxConReg register for 14B_106.
        """
        return Registers_Rc663_TxConReg14B106(self)
    @property
    def Registers_Rc663_TxConReg15(self) -> Registers_Rc663_TxConReg15:
        """
        Specifies settings of the TxConReg register for 15.
        """
        return Registers_Rc663_TxConReg15(self)
    @property
    def Registers_Rc663_TxConReg14A(self) -> Registers_Rc663_TxConReg14A:
        """
        Specifies settings of the TxConReg register for 14A.
        """
        return Registers_Rc663_TxConReg14A(self)
    @property
    def Registers_Rc663_TxConReg14B(self) -> Registers_Rc663_TxConReg14B:
        """
        Specifies settings of the TxConReg register for 14B.
        """
        return Registers_Rc663_TxConReg14B(self)
    @property
    def Registers_Rc663_TxConRegALL(self) -> Registers_Rc663_TxConRegALL:
        """
        Specifies settings of the TxConReg register for ALL.
        """
        return Registers_Rc663_TxConRegALL(self)
    @property
    def Registers_Rc663_TxConRegVOLATILE(self) -> Registers_Rc663_TxConRegVOLATILE:
        """
        Specifies settings of the TxConReg register for VOLATILE.
        """
        return Registers_Rc663_TxConRegVOLATILE(self)
    @property
    def Registers_Rc663_TxlReg14A848(self) -> Registers_Rc663_TxlReg14A848:
        """
        Specifies settings of the TxlReg register for 14A_848.
        """
        return Registers_Rc663_TxlReg14A848(self)
    @property
    def Registers_Rc663_TxlReg14A424(self) -> Registers_Rc663_TxlReg14A424:
        """
        Specifies settings of the TxlReg register for 14A_424.
        """
        return Registers_Rc663_TxlReg14A424(self)
    @property
    def Registers_Rc663_TxlReg14A212(self) -> Registers_Rc663_TxlReg14A212:
        """
        Specifies settings of the TxlReg register for 14A_212.
        """
        return Registers_Rc663_TxlReg14A212(self)
    @property
    def Registers_Rc663_TxlReg14A106(self) -> Registers_Rc663_TxlReg14A106:
        """
        Specifies settings of the TxlReg register for 14A_106.
        """
        return Registers_Rc663_TxlReg14A106(self)
    @property
    def Registers_Rc663_TxlReg14B848(self) -> Registers_Rc663_TxlReg14B848:
        """
        Specifies settings of the TxlReg register for 14B_848.
        """
        return Registers_Rc663_TxlReg14B848(self)
    @property
    def Registers_Rc663_TxlReg14B424(self) -> Registers_Rc663_TxlReg14B424:
        """
        Specifies settings of the TxlReg register for 14B_424.
        """
        return Registers_Rc663_TxlReg14B424(self)
    @property
    def Registers_Rc663_TxlReg14B212(self) -> Registers_Rc663_TxlReg14B212:
        """
        Specifies settings of the TxlReg register for 14B_212.
        """
        return Registers_Rc663_TxlReg14B212(self)
    @property
    def Registers_Rc663_TxlReg14B106(self) -> Registers_Rc663_TxlReg14B106:
        """
        Specifies settings of the TxlReg register for 14B_106.
        """
        return Registers_Rc663_TxlReg14B106(self)
    @property
    def Registers_Rc663_TxlReg15(self) -> Registers_Rc663_TxlReg15:
        """
        Specifies settings of the TxlReg register for 15.
        """
        return Registers_Rc663_TxlReg15(self)
    @property
    def Registers_Rc663_TxlReg14A(self) -> Registers_Rc663_TxlReg14A:
        """
        Specifies settings of the TxlReg register for 14A.
        """
        return Registers_Rc663_TxlReg14A(self)
    @property
    def Registers_Rc663_TxlReg14B(self) -> Registers_Rc663_TxlReg14B:
        """
        Specifies settings of the TxlReg register for 14B.
        """
        return Registers_Rc663_TxlReg14B(self)
    @property
    def Registers_Rc663_TxlRegALL(self) -> Registers_Rc663_TxlRegALL:
        """
        Specifies settings of the TxlReg register for ALL.
        """
        return Registers_Rc663_TxlRegALL(self)
    @property
    def Registers_Rc663_TxlRegVOLATILE(self) -> Registers_Rc663_TxlRegVOLATILE:
        """
        Specifies settings of the TxlReg register for VOLATILE.
        """
        return Registers_Rc663_TxlRegVOLATILE(self)
    @property
    def Registers_Rc663_RxWaitReg14A848(self) -> Registers_Rc663_RxWaitReg14A848:
        """
        Specifies settings of the RxWaitReg register for 14A_848.
        """
        return Registers_Rc663_RxWaitReg14A848(self)
    @property
    def Registers_Rc663_RxWaitReg14A424(self) -> Registers_Rc663_RxWaitReg14A424:
        """
        Specifies settings of the RxWaitReg register for 14A_424.
        """
        return Registers_Rc663_RxWaitReg14A424(self)
    @property
    def Registers_Rc663_RxWaitReg14A212(self) -> Registers_Rc663_RxWaitReg14A212:
        """
        Specifies settings of the RxWaitReg register for 14A_212.
        """
        return Registers_Rc663_RxWaitReg14A212(self)
    @property
    def Registers_Rc663_RxWaitReg14A106(self) -> Registers_Rc663_RxWaitReg14A106:
        """
        Specifies settings of the RxWaitReg register for 14A_106.
        """
        return Registers_Rc663_RxWaitReg14A106(self)
    @property
    def Registers_Rc663_RxWaitReg14B848(self) -> Registers_Rc663_RxWaitReg14B848:
        """
        Specifies settings of the RxWaitReg register for 14B_848.
        """
        return Registers_Rc663_RxWaitReg14B848(self)
    @property
    def Registers_Rc663_RxWaitReg14B424(self) -> Registers_Rc663_RxWaitReg14B424:
        """
        Specifies settings of the RxWaitReg register for 14B_424.
        """
        return Registers_Rc663_RxWaitReg14B424(self)
    @property
    def Registers_Rc663_RxWaitReg14B212(self) -> Registers_Rc663_RxWaitReg14B212:
        """
        Specifies settings of the RxWaitReg register for 14B_212.
        """
        return Registers_Rc663_RxWaitReg14B212(self)
    @property
    def Registers_Rc663_RxWaitReg14B106(self) -> Registers_Rc663_RxWaitReg14B106:
        """
        Specifies settings of the RxWaitReg register for 14B_106.
        """
        return Registers_Rc663_RxWaitReg14B106(self)
    @property
    def Registers_Rc663_RxWaitReg15(self) -> Registers_Rc663_RxWaitReg15:
        """
        Specifies settings of the RxWaitReg register for 15.
        """
        return Registers_Rc663_RxWaitReg15(self)
    @property
    def Registers_Rc663_RxWaitReg14A(self) -> Registers_Rc663_RxWaitReg14A:
        """
        Specifies settings of the RxWaitReg register for 14A.
        """
        return Registers_Rc663_RxWaitReg14A(self)
    @property
    def Registers_Rc663_RxWaitReg14B(self) -> Registers_Rc663_RxWaitReg14B:
        """
        Specifies settings of the RxWaitReg register for 14B.
        """
        return Registers_Rc663_RxWaitReg14B(self)
    @property
    def Registers_Rc663_RxWaitRegALL(self) -> Registers_Rc663_RxWaitRegALL:
        """
        Specifies settings of the RxWaitReg register for ALL.
        """
        return Registers_Rc663_RxWaitRegALL(self)
    @property
    def Registers_Rc663_RxWaitRegVOLATILE(self) -> Registers_Rc663_RxWaitRegVOLATILE:
        """
        Specifies settings of the RxWaitReg register for VOLATILE.
        """
        return Registers_Rc663_RxWaitRegVOLATILE(self)
    @property
    def Registers_Rc663_RcvReg14A848(self) -> Registers_Rc663_RcvReg14A848:
        """
        Specifies settings of the RcvReg register for 14A_848.
        """
        return Registers_Rc663_RcvReg14A848(self)
    @property
    def Registers_Rc663_RcvReg14A424(self) -> Registers_Rc663_RcvReg14A424:
        """
        Specifies settings of the RcvReg register for 14A_424.
        """
        return Registers_Rc663_RcvReg14A424(self)
    @property
    def Registers_Rc663_RcvReg14A212(self) -> Registers_Rc663_RcvReg14A212:
        """
        Specifies settings of the RcvReg register for 14A_212.
        """
        return Registers_Rc663_RcvReg14A212(self)
    @property
    def Registers_Rc663_RcvReg14A106(self) -> Registers_Rc663_RcvReg14A106:
        """
        Specifies settings of the RcvReg register for 14A_106.
        """
        return Registers_Rc663_RcvReg14A106(self)
    @property
    def Registers_Rc663_RcvReg14B848(self) -> Registers_Rc663_RcvReg14B848:
        """
        Specifies settings of the RcvReg register for 14B_848.
        """
        return Registers_Rc663_RcvReg14B848(self)
    @property
    def Registers_Rc663_RcvReg14B424(self) -> Registers_Rc663_RcvReg14B424:
        """
        Specifies settings of the RcvReg register for 14B_424.
        """
        return Registers_Rc663_RcvReg14B424(self)
    @property
    def Registers_Rc663_RcvReg14B212(self) -> Registers_Rc663_RcvReg14B212:
        """
        Specifies settings of the RcvReg register for 14B_212.
        """
        return Registers_Rc663_RcvReg14B212(self)
    @property
    def Registers_Rc663_RcvReg14B106(self) -> Registers_Rc663_RcvReg14B106:
        """
        Specifies settings of the RcvReg register for 14B_106.
        """
        return Registers_Rc663_RcvReg14B106(self)
    @property
    def Registers_Rc663_RcvReg15(self) -> Registers_Rc663_RcvReg15:
        """
        Specifies settings of the RcvReg register for 15.
        """
        return Registers_Rc663_RcvReg15(self)
    @property
    def Registers_Rc663_RcvReg14A(self) -> Registers_Rc663_RcvReg14A:
        """
        Specifies settings of the RcvReg register for 14A.
        """
        return Registers_Rc663_RcvReg14A(self)
    @property
    def Registers_Rc663_RcvReg14B(self) -> Registers_Rc663_RcvReg14B:
        """
        Specifies settings of the RcvReg register for 14B.
        """
        return Registers_Rc663_RcvReg14B(self)
    @property
    def Registers_Rc663_RcvRegALL(self) -> Registers_Rc663_RcvRegALL:
        """
        Specifies settings of the RcvReg register for ALL.
        """
        return Registers_Rc663_RcvRegALL(self)
    @property
    def Registers_Rc663_RcvRegVOLATILE(self) -> Registers_Rc663_RcvRegVOLATILE:
        """
        Specifies settings of the RcvReg register for VOLATILE.
        """
        return Registers_Rc663_RcvRegVOLATILE(self)
    @property
    def Registers_Rc663_SigOutReg14A848(self) -> Registers_Rc663_SigOutReg14A848:
        """
        Specifies settings of the SigOutReg register for 14A_848.
        """
        return Registers_Rc663_SigOutReg14A848(self)
    @property
    def Registers_Rc663_SigOutReg14A424(self) -> Registers_Rc663_SigOutReg14A424:
        """
        Specifies settings of the SigOutReg register for 14A_424.
        """
        return Registers_Rc663_SigOutReg14A424(self)
    @property
    def Registers_Rc663_SigOutReg14A212(self) -> Registers_Rc663_SigOutReg14A212:
        """
        Specifies settings of the SigOutReg register for 14A_212.
        """
        return Registers_Rc663_SigOutReg14A212(self)
    @property
    def Registers_Rc663_SigOutReg14A106(self) -> Registers_Rc663_SigOutReg14A106:
        """
        Specifies settings of the SigOutReg register for 14A_106.
        """
        return Registers_Rc663_SigOutReg14A106(self)
    @property
    def Registers_Rc663_SigOutReg14B848(self) -> Registers_Rc663_SigOutReg14B848:
        """
        Specifies settings of the SigOutReg register for 14B_848.
        """
        return Registers_Rc663_SigOutReg14B848(self)
    @property
    def Registers_Rc663_SigOutReg14B424(self) -> Registers_Rc663_SigOutReg14B424:
        """
        Specifies settings of the SigOutReg register for 14B_424.
        """
        return Registers_Rc663_SigOutReg14B424(self)
    @property
    def Registers_Rc663_SigOutReg14B212(self) -> Registers_Rc663_SigOutReg14B212:
        """
        Specifies settings of the SigOutReg register for 14B_212.
        """
        return Registers_Rc663_SigOutReg14B212(self)
    @property
    def Registers_Rc663_SigOutReg14B106(self) -> Registers_Rc663_SigOutReg14B106:
        """
        Specifies settings of the SigOutReg register for 14B_106.
        """
        return Registers_Rc663_SigOutReg14B106(self)
    @property
    def Registers_Rc663_SigOutReg15(self) -> Registers_Rc663_SigOutReg15:
        """
        Specifies settings of the SigOutReg register for 15.
        """
        return Registers_Rc663_SigOutReg15(self)
    @property
    def Registers_Rc663_SigOutReg14A(self) -> Registers_Rc663_SigOutReg14A:
        """
        Specifies settings of the SigOutReg register for 14A.
        """
        return Registers_Rc663_SigOutReg14A(self)
    @property
    def Registers_Rc663_SigOutReg14B(self) -> Registers_Rc663_SigOutReg14B:
        """
        Specifies settings of the SigOutReg register for 14B.
        """
        return Registers_Rc663_SigOutReg14B(self)
    @property
    def Registers_Rc663_SigOutRegALL(self) -> Registers_Rc663_SigOutRegALL:
        """
        Specifies settings of the SigOutReg register for ALL.
        """
        return Registers_Rc663_SigOutRegALL(self)
    @property
    def Registers_Rc663_SigOutRegVOLATILE(self) -> Registers_Rc663_SigOutRegVOLATILE:
        """
        Specifies settings of the SigOutReg register for VOLATILE.
        """
        return Registers_Rc663_SigOutRegVOLATILE(self)
    @property
    def Project(self) -> Project:
        """
        This masterkey contains all values specific to the RFID interface component
        apart from [Autoread](autoread.xml#Autoread), [VHL](vhl.xml#VhlCfg) and
        ProjectRegisters.
        """
        return Project(self)
    @property
    def Project_VhlSettings(self) -> Project_VhlSettings:
        """
        Contains all non-File specific VHL settings
        """
        return Project_VhlSettings(self)
    @property
    def Project_VhlSettings_ScanCardFamilies(self) -> Project_VhlSettings_ScanCardFamilies:
        """
        Defines a bitsmask that is used by VHLSelect() to restrict the frequencies and
        HF-protocols that are polled. This can speed up the scanning.
        
        **If not set this value defaults to 0xFFFF (=accept all card types) if
        neither[
        Device/VhlSettings125Khz/ScanCardTypes](card_125khz.xml#Device.VhlSettings125Khz.ScanCardTypes)
        ,[
        Project/VhlSettings125Khz/ScanCardTypesPart1](card_125khz.xml#Project.VhlSettings125Khz.ScanCardTypesPart1)
        nor[
        Project/VhlSettings125Khz/ScanCardTypesPart2](card_125khz.xml#Project.VhlSettings125Khz.ScanCardTypesPart2)
        are set. In the latter case it defaults to _125Khz_ .**
        """
        return Project_VhlSettings_ScanCardFamilies(self)
    @property
    def Project_VhlSettings_ForceReselect(self) -> Project_VhlSettings_ForceReselect:
        """
        Setting this value to True enforces a Reselect on every VHLSelect.
        """
        return Project_VhlSettings_ForceReselect(self)
    @property
    def Project_VhlSettings_DelayRequestATS(self) -> Project_VhlSettings_DelayRequestATS:
        """
        Specifies the delay in ms that shall be waited after detecting an ISO14443
        card and before requesting its ATS (Answer To Select).
        """
        return Project_VhlSettings_DelayRequestATS(self)
    @property
    def Project_VhlSettings_DelayPerformPPS(self) -> Project_VhlSettings_DelayPerformPPS:
        """
        Specifies the delay in ms that shall be waited after receiving the ATS of an
        ISO14443 card and before performing its PPS.
        """
        return Project_VhlSettings_DelayPerformPPS(self)
    @property
    def Project_VhlSettings_MaxBaudrateIso14443A(self) -> Project_VhlSettings_MaxBaudrateIso14443A:
        """
        When VHLSelect / autoread detects a Iso14443/A card it negotiates the send and
        the receive baudrate automatically. Usually it tries to communicate as fast as
        possible (that means as fast as the card is supporting). If the performance
        shall be limited (i.e. due to HF instabilities) this value can be used to set
        a Maximum value for DSI (=reader to card baudrate) and DRI (=card to reader
        baudrate).
        """
        return Project_VhlSettings_MaxBaudrateIso14443A(self)
    @property
    def Project_VhlSettings_MaxBaudrateIso14443B(self) -> Project_VhlSettings_MaxBaudrateIso14443B:
        """
        When VHLSelect / autoread detects a Iso14443/B card it negotiates the send and
        the receive baudrate automatically. Usually it tries to communicate as fast as
        possible (that means as fast as the card is supporting). If the performance
        shall be limited (i.e. due to HF instabilities) this value can be used to set
        a Maximum value for DSI (=reader to card baudrate) and DRI (=card to reader
        baudrate).
        """
        return Project_VhlSettings_MaxBaudrateIso14443B(self)
    @property
    def Project_VhlSettings_HighPrioTaglist(self) -> Project_VhlSettings_HighPrioTaglist:
        """
        If this list of card types exists card types will be prioritized in descending
        order.
        """
        return Project_VhlSettings_HighPrioTaglist(self)
    @property
    def Project_VhlSettings_HighPrioDelay(self) -> Project_VhlSettings_HighPrioDelay:
        """
        This parameter indicates the delay present between the scanning of different
        cards in the VHL priority list.
        """
        return Project_VhlSettings_HighPrioDelay(self)
    @property
    def Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder(self) -> Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder:
        """
        This parameter allows to enable a special handling for Legic CTC4096
        transponders by ignoring the ISO14443A and ISO15693 interfaces of this
        transponder.
        
        Legic CTC4096 transponders support several RFID interfaces (Legic prime,
        ISO14443A and optionally ISO15693). They behave similar like a multichip card.
        VHL normally addresses every interface successively thus returning a different
        card type and a different UID for each RF interface of the CTC.
        
        If this parameter is set to True, VHL ignores the ISO interfaces and handles a
        CTC transponder like a card that contains a Legic prime chip only.
        
        A common use case for this parameter is a configuration that reads UIDs via
        Autoread. In the normal case this configuration returns two/three UIDs on a
        CTC card presentation. If this parameter is set to True then only one UID is
        returned.
        """
        return Project_VhlSettings_HandleLegicCTCAsSinglePrimeTransponder(self)
    @property
    def Project_VhlSettings_PrioritizeCardFamilies(self) -> Project_VhlSettings_PrioritizeCardFamilies:
        """
        This value provides a bitmask of card families that shall be prioritized by
        [VHL.Select](../cmds/vhl.xml#VHL.Select) when more than one card is detected
        at same time.
        
        The reader guarantees that in case of presenting multiple cards at once always
        the prioritized card families are returned first.
        
        **If Autoread is used,[ CardFamilies](autoread.xml#Autoread.Rule.CardFamilies)
        in combination with[
        PrioritizationMode](autoread.xml#Autoread.Rule.PrioritizationMode) should be
        used instead.**
        """
        return Project_VhlSettings_PrioritizeCardFamilies(self)
    @property
    def Project_VhlSettings_PrioritizationTriggeringCardFamilies(self) -> Project_VhlSettings_PrioritizationTriggeringCardFamilies:
        """
        This value defines the card families which trigger the [prioritization
        mechanism](.#Project.VhlSettings.PrioritizeCardFamilies). Only if the reader
        detects a card which belongs to one of the specified card families, it checks
        for a [prioritized card](.#Project.VhlSettings.PrioritizeCardFamilies) which
        it would return instead of the originally detected card.
        
        If this value is not set, the reader applies the [prioritization
        mechanism](.#Project.VhlSettings.PrioritizeCardFamilies) to every detected
        card. Because the prioritization consumes additional time the processing speed
        can be optimized by defining this value and restricting the prioritization to
        the relevant cards only.
        
        **If Autoread is used,[ this configuration
        value](autoread.xml#Autoread.Rule.PrioritizationTriggeringCardFamilies) should
        be used instead.**
        """
        return Project_VhlSettings_PrioritizationTriggeringCardFamilies(self)
    @property
    def Project_VhlSettings_PrioritizeDelay(self) -> Project_VhlSettings_PrioritizeDelay:
        """
        Specifies the Time that shall be waited _after_ resetting the HF and _before_
        scannning for [prioritized card
        systems](.#Project.VhlSettings.PrioritizeCardFamilies)
        """
        return Project_VhlSettings_PrioritizeDelay(self)
    @property
    def Project_VhlSettings_ConfCardCardFamilies(self) -> Project_VhlSettings_ConfCardCardFamilies:
        """
        Specifies the card families that are scanned when searching for configuration
        cards. These card families will be scanned even if the corresponding card
        family is not included in
        [Project.VhlSettings.ScanCardFamilies](.#Project.VhlSettings.ScanCardFamilies).
        In the latter case detected cards that are non-configuration cards are
        ignored.
        """
        return Project_VhlSettings_ConfCardCardFamilies(self)
    @property
    def Project_VhlSettings_DesfireEV1RetryLoopTime(self) -> Project_VhlSettings_DesfireEV1RetryLoopTime:
        """
        If the card is not yet close enough to the reader for DESFire VHL.Read/Write,
        retries are carried out. The maximum time can be adjusted here.
        """
        return Project_VhlSettings_DesfireEV1RetryLoopTime(self)
    @property
    def Project_VhlSettings_Iso14aVasup(self) -> Project_VhlSettings_Iso14aVasup:
        """
        Specifies parameters for VASUP-A.
        """
        return Project_VhlSettings_Iso14aVasup(self)
    @property
    def Project_VhlSettingsLegic(self) -> Project_VhlSettingsLegic:
        """
        Contains generic settings for Legic Readers that are working with
        VHL/Autoread.
        """
        return Project_VhlSettingsLegic(self)
    @property
    def Project_VhlSettingsLegic_RfStdList(self) -> Project_VhlSettingsLegic_RfStdList:
        """
        **The support for this value has been discontinued in September 2017. It is
        included here only for compatibility reasons. Please use[
        VhlSettings.ScanCardFamilies](vhl.xml#Project.VhlSettings.ScanCardFamilies)
        instead.**
        
        List of RFID standards that VHLSelect() should account for. By
        restricting/ordering the supported RFID standards the detection speed can be
        increased/optimized especially for dual-chip cards.
        """
        return Project_VhlSettingsLegic_RfStdList(self)
    @property
    def Project_VhlSettingsLegic_TxpType(self) -> Project_VhlSettingsLegic_TxpType:
        """
        **The support for this value has been discontinued in September 2017. It is
        included here only for compatibility reasons.**
        
        List of transponder types that VHLSelect should account for. By default there
        is no restriction.
        """
        return Project_VhlSettingsLegic_TxpType(self)
    @property
    def Project_VhlSettingsLegic_TxpFamily(self) -> Project_VhlSettingsLegic_TxpFamily:
        """
        **The support for this value has been discontinued in September 2017. It is
        included here only for compatibility reasons.**
        
        List of transponder families that VHLSelect should account for. By default
        there is no restriction.
        """
        return Project_VhlSettingsLegic_TxpFamily(self)
    @property
    def Project_HidSam(self) -> Project_HidSam:
        """
        This subkey contains Hid SAM specific settings.
        """
        return Project_HidSam(self)
    @property
    def Project_HidSam_Confcard(self) -> Project_HidSam_Confcard:
        """
        Enables the reader to scan for HID configuration cards.
        """
        return Project_HidSam_Confcard(self)
    @property
    def Project_HidSam_ScanTime(self) -> Project_HidSam_ScanTime:
        """
        configures scan time for HID cards in ms after power up of the reader.
        """
        return Project_HidSam_ScanTime(self)
    @property
    def Project_HidSam_Retries(self) -> Project_HidSam_Retries:
        """
        retry counter for HID config cards
        """
        return Project_HidSam_Retries(self)
    @property
    def Project_VhlSettings125Khz(self) -> Project_VhlSettings125Khz:
        """
        Contains generic settings for 125kHz Reader that are working with
        VHL/Autoread.
        """
        return Project_VhlSettings125Khz(self)
    @property
    def Project_VhlSettings125Khz_ScanCardTypesPart1(self) -> Project_VhlSettings125Khz_ScanCardTypesPart1:
        """
        Defines a bitsmask that is used by VHLSelect() to restrict the HF-protocols
        that are polled. This can speed up the scanning. This is an extension to
        [Project/VhlSettings/ScanCardFamilies](vhl.xml#Project.VhlSettings.ScanCardFamilies).
        """
        return Project_VhlSettings125Khz_ScanCardTypesPart1(self)
    @property
    def Project_VhlSettings125Khz_ScanCardTypesPart2(self) -> Project_VhlSettings125Khz_ScanCardTypesPart2:
        """
        Defines a bitsmask that is used by VHLSelect() to restrict the HF-protocols
        that are polled. This can speed up the scanning. This is an extension to
        [Project/VhlSettings/ScanCardFamilies](vhl.xml#Project.VhlSettings.ScanCardFamilies).
        """
        return Project_VhlSettings125Khz_ScanCardTypesPart2(self)
    @property
    def Project_VhlSettings125Khz_TTFModType(self) -> Project_VhlSettings125Khz_TTFModType:
        """
        This value specifies the modulation type for the TTF card type.
        """
        return Project_VhlSettings125Khz_TTFModType(self)
    @property
    def Project_VhlSettings125Khz_TTFBaudrate(self) -> Project_VhlSettings125Khz_TTFBaudrate:
        """
        This value specifies the baud rate for the TTF card type. Currently, this
        value is only used for EM4100 cards.
        """
        return Project_VhlSettings125Khz_TTFBaudrate(self)
    @property
    def Project_VhlSettings125Khz_TTFHeaderLength(self) -> Project_VhlSettings125Khz_TTFHeaderLength:
        """
        Specifies the pattern length in bit, the reader searches for.
        """
        return Project_VhlSettings125Khz_TTFHeaderLength(self)
    @property
    def Project_VhlSettings125Khz_TTFHeader(self) -> Project_VhlSettings125Khz_TTFHeader:
        """
        Pattern which has to match to read a card successfully. The pattern length is
        specified by
        [Project/VhlSettings125Khz/TTFHeaderLength](.#Project.VhlSettings125Khz.TTFHeaderLength).
        """
        return Project_VhlSettings125Khz_TTFHeader(self)
    @property
    def Project_VhlSettings125Khz_TTFDataLength(self) -> Project_VhlSettings125Khz_TTFDataLength:
        """
        Card data length (includes also Pattern Length) to read.
        """
        return Project_VhlSettings125Khz_TTFDataLength(self)
    @property
    def Project_VhlSettings125Khz_TTFOkCounter(self) -> Project_VhlSettings125Khz_TTFOkCounter:
        """
        Number of consecutive successfully reads until a card searched by a pattern is
        reported as detected by VHL.
        """
        return Project_VhlSettings125Khz_TTFOkCounter(self)
    @property
    def Project_VhlSettings125Khz_IndaspDecode(self) -> Project_VhlSettings125Khz_IndaspDecode:
        """
        This value refers to a template for the data converter. It converts the raw
        data stream of Indala asp cards to a 26 bit wiegand format. Always 5 bytes are
        expected: Byte 0 and byte 4 contain the Wiegand parity bit, byte 1 the site
        code and byte 2/3 the serial number (MSByte first). (Baltech internal
        documentation: jira:EQT-229)
        """
        return Project_VhlSettings125Khz_IndaspDecode(self)
    @property
    def Project_VhlSettings125Khz_IndaspParityCheck(self) -> Project_VhlSettings125Khz_IndaspParityCheck:
        """
        This value disables parity checking of the 26 bit indala wiegand format.
        Parity checking is done after processing the template defined by
        [Project/VhlSettings125Khz/IndaspDecode](.#Project.VhlSettings125Khz.IndaspDecode).
        """
        return Project_VhlSettings125Khz_IndaspParityCheck(self)
    @property
    def Project_VhlSettings125Khz_IndaspOkCounter(self) -> Project_VhlSettings125Khz_IndaspOkCounter:
        """
        Number of consecutive successfully reads until a Indala ASP card is reported
        as detected by VHL.
        """
        return Project_VhlSettings125Khz_IndaspOkCounter(self)
    @property
    def Project_VhlSettings125Khz_AwidOkCounter(self) -> Project_VhlSettings125Khz_AwidOkCounter:
        """
        Number of consecutive successfully reads until a Awid card is reported as
        detected by VHL.
        """
        return Project_VhlSettings125Khz_AwidOkCounter(self)
    @property
    def Project_VhlSettings125Khz_HidProxOkCounter(self) -> Project_VhlSettings125Khz_HidProxOkCounter:
        """
        Number of consecutive successfully reads until a HID Prox card is reported as
        detected by VHL.
        """
        return Project_VhlSettings125Khz_HidProxOkCounter(self)
    @property
    def Project_VhlSettings125Khz_QuadrakeyOkCounter(self) -> Project_VhlSettings125Khz_QuadrakeyOkCounter:
        """
        Number of consecutive successfully reads until a Quadrakey card is reported as
        detected by VHL.
        """
        return Project_VhlSettings125Khz_QuadrakeyOkCounter(self)
    @property
    def Project_VhlSettings125Khz_IoproxOkCounter(self) -> Project_VhlSettings125Khz_IoproxOkCounter:
        """
        Number of consecutive successfully reads until a Ioprox card is reported as
        detected by VHL.
        """
        return Project_VhlSettings125Khz_IoproxOkCounter(self)
    @property
    def Project_VhlSettings125Khz_TTFReadStartpos(self) -> Project_VhlSettings125Khz_TTFReadStartpos:
        """
        Specifies Startbitposition of TTF bitstream.
        """
        return Project_VhlSettings125Khz_TTFReadStartpos(self)
    @property
    def Project_VhlSettings125Khz_HidProxSerialNrFormat(self) -> Project_VhlSettings125Khz_HidProxSerialNrFormat:
        """
        This value specifies the format that shall be used when the SerialNumber of a
        HID Prox card is returned via VhlGetSnr().
        
        **The default value for this settings has changed. In Firmware released until
        02/2014 the defaultvalue when _not_ specifying this value was _McmCompatible_
        .**
        """
        return Project_VhlSettings125Khz_HidProxSerialNrFormat(self)
    @property
    def Project_VhlSettings125Khz_ModType(self) -> Project_VhlSettings125Khz_ModType:
        """
        This value specifies the modulation type for some cards. Currently, this value
        is only used for EM4205 cards.
        """
        return Project_VhlSettings125Khz_ModType(self)
    @property
    def Project_VhlSettings125Khz_BaudRate(self) -> Project_VhlSettings125Khz_BaudRate:
        """
        This value specifies the baud rate for some cards. Currently, this value is
        only used for EM4100 / 4205 cards.
        """
        return Project_VhlSettings125Khz_BaudRate(self)
    @property
    def Project_VhlSettings125Khz_GenericOkCounter(self) -> Project_VhlSettings125Khz_GenericOkCounter:
        """
        Number of consecutive successfully reads until a TTF card is reported as
        detected by VHL.
        """
        return Project_VhlSettings125Khz_GenericOkCounter(self)
    @property
    def Project_VhlSettings125Khz_SnrVersionCotag(self) -> Project_VhlSettings125Khz_SnrVersionCotag:
        """
        Value allows several serial number versions.
        """
        return Project_VhlSettings125Khz_SnrVersionCotag(self)
    @property
    def Project_VhlSettings125Khz_SnrVersionIdteck(self) -> Project_VhlSettings125Khz_SnrVersionIdteck:
        """
        Value allows several serial number versions
        """
        return Project_VhlSettings125Khz_SnrVersionIdteck(self)
    @property
    def Project_VhlSettings125Khz_EM4100SerialNrFormat(self) -> Project_VhlSettings125Khz_EM4100SerialNrFormat:
        """
        This value specifies the format that shall be used when the SerialNumber of a
        EM 4100 card is returned via VhlGetSnr().
        """
        return Project_VhlSettings125Khz_EM4100SerialNrFormat(self)
    @property
    def Project_VhlSettings125Khz_AwidSerialNrFormat(self) -> Project_VhlSettings125Khz_AwidSerialNrFormat:
        """
        This value specifies the format that shall be used when the SerialNumber of a
        Awid card is returned via VhlGetSnr().
        """
        return Project_VhlSettings125Khz_AwidSerialNrFormat(self)
    @property
    def Project_VhlSettings125Khz_IoProxSerialNrFormat(self) -> Project_VhlSettings125Khz_IoProxSerialNrFormat:
        """
        This value specifies the format that shall be used when the SerialNumber of a
        IoProx card is returned via [VHL.GetSnr](../cmds/vhl.xml#VHL.GetSnr).
        """
        return Project_VhlSettings125Khz_IoProxSerialNrFormat(self)
    @property
    def Project_VhlSettings125Khz_PyramidSerialNrFormat(self) -> Project_VhlSettings125Khz_PyramidSerialNrFormat:
        """
        This value specifies the format that shall be used when the serial number of a
        Farpointe Pyramid card is returned via
        [VHL.GetSnr](../cmds/vhl.xml#VHL.GetSnr).
        """
        return Project_VhlSettings125Khz_PyramidSerialNrFormat(self)
    @property
    def Project_SamAVx(self) -> Project_SamAVx:
        """
        Desfire AVx SAM specific configuration values
        """
        return Project_SamAVx(self)
    @property
    def Project_SamAVx_PowerUpState(self) -> Project_SamAVx_PowerUpState:
        """
        SAM Keyidx to unlock SAM.
        """
        return Project_SamAVx_PowerUpState(self)
    @property
    def Project_SamAVx_UnlockKeyNr(self) -> Project_SamAVx_UnlockKeyNr:
        """
        SAM Key number of the unlock key.
        """
        return Project_SamAVx_UnlockKeyNr(self)
    @property
    def Project_SamAVx_UnlockKeyVersion(self) -> Project_SamAVx_UnlockKeyVersion:
        """
        SAM key version of the unlock key.
        """
        return Project_SamAVx_UnlockKeyVersion(self)
    @property
    def Project_SamAVx_UnlockKeyCryptoMemoryIdx(self) -> Project_SamAVx_UnlockKeyCryptoMemoryIdx:
        """
        Keyindex to the project crypto memory to unlock the SAM
        """
        return Project_SamAVx_UnlockKeyCryptoMemoryIdx(self)
    @property
    def Project_SamAVx_AuthKeyNr(self) -> Project_SamAVx_AuthKeyNr:
        """
        SAM Key number to authenticate SAM.
        """
        return Project_SamAVx_AuthKeyNr(self)
    @property
    def Project_SamAVx_AuthKeyVersion(self) -> Project_SamAVx_AuthKeyVersion:
        """
        SAM key version of the authentication key.
        """
        return Project_SamAVx_AuthKeyVersion(self)
    @property
    def Project_SamAVx_AuthKeyCryptoMemoryIdx(self) -> Project_SamAVx_AuthKeyCryptoMemoryIdx:
        """
        Keyindex to the project crypto memory to authenticate the SAM
        """
        return Project_SamAVx_AuthKeyCryptoMemoryIdx(self)
    @property
    def Project_SamAVx_SecureMessaging(self) -> Project_SamAVx_SecureMessaging:
        """
        SAM secure messaging mode
        """
        return Project_SamAVx_SecureMessaging(self)
    @property
    def Project_CryptoKey(self) -> Project_CryptoKey:
        """
        Key container used by the crypto manager for crypto operations.
        """
        return Project_CryptoKey(self)
    @property
    def Project_CryptoKey_Entry(self) -> Project_CryptoKey_Entry:
        """
        Key entry which contains a key and its according CryptoOptions with
        KeyAccessRights used by the crypto manager.
        """
        return Project_CryptoKey_Entry(self)
    @property
    def Project_DiversificationData(self) -> Project_DiversificationData:
        """
        Data converter rules for diversification data generation
        """
        return Project_DiversificationData(self)
    @property
    def Project_DiversificationData_Entry(self) -> Project_DiversificationData_Entry:
        """
        Entry contains a rule processed by the data converter. For card number
        generation only SerialNumber is supported.
        """
        return Project_DiversificationData_Entry(self)
    @property
    def Project_SamAVxKeySettings(self) -> Project_SamAVxKeySettings:
        """
        Extensions for AV2/3 SAM key entries
        """
        return Project_SamAVxKeySettings(self)
    @property
    def Project_SamAVxKeySettings_Index(self) -> Project_SamAVxKeySettings_Index:
        """
        This entry expands a sam key index about additional diversification settings.
        """
        return Project_SamAVxKeySettings_Index(self)
    @property
    def Project_Bluetooth(self) -> Project_Bluetooth:
        """
        This key contains values that allow parameterizing Bluetooth Low Energy
        functionality.
        """
        return Project_Bluetooth(self)
    @property
    def Project_Bluetooth_DiscoveryMode(self) -> Project_Bluetooth_DiscoveryMode:
        """
        This value defines the Generic Access Profile (GAP) discovery mode of the BLE
        reader device.
        """
        return Project_Bluetooth_DiscoveryMode(self)
    @property
    def Project_Bluetooth_ConnectionMode(self) -> Project_Bluetooth_ConnectionMode:
        """
        This value defines the Generic Access Profile (GAP) connection mode of the BLE
        reader device.
        """
        return Project_Bluetooth_ConnectionMode(self)
    @property
    def Project_Bluetooth_AdvertisementData(self) -> Project_Bluetooth_AdvertisementData:
        """
        This value defines the advertisement data which shall be contained in the
        Protocol Data Unit (PDU) of the GAP advertising packet.
        """
        return Project_Bluetooth_AdvertisementData(self)
    @property
    def Project_Bluetooth_ScanResponseData(self) -> Project_Bluetooth_ScanResponseData:
        """
        This value defines the scan response data which the device shall send in
        response to a Scan Request from a BLE central device. It usually contains the
        device name or services that couldn't be placed in the advertising packet.
        """
        return Project_Bluetooth_ScanResponseData(self)
    @property
    def Project_Bluetooth_MinAdvertisingInterval(self) -> Project_Bluetooth_MinAdvertisingInterval:
        """
        Minimum interval in units of 0.625 ms for advertisement packets to be sent by
        the device.
        """
        return Project_Bluetooth_MinAdvertisingInterval(self)
    @property
    def Project_Bluetooth_MaxAdvertisingInterval(self) -> Project_Bluetooth_MaxAdvertisingInterval:
        """
        Maximum interval in units of 0.625 ms for advertisement packets to be sent by
        the device.
        
        This value must be chosen at least equal or greater than
        [Project/Bluetooth/MinAdvertisingInterval](.#Project.Bluetooth.MinAdvertisingInterval)!
        """
        return Project_Bluetooth_MaxAdvertisingInterval(self)
    @property
    def Project_Bluetooth_AdvertizingChannels(self) -> Project_Bluetooth_AdvertizingChannels:
        """
        This value specifies which of the three available channels should be used for
        advertizing.
        """
        return Project_Bluetooth_AdvertizingChannels(self)
    @property
    def Project_Bluetooth_MinConnectionInterval(self) -> Project_Bluetooth_MinConnectionInterval:
        """
        Minimum value for the connection event interval in units of 1.25 ms.
        """
        return Project_Bluetooth_MinConnectionInterval(self)
    @property
    def Project_Bluetooth_MaxConnectionInterval(self) -> Project_Bluetooth_MaxConnectionInterval:
        """
        Maximum value for the connection event interval in units of 1.25 ms.
        
        This value must be chosen at least equal or greater than
        [Project/Bluetooth/MinConnectionInterval](.#Project.Bluetooth.MinConnectionInterval)!
        """
        return Project_Bluetooth_MaxConnectionInterval(self)
    @property
    def Project_Bluetooth_ConnectionSupervisionTimeout(self) -> Project_Bluetooth_ConnectionSupervisionTimeout:
        """
        This value specifies the supervision timeout in units of 10 ms. This timeout
        defines for how long a connection is maintained despite the device being
        unable to communicate at the currently configured connection intervals.
        
        It is recommended that the supervision timeout is set at a value which allows
        communication attempts over at least a few connection intervals.
        """
        return Project_Bluetooth_ConnectionSupervisionTimeout(self)
    @property
    def Project_Bluetooth_DeviceNameLegacy(self) -> Project_Bluetooth_DeviceNameLegacy:
        """
        This value was used to define the Generic Access Profile (GAP) characteristic
        Device Name, which is advertized by the reader. It is replaced by
        [Project.Bluetooth.AdvertizedDeviceName](.#Project.Bluetooth.AdvertizedDeviceName).
        """
        return Project_Bluetooth_DeviceNameLegacy(self)
    @property
    def Project_Bluetooth_Appearance(self) -> Project_Bluetooth_Appearance:
        """
        This value defines the Generic Access Profile (GAP) characteristic Appearance.
        This value is readable from a BLE GATT client by accessing the GAP profile of
        the device.
        """
        return Project_Bluetooth_Appearance(self)
    @property
    def Project_Bluetooth_AdvertizedDeviceName(self) -> Project_Bluetooth_AdvertizedDeviceName:
        """
        This value defines the Generic Access Profile (GAP) characteristic Device
        Name, which is advertized by the reader.
        
        This value is a template which allows you to insert the reader serial number
        or the Bluetooth MAC address (use SerialNr for this purpose) into the name
        string.
        
        **The length of the resulting string may not exceed 24 digits!**
        """
        return Project_Bluetooth_AdvertizedDeviceName(self)
    @property
    def Project_Mce(self) -> Project_Mce:
        """
        This key contains values to set up the Mobile Card Emulation (MCE)
        functionality.
        """
        return Project_Mce(self)
    @property
    def Project_Mce_Mode(self) -> Project_Mce_Mode:
        """
        This value allows you to enable/disable MCE.
        """
        return Project_Mce_Mode(self)
    @property
    def Project_MobileId(self) -> Project_MobileId:
        """
        This key contains values that allow you to set up the Mobile ID functionality
        to read Mobile ID credentials using Autoread.
        """
        return Project_MobileId(self)
    @property
    def Project_MobileId_Mode(self) -> Project_MobileId_Mode:
        """
        This value enables/disables Mobile ID within Autoread.
        """
        return Project_MobileId_Mode(self)
    @property
    def Project_MobileId_DisplayName(self) -> Project_MobileId_DisplayName:
        """
        This value defines a human-readable name of the reader (ASCII string), which
        is reported to the Mobile ID app directly after the connection is established.
        
        The value may be used in combination with the [Trigger from
        Distance](.#Project.MobileId.TriggerFromDistance) capability. Displayed on the
        mobile device, the name allows the user to identify the reader to be triggered
        at the touch af a button.
        
        **The name can be a maximum of 48 characters long.**
        """
        return Project_MobileId_DisplayName(self)
    @property
    def Project_MobileId_TriggerFromDistance(self) -> Project_MobileId_TriggerFromDistance:
        """
        This value indicates if the reader can be triggered from a distance, i.e. by a
        trigger moment other than sufficient proximity to the reader (RSSI). It
        corresponds to the _Remote_ option in the _User Interaction_ dropdown in the
        Mobile ID configuration component in BALTECH ConfigEditor.
        
        The Trigger from Distance capability is reported to the Mobile ID app after
        the connection is established. If set, the app may use this information to
        define its own trigger moment, e.g. a button press by the user.
        """
        return Project_MobileId_TriggerFromDistance(self)
    @property
    def Project_MobileId_ConvenientAccess(self) -> Project_MobileId_ConvenientAccess:
        """
        This value indicates if the reader supports the Convenient Access capability
        of Mobile ID. If enabled, the reader can be triggered with the phone left in
        the pocket. This value corresponds to the _Convenient_ option in the _User
        Interaction_ dropdown in the Mobile ID configuration component in BALTECH
        ConfigEditor.
        """
        return Project_MobileId_ConvenientAccess(self)
    @property
    def Project_MobileId_AdvertisementFilter(self) -> Project_MobileId_AdvertisementFilter:
        """
        This value enables/disables the advertisement filter of the Mobile ID
        protocol. The filter ensures that only devices are processed that send
        advertisement data containing the Mobile ID service UUID or manufacturer-
        specific data with the Apple company ID (0x004C).
        
        **The advertisement filter is only applied to devices with an RSSI below the
        activation threshold. The filter is overridden if the RSSI exceeds this
        threshold.**
        """
        return Project_MobileId_AdvertisementFilter(self)
    @property
    def Project_MobileId_RssiCorrectionConvenientAccess(self) -> Project_MobileId_RssiCorrectionConvenientAccess:
        """
        This is an RSSI offset that will be taken into account to compensate reader
        model/environment-specific variations in Convenient Access mode.
        """
        return Project_MobileId_RssiCorrectionConvenientAccess(self)
    @property
    def Project_MobileId_DetectionRssiFilter(self) -> Project_MobileId_DetectionRssiFilter:
        """
        This value enables/disables the detection RSSI filter of the Mobile ID
        protocol. The filter ensures that only devices are processed that exceed a
        minimum RSSI dependent on the reader model.
        """
        return Project_MobileId_DetectionRssiFilter(self)
    @property
    def Project_MobileId_MsgType(self) -> Project_MobileId_MsgType:
        """
        This value defines the message type that the command
        [AR.GetMessage](../cmds/autoread.xml#AR.GetMessage) returns when a Mobile ID
        credential is detected.
        """
        return Project_MobileId_MsgType(self)
    @property
    def Project_MobileId_OnMatchEvent(self) -> Project_MobileId_OnMatchEvent:
        """
        This event is fired when a Mobile ID credential is presented. If the script
        that is executed on this event contains a _DefaultAction_ , one of the
        following events will be fired subsequently:
        
          * [OnAccepted](autoread.xml#Scripts.Events.OnAccepted)
          * [OnMatchMsg[X]](autoread.xml#Scripts.Events.OnMatchMsg)
          * [OnInvalidCard](autoread.xml#Scripts.Events.OnInvalidCard)
        
        **If the script contains no _DefaultAction_ , the events listed above will be
        omitted.**
        """
        return Project_MobileId_OnMatchEvent(self)
    @property
    def Project_MobileId_Key(self) -> Project_MobileId_Key:
        """
        These values define a list of one or more project-specific Mobile ID
        encryption keys.
        """
        return Project_MobileId_Key(self)
    @property
    def ProjectRegisters(self) -> ProjectRegisters:
        """
        This masterkey contains all values specific to the RFID interface component
        for register management (see also [Registers](.#Registers).
        """
        return ProjectRegisters(self)
    @property
    def ProjectRegisters_Rc(self) -> ProjectRegisters_Rc:
        """
        This value contains HF Settings (Register Settings) of the RC500 / RC400 /
        RC632 reader chip.
        """
        return ProjectRegisters_Rc(self)
    @property
    def ProjectRegisters_Rc_TxControl14A848(self) -> ProjectRegisters_Rc_TxControl14A848:
        """
        Specifies settings of the TxControl register for 14A_848.
        """
        return ProjectRegisters_Rc_TxControl14A848(self)
    @property
    def ProjectRegisters_Rc_TxControl14A424(self) -> ProjectRegisters_Rc_TxControl14A424:
        """
        Specifies settings of the TxControl register for 14A_424.
        """
        return ProjectRegisters_Rc_TxControl14A424(self)
    @property
    def ProjectRegisters_Rc_TxControl14A212(self) -> ProjectRegisters_Rc_TxControl14A212:
        """
        Specifies settings of the TxControl register for 14A_212.
        """
        return ProjectRegisters_Rc_TxControl14A212(self)
    @property
    def ProjectRegisters_Rc_TxControl14A106(self) -> ProjectRegisters_Rc_TxControl14A106:
        """
        Specifies settings of the TxControl register for 14A_106.
        """
        return ProjectRegisters_Rc_TxControl14A106(self)
    @property
    def ProjectRegisters_Rc_TxControl14B848(self) -> ProjectRegisters_Rc_TxControl14B848:
        """
        Specifies settings of the TxControl register for 14B_848.
        """
        return ProjectRegisters_Rc_TxControl14B848(self)
    @property
    def ProjectRegisters_Rc_TxControl14B424(self) -> ProjectRegisters_Rc_TxControl14B424:
        """
        Specifies settings of the TxControl register for 14B_424.
        """
        return ProjectRegisters_Rc_TxControl14B424(self)
    @property
    def ProjectRegisters_Rc_TxControl14B212(self) -> ProjectRegisters_Rc_TxControl14B212:
        """
        Specifies settings of the TxControl register for 14B_212.
        """
        return ProjectRegisters_Rc_TxControl14B212(self)
    @property
    def ProjectRegisters_Rc_TxControl14B106(self) -> ProjectRegisters_Rc_TxControl14B106:
        """
        Specifies settings of the TxControl register for 14B_106.
        """
        return ProjectRegisters_Rc_TxControl14B106(self)
    @property
    def ProjectRegisters_Rc_TxControl15Standard(self) -> ProjectRegisters_Rc_TxControl15Standard:
        """
        Specifies settings of the TxControl register for 15Standard.
        """
        return ProjectRegisters_Rc_TxControl15Standard(self)
    @property
    def ProjectRegisters_Rc_TxControl15Fast(self) -> ProjectRegisters_Rc_TxControl15Fast:
        """
        Specifies settings of the TxControl register for 15Fast.
        """
        return ProjectRegisters_Rc_TxControl15Fast(self)
    @property
    def ProjectRegisters_Rc_TxControl14A(self) -> ProjectRegisters_Rc_TxControl14A:
        """
        Specifies settings of the TxControl register for 14A.
        """
        return ProjectRegisters_Rc_TxControl14A(self)
    @property
    def ProjectRegisters_Rc_TxControl14B(self) -> ProjectRegisters_Rc_TxControl14B:
        """
        Specifies settings of the TxControl register for 14B.
        """
        return ProjectRegisters_Rc_TxControl14B(self)
    @property
    def ProjectRegisters_Rc_TxControl15(self) -> ProjectRegisters_Rc_TxControl15:
        """
        Specifies settings of the TxControl register for 15.
        """
        return ProjectRegisters_Rc_TxControl15(self)
    @property
    def ProjectRegisters_Rc_TxControlALL(self) -> ProjectRegisters_Rc_TxControlALL:
        """
        Specifies settings of the TxControl register for ALL.
        """
        return ProjectRegisters_Rc_TxControlALL(self)
    @property
    def ProjectRegisters_Rc_TxControlVOLATILE(self) -> ProjectRegisters_Rc_TxControlVOLATILE:
        """
        Specifies settings of the TxControl register for VOLATILE.
        """
        return ProjectRegisters_Rc_TxControlVOLATILE(self)
    @property
    def ProjectRegisters_Rc_CwConductance14A848(self) -> ProjectRegisters_Rc_CwConductance14A848:
        """
        Specifies settings of the CwConductance register for 14A_848.
        """
        return ProjectRegisters_Rc_CwConductance14A848(self)
    @property
    def ProjectRegisters_Rc_CwConductance14A424(self) -> ProjectRegisters_Rc_CwConductance14A424:
        """
        Specifies settings of the CwConductance register for 14A_424.
        """
        return ProjectRegisters_Rc_CwConductance14A424(self)
    @property
    def ProjectRegisters_Rc_CwConductance14A212(self) -> ProjectRegisters_Rc_CwConductance14A212:
        """
        Specifies settings of the CwConductance register for 14A_212.
        """
        return ProjectRegisters_Rc_CwConductance14A212(self)
    @property
    def ProjectRegisters_Rc_CwConductance14A106(self) -> ProjectRegisters_Rc_CwConductance14A106:
        """
        Specifies settings of the CwConductance register for 14A_106.
        """
        return ProjectRegisters_Rc_CwConductance14A106(self)
    @property
    def ProjectRegisters_Rc_CwConductance14B848(self) -> ProjectRegisters_Rc_CwConductance14B848:
        """
        Specifies settings of the CwConductance register for 14B_848.
        """
        return ProjectRegisters_Rc_CwConductance14B848(self)
    @property
    def ProjectRegisters_Rc_CwConductance14B424(self) -> ProjectRegisters_Rc_CwConductance14B424:
        """
        Specifies settings of the CwConductance register for 14B_424.
        """
        return ProjectRegisters_Rc_CwConductance14B424(self)
    @property
    def ProjectRegisters_Rc_CwConductance14B212(self) -> ProjectRegisters_Rc_CwConductance14B212:
        """
        Specifies settings of the CwConductance register for 14B_212.
        """
        return ProjectRegisters_Rc_CwConductance14B212(self)
    @property
    def ProjectRegisters_Rc_CwConductance14B106(self) -> ProjectRegisters_Rc_CwConductance14B106:
        """
        Specifies settings of the CwConductance register for 14B_106.
        """
        return ProjectRegisters_Rc_CwConductance14B106(self)
    @property
    def ProjectRegisters_Rc_CwConductance15Standard(self) -> ProjectRegisters_Rc_CwConductance15Standard:
        """
        Specifies settings of the CwConductance register for 15Standard.
        """
        return ProjectRegisters_Rc_CwConductance15Standard(self)
    @property
    def ProjectRegisters_Rc_CwConductance15Fast(self) -> ProjectRegisters_Rc_CwConductance15Fast:
        """
        Specifies settings of the CwConductance register for 15Fast.
        """
        return ProjectRegisters_Rc_CwConductance15Fast(self)
    @property
    def ProjectRegisters_Rc_CwConductance14A(self) -> ProjectRegisters_Rc_CwConductance14A:
        """
        Specifies settings of the CwConductance register for 14A.
        """
        return ProjectRegisters_Rc_CwConductance14A(self)
    @property
    def ProjectRegisters_Rc_CwConductance14B(self) -> ProjectRegisters_Rc_CwConductance14B:
        """
        Specifies settings of the CwConductance register for 14B.
        """
        return ProjectRegisters_Rc_CwConductance14B(self)
    @property
    def ProjectRegisters_Rc_CwConductance15(self) -> ProjectRegisters_Rc_CwConductance15:
        """
        Specifies settings of the CwConductance register for 15.
        """
        return ProjectRegisters_Rc_CwConductance15(self)
    @property
    def ProjectRegisters_Rc_CwConductanceALL(self) -> ProjectRegisters_Rc_CwConductanceALL:
        """
        Specifies settings of the CwConductance register for ALL.
        """
        return ProjectRegisters_Rc_CwConductanceALL(self)
    @property
    def ProjectRegisters_Rc_CwConductanceVOLATILE(self) -> ProjectRegisters_Rc_CwConductanceVOLATILE:
        """
        Specifies settings of the CwConductance register for VOLATILE.
        """
        return ProjectRegisters_Rc_CwConductanceVOLATILE(self)
    @property
    def ProjectRegisters_Rc_ModConductance14A848(self) -> ProjectRegisters_Rc_ModConductance14A848:
        """
        Specifies settings of the ModConductance register for 14A_848.
        """
        return ProjectRegisters_Rc_ModConductance14A848(self)
    @property
    def ProjectRegisters_Rc_ModConductance14A424(self) -> ProjectRegisters_Rc_ModConductance14A424:
        """
        Specifies settings of the ModConductance register for 14A_424.
        """
        return ProjectRegisters_Rc_ModConductance14A424(self)
    @property
    def ProjectRegisters_Rc_ModConductance14A212(self) -> ProjectRegisters_Rc_ModConductance14A212:
        """
        Specifies settings of the ModConductance register for 14A_212.
        """
        return ProjectRegisters_Rc_ModConductance14A212(self)
    @property
    def ProjectRegisters_Rc_ModConductance14A106(self) -> ProjectRegisters_Rc_ModConductance14A106:
        """
        Specifies settings of the ModConductance register for 14A_106.
        """
        return ProjectRegisters_Rc_ModConductance14A106(self)
    @property
    def ProjectRegisters_Rc_ModConductance14B848(self) -> ProjectRegisters_Rc_ModConductance14B848:
        """
        Specifies settings of the ModConductance register for 14B_848.
        """
        return ProjectRegisters_Rc_ModConductance14B848(self)
    @property
    def ProjectRegisters_Rc_ModConductance14B424(self) -> ProjectRegisters_Rc_ModConductance14B424:
        """
        Specifies settings of the ModConductance register for 14B_424.
        """
        return ProjectRegisters_Rc_ModConductance14B424(self)
    @property
    def ProjectRegisters_Rc_ModConductance14B212(self) -> ProjectRegisters_Rc_ModConductance14B212:
        """
        Specifies settings of the ModConductance register for 14B_212.
        """
        return ProjectRegisters_Rc_ModConductance14B212(self)
    @property
    def ProjectRegisters_Rc_ModConductance14B106(self) -> ProjectRegisters_Rc_ModConductance14B106:
        """
        Specifies settings of the ModConductance register for 14B_106.
        """
        return ProjectRegisters_Rc_ModConductance14B106(self)
    @property
    def ProjectRegisters_Rc_ModConductance15Standard(self) -> ProjectRegisters_Rc_ModConductance15Standard:
        """
        Specifies settings of the ModConductance register for 15Standard.
        """
        return ProjectRegisters_Rc_ModConductance15Standard(self)
    @property
    def ProjectRegisters_Rc_ModConductance15Fast(self) -> ProjectRegisters_Rc_ModConductance15Fast:
        """
        Specifies settings of the ModConductance register for 15Fast.
        """
        return ProjectRegisters_Rc_ModConductance15Fast(self)
    @property
    def ProjectRegisters_Rc_ModConductance14A(self) -> ProjectRegisters_Rc_ModConductance14A:
        """
        Specifies settings of the ModConductance register for 14A.
        """
        return ProjectRegisters_Rc_ModConductance14A(self)
    @property
    def ProjectRegisters_Rc_ModConductance14B(self) -> ProjectRegisters_Rc_ModConductance14B:
        """
        Specifies settings of the ModConductance register for 14B.
        """
        return ProjectRegisters_Rc_ModConductance14B(self)
    @property
    def ProjectRegisters_Rc_ModConductance15(self) -> ProjectRegisters_Rc_ModConductance15:
        """
        Specifies settings of the ModConductance register for 15.
        """
        return ProjectRegisters_Rc_ModConductance15(self)
    @property
    def ProjectRegisters_Rc_ModConductanceALL(self) -> ProjectRegisters_Rc_ModConductanceALL:
        """
        Specifies settings of the ModConductance register for ALL.
        """
        return ProjectRegisters_Rc_ModConductanceALL(self)
    @property
    def ProjectRegisters_Rc_ModConductanceVOLATILE(self) -> ProjectRegisters_Rc_ModConductanceVOLATILE:
        """
        Specifies settings of the ModConductance register for VOLATILE.
        """
        return ProjectRegisters_Rc_ModConductanceVOLATILE(self)
    @property
    def ProjectRegisters_Rc_ModWidth14A848(self) -> ProjectRegisters_Rc_ModWidth14A848:
        """
        Specifies settings of the ModWidth register for 14A_848.
        """
        return ProjectRegisters_Rc_ModWidth14A848(self)
    @property
    def ProjectRegisters_Rc_ModWidth14A424(self) -> ProjectRegisters_Rc_ModWidth14A424:
        """
        Specifies settings of the ModWidth register for 14A_424.
        """
        return ProjectRegisters_Rc_ModWidth14A424(self)
    @property
    def ProjectRegisters_Rc_ModWidth14A212(self) -> ProjectRegisters_Rc_ModWidth14A212:
        """
        Specifies settings of the ModWidth register for 14A_212.
        """
        return ProjectRegisters_Rc_ModWidth14A212(self)
    @property
    def ProjectRegisters_Rc_ModWidth14A106(self) -> ProjectRegisters_Rc_ModWidth14A106:
        """
        Specifies settings of the ModWidth register for 14A_106.
        """
        return ProjectRegisters_Rc_ModWidth14A106(self)
    @property
    def ProjectRegisters_Rc_ModWidth14B848(self) -> ProjectRegisters_Rc_ModWidth14B848:
        """
        Specifies settings of the ModWidth register for 14B_848.
        """
        return ProjectRegisters_Rc_ModWidth14B848(self)
    @property
    def ProjectRegisters_Rc_ModWidth14B424(self) -> ProjectRegisters_Rc_ModWidth14B424:
        """
        Specifies settings of the ModWidth register for 14B_424.
        """
        return ProjectRegisters_Rc_ModWidth14B424(self)
    @property
    def ProjectRegisters_Rc_ModWidth14B212(self) -> ProjectRegisters_Rc_ModWidth14B212:
        """
        Specifies settings of the ModWidth register for 14B_212.
        """
        return ProjectRegisters_Rc_ModWidth14B212(self)
    @property
    def ProjectRegisters_Rc_ModWidth14B106(self) -> ProjectRegisters_Rc_ModWidth14B106:
        """
        Specifies settings of the ModWidth register for 14B_106.
        """
        return ProjectRegisters_Rc_ModWidth14B106(self)
    @property
    def ProjectRegisters_Rc_ModWidth15Standard(self) -> ProjectRegisters_Rc_ModWidth15Standard:
        """
        Specifies settings of the ModWidth register for 15Standard.
        """
        return ProjectRegisters_Rc_ModWidth15Standard(self)
    @property
    def ProjectRegisters_Rc_ModWidth15Fast(self) -> ProjectRegisters_Rc_ModWidth15Fast:
        """
        Specifies settings of the ModWidth register for 15Fast.
        """
        return ProjectRegisters_Rc_ModWidth15Fast(self)
    @property
    def ProjectRegisters_Rc_ModWidth14A(self) -> ProjectRegisters_Rc_ModWidth14A:
        """
        Specifies settings of the ModWidth register for 14A.
        """
        return ProjectRegisters_Rc_ModWidth14A(self)
    @property
    def ProjectRegisters_Rc_ModWidth14B(self) -> ProjectRegisters_Rc_ModWidth14B:
        """
        Specifies settings of the ModWidth register for 14B.
        """
        return ProjectRegisters_Rc_ModWidth14B(self)
    @property
    def ProjectRegisters_Rc_ModWidth15(self) -> ProjectRegisters_Rc_ModWidth15:
        """
        Specifies settings of the ModWidth register for 15.
        """
        return ProjectRegisters_Rc_ModWidth15(self)
    @property
    def ProjectRegisters_Rc_ModWidthALL(self) -> ProjectRegisters_Rc_ModWidthALL:
        """
        Specifies settings of the ModWidth register for ALL.
        """
        return ProjectRegisters_Rc_ModWidthALL(self)
    @property
    def ProjectRegisters_Rc_ModWidthVOLATILE(self) -> ProjectRegisters_Rc_ModWidthVOLATILE:
        """
        Specifies settings of the ModWidth register for VOLATILE.
        """
        return ProjectRegisters_Rc_ModWidthVOLATILE(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14A848(self) -> ProjectRegisters_Rc_ModWidthSOF14A848:
        """
        Specifies settings of the ModWidthSOF register for 14A_848.
        """
        return ProjectRegisters_Rc_ModWidthSOF14A848(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14A424(self) -> ProjectRegisters_Rc_ModWidthSOF14A424:
        """
        Specifies settings of the ModWidthSOF register for 14A_424.
        """
        return ProjectRegisters_Rc_ModWidthSOF14A424(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14A212(self) -> ProjectRegisters_Rc_ModWidthSOF14A212:
        """
        Specifies settings of the ModWidthSOF register for 14A_212.
        """
        return ProjectRegisters_Rc_ModWidthSOF14A212(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14A106(self) -> ProjectRegisters_Rc_ModWidthSOF14A106:
        """
        Specifies settings of the ModWidthSOF register for 14A_106.
        """
        return ProjectRegisters_Rc_ModWidthSOF14A106(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14B848(self) -> ProjectRegisters_Rc_ModWidthSOF14B848:
        """
        Specifies settings of the ModWidthSOF register for 14B_848.
        """
        return ProjectRegisters_Rc_ModWidthSOF14B848(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14B424(self) -> ProjectRegisters_Rc_ModWidthSOF14B424:
        """
        Specifies settings of the ModWidthSOF register for 14B_424.
        """
        return ProjectRegisters_Rc_ModWidthSOF14B424(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14B212(self) -> ProjectRegisters_Rc_ModWidthSOF14B212:
        """
        Specifies settings of the ModWidthSOF register for 14B_212.
        """
        return ProjectRegisters_Rc_ModWidthSOF14B212(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14B106(self) -> ProjectRegisters_Rc_ModWidthSOF14B106:
        """
        Specifies settings of the ModWidthSOF register for 14B_106.
        """
        return ProjectRegisters_Rc_ModWidthSOF14B106(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF15Standard(self) -> ProjectRegisters_Rc_ModWidthSOF15Standard:
        """
        Specifies settings of the ModWidthSOF register for 15Standard.
        """
        return ProjectRegisters_Rc_ModWidthSOF15Standard(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF15Fast(self) -> ProjectRegisters_Rc_ModWidthSOF15Fast:
        """
        Specifies settings of the ModWidthSOF register for 15Fast.
        """
        return ProjectRegisters_Rc_ModWidthSOF15Fast(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14A(self) -> ProjectRegisters_Rc_ModWidthSOF14A:
        """
        Specifies settings of the ModWidthSOF register for 14A.
        """
        return ProjectRegisters_Rc_ModWidthSOF14A(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF14B(self) -> ProjectRegisters_Rc_ModWidthSOF14B:
        """
        Specifies settings of the ModWidthSOF register for 14B.
        """
        return ProjectRegisters_Rc_ModWidthSOF14B(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOF15(self) -> ProjectRegisters_Rc_ModWidthSOF15:
        """
        Specifies settings of the ModWidthSOF register for 15.
        """
        return ProjectRegisters_Rc_ModWidthSOF15(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOFALL(self) -> ProjectRegisters_Rc_ModWidthSOFALL:
        """
        Specifies settings of the ModWidthSOF register for ALL.
        """
        return ProjectRegisters_Rc_ModWidthSOFALL(self)
    @property
    def ProjectRegisters_Rc_ModWidthSOFVOLATILE(self) -> ProjectRegisters_Rc_ModWidthSOFVOLATILE:
        """
        Specifies settings of the ModWidthSOF register for VOLATILE.
        """
        return ProjectRegisters_Rc_ModWidthSOFVOLATILE(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14A848(self) -> ProjectRegisters_Rc_TypeBFraming14A848:
        """
        Specifies settings of the TypeBFraming register for 14A_848.
        """
        return ProjectRegisters_Rc_TypeBFraming14A848(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14A424(self) -> ProjectRegisters_Rc_TypeBFraming14A424:
        """
        Specifies settings of the TypeBFraming register for 14A_424.
        """
        return ProjectRegisters_Rc_TypeBFraming14A424(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14A212(self) -> ProjectRegisters_Rc_TypeBFraming14A212:
        """
        Specifies settings of the TypeBFraming register for 14A_212.
        """
        return ProjectRegisters_Rc_TypeBFraming14A212(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14A106(self) -> ProjectRegisters_Rc_TypeBFraming14A106:
        """
        Specifies settings of the TypeBFraming register for 14A_106.
        """
        return ProjectRegisters_Rc_TypeBFraming14A106(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14B848(self) -> ProjectRegisters_Rc_TypeBFraming14B848:
        """
        Specifies settings of the TypeBFraming register for 14B_848.
        """
        return ProjectRegisters_Rc_TypeBFraming14B848(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14B424(self) -> ProjectRegisters_Rc_TypeBFraming14B424:
        """
        Specifies settings of the TypeBFraming register for 14B_424.
        """
        return ProjectRegisters_Rc_TypeBFraming14B424(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14B212(self) -> ProjectRegisters_Rc_TypeBFraming14B212:
        """
        Specifies settings of the TypeBFraming register for 14B_212.
        """
        return ProjectRegisters_Rc_TypeBFraming14B212(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14B106(self) -> ProjectRegisters_Rc_TypeBFraming14B106:
        """
        Specifies settings of the TypeBFraming register for 14B_106.
        """
        return ProjectRegisters_Rc_TypeBFraming14B106(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming15Standard(self) -> ProjectRegisters_Rc_TypeBFraming15Standard:
        """
        Specifies settings of the TypeBFraming register for 15Standard.
        """
        return ProjectRegisters_Rc_TypeBFraming15Standard(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming15Fast(self) -> ProjectRegisters_Rc_TypeBFraming15Fast:
        """
        Specifies settings of the TypeBFraming register for 15Fast.
        """
        return ProjectRegisters_Rc_TypeBFraming15Fast(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14A(self) -> ProjectRegisters_Rc_TypeBFraming14A:
        """
        Specifies settings of the TypeBFraming register for 14A.
        """
        return ProjectRegisters_Rc_TypeBFraming14A(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming14B(self) -> ProjectRegisters_Rc_TypeBFraming14B:
        """
        Specifies settings of the TypeBFraming register for 14B.
        """
        return ProjectRegisters_Rc_TypeBFraming14B(self)
    @property
    def ProjectRegisters_Rc_TypeBFraming15(self) -> ProjectRegisters_Rc_TypeBFraming15:
        """
        Specifies settings of the TypeBFraming register for 15.
        """
        return ProjectRegisters_Rc_TypeBFraming15(self)
    @property
    def ProjectRegisters_Rc_TypeBFramingALL(self) -> ProjectRegisters_Rc_TypeBFramingALL:
        """
        Specifies settings of the TypeBFraming register for ALL.
        """
        return ProjectRegisters_Rc_TypeBFramingALL(self)
    @property
    def ProjectRegisters_Rc_TypeBFramingVOLATILE(self) -> ProjectRegisters_Rc_TypeBFramingVOLATILE:
        """
        Specifies settings of the TypeBFraming register for VOLATILE.
        """
        return ProjectRegisters_Rc_TypeBFramingVOLATILE(self)
    @property
    def ProjectRegisters_Rc_RxControl114A848(self) -> ProjectRegisters_Rc_RxControl114A848:
        """
        Specifies settings of the RxControl1 register for 14A_848.
        """
        return ProjectRegisters_Rc_RxControl114A848(self)
    @property
    def ProjectRegisters_Rc_RxControl114A424(self) -> ProjectRegisters_Rc_RxControl114A424:
        """
        Specifies settings of the RxControl1 register for 14A_424.
        """
        return ProjectRegisters_Rc_RxControl114A424(self)
    @property
    def ProjectRegisters_Rc_RxControl114A212(self) -> ProjectRegisters_Rc_RxControl114A212:
        """
        Specifies settings of the RxControl1 register for 14A_212.
        """
        return ProjectRegisters_Rc_RxControl114A212(self)
    @property
    def ProjectRegisters_Rc_RxControl114A106(self) -> ProjectRegisters_Rc_RxControl114A106:
        """
        Specifies settings of the RxControl1 register for 14A_106.
        """
        return ProjectRegisters_Rc_RxControl114A106(self)
    @property
    def ProjectRegisters_Rc_RxControl114B848(self) -> ProjectRegisters_Rc_RxControl114B848:
        """
        Specifies settings of the RxControl1 register for 14B_848.
        """
        return ProjectRegisters_Rc_RxControl114B848(self)
    @property
    def ProjectRegisters_Rc_RxControl114B424(self) -> ProjectRegisters_Rc_RxControl114B424:
        """
        Specifies settings of the RxControl1 register for 14B_424.
        """
        return ProjectRegisters_Rc_RxControl114B424(self)
    @property
    def ProjectRegisters_Rc_RxControl114B212(self) -> ProjectRegisters_Rc_RxControl114B212:
        """
        Specifies settings of the RxControl1 register for 14B_212.
        """
        return ProjectRegisters_Rc_RxControl114B212(self)
    @property
    def ProjectRegisters_Rc_RxControl114B106(self) -> ProjectRegisters_Rc_RxControl114B106:
        """
        Specifies settings of the RxControl1 register for 14B_106.
        """
        return ProjectRegisters_Rc_RxControl114B106(self)
    @property
    def ProjectRegisters_Rc_RxControl115Standard(self) -> ProjectRegisters_Rc_RxControl115Standard:
        """
        Specifies settings of the RxControl1 register for 15Standard.
        """
        return ProjectRegisters_Rc_RxControl115Standard(self)
    @property
    def ProjectRegisters_Rc_RxControl115Fast(self) -> ProjectRegisters_Rc_RxControl115Fast:
        """
        Specifies settings of the RxControl1 register for 15Fast.
        """
        return ProjectRegisters_Rc_RxControl115Fast(self)
    @property
    def ProjectRegisters_Rc_RxControl114A(self) -> ProjectRegisters_Rc_RxControl114A:
        """
        Specifies settings of the RxControl1 register for 14A.
        """
        return ProjectRegisters_Rc_RxControl114A(self)
    @property
    def ProjectRegisters_Rc_RxControl114B(self) -> ProjectRegisters_Rc_RxControl114B:
        """
        Specifies settings of the RxControl1 register for 14B.
        """
        return ProjectRegisters_Rc_RxControl114B(self)
    @property
    def ProjectRegisters_Rc_RxControl115(self) -> ProjectRegisters_Rc_RxControl115:
        """
        Specifies settings of the RxControl1 register for 15.
        """
        return ProjectRegisters_Rc_RxControl115(self)
    @property
    def ProjectRegisters_Rc_RxControl1ALL(self) -> ProjectRegisters_Rc_RxControl1ALL:
        """
        Specifies settings of the RxControl1 register for ALL.
        """
        return ProjectRegisters_Rc_RxControl1ALL(self)
    @property
    def ProjectRegisters_Rc_RxControl1VOLATILE(self) -> ProjectRegisters_Rc_RxControl1VOLATILE:
        """
        Specifies settings of the RxControl1 register for VOLATILE.
        """
        return ProjectRegisters_Rc_RxControl1VOLATILE(self)
    @property
    def ProjectRegisters_Rc_BitPhase14A848(self) -> ProjectRegisters_Rc_BitPhase14A848:
        """
        Specifies settings of the BitPhase register for 14A_848.
        """
        return ProjectRegisters_Rc_BitPhase14A848(self)
    @property
    def ProjectRegisters_Rc_BitPhase14A424(self) -> ProjectRegisters_Rc_BitPhase14A424:
        """
        Specifies settings of the BitPhase register for 14A_424.
        """
        return ProjectRegisters_Rc_BitPhase14A424(self)
    @property
    def ProjectRegisters_Rc_BitPhase14A212(self) -> ProjectRegisters_Rc_BitPhase14A212:
        """
        Specifies settings of the BitPhase register for 14A_212.
        """
        return ProjectRegisters_Rc_BitPhase14A212(self)
    @property
    def ProjectRegisters_Rc_BitPhase14A106(self) -> ProjectRegisters_Rc_BitPhase14A106:
        """
        Specifies settings of the BitPhase register for 14A_106.
        """
        return ProjectRegisters_Rc_BitPhase14A106(self)
    @property
    def ProjectRegisters_Rc_BitPhase14B848(self) -> ProjectRegisters_Rc_BitPhase14B848:
        """
        Specifies settings of the BitPhase register for 14B_848.
        """
        return ProjectRegisters_Rc_BitPhase14B848(self)
    @property
    def ProjectRegisters_Rc_BitPhase14B424(self) -> ProjectRegisters_Rc_BitPhase14B424:
        """
        Specifies settings of the BitPhase register for 14B_424.
        """
        return ProjectRegisters_Rc_BitPhase14B424(self)
    @property
    def ProjectRegisters_Rc_BitPhase14B212(self) -> ProjectRegisters_Rc_BitPhase14B212:
        """
        Specifies settings of the BitPhase register for 14B_212.
        """
        return ProjectRegisters_Rc_BitPhase14B212(self)
    @property
    def ProjectRegisters_Rc_BitPhase14B106(self) -> ProjectRegisters_Rc_BitPhase14B106:
        """
        Specifies settings of the BitPhase register for 14B_106.
        """
        return ProjectRegisters_Rc_BitPhase14B106(self)
    @property
    def ProjectRegisters_Rc_BitPhase15Standard(self) -> ProjectRegisters_Rc_BitPhase15Standard:
        """
        Specifies settings of the BitPhase register for 15Standard.
        """
        return ProjectRegisters_Rc_BitPhase15Standard(self)
    @property
    def ProjectRegisters_Rc_BitPhase15Fast(self) -> ProjectRegisters_Rc_BitPhase15Fast:
        """
        Specifies settings of the BitPhase register for 15Fast.
        """
        return ProjectRegisters_Rc_BitPhase15Fast(self)
    @property
    def ProjectRegisters_Rc_BitPhase14A(self) -> ProjectRegisters_Rc_BitPhase14A:
        """
        Specifies settings of the BitPhase register for 14A.
        """
        return ProjectRegisters_Rc_BitPhase14A(self)
    @property
    def ProjectRegisters_Rc_BitPhase14B(self) -> ProjectRegisters_Rc_BitPhase14B:
        """
        Specifies settings of the BitPhase register for 14B.
        """
        return ProjectRegisters_Rc_BitPhase14B(self)
    @property
    def ProjectRegisters_Rc_BitPhase15(self) -> ProjectRegisters_Rc_BitPhase15:
        """
        Specifies settings of the BitPhase register for 15.
        """
        return ProjectRegisters_Rc_BitPhase15(self)
    @property
    def ProjectRegisters_Rc_BitPhaseALL(self) -> ProjectRegisters_Rc_BitPhaseALL:
        """
        Specifies settings of the BitPhase register for ALL.
        """
        return ProjectRegisters_Rc_BitPhaseALL(self)
    @property
    def ProjectRegisters_Rc_BitPhaseVOLATILE(self) -> ProjectRegisters_Rc_BitPhaseVOLATILE:
        """
        Specifies settings of the BitPhase register for VOLATILE.
        """
        return ProjectRegisters_Rc_BitPhaseVOLATILE(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14A848(self) -> ProjectRegisters_Rc_RxThreshold14A848:
        """
        Specifies settings of the RxThreshold register for 14A_848.
        """
        return ProjectRegisters_Rc_RxThreshold14A848(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14A424(self) -> ProjectRegisters_Rc_RxThreshold14A424:
        """
        Specifies settings of the RxThreshold register for 14A_424.
        """
        return ProjectRegisters_Rc_RxThreshold14A424(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14A212(self) -> ProjectRegisters_Rc_RxThreshold14A212:
        """
        Specifies settings of the RxThreshold register for 14A_212.
        """
        return ProjectRegisters_Rc_RxThreshold14A212(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14A106(self) -> ProjectRegisters_Rc_RxThreshold14A106:
        """
        Specifies settings of the RxThreshold register for 14A_106.
        """
        return ProjectRegisters_Rc_RxThreshold14A106(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14B848(self) -> ProjectRegisters_Rc_RxThreshold14B848:
        """
        Specifies settings of the RxThreshold register for 14B_848.
        """
        return ProjectRegisters_Rc_RxThreshold14B848(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14B424(self) -> ProjectRegisters_Rc_RxThreshold14B424:
        """
        Specifies settings of the RxThreshold register for 14B_424.
        """
        return ProjectRegisters_Rc_RxThreshold14B424(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14B212(self) -> ProjectRegisters_Rc_RxThreshold14B212:
        """
        Specifies settings of the RxThreshold register for 14B_212.
        """
        return ProjectRegisters_Rc_RxThreshold14B212(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14B106(self) -> ProjectRegisters_Rc_RxThreshold14B106:
        """
        Specifies settings of the RxThreshold register for 14B_106.
        """
        return ProjectRegisters_Rc_RxThreshold14B106(self)
    @property
    def ProjectRegisters_Rc_RxThreshold15Standard(self) -> ProjectRegisters_Rc_RxThreshold15Standard:
        """
        Specifies settings of the RxThreshold register for 15Standard.
        """
        return ProjectRegisters_Rc_RxThreshold15Standard(self)
    @property
    def ProjectRegisters_Rc_RxThreshold15Fast(self) -> ProjectRegisters_Rc_RxThreshold15Fast:
        """
        Specifies settings of the RxThreshold register for 15Fast.
        """
        return ProjectRegisters_Rc_RxThreshold15Fast(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14A(self) -> ProjectRegisters_Rc_RxThreshold14A:
        """
        Specifies settings of the RxThreshold register for 14A.
        """
        return ProjectRegisters_Rc_RxThreshold14A(self)
    @property
    def ProjectRegisters_Rc_RxThreshold14B(self) -> ProjectRegisters_Rc_RxThreshold14B:
        """
        Specifies settings of the RxThreshold register for 14B.
        """
        return ProjectRegisters_Rc_RxThreshold14B(self)
    @property
    def ProjectRegisters_Rc_RxThreshold15(self) -> ProjectRegisters_Rc_RxThreshold15:
        """
        Specifies settings of the RxThreshold register for 15.
        """
        return ProjectRegisters_Rc_RxThreshold15(self)
    @property
    def ProjectRegisters_Rc_RxThresholdALL(self) -> ProjectRegisters_Rc_RxThresholdALL:
        """
        Specifies settings of the RxThreshold register for ALL.
        """
        return ProjectRegisters_Rc_RxThresholdALL(self)
    @property
    def ProjectRegisters_Rc_RxThresholdVOLATILE(self) -> ProjectRegisters_Rc_RxThresholdVOLATILE:
        """
        Specifies settings of the RxThreshold register for VOLATILE.
        """
        return ProjectRegisters_Rc_RxThresholdVOLATILE(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14A848(self) -> ProjectRegisters_Rc_BPSKDemControl14A848:
        """
        Specifies settings of the BPSKDemControl register for 14A_848.
        """
        return ProjectRegisters_Rc_BPSKDemControl14A848(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14A424(self) -> ProjectRegisters_Rc_BPSKDemControl14A424:
        """
        Specifies settings of the BPSKDemControl register for 14A_424.
        """
        return ProjectRegisters_Rc_BPSKDemControl14A424(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14A212(self) -> ProjectRegisters_Rc_BPSKDemControl14A212:
        """
        Specifies settings of the BPSKDemControl register for 14A_212.
        """
        return ProjectRegisters_Rc_BPSKDemControl14A212(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14A106(self) -> ProjectRegisters_Rc_BPSKDemControl14A106:
        """
        Specifies settings of the BPSKDemControl register for 14A_106.
        """
        return ProjectRegisters_Rc_BPSKDemControl14A106(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14B848(self) -> ProjectRegisters_Rc_BPSKDemControl14B848:
        """
        Specifies settings of the BPSKDemControl register for 14B_848.
        """
        return ProjectRegisters_Rc_BPSKDemControl14B848(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14B424(self) -> ProjectRegisters_Rc_BPSKDemControl14B424:
        """
        Specifies settings of the BPSKDemControl register for 14B_424.
        """
        return ProjectRegisters_Rc_BPSKDemControl14B424(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14B212(self) -> ProjectRegisters_Rc_BPSKDemControl14B212:
        """
        Specifies settings of the BPSKDemControl register for 14B_212.
        """
        return ProjectRegisters_Rc_BPSKDemControl14B212(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14B106(self) -> ProjectRegisters_Rc_BPSKDemControl14B106:
        """
        Specifies settings of the BPSKDemControl register for 14B_106.
        """
        return ProjectRegisters_Rc_BPSKDemControl14B106(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl15Standard(self) -> ProjectRegisters_Rc_BPSKDemControl15Standard:
        """
        Specifies settings of the BPSKDemControl register for 15Standard.
        """
        return ProjectRegisters_Rc_BPSKDemControl15Standard(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl15Fast(self) -> ProjectRegisters_Rc_BPSKDemControl15Fast:
        """
        Specifies settings of the BPSKDemControl register for 15Fast.
        """
        return ProjectRegisters_Rc_BPSKDemControl15Fast(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14A(self) -> ProjectRegisters_Rc_BPSKDemControl14A:
        """
        Specifies settings of the BPSKDemControl register for 14A.
        """
        return ProjectRegisters_Rc_BPSKDemControl14A(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl14B(self) -> ProjectRegisters_Rc_BPSKDemControl14B:
        """
        Specifies settings of the BPSKDemControl register for 14B.
        """
        return ProjectRegisters_Rc_BPSKDemControl14B(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControl15(self) -> ProjectRegisters_Rc_BPSKDemControl15:
        """
        Specifies settings of the BPSKDemControl register for 15.
        """
        return ProjectRegisters_Rc_BPSKDemControl15(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControlALL(self) -> ProjectRegisters_Rc_BPSKDemControlALL:
        """
        Specifies settings of the BPSKDemControl register for ALL.
        """
        return ProjectRegisters_Rc_BPSKDemControlALL(self)
    @property
    def ProjectRegisters_Rc_BPSKDemControlVOLATILE(self) -> ProjectRegisters_Rc_BPSKDemControlVOLATILE:
        """
        Specifies settings of the BPSKDemControl register for VOLATILE.
        """
        return ProjectRegisters_Rc_BPSKDemControlVOLATILE(self)
    @property
    def ProjectRegisters_Rc_RxWait14A848(self) -> ProjectRegisters_Rc_RxWait14A848:
        """
        Specifies settings of the RxWait register for 14A_848.
        """
        return ProjectRegisters_Rc_RxWait14A848(self)
    @property
    def ProjectRegisters_Rc_RxWait14A424(self) -> ProjectRegisters_Rc_RxWait14A424:
        """
        Specifies settings of the RxWait register for 14A_424.
        """
        return ProjectRegisters_Rc_RxWait14A424(self)
    @property
    def ProjectRegisters_Rc_RxWait14A212(self) -> ProjectRegisters_Rc_RxWait14A212:
        """
        Specifies settings of the RxWait register for 14A_212.
        """
        return ProjectRegisters_Rc_RxWait14A212(self)
    @property
    def ProjectRegisters_Rc_RxWait14A106(self) -> ProjectRegisters_Rc_RxWait14A106:
        """
        Specifies settings of the RxWait register for 14A_106.
        """
        return ProjectRegisters_Rc_RxWait14A106(self)
    @property
    def ProjectRegisters_Rc_RxWait14B848(self) -> ProjectRegisters_Rc_RxWait14B848:
        """
        Specifies settings of the RxWait register for 14B_848.
        """
        return ProjectRegisters_Rc_RxWait14B848(self)
    @property
    def ProjectRegisters_Rc_RxWait14B424(self) -> ProjectRegisters_Rc_RxWait14B424:
        """
        Specifies settings of the RxWait register for 14B_424.
        """
        return ProjectRegisters_Rc_RxWait14B424(self)
    @property
    def ProjectRegisters_Rc_RxWait14B212(self) -> ProjectRegisters_Rc_RxWait14B212:
        """
        Specifies settings of the RxWait register for 14B_212.
        """
        return ProjectRegisters_Rc_RxWait14B212(self)
    @property
    def ProjectRegisters_Rc_RxWait14B106(self) -> ProjectRegisters_Rc_RxWait14B106:
        """
        Specifies settings of the RxWait register for 14B_106.
        """
        return ProjectRegisters_Rc_RxWait14B106(self)
    @property
    def ProjectRegisters_Rc_RxWait15Standard(self) -> ProjectRegisters_Rc_RxWait15Standard:
        """
        Specifies settings of the RxWait register for 15Standard.
        """
        return ProjectRegisters_Rc_RxWait15Standard(self)
    @property
    def ProjectRegisters_Rc_RxWait15Fast(self) -> ProjectRegisters_Rc_RxWait15Fast:
        """
        Specifies settings of the RxWait register for 15Fast.
        """
        return ProjectRegisters_Rc_RxWait15Fast(self)
    @property
    def ProjectRegisters_Rc_RxWait14A(self) -> ProjectRegisters_Rc_RxWait14A:
        """
        Specifies settings of the RxWait register for 14A.
        """
        return ProjectRegisters_Rc_RxWait14A(self)
    @property
    def ProjectRegisters_Rc_RxWait14B(self) -> ProjectRegisters_Rc_RxWait14B:
        """
        Specifies settings of the RxWait register for 14B.
        """
        return ProjectRegisters_Rc_RxWait14B(self)
    @property
    def ProjectRegisters_Rc_RxWait15(self) -> ProjectRegisters_Rc_RxWait15:
        """
        Specifies settings of the RxWait register for 15.
        """
        return ProjectRegisters_Rc_RxWait15(self)
    @property
    def ProjectRegisters_Rc_RxWaitALL(self) -> ProjectRegisters_Rc_RxWaitALL:
        """
        Specifies settings of the RxWait register for ALL.
        """
        return ProjectRegisters_Rc_RxWaitALL(self)
    @property
    def ProjectRegisters_Rc_RxWaitVOLATILE(self) -> ProjectRegisters_Rc_RxWaitVOLATILE:
        """
        Specifies settings of the RxWait register for VOLATILE.
        """
        return ProjectRegisters_Rc_RxWaitVOLATILE(self)
    @property
    def ProjectRegisters_Pn(self) -> ProjectRegisters_Pn:
        """
        This value contains HF Settings (Register Settings) of the PN512 reader chip.
        """
        return ProjectRegisters_Pn(self)
    @property
    def ProjectRegisters_Pn_TxMode14A848(self) -> ProjectRegisters_Pn_TxMode14A848:
        """
        Specifies settings of the TxMode register for 14A_848.
        """
        return ProjectRegisters_Pn_TxMode14A848(self)
    @property
    def ProjectRegisters_Pn_TxMode14A424(self) -> ProjectRegisters_Pn_TxMode14A424:
        """
        Specifies settings of the TxMode register for 14A_424.
        """
        return ProjectRegisters_Pn_TxMode14A424(self)
    @property
    def ProjectRegisters_Pn_TxMode14A212(self) -> ProjectRegisters_Pn_TxMode14A212:
        """
        Specifies settings of the TxMode register for 14A_212.
        """
        return ProjectRegisters_Pn_TxMode14A212(self)
    @property
    def ProjectRegisters_Pn_TxMode14A106(self) -> ProjectRegisters_Pn_TxMode14A106:
        """
        Specifies settings of the TxMode register for 14A_106.
        """
        return ProjectRegisters_Pn_TxMode14A106(self)
    @property
    def ProjectRegisters_Pn_TxMode14B848(self) -> ProjectRegisters_Pn_TxMode14B848:
        """
        Specifies settings of the TxMode register for 14B_848.
        """
        return ProjectRegisters_Pn_TxMode14B848(self)
    @property
    def ProjectRegisters_Pn_TxMode14B424(self) -> ProjectRegisters_Pn_TxMode14B424:
        """
        Specifies settings of the TxMode register for 14B_424.
        """
        return ProjectRegisters_Pn_TxMode14B424(self)
    @property
    def ProjectRegisters_Pn_TxMode14B212(self) -> ProjectRegisters_Pn_TxMode14B212:
        """
        Specifies settings of the TxMode register for 14B_212.
        """
        return ProjectRegisters_Pn_TxMode14B212(self)
    @property
    def ProjectRegisters_Pn_TxMode14B106(self) -> ProjectRegisters_Pn_TxMode14B106:
        """
        Specifies settings of the TxMode register for 14B_106.
        """
        return ProjectRegisters_Pn_TxMode14B106(self)
    @property
    def ProjectRegisters_Pn_TxMode14A(self) -> ProjectRegisters_Pn_TxMode14A:
        """
        Specifies settings of the TxMode register for 14A.
        """
        return ProjectRegisters_Pn_TxMode14A(self)
    @property
    def ProjectRegisters_Pn_TxMode14B(self) -> ProjectRegisters_Pn_TxMode14B:
        """
        Specifies settings of the TxMode register for 14B.
        """
        return ProjectRegisters_Pn_TxMode14B(self)
    @property
    def ProjectRegisters_Pn_TxModeALL(self) -> ProjectRegisters_Pn_TxModeALL:
        """
        Specifies settings of the TxMode register for ALL.
        """
        return ProjectRegisters_Pn_TxModeALL(self)
    @property
    def ProjectRegisters_Pn_TxModeVOLATILE(self) -> ProjectRegisters_Pn_TxModeVOLATILE:
        """
        Specifies settings of the TxMode register for VOLATILE.
        """
        return ProjectRegisters_Pn_TxModeVOLATILE(self)
    @property
    def ProjectRegisters_Pn_RxMode14A848(self) -> ProjectRegisters_Pn_RxMode14A848:
        """
        Specifies settings of the RxMode register for 14A_848.
        """
        return ProjectRegisters_Pn_RxMode14A848(self)
    @property
    def ProjectRegisters_Pn_RxMode14A424(self) -> ProjectRegisters_Pn_RxMode14A424:
        """
        Specifies settings of the RxMode register for 14A_424.
        """
        return ProjectRegisters_Pn_RxMode14A424(self)
    @property
    def ProjectRegisters_Pn_RxMode14A212(self) -> ProjectRegisters_Pn_RxMode14A212:
        """
        Specifies settings of the RxMode register for 14A_212.
        """
        return ProjectRegisters_Pn_RxMode14A212(self)
    @property
    def ProjectRegisters_Pn_RxMode14A106(self) -> ProjectRegisters_Pn_RxMode14A106:
        """
        Specifies settings of the RxMode register for 14A_106.
        """
        return ProjectRegisters_Pn_RxMode14A106(self)
    @property
    def ProjectRegisters_Pn_RxMode14B848(self) -> ProjectRegisters_Pn_RxMode14B848:
        """
        Specifies settings of the RxMode register for 14B_848.
        """
        return ProjectRegisters_Pn_RxMode14B848(self)
    @property
    def ProjectRegisters_Pn_RxMode14B424(self) -> ProjectRegisters_Pn_RxMode14B424:
        """
        Specifies settings of the RxMode register for 14B_424.
        """
        return ProjectRegisters_Pn_RxMode14B424(self)
    @property
    def ProjectRegisters_Pn_RxMode14B212(self) -> ProjectRegisters_Pn_RxMode14B212:
        """
        Specifies settings of the RxMode register for 14B_212.
        """
        return ProjectRegisters_Pn_RxMode14B212(self)
    @property
    def ProjectRegisters_Pn_RxMode14B106(self) -> ProjectRegisters_Pn_RxMode14B106:
        """
        Specifies settings of the RxMode register for 14B_106.
        """
        return ProjectRegisters_Pn_RxMode14B106(self)
    @property
    def ProjectRegisters_Pn_RxMode14A(self) -> ProjectRegisters_Pn_RxMode14A:
        """
        Specifies settings of the RxMode register for 14A.
        """
        return ProjectRegisters_Pn_RxMode14A(self)
    @property
    def ProjectRegisters_Pn_RxMode14B(self) -> ProjectRegisters_Pn_RxMode14B:
        """
        Specifies settings of the RxMode register for 14B.
        """
        return ProjectRegisters_Pn_RxMode14B(self)
    @property
    def ProjectRegisters_Pn_RxModeALL(self) -> ProjectRegisters_Pn_RxModeALL:
        """
        Specifies settings of the RxMode register for ALL.
        """
        return ProjectRegisters_Pn_RxModeALL(self)
    @property
    def ProjectRegisters_Pn_RxModeVOLATILE(self) -> ProjectRegisters_Pn_RxModeVOLATILE:
        """
        Specifies settings of the RxMode register for VOLATILE.
        """
        return ProjectRegisters_Pn_RxModeVOLATILE(self)
    @property
    def ProjectRegisters_Pn_RxSel14A848(self) -> ProjectRegisters_Pn_RxSel14A848:
        """
        Specifies settings of the RxSel register for 14A_848.
        """
        return ProjectRegisters_Pn_RxSel14A848(self)
    @property
    def ProjectRegisters_Pn_RxSel14A424(self) -> ProjectRegisters_Pn_RxSel14A424:
        """
        Specifies settings of the RxSel register for 14A_424.
        """
        return ProjectRegisters_Pn_RxSel14A424(self)
    @property
    def ProjectRegisters_Pn_RxSel14A212(self) -> ProjectRegisters_Pn_RxSel14A212:
        """
        Specifies settings of the RxSel register for 14A_212.
        """
        return ProjectRegisters_Pn_RxSel14A212(self)
    @property
    def ProjectRegisters_Pn_RxSel14A106(self) -> ProjectRegisters_Pn_RxSel14A106:
        """
        Specifies settings of the RxSel register for 14A_106.
        """
        return ProjectRegisters_Pn_RxSel14A106(self)
    @property
    def ProjectRegisters_Pn_RxSel14B848(self) -> ProjectRegisters_Pn_RxSel14B848:
        """
        Specifies settings of the RxSel register for 14B_848.
        """
        return ProjectRegisters_Pn_RxSel14B848(self)
    @property
    def ProjectRegisters_Pn_RxSel14B424(self) -> ProjectRegisters_Pn_RxSel14B424:
        """
        Specifies settings of the RxSel register for 14B_424.
        """
        return ProjectRegisters_Pn_RxSel14B424(self)
    @property
    def ProjectRegisters_Pn_RxSel14B212(self) -> ProjectRegisters_Pn_RxSel14B212:
        """
        Specifies settings of the RxSel register for 14B_212.
        """
        return ProjectRegisters_Pn_RxSel14B212(self)
    @property
    def ProjectRegisters_Pn_RxSel14B106(self) -> ProjectRegisters_Pn_RxSel14B106:
        """
        Specifies settings of the RxSel register for 14B_106.
        """
        return ProjectRegisters_Pn_RxSel14B106(self)
    @property
    def ProjectRegisters_Pn_RxSel14A(self) -> ProjectRegisters_Pn_RxSel14A:
        """
        Specifies settings of the RxSel register for 14A.
        """
        return ProjectRegisters_Pn_RxSel14A(self)
    @property
    def ProjectRegisters_Pn_RxSel14B(self) -> ProjectRegisters_Pn_RxSel14B:
        """
        Specifies settings of the RxSel register for 14B.
        """
        return ProjectRegisters_Pn_RxSel14B(self)
    @property
    def ProjectRegisters_Pn_RxSelALL(self) -> ProjectRegisters_Pn_RxSelALL:
        """
        Specifies settings of the RxSel register for ALL.
        """
        return ProjectRegisters_Pn_RxSelALL(self)
    @property
    def ProjectRegisters_Pn_RxSelVOLATILE(self) -> ProjectRegisters_Pn_RxSelVOLATILE:
        """
        Specifies settings of the RxSel register for VOLATILE.
        """
        return ProjectRegisters_Pn_RxSelVOLATILE(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14A848(self) -> ProjectRegisters_Pn_RxThreshold14A848:
        """
        Specifies settings of the RxThreshold register for 14A_848.
        """
        return ProjectRegisters_Pn_RxThreshold14A848(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14A424(self) -> ProjectRegisters_Pn_RxThreshold14A424:
        """
        Specifies settings of the RxThreshold register for 14A_424.
        """
        return ProjectRegisters_Pn_RxThreshold14A424(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14A212(self) -> ProjectRegisters_Pn_RxThreshold14A212:
        """
        Specifies settings of the RxThreshold register for 14A_212.
        """
        return ProjectRegisters_Pn_RxThreshold14A212(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14A106(self) -> ProjectRegisters_Pn_RxThreshold14A106:
        """
        Specifies settings of the RxThreshold register for 14A_106.
        """
        return ProjectRegisters_Pn_RxThreshold14A106(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14B848(self) -> ProjectRegisters_Pn_RxThreshold14B848:
        """
        Specifies settings of the RxThreshold register for 14B_848.
        """
        return ProjectRegisters_Pn_RxThreshold14B848(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14B424(self) -> ProjectRegisters_Pn_RxThreshold14B424:
        """
        Specifies settings of the RxThreshold register for 14B_424.
        """
        return ProjectRegisters_Pn_RxThreshold14B424(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14B212(self) -> ProjectRegisters_Pn_RxThreshold14B212:
        """
        Specifies settings of the RxThreshold register for 14B_212.
        """
        return ProjectRegisters_Pn_RxThreshold14B212(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14B106(self) -> ProjectRegisters_Pn_RxThreshold14B106:
        """
        Specifies settings of the RxThreshold register for 14B_106.
        """
        return ProjectRegisters_Pn_RxThreshold14B106(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14A(self) -> ProjectRegisters_Pn_RxThreshold14A:
        """
        Specifies settings of the RxThreshold register for 14A.
        """
        return ProjectRegisters_Pn_RxThreshold14A(self)
    @property
    def ProjectRegisters_Pn_RxThreshold14B(self) -> ProjectRegisters_Pn_RxThreshold14B:
        """
        Specifies settings of the RxThreshold register for 14B.
        """
        return ProjectRegisters_Pn_RxThreshold14B(self)
    @property
    def ProjectRegisters_Pn_RxThresholdALL(self) -> ProjectRegisters_Pn_RxThresholdALL:
        """
        Specifies settings of the RxThreshold register for ALL.
        """
        return ProjectRegisters_Pn_RxThresholdALL(self)
    @property
    def ProjectRegisters_Pn_RxThresholdVOLATILE(self) -> ProjectRegisters_Pn_RxThresholdVOLATILE:
        """
        Specifies settings of the RxThreshold register for VOLATILE.
        """
        return ProjectRegisters_Pn_RxThresholdVOLATILE(self)
    @property
    def ProjectRegisters_Pn_Demod14A848(self) -> ProjectRegisters_Pn_Demod14A848:
        """
        Specifies settings of the Demod register for 14A_848.
        """
        return ProjectRegisters_Pn_Demod14A848(self)
    @property
    def ProjectRegisters_Pn_Demod14A424(self) -> ProjectRegisters_Pn_Demod14A424:
        """
        Specifies settings of the Demod register for 14A_424.
        """
        return ProjectRegisters_Pn_Demod14A424(self)
    @property
    def ProjectRegisters_Pn_Demod14A212(self) -> ProjectRegisters_Pn_Demod14A212:
        """
        Specifies settings of the Demod register for 14A_212.
        """
        return ProjectRegisters_Pn_Demod14A212(self)
    @property
    def ProjectRegisters_Pn_Demod14A106(self) -> ProjectRegisters_Pn_Demod14A106:
        """
        Specifies settings of the Demod register for 14A_106.
        """
        return ProjectRegisters_Pn_Demod14A106(self)
    @property
    def ProjectRegisters_Pn_Demod14B848(self) -> ProjectRegisters_Pn_Demod14B848:
        """
        Specifies settings of the Demod register for 14B_848.
        """
        return ProjectRegisters_Pn_Demod14B848(self)
    @property
    def ProjectRegisters_Pn_Demod14B424(self) -> ProjectRegisters_Pn_Demod14B424:
        """
        Specifies settings of the Demod register for 14B_424.
        """
        return ProjectRegisters_Pn_Demod14B424(self)
    @property
    def ProjectRegisters_Pn_Demod14B212(self) -> ProjectRegisters_Pn_Demod14B212:
        """
        Specifies settings of the Demod register for 14B_212.
        """
        return ProjectRegisters_Pn_Demod14B212(self)
    @property
    def ProjectRegisters_Pn_Demod14B106(self) -> ProjectRegisters_Pn_Demod14B106:
        """
        Specifies settings of the Demod register for 14B_106.
        """
        return ProjectRegisters_Pn_Demod14B106(self)
    @property
    def ProjectRegisters_Pn_Demod14A(self) -> ProjectRegisters_Pn_Demod14A:
        """
        Specifies settings of the Demod register for 14A.
        """
        return ProjectRegisters_Pn_Demod14A(self)
    @property
    def ProjectRegisters_Pn_Demod14B(self) -> ProjectRegisters_Pn_Demod14B:
        """
        Specifies settings of the Demod register for 14B.
        """
        return ProjectRegisters_Pn_Demod14B(self)
    @property
    def ProjectRegisters_Pn_DemodALL(self) -> ProjectRegisters_Pn_DemodALL:
        """
        Specifies settings of the Demod register for ALL.
        """
        return ProjectRegisters_Pn_DemodALL(self)
    @property
    def ProjectRegisters_Pn_DemodVOLATILE(self) -> ProjectRegisters_Pn_DemodVOLATILE:
        """
        Specifies settings of the Demod register for VOLATILE.
        """
        return ProjectRegisters_Pn_DemodVOLATILE(self)
    @property
    def ProjectRegisters_Pn_MifNFC14A848(self) -> ProjectRegisters_Pn_MifNFC14A848:
        """
        Specifies settings of the MifNFC register for 14A_848.
        """
        return ProjectRegisters_Pn_MifNFC14A848(self)
    @property
    def ProjectRegisters_Pn_MifNFC14A424(self) -> ProjectRegisters_Pn_MifNFC14A424:
        """
        Specifies settings of the MifNFC register for 14A_424.
        """
        return ProjectRegisters_Pn_MifNFC14A424(self)
    @property
    def ProjectRegisters_Pn_MifNFC14A212(self) -> ProjectRegisters_Pn_MifNFC14A212:
        """
        Specifies settings of the MifNFC register for 14A_212.
        """
        return ProjectRegisters_Pn_MifNFC14A212(self)
    @property
    def ProjectRegisters_Pn_MifNFC14A106(self) -> ProjectRegisters_Pn_MifNFC14A106:
        """
        Specifies settings of the MifNFC register for 14A_106.
        """
        return ProjectRegisters_Pn_MifNFC14A106(self)
    @property
    def ProjectRegisters_Pn_MifNFC14B848(self) -> ProjectRegisters_Pn_MifNFC14B848:
        """
        Specifies settings of the MifNFC register for 14B_848.
        """
        return ProjectRegisters_Pn_MifNFC14B848(self)
    @property
    def ProjectRegisters_Pn_MifNFC14B424(self) -> ProjectRegisters_Pn_MifNFC14B424:
        """
        Specifies settings of the MifNFC register for 14B_424.
        """
        return ProjectRegisters_Pn_MifNFC14B424(self)
    @property
    def ProjectRegisters_Pn_MifNFC14B212(self) -> ProjectRegisters_Pn_MifNFC14B212:
        """
        Specifies settings of the MifNFC register for 14B_212.
        """
        return ProjectRegisters_Pn_MifNFC14B212(self)
    @property
    def ProjectRegisters_Pn_MifNFC14B106(self) -> ProjectRegisters_Pn_MifNFC14B106:
        """
        Specifies settings of the MifNFC register for 14B_106.
        """
        return ProjectRegisters_Pn_MifNFC14B106(self)
    @property
    def ProjectRegisters_Pn_MifNFC14A(self) -> ProjectRegisters_Pn_MifNFC14A:
        """
        Specifies settings of the MifNFC register for 14A.
        """
        return ProjectRegisters_Pn_MifNFC14A(self)
    @property
    def ProjectRegisters_Pn_MifNFC14B(self) -> ProjectRegisters_Pn_MifNFC14B:
        """
        Specifies settings of the MifNFC register for 14B.
        """
        return ProjectRegisters_Pn_MifNFC14B(self)
    @property
    def ProjectRegisters_Pn_MifNFCALL(self) -> ProjectRegisters_Pn_MifNFCALL:
        """
        Specifies settings of the MifNFC register for ALL.
        """
        return ProjectRegisters_Pn_MifNFCALL(self)
    @property
    def ProjectRegisters_Pn_MifNFCVOLATILE(self) -> ProjectRegisters_Pn_MifNFCVOLATILE:
        """
        Specifies settings of the MifNFC register for VOLATILE.
        """
        return ProjectRegisters_Pn_MifNFCVOLATILE(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14A848(self) -> ProjectRegisters_Pn_ManualRCV14A848:
        """
        Specifies settings of the ManualRCV register for 14A_848.
        """
        return ProjectRegisters_Pn_ManualRCV14A848(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14A424(self) -> ProjectRegisters_Pn_ManualRCV14A424:
        """
        Specifies settings of the ManualRCV register for 14A_424.
        """
        return ProjectRegisters_Pn_ManualRCV14A424(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14A212(self) -> ProjectRegisters_Pn_ManualRCV14A212:
        """
        Specifies settings of the ManualRCV register for 14A_212.
        """
        return ProjectRegisters_Pn_ManualRCV14A212(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14A106(self) -> ProjectRegisters_Pn_ManualRCV14A106:
        """
        Specifies settings of the ManualRCV register for 14A_106.
        """
        return ProjectRegisters_Pn_ManualRCV14A106(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14B848(self) -> ProjectRegisters_Pn_ManualRCV14B848:
        """
        Specifies settings of the ManualRCV register for 14B_848.
        """
        return ProjectRegisters_Pn_ManualRCV14B848(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14B424(self) -> ProjectRegisters_Pn_ManualRCV14B424:
        """
        Specifies settings of the ManualRCV register for 14B_424.
        """
        return ProjectRegisters_Pn_ManualRCV14B424(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14B212(self) -> ProjectRegisters_Pn_ManualRCV14B212:
        """
        Specifies settings of the ManualRCV register for 14B_212.
        """
        return ProjectRegisters_Pn_ManualRCV14B212(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14B106(self) -> ProjectRegisters_Pn_ManualRCV14B106:
        """
        Specifies settings of the ManualRCV register for 14B_106.
        """
        return ProjectRegisters_Pn_ManualRCV14B106(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14A(self) -> ProjectRegisters_Pn_ManualRCV14A:
        """
        Specifies settings of the ManualRCV register for 14A.
        """
        return ProjectRegisters_Pn_ManualRCV14A(self)
    @property
    def ProjectRegisters_Pn_ManualRCV14B(self) -> ProjectRegisters_Pn_ManualRCV14B:
        """
        Specifies settings of the ManualRCV register for 14B.
        """
        return ProjectRegisters_Pn_ManualRCV14B(self)
    @property
    def ProjectRegisters_Pn_ManualRCVALL(self) -> ProjectRegisters_Pn_ManualRCVALL:
        """
        Specifies settings of the ManualRCV register for ALL.
        """
        return ProjectRegisters_Pn_ManualRCVALL(self)
    @property
    def ProjectRegisters_Pn_ManualRCVVOLATILE(self) -> ProjectRegisters_Pn_ManualRCVVOLATILE:
        """
        Specifies settings of the ManualRCV register for VOLATILE.
        """
        return ProjectRegisters_Pn_ManualRCVVOLATILE(self)
    @property
    def ProjectRegisters_Pn_TypeB14A848(self) -> ProjectRegisters_Pn_TypeB14A848:
        """
        Specifies settings of the TypeB register for 14A_848.
        """
        return ProjectRegisters_Pn_TypeB14A848(self)
    @property
    def ProjectRegisters_Pn_TypeB14A424(self) -> ProjectRegisters_Pn_TypeB14A424:
        """
        Specifies settings of the TypeB register for 14A_424.
        """
        return ProjectRegisters_Pn_TypeB14A424(self)
    @property
    def ProjectRegisters_Pn_TypeB14A212(self) -> ProjectRegisters_Pn_TypeB14A212:
        """
        Specifies settings of the TypeB register for 14A_212.
        """
        return ProjectRegisters_Pn_TypeB14A212(self)
    @property
    def ProjectRegisters_Pn_TypeB14A106(self) -> ProjectRegisters_Pn_TypeB14A106:
        """
        Specifies settings of the TypeB register for 14A_106.
        """
        return ProjectRegisters_Pn_TypeB14A106(self)
    @property
    def ProjectRegisters_Pn_TypeB14B848(self) -> ProjectRegisters_Pn_TypeB14B848:
        """
        Specifies settings of the TypeB register for 14B_848.
        """
        return ProjectRegisters_Pn_TypeB14B848(self)
    @property
    def ProjectRegisters_Pn_TypeB14B424(self) -> ProjectRegisters_Pn_TypeB14B424:
        """
        Specifies settings of the TypeB register for 14B_424.
        """
        return ProjectRegisters_Pn_TypeB14B424(self)
    @property
    def ProjectRegisters_Pn_TypeB14B212(self) -> ProjectRegisters_Pn_TypeB14B212:
        """
        Specifies settings of the TypeB register for 14B_212.
        """
        return ProjectRegisters_Pn_TypeB14B212(self)
    @property
    def ProjectRegisters_Pn_TypeB14B106(self) -> ProjectRegisters_Pn_TypeB14B106:
        """
        Specifies settings of the TypeB register for 14B_106.
        """
        return ProjectRegisters_Pn_TypeB14B106(self)
    @property
    def ProjectRegisters_Pn_TypeB14A(self) -> ProjectRegisters_Pn_TypeB14A:
        """
        Specifies settings of the TypeB register for 14A.
        """
        return ProjectRegisters_Pn_TypeB14A(self)
    @property
    def ProjectRegisters_Pn_TypeB14B(self) -> ProjectRegisters_Pn_TypeB14B:
        """
        Specifies settings of the TypeB register for 14B.
        """
        return ProjectRegisters_Pn_TypeB14B(self)
    @property
    def ProjectRegisters_Pn_TypeBALL(self) -> ProjectRegisters_Pn_TypeBALL:
        """
        Specifies settings of the TypeB register for ALL.
        """
        return ProjectRegisters_Pn_TypeBALL(self)
    @property
    def ProjectRegisters_Pn_TypeBVOLATILE(self) -> ProjectRegisters_Pn_TypeBVOLATILE:
        """
        Specifies settings of the TypeB register for VOLATILE.
        """
        return ProjectRegisters_Pn_TypeBVOLATILE(self)
    @property
    def ProjectRegisters_Pn_GsNOff14A848(self) -> ProjectRegisters_Pn_GsNOff14A848:
        """
        Specifies settings of the GsNOff register for 14A_848.
        """
        return ProjectRegisters_Pn_GsNOff14A848(self)
    @property
    def ProjectRegisters_Pn_GsNOff14A424(self) -> ProjectRegisters_Pn_GsNOff14A424:
        """
        Specifies settings of the GsNOff register for 14A_424.
        """
        return ProjectRegisters_Pn_GsNOff14A424(self)
    @property
    def ProjectRegisters_Pn_GsNOff14A212(self) -> ProjectRegisters_Pn_GsNOff14A212:
        """
        Specifies settings of the GsNOff register for 14A_212.
        """
        return ProjectRegisters_Pn_GsNOff14A212(self)
    @property
    def ProjectRegisters_Pn_GsNOff14A106(self) -> ProjectRegisters_Pn_GsNOff14A106:
        """
        Specifies settings of the GsNOff register for 14A_106.
        """
        return ProjectRegisters_Pn_GsNOff14A106(self)
    @property
    def ProjectRegisters_Pn_GsNOff14B848(self) -> ProjectRegisters_Pn_GsNOff14B848:
        """
        Specifies settings of the GsNOff register for 14B_848.
        """
        return ProjectRegisters_Pn_GsNOff14B848(self)
    @property
    def ProjectRegisters_Pn_GsNOff14B424(self) -> ProjectRegisters_Pn_GsNOff14B424:
        """
        Specifies settings of the GsNOff register for 14B_424.
        """
        return ProjectRegisters_Pn_GsNOff14B424(self)
    @property
    def ProjectRegisters_Pn_GsNOff14B212(self) -> ProjectRegisters_Pn_GsNOff14B212:
        """
        Specifies settings of the GsNOff register for 14B_212.
        """
        return ProjectRegisters_Pn_GsNOff14B212(self)
    @property
    def ProjectRegisters_Pn_GsNOff14B106(self) -> ProjectRegisters_Pn_GsNOff14B106:
        """
        Specifies settings of the GsNOff register for 14B_106.
        """
        return ProjectRegisters_Pn_GsNOff14B106(self)
    @property
    def ProjectRegisters_Pn_GsNOff14A(self) -> ProjectRegisters_Pn_GsNOff14A:
        """
        Specifies settings of the GsNOff register for 14A.
        """
        return ProjectRegisters_Pn_GsNOff14A(self)
    @property
    def ProjectRegisters_Pn_GsNOff14B(self) -> ProjectRegisters_Pn_GsNOff14B:
        """
        Specifies settings of the GsNOff register for 14B.
        """
        return ProjectRegisters_Pn_GsNOff14B(self)
    @property
    def ProjectRegisters_Pn_GsNOffALL(self) -> ProjectRegisters_Pn_GsNOffALL:
        """
        Specifies settings of the GsNOff register for ALL.
        """
        return ProjectRegisters_Pn_GsNOffALL(self)
    @property
    def ProjectRegisters_Pn_GsNOffVOLATILE(self) -> ProjectRegisters_Pn_GsNOffVOLATILE:
        """
        Specifies settings of the GsNOff register for VOLATILE.
        """
        return ProjectRegisters_Pn_GsNOffVOLATILE(self)
    @property
    def ProjectRegisters_Pn_ModWith14A848(self) -> ProjectRegisters_Pn_ModWith14A848:
        """
        Specifies settings of the ModWith register for 14A_848.
        """
        return ProjectRegisters_Pn_ModWith14A848(self)
    @property
    def ProjectRegisters_Pn_ModWith14A424(self) -> ProjectRegisters_Pn_ModWith14A424:
        """
        Specifies settings of the ModWith register for 14A_424.
        """
        return ProjectRegisters_Pn_ModWith14A424(self)
    @property
    def ProjectRegisters_Pn_ModWith14A212(self) -> ProjectRegisters_Pn_ModWith14A212:
        """
        Specifies settings of the ModWith register for 14A_212.
        """
        return ProjectRegisters_Pn_ModWith14A212(self)
    @property
    def ProjectRegisters_Pn_ModWith14A106(self) -> ProjectRegisters_Pn_ModWith14A106:
        """
        Specifies settings of the ModWith register for 14A_106.
        """
        return ProjectRegisters_Pn_ModWith14A106(self)
    @property
    def ProjectRegisters_Pn_ModWith14B848(self) -> ProjectRegisters_Pn_ModWith14B848:
        """
        Specifies settings of the ModWith register for 14B_848.
        """
        return ProjectRegisters_Pn_ModWith14B848(self)
    @property
    def ProjectRegisters_Pn_ModWith14B424(self) -> ProjectRegisters_Pn_ModWith14B424:
        """
        Specifies settings of the ModWith register for 14B_424.
        """
        return ProjectRegisters_Pn_ModWith14B424(self)
    @property
    def ProjectRegisters_Pn_ModWith14B212(self) -> ProjectRegisters_Pn_ModWith14B212:
        """
        Specifies settings of the ModWith register for 14B_212.
        """
        return ProjectRegisters_Pn_ModWith14B212(self)
    @property
    def ProjectRegisters_Pn_ModWith14B106(self) -> ProjectRegisters_Pn_ModWith14B106:
        """
        Specifies settings of the ModWith register for 14B_106.
        """
        return ProjectRegisters_Pn_ModWith14B106(self)
    @property
    def ProjectRegisters_Pn_ModWith14A(self) -> ProjectRegisters_Pn_ModWith14A:
        """
        Specifies settings of the ModWith register for 14A.
        """
        return ProjectRegisters_Pn_ModWith14A(self)
    @property
    def ProjectRegisters_Pn_ModWith14B(self) -> ProjectRegisters_Pn_ModWith14B:
        """
        Specifies settings of the ModWith register for 14B.
        """
        return ProjectRegisters_Pn_ModWith14B(self)
    @property
    def ProjectRegisters_Pn_ModWithALL(self) -> ProjectRegisters_Pn_ModWithALL:
        """
        Specifies settings of the ModWith register for ALL.
        """
        return ProjectRegisters_Pn_ModWithALL(self)
    @property
    def ProjectRegisters_Pn_ModWithVOLATILE(self) -> ProjectRegisters_Pn_ModWithVOLATILE:
        """
        Specifies settings of the ModWith register for VOLATILE.
        """
        return ProjectRegisters_Pn_ModWithVOLATILE(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14A848(self) -> ProjectRegisters_Pn_TxBitPhase14A848:
        """
        Specifies settings of the TxBitPhase register for 14A_848.
        """
        return ProjectRegisters_Pn_TxBitPhase14A848(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14A424(self) -> ProjectRegisters_Pn_TxBitPhase14A424:
        """
        Specifies settings of the TxBitPhase register for 14A_424.
        """
        return ProjectRegisters_Pn_TxBitPhase14A424(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14A212(self) -> ProjectRegisters_Pn_TxBitPhase14A212:
        """
        Specifies settings of the TxBitPhase register for 14A_212.
        """
        return ProjectRegisters_Pn_TxBitPhase14A212(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14A106(self) -> ProjectRegisters_Pn_TxBitPhase14A106:
        """
        Specifies settings of the TxBitPhase register for 14A_106.
        """
        return ProjectRegisters_Pn_TxBitPhase14A106(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14B848(self) -> ProjectRegisters_Pn_TxBitPhase14B848:
        """
        Specifies settings of the TxBitPhase register for 14B_848.
        """
        return ProjectRegisters_Pn_TxBitPhase14B848(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14B424(self) -> ProjectRegisters_Pn_TxBitPhase14B424:
        """
        Specifies settings of the TxBitPhase register for 14B_424.
        """
        return ProjectRegisters_Pn_TxBitPhase14B424(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14B212(self) -> ProjectRegisters_Pn_TxBitPhase14B212:
        """
        Specifies settings of the TxBitPhase register for 14B_212.
        """
        return ProjectRegisters_Pn_TxBitPhase14B212(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14B106(self) -> ProjectRegisters_Pn_TxBitPhase14B106:
        """
        Specifies settings of the TxBitPhase register for 14B_106.
        """
        return ProjectRegisters_Pn_TxBitPhase14B106(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14A(self) -> ProjectRegisters_Pn_TxBitPhase14A:
        """
        Specifies settings of the TxBitPhase register for 14A.
        """
        return ProjectRegisters_Pn_TxBitPhase14A(self)
    @property
    def ProjectRegisters_Pn_TxBitPhase14B(self) -> ProjectRegisters_Pn_TxBitPhase14B:
        """
        Specifies settings of the TxBitPhase register for 14B.
        """
        return ProjectRegisters_Pn_TxBitPhase14B(self)
    @property
    def ProjectRegisters_Pn_TxBitPhaseALL(self) -> ProjectRegisters_Pn_TxBitPhaseALL:
        """
        Specifies settings of the TxBitPhase register for ALL.
        """
        return ProjectRegisters_Pn_TxBitPhaseALL(self)
    @property
    def ProjectRegisters_Pn_TxBitPhaseVOLATILE(self) -> ProjectRegisters_Pn_TxBitPhaseVOLATILE:
        """
        Specifies settings of the TxBitPhase register for VOLATILE.
        """
        return ProjectRegisters_Pn_TxBitPhaseVOLATILE(self)
    @property
    def ProjectRegisters_Pn_RFCfg14A848(self) -> ProjectRegisters_Pn_RFCfg14A848:
        """
        Specifies settings of the RFCfg register for 14A_848.
        """
        return ProjectRegisters_Pn_RFCfg14A848(self)
    @property
    def ProjectRegisters_Pn_RFCfg14A424(self) -> ProjectRegisters_Pn_RFCfg14A424:
        """
        Specifies settings of the RFCfg register for 14A_424.
        """
        return ProjectRegisters_Pn_RFCfg14A424(self)
    @property
    def ProjectRegisters_Pn_RFCfg14A212(self) -> ProjectRegisters_Pn_RFCfg14A212:
        """
        Specifies settings of the RFCfg register for 14A_212.
        """
        return ProjectRegisters_Pn_RFCfg14A212(self)
    @property
    def ProjectRegisters_Pn_RFCfg14A106(self) -> ProjectRegisters_Pn_RFCfg14A106:
        """
        Specifies settings of the RFCfg register for 14A_106.
        """
        return ProjectRegisters_Pn_RFCfg14A106(self)
    @property
    def ProjectRegisters_Pn_RFCfg14B848(self) -> ProjectRegisters_Pn_RFCfg14B848:
        """
        Specifies settings of the RFCfg register for 14B_848.
        """
        return ProjectRegisters_Pn_RFCfg14B848(self)
    @property
    def ProjectRegisters_Pn_RFCfg14B424(self) -> ProjectRegisters_Pn_RFCfg14B424:
        """
        Specifies settings of the RFCfg register for 14B_424.
        """
        return ProjectRegisters_Pn_RFCfg14B424(self)
    @property
    def ProjectRegisters_Pn_RFCfg14B212(self) -> ProjectRegisters_Pn_RFCfg14B212:
        """
        Specifies settings of the RFCfg register for 14B_212.
        """
        return ProjectRegisters_Pn_RFCfg14B212(self)
    @property
    def ProjectRegisters_Pn_RFCfg14B106(self) -> ProjectRegisters_Pn_RFCfg14B106:
        """
        Specifies settings of the RFCfg register for 14B_106.
        """
        return ProjectRegisters_Pn_RFCfg14B106(self)
    @property
    def ProjectRegisters_Pn_RFCfg14A(self) -> ProjectRegisters_Pn_RFCfg14A:
        """
        Specifies settings of the RFCfg register for 14A.
        """
        return ProjectRegisters_Pn_RFCfg14A(self)
    @property
    def ProjectRegisters_Pn_RFCfg14B(self) -> ProjectRegisters_Pn_RFCfg14B:
        """
        Specifies settings of the RFCfg register for 14B.
        """
        return ProjectRegisters_Pn_RFCfg14B(self)
    @property
    def ProjectRegisters_Pn_RFCfgALL(self) -> ProjectRegisters_Pn_RFCfgALL:
        """
        Specifies settings of the RFCfg register for ALL.
        """
        return ProjectRegisters_Pn_RFCfgALL(self)
    @property
    def ProjectRegisters_Pn_RFCfgVOLATILE(self) -> ProjectRegisters_Pn_RFCfgVOLATILE:
        """
        Specifies settings of the RFCfg register for VOLATILE.
        """
        return ProjectRegisters_Pn_RFCfgVOLATILE(self)
    @property
    def ProjectRegisters_Pn_GsNOn14A848(self) -> ProjectRegisters_Pn_GsNOn14A848:
        """
        Specifies settings of the GsNOn register for 14A_848.
        """
        return ProjectRegisters_Pn_GsNOn14A848(self)
    @property
    def ProjectRegisters_Pn_GsNOn14A424(self) -> ProjectRegisters_Pn_GsNOn14A424:
        """
        Specifies settings of the GsNOn register for 14A_424.
        """
        return ProjectRegisters_Pn_GsNOn14A424(self)
    @property
    def ProjectRegisters_Pn_GsNOn14A212(self) -> ProjectRegisters_Pn_GsNOn14A212:
        """
        Specifies settings of the GsNOn register for 14A_212.
        """
        return ProjectRegisters_Pn_GsNOn14A212(self)
    @property
    def ProjectRegisters_Pn_GsNOn14A106(self) -> ProjectRegisters_Pn_GsNOn14A106:
        """
        Specifies settings of the GsNOn register for 14A_106.
        """
        return ProjectRegisters_Pn_GsNOn14A106(self)
    @property
    def ProjectRegisters_Pn_GsNOn14B848(self) -> ProjectRegisters_Pn_GsNOn14B848:
        """
        Specifies settings of the GsNOn register for 14B_848.
        """
        return ProjectRegisters_Pn_GsNOn14B848(self)
    @property
    def ProjectRegisters_Pn_GsNOn14B424(self) -> ProjectRegisters_Pn_GsNOn14B424:
        """
        Specifies settings of the GsNOn register for 14B_424.
        """
        return ProjectRegisters_Pn_GsNOn14B424(self)
    @property
    def ProjectRegisters_Pn_GsNOn14B212(self) -> ProjectRegisters_Pn_GsNOn14B212:
        """
        Specifies settings of the GsNOn register for 14B_212.
        """
        return ProjectRegisters_Pn_GsNOn14B212(self)
    @property
    def ProjectRegisters_Pn_GsNOn14B106(self) -> ProjectRegisters_Pn_GsNOn14B106:
        """
        Specifies settings of the GsNOn register for 14B_106.
        """
        return ProjectRegisters_Pn_GsNOn14B106(self)
    @property
    def ProjectRegisters_Pn_GsNOn14A(self) -> ProjectRegisters_Pn_GsNOn14A:
        """
        Specifies settings of the GsNOn register for 14A.
        """
        return ProjectRegisters_Pn_GsNOn14A(self)
    @property
    def ProjectRegisters_Pn_GsNOn14B(self) -> ProjectRegisters_Pn_GsNOn14B:
        """
        Specifies settings of the GsNOn register for 14B.
        """
        return ProjectRegisters_Pn_GsNOn14B(self)
    @property
    def ProjectRegisters_Pn_GsNOnALL(self) -> ProjectRegisters_Pn_GsNOnALL:
        """
        Specifies settings of the GsNOn register for ALL.
        """
        return ProjectRegisters_Pn_GsNOnALL(self)
    @property
    def ProjectRegisters_Pn_GsNOnVOLATILE(self) -> ProjectRegisters_Pn_GsNOnVOLATILE:
        """
        Specifies settings of the GsNOn register for VOLATILE.
        """
        return ProjectRegisters_Pn_GsNOnVOLATILE(self)
    @property
    def ProjectRegisters_Pn_CWGsP14A848(self) -> ProjectRegisters_Pn_CWGsP14A848:
        """
        Specifies settings of the CWGsP register for 14A_848.
        """
        return ProjectRegisters_Pn_CWGsP14A848(self)
    @property
    def ProjectRegisters_Pn_CWGsP14A424(self) -> ProjectRegisters_Pn_CWGsP14A424:
        """
        Specifies settings of the CWGsP register for 14A_424.
        """
        return ProjectRegisters_Pn_CWGsP14A424(self)
    @property
    def ProjectRegisters_Pn_CWGsP14A212(self) -> ProjectRegisters_Pn_CWGsP14A212:
        """
        Specifies settings of the CWGsP register for 14A_212.
        """
        return ProjectRegisters_Pn_CWGsP14A212(self)
    @property
    def ProjectRegisters_Pn_CWGsP14A106(self) -> ProjectRegisters_Pn_CWGsP14A106:
        """
        Specifies settings of the CWGsP register for 14A_106.
        """
        return ProjectRegisters_Pn_CWGsP14A106(self)
    @property
    def ProjectRegisters_Pn_CWGsP14B848(self) -> ProjectRegisters_Pn_CWGsP14B848:
        """
        Specifies settings of the CWGsP register for 14B_848.
        """
        return ProjectRegisters_Pn_CWGsP14B848(self)
    @property
    def ProjectRegisters_Pn_CWGsP14B424(self) -> ProjectRegisters_Pn_CWGsP14B424:
        """
        Specifies settings of the CWGsP register for 14B_424.
        """
        return ProjectRegisters_Pn_CWGsP14B424(self)
    @property
    def ProjectRegisters_Pn_CWGsP14B212(self) -> ProjectRegisters_Pn_CWGsP14B212:
        """
        Specifies settings of the CWGsP register for 14B_212.
        """
        return ProjectRegisters_Pn_CWGsP14B212(self)
    @property
    def ProjectRegisters_Pn_CWGsP14B106(self) -> ProjectRegisters_Pn_CWGsP14B106:
        """
        Specifies settings of the CWGsP register for 14B_106.
        """
        return ProjectRegisters_Pn_CWGsP14B106(self)
    @property
    def ProjectRegisters_Pn_CWGsP14A(self) -> ProjectRegisters_Pn_CWGsP14A:
        """
        Specifies settings of the CWGsP register for 14A.
        """
        return ProjectRegisters_Pn_CWGsP14A(self)
    @property
    def ProjectRegisters_Pn_CWGsP14B(self) -> ProjectRegisters_Pn_CWGsP14B:
        """
        Specifies settings of the CWGsP register for 14B.
        """
        return ProjectRegisters_Pn_CWGsP14B(self)
    @property
    def ProjectRegisters_Pn_CWGsPALL(self) -> ProjectRegisters_Pn_CWGsPALL:
        """
        Specifies settings of the CWGsP register for ALL.
        """
        return ProjectRegisters_Pn_CWGsPALL(self)
    @property
    def ProjectRegisters_Pn_CWGsPVOLATILE(self) -> ProjectRegisters_Pn_CWGsPVOLATILE:
        """
        Specifies settings of the CWGsP register for VOLATILE.
        """
        return ProjectRegisters_Pn_CWGsPVOLATILE(self)
    @property
    def ProjectRegisters_Pn_ModGsP14A848(self) -> ProjectRegisters_Pn_ModGsP14A848:
        """
        Specifies settings of the ModGsP register for 14A_848.
        """
        return ProjectRegisters_Pn_ModGsP14A848(self)
    @property
    def ProjectRegisters_Pn_ModGsP14A424(self) -> ProjectRegisters_Pn_ModGsP14A424:
        """
        Specifies settings of the ModGsP register for 14A_424.
        """
        return ProjectRegisters_Pn_ModGsP14A424(self)
    @property
    def ProjectRegisters_Pn_ModGsP14A212(self) -> ProjectRegisters_Pn_ModGsP14A212:
        """
        Specifies settings of the ModGsP register for 14A_212.
        """
        return ProjectRegisters_Pn_ModGsP14A212(self)
    @property
    def ProjectRegisters_Pn_ModGsP14A106(self) -> ProjectRegisters_Pn_ModGsP14A106:
        """
        Specifies settings of the ModGsP register for 14A_106.
        """
        return ProjectRegisters_Pn_ModGsP14A106(self)
    @property
    def ProjectRegisters_Pn_ModGsP14B848(self) -> ProjectRegisters_Pn_ModGsP14B848:
        """
        Specifies settings of the ModGsP register for 14B_848.
        """
        return ProjectRegisters_Pn_ModGsP14B848(self)
    @property
    def ProjectRegisters_Pn_ModGsP14B424(self) -> ProjectRegisters_Pn_ModGsP14B424:
        """
        Specifies settings of the ModGsP register for 14B_424.
        """
        return ProjectRegisters_Pn_ModGsP14B424(self)
    @property
    def ProjectRegisters_Pn_ModGsP14B212(self) -> ProjectRegisters_Pn_ModGsP14B212:
        """
        Specifies settings of the ModGsP register for 14B_212.
        """
        return ProjectRegisters_Pn_ModGsP14B212(self)
    @property
    def ProjectRegisters_Pn_ModGsP14B106(self) -> ProjectRegisters_Pn_ModGsP14B106:
        """
        Specifies settings of the ModGsP register for 14B_106.
        """
        return ProjectRegisters_Pn_ModGsP14B106(self)
    @property
    def ProjectRegisters_Pn_ModGsP14A(self) -> ProjectRegisters_Pn_ModGsP14A:
        """
        Specifies settings of the ModGsP register for 14A.
        """
        return ProjectRegisters_Pn_ModGsP14A(self)
    @property
    def ProjectRegisters_Pn_ModGsP14B(self) -> ProjectRegisters_Pn_ModGsP14B:
        """
        Specifies settings of the ModGsP register for 14B.
        """
        return ProjectRegisters_Pn_ModGsP14B(self)
    @property
    def ProjectRegisters_Pn_ModGsPALL(self) -> ProjectRegisters_Pn_ModGsPALL:
        """
        Specifies settings of the ModGsP register for ALL.
        """
        return ProjectRegisters_Pn_ModGsPALL(self)
    @property
    def ProjectRegisters_Pn_ModGsPVOLATILE(self) -> ProjectRegisters_Pn_ModGsPVOLATILE:
        """
        Specifies settings of the ModGsP register for VOLATILE.
        """
        return ProjectRegisters_Pn_ModGsPVOLATILE(self)
    @property
    def ProjectRegisters_Rc663(self) -> ProjectRegisters_Rc663:
        """
        This value contains HF Settings (Register Settings) of the RC663 reader chip.
        """
        return ProjectRegisters_Rc663(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14A848(self) -> ProjectRegisters_Rc663_TxAmpReg14A848:
        """
        Specifies settings of the TxAmpReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_TxAmpReg14A848(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14A424(self) -> ProjectRegisters_Rc663_TxAmpReg14A424:
        """
        Specifies settings of the TxAmpReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_TxAmpReg14A424(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14A212(self) -> ProjectRegisters_Rc663_TxAmpReg14A212:
        """
        Specifies settings of the TxAmpReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_TxAmpReg14A212(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14A106(self) -> ProjectRegisters_Rc663_TxAmpReg14A106:
        """
        Specifies settings of the TxAmpReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_TxAmpReg14A106(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14B848(self) -> ProjectRegisters_Rc663_TxAmpReg14B848:
        """
        Specifies settings of the TxAmpReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_TxAmpReg14B848(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14B424(self) -> ProjectRegisters_Rc663_TxAmpReg14B424:
        """
        Specifies settings of the TxAmpReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_TxAmpReg14B424(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14B212(self) -> ProjectRegisters_Rc663_TxAmpReg14B212:
        """
        Specifies settings of the TxAmpReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_TxAmpReg14B212(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14B106(self) -> ProjectRegisters_Rc663_TxAmpReg14B106:
        """
        Specifies settings of the TxAmpReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_TxAmpReg14B106(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg15(self) -> ProjectRegisters_Rc663_TxAmpReg15:
        """
        Specifies settings of the TxAmpReg register for 15.
        """
        return ProjectRegisters_Rc663_TxAmpReg15(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14A(self) -> ProjectRegisters_Rc663_TxAmpReg14A:
        """
        Specifies settings of the TxAmpReg register for 14A.
        """
        return ProjectRegisters_Rc663_TxAmpReg14A(self)
    @property
    def ProjectRegisters_Rc663_TxAmpReg14B(self) -> ProjectRegisters_Rc663_TxAmpReg14B:
        """
        Specifies settings of the TxAmpReg register for 14B.
        """
        return ProjectRegisters_Rc663_TxAmpReg14B(self)
    @property
    def ProjectRegisters_Rc663_TxAmpRegALL(self) -> ProjectRegisters_Rc663_TxAmpRegALL:
        """
        Specifies settings of the TxAmpReg register for ALL.
        """
        return ProjectRegisters_Rc663_TxAmpRegALL(self)
    @property
    def ProjectRegisters_Rc663_TxAmpRegVOLATILE(self) -> ProjectRegisters_Rc663_TxAmpRegVOLATILE:
        """
        Specifies settings of the TxAmpReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_TxAmpRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14A848(self) -> ProjectRegisters_Rc663_TxDataModWithReg14A848:
        """
        Specifies settings of the TxDataModWithReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14A848(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14A424(self) -> ProjectRegisters_Rc663_TxDataModWithReg14A424:
        """
        Specifies settings of the TxDataModWithReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14A424(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14A212(self) -> ProjectRegisters_Rc663_TxDataModWithReg14A212:
        """
        Specifies settings of the TxDataModWithReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14A212(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14A106(self) -> ProjectRegisters_Rc663_TxDataModWithReg14A106:
        """
        Specifies settings of the TxDataModWithReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14A106(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14B848(self) -> ProjectRegisters_Rc663_TxDataModWithReg14B848:
        """
        Specifies settings of the TxDataModWithReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14B848(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14B424(self) -> ProjectRegisters_Rc663_TxDataModWithReg14B424:
        """
        Specifies settings of the TxDataModWithReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14B424(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14B212(self) -> ProjectRegisters_Rc663_TxDataModWithReg14B212:
        """
        Specifies settings of the TxDataModWithReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14B212(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14B106(self) -> ProjectRegisters_Rc663_TxDataModWithReg14B106:
        """
        Specifies settings of the TxDataModWithReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14B106(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg15(self) -> ProjectRegisters_Rc663_TxDataModWithReg15:
        """
        Specifies settings of the TxDataModWithReg register for 15.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg15(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14A(self) -> ProjectRegisters_Rc663_TxDataModWithReg14A:
        """
        Specifies settings of the TxDataModWithReg register for 14A.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14A(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithReg14B(self) -> ProjectRegisters_Rc663_TxDataModWithReg14B:
        """
        Specifies settings of the TxDataModWithReg register for 14B.
        """
        return ProjectRegisters_Rc663_TxDataModWithReg14B(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithRegALL(self) -> ProjectRegisters_Rc663_TxDataModWithRegALL:
        """
        Specifies settings of the TxDataModWithReg register for ALL.
        """
        return ProjectRegisters_Rc663_TxDataModWithRegALL(self)
    @property
    def ProjectRegisters_Rc663_TxDataModWithRegVOLATILE(self) -> ProjectRegisters_Rc663_TxDataModWithRegVOLATILE:
        """
        Specifies settings of the TxDataModWithReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_TxDataModWithRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14A848(self) -> ProjectRegisters_Rc663_RxThresholdReg14A848:
        """
        Specifies settings of the RxThresholdReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14A848(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14A424(self) -> ProjectRegisters_Rc663_RxThresholdReg14A424:
        """
        Specifies settings of the RxThresholdReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14A424(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14A212(self) -> ProjectRegisters_Rc663_RxThresholdReg14A212:
        """
        Specifies settings of the RxThresholdReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14A212(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14A106(self) -> ProjectRegisters_Rc663_RxThresholdReg14A106:
        """
        Specifies settings of the RxThresholdReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14A106(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14B848(self) -> ProjectRegisters_Rc663_RxThresholdReg14B848:
        """
        Specifies settings of the RxThresholdReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14B848(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14B424(self) -> ProjectRegisters_Rc663_RxThresholdReg14B424:
        """
        Specifies settings of the RxThresholdReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14B424(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14B212(self) -> ProjectRegisters_Rc663_RxThresholdReg14B212:
        """
        Specifies settings of the RxThresholdReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14B212(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14B106(self) -> ProjectRegisters_Rc663_RxThresholdReg14B106:
        """
        Specifies settings of the RxThresholdReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14B106(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg15(self) -> ProjectRegisters_Rc663_RxThresholdReg15:
        """
        Specifies settings of the RxThresholdReg register for 15.
        """
        return ProjectRegisters_Rc663_RxThresholdReg15(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14A(self) -> ProjectRegisters_Rc663_RxThresholdReg14A:
        """
        Specifies settings of the RxThresholdReg register for 14A.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14A(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdReg14B(self) -> ProjectRegisters_Rc663_RxThresholdReg14B:
        """
        Specifies settings of the RxThresholdReg register for 14B.
        """
        return ProjectRegisters_Rc663_RxThresholdReg14B(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdRegALL(self) -> ProjectRegisters_Rc663_RxThresholdRegALL:
        """
        Specifies settings of the RxThresholdReg register for ALL.
        """
        return ProjectRegisters_Rc663_RxThresholdRegALL(self)
    @property
    def ProjectRegisters_Rc663_RxThresholdRegVOLATILE(self) -> ProjectRegisters_Rc663_RxThresholdRegVOLATILE:
        """
        Specifies settings of the RxThresholdReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_RxThresholdRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14A848(self) -> ProjectRegisters_Rc663_RxAnaReg14A848:
        """
        Specifies settings of the RxAnaReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_RxAnaReg14A848(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14A424(self) -> ProjectRegisters_Rc663_RxAnaReg14A424:
        """
        Specifies settings of the RxAnaReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_RxAnaReg14A424(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14A212(self) -> ProjectRegisters_Rc663_RxAnaReg14A212:
        """
        Specifies settings of the RxAnaReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_RxAnaReg14A212(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14A106(self) -> ProjectRegisters_Rc663_RxAnaReg14A106:
        """
        Specifies settings of the RxAnaReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_RxAnaReg14A106(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14B848(self) -> ProjectRegisters_Rc663_RxAnaReg14B848:
        """
        Specifies settings of the RxAnaReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_RxAnaReg14B848(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14B424(self) -> ProjectRegisters_Rc663_RxAnaReg14B424:
        """
        Specifies settings of the RxAnaReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_RxAnaReg14B424(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14B212(self) -> ProjectRegisters_Rc663_RxAnaReg14B212:
        """
        Specifies settings of the RxAnaReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_RxAnaReg14B212(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14B106(self) -> ProjectRegisters_Rc663_RxAnaReg14B106:
        """
        Specifies settings of the RxAnaReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_RxAnaReg14B106(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg15(self) -> ProjectRegisters_Rc663_RxAnaReg15:
        """
        Specifies settings of the RxAnaReg register for 15.
        """
        return ProjectRegisters_Rc663_RxAnaReg15(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14A(self) -> ProjectRegisters_Rc663_RxAnaReg14A:
        """
        Specifies settings of the RxAnaReg register for 14A.
        """
        return ProjectRegisters_Rc663_RxAnaReg14A(self)
    @property
    def ProjectRegisters_Rc663_RxAnaReg14B(self) -> ProjectRegisters_Rc663_RxAnaReg14B:
        """
        Specifies settings of the RxAnaReg register for 14B.
        """
        return ProjectRegisters_Rc663_RxAnaReg14B(self)
    @property
    def ProjectRegisters_Rc663_RxAnaRegALL(self) -> ProjectRegisters_Rc663_RxAnaRegALL:
        """
        Specifies settings of the RxAnaReg register for ALL.
        """
        return ProjectRegisters_Rc663_RxAnaRegALL(self)
    @property
    def ProjectRegisters_Rc663_RxAnaRegVOLATILE(self) -> ProjectRegisters_Rc663_RxAnaRegVOLATILE:
        """
        Specifies settings of the RxAnaReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_RxAnaRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14A848(self) -> ProjectRegisters_Rc663_TxModeReg14A848:
        """
        Specifies settings of the TxModeReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_TxModeReg14A848(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14A424(self) -> ProjectRegisters_Rc663_TxModeReg14A424:
        """
        Specifies settings of the TxModeReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_TxModeReg14A424(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14A212(self) -> ProjectRegisters_Rc663_TxModeReg14A212:
        """
        Specifies settings of the TxModeReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_TxModeReg14A212(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14A106(self) -> ProjectRegisters_Rc663_TxModeReg14A106:
        """
        Specifies settings of the TxModeReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_TxModeReg14A106(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14B848(self) -> ProjectRegisters_Rc663_TxModeReg14B848:
        """
        Specifies settings of the TxModeReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_TxModeReg14B848(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14B424(self) -> ProjectRegisters_Rc663_TxModeReg14B424:
        """
        Specifies settings of the TxModeReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_TxModeReg14B424(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14B212(self) -> ProjectRegisters_Rc663_TxModeReg14B212:
        """
        Specifies settings of the TxModeReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_TxModeReg14B212(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14B106(self) -> ProjectRegisters_Rc663_TxModeReg14B106:
        """
        Specifies settings of the TxModeReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_TxModeReg14B106(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg15(self) -> ProjectRegisters_Rc663_TxModeReg15:
        """
        Specifies settings of the TxModeReg register for 15.
        """
        return ProjectRegisters_Rc663_TxModeReg15(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14A(self) -> ProjectRegisters_Rc663_TxModeReg14A:
        """
        Specifies settings of the TxModeReg register for 14A.
        """
        return ProjectRegisters_Rc663_TxModeReg14A(self)
    @property
    def ProjectRegisters_Rc663_TxModeReg14B(self) -> ProjectRegisters_Rc663_TxModeReg14B:
        """
        Specifies settings of the TxModeReg register for 14B.
        """
        return ProjectRegisters_Rc663_TxModeReg14B(self)
    @property
    def ProjectRegisters_Rc663_TxModeRegALL(self) -> ProjectRegisters_Rc663_TxModeRegALL:
        """
        Specifies settings of the TxModeReg register for ALL.
        """
        return ProjectRegisters_Rc663_TxModeRegALL(self)
    @property
    def ProjectRegisters_Rc663_TxModeRegVOLATILE(self) -> ProjectRegisters_Rc663_TxModeRegVOLATILE:
        """
        Specifies settings of the TxModeReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_TxModeRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14A848(self) -> ProjectRegisters_Rc663_TxConReg14A848:
        """
        Specifies settings of the TxConReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_TxConReg14A848(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14A424(self) -> ProjectRegisters_Rc663_TxConReg14A424:
        """
        Specifies settings of the TxConReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_TxConReg14A424(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14A212(self) -> ProjectRegisters_Rc663_TxConReg14A212:
        """
        Specifies settings of the TxConReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_TxConReg14A212(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14A106(self) -> ProjectRegisters_Rc663_TxConReg14A106:
        """
        Specifies settings of the TxConReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_TxConReg14A106(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14B848(self) -> ProjectRegisters_Rc663_TxConReg14B848:
        """
        Specifies settings of the TxConReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_TxConReg14B848(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14B424(self) -> ProjectRegisters_Rc663_TxConReg14B424:
        """
        Specifies settings of the TxConReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_TxConReg14B424(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14B212(self) -> ProjectRegisters_Rc663_TxConReg14B212:
        """
        Specifies settings of the TxConReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_TxConReg14B212(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14B106(self) -> ProjectRegisters_Rc663_TxConReg14B106:
        """
        Specifies settings of the TxConReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_TxConReg14B106(self)
    @property
    def ProjectRegisters_Rc663_TxConReg15(self) -> ProjectRegisters_Rc663_TxConReg15:
        """
        Specifies settings of the TxConReg register for 15.
        """
        return ProjectRegisters_Rc663_TxConReg15(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14A(self) -> ProjectRegisters_Rc663_TxConReg14A:
        """
        Specifies settings of the TxConReg register for 14A.
        """
        return ProjectRegisters_Rc663_TxConReg14A(self)
    @property
    def ProjectRegisters_Rc663_TxConReg14B(self) -> ProjectRegisters_Rc663_TxConReg14B:
        """
        Specifies settings of the TxConReg register for 14B.
        """
        return ProjectRegisters_Rc663_TxConReg14B(self)
    @property
    def ProjectRegisters_Rc663_TxConRegALL(self) -> ProjectRegisters_Rc663_TxConRegALL:
        """
        Specifies settings of the TxConReg register for ALL.
        """
        return ProjectRegisters_Rc663_TxConRegALL(self)
    @property
    def ProjectRegisters_Rc663_TxConRegVOLATILE(self) -> ProjectRegisters_Rc663_TxConRegVOLATILE:
        """
        Specifies settings of the TxConReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_TxConRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14A848(self) -> ProjectRegisters_Rc663_TxlReg14A848:
        """
        Specifies settings of the TxlReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_TxlReg14A848(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14A424(self) -> ProjectRegisters_Rc663_TxlReg14A424:
        """
        Specifies settings of the TxlReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_TxlReg14A424(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14A212(self) -> ProjectRegisters_Rc663_TxlReg14A212:
        """
        Specifies settings of the TxlReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_TxlReg14A212(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14A106(self) -> ProjectRegisters_Rc663_TxlReg14A106:
        """
        Specifies settings of the TxlReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_TxlReg14A106(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14B848(self) -> ProjectRegisters_Rc663_TxlReg14B848:
        """
        Specifies settings of the TxlReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_TxlReg14B848(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14B424(self) -> ProjectRegisters_Rc663_TxlReg14B424:
        """
        Specifies settings of the TxlReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_TxlReg14B424(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14B212(self) -> ProjectRegisters_Rc663_TxlReg14B212:
        """
        Specifies settings of the TxlReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_TxlReg14B212(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14B106(self) -> ProjectRegisters_Rc663_TxlReg14B106:
        """
        Specifies settings of the TxlReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_TxlReg14B106(self)
    @property
    def ProjectRegisters_Rc663_TxlReg15(self) -> ProjectRegisters_Rc663_TxlReg15:
        """
        Specifies settings of the TxlReg register for 15.
        """
        return ProjectRegisters_Rc663_TxlReg15(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14A(self) -> ProjectRegisters_Rc663_TxlReg14A:
        """
        Specifies settings of the TxlReg register for 14A.
        """
        return ProjectRegisters_Rc663_TxlReg14A(self)
    @property
    def ProjectRegisters_Rc663_TxlReg14B(self) -> ProjectRegisters_Rc663_TxlReg14B:
        """
        Specifies settings of the TxlReg register for 14B.
        """
        return ProjectRegisters_Rc663_TxlReg14B(self)
    @property
    def ProjectRegisters_Rc663_TxlRegALL(self) -> ProjectRegisters_Rc663_TxlRegALL:
        """
        Specifies settings of the TxlReg register for ALL.
        """
        return ProjectRegisters_Rc663_TxlRegALL(self)
    @property
    def ProjectRegisters_Rc663_TxlRegVOLATILE(self) -> ProjectRegisters_Rc663_TxlRegVOLATILE:
        """
        Specifies settings of the TxlReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_TxlRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14A848(self) -> ProjectRegisters_Rc663_RxWaitReg14A848:
        """
        Specifies settings of the RxWaitReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_RxWaitReg14A848(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14A424(self) -> ProjectRegisters_Rc663_RxWaitReg14A424:
        """
        Specifies settings of the RxWaitReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_RxWaitReg14A424(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14A212(self) -> ProjectRegisters_Rc663_RxWaitReg14A212:
        """
        Specifies settings of the RxWaitReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_RxWaitReg14A212(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14A106(self) -> ProjectRegisters_Rc663_RxWaitReg14A106:
        """
        Specifies settings of the RxWaitReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_RxWaitReg14A106(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14B848(self) -> ProjectRegisters_Rc663_RxWaitReg14B848:
        """
        Specifies settings of the RxWaitReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_RxWaitReg14B848(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14B424(self) -> ProjectRegisters_Rc663_RxWaitReg14B424:
        """
        Specifies settings of the RxWaitReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_RxWaitReg14B424(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14B212(self) -> ProjectRegisters_Rc663_RxWaitReg14B212:
        """
        Specifies settings of the RxWaitReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_RxWaitReg14B212(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14B106(self) -> ProjectRegisters_Rc663_RxWaitReg14B106:
        """
        Specifies settings of the RxWaitReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_RxWaitReg14B106(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg15(self) -> ProjectRegisters_Rc663_RxWaitReg15:
        """
        Specifies settings of the RxWaitReg register for 15.
        """
        return ProjectRegisters_Rc663_RxWaitReg15(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14A(self) -> ProjectRegisters_Rc663_RxWaitReg14A:
        """
        Specifies settings of the RxWaitReg register for 14A.
        """
        return ProjectRegisters_Rc663_RxWaitReg14A(self)
    @property
    def ProjectRegisters_Rc663_RxWaitReg14B(self) -> ProjectRegisters_Rc663_RxWaitReg14B:
        """
        Specifies settings of the RxWaitReg register for 14B.
        """
        return ProjectRegisters_Rc663_RxWaitReg14B(self)
    @property
    def ProjectRegisters_Rc663_RxWaitRegALL(self) -> ProjectRegisters_Rc663_RxWaitRegALL:
        """
        Specifies settings of the RxWaitReg register for ALL.
        """
        return ProjectRegisters_Rc663_RxWaitRegALL(self)
    @property
    def ProjectRegisters_Rc663_RxWaitRegVOLATILE(self) -> ProjectRegisters_Rc663_RxWaitRegVOLATILE:
        """
        Specifies settings of the RxWaitReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_RxWaitRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14A848(self) -> ProjectRegisters_Rc663_RcvReg14A848:
        """
        Specifies settings of the RcvReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_RcvReg14A848(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14A424(self) -> ProjectRegisters_Rc663_RcvReg14A424:
        """
        Specifies settings of the RcvReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_RcvReg14A424(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14A212(self) -> ProjectRegisters_Rc663_RcvReg14A212:
        """
        Specifies settings of the RcvReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_RcvReg14A212(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14A106(self) -> ProjectRegisters_Rc663_RcvReg14A106:
        """
        Specifies settings of the RcvReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_RcvReg14A106(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14B848(self) -> ProjectRegisters_Rc663_RcvReg14B848:
        """
        Specifies settings of the RcvReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_RcvReg14B848(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14B424(self) -> ProjectRegisters_Rc663_RcvReg14B424:
        """
        Specifies settings of the RcvReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_RcvReg14B424(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14B212(self) -> ProjectRegisters_Rc663_RcvReg14B212:
        """
        Specifies settings of the RcvReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_RcvReg14B212(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14B106(self) -> ProjectRegisters_Rc663_RcvReg14B106:
        """
        Specifies settings of the RcvReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_RcvReg14B106(self)
    @property
    def ProjectRegisters_Rc663_RcvReg15(self) -> ProjectRegisters_Rc663_RcvReg15:
        """
        Specifies settings of the RcvReg register for 15.
        """
        return ProjectRegisters_Rc663_RcvReg15(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14A(self) -> ProjectRegisters_Rc663_RcvReg14A:
        """
        Specifies settings of the RcvReg register for 14A.
        """
        return ProjectRegisters_Rc663_RcvReg14A(self)
    @property
    def ProjectRegisters_Rc663_RcvReg14B(self) -> ProjectRegisters_Rc663_RcvReg14B:
        """
        Specifies settings of the RcvReg register for 14B.
        """
        return ProjectRegisters_Rc663_RcvReg14B(self)
    @property
    def ProjectRegisters_Rc663_RcvRegALL(self) -> ProjectRegisters_Rc663_RcvRegALL:
        """
        Specifies settings of the RcvReg register for ALL.
        """
        return ProjectRegisters_Rc663_RcvRegALL(self)
    @property
    def ProjectRegisters_Rc663_RcvRegVOLATILE(self) -> ProjectRegisters_Rc663_RcvRegVOLATILE:
        """
        Specifies settings of the RcvReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_RcvRegVOLATILE(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14A848(self) -> ProjectRegisters_Rc663_SigOutReg14A848:
        """
        Specifies settings of the SigOutReg register for 14A_848.
        """
        return ProjectRegisters_Rc663_SigOutReg14A848(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14A424(self) -> ProjectRegisters_Rc663_SigOutReg14A424:
        """
        Specifies settings of the SigOutReg register for 14A_424.
        """
        return ProjectRegisters_Rc663_SigOutReg14A424(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14A212(self) -> ProjectRegisters_Rc663_SigOutReg14A212:
        """
        Specifies settings of the SigOutReg register for 14A_212.
        """
        return ProjectRegisters_Rc663_SigOutReg14A212(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14A106(self) -> ProjectRegisters_Rc663_SigOutReg14A106:
        """
        Specifies settings of the SigOutReg register for 14A_106.
        """
        return ProjectRegisters_Rc663_SigOutReg14A106(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14B848(self) -> ProjectRegisters_Rc663_SigOutReg14B848:
        """
        Specifies settings of the SigOutReg register for 14B_848.
        """
        return ProjectRegisters_Rc663_SigOutReg14B848(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14B424(self) -> ProjectRegisters_Rc663_SigOutReg14B424:
        """
        Specifies settings of the SigOutReg register for 14B_424.
        """
        return ProjectRegisters_Rc663_SigOutReg14B424(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14B212(self) -> ProjectRegisters_Rc663_SigOutReg14B212:
        """
        Specifies settings of the SigOutReg register for 14B_212.
        """
        return ProjectRegisters_Rc663_SigOutReg14B212(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14B106(self) -> ProjectRegisters_Rc663_SigOutReg14B106:
        """
        Specifies settings of the SigOutReg register for 14B_106.
        """
        return ProjectRegisters_Rc663_SigOutReg14B106(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg15(self) -> ProjectRegisters_Rc663_SigOutReg15:
        """
        Specifies settings of the SigOutReg register for 15.
        """
        return ProjectRegisters_Rc663_SigOutReg15(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14A(self) -> ProjectRegisters_Rc663_SigOutReg14A:
        """
        Specifies settings of the SigOutReg register for 14A.
        """
        return ProjectRegisters_Rc663_SigOutReg14A(self)
    @property
    def ProjectRegisters_Rc663_SigOutReg14B(self) -> ProjectRegisters_Rc663_SigOutReg14B:
        """
        Specifies settings of the SigOutReg register for 14B.
        """
        return ProjectRegisters_Rc663_SigOutReg14B(self)
    @property
    def ProjectRegisters_Rc663_SigOutRegALL(self) -> ProjectRegisters_Rc663_SigOutRegALL:
        """
        Specifies settings of the SigOutReg register for ALL.
        """
        return ProjectRegisters_Rc663_SigOutRegALL(self)
    @property
    def ProjectRegisters_Rc663_SigOutRegVOLATILE(self) -> ProjectRegisters_Rc663_SigOutRegVOLATILE:
        """
        Specifies settings of the SigOutReg register for VOLATILE.
        """
        return ProjectRegisters_Rc663_SigOutRegVOLATILE(self)
    @property
    def ProjectRegisters_Htrc110(self) -> ProjectRegisters_Htrc110:
        """
        This value contains HF Settings (Register Settings) of the HTRC110 reader
        chip. (125 kHz)
        """
        return ProjectRegisters_Htrc110(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainHTG8(self) -> ProjectRegisters_Htrc110_MainfilterGainHTG8:
        """
        Specifies settings of the MainfilterGain register for HTG8.
        """
        return ProjectRegisters_Htrc110_MainfilterGainHTG8(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainHTG16(self) -> ProjectRegisters_Htrc110_MainfilterGainHTG16:
        """
        Specifies settings of the MainfilterGain register for HTG16.
        """
        return ProjectRegisters_Htrc110_MainfilterGainHTG16(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainHTG32(self) -> ProjectRegisters_Htrc110_MainfilterGainHTG32:
        """
        Specifies settings of the MainfilterGain register for HTG32.
        """
        return ProjectRegisters_Htrc110_MainfilterGainHTG32(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainHTG64(self) -> ProjectRegisters_Htrc110_MainfilterGainHTG64:
        """
        Specifies settings of the MainfilterGain register for HTG64.
        """
        return ProjectRegisters_Htrc110_MainfilterGainHTG64(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainEM8(self) -> ProjectRegisters_Htrc110_MainfilterGainEM8:
        """
        Specifies settings of the MainfilterGain register for EM8.
        """
        return ProjectRegisters_Htrc110_MainfilterGainEM8(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainEM16(self) -> ProjectRegisters_Htrc110_MainfilterGainEM16:
        """
        Specifies settings of the MainfilterGain register for EM16.
        """
        return ProjectRegisters_Htrc110_MainfilterGainEM16(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainEM32(self) -> ProjectRegisters_Htrc110_MainfilterGainEM32:
        """
        Specifies settings of the MainfilterGain register for EM32.
        """
        return ProjectRegisters_Htrc110_MainfilterGainEM32(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainEM64(self) -> ProjectRegisters_Htrc110_MainfilterGainEM64:
        """
        Specifies settings of the MainfilterGain register for EM64.
        """
        return ProjectRegisters_Htrc110_MainfilterGainEM64(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainPSK(self) -> ProjectRegisters_Htrc110_MainfilterGainPSK:
        """
        Specifies settings of the MainfilterGain register for PSK.
        """
        return ProjectRegisters_Htrc110_MainfilterGainPSK(self)
    @property
    def ProjectRegisters_Htrc110_MainfilterGainFSK(self) -> ProjectRegisters_Htrc110_MainfilterGainFSK:
        """
        Specifies settings of the MainfilterGain register for FSK.
        """
        return ProjectRegisters_Htrc110_MainfilterGainFSK(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpHTG8(self) -> ProjectRegisters_Htrc110_SmartcompLpHTG8:
        """
        Specifies settings of the SmartcompLp register for HTG8.
        """
        return ProjectRegisters_Htrc110_SmartcompLpHTG8(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpHTG16(self) -> ProjectRegisters_Htrc110_SmartcompLpHTG16:
        """
        Specifies settings of the SmartcompLp register for HTG16.
        """
        return ProjectRegisters_Htrc110_SmartcompLpHTG16(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpHTG32(self) -> ProjectRegisters_Htrc110_SmartcompLpHTG32:
        """
        Specifies settings of the SmartcompLp register for HTG32.
        """
        return ProjectRegisters_Htrc110_SmartcompLpHTG32(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpHTG64(self) -> ProjectRegisters_Htrc110_SmartcompLpHTG64:
        """
        Specifies settings of the SmartcompLp register for HTG64.
        """
        return ProjectRegisters_Htrc110_SmartcompLpHTG64(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpEM8(self) -> ProjectRegisters_Htrc110_SmartcompLpEM8:
        """
        Specifies settings of the SmartcompLp register for EM8.
        """
        return ProjectRegisters_Htrc110_SmartcompLpEM8(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpEM16(self) -> ProjectRegisters_Htrc110_SmartcompLpEM16:
        """
        Specifies settings of the SmartcompLp register for EM16.
        """
        return ProjectRegisters_Htrc110_SmartcompLpEM16(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpEM32(self) -> ProjectRegisters_Htrc110_SmartcompLpEM32:
        """
        Specifies settings of the SmartcompLp register for EM32.
        """
        return ProjectRegisters_Htrc110_SmartcompLpEM32(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpEM64(self) -> ProjectRegisters_Htrc110_SmartcompLpEM64:
        """
        Specifies settings of the SmartcompLp register for EM64.
        """
        return ProjectRegisters_Htrc110_SmartcompLpEM64(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpPSK(self) -> ProjectRegisters_Htrc110_SmartcompLpPSK:
        """
        Specifies settings of the SmartcompLp register for PSK.
        """
        return ProjectRegisters_Htrc110_SmartcompLpPSK(self)
    @property
    def ProjectRegisters_Htrc110_SmartcompLpFSK(self) -> ProjectRegisters_Htrc110_SmartcompLpFSK:
        """
        Specifies settings of the SmartcompLp register for FSK.
        """
        return ProjectRegisters_Htrc110_SmartcompLpFSK(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseHTG8(self) -> ProjectRegisters_Htrc110_SamplingPhaseHTG8:
        """
        Specifies settings of the SamplingPhase register for HTG8.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseHTG8(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseHTG16(self) -> ProjectRegisters_Htrc110_SamplingPhaseHTG16:
        """
        Specifies settings of the SamplingPhase register for HTG16.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseHTG16(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseHTG32(self) -> ProjectRegisters_Htrc110_SamplingPhaseHTG32:
        """
        Specifies settings of the SamplingPhase register for HTG32.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseHTG32(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseHTG64(self) -> ProjectRegisters_Htrc110_SamplingPhaseHTG64:
        """
        Specifies settings of the SamplingPhase register for HTG64.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseHTG64(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseEM8(self) -> ProjectRegisters_Htrc110_SamplingPhaseEM8:
        """
        Specifies settings of the SamplingPhase register for EM8.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseEM8(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseEM16(self) -> ProjectRegisters_Htrc110_SamplingPhaseEM16:
        """
        Specifies settings of the SamplingPhase register for EM16.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseEM16(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseEM32(self) -> ProjectRegisters_Htrc110_SamplingPhaseEM32:
        """
        Specifies settings of the SamplingPhase register for EM32.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseEM32(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseEM64(self) -> ProjectRegisters_Htrc110_SamplingPhaseEM64:
        """
        Specifies settings of the SamplingPhase register for EM64.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseEM64(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhasePSK(self) -> ProjectRegisters_Htrc110_SamplingPhasePSK:
        """
        Specifies settings of the SamplingPhase register for PSK.
        """
        return ProjectRegisters_Htrc110_SamplingPhasePSK(self)
    @property
    def ProjectRegisters_Htrc110_SamplingPhaseFSK(self) -> ProjectRegisters_Htrc110_SamplingPhaseFSK:
        """
        Specifies settings of the SamplingPhase register for FSK.
        """
        return ProjectRegisters_Htrc110_SamplingPhaseFSK(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelHTG8(self) -> ProjectRegisters_Htrc110_AcLevelHTG8:
        """
        Specifies settings of the AcLevel register for HTG8.
        """
        return ProjectRegisters_Htrc110_AcLevelHTG8(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelHTG16(self) -> ProjectRegisters_Htrc110_AcLevelHTG16:
        """
        Specifies settings of the AcLevel register for HTG16.
        """
        return ProjectRegisters_Htrc110_AcLevelHTG16(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelHTG32(self) -> ProjectRegisters_Htrc110_AcLevelHTG32:
        """
        Specifies settings of the AcLevel register for HTG32.
        """
        return ProjectRegisters_Htrc110_AcLevelHTG32(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelHTG64(self) -> ProjectRegisters_Htrc110_AcLevelHTG64:
        """
        Specifies settings of the AcLevel register for HTG64.
        """
        return ProjectRegisters_Htrc110_AcLevelHTG64(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelEM8(self) -> ProjectRegisters_Htrc110_AcLevelEM8:
        """
        Specifies settings of the AcLevel register for EM8.
        """
        return ProjectRegisters_Htrc110_AcLevelEM8(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelEM16(self) -> ProjectRegisters_Htrc110_AcLevelEM16:
        """
        Specifies settings of the AcLevel register for EM16.
        """
        return ProjectRegisters_Htrc110_AcLevelEM16(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelEM32(self) -> ProjectRegisters_Htrc110_AcLevelEM32:
        """
        Specifies settings of the AcLevel register for EM32.
        """
        return ProjectRegisters_Htrc110_AcLevelEM32(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelEM64(self) -> ProjectRegisters_Htrc110_AcLevelEM64:
        """
        Specifies settings of the AcLevel register for EM64.
        """
        return ProjectRegisters_Htrc110_AcLevelEM64(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelPSK(self) -> ProjectRegisters_Htrc110_AcLevelPSK:
        """
        Specifies settings of the AcLevel register for PSK.
        """
        return ProjectRegisters_Htrc110_AcLevelPSK(self)
    @property
    def ProjectRegisters_Htrc110_AcLevelFSK(self) -> ProjectRegisters_Htrc110_AcLevelFSK:
        """
        Specifies settings of the AcLevel register for FSK.
        """
        return ProjectRegisters_Htrc110_AcLevelFSK(self)
    @property
    def ProjectRegisters_Htrc110_AcHystHTG8(self) -> ProjectRegisters_Htrc110_AcHystHTG8:
        """
        Specifies settings of the AcHyst register for HTG8.
        """
        return ProjectRegisters_Htrc110_AcHystHTG8(self)
    @property
    def ProjectRegisters_Htrc110_AcHystHTG16(self) -> ProjectRegisters_Htrc110_AcHystHTG16:
        """
        Specifies settings of the AcHyst register for HTG16.
        """
        return ProjectRegisters_Htrc110_AcHystHTG16(self)
    @property
    def ProjectRegisters_Htrc110_AcHystHTG32(self) -> ProjectRegisters_Htrc110_AcHystHTG32:
        """
        Specifies settings of the AcHyst register for HTG32.
        """
        return ProjectRegisters_Htrc110_AcHystHTG32(self)
    @property
    def ProjectRegisters_Htrc110_AcHystHTG64(self) -> ProjectRegisters_Htrc110_AcHystHTG64:
        """
        Specifies settings of the AcHyst register for HTG64.
        """
        return ProjectRegisters_Htrc110_AcHystHTG64(self)
    @property
    def ProjectRegisters_Htrc110_AcHystEM8(self) -> ProjectRegisters_Htrc110_AcHystEM8:
        """
        Specifies settings of the AcHyst register for EM8.
        """
        return ProjectRegisters_Htrc110_AcHystEM8(self)
    @property
    def ProjectRegisters_Htrc110_AcHystEM16(self) -> ProjectRegisters_Htrc110_AcHystEM16:
        """
        Specifies settings of the AcHyst register for EM16.
        """
        return ProjectRegisters_Htrc110_AcHystEM16(self)
    @property
    def ProjectRegisters_Htrc110_AcHystEM32(self) -> ProjectRegisters_Htrc110_AcHystEM32:
        """
        Specifies settings of the AcHyst register for EM32.
        """
        return ProjectRegisters_Htrc110_AcHystEM32(self)
    @property
    def ProjectRegisters_Htrc110_AcHystEM64(self) -> ProjectRegisters_Htrc110_AcHystEM64:
        """
        Specifies settings of the AcHyst register for EM64.
        """
        return ProjectRegisters_Htrc110_AcHystEM64(self)
    @property
    def ProjectRegisters_Htrc110_AcHystPSK(self) -> ProjectRegisters_Htrc110_AcHystPSK:
        """
        Specifies settings of the AcHyst register for PSK.
        """
        return ProjectRegisters_Htrc110_AcHystPSK(self)
    @property
    def ProjectRegisters_Htrc110_AcHystFSK(self) -> ProjectRegisters_Htrc110_AcHystFSK:
        """
        Specifies settings of the AcHyst register for FSK.
        """
        return ProjectRegisters_Htrc110_AcHystFSK(self)
    @property
    def Protocols(self) -> Protocols:
        """
        This key contains all host protocol specific settings. Every subkey is for a
        specific protocol.
        """
        return Protocols(self)
    @property
    def Protocols_BrpSerial(self) -> Protocols_BrpSerial:
        """
        Specifies all Values than can be used to parametrize the BRP over Serial
        protocol. BRP over Serial includes data transfer via RS-232/UART and via USB
        using a Virtual-COM-Port driver at the host PC.
        """
        return Protocols_BrpSerial(self)
    @property
    def Protocols_BrpSerial_Baudrate(self) -> Protocols_BrpSerial_Baudrate:
        """
        Define the Data transfer speed in 100 bits per second
        """
        return Protocols_BrpSerial_Baudrate(self)
    @property
    def Protocols_BrpSerial_Parity(self) -> Protocols_BrpSerial_Parity:
        """
        Define if a parity bit shall be used to ensure correctness of transfer data
        and if so, what type of parity bits shall be used.
        """
        return Protocols_BrpSerial_Parity(self)
    @property
    def Protocols_BrpSerial_InterbyteTimeout(self) -> Protocols_BrpSerial_InterbyteTimeout:
        """
        Specifies the maximum time in ms which may elapse between two bytes within the
        same frame.
        
        Two value formats are supported: 8-bit is the legacy format. For new projects
        16-bit values should be used.
        """
        return Protocols_BrpSerial_InterbyteTimeout(self)
    @property
    def Protocols_BrpSerial_CmdWorkInterval(self) -> Protocols_BrpSerial_CmdWorkInterval:
        """
        Time in ms between a command sent in continuous or repeat mode and the first
        CMD_WORK message.
        
        When this value is set to 0xFFFF (default), no CMD_WORK message is sent until
        the command is finished.
        """
        return Protocols_BrpSerial_CmdWorkInterval(self)
    @property
    def Protocols_BrpSerial_RepeatModeMinDelay(self) -> Protocols_BrpSerial_RepeatModeMinDelay:
        """
        This value specifies the minimum time in ms between two responses sent in
        repeat mode. If not set, a default of 100ms is assumed.
        """
        return Protocols_BrpSerial_RepeatModeMinDelay(self)
    @property
    def Protocols_BrpSerial_HostMsgFormatTemplate(self) -> Protocols_BrpSerial_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_BrpSerial_HostMsgFormatTemplate(self)
    @property
    def Protocols_BrpSerial_AutoRunCommand(self) -> Protocols_BrpSerial_AutoRunCommand:
        """
        A list of BRP command frames that shall be executed automatically at powerup
        (including sending their responses to the host) before starting with normal
        operation.
        
        **These commands are executed in order (_first_ StartupRunCmd[0],_then_
        StartupRunCmd[1], ...) until the first index without corresponding
        StartupRunCmd value.**
        """
        return Protocols_BrpSerial_AutoRunCommand(self)
    @property
    def Protocols_BrpHid(self) -> Protocols_BrpHid:
        """
        USB Protocol that tunnels BRP over the Human Interface Protocol specified at
        usb.org (see http://en.wikipedia.org/wiki/Human_interface_device). For a
        detailed spec how BRP frames are packed into HID frames see BRP.pdf
        """
        return Protocols_BrpHid(self)
    @property
    def Protocols_BrpHid_CmdWorkInterval(self) -> Protocols_BrpHid_CmdWorkInterval:
        """
        Time in ms between a command sent in continuous or repeat mode and the first
        CMD_WORK message.
        
        When this value is set to 0xFFFF (default), no CMD_WORK message is sent until
        the command is finished.
        """
        return Protocols_BrpHid_CmdWorkInterval(self)
    @property
    def Protocols_BrpHid_RepeatModeMinDelay(self) -> Protocols_BrpHid_RepeatModeMinDelay:
        """
        This value specifies the minimum time in ms between two responses sent in
        repeat mode. If not set, a default of 100ms is assumed.
        """
        return Protocols_BrpHid_RepeatModeMinDelay(self)
    @property
    def Protocols_BrpHid_UsbVendorName(self) -> Protocols_BrpHid_UsbVendorName:
        """
        This is the USB Vendor Name that the device reports to the USB host.
        """
        return Protocols_BrpHid_UsbVendorName(self)
    @property
    def Protocols_BrpHid_UsbProductName(self) -> Protocols_BrpHid_UsbProductName:
        """
        This is the USB Product Name that the device reports to the USB host.
        """
        return Protocols_BrpHid_UsbProductName(self)
    @property
    def Protocols_BrpHid_UsbSerialNumber(self) -> Protocols_BrpHid_UsbSerialNumber:
        """
        This is the USB Serial number the device reports to the USB host. If this
        value is not defined the reader uses the factory programmed device serial
        number.
        """
        return Protocols_BrpHid_UsbSerialNumber(self)
    @property
    def Protocols_BrpHid_HostMsgFormatTemplate(self) -> Protocols_BrpHid_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_BrpHid_HostMsgFormatTemplate(self)
    @property
    def Protocols_BrpHid_AutoRunCommand(self) -> Protocols_BrpHid_AutoRunCommand:
        """
        A list of BRP command frames that shall be executed automatically at powerup
        (including sending their responses to the host) before starting with normal
        operation.
        
        **These commands are executed in order (_first_ StartupRunCmd[0],_then_
        StartupRunCmd[1], ...) until the first index without corresponding
        StartupRunCmd value.**
        """
        return Protocols_BrpHid_AutoRunCommand(self)
    @property
    def Protocols_SNet(self) -> Protocols_SNet:
        """
        Configuration values for S-Net protocol used in ACCESS200
        """
        return Protocols_SNet(self)
    @property
    def Protocols_SNet_BusAddress(self) -> Protocols_SNet_BusAddress:
        """
        S-Net bus address values: 0x00-0x7F. If you don't want to use BALTECH AdrCard,
        you can set a fixed bus address with this value.
        """
        return Protocols_SNet_BusAddress(self)
    @property
    def Protocols_SNet_DeviceType(self) -> Protocols_SNet_DeviceType:
        return Protocols_SNet_DeviceType(self)
    @property
    def Protocols_SNet_HostMsgFormatTemplate(self) -> Protocols_SNet_HostMsgFormatTemplate:
        """
        Specifies the way the ASCII decimal number read from the card by Autoread is
        to be converted to the low-level format needed by this protocol.
        """
        return Protocols_SNet_HostMsgFormatTemplate(self)
    @property
    def Protocols_BrpTcp(self) -> Protocols_BrpTcp:
        """
        This subkey specifies all protocol parameters needed for the BRP over TCP
        protocol.
        """
        return Protocols_BrpTcp(self)
    @property
    def Protocols_BrpTcp_CmdWorkInterval(self) -> Protocols_BrpTcp_CmdWorkInterval:
        """
        Time in ms between a command sent in continuous or repeat mode and the first
        CMD_WORK message.
        
        When this value is set to 0xFFFF (default), no CMD_WORK message is sent until
        the command is finished.
        """
        return Protocols_BrpTcp_CmdWorkInterval(self)
    @property
    def Protocols_BrpTcp_RepeatModeMinDelay(self) -> Protocols_BrpTcp_RepeatModeMinDelay:
        """
        This value specifies the minimum time in ms between two responses sent in
        repeat mode. If not set, a default of 100ms is assumed.
        """
        return Protocols_BrpTcp_RepeatModeMinDelay(self)
    @property
    def Protocols_BrpTcp_TcpPort(self) -> Protocols_BrpTcp_TcpPort:
        """
        This is the local TCP port used for the BRP protocol. The reader listens on
        this port for incoming connection requests.
        """
        return Protocols_BrpTcp_TcpPort(self)
    @property
    def Protocols_BrpTcp_TcpHost(self) -> Protocols_BrpTcp_TcpHost:
        """
        This is the preferred host that shall be contacted in case the reader operates
        in standalone mode and a card is presented.
        
        As soon as the reader detects a card it tries to establish a TCP connection to
        this host. In case the host is not available the reader tries to contact the
        alternate host [TcpAlternateHost](.#Protocols.BrpTcp.TcpAlternateHost). If
        this is successful the reader switches priority internally, which means it
        will prefer the alternate host the next time.
        """
        return Protocols_BrpTcp_TcpHost(self)
    @property
    def Protocols_BrpTcp_TcpHostPort(self) -> Protocols_BrpTcp_TcpHostPort:
        """
        This is the TCP port of the preferred host
        ([TcpHost](.#Protocols.BrpTcp.TcpHost)).
        """
        return Protocols_BrpTcp_TcpHostPort(self)
    @property
    def Protocols_BrpTcp_TcpAlternateHost(self) -> Protocols_BrpTcp_TcpAlternateHost:
        """
        This is the alternate host that shall be contacted in case of card
        presentation if the preferred host ([TcpHost](.#Protocols.BrpTcp.TcpHost)) is
        not available.
        
        In the case that the preferred host is not available but the alternate host
        can be contacted instead, the reader switches internally the preferred and the
        alternate host.
        """
        return Protocols_BrpTcp_TcpAlternateHost(self)
    @property
    def Protocols_BrpTcp_TcpAlternateHostPort(self) -> Protocols_BrpTcp_TcpAlternateHostPort:
        """
        This is the TCP port of the alternate host
        ([TcpAlternateHost](.#Protocols.BrpTcp.TcpAlternateHost)).
        """
        return Protocols_BrpTcp_TcpAlternateHostPort(self)
    @property
    def Protocols_BrpTcp_TcpAutoCloseTimeout(self) -> Protocols_BrpTcp_TcpAutoCloseTimeout:
        """
        This is the timeout for closing unused open connections.
        
        If this time elapses without having received a BRP command from the host, the
        reader will automatically close an opened TCP connection.
        
        If this value is set to 0, the auto-close feature is disabled, i.e. the reader
        keeps a connection always open. It is the matter of the host to close open
        connections.
        """
        return Protocols_BrpTcp_TcpAutoCloseTimeout(self)
    @property
    def Protocols_BrpTcp_TcpOutgoingPort(self) -> Protocols_BrpTcp_TcpOutgoingPort:
        """
        This is the TCP port number that is used for the BRP protocol in case a BRP
        communication session is initiated by the reader.
        
        For BRP communication that the host initiates refer to
        ([TcpPort](.#Protocols.BrpTcp.TcpPort)).
        
        If this value is not set, a port number is chosen incidentally on every
        connection trial.
        """
        return Protocols_BrpTcp_TcpOutgoingPort(self)
    @property
    def Protocols_BrpTcp_TcpConnectTrialMinDelay(self) -> Protocols_BrpTcp_TcpConnectTrialMinDelay:
        """
        This is the minimum time in seconds the reader will wait after an unsuccessful
        connection request before it starts the next trial.
        
        The actual delay is chosen randomly within the limits of this minimum value
        and ([TcpConnectTrialMaxDelay](.#Protocols.BrpTcp.TcpConnectTrialMaxDelay)).
        """
        return Protocols_BrpTcp_TcpConnectTrialMinDelay(self)
    @property
    def Protocols_BrpTcp_TcpConnectTrialMaxDelay(self) -> Protocols_BrpTcp_TcpConnectTrialMaxDelay:
        """
        This is the maximum time in seconds the reader will wait after an unsuccessful
        connection request before it starts the next trial.
        
        The actual delay is chosen randomly within the limits of
        ([TcpConnectTrialMinDelay](.#Protocols.BrpTcp.TcpConnectTrialMinDelay)) and
        this value.
        """
        return Protocols_BrpTcp_TcpConnectTrialMaxDelay(self)
    @property
    def Protocols_BrpTcp_TcpSoftResetDelay(self) -> Protocols_BrpTcp_TcpSoftResetDelay:
        """
        This is the time in milliseconds the reader will wait after a software reset
        before it tries to reconnect to the host. This delay, which is only applied in
        case the connection was initiated by the host and not by the reader, allows
        the host for reconnecting the reader after it has rebooted.
        """
        return Protocols_BrpTcp_TcpSoftResetDelay(self)
    @property
    def Protocols_BrpTcp_TcpMaskLinkChangeEventDelay(self) -> Protocols_BrpTcp_TcpMaskLinkChangeEventDelay:
        """
        This is the time in milliseconds the reader won't report link change events to
        the host after reboot.
        """
        return Protocols_BrpTcp_TcpMaskLinkChangeEventDelay(self)
    @property
    def Protocols_BrpTcp_SlpAttributes(self) -> Protocols_BrpTcp_SlpAttributes:
        """
        These are up to 16 application specific attributes the SLP protocol will
        advertise if requested by a host.
        """
        return Protocols_BrpTcp_SlpAttributes(self)
    @property
    def Protocols_BrpTcp_HostMsgFormatTemplate(self) -> Protocols_BrpTcp_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_BrpTcp_HostMsgFormatTemplate(self)
    @property
    def Protocols_BrpTcp_AutoRunCommand(self) -> Protocols_BrpTcp_AutoRunCommand:
        """
        A list of BRP command frames that shall be executed automatically at powerup
        (including sending their responses to the host) before starting with normal
        operation.
        
        **These commands are executed in order (_first_ StartupRunCmd[0],_then_
        StartupRunCmd[1], ...) until the first index without corresponding
        StartupRunCmd value.**
        """
        return Protocols_BrpTcp_AutoRunCommand(self)
    @property
    def Protocols_Wiegand(self) -> Protocols_Wiegand:
        """
        Specify settings for Wiegand interface (output). To use this interface
        [autoread functionality](autoread.xml#Autoread) has to be activated.
        """
        return Protocols_Wiegand(self)
    @property
    def Protocols_Wiegand_HostMsgFormatTemplate(self) -> Protocols_Wiegand_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_Wiegand_HostMsgFormatTemplate(self)
    @property
    def Protocols_Wiegand_MessageLength(self) -> Protocols_Wiegand_MessageLength:
        """
        The size of a single Wiegand message in bits.
        
        With [Wiegand/Mode = Standard](.#Protocols.Wiegand.Mode) only values that are
        a multiple of 8 plus 2 are allowed (e.g. 34). If [Wiegand/Mode =
        Raw](.#Protocols.Wiegand.Mode) any bit length may be selected.
        
        **The value 0xFF means, that the length of the message depends on the length
        of the data returned by the autoread functionality.**
        """
        return Protocols_Wiegand_MessageLength(self)
    @property
    def Protocols_Wiegand_BitOrder(self) -> Protocols_Wiegand_BitOrder:
        """
        Specifies the order of the bits within a Wiegand message.
        """
        return Protocols_Wiegand_BitOrder(self)
    @property
    def Protocols_Wiegand_PinMessageFormat(self) -> Protocols_Wiegand_PinMessageFormat:
        """
        Specifies the format of PINs entered by user via keyboard (see MessageType =
        Keyboard) that shall be send via Wiegand.
        """
        return Protocols_Wiegand_PinMessageFormat(self)
    @property
    def Protocols_Wiegand_PulseWidth(self) -> Protocols_Wiegand_PulseWidth:
        """
        Specifies the time of a Wiegand pulse in 1/100 ms.
        """
        return Protocols_Wiegand_PulseWidth(self)
    @property
    def Protocols_Wiegand_PulseInterval(self) -> Protocols_Wiegand_PulseInterval:
        """
        Specifies the time between two Wiegand pulses in ms.
        """
        return Protocols_Wiegand_PulseInterval(self)
    @property
    def Protocols_Wiegand_Mode(self) -> Protocols_Wiegand_Mode:
        """
        Specifies the mode how Wiegand data are sent to the host. Currently two modes
        are supported: Standard and raw mode.
        """
        return Protocols_Wiegand_Mode(self)
    @property
    def Protocols_RawSerial(self) -> Protocols_RawSerial:
        """
        This subkey specifies all protocol parameters needed for the RawSerial
        protocol, which transfers messages via RS-232/UART to the host without any
        extra protocol overhead.
        """
        return Protocols_RawSerial(self)
    @property
    def Protocols_RawSerial_Baudrate(self) -> Protocols_RawSerial_Baudrate:
        """
        Specifies the Baudrate.
        """
        return Protocols_RawSerial_Baudrate(self)
    @property
    def Protocols_RawSerial_Parity(self) -> Protocols_RawSerial_Parity:
        """
        Parity-mode that shall be used for transfer of data. If not specified "None"
        is assumed.
        """
        return Protocols_RawSerial_Parity(self)
    @property
    def Protocols_RawSerial_BitsPerByte(self) -> Protocols_RawSerial_BitsPerByte:
        """
        Specifies the number of payload bits per byte (without start/stop/parity
        bits). If this value is not specified 8 is assumed.
        """
        return Protocols_RawSerial_BitsPerByte(self)
    @property
    def Protocols_RawSerial_Channel(self) -> Protocols_RawSerial_Channel:
        """
        Specifies the Pins that shall be used to transfer the data to the host.
        
        **This value is only relevant for ID-engine SD readers, which provide two
        RS-232/UART interfaces. ID-engine X and ID-engine Z readers, which feature
        only one RS-232/UART, ignore this value.**
        """
        return Protocols_RawSerial_Channel(self)
    @property
    def Protocols_RawSerial_HostMsgFormatTemplate(self) -> Protocols_RawSerial_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_RawSerial_HostMsgFormatTemplate(self)
    @property
    def Protocols_LowLevelIoPorts(self) -> Protocols_LowLevelIoPorts:
        """
        When this protocol is activated, the physical pins of the second protocol
        channel (used also for [Wiegand](.#Protocols.Wiegand) and
        [RawSerial](.#Protocols.RawSerial) are use for I/O and thus can be set via
        commands for setting/getting IO-Ports.
        """
        return Protocols_LowLevelIoPorts(self)
    @property
    def Protocols_LowLevelIoPorts_PhysicalPinMap(self) -> Protocols_LowLevelIoPorts_PhysicalPinMap:
        """
        If this protocol is activated every physical pin of the 3 pins of the second
        channel is assigned to a virtual Port. This assignment can be changed by
        setting an entry of this list to a specific virtual Port. The list entries are
        assigned to this physical pins (in order):
        
          1. TX os RS-232/UART when configured for RawSerial 
          2. Direction pin when configuration for a RS485 based protocol like OSDP 
          3. RX os RS-232/UART when configured for RawSerial
        """
        return Protocols_LowLevelIoPorts_PhysicalPinMap(self)
    @property
    def Protocols_MagstripeEmulation(self) -> Protocols_MagstripeEmulation:
        """
        This subkey specifies the parameters for the magstripe emulation interface,
        which makes a SmartCard reader emulate a magstripe card reader.
        """
        return Protocols_MagstripeEmulation(self)
    @property
    def Protocols_MagstripeEmulation_Encoding(self) -> Protocols_MagstripeEmulation_Encoding:
        """
        Specifies the character encoding for magstripe emulation.
        """
        return Protocols_MagstripeEmulation_Encoding(self)
    @property
    def Protocols_Network(self) -> Protocols_Network:
        """
        This subkey specifies all protocol parameters needed for the network
        communication (Ethernet, WLAN).
        """
        return Protocols_Network(self)
    @property
    def Protocols_Network_IpAddress(self) -> Protocols_Network_IpAddress:
        """
        This is the IP-Address the reader device should apply for network
        communication.
        
        This value is a part of the static IP configuration of a reader device. A
        complete static IP configuration consists of
        [IpAddress](.#Protocols.Network.IpAddress)
        [IpSubnetMask](.#Protocols.Network.IpSubnetMask),
        [IpGateway](.#Protocols.Network.IpGateway) and
        [IpDnsServer](.#Protocols.Network.IpDnsServer).
        
        These values should be set by the network administrator if the dynamic IP
        configuration is disabled (refer to [DhcpMode](.#Protocols.Network.DhcpMode)).
        """
        return Protocols_Network_IpAddress(self)
    @property
    def Protocols_Network_IpSubnetMask(self) -> Protocols_Network_IpSubnetMask:
        """
        This is the subnet mask.
        
        The subnet mask specifies which IP addresses belong to the readers subnet. The
        reader uses this value to decide if a host is located in the same subnet
        (these packets are sent directly) or not (these packets are sent to
        [IpGateway](.#Protocols.Network.IpGateway)).
        
        This value is part of the static IP configuration. Refer to
        [IpAddress](.#Protocols.Network.IpAddress).
        """
        return Protocols_Network_IpSubnetMask(self)
    @property
    def Protocols_Network_IpGateway(self) -> Protocols_Network_IpGateway:
        """
        This is the IP address of the gateway.
        
        The reader will always try to send IP packets directly to the receiver if it
        is located in the same subnet. All other packets will be sent to the standard
        gateway, which takes care of routing this packets correctly.
        
        This value is part of the static IP configuration. Refer to
        [IpAddress](.#Protocols.Network.IpAddress).
        """
        return Protocols_Network_IpGateway(self)
    @property
    def Protocols_Network_IpDnsServer(self) -> Protocols_Network_IpDnsServer:
        """
        This is the IP address of the DNS server.
        
        The reader tries to contact the DNS server in case there are host names to be
        resolved.
        
        This value is part of the static IP configuration. Refer to
        [IpAddress](.#Protocols.Network.IpAddress).
        """
        return Protocols_Network_IpDnsServer(self)
    @property
    def Protocols_Network_DhcpMode(self) -> Protocols_Network_DhcpMode:
        """
        Activates/deactivates the DHCP client of the reader.
        
        If DHCP is enabled the reader tries to get a dynamic IP configuration from a
        DHCP server at startup.
        
        If the DHCP client is disabled a static IP configuration should be available
        (refer to [IpAddress](.#Protocols.Network.IpAddress)). Otherwise the device
        may only be accessed via a link-local address.
        
        If mode is set to "Auto" then the DHCP client is only enabled if a static IP
        configuration is not available.
        """
        return Protocols_Network_DhcpMode(self)
    @property
    def Protocols_Network_DhcpLastAssignedIp(self) -> Protocols_Network_DhcpLastAssignedIp:
        """
        The DHCP client stores here the IP address that has been assigned to it the
        last time. It will request this address again in case of restarts.
        
        **This value is normally only used internally.**
        """
        return Protocols_Network_DhcpLastAssignedIp(self)
    @property
    def Protocols_Network_DhcpVendorClassIdentifier(self) -> Protocols_Network_DhcpVendorClassIdentifier:
        """
        This value defines the Vendor class identifier the reader advertises in its
        DHCP discover and request messages (DHCP option 60).
        
        **Option 60 is omitted if this value is set to an empty string "".**
        """
        return Protocols_Network_DhcpVendorClassIdentifier(self)
    @property
    def Protocols_Network_LinkLocalLastAssignedIp(self) -> Protocols_Network_LinkLocalLastAssignedIp:
        """
        Here the Link-local IP address is stored that has been acquired the last time.
        The reader tries to re-acquire this address again in case of restarts.
        
        **This value is normally only used internally.**
        """
        return Protocols_Network_LinkLocalLastAssignedIp(self)
    @property
    def Protocols_Network_LinkLocalMode(self) -> Protocols_Network_LinkLocalMode:
        """
        Activates/deactivates Link-Local address acquirement.
        
        In case Link-Local is enabled the reader tries to get a link-local address
        ("169.254.x.x") at startup.
        
        If the auto mode is selected then the reader starts Link-Local acquirement
        delayed. If a DHCP address can be acquired during this delay Link-Local will
        not be started (refer to
        [LinkLocalAcquireDelay](.#Protocols.Network.LinkLocalAcquireDelay)).
        
        As default Link-local is disabled.
        """
        return Protocols_Network_LinkLocalMode(self)
    @property
    def Protocols_Network_LinkLocalAcquireDelay(self) -> Protocols_Network_LinkLocalAcquireDelay:
        """
        Specifies the delay of the Link-Local address acquirement at startup of the
        reader in case of Link-Local auto mode (refer to
        [LinkLocalMode](.#Protocols.Network.LinkLocalMode)).
        
        To avoid excessive network traffic at startup the Firmware supports the
        following mechanism: A Link-Local address is only acquired with an initial
        delay. In case the reader gets an IP address from a DHCP server within this
        time, it won't request a link-local address any more as this address is only
        required if no other addressing mechanism is available.
        
        **The delay should be chosen large enough to ensure that the reader is able to
        retrieve a DHCP address in case a DHCP server is available.**
        """
        return Protocols_Network_LinkLocalAcquireDelay(self)
    @property
    def Protocols_Network_DetectIpEnable(self) -> Protocols_Network_DetectIpEnable:
        """
        Activates/deactivates IP detection of a connected network device.
        
        If this value is set to "Yes" the reader investigates incoming frames to find
        out the IP address of a network device (e.g. printer) that is directly
        connected to the reader switch. The host can retrieve this IP address from the
        reader via BRP over TCP.
        """
        return Protocols_Network_DetectIpEnable(self)
    @property
    def Protocols_Network_ResolverEnable(self) -> Protocols_Network_ResolverEnable:
        """
        Activates/deactivates DNS resolver.
        
        If this value is set to "Yes" the reader tries to resolve host names to IP
        addresses. This will only work if the reader has the IP address of a valid DNS
        server (either through DHCP or static configuration - refer to
        [IpDnsServer](.#Protocols.Network.IpDnsServer)).
        """
        return Protocols_Network_ResolverEnable(self)
    @property
    def Protocols_Network_ResolverInterval(self) -> Protocols_Network_ResolverInterval:
        """
        Specifies the time interval the reader should restart resolving host names.
        This is done to keep updated in case of IP address changes in the network.
        """
        return Protocols_Network_ResolverInterval(self)
    @property
    def Protocols_Network_UdpIntrospecEnable(self) -> Protocols_Network_UdpIntrospecEnable:
        """
        Activates/deactivates UDP introspection.
        
        If this value is set to "Yes" the reader investigates all frames that arrive
        at the reader switch in order to find a certain UDP packet the host is sending
        to the directly connected network device (e.g. printer). Once this frame has
        been detected the reader extracts the IP address and port and opens a TCP
        connection to the host.
        """
        return Protocols_Network_UdpIntrospecEnable(self)
    @property
    def Protocols_Network_SlpEnable(self) -> Protocols_Network_SlpEnable:
        """
        Activates/deactivates Service Location Protocol (SLP).
        
        If this value is set to "Yes" the reader activates SLP. A User Agent can find
        the reader then by searching for the SLP service "service:x-proxreader".
        """
        return Protocols_Network_SlpEnable(self)
    @property
    def Protocols_Network_SlpScope(self) -> Protocols_Network_SlpScope:
        """
        This value configures the SLP scope. The device will only reply to service
        requests for this scope.
        
        The reader supports one scope consisting of 10 characters. If this value does
        not exist, the reader uses the default scope ("DEFAULT").
        
        **Only lower-case letters are allowed!**
        """
        return Protocols_Network_SlpScope(self)
    @property
    def Protocols_Network_SlpDirectoryAgent(self) -> Protocols_Network_SlpDirectoryAgent:
        """
        This value specifies the SLP Directory Agent (DA). The reader device will
        register its service to the DA if available.
        
        In case the IP address of the DA is not specified directly but only the host
        name, the reader tries to resolve the name using DNS resolver (refer to
        [ResolverEnable](.#Protocols.Network.ResolverEnable)).
        """
        return Protocols_Network_SlpDirectoryAgent(self)
    @property
    def Protocols_Network_SlpActiveDiscovery(self) -> Protocols_Network_SlpActiveDiscovery:
        """
        Activates/deactivates SLP active discovery of Directory Agents (DA).
        
        If this value is set to "Disabled" the reader will _not_ actively try to find
        DAs by sending out Multicast/Broadcast DA-Request messages.
        """
        return Protocols_Network_SlpActiveDiscovery(self)
    @property
    def Protocols_Network_SlpPassiveDiscovery(self) -> Protocols_Network_SlpPassiveDiscovery:
        """
        Activates/deactivates SLP passive discovery of Directory Agents (DA).
        
        If this value is set to "Disabled" the reader will _not_ react to received DA-
        Advert messages.
        """
        return Protocols_Network_SlpPassiveDiscovery(self)
    @property
    def Protocols_Network_SlpMulticastTtl(self) -> Protocols_Network_SlpMulticastTtl:
        """
        Specifies the time to live (TTL) value for outgoing multicast requests.
        
        The TTL field of a frame is decreased by every host that passes the frame by
        at least 1. If it reaches 0 the frame is not forwarded any more.
        """
        return Protocols_Network_SlpMulticastTtl(self)
    @property
    def Protocols_Network_SlpRegistratonLifetime(self) -> Protocols_Network_SlpRegistratonLifetime:
        """
        Specifies the lifetime of service registrations. The reader starts to re-
        register its service at the DA as soon as 75% of this time has elapsed.
        """
        return Protocols_Network_SlpRegistratonLifetime(self)
    @property
    def Protocols_Network_SlpUseBroadcast(self) -> Protocols_Network_SlpUseBroadcast:
        """
        If this value is set to "Yes" the reader will use Broadcasts instead of
        Multicasts.
        
        This feature is intended for smaller networks that doesn't support Multicast.
        """
        return Protocols_Network_SlpUseBroadcast(self)
    @property
    def Protocols_Network_RecoveryPointStatus(self) -> Protocols_Network_RecoveryPointStatus:
        """
        Status of actual recovery point.
        
        This value is managed by the reader firmware. Don't change its value manually!
        """
        return Protocols_Network_RecoveryPointStatus(self)
    @property
    def Protocols_Network_NicNetworkPortSpeedDuplexMode(self) -> Protocols_Network_NicNetworkPortSpeedDuplexMode:
        """
        Select Speed and Duplex mode for Network port.
        """
        return Protocols_Network_NicNetworkPortSpeedDuplexMode(self)
    @property
    def Protocols_Network_NicFlowControl(self) -> Protocols_Network_NicFlowControl:
        """
        Enable/Disable Flow Control. Enables/Disabled the pause packet for high/low
        water threshold control.
        """
        return Protocols_Network_NicFlowControl(self)
    @property
    def Protocols_Network_NicPrinterPortSpeedDuplexMode(self) -> Protocols_Network_NicPrinterPortSpeedDuplexMode:
        """
        Select Speed and Duplex mode for Printer/Device port.
        
        Note: To allow for Maintenance Mode being entered without difficulty printer
        port is forced to operate in Autonegotiation mode as soon as Network port link
        gets lost.
        """
        return Protocols_Network_NicPrinterPortSpeedDuplexMode(self)
    @property
    def Protocols_Network_WlanSsid(self) -> Protocols_Network_WlanSsid:
        """
        This value specifies the service set identifer (SSID) in a wireless network
        (WLAN). This value is commonly called network name.
        """
        return Protocols_Network_WlanSsid(self)
    @property
    def Protocols_Network_WlanEncryptionMode(self) -> Protocols_Network_WlanEncryptionMode:
        """
        This value specifies the encryption mode used in the WLAN.
        """
        return Protocols_Network_WlanEncryptionMode(self)
    @property
    def Protocols_Network_WlanKey(self) -> Protocols_Network_WlanKey:
        """
        This value specifies the key/passphrase used in an encrypted WLAN.
        """
        return Protocols_Network_WlanKey(self)
    @property
    def Protocols_Network_WlanUserName(self) -> Protocols_Network_WlanUserName:
        """
        This value specifies the public user name for wireless networks using
        LEAP/PEAP/EAP-TLS.
        """
        return Protocols_Network_WlanUserName(self)
    @property
    def Protocols_Network_WlanDomainName(self) -> Protocols_Network_WlanDomainName:
        """
        This value specifies the public domain name for wireless networks using
        LEAP/PEAP/EAP-TLS (optional).
        """
        return Protocols_Network_WlanDomainName(self)
    @property
    def Protocols_KeyboardEmulation(self) -> Protocols_KeyboardEmulation:
        """
        If the USB keyboard emulation protocol is enabled (see
        [Device/Run/EnabledProtocols](base.xml#Device.Run.EnabledProtocols)), you can
        fine-tune it with these values.
        """
        return Protocols_KeyboardEmulation(self)
    @property
    def Protocols_KeyboardEmulation_RegisterInterface(self) -> Protocols_KeyboardEmulation_RegisterInterface:
        """
        **This is a legacy value.**
        
        Specifies if the USB HID interface shall be registered during connecting the
        USB device even if the KeyboardEmulation protocol is not enabled.
        """
        return Protocols_KeyboardEmulation_RegisterInterface(self)
    @property
    def Protocols_KeyboardEmulation_ScancodesMap(self) -> Protocols_KeyboardEmulation_ScancodesMap:
        """
        Defines a map that describe how to map various ASCII characters to Scancodes
        (=codes that are transferred via USB). Since scancodes are keyboard layout
        specific (=country specific) they have to be adapted for different countries.
        """
        return Protocols_KeyboardEmulation_ScancodesMap(self)
    @property
    def Protocols_KeyboardEmulation_KeypressDelay(self) -> Protocols_KeyboardEmulation_KeypressDelay:
        """
        Specifies the minimum delay in ms between two emulated keypresses. For most
        (!) firmware variants this defaults to 4. But with this configuration value
        you can increase the value if the host is not fast enough.
        """
        return Protocols_KeyboardEmulation_KeypressDelay(self)
    @property
    def Protocols_KeyboardEmulation_UsbInterfaceSubClass(self) -> Protocols_KeyboardEmulation_UsbInterfaceSubClass:
        """
        Specifies the subclass of the USB interface for keyboard emulation.
        """
        return Protocols_KeyboardEmulation_UsbInterfaceSubClass(self)
    @property
    def Protocols_KeyboardEmulation_UsbInterfaceOrder(self) -> Protocols_KeyboardEmulation_UsbInterfaceOrder:
        """
        Specifies if the keyboard emulation USB interface is returned before or after
        the BRP/HID interface (see USB command GetConfiguration).
        """
        return Protocols_KeyboardEmulation_UsbInterfaceOrder(self)
    @property
    def Protocols_KeyboardEmulation_HostMsgFormatTemplate(self) -> Protocols_KeyboardEmulation_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_KeyboardEmulation_HostMsgFormatTemplate(self)
    @property
    def Protocols_Ccid(self) -> Protocols_Ccid:
        """
        If the CCID protocol is enabled (see
        [Device/Run/EnabledProtocols](base.xml#Device.Run.EnabledProtocols)), you can
        fine-tune it with these values.
        
        **As CCID starts Autoread autonomously,[
        Device/Boot/StartAutoreadAtPowerup](autoread.xml#Device.Boot.StartAutoreadAtPowerup)
        should always be set to _Disabled_ to avoid undesired behavior at power-up.**
        """
        return Protocols_Ccid(self)
    @property
    def Protocols_Ccid_InterfaceMode(self) -> Protocols_Ccid_InterfaceMode:
        """
        Defines the interfaces the reader device registers to the USB host.
        """
        return Protocols_Ccid_InterfaceMode(self)
    @property
    def Protocols_Ccid_CardTypeMask(self) -> Protocols_Ccid_CardTypeMask:
        """
        Restrict card type mask for CCID card selection. See also
        [Project/VhlSettings/ScanCardFamilies](vhl.xml#Project.VhlSettings.ScanCardFamilies).
        """
        return Protocols_Ccid_CardTypeMask(self)
    @property
    def Protocols_Ccid_ForceApduCardType(self) -> Protocols_Ccid_ForceApduCardType:
        """
        Forces the card type used for APDU exchange with the card to a certain value.
        If not specified the card type which has been determined by VHL select is
        used.
        """
        return Protocols_Ccid_ForceApduCardType(self)
    @property
    def Protocols_Ccid_LedControl(self) -> Protocols_Ccid_LedControl:
        """
        This value can be used to disable the legacy LED control via the CCID
        protocol. This allows LEDs to be controlled using [Autoread
        Events](autoread.xml#Scripts.Events).
        """
        return Protocols_Ccid_LedControl(self)
    @property
    def Protocols_Osdp(self) -> Protocols_Osdp:
        """
        If the OSDP protocol is enabled (see
        [Device/Run/EnabledProtocols](base.xml#Device.Run.EnabledProtocols)), you can
        fine-tune it with these values.
        """
        return Protocols_Osdp(self)
    @property
    def Protocols_Osdp_BaudRate(self) -> Protocols_Osdp_BaudRate:
        """
        Baudrate used by Osdp Protocol. (unit: value in 100 bits per second)
        """
        return Protocols_Osdp_BaudRate(self)
    @property
    def Protocols_Osdp_Address(self) -> Protocols_Osdp_Address:
        """
        Device id of this osdp device. Values: 0x00-0x7F
        """
        return Protocols_Osdp_Address(self)
    @property
    def Protocols_Osdp_CharTimeout(self) -> Protocols_Osdp_CharTimeout:
        """
        Character timeout in ms for the osdp device. Specifies the maximum time in ms
        which may elapse between two bytes within the same frame.
        """
        return Protocols_Osdp_CharTimeout(self)
    @property
    def Protocols_Osdp_SCBKeyDefault(self) -> Protocols_Osdp_SCBKeyDefault:
        """
        This is the default key for OSDP protocol encryption. (SCBK-D). Will be used
        in install mode.
        """
        return Protocols_Osdp_SCBKeyDefault(self)
    @property
    def Protocols_Osdp_SCBKey(self) -> Protocols_Osdp_SCBKey:
        """
        This is the secure key for OSDP protocol encryption. In the standard OSDP
        specification this key is diversified and installed over the OSDP protocol. If
        this key exists OSDP works in secure mode.
        """
        return Protocols_Osdp_SCBKey(self)
    @property
    def Protocols_Osdp_SecureInstallMode(self) -> Protocols_Osdp_SecureInstallMode:
        """
        Flag for special install mode.
        """
        return Protocols_Osdp_SecureInstallMode(self)
    @property
    def Protocols_Osdp_DataMode(self) -> Protocols_Osdp_DataMode:
        """
        Adjustes OSDP message type for card data replies: ASCII data, Bitstream raw
        data or Bitstream wiegand data
        """
        return Protocols_Osdp_DataMode(self)
    @property
    def Protocols_Osdp_HostMsgFormatTemplate(self) -> Protocols_Osdp_HostMsgFormatTemplate:
        """
        Specifies the way the ascii decimal number read from the card by autoread
        shall be converted to the lowlevel format needed by this protocol.
        """
        return Protocols_Osdp_HostMsgFormatTemplate(self)
    @property
    def Protocols_HttpsClient(self) -> Protocols_HttpsClient:
        """
        This protocol requires a BALTECH IF Converter that connects to a server via
        Ethernet as HTTPS client.
        """
        return Protocols_HttpsClient(self)
    @property
    def Protocols_HttpsClient_AuthUrl(self) -> Protocols_HttpsClient_AuthUrl:
        """
        Specifies the root path of the HTTP(S) service to contact for reader
        operations (i.e. transmission of Autoread messages).
        
        As an option, you can specify 2 servers. Then, a failover to the second server
        will occur if connecting to the first server fails. As soon as the first
        server can be connected again, IF Converter will switch back.
        """
        return Protocols_HttpsClient_AuthUrl(self)
    @property
    def Protocols_HttpsClient_ConfigUrl(self) -> Protocols_HttpsClient_ConfigUrl:
        """
        Specifies the HTTPS server to contact in order to check for updates of the
        BEC2 file that contains the reader configuration (and optionally firmware). If
        not specified,
        [<AuthUrl>/reader/<Snr>/config](.#Protocols.HttpsClient.AuthUrl) will be used
        instead.
        """
        return Protocols_HttpsClient_ConfigUrl(self)
    @property
    def Protocols_HttpsClient_UpdateUrl(self) -> Protocols_HttpsClient_UpdateUrl:
        """
        Specifies the HTTPS server to contact in order to check for updates of IF
        Converter image.
        """
        return Protocols_HttpsClient_UpdateUrl(self)
    @property
    def Protocols_HttpsClient_UpdateTime(self) -> Protocols_HttpsClient_UpdateTime:
        """
        Specifies the time of day at which IF Converter is to check for an update.
        """
        return Protocols_HttpsClient_UpdateTime(self)
    @property
    def Protocols_HttpsClient_UpdateTimeSpread(self) -> Protocols_HttpsClient_UpdateTimeSpread:
        """
        Specifies the maximum delay after
        [UpdateTime](.#Protocols.HttpsClient.UpdateTime) to wait before checking if an
        update is available. The actual delay is determined individually for each IF
        Converter, using a random value between 0 and _UpdateSpreadTime_. This ensures
        that not all devices connect to the server at the same time. This value should
        depend on the expected number of readers in your project and on the speed of
        your network connection.
        """
        return Protocols_HttpsClient_UpdateTimeSpread(self)
    @property
    def Protocols_HttpsClient_InitialEncryptedAuthToken(self) -> Protocols_HttpsClient_InitialEncryptedAuthToken:
        """
        Project-specific, encrypted authentication token for the server specified in
        [AuthUrl](.#Protocols.HttpsClient.AuthUrl).
        
        The token will be used on the first successful connection to replace the
        authentication token with a token individual to the reader.
        """
        return Protocols_HttpsClient_InitialEncryptedAuthToken(self)
    @property
    def Protocols_HttpsClient_RootCertServer(self) -> Protocols_HttpsClient_RootCertServer:
        """
        If one of the servers referred by the URL Configvalues (i.e.
        [Protocols.HttpsClient.AuthUrl(0)](.#Protocols.HttpsClient.AuthUrl)) uses
        HTTPS/TLS with a custom root certificate, provide the root certificates here.
        
        You need to split the DER-encoded root certificate into chunks of not more
        than 120 bytes in size. Then assign every _RootCertServer(x)_ array entry one
        of these chunks. At last ensure that the array entry following the last
        certificate chunk is unused to indicate the end of the certificate.
        
        You may concatenate multiple root certificates in the method as described
        above (ensuring that there is always exactly one unused array entry). The IF
        Converter will automaticially select the right root certificate when
        connecting to a HTTPS URL.
        """
        return Protocols_HttpsClient_RootCertServer(self)
    @property
    def Protocols_AccessConditionBitsStd(self) -> Protocols_AccessConditionBitsStd:
        """
        Under this subkey all protocol specific access condition bits are specified.
        """
        return Protocols_AccessConditionBitsStd(self)
    @property
    def Protocols_AccessConditionBitsStd_BrpOverSerial(self) -> Protocols_AccessConditionBitsStd_BrpOverSerial:
        """
        Specifies the access rights when running a BRP (over serial) command.
        """
        return Protocols_AccessConditionBitsStd_BrpOverSerial(self)
    @property
    def Protocols_AccessConditionBitsStd_BrpOverHid(self) -> Protocols_AccessConditionBitsStd_BrpOverHid:
        """
        Specifies the access rights when running a BRP over HID command.
        """
        return Protocols_AccessConditionBitsStd_BrpOverHid(self)
    @property
    def Protocols_AccessConditionBitsStd_BrpOverCdc(self) -> Protocols_AccessConditionBitsStd_BrpOverCdc:
        """
        Specifies the access rights when running a BRP over CDC command.
        """
        return Protocols_AccessConditionBitsStd_BrpOverCdc(self)
    @property
    def Protocols_AccessConditionBitsStd_BrpOverOsdp(self) -> Protocols_AccessConditionBitsStd_BrpOverOsdp:
        """
        Specifies the access rights when running BRP commands over OSDP. Configuration
        value is used, if: - OSDP is configured to run in secure mode and the secure
        connection has already been established. - OSDP is configured to run in
        unsecure mode.
        """
        return Protocols_AccessConditionBitsStd_BrpOverOsdp(self)
    @property
    def Protocols_AccessConditionBitsStd_AutoreadTask(self) -> Protocols_AccessConditionBitsStd_AutoreadTask:
        """
        Specifies the access rights when running the autoread task.
        """
        return Protocols_AccessConditionBitsStd_AutoreadTask(self)
    @property
    def Protocols_AccessConditionBitsStd_Ccid(self) -> Protocols_AccessConditionBitsStd_Ccid:
        """
        Specifies the access rights when running CCID protocol.
        """
        return Protocols_AccessConditionBitsStd_Ccid(self)
    @property
    def Protocols_AccessConditionBitsStd_Tcp(self) -> Protocols_AccessConditionBitsStd_Tcp:
        """
        Specifies the access rights when running Tcp protocol unencrypted
        """
        return Protocols_AccessConditionBitsStd_Tcp(self)
    @property
    def Protocols_AccessConditionBitsAlt(self) -> Protocols_AccessConditionBitsAlt:
        """
        Under this subkey special protocol specific access condition bits are
        specified.
        """
        return Protocols_AccessConditionBitsAlt(self)
    @property
    def Protocols_AccessConditionBitsAlt_BrpOverOsdpLimited(self) -> Protocols_AccessConditionBitsAlt_BrpOverOsdpLimited:
        """
        Specifies the access rights when running BRP commands over OSDP, at which OSDP
        is configured to run in secure mode and the secure connection has not yet been
        established.
        """
        return Protocols_AccessConditionBitsAlt_BrpOverOsdpLimited(self)
    @property
    def Protocols_AccessConditionBitsAlt_TcpMaintenanceMode(self) -> Protocols_AccessConditionBitsAlt_TcpMaintenanceMode:
        """
        Limits the access rights when running Tcp in maintenance mode (= _only_ the
        second ethernet link is connected).
        """
        return Protocols_AccessConditionBitsAlt_TcpMaintenanceMode(self)
    @property
    def VhlCfg(self) -> VhlCfg:
        """
        Contains a list of VHL (very high level) descriptions how to read/write/format
        a card (=files). Every subkey corresponds to a specific VHL file id.
        """
        return VhlCfg(self)
    @property
    def VhlCfg_File(self) -> VhlCfg_File:
        """
        This key contains a description how to access a card of a specific type with
        VHLRead / VHLWrite / VHLFormat.
        """
        return VhlCfg_File(self)
    @property
    def VhlCfg_File_AreaList125(self) -> VhlCfg_File_AreaList125:
        """
        List of 2 byte tuples. First byte specifies the page address, the second byte
        the number of pages that shall be accessed via this VHL file.
        """
        return VhlCfg_File_AreaList125(self)
    @property
    def VhlCfg_File_Secret125(self) -> VhlCfg_File_Secret125:
        """
        * \- 4-byte password for EM4205 cards 
          * \- 4-byte password (RWD) for Hitag2 cards 
          * \- 4-byte password (RWD) and 3-byte password (TAG) for Hitag2 cards
        """
        return VhlCfg_File_Secret125(self)
    @property
    def VhlCfg_File_DesfireAid(self) -> VhlCfg_File_DesfireAid:
        """
        Desfire Application Identifier: only one Desfire Application can be processed
        per VHL file.  
        
        **VHLReadWrite():** this is the AID of the Desfire Application that shall be
        processed.  
        
        **VHLFormat():** Desfire application will be created if not existent.
        Depending on the master key settings, key authentication may be required -
        therefore the value
        [VhlCfg/File/DesfirePiccMasterKeys](.#VhlCfg.File.DesfirePiccMasterKeys) may
        be defined.
        
        **This value has to be specified in MSB first order (as all Baltech
        configuration values). Care has to be taken if the AID is retrieved directly
        from a Desfire internal representation, which uses LSB first order (In this
        case the AID has to be rotated).**
        
        ` ConfigValue: 0x00 0x12 0x34 0x56 AID: 0x123456 Desfire internal
        representation: 0x56 0x34 0x12 `
        """
        return VhlCfg_File_DesfireAid(self)
    @property
    def VhlCfg_File_DesfireKeyList(self) -> VhlCfg_File_DesfireKeyList:
        """
        Contains the list of keys needed to access a Desfire card with this VHL file.
        These keys are referenced by
        [VhlCfg/File/DesfireFileDesc](.#VhlCfg.File.DesfireFileDesc)
        """
        return VhlCfg_File_DesfireKeyList(self)
    @property
    def VhlCfg_File_DesfireFileDesc(self) -> VhlCfg_File_DesfireFileDesc:
        """
        A VHL file can be composed of multiple files of a single desfire application.
        One list entry specifies the file settings of exactly one desfire file and
        contains one (or more) entries that describes how to access the desfire file
        and what part of the desfire file shall be accessed.
        
        **VHLReadWrite():** a Desfire application with two Desfire files of 50 bytes
        each could be mapped into single VHL file by specifing a DesfireFileDesc with
        two entries. The first entry maps desfire file 0 into the VHL file bytes 0-49
        and the desfire file 1 is mapped by the second entry into the VHL file bytes
        50-99. When reading VHL file bytes 48-52 the reader will implicitly read the
        last 2 bytes of desfire file 0 and the first two bytes of the desfire file 1
        and return the concatenated result.
        
        **VHLFormat():** after executing VHLFormat() command all files should have the
        same settings as specified in the list entries. I.e. if a file already exists
        on card and the file settings of the card differ from the settings in the list
        entry, the existing file settings will be changed (success depends on access
        rights of the file). If file size is different the file will be deleted and
        created again. If a file exists on card but not in the file descriptor list it
        will be preserved. (e.g. on card exists file 1,2,5 - file descriptor contains
        file 1,2,6 - after execution of VHLFormat() the card contains file 1,2,5,6,
        files 1,2 have been adapted to new configuration values.
        
        The last list entry may be specified incompletely. All missing data at the end
        of the entry will be assumed to have default values (This is only a
        convenience feature).
        """
        return VhlCfg_File_DesfireFileDesc(self)
    @property
    def VhlCfg_File_DesfirePiccMasterKeys(self) -> VhlCfg_File_DesfirePiccMasterKeys:
        """
        This entry is only needed for running VHLFormat() and specifies the key index
        for the PICC master key.
        """
        return VhlCfg_File_DesfirePiccMasterKeys(self)
    @property
    def VhlCfg_File_DesfireProtocol(self) -> VhlCfg_File_DesfireProtocol:
        """
        This value allows to select the communication protocol to a Desfire card.
        """
        return VhlCfg_File_DesfireProtocol(self)
    @property
    def VhlCfg_File_DesfireFormatMasterPiccKeySettings(self) -> VhlCfg_File_DesfireFormatMasterPiccKeySettings:
        """
        Only used by VHLFormat() this entry changes the card master key settings.
        """
        return VhlCfg_File_DesfireFormatMasterPiccKeySettings(self)
    @property
    def VhlCfg_File_DesfireFormatPiccDefaultKey(self) -> VhlCfg_File_DesfireFormatPiccDefaultKey:
        """
        This entry is only needed for running VHLFormat() and specifies the key index
        of the new default key for Desfire EV1 cards.
        
        Only VHL key memory can be referenced:
        [DesfireKeyList](.#VhlCfg.File.DesfireKeyList) (values >= 0xC0). The crypto
        mode of this entry will be ignored - so it is recommend to define the default
        key as 3K3DES key to accomplish 24 byte key length. If the length of the given
        key is smaller, the remaining bytes will be filled up with 0.
        """
        return VhlCfg_File_DesfireFormatPiccDefaultKey(self)
    @property
    def VhlCfg_File_DesfireFormatPiccConfig(self) -> VhlCfg_File_DesfireFormatPiccConfig:
        """
        This entry is only needed for running VHLFormat() and specifies configuration
        settings (enable/disable format card and random ID) only for Desfire EV1
        cards.
        """
        return VhlCfg_File_DesfireFormatPiccConfig(self)
    @property
    def VhlCfg_File_DesfireFormatPiccATS(self) -> VhlCfg_File_DesfireFormatPiccATS:
        """
        This entry is only needed for running VHLFormat() and specifies the ATS which
        the card returns executing the RATS command.
        """
        return VhlCfg_File_DesfireFormatPiccATS(self)
    @property
    def VhlCfg_File_DesfireFormatAppMasterkeyIdx(self) -> VhlCfg_File_DesfireFormatAppMasterkeyIdx:
        """
        This entry is only needed for running VHLFormat() and specifies a list of
        indices to application master keys. The first entry in the list specifies the
        new application master key the others existing application master keys.
        """
        return VhlCfg_File_DesfireFormatAppMasterkeyIdx(self)
    @property
    def VhlCfg_File_DesfireMapKeyidx(self) -> VhlCfg_File_DesfireMapKeyidx:
        """
        If this entry exists all desfire key indexes within the configuration are
        mapped to 16 bit values.
        
          * If the key index refers to a crypto memory key (0x80..0xBF) the MSB of the 16 bit value refers to a page of the project crypto memory (0x00..0x0F), the LSB corresponds to the 8 bit value. 
          * If the key index refers to a SAM key (0x00..0x7F) the MSB of the 16 bit value denotes an index to the SamAVxKeySettings list, the LSB corresponds to the 8 bit value. 
          * For all other types of key references the MSB should be set to 0x00, all other values are rfu.
        """
        return VhlCfg_File_DesfireMapKeyidx(self)
    @property
    def VhlCfg_File_DesfireFormatResetPicc(self) -> VhlCfg_File_DesfireFormatResetPicc:
        """
        This entry is only needed for running VHLFormat(). If set to Reset the card
        will be formatted and all applications are deleted.
        """
        return VhlCfg_File_DesfireFormatResetPicc(self)
    @property
    def VhlCfg_File_DesfireFormatAppKeySettings(self) -> VhlCfg_File_DesfireFormatAppKeySettings:
        """
        This entry is only needed for running VHLFormat() and contains the necessary
        key settings parameter (KS1/2/3) for defining an application. KS3 is only
        needed by EV2 cards and has to be omitted for compatibility reasons if not
        needed.
        
        Rules for coding key settings:
        
          * if KS1 is different from the existing one, the key settings will be changed. 
          * if KS2 is different from the existing one the existing application will be deleted and created again. 
          * if KS3 is different from the existing one the existing application will be deleted and created again.
        """
        return VhlCfg_File_DesfireFormatAppKeySettings(self)
    @property
    def VhlCfg_File_DesfireFormatAppIsoFileID(self) -> VhlCfg_File_DesfireFormatAppIsoFileID:
        """
        This entry is only needed for running VHLFormat() and contains the ISO 7816
        file identifier, a optional parameter for defining an application.
        
        **If the application already exists on card and the new file identifier is
        different from the existing one, the existing application will be deleted and
        then created with new file identifier.**
        """
        return VhlCfg_File_DesfireFormatAppIsoFileID(self)
    @property
    def VhlCfg_File_DesfireFormatAppIsoFileDFName(self) -> VhlCfg_File_DesfireFormatAppIsoFileDFName:
        """
        This entry is only needed for running VHLFormat() and contains the ISO 7816
        application identifier by name, a optional parameter for defining an
        application.
        
        **If the application already exists on card and the new DF-name is different
        from the existing one, the existing application will be deleted and then
        created with new DF-name.**
        """
        return VhlCfg_File_DesfireFormatAppIsoFileDFName(self)
    @property
    def VhlCfg_File_DesfireFormatAppChangeKeys(self) -> VhlCfg_File_DesfireFormatAppChangeKeys:
        """
        This entry is only needed for running VHL-Format() and is used to change any
        application key (except the application master key). It contains a list of 3
        bytes entries, whereas each list entry specifies exactly one application key.
        
        **Note: if the applications change key should be changed (and if it is not
        equal to the application master key) it has to be the first entry in the
        list.**
        """
        return VhlCfg_File_DesfireFormatAppChangeKeys(self)
    @property
    def VhlCfg_File_DesfireFormatAppChangeKeyIdx(self) -> VhlCfg_File_DesfireFormatAppChangeKeyIdx:
        """
        This entry is only needed for running VHL-Format(). It specifies the index to
        the application change key. It can be omitted if the change key is the
        application master key: then
        [DesfireFormatAppMasterkeyIdx](.#VhlCfg.File.DesfireFormatAppMasterkeyIdx)
        value will be used instead.
        """
        return VhlCfg_File_DesfireFormatAppChangeKeyIdx(self)
    @property
    def VhlCfg_File_DesfireRandomIdKey(self) -> VhlCfg_File_DesfireRandomIdKey:
        """
        The value is required to authenticate with MIFARE DESFire cards with random
        UID to be able to read the real UID. It is currently only used for
        diversification.
        """
        return VhlCfg_File_DesfireRandomIdKey(self)
    @property
    def VhlCfg_File_DesfireEv2FormatPiccKeys(self) -> VhlCfg_File_DesfireEv2FormatPiccKeys:
        """
        This entry specifies a list of keys at picc level, which will be changed
        during VHL Format.
        """
        return VhlCfg_File_DesfireEv2FormatPiccKeys(self)
    @property
    def VhlCfg_File_DesfireEv2FormatAppKeysetParams(self) -> VhlCfg_File_DesfireEv2FormatAppKeysetParams:
        """
        This entry specifies all parameters for an application with multiple keysets
        """
        return VhlCfg_File_DesfireEv2FormatAppKeysetParams(self)
    @property
    def VhlCfg_File_DesfireEv2FormatAppDAM(self) -> VhlCfg_File_DesfireEv2FormatAppDAM:
        """
        This entry specifies all parameters to create a delegated application.
        """
        return VhlCfg_File_DesfireEv2FormatAppDAM(self)
    @property
    def VhlCfg_File_DesfireEv2FormatAppKeysetKeylist(self) -> VhlCfg_File_DesfireEv2FormatAppKeysetKeylist:
        """
        This entry specifies all parameters to initialize multiple keysets of an
        application
        """
        return VhlCfg_File_DesfireEv2FormatAppKeysetKeylist(self)
    @property
    def VhlCfg_File_DesfireEv2FormatAppSwitchKeyset(self) -> VhlCfg_File_DesfireEv2FormatAppSwitchKeyset:
        """
        If this key entry exists the application keyset will be changed to the
        specified keyset number.
        """
        return VhlCfg_File_DesfireEv2FormatAppSwitchKeyset(self)
    @property
    def VhlCfg_File_DesfireProxcheck(self) -> VhlCfg_File_DesfireProxcheck:
        """
        If this key entry exists the reader performs a Proximity Check.
        """
        return VhlCfg_File_DesfireProxcheck(self)
    @property
    def VhlCfg_File_DesfireVcsParams(self) -> VhlCfg_File_DesfireVcsParams:
        """
        If this key entry exists the reader performs a virtual card selection.
        """
        return VhlCfg_File_DesfireVcsParams(self)
    @property
    def VhlCfg_File_DesfireEV2FormatFileMultAccessCond(self) -> VhlCfg_File_DesfireEV2FormatFileMultAccessCond:
        """
        This entry specifies multiple access conditions for files within an
        application. (only for EV2 cards)
        """
        return VhlCfg_File_DesfireEV2FormatFileMultAccessCond(self)
    @property
    def VhlCfg_File_ForceCardSM(self) -> VhlCfg_File_ForceCardSM:
        """
        Forces a minimum secure messaging (SM) level for the communication between a
        Secure Access Module (SAM) and the card, typically in high-security
        environments.
        
          * If this value is not set, the hightest SM level supported by both the SAM and the card is used.
          * If this value is set, the minimum SM level specified must always be maintained. If either the SAM or the card does not support this level, communication between them is not possible.
        """
        return VhlCfg_File_ForceCardSM(self)
    @property
    def VhlCfg_File_DesfireDiversificationData(self) -> VhlCfg_File_DesfireDiversificationData:
        """
        Entry contains a rule processed by the data converter. For card number
        generation, only SerialNumber is supported.
        """
        return VhlCfg_File_DesfireDiversificationData(self)
    @property
    def VhlCfg_File_FelicaSystemCode(self) -> VhlCfg_File_FelicaSystemCode:
        """
        This value specifies the system code (logical card)
        """
        return VhlCfg_File_FelicaSystemCode(self)
    @property
    def VhlCfg_File_FelicaServiceCodeList(self) -> VhlCfg_File_FelicaServiceCodeList:
        """
        List of service codes This value is a list of service codes to access.
        (integer 16bit values). For every entry also an entry in
        [FelicaAreaList](.#VhlCfg.File.FelicaAreaList) has to be defined.
        """
        return VhlCfg_File_FelicaServiceCodeList(self)
    @property
    def VhlCfg_File_FelicaAreaList(self) -> VhlCfg_File_FelicaAreaList:
        """
        List of 2 byte tuples. First byte specifies the block address, (0-255) the
        second byte the number of blocks (1..) that shall be accessed via this VHL
        file. For every tuple also an entry in
        [FelicaServiceCodeList](.#VhlCfg.File.FelicaServiceCodeList) has to be
        defined.
        """
        return VhlCfg_File_FelicaAreaList(self)
    @property
    def VhlCfg_File_FidoRpid(self) -> VhlCfg_File_FidoRpid:
        """
        This value specifies the relying party identifier (RPID). It's required for
        referencing a FIDO2 credential that is stored on the authenticator (here:
        Yubikey). It's used to read the certificate contained in the large blop of the
        tox credential.
        """
        return VhlCfg_File_FidoRpid(self)
    @property
    def VhlCfg_File_FidoPublicKey(self) -> VhlCfg_File_FidoPublicKey:
        """
        This value specifies the public CA key (ECC P-256) of the certificate
        authority (CA) that issued the certificate stored in the authenticator's large
        blob.
        """
        return VhlCfg_File_FidoPublicKey(self)
    @property
    def VhlCfg_File_IntIndFileDescList(self) -> VhlCfg_File_IntIndFileDescList:
        """
        This value specifies a list of file ID's of n interindustry card. File ID's
        can be a Name or a 2 byte file identifier (FID)
        """
        return VhlCfg_File_IntIndFileDescList(self)
    @property
    def VhlCfg_File_IntIndSegment(self) -> VhlCfg_File_IntIndSegment:
        """
        Offset and Value to read/write from. Both values are Integer
        """
        return VhlCfg_File_IntIndSegment(self)
    @property
    def VhlCfg_File_IntIndKeyIdx(self) -> VhlCfg_File_IntIndKeyIdx:
        return VhlCfg_File_IntIndKeyIdx(self)
    @property
    def VhlCfg_File_IntIndRecordNumber(self) -> VhlCfg_File_IntIndRecordNumber:
        return VhlCfg_File_IntIndRecordNumber(self)
    @property
    def VhlCfg_File_IntIndOnReadSelectOnly(self) -> VhlCfg_File_IntIndOnReadSelectOnly:
        """
        With this value the Interindustry VHL can be enforced to execute a SELECT
        application only.
        """
        return VhlCfg_File_IntIndOnReadSelectOnly(self)
    @property
    def VhlCfg_File_IntIndTimeout(self) -> VhlCfg_File_IntIndTimeout:
        """
        This value specifies the maximum time the reader should wait for an APDU
        command response from the card in the context of an Interindustry VHL read or
        write access.
        """
        return VhlCfg_File_IntIndTimeout(self)
    @property
    def VhlCfg_File_Iso15Afi(self) -> VhlCfg_File_Iso15Afi:
        """
        This optional value may be set to address only transponders with a certain
        application family identifier (AFI).
        """
        return VhlCfg_File_Iso15Afi(self)
    @property
    def VhlCfg_File_Iso15DsfId(self) -> VhlCfg_File_Iso15DsfId:
        """
        This optional value may be set to address only transponders with a certain
        data storage format identifier (DSFID).
        """
        return VhlCfg_File_Iso15DsfId(self)
    @property
    def VhlCfg_File_Iso15BlockList(self) -> VhlCfg_File_Iso15BlockList:
        """
        The configuration value is a list of 1 or more block descriptions that specify
        which ISO 15693 memory blocks have to be accessed by VHL. Every entry consists
        of 2 bytes: The first byte addresses the start block number (first block = 0),
        the second byte defines the number of blocks.
        
        Either this value or the value
        [Iso15ExtendedBlockList](.#VhlCfg.File.Iso15ExtendedBlockList) is mandatory
        for an ISO 15693 VHL definition.
        """
        return VhlCfg_File_Iso15BlockList(self)
    @property
    def VhlCfg_File_Iso15BlockSize(self) -> VhlCfg_File_Iso15BlockSize:
        """
        Forces block size to a certain value.
        """
        return VhlCfg_File_Iso15BlockSize(self)
    @property
    def VhlCfg_File_Iso15WriteOptFlag(self) -> VhlCfg_File_Iso15WriteOptFlag:
        """
        Selects option flag value for write operations.
        """
        return VhlCfg_File_Iso15WriteOptFlag(self)
    @property
    def VhlCfg_File_Iso15ReadCmd(self) -> VhlCfg_File_Iso15ReadCmd:
        """
        Selects the ISO 15693 command that is used for a VHL read operation. With the
        default settings _ReadAuto_ , the reader will do the following:
        
          * If there are more than 4 blocks to read, the reader will first try the _ReadMultipleBlocks_ command. If this command isn't supported, _ReadSingleBlock_ will be used as a fallback. 
          * If there are fewer than 4 blocks to read, the reader will first try the _ReadSingleBlock_ command. If this command isn't supported, _ReadMultipleBlocks_ will be used as a fallback.
        """
        return VhlCfg_File_Iso15ReadCmd(self)
    @property
    def VhlCfg_File_Iso15WriteCmd(self) -> VhlCfg_File_Iso15WriteCmd:
        """
        Selects the ISO 15693 command that is used for a VHL write operation. With the
        default setting _WriteAuto_ , the reader will do the following:
        
          * If there are more than 4 blocks to write, the reader will first try the _WriteMultipleBlocks_ command. If this command isn't supported, _WriteSingleBlock_ will be used as a fallback. 
          * If there are fewer than 4 blocks to write, the reader will first try the _WriteSingleBlock_ command. If this command isn't supported, _WriteMultipleBlocks_ will be used as a fallback.
        """
        return VhlCfg_File_Iso15WriteCmd(self)
    @property
    def VhlCfg_File_Iso15ExtendedBlockList(self) -> VhlCfg_File_Iso15ExtendedBlockList:
        """
        The configuration value is a list of 1 or more block descriptions that specify
        which ISO 15693 memory blocks have to be accessed by VHL. Each entry consists
        of 2 16-bit parameters: The first parameter addresses the start block number
        (first block = 0), the second parameter defines the number of blocks.
        
        The configuration value is supported by firmware version 1100 v2.07 or above.
        
        Either this value or the value [Iso15BlockList](.#VhlCfg.File.Iso15BlockList)
        is mandatory for an ISO 15693 VHL definition.
        """
        return VhlCfg_File_Iso15ExtendedBlockList(self)
    @property
    def VhlCfg_File_LegicSegmentListLegacy(self) -> VhlCfg_File_LegicSegmentListLegacy:
        """
        **Please use[
        LegicApplicationSegmentList](.#VhlCfg.File.LegicApplicationSegmentList)
        instead of this value for new applications.**
        
        _General information about Legic VHL definition:_  
        A Legic VHL description consists of one or more so-called fragments. Each
        fragment represents a certain data area on a Legic card. It can be a whole
        segment or only a part of it.  
        A fragment is described by a segment information (this value), by its length
        [LegicLengthList](.#VhlCfg.File.LegicLengthList) and by the starting address
        within the desired segment [LegicAddressList](.#VhlCfg.File.LegicAddressList).
        Optionally a CRC checksum may be verified for every fragment
        ([LegicCRCAddressList](.#VhlCfg.File.LegicCRCAddressList)) and a certain
        segment type may be specified
        ([LegicSegmentType](.#VhlCfg.File.LegicSegmentTypeList)).
        
        The configuration value LegicSegmentListLegacy is a list of one or more
        segment descriptions. Every entry corresponds to a certain fragment and
        specifies which Legic segment has to be accessed by VHL.
        
        This value is mandatory for a Legic VHL fragment definition.
        
        Every entry in the list consists of at least two bytes: The first byte
        specifies the method the segment is identified (SegmentIdentification).
        Depending on this value one or more bytes follow with required identification
        attributes.  
          
        Basically there are two ways to identify a segment:
        
          * ID: SegmentIdentification has to be set to 0 (Bit0...7). Bit8 encodes the Address mode. SegmentInformation is the segment ID and has to be a value between 1 and 127 (0x01...0x7F) 
          * Stamp: SegmentIdentification has to be set to the Stamp length (Bit0...7). The maximum allowed value is 12 (0x0C). Bit8 encodes the Address mode. SegmentInformation is the desired Stamp. 
        
        ` "ProtocolHeaderAddressMode 1": address segment 1 in Protocol Header mode
        "AdvantAddressMode 3": address segment 3 in Advant Address Mode
        "ProtocolHeaderAddressMode|3 0x12 0x23 0x45": address segment with stamp "12
        34 56" in Protocol Header mode "AdvantAddressMode|3 0x12 0x23 0x45": address
        segment with stamp "12 34 56" in Advant Address mode `
        """
        return VhlCfg_File_LegicSegmentListLegacy(self)
    @property
    def VhlCfg_File_LegicLengthList(self) -> VhlCfg_File_LegicLengthList:
        """
        This is a list of 16-bit length values. Every entry specifies the length (MSB)
        of the corresponding fragment.
        
        This value is mandatory for a Legic VHL fragment definition.
        
        Refer to [LegicSegmentListLegacy](.#VhlCfg.File.LegicSegmentListLegacy) for an
        overview about the Legic fragment definition.
        """
        return VhlCfg_File_LegicLengthList(self)
    @property
    def VhlCfg_File_LegicAddressList(self) -> VhlCfg_File_LegicAddressList:
        """
        This is a list of 16-bit address values. Every entry specifies the starting
        address (MSB) of the corresponding fragment within the specified segment.
        
        This value is mandatory for a Legic VHL fragment definition.
        
        Refer to [LegicSegmentListLegacy](.#VhlCfg.File.LegicSegmentListLegacy) for an
        overview about the Legic fragment definition.
        """
        return VhlCfg_File_LegicAddressList(self)
    @property
    def VhlCfg_File_LegicCRCAddressList(self) -> VhlCfg_File_LegicCRCAddressList:
        """
        This is a list of 16-bit CRC address values. Every entry specifies the address
        (MSB) the CRC is stored within the specified segment.
        
        This value is optional. Because there must only be an entry for a fragment
        that has enabled the CRC check (refer to
        [LegicAddressList](.#VhlCfg.File.LegicAddressList)), this list may be shorter
        than the other lists.
        
        Refer to [LegicSegmentListLegacy](.#VhlCfg.File.LegicSegmentListLegacy) for an
        overview about the Legic fragment definition.
        """
        return VhlCfg_File_LegicCRCAddressList(self)
    @property
    def VhlCfg_File_LegicSegmentTypeList(self) -> VhlCfg_File_LegicSegmentTypeList:
        """
        This is a list of 8-bit segment types. Every entry specifies the segment type
        according to the Legic definition that is used to access the corresponding
        fragment.
        
        This value is optional. If no list is given VHL will assume a Data segment for
        every fragment. Usually a segment type must only be specified in case of
        Access or Biometric segments.
        
        **The segment type "Any" may only be used if segment is selected by ID! It
        doesn't work with Stamp search.**
        
        Refer to [LegicSegmentListLegacy](.#VhlCfg.File.LegicSegmentListLegacy) for an
        overview about the Legic fragment definition.
        """
        return VhlCfg_File_LegicSegmentTypeList(self)
    @property
    def VhlCfg_File_LegicApplicationSegmentList(self) -> VhlCfg_File_LegicApplicationSegmentList:
        """
        _General information about Legic VHL definition:_  
        A Legic VHL description consists of one or more so-called fragments. Each
        fragment represents a certain data area on a Legic card. It can be a whole
        segment or only a part of it.  
        A fragment is described by a segment information (this value), by its length
        [LegicLengthList](.#VhlCfg.File.LegicLengthList) and by the starting address
        within the desired segment [LegicAddressList](.#VhlCfg.File.LegicAddressList).
        Optionally a CRC checksum may be verified for every fragment
        ([LegicCRCAddressList](.#VhlCfg.File.LegicCRCAddressList)) and a certain
        segment type may be specified
        ([LegicSegmentTypeList](.#VhlCfg.File.LegicSegmentTypeList)).
        
        The configuration value LegicApplicationSegmentList is a list of one or more
        segment descriptions. Every entry corresponds to a certain fragment and
        specifies which Legic segment has to be accessed by VHL.
        
        This value is mandatory for a Legic VHL fragment definition.
        
        Every entry in the list consists of two components: The first byte specifies
        how the segment shall be accessed by the reader (SegmentIdentification). The
        following bytes specify the required segment identification attributes.
        Depending on the selected value of SegmentIdentification they will be
        interpreted as segment ID or stamp respectively.
        
        ` "ProtocolHeaderAddressMode 1 1": address segment 1 in Protocol Header mode
        "AdvantAddressMode 1 3": address segment 3 in Advant Address Mode "StampSearch
        3 0x12 0x23 0x45": address segment with stamp "12 34 56" in Protocol Header
        mode "AdvantAddressMode|StampSearch 3 0x12 0x23 0x45": address segment with
        stamp "12 34 56" in Advant Address mode `
        """
        return VhlCfg_File_LegicApplicationSegmentList(self)
    @property
    def VhlCfg_File_MifareMode(self) -> VhlCfg_File_MifareMode:
        """
        Specifies if addressing of a Mifare Classic/Plus card shall be done via
        absolute addresses or relative to MAD (Mifare Application Directory) sectors.
        """
        return VhlCfg_File_MifareMode(self)
    @property
    def VhlCfg_File_MifarePlusMadKeyBIndex(self) -> VhlCfg_File_MifarePlusMadKeyBIndex:
        """
        This entry is only needed for running VHL-Format(). If MAD encoding is enabled
        (MAD_AID does exist), this value contains a 2 byte index to the write key (Key
        B) of the MAD. This key is needed by VHL-Format() to create the MAD or to
        adapt the MAD when adding a new application. If MAD encoding is not enabled,
        this value may be omitted. This value is used by Mifare plus firmware only.
        For Mifare classic firmware use
        [MifareClassicMadKeyB](.#VhlCfg.File.MifareClassicMadKeyB) instead.
        """
        return VhlCfg_File_MifarePlusMadKeyBIndex(self)
    @property
    def VhlCfg_File_MifareKeyList(self) -> VhlCfg_File_MifareKeyList:
        """
        Contains a list of 7 bytes: one byte access limitations and 6 bytes Mifare
        key.
        """
        return VhlCfg_File_MifareKeyList(self)
    @property
    def VhlCfg_File_MifareTransferToSecureMemory(self) -> VhlCfg_File_MifareTransferToSecureMemory:
        """
        This command transfers all Mifare classic keys from
        [MifareKeyList](.#VhlCfg.File.MifareKeyList) (or
        [MifareClassicKeyList](.#VhlCfg.File.MifareClassicKeyList)) to secure memory,
        which is better protected against attacks.
        
        Key transfer is done at power up of the reader and after key transfer is
        finished all keys are deleted from the configuration. This value is replaced
        by the firmware of the reader and designates the VHL key offset of this file
        within the secure memory.  
        Usually, the first key is transferred to the reader chip's memory address 0,
        the second one to the reader chip's memory address 1 and so on. A different
        address range can be specified, however, by definition of the START_RC500_EEP
        Value, please refer to
        [Device/Run/FirstVhlRc500Key](base.xml#Device.Run.FirstVhlRc500Key).
        
        **If TRANSFER is set and according rights definition in[
        MifareKeyList](.#VhlCfg.File.MifareKeyList) is restricted, the corresponding
        key will not be transferred.**
        """
        return VhlCfg_File_MifareTransferToSecureMemory(self)
    @property
    def VhlCfg_File_MifareMadAid(self) -> VhlCfg_File_MifareMadAid:
        """
        This value is only needed if the card has a Mifare Application Directory (MAD)
        and [MifareMode](.#VhlCfg.File.MifareMode) is set to "MAD". It specifies the
        Application-ID within a MAD sector.
        """
        return VhlCfg_File_MifareMadAid(self)
    @property
    def VhlCfg_File_MifarePlusAesKeyList(self) -> VhlCfg_File_MifarePlusAesKeyList:
        """
        Contains a list of 7 bytes: one byte access limitations and 16 bytes AES key.
        This value is used by Mifare plus firmware only.
        """
        return VhlCfg_File_MifarePlusAesKeyList(self)
    @property
    def VhlCfg_File_MifareSectorList(self) -> VhlCfg_File_MifareSectorList:
        """
        This value contains a list of sectors which shall be accessed. It replaces the
        [MifareClassicBlockList](.#VhlCfg.File.MifareClassicBlockList) value, which
        specifies sectors instead of blocks. This value can also be used for VHL-
        Format(): it contains a list of sectors numbers which shall be formatted - if
        an AID is specified this list contains sectors which belongs to the AID: then
        the sectors are addressed relatively to the MAD. Refer also to
        [MifareMode](.#VhlCfg.File.MifareMode).
        """
        return VhlCfg_File_MifareSectorList(self)
    @property
    def VhlCfg_File_MifareFormatAsMad2(self) -> VhlCfg_File_MifareFormatAsMad2:
        """
        This entry is only needed for running VHL-Format(). If the value
        [MifareMadAid](.#VhlCfg.File.MifareMadAid) is defined and this value is set to
        Yes, the MAD encoded to the card is MAD2 conform.
        """
        return VhlCfg_File_MifareFormatAsMad2(self)
    @property
    def VhlCfg_File_MifarePlusKeyAssignment(self) -> VhlCfg_File_MifarePlusKeyAssignment:
        """
        This value primary used for VHL format consists of a 10 byte list which
        contains the information for the complete sector trailer and according keys A
        and B (AES and/or Mifare, dependant of the card security level). For each
        sector in [MifareSectorList](.#VhlCfg.File.MifareSectorList) this information
        is programmed.
        
          * Security level 3: for each sector 2 AES keys (A and B) and a sector trailer containing 5 bytes access conditions (AC bytes / all other bytes are set to 0) are programmed. 
          * Security level 0 and 2: for each sector 2 AES keys (A and B) and the complete sector trailer with Mifare keys (A and B) and 4 byte access condition are programmed. 
          * Security level 1: the complete sector trailer with Mifare keys (A and B) and 4 byte access condition is programmed. 
        
        **Currently for key A/B only VHL keys can be used.**
        
        For VHL-read/write() this value specifies the key to authenticate with - for
        this purpose ACS bytes will be discarded.
        
        This value is used by Mifare plus firmware only. For Mifare classic firmware
        use
        [MifareClassicFormatSectorTrailer](.#VhlCfg.File.MifareClassicFormatSectorTrailer).
        """
        return VhlCfg_File_MifarePlusKeyAssignment(self)
    @property
    def VhlCfg_File_MifarePlusCommunicationMode(self) -> VhlCfg_File_MifarePlusCommunicationMode:
        """
        This value is used by Mifare plus firmware only. It specifies the
        communication mode in security level 3 of a Mifare plus card.
        """
        return VhlCfg_File_MifarePlusCommunicationMode(self)
    @property
    def VhlCfg_File_MifarePlusProxyimityCheck(self) -> VhlCfg_File_MifarePlusProxyimityCheck:
        """
        This value is used by Mifare plus firmware only and specifies an index to the
        proximity check key. If configuration value is missing no proximity check by
        the reader will be done. Cards with proximity check enabled do not work
        without this check.
        """
        return VhlCfg_File_MifarePlusProxyimityCheck(self)
    @property
    def VhlCfg_File_MifareVcsParams(self) -> VhlCfg_File_MifareVcsParams:
        """
        This value enables Virtual Card Selection. An ISO Select command is performed
        to select a particular MIFARE (Plus) installation. If valid keys are
        specified, an additional ISO External Authenticate will be executed.
        """
        return VhlCfg_File_MifareVcsParams(self)
    @property
    def VhlCfg_File_MifarePlusFormatOriginalKeyIdx(self) -> VhlCfg_File_MifarePlusFormatOriginalKeyIdx:
        """
        This value is used by MIFARE Plus firmware only and needed for running
        VHL.Format(). To encode the new sector trailer, the reader tries to
        authenticate with all the keys specified in the list. If this value is
        omitted, it defaults to authenticate with 'FF' * 6 as Key A (MIFARE transport
        keys) or with '00' * 16 (AES transport keys). Using MIFARE Plus with cards in
        SL3, VHL.Format() first updates the AES keylist, then the the sector trailer.
        To allow for retries of the VHL.Format() command, also the new keys used for
        key change should be included in this configuration value.
        """
        return VhlCfg_File_MifarePlusFormatOriginalKeyIdx(self)
    @property
    def VhlCfg_File_MifarePlusKeyIdxOffset(self) -> VhlCfg_File_MifarePlusKeyIdxOffset:
        """
        This value is used by Mifare plus firmware only. It describes for SAM and
        crypto memory keys an offset for Mifare keys to AES keys (!-signed value).
        This value is only useful at security level 0 and 2 - in this cases for access
        / authentication both keys are needed. Default value is 1.
        """
        return VhlCfg_File_MifarePlusKeyIdxOffset(self)
    @property
    def VhlCfg_File_MifarePlusFormatLevelSwitchKeyIdx(self) -> VhlCfg_File_MifarePlusFormatLevelSwitchKeyIdx:
        """
        This value is used by Mifare plus firmware only. It is used by VHL-Format()
        and switches to the respective security level.
        """
        return VhlCfg_File_MifarePlusFormatLevelSwitchKeyIdx(self)
    @property
    def VhlCfg_File_MifarePlusFormatCardConfigurationKeyList(self) -> VhlCfg_File_MifarePlusFormatCardConfigurationKeyList:
        """
        This value is used by Mifare plus firmware only. It is used by VHL-Format()
        and changes the card configuration key itself and all keys with can be changed
        with the card configuration key. It contains 2 byte key index entries to:
        
          * old card configuration key, only needed if card configuration key should be changed 
          * new or current card configuration key 
          * select virtual card key 
          * virtual card encryption key 
          * virtual card mac key 
          * proximity check key 
        
        A key index not used has to be set to 0xFF 0xFF.
        """
        return VhlCfg_File_MifarePlusFormatCardConfigurationKeyList(self)
    @property
    def VhlCfg_File_MifarePlusFormatCardMasterKeyList(self) -> VhlCfg_File_MifarePlusFormatCardMasterKeyList:
        """
        This value is used by Mifare plus firmware only. It is used by VHL-Format()
        and changes the card master key itself and all keys with can be changed with
        the card master key. It contains 2 byte key index entries to:
        
          * old card master key, only needed if card configuration key should be changed 
          * new or current card master key 
          * level 2 switch key 
          * level 3 switch key 
          * SL1 card authentication key 
        
        A key index not used has to be set to 0xFF 0xFF.
        """
        return VhlCfg_File_MifarePlusFormatCardMasterKeyList(self)
    @property
    def VhlCfg_File_MifareClassicFormatSectorTrailer(self) -> VhlCfg_File_MifareClassicFormatSectorTrailer:
        """
        **This value is is used by Mifare classic firmware only. For Mifare plus
        firmware use[
        MifareClassicKeyAssignment](.#VhlCfg.File.MifarePlusKeyAssignment) instead. It
        is only needed by VHL-Format(). Every sector trailer will be overwritten with
        this array.**
        """
        return VhlCfg_File_MifareClassicFormatSectorTrailer(self)
    @property
    def VhlCfg_File_MifareClassicKeyList(self) -> VhlCfg_File_MifareClassicKeyList:
        """
        Contains a list of 6 byte keys. These keys are referenced by
        [MifareClassicWriteKeyAssignment](.#VhlCfg.File.MifareClassicWriteKeyAssignment)
        and
        [MifareClassicReadKeyAssignment](.#VhlCfg.File.MifareClassicReadKeyAssignment)
        
        **This value is used by Mifare classic firmware only. For Mifare plus firmware
        use[ MifareKeyList](.#VhlCfg.File.MifareKeyList) instead.**
        """
        return VhlCfg_File_MifareClassicKeyList(self)
    @property
    def VhlCfg_File_MifareClassicBlockList(self) -> VhlCfg_File_MifareClassicBlockList:
        """
        This value cannot be used with VHL-Format(). It contains a list of blocks that
        shall be accessible via this VHL file. Every entry is a zero-based 8bit
        address. This means: if [MifareMode](.#VhlCfg.File.MifareMode) is set to
        Absolute
        
          * Block 0 is the information block 
          * Block 3 is the sector trailer of block 0 
          * Block 4 is block 0 of sector 1 
          * ... 
        
        **This value is used by Mifare classic firmware only. For Mifare plus firmware
        use[ MifareSectorList](.#VhlCfg.File.MifareSectorList) instead.**
        
        **If Mad is enabled (see[ MifareMode](.#VhlCfg.File.MifareMode) ) the blocks
        are relative to the first sector of the application.**
        """
        return VhlCfg_File_MifareClassicBlockList(self)
    @property
    def VhlCfg_File_MifareClassicReadKeyAssignment(self) -> VhlCfg_File_MifareClassicReadKeyAssignment:
        """
        For every entry in [MifareSectorList](.#VhlCfg.File.MifareSectorList) (or
        [MifareClassicBlockList](.#VhlCfg.File.MifareClassicBlockList) for legacy
        configurations) an entry in this list has to be specified, that refers to a
        key in [MifareKeyList](.#VhlCfg.File.MifareKeyList) (or
        [MifareClassicKeyList](.#VhlCfg.File.MifareClassicKeyList)). Furthermore every
        entry has to be bitmask-combined with either KeyA or KeyB to inform the reader
        if the key at the corresponding key index shall be applied as key A/B.
        
        If this value contains less entries than MifareSectorList the missing entries
        will be filled up by duplicating the last entry in this list. If this value is
        not defined all sectors will be read by using key 0 as KeyA.
        
        **This value is used by Mifare classic firmware only. For Mifare plus
        firmware[ MifarePlusKeyAssignment](.#VhlCfg.File.MifarePlusKeyAssignment)
        instead.**
        """
        return VhlCfg_File_MifareClassicReadKeyAssignment(self)
    @property
    def VhlCfg_File_MifareClassicWriteKeyAssignment(self) -> VhlCfg_File_MifareClassicWriteKeyAssignment:
        """
        For every entry in [MifareSectorList](.#VhlCfg.File.MifareSectorList) (or
        [MifareClassicBlockList](.#VhlCfg.File.MifareClassicBlockList) for legacy
        configurations) an entry in this list has to be specified, that refers to a
        key in [MifareKeyList](.#VhlCfg.File.MifareKeyList) (or
        [MifareClassicKeyList](.#VhlCfg.File.MifareClassicKeyList)). Furthermore every
        entry has to be bitmask-combined with either KeyA or KeyB to inform the reader
        if the key at the corresponding key index shall be applied as key A or key B.
        
        If this value contains less entries than MifareSectorList the missing entries
        will be filled up by duplicating the last entry in this list. If this value is
        not defined all sectors will be written by using key 1 as KeyB.
        
        **This value is used by Mifare classic firmware only. For Mifare plus firmware
        use[ MifarePlusKeyAssignment](.#VhlCfg.File.MifarePlusKeyAssignment)
        instead.**
        """
        return VhlCfg_File_MifareClassicWriteKeyAssignment(self)
    @property
    def VhlCfg_File_MifareClassicFormatOriginalKeyList(self) -> VhlCfg_File_MifareClassicFormatOriginalKeyList:
        """
        This list is only needed for VHL-Format() support. To encode the new sector
        trailer, the card is authenticated with one of these keys. The VHL Format
        command tries to authenticate with all keys if the list contains more than one
        key.
        
        If this value is not set, the card will by authenticated with factory keys
        (0xFF, 0xFF, ... 0xFF; KeyA).
        
        **This value is used by Mifare classic firmware only. For Mifare plus firmware
        use[ MifarePlusKeyAssignment](.#VhlCfg.File.MifarePlusKeyAssignment)
        instead.**
        """
        return VhlCfg_File_MifareClassicFormatOriginalKeyList(self)
    @property
    def VhlCfg_File_MifareClassicMadKeyB(self) -> VhlCfg_File_MifareClassicMadKeyB:
        """
        This list is only needed by VHL-Format(). If MAD encoding is enabled (refer to
        [MifareMadAid](.#VhlCfg.File.MifareMadAid)), this value contains the write key
        (Key B) of the MAD. This key is needed by VHL Format to create the MAD / adapt
        the MAD when adding a new application. If MAD encoding is not enabled, this
        value may be omitted.
        
        **This value is used by Mifare classic firmware only. For Mifare plus firmware
        use[ MifarePlusKeyAssignment](.#VhlCfg.File.MifarePlusKeyAssignment)
        instead.**
        """
        return VhlCfg_File_MifareClassicMadKeyB(self)
    @property
    def VhlCfg_File_MifareClassicFormatSectorList(self) -> VhlCfg_File_MifareClassicFormatSectorList:
        """
        Only used by VHL-Format() with MAD support enabled. This value contains a list
        of sectors numbers which shall be formatted. On non-MAD cards this value may
        be omitted. In this case [MifareSectorList](.#VhlCfg.File.MifareSectorList)
        (or [MifareClassicBlockList](.#VhlCfg.File.MifareClassicBlockList)) will be
        used instead.
        
        **This value is used by Mifare classic firmware only. For Mifare plus firmware
        use[ MifarePlusKeyAssignment](.#VhlCfg.File.MifarePlusKeyAssignment)
        instead.**
        """
        return VhlCfg_File_MifareClassicFormatSectorList(self)
    @property
    def VhlCfg_File_PivPublicKey(self) -> VhlCfg_File_PivPublicKey:
        """
        This value specifies the public key (ECC P-256) required to perform PIV
        cardholder authentication via PKI-CAK (NIST SP 800-73). It must represent the
        public key of the certificate authority (CA) that issued the Card
        Authentication certificates stored on the cards to be authenticated and read.
        
        **If this value isn't available, the firmware assumes self-signed
        certificates, and the public key is retrieved from the Card Authentication
        certificate.**
        """
        return VhlCfg_File_PivPublicKey(self)
    @property
    def VhlCfg_File_UltralightBlockList(self) -> VhlCfg_File_UltralightBlockList:
        """
        This configuration value is a list of 1 or more block descriptions that
        specify which Ultralight memory blocks have to be accessed by VHL. Each entry
        consists of 2 bytes: The first byte addresses the start block number (first
        block = 0), the second byte defines the number of blocks.
        
        **This value is mandatory for an Ultralight VHL definition.**
        """
        return VhlCfg_File_UltralightBlockList(self)
    @property
    def VhlCfg_File_UltralightKeyIdx(self) -> VhlCfg_File_UltralightKeyIdx:
        """
        This entry is only needed for Ultralight-C. If defined, an authentication is
        performed to allow access to memory areas that are only readable and/or
        writeable after authentication.
        """
        return VhlCfg_File_UltralightKeyIdx(self)
    @property
    def VhlCfg_File_UltralightExtendedBlockList(self) -> VhlCfg_File_UltralightExtendedBlockList:
        """
        This configuration value is a list of 1 or more block descriptions that
        specify which Ultralight memory blocks have to be accessed by VHL. Each entry
        consists of 2 16 bit values: The first addresses the start block number (first
        block = 0), the second value defines the number of blocks.
        """
        return VhlCfg_File_UltralightExtendedBlockList(self)
    @property
    def VhlCfg_File_UltralightKeyList(self) -> VhlCfg_File_UltralightKeyList:
        """
        Contains the list of keys needed to access a MIFARE Ultralight C/EV1 card with
        this VHL file. These keys are referenced by
        [VhlCfg/File/UltralightKeyIdx](.#VhlCfg.File.UltralightKeyIdx)
        """
        return VhlCfg_File_UltralightKeyList(self)
    @property
    def VhlCfg_File_UltralightPassword(self) -> VhlCfg_File_UltralightPassword:
        """
        This entry is only needed for Ultralight-EV1 cards to allow access to
        password-protected memory areas. If defined, a password verification is
        performed.
        """
        return VhlCfg_File_UltralightPassword(self)
    @property
    def VhlCfg_File_Filename(self) -> VhlCfg_File_Filename:
        """
        This is mainly for use by host applications using VHL-Kommands. They can
        search for the corresponding VHL file ID via the
        [VHL.ResolveFilename](../cmds/vhl.xml#VHL.ResolveFilename) command if this
        name is known.
        """
        return VhlCfg_File_Filename(self)
    @property
    def VhlCfg_File_CardType(self) -> VhlCfg_File_CardType:
        """
        Usually the VHL system guesses the card type automatically and uses the
        corresponding configuration values for accessing the card. But for cases where
        the cardtype is guessed wrong or a card contains more than one cardtype this
        value can be used to force the VHL system to work as if a card of this type
        would have been detected.
        """
        return VhlCfg_File_CardType(self)
    @property
    def VhlCfg_File_RetryCnt(self) -> VhlCfg_File_RetryCnt:
        """
        This value specifies how often the firmware shall do retries when card access
        failed.
        
        **This value is not supported in current firmware versions any more. The
        number of retries is determined automatically now (usually 1).**
        """
        return VhlCfg_File_RetryCnt(self)
__all__ = ['Commands', 'ConfigAccessor', 'BaltechScript', 'Template']