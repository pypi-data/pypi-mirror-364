# llm-tr: translate text using llm in your terminal

[![PyPI](https://img.shields.io/pypi/v/llm-tr.svg)](https://pypi.org/project/llm-tr/)
[![Changelog](https://img.shields.io/github/v/release/mgaitan/llm-tr?include_prereleases&label=changelog)](https://github.com/mgaitan/llm-tr/releases)
[![Tests](https://github.com/mgaitan/llm-tr/actions/workflows/ci.yml/badge.svg)](https://github.com/mgaitan/llm-tr/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mgaitan/llm-tr/blob/main/LICENSE)

**llm-tr** is a plugin for [LLM](https://llm.datasette.io/) that lets you translate text directly from your terminal using your favorite large language model. It automatically detects the source language and translates to your preferred language, with smart fallbacks and clipboard integration.

## Installation

First, install [LLM](https://llm.datasette.io/) if you haven't already.

Then install llm-tr:

```bash
llm install llm-tr
```

If you want automatic copying of results to your clipboard, install with the `pyclip` extra:

```bash
llm install 'llm-tr[pyclip]'
```

---

## Usage

Translate any text from your terminal:

```bash
llm tr Hola mundo
```

Or translate the contents of a file:

```bash
llm tr document.txt
```

The plugin will:
- Detect the source language of the input (text or file content).
- Translate to your preferred language (see below for how this is chosen).
- Print the translation to stdout.
- If installed with `[pyclip]`, copy the result to your clipboard automatically.

### File Translation

When you provide a single argument that is a valid file path, llm-tr will automatically read the file's content and translate it:

```bash
# Translate a text file
llm tr readme.txt

# Translate a markdown file
llm tr documentation.md

# Works with any text file
llm tr script.py
```

If the file cannot be read (doesn't exist, permission issues, or binary file), the argument will be treated as regular text to translate.

## Preferred Language Logic

llm-tr determines your target translation language using the following priority:

1. **Explicit Language (CLI or Environment Variable):**
   - Use the `--language` (or `-l`) option:
     ```bash
     llm tr -l french Hello world
     ```
   - Or set the `LLM_TR_LANGUAGE` environment variable:
     ```bash
     export LLM_TR_LANGUAGE=spanish

     ```

2. **System Language:**
   - If no explicit language is set, llm-tr uses your system locale (e.g., `LANG` environment variable or OS locale settings).

3. **Fallback to English:**
   - If neither of the above is available or recognized, English is used as the default target language.

**Note:** The plugin will never translate into the detected source language. If your preferred language matches the source, it will use the next available option.

### Examples

- Translate to French explicitly:
  ```bash
  llm tr -l french ¡Viva Perón y que la chupen los gorilas!
  ```
- Use environment variable for Spanish and quote the input
  ```bash
  export LLM_TR_LANGUAGE=spanish
  llm tr "Proletarier aller Länder, vereinigt euch!"
  ```
- Let the system locale decide (e.g., if your system is set to German):
  ```bash
  llm tr Good morning
  ```
  (If your system language is German, this will translate to German unless the input is already in German.)


## Clipboard Integration

If you install llm-tr with [pyclip](https://pypi.org/project/pyclip/` extra (i.e., `llm install 'llm-tr[pyclip]'`), the translated result will be automatically copied to your clipboard after each translation.

In addition, you can also translate text from your clipboard using the `-x` (or `--paste`) option:

```bash
llm tr -x
```

This will read the current clipboard content as the input text to translate, instead of requiring you to type or paste it into the terminal. This is especially useful for quickly translating text you've just copied from another application.

If `pyclip` is not available or clipboard setup fails, these features are ignored.

## System Prompt

llm-tr uses the following system prompt for the LLM:

> First, detect the source language of the input text.
>
> You have two preferred languages as target languages: {second_language} and {system_language}.
> Translate the text into the first preferred language that is different from the detected source language.
>
> Return only the translated text as a string, with no explanations or extra output.

## Supported Languages

You can specify your preferred language using either the language name or its code. Supported languages include:

afrikaans (`af`), arabic (`ar`), bulgarian (`bg`), bengali (`bn`), catalan (`ca`), czech (`cs`), danish (`da`), german (`de`), greek (`el`), english (`en`), spanish (`es`), estonian (`et`), persian (`fa`), finnish (`fi`), french (`fr`), hebrew (`he`), hindi (`hi`), croatian (`hr`), hungarian (`hu`), indonesian (`id`), italian (`it`), japanese (`ja`), korean (`ko`), lithuanian (`lt`), latvian (`lv`), macedonian (`mk`), malay (`ms`), norwegian bokmål (`nb`), dutch (`nl`), polish (`pl`), portuguese (`pt`), romanian (`ro`), russian (`ru`), slovak (`sk`), slovenian (`sl`), serbian (`sr`), swedish (`sv`), thai (`th`), turkish (`tr`), ukrainian (`uk`), vietnamese (`vi`), chinese (`zh`).
