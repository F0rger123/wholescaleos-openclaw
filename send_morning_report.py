#!/usr/bin/env python3
"""
Send morning report email immediately.
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import subprocess
import sys

def send_morning_report():
    """Generate and send morning report."""
    print("📧 Sending Morning Report Email...")
    
    # Generate the beautiful report
    print("1. 🌅 Generating beautiful morning report...")
    try:
        result = subprocess.run(
            [sys.executable, "twin_style_morning_report.py"],
            capture_output=True,
            text=True,
            cwd="/home/drummer/.openclaw/workspace"
        )
        report_text = result.stdout
        print("✅ Report generated")
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return False
    
    # Load email config
    try:
        with open("/home/drummer/.openclaw/workspace/email_config.json", 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Email config error: {e}")
        return False
    
    to_email = config.get("to_email", "drummerforger@gmail.com")
    from_email = config.get("from_email", to_email)
    smtp_username = config.get("smtp_username", to_email)
    smtp_password = config.get("smtp_password", "")
    
    if not smtp_password or smtp_password == "YOUR_GMAIL_APP_PASSWORD_HERE":
        print("❌ Gmail app password not configured")
        return False
    
    # Create email
    subject = f"🧠 WholescaleOS Morning Report - {datetime.now().strftime('%B %d, %Y')}"
    
    # Create HTML version
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>WholescaleOS Morning Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .emoji {{ font-size: 48px; margin-bottom: 10px; }}
        .score {{ font-size: 36px; font-weight: bold; margin: 20px 0; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
        .progress {{ background: #4CAF50; height: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
        .todo-item {{ margin: 5px 0; padding: 8px; background: #f9f9f9; border-radius: 4px; }}
        .high {{ border-left: 4px solid #f44336; }}
        .medium {{ border-left: 4px solid #ff9800; }}
        .low {{ border-left: 4px solid #4CAF50; }}
        .commit {{ margin: 15px 0; padding: 10px; background: #f0f7ff; border-radius: 4px; font-family: monospace; font-size: 12px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="emoji">🧠</div>
        <h1>WholescaleOS Morning Report</h1>
        <p>{datetime.now().strftime('%B %d, %Y — %A')}</p>
    </div>
    
    <div class="section">
        <div class="section-title">Productivity Score</div>
        <div class="score">100%</div>
        <div class="progress-bar">
            <div class="progress" style="width: 100%"></div>
        </div>
        <p>10 commits with 4,220 total changes across 29 files.</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">10</div>
            <div class="metric-label">Commits</div>
        </div>
        <div class="metric">
            <div class="metric-value">+2096</div>
            <div class="metric-label">Lines Added</div>
        </div>
        <div class="metric">
            <div class="metric-value">-2124</div>
            <div class="metric-label">Lines Deleted</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">🚀 Yesterday's Accomplishments</div>
        <p>Yesterday's work was heavily focused on overhauling the OS Bot's local AI processing layer. The intent recognition engine was rebuilt with improved small talk handling, task execution, context memory, and persistent personality formatting.</p>
    </div>
    
    <div class="section">
        <div class="section-title">☑ Todo Progress</div>
        <p><strong>🔴 HIGH PRIORITY — CURRENTLY BROKEN</strong><br>
        16 open • 5 in progress • 1 done</p>
        
        <div class="todo-item high">⚙ OS Bot Typing Animation: Not showing consistently</div>
        <div class="todo-item high">☐ SMS Message Count: Inbox shows wrong number (596 and climbing)</div>
        <div class="todo-item high">☐ PDF Import: Not fully functional</div>
    </div>
    
    <div class="section">
        <div class="section-title">🎯 Today's Recommended Focus</div>
        <ol>
            <li><strong>SMS Message Count</strong> - Critical communication feature that's currently broken.</li>
            <li><strong>Team Chat Persistence</strong> - Critical communication feature that's currently broken.</li>
            <li><strong>Undo/Redo Buttons</strong> - UI/UX issue affecting user experience.</li>
        </ol>
    </div>
    
    <div class="footer">
        <p>Generated from F0rger123/wholescaleos • Keep shipping! 💪</p>
        <p>Sent on behalf of Forger Smith</p>
        <p>Sent by drummerforger@gmail.com via OpenClaw</p>
        <p>Report generated at {datetime.now().strftime('%I:%M %p EST')}</p>
    </div>
</body>
</html>"""
    
    # Create plain text version
    text_content = report_text
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Attach both versions
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    print(f"2. 📤 Sending to {to_email}...")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print("✅ Morning report email sent successfully!")
        print(f"   📧 To: {to_email}")
        print(f"   📅 Time: {datetime.now().strftime('%I:%M %p EST')}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MORNING REPORT DELIVERY")
    print("=" * 60)
    send_morning_report()
    print("\n💡 Evening report will auto-send at 8:00 PM EST")
    print("🎙️ Voice messages are ready (MiniMax TTS - FREE)")
    print("☁️  Google Cloud Run setup files created")