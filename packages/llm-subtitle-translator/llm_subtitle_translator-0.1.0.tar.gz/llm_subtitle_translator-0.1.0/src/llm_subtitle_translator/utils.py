"""
Utility functions for the subtitle translation system.
"""

import os
import re


def extract_media_info(filename: str) -> str:
    """
    Extract media information (title, year, season, episode) from the filename.

    Args:
        filename: The name of the subtitle file

    Returns:
        A string with the extracted media information
    """
    base_filename = os.path.basename(filename)

    # Try to match movie pattern: "Title (yyyy) ..."
    movie_match = re.search(r"(.+?)\s*\((\d{4})\)", base_filename)
    if movie_match:
        title = movie_match.group(1).strip()
        year = movie_match.group(2)
        return f"Movie: {title} ({year})"

    # Try to match TV show pattern: "Title - SxxExx - ..."
    tv_match = re.search(r"(.+?)\s*-\s*S(\d+)E(\d+)\s*-", base_filename)
    if tv_match:
        title = tv_match.group(1).strip()
        season = tv_match.group(2)
        episode = tv_match.group(3)
        return f"TV Show: {title}, Season {int(season)}, Episode {int(episode)}"

    # If no pattern matches, return the filename without extension
    name_without_ext, _ = os.path.splitext(base_filename)
    return f"Media: {name_without_ext}"


def format_timestamp(ms: int) -> str:
    """
    Format milliseconds into a timestamp string (HH:MM:SS,mmm).

    Args:
        ms: Time in milliseconds

    Returns:
        Formatted timestamp string
    """
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def generate_output_filename(input_file: str, new_ext: str = ".ass") -> str:
    """
    Generate an output filename based on the input file, with a new extension.

    Args:
        input_file: Path to the input file.
        new_ext: The new extension for the output file (e.g., ".ass").

    Returns:
        Path to the output file.
    """
    # Get the base filename without extension
    base_path, _ = os.path.splitext(input_file)

    # Remove common language suffixes if present (e.g., .en, .zh)
    for lang_suffix in [".en", ".zh", ".eng"]:
        if base_path.endswith(lang_suffix):
            base_path = base_path[: -len(lang_suffix)]
            break

    # Create output filename with the new extension
    return f"{base_path}{new_ext}"
