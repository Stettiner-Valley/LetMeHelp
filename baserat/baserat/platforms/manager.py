import os
import platform
from dataclasses import dataclass

from baserat.platforms.macos import MacOSManager


@dataclass(frozen=True)
class OSConstants:
    MAC: str = "Darwin"
    WINDOWS: str = "Windows"
    LINUX: str = "Linux"
    UNKNOWN: str = "Unknown OS"

    os_mapping = {
        "Darwin": MAC,
        "Windows": WINDOWS,
        "Linux": LINUX,
    }

    @classmethod
    def detect_os(cls):
        os_name = platform.system()
        return cls.os_mapping.get(os_name, cls.UNKNOWN)


class OS():
    OPERATING_SYSTEM: str = OSConstants.detect_os()

    def __init__(self):
        if OS.OPERATING_SYSTEM == OSConstants.MAC:
            print("MacOS detected initializing OS manager ..")
            self.os = MacOSManager()
        else:
            print("FATAL ERROR, UNSUPPORTED OS. Exiting ..")
            exit()