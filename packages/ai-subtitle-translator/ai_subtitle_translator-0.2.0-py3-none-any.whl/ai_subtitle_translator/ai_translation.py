#!/usr/bin/env python3
"""
This module provides a functional, registry-based architecture for translating text
using different LLM providers and prompt templates. It is designed to be reusable,
extensible, and easy to maintain.

Key Components:
- Provider Registry: A dictionary (`TRANSLATION_PROVIDERS`) that maps provider names
  (e.g., "openai") to their corresponding translation functions.
- Prompt Registry: A dictionary (`PROMPT_TEMPLATES`) that maps prompt template names
  (e.g., "selective") to functions that generate the final prompt string.
- Public API: A single function, `translate_batch`, serves as the entry point. It
  dynamically selects the provider and prompt template based on its arguments.

This design avoids inheritance and complex object-oriented patterns in favor of
a more straightforward, data-driven approach.
"""

import json
import os
import time
from collections.abc import Callable

# --- Provider Availability Checks ---
try:
    import openai
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# --- Constants ---
DEFAULT_OPENAI_MODEL = "gpt-4.1"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"  # Or "deepseek-coder"

# --- Prompt Template Generation ---


def _create_full_text_prompt(
    subtitle_lines: list[tuple[int, str]], media_info: str
) -> str:
    """
    Creates a prompt to translate all subtitle lines.

    Args:
        subtitle_lines: A list of tuples, where each tuple contains the
                        original line index and the text to be translated.
        media_info: A string providing context about the media (e.g., title, year).

    Returns:
        A formatted string to be used as the prompt for the LLM.
    """
    prompt_lines = [f'[{i}]: "{text}"' for i, text in subtitle_lines]
    prompt_text = "\n".join(prompt_lines)

    return f"""You are a professional subtitle translator. Translate the following batch of subtitles to Chinese for the media: {media_info}

Guidelines:
• You are processing a batch of subtitles from a larger file. Keep in mind they are part of a larger dialogue.
• If you recognize this media, use the official or widely-accepted Chinese translations for names, terms, or catchphrases.
• Maintain any special formatting like italics or emphasis.
• If a line contains wordplay, rare cultural references, or untranslatable terms, add a brief note for clarity.

Here is the current batch of subtitles to translate:
{prompt_text}

Respond in JSON format, where keys are the original line indices (as strings) and values are the Chinese translations.
TranslationResponse = dict[str, str]

Example:
{{"0": "你好，世界", "1": "这是一个测试"}}
"""


def _create_selective_difficulty_prompt(
    subtitle_lines: list[tuple[int, str]], media_info: str
) -> str:
    """
    Creates a prompt that asks the AI to selectively translate only difficult
    or complex phrases, slang, or cultural references.

    Args:
        subtitle_lines: A list of tuples, where each tuple contains the
                        original line index and the text to be translated.
        media_info: A string providing context about the media.

    Returns:
        A formatted string to be used as the prompt for the LLM.
    """
    prompt_lines = [f'[{i}]: "{text}"' for i, text in subtitle_lines]
    prompt_text = "\n".join(prompt_lines)

    return f"""You are assisting a Chinese audience in watching: {media_info}

You are processing a batch of subtitles from a larger file. The viewer understands basic English.
Your task is to provide brief notes or translations for lines in this batch that contain:
• Uncommon or advanced vocabulary and phrases
• Idioms, slang, or cultural references
• Names of people, organizations, or brands that are well-known in China
• Long or complex sentence structures

Skip lines that are simple and fully understandable.

Here is the current batch of subtitles to analyze:
{prompt_text}

Respond in JSON format, where keys are the original line indices (as strings) and values are the notes/translations.
TranslationResponse = dict[str, str]

Example:
{{"15": "subpoena: 传票", "22": "the fifth amendment: 第五修正案"}}
"""


# --- Provider-Specific Translation Functions ---


def _translate_openai(prompt: str, model: str, is_json: bool = True) -> dict[int, str]:
    """
    Sends a prompt to the OpenAI API and parses the response.

    Args:
        prompt: The prompt to send to the model.
        model: The specific OpenAI model to use.
        is_json: Whether to expect a JSON response.

    Returns:
        A dictionary mapping line indices to their translations.
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI SDK not found. Please run 'pip install openai'.")

    client = OpenAI()
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response_config = {"temperature": 0.0}
            if is_json:
                response_config["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **response_config,
            )
            content = response.choices[0].message.content

            if is_json:
                translations_str_keys = json.loads(content)
                return {int(k): v for k, v in translations_str_keys.items()}

            # Handle plain text response for full text translation
            # This part would need to align the translated lines back to original indices,
            # which can be complex. For now, we'll assume a simple split.
            lines = content.strip().split("\n")
            return dict(enumerate(lines))

        except openai.RateLimitError:
            print(f"Rate limited. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return {}
    return {}


def _translate_deepseek(
    prompt: str, model: str, is_json: bool = True
) -> dict[int, str]:
    """
    Sends a prompt to the DeepSeek API using the OpenAI-compatible client.

    Args:
        prompt: The prompt to send to the model.
        model: The specific DeepSeek model to use.
        is_json: Whether to expect a JSON response.

    Returns:
        A dictionary mapping line indices to their translations.
    """
    if not OPENAI_AVAILABLE:  # DeepSeek uses the OpenAI client
        raise ImportError("OpenAI SDK not found. Please run 'pip install openai'.")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")

    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com/v1"
    )
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response_config = {"temperature": 0.0}
            if is_json:
                response_config["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **response_config,
            )
            content = response.choices[0].message.content

            if is_json:
                translations_str_keys = json.loads(content)
                return {int(k): v for k, v in translations_str_keys.items()}

            lines = content.strip().split("\n")
            return dict(enumerate(lines))

        except openai.RateLimitError:
            print(f"Rate limited. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return {}
    return {}


def _translate_gemini(prompt: str, model: str, is_json: bool = True) -> dict[int, str]:
    """
    Sends a prompt to the Google Gemini API and parses the response.

    Args:
        prompt: The prompt to send to the model.
        model: The specific Gemini model to use.
        is_json: Whether to expect a JSON response.

    Returns:
        A dictionary mapping line indices to their translations.
    """
    if not GEMINI_AVAILABLE:
        raise ImportError(
            "Google Generative AI SDK not found. Please run 'pip install google-generativeai'."
        )

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    max_retries = 3
    retry_delay = 5

    generation_config = genai.types.GenerationConfig(temperature=0.0)
    if is_json:
        generation_config.response_mime_type = "application/json"

    model = genai.GenerativeModel(model, generation_config=generation_config)

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)

            if is_json:
                translations_str_keys = json.loads(response.text)
                return {int(k): v for k, v in translations_str_keys.items()}

            lines = response.text.strip().split("\n")
            return dict(enumerate(lines))

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                return {}
    return {}


# --- Registries ---

PROMPT_TEMPLATES: dict[str, Callable] = {
    "full_text": _create_full_text_prompt,
    "selective_difficulty": _create_selective_difficulty_prompt,
}

TRANSLATION_PROVIDERS: dict[str, Callable] = {
    "openai": _translate_openai,
    "gemini": _translate_gemini,
    "deepseek": _translate_deepseek,
}

# --- Public API ---


def translate_batch(
    provider: str,
    prompt_template: str,
    subtitle_lines: list[tuple[int, str]],
    media_info: str,
    model: str | None = None,
) -> dict[int, str]:
    """
    Translates a batch of subtitle lines using a specified provider and prompt template.

    This function acts as the main entry point for the translation module. It uses
    the registries to dynamically select the correct functions for prompt generation
    and translation.

    Args:
        provider: The name of the translation provider (e.g., "openai").
        prompt_template: The name of the prompt template to use (e.g., "selective").
        subtitle_lines: The list of subtitle lines to translate.
        media_info: Contextual information about the media.
        model: The specific model to use (optional).

    Returns:
        A dictionary of translations.

    Raises:
        ValueError: If the specified provider or prompt template is not supported.
    """
    # 1. Select the prompt generation function from the registry
    prompt_function = PROMPT_TEMPLATES.get(prompt_template)
    if not prompt_function:
        supported_templates = list(PROMPT_TEMPLATES.keys())
        raise ValueError(
            f"Unsupported prompt template: '{prompt_template}'. "
            f"Supported: {supported_templates}"
        )

    # 2. Select the translation function from the registry
    provider_function = TRANSLATION_PROVIDERS.get(provider)
    if not provider_function:
        raise ValueError(
            f"Unsupported provider: '{provider}'. Supported: {list(TRANSLATION_PROVIDERS.keys())}"
        )

    # 3. Determine the model to use
    if not model:
        if provider == "openai":
            model = DEFAULT_OPENAI_MODEL
        elif provider == "gemini":
            model = DEFAULT_GEMINI_MODEL
        elif provider == "deepseek":
            model = DEFAULT_DEEPSEEK_MODEL

    print(f"Using provider: {provider}, model: {model}, prompt: {prompt_template}")

    # 4. Generate the prompt
    prompt = prompt_function(subtitle_lines, media_info)

    # 5. Execute the translation
    translations = provider_function(prompt, model, is_json=True)

    return translations
