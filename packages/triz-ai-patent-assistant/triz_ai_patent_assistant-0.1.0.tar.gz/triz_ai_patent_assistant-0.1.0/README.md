# TRIZ-AI Patent Assistant

> 🧠 AI + TRIZ system for generating and validating patent claims

![CI](https://github.com/voroninsergei/triz-ai-patent-assistant/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/github/license/voroninsergei/triz-ai-patent-assistant)

## Features

- Generate patent formulas from natural language ideas
- Assess novelty and inventive step (non-obviousness)
- Extract TRIZ contradictions and IPC classes
- Export structured Word reports
- Use LLMs to improve claims (OpenAI, Azure, Anthropic)

## Quickstart

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Run tests

```bash
pytest tests/
```

## License

MIT License — use freely with attribution.