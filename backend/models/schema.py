from typing import Optional
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    """
    Configuration for AI models (OpenAI/Local LLMs).
    """
    api_key: str = Field(default="sk-...", description="API key for the AI service.")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the AI service API."
    )
    model_name: str = Field(default="gpt-3.5-turbo", description="Name of the model to use.")
    temperature: float = Field(default=0.3, description="Sampling temperature.")
    batch_size: int = Field(default=10, description="Number of lines to translate per batch.")

class WhisperConfig(BaseModel):
    """
    Configuration for Faster-Whisper.
    """
    model_size: str = Field(default="base", description="Whisper model size to use.")
    device: str = Field(default="auto", description="Device to use (cuda/cpu).")
    compute_type: str = Field(default="default", description="Quantization (int8, float16, etc.).")
    language: Optional[str] = Field(default=None, description="Source language (auto if None).")

class AppConfig(BaseModel):
    """
    Global application configuration.
    """
    theme: str = Field(default="dark", description="UI theme (light/dark).")
    output_dir: str = Field(default=".", description="Default output directory for subtitles.")
    ffmpeg_path: Optional[str] = Field(default=None, description="Manual path to ffmpeg binary.")

class GlobalConfig(BaseModel):
    """
    Combined configuration object.
    """
    app: AppConfig = Field(default_factory=AppConfig)
    whisper: WhisperConfig = Field(default_factory=WhisperConfig)
    ai: ModelConfig = Field(default_factory=ModelConfig)
