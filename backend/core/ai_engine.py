from typing import List
from openai import OpenAI
from backend.services.logger import logger
from backend.services.config_mgr import config_mgr

class AIEngine:
    """
    Engine for translating subtitle segments using OpenAI-compatible LLMs.
    """

    def __init__(self) -> None:
        self.client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        """
        Returns a configured OpenAI client.
        """
        config = config_mgr.config.ai
        return OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def translate_batch(self, lines: List[str], target_lang: str = "Chinese") -> List[str]:
        """
        Translates a batch of subtitle lines to the target language.

        Args:
            lines (List[str]): List of source text lines.
            target_lang (str): Target language for translation.

        Returns:
            List[str]: List of translated text lines.
        """
        if not lines:
            return []

        config = config_mgr.config.ai
        client = self._get_client()

        # Construct prompt for batch translation to preserve context
        prompt = (
            f"You are a professional subtitle translator. Translate the following subtitles into {target_lang}. "
            "Maintain the context and tone. Keep the same number of lines. Return ONLY the translated lines, "
            "one per line, without any numbering or extra text.\n\n"
        )
        prompt += "\n".join(lines)

        logger.info(f"ai_translation_batch_started: {len(lines)} lines")

        try:
            response = client.chat.completions.create(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature
            )

            result_text = response.choices[0].message.content or ""
            translated_lines = [line.strip() for line in result_text.strip().split("\n") if line.strip()]

            # Basic verification: line count should match
            if len(translated_lines) != len(lines):
                logger.warning(
                    f"translation_line_count_mismatch: expected {len(lines)}, got {len(translated_lines)}"
                )
                # If mismatch, we might need a more robust strategy, 
                # but for now we'll just return what we got or pad/truncate.
                if len(translated_lines) < len(lines):
                    translated_lines += [""] * (len(lines) - len(translated_lines))
                else:
                    translated_lines = translated_lines[:len(lines)]

            logger.info("ai_translation_batch_success")
            return translated_lines

        except Exception as e:
            logger.error(f"ai_translation_failed: {e}", exc_info=True)
            # Fallback to returning original lines if AI fails
            return lines

# Global AI engine instance
ai_engine = AIEngine()
