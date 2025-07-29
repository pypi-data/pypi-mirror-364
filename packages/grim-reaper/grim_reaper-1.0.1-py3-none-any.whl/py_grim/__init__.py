"""
Grim Reaper Python Package
The Ultimate Backup, Monitoring, and Security System

Install with: pip install grim-reaper
"""

__version__ = "1.0.0"
__author__ = "Bernie Gengel and his beagle Buddy"
__email__ = "packages@tuskt.sk"
__url__ = "https://grim.so"
__license__ = "BBL"

from .grim_gateway import GrimGateway
from .backup import GrimBackup
from .monitor import GrimMonitor
from .scanner import GrimScanner
from .health import GrimHealth

__all__ = [
    "GrimGateway",
    "GrimBackup", 
    "GrimMonitor",
    "GrimScanner",
    "GrimHealth",
    "__version__",
    "__author__",
    "__email__",
    "__url__",
    "__license__",
]

def main():
    """Main entry point for the grim-reaper package"""
    from .grim_gateway import main as gateway_main
    gateway_main()

if __name__ == "__main__":
    main() 