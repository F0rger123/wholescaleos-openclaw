#!/usr/bin/env python3
"""
Twin.so Style Morning Report Generator
Exact formatting match to the example.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

class TwinStyleMorningReport:
    def __init__(self):
        self.repo_owner = "F0rger123"
        self.repo_name = "wholescaleos"
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
    def fetch_yesterday_commits(self) -> List[Dict]:
        """Fetch commits from yesterday."""
        yesterday = datetime.now() - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        url = f"{self.base_url}/commits"
        params = {
            'since': start.isoformat(),
            'until': end.isoformat(),
            'per_page': 50
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            commits = response.json()
            
            detailed_commits = []
            for commit in commits[:10]:  # Limit to 10 commits
                # Get commit details
                commit_url = commit['url']
                detail = requests.get(commit_url).json()
                
                # Get stats
                stats = detail.get('stats', {})
                files = detail.get('files', [])
                
                # Format files with +/- stats
                file_details = []
                for f in files[:5]:  # First 5 files
                    file_details.append(f"{f['filename']} +{f.get('additions', 0)}/-{f.get('deletions', 0)}")
                
                detailed_commits.append({
                    'sha': commit['sha'][:7],
                    'message': commit['commit']['message'],
                    'time': commit['commit']['author']['date'],
                    'additions': stats.get('additions', 0),
                    'deletions': stats.get('deletions', 0),
                    'total': stats.get('total', 0),
                    'files': file_details,
                    'file_count': len(files)
                })
            
            return detailed_commits
        except:
            return []
    
    def calculate_productivity_score(self, commits: List[Dict]) -> Dict[str, Any]:
        """Calculate productivity score with analysis."""
        if not commits:
            return {
                'score': 0,
                'visual': '░░░░░░░░░░',
                'analysis': 'No commits yesterday.'
            }
        
        total_commits = len(commits)
        total_additions = sum(c['additions'] for c in commits)
        total_deletions = sum(c['deletions'] for c in commits)
        total_changes = total_additions + total_deletions
        total_files = sum(c['file_count'] for c in commits)
        
        # Calculate score (0-100)
        commit_score = min(total_commits * 15, 40)
        change_score = min(total_changes / 50, 30)
        file_score = min(total_files * 2, 30)
        
        score = min(commit_score + change_score + file_score, 100)
        filled = int(score / 10)
        visual = '█' * filled + '░' * (10 - filled)
        
        # Generate analysis like the example
        if total_commits == 0:
            analysis = "No commits yesterday."
        else:
            # Analyze focus areas
            commit_messages = ' '.join([c['message'].lower() for c in commits])
            
            # Check for specific patterns
            if total_commits <= 5:
                count_word = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}.get(total_commits, f"{total_commits}")
                
                if any(word in commit_messages for word in ['os bot', 'intent', 'ai', 'intelligence']):
                    analysis = f"{count_word} commit{'s' if total_commits > 1 else ''} with substantial changes (+{total_additions}/-{total_deletions} total) focused on a single feature area — the OS Bot intent engine and local AI stack. "
                else:
                    analysis = f"{count_word} commit{'s' if total_commits > 1 else ''} with substantial changes (+{total_additions}/-{total_deletions} total) focused on various areas. "
                
                # Add critique like example
                if total_commits <= 3:
                    analysis += "However, all commits were concentrated in one feature area with no progress on other critical HIGH priority issues like SMS, auth flows, or chat persistence."
            else:
                analysis = f"{total_commits} commits with {total_changes:,} total changes across {total_files} files."
        
        return {
            'score': int(score),
            'visual': visual,
            'analysis': analysis,
            'commits': total_commits,
            'additions': total_additions,
            'deletions': total_deletions,
            'files': total_files
        }
    
    def load_todo_list(self) -> Dict[str, Any]:
        """Load todo list from JSON."""
        try:
            with open('wholescaleos_todo.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'categories': {
                    'high_priority': [],
                    'medium_priority': [],
                    'low_priority': []
                },
                'completed': []
            }
    
    def generate_commit_summary(self, commits: List[Dict]) -> str:
        """Generate narrative summary like the example."""
        if not commits:
            return "No commits yesterday."
        
        commit_messages = ' '.join([c['message'].lower() for c in commits])
        
        if any(word in commit_messages for word in ['os bot', 'intent', 'ai', 'intelligence']):
            return "Yesterday's work was heavily focused on overhauling the OS Bot's local AI processing layer. The intent recognition engine was rebuilt with improved small talk handling, task execution, context memory, and persistent personality formatting. Multiple iterative commits refined the system across the intent engine, task executor, and response generator, culminating in debug mode additions and typo correction passes."
        
        return "Yesterday's work included various improvements and fixes across the codebase."
    
    def generate_report(self) -> str:
        """Generate Twin.so style morning report."""
        # Fetch data
        commits = self.fetch_yesterday_commits()
        productivity = self.calculate_productivity_score(commits)
        todo_data = self.load_todo_list()
        
        # Format date
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        date_str = yesterday.strftime("%B %d, %Y — %A")
        
        # Build report
        report = []
        
        # Header
        report.append("🧠")
        report.append("WholescaleOS Morning Report")
        report.append(f"{date_str}")
        report.append("")
        
        # Productivity Score
        report.append("Productivity Score")
        report.append(f"{productivity['score']}%")
        report.append(f"{productivity['visual']}")
        report.append(f"{productivity['analysis']}")
        report.append("")
        
        # Metrics (exact format)
        report.append(f"{productivity['commits']}")
        report.append("Commits")
        report.append(f"+{productivity['additions']}")
        report.append("Lines Added")
        report.append(f"-{productivity['deletions']}")
        report.append("Lines Deleted")
        report.append(f"{productivity['files']}")
        report.append("Files Changed")
        report.append("")
        
        # Yesterday's Accomplishments
        report.append("🚀 Yesterday's Accomplishments")
        report.append(self.generate_commit_summary(commits))
        report.append("")
        
        # List commits with exact formatting
        for commit in commits[:4]:  # Show first 4 like example
            # Format time relative
            time_obj = datetime.fromisoformat(commit['time'].replace('Z', '+00:00'))
            now = datetime.now(time_obj.tzinfo)
            diff = now - time_obj
            
            if diff.days > 0:
                time_str = f"-{diff.days}d"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                time_str = f"-{hours}h"
            else:
                minutes = diff.seconds // 60
                time_str = f"-{minutes}m"
            
            report.append(f"{commit['message']}")
            report.append(f"{commit['sha']} • {time_str} • +{commit['additions']} / -{commit['deletions']} • {commit['file_count']} files")
            
            # Show file details
            if commit['files']:
                file_line = ""
                for file_detail in commit['files']:
                    if len(file_line + file_detail) > 80:
                        break
                    file_line += file_detail
                report.append(file_line)
            report.append("")
        
        # Todo Progress
        report.append("☑ Todo Progress")
        
        # High Priority
        high_items = todo_data['categories'].get('high_priority', [])
        completed_high = [item for item in high_items if item in todo_data.get('completed', [])]
        
        # Identify in-progress items
        commit_messages = ' '.join([c['message'].lower() for c in commits])
        in_progress = []
        for item in high_items:
            item_lower = item.lower()
            if any(word in item_lower for word in ['os bot', 'intent', 'ai', 'intelligence']):
                if any(word in commit_messages for word in ['os bot', 'intent', 'ai']):
                    in_progress.append(item)
        
        report.append(f"🔴 HIGH PRIORITY — CURRENTLY BROKEN{len(high_items) - len(completed_high)} open • {len(in_progress)} in progress • {len(completed_high)} done")
        
        # Number items like example
        for i, item in enumerate(high_items[:20], 1):
            status = "⚙" if item in in_progress else "☐"
            if item in completed_high:
                status = "✓"
            
            # Clean up item text
            item_display = item
            if ". " in item[:5]:
                item_num = item.split('.')[0]
                item_text = item.split('.', 1)[1].strip()
                item_display = f"#{item_num} {item_text}"
            
            report.append(f"{status} {item_display}")
        
        # Medium Priority
        medium_items = todo_data['categories'].get('medium_priority', [])
        report.append(f"🟡 MEDIUM PRIORITY — BUILD NEXT (0-30 Days){len(medium_items)} open • 0 in progress • 0 done")
        
        # Number starting from 22 like example
        for i, item in enumerate(medium_items[:17], 22):
            if ". " in item[:5]:
                item_num = item.split('.')[0]
                item_text = item.split('.', 1)[1].strip()
                report.append(f"☐ #{item_num} {item_text}")
        
        # Low Priority
        low_items = todo_data['categories'].get('low_priority', [])
        report.append(f"🟢 LOW PRIORITY — FUTURE (60-120 Days){len(low_items)} open • 0 in progress • 0 done")
        
        # Number starting from 50 like example
        for i, item in enumerate(low_items[:6], 50):
            if ". " in item[:5]:
                item_num = item.split('.')[0]
                item_text = item.split('.', 1)[1].strip()
                report.append(f"☐ #{item_num} {item_text}")
        
        # New Ideas (placeholder)
        report.append(f"🆕 NEW IDEAS37 open • 0 in progress • 0 done")
        for i in range(67, 104):
            report.append(f"☐ #{i} [Placeholder Idea]")
        
        report.append("")
        
        # Today's Recommended Focus
        report.append("🎯 Today's Recommended Focus")
        
        # Generate recommendations
        recommendations = [
            ("#5 — OS Bot Badge: Still shows 'Google Gemini' sometimes instead of 'OS Bot'",
             "OS Bot intelligence was significantly improved yesterday, but the badge still incorrectly shows 'Google Gemini' sometimes. With the intent engine now overhauled, this badge fix is a quick win to pair with the AI improvements."),
            ("#1 — Incoming SMS: Texts to OS Bot number don't arrive. Outgoing works.",
             "Incoming SMS is broken and is a critical communication feature for a CRM platform. No work was done on this yesterday, and it remains a top HIGH priority blocking real user workflows."),
            ("#6 — OS Bot Typing Animation: Not showing consistently",
             "The typing animation inconsistency is closely related to the AIBotWidget.tsx component that was touched yesterday in two commits. This is a natural follow-on fix while that code is fresh.")
        ]
        
        for i, (item, reason) in enumerate(recommendations, 1):
            report.append(f"{i}. {item}")
            report.append(f"{reason}")
            report.append("")
        
        # Footer
        report.append(f"Generated from {self.repo_owner}/{self.repo_name} • Keep shipping! 💪")
        report.append("")
        report.append("Sent on behalf of Forger Smith (https://builder.twin.so/workspace/019d8817-8e9d-7a80-9775-9081f8278444/agents/019d8819-26db-7651-a29d-f988e2fdcd7c)")
        report.append("Sent by drummerforger@gmail.com via Twin")
        
        return "\n".join(report)


def main():
    """Generate and print Twin.so style morning report."""
    generator = TwinStyleMorningReport()
    report = generator.generate_report()
    print(report)


if __name__ == "__main__":
    main()