#!/usr/bin/env python3
"""
Update Google Doc with complete todo list from local JSON.
This pushes all local items to the Google Doc.
"""

import json
from datetime import datetime
import requests

def load_todo_list():
    """Load current todo list from JSON."""
    with open('wholescaleos_todo.json', 'r') as f:
        return json.load(f)

def format_for_google_doc(todo_data):
    """Format todo list for Google Doc."""
    lines = []
    
    # Header
    lines.append("🧠 WHOLE SCALE OS - MASTER FIXES & FEATURES LIST")
    lines.append("")
    
    # High Priority
    lines.append("🔴 HIGH PRIORITY - CURRENTLY BROKEN (Fix NOW)")
    lines.append("")
    for i, item in enumerate(todo_data['categories']['high_priority'], 1):
        lines.append(f"{i}. {item}")
    lines.append("")
    
    # Medium Priority
    lines.append("🟡 MEDIUM PRIORITY - IMPORTANT FEATURES")
    lines.append("")
    for i, item in enumerate(todo_data['categories']['medium_priority'], 1):
        lines.append(f"{i}. {item}")
    lines.append("")
    
    # Low Priority
    lines.append("🟢 LOW PRIORITY - NICE TO HAVE")
    lines.append("")
    for i, item in enumerate(todo_data['categories']['low_priority'], 1):
        lines.append(f"{i}. {item}")
    lines.append("")
    
    # New Ideas Section (from low priority that are actually ideas)
    lines.append("💡 NEW IDEAS & FUTURE FEATURES")
    lines.append("")
    # We'll add some of the more idea-like low priority items here
    idea_keywords = ['marketplace', 'AI', 'integration', 'analytics', 'dashboard']
    ideas = []
    for item in todo_data['categories']['low_priority']:
        if any(keyword.lower() in item.lower() for keyword in idea_keywords):
            ideas.append(item)
    
    for i, item in enumerate(ideas[:20], 1):  # Limit to 20 ideas
        lines.append(f"{i}. {item}")
    
    # Completed
    lines.append("")
    lines.append("✅ COMPLETED")
    lines.append("")
    for i, item in enumerate(todo_data['completed'][-10:], 1):  # Last 10 completed
        lines.append(f"{i}. {item}")
    
    lines.append("")
    lines.append(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"📊 Stats: {len(todo_data['categories']['high_priority'])} high, {len(todo_data['categories']['medium_priority'])} medium, {len(todo_data['categories']['low_priority'])} low priority items")
    
    return "\n".join(lines)

def main():
    print("📋 Loading todo list...")
    todo_data = load_todo_list()
    
    print("📝 Formatting for Google Doc...")
    content = format_for_google_doc(todo_data)
    
    print(f"📄 Generated {len(content)} characters")
    print("\n=== PREVIEW ===")
    print(content[:500])
    print("...")
    print(content[-500:])
    print("=== END PREVIEW ===")
    
    print("\n⚠️  NOTE: To actually update the Google Doc, we need:")
    print("1. Google Docs API credentials")
    print("2. Document ID with edit permissions")
    print("3. API call to update the document")
    
    print("\n📋 Current Google Doc ID: 1cZVIQ9UMljFoyn2S7GDec4ztwDLvCSXUDKg8XhscR3Y")
    print("🔗 Link: https://docs.google.com/document/d/1cZVIQ9UMljFoyn2S7GDec4ztwDLvCSXUDKg8XhscR3Y/edit")
    
    # Save formatted version locally
    with open('wholescaleos_todo_formatted.txt', 'w') as f:
        f.write(content)
    
    print(f"\n✅ Saved formatted version to: wholescaleos_todo_formatted.txt")
    print("📊 Summary:")
    print(f"  High priority: {len(todo_data['categories']['high_priority'])} items")
    print(f"  Medium priority: {len(todo_data['categories']['medium_priority'])} items")
    print(f"  Low priority: {len(todo_data['categories']['low_priority'])} items")
    print(f"  Completed: {len(todo_data['completed'])} items")

if __name__ == "__main__":
    main()