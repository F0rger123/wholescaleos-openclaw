# GitHub Productivity Monitor - Deployment Guide

## Overview
This system monitors your GitHub commits and sends daily productivity reports via email at 7:00 AM (morning) and 8:00 PM (evening) EST.

## Prerequisites

### 1. API Keys & Accounts
You need the following free accounts:

1. **GitHub Personal Access Token**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` scope (full control of private repositories)
   - Save the token securely

2. **Google Gemini API Key** (Free tier: 60 requests/minute)
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create API key
   - Enable the Gemini API

3. **Resend Account** (Free tier: 100 emails/day)
   - Sign up at [Resend](https://resend.com)
   - Get your API key from dashboard
   - Verify your sending domain or use their test domain

### 2. Repository Setup
Your repository should have the following structure:
```
wholescaleos/
├── .github/workflows/
│   └── productivity-reports.yml
├── scripts/
│   ├── report_generator.py
│   └── todo_manager.py
├── templates/
│   ├── morning_report.html
│   └── evening_report.html
├── config/
│   └── secrets.json
├── data/
│   └── todo_list.json
└── requirements.txt
```

## Step-by-Step Deployment

### Step 1: Clone or Create Repository Structure
```bash
# Clone your repository
git clone https://github.com/F0rger123/wholescaleos.git
cd wholescaleos

# Create directory structure
mkdir -p .github/workflows scripts templates config data
```

### Step 2: Copy Files
Copy all the provided files to their respective locations:
- `.github/workflows/productivity-reports.yml`
- `scripts/report_generator.py`
- `scripts/todo_manager.py`
- `scripts/run_report.py`
- `templates/morning_report.html`
- `templates/evening_report.html`
- `config/secrets.json.example` → Rename to `config/secrets.json`

### Step 3: Configure Secrets
Edit `config/secrets.json` with your actual API keys:
```json
{
  "GITHUB_TOKEN": "ghp_your_github_token_here",
  "REPO_OWNER": "F0rger123",
  "REPO_NAME": "wholescaleos",
  "GEMINI_API_KEY": "your_gemini_api_key_here",
  "EMAIL": {
    "provider": "resend",
    "api_key": "re_your_resend_api_key_here",
    "from_email": "productivity@yourdomain.com",
    "to_email": "your.email@example.com"
  }
}
```

### Step 4: Set Up GitHub Secrets
Go to your repository on GitHub:
1. **Settings** → **Secrets and variables** → **Actions**
2. Add the following repository secrets:
   - `GITHUB_TOKEN`: (Automatically available, no need to add)
   - `GEMINI_API_KEY`: Your Gemini API key
   - `RESEND_API_KEY`: Your Resend API key
   - `REPORT_RECIPIENT_EMAIL`: Your email address

### Step 5: Initialize Todo List
Create your initial todo list:
```bash
# Using the todo manager
python scripts/todo_manager.py --import your_todo_list.txt

# Or create data/todo_list.json manually:
{
  "categories": {
    "high_priority": [
      "Implement core system bootloader",
      "Set up basic kernel modules"
    ],
    "medium_priority": [
      "Create package management system",
      "Design filesystem structure"
    ],
    "low_priority": [
      "Create documentation framework",
      "Build testing infrastructure"
    ]
  },
  "completed": [
    "Project initialization",
    "Repository setup"
  ],
  "last_updated": "2024-01-01T00:00:00"
}
```

### Step 6: Create Requirements File
Create `requirements.txt` in your repository root:
```txt
requests>=2.31.0
google-generativeai>=0.3.0
resend>=1.0.0
```

### Step 7: Test Locally
Before committing, test the system locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Test morning report (dry run)
python scripts/run_report.py --type morning --dry-run

# Test evening report (dry run)
python scripts/run_report.py --type evening --dry-run
```

### Step 8: Commit and Push
```bash
git add .
git commit -m "Add productivity monitoring system"
git push origin main
```

### Step 9: Verify GitHub Actions
1. Go to your repository on GitHub
2. Click **Actions** tab
3. You should see the "Productivity Reports" workflow
4. You can manually trigger it to test

## Customization

### 1. Change Schedule
Edit `.github/workflows/productivity-reports.yml`:
```yaml
schedule:
  # Morning report at 7:00 AM EST (12:00 UTC)
  - cron: '0 12 * * *'
  # Evening report at 8:00 PM EST (01:00 UTC next day)
  - cron: '0 1 * * *'
```

### 2. Use Different Email Provider
Edit `config/secrets.json` for SMTP (Gmail example):
```json
"EMAIL": {
  "provider": "smtp",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 465,
  "smtp_username": "your.email@gmail.com",
  "smtp_password": "your_app_password_here",
  "from_email": "your.email@gmail.com",
  "to_email": "your.email@example.com"
}
```

### 3. Customize Email Templates
Edit `templates/morning_report.html` and `templates/evening_report.html` to match your branding.

### 4. Adjust Todo Matching Logic
Edit `report_generator.py` in the `analyze_todo_completion` method to improve how commits are matched to todo items.

## Monitoring and Maintenance

### Check Workflow Runs
- Go to GitHub → Actions → Productivity Reports
- View logs for any failures

### Update Todo List
```bash
# Add new item
python scripts/todo_manager.py --add "New feature" --category high

# Mark item as completed
python scripts/todo_manager.py --complete "Completed feature"

# Export current list
python scripts/todo_manager.py --export > updated_todos.txt
```

### Cost Monitoring
- **GitHub Actions**: Free for public repos, 2000 minutes/month for private
- **Gemini API**: Free tier (60 requests/minute)
- **Resend**: Free tier (100 emails/day)

## Troubleshooting

### Common Issues

1. **Workflow fails with "ModuleNotFoundError"**
   - Ensure `requirements.txt` is in repository root
   - Check Python version in workflow (3.11)

2. **No emails received**
   - Check Resend dashboard for sent emails
   - Verify email addresses in secrets
   - Check spam folder

3. **GitHub API rate limits**
   - The script limits to 50 commits per run
   - Free tier: 60 requests/hour (should be sufficient)

4. **Todo items not being marked complete**
   - Commit messages need to contain keywords from todo items
   - Adjust matching logic in `analyze_todo_completion` method

### Debug Mode
Run locally with debug output:
```bash
python scripts/run_report.py --type morning --dry-run --verbose
```

## Security Notes

1. **Never commit `config/secrets.json`** - Use `.gitignore`
2. **Use GitHub Secrets** for sensitive data
3. **Regularly rotate API keys**
4. **Review GitHub Actions permissions** - Minimal required scopes

## Support
For issues or questions:
1. Check GitHub Actions logs
2. Review generated report files in `reports/` directory
3. Test locally with `--dry-run` flag
4. Open an issue in your repository

The system will now automatically send you productivity reports every day at 7:00 AM and 8:00 PM EST!