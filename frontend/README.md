# Resume Assistant — frontend

A two-step Next.js UI for the FastAPI RAG resume backend:

1. **Upload** — drag or choose a `.pdf`/`.docx` resume → `POST /upload-document`
2. **Analyze** — pick a feature from the dropdown, add context if needed, ask →
   `POST /ask-query`

```
app/
├── layout.tsx      Fonts (IBM Plex Mono + Inter) and page metadata
├── page.tsx        The whole upload → ask flow
└── globals.css     Design tokens + all component styles
lib/
└── api.ts          Typed fetch calls matching the backend's exact response shape
```

## Setup

```bash
npm install
cp .env.local.example .env.local   # points to http://localhost:8000 by default
npm run dev
```

Open http://localhost:3000.

## Before you run it

**Start the FastAPI backend first**, on port 8000, with CORS already configured
for `http://localhost:3000` (your `app.py` already has this).

If your backend runs on a different port, edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## How the two steps connect

- After a successful upload, the response's `data.chunks` and
  `data.collection_count` are shown as confirmation, and the UI reveals the
  "Analyze" card — there's no separate upload ID; the backend's vectorstore is
  a single persisted Chroma collection, so any question after any upload
  searches everything indexed so far.
- The feature dropdown values (`ats_score`, `skill_gap`, `job_match`,
  `interview_questions`, `resume_rewrite`) match `apps/prompt.py` exactly —
  if you add a new feature there, add it to `FEATURES` in `lib/api.ts` too.

## One backend quirk worth knowing

In `rag_process.py`, `get_answer_from_llm_vectorstore` always hardcodes
`"target_role": ""` when invoking the prompt — so for `resume_rewrite`, typing
a target role in the UI currently doesn't change the output; it only affects
what's searched for in the vectorstore. To actually wire it through:

```python
def get_answer_from_llm_vectorstore(query, feature, target_role=""):
    ...
    final_prompt = rag_prompt.invoke({
        "resume_text": context,
        "job_description": query,
        "target_role": target_role
    })
```
and pass `target_role` from `ask_question` → `AskQuery` the same way `query`
and `feature` already flow through. Happy to wire this up if you want — just
say the word.
