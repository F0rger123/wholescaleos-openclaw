#!/usr/bin/env python3
"""
Test script to demonstrate the WholescaleOS productivity monitoring system.
"""

import json
from datetime import datetime, timedelta

def test_todo_manager():
    """Test the todo manager with WholescaleOS data."""
    print("🧠 Testing WholescaleOS Todo Manager")
    print("=" * 50)
    
    # Load the todo list
    with open('data/todo_list.json', 'r') as f:
        todo_data = json.load(f)
    
    # Show statistics
    high_priority = len(todo_data['categories']['high_priority'])
    medium_priority = len(todo_data['categories']['medium_priority'])
    low_priority = len(todo_data['categories']['low_priority'])
    completed = len(todo_data['completed'])
    
    print(f"📊 Todo Statistics:")
    print(f"  🔴 High Priority: {high_priority} items")
    print(f"  🟡 Medium Priority: {medium_priority} items")
    print(f"  🟢 Low Priority: {low_priority} items")
    print(f"  ✅ Completed: {completed} items")
    print(f"  📈 Total: {high_priority + medium_priority + low_priority + completed} items")
    
    # Show sample high priority items
    print(f"\n🔴 Sample High Priority Items:")
    for i, item in enumerate(todo_data['categories']['high_priority'][:3], 1):
        print(f"  {i}. {item[:80]}...")
    
    return todo_data

def simulate_commits():
    """Simulate GitHub commits for testing."""
    print(f"\n📝 Simulating GitHub Commits")
    print("=" * 50)
    
    # Simulate some commits that would match todo items
    simulated_commits = [
        {
            'message': 'Fixed OS Bot badge to show 🤖 OS Bot instead of Google Gemini',
            'files_changed': ['src/components/OSBotBadge.js', 'src/styles/badge.css'],
            'date': (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            'message': 'Implemented basic PDF import functionality',
            'files_changed': ['src/utils/pdfParser.js', 'tests/pdfImport.test.js'],
            'date': (datetime.now() - timedelta(hours=4)).isoformat()
        },
        {
            'message': 'Added undo/redo buttons with proper functionality',
            'files_changed': ['src/components/Toolbar.js', 'src/hooks/useUndoRedo.js'],
            'date': (datetime.now() - timedelta(hours=6)).isoformat()
        }
    ]
    
    print(f"Simulated {len(simulated_commits)} commits:")
    for commit in simulated_commits:
        print(f"  • {commit['message']}")
        print(f"    Files: {len(commit['files_changed'])} | Time: {commit['date'][11:16]}")
    
    return simulated_commits

def analyze_todo_completion(commits, todo_data):
    """Analyze which todo items would be completed based on commits."""
    print(f"\n✅ Analyzing Todo Completion")
    print("=" * 50)
    
    # Simple keyword matching (same logic as in report_generator.py)
    commit_messages = ' '.join([c['message'].lower() for c in commits])
    
    completed_items = []
    
    # Check high priority items
    for item in todo_data['categories']['high_priority']:
        item_lower = item.lower()
        # Check if any significant words from todo item appear in commit messages
        keywords = [word for word in item_lower.split() if len(word) > 4]
        if any(keyword in commit_messages for keyword in keywords[:3]):
            completed_items.append(item)
    
    print(f"Based on commits, these items would be marked as completed:")
    for item in completed_items[:5]:  # Show first 5
        print(f"  ✓ {item[:60]}...")
    
    if completed_items:
        completion_rate = len(completed_items) / len(todo_data['categories']['high_priority']) * 100
        print(f"\n📈 Completion rate for high priority: {completion_rate:.1f}%")
    else:
        print("No todo items matched the commits.")
    
    return completed_items

def generate_sample_report():
    """Generate a sample report output."""
    print(f"\n📧 Sample Morning Report Preview")
    print("=" * 50)
    
    print("""
🌅 MORNING PRODUCTIVITY REPORT - 2024-01-15
==========================================

YESTERDAY'S ACCOMPLISHMENTS:
• Fixed OS Bot badge to show 🤖 OS Bot instead of Google Gemini
  Files: 2 | Time: 08:45
• Implemented basic PDF import functionality
  Files: 2 | Time: 10:30
• Added undo/redo buttons with proper functionality
  Files: 2 | Time: 14:20

Summary: Made significant progress on UI components and file import functionality.
Fixed critical badge display issue and implemented core undo/redo system.

TODO PROGRESS:
Completed: 3 items
Remaining: 15 items

TODAY'S RECOMMENDED FOCUS:
1. Incoming SMS: Texts to OS Bot number don't arrive (outgoing works)
2. Team Chat Persistence: Messages don't save after reload/navigation
3. 2FA: Not actually working
""")

def main():
    """Run all tests."""
    print("🚀 WholescaleOS Productivity Monitor - System Test")
    print("=" * 60)
    
    # Test 1: Todo Manager
    todo_data = test_todo_manager()
    
    # Test 2: Simulate commits
    commits = simulate_commits()
    
    # Test 3: Analyze completion
    completed = analyze_todo_completion(commits, todo_data)
    
    # Test 4: Show sample report
    generate_sample_report()
    
    print(f"\n✅ System test completed successfully!")
    print(f"\n📋 Next steps:")
    print(f"1. Get your free API keys (GitHub, Gemini, Resend)")
    print(f"2. Follow the deployment guide in DEPLOYMENT.md")
    print(f"3. Your reports will be sent to: drummerforger@gmail.com")
    print(f"4. Schedule: 7:00 AM & 8:00 PM EST daily")

if __name__ == "__main__":
    main()