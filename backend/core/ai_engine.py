from typing import List

from openai import OpenAI

from backend.services.config_mgr import config_mgr
from backend.services.logger import logger


class AIEngine:
    """
    Engine for translating subtitle segments using OpenAI-compatible LLMs.
    """

    def __init__(self) -> None:
        self.client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        """
        Returns a configured OpenAI client.

        Bypasses system proxies for local connections to avoid issues
        with system-wide proxies on Windows/WSL.
        """
        import httpx

        config = config_mgr.config.ai
        logger.debug(f"initializing_ai_client: base_url={config.base_url}")

        # trust_env=False prevents httpx from looking at system proxy environment variables
        # Set a longer timeout (60s) for local models which can be slow
        http_client = httpx.Client(trust_env=False, timeout=60.0)

        return OpenAI(
            api_key=config.api_key, base_url=config.base_url, http_client=http_client
        )

    def translate_batch(
        self, lines: List[str], target_lang: str = "Chinese"
    ) -> List[str]:
        """
        Translates a batch of subtitle lines to the target language.
        """
        if not lines:
            return []

        config = config_mgr.config.ai
        client = self._get_client()

        # Step 1: Format input with <L数字> markers as requested by prompt
        batch_lines = []
        for i, line in enumerate(lines):
            batch_lines.append(f"<L{i+1}> {line}")
        batch_text = "\n".join(batch_lines)

        logger.info(f"ai_translation_batch_started: {len(lines)} lines")

        try:
            response = client.chat.completions.create(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": config.system_prompt},
                    {"role": "user", "content": batch_text},
                ],
                temperature=config.temperature,
            )

            result_text = response.choices[0].message.content or ""
            logger.debug(f"ai_raw_response: {repr(result_text)}")

            # Parsing Step 1: Extract text by matching <L数字>
            import re

            cleaned_lines: list[str | None] = [None] * len(lines)

            # Find all patterns like <L1> Text
            matches = re.findall(r"<L(\d+)>(.*?)(?=<L\d+>|$)", result_text, re.DOTALL)

            for index_str, content in matches:
                try:
                    idx = int(index_str) - 1
                    if 0 <= idx < len(lines):
                        cleaned_lines[idx] = content.strip()
                except ValueError:
                    continue

            final_lines = []
            missing_indices: list[int] = []
            for i, seg_text in enumerate(cleaned_lines):
                if seg_text is None:
                    missing_indices.append(i)
                    final_lines.append(lines[i])  # Fallback to original
                else:
                    final_lines.append(seg_text)

            # If count mismatch or too many missing, try line-by-line fallback if config allows
            if len(missing_indices) > 0:
                logger.warning(
                    f"batch_parsing_partial_failure: missing {len(missing_indices)} lines. falling_back_to_line_by_line"
                )
                for i in missing_indices:
                    try:
                        line_resp = client.chat.completions.create(
                            model=config.model_name,
                            messages=[
                                {"role": "system", "content": config.fallback_prompt},
                                {"role": "user", "content": lines[i]},
                            ],
                            temperature=config.temperature,
                        )
                        final_lines[i] = (
                            line_resp.choices[0].message.content or lines[i]
                        ).strip()
                    except Exception as le:
                        logger.error(f"line_fallback_failed for index {i}: {le}")

            logger.info("ai_translation_batch_success")
            return final_lines

        except Exception as e:
            logger.error(f"ai_translation_failed: {e}", exc_info=True)
            # Re-raise exception to alert the user immediately
            raise e


# Global AI engine instance
ai_engine = AIEngine()
