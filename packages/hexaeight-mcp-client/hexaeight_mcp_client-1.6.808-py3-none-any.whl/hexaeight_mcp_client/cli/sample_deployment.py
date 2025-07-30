"""
Sample deployment CLI for HexaEight MCP Client
"""

import os
import stat
from typing import List, Dict
from .utils import (
    get_template_content, 
    write_template_file, 
    print_section, 
    confirm_action
)

class SampleDeploymentCLI:
    """CLI for deploying multi-agent sample system"""
    
    def run(self, args: List[str]) -> None:
        """Deploy multi-agent weather sample system"""
        
        print_section(
            "Deploy Multi-Agent Weather Sample System",
            "This will copy sample weather agent files to your current directory..."
        )
        
        current_dir = os.getcwd()
        print(f"📁 Target directory: {current_dir}")
        
        # Check for existing files
        sample_files = [
            "autogen_weather_agent.py",
            "crewai_weather_agent.py",
            "langchain_weather_agent.py", 
            "shared_components.py",
            "setup_environment.sh",
            ".env.sample"
        ]
        
        existing_files = [f for f in sample_files if os.path.exists(f)]
        if existing_files:
            print(f"⚠️  Existing files found: {', '.join(existing_files)}")
            if not confirm_action("Override existing files?"):
                print("👋 Sample deployment cancelled")
                return
        
        try:
            # Deploy sample files
            self._deploy_agent_files()
            self._deploy_environment_setup()
            self._create_readme()
            
            print_section("✅ Sample Deployment Complete")
            print(f"📁 Files deployed to: {current_dir}")
            print(f"")
            print(f"🎯 Next Steps:")
            print(f"1. Configure your environment variables:")
            print(f"   cp .env.sample .env")
            print(f"   # Edit .env with your actual values")
            print(f"")
            print(f"2. Set up environment:")
            print(f"   source setup_environment.sh")
            print(f"")
            print(f"3. Run the agents:")
            print(f"   python autogen_weather_agent.py     # Terminal 1")
            print(f"   python crewai_weather_agent.py      # Terminal 2")
            print(f"   python langchain_weather_agent.py   # Terminal 3")
            print(f"")
            print(f"4. Test with user messages via HexaEight PubSub")
            
        except Exception as e:
            print(f"❌ Sample deployment failed: {e}")
            raise
    
    def _deploy_agent_files(self) -> None:
        """Deploy agent Python files"""
        
        print("📦 Deploying agent files...")
        
        agent_files = {
            "autogen_weather_agent.py": "agents/autogen_weather_agent.py",
            "crewai_weather_agent.py": "agents/crewai_weather_agent.py",
            "langchain_weather_agent.py": "agents/langchain_weather_agent.py",
            "shared_components.py": "agents/shared_components.py"
        }
        
        for dest_file, template_path in agent_files.items():
            try:
                content = get_template_content(template_path)
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Created: {dest_file}")
            except Exception as e:
                print(f"❌ Failed to create {dest_file}: {e}")
                raise
    
    def _deploy_environment_setup(self) -> None:
        """Deploy environment setup files"""
        
        print("🔧 Creating environment setup files...")
        
        # Create environment setup script
        setup_script_content = '''#!/bin/bash

# HexaEight Multi-Agent Weather System Environment Setup

echo "🔧 Setting up HexaEight Multi-Agent Weather System Environment"
echo "=============================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "💡 Copy .env.sample to .env and configure your values:"
    echo "   cp .env.sample .env"
    echo "   # Edit .env with your actual configuration"
    exit 1
fi

# Load environment variables from .env
echo "📋 Loading environment variables from .env..."
export $(grep -v '^#' .env | xargs)

# Validate required variables
required_vars=(
    "HEXAEIGHT_PUBSUB_URL"
    "HEXAEIGHT_CLIENT_ID" 
    "HEXAEIGHT_TOKENSERVER_URL"
    "HEXAEIGHT_CHILD_CONFIG_PASSSWORD"
    "HEXAEIGHT_CHILD_CONFIG_FILENAME"
    "WEATHER_API_KEY"
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_OPENAI_KEY"
    "AZURE_OPENAI_API_VERSION"
    "AZURE_OPENAI_MODEL"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   • $var"
    done
    echo ""
    echo "💡 Please configure these variables in your .env file"
    exit 1
fi

echo "✅ All required environment variables configured"
echo ""
echo "🎯 Environment Ready!"
echo "Now you can run the weather agents:"
echo "   python autogen_weather_agent.py     # Terminal 1"  
echo "   python crewai_weather_agent.py      # Terminal 2"
echo "   python langchain_weather_agent.py   # Terminal 3"
echo ""
echo "📋 Current Configuration:"
echo "   PubSub URL: ${HEXAEIGHT_PUBSUB_URL}"
echo "   Client ID: ${HEXAEIGHT_CLIENT_ID}"
echo "   Child Config: ${HEXAEIGHT_CHILD_CONFIG_FILENAME}"
echo "   Weather API: ✅ Configured"
echo "   Azure OpenAI: ✅ Configured"
'''
        
        with open("setup_environment.sh", 'w', encoding='utf-8') as f:
            f.write(setup_script_content)
        
        # Make executable
        os.chmod("setup_environment.sh", stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        print(f"✅ Created: setup_environment.sh")
        
        # Create sample .env file
        env_sample_content = '''# HexaEight Multi-Agent Weather System Configuration
# Copy this file to .env and configure with your actual values

# HexaEight Client Application Settings (from Agentic IAM Server)
HEXAEIGHT_PUBSUB_URL="https://your-server.cloudapp.azure.com:2083/pubsub/YOUR_CLIENT_ID"
HEXAEIGHT_CLIENT_ID="YOUR_CLIENT_ID"
HEXAEIGHT_TOKENSERVER_URL="https://your-server.cloudapp.azure.com:8443"

# Legacy compatibility (same values as above)
HEXA8_TOKENSERVERURL="https://your-server.cloudapp.azure.com:8443"
HEXA8_CLIENTID="YOUR_CLIENT_ID"

# Child Agent Configuration (from generated child agent)
HEXAEIGHT_CHILD_CONFIG_PASSSWORD="P@sswoxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
HEXAEIGHT_CHILD_CONFIG_FILENAME="child_child_05.json"

# Weather API Configuration (from weatherapi.com)
WEATHER_API_KEY="1012af1a47a74aa2acb104924230911"

# Azure OpenAI Configuration (for LLM capabilities)
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
AZURE_OPENAI_KEY="your-azure-openai-api-key"
AZURE_OPENAI_API_VERSION="2025-01-01-preview"
AZURE_OPENAI_MODEL="gpt-4o-mini"

# Optional: Alternative OpenAI Configuration  
# OPENAI_API_KEY="sk-your-openai-api-key"
# OPENAI_MODEL="gpt-4o-mini"
'''
        
        with open(".env.sample", 'w', encoding='utf-8') as f:
            f.write(env_sample_content)
        print(f"✅ Created: .env.sample")
    
    def _create_readme(self) -> None:
        """Create README for the sample system"""
        
        readme_content = '''# HexaEight Multi-Agent Weather System

This directory contains a complete multi-agent weather system built with HexaEight MCP Client.

## 🌤️ System Components

### Agent Files
- **autogen_weather_agent.py** - AutoGen-powered weather specialist agent
- **crewai_weather_agent.py** - CrewAI-powered weather specialist agent
- **langchain_weather_agent.py** - LangChain-powered weather specialist agent  
- **shared_components.py** - Common utilities and base classes

### Configuration Files
- **.env.sample** - Sample environment configuration
- **setup_environment.sh** - Environment setup script

## 🚀 Quick Start

### 1. Configure Environment
```bash
# Copy sample configuration
cp .env.sample .env

# Edit .env with your actual values:
# - HexaEight Client Application details
# - Child agent password and config file
# - Weather API key (from weatherapi.com)
# - Azure OpenAI credentials
```

### 2. Setup Environment
```bash
# Load and validate environment
source setup_environment.sh
```

### 3. Run Weather Agents
```bash
# Terminal 1: AutoGen weather agent
python autogen_weather_agent.py

# Terminal 2: CrewAI weather agent  
python crewai_weather_agent.py

# Terminal 3: LangChain weather agent
python langchain_weather_agent.py
```

**Note**: Each agent requires its respective framework to be installed:
- AutoGen: `pip install pyautogen`
- CrewAI: `pip install crewai`  
- LangChain: `pip install langchain`

## 🎯 How It Works

### Agent Types
- **Framework-Specific**: Each agent responds to framework-targeted requests
- **Competitive**: All three agents compete for general weather requests
- **Intelligent**: LLM-powered query understanding and natural responses

### Message Examples

**Framework-Targeted** (only specific agent responds):
- "Can the autogen agent tell me the weather in London?"
- "I need weather for Paris. Can the crewai agent respond?"
- "Show me Tokyo weather. Can the langchain agent help?"

**General Weather** (all agents compete):
- "What's the weather in Tokyo?"
- "Give me the forecast for Mumbai"

### Features
- ✅ Real-time weather data via WeatherAPI
- ✅ Natural language responses
- ✅ Framework-specific targeting
- ✅ Competitive message locking
- ✅ Comprehensive weather tools (current, forecast, historical, alerts)
- ✅ Cyclone/storm detection and guidance
- ✅ Secure HexaEight communication

## 🔧 Configuration Requirements

### HexaEight Client Application
Create via: https://azuremarketplace.microsoft.com/en-us/marketplace/apps/hexaeightopcprivatelimited1653195738074.hexaeight-agentic-iam

### Weather API
Sign up at: https://www.weatherapi.com/

### Azure OpenAI
Configure Azure OpenAI resource with gpt-4o-mini model

## 📋 Environment Variables

### Required Variables
- `HEXAEIGHT_PUBSUB_URL` - PubSub server URL from Client Application
- `HEXAEIGHT_CLIENT_ID` - Client ID from HexaEight Agentic IAM
- `HEXAEIGHT_TOKENSERVER_URL` - Token server URL
- `HEXAEIGHT_CHILD_CONFIG_PASSSWORD` - Password from generated child agent
- `HEXAEIGHT_CHILD_CONFIG_FILENAME` - Child agent config file name
- `WEATHER_API_KEY` - API key from weatherapi.com
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_API_VERSION` - API version (e.g., 2025-01-01-preview)
- `AZURE_OPENAI_MODEL` - Model name (e.g., gpt-4o-mini)

## 🎮 Testing the System

### Using HexaEight Publisher (TODO: Add publisher tool)
Send test messages to your PubSub server to see agents respond.

### Agent Status Monitoring
Each agent shows:
- Connection status
- Message processing stats
- Framework targeting decisions
- Weather API responses

## 🛠️ Troubleshooting

### Common Issues
1. **Connection Failed**: Check HexaEight Client Application settings
2. **No Responses**: Verify child agent password and config file
3. **Weather API Errors**: Check weather API key validity
4. **LLM Errors**: Verify Azure OpenAI configuration

### Debug Mode
Set environment variable for detailed logging:
```bash
export HEXAEIGHT_DEBUG=true
```

## 📚 Learn More

- [HexaEight MCP Client Documentation](https://github.com/HexaEightTeam/hexaeight-mcp-client)
- [AutoGen Framework](https://github.com/microsoft/autogen)
- [CrewAI Framework](https://github.com/joaomdmoura/crewAI)
- [LangChain Framework](https://github.com/langchain-ai/langchain)
- [WeatherAPI Documentation](https://www.weatherapi.com/docs/)
'''
        
        with open("README.md", 'w') as f:
            f.write(readme_content)
        print(f"✅ Created: README.md")
