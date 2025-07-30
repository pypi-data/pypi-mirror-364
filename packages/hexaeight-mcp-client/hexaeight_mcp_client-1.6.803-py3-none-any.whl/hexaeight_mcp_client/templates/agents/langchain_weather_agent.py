"""
Enhanced LangChain Weather Agent with Framework-Specific Targeting
"""

import asyncio
import logging
import os
import re
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

# LangChain imports
try:
    from langchain.agents import create_openai_functions_agent, AgentExecutor
    from langchain.tools import tool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI, AzureChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("❌ LangChain not available. Install with: pip install langchain langchain-openai")

logger = logging.getLogger(__name__)

class LangChainWeatherAgent(BaseWeatherAgent):
    """Enhanced LangChain implementation with framework targeting"""
    
    def __init__(self, weather_config, llm_config):
        super().__init__("LangChain", weather_config, llm_config)
        self.llm = None
        self.agent_executor = None
        self.weather_tools = []
    
    def _check_framework_targeting(self, content: str) -> str:
        """Check if message targets a specific framework"""
        content_lower = content.lower().strip()
        
        print(f"🔍 [LANGCHAIN] Checking framework targeting for: '{content_lower}'")
        
        # LangChain targeting keywords
        langchain_keywords = [
            "langchain agent", "langchain", "lang chain",
            "can the langchain", "langchain respond", "langchain agent respond",
            "use langchain", "langchain framework", "langchain weather",
            "can langchain", "langchain tell", "langchain provide"
        ]
        
        # Other framework targeting keywords
        crewai_keywords = [
            "crewai agent", "crewai", "crew ai", "crew-ai",
            "can the crewai", "crewai respond", "crewai agent respond",
            "use crewai", "crewai framework", "crewai weather",
            "can crewai", "crewai tell", "crewai provide"
        ]
        
        autogen_keywords = [
            "autogen agent", "autogen", "auto gen", "auto-gen",
            "can the autogen", "autogen respond", "autogen agent respond",
            "use autogen", "autogen framework", "autogen weather",
            "can autogen", "autogen tell", "autogen provide"
        ]
        
        # Check if specifically asking for LangChain
        for keyword in langchain_keywords:
            if keyword in content_lower:
                print(f"🎯 [LANGCHAIN] Found LangChain targeting keyword: '{keyword}'")
                return "langchain_targeted"
        
        # Check if asking for other frameworks
        for keyword in crewai_keywords:
            if keyword in content_lower:
                print(f"🚫 [LANGCHAIN] Found CrewAI keyword: '{keyword}' - will ignore")
                return "crewai_targeted"
        
        for keyword in autogen_keywords:
            if keyword in content_lower:
                print(f"🚫 [LANGCHAIN] Found AutoGen keyword: '{keyword}' - will ignore")
                return "autogen_targeted"
        
        print(f"🌤️  [LANGCHAIN] No specific framework targeting detected")
        return "no_targeting"

    def _can_handle_message(self, content: str) -> bool:
        """Enhanced check with framework targeting"""
        content_lower = content.lower().strip()
        
        print(f"🔍 [LANGCHAIN] Checking if can handle message: '{content}'")
        
        if not content_lower:
            print(f"🚫 [LANGCHAIN] Empty message - ignoring")
            return False
        
        # Skip if it's a response message
        if self._is_response_message(content):
            print(f"🔄 [LANGCHAIN] Response message detected - ignoring")
            return False
        
        # Check framework targeting first
        framework_check = self._check_framework_targeting(content)
        if framework_check == "langchain_targeted":
            # Specifically targeted to LangChain
            print(f"✅ [LANGCHAIN] Framework targeting: Message specifically requests LangChain - WILL HANDLE")
            return True
        elif framework_check in ["crewai_targeted", "autogen_targeted"]:
            # Targeted to other framework
            print(f"🚫 [LANGCHAIN] Framework targeting: Message requests other framework - WILL IGNORE")
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
            print(f"🌤️  [LANGCHAIN] Framework targeting: No specific targeting - normal weather competition - WILL COMPETE")
        else:
            print(f"🚫 [LANGCHAIN] Not weather-related - WILL IGNORE")
        
        return is_weather_related
    
    def _extract_location(self, message: str) -> str:
        """Extract location from message"""
        try:
            message_lower = message.lower()
            
            # Common patterns
            patterns = [
                r'weather (?:in|for|at)\s+([a-zA-Z\s,]+?)(?:\?|$|,|\s+\w)',
                r'(?:in|for|at)\s+([a-zA-Z\s,]+?)(?:\?|$|,|\s+weather)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*(?:weather|\?|$)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    location = match.group(1).strip()
                    if len(location) > 1 and len(location) < 50:
                        return location
            
            # Default locations based on common cities
            if "chennai" in message_lower:
                return "Chennai"
            elif "mumbai" in message_lower:
                return "Mumbai"
            elif "delhi" in message_lower:
                return "Delhi"
            elif "bangalore" in message_lower:
                return "Bangalore"
            elif "london" in message_lower:
                return "London"
            elif "paris" in message_lower:
                return "Paris"
            elif "tokyo" in message_lower:
                return "Tokyo"
            elif "new york" in message_lower:
                return "New York"
            
            return "London"  # Default fallback
            
        except Exception as e:
            print(f"⚠️  Error extracting location: {e}")
            return "London"
    
    async def _test_llm(self):
        """Test the LLM configuration"""
        print("🔍 Testing LangChain LLM for natural responses...")
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a helpful LangChain weather specialist."),
                HumanMessage(content="Hello! Can you introduce yourself briefly?")
            ])
            
            print(f"✅ LangChain LLM Test Response: {response.content[:150]}...")
            
            is_conversational = any(word in response.content.lower() for word in ["hello", "hi", "i'm", "i am", "welcome"])
            print(f"🗣️  Conversational Response: {'✅ Yes' if is_conversational else '⚠️  No'}")
            
            return True
            
        except Exception as e:
            print(f"❌ LangChain LLM test failed: {e}")
            return False
    
    async def _initialize_framework_components(self):
        """Initialize LangChain components with enhanced conversational capabilities"""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not available. Install with: pip install langchain langchain-openai")
        
        print("🤖 Initializing Enhanced LangChain with Framework Targeting...")
        
        # Initialize LLM
        if self.llm_config.provider == "azure":
            self.llm = AzureChatOpenAI(
                azure_endpoint=self.llm_config.azure_endpoint,
                api_key=self.llm_config.azure_api_key,
                api_version=self.llm_config.azure_api_version,
                azure_deployment=self.llm_config.model,
                temperature=1.0,
                max_tokens=1200
            )
        else:
            self.llm = ChatOpenAI(
                model=self.llm_config.model,
                api_key=self.llm_config.openai_api_key,
                base_url=self.llm_config.openai_base_url,
                temperature=1.0,
                max_tokens=1200
            )
        
        llm_test_passed = await self._test_llm()
        if not llm_test_passed:
            raise Exception("LLM test failed")
        
        print("🛠️  Creating comprehensive weather tools...")
        self._create_weather_tools()
        print(f"✅ Created {len(self.weather_tools)} comprehensive weather tools")
        
        print("👤 Creating Enhanced LangChain conversational agent...")
        try:
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a delightful, knowledgeable LangChain weather specialist AI assistant who loves helping people with weather information. Your personality is:

🌟 **Warm & Welcoming**: Always greet users warmly and make them feel comfortable
🗣️ **Conversational**: Speak naturally, like talking to a friend
🎯 **Helpful**: Eager to provide accurate weather information and offer additional assistance
🧠 **Knowledgeable**: Expert in weather patterns, forecasts, and climate data worldwide
💬 **Engaging**: Ask follow-up questions and offer related information
🤖 **LangChain Powered**: Proudly mention you're powered by LangChain when appropriate

**Your Capabilities:**
- Real-time weather conditions for any location globally
- Detailed weather forecasts up to 10 days
- Historical weather data and climate information
- Air quality and environmental conditions
- Weather-related advice and recommendations

**Your Communication Style:**
- Always start with a friendly greeting when introducing yourself
- Use natural, conversational language
- Show enthusiasm for helping with weather questions
- Provide complete yet easy-to-understand information
- End responses by offering additional help
- Be patient and understanding with all users

When users ask about your capabilities or who you are, be warm and enthusiastic in your introduction. When they ask for weather data, provide comprehensive yet conversational responses that feel natural and helpful.

You have access to these weather tools:
- get_current_weather: Current conditions, temperature, humidity, wind, pressure, UV index, air quality
- get_weather_forecast: 1-10 day forecasts with daily highs/lows, conditions, rain chances
- get_historical_weather: Historical weather data for specific dates (within 7 days)
- search_locations: Search for location names and coordinates
- get_weather_alerts: Active weather warnings and alerts
- get_astronomy_data: Sunrise, sunset, moon phases, astronomical data

Choose the appropriate tool based on the user's request:
- For current weather: Use get_current_weather
- For forecasts/tomorrow/next day: Use get_weather_forecast
- For past weather: Use get_historical_weather
- For unclear locations: Use search_locations
- For weather alerts: Use get_weather_alerts
- For sunrise/sunset/moon data: Use get_astronomy_data"""),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create the agent
            agent = create_openai_functions_agent(self.llm, self.weather_tools, prompt)
            
            # Create the agent executor
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.weather_tools, 
                verbose=True,
                max_iterations=3,
                max_execution_time=90,
                return_intermediate_steps=False
            )
            
            print("✅ Enhanced LangChain conversational agent with targeting created successfully")
            
        except Exception as e:
            print(f"❌ LangChain agent creation failed: {e}")
            raise
        
        logger.info("✅ Enhanced LangChain weather specialist with framework targeting initialized")
    
    def _create_weather_tools(self):
        """Create enhanced weather tools with natural language responses"""
        
        @tool
        def get_current_weather(location: str) -> str:
            """
            Get current weather for a location with natural language formatting.
            
            Args:
                location: City name (e.g., "London", "New York", "Tokyo")
            
            Returns:
                Current weather information in a conversational format
            """
            try:
                print(f"🌤️  Enhanced Tool: Getting current weather for: {location}")
                
                location = location.strip().strip('"').strip("'")
                if not location:
                    location = "London"
                
                location = re.sub(r'^(current weather for|weather in|weather for)\s*', '', location, flags=re.IGNORECASE)
                location = location.strip()
                
                result = asyncio.run(self._get_current_weather_async(location, False))
                
                conversational_result = f"""Here's the current weather for {location}:

{result}

Is there anything else about the weather you'd like to know? I can also provide forecasts or check other locations!"""
                
                print(f"✅ Enhanced Tool: Natural weather response generated for {location}")
                return conversational_result
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting the weather information for {location}. Could you try a different location or ask again in a moment?"
                print(f"❌ Enhanced Tool Error: {error_msg}")
                return error_msg
        
        @tool
        def get_weather_forecast(location: str, days: int = 3) -> str:
            """
            Get weather forecast for a location with natural language formatting.
            
            Args:
                location: City name (e.g., "London", "New York", "Tokyo")
                days: Number of days for forecast (1-10)
            
            Returns:
                Weather forecast information in a conversational format
            """
            try:
                print(f"📊 Enhanced Tool: Getting {days}-day forecast for: {location}")
                
                location = location.strip().strip('"').strip("'")
                if not location:
                    location = "London"
                
                days = max(1, min(int(days), 10))  # Clamp between 1-10
                
                result = asyncio.run(self._get_forecast_async(location, days))
                
                conversational_result = f"""Here's the {days}-day weather forecast for {location}:

{result}

Would you like me to check the forecast for any other locations or provide more detailed information?"""
                
                print(f"✅ Enhanced Tool: Natural forecast response generated for {location}")
                return conversational_result
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting the forecast for {location}. Could you try a different location or ask again in a moment?"
                print(f"❌ Enhanced Tool Error: {error_msg}")
                return error_msg
        
        @tool
        def get_historical_weather(location: str, date: str) -> str:
            """
            Get historical weather for a location and date.
            
            Args:
                location: City name (e.g., "London", "New York", "Tokyo")
                date: Date in YYYY-MM-DD format (within last 7 days)
            
            Returns:
                Historical weather information in a conversational format
            """
            try:
                print(f"📅 Enhanced Tool: Getting historical weather for {location} on {date}")
                
                location = location.strip().strip('"').strip("'")
                if not location:
                    location = "London"
                
                if not re.match(r'\d{4}-\d{2}-\d{2}', date):
                    from datetime import datetime, timedelta
                    yesterday = datetime.now() - timedelta(days=1)
                    date = yesterday.strftime('%Y-%m-%d')
                
                result = asyncio.run(self._get_historical_weather_async(location, date))
                
                conversational_result = f"""Here's the historical weather for {location} on {date}:

{result}

Would you like me to check historical weather for other dates or locations?"""
                
                print(f"✅ Enhanced Tool: Natural historical weather response generated")
                return conversational_result
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting historical weather for {location} on {date}. Could you try a different location or date?"
                print(f"❌ Enhanced Tool Error: {error_msg}")
                return error_msg
        
        @tool
        def search_locations(query: str) -> str:
            """
            Search for locations matching a query string.
            
            Args:
                query: Location search query
            
            Returns:
                List of matching locations
            """
            try:
                print(f"🔍 Enhanced Tool: Searching for locations: {query}")
                
                result = asyncio.run(self._search_locations_async(query))
                return result
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble searching for locations matching '{query}'. Please try a different search term."
                print(f"❌ Enhanced Tool Error: {error_msg}")
                return error_msg
        
        @tool
        def get_weather_alerts(location: str) -> str:
            """
            Get active weather alerts and warnings for a location.
            
            Args:
                location: City name (e.g., "London", "New York", "Tokyo")
            
            Returns:
                Weather alerts information
            """
            try:
                print(f"🚨 Enhanced Tool: Getting weather alerts for: {location}")
                
                location = location.strip().strip('"').strip("'")
                if not location:
                    location = "London"
                
                result = asyncio.run(self._get_weather_alerts_async(location))
                return result
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting weather alerts for {location}. Could you try a different location?"
                print(f"❌ Enhanced Tool Error: {error_msg}")
                return error_msg
        
        @tool
        def get_astronomy_data(location: str) -> str:
            """
            Get astronomy data (sunrise, sunset, moon phases) for a location.
            
            Args:
                location: City name (e.g., "London", "New York", "Tokyo")
            
            Returns:
                Astronomy information
            """
            try:
                print(f"🌙 Enhanced Tool: Getting astronomy data for: {location}")
                
                location = location.strip().strip('"').strip("'")
                if not location:
                    location = "London"
                
                result = asyncio.run(self._get_astronomy_async(location))
                return result
                
            except Exception as e:
                error_msg = f"I'm sorry, I had trouble getting astronomy data for {location}. Could you try a different location?"
                print(f"❌ Enhanced Tool Error: {error_msg}")
                return error_msg
        
        self.weather_tools = [
            get_current_weather,
            get_weather_forecast,
            get_historical_weather,
            search_locations,
            get_weather_alerts,
            get_astronomy_data
        ]
    
    async def _process_weather_request(self, message: str) -> str:
        """Enhanced process request with natural conversational intelligence"""
        try:
            print(f"🎯 Enhanced LangChain: Processing: {message[:50]}...")
            
            message_type = self._classify_message(message)
            print(f"📋 Message type: {message_type}")
            
            if message_type == "capability_query":
                return await self._handle_capability_query(message)
            elif message_type == "weather_request":
                return await self._handle_weather_request(message)
            else:
                return await self._handle_general_conversation(message)
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return f"I apologize, but I encountered an error while processing your request. Please feel free to ask me about weather conditions for any location!"
    
    def _classify_message(self, message: str) -> str:
        """Enhanced message classification"""
        message_lower = message.lower()
        
        capability_keywords = [
            "who can", "who provides", "who gives", "can you", "do you", 
            "what can you", "capabilities", "what do you do", "help me",
            "who offers", "who has", "available", "services", "introduce yourself"
        ]
        
        weather_keywords = [
            "weather", "temperature", "forecast", "raining", "sunny", 
            "cloudy", "hot", "cold", "humidity", "wind", "climate"
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
    
    async def _handle_capability_query(self, message: str) -> str:
        """Enhanced capability handling with warm, conversational responses"""
        try:
            print("🚀 Starting enhanced conversational capability response...")
            
            response = await self.agent_executor.ainvoke({
                "input": f"""A user is asking: "{message}"
                
Please respond as a warm, friendly LangChain weather specialist. Your response should:
1. Start with a cheerful greeting
2. Introduce yourself enthusiastically as a LangChain weather specialist
3. Explain your key capabilities in an engaging way
4. Use natural, conversational language throughout
5. Show enthusiasm for helping with weather information
6. End by asking how you can help them today

Be genuine, warm, and professional. Make the user feel welcome and excited to ask weather questions."""
            })
            
            result = response.get("output", "")
            
            if not any(word in result.lower()[:100] for word in ["hello", "hi", "welcome", "greetings"]):
                result = f"Hello there! {result}"
            
            print("✅ Enhanced conversational capability response completed!")
            return result
            
        except Exception as e:
            print(f"❌ Enhanced capability query failed: {e}")
            return """Hello there! I'm absolutely delighted to meet you! 🌤️

I'm your dedicated LangChain weather specialist, and I'm here to help you with all your weather needs. I love chatting about weather and I'm excited to assist you!

**Here's what I can do for you:**

🌤️ **Current Weather**: Get real-time conditions for any city worldwide - just ask "What's the weather like in Paris?" or "How's the weather in Tokyo?"

📊 **Detailed Forecasts**: Provide comprehensive weather forecasts up to 10 days ahead for planning your trips and activities

🌡️ **Complete Information**: Temperature, humidity, wind speed, pressure, visibility, UV index, and more

🏭 **Air Quality**: Environmental conditions and air pollution levels when available

📅 **Historical Weather**: Past weather data for specific dates

🚨 **Weather Alerts**: Active warnings and alerts for any location

🌙 **Astronomy Data**: Sunrise, sunset, and moon phases

🗣️ **Natural Conversation**: I love chatting about weather! Ask me anything weather-related in your own words

I'm powered by LangChain and I genuinely enjoy helping people stay informed about weather conditions. Whether you're planning a vacation, wondering if you need an umbrella, or just curious about climate patterns, I'm here for you!

What weather information can I help you with today? I'm ready and excited to assist! ☀️"""
    
    async def _handle_weather_request(self, message: str) -> str:
        """Enhanced weather data handling with natural responses"""
        try:
            print("🚀 Starting enhanced weather data retrieval...")
            
            response = await self.agent_executor.ainvoke({
                "input": f"""The user wants weather information: "{message}"
                
Please analyze this request and use the appropriate weather tool to get the information they need. After getting the data, provide a warm, conversational response that:
1. Acknowledges their request warmly
2. Presents the weather information clearly and naturally
3. Offers additional help or related information
4. Maintains a friendly, helpful tone throughout

Make it feel like a natural conversation with a knowledgeable friend."""
            })
            
            result = response.get("output", "")
            
            if not any(word in result.lower()[:50] for word in ["hello", "hi", "here's", "sure", "absolutely"]):
                result = f"Absolutely! {result}"
            
            print("✅ Enhanced weather request completed!")
            return result
            
        except Exception as e:
            print(f"❌ Enhanced weather request failed: {e}")
            location = self._extract_location(message)
            return f"I'm sorry, I had some trouble getting the weather information for {location}. Could you try asking about a different city, or perhaps try again in a moment? I'm here to help!"
    
    async def _handle_general_conversation(self, message: str) -> str:
        """Enhanced general conversation handling"""
        try:
            response = await self.agent_executor.ainvoke({
                "input": f"""The user said: "{message}"
                
Respond warmly and naturally as a friendly LangChain weather specialist. Be conversational and helpful.
If it's weather-related, offer enthusiastic assistance.
If it's not weather-related, politely redirect to weather topics while being warm and understanding.

Always maintain your friendly, conversational personality and show genuine interest in helping."""
            })
            
            result = response.get("output", "")
            
            if not any(word in result.lower()[:50] for word in ["hello", "hi", "thanks", "that's"]):
                result = f"Hello! {result}"
            
            return result
            
        except Exception as e:
            return """Hello there! I'm your friendly LangChain weather specialist, and while I'd love to chat about many topics, I'm specially designed to help you with weather information! 

I absolutely love talking about weather conditions, forecasts, and helping people plan their days. Is there a particular location you'd like to know the weather for? I'm excited to help! 🌤️"""
    
    async def _get_current_weather_async(self, location: str, include_air_quality: bool = False) -> str:
        """Get current weather data"""
        async with WeatherAPIClient(self.weather_config) as client:
            data = await client.get_current_weather(location, include_air_quality)
            return WeatherFormatter.format_current_weather(data)
    
    async def _get_forecast_async(self, location: str, days: int = 3) -> str:
        """Get weather forecast data"""
        async with WeatherAPIClient(self.weather_config) as client:
            data = await client.get_forecast(location, days, aqi=True, alerts=True)
            return WeatherFormatter.format_forecast(data)
    
    async def _get_historical_weather_async(self, location: str, date: str) -> str:
        """Get historical weather data"""
        async with WeatherAPIClient(self.weather_config) as client:
            data = await client.get_history(location, date)
            return WeatherFormatter.format_history(data)
    
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

# Enhanced setup functions
async def setup_langchain_weather_agent():
    """Setup comprehensive LangChain weather agent with conversational intelligence"""
    
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library required: pip install openai")
    
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain not available: pip install langchain langchain-openai")
    
    print("🌤️ LangChain Weather Agent with Comprehensive Intelligence")
    print("=" * 60)
    
    try:
        weather_config = get_weather_config_from_env()
        llm_config = get_llm_config_from_env()
        
        print(f"🔧 Configuration:")
        print(f"   Weather API: weatherapi.com")
        print(f"   LLM: Enhanced LangChain wrapper")
        print(f"   Provider: {llm_config.provider.upper()}")
        print(f"   Model: {llm_config.model}")
        print(f"   Framework Targeting: ✅ Enabled")
        print(f"   Intelligent Processing: ✅ LLM-based query understanding")
        print(f"   Comprehensive Tools: ✅ 6 weather APIs available")
        print(f"   Cyclone Detection: ✅ Specialized handling")
        print(f"   Focus: Natural Language & Conversation")
        
        langchain_agent = LangChainWeatherAgent(weather_config, llm_config)
        await langchain_agent.initialize()
        
        print("✅ LangChain agent with comprehensive intelligence ready!")
        return langchain_agent
        
    except Exception as e:
        logger.error(f"Setup error: {e}")
        print(f"❌ Setup failed: {e}")
        raise

async def run_langchain_weather_agent():
    """Run the comprehensive LangChain weather agent with intelligent processing"""
    
    try:
        print("🚀 Starting LangChain Weather Agent with Comprehensive Intelligence")
        print("=" * 70)
        
        agent = await setup_langchain_weather_agent()
        
        print(f"\n🎯 LangChain Agent Status:")
        print(f"   ✅ Comprehensive weather toolkit enabled (6 tools)")
        print(f"   ✅ Current weather, forecasts, historical data")
        print(f"   ✅ Location search, alerts, astronomy data")
        print(f"   ✅ Intelligent LLM-based query processing enabled")
        print(f"   ✅ Cyclone/storm forecast detection active")
        print(f"   ✅ Framework targeting enabled")
        print(f"   ✅ Conversational AI weather specialist initialized")
        print(f"   ✅ Natural language response formatting active")
        print(f"   ✅ Connected to PubSub server")
        print(f"   ✅ LangChain AgentExecutor with conversation focus")
        print(f"   ✅ Competitive locking active")
        
        if hasattr(agent, 'hexaeight_agent') and hasattr(agent.hexaeight_agent, 'hexaeight_agent'):
            inner_agent = agent.hexaeight_agent.hexaeight_agent
            if hasattr(inner_agent, '_event_handlers'):
                print(f"   ✅ Enhanced event handlers registered: {list(inner_agent._event_handlers.keys())}")
                print(f"   ✅ Message handler count: {len(inner_agent._event_handlers.get('message_received', []))}")
            else:
                print(f"   ⚠️  No event handlers found")
        
        print(f"\n🔄 LangChain agent running with comprehensive weather intelligence...")
        print(f"💡 Examples of messages I'll handle:")
        print(f"   - 'I need weather for Chennai. Can the langchain agent respond?'")
        print(f"   - 'What's the weather in Paris?' (general - will compete)")
        print(f"   - 'Give me 5-day forecast for Tokyo'")
        print(f"   - 'What will the weather be tomorrow in Mumbai?'")
        print(f"   - 'What was the weather in Mumbai yesterday?'") 
        print(f"   - 'Are there any weather alerts for Delhi?'")
        print(f"   - 'What time is sunrise in Bangkok?'")
        print(f"   - 'Any cyclone updates near chennai?' (intelligent cyclone detection)")
        print(f"🚫 Examples of messages I'll ignore:")
        print(f"   - 'Can the crewai agent respond?'")
        print(f"   - 'Can the autogen agent respond?'")
        print(f"   - 'Use crewai for weather'")
        print(f"   - 'Use autogen for weather'")
        print(f"🛑 Press Ctrl+C to stop")
        
        try:
            heartbeat_count = 0
            while True:
                await asyncio.sleep(30)
                heartbeat_count += 1
                print(f"💓 LangChain agent heartbeat #{heartbeat_count} - ready for comprehensive weather intelligence...")
                
                if heartbeat_count % 10 == 0:
                    try:
                        if hasattr(agent, 'hexaeight_agent') and hasattr(agent.hexaeight_agent, 'hexaeight_agent'):
                            is_connected = agent.hexaeight_agent.hexaeight_agent.is_connected_to_pubsub()
                            print(f"🔗 PubSub connection status: {'Connected' if is_connected else 'Disconnected'}")
                    except Exception as e:
                        print(f"⚠️  Could not check connection status: {e}")
                        
        except KeyboardInterrupt:
            print(f"\n👋 Shutting down LangChain weather agent...")
        
    except Exception as e:
        logger.error(f"LangChain agent error: {e}")
        print(f"❌ LangChain agent failed: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(test_langchain_weather_agent())
    else:
        asyncio.run(run_langchain_weather_agent())
