from typing import Any, Dict, List


def format_timestamp(seconds: float) -> str:
    """
    Converts seconds to SRT timestamp format (HH:MM:SS,mmm).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def save_srt(
    segments: List[Dict[str, Any]], output_path: str, use_translated: bool = True
) -> None:
    """
    Saves subtitle segments to an SRT file.

    Args:
        segments: List of segment dictionaries containing 'start', 'end', and 'translated_text' or 'text'.
        output_path: Path where to save the .srt file.
        use_translated: If True, uses 'translated_text' if available.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, 1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])

            # Use translated text if available and requested, fallback to original text
            text = (
                segment.get("translated_text")
                if use_translated
                else segment.get("text")
            )
            if text is None:
                text = segment.get("text", "")

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
