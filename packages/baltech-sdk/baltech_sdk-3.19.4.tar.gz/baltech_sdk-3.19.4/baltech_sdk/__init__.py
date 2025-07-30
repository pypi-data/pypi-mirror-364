import sys
import importlib.resources
from pathlib import Path
from typing import Protocol, Tuple, Optional, Union

from .baltech_api import Commands, ConfigAccessor
from .baltech_api.typedefs import Sys_ErrCfgNotFound
from .brp_lib.protocols import BrpStack, UsbHid, RS232, SecureChannel, PKI, Tcp
from .brp_lib.dll_wrapper import c_brp_lib

from .baltech_api.typedefs import *
from .baltech_api.template import *
from .baltech_api.baltech_script import *


class Brp(BrpStack, Commands):
    pass


class ConfDict(Protocol):
    def __getitem__(self, item: Tuple[int, Optional[int]]) -> bytes: ...
    def __setitem__(self, key: Tuple[int, Optional[int]], content: Optional[bytes]) -> None: ...


class _CommandsConfDictWrapper(ConfDict):
    def __init__(self, cmds: Commands) -> None:
        self.cmds = cmds

    def __getitem__(self, item: Tuple[int, Optional[int]]) -> bytes:
        key, value = item
        if value is None:
            raise KeyError(item)
        try:
            return self.cmds.Sys_CfgGetValue(Key=key, Value=value)
        except Sys_ErrCfgNotFound:
            raise KeyError(item)

    def __setitem__(self, item: Tuple[int, Optional[int]], content: Optional[bytes]) -> None:
        key, value = item
        if content is None:
            try:
                self.cmds.Sys_CfgDelValues(Key=key, Value=value if value is not None else 0xFF)
            except Sys_ErrCfgNotFound:
                raise KeyError(item)
        else:
            if value is None:
                raise KeyError(item)
            try:
                self.cmds.Sys_CfgSetValue(Key=key, Value=value, Content=content)
            except Sys_ErrCfgNotFound:
                raise KeyError(item)


class Config(ConfigAccessor):
    def __init__(self, cfg_src: Union[ConfDict, Commands]) -> None:
        self.confdict = _CommandsConfDictWrapper(cfg_src) if isinstance(cfg_src, Commands) else cfg_src

    def execute(self, frame: bytes) -> bytes:
        mode = frame[0]
        masterkey = frame[1]
        subkey = frame[2] if len(frame) > 2 else 0xFF
        value = frame[3] if len(frame) > 3 else None
        content = frame[4:] if len(frame) > 4 else b""
        key = (masterkey << 8) | subkey

        if mode == 0:  # get
            return self.confdict[(key, value)]

        if mode == 1:  # set
            self.confdict[(key, value)] = content
            return b""

        if mode == 2:
            self.confdict[(key, value)] = None
            return b""

        raise ValueError(f"unknown mode '{mode}' in configuration frame {frame!r}")


def get_brp_lib_path() -> Optional[Path]:
    return c_brp_lib.dll_path


def set_brp_lib_path(path: Union[Path, str]) -> None:
    c_brp_lib.dll_path = Path(path)


def _autodetect_brp_lib() -> None:
    arch = 64 if sys.maxsize > 2 ** 32 else 32
    platform = sys.platform.replace("win32", "win")
    extension = {
        "win": "dll"
    }.get(platform, "unknown")
    dll_name = f"brp_lib.{platform}{arch}.{extension}"

    root_resource = importlib.resources.files("baltech_sdk")
    dll_resource = root_resource / "brp_lib" / dll_name
    dll_path = Path(str(dll_resource))
    if dll_path.exists():
        set_brp_lib_path(dll_path)


_autodetect_brp_lib()
