"""
Subtitle handling functionality for the subtitle translation system.
"""

import re

import pysubs2

from . import config
from .utils import format_timestamp


def int_to_ass_color(color_int):
    """Convert integer color to ASS color format."""
    return f"&H{color_int:06X}"


class SubtitleHandler:
    """
    Handles subtitle file operations including loading, styling, and saving.
    """

    def __init__(self):
        # Compile the regex pattern for cleaning subtitle text
        self.tag_regex = re.compile(config.SRT_TAG_PATTERN)

    def load_subtitles(self, input_file):
        """
        Load subtitle file with automatic encoding detection.

        Args:
            input_file: Path to the subtitle file

        Returns:
            pysubs2.SSAFile: Subtitle object
        """
        # Try to load the subtitle file with different encodings
        encodings = ["utf-8", "utf-16", "cp1252"]
        subs = None

        for encoding in encodings:
            try:
                subs = pysubs2.load(input_file, encoding=encoding)
                print(f"Successfully read file using {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue

        if subs is None:
            raise ValueError(
                f"Failed to decode file with any of the attempted encodings: {encodings}"
            )

        return subs

    def setup_styles(self, subs):
        """
        Set up styles and info for the subtitle object.

        Args:
            subs: Subtitle object

        Returns:
            str: The formatted separator for Chinese text
        """
        # Set PlayResX and PlayResY
        subs.info["PlayResX"] = config.PLAY_RES_X
        subs.info["PlayResY"] = config.PLAY_RES_Y

        # Add EnConverted style for English text
        subs.styles[config.EN_STYLE] = pysubs2.SSAStyle(
            fontname=config.TOP_TEXT_FONTNAME,
            fontsize=config.TOP_TEXT_FONTSIZE,
            primarycolor=config.TOP_TEXT_COLOR,
            secondarycolor=config.TOP_TEXT_SECONDARY_COLOR,
            outlinecolor=config.TOP_TEXT_OUTLINE_COLOR,
            backcolor=config.TOP_TEXT_BACK_COLOR,
            bold=False,
            italic=False,
            underline=False,
            strikeout=False,
            scalex=100,
            scaley=100,
            spacing=0,
            angle=0,
            borderstyle=1,
            outline=2,
            shadow=1,
            alignment=pysubs2.common.Alignment.BOTTOM_CENTER,
            marginl=5,
            marginr=5,
            marginv=2,
        )

        # Prepare the separator with Chinese text formatting
        bottom_color_str = int_to_ass_color(config.BOTTOM_TEXT_COLOR)
        bottom_tag = (
            f"\\fn{config.BOTTOM_TEXT_FONTNAME}"
            f"\\fs{config.BOTTOM_TEXT_FONTSIZE}\\c{bottom_color_str}"
        )
        return f"\\N{{{bottom_tag}}}"

    def prepare_lines_for_translation(self, subs):
        """
        Prepare subtitle lines for translation.

        Args:
            subs: Subtitle object

        Returns:
            tuple: (lines_to_translate, total_lines)
            lines_to_translate contains tuples: (index, cleaned_text, duration, start, end)
        """
        total_lines = 0
        lines_to_translate = []

        for i, line in enumerate(subs):
            if line.type == "Dialogue":
                line.style = config.EN_STYLE
                total_lines += 1

                # Calculate duration in milliseconds
                duration_ms = line.end - line.start

                # Clean the text: remove tags and replace \N with space
                cleaned_text = self.tag_regex.sub("", line.text)
                cleaned_text = cleaned_text.replace("\\N", " ").strip()

                # Store line index, cleaned text, duration, start time, and end time
                lines_to_translate.append(
                    (i, cleaned_text, duration_ms, line.start, line.end)
                )

        return lines_to_translate, total_lines

    def apply_translations(self, subs, translations, separator):
        """
        Apply translations to subtitle lines.

        Args:
            subs: Subtitle object
            translations: Dictionary of translations
            separator: Formatted separator for Chinese text
        """
        for i, line in enumerate(subs):
            if i in translations and translations[i]:
                # Add the translated text as bottom text
                line.text = f"{line.text}{separator}{translations[i]}"

    def apply_translations_replace(self, subs, translations):
        """
        Apply translations by replacing the original text.

        Args:
            subs: Subtitle object
            translations: Dictionary of translations
        """
        for i, line in enumerate(subs):
            if i in translations and translations[i]:
                # Replace the original text with the translated text
                line.text = translations[i]

    def save_subtitles(self, subs, output_file):
        """
        Save the subtitle file as ASS.

        Args:
            subs: Subtitle object
            output_file: Path to the output file
        """
        subs.save(output_file, encoding="utf-8")
        print(f"Saved subtitle file to: {output_file}")

    def create_timestamp_mapping(self, batch):
        """
        Create a mapping from timestamp to line index for a batch of subtitle lines.

        Args:
            batch: List of subtitle line tuples

        Returns:
            dict: Mapping from timestamp string to line index
        """
        timestamp_to_idx = {}
        for idx, _, _, start_ms, end_ms in batch:
            timestamp = f"{format_timestamp(start_ms)}-->{format_timestamp(end_ms)}"
            timestamp_to_idx[timestamp] = idx
        return timestamp_to_idx
