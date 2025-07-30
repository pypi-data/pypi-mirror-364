# HexaEight MCP Client

🚀 **Framework-agnostic MCP integration with automatic multi-agent coordination and military-grade encryption.**

Build sophisticated multi-agent systems with minimal code while maintaining complete security and framework choice.

## 🌟 Key Features

- 🔐 **Secure Agent Identity** - Military-grade encryption for agent authentication and communication
- 🤖 **Framework Integration** - AutoGen, CrewAI, LangChain with secure agent coordination  
- 🛠️ **Multi-Agent Types** - LLM agents, Tool agents, User agents with automatic coordination
- 🌐 **Automatic Discovery** - Dynamic capability discovery and intelligent message routing
- 📡 **PubSub Coordination** - Seamless agent communication and task delegation
- ⚡ **One-Line Setup** - From configuration to production-ready agents instantly
- 🎯 **Business Logic** - Write your actual API/database code once in tool agents
- 🔒 **Production Security** - Zero plain-text secrets, secure agent identity management

## 📋 Prerequisites

### 1. HexaEight Agentic IAM Server
Deploy from Azure Marketplace to create Client Applications:
- **Azure Marketplace**: [HexaEight Agentic IAM](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/hexaeightopcprivatelimited1653195738074.hexaeight-agentic-iam)
- Creates ClientID, Token Server URL, PubSub URL
- Enables secure agent identity management

### 2. Machine License
Purchase and activate on your development machine:
- **License Store**: [store.hexaeight.com](https://store.hexaeight.com)
- Pricing: 1 CPU = $15, 2 CPU = $30, 4 CPU = $60 (minimum 5 days)
- Enables creation of **1 parent configuration** + **unlimited child configurations**

### 3. Mobile App Setup
- Download **"HexaEight Authenticator"** app (iOS/Android)
- Create generic resource (instant) or domain-based resource (branded)
- Used for secure license activation

### Agent Licensing Model

| Agent Type | License Requirement | Expiry Behavior |
|------------|--------------------|-----------------| 
| **Parent Agents** | ✅ Active HexaEight license required | ❌ Stop working when license expires |
| **Child Agents** | ✅ Created with valid license | ✅ Continue working after license expires |

## 🚀 Installation

```bash
# Basic installation
pip install hexaeight-mcp-client

# With framework support
pip install hexaeight-mcp-client[autogen]    # For AutoGen
pip install hexaeight-mcp-client[crewai]     # For CrewAI
pip install hexaeight-mcp-client[langchain]  # For LangChain
pip install hexaeight-mcp-client[all]        # All frameworks
```

### Prerequisites Installation

```bash
# Core HexaEight agent package
pip install hexaeight-agent

# Optional: Framework packages
pip install pyautogen  # For AutoGen integration
pip install crewai     # For CrewAI integration  
pip install langchain  # For LangChain integration
```

## 🎓 Quick Start Guide

### Step 1: Learn the Concepts
```bash
# Interactive presentation of HexaEight AI agent concepts
hexaeight-start show-concepts

# Auto-advancing presentation (no interaction required)
hexaeight-start show-concepts --auto
```

### Step 2: Check Prerequisites
```bash
# Verify system requirements (.NET, dotnet-script)
hexaeight-start check-prerequisites
```

### Step 3: Activate License
```bash
# Clean, focused license activation process
hexaeight-start license-activation
```

### Step 4: Create Development Environment
```bash
# Create organized workspace with license hardlinks
hexaeight-start create-directory-linked-to-hexaeight-license my-ai-project
cd my-ai-project

# Generate parent and child agent configuration files
hexaeight-start generate-parent-or-child-agent-licenses

# Deploy sample multi-agent weather system
hexaeight-start deploy-multi-ai-agent-samples
```

## 🔐 Secure LLM Configuration

### Supported LLM Providers

| Provider | Configuration Example |
|----------|----------------------|
| **OpenAI** | `{"provider": "openai", "api_key": "sk-...", "model": "gpt-4"}` |
| **Azure OpenAI** | `{"provider": "azure_openai", "api_key": "...", "azure_endpoint": "https://..."}` |
| **Anthropic** | `{"provider": "anthropic", "api_key": "sk-ant-...", "model": "claude-3-sonnet"}` |
| **Local Ollama** | `{"provider": "ollama", "base_url": "http://localhost:11434", "model": "llama2"}` |

## 🤖 Framework Integration

### AutoGen Integration

```python
from hexaeight_mcp_client import create_autogen_agent_with_hexaeight

# Create AutoGen agent with secure HexaEight integration
autogen_agent, hexaeight_agent = await create_autogen_agent_with_hexaeight(
    config_file="parent_config.json",
    agent_type="parentLLM",
    name="IntelligentCoordinator",
    system_message="You can coordinate with multiple specialized agents and services."
)

# AutoGen agent now has:
# ✅ Secure HexaEight integration
# ✅ HexaEight coordination tools
# ✅ Automatic capability discovery
# ✅ Multi-agent coordination via PubSub
```

### CrewAI Integration

```python
from hexaeight_mcp_client import create_crewai_agent_with_hexaeight

# Create CrewAI agent with secure HexaEight integration
crewai_agent, hexaeight_agent = await create_crewai_agent_with_hexaeight(
    config_file="parent_config.json",
    agent_type="parentLLM", 
    role="Multi-Agent Coordinator",
    goal="Coordinate complex workflows using available tools and services",
    backstory="Expert in orchestrating multi-agent systems with secure communication"
)
```

### LangChain Integration

```python
from hexaeight_mcp_client import HexaEightAutoConfig
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

# Create LangChain setup with HexaEight integration
hexaeight_agent = await HexaEightAutoConfig.create_llm_agent(
    agent_type="parentLLM",
    config_file="parent_config.json",
    framework="langchain"
)

# Use with LangChain for secure multi-agent coordination
tools = hexaeight_agent.get_available_tools()
# Integrate with your LangChain LLM of choice
```

## 🛠️ Multi-Agent Architecture

### Agent Types

| Agent Type | Purpose | Verification | Broadcasts | Use Case |
|------------|---------|--------------|------------|----------|
| **parentLLM** | LLM coordination | ✅ Required | ✅ Receives all | Main intelligence and coordination |
| **childLLM** | LLM task execution | ✅ Required | ✅ Receives all | Specialized LLM workers |
| **parentTOOL** | Service provision | ❌ Not required | ❌ Ignores broadcasts | API services, databases |
| **childTOOL** | Specialized services | ❌ Not required | ❌ Ignores broadcasts | Specific tool implementations |
| **USER** | Human interaction | ❌ Not required | ❌ Broadcasts to LLMs only | User interfaces |

### Quick Agent Creation

```python
from hexaeight_mcp_client import quick_autogen_llm, quick_tool_agent, quick_user_agent

# LLM Agent (Intelligence Layer)
llm_agent = await quick_autogen_llm(
    config_file="parent_config.json",
    agent_type="parentLLM"
)

# Tool Agent (Business Logic Layer) 
weather_agent = await quick_tool_agent(
    config_file="weather_config.json",
    service_formats=["weather_request", "forecast_request"],
    agent_type="parentTOOL"
)

# User Agent (Interface Layer)
user_agent = await quick_user_agent(
    config_file="user_config.json"
)
```

## 🔧 Implementing Business Logic (Tool Agents)

### Weather Service Example

```python
class WeatherService:
    async def initialize(self):
        # Create tool agent
        self.agent = await quick_tool_agent(
            config_file="weather_config.json",
            service_formats=["weather_request", "location_query"],
            agent_type="parentTOOL"
        )
        
        # Register your business logic
        self.agent.register_service_handler("weather_request", self.handle_weather)
    
    async def handle_weather(self, content, event, tracker):
        """YOUR ACTUAL BUSINESS LOGIC GOES HERE"""
        
        # Parse request
        request = json.loads(content)
        location = request.get("location", "London")
        
        # 🌍 CALL YOUR ACTUAL WEATHER API
        weather_data = await self.call_openweather_api(location)
        
        # Process and enhance data
        enhanced_data = self.process_weather_data(weather_data)
        
        # Send structured response
        response = {
            "type": "weather_response",
            "location": location,
            "data": enhanced_data,
            "processed_by": self.agent.agent_name
        }
        
        await self.agent.hexaeight_agent.publish_to_agent(
            self.agent.pubsub_url,
            "internal_id",
            event.sender_internal_id,
            json.dumps(response),
            "weather_response"
        )
        
        return True
```

## 🌐 Portable Child Agent Deployment

Deploy child agents anywhere without license requirements:

```bash
# Setup child agent environment on any machine
hexaeight-start setup-portable-child-agent-environment child_config.json
```

**Deployment Benefits:**
- 🌍 Deploy on cloud services (AWS, Azure, GCP)
- 🔧 Edge computing (Raspberry Pi, IoT devices)
- 📦 Container deployment (Docker, Kubernetes)
- ♾️ Child agents work forever (even after parent license expires)

## 📊 Complete Development Workflow

```bash
# 1. Learn concepts first
hexaeight-start show-concepts

# 2. Check system requirements
hexaeight-start check-prerequisites

# 3. Clean license activation
hexaeight-start license-activation

# 4. Create organized workspace
hexaeight-start create-directory-linked-to-hexaeight-license my-project
cd my-project

# 5. Generate agent configurations
hexaeight-start generate-parent-or-child-agent-licenses

# 6. Deploy sample multi-agent system
hexaeight-start deploy-multi-ai-agent-samples

# 7. Run the sample agents
python autogen_weather_agent.py     # Terminal 1
python crewai_weather_agent.py      # Terminal 2
python langchain_weather_agent.py   # Terminal 3

# 8. Setup portable child agents on other machines
hexaeight-start setup-portable-child-agent-environment child_config.json
```

## 🎯 Use Cases

### Enterprise AI Assistants
- **LLM Agents**: Understand user requests, coordinate responses
- **Tool Agents**: CRM data, financial systems, inventory management
- **User Agents**: Employee interfaces, customer portals

### Data Analysis Platforms  
- **LLM Agents**: Interpret analysis requests, generate insights
- **Tool Agents**: Database queries, API data feeds, visualization
- **User Agents**: Analyst interfaces, report generation

### Customer Service Automation
- **LLM Agents**: Natural language understanding, response generation  
- **Tool Agents**: Ticketing systems, knowledge bases, payment processing
- **User Agents**: Customer chat interfaces, agent dashboards

### IoT and Smart Systems
- **LLM Agents**: Command interpretation, system orchestration
- **Tool Agents**: Device control, sensor data, automation rules
- **User Agents**: Mobile apps, voice interfaces, dashboards

## 🔒 Security Features

- **🛡️ Secure Agent Identity**: Cryptographic agent authentication and authorization  
- **📡 Encrypted Communication**: All agent messages encrypted via HexaEight PubSub
- **🎯 Message Filtering**: Agents only process relevant messages based on type and format
- **🔍 Capability Isolation**: Tool agents expose only intended service capabilities
- **⚡ Automatic Locking**: Single-attempt message locking prevents processing conflicts

## 🛠️ Development Tools

```python
from hexaeight_mcp_client import *

# Check package info and framework availability
print_package_info()

# Setup development environment with example configs
setup_development_environment()

# Discover available configuration files
config_files = discover_config_files()
print("Available configs:", config_files)

# Validate agent types and configurations  
is_valid = validate_agent_type("parentLLM")
agent_info = get_agent_type_info("parentLLM")
```

## 🆘 Troubleshooting

### Common Issues

**Q: "Failed to encrypt LLM configuration"**  
A: Ensure you have a valid HexaEight agent loaded before creating the config protector.

**Q: "Tool agent not receiving messages"**  
A: Verify your service_formats match the message types being sent by LLM agents.

**Q: "LLM verification failed"**  
A: Make sure your agent_type is "parentLLM" or "childLLM" and provide appropriate verification responses.

**Q: "Connection to PubSub failed"**  
A: Check that your Client Application is properly configured and PubSub server is running.

## 🚀 Getting Started Checklist

- [ ] Deploy HexaEight Agentic IAM Server from [Azure Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/hexaeightopcprivatelimited1653195738074.hexaeight-agentic-iam)
- [ ] Create Client Application (get ClientID, Token Server URL, PubSub URL)
- [ ] Purchase HexaEight License from [store.hexaeight.com](https://store.hexaeight.com)
- [ ] Download "HexaEight Authenticator" mobile app
- [ ] Install hexaeight-mcp-client: `pip install hexaeight-mcp-client[all]`
- [ ] Run: `hexaeight-start show-concepts` (learn the concepts)
- [ ] Run: `hexaeight-start check-prerequisites`
- [ ] Run: `hexaeight-start license-activation`
- [ ] Create your first multi-agent system
- [ ] Build your first tool agent with actual business logic
- [ ] Test multi-agent coordination
- [ ] Deploy to production with real PubSub server

## 🔗 Links & Resources

- **🌐 Azure Marketplace**: [HexaEight Agentic IAM](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/hexaeightopcprivatelimited1653195738074.hexaeight-agentic-iam) - Deploy IAM Server
- **🏪 HexaEight Store**: [store.hexaeight.com](https://store.hexaeight.com) - Purchase licenses
- **📖 Documentation**: [GitHub Repository](https://github.com/HexaEightTeam/hexaeight-mcp-client)
- **🐛 Issues**: [GitHub Issues](https://github.com/HexaEightTeam/hexaeight-mcp-client/issues)
- **📦 HexaEight Agent**: [hexaeight-agent on PyPI](https://pypi.org/project/hexaeight-agent/)
- **📱 Mobile App**: Search "HexaEight Authenticator" in app stores

## 📄 License

MIT License - see LICENSE file for details.

---

**🌟 Ready to build intelligent multi-agent systems with enterprise-grade security?**

Start with `pip install hexaeight-mcp-client[all]` and learn the concepts with `hexaeight-start show-concepts`!
