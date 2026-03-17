# KumuBot

KumuBot is a collection of AI-powered tools for learning about the Hawaiian language and culture. The live project includes chat, translation, dictionary, proverb, image-generation, and word-game experiences built around Hawaiian-focused workflows.

Live site: [kumubot.com](https://kumubot.com)  
About the project: [kumubot.com/about](https://kumubot.com/about)

## Mission

KumuBot was created by Koa Lanakila Chang to make Hawaiian language and culture feel more accessible to people from all backgrounds. The project combines educational tooling with generative AI so users can explore vocabulary, proverbs, conversation, visual storytelling, and interactive games in one place.

## Products

- `KumuChat`: a Hawaiian-focused chat assistant for questions about Hawaiʻi, Hawaiian language, and culture.
- `KumuArt`: an image generator that creates Hawaiian-themed visuals from natural-language prompts.
- `KumuTranslator`: an English <-> Hawaiian translation tool.
- `KumuDictionary`: a Hawaiian word lookup experience with definitions and example usage.
- `KumuNoʻeau`: a proverb tool for finding or generating Hawaiian ʻŌlelo Noʻeau.
- `KumuWordle`: a Hawaiian-inspired Wordle-style game.

## Technical Highlights

This repository uses OpenAI APIs across both the product endpoints and the shared backend infrastructure, including:

- `Responses API`
- `GPT-5`
- `gpt-image-1`
- multimodal chat input support
- vector-store RAG
- `file_search`
- built-in `web_search`
- agentic tool calling
- structured outputs with JSON schema
- text-to-speech and speech-to-text APIs

The current OpenAI capability routes live in the consolidated backend under:

- `/openai/capabilities`
- `/openai/agent`
- `/openai/web-search`
- `/openai/rag/index`
- `/openai/rag/query`
- `/openai/voice/speech`
- `/openai/voice/transcribe`
- `/openai/structured-plan`

## Repository Layout

```text
src/
  KumuChat/         Flask app for the KumuChat web experience
  KumuArt/          Flask app for the KumuArt web experience
  KumuTranslator/   Flask app for translation
  KumuDictionary/   Flask app for dictionary lookups
  KumuNoeau/        Flask app for proverb search/generation
  KumubotBackend/   Consolidated backend with all core routes and OpenAI capability endpoints
  KumuWordle/       Static Hawaiian Wordle-style frontend
  shared/           Shared OpenAI and logging utilities used by multiple apps
media/
  Examples/         Product screenshots and media assets
```

## Architecture

Each product directory contains its own small Flask app plus `templates/` and `static/` assets. The project also includes a centralized backend in [`src/KumubotBackend/backend.py`](src/KumubotBackend/backend.py) that contains:

- the up-to-date product routes for chat, art, translation, dictionary, and proverb features
- shared OpenAI request helpers
- OpenAI-powered capability routes for tool calling, retrieval, voice, structured outputs, and research workflows

The frontend stack is intentionally lightweight: Flask, server-rendered HTML, and vanilla JavaScript/CSS.

## Running Locally

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

For the most up-to-date OpenAI backend work, start with the consolidated backend requirements:

```bash
pip install -r src/KumubotBackend/requirements.txt
```

### 3. Run the consolidated backend

```bash
cd src/KumubotBackend
python backend.py
```

This backend exposes the main product endpoints:

- `/chat`
- `/art`
- `/translate`
- `/dictionary`
- `/noeau`

and the newer OpenAI capability endpoints listed above.

### 4. Run an individual product app

If you want to work on a single frontend experience, run its local Flask app from that directory. Example:

```bash
cd src/KumuChat
python app.py
```

The same pattern applies to `KumuArt`, `KumuTranslator`, `KumuDictionary`, and `KumuNoeau`.

## Tests

Backend tests for the OpenAI capability routes live in:

- [`src/KumubotBackend/test_openai_capabilities.py`](src/KumubotBackend/test_openai_capabilities.py)

Run them with:

```bash
pytest src/KumubotBackend/test_openai_capabilities.py -q
```

## Media

Example screenshots for the products are stored in [`media/Examples`](media/Examples).

## Operational Notes

- This repository is organized as a multi-app Flask monorepo.
- Several app folders include their own `requirements.txt`, `.env`, and `Procfile` files for independent deployment.
- For production use, API keys and secrets should be supplied through environment variables rather than committed in source files.

## Credits

KumuBot is a student-built project focused on using AI to make Hawaiian language and culture more approachable, interactive, and useful in everyday learning.
