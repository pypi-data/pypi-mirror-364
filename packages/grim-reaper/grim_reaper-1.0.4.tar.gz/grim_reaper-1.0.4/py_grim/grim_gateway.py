#!/usr/bin/env python3
"""
Grim Reaper Gateway
Main entry point for the Python package
"""

import sys
import argparse
import subprocess
import os
from pathlib import Path

class GrimGateway:
    """Main gateway for Grim Reaper Python package"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.description = "The Ultimate Backup, Monitoring, and Security System"
        # Set the correct GRIM_ROOT for PyPI installations
        self.grim_root = "/opt/reaper"
        
    def show_banner(self):
        """Display the Grim Reaper banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🗡️ GRIM REAPER 🗡️                        ║
║                                                              ║
║  {self.description}                    ║
║  Version: {self.version}                                    ║
║  Python Package - pip install grim-reaper                   ║
║  GRIM_ROOT: {self.grim_root}                                ║
║                                                              ║
║  🚀 Backup • 🔍 Monitor • 🛡️ Security • 🤖 AI              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  grim backup     - Backup system and files
  grim monitor    - Monitor system health and performance
  grim scan       - Security scanning and analysis
  grim health     - System health check
  grim scythe     - Orchestration and automation
  
Examples:
  grim backup --source /home --dest /backups
  grim monitor --interval 30
  grim scan --path /var/www
  grim health --verbose
  
For more information: https://grim.so
        """
        print(help_text)
    
    def run_command(self, command, args=None):
        """Run a Grim command"""
        try:
            # Set environment variable for GRIM_ROOT
            env = os.environ.copy()
            env['GRIM_ROOT'] = self.grim_root
            
            # Check multiple locations for grim_throne.sh
            possible_paths = [
                Path(self.grim_root) / "grim_throne.sh",  # Primary location
                Path(__file__).parent.parent / "grim_throne.sh",  # Development
                Path("/usr/local/share/grim-reaper/grim_throne.sh"),  # System install
                Path("/usr/share/grim-reaper/grim_throne.sh"),  # System install
                Path(sys.prefix) / "share/grim-reaper/grim_throne.sh",  # Virtual env
            ]
            
            grim_script = None
            for path in possible_paths:
                if path.exists():
                    grim_script = path
                    break
            
            if grim_script:
                cmd = [str(grim_script), command] + (args or [])
                result = subprocess.run(cmd, capture_output=True, text=True, env=env)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                return result.returncode
            else:
                print("❌ Error: grim_throne.sh not found in any expected location")
                print(f"GRIM_ROOT: {self.grim_root}")
                print("Expected locations:")
                for path in possible_paths:
                    print(f"  - {path}")
                return 1
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return 1
    
    def main(self, args=None):
        """Main entry point"""
        if args is None:
            args = sys.argv[1:]
        
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  grim backup --source /home --dest /backups
  grim monitor --interval 30
  grim scan --path /var/www
  grim health --verbose
            """
        )
        
        parser.add_argument(
            "command",
            nargs="?",
            choices=["backup", "monitor", "scan", "health", "scythe", "help"],
            help="Grim command to execute"
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version=f"grim-reaper {self.version}"
        )
        
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="Arguments to pass to the command"
        )
        
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            self.show_banner()
            self.show_help()
            return 0
        
        if parsed_args.command == "help":
            self.show_banner()
            self.show_help()
            return 0
        
        # Run the command
        return self.run_command(parsed_args.command, parsed_args.args)

def main():
    """Main function for console script entry point"""
    gateway = GrimGateway()
    sys.exit(gateway.main())

if __name__ == "__main__":
    main() 