# AI guide: wholescaleos-openclaw

**For AI assistants (Claude, ChatGPT, Codex, Cursor, Gemini).** Someone gave you a link to this repository. Use this page to explain it, set it up, or help them use it. Talk in plain English; the person may not be technical.

## What this is

A productivity bot for the WholeScale OS project: it watches your code changes and to-do list and sends morning and evening report emails.

**Usually used by:** The project owner.

## Ask first

Ask these together in one short message, then repeat back what you heard in a line or two. Skip anything they already told you.

- Run it on your computer, or 24/7 on Google Cloud?
- Email by Gmail or Resend?

## Set it up

Do one step at a time. Check each one worked before moving on.

| # | Do this | It worked if |
|---|---|---|
| 1 | `pip install -r requirements.txt` | No errors |
| 2 | The person sets `SMTP_PASSWORD` (or `RESEND_API_KEY`) as an environment variable, never in a file | Variable is set |
| 3 | Run a test: `python test_email_now.py` | An email arrives |

## Use it

- See `DEPLOYMENT.md` for running it 24/7.

## How it works, in plain words

1. It reads your recent code changes, ticks off to-dos and writes an AI summary.

## Never

- Never ask for, paste or print passwords, API keys or tokens. Tell the person where to put them (their own `.env` file or the hosting dashboard) and let them do it.
- Never deploy, push to `main`, change a live database or spend money without the person saying yes to that exact step.
- Never put the email password back into `email_config.json`.

## Read next

- [Deploying](DEPLOYMENT.md)
- [Gmail setup](GMAIL_SETUP.md)

## When you're done

Tell the person, in a few lines: what is set up and checked, what isn't yet, and two or three things they can ask you next.
