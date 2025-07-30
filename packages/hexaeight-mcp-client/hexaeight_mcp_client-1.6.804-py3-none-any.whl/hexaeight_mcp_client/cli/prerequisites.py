"""
Prerequisites check CLI for HexaEight MCP Client
"""

import subprocess
from typing import List, Tuple
from .utils import check_command_exists, run_command, print_section

class PrerequisitesCLI:
    """CLI for checking prerequisites"""
    
    def run(self, args: List[str]) -> None:
        """Run prerequisites check"""
        
        print_section(
            "HexaEight Prerequisites Check", 
            "Checking required software installations..."
        )
        
        all_good = True
        
        # Check .NET 8
        dotnet_ok, dotnet_version = self._check_dotnet()
        if dotnet_ok:
            print(f"✅ .NET SDK: {dotnet_version}")
        else:
            print(f"❌ .NET SDK: Not found or incorrect version")
            all_good = False
        
        # Check dotnet-script
        script_ok, script_version = self._check_dotnet_script()
        if script_ok:
            print(f"✅ dotnet-script: {script_version}")
        else:
            print(f"❌ dotnet-script: Not installed")
            all_good = False
        
        # Summary and instructions
        if all_good:
            print_section("✅ All Prerequisites Met", "Your system is ready for HexaEight agent development!")
        else:
            print_section("❌ Missing Prerequisites", "Please install the missing software:")
            
            if not dotnet_ok:
                print(f"\n📥 Install .NET 8 SDK:")
                print(f"   Visit: https://dotnet.microsoft.com/download/dotnet/8.0")
                print(f"   Download and install .NET 8 SDK for your platform")
            
            if not script_ok:
                print(f"\n📥 Install dotnet-script:")
                print(f"   Run: dotnet tool install -g dotnet-script")
                print(f"   This will install the global dotnet-script tool")
            
            print(f"\n🔄 After installation, run this command again to verify:")
            print(f"   hexaeight-check check-prerequisites")
    
    def _check_dotnet(self) -> Tuple[bool, str]:
        """Check .NET SDK installation and version"""
        try:
            result = run_command(["dotnet", "--version"], check=True)
            version = result.stdout.strip()
            
            # Check if it's .NET 8.x
            if version.startswith("8."):
                return True, f"v{version} (Compatible)"
            else:
                # Check if .NET 8 is available among installed SDKs
                try:
                    sdk_result = run_command(["dotnet", "--list-sdks"], check=True)
                    sdks = sdk_result.stdout
                    
                    if "8." in sdks:
                        return True, f"v{version} (.NET 8 available)"
                    else:
                        return False, f"v{version} (.NET 8 required)"
                except:
                    return False, f"v{version} (.NET 8 required)"
                    
        except Exception:
            return False, "Not installed"
    
    def _check_dotnet_script(self) -> Tuple[bool, str]:
        """Check dotnet-script installation"""
        try:
            result = run_command(["dotnet", "script", "--version"], check=True)
            version = result.stdout.strip()
            return True, f"v{version}"
        except Exception:
            # Try alternative check
            try:
                result = run_command(["dotnet", "tool", "list", "-g"], check=True)
                if "dotnet-script" in result.stdout:
                    return True, "Installed (version check failed)"
                else:
                    return False, "Not installed"
            except Exception:
                return False, "Not installed"
