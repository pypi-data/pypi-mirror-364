"""
Clean License activation CLI for HexaEight MCP Client
"""

import os
import subprocess
from typing import List
from .utils import (
    download_machine_token_utility,
    print_section, 
    confirm_action,
    save_package_state,
    get_template_content
)

class LicenseActivationCLI:
    """CLI for license activation using machine token utility"""
    
    def run(self, args: List[str]) -> None:
        """Run license activation process"""
        
        print_section(
            "HexaEight License Activation",
            "Set up and activate your AI agent license"
        )
        
        # Check current directory
        current_dir = os.getcwd()
        print(f"📁 License will be created in: {current_dir}")
        
        # Quick warning about license location
        print(f"⚠️  The license file cannot be moved after creation")
        
        if not confirm_action("Continue with license activation setup?", default=True):
            print("👋 License activation cancelled")
            return
        
        try:
            # Step 1: Setup machine token utility
            executable_path = self._setup_utility()
            
            # Step 2: Quick system check
            self._quick_system_check(executable_path)
            
            # Step 3: Show activation guide
            self._show_activation_guide(executable_path)
            
        except Exception as e:
            print(f"❌ License activation setup failed: {e}")
            raise
    
    def _setup_utility(self) -> str:
        """Setup machine token utility"""
        print_section("Machine Token Utility Setup")
        
        executable_path = download_machine_token_utility()
        
        # Save license directory for future reference
        save_package_state("license_directory", os.getcwd())
        
        print(f"✅ Machine token utility ready: {executable_path}")
        return executable_path
    
    def _quick_system_check(self, executable_path: str) -> None:
        """Quick system verification"""
        
        print_section("System Check")
        
        if confirm_action("Run CPU cores check?", default=True):
            self._run_cpu_check(executable_path)
        
        if confirm_action("Verify environment?", default=True):
            self._run_environment_check(executable_path)
        
        print("✅ System checks complete")
    
    def _show_activation_guide(self, executable_path: str) -> None:
        """Show clean activation guide"""
        
        print_section("License Activation Process")
        
        print("📱 **Prerequisites:**")
        print("   1. Download 'HexaEight Authenticator' app")
        print("   2. Create identity resource (generic or domain-based)")
        print("   3. Purchase license at https://store.hexaeight.com")
        print()
        
        print("🚀 **Activation Steps:**")
        print(f"   1. Run: ./{os.path.basename(executable_path)} --newtoken")
        print("   2. Enter your resource name")
        print("   3. Open QR code link in browser")
        print("   4. Scan with HexaEight app")
        print("   5. Approve in mobile app")
        print("   6. Press Enter to complete")
        print()
        
        print("💡 **Identity Options:**")
        print("   • Generic: storm23-cloud-wave-bright09 (instant)")
        print("   • Domain: weather-agent.yourcompany.com (branded)")
        print()
        
        if confirm_action("Start license activation now?", default=False):
            self._start_activation(executable_path)
        else:
            print(f"💾 Ready when you are!")
            print(f"   Run: ./{os.path.basename(executable_path)} --newtoken")
            print(f"   Renew: ./{os.path.basename(executable_path)} --renewtoken")
    
    def _start_activation(self, executable_path: str) -> None:
        """Start license activation process"""
        
        print_section("Starting License Activation")
        
        print(f"🔑 Running activation process...")
        print(f"📋 Command: {os.path.basename(executable_path)} --newtoken")
        print("=" * 50)
        
        try:
            # Run activation interactively
            result = subprocess.run([executable_path, "--newtoken"], check=True)
            
            print("=" * 50)
            
            # Check for success
            license_file = os.path.join(os.getcwd(), "hexaeight.mac")
            if os.path.exists(license_file):
                self._show_success_message()
            else:
                print("⚠️  License file not found - activation may have failed")
                print("🔄 Try again if needed")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Activation failed (exit code: {e.returncode})")
            print("💡 Check the error messages above")
        except KeyboardInterrupt:
            print("\n👋 Activation cancelled")
        except Exception as e:
            print(f"❌ Activation error: {e}")
    
    def _show_success_message(self) -> None:
        """Show success message and next steps"""
        
        print_section("🎉 License Activation Complete!")
        
        print("✅ License file created: hexaeight.mac")
        print("🔒 Your AI agent license is now active")
        print()
        
        print("🚀 **Next Steps:**")
        print("   1. hexaeight-start create-directory-linked-to-hexaeight-license my-project")
        print("   2. hexaeight-start generate-parent-or-child-agent-licenses")
        print("   3. hexaeight-start deploy-multi-ai-agent-samples")
        print()
        
        print("💡 **Key Points:**")
        print("   • Create unlimited child agents during license period")
        print("   • Child agents work forever (even after license expires)")
        print("   • Use organized workspace for development")
        print("   • Deploy child agents anywhere globally")
    
    def _run_cpu_check(self, executable_path: str) -> None:
        """Run CPU cores check"""
        try:
            print(f"🔍 Checking CPU cores...")
            result = subprocess.run([executable_path, "--cpucores"], check=True)
            print("✅ CPU check completed")
        except subprocess.CalledProcessError:
            print("⚠️  CPU check failed (non-critical)")
        except Exception as e:
            print(f"⚠️  CPU check error: {e}")
    
    def _run_environment_check(self, executable_path: str) -> None:
        """Run environment check"""
        try:
            print(f"🔍 Verifying environment...")
            result = subprocess.run([executable_path, "--verifyenvironment"], check=True)
            print("✅ Environment check completed")
        except subprocess.CalledProcessError:
            print("⚠️  Environment check failed (non-critical)")
        except Exception as e:
            print(f"⚠️  Environment check error: {e}")
