#!/usr/bin/env python3
"""
Advanced Subtitle Translator (SRT to ASS)

This script translates SRT subtitle files into styled ASS format with options for
bilingual or monolingual output and different translation granularities.

Features:
- Converts SRT to ASS with rich styling.
- **Bilingual Mode**: Displays original text on top and translated text below.
- **Monolingual Mode**: Replaces original text with the translation.
- **Full Text Prompt**: Translates every line.
- **Selective Difficulty Prompt**: Translates only complex phrases, slang, or cultural references.
- **Resumable**: Automatically saves progress and can resume if interrupted.
- **Batch Processing**: Processes subtitles in batches for efficient and reliable API usage.
- Supports multiple AI providers (OpenAI, Gemini, DeepSeek).

Usage:
    python translate_subtitles.py input.srt --translation-mode bilingual --prompt-template selective_difficulty

Note: Requires an API key for the chosen provider (e.g., OPENAI_API_KEY).
"""

import argparse
import json
import os
import sys

from .console_utils import (
    Emojis,
    console,
    create_progress_bar,
    create_summary_panel,
    print_batch_info,
    print_completion_celebration,
    print_config_info,
    print_error,
    print_error_with_help,
    print_file_info,
    print_helpful_tip,
    print_info,
    print_processing,
    print_resume_info,
    print_warning,
    print_welcome_banner,
)
from .ai_translation import translate_batch
from .subtitle_handler import SubtitleHandler
from .utils import extract_media_info, generate_output_filename


def translate_subtitles(
    input_file,
    output_file=None,
    provider="openai",
    model=None,
    translation_mode="bilingual",
    prompt_template="full_text",
    batch_size=150,
    progress_callback=None,
):
    """
    Translates an SRT subtitle file to a styled ASS file with advanced options.

    Args:
        input_file (str): Path to the input SRT file.
        output_file (str, optional): Path to the output ASS file. Defaults to None.
        provider (str, optional): AI provider ('openai', 'gemini', 'deepseek'). Defaults to "openai".
        model (str, optional): Provider-specific model name. Defaults to None.
        translation_mode (str, optional): 'bilingual' or 'monolingual'. Defaults to "bilingual".
        prompt_template (str, optional): 'selective_difficulty' or 'full_text'.
            Defaults to "selective_difficulty".
        batch_size (int, optional): Number of lines to process per API call. Defaults to 150.
        progress_callback (callable, optional): Callback function for progress updates.
            Should accept (current_batch: int, total_batches: int).

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        media_info = extract_media_info(input_file)
        print_info(f"Detected: {media_info}")

        if not output_file:
            output_file = generate_output_filename(input_file, ".en-zh.ass")

        # Define paths for temporary progress files
        base_name = os.path.splitext(output_file)[0]
        progress_file = f"{base_name}.progress.json"
        translations_file = f"{base_name}.trans.json"

        subtitle_handler = SubtitleHandler()
        subs = subtitle_handler.load_subtitles(input_file)
        separator = subtitle_handler.setup_styles(subs)

        # Load existing progress if available
        translated_indices = set()
        all_translations = {}
        if os.path.exists(progress_file) and os.path.exists(translations_file):
            try:
                with open(progress_file, encoding="utf-8") as f:
                    translated_indices = set(json.load(f))
                with open(translations_file, encoding="utf-8") as f:
                    all_translations = json.load(f)
                print_resume_info(len(translated_indices))
            except (OSError, json.JSONDecodeError) as e:
                print_warning(
                    f"Could not load progress files. Starting fresh. Error: {e}"
                )
                translated_indices = set()
                all_translations = {}

        lines_to_translate, total_lines = (
            subtitle_handler.prepare_lines_for_translation(subs)
        )

        # Filter out lines that have already been translated
        untranslated_lines = [
            line for line in lines_to_translate if line[0] not in translated_indices
        ]

        if not untranslated_lines:
            print_info(
                "All lines have already been translated. Proceeding to file generation."
            )
        else:
            print_processing(
                f"Translating {len(untranslated_lines)} remaining lines..."
            )
            total_batches = (len(untranslated_lines) + batch_size - 1) // batch_size

            with create_progress_bar() as progress:
                batch_task = progress.add_task(
                    f"{Emojis.BATCH} Processing batches...", total=total_batches
                )

                for i in range(0, len(untranslated_lines), batch_size):
                    batch = untranslated_lines[i : i + batch_size]
                    batch_line_indices = [line[0] for line in batch]
                    current_batch = i // batch_size + 1

                    print_batch_info(
                        batch_line_indices[0],
                        batch_line_indices[-1],
                        current_batch,
                        total_batches,
                    )

                    new_translations = translate_batch(
                        provider=provider,
                        prompt_template=prompt_template,
                        subtitle_lines=[(idx, text) for idx, text, _, _, _ in batch],
                        media_info=media_info,
                        model=model,
                    )

                    # Update progress and save incrementally
                    all_translations.update(new_translations)
                    translated_indices.update(new_translations.keys())

                    with open(progress_file, "w", encoding="utf-8") as f:
                        json.dump(list(translated_indices), f)
                    with open(translations_file, "w", encoding="utf-8") as f:
                        json.dump(all_translations, f)

                    progress.update(batch_task, advance=1)
                    completed_msg = (
                        f"Completed batch. Total translated: "
                        f"{len(translated_indices)}/{total_lines}"
                    )
                    print_info(completed_msg)

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(current_batch, total_batches)

        # Apply translations based on the selected mode
        if translation_mode == "bilingual":
            subtitle_handler.apply_translations(subs, all_translations, separator)
        elif translation_mode == "monolingual":
            subtitle_handler.apply_translations_replace(subs, all_translations)

        subtitle_handler.save_subtitles(subs, output_file)

        # Clean up temporary files
        for temp_file in [progress_file, translations_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        # Display summary panel
        summary_panel = create_summary_panel(
            status="Success!",
            output_file=output_file,
            mode=translation_mode,
            template=prompt_template,
            provider=provider,
            translated_count=len(all_translations),
            total_count=total_lines,
        )
        console.print(summary_panel)

        # Print celebration
        print_completion_celebration(len(all_translations), total_lines)

        return True

    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        print_helpful_tip("Check your API keys and internet connection")
        import traceback

        traceback.print_exc()
        return False


def main():
    print_welcome_banner()

    parser = argparse.ArgumentParser(
        description="Advanced subtitle translator (SRT to ASS).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", help="Input SRT subtitle file.")
    parser.add_argument(
        "-o", "--output", help="Output ASS file path (default: [input_file].ass)."
    )

    # Core translation options
    parser.add_argument(
        "--translation-mode",
        choices=["bilingual", "monolingual"],
        default="bilingual",
        help="bilingual: Appends translation below original text.\n"
        "monolingual: Replaces original text with translation.",
    )
    parser.add_argument(
        "--prompt-template",
        choices=["full_text", "selective_difficulty"],
        default="full_text",
        help="full_text: Translates every line.\n"
        "selective_difficulty: Translates only complex/idiomatic lines.",
    )

    # Provider and model options
    parser.add_argument(
        "-p",
        "--provider",
        choices=["openai", "gemini", "deepseek"],
        default="deepseek",
        help="AI provider for translation (default: deepseek).",
    )
    parser.add_argument(
        "-m", "--model", help="Specific model to use (e.g., gpt-4o, gemini-1.5-pro)."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=120,
        help="Number of lines to process in each API call (default: 120).",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print_error_with_help(
            f"Input file '{args.input_file}' not found.",
            "Please check the file path and try again.",
        )
        sys.exit(1)

    if not args.input_file.lower().endswith(".srt"):
        print_error_with_help(
            "Input file must be an SRT file (*.srt).",
            "Please provide a valid SRT subtitle file.",
        )
        sys.exit(1)

    # Generate output filename if not provided
    output_file = args.output
    if not output_file:
        output_file = generate_output_filename(args.input_file, ".en-zh.ass")

    # Display file and configuration info
    print_file_info(args.input_file, output_file)
    print_config_info(
        args.provider, args.translation_mode, args.prompt_template, args.batch_size
    )

    # Add helpful tip
    print_helpful_tip(
        "Translation may take a few minutes depending on file size and batch size"
    )
    console.print()

    success = translate_subtitles(
        args.input_file,
        output_file,
        args.provider,
        args.model,
        args.translation_mode,
        args.prompt_template,
        args.batch_size,
    )

    if success:
        print_helpful_tip(
            f"You can now use the ASS file '{output_file}' with your media player"
        )
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
