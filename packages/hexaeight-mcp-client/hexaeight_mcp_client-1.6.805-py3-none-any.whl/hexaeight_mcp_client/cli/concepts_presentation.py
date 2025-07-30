"""
HexaEight Concepts Presentation CLI - Clean UI without border lines
"""

import os
import sys
import time
import shutil
from typing import List, Tuple
from .utils import confirm_action

class ConceptsPresentationCLI:
    """CLI for showing HexaEight concepts presentation with clean UI"""
    
    def __init__(self):
        self.width, self.height = self._get_terminal_size()
        self.content_width = min(80, self.width - 4)
        
    def run(self, args: List[str]) -> None:
        """Run concepts presentation with clean UI"""
        
        # Check modes
        interactive = len(args) == 0 or "--interactive" in args
        auto_advance = "--auto" in args
        
        # Welcome screen
        self._show_welcome_screen(interactive, auto_advance)
        
        if interactive and not auto_advance:
            input("\nPress Enter to start presentation...")
        else:
            time.sleep(2)
        
        slides = self._get_slides()
        
        for i, (title, content) in enumerate(slides, 1):
            self._show_slide(i, len(slides), title, content)
            
            if interactive and not auto_advance:
                print()
                controls = "Press Enter for next • 'q' to quit • 's' to skip • 'b' for back"
                print(self._center_text(controls))
                
                user_input = input().strip().lower()
                if user_input == 'q':
                    self._show_goodbye_screen()
                    return
                elif user_input == 's':
                    break
                elif user_input == 'b' and i > 1:
                    i -= 2
                    continue
            elif auto_advance:
                time.sleep(4)
        
        self._show_completion_screen()
    
    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal dimensions"""
        try:
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24
    
    def _clear_screen(self):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _center_text(self, text: str) -> str:
        """Center text horizontally"""
        return text.center(self.width)
    
    def _print_centered_content(self, content: str, indent: int = 0):
        """Print content centered with proper formatting"""
        lines = content.strip().split('\n')
        
        for line in lines:
            if line.strip():
                # Add indent for content
                spaced_line = (" " * indent) + line
                print(self._center_text(spaced_line))
            else:
                print()
    
    def _show_slide(self, slide_num: int, total_slides: int, title: str, content: str):
        """Show a single slide with clean formatting"""
        self._clear_screen()
        
        # Add vertical padding
        vertical_padding = max(3, (self.height - 15) // 2)
        for _ in range(vertical_padding):
            print()
        
        # Progress indicator
        progress_bar = self._create_progress_bar(slide_num, total_slides)
        print(self._center_text(progress_bar))
        print()
        print()
        
        # Title with decoration
        title_line = f"🚀 {title} 🚀"
        print(self._center_text(title_line))
        print(self._center_text("=" * len(title_line)))
        print()
        print()
        
        # Content with slight indent for readability
        self._print_centered_content(content, indent=2)
        
        # Bottom spacing and slide info
        print()
        print()
        slide_info = f"Slide {slide_num} of {total_slides}"
        print(self._center_text("─" * len(slide_info)))
        print(self._center_text(slide_info))
    
    def _create_progress_bar(self, current: int, total: int) -> str:
        """Create a visual progress bar"""
        bar_width = 30
        filled = int((current / total) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        percentage = int((current / total) * 100)
        return f"Progress: [{bar}] {percentage}%"
    
    def _show_welcome_screen(self, interactive: bool, auto_advance: bool):
        """Show welcome screen"""
        self._clear_screen()
        
        # Center vertically
        for _ in range(self.height // 3):
            print()
        
        print(self._center_text("🚀 HexaEight AI Agent Concepts 🚀"))
        print()
        print(self._center_text("Interactive Educational Presentation"))
        print()
        print(self._center_text("Transform Your Business with Enterprise AI Agents"))
        print()
        print(self._center_text("=" * 60))
        print()
        
        if interactive and not auto_advance:
            controls_text = "🎯 Interactive Mode: Navigate with Enter, 'q' to quit, 's' to skip, 'b' to go back"
        elif auto_advance:
            controls_text = "⚡ Auto-Advance Mode: Slides change automatically every 4 seconds"
        else:
            controls_text = "📖 Reading Mode: All slides will be displayed"
        
        print(self._center_text(controls_text))
    
    def _show_completion_screen(self):
        """Show completion screen"""
        self._clear_screen()
        
        for _ in range(self.height // 3):
            print()
        
        print(self._center_text("🎉 Concepts Presentation Complete! 🎉"))
        print()
        print(self._center_text("Ready to Build Your AI Agent Infrastructure?"))
        print()
        print()
        print(self._center_text("Next Steps:"))
        print(self._center_text("• hexaeight-start license-activation"))
        print(self._center_text("• hexaeight-start create-directory-linked-to-hexaeight-license my-project"))
        print(self._center_text("• hexaeight-start generate-parent-or-child-agent-licenses"))
        print()
        print()
        print(self._center_text("Press Enter to continue..."))
        input()
    
    def _show_goodbye_screen(self):
        """Show goodbye screen"""
        self._clear_screen()
        
        for _ in range(self.height // 2):
            print()
        
        print(self._center_text("👋 Thanks for Learning About HexaEight AI Agents! 👋"))
        print()
        print(self._center_text("Ready when you are: hexaeight-start license-activation"))
        print()
        
        time.sleep(2)
    
    def _get_slides(self) -> List[Tuple[str, str]]:
        """Get all presentation slides"""
        return [
            ("hexaeight-mcp-client Prerequisites", """
Before Using hexaeight-mcp-client for AI Agent Development

You've installed hexaeight-mcp-client Python package.
Before integrating MCP into AI agents, groundwork is required:

📋 Required Prerequisites :

1. 🏢 HexaEight-Agentic-IAM Server
   Deploy from Azure Marketplace to create Client Applications

2. 🔑 Client Application 
   ClientID, Token Server URL, PubSub URL from IAM Server

3. 💻 Machine License
   Install where your agents will run (NOT on IAM Server)
   Enables creation of agent configuration files

4. 📄 Agent Configuration Files
   Identity files for secure agent communication via PubSub
"""),
            
            ("HexaEight-Agentic-IAM Server Setup", """
Azure Marketplace Deployment

🏢 HexaEight-Agentic-IAM Server:
   Available on Azure Marketplace
   Central identity and application management server
   Allows creation of unlimited Client Applications

📋 What it provides:
• Client Application management interface
• Token Server URL generation
• PubSub URL provisioning
• Agent identity verification
• Cross-domain communication coordination

🔗 Each Client Application gets:
• Unique ClientID
• Token Server URL (for agent authentication)
• PubSub URL (for agent communication)

⚠️  Note: This is infrastructure setup, not where agents run
"""),
            
            ("Client Application Configuration", """
Getting Your Development Credentials

After deploying HexaEight-Agentic-IAM Server:

🔧 Create Client Application using Option 2 and use Option 6 to show:
• ClientID
• Token Server URL
• PubSub URL

📝 Required Environment Variables:
   HEXAEIGHT_CLIENT_ID="your_client_id"
   HEXAEIGHT_TOKENSERVER_URL="https://your-server:8443"
   HEXAEIGHT_PUBSUB_URL="https://your-server:2083/pubsub/client_id"

✅ Prerequisites Check:
   hexaeight-start check-prerequisites
   
   Verifies all required credentials are configured
"""),
            
            ("Machine License Requirements", """
License Installation for Agent Development

💻 Install License Where Agents Will Run:
• Local development machine
• Cloud servers (AWS, Azure, GCP)
• Edge devices (Raspberry Pi, IoT)
• NOT on the HexaEight-Agentic-IAM Server

🔑 License Purpose:
• Creates parent and child agent configuration files
• Enables secure agent identity generation
• Required for agent-to-agent communication setup

📦 How to purchase License:
   Visit https://store.hexaeight.com
   Note: Licences are based on number of CPUs
   1 CPU: $15 (Minimum 5 daysi License)

   If you plan to run Parent Agents permnantly you need to purchase monthly licenses

⚡ Activation:
   hexaeight-start license-activation
"""),
            
            ("Agent Configuration Files", """
Identity System for Secure Communication

📄 Configuration Files = Agent Identities:
• parent_config.json - Main agent (licensed machine)
• child_config.json - Distributed agents (any machine)

🔐 What configuration files contain:
• Agent Identities
• Internal Agent Identities
• Asymmetric Shared keysa for communication

🏗️  Agent Creation Process:
   hexaeight-start generate-parent-or-child-agent-licenses
   
   Creates configuration files with secure identities
   Child agents: Require 32+ character password
   Parent agents: No password required

✅ Result: Agents can securely communicate via PubSub system
"""),
            
            ("hexaeight-mcp-client Benefits", """
Technical Benefits for AI Agent Development

🔧 Framework Integration:
• AutoGen: Multi-agent conversations with secure identity
• CrewAI: Role-based agents with encrypted communication
• LangChain: Chain-based reasoning with secure messaging
• Generic: Custom framework support

⚡ Developer Benefits:
• Secure agent-to-agent communication out-of-the-box
• Built-in message encryption/decryption
• Cross-domain agent coordination
• No custom security implementation required
• No Https Certificates Required

🏗️  MCP Features:
• Tool sharing between agents
• Message locking for coordination
• Capability discovery across agent networks
• Task delegation and workflow management

🌍 Deployment Flexibility:
• Agents run anywhere with configuration file
• No network restrictions or VPN requirements
• Secure communication over public internet
"""),
            
            ("Agent Architecture", """
Parent and Child Agent System

👑 Parent Agent (Licensed Machine):
• Runs on machine with active license
• Creates child agent configuration files
• Manages cross-domain communication
• Coordinates multi-agent workflows
• Handles complex task delegation

👥 Child Agent (Any Machine):
• Uses configuration file created by parent
• No license required on deployment machine
• Permanent (works even after parent license expires)
• Handles specific tasks and tools
• Communicates via PubSub system

🔑 Key Technical Points:
• Parent agents: Can Establish Direct secure communication without PubSub Server
• Child agents: PubSub-based communication within applications
• Configuration files contain all necessary security credentials
• No ongoing license fees for child agents
"""),
            
            ("PubSub Communication System", """
Secure Agent Messaging Architecture

🔄 Communication Flow:

Parent-to-Parent: Direct Secure Channels
   Domain A ←→ Domain B (No PubSub required)

Parent-to-Child: PubSub Coordination
   Parent → PubSub Server → Child Agents

Child-to-Child: Application-Scoped PubSub
   Child A ←→ PubSub Server ←→ Child B (Same ClientID)

🔐 Security Features:
• End-to-end message encryption
• Agent identity validation
• Message locking for coordination
• Cross-domain secure channels

📡 PubSub Server:
• Message routing and delivery
• Agent presence management
• Message queuing and reliability
• Cross-application isolation
"""),
            
            ("Development Workflow", """
Step-by-Step Development Process

✅ Prerequisites Complete:
• HexaEight-Agentic-IAM Server deployed
• Client Application created (ClientID, URLs)
• Machine license activated
• Environment variables configured

🔧 Development Steps Post License Activation:

1. Create Workspace Directory:
   hexaeight-start create-directory-linked-to-hexaeight-license my-project

2. Generate Agent Configurations:
   hexaeight-start generate-parent-or-child-agent-licenses

3. Deploy Sample System:
   hexaeight-start deploy-multi-ai-agent-samples

4. Test Framework Integration:
   Run AutoGen, CrewAI, or LangChain samples with secure communication

5. Develop Custom Agents:
   Use hexaeight-mcp-client APIs in your Python code
"""),
            
            ("Framework Integration Guide", """
Using hexaeight-mcp-client in Your Code

🐍 Python Integration:

from hexaeight_mcp_client import quick_autogen_llm, quick_tool_agent

# Create LLM agent with secure identity
llm_agent = await quick_autogen_llm('parent_config.json')

# Create tool agent for specific services
tool_agent = await quick_tool_agent(
    'child_config.json', 
    ['weather_api', 'database_query']
)

🔧 Framework Support:
• AutoGen: Secure conversational agents
• CrewAI: Role-based coordination
• LangChain: Tool chaining with security
• Custom: Generic adapter for any framework

✅ What You Get:
• Automatic secure communication setup
• Built-in message encryption
• Agent coordination primitives
• No manual security implementation needed
"""),
            
            ("Portable Child Agent Environment", """
Deploy Child Agents Anywhere Without License

🌍 Portable Deployment Concept:
Once you have a child agent configuration file and password,
you can deploy it on ANY machine globally without needing
the original license or parent agent infrastructure.

📋 Prerequisites for Portable Setup:
• Child agent configuration file (child_config.json)
• 32+ character password used during child agent creation
• hexaeight-mcp-client Python package installed
• Environment variables (ClientID, PubSub URL, Token Server)

🚀 Deployment Command:
   hexaeight-start setup-portable-child-agent-environment child_config.json

✅ What This Enables:
• Cloud deployment (AWS, Azure, GCP, DigitalOcean)
• Edge computing (Raspberry Pi, IoT devices)
• Container deployment (Docker, Kubernetes)
• Distributed agent networks across global infrastructure

🔑 Key Benefits:
• No license file needed on deployment machine
• Child agents work forever (even after parent license expires)
• Complete independence from parent infrastructure
• Secure communication maintained via configuration file
""")
        ]

def show_hexaeight_concepts(interactive: bool = True, auto_advance: bool = False):
    """Show HexaEight concepts presentation with clean UI"""
    cli = ConceptsPresentationCLI()
    args = []
    if interactive:
        args.append("--interactive")
    if auto_advance:
        args.append("--auto")
    cli.run(args)
