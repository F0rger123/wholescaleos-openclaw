#!/usr/bin/env python3
"""
WholescaleOS Public Repository Monitor
Monitors F0rger123/wholescaleos public repo and generates productivity reports.
No API keys needed for public repositories.
"""

import json
import requests
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any
import re

class WholescaleOSMonitor:
    def __init__(self):
        """Initialize monitor for public GitHub repo."""
        self.repo_owner = "F0rger123"
        self.repo_name = "wholescaleos"
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        # Load todo list
        self.todo_list_path = "wholescaleos_todo.json"
        self.todo_data = self.load_todo_list()
        
        # State tracking
        self.state_path = "wholescaleos_monitor_state.json"
        self.state = self.load_state()
    
    def load_todo_list(self) -> Dict[str, Any]:
        """Load WholescaleOS todo list."""
        try:
            with open(self.todo_list_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default structure
            return {
                "categories": {
                    "high_priority": [],
                    "medium_priority": [],
                    "low_priority": []
                },
                "completed": [],
                "last_checked": None,
                "last_commit_sha": None
            }
    
    def save_todo_list(self):
        """Save todo list."""
        self.todo_data["last_checked"] = datetime.now().isoformat()
        with open(self.todo_list_path, 'w') as f:
            json.dump(self.todo_data, f, indent=2)
    
    def load_state(self) -> Dict[str, Any]:
        """Load monitor state."""
        try:
            with open(self.state_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "last_run": None,
                "last_morning_report": None,
                "last_evening_report": None,
                "processed_commits": []
            }
    
    def save_state(self):
        """Save monitor state."""
        self.state["last_run"] = datetime.now().isoformat()
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def fetch_recent_commits(self, hours: int = 24) -> List[Dict]:
        """Fetch recent commits from public repository."""
        url = f"{self.base_url}/commits"
        
        # Calculate since time
        since_time = datetime.now() - timedelta(hours=hours)
        params = {
            'since': since_time.isoformat(),
            'per_page': 50  # Limit for public API
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            commits = response.json()
            
            # Process commits
            processed_commits = []
            for commit in commits[:30]:  # Limit to 30 commits
                commit_data = {
                    'sha': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'url': commit['html_url']
                }
                
                # Get commit details if we haven't seen it before
                if commit['sha'] not in self.state.get("processed_commits", []):
                    detail = self.get_commit_details(commit['sha'])
                    if detail:
                        commit_data.update(detail)
                    
                    # Mark as processed
                    self.state.setdefault("processed_commits", []).append(commit['sha'])
                
                processed_commits.append(commit_data)
            
            return processed_commits
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commits: {e}")
            return []
    
    def get_commit_details(self, sha: str) -> Dict[str, Any]:
        """Get detailed commit information."""
        url = f"{self.base_url}/commits/{sha}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract file changes
            files_changed = [file['filename'] for file in data.get('files', [])]
            
            # Get stats
            stats = data.get('stats', {})
            
            return {
                'files_changed': files_changed,
                'additions': stats.get('additions', 0),
                'deletions': stats.get('deletions', 0),
                'total_changes': stats.get('total', 0)
            }
        except:
            return {}
    
    def analyze_todo_completion(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze which todo items were completed based on commits."""
        # Extract all commit messages
        commit_messages = ' '.join([c['message'].lower() for c in commits])
        
        completed_items = []
        
        # Check each category
        for category in ['high_priority', 'medium_priority', 'low_priority']:
            category_items = self.todo_data['categories'].get(category, [])
            for item in category_items[:]:  # Copy for iteration
                item_lower = item.lower()
                
                # Simple keyword matching
                # Extract meaningful keywords (words > 4 chars)
                keywords = [word for word in item_lower.split() 
                           if len(word) > 4 and word not in ['priority', 'intelligence', 'functionality']]
                
                if keywords and any(keyword in commit_messages for keyword in keywords[:3]):
                    # Move from category to completed
                    self.todo_data['categories'][category].remove(item)
                    if item not in self.todo_data['completed']:
                        self.todo_data['completed'].append(item)
                    completed_items.append({
                        'item': item,
                        'category': category
                    })
        
        if completed_items:
            self.save_todo_list()
        
        return {
            'completed': completed_items,
            'total_completed': len(completed_items)
        }
    
    def generate_morning_report(self, commits: List[Dict]) -> str:
        """Generate morning report text."""
        report = []
        report.append("🌅 **WHOLESCALEOS MORNING REPORT**")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %I:%M %p %Z')}")
        report.append("")
        
        # Yesterday's commits
        report.append("📊 **YESTERDAY'S COMMITS**")
        if commits:
            for i, commit in enumerate(commits[:10], 1):
                # Truncate long messages
                message = commit['message'].split('\n')[0]
                if len(message) > 80:
                    message = message[:77] + "..."
                
                time_str = commit['date'][11:16] if 'date' in commit else "N/A"
                files = len(commit.get('files_changed', []))
                
                report.append(f"{i}. {message}")
                report.append(f"   ⏰ {time_str} | 📁 {files} files")
        else:
            report.append("No commits yesterday.")
        report.append("")
        
        # Todo analysis
        todo_analysis = self.analyze_todo_completion(commits)
        report.append("✅ **TODO PROGRESS**")
        
        # Count items in each category
        high_count = len(self.todo_data['categories'].get('high_priority', []))
        medium_count = len(self.todo_data['categories'].get('medium_priority', []))
        low_count = len(self.todo_data['categories'].get('low_priority', []))
        completed_count = len(self.todo_data.get('completed', []))
        
        report.append(f"🔴 High Priority: {high_count} items")
        report.append(f"🟡 Medium Priority: {medium_count} items")
        report.append(f"🟢 Low Priority: {low_count} items")
        report.append(f"✅ Completed: {completed_count} items")
        report.append(f"📈 Newly Completed: {todo_analysis['total_completed']}")
        report.append("")
        
        # Recommended focus
        report.append("🎯 **TODAY'S RECOMMENDED FOCUS**")
        high_priority = self.todo_data['categories'].get('high_priority', [])
        if high_priority:
            for i, item in enumerate(high_priority[:3], 1):
                # Shorten long items
                if len(item) > 60:
                    item = item[:57] + "..."
                report.append(f"{i}. {item}")
        else:
            report.append("All high priority items completed! 🎉")
        
        return "\n".join(report)
    
    def generate_evening_report(self, commits: List[Dict]) -> str:
        """Generate evening report text."""
        report = []
        report.append("🌙 **WHOLESCALEOS EVENING REPORT**")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %I:%M %p %Z')}")
        report.append("")
        
        # Today's activity
        report.append("📈 **TODAY'S ACTIVITY**")
        if commits:
            commit_count = len(commits)
            total_files = sum(len(c.get('files_changed', [])) for c in commits)
            total_changes = sum(c.get('total_changes', 0) for c in commits)
            
            report.append(f"• Commits: {commit_count}")
            report.append(f"• Files changed: {total_files}")
            report.append(f"• Total changes: {total_changes} (+/-)")
            
            # Show top commits
            if commits:
                report.append("")
                report.append("**Top commits today:**")
                for i, commit in enumerate(commits[:5], 1):
                    message = commit['message'].split('\n')[0]
                    if len(message) > 60:
                        message = message[:57] + "..."
                    report.append(f"{i}. {message}")
        else:
            report.append("No commits today.")
        report.append("")
        
        # Productivity score
        report.append("📊 **PRODUCTIVITY SCORE**")
        
        if commits:
            # Simple scoring based on commits and changes
            commit_score = min(len(commits) * 10, 40)
            change_score = min(sum(len(c.get('files_changed', [])) for c in commits) * 2, 30)
            todo_score = len(self.todo_data.get('completed', [])) * 1
            
            total_score = min(commit_score + change_score + todo_score, 100)
            
            # Visual indicator
            filled = int(total_score / 10)
            visual = "█" * filled + "░" * (10 - filled)
            
            report.append(f"{visual} {total_score}%")
            report.append(f"• Based on {len(commits)} commits")
            report.append(f"• {sum(len(c.get('files_changed', [])) for c in commits)} files changed")
        else:
            report.append("░░░░░░░░░░ 0%")
            report.append("• No activity today")
        report.append("")
        
        # Tomorrow's preview
        report.append("🔮 **TOMORROW'S PREVIEW**")
        high_priority = self.todo_data['categories'].get('high_priority', [])
        if high_priority:
            for i, item in enumerate(high_priority[:3], 1):
                if len(item) > 50:
                    item = item[:47] + "..."
                report.append(f"{i}. {item}")
        else:
            medium_priority = self.todo_data['categories'].get('medium_priority', [])
            if medium_priority:
                for i, item in enumerate(medium_priority[:2], 1):
                    if len(item) > 50:
                        item = item[:47] + "..."
                    report.append(f"{i}. {item}")
            else:
                report.append("All priorities addressed! Consider adding new features.")
        
        return "\n".join(report)
    
    def run_morning_check(self):
        """Run morning check and return report."""
        print("Running morning check...")
        
        # Get commits from last 24 hours
        commits = self.fetch_recent_commits(hours=24)
        
        # Generate report
        report = self.generate_morning_report(commits)
        
        # Update state
        self.state["last_morning_report"] = datetime.now().isoformat()
        self.save_state()
        
        return report
    
    def run_evening_check(self):
        """Run evening check and return report."""
        print("Running evening check...")
        
        # Get commits from last 12 hours (since morning)
        commits = self.fetch_recent_commits(hours=12)
        
        # Generate report
        report = self.generate_evening_report(commits)
        
        # Update state
        self.state["last_evening_report"] = datetime.now().isoformat()
        self.save_state()
        
        return report


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WholescaleOS Monitor")
    parser.add_argument("--morning", action="store_true", help="Generate morning report")
    parser.add_argument("--evening", action="store_true", help="Generate evening report")
    parser.add_argument("--test", action="store_true", help="Test with sample data")
    
    args = parser.parse_args()
    
    monitor = WholescaleOSMonitor()
    
    if args.morning:
        report = monitor.run_morning_check()
        print(report)
    elif args.evening:
        report = monitor.run_evening_check()
        print(report)
    elif args.test:
        # Test with sample data
        print("🧪 Testing WholescaleOS Monitor...")
        print("=" * 50)
        
        # Simulate some commits
        sample_commits = [
            {
                'sha': 'test123',
                'message': 'Fixed OS Bot badge display issue',
                'author': 'F0rger123',
                'date': (datetime.now() - timedelta(hours=2)).isoformat(),
                'files_changed': ['src/components/Badge.js', 'src/styles/ui.css'],
                'total_changes': 45
            }
        ]
        
        morning_report = monitor.generate_morning_report(sample_commits)
        print("\n📧 Sample Morning Report:")
        print("=" * 50)
        print(morning_report)
        
        print("\n✅ Test completed successfully!")
    else:
        # Default: show status
        print("WholescaleOS Monitor - Status")
        print(f"Repo: {monitor.repo_owner}/{monitor.repo_name}")
        print(f"Last run: {monitor.state.get('last_run', 'Never')}")
        
        high_count = len(monitor.todo_data['categories'].get('high_priority', []))
        print(f"High priority items: {high_count}")


if __name__ == "__main__":
    main()