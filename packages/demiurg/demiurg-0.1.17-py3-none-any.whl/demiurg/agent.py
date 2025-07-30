"""
Base Agent class for Demiurg framework.
"""

import base64
import json
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

# FastAPI is optional - only needed if using with FastAPI server
try:
    from fastapi.responses import JSONResponse
except ImportError:
    JSONResponse = None

# Type hints
if TYPE_CHECKING:
    from .tools import Composio
    from .providers.base import Provider

from .exceptions import DemiurgError
from .llm import process_message as llm_process_message
from .messaging import (
    MessagingClient,
    enqueue_message_for_processing,
    get_messaging_client,
    send_text_message,
    send_file_message,
)
from .models import Config, Message, Response
from .providers import get_provider
from .utils.files import (
    create_file_content,
    download_file,
    encode_file_base64,
    get_file_info,
    get_file_type,
    is_file_message,
)
from .utils.tools import execute_tools, format_tool_results, init_tools, get_tool_provider

logger = logging.getLogger(__name__)


class Agent:
    """
    Base Demiurg AI Agent class.
    
    This provides the foundation for AI agents with:
    - Multi-provider LLM integration
    - Built-in messaging system
    - Conversation management
    - File handling capabilities
    - Tool execution support
    - Message queue to prevent race conditions
    """
    
    def __init__(
        self, 
        provider: Optional['Provider'] = None,
        tools: Optional['Composio'] = None,
        billing: str = "builder",
        config: Optional[Config] = None
    ):
        """
        Initialize the agent with clean API.
        
        Args:
            provider: LLM provider instance (e.g., OpenAIProvider())
            tools: Composio instance for tool configuration (e.g., Composio("TWITTER", "GMAIL"))
            billing: Billing mode - "builder" or "user" (who pays for API calls)
            config: Optional Config object for advanced settings
            
        Examples:
            # Simple agent with tools
            agent = Agent(OpenAIProvider(), Composio("TWITTER", "GMAIL"), "user")
            
            # Agent without tools  
            agent = Agent(OpenAIProvider(), billing="builder")
            
            # Agent with custom config
            agent = Agent(OpenAIProvider(), config=custom_config)
        """
        # Handle legacy initialization for backward compatibility
        if isinstance(provider, Config):
            # Old style: Agent(config, provider)
            self.config = provider
            self._provider_instance = tools if tools else None
        else:
            # New style: Agent(provider, tools, billing, config)
            self.config = config or Config()
            self.config.billing_mode = billing
            self._provider_instance = provider
            self._composio_config = tools
        
        self.agent_id = f"agent_{self.config.name.lower().replace(' ', '_')}"
        
        # Set up system prompt
        self.system_prompt = self.config.system_prompt or self._get_default_system_prompt()
        
        # Initialize messaging
        self._init_messaging()
        
        # Initialize file handling
        self.file_cache_dir = Path(tempfile.gettempdir()) / "demiurg_agent_files"
        self.file_cache_dir.mkdir(exist_ok=True)
        
        # Configure Composio if provided
        if hasattr(self, '_composio_config') and self._composio_config:
            from .tools import Composio
            if isinstance(self._composio_config, Composio):
                self._setup_composio(self._composio_config)
        
        # Initialize tools
        self.tools = []
        self.tool_provider = None
        self._init_tools()
        
        # OpenAI tools (built-in + custom)
        self.openai_tools = []
        self.custom_tool_handlers = {}
        if self.config.use_tools and self.config.provider == "openai":
            from .tools.openai_tools import OPENAI_TOOLS
            self.openai_tools = OPENAI_TOOLS.copy()
        
        # Initialize provider
        self._init_provider()
        
        logger.info(f"Initialized {self.config.name} v{self.config.version}")
        logger.info(f"Provider: {self.config.provider}")
        logger.info(f"Tools: {len(self.tools)} available")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent."""
        base_prompt = f"""You are {self.config.name}, a helpful AI assistant.

{self.config.description}

You should:
- Be helpful, polite, and professional
- Provide accurate and relevant information
- Ask for clarification when needed
- Use available tools when appropriate

File handling capabilities:
- You CAN view and analyze images (PNG, JPEG, WEBP, GIF)
- You CAN transcribe audio files (MP3, WAV, etc.)
- You CAN read text files (TXT, JSON, XML, etc.)
- You CANNOT analyze PDF content yet (you'll receive a notification when PDFs are sent)
- When you receive an image, describe what you see clearly and accurately

Current date: {datetime.now().strftime("%Y-%m-%d")}"""
        
        # Add OpenAI tools instructions if using tools
        if self.config.provider == "openai" and self.config.use_tools:
            base_prompt += """

Available tools:
- generate_image: Create images using DALL-E 3 based on text descriptions
- text_to_speech: Convert text to natural-sounding speech
- transcribe_audio: Transcribe audio files when explicitly requested (note: audio messages are automatically transcribed)

Use these tools when users request image generation, speech synthesis, or manual audio transcription."""
        
        return base_prompt
    
    def _init_messaging(self):
        """Initialize messaging client."""
        try:
            self.messaging_client = get_messaging_client()
            self.messaging_enabled = True
            logger.info("Messaging client initialized")
        except Exception as e:
            logger.warning(f"Messaging client initialization failed: {e}")
            self.messaging_enabled = False
            self.messaging_client = None
        
        # Store current conversation ID for file sending
        self.current_conversation_id: Optional[str] = None
    
    def _setup_composio(self, composio: 'Composio'):
        """Setup Composio configuration from Composio instance."""
        # Set environment variables
        os.environ["TOOL_PROVIDER"] = "composio"
        os.environ["COMPOSIO_TOOLS"] = ",".join(composio.toolkits)
        
        # Load auth configs from file
        self.composio_auth_configs = self._load_composio_auth_file(composio.auth_file)
        
        logger.info(f"Configured Composio with toolkits: {', '.join(composio.toolkits)}")
    
    def _load_composio_auth_file(self, auth_file: str) -> Dict[str, str]:
        """Load Composio auth configs from file."""
        configs = {}
        try:
            with open(auth_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        toolkit, auth_id = line.split('=', 1)
                        configs[toolkit.strip()] = auth_id.strip()
                        # Also set as environment variable for SDK compatibility
                        os.environ[f"COMPOSIO_AUTH_CONFIG_{toolkit.strip()}"] = auth_id.strip()
            logger.info(f"Loaded {len(configs)} Composio auth configs from {auth_file}")
        except FileNotFoundError:
            logger.warning(f"Composio auth file '{auth_file}' not found")
        except Exception as e:
            logger.error(f"Error loading Composio auth configs: {e}")
        return configs
    
    def _init_provider(self):
        """Initialize LLM provider."""
        try:
            if self._provider_instance:
                # Use provided instance
                self.provider = self._provider_instance
                self.provider_available = True
                # Update config to match provider
                if hasattr(self.provider, '__class__'):
                    provider_name = self.provider.__class__.__name__.lower().replace('provider', '')
                    self.config.provider = provider_name
                # Update billing mode if provider supports it
                if hasattr(self.provider, 'billing_mode'):
                    self.provider.billing_mode = self.config.billing_mode
            else:
                # Create from config
                if self.config.provider == "openai":
                    from .providers import OpenAIProvider
                    self.provider = OpenAIProvider(billing_mode=self.config.billing_mode)
                else:
                    self.provider = get_provider(self.config.provider)
                self.provider_available = True
        except Exception as e:
            logger.warning(f"Provider '{self.config.provider}' initialization failed: {e}")
            self.provider = None
            self.provider_available = False
    
    def _init_tools(self, user_id: Optional[str] = None):
        """Initialize tools."""
        try:
            # Try to initialize tools with configured provider
            tool_provider_name = os.getenv("TOOL_PROVIDER", "composio")
            self.tools = init_tools(provider=tool_provider_name, user_id=user_id)
            
            # Always set tool_provider based on configuration, not on tools availability
            # For Composio, tools may be empty initially until users connect services
            self.tool_provider = tool_provider_name
            
            if self.tools:
                logger.info(f"Loaded {len(self.tools)} tools via {tool_provider_name}")
            else:
                logger.info(f"Tool provider '{tool_provider_name}' configured, awaiting connections")
            
        except Exception as e:
            logger.warning(f"Failed to load tools: {e}")
            self.tools = []
            self.tool_provider = None
        
        # Store composio auth settings if available
        self.composio_auth_configs = {}
        if self.tool_provider == "composio":
            # Load auth configs from environment
            for key, value in os.environ.items():
                if key.startswith("COMPOSIO_AUTH_CONFIG_"):
                    toolkit = key.replace("COMPOSIO_AUTH_CONFIG_", "")
                    self.composio_auth_configs[toolkit] = value
                    logger.info(f"Found auth config for {toolkit}: {value}")
    
    async def handle_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main message handler that queues messages for sequential processing.
        
        Args:
            payload: The incoming message payload
            
        Returns:
            Response dictionary or JSONResponse object
        """
        try:
            # Validate payload first
            message = Message(**payload)
            
            logger.info(f"Received {message.message_type} from {message.user_id} for conversation {message.conversation_id}")
            
            # Enqueue the message for sequential processing
            await enqueue_message_for_processing(
                message.conversation_id,
                self._process_message_internal,
                payload
            )
            
            # Return immediate acknowledgment
            return {
                "status": "queued",
                "message": "Message queued for processing",
                "conversation_id": message.conversation_id,
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            
            error_response = {
                "status": "error",
                "message": "Failed to queue message for processing",
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if JSONResponse:
                return JSONResponse(
                    status_code=500,
                    content=error_response
                )
            else:
                # Return dict if FastAPI not available
                return error_response
    
    async def _process_message_internal(self, payload: Dict[str, Any]) -> None:
        """
        Internal message processing method.
        This processes messages sequentially per conversation to prevent race conditions.
        
        Args:
            payload: The incoming message payload
        """
        start_time = time.time()
        
        try:
            # Validate payload
            message = Message(**payload)
            
            logger.info(f"Processing {message.message_type} from {message.user_id} for conversation {message.conversation_id}")
            
            # Store conversation ID for potential file sending
            self.current_conversation_id = message.conversation_id
            
            # Process the message
            if is_file_message(message.message_type, message.metadata):
                response_content = await self.process_file_message(message)
            else:
                response_content = await self.process_message(message)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            processing_speed = "fast" if processing_time_ms < 1000 else "normal" if processing_time_ms < 3000 else "slow"
            
            # Create response
            response = Response(
                content=response_content,
                agent_id=self.agent_id,
                conversation_id=message.conversation_id,
                metadata={
                    "processing_time": processing_speed,
                    "processing_time_ms": processing_time_ms,
                    "confidence": 0.9,
                    "agent_version": self.config.version,
                    "messaging_enabled": self.messaging_enabled,
                    "provider": self.config.provider,
                    "model": self.config.model
                }
            )
            
            # Send response if messaging enabled
            if self.messaging_enabled and self.messaging_client:
                await self._send_response(message, response)
            
            logger.info(f"Successfully processed message for conversation {message.conversation_id} in {processing_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Error processing message internally: {str(e)}", exc_info=True)
            
            # Send error response
            try:
                if self.messaging_enabled and self.messaging_client:
                    error_message = "I apologize, but I encountered an error processing your message. Please try again."
                    await send_text_message(
                        message.conversation_id, 
                        error_message,
                        {"error": True, "error_details": str(e)}
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error response: {send_error}")
    
    async def process_message(
        self, 
        message: Message, 
        content: Optional[Union[str, List[Dict[str, Any]]]] = None
    ) -> str:
        """
        Process message using configured LLM provider.
        
        Args:
            message: The message to process
            content: Optional custom content (can be string or content array for multimodal)
            
        Returns:
            Response content
        """
        if not self.provider_available or not self.provider:
            return f"I'm currently unable to process your request as the {self.config.provider} service is unavailable."
        
        try:
            # Store conversation ID for file operations
            self.current_conversation_id = message.conversation_id
            
            # Set current user for dynamic billing mode
            if self.config.billing_mode == "user" and hasattr(self.provider, 'set_current_user'):
                self.provider.set_current_user(message.user_id)
            
            # Reload tools for the specific user if using user billing mode and Composio
            if self.config.billing_mode == "user" and self.tool_provider == "composio":
                # Reinitialize tools for this specific user
                self._init_tools(user_id=message.user_id)
                logger.info(f"Reloaded {len(self.tools)} tools for user {message.user_id}")
            
            # Get conversation history
            from .messaging import get_conversation_history
            history = await get_conversation_history(
                message.conversation_id, 
                limit=10, 
                provider=self.config.provider
            )
            
            # Build messages list
            messages = []
            
            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add history
            if history:
                messages.extend(history)
            
            # Add current message
            if content is not None:
                messages.append({
                    "role": "user",
                    "content": content
                })
            else:
                messages.append({
                    "role": "user",
                    "content": message.content
                })
            
            # Check for special OpenAI commands before processing
            if self.config.provider == "openai" and isinstance(message.content, str):
                lower_content = message.content.lower()
                
                # Handle image generation
                if lower_content.startswith("generate image:") or lower_content.startswith("dall-e:"):
                    return await self._handle_image_generation(message.content)
                
                # Handle text-to-speech
                elif lower_content.startswith("tts:") or lower_content.startswith("speak:"):
                    return await self._handle_tts(message.content)
            
            # Check if provider is OpenAI and we should use tools
            if self.config.provider == "openai" and self.config.use_tools:
                return await self._process_with_openai_tools(messages)
            
            # Process with provider (standard path)
            response = await self.provider.process(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                return_full_response=True if self.tools else False
            )
            
            # Handle Composio tool calls if present
            if self.tools and isinstance(response, dict) and response.get("tool_calls") and self.tool_provider == "composio":
                # For Composio tools, use the built-in handle_tool_calls method
                tool_provider = get_tool_provider("composio")
                # Use Composio's handle_tool_calls which returns the raw API response
                tool_results = tool_provider.handle_tool_calls(response=response, user_id=message.user_id)
                
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": response.get("content") or "",
                    "tool_calls": response["tool_calls"]
                })
                
                # Add tool results as tool messages
                # Convert Composio results to OpenAI tool message format
                if isinstance(tool_results, list):
                    for i, result in enumerate(tool_results):
                        messages.append({
                            "role": "tool",
                            "tool_call_id": response["tool_calls"][i]["id"],
                            "content": json.dumps(result)
                        })
                else:
                    # Single result
                    messages.append({
                        "role": "tool",
                        "tool_call_id": response["tool_calls"][0]["id"],
                        "content": json.dumps(tool_results)
                    })
                
                # Get final response from LLM after tool execution
                final_response = await self.provider.process(
                    messages=messages,
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                return final_response
            
            # No tool calls, return regular response
            return response.get("content", "") if isinstance(response, dict) else response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def process_file_message(self, message: Message) -> str:
        """
        Process messages containing files.
        
        Args:
            message: Message with file metadata
            
        Returns:
            Response content
        """
        try:
            file_info = get_file_info(message.metadata)
            if not file_info:
                return "I received a file but couldn't extract its information."
            
            # Download the file
            file_path = await download_file(
                file_info['url'],
                file_info['name'],
                self.file_cache_dir
            )
            
            if not file_path:
                return f"I received your file '{file_info['name']}' but had trouble downloading it."
            
            # Get file type
            file_type = get_file_type(file_info['mime_type'])
            user_text = message.content or "What's in this file?"
            
            # Handle different file types
            if file_type == 'image':
                # For images, create multimodal content
                base64_data, mime_type = encode_file_base64(file_path)
                content = [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_data}"
                        }
                    }
                ]
                
                # Ensure we're using a vision-capable model
                if self.config.provider == "openai" and hasattr(self.provider, 'is_vision_model'):
                    if not self.provider.is_vision_model(self.config.model):
                        # Switch to vision model
                        original_model = self.config.model
                        self.config.model = "gpt-4o-mini"
                        response = await self.process_message(message, content)
                        self.config.model = original_model  # Restore
                        return response
                
            elif file_type == 'audio':
                # Handle audio transcription
                if self.config.provider == "openai" and hasattr(self.provider, 'transcribe'):
                    try:
                        transcription = await self.provider.transcribe(str(file_path))
                        content = f"{user_text}\n\nTranscription of audio file '{file_info['name']}':\n\n{transcription}"
                    except Exception as e:
                        logger.error(f"Error transcribing audio: {e}")
                        content = f"{user_text}\n\n[Audio file '{file_info['name']}' - transcription failed]"
                else:
                    content = f"{user_text}\n\n[Audio file '{file_info['name']}' - transcription not available for {self.config.provider}]"
            
            else:
                # For other file types, create text content
                content = create_file_content(file_path, file_info['mime_type'], user_text)
            
            # Process with LLM
            return await self.process_message(message, content)
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return "I received your file but encountered an error processing it."
    
    def register_tool(self, tool_definition: Dict[str, Any], handler: callable):
        """
        Register a custom tool for OpenAI function calling.
        
        Args:
            tool_definition: OpenAI tool definition dict with type, function name, description, parameters
            handler: Async callable that handles the tool execution
        """
        if not self.config.use_tools or self.config.provider != "openai":
            raise ValueError("Custom tools require use_tools=True and provider='openai'")
        
        # Add to tools list
        self.openai_tools.append(tool_definition)
        
        # Register handler
        tool_name = tool_definition["function"]["name"]
        self.custom_tool_handlers[tool_name] = handler
        
        logger.info(f"Registered custom tool: {tool_name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "status": "healthy",
            "agent_name": self.config.name,
            "agent_version": self.config.version,
            "services": {
                "provider": self.provider_available,
                "provider_name": self.config.provider,
                "tools": len(self.tools) > 0,
                "tool_provider": self.tool_provider,
                "messaging": self.messaging_enabled
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get status of message queues for debugging."""
        try:
            from .messaging import get_queue_status
            return get_queue_status()
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {"error": str(e)}
    
    async def _handle_image_generation(self, prompt: str) -> str:
        """Handle image generation requests for OpenAI provider."""
        try:
            # Extract the actual prompt
            if ":" in prompt:
                image_prompt = prompt.split(":", 1)[1].strip()
            else:
                # Fallback if no colon
                image_prompt = prompt.replace("generate image", "").replace("dall-e", "").strip()
            
            if not image_prompt:
                return "Please provide a prompt for image generation. Example: 'generate image: a sunset over mountains'"
            
            # Generate image with DALL-E 3, requesting base64 to avoid URL expiration
            images = await self.provider.generate_image(
                prompt=image_prompt,
                model="dall-e-3",
                size="1024x1024",
                quality="standard",
                style="vivid",
                response_format="b64_json"  # Get base64 instead of URL
            )
            
            if not images:
                return "Failed to generate image"
            
            image_data = images[0]
            response_parts = [f"Generated image for: '{image_prompt}'"]
            
            # Handle base64 image data
            if 'b64_json' in image_data:
                # Decode and save image
                image_bytes = base64.b64decode(image_data['b64_json'])
                save_path = Path(f"/tmp/dalle_generated_{hash(image_prompt)}.png")
                save_path.write_bytes(image_bytes)
                
                # Send as file attachment
                try:
                    await send_file_message(
                        self.current_conversation_id,
                        str(save_path),
                        caption="DALL-E 3 generated image",
                        metadata={
                            "source": "dall-e-3",
                            "prompt": image_prompt,
                            "revised_prompt": image_data.get('revised_prompt', image_prompt)
                        }
                    )
                    
                    if 'revised_prompt' in image_data:
                        response_parts.append(f"\nRevised prompt: {image_data['revised_prompt']}")
                    
                except Exception as e:
                    logger.error(f"Failed to send image file: {e}")
                    response_parts.append(f"\nGenerated image but failed to send: {str(e)}")
            
            # Fallback: Handle URL if API returns it despite our request
            elif 'url' in image_data:
                # Download the image before URL expires
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_data['url'])
                        if response.status_code == 200:
                            save_path = Path(f"/tmp/dalle_downloaded_{hash(image_prompt)}.png")
                            save_path.write_bytes(response.content)
                            
                            # Send as file
                            await send_file_message(
                                self.current_conversation_id,
                                str(save_path),
                                caption="DALL-E 3 generated image",
                                metadata={
                                    "source": "dall-e-3",
                                    "prompt": image_prompt,
                                    "revised_prompt": image_data.get('revised_prompt', image_prompt)
                                }
                            )
                            
                            if 'revised_prompt' in image_data:
                                response_parts.append(f"\nRevised prompt: {image_data['revised_prompt']}")
                        else:
                            response_parts.append(f"\nFailed to download image from URL")
                except Exception as e:
                    logger.error(f"Failed to download/send image: {e}")
                    response_parts.append(f"\nImage URL: {image_data['url']}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return f"Image generation failed: {str(e)}"
    
    async def _handle_tts(self, text: str) -> str:
        """Handle text-to-speech requests for OpenAI provider."""
        try:
            # Extract text to speak
            if ":" in text:
                speak_text = text.split(":", 1)[1].strip()
            else:
                speak_text = text.replace("tts", "").replace("speak", "").strip()
            
            if not speak_text:
                return "Please provide text to convert to speech. Example: 'tts: Hello world'"
            
            # Generate speech
            audio_data = await self.provider.generate_speech(
                text=speak_text,
                model="tts-1",
                voice="alloy",
                response_format="mp3"
            )
            
            # Save audio file
            audio_path = Path(f"/tmp/tts_output_{hash(speak_text)}.mp3")
            audio_path.write_bytes(audio_data)
            
            # Send as file
            try:
                await send_file_message(
                    self.current_conversation_id,
                    str(audio_path),
                    caption=f"Text-to-speech: '{speak_text}'",
                    metadata={
                        "source": "tts-1",
                        "text": speak_text,
                        "voice": "alloy"
                    }
                )
                
                return f"Generated speech for: '{speak_text}'\nAudio sent as attachment ({len(audio_data)} bytes)"
                
            except Exception as e:
                logger.error(f"Failed to send audio file: {e}")
                return f"Generated speech but failed to send: {str(e)}"
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return f"Text-to-speech failed: {str(e)}"
    
    async def _send_response(self, original_message: Message, response: Response):
        """Send response back to conversation."""
        try:
            metadata = {
                "response_type": "agent_response",
                "agent_id": self.agent_id,
            }
            
            if original_message.metadata and "messageId" in original_message.metadata:
                metadata["in_reply_to"] = original_message.metadata["messageId"]
            
            await send_text_message(
                original_message.conversation_id,
                response.content,
                metadata
            )
        except Exception as e:
            logger.error(f"Failed to send response: {e}")
    
    async def _process_with_openai_tools(self, messages: List[Dict[str, Any]]) -> str:
        """Process messages with OpenAI function calling tools."""
        import json
        
        try:
            # Make API call with dynamic tools list
            response = await self.provider.process(
                messages=messages,
                model=self.config.model,
                tools=self.openai_tools,
                tool_choice="auto",
                return_full_response=True
            )
            
            # Handle tool calls if present
            if response.get("tool_calls"):
                tool_results = []
                
                for tool_call in response["tool_calls"]:
                    # Handle both object and dict formats
                    if hasattr(tool_call, 'function'):
                        # It's an object
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        tool_call_id = tool_call.id
                    else:
                        # It's a dict
                        function_name = tool_call["function"]["name"]
                        function_args = json.loads(tool_call["function"]["arguments"])
                        tool_call_id = tool_call["id"]
                    
                    logger.info(f"Executing tool: {function_name} with args: {function_args}")
                    
                    # Execute the tool
                    if function_name == "generate_image":
                        result = await self._openai_generate_image(**function_args)
                    elif function_name == "text_to_speech":
                        result = await self._openai_text_to_speech(**function_args)
                    elif function_name == "transcribe_audio":
                        result = await self._openai_transcribe_audio(**function_args)
                    elif function_name in self.custom_tool_handlers:
                        # Execute custom tool
                        handler = self.custom_tool_handlers[function_name]
                        result = await handler(**function_args)
                        # Convert result to string if needed
                        if not isinstance(result, str):
                            result = json.dumps(result)
                    else:
                        result = f"Unknown tool: {function_name}"
                    
                    tool_results.append({
                        "tool_call_id": tool_call_id,
                        "role": "tool",
                        "content": result
                    })
                
                # Add assistant message with tool calls
                # Convert tool calls to dict format if needed
                tool_calls_dict = []
                for tc in response["tool_calls"]:
                    if hasattr(tc, 'model_dump'):
                        tool_calls_dict.append(tc.model_dump())
                    else:
                        tool_calls_dict.append(tc)
                
                messages.append({
                    "role": "assistant",
                    "content": response.get("content"),
                    "tool_calls": tool_calls_dict
                })
                
                # Add tool results
                messages.extend(tool_results)
                
                # Get final response
                final_response = await self.provider.process(
                    messages=messages,
                    model=self.config.model
                )
                
                return final_response
            else:
                # No tool calls, return regular response
                return response.get("content", "")
                
        except Exception as e:
            logger.error(f"Error processing with OpenAI tools: {e}")
            raise
    
    async def _openai_generate_image(self, prompt: str, style: str = "vivid", quality: str = "standard") -> str:
        """Generate an image using DALL-E 3."""
        try:
            from .messaging import send_file_message as send_file, send_text_message as send_text
            
            # Send progress indicator if enabled
            if self.config.show_progress_indicators and self.current_conversation_id:
                await send_text(
                    self.current_conversation_id,
                    "🎨 Creating your image... This may take a moment."
                )
            
            # Generate image
            images = await self.provider.generate_image(
                prompt=prompt,
                model="dall-e-3",
                size="1024x1024",
                quality=quality,
                style=style,
                response_format="b64_json"
            )
            
            if not images:
                return "Failed to generate image"
            
            image_data = images[0]
            
            # Save image
            if 'b64_json' in image_data:
                image_bytes = base64.b64decode(image_data['b64_json'])
                save_path = Path(f"/tmp/dalle_generated_{hash(prompt)}.png")
                save_path.write_bytes(image_bytes)
                
                # Send as file
                await send_file(
                    self.current_conversation_id,
                    str(save_path),
                    caption="DALL-E 3 generated image",
                    metadata={
                        "source": "dall-e-3",
                        "prompt": prompt,
                        "revised_prompt": image_data.get('revised_prompt', prompt)
                    }
                )
                
                result = f"Successfully generated image for: '{prompt}'"
                if 'revised_prompt' in image_data:
                    result += f"\nRevised prompt: {image_data['revised_prompt']}"
                
                return result
            
            return "Image generation failed - no data returned"
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return f"Image generation failed: {str(e)}"
    
    async def _openai_text_to_speech(self, text: str, voice: str = "alloy") -> str:
        """Convert text to speech."""
        try:
            from .messaging import send_file_message as send_file
            
            # Generate speech
            audio_data = await self.provider.generate_speech(
                text=text,
                model="tts-1",
                voice=voice,
                response_format="mp3"
            )
            
            # Save audio file
            save_path = Path(f"/tmp/tts_output_{hash(text)}.mp3")
            save_path.write_bytes(audio_data)
            
            # Send as file
            await send_file(
                self.current_conversation_id,
                str(save_path),
                caption=f"Text-to-speech: '{text[:50]}...'",
                metadata={
                    "model": "tts-1",
                    "voice": voice,
                    "text": text
                }
            )
            
            return f"Successfully converted text to speech using voice '{voice}'"
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return f"Text-to-speech failed: {str(e)}"
    
    async def _openai_transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio file."""
        try:
            from .messaging import send_text_message as send_text
            
            # Send progress indicator if enabled
            if self.config.show_progress_indicators and self.current_conversation_id:
                await send_text(
                    self.current_conversation_id,
                    "🎵 Transcribing audio... This may take a moment."
                )
            
            # If it's a URL, we need to download it first
            if audio_path.startswith('http'):
                from .utils.files import download_file
                
                # Extract filename from URL
                filename = audio_path.split('/')[-1]
                if '?' in filename:
                    filename = filename.split('?')[0]
                
                # Download to temp directory
                temp_dir = Path(tempfile.gettempdir()) / "demiurg_agent_files"
                temp_dir.mkdir(exist_ok=True)
                
                file_path = await download_file(audio_path, filename, temp_dir)
                if not file_path:
                    return f"Failed to download audio file from: {audio_path}"
                
                audio_path = str(file_path)
            
            # Check if file exists
            if not Path(audio_path).exists():
                return f"Audio file not found at: {audio_path}"
            
            # Transcribe
            transcription = await self.provider.transcribe(
                audio_path,
                model="whisper-1"
            )
            
            return f"Transcription: {transcription}"
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return f"Transcription failed: {str(e)}"
    
    async def check_composio_connection(self, toolkit: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if user has an active Composio connection for a toolkit."""
        if self.tool_provider != "composio":
            return {"connected": False, "error": "Composio not configured"}
        
        try:
            from .utils.tools import get_tool_provider
            
            if user_id is None:
                user_id = os.getenv("COMPOSIO_USER_ID", "default")
            
            provider = get_tool_provider("composio")
            status = provider.get_connection_status(user_id, toolkit)
            
            logger.info(f"Connection status for {toolkit}: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Error checking Composio connection: {e}")
            return {"connected": False, "error": str(e)}
    
    async def initiate_composio_auth(
        self, 
        toolkit: str, 
        user_id: str,
        auth_config_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate Composio authentication flow for a toolkit."""
        if self.tool_provider != "composio":
            return {
                "success": False, 
                "error": "Composio not configured as tool provider"
            }
        
        try:
            from .utils.tools import get_tool_provider
            from .messaging import send_text_message
            
            # Check if already connected
            status = await self.check_composio_connection(toolkit, user_id)
            if status.get("connected"):
                return {
                    "success": True,
                    "already_connected": True,
                    "message": f"You're already connected to {toolkit}! No need to re-authorize.",
                    "connection_id": status.get("connection_id")
                }
            
            # Get auth config ID
            if auth_config_id is None:
                # Check environment variable
                auth_config_id = self.composio_auth_configs.get(toolkit.upper())
                if not auth_config_id:
                    auth_config_id = os.getenv(f"COMPOSIO_AUTH_CONFIG_{toolkit.upper()}")
            
            if not auth_config_id:
                return {
                    "success": False,
                    "error": f"No auth config ID found for {toolkit}. Please add it to composio-tools.txt or set COMPOSIO_AUTH_CONFIG_{toolkit.upper()} environment variable."
                }
            
            # Initiate connection
            provider = get_tool_provider("composio")
            result = provider.initiate_connection(user_id, auth_config_id)
            
            # Send auth URL to user if we have a conversation context
            if self.messaging_enabled and self.current_conversation_id:
                auth_message = f"🔐 Please authorize {toolkit} access:\n\n👉 {result['redirect_url']}\n\nI'll wait for you to complete the authorization."
                await send_text_message(
                    self.current_conversation_id,
                    auth_message,
                    {"auth_flow": True, "toolkit": toolkit}
                )
            
            return {
                "success": True,
                "redirect_url": result["redirect_url"],
                "connection_request": result["connection_request"],
                "message": f"Please visit the URL to authorize {toolkit} access"
            }
            
        except Exception as e:
            logger.error(f"Error initiating Composio auth: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def wait_for_composio_auth(
        self, 
        connection_request, 
        timeout: int = 300
    ) -> bool:
        """Wait for user to complete Composio authorization."""
        if self.tool_provider != "composio":
            return False
        
        try:
            from .utils.tools import get_tool_provider
            from .messaging import send_text_message
            
            provider = get_tool_provider("composio")
            success = provider.wait_for_connection(connection_request, timeout)
            
            if success and self.messaging_enabled and self.current_conversation_id:
                await send_text_message(
                    self.current_conversation_id,
                    "✅ Authorization successful! The tools are now available.",
                    {"auth_completed": True}
                )
                
                # Reinitialize tools to include newly connected toolkit
                self._init_tools()
            
            return success
            
        except Exception as e:
            logger.error(f"Error waiting for Composio auth: {e}")
            return False
    
    async def handle_composio_auth_in_conversation(
        self, 
        message: Message,
        toolkit: str
    ) -> str:
        """Handle Composio authentication flow within a conversation."""
        user_id = message.user_id
        
        # Initiate auth
        auth_result = await self.initiate_composio_auth(toolkit, user_id)
        
        if not auth_result["success"]:
            return f"❌ Failed to initiate authorization: {auth_result.get('error', 'Unknown error')}"
        
        if auth_result.get("already_connected"):
            return auth_result["message"]
        
        # Wait for authorization
        connection_request = auth_result.get("connection_request")
        if connection_request:
            success = await self.wait_for_composio_auth(connection_request)
            if success:
                return f"✅ Successfully connected to {toolkit}! You can now use all {toolkit} tools."
            else:
                return f"❌ Authorization timed out or was cancelled. Please try again."
        
        return auth_result.get("message", "Please complete the authorization process.")


