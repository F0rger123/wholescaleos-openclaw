#!/usr/bin/env python3
"""
GitHub Commit Monitor & Productivity Report Generator
Generates morning and evening productivity reports based on GitHub commits.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re

class GitHubCommitMonitor:
    def __init__(self, config_path: str = "config/secrets.json"):
        """Initialize with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # GitHub API setup
        self.github_token = self.config.get('GITHUB_TOKEN')
        self.repo_owner = self.config.get('REPO_OWNER', 'F0rger123')
        self.repo_name = self.config.get('REPO_NAME', 'wholescaleos')
        self.github_headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Email setup
        self.email_config = self.config.get('EMAIL', {})
        
        # Gemini AI setup
        gemini_api_key = self.config.get('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.ai_model = genai.GenerativeModel('gemini-pro')
        else:
            self.ai_model = None
        
        # Load todo list
        self.todo_list = self.load_todo_list()
        
    def load_todo_list(self) -> Dict[str, Any]:
        """Load todo list from JSON file."""
        try:
            with open('data/todo_list.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default structure
            return {
                "categories": {
                    "high_priority": [],
                    "medium_priority": [],
                    "low_priority": []
                },
                "completed": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def save_todo_list(self):
        """Save updated todo list to JSON file."""
        self.todo_list["last_updated"] = datetime.now().isoformat()
        with open('data/todo_list.json', 'w') as f:
            json.dump(self.todo_list, f, indent=2)
    
    def fetch_commits(self, since: datetime, until: datetime = None) -> List[Dict]:
        """Fetch commits from GitHub API for a given time period."""
        if until is None:
            until = datetime.now()
        
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
        params = {
            'since': since.isoformat(),
            'until': until.isoformat(),
            'per_page': 100
        }
        
        try:
            response = requests.get(url, headers=self.github_headers, params=params)
            response.raise_for_status()
            commits = response.json()
            
            # Get detailed commit info
            detailed_commits = []
            for commit in commits[:50]:  # Limit to 50 commits to avoid rate limits
                commit_url = commit['url']
                commit_detail = requests.get(commit_url, headers=self.github_headers).json()
                
                detailed_commits.append({
                    'sha': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'files_changed': self.get_commit_files(commit['sha']),
                    'stats': commit_detail.get('stats', {})
                })
            
            return detailed_commits
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commits: {e}")
            return []
    
    def get_commit_files(self, sha: str) -> List[str]:
        """Get list of files changed in a commit."""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits/{sha}"
        try:
            response = requests.get(url, headers=self.github_headers)
            response.raise_for_status()
            commit_data = response.json()
            return [file['filename'] for file in commit_data.get('files', [])]
        except:
            return []
    
    def analyze_todo_completion(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze which todo items were completed based on commit messages."""
        completed_items = []
        remaining_items = []
        
        # Extract todo items from all categories
        all_todos = []
        for category in ['high_priority', 'medium_priority', 'low_priority']:
            all_todos.extend(self.todo_list['categories'].get(category, []))
        
        # Check commit messages for todo completion patterns
        commit_messages = ' '.join([c['message'] for c in commits])
        
        for todo in all_todos:
            todo_lower = todo.lower()
            # Simple keyword matching (can be enhanced with AI)
            if any(keyword in commit_messages.lower() for keyword in todo_lower.split()[:3]):
                completed_items.append(todo)
            else:
                remaining_items.append(todo)
        
        # Update todo list
        self.todo_list['completed'].extend(completed_items)
        for category in ['high_priority', 'medium_priority', 'low_priority']:
            self.todo_list['categories'][category] = [
                item for item in self.todo_list['categories'].get(category, [])
                if item not in completed_items
            ]
        
        self.save_todo_list()
        
        return {
            'completed': completed_items,
            'remaining': remaining_items,
            'completion_rate': len(completed_items) / len(all_todos) * 100 if all_todos else 0
        }
    
    def generate_ai_summary(self, commits: List[Dict], period: str) -> str:
        """Generate AI summary of commits using Gemini."""
        if not self.ai_model:
            return self.generate_basic_summary(commits, period)
        
        commit_details = "\n".join([
            f"- {c['message']} ({c['date']}): Changed {len(c['files_changed'])} files"
            for c in commits[:10]  # Limit for token count
        ])
        
        prompt = f"""Summarize these GitHub commits from the {period} in a concise, professional way:
        
        {commit_details}
        
        Focus on:
        1. What was accomplished
        2. Technical patterns or themes
        3. Progress toward project goals
        
        Keep it under 150 words."""
        
        try:
            response = self.ai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"AI summary error: {e}")
            return self.generate_basic_summary(commits, period)
    
    def generate_basic_summary(self, commits: List[Dict], period: str) -> str:
        """Generate basic summary without AI."""
        if not commits:
            return f"No commits during the {period}."
        
        total_files = sum(len(c['files_changed']) for c in commits)
        return f"Completed {len(commits)} commits changing {total_files} files during the {period}."
    
    def calculate_productivity_score(self, commits: List[Dict], todo_analysis: Dict) -> Dict[str, Any]:
        """Calculate productivity metrics."""
        if not commits:
            return {
                'score': 0,
                'commits_count': 0,
                'files_changed': 0,
                'todo_completion': 0,
                'visual': "░░░░░░░░░░ 0%"
            }
        
        # Base score on commits and todo completion
        commits_score = min(len(commits) * 10, 50)  # Max 50 points for commits
        todo_score = todo_analysis['completion_rate'] * 0.5  # Max 50 points for todos
        
        total_score = commits_score + todo_score
        normalized_score = min(total_score, 100)
        
        # Create visual indicator
        filled = int(normalized_score / 10)
        visual = "█" * filled + "░" * (10 - filled)
        
        return {
            'score': normalized_score,
            'commits_count': len(commits),
            'files_changed': sum(len(c['files_changed']) for c in commits),
            'todo_completion': todo_analysis['completion_rate'],
            'visual': f"{visual} {normalized_score:.0f}%"
        }
    
    def generate_morning_report(self) -> Dict[str, Any]:
        """Generate morning report data."""
        # Get yesterday's commits
        yesterday = datetime.now() - timedelta(days=1)
        start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        commits = self.fetch_commits(start_of_yesterday, end_of_yesterday)
        todo_analysis = self.analyze_todo_completion(commits)
        
        # Get remaining todos for focus recommendations
        remaining_todos = []
        for category in ['high_priority', 'medium_priority', 'low_priority']:
            remaining_todos.extend(self.todo_list['categories'].get(category, []))
        
        # Recommend focus items (top 3 from high priority)
        high_priority = self.todo_list['categories'].get('high_priority', [])
        recommended_focus = high_priority[:3] if high_priority else remaining_todos[:3]
        
        return {
            'report_type': 'morning',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'yesterday_commits': commits,
            'yesterday_summary': self.generate_ai_summary(commits, "previous day"),
            'todo_analysis': todo_analysis,
            'recommended_focus': recommended_focus,
            'remaining_todos': remaining_todos
        }
    
    def generate_evening_report(self) -> Dict[str, Any]:
        """Generate evening report data."""
        # Get today's commits
        today = datetime.now()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        commits = self.fetch_commits(start_of_today)
        todo_analysis = self.analyze_todo_completion(commits)
        productivity = self.calculate_productivity_score(commits, todo_analysis)
        
        # Get todos for tomorrow
        remaining_todos = []
        for category in ['high_priority', 'medium_priority', 'low_priority']:
            remaining_todos.extend(self.todo_list['categories'].get(category, []))
        
        # Identify overdue items (high priority not completed)
        overdue_items = self.todo_list['categories'].get('high_priority', [])[:5]
        
        return {
            'report_type': 'evening',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'today_commits': commits,
            'today_summary': self.generate_ai_summary(commits, "today"),
            'productivity': productivity,
            'todo_analysis': todo_analysis,
            'tomorrow_preview': remaining_todos[:5],
            'overdue_items': overdue_items
        }
    
    def send_email(self, report_data: Dict[str, Any]):
        """Send email report using Resend API."""
        if self.email_config.get('provider') == 'resend':
            return self.send_via_resend(report_data)
        elif self.email_config.get('provider') == 'smtp':
            return self.send_via_smtp(report_data)
        else:
            print("No email provider configured")
            return False
    
    def send_via_resend(self, report_data: Dict[str, Any]) -> bool:
        """Send email using Resend API."""
        import resend
        
        resend.api_key = self.email_config.get('api_key')
        
        # Load appropriate template
        template_file = f"templates/{report_data['report_type']}_report.html"
        with open(template_file, 'r') as f:
            html_content = f.read()
        
        # Render template with data
        html_content = self.render_template(html_content, report_data)
        
        # Create plain text version
        plain_text = self.generate_plain_text(report_data)
        
        try:
            resend.Emails.send({
                "from": self.email_config.get('from_email'),
                "to": [self.email_config.get('to_email')],
                "subject": self.generate_subject(report_data),
                "html": html_content,
                "text": plain_text
            })
            return True
        except Exception as e:
            print(f"Error sending email via Resend: {e}")
            return False
    
    def send_via_smtp(self, report_data: Dict[str, Any]) -> bool:
        """Send email via SMTP (Gmail, etc.)."""
        # Load template
        template_file = f"templates/{report_data['report_type']}_report.html"
        with open(template_file, 'r') as f:
            html_content = f.read()
        
        html_content = self.render_template(html_content, report_data)
        plain_text = self.generate_plain_text(report_data)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.generate_subject(report_data)
        msg['From'] = self.email_config.get('from_email')
        msg['To'] = self.email_config.get('to_email')
        
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            with smtplib.SMTP_SSL(self.email_config.get('smtp_server'), 
                                 self.email_config.get('smtp_port', 465)) as server:
                server.login(self.email_config.get('smtp_username'),
                           self.email_config.get('smtp_password'))
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email via SMTP: {e}")
            return False
    
    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Simple template rendering with placeholders."""
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                template = template.replace(f'{{{{{key}}}}}', str(value))
            elif isinstance(value, list):
                # Handle lists specially
                if key == 'yesterday_commits':
                    items_html = ''
                    for commit in value[:10]:  # Limit to 10 commits
                        items_html += f"""
                        <div class="commit-item">
                            <strong>{commit['message'].split('\n')[0]}</strong><br>
                            <small>Files: {len(commit['files_changed'])} | Time: {commit['date'][11:16]}</small>
                        </div>
                        """
                    template = template.replace('{{yesterday_commits}}', items_html)
                elif key == 'recommended_focus':
                    items_html = ''.join([f'<li>{item}</li>' for item in value])
                    template = template.replace('{{recommended_focus}}', items_html)
        
        return template
    
    def generate_plain_text(self, report_data: Dict[str, Any]) -> str:
        """Generate plain text version of report."""
        if report_data['report_type'] == 'morning':
            return self._generate_morning_plain_text(report_data)
        else:
            return self._generate_evening_plain_text(report_data)
    
    def _generate_morning_plain_text(self, report_data: Dict[str, Any]) -> str:
        """Generate plain text morning report."""
        text = f"Morning Productivity Report - {report_data['date']}\n"
        text += "=" * 50 + "\n\n"
        
        text += "YESTERDAY'S ACCOMPLISHMENTS:\n"
        if report_data['yesterday_commits']:
            for commit in report_data['yesterday_commits'][:5]:
                text += f"- {commit['message'].split('\n')[0]}\n"
                text += f"  Files: {len(commit['files_changed'])} | Time: {commit['date'][11:16]}\n"
        else:
            text += "No commits yesterday.\n"
        
        text += f"\nSummary: {report_data['yesterday_summary']}\n\n"
        
        text += "TODO PROGRESS:\n"
        text += f"Completed: {len(report_data['todo_analysis']['completed'])} items\n"
        text += f"Remaining: {len(report_data['todo_analysis']['remaining'])} items\n\n"
        
        text += "TODAY'S RECOMMENDED FOCUS:\n"
        for item in report_data['recommended_focus']:
            text += f"- {item}\n"
        
        return text
    
    def _generate_evening_plain_text(self, report_data: Dict[str, Any]) -> str:
        """Generate plain text evening report."""
        text = f"Evening Productivity Report - {report_data['date']}\n"
        text += "=" * 50 + "\n\n"
        
        text += "TODAY'S ACTIVITY:\n"
        if report_data['today_commits']:
            text += f"Commits: {len(report_data['today_commits'])}\n"
            text += f"Files changed: {report_data['productivity']['files_changed']}\n"
        else:
            text += "No commits today.\n"
        
        text += f"\nSummary: {report_data['today_summary']}\n\n"
        
        text += "PRODUCTIVITY SCORE:\n"
        text += f"{report_data['productivity']['visual']}\n"
        text += f"Todo completion: {report_data['todo_analysis']['completion_rate']:.1f}%\n\n"
        
        text += "TOMORROW'S PREVIEW:\n"
        for item in report_data['tomorrow_preview']:
            text += f"- {item}\n"
        
