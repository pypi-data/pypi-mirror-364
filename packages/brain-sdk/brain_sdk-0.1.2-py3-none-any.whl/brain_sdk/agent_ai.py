import json
import os
import re
from typing import Any, Dict, List, Optional, Type, Union, Literal
import requests
from brain_sdk.agent_utils import AgentUtils
from httpx import HTTPStatusError
from pydantic import BaseModel


class AgentAI:
    """AI/LLM Integration functionality for Brain Agent"""
    
    def __init__(self, agent_instance):
        """
        Initialize AgentAI with a reference to the main agent instance.
        
        Args:
            agent_instance: The main Agent instance
        """
        self.agent = agent_instance
    
    async def ai(
        self,
        *args: Any,
        system: Optional[str] = None,
        user: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: Optional[bool] = None,
        response_format: Optional[Union[Literal["auto", "json", "text"], Dict]] = None,
        context: Optional[Dict] = None,
        memory_scope: Optional[List[str]] = None,
        **kwargs,
    ) -> Any:
        """
        Universal AI method supporting multimodal inputs with intelligent type detection.

        This method provides a flexible interface for interacting with various LLMs,
        supporting text, image, audio, and file inputs. It intelligently detects
        input types and applies a hierarchical configuration system.

        Args:
            *args: Flexible inputs - text, images, audio, files, or mixed content.
                   - str: Text content, URLs, or file paths (auto-detected).
                   - bytes: Binary data (images, audio, documents).
                   - dict: Structured input with explicit keys (e.g., {"image": "url"}).
                   - list: Multimodal conversation or content list.

            system (str, optional): System prompt for AI behavior.
            user (str, optional): User message (alternative to positional args).
            schema (Type[BaseModel], optional): Pydantic model for structured output validation.
            model (str, optional): Override default model (e.g., "gpt-4", "claude-3").
            temperature (float, optional): Creativity level (0.0-2.0).
            max_tokens (int, optional): Maximum response length.
            stream (bool, optional): Enable streaming response.
            response_format (str, optional): Desired response format ('auto', 'json', 'text').
            context (Dict, optional): Additional context data to pass to the LLM.
            memory_scope (List[str], optional): Memory scopes to inject (e.g., ['workflow', 'session', 'reasoner']).
            **kwargs: Additional provider-specific parameters to pass to the LLM.

        Returns:
            Any: The AI response - raw text, structured object (if schema), or a stream.

        Examples:
            # Simple text input
            response = await app.ai("Summarize this document.")

            # System and user prompts
            response = await app.ai(
                system="You are a helpful assistant.",
                user="What is the capital of France?"
            )

            # Multimodal input with auto-detection (image URL and text)
            response = await app.ai(
                "Describe this image:",
                "https://example.com/image.jpg"
            )

            # Multimodal input with file path (audio)
            response = await app.ai(
                "Transcribe this audio:",
                "./audio.mp3"
            )

            # Structured output with Pydantic schema
            class SentimentResult(BaseModel):
                sentiment: str
                confidence: float

            result = await app.ai(
                "Analyze the sentiment of 'I love this product!'",
                schema=SentimentResult
            )

            # Override default AI configuration parameters
            response = await app.ai(
                "Generate a creative story.",
                model="gpt-4-turbo",
                temperature=0.9,
                max_tokens=500,
                stream=True
            )

            # Complex multimodal conversation
            response = await app.ai([
                {"role": "system", "content": "You are a visual assistant."},
                {"role": "user", "content": "What do you see here?"},
                "https://example.com/chart.png",
                {"role": "user", "content": "Can you explain the trend?"}
            ])
        """
        # Apply hierarchical configuration: Agent defaults < Method overrides < Runtime overrides
        final_config = self.agent.ai_config.copy(deep=True)

        # Apply method-level overrides
        if model:
            final_config.model = model
        if temperature is not None:
            final_config.temperature = temperature
        if max_tokens is not None:
            final_config.max_tokens = max_tokens
        if stream is not None:
            final_config.stream = stream
        if response_format is not None:
            if isinstance(response_format, str):
                final_config.response_format = response_format

        # TODO: Integrate memory injection based on memory_scope and self.memory_config
        # For now, just pass context if provided
        if context:
            # This would be where memory data is merged into the context
            pass

        # Prepare messages for LiteLLM
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        # Handle flexible user input with intelligent processing
        if user:
            messages.append({"role": "user", "content": user})
        elif args:
            processed_content = self._process_multimodal_args(args)
            if processed_content:
                messages.extend(processed_content)

        # Integrate LiteLLM call here
        try:
            import litellm
        except ImportError:
            raise ImportError(
                "litellm is not installed. Please install it with `pip install litellm`."
            )

        # Prepare LiteLLM parameters using the config's method
        # This leverages LiteLLM's standard environment variable handling
        litellm_params = final_config.get_litellm_params(
            messages=messages, **kwargs  # Runtime overrides have highest priority
        )

        if schema:
            # Use LiteLLM's native Pydantic model support for structured outputs
            litellm_params["response_format"] = schema

        print(f"Making LiteLLM call with params: {litellm_params}")

        try:
            response = await litellm.acompletion(**litellm_params)
            if final_config.stream:
                # For streaming, return the generator
                return response
            else:
                # For non-streaming, return the content
                content = ""
                if response and hasattr(response, "choices") and response.choices:
                    content = response.choices[0].message.content

                if content is None:
                    raise ValueError("Received empty response content from LLM.")

                if schema:
                    # Parse JSON response and validate with Pydantic schema
                    try:
                        json_data = json.loads(str(content))
                        return schema(**json_data)
                    except (json.JSONDecodeError, ValueError) as parse_error:
                        print(f"Failed to parse JSON response: {parse_error}")
                        print(f"Raw response: {content}")
                        # Fallback: try to extract JSON from the response
                        json_match = re.search(r"\{.*\}", str(content), re.DOTALL)
                        if json_match:
                            try:
                                json_data = json.loads(json_match.group())
                                return schema(**json_data)
                            except (json.JSONDecodeError, ValueError):
                                pass
                        raise ValueError(
                            f"Could not parse structured response: {content}"
                        )
                return content
        except HTTPStatusError as e:
            print(
                f"LiteLLM HTTP call failed: {e.response.status_code} - {e.response.text}"
            )
            raise
        except (
            requests.exceptions.RequestException
        ) as e:  # Catch RequestException specifically
            print(f"LiteLLM network call failed: {e}")
            if e.response is not None:  # Check if response attribute exists
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
        except Exception as e:
            print(f"LiteLLM call failed: {e}")
            raise

    def _process_multimodal_args(self, args: tuple) -> List[Dict[str, Any]]:
        """Process multimodal arguments into LiteLLM-compatible message format"""
        messages = []
        user_content = []

        for arg in args:
            detected_type = AgentUtils.detect_input_type(arg)

            if detected_type == "text":
                user_content.append({"type": "text", "text": arg})

            elif detected_type == "image_url":
                user_content.append(
                    {"type": "image_url", "image_url": {"url": arg, "detail": "high"}}
                )

            elif detected_type == "image_file":
                # Convert file to base64 data URL
                try:
                    import base64

                    with open(arg, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode()
                    ext = os.path.splitext(arg)[1].lower()
                    mime_type = AgentUtils.get_mime_type(ext)
                    data_url = f"data:{mime_type};base64,{image_data}"
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url, "detail": "high"},
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not read image file {arg}: {e}")
                    user_content.append(
                        {"type": "text", "text": f"[Image file: {arg}]"}
                    )

            elif detected_type == "audio_file":
                # For audio files, we might need transcription first
                # For now, just reference the file
                user_content.append(
                    {"type": "text", "text": f"[Audio file: {os.path.basename(arg)}]"}
                )

            elif detected_type == "document_file":
                # For documents, we might need to extract text
                # For now, just reference the file
                user_content.append(
                    {
                        "type": "text",
                        "text": f"[Document file: {os.path.basename(arg)}]",
                    }
                )

            elif detected_type == "image_base64":
                user_content.append(
                    {"type": "image_url", "image_url": {"url": arg, "detail": "high"}}
                )

            elif detected_type == "audio_base64":
                user_content.append({"type": "text", "text": "[Audio data provided]"})

            elif detected_type == "image_bytes":
                # Convert bytes to base64 data URL
                try:
                    import base64

                    image_data = base64.b64encode(arg).decode()
                    # Try to detect image type from bytes
                    if arg.startswith(b"\xff\xd8\xff"):
                        mime_type = "image/jpeg"
                    elif arg.startswith(b"\x89PNG"):
                        mime_type = "image/png"
                    elif arg.startswith(b"GIF8"):
                        mime_type = "image/gif"
                    else:
                        mime_type = "image/png"  # Default

                    data_url = f"data:{mime_type};base64,{image_data}"
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url, "detail": "high"},
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not process image bytes: {e}")
                    user_content.append(
                        {"type": "text", "text": "[Image data provided]"}
                    )

            elif detected_type == "audio_bytes":
                user_content.append({"type": "text", "text": "[Audio data provided]"})

            elif detected_type == "structured_input":
                # Handle dict with explicit keys
                if "system" in arg:
                    messages.append({"role": "system", "content": arg["system"]})
                if "user" in arg:
                    user_content.append({"type": "text", "text": arg["user"]})
                if "text" in arg:
                    user_content.append({"type": "text", "text": arg["text"]})
                if "image" in arg or "image_url" in arg:
                    image_url = arg.get("image") or arg.get("image_url")
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url, "detail": "high"},
                        }
                    )
                if "audio" in arg:
                    user_content.append(
                        {"type": "text", "text": f"[Audio: {arg['audio']}]"}
                    )
                # Handle other configuration in the dict
                for key, value in arg.items():
                    if key not in [
                        "system",
                        "user",
                        "text",
                        "image",
                        "image_url",
                        "audio",
                    ]:
                        # These might be AI configuration overrides
                        pass

            elif detected_type == "message_dict":
                # Handle message format dict
                messages.append(arg)

            elif detected_type == "conversation_list":
                # Handle list of messages
                messages.extend(arg)

            elif detected_type == "multimodal_list":
                # Handle mixed list of content
                for item in arg:
                    if isinstance(item, str):
                        user_content.append({"type": "text", "text": item})
                    elif isinstance(item, dict):
                        if "role" in item:
                            messages.append(item)
                        else:
                            # Process as structured input
                            sub_messages = self._process_multimodal_args((item,))
                            messages.extend(sub_messages)

            elif detected_type == "dict":
                # Generic dict - convert to text representation
                user_content.append(
                    {"type": "text", "text": f"Data: {json.dumps(arg, indent=2)}"}
                )

            else:
                # Fallback for unknown types
                user_content.append({"type": "text", "text": str(arg)})

        # Add user content as a message if we have any
        if user_content:
            if len(user_content) == 1 and user_content[0]["type"] == "text":
                # Simplify single text content
                messages.append({"role": "user", "content": user_content[0]["text"]})
            else:
                # Multiple content types
                messages.append({"role": "user", "content": user_content})

        return messages