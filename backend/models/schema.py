from typing import Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """
    Configuration for AI models (OpenAI/Local LLMs).
    """

    api_key: str = Field(default="sk-...", description="API key for the AI service.")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the AI service API.",
    )
    model_name: str = Field(
        default="gpt-3.5-turbo", description="Name of the model to use."
    )
    temperature: float = Field(default=0.3, description="Sampling temperature.")
    batch_size: int = Field(
        default=10, description="Number of lines to translate per batch."
    )
    system_prompt: str = Field(
        default=(
            "你是专业的日译中字幕翻译助手。\n"
            "你将收到多行日文字幕，每行以 <L数字> 开头。\n"
            "请逐行翻译成自然、通顺的简体中文，并严格保持行号与行数不变。\n"
            "硬性要求：\n"
            "- 输出必须逐行对应输入：有多少行就输出多少行\n"
            "- 每一行必须以相同的 <L数字> 开头（例如 <L1>、<L2>...）\n"
            "- 不要合并、删除、新增任何行\n"
            "- 只输出译文，不要解释\n"
            "- 不要输出日文原文\n"
        ),
        description="System prompt for batch translation.",
    )
    fallback_prompt: str = Field(
        default=(
            "你是专业的日译中字幕翻译助手。\n"
            "任务：将输入的单行日文字幕翻译为自然、通顺的简体中文。\n"
            "要求：\n"
            "- 只输出译文，不要解释\n"
            "- 不要输出日文原文\n"
            "- 保持简短，符合字幕阅读习惯\n"
        ),
        description="System prompt for line-by-line fallback translation.",
    )


class WhisperConfig(BaseModel):
    """
    Configuration for Faster-Whisper.
    """

    model_size: str = Field(default="base", description="Whisper model size to use.")
    device: str = Field(default="auto", description="Device to use (cuda/cpu).")
    compute_type: str = Field(
        default="default", description="Quantization (int8, float16, etc.)."
    )
    language: Optional[str] = Field(
        default=None, description="Source language (auto if None)."
    )


class AppConfig(BaseModel):
    """
    Global application configuration.
    """

    theme: str = Field(default="dark", description="UI theme (light/dark).")
    output_dir: str = Field(
        default=".", description="Default output directory for subtitles."
    )
    pypi_mirror: str = Field(
        default="https://pypi.org",
        description="PyPI mirror URL for downloading dependencies.",
    )
    language: str = Field(default="en", description="UI language (en/zh).")
    log_level: str = Field(
        default="INFO", description="Log level (DEBUG/INFO/WARNING/ERROR)."
    )


class GlobalConfig(BaseModel):
    """
    Combined configuration object.
    """

    app: AppConfig = Field(default_factory=AppConfig)
    whisper: WhisperConfig = Field(default_factory=WhisperConfig)
    ai: ModelConfig = Field(default_factory=ModelConfig)
