#!/usr/bin/env python3
"""
Email Reporter for WholescaleOS Productivity Reports - Fixed Version
Sends reports via email using Resend API or SMTP.
"""

import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional

class EmailReporter:
    def __init__(self, config_file: str = "email_config.json"):
        """Initialize email reporter."""
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load email configuration."""
        default_config = {
            "provider": "resend",
            "to_email": "drummerforger@gmail.com",
            "from_email": "productivity@wholescaleos.com",
            "resend_api_key": "",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "enable_html": True
        }
        
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Config file {self.config_file} not found or invalid. Using defaults.")
            # Create template config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created template config at {self.config_file}")
            print("Please edit it with your email settings.")
        
        return default_config
    
    def send_via_resend(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email using Resend API."""
        api_key = self.config.get("resend_api_key")
        if not api_key or api_key == "your_resend_api_key_here":
            print("❌ Resend API key not configured")
            return False
        
        from_email = self.config.get("from_email", "productivity@wholescaleos.com")
        to_email = self.config.get("to_email", "drummerforger@gmail.com")
        
        # Try to import resend
        try:
            import resend
        except ImportError:
            print("Resend library not installed. Trying to install...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "resend"])
                import resend
            except:
                print("Failed to install resend library")
                return False
        
        resend.api_key = api_key
        
        try:
            params = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }
            
            resend.Emails.send(params)
            print(f"✅ Email sent via Resend to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending email via Resend: {e}")
            return False
    
    def send_via_smtp(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email via SMTP."""
        smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
        smtp_port = self.config.get("smtp_port", 587)
        smtp_username = self.config.get("smtp_username", "")
        smtp_password = self.config.get("smtp_password", "")
        from_email = self.config.get("from_email", smtp_username)
        to_email = self.config.get("to_email", "drummerforger@gmail.com")
        
        if not smtp_username or not smtp_password:
            print("❌ SMTP credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Attach both text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent via SMTP to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending email via SMTP: {e}")
            return False
    
    def send_report(self, report_type: str, report_data: Dict[str, Any]) -> bool:
        """Send a productivity report via email."""
        if report_type == "morning":
            subject = f"🌅 WholescaleOS Morning Report - {datetime.now().strftime('%Y-%m-%d')}"
            html_content = self.generate_morning_html(report_data)
            text_content = self.generate_morning_text(report_data)
        else:  # evening
            subject = f"🌙 WholescaleOS Evening Report - {datetime.now().strftime('%Y-%m-%d')}"
            html_content = self.generate_evening_html(report_data)
            text_content = self.generate_evening_text(report_data)
        
        # Choose provider
        provider = self.config.get("provider", "resend")
        
        if provider == "resend":
            return self.send_via_resend(subject, html_content, text_content)
        elif provider == "smtp":
            return self.send_via_smtp(subject, html_content, text_content)
        else:
            print(f"❌ Unknown email provider: {provider}")
            return False
    
    def generate_morning_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for morning report."""
        commits = data.get("commits", [])
        todo_stats = data.get("todo_stats", {})
        focus_items = data.get("focus_items", [])
        
        # Build commits HTML
        commits_html = ""
        if commits:
            for commit in commits[:10]:
                message = commit.get('message', '').split('\n')[0]
                if len(message) > 80:
                    message = message[:77] + "..."
                time_str = commit.get('date', '')[11:16] if commit.get('date') else "N/A"
                files = len(commit.get('files_changed', []))
                
                commits_html += f"""
                <div class="commit-item">
                    <strong>{message}</strong><br>
                    <small>⏰ {time_str} | 📁 {files} files</small>
                </div>
                """
        else:
            commits_html = "<p>No commits yesterday.</p>"
        
        # Build focus items HTML
        focus_html = ""
        for item in focus_items[:3]:
            if len(item) > 60:
                item = item[:57] + "..."
            focus_html += f"<li>{item}</li>"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WholescaleOS Morning Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #4a5568; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        .commit-item {{ background: white; padding: 15px; margin-bottom: 10px; border-left: 4px solid #4299e1; border-radius: 0 8px 8px 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }}
        .stat-box {{ background: white; padding: 20px; text-align: center; border-radius: 8px; border: 1px solid #e2e8f0; }}
        .stat-number {{ font-size: 24px; font-weight: 700; display: block; }}
        .stat-label {{ font-size: 14px; color: #718096; margin-top: 5px; }}
        .focus-list {{ list-style: none; padding: 0; }}
        .focus-list li {{ padding: 12px 15px; margin-bottom: 10px; background: #ebf8ff; border-left: 4px solid #4299e1; border-radius: 0 8px 8px 0; }}
        @media (max-width: 480px) {{ .stats-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌅 WholescaleOS Morning Report</h1>
            <p>{datetime.now().strftime('%Y-%m-%d %I:%M %p %Z')}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2 class="section-title">📊 Yesterday's Commits</h2>
                {commits_html}
            </div>
            
            <div class="section">
                <h2 class="section-title">✅ Todo Progress</h2>
                <div class="stats-grid">
                    <div class="stat-box" style="border-color: #fc8181;">
                        <span class="stat-number">{todo_stats.get('high', 0)}</span>
                        <span class="stat-label">🔴 High Priority</span>
                    </div>
                    <div class="stat-box" style="border-color: #f6ad55;">
                        <span class="stat-number">{todo_stats.get('medium', 0)}</span>
                        <span class="stat-label">🟡 Medium Priority</span>
                    </div>
                    <div class="stat-box" style="border-color: #68d391;">
                        <span class="stat-number">{todo_stats.get('low', 0)}</span>
                        <span class="stat-label">🟢 Low Priority</span>
                    </div>
                    <div class="stat-box" style="border-color: #4fd1c5;">
                        <span class="stat-number">{todo_stats.get('completed', 0)}</span>
                        <span class="stat-label">✅ Completed</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">🎯 Today's Recommended Focus</h2>
                <ul class="focus-list">
                    {focus_html}
                </ul>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px; color: #718096; font-size: 14px; border-top: 1px solid #e2e8f0; margin-top: 20px;">
            <p>Generated automatically by WholescaleOS Productivity Monitor</p>
            <p>Repository: F0rger123/wholescaleos</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_morning_text(self, data: Dict[str, Any]) -> str:
        """Generate plain text for morning report."""
        text = f"🌅 WHOLESCALEOS MORNING REPORT\n"
        text += f"📅 {datetime.now().strftime('%Y-%m-%d %I:%M %p %Z')}\n"
        text += "=" * 50 + "\n\n"
        
        text += "📊 YESTERDAY'S COMMITS:\n"
        commits = data.get("commits", [])
        if commits:
            for i, commit in enumerate(commits[:5], 1):
                message = commit.get('message', '').split('\n')[0]
                if len(message) > 60:
                    message = message[:57] + "..."
                time_str = commit.get('date', '')[11:16] if commit.get('date') else "N/A"
                files = len(commit.get('files_changed', []))
                text += f"{i}. {message}\n"
                text += f"   Time: {time_str} | Files: {files}\n"
        else:
            text += "No commits yesterday.\n"
        
        text += "\n"
        
        todo_stats = data.get("todo_stats", {})
        text += "✅ TODO PROGRESS:\n"
        text += f"🔴 High Priority: {todo_stats.get('high', 0)} items\n"
        text += f"🟡 Medium Priority: {todo_stats.get('medium', 0)} items\n"
        text += f"🟢 Low Priority: {todo_stats.get('low', 0)} items\n"
        text += f"✅ Completed: {todo_stats.get('completed', 0)} items\n"
        
        text += "\n"
        
        focus_items = data.get("focus_items", [])
        text += "🎯 TODAY'S RECOMMENDED FOCUS:\n"
        for i, item in enumerate(focus_items[:3], 1):
            if len(item) > 50:
                item = item[:47] + "..."
            text += f"{i}. {item}\n"
        
        text += "\n" + "=" * 50 + "\n"
        text += "Generated automatically by WholescaleOS Productivity Monitor\n"
        text += "Repository: F0rger123/wholescaleos\n"
        
        return text
    
    def generate_evening_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for evening report."""
        commits = data.get("commits", [])
        productivity = data.get("productivity", {})
        focus_items = data.get("focus_items", [])
        
        score = productivity.get('score', 0)
        filled = int(score / 10)
        visual = "█" * filled + "░" * (10 - filled)
        
        # Build focus items HTML
        focus_html = ""
        for item in focus_items[:3]:
            if len(item) > 60:
                item = item[:57] + "..."
            focus_html += f"<li>{item}</li>"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WholescaleOS Evening Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #4a5568; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        .activity-stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }}
        .activity-stat {{ background: white; padding: 20px; text-align: center; border-radius: 8px; border: 1px solid #e2e8f0; }}
        .activity-number {{ font-size: 28px; font-weight: 700; display: block; }}
        .activity-label {{ font-size: 14px; color: #718096; margin-top: 5px; }}
        .productivity-score {{ text-align: center; padding: 25px; background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%); border-radius: 12px; margin-bottom: 25px; }}
        .score-visual {{ font-size: 24px; letter-spacing: 2px; margin: 15px 0; }}
        .score-number {{ font-size: 48px; font-weight: 700; margin: 10px 0; }}
        .focus-list {{ list-style: none; padding: 0; }}
        .focus-list li {{ padding: 12px 15px; margin-bottom: 10px; background: #fff5f5; border-left: 4px solid #f56565; border-radius: 0 8px 8px 0; }}
        @media (max-width: 480px) {{ .activity-stats {{ grid-template-columns: 1fr; }} .score-number {{ font-size: 36px; }} }}
