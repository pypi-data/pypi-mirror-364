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
        
    def show_banner(self):
        """Display the Grim Reaper banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🗡️ GRIM REAPER 🗡️                        ║
║                                                              ║
║  {self.description}                    ║
║  Version: {self.version}                                    ║
║  Python Package - pip install grim-reaper                   ║
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
            # Check if grim_throne.sh exists
            grim_script = Path(__file__).parent.parent / "grim_throne.sh"
            if grim_script.exists():
                cmd = [str(grim_script), command] + (args or [])
                result = subprocess.run(cmd, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                return result.returncode
            else:
                print("❌ Error: grim_throne.sh not found")
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