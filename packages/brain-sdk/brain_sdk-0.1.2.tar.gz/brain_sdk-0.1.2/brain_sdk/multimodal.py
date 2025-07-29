from typing import Union, Literal
from pydantic import BaseModel, Field

class Text(BaseModel):
    """Represents text content in a multimodal prompt."""
    type: Literal["text"] = "text"
    text: str = Field(..., description="The text content.")

class Image(BaseModel):
    """Represents image content in a multimodal prompt."""
    type: Literal["image_url"] = "image_url"
    image_url: Union[str, dict] = Field(..., description="The URL of the image, or a dictionary with 'url' and optional 'detail' (e.g., {'url': 'https://example.com/image.jpg', 'detail': 'high'}).")

class Audio(BaseModel):
    """Represents audio content in a multimodal prompt."""
    type: Literal["audio"] = "audio"
    audio: Union[str, dict] = Field(..., description="The URL of the audio file, or a dictionary with 'url' and optional 'format'.")

class File(BaseModel):
    """Represents a generic file content in a multimodal prompt."""
    type: Literal["file"] = "file"
    file: Union[str, dict] = Field(..., description="The URL of the file, or a dictionary with 'url' and optional 'mime_type'.")

# Union type for all multimodal content types
MultimodalContent = Union[Text, Image, Audio, File]
