#!/usr/bin/env python3
"""
Auto-sync Google Doc with WholescaleOS Todo List
Automatically syncs without asking for confirmation.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any
import requests

def auto_sync_google_doc():
    """Automatically sync Google Doc with local todo list."""
    print("🔄 Auto-syncing with Google Doc...")
    
    # Configuration
    doc_url = "https://docs.google.com/document/d/1cZVIQ9UMljFoyn2S7GDec4ztwDLvCSXUDKg8XhscR3Y/export?format=txt"
    todo_file = "wholescaleos_todo.json"
    
    # Load current todo list
    try:
        with open(todo_file, 'r') as f:
            todo_data = json.load(f)
    except FileNotFoundError:
        todo_data = {
            "categories": {
                "high_priority": [],
                "medium_priority": [],
                "low_priority": []
            },
            "completed": [],
            "last_sync": None,
            "source": "google_doc"
        }
    
    # Fetch Google Doc
    try:
        response = requests.get(doc_url)
        response.raise_for_status()
        content = response.text
        
        # Extract content between markers
        if "<<<EXTERNAL_UNTRUSTED_CONTENT" in content:
            start = content.find("<<<EXTERNAL_UNTRUSTED_CONTENT")
            end = content.find("<<<END_EXTERNAL_UNTRUSTED_CONTENT")
            if start != -1 and end != -1:
                content_start = content.find("---\n", start) + 4
                content = content[content_start:end].strip()
        
        print(f"✅ Fetched {len(content)} characters from Google Doc")
    except Exception as e:
        print(f"❌ Failed to fetch Google Doc: {e}")
        return
    
    # Parse Google Doc content
    categories = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": [],
        "new_ideas": []
    }
    
    current_category = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        if not line:
            continue
        
        # Detect category headers
        if "🔴 HIGH PRIORITY" in line:
            current_category = "high_priority"
            continue
        elif "🟡 MEDIUM PRIORITY" in line:
            current_category = "medium_priority"
            continue
        elif "🟢 LOW PRIORITY" in line:
            current_category = "low_priority"
            continue
        elif "🆕 NEW IDEAS" in line:
            current_category = "new_ideas"
            continue
        
        # Skip section headers
        if line.startswith("AI &") or line.startswith("CRM &") or line.startswith("UI &") or line.startswith("Team &"):
            continue
        
        # Parse todo items
        match = re.match(r'^(\d+\.|🔄\s*\d+\.)\s*(.+)$', line)
        if match and current_category:
            item_text = match.group(2).strip()
            
            # Clean up the item text
            item_text = re.sub(r'\[Updated.*?\]', '', item_text)
            item_text = item_text.strip()
            
            if item_text and item_text not in categories[current_category]:
                categories[current_category].append(item_text)
        
        # Also catch items without numbers
        elif current_category and len(line) > 10 and not line.startswith("Currently"):
            if any(indicator in line for indicator in [". ", ": ", " - "]):
                if line not in categories[current_category]:
                    categories[current_category].append(line)
    
    print(f"📊 Parsed categories from Google Doc:")
    print(f"  🔴 High Priority: {len(categories['high_priority'])} items")
    print(f"  🟡 Medium Priority: {len(categories['medium_priority'])} items")
    print(f"  🟢 Low Priority: {len(categories['low_priority'])} items")
    print(f"  💡 New Ideas: {len(categories['new_ideas'])} items")
    
    # Sync with local todo list
    changes = {
        "added": 0,
        "removed": 0,
        "completed": 0
    }
    
    # Sync each category
    for category, google_items in categories.items():
        if category == "new_ideas":
            # New ideas go to low priority
            target_category = "low_priority"
            google_items = google_items  # Add all new ideas
        else:
            target_category = category
        
        local_items = todo_data["categories"].get(target_category, [])
        
        # Convert to sets for comparison
        google_set = set(google_items)
        local_set = set(local_items)
        
        # Add items from Google Doc
        for item in google_set - local_set:
            if item not in local_items:
                local_items.append(item)
                changes["added"] += 1
                print(f"  ➕ Added to {target_category}: {item[:50]}...")
        
        # For high and medium priority, remove items not in Google Doc
        if category in ["high_priority", "medium_priority"]:
            for item in local_set - google_set:
                if item in local_items and item not in todo_data["completed"]:
                    local_items.remove(item)
                    changes["removed"] += 1
                    print(f"  ➖ Removed from {target_category}: {item[:50]}...")
        
        # Update the category
        todo_data["categories"][target_category] = local_items
    
    # Check for completed items (items with [Updated] notes)
    print("\n🔍 Checking for completed items...")
    for line in content.split('\n'):
        if "[Updated" in line and "commits" in line.lower():
            match = re.search(r'(\d+)\.', line)
            if match:
                item_num = match.group(1)
                # Find the corresponding item
                for category in ["high_priority", "medium_priority", "low_priority"]:
                    for item in todo_data["categories"].get(category, []):
                        if item.startswith(f"{item_num}.") or f"{item_num}. " in item:
                            if item not in todo_data["completed"]:
                                todo_data["completed"].append(item)
                                todo_data["categories"][category].remove(item)
                                changes["completed"] += 1
                                print(f"  ✅ Marked as completed: {item[:50]}...")
                            break
    
    # Save updated todo list
    todo_data["last_sync"] = datetime.now().isoformat()
    with open(todo_file, 'w') as f:
        json.dump(todo_data, f, indent=2)
    
    print(f"\n📊 Sync Summary:")
    print(f"  ➕ Added: {changes['added']} items")
    print(f"  ➖ Removed: {changes['removed']} items")
    print(f"  ✅ Marked completed: {changes['completed']} items")
    
    # Show final statistics
    print("\n📈 Final Todo Statistics:")
    high = len(todo_data["categories"].get("high_priority", []))
    medium = len(todo_data["categories"].get("medium_priority", []))
    low = len(todo_data["categories"].get("low_priority", []))
    completed = len(todo_data.get("completed", []))
    
    print(f"  🔴 High Priority: {high} items")
    print(f"  🟡 Medium Priority: {medium} items")
    print(f"  🟢 Low Priority: {low} items")
    print(f"  ✅ Completed: {completed} items")
    print(f"  📈 Total: {high + medium + low + completed} items")
    print(f"  📅 Last sync: {todo_data['last_sync']}")
    
    return todo_data


if __name__ == "__main__":
    auto_sync_google_doc()