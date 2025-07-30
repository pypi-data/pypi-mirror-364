import locale
import os
from pathlib import Path

import click
import llm
from llm import hookimpl
from llm.cli import get_default_model

try:
    import pyclip
except ImportError:
    pyclip = None

SYSTEM_PROMPT = """
First, detect the source language of the input text.

You have two preferred languages as target languages: {second_language} and {system_language}.
Translate the text into the first preferred language that is different from the detected source language.

Return only the translated text as a string, with no explanations or extra output.
"""


lang_map = {
    "af": "afrikaans",
    "ar": "arabic",
    "bg": "bulgarian",
    "bn": "bengali",
    "ca": "catalan",
    "cs": "czech",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "et": "estonian",
    "fa": "persian",
    "fi": "finnish",
    "fr": "french",
    "he": "hebrew",
    "hi": "hindi",
    "hr": "croatian",
    "hu": "hungarian",
    "id": "indonesian",
    "it": "italian",
    "ja": "japanese",
    "ko": "korean",
    "lt": "lithuanian",
    "lv": "latvian",
    "mk": "macedonian",
    "ms": "malay",
    "nb": "norwegian bokmål",
    "nl": "dutch",
    "pl": "polish",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sk": "slovak",
    "sl": "slovenian",
    "sr": "serbian",
    "sv": "swedish",
    "th": "thai",
    "tr": "turkish",
    "uk": "ukrainian",
    "vi": "vietnamese",
    "zh": "chinese",
}


def get_system_language_name() -> str:
    lang_code, _ = locale.getdefaultlocale() or os.environ.get("LANG", "en")
    lang_code_short = lang_code.split("_")[0].split("-")[0].lower()
    return lang_map.get(lang_code_short, f"Language with locale '{lang_code}'")


def validate_language(ctx, param, value) -> str:
    val = value.lower()
    # Check if it's a key in lang_map
    if val in lang_map:
        return lang_map[val]
    elif val in lang_map.values():
        return val
    raise click.BadParameter(f"Invalid language '{value}'")


def get_paste():
    if not pyclip:
        raise click.BadParameter(
            "pyclip is not installed. reinstall: llm install llm-tr[pyclip]"
        )
    try:
        return pyclip.paste()
    except pyclip.ClipboardSetupException:
        return None


def read_file_content(file_path: str) -> str:
    """Read content from file if it exists and is readable."""
    try:
        path = Path(file_path)
        if path.is_file():
            return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        pass
    return None


@hookimpl
def register_commands(cli):
    @cli.command()
    @click.argument("args", nargs=-1)
    @click.option("-m", "--model", default=None, help="Specify the model to use")
    @click.option("-s", "--system", help="Custom system prompt")
    @click.option("--key", help="API key to use")
    @click.option(
        "-l",
        "--language",
        envvar="LLM_TR_LANGUAGE",
        help="Force language for translation",
        default="english",
        callback=validate_language,
    )
    @click.option(
        "-x",
        "--paste",
        help="Try to paste the text from clipboard",
        is_flag=True,
        default=False,
    )
    def tr(args, model, system, key, language, paste):
        """Translate the given text to one of your preferred languages"""
        if paste:
            prompt = get_paste()
        else:
            # Check if the first argument is a valid file path
            if len(args) == 1:
                file_content = read_file_content(args[0])
                if file_content is not None:
                    prompt = file_content
                else:
                    prompt = " ".join(args)
            else:
                prompt = " ".join(args)
        model_id = model or get_default_model()
        model_obj = llm.get_model(model_id)
        if model_obj.needs_key:
            model_obj.key = llm.get_key(key, model_obj.needs_key, model_obj.key_env_var)

        translation = model_obj.prompt(
            f"Translate the following text:\n----\n{prompt}",
            system=SYSTEM_PROMPT.format(
                system_language=get_system_language_name(),
                second_language=language,
            ),
        )
        print(translation)

        # copy translation to clipboard if available
        if pyclip:
            try:
                pyclip.copy(str(translation))
            except pyclip.ClipboardSetupException:
                pass
