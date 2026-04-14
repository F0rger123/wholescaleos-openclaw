#!/usr/bin/env python3
"""
Enhanced Morning Report Generator
Matches the beautiful Twin.so report format.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

class EnhancedMorningReport:
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
            for commit in commits[:20]:  # Limit to 20 commits
                # Get commit details
                commit_url = commit['url']
                detail = requests.get(commit_url).json()
                
                # Get stats
                stats = detail.get('stats', {})
                files = detail.get('files', [])
                
                detailed_commits.append({
                    'sha': commit['sha'][:7],
                    'message': commit['commit']['message'],
                    'time': commit['commit']['author']['date'],
                    'additions': stats.get('additions', 0),
                    'deletions': stats.get('deletions', 0),
                    'total': stats.get('total', 0),
                    'files': [f['filename'] for f in files[:5]],  # First 5 files
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
        commit_score = min(total_commits * 15, 40)  # Max 40 for commits
        change_score = min(total_changes / 50, 30)  # Max 30 for changes
        file_score = min(total_files * 2, 30)       # Max 30 for files
        
        score = min(commit_score + change_score + file_score, 100)
        filled = int(score / 10)
        visual = '█' * filled + '░' * (10 - filled)
        
        # Generate analysis
        if total_commits == 0:
            analysis = "No commits yesterday."
        elif total_commits == 1:
            analysis = f"One commit with {total_changes:,} total changes across {total_files} files."
        else:
            # Analyze focus areas
            commit_messages = ' '.join([c['message'].lower() for c in commits])
            focus_areas = []
            
            if any(word in commit_messages for word in ['os bot', 'intent', 'ai', 'intelligence']):
                focus_areas.append("OS Bot/AI")
            if any(word in commit_messages for word in ['sms', 'text', 'message']):
                focus_areas.append("SMS/Communication")
            if any(word in commit_messages for word in ['ui', 'sidebar', 'button', 'theme']):
                focus_areas.append("UI/UX")
            if any(word in commit_messages for word in ['auth', '2fa', 'password', 'login']):
                focus_areas.append("Authentication")
            if any(word in commit_messages for word in ['workflow', 'automation', 'template']):
                focus_areas.append("Workflows")
            
            if focus_areas:
                focus_text = " — ".join(focus_areas)
                analysis = f"{total_commits} commits with {total_changes:,} total changes focused on {focus_text}."
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
    
    def generate_report(self) -> str:
        """Generate enhanced morning report."""
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
        
        # Metrics
        report.append(f"{productivity['commits']}")
        report.append("Commits")
        report.append(f"+{productivity['additions']:,}")
        report.append("Lines Added")
        report.append(f"-{productivity['deletions']:,}")
        report.append("Lines Deleted")
        report.append(f"{productivity['files']}")
        report.append("Files Changed")
        report.append("")
        
        # Yesterday's Accomplishments
        report.append("🚀 Yesterday's Accomplishments")
        if commits:
            # Generate narrative summary
            summary = self.generate_commit_summary(commits)
            report.append(summary)
            report.append("")
            
            # List commits
            for commit in commits[:5]:  # Show first 5 commits
                time_str = datetime.fromisoformat(commit['time'].replace('Z', '+00:00'))
                time_display = time_str.strftime("%-I:%M %p UTC")
                
                # Truncate message
                message = commit['message']
                if len(message) > 80:
                    message = message[:77] + "..."
                
                report.append(f"{message}")
                report.append(f"{commit['sha']} • {time_display} • +{commit['additions']} / -{commit['deletions']} • {commit['file_count']} files")
                
                # Show files (truncated)
                if commit['files']:
                    files_text = " ".join(commit['files'][:3])
                    if len(commit['files']) > 3:
                        files_text += f" +{len(commit['files']) - 3} more"
                    report.append(files_text)
                report.append("")
        else:
            report.append("No commits yesterday.")
            report.append("")
        
        # Todo Progress
        report.append("☑ Todo Progress")
        
        # High Priority
        high_items = todo_data['categories'].get('high_priority', [])
        completed_high = [item for item in high_items if item in todo_data.get('completed', [])]
        in_progress = self.identify_in_progress(commits, high_items)
        
        report.append(f"🔴 HIGH PRIORITY — CURRENTLY BROKEN")
        report.append(f"{len(high_items) - len(completed_high)} open • {len(in_progress)} in progress • {len(completed_high)} done")
        
        for i, item in enumerate(high_items[:20], 1):  # Show first 20
            status = "⚙" if item in in_progress else "☐"
            if item in completed_high:
                status = "✓"
            
            # Extract item number if present
            item_display = item
            if ". " in item[:5]:
                item_display = f"#{item.split('.')[0]} {item.split('.', 1)[1].strip()}"
            
            report.append(f"{status} {item_display}")
        report.append("")
        
        # Medium Priority
        medium_items = todo_data['categories'].get('medium_priority', [])
        report.append(f"🟡 MEDIUM PRIORITY — BUILD NEXT (0-30 Days)")
        report.append(f"{len(medium_items)} open • 0 in progress • 0 done")
        
        for i, item in enumerate(medium_items[:10], 22):  # Continue numbering
            if ". " in item[:5]:
                item_num = item.split('.')[0]
                item_display = f"#{item_num} {item.split('.', 1)[1].strip()}"
                report.append(f"☐ {item_display}")
        report.append("")
        
        # Low Priority
        low_items = todo_data['categories'].get('low_priority', [])
        report.append(f"🟢 LOW PRIORITY — FUTURE (60-120 Days)")
        report.append(f"{len(low_items)} open • 0 in progress • 0 done")
        
        for i, item in enumerate(low_items[:6], 50):  # Continue numbering
            if ". " in item[:5]:
                item_num = item.split('.')[0]
                item_display = f"#{item_num} {item.split('.', 1)[1].strip()}"
                report.append(f"☐ {item_display}")
        report.append("")
        
        # Today's Recommended Focus
        report.append("🎯 Today's Recommended Focus")
        focus_items = self.recommend_focus_items(todo_data, commits)
        
        for i, (item, reason) in enumerate(focus_items[:3], 1):
            # Extract item number
            item_num = "?"
            if ". " in item[:5]:
                item_num = item.split('.')[0]
            
            report.append(f"{i}. #{item_num} — {item.split('.', 1)[1].strip() if '. ' in item else item}")
            report.append(f"{reason}")
            report.append("")
        
        # Footer
        report.append(f"Generated from {self.repo_owner}/{self.repo_name} • Keep shipping! 💪")
        report.append("")
        report.append("Sent on behalf of Forger Smith")
        report.append("Sent by drummerforger@gmail.com via OpenClaw")
        
        return "\n".join(report)
    
    def generate_commit_summary(self, commits: List[Dict]) -> str:
        """Generate narrative summary of commits."""
        if not commits:
            return "No commits yesterday."
        
        total_commits = len(commits)
        total_changes = sum(c['additions'] + c['deletions'] for c in commits)
        
        # Analyze commit messages
        messages = ' '.join([c['message'].lower() for c in commits])
        
        # Check for feature areas
        features = []
        if any(word in messages for word in ['os bot', 'intent', 'ai', 'intelligence']):
            features.append("OS Bot intelligence")
        if any(word in messages for word in ['fix', 'bug', 'error', 'resolve']):
            features.append("bug fixes")
        if any(word in messages for word in ['feat', 'implement', 'add', 'create']):
            features.append("new features")
        if any(word in messages for word in ['refactor', 'improve', 'optimize', 'enhance']):
            features.append("improvements")
        
        if features:
            features_text = ", ".join(features[:-1]) + " and " + features[-1] if len(features) > 1 else features[0]
            return f"Yesterday's work included {total_commits} commits with {total_changes:,} total changes focused on {features_text}."
        else:
            return f"Yesterday included {total_commits} commits with {total_changes:,} total changes."
    
    def identify_in_progress(self, commits: List[Dict], todo_items: List[str]) -> List[str]:
        """Identify which todo items are in progress based on commits."""
        in_progress = []
        if not commits:
            return in_progress
        
        commit_messages = ' '.join([c['message'].lower() for c in commits])
        
        for item in todo_items:
            item_lower = item.lower()
            # Extract keywords from todo item
            keywords = [word for word in item_lower.split() if len(word) > 4]
            
            # Check if any keyword appears in commit messages
            if keywords and any(keyword in commit_messages for keyword in keywords[:3]):
                in_progress.append(item)
        
        return in_progress
    
    def recommend_focus_items(self, todo_data: Dict[str, Any], commits: List[Dict]) -> List[tuple]:
        """Recommend focus items for today."""
        high_priority = todo_data['categories'].get('high_priority', [])
        completed = todo_data.get('completed', [])
        
        # Filter out completed items
        available_items = [item for item in high_priority if item not in completed]
        
        # Check which items might be related to yesterday's work
        commit_messages = ' '.join([c['message'].lower() for c in commits]) if commits else ""
        
        recommendations = []
        
        # First priority: Items related to yesterday's work
        for item in available_items:
            item_lower = item.lower()
            keywords = [word for word in item_lower.split() if len(word) > 4]
            
            if keywords and any(keyword in commit_messages for keyword in keywords[:3]):
                reason = "Related to yesterday's work — natural follow-up."
                recommendations.append((item, reason))
        
        # Second priority: Critical communication features
        communication_items = [item for item in available_items 
                              if any(word in item.lower() for word in ['sms', 'text', 'message', 'incoming'])]
        for item in communication_items[:2]:
            if item not in [r[0] for r in recommendations]:
                reason = "Critical communication feature that's currently broken."
                recommendations.append((item, reason))
        
        # Third priority: UI/UX issues
        ui_items = [item for item in available_items 
                   if any(word in item.lower() for word in ['ui', 'sidebar', 'button', 'theme', 'badge'])]
        for item in ui_items[:2]:
            if item not in [r[0] for r in recommendations]:
                reason = "UI/UX issue affecting user experience."
                recommendations.append((item, reason))
        
        # Fill remaining slots with other high priority items
        for item in available_items:
            if len(recommendations) >= 3:
                break
            if item not in [r[0] for r in recommendations]:
                reason = "High priority item that needs attention."
                recommendations.append((item, reason))
        
        return recommendations[:3]


def main():
    """Generate and print enhanced morning report."""
    generator = EnhancedMorningReport()
    report = generator.generate_report()
    print(report)


if __name__ == "__main__":
    main()