"""
Enhanced Shared Components for HexaEight Competitive Weather Agents
- Added RESPONSE format: "RESPONSE from <agentname> {messageid} :"
- Response filtering to prevent processing responses from other agents
- Natural language response formatting
"""

import asyncio
import json
import aiohttp
import os
import time
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

# HexaEight imports
from hexaeight_mcp_client import (
    HexaEightAgentConfig,
    HexaEightLLMAgent,
    ToolResult,
    MCPConnectionError
)

# OpenAI imports
try:
    import openai
    from openai import AzureOpenAI, OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class WeatherConfig:
    """Weather API configuration"""
    api_key: str
    base_url: str = "http://api.weatherapi.com/v1"
    timeout: int = 30

@dataclass
class LLMConfig:
    """LLM configuration for capability evaluation"""
    provider: str  # "azure" or "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 150
    
    # Azure specific
    azure_endpoint: Optional[str] = None
    azure_api_key: Optional[str] = None
    azure_api_version: str = "2024-02-15-preview"
    
    # OpenAI specific
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None

class WeatherAPIClient:
    """Weather API client for weatherapi.com"""
    
    def __init__(self, config: WeatherConfig):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_weather(self, location: str, aqi: bool = False) -> Dict[str, Any]:
        """Get current weather for a location"""
        url = f"{self.config.base_url}/current.json"
        params = {
            "key": self.config.api_key,
            "q": location,
            "aqi": "yes" if aqi else "no"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Weather API error: {response.status} - {error_text}")
    
    async def get_forecast(self, location: str, days: int = 3, aqi: bool = False, alerts: bool = True) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        url = f"{self.config.base_url}/forecast.json"
        params = {
            "key": self.config.api_key,
            "q": location,
            "days": min(days, 10),
            "aqi": "yes" if aqi else "no",
            "alerts": "yes" if alerts else "no"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Weather API error: {response.status} - {error_text}")
    
    async def get_history(self, location: str, date: str) -> Dict[str, Any]:
        """Get historical weather for a location and date"""
        url = f"{self.config.base_url}/history.json"
        params = {
            "key": self.config.api_key,
            "q": location,
            "dt": date
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Weather API error: {response.status} - {error_text}")

class BaseWeatherAgent(ABC):
    """Enhanced base class with response format and filtering"""
    
    def __init__(self, framework_name: str, weather_config: WeatherConfig, llm_config: LLMConfig):
        self.framework_name = framework_name
        self.weather_config = weather_config
        self.llm_config = llm_config
        self.hexaeight_agent = None
        
        # Message queue for deduplication
        self.message_queue = {}  # {message_id: "processing"|"completed"|"failed"|"ignored"|"error"}
        
        # Get child agent configuration from environment
        self.child_password = os.getenv("HEXAEIGHT_CHILD_CONFIG_PASSSWORD")
        if not self.child_password:
            raise ValueError("HEXAEIGHT_CHILD_CONFIG_PASSSWORD environment variable required")
        
        self.config_file = os.getenv("HEXAEIGHT_CHILD_CONFIG_FILENAME", "child_config.json")
        
        # Setup framework-compatible environment variables
        self._setup_framework_env_vars()
        
        print(f"🚀 Initialized {framework_name} weather agent with enhanced response format")
        logger.info(f"Initialized {framework_name} weather agent with response format enhancements")
    
    def _setup_framework_env_vars(self):
        """Setup framework-specific environment variables for LLM access"""
        if self.llm_config.provider == "azure":
            os.environ["AZURE_OPENAI_ENDPOINT"] = self.llm_config.azure_endpoint or ""
            os.environ["AZURE_OPENAI_API_KEY"] = self.llm_config.azure_api_key or ""
            os.environ["AZURE_OPENAI_API_VERSION"] = self.llm_config.azure_api_version
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = self.llm_config.model
            os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = self.llm_config.model
            
        elif self.llm_config.provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.llm_config.openai_api_key or ""
            if self.llm_config.openai_base_url:
                os.environ["OPENAI_API_BASE"] = self.llm_config.openai_base_url
            os.environ["OPENAI_MODEL_NAME"] = self.llm_config.model
        
        if not os.getenv("OPENAI_MODEL_NAME"):
            os.environ["OPENAI_MODEL_NAME"] = self.llm_config.model
    
    async def initialize(self):
        """Initialize the HexaEight agent and framework-specific components"""
        
        print(f"🔧 Initializing {self.framework_name} agent...")
        
        # Initialize HexaEight LLM agent based on framework
        await self._initialize_hexaeight_agent()
        print(f"✅ HexaEight {self.framework_name} agent initialized")
        
        # Initialize framework-specific components
        await self._initialize_framework_components()
        print(f"✅ {self.framework_name} framework components initialized")
        
        # Start message listening
        await self._start_message_listener()
        print(f"✅ {self.framework_name} message listener started")
        
        print(f"🎯 {self.framework_name} agent ready and listening for messages")
        logger.info(f"{self.framework_name} weather agent fully initialized and listening")
    
    async def _initialize_hexaeight_agent(self):
        """Initialize HexaEight agent for the specific framework"""
        from hexaeight_mcp_client import quick_crewai_llm, quick_autogen_llm, quick_langchain_llm

        client_id = os.getenv("HEXAEIGHT_CLIENT_ID") or os.getenv("HEXA8_CLIENTID") or ""
        token_server_url = os.getenv("HEXAEIGHT_TOKENSERVER_URL") or os.getenv("HEXA8_TOKENSERVERURL") or ""

        if self.framework_name.lower() == "crewai":
            self.hexaeight_agent = await quick_crewai_llm(
                config_file=self.config_file,
                agent_type="childLLM",
                password=self.child_password,
                client_id=client_id,
                token_server_url=token_server_url
            ) 
        elif self.framework_name.lower() == "autogen":
            self.hexaeight_agent = await quick_autogen_llm(
                config_file=self.config_file,
                agent_type="childLLM", 
                password=self.child_password,
                client_id=client_id,
                token_server_url=token_server_url
            )
        elif self.framework_name.lower() == "langchain":
            self.hexaeight_agent = await quick_langchain_llm(
                config_file=self.config_file,
                agent_type="childLLM",
                password=self.child_password,
                client_id=client_id,
                token_server_url=token_server_url
            )
        else:
            raise ValueError(f"Unsupported framework: {self.framework_name}")
    
    @abstractmethod
    async def _initialize_framework_components(self):
        """Initialize framework-specific components (CrewAI agents, AutoGen, etc.)"""
        pass
    
    @abstractmethod
    async def _process_weather_request(self, message: str) -> str:
        """Process weather request using framework-specific logic"""
        pass
    
    def _is_response_message(self, content: str) -> bool:
        """Check if message is a response from another agent that should be ignored"""
        content_stripped = content.strip()
        
        # Check for response format: "RESPONSE from <agentname> {messageid} :"
        response_pattern = r'^RESPONSE from .+ \{.+\} :'
        
        if re.match(response_pattern, content_stripped):
            print(f"🔍 [{self.framework_name.upper()}] Detected response message - ignoring")
            return True
        
        # Also check for other common response indicators
        response_indicators = [
            "RESPONSE from",
            "Response from",
            "🤖 [AUTOGEN] Response:",
            "🤖 [CREWAI] Response:",
            "🤖 [LANGCHAIN] Response:"
        ]
        
        for indicator in response_indicators:
            if content_stripped.startswith(indicator):
                print(f"🔍 [{self.framework_name.upper()}] Detected response indicator '{indicator}' - ignoring")
                return True
        
        return False
    
    async def _start_message_listener(self):
        """Enhanced message listener with response filtering"""

        inner_agent = self.hexaeight_agent.hexaeight_agent

        # Check and replace existing handlers
        if hasattr(inner_agent, '_event_handlers'):
            existing_handlers = inner_agent._event_handlers.get('message_received', [])
            if existing_handlers:
                print(f"🔄 [{self.framework_name.upper()}] Found {len(existing_handlers)} existing message handlers - replacing with enhanced handler")
                inner_agent._event_handlers['message_received'] = []
                print(f"✅ [{self.framework_name.upper()}] Cleared existing message handlers")
            else:
                print(f"👂 [{self.framework_name.upper()}] No existing handlers found - registering enhanced handler")

        async def enhanced_message_handler(event):
            message_id = getattr(event, 'message_id', str(uuid.uuid4()))
            content = getattr(event, 'decrypted_content', '')
            sender = getattr(event, 'sender', 'unknown')

            # Check if already in queue
            if message_id in self.message_queue:
                print(f"⏭️  [{self.framework_name.upper()}] Message {message_id} already in queue - ignoring")
                return

            # ENHANCEMENT: Check if this is a response message
            if self._is_response_message(content):
                print(f"🔄 [{self.framework_name.upper()}] Ignoring response message from another agent")
                print(f"📝 Content preview: {content[:100]}...")
                self.message_queue[message_id] = "ignored_response"
                return

            # Add to queue immediately
            self.message_queue[message_id] = "processing"

            print(f"\n🔍 [{self.framework_name.upper()}] Message Received (ID: {message_id})")
            print(f"📝 Content: {content}")
            print(f"🔄 Reference: {self.framework_name}-msg_{int(time.time())}")
            print(f"🕐 Received at: {datetime.now().strftime('%H:%M:%S')}")

            try:
                # Check if we can handle this message
                if self._can_handle_message(content):
                    print(f"🎯 Framework Targeting: No specific framework targeting - general request")
                    print(f"🌤️  Weather Relevance: {self._get_weather_relevance(content)}")
                    print(f"📊 Decision: ✅ HANDLING - General weather request, no competition detected")
                    print(f"─" * 60)

                    # Try to lock and process with message_id
                    success = await self._try_lock_and_process(message_id, content, event)

                    if success:
                        self.message_queue[message_id] = "completed"
                        print(f"✅ [{self.framework_name.upper()}] Message {message_id} completed successfully")
                    else:
                        self.message_queue[message_id] = "failed"
                        print(f"🔒 [{self.framework_name.upper()}] Message {message_id} failed (another agent got it)")
                else:
                    self.message_queue[message_id] = "ignored"
                    print(f"🎯 Framework Targeting: Not weather-related")
                    print(f"📊 Decision: 🚫 IGNORING - Not weather-related and not targeted to us")
                    print(f"─" * 60)
                    print(f"📤 [{self.framework_name.upper()}] Message {message_id} ignored (not for us)")

            except Exception as e:
                self.message_queue[message_id] = "error"
                print(f"❌ [{self.framework_name.upper()}] Error processing {message_id}: {e}")
                logger.error(f"{self.framework_name}: Error handling message: {e}")

        # Register the enhanced handler
        inner_agent.register_event_handler('message_received', enhanced_message_handler)

        # Verify registration
        if hasattr(inner_agent, '_event_handlers'):
            handler_count = len(inner_agent._event_handlers.get('message_received', []))
            print(f"✅ [{self.framework_name.upper()}] Enhanced message handler registered ({handler_count} total handlers)")

        print(f"👂 [{self.framework_name.upper()}] Enhanced message handler active - ready to receive messages")
        logger.info(f"{self.framework_name}: Enhanced message handler registered and active")

    def _can_handle_message(self, content: str) -> bool:
        """Enhanced check: is this a weather message we should handle?"""
        content_lower = content.lower().strip()
        
        if not content_lower:
            return False
        
        # Skip if it's a response message (double-check)
        if self._is_response_message(content):
            return False
        
        # Weather keywords
        weather_words = [
            "weather", "temperature", "forecast", "rain", "raining", "sunny", "cloudy", 
            "hot", "cold", "humidity", "wind", "storm", "snow", "climate",
            "degrees", "celsius", "fahrenheit", "precipitation", "umbrella"
        ]
        
        # Location indicators
        location_words = [" in ", " for ", " at ", " of "]
        
        # Common locations
        cities = [
            "bangalore", "london", "paris", "tokyo", "new york", "delhi", 
            "mumbai", "chennai", "hyderabad", "pune", "kolkata", "ahmedabad"
        ]
        
        has_weather = any(word in content_lower for word in weather_words)
        has_location_indicator = any(word in content_lower for word in location_words)
        has_city = any(city in content_lower for city in cities)
        
        return has_weather or has_location_indicator or has_city
    
    def _get_weather_relevance(self, content: str) -> str:
        """Get weather relevance description"""
        content_lower = content.lower()
        
        weather_words = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"]
        location_words = [" in ", " for ", " at "]
        cities = ["bangalore", "london", "paris", "tokyo", "chennai"]
        
        weather_found = [w for w in weather_words if w in content_lower][:2]
        location_found = [w.strip() for w in location_words if w in content_lower][:2]
        city_found = [c for c in cities if c in content_lower][:2]
        
        if weather_found and (location_found or city_found):
            return f"Clear weather request (keywords: {weather_found}, locations: {location_found or city_found})"
        elif weather_found:
            return f"Weather-related (keywords: {weather_found})"
        elif location_found or city_found:
            return f"Location mentioned (locations: {location_found or city_found})"
        else:
            return "General message"

    async def _try_lock_and_process(self, message_id: str, content: str, event) -> bool:
        """Enhanced lock and process with message_id passing"""
        
        print(f"🔐 [{self.framework_name.upper()}] Attempting to acquire message lock...")
        
        try:
            pubsub_url = getattr(self.hexaeight_agent, 'pubsub_url', 'http://localhost:5000')
            inner_agent = self.hexaeight_agent.hexaeight_agent
            
            # Debug information
            try:
                agent_name = await inner_agent.get_agent_name()
                print(f"🔍 DEBUG: My agent name: {agent_name}")
            except Exception as e:
                print(f"🔍 DEBUG: Error getting agent name: {e}")
                
            try:
                internal_id = inner_agent.get_internal_identity()
                print(f"🔍 DEBUG: My internal ID: {internal_id}")
            except Exception as e:
                print(f"🔍 DEBUG: Error getting internal ID: {e}")
                
            try:
                is_connected = inner_agent.is_connected_to_pubsub()
                print(f"🔍 DEBUG: Connected to PubSub: {is_connected}")
            except Exception as e:
                print(f"🔍 DEBUG: Error checking connection: {e}")
            
            print(f"🔍 DEBUG: PubSub URL: {pubsub_url}")
            print(f"🔍 DEBUG: Message ID: {message_id}")
            
            # First lock attempt
            print(f"🔐 [{self.framework_name.upper()}] Lock attempt #1 for message {message_id}")
            
            try:
                lock_result = await inner_agent.lock_message(pubsub_url, message_id)
                print(f"🔍 DEBUG: Lock attempt #1 raw result: {lock_result}")
                
                if lock_result:
                    print(f"✅ [{self.framework_name.upper()}] Lock acquired on attempt #1!")
                    await self._process_locked_message(message_id, content, event, pubsub_url)
                    return True
                else:
                    print(f"🔒 [{self.framework_name.upper()}] Lock attempt #1 failed - lock_result was: {lock_result}")
            except Exception as e:
                print(f"❌ [{self.framework_name.upper()}] Lock attempt #1 exception: {e}")
            
            # Wait and retry
            print(f"⏳ [{self.framework_name.upper()}] Waiting 1 second before retry...")
            await asyncio.sleep(1.0)
            
            print(f"🔐 [{self.framework_name.upper()}] Lock attempt #2 for message {message_id}")
            
            try:
                lock_result = await inner_agent.lock_message(pubsub_url, message_id)
                print(f"🔍 DEBUG: Lock attempt #2 raw result: {lock_result}")
                
                if lock_result:
                    print(f"✅ [{self.framework_name.upper()}] Lock acquired on attempt #2!")
                    await self._process_locked_message(message_id, content, event, pubsub_url)
                    return True
                else:
                    print(f"🔒 [{self.framework_name.upper()}] Lock attempt #2 failed")
                    print(f"🚫 [{self.framework_name.upper()}] Failed to acquire lock after 2 attempts")
                    return False
            except Exception as e:
                print(f"❌ [{self.framework_name.upper()}] Lock attempt #2 exception: {e}")
                return False
                
        except Exception as e:
            print(f"❌ [{self.framework_name.upper()}] Lock/process error: {e}")
            return False 

    async def _process_locked_message(self, message_id: str, content: str, event, pubsub_url: str):
        """Enhanced message processing with natural language response"""
        
        try:
            print(f"⚡ [{self.framework_name.upper()}] Processing locked message after 1 second delay...")
            await asyncio.sleep(1.0)
            
            # Process the weather request
            print(f"🌤️  [{self.framework_name.upper()}] Generating weather response...")
            response = await self._process_weather_request(content)
            
            # ENHANCEMENT: Ensure response is in natural language format
            natural_response = await self._format_natural_language_response(response, content)
            
            # Send enhanced response back
            print(f"📤 [{self.framework_name.upper()}] Sending enhanced response back to {getattr(event, 'sender', 'unknown')}")
            await self._send_enhanced_response(event, natural_response, message_id)
            
            print(f"✅ [{self.framework_name.upper()}] Successfully completed enhanced message processing!")
            
        except Exception as e:
            print(f"❌ [{self.framework_name.upper()}] Error processing locked message: {e}")
            logger.error(f"{self.framework_name}: Error processing locked message: {e}")
        finally:
            # Always release the lock
            try:
                await self.hexaeight_agent.hexaeight_agent.release_lock(pubsub_url, message_id)
                print(f"🔓 [{self.framework_name.upper()}] Lock released for message {message_id}")
            except Exception as e:
                print(f"❌ [{self.framework_name.upper()}] Error releasing lock: {e}")
                logger.error(f"{self.framework_name}: Error releasing lock: {e}")
    
    async def _format_natural_language_response(self, response: str, original_message: str) -> str:
        """Format response in natural language rather than just tool output"""
        
        try:
            # If response already looks like natural language (has conversational elements), return as-is
            conversational_indicators = [
                "hello", "hi there", "i'm", "i am", "let me", "here's", "here is",
                "the weather", "currently", "right now", "as of", "looking at"
            ]
            
            response_lower = response.lower()
            if any(indicator in response_lower for indicator in conversational_indicators):
                print(f"✅ [{self.framework_name.upper()}] Response already in natural language format")
                return response
            
            # If response looks like raw tool output, enhance it
            if response.startswith("🌤️") or response.startswith("📊") or "Weather for" in response:
                print(f"🔄 [{self.framework_name.upper()}] Enhancing raw weather data with natural language")
                
                # Extract location if possible
                location = self._extract_location_from_message(original_message)
                
                enhanced_response = f"Hello! I've got the weather information you requested.\n\n"
                
                if "current weather" in original_message.lower() or "weather in" in original_message.lower():
                    enhanced_response += f"Here's the current weather for {location}:\n\n{response}"
                elif "forecast" in original_message.lower():
                    enhanced_response += f"Here's the weather forecast for {location}:\n\n{response}"
                else:
                    enhanced_response += f"Here's the weather information for {location}:\n\n{response}"
                
                enhanced_response += f"\n\nIs there anything else about the weather you'd like to know?"
                
                return enhanced_response
            
            # For other responses, add a conversational wrapper
            return f"Hello! {response}\n\nFeel free to ask me about weather conditions for any location!"
            
        except Exception as e:
            print(f"⚠️  [{self.framework_name.upper()}] Error formatting natural language response: {e}")
            return response  # Return original if enhancement fails
    
    def _extract_location_from_message(self, message: str) -> str:
        """Extract location from user message for natural language responses"""
        try:
            # Common patterns for location extraction
            patterns = [
                r'\b(?:in|for|at)\s+([A-Za-z\s,]+?)(?:\?|$|,)',
                r'\b(?:weather)\s+(?:in|for|at)\s+([A-Za-z\s,]+?)(?:\?|$|,)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\?*$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    location = match.group(1).strip()
                    if len(location) > 2 and len(location) < 50:
                        return location
            
            return "the requested location"
            
        except Exception:
            return "the requested location"
    
    async def _send_enhanced_response(self, event, response: str, message_id: str):
        """ENHANCEMENT: Send response with proper format"""
        try:
            sender = getattr(event, 'sender', 'unknown')
            pubsub_url = getattr(self.hexaeight_agent, 'pubsub_url', 'http://localhost:5000')
            
            # Get agent name for the response format
            try:
                agent_name = await self.hexaeight_agent.hexaeight_agent.get_agent_name()
            except Exception as e:
                print(f"⚠️  Could not get agent name: {e}")
                agent_name = f"{self.framework_name}_Agent"
            
            # ENHANCEMENT: Format response with required format
            formatted_response = f"RESPONSE from {agent_name} {{{message_id}}} : {response}"
            
            await self.hexaeight_agent.hexaeight_agent.publish_to_agent(
                pubsub_url,
                sender,
                formatted_response
            )
            
            print(f"✅ [{self.framework_name.upper()}] Enhanced response successfully sent to {sender}")
            print(f"📝 Response format: RESPONSE from {agent_name} {{{message_id}}} : [content...]")
            logger.info(f"{self.framework_name}: Enhanced response sent to {sender} with message ID {message_id}")
            
        except Exception as e:
            print(f"❌ [{self.framework_name.upper()}] Error sending enhanced response: {e}")
            logger.error(f"{self.framework_name}: Error sending enhanced response: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get enhanced queue statistics"""
        stats = {
            "total_messages": len(self.message_queue),
            "by_status": {}
        }
        
        for status in ["processing", "completed", "failed", "ignored", "ignored_response", "error"]:
            count = sum(1 for s in self.message_queue.values() if s == status)
            stats["by_status"][status] = count
        
        return stats

# Configuration helper functions (unchanged)
def get_llm_config_from_env() -> LLMConfig:
    """Get LLM configuration from environment variables"""
    
    # Check for Azure OpenAI first
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_KEY")
    
    if azure_endpoint and azure_api_key:
        return LLMConfig(
            provider="azure",
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_api_key,
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
    
    # Fall back to OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return LLMConfig(
            provider="openai",
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            openai_api_key=openai_api_key,
            openai_base_url=os.getenv("OPENAI_BASE_URL")
        )
    
    raise ValueError("No LLM configuration found. Set AZURE_OPENAI_* or OPENAI_API_KEY environment variables")

def get_weather_config_from_env() -> WeatherConfig:
    """Get weather configuration from environment variables"""
    weather_api_key = os.getenv("WEATHER_API_KEY")
    if not weather_api_key:
        raise ValueError("WEATHER_API_KEY environment variable required")
    
    return WeatherConfig(
        api_key=weather_api_key,
        base_url=os.getenv("WEATHER_API_BASE_URL", "http://api.weatherapi.com/v1")
    )

# Weather data formatting utilities (unchanged)
class WeatherFormatter:
    """Utility class for formatting weather data"""
    
    @staticmethod
    def format_current_weather(data: Dict[str, Any]) -> str:
        """Format current weather data for human readability"""
        current = data.get("current", {})
        location = data.get("location", {})
        
        formatted = f"""🌤️ Current Weather for {location.get('name', 'Unknown')}, {location.get('country', 'Unknown')}
📍 Local Time: {location.get('localtime', 'Unknown')}

🌡️ Temperature: {current.get('temp_c', 'N/A')}°C ({current.get('temp_f', 'N/A')}°F)
🤔 Feels Like: {current.get('feelslike_c', 'N/A')}°C ({current.get('feelslike_f', 'N/A')}°F)
☁️ Condition: {current.get('condition', {}).get('text', 'Unknown')}
💧 Humidity: {current.get('humidity', 'N/A')}%
💨 Wind: {current.get('wind_kph', 'N/A')} km/h {current.get('wind_dir', '')}
🌡️ Pressure: {current.get('pressure_mb', 'N/A')} mb
👁️ Visibility: {current.get('vis_km', 'N/A')} km
☀️ UV Index: {current.get('uv', 'N/A')}"""
        
        if 'air_quality' in current:
            aq = current['air_quality']
            formatted += f"\n\n🏭 Air Quality:\n"
            formatted += f"   CO: {aq.get('co', 'N/A')} μg/m³\n"
            formatted += f"   NO2: {aq.get('no2', 'N/A')} μg/m³\n"
            formatted += f"   PM2.5: {aq.get('pm2_5', 'N/A')} μg/m³"
        
        return formatted.strip()
    
    @staticmethod
    def format_forecast(data: Dict[str, Any]) -> str:
        """Format forecast data for human readability"""
        location = data.get("location", {})
        forecast_days = data.get("forecast", {}).get("forecastday", [])
        
        formatted = f"📊 Weather Forecast for {location.get('name', 'Unknown')}, {location.get('country', 'Unknown')}\n\n"
        
        for i, day in enumerate(forecast_days):
            date = day.get("date", "Unknown")
            day_data = day.get("day", {})
            
            day_label = "Today" if i == 0 else "Tomorrow" if i == 1 else f"Day {i+1}"
            
            formatted += f"📅 {day_label} ({date})\n"
            formatted += f"   🔺 High: {day_data.get('maxtemp_c', 'N/A')}°C ({day_data.get('maxtemp_f', 'N/A')}°F)\n"
            formatted += f"   🔻 Low: {day_data.get('mintemp_c', 'N/A')}°C ({day_data.get('mintemp_f', 'N/A')}°F)\n"
            formatted += f"   ☁️ Condition: {day_data.get('condition', {}).get('text', 'Unknown')}\n"
            formatted += f"   🌧️ Rain Chance: {day_data.get('daily_chance_of_rain', 'N/A')}%\n\n"
        
        return formatted.strip()
    
    @staticmethod
    def format_history(data: Dict[str, Any]) -> str:
        """Format historical weather data"""
        location = data.get("location", {})
        forecast_day = data.get("forecast", {}).get("forecastday", [{}])[0]
        date = forecast_day.get("date", "Unknown")
        day_data = forecast_day.get("day", {})
        
        formatted = f"""📊 Historical Weather for {location.get('name', 'Unknown')}, {location.get('country', 'Unknown')}
📅 Date: {date}

🔺 High: {day_data.get('maxtemp_c', 'N/A')}°C ({day_data.get('maxtemp_f', 'N/A')}°F)
🔻 Low: {day_data.get('mintemp_c', 'N/A')}°C ({day_data.get('mintemp_f', 'N/A')}°F)
📊 Average: {day_data.get('avgtemp_c', 'N/A')}°C ({day_data.get('avgtemp_f', 'N/A')}°F)
☁️ Condition: {day_data.get('condition', {}).get('text', 'Unknown')}
🌧️ Precipitation: {day_data.get('totalprecip_mm', 'N/A')} mm"""
        
        return formatted.strip()
