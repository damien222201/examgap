# ExamGap

A WAEC/JAMB-style practice quiz tool that tracks your accuracy by topic over time — so instead of guessing what to revise, you can see exactly where your weak spots actually are.

## On the content

The 40 practice questions (8 each across Mathematics, English Language, Physics, Chemistry, and Biology) are **original content written in the style and topic coverage of the WAEC/JAMB syllabus — not reproductions of actual past exam questions.** Real past questions are copyrighted by the exam bodies and can't be freely redistributed. Explanations are written in rather than generated live by an AI, which also means this runs with **zero ongoing API cost.**

## How it works

1. **Practice** — enter your email, pick a subject, answer a random set of questions.
2. **Results** — see your score immediately, plus a written explanation for every question (not just the ones you got wrong, so right answers get reinforced too).
3. **My progress** — enter your email anytime to see your accuracy broken down by topic, across every practice set you've ever taken, worst-first. A topic you keep getting wrong stays visible until you actually improve on it — that's the "gap" the name refers to.

## Tech stack

Flask + Flask-SQLAlchemy, PostgreSQL on Render, server-rendered Jinja2, no JS framework, no external API calls at runtime.

## Running locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
export $(cat .env | xargs)

python app.py
```

Falls back to local SQLite (`examgap_dev.db`) if `DATABASE_URL` isn't set. Visit `http://localhost:5000`.

## Deploying to Render

**Option A — blueprint:** push to GitHub, "New Blueprint" in Render pointed at the repo — `render.yaml` sets up the web service and free Postgres together.

**Option B — manual:** create a Postgres DB, create a Web Service (`pip install -r requirements.txt` / `gunicorn app:app`), add `DATABASE_URL` and `SECRET_KEY` env vars.

## Project structure

```
app.py              # routes + app factory
models.py           # Attempt model (one row per answered question)
questions.py         # the original 40-question bank, with topics and explanations baked in
utils.py            # email validation, quiz sampling, topic-gap aggregation
templates/            # index, quiz, results, progress pages + shared base layout
static/style.css      # all styling
```

## Adding more questions

Open `questions.py` and add entries to the relevant subject's list in `QUESTION_BANK`. Each question needs a unique `id`, a `topic` tag (this is what drives the progress tracking — reuse an existing topic name to group with it, or add a new one), `question` text, four `options`, the correct `answer` letter, and an `explanation`. No other code changes needed — the quiz sampling and progress tracking both work automatically off whatever's in the bank.

## Known limitations / next steps

- **Small question bank (40 total).** Enough to demonstrate the topic-tracking concept properly; growing it is just a matter of adding more entries to `questions.py` in the same format.
- **No login/accounts** — email is just a tracking key, not authenticated. Anyone who knows (or guesses) an email could view that person's progress. Fine for a personal/demo tool; would need real auth for a multi-user product.
- **Fixed quiz size (5 questions per set)** — adjustable via `DEFAULT_QUIZ_SIZE` in `utils.py`.

## License

MIT — see [LICENSE](LICENSE).
