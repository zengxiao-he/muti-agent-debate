## Multi-Agent Debate System (MVP)

A small FastAPI + OpenAI playground for multi-agent deep research and debate.

Each teammate should run it **locally with their own OpenAI API key**.  
No API keys should ever be committed to Git or shared in code.

---

### 1. Local setup (for every teammate)

```bash
git clone <your-repo-url>
cd multi-agent-debate

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

### 2. Configure your own OpenAI key

In the same terminal (after activating the venv):

```bash
export OPENAI_API_KEY="your_own_openai_key"

# Optional: choose a model; mini models are cheaper and faster
export OPENAI_MODEL="gpt-4o-mini"
# or: export OPENAI_MODEL="gpt-4.1-mini"
```

> Important:  
> - Do **not** hardcode the key in any file.  
> - Do **not** commit the key to Git or share it with others.  
> - Every teammate uses their **own** key and pays for their own usage.

---

### 3. Run the app

```bash
uvicorn backend.main:app --reload
```

By default the server listens on `http://127.0.0.1:8000`.

You can verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

If it returns JSON with `"status": "ok"` and `"openai_key_configured": true`,
you are ready to use the UI.

---

### 4. Use the web UI

Open in your browser:

```text
http://127.0.0.1:8000
```

On the page:
- Enter a topic in **Topic (policy / thesis / problem)**.
- Adjust:
  - **Number of candidate proposals** (3–5, default 4)
  - **Batches** (default 2)
  - **Rounds per batch** (default 2)
- Click **Start multi-agent debate**.

The app will:
1. Do deep research and generate multiple candidate proposals.  
2. Create one agent per proposal (plus a moderator).  
3. Run multi-batch, multi-round debate.  
4. Produce a final report comparing proposals and recommending the best one.

> Tip: For faster and cheaper runs, start with:
> - 3 proposals  
> - 1 batch  
> - 1 round per batch  
> and a mini model like `gpt-4o-mini`.

---

### 5. Suggested `.gitignore`

Make sure your repo ignores local and sensitive files. For example:

```gitignore
.venv/
__pycache__/
.env
```

This prevents virtualenvs and local secrets from being committed.



