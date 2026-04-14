#!/usr/bin/env python3
"""
WholescaleOS Complete Productivity System
Combines monitoring, idea collection, and email reporting.
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any

def run_complete_system(report_type: str = "morning"):
    """Run the complete WholescaleOS productivity system."""
    print(f"🚀 Running WholescaleOS {report_type.capitalize()} System")
    print("=" * 60)
    
    # Step 1: Run monitor
    print("1. 📊 Monitoring GitHub repository...")
    from wholescaleos_monitor import WholescaleOSMonitor
    monitor = WholescaleOSMonitor()
    
    if report_type == "morning":
        commits = monitor.fetch_recent_commits(hours=24)
        report_text = monitor.generate_morning_report(commits)
        todo_analysis = monitor.analyze_todo_completion(commits)
        
        # Prepare data for email
        todo_stats = {
            'high': len(monitor.todo_data['categories'].get('high_priority', [])),
            'medium': len(monitor.todo_data['categories'].get('medium_priority', [])),
            'low': len(monitor.todo_data['categories'].get('low_priority', [])),
            'completed': len(monitor.todo_data.get('completed', []))
        }
        
        focus_items = monitor.todo_data['categories'].get('high_priority', [])[:3]
        
        email_data = {
            'commits': commits[:10],  # Limit for email
            'todo_stats': todo_stats,
            'focus_items': focus_items
        }
    else:  # evening
        commits = monitor.fetch_recent_commits(hours=12)
        report_text = monitor.generate_evening_report(commits)
        todo_analysis = monitor.analyze_todo_completion(commits)
        
        # Calculate productivity score
        if commits:
            commit_score = min(len(commits) * 10, 40)
            change_score = min(sum(len(c.get('files_changed', [])) for c in commits) * 2, 30)
            todo_score = len(monitor.todo_data.get('completed', [])) * 1
            total_score = min(commit_score + change_score + todo_score, 100)
        else:
            total_score = 0
        
        focus_items = monitor.todo_data['categories'].get('high_priority', [])[:3]
        
        email_data = {
            'commits': commits[:10],
            'productivity': {
                'score': total_score,
                'commits_count': len(commits),
                'files_changed': sum(len(c.get('files_changed', [])) for c in commits)
            },
            'focus_items': focus_items
        }
    
    print(f"   ✓ Found {len(commits)} commits")
    print(f"   ✓ {todo_analysis['total_completed']} todo items completed")
    
    # Step 2: Send to WhatsApp (via OpenClaw)
    print("\n2. 💬 Sending to WhatsApp...")
    print(report_text)
    print("   ✓ Report ready for WhatsApp")
    
    # Step 3: Send email if configured
    print("\n3. 📧 Sending email report...")
    try:
        from gmail_reporter import GmailReporter
        reporter = GmailReporter()
        
        success = reporter.send_report(report_type, report_text)
        if success:
            print(f"   ✓ Email sent to drummerforger@gmail.com")
    except Exception as e:
        print(f"   ⚠️ Email error: {e}")
    
    # Step 4: Update state
    print("\n4. 💾 Saving system state...")
    monitor.save_state()
    print("   ✓ State saved")
    
    print("\n" + "=" * 60)
    print(f"✅ {report_type.capitalize()} system run completed!")
    
    return {
        'success': True,
        'report_type': report_type,
        'commits_found': len(commits),
        'todo_completed': todo_analysis['total_completed'],
        'report_text': report_text
    }


def process_whatsapp_idea(message: str):
    """Process a WhatsApp message as an idea."""
    print(f"💡 Processing WhatsApp idea...")
    print(f"Message: {message[:100]}...")
    
    try:
        from idea_collector import IdeaCollector
        collector = IdeaCollector()
        
        result = collector.process_whatsapp_message(message)
        
        if result['processed']:
            if result['added']:
                print(f"✅ Idea added to {result['category']}:")
                print(f"   {result['idea'][:80]}...")
                
                # Show updated stats
                stats = collector.show_stats()
                
                return {
                    'success': True,
                    'added': True,
                    'category': result['category'],
                    'idea': result['idea'],
                    'stats': stats
                }
            else:
                print("📝 Idea logged but not added (may be duplicate)")
                return {
                    'success': True,
                    'added': False,
                    'reason': 'Possible duplicate',
                    'idea': result.get('idea', '')
                }
        else:
            print(f"ℹ️  Not processed as idea: {result['reason']}")
            return {
                'success': True,
                'processed': False,
                'reason': result['reason']
            }
    except Exception as e:
        print(f"❌ Error processing idea: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def show_system_status():
    """Show current system status."""
    print("📊 WholescaleOS Productivity System - Status")
    print("=" * 60)
    
    # Load monitor state
    try:
        with open("wholescaleos_monitor_state.json", 'r') as f:
            state = json.load(f)
        print(f"📅 Last run: {state.get('last_run', 'Never')}")
        print(f"🌅 Last morning report: {state.get('last_morning_report', 'Never')}")
        print(f"🌙 Last evening report: {state.get('last_evening_report', 'Never')}")
        print(f"📝 Processed commits: {len(state.get('processed_commits', []))}")
    except FileNotFoundError:
        print("📅 System state: Not initialized")
    
    print()
    
    # Load todo stats
    try:
        with open("wholescaleos_todo.json", 'r') as f:
            todo_data = json.load(f)
        
        high = len(todo_data['categories'].get('high_priority', []))
        medium = len(todo_data['categories'].get('medium_priority', []))
        low = len(todo_data['categories'].get('low_priority', []))
        completed = len(todo_data.get('completed', []))
        
        print("✅ Todo Statistics:")
        print(f"   🔴 High Priority: {high} items")
        print(f"   🟡 Medium Priority: {medium} items")
        print(f"   🟢 Low Priority: {low} items")
        print(f"   ✅ Completed: {completed} items")
        print(f"   📈 Total: {high + medium + low + completed} items")
    except FileNotFoundError:
        print("✅ Todo system: Not initialized")
    
    print()
    
    # Check email config
    try:
        with open("email_config.json", 'r') as f:
            email_config = json.load(f)
        
        provider = email_config.get('provider', 'not configured')
        to_email = email_config.get('to_email', 'not set')
        
        print("📧 Email Configuration:")
        print(f"   Provider: {provider}")
        print(f"   Send to: {to_email}")
        
        if provider == 'smtp':
            password = email_config.get('smtp_password', '')
            if password and password != 'YOUR_GMAIL_APP_PASSWORD_HERE':
                print("   Status: ✅ Gmail SMTP configured")
            else:
                print("   Status: ⚠️ Needs Gmail app password")
                print("   ℹ️  Get from: https://myaccount.google.com/apppasswords")
        else:
            print("   Status: ⚠️ Not configured for Gmail")
    except (FileNotFoundError, json.JSONDecodeError):
        print("📧 Email: Not configured")
    
    print()
    print("🔄 Cron Jobs:")
    print("   Morning report: 7:00 AM EST (cron: 0 12 * * *)")
    print("   Evening report: 8:00 PM EST (cron: 0 1 * * *)")
    print("   Log file: /home/drummer/.openclaw/workspace/monitor.log")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WholescaleOS Complete Productivity System")
    parser.add_argument("--morning", action="store_true", help="Run morning report")
    parser.add_argument("--evening", action="store_true", help="Run evening report")
    parser.add_argument("--idea", help="Process an idea from WhatsApp")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--test", action="store_true", help="Test complete system")
    
    args = parser.parse_args()
    
    if args.morning:
        run_complete_system("morning")
    elif args.evening:
        run_complete_system("evening")
    elif args.idea:
        process_whatsapp_idea(args.idea)
    elif args.status:
        show_system_status()
    elif args.test:
        print("🧪 Testing Complete System...")
        print("=" * 60)
        
        # Test morning report
        print("\n1. Testing morning report:")
        test_result = run_complete_system("morning")
        
        print("\n2. Testing idea processing:")
        test_idea = "We should add AI-powered code review suggestions"
        idea_result = process_whatsapp_idea(test_idea)
        
        print("\n3. Showing system status:")
        show_system_status()
        
        print("\n" + "=" * 60)
        print("✅ Complete system test finished!")
    else:
        # Show help
        print("WholescaleOS Complete Productivity System")
        print("=" * 40)
        print("\nCommands:")
        print("  --morning     Run morning report (WhatsApp + Email)")
        print("  --evening     Run evening report (WhatsApp + Email)")
        print("  --idea 'text' Process WhatsApp idea")
        print("  --status      Show system status")
        print("  --test        Test complete system")
        print("\nCron jobs are already set up for:")
        print("  • Morning: 7:00 AM EST")
        print("  • Evening: 8:00 PM EST")
        print("\nTo configure email:")
        print("  1. Edit email_config.json")
        print("  2. Add your Resend API key or SMTP credentials")


if __name__ == "__main__":
    main()