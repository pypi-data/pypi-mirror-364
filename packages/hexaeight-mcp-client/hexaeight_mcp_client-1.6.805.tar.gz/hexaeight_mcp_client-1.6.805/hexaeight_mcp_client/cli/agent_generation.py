"""
Agent generation CLI for HexaEight MCP Client
"""

import os
import subprocess
from typing import List, Dict, Any
from hexaeight_agent import get_create_scripts_path
from .utils import (
    check_command_exists, 
    run_command, 
    print_section, 
    confirm_action,
    validate_environment_variables
)

class AgentGenerationCLI:
    """CLI for generating parent and child agent licenses"""
    
    def run(self, args: List[str]) -> None:
        """Run agent generation process"""
        
        print_section(
            "HexaEight Agent License Generation",
            "Generate parent and child agent configuration files using .NET scripts..."
        )
        
        # Check prerequisites first
        if not self._check_prerequisites():
            return
        
        # Check for required environment variables
        if not self._check_environment_setup():
            return
        
        # Get and copy CSX scripts
        scripts_dir = self._setup_scripts()
        if not scripts_dir:
            return
        
        # Show environment info
        self._show_environment_info()
        
        # Interactive generation process
        self._interactive_generation()
    
    def _check_prerequisites(self) -> bool:
        """Check if .NET and dotnet-script are available"""
        
        print("🔍 Checking prerequisites...")
        
        if not check_command_exists("dotnet"):
            print("❌ .NET SDK not found")
            print("💡 Run: hexaeight-check check-prerequisites")
            return False
        
        try:
            run_command(["dotnet", "script", "--version"])
            print("✅ Prerequisites met")
            return True
        except:
            print("❌ dotnet-script not found")
            print("💡 Run: hexaeight-check check-prerequisites")
            return False
    
    def _check_environment_setup(self) -> bool:
        """Check if required environment variables are set"""
        
        print("🔍 Checking environment variables...")
        
        required_vars = [
            "HEXAEIGHT_PUBSUB_URL",
            "HEXAEIGHT_CLIENT_ID", 
            "HEXAEIGHT_TOKENSERVER_URL"
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print("❌ Missing required environment variables:")
            for var in missing:
                print(f"   • {var}")
            
            print("\n💡 You need to set up a HexaEight Client Application first.")
            print("🔗 Visit: https://azuremarketplace.microsoft.com/en-us/marketplace/apps/hexaeightopcprivatelimited1653195738074.hexaeight-agentic-iam?tab=Overview")
            print("\n📋 Example environment setup:")
            print('export HEXAEIGHT_PUBSUB_URL="https://your-server.cloudapp.azure.com:2083/pubsub/YOUR_CLIENT_ID"')
            print('export HEXAEIGHT_CLIENT_ID="YOUR_CLIENT_ID"')
            print('export HEXAEIGHT_TOKENSERVER_URL="https://your-server.cloudapp.azure.com:8443"')
            
            return False
        
        print("✅ Environment variables configured")
        return True
    
    def _setup_scripts(self) -> str:
        """Setup CSX scripts in current directory"""
        
        print("📦 Setting up agent creation scripts...")
        
        try:
            scripts_path = get_create_scripts_path()
            print(f"📁 Scripts source: {scripts_path}")
            
            if not os.path.exists(scripts_path):
                print(f"❌ Scripts directory not found: {scripts_path}")
                return None
            
            # Copy scripts to current directory (FIXED: automatic overwrite)
            script_files = []
            for filename in os.listdir(scripts_path):
                if filename.endswith('.csx'):
                    source = os.path.join(scripts_path, filename)
                    dest = os.path.join('.', filename)
                    
                    # FIXED: Remove existing file without prompting
                    if os.path.exists(dest):
                        os.remove(dest)
                        print(f"🔄 Overwriting existing {filename}")
                    
                    with open(source, 'r') as src_file:
                        content = src_file.read()
                    
                    with open(dest, 'w') as dst_file:
                        dst_file.write(content)
                    
                    script_files.append(filename)
                    print(f"✅ Copied: {filename}")
            
            if not script_files:
                print("❌ No .csx script files found")
                return None
            
            print(f"✅ {len(script_files)} script files ready")
            return os.getcwd()
            
        except Exception as e:
            print(f"❌ Failed to setup scripts: {e}")
            return None
    
    def _show_environment_info(self) -> None:
        """Show current environment configuration"""
        
        print_section("Environment Configuration")
        
        env_vars = {
            "HEXAEIGHT_PUBSUB_URL": os.getenv("HEXAEIGHT_PUBSUB_URL"),
            "HEXAEIGHT_CLIENT_ID": os.getenv("HEXAEIGHT_CLIENT_ID"),
            "HEXAEIGHT_TOKENSERVER_URL": os.getenv("HEXAEIGHT_TOKENSERVER_URL")
        }
        
        for key, value in env_vars.items():
            if value:
                # Mask sensitive parts of URLs and IDs
                display_value = self._mask_sensitive_value(value)
                print(f"✅ {key}: {display_value}")
            else:
                print(f"❌ {key}: Not set")
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive parts of environment values"""
        if len(value) > 20:
            return f"{value[:10]}...{value[-6:]}"
        return value
    
    def _interactive_generation(self) -> None:
        """Interactive agent generation process"""
        
        print_section("Agent Generation Options")
        print("1. Generate Parent Agent Configuration")
        print("2. Generate Child Agent Configuration")
        print("3. Generate Both (Parent first, then Child)")
        print("4. Exit")
        
        while True:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self._generate_parent_agent()
                break
            elif choice == "2":
                self._generate_child_agent()
                break
            elif choice == "3":
                if self._generate_parent_agent():
                    self._generate_child_agent()
                break
            elif choice == "4":
                print("👋 Agent generation cancelled")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    def _generate_parent_agent(self) -> bool:
        """Generate parent agent configuration"""
        
        print_section("Generate Parent Agent")
        
        # Get agent name
        default_name = "parent-agent"
        agent_name = input(f"Enter parent agent name (default: {default_name}): ").strip()
        if not agent_name:
            agent_name = default_name
        
        config_filename = f"{agent_name}.json"
        
        # Confirm generation
        print(f"\n📋 Parent Agent Configuration:")
        print(f"   Agent Name: {agent_name}")
        print(f"   Config File: {config_filename}")
        print(f"   Script: create-identity-for-parent-agent.csx")
        
        if not confirm_action("Generate parent agent configuration?"):
            return False
        
        try:
            print(f"\n🚀 Generating parent agent...")
            
            cmd = [
                "dotnet", "script", 
                "create-identity-for-parent-agent.csx",
                config_filename,
                "--no-cache"
            ]
            
            print(f"📋 Running: {' '.join(cmd)}")
            print(f"=" * 60)
            
            # Run interactively without capturing output
            result = subprocess.run(cmd, check=False)
            
            print(f"=" * 60)
            
            if result.returncode == 0:
                print(f"✅ Parent agent created successfully!")
                print(f"📄 Configuration file: {config_filename}")
                return True
            else:
                print(f"❌ Parent agent generation failed (exit code: {result.returncode})")
                print(f"💡 Check the output above for error details")
                return False
                
        except KeyboardInterrupt:
            print(f"\n👋 Parent agent generation cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Error generating parent agent: {e}")
            return False
    
    def _generate_child_agent(self) -> bool:
        """Generate child agent configuration"""
        
        print_section("Generate Child Agent")
        
        # Check for parent config files
        parent_configs = [f for f in os.listdir('.') if f.startswith('parent-') and f.endswith('.json')]
        
        if not parent_configs:
            print("❌ No parent agent configuration files found")
            print("💡 Generate a parent agent first")
            return False
        
        # Select parent config
        if len(parent_configs) == 1:
            parent_config = parent_configs[0]
            print(f"📄 Using parent config: {parent_config}")
        else:
            print("📄 Available parent configurations:")
            for i, config in enumerate(parent_configs, 1):
                print(f"   {i}. {config}")
            
            while True:
                try:
                    choice = int(input("Select parent config (number): ").strip())
                    if 1 <= choice <= len(parent_configs):
                        parent_config = parent_configs[choice - 1]
                        break
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Please enter a number")
        
        # Get child agent details
        default_child_name = "child_01"
        child_name = input(f"Enter child agent name (default: {default_child_name}): ").strip()
        if not child_name:
            child_name = default_child_name
        
        # Confirm generation
        print(f"\n📋 Child Agent Configuration:")
        print(f"   Child Name: {child_name}")
        print(f"   Parent Config: {parent_config}")
        print(f"   Script: create-identity-for-child-agent.csx")
        
        if not confirm_action("Generate child agent configuration?"):
            return False
        
        try:
            print(f"\n🚀 Generating child agent...")
            print(f"⚠️  NOTE: You will be prompted to enter a password for the child agent")
            
            cmd = [
                "dotnet", "script",
                "create-identity-for-child-agent.csx",
                child_name,
                parent_config,
                "--no-cache"
            ]
            
            print(f"📋 Running: {' '.join(cmd)}")
            print(f"=" * 60)
            
            # Run interactively without capturing output
            result = subprocess.run(cmd, check=False)
            
            print(f"=" * 60)
            
            if result.returncode == 0:
                print(f"✅ Child agent created successfully!")
                print(f"🔑 IMPORTANT: Save the password displayed above - you'll need it to run the child agent")
                return True
            else:
                print(f"❌ Child agent generation failed (exit code: {result.returncode})")
                print(f"💡 Check the output above for error details")
                return False
                
        except KeyboardInterrupt:
            print(f"\n👋 Child agent generation cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Error generating child agent: {e}")
            return False
