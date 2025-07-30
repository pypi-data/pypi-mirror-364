"""
Enhanced AutoGen Weather Agent with Framework-Specific Targeting
"""

import asyncio
import logging
import os
import re
import json
from typing import Dict, Any, Optional, List

# Import enhanced shared components
from shared_components import (
    BaseWeatherAgent, 
    WeatherAPIClient,
    WeatherFormatter,
    get_llm_config_from_env,
    get_weather_config_from_env,
    OPENAI_AVAILABLE
)

# AutoGen imports - try different strategies
AUTOGEN_AVAILABLE = False
AUTOGEN_VERSION = None

# Strategy 1: Try pyautogen (older API under new installation)
try:
    import pyautogen as autogen
    from pyautogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = "pyautogen"
    print("✅ Using pyautogen compatibility layer")
except ImportError:
    # Strategy 2: Try newer autogen_agentchat API
    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.base import ChatAgent
        from autogen_agentchat.messages import TextMessage
        AUTOGEN_AVAILABLE = True
        AUTOGEN_VERSION = "new"
        print("✅ Using newer autogen_agentchat API")
    except ImportError:
        # Strategy 3: Try basic autogen_core approach
        try:
            import autogen_core
            from autogen_core import Agent
            AUTOGEN_AVAILABLE = True
            AUTOGEN_VERSION = "core"
            print("✅ Using autogen_core basic API")
        except ImportError:
            AUTOGEN_AVAILABLE = False
            print("❌ No compatible AutoGen version found")

logger = logging.getLogger(__name__)

class AutoGenWeatherAgent(BaseWeatherAgent):
    """Enhanced AutoGen implementation with framework targeting"""
    
    def __init__(self, weather_config, llm_config):
        super().__init__("AutoGen", weather_config, llm_config)
        self.weather_specialist = None
        self.llm_config_dict = None
    
    def _is_framework_targeted(self, content: str) -> bool:
        """Check if message specifically targets this framework"""
        content_lower = content.lower().strip()
        
        print(f"🔍 [AUTOGEN] Checking framework targeting for: '{content_lower}'")
        
        # AutoGen targeting keywords - more comprehensive
        autogen_keywords = [
            "autogen agent", "autogen", "auto gen", "auto-gen",
            "can the autogen", "autogen respond", "autogen agent respond",
            "use autogen", "autogen framework", "autogen weather",
            "can autogen", "autogen tell", "autogen provide"
        ]
        
        # Other framework keywords (should make us ignore)
        other_framework_keywords = [
            "crewai agent", "crewai", "crew ai", "crew-ai", 
            "can the crewai", "crewai respond", "crewai agent respond",
            "use crewai", "crewai framework", "crewai weather",
            "can crewai", "crewai tell", "crewai provide",
            "langchain agent", "langchain", "lang chain",
            "openai agent", "chatgpt agent"
        ]
        
        # Check if specifically asking for AutoGen
        for keyword in autogen_keywords:
            if keyword in content_lower:
                print(f"🎯 [AUTOGEN] Found AutoGen targeting keyword: '{keyword}'")
                return True
        
        # Check if asking for other frameworks
        for keyword in other_framework_keywords:
            if keyword in content_lower:
                print(f"🚫 [AUTOGEN] Found other framework keyword: '{keyword}' - will ignore")
                return False
        
        print(f"🌤️  [AUTOGEN] No specific framework targeting detected")
        return None
    
    def _can_handle_message(self, content: str) -> bool:
        """Enhanced check with framework targeting"""
        content_lower = content.lower().strip()
        
        print(f"🔍 [AUTOGEN] Checking if can handle message: '{content}'")
        
        if not content_lower:
            print(f"🚫 [AUTOGEN] Empty message - ignoring")
            return False
        
        # Skip if it's a response message
        if self._is_response_message(content):
            print(f"🔄 [AUTOGEN] Response message detected - ignoring")
            return False
        
        # Check framework targeting first
        framework_check = self._is_framework_targeted(content)
        if framework_check is True:
            # Specifically targeted to AutoGen
            print(f"✅ [AUTOGEN] Framework targeting: Message specifically requests AutoGen - WILL HANDLE")
            return True
        elif framework_check is False:
            # Targeted to other framework
            print(f"🚫 [AUTOGEN] Framework targeting: Message requests other framework - WILL IGNORE")
            return False
        
        # No specific targeting - check if it's weather-related
        weather_words = [
            "weather", "temperature", "forecast", "rain", "raining", "sunny", "cloudy", 
            "hot", "cold", "humidity", "wind", "storm", "snow", "climate",
            "degrees", "celsius", "fahrenheit", "precipitation", "umbrella"
        ]
        
        location_words = [" in ", " for ", " at ", " of ", " or "]
        
        cities = [
            "bangalore", "london", "paris", "tokyo", "new york", "delhi", 
            "mumbai", "chennai", "hyderabad", "pune", "kolkata", "ahmedabad"
        ]
        
        has_weather = any(word in content_lower for word in weather_words)
        has_location_indicator = any(word in content_lower for word in location_words)
        has_city = any(city in content_lower for city in cities)
        
        is_weather_related = has_weather or has_location_indicator or has_city
        
        if is_weather_related:
            print(f"🌤️  [AUTOGEN] Framework targeting: No specific targeting - normal weather competition - WILL COMPETE")
        else:
            print(f"🚫 [AUTOGEN] Not weather-related - WILL IGNORE")
        
        return is_weather_related
    
    def _sanitize_string_for_hexaeight(self, text: str) -> str:
        """Sanitize string to prevent HexaEight string manipulation errors"""
        if not text:
            return ""
        
        try:
            sanitized = text.replace('\u00a0', ' ')
            sanitized = re.sub(r'[\u2000-\u200f\u2028-\u202f]', ' ', sanitized)
            sanitized = re.sub(r'[\u00ad\ufeff]', '', sanitized)
            
            lines = sanitized.split('\n')
            safe_lines = []
            for line in lines:
                if len(line) > 500:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) > 500:
                            if current_line:
                                safe_lines.append(current_line.strip())
                                current_line = word
                            else:
                                safe_lines.append(word[:497] + "...")
                                current_line = ""
                        else:
                            current_line += (" " + word) if current_line else word
                    if current_line:
                        safe_lines.append(current_line.strip())
                else:
                    safe_lines.append(line)
            
            sanitized = '\n'.join(safe_lines)
            
            if len(sanitized) > 2000:
                sanitized = sanitized[:1997] + "..."
            
            sanitized = sanitized.encode('utf-8', errors='replace').decode('utf-8')
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing string: {e}")
            return f"AutoGen Weather Agent: Data processing error occurred."
    
    def _get_model_temperature(self):
        """Get appropriate temperature for the model"""
        model_name = self.llm_config.model.lower()
        if "o4" in model_name or "o1" in model_name:
            print(f"⚠️  Model {self.llm_config.model} only supports default temperature (1.0)")
            return 1.0
        return 0.1
    
    def _setup_llm_config(self):
        """Setup LLM configuration for AutoGen"""
        temperature = self._get_model_temperature()
        
        if self.llm_config.provider == "azure":
            self.llm_config_dict = {
                "config_list": [{
                    "model": self.llm_config.model,
                    "api_type": "azure",
                    "base_url": self.llm_config.azure_endpoint,
                    "api_key": self.llm_config.azure_api_key,
                    "api_version": self.llm_config.azure_api_version,
                }],
                "temperature": temperature,
                "timeout": 60,
                "cache_seed": None
            }
        else:
            self.llm_config_dict = {
                "config_list": [{
                    "model": self.llm_config.model,
                    "api_key": self.llm_config.openai_api_key,
                    "base_url": self.llm_config.openai_base_url,
                }],
                "temperature": temperature,
                "timeout": 60,
                "cache_seed": None
            }
        
        print(f"✅ AutoGen LLM config created with temperature: {temperature}")
    
    async def _test_llm_direct(self):
        """Test LLM configuration directly with OpenAI client"""
        print("🔍 Testing LLM configuration directly...")
        
        try:
            if self.llm_config.provider == "azure":
                from openai import AzureOpenAI
                client = AzureOpenAI(
                    api_key=self.llm_config.azure_api_key,
                    api_version=self.llm_config.azure_api_version,
                    azure_endpoint=self.llm_config.azure_endpoint
                )
                
                response = client.chat.completions.create(
                    model=self.llm_config.model,
                    messages=[{"role": "user", "content": "Say 'Hello from AutoGen'"}],
                    temperature=self._get_model_temperature(),
                    max_tokens=50
                )
                
                result = response.choices[0].message.content
                print(f"✅ Direct LLM test successful: {result}")
                return True
                
            else:
                from openai import OpenAI
                client = OpenAI(
                    api_key=self.llm_config.openai_api_key,
                    base_url=self.llm_config.openai_base_url
                )
                
                response = client.chat.completions.create(
                    model=self.llm_config.model,
                    messages=[{"role": "user", "content": "Say 'Hello from AutoGen'"}],
                    temperature=self._get_model_temperature(),
                    max_tokens=50
                )
                
                result = response.choices[0].message.content
                print(f"✅ Direct LLM test successful: {result}")
                return True
                
        except Exception as e:
            print(f"❌ Direct LLM test failed: {e}")
            return False

    async def _initialize_framework_components(self):
        """Initialize AutoGen components"""
        print(f"🔍 INIT DEBUG: _initialize_framework_components called")

        if not AUTOGEN_AVAILABLE:
            raise ImportError("AutoGen not available. Install with: pip install pyautogen")

        print(f"🤖 Initializing AutoGen weather system (version: {AUTOGEN_VERSION})...")
    
        llm_test_passed = await self._test_llm_direct()
        if not llm_test_passed:
            raise Exception("Direct LLM test failed")
        
        if AUTOGEN_VERSION == "pyautogen":
            await self._initialize_pyautogen()
        elif AUTOGEN_VERSION == "new":
            await self._initialize_new_autogen()
        elif AUTOGEN_VERSION == "core":
            await self._initialize_core_autogen()
        else:
            raise Exception(f"Unsupported AutoGen version: {AUTOGEN_VERSION}")
        
        print("✅ AutoGen framework components with targeting initialized")
        logger.info("✅ AutoGen framework components with targeting initialized")
    
    async def _initialize_pyautogen(self):
        """Initialize using pyautogen"""
        print("🔧 Using pyautogen API...")
        
        self._setup_llm_config()
        
        self.weather_specialist = ConversableAgent(
            name="WeatherSpecialist",
            system_message="""You are a friendly, conversational weather specialist AI powered by AutoGen.

Your role is to:
- Provide helpful, accurate weather information for any location worldwide
- Respond in a natural, conversational manner
- Always be friendly and approachable
- Use clear, easy-to-understand language

When introducing yourself:
- Be warm and welcoming
- Explain that you're an AutoGen-powered weather specialist
- Mention your key capabilities briefly
- Always offer to help with weather questions

When providing weather data:
- Start with a friendly greeting or acknowledgment
- Present the information clearly and conversationally
- End with an offer to help with additional questions

You have access to comprehensive weather tools including:
- get_current_weather: Current conditions, temperature, humidity, wind, pressure, UV index, air quality
- get_weather_forecast: 1-10 day forecasts with daily highs/lows, conditions, rain chances
- get_historical_weather: Historical weather data for specific dates (within 7 days)
- search_locations: Search for location names and coordinates
- get_weather_alerts: Active weather warnings and alerts
- get_astronomy_data: Sunrise, sunset, moon phases, astronomical data

Choose the appropriate tool based on the user's request:
- For current weather: Use get_current_weather
- For forecasts/next day/tomorrow: Use get_weather_forecast
- For past weather: Use get_historical_weather
- For unclear locations: Use search_locations
- For weather alerts: Use get_weather_alerts
- For sunrise/sunset/moon data: Use get_astronomy_data

Keep responses conversational and natural - avoid overly technical language.""",
            llm_config=self.llm_config_dict,
            human_input_mode="NEVER",
            code_execution_config=False,
            max_consecutive_auto_reply=1
        )
        
        self._register_weather_functions_pyautogen()
        print("✅ pyautogen components initialized")
    
    async def _initialize_new_autogen(self):
        """Initialize using newer autogen_agentchat API"""
        print("🔧 Using newer autogen_agentchat API...")
        self.weather_specialist = "new_agent"
        print("✅ New AutoGen components initialized (simplified)")
    
    async def _initialize_core_autogen(self):
        """Initialize using autogen_core API"""
        print("🔧 Using autogen_core API...")
        self.weather_specialist = "core_agent"
        print("✅ Core AutoGen components initialized (simplified)")
    
    def _register_weather_functions_pyautogen(self):
        """Register ALL weather functions with pyautogen"""
        
        def get_current_weather(location: str, include_air_quality: bool = False) -> str:
            """Get current weather conditions for a specified location."""
            try:
                print(f"🌤️  AutoGen Tool: Getting current weather for: {location}")
                
                location = str(location).strip().strip('"').strip("'")
                if not location or len(location) < 2:
                    location = "London"
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._get_current_weather_sync(location, include_air_quality))
                            result = future.result(timeout=30)
                    else:
                        result = loop.run_until_complete(self._get_current_weather_async(location, include_air_quality))
                except RuntimeError:
                    import threading
                    import concurrent.futures
                    
                    def run_in_thread():
                        return asyncio.run(self._get_current_weather_async(location, include_air_quality))
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)
                
                print(f"✅ AutoGen Tool: Current weather data retrieved")
                return self._sanitize_string_for_hexaeight(result)
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting the current weather for {location}. Please try again or ask about a different location."
                print(f"❌ AutoGen Tool Error: {error_msg}")
                return self._sanitize_string_for_hexaeight(error_msg)
        
        def get_weather_forecast(location: str, days: int = 3) -> str:
            """Get weather forecast for a specified location and number of days (1-10 days)."""
            try:
                print(f"📊 AutoGen Tool: Getting {days}-day forecast for: {location}")
                
                location = str(location).strip().strip('"').strip("'")
                if not location or len(location) < 2:
                    location = "London"
                
                days = int(days) if str(days).isdigit() else 3
                days = max(1, min(days, 10))  # Clamp between 1-10 days
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._get_forecast_sync(location, days))
                            result = future.result(timeout=30)
                    else:
                        result = loop.run_until_complete(self._get_forecast_async(location, days))
                except RuntimeError:
                    import threading
                    import concurrent.futures
                    
                    def run_in_thread():
                        return asyncio.run(self._get_forecast_async(location, days))
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)
                
                print(f"✅ AutoGen Tool: {days}-day forecast data retrieved")
                return self._sanitize_string_for_hexaeight(result)
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting the forecast for {location}. Please try again or ask about a different location."
                print(f"❌ AutoGen Tool Error: {error_msg}")
                return self._sanitize_string_for_hexaeight(error_msg)
        
        def get_historical_weather(location: str, date: str) -> str:
            """Get historical weather for a specified location and date (YYYY-MM-DD format, within last 7 days)."""
            try:
                print(f"📅 AutoGen Tool: Getting historical weather for {location} on {date}")
                
                location = str(location).strip().strip('"').strip("'")
                if not location or len(location) < 2:
                    location = "London"
                
                date = str(date).strip()
                if not re.match(r'\d{4}-\d{2}-\d{2}', date):
                    from datetime import datetime, timedelta
                    yesterday = datetime.now() - timedelta(days=1)
                    date = yesterday.strftime('%Y-%m-%d')
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._get_historical_weather_sync(location, date))
                            result = future.result(timeout=30)
                    else:
                        result = loop.run_until_complete(self._get_historical_weather_async(location, date))
                except RuntimeError:
                    import threading
                    import concurrent.futures
                    
                    def run_in_thread():
                        return asyncio.run(self._get_historical_weather_async(location, date))
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)
                
                print(f"✅ AutoGen Tool: Historical weather data retrieved")
                return self._sanitize_string_for_hexaeight(result)
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting historical weather for {location} on {date}. Please try again or ask about a different location/date."
                print(f"❌ AutoGen Tool Error: {error_msg}")
                return self._sanitize_string_for_hexaeight(error_msg)
        
        def search_locations(query: str) -> str:
            """Search for locations matching a query string."""
            try:
                print(f"🔍 AutoGen Tool: Searching for locations: {query}")
                
                query = str(query).strip().strip('"').strip("'")
                if not query or len(query) < 2:
                    return "Please provide a location name to search for."
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._search_locations_sync(query))
                            result = future.result(timeout=30)
                    else:
                        result = loop.run_until_complete(self._search_locations_async(query))
                except RuntimeError:
                    import threading
                    import concurrent.futures
                    
                    def run_in_thread():
                        return asyncio.run(self._search_locations_async(query))
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)
                
                print(f"✅ AutoGen Tool: Location search completed")
                return self._sanitize_string_for_hexaeight(result)
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble searching for locations matching '{query}'. Please try a different search term."
                print(f"❌ AutoGen Tool Error: {error_msg}")
                return self._sanitize_string_for_hexaeight(error_msg)
        
        def get_weather_alerts(location: str) -> str:
            """Get active weather alerts and warnings for a specified location."""
            try:
                print(f"🚨 AutoGen Tool: Getting weather alerts for: {location}")
                
                location = str(location).strip().strip('"').strip("'")
                if not location or len(location) < 2:
                    location = "London"
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._get_weather_alerts_sync(location))
                            result = future.result(timeout=30)
                    else:
                        result = loop.run_until_complete(self._get_weather_alerts_async(location))
                except RuntimeError:
                    import threading
                    import concurrent.futures
                    
                    def run_in_thread():
                        return asyncio.run(self._get_weather_alerts_async(location))
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)
                
                print(f"✅ AutoGen Tool: Weather alerts data retrieved")
                return self._sanitize_string_for_hexaeight(result)
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting weather alerts for {location}. Please try again or ask about a different location."
                print(f"❌ AutoGen Tool Error: {error_msg}")
                return self._sanitize_string_for_hexaeight(error_msg)
        
        def get_astronomy_data(location: str) -> str:
            """Get astronomy data (sunrise, sunset, moon phases) for a specified location."""
            try:
                print(f"🌙 AutoGen Tool: Getting astronomy data for: {location}")
                
                location = str(location).strip().strip('"').strip("'")
                if not location or len(location) < 2:
                    location = "London"
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._get_astronomy_sync(location))
                            result = future.result(timeout=30)
                    else:
                        result = loop.run_until_complete(self._get_astronomy_async(location))
                except RuntimeError:
                    import threading
                    import concurrent.futures
                    
                    def run_in_thread():
                        return asyncio.run(self._get_astronomy_async(location))
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        result = future.result(timeout=30)
                
                print(f"✅ AutoGen Tool: Astronomy data retrieved")
                return self._sanitize_string_for_hexaeight(result)
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting astronomy data for {location}. Please try again or ask about a different location."
                print(f"❌ AutoGen Tool Error: {error_msg}")
                return self._sanitize_string_for_hexaeight(error_msg)
        
        try:
            # Register ALL weather functions for execution and LLM
            functions = [
                (get_current_weather, "Get current weather conditions for any location worldwide"),
                (get_weather_forecast, "Get weather forecast for 1-10 days for any location worldwide"),
                (get_historical_weather, "Get historical weather data for a specific date (within 7 days)"),
                (search_locations, "Search for location names and coordinates"),
                (get_weather_alerts, "Get active weather alerts and warnings for a location"),
                (get_astronomy_data, "Get sunrise, sunset, and moon phase data for a location")
            ]
            
            for func, description in functions:
                self.weather_specialist.register_for_execution(name=func.__name__)(func)
                self.weather_specialist.register_for_llm(
                    name=func.__name__, 
                    description=description
                )(func)
            
            print(f"✅ Registered {len(functions)} comprehensive weather functions with pyautogen")
        except Exception as e:
            print(f"⚠️  Function registration failed: {e}")
            print("   Will use direct weather API calls instead")
    
    async def _get_current_weather_sync(self, location: str, include_air_quality: bool = False) -> str:
        """Synchronous wrapper for current weather API call"""
        return await self._get_current_weather_async(location, include_air_quality)
    
    async def _get_forecast_sync(self, location: str, days: int = 3) -> str:
        """Synchronous wrapper for forecast API call"""
        return await self._get_forecast_async(location, days)
    
    async def _get_historical_weather_sync(self, location: str, date: str) -> str:
        """Synchronous wrapper for historical weather API call"""
        return await self._get_historical_weather_async(location, date)
    
    async def _search_locations_sync(self, query: str) -> str:
        """Synchronous wrapper for location search API call"""
        return await self._search_locations_async(query)
    
    async def _get_weather_alerts_sync(self, location: str) -> str:
        """Synchronous wrapper for weather alerts API call"""
        return await self._get_weather_alerts_async(location)
    
    async def _get_astronomy_sync(self, location: str) -> str:
        """Synchronous wrapper for astronomy API call"""
        return await self._get_astronomy_async(location)
    
    def _classify_message(self, message: str) -> str:
        """Classify the type of message"""
        try:
            message_lower = str(message).lower().strip()
            
            capability_keywords = [
                "who can", "who provides", "who gives", "can you", "do you", 
                "what can you", "capabilities", "what do you do", "help me",
                "who offers", "who has", "available", "services"
            ]
            
            weather_keywords = [
                "weather", "temperature", "forecast", "raining", "sunny", 
                "cloudy", "hot", "cold", "humidity", "wind"
            ]
            
            location_indicators = [
                " in ", " for ", " at ", "paris", "london", "tokyo", "new york"
            ]
            
            if any(keyword in message_lower for keyword in capability_keywords):
                return "capability_query"
            
            if any(keyword in message_lower for keyword in weather_keywords) or \
               any(indicator in message_lower for indicator in location_indicators):
                return "weather_request"
            
            return "general_conversation"
            
        except Exception as e:
            logger.error(f"Error classifying message: {e}")
            return "general_conversation"
    
    async def _process_weather_request(self, message: str) -> str:
        """Enhanced process request with natural language responses"""
        try:
            print(f"🎯 AutoGen: Processing: {str(message)[:50]}...")
            
            message_type = self._classify_message(message)
            print(f"📋 Message type: {message_type}")
            
            if message_type == "capability_query":
                response = await self._handle_capability_query(message)
            elif message_type == "weather_request":
                response = await self._handle_weather_request(message)
            else:
                response = await self._handle_general_conversation(message)
            
            natural_response = self._ensure_natural_language_response(response)
            
            return self._sanitize_string_for_hexaeight(natural_response)
            
        except Exception as e:
            print(f"❌ AutoGen processing error: {e}")
            error_response = f"I apologize, but I encountered an error while processing your request. Please try asking again in a moment."
            return self._sanitize_string_for_hexaeight(error_response)
    
    def _ensure_natural_language_response(self, response: str) -> str:
        """Ensure response is in natural, conversational language"""
        try:
            conversational_starters = [
                "hello", "hi", "i'm", "i am", "let me", "here's", "here is",
                "sure", "absolutely", "of course", "i'd be happy", "i can help"
            ]
            
            response_lower = response.lower().strip()
            
            if any(response_lower.startswith(starter) for starter in conversational_starters):
                return response
            
            if "autogen" in response_lower or "specialist" in response_lower:
                return response
            
            if response.strip().startswith(('🤖', '🌤️', '📊', '☀️', '⛅')):
                return response
            
            if "weather" in response_lower:
                return f"Here's the weather information you requested:\n\n{response}"
            else:
                return f"Hello! {response}"
                
        except Exception as e:
            print(f"⚠️  Error ensuring natural language: {e}")
            return response
    
    async def _handle_capability_query(self, message: str) -> str:
        """Handle capability and identity questions"""
        try:
            if AUTOGEN_VERSION == "pyautogen" and self.weather_specialist:
                try:
                    conversational_prompt = f"""A user is asking: "{message}"
                    
Please respond naturally and conversationally as a friendly AutoGen weather specialist. Introduce yourself warmly, explain your capabilities, and offer to help with weather questions. Be approachable and helpful."""
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.weather_specialist.generate_reply,
                            [{"role": "user", "content": conversational_prompt}]
                        ),
                        timeout=15.0
                    )
                    
                    if response and len(str(response)) > 20:
                        if not any(word in str(response).lower() for word in ["hello", "hi", "i'm", "i am"]):
                            return f"Hello! {response}"
                        return str(response)
                    else:
                        raise Exception("Empty or invalid response from AutoGen")
                        
                except Exception as e:
                    print(f"⚠️  AutoGen capability response failed: {e}")
            
            return """Hello! I'm your friendly AutoGen-powered weather specialist, and I'm delighted to help you with all your weather needs!

Here's what I can do for you:

🌤️ **Current Weather**: I can get real-time weather conditions for any city worldwide - just ask "What's the weather in [city]?"

📊 **Weather Forecasts**: I provide detailed forecasts up to 10 days ahead for planning your activities

🌡️ **Detailed Information**: Temperature, humidity, wind speed, pressure, visibility, and UV index

🏭 **Air Quality**: Information about air pollution levels when available

📅 **Historical Weather**: Past weather data for specific dates

🚨 **Weather Alerts**: Active warnings and alerts for any location

🌙 **Astronomy Data**: Sunrise, sunset, and moon phases

I'm powered by the AutoGen framework and I love chatting about weather! Whether you're planning a trip, wondering if you need an umbrella, or just curious about conditions somewhere, I'm here to help.

What weather information can I get for you today?"""
            
        except Exception as e:
            print(f"❌ Capability query failed: {e}")
            return """Hello! I'm your AutoGen weather specialist, and I'm here to help you with weather information for any location worldwide. What can I look up for you today?"""
    
    async def _handle_weather_request(self, message: str) -> str:
        """Handle weather data requests with LLM intelligence"""
        try:
            print("🌤️  AutoGen: Processing weather data request with LLM intelligence...")
            
            # Let LLM handle the entire query understanding and tool selection
            if AUTOGEN_VERSION == "pyautogen" and self.weather_specialist:
                try:
                    intelligent_prompt = f"""The user is asking: "{message}"

You are a comprehensive weather specialist with access to multiple weather tools. Analyze this query and respond appropriately using the most suitable tool:

Available Tools (choose the RIGHT one based on the request):
- get_current_weather: Current conditions, temperature, humidity, wind, pressure, UV index, air quality
- get_weather_forecast: 1-10 day forecasts with daily highs/lows, conditions, rain chances (USE THIS for "tomorrow", "next day", "forecast", "next few days")
- get_historical_weather: Historical weather data for specific dates (within 7 days) (USE THIS for "yesterday", "last week", specific past dates)
- search_locations: Search for location names and coordinates (USE THIS if location is unclear)
- get_weather_alerts: Active weather warnings and alerts
- get_astronomy_data: Sunrise, sunset, moon phases, astronomical data

Instructions:
1. For current weather: Use get_current_weather with the location
2. For forecasts/tomorrow/next day/next few days: Use get_weather_forecast with location and number of days (default 3)
3. For past weather/yesterday: Use get_historical_weather with location and date (YYYY-MM-DD)
4. For cyclone/hurricane/storm tracking: Explain these require specialized meteorological services (IMD, NOAA, etc.)
5. For location searches: Use search_locations if the location is unclear
6. For weather alerts: Use get_weather_alerts
7. For sunrise/sunset/moon data: Use get_astronomy_data

IMPORTANT: 
- If user asks for "tomorrow" or "next day", use get_weather_forecast with 2-3 days
- If user asks for "forecast" or "next few days", use get_weather_forecast
- Always understand the location from context (like "near chennai" means Chennai)
- Be conversational and helpful in your responses"""
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.weather_specialist.generate_reply,
                            [{"role": "user", "content": intelligent_prompt}]
                        ),
                        timeout=30.0
                    )
                    
                    if response and len(str(response)) > 30:
                        return str(response)
                        
                except Exception as e:
                    print(f"⚠️  AutoGen LLM processing failed: {e}")
            
            # Fallback: simple pattern matching (now handles forecasts properly)
            print("🔄 Using fallback pattern matching...")
            
            message_lower = message.lower()
            
            if "cyclone" in message_lower or "hurricane" in message_lower or "storm" in message_lower:
                location = "Chennai" if "chennai" in message_lower else "the area"
                return f"""I understand you're asking about cyclone forecasts near {location}.

While I can provide current weather conditions, specialized cyclone and storm tracking requires real-time meteorological data from services like the India Meteorological Department (IMD) or regional weather services.

For accurate cyclone forecasts and warnings near {location}, I recommend checking:
- India Meteorological Department (IMD) official website
- Local weather services
- Emergency management authorities

I can provide current weather conditions for {location} if that would be helpful. Would you like me to check the current weather conditions instead?"""
            
            # Extract location
            location = "Chennai" if "chennai" in message_lower else \
                      "Mumbai" if "mumbai" in message_lower else \
                      "Delhi" if "delhi" in message_lower else \
                      "Bangalore" if "bangalore" in message_lower else \
                      "London" if "london" in message_lower else \
                      "Paris" if "paris" in message_lower else \
                      "Tokyo" if "tokyo" in message_lower else "London"
            
            # Check if it's a forecast request
            forecast_keywords = ["tomorrow", "next day", "forecast", "next few days", "coming days", "upcoming"]
            is_forecast_request = any(keyword in message_lower for keyword in forecast_keywords)
            
            if is_forecast_request:
                # Get forecast instead of current weather
                days = 3
                if "tomorrow" in message_lower or "next day" in message_lower:
                    days = 2
                elif "5 day" in message_lower or "5-day" in message_lower:
                    days = 5
                elif "week" in message_lower:
                    days = 7
                
                weather_data = await self._get_forecast_async(location, days)
                
                return f"""I've got the weather forecast for {location}:

{weather_data}

Is there anything else about the weather you'd like to know? I can also provide current conditions for other locations!"""
            else:
                # Get current weather
                weather_data = await self._get_current_weather_async(location, False)
                
                return f"""I've got the current weather information for {location}:

{weather_data}

Is there anything else about the weather you'd like to know? I can also provide forecasts or check other locations!"""
            
        except Exception as e:
            print(f"❌ Weather request failed: {e}")
            return f"I'm sorry, I'm having trouble processing your weather request right now. Could you try asking again, or rephrase your question?"

    async def _handle_general_conversation(self, message: str) -> str:
        """Handle general conversation"""
        try:
            if AUTOGEN_VERSION == "pyautogen" and self.weather_specialist:
                try:
                    conversational_prompt = f"""The user said: "{message}"
                    
Respond naturally as a friendly AutoGen weather specialist. If it's weather-related, offer to help. If not weather-related, politely redirect to weather topics while being helpful and conversational."""
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.weather_specialist.generate_reply,
                            [{"role": "user", "content": conversational_prompt}]
                        ),
                        timeout=15.0
                    )
                    
                    if response and len(str(response)) > 10:
                        return str(response)
                        
                except Exception as e:
                    print(f"⚠️  AutoGen general conversation failed: {e}")
            
            return """Hello! I'm your AutoGen weather specialist. While I'd love to chat about many topics, I'm specially designed to help you with weather information! 

I can tell you current conditions, forecasts, and detailed weather data for any location worldwide. Is there a particular place you'd like to know the weather for?"""
            
        except Exception as e:
            return "Hello! I'm your AutoGen weather specialist. How can I help you with weather information today?"
    
    async def _get_current_weather_async(self, location: str, include_air_quality: bool = False) -> str:
        """Enhanced async helper for current weather"""
        try:
            async with WeatherAPIClient(self.weather_config) as client:
                data = await client.get_current_weather(location, include_air_quality)
                formatted_data = WeatherFormatter.format_current_weather(data)
                
                if len(formatted_data) > 1500:
                    formatted_data = formatted_data[:1497] + "..."
                
                return formatted_data
                
        except Exception as e:
            print(f"Weather API error: {e}")
            return f"I'm having trouble getting the weather data for {location} right now. Please try again in a moment, or ask about a different location."

    async def _get_forecast_async(self, location: str, days: int = 3) -> str:
        """Get weather forecast data"""
        try:
            async with WeatherAPIClient(self.weather_config) as client:
                data = await client.get_forecast(location, days, aqi=True, alerts=True)
                formatted_data = WeatherFormatter.format_forecast(data)
                
                if len(formatted_data) > 1500:
                    formatted_data = formatted_data[:1497] + "..."
                
                return formatted_data
                
        except Exception as e:
            print(f"Forecast API error: {e}")
            return f"I'm having trouble getting the forecast for {location} right now. Please try again in a moment, or ask about a different location."

    async def _get_historical_weather_async(self, location: str, date: str) -> str:
        """Get historical weather data"""
        try:
            async with WeatherAPIClient(self.weather_config) as client:
                data = await client.get_history(location, date)
                formatted_data = WeatherFormatter.format_history(data)
                
                if len(formatted_data) > 1500:
                    formatted_data = formatted_data[:1497] + "..."
                
                return formatted_data
                
        except Exception as e:
            print(f"Historical weather API error: {e}")
            return f"I'm having trouble getting historical weather for {location} on {date}. Please try again in a moment, or ask about a different location/date."

    async def _search_locations_async(self, query: str) -> str:
        """Search for locations"""
        try:
            async with WeatherAPIClient(self.weather_config) as client:
                # Use search endpoint if available, otherwise return guidance
                url = f"{client.config.base_url}/search.json"
                params = {
                    "key": client.config.api_key,
                    "q": query
                }
                
                async with client.session.get(url, params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        if results:
                            formatted = "Found locations:\n"
                            for i, location in enumerate(results[:5], 1):
                                name = location.get('name', 'Unknown')
                                region = location.get('region', '')
                                country = location.get('country', '')
                                lat = location.get('lat', '')
                                lon = location.get('lon', '')
                                
                                location_str = f"{name}"
                                if region: location_str += f", {region}"
                                if country: location_str += f", {country}"
                                if lat and lon: location_str += f" ({lat}, {lon})"
                                
                                formatted += f"{i}. {location_str}\n"
                            return formatted.strip()
                        else:
                            return f"No locations found matching '{query}'. Try a different search term."
                    else:
                        return f"Location search temporarily unavailable. Try using a specific city name."
        except Exception as e:
            return f"Location search error: {str(e)}. Try using a specific city name."

    async def _get_weather_alerts_async(self, location: str) -> str:
        """Get weather alerts"""
        try:
            async with WeatherAPIClient(self.weather_config) as client:
                data = await client.get_forecast(location, days=1, aqi=False, alerts=True)
                
                alerts = data.get('alerts', {}).get('alert', [])
                if alerts:
                    formatted = "🚨 Active Weather Alerts:\n\n"
                    for i, alert in enumerate(alerts, 1):
                        title = alert.get('headline', 'Weather Alert')
                        severity = alert.get('severity', 'Unknown')
                        desc = alert.get('desc', 'No description available')
                        
                        formatted += f"{i}. **{title}**\n"
                        formatted += f"   Severity: {severity}\n"
                        formatted += f"   Details: {desc[:200]}...\n\n"
                    
                    return formatted.strip()
                else:
                    return f"✅ No active weather alerts for {location}."
                    
        except Exception as e:
            return f"Weather alerts check failed: {str(e)}"

    async def _get_astronomy_async(self, location: str) -> str:
        """Get astronomy data"""
        try:
            async with WeatherAPIClient(self.weather_config) as client:
                data = await client.get_current_weather(location, aqi=False)
                
                astro = data.get('forecast', {}).get('forecastday', [{}])[0].get('astro', {}) if 'forecast' in data else {}
                
                if not astro:
                    # Get astronomy from forecast endpoint
                    forecast_data = await client.get_forecast(location, days=1)
                    astro = forecast_data.get('forecast', {}).get('forecastday', [{}])[0].get('astro', {})
                
                if astro:
                    formatted = f"🌙 Astronomy Data for {location}:\n\n"
                    formatted += f"🌅 Sunrise: {astro.get('sunrise', 'N/A')}\n"
                    formatted += f"🌇 Sunset: {astro.get('sunset', 'N/A')}\n"
                    formatted += f"🌙 Moonrise: {astro.get('moonrise', 'N/A')}\n"
                    formatted += f"🌑 Moonset: {astro.get('moonset', 'N/A')}\n"
                    formatted += f"🌕 Moon Phase: {astro.get('moon_phase', 'N/A')}\n"
                    formatted += f"🌟 Moon Illumination: {astro.get('moon_illumination', 'N/A')}%"
                    
                    return formatted
                else:
                    return f"Astronomy data not available for {location}."
                    
        except Exception as e:
            return f"Astronomy data error: {str(e)}"

# Setup functions
async def setup_autogen_weather_agent():
    """Setup AutoGen weather agent with comprehensive intelligence"""
    
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library required: pip install openai")
    
    if not AUTOGEN_AVAILABLE:
        raise ImportError("AutoGen not available. Install with: pip install pyautogen")
    
    print("🌤️ AutoGen Weather Agent with Comprehensive Intelligence")
    print("=" * 60)
    
    try:
        weather_config = get_weather_config_from_env()
        llm_config = get_llm_config_from_env()
        
        print(f"🔧 Configuration loaded:")
        print(f"   Weather API: weatherapi.com")
        print(f"   LLM Provider: {llm_config.provider.upper()}")
        print(f"   LLM Model: {llm_config.model}")
        print(f"   AutoGen Version: {AUTOGEN_VERSION}")
        print(f"   Framework Targeting: ✅ Enabled")
        print(f"   Intelligent Processing: ✅ LLM-based query understanding")
        print(f"   Comprehensive Tools: ✅ 6 weather APIs available")
        print(f"   Cyclone Detection: ✅ Specialized handling")
        print(f"   Child Config: {os.getenv('HEXAEIGHT_CHILD_CONFIG_FILENAME', 'child_config.json')}")
        
        autogen_agent = AutoGenWeatherAgent(weather_config, llm_config)
        await autogen_agent.initialize()
        
        print("✅ AutoGen weather agent with comprehensive intelligence ready!")
        return autogen_agent
        
    except Exception as e:
        logger.error(f"Error setting up AutoGen agent: {e}")
        print(f"❌ Setup failed: {e}")
        raise

async def run_autogen_weather_agent():
    """Run the comprehensive AutoGen weather agent with intelligent processing"""
    
    try:
        print("🚀 Starting AutoGen Weather Agent with Comprehensive Intelligence")
        print("=" * 75)
        
        agent = await setup_autogen_weather_agent()

        try:
            inner = agent.hexaeight_agent.hexaeight_agent
            
            agent_name = await inner.get_agent_name()
            internal_id = inner.get_internal_identity()
            is_connected = inner.is_connected_to_pubsub()
            
            print(f"   ✅ Agent Name: {agent_name}")
            print(f"   ✅ Internal ID: {internal_id}")
            print(f"   ✅ PubSub Connected: {is_connected}")
            
        except Exception as e:
            print(f"   ❌ Error getting agent info: {e}")
        
        print(f"\n🎯 AutoGen Agent Status:")
        print(f"   ✅ Comprehensive weather toolkit enabled (6 tools)")
        print(f"   ✅ Current weather, forecasts, historical data")
        print(f"   ✅ Location search, alerts, astronomy data") 
        print(f"   ✅ Intelligent LLM-based query processing enabled")
        print(f"   ✅ Forecast support: tomorrow, next day, 5-day, weekly")
        print(f"   ✅ Cyclone/storm forecast detection active")
        print(f"   ✅ Framework targeting enabled")
        print(f"   ✅ Natural language response formatting active")
        print(f"   ✅ Connected to PubSub server")
        print(f"   ✅ AutoGen framework integration ({AUTOGEN_VERSION})")
        
        print(f"\n🔄 AutoGen agent running with comprehensive weather intelligence...")
        print(f"💡 Examples of messages I'll handle:")
        print(f"   - 'I need weather for Chennai. Can the autogen agent respond?'")
        print(f"   - 'What's the weather in Paris?' (general - will compete)")
        print(f"   - 'Give me 5-day forecast for Tokyo'") 
        print(f"   - 'What will the weather be tomorrow in Mumbai?'")
        print(f"   - 'What was the weather in Mumbai yesterday?'")
        print(f"   - 'Are there any weather alerts for Delhi?'")
        print(f"   - 'What time is sunrise in Bangkok?'")
        print(f"   - 'Any cyclone updates near chennai?' (intelligent cyclone detection)")
        print(f"🚫 Examples of messages I'll ignore:")
        print(f"   - 'Can the crewai agent respond?'")
        print(f"   - 'Use crewai for weather'")
        print(f"🛑 Press Ctrl+C to stop")
        
        try:
            heartbeat_count = 0
            while True:
                await asyncio.sleep(30)
                heartbeat_count += 1
                print(f"💓 AutoGen agent heartbeat #{heartbeat_count} - ready for comprehensive weather intelligence...")
        except KeyboardInterrupt:
            print(f"\n👋 Shutting down AutoGen weather agent...")
        
    except Exception as e:
        logger.error(f"AutoGen agent error: {e}")
        print(f"❌ AutoGen agent failed: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(test_autogen_weather_agent())
    else:
        asyncio.run(run_autogen_weather_agent())
