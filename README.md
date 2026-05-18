# Multi-Agent Debate

FastAPI playground for comparing candidate solutions with several LLM-backed proposal agents and a moderator. The app turns a topic into competing proposals, runs a configurable debate, and returns a final recommendation with the debate history.

This is an MVP intended to demonstrate agent orchestration, structured prompts, and a simple web UI. It is not a production research system yet.

## What It Does

- Generates multiple candidate proposals for a user-supplied topic.
- Creates one proposal agent per candidate plus a moderator agent.
- Runs multi-batch, multi-round rebuttals.
- Produces a final report that compares the proposals and recommends a direction.
- Serves a small browser UI from the same FastAPI app.

## Architecture

```text
frontend/
  index.html, script.js, styles.css

backend/
  main.py       FastAPI app, health check, static UI, debate endpoint
  models.py     Pydantic request and response models
  debate.py     Debate pipeline orchestration
  agents.py     Proposal and moderator agent behavior
  research.py   Candidate proposal and evidence generation
  llm.py        OpenAI client wrapper
  config.py     Environment-based settings
```

## Quickstart

```bash
git clone https://github.com/zengxiao-he/multi-agent-debate.git
cd multi-agent-debate

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Set your OpenAI key in the same terminal:

```bash
export OPENAI_API_KEY="your_openai_key"
export OPENAI_MODEL="gpt-4o-mini"
```

Run the app:

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## API

```bash
curl -X POST http://127.0.0.1:8000/api/debate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Should a startup build an internal AI support agent?",
    "language": "en",
    "config": {
      "num_solutions": 3,
      "num_batches": 1,
      "rounds_per_batch": 1
    }
  }'
```

## Current Limitations

- LLM calls are sequential for readability; parallel proposal generation would reduce latency.
- The research step depends on model-generated evidence rather than a verified external retrieval pipeline.
- There is no persisted run history, authentication, or cost tracking yet.
- The final report is qualitative; a future version should add an evaluation rubric and score proposals explicitly.

## Repository Hygiene

Local environments, Python bytecode, API keys, and OS artifacts are ignored through `.gitignore`. Do not commit `.venv/`, `__pycache__/`, `.env`, or generated caches.
