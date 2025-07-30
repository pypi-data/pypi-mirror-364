"""
Portable child agent environment setup CLI for HexaEight MCP Client
"""

import os
import json
import subprocess
import asyncio
from typing import List, Dict, Optional

# FIXED: Use modern importlib.resources instead of deprecated pkg_resources
try:
    from importlib import resources
except ImportError:
    # Fallback for Python < 3.9
    import importlib_resources as resources

from .utils import (
    print_section, 
    confirm_action,
    validate_environment_variables,
    run_command,
    get_template_content
)

class PortableSetupCLI:
    """CLI for setting up portable child agent environment on secondary machines"""
    
    def run(self, args: List[str]) -> None:
        """Run portable child agent environment setup"""
        
        print_section(
            "HexaEight Portable Child Agent Environment Setup",
            "Set up child agent environment on a secondary machine (no license file needed)"
        )
        
        # Get child config file
        child_config_file = args[0] if args else None
        if not child_config_file:
            child_config_file = self._find_or_ask_for_config_file()
        
        if not child_config_file:
            print("❌ Child agent configuration file required")
            return
        
        try:
            # Step 1: Check prerequisites (Python packages, not .NET)
            if not self._check_python_prerequisites():
                return
            
            # Step 2: Verify child config file
            if not self._verify_child_config(child_config_file):
                return
            
            # Step 3: Check environment variables
            if not self._check_environment_variables():
                return
            
            # Step 4: Copy and test connection with hexaeight_demo.py
            if not asyncio.run(self._test_pubsub_connection()):
                return
            
            # Step 5: Setup weather environment
            if not self._setup_weather_environment():
                return
            
            # Step 6: Optional - deploy sample agents
            self._optional_deploy_samples()
            
            # Step 7: Provide next steps
            self._show_next_steps()
            
        except Exception as e:
            print(f"❌ Portable setup failed: {e}")
            raise
    
    def _find_or_ask_for_config_file(self) -> Optional[str]:
        """Find or ask user for child config file"""
        
        # Look for child config files in current directory
        child_configs = []
        for file in os.listdir('.'):
            if file.endswith('.json') and ('child' in file.lower()):
                child_configs.append(file)
        
        if len(child_configs) == 1:
            config_file = child_configs[0]
            print(f"📄 Found child config: {config_file}")
            if confirm_action(f"Use {config_file}?"):
                return config_file
        
        elif len(child_configs) > 1:
            print("📄 Multiple child config files found:")
            for i, config in enumerate(child_configs, 1):
                print(f"   {i}. {config}")
            
            while True:
                try:
                    choice = int(input("Select config file (number): ").strip())
                    if 1 <= choice <= len(child_configs):
                        return child_configs[choice - 1]
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Please enter a number")
        
        # Ask user to specify
        config_file = input("Enter path to child agent config file (.json): ").strip()
        if config_file and os.path.exists(config_file):
            return config_file
        
        return None
    
    def _check_python_prerequisites(self) -> bool:
        """Check Python package prerequisites for child agents"""
        
        print_section("Prerequisites Check", "Checking Python packages for portable child agent...")
        
        required_packages = {
            "hexaeight_agent": "1.6.808",
            "hexaeight_mcp_client": "1.6.802"
        }
        
        missing_packages = []
        version_issues = []
        
        for package, min_version in required_packages.items():
            try:
                if package == "hexaeight_agent":
                    import hexaeight_agent
                    installed_version = getattr(hexaeight_agent, '__version__', 'unknown')
                elif package == "hexaeight_mcp_client":
                    import hexaeight_mcp_client
                    installed_version = getattr(hexaeight_mcp_client, '__version__', 'unknown')
                
                print(f"✅ {package}: v{installed_version}")
                
                # Version check (basic string comparison)
                if installed_version != 'unknown' and installed_version < min_version:
                    version_issues.append(f"{package} v{installed_version} < v{min_version}")
                    
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}: Not installed")
        
        # Check optional framework packages
        optional_packages = ["pyautogen", "crewai", "langchain", "openai"]
        print(f"\nOptional Framework Packages:")
        
        for package in optional_packages:
            try:
                __import__(package)
                print(f"✅ {package}: Available")
            except ImportError:
                print(f"⚠️  {package}: Not installed (optional)")
        
        if missing_packages:
            print(f"\n❌ Missing required packages:")
            for package in missing_packages:
                if package == "hexaeight_agent":
                    print(f"   pip install hexaeight-agent>={required_packages[package]}")
                elif package == "hexaeight_mcp_client":
                    print(f"   pip install hexaeight-mcp-client>={required_packages[package]}")
            return False
        
        if version_issues:
            print(f"\n⚠️  Version issues:")
            for issue in version_issues:
                print(f"   {issue}")
            print(f"💡 Consider upgrading: pip install --upgrade hexaeight-agent hexaeight-mcp-client")
        
        print(f"✅ Python prerequisites met for portable child agent")
        return True
    
    def _verify_child_config(self, config_file: str) -> bool:
        """Verify child configuration file"""
        
        print_section("Child Config Verification", f"Verifying: {config_file}")
        
        if not os.path.exists(config_file):
            print(f"❌ Config file not found: {config_file}")
            return False
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            print(f"✅ Config file is valid JSON")
            
            # Check for expected fields (basic validation)
            if 'agent_type' in config_data:
                agent_type = config_data['agent_type']
                print(f"✅ Agent type: {agent_type}")
                
                if 'child' not in agent_type.lower():
                    print(f"⚠️  Agent type '{agent_type}' doesn't appear to be a child agent")
                    if not confirm_action("Continue anyway?"):
                        return False
            else:
                print(f"⚠️  No 'agent_type' field found in config")
            
            print(f"✅ Child config file verified: {config_file}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return False
    
    def _check_environment_variables(self) -> bool:
        """Check required environment variables for child agents"""
        
        print_section("Environment Variables Check", "Checking environment for portable child agent...")
        
        required_vars = [
            "HEXAEIGHT_PUBSUB_URL",
            "HEXAEIGHT_CLIENT_ID",
            "HEXAEIGHT_TOKENSERVER_URL",
            "HEXAEIGHT_CHILD_CONFIG_PASSSWORD",  # Note: spelling matches your examples
            "HEXAEIGHT_CHILD_CONFIG_FILENAME"
        ]
        
        optional_vars = [
            "HEXA8_TOKENSERVERURL",  # Legacy compatibility
            "HEXA8_CLIENTID"         # Legacy compatibility
        ]
        
        # Check required variables
        missing_required = []
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values for display
                display_value = self._mask_sensitive_value(value)
                print(f"✅ {var}: {display_value}")
            else:
                missing_required.append(var)
                print(f"❌ {var}: Not set")
        
        # Check optional variables
        print(f"\nOptional/Legacy Variables:")
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                display_value = self._mask_sensitive_value(value)
                print(f"✅ {var}: {display_value}")
            else:
                print(f"ℹ️  {var}: Not set (optional)")
        
        if missing_required:
            print(f"\n❌ Missing required environment variables:")
            for var in missing_required:
                print(f"   {var}")
            
            print(f"\n💡 Set these environment variables before running child agents:")
            print(f"   export HEXAEIGHT_PUBSUB_URL=\"https://your-server:2083/pubsub/YOUR_CLIENT_ID\"")
            print(f"   export HEXAEIGHT_CLIENT_ID=\"YOUR_CLIENT_ID\"")
            print(f"   export HEXAEIGHT_TOKENSERVER_URL=\"https://your-server:8443\"")
            print(f"   export HEXAEIGHT_CHILD_CONFIG_PASSSWORD=\"child_agent_password\"")
            print(f"   export HEXAEIGHT_CHILD_CONFIG_FILENAME=\"child_config.json\"")
            
            if confirm_action("Would you like guidance on setting environment variables?"):
                self._show_environment_setup_guide()
            
            return False
        
        print(f"✅ Environment variables configured for portable child agent")
        return True
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive parts of environment values"""
        if len(value) > 20:
            return f"{value[:10]}...{value[-6:]}"
        elif len(value) > 10:
            return f"{value[:6]}...{value[-3:]}"
        return value
    
    def _show_environment_setup_guide(self) -> None:
        """Show detailed environment setup guide"""
        
        print_section("Environment Setup Guide")
        
        print(f"📋 Required Environment Variables for Portable Child Agent:")
        print(f"")
        print(f"1. **HexaEight Client Application Settings** (from main machine):")
        print(f"   export HEXAEIGHT_PUBSUB_URL=\"https://your-server.cloudapp.azure.com:2083/pubsub/YOUR_CLIENT_ID\"")
        print(f"   export HEXAEIGHT_CLIENT_ID=\"YOUR_CLIENT_ID\"")
        print(f"   export HEXAEIGHT_TOKENSERVER_URL=\"https://your-server.cloudapp.azure.com:8443\"")
        print(f"")
        print(f"2. **Child Agent Configuration** (from generated child agent):")
        print(f"   export HEXAEIGHT_CHILD_CONFIG_PASSSWORD=\"P@sswo...\" # Password from child agent creation")
        print(f"   export HEXAEIGHT_CHILD_CONFIG_FILENAME=\"child_agent.json\" # Your config file name")
        print(f"")
        print(f"3. **Optional: Create .env file for persistence:**")
        print(f"   echo 'HEXAEIGHT_PUBSUB_URL=https://your-server...' > .env")
        print(f"   echo 'HEXAEIGHT_CLIENT_ID=YOUR_CLIENT_ID' >> .env")
        print(f"   # ... add other variables")
        print(f"   source .env  # Load variables")
    
    async def _test_pubsub_connection(self) -> bool:
        """Test PubSub connection using hexaeight_demo.py"""
        
        print_section("PubSub Connection Test", "Testing connection with hexaeight_demo.py...")
        
        # Copy hexaeight_demo.py from package
        demo_file = "hexaeight_demo.py"
        if os.path.exists(demo_file):
            if not confirm_action(f"Override existing {demo_file}?"):
                print(f"✅ Using existing {demo_file}")
            else:
                self._copy_demo_script(demo_file)
        else:
            self._copy_demo_script(demo_file)
        
        print(f"📄 Demo script ready: {demo_file}")
        
        # Check if user wants to test connection
        if not confirm_action("Test PubSub connection now?"):
            print(f"⏭️  Skipping connection test")
            print(f"💡 You can test later by running: python {demo_file}")
            return True
        
        print(f"🔗 Testing PubSub connection...")
        print(f"📋 Running: python {demo_file}")
        
        try:
            # Run the demo script
            result = subprocess.run(
                ["python", demo_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ PubSub connection test successful!")
                if result.stdout:
                    print(f"📋 Output:")
                    print(result.stdout)
                return True
            else:
                print(f"❌ PubSub connection test failed")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                
                print(f"\n💡 Troubleshooting:")
                print(f"   • Check environment variables")
                print(f"   • Verify PubSub server is accessible")
                print(f"   • Ensure child config file is correct")
                
                return confirm_action("Continue setup despite connection test failure?")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Connection test timed out")
            print(f"💡 This might indicate network issues or incorrect configuration")
            return confirm_action("Continue setup despite timeout?")
        except Exception as e:
            print(f"❌ Error running connection test: {e}")
            return confirm_action("Continue setup despite test error?")
    
    def _copy_demo_script(self, demo_file: str) -> None:
        """Copy hexaeight_demo.py from package"""
        
        try:
            # FIXED: Use modern importlib.resources instead of pkg_resources
            import hexaeight_agent
            
            try:
                # Try modern approach first
                with resources.files(hexaeight_agent).joinpath('demo/hexaeight_demo.py').open('r', encoding='utf-8') as demo_script:
                    demo_content = demo_script.read()
            except (AttributeError, FileNotFoundError):
                # Fallback for older package structure or different path
                try:
                    with resources.files(hexaeight_agent).joinpath('hexaeight_demo.py').open('r', encoding='utf-8') as demo_script:
                        demo_content = demo_script.read()
                except (AttributeError, FileNotFoundError):
                    # Last resort: check if available in package root
                    demo_content = resources.files(hexaeight_agent).joinpath('demo.py').read_text(encoding='utf-8')
            
            with open(demo_file, 'w') as f:
                f.write(demo_content)
            
            print(f"✅ Copied demo script: {demo_file}")
            
        except Exception as e:
            print(f"❌ Failed to copy demo script: {e}")
            print(f"💡 You can manually copy from: $HOME/venv/lib64/python3.12/site-packages/hexaeight_agent/demo/hexaeight_demo.py")
            raise
    
    def _setup_weather_environment(self) -> bool:
        """Guide through weather agent environment setup"""
        
        print_section("Weather Agent Environment Setup", "Configure environment for weather agents...")
        
        # Check for weather-related environment variables
        weather_vars = {
            "WEATHER_API_KEY": "Weather API key from weatherapi.com",
            "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint URL",
            "AZURE_OPENAI_KEY": "Azure OpenAI API key",
            "AZURE_OPENAI_API_VERSION": "Azure OpenAI API version",
            "AZURE_OPENAI_MODEL": "Azure OpenAI model name"
        }
        
        missing_weather_vars = []
        
        print(f"🌤️  Weather Agent Environment Variables:")
        for var, description in weather_vars.items():
            value = os.getenv(var)
            if value:
                display_value = self._mask_sensitive_value(value) if 'key' in var.lower() else value
                print(f"✅ {var}: {display_value}")
            else:
                missing_weather_vars.append(var)
                print(f"❌ {var}: Not set ({description})")
        
        if missing_weather_vars:
            print(f"\n⚠️  Missing weather agent environment variables")
            print(f"💡 Weather agents require additional configuration:")
            print(f"")
            print(f"🌤️  **Weather API** (sign up at weatherapi.com):")
            print(f"   export WEATHER_API_KEY=\"your-weather-api-key\"")
            print(f"")
            print(f"🤖 **Azure OpenAI** (for LLM capabilities):")
            print(f"   export AZURE_OPENAI_ENDPOINT=\"https://your-openai.openai.azure.com\"")
            print(f"   export AZURE_OPENAI_KEY=\"your-azure-openai-key\"")
            print(f"   export AZURE_OPENAI_API_VERSION=\"2025-01-01-preview\"")
            print(f"   export AZURE_OPENAI_MODEL=\"gpt-4o-mini\"")
            
            if confirm_action("Would you like to create a .env template for weather agents?"):
                self._create_weather_env_template()
        
        print(f"✅ Weather environment setup guidance provided")
        return True
    
    def _create_weather_env_template(self) -> None:
        """Create .env template for weather agents"""
        
        env_template = """# HexaEight Portable Child Agent Environment
# Copy and configure these variables for weather agents

# HexaEight Client Application (from main machine)
HEXAEIGHT_PUBSUB_URL="https://your-server.cloudapp.azure.com:2083/pubsub/YOUR_CLIENT_ID"
HEXAEIGHT_CLIENT_ID="YOUR_CLIENT_ID"
HEXAEIGHT_TOKENSERVER_URL="https://your-server.cloudapp.azure.com:8443"

# Legacy compatibility
HEXA8_TOKENSERVERURL="https://your-server.cloudapp.azure.com:8443"
HEXA8_CLIENTID="YOUR_CLIENT_ID"

# Child Agent Configuration (from generated child agent)
HEXAEIGHT_CHILD_CONFIG_PASSSWORD="P@sswo...child-agent-password"
HEXAEIGHT_CHILD_CONFIG_FILENAME="child_config.json"

# Weather API (from weatherapi.com)
WEATHER_API_KEY="your-weather-api-key"

# Azure OpenAI (for LLM capabilities)
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
AZURE_OPENAI_KEY="your-azure-openai-key"
AZURE_OPENAI_API_VERSION="2025-01-01-preview"
AZURE_OPENAI_MODEL="gpt-4o-mini"

# Optional: Alternative OpenAI
# OPENAI_API_KEY="sk-your-openai-api-key"
# OPENAI_MODEL="gpt-4o-mini"
"""
        
        env_file = ".env.portable-child-agent"
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        print(f"✅ Created environment template: {env_file}")
        print(f"💡 Configure this file and load with: source {env_file}")
    
    def _optional_deploy_samples(self) -> None:
        """Optional deployment of sample agents"""
        
        print_section("Sample Agents Deployment", "Deploy sample weather agents for testing...")
        
        if confirm_action("Deploy sample weather agents (AutoGen, CrewAI, LangChain)?"):
            try:
                # Import and run the sample deployment
                from .sample_deployment import SampleDeploymentCLI
                
                print(f"🚀 Deploying sample agents...")
                sample_cli = SampleDeploymentCLI()
                sample_cli.run([])
                
                print(f"✅ Sample agents deployed successfully")
                
            except Exception as e:
                print(f"❌ Sample deployment failed: {e}")
                print(f"💡 You can deploy manually later with: hexaeight-deploy multi-ai-agent-samples")
        else:
            print(f"⏭️  Skipping sample deployment")
            print(f"💡 Deploy later with: hexaeight-deploy multi-ai-agent-samples")
    
    def _show_next_steps(self) -> None:
        """Show next steps for running portable child agents"""
        
        print_section("✅ Portable Child Agent Setup Complete", "Next steps to run your child agents...")
        
        print(f"🎯 **Your portable child agent environment is ready!**")
        print(f"")
        print(f"📋 **Next Steps:**")
        print(f"")
        print(f"1. **Load Environment Variables:**")
        print(f"   source .env.portable-child-agent  # If you created the template")
        print(f"   # OR manually export all required variables")
        print(f"")
        print(f"2. **Test Connection** (if you haven't already):")
        print(f"   python hexaeight_demo.py")
        print(f"")
        print(f"3. **Run Weather Agents** (if deployed):")
        print(f"   python autogen_weather_agent.py     # Terminal 1")
        print(f"   python crewai_weather_agent.py      # Terminal 2")
        print(f"   python langchain_weather_agent.py   # Terminal 3")
        print(f"")
        print(f"4. **Install Framework Dependencies** (as needed):")
        print(f"   pip install pyautogen    # For AutoGen agent")
        print(f"   pip install crewai       # For CrewAI agent")
        print(f"   pip install langchain    # For LangChain agent")
        print(f"")
        print(f"🎮 **Testing Your Agents:**")
        print(f"   Send messages via HexaEight PubSub to test agent responses")
        print(f"")
        print(f"🆘 **Troubleshooting:**")
        print(f"   • Verify all environment variables are set")
        print(f"   • Check network connectivity to PubSub server")
        print(f"   • Ensure child config file password is correct")
        print(f"   • Test with hexaeight_demo.py for basic connectivity")
        print(f"")
        print(f"🎉 **Happy multi-agent development!**")
