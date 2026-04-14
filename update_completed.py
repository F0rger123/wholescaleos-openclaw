#!/usr/bin/env python3
"""
Update completed items based on Google Doc notes.
"""

import json

# Load todo list
with open('wholescaleos_todo.json', 'r') as f:
    todo_data = json.load(f)

# Item 4 from Google Doc has [Updated Apr 13: Massive OS Bot overhaul...]
# This suggests it's completed or significantly progressed
item_to_complete = "OS Bot Intelligence: Poor intent recognition: \"what's up\", \"what's the weather\", \"what are my preferences\" fail"

print("🔄 Updating completed items based on Google Doc notes...")

# Check if item is in high priority
if item_to_complete in todo_data["categories"]["high_priority"]:
    todo_data["categories"]["high_priority"].remove(item_to_complete)
    if item_to_complete not in todo_data["completed"]:
        todo_data["completed"].append(item_to_complete)
    print(f"✅ Marked as completed: {item_to_complete[:60]}...")
else:
    print(f"ℹ️ Item not found in high priority: {item_to_complete[:60]}...")

# Also check for any other items that might be completed
# Based on the commits we saw earlier, some items might be done
potential_completed = [
    "OS Bot Intelligence: Poor intent recognition for 'what's up', 'what's the weather', 'what are my preferences'",
    "fix: resolve v9.2 lint error & finalize logic",
    "feat: OS Bot v9.2 urgent intent & logic fixes",
    "feat: OS Bot v9.1 critical logic & analysis fixes",
    "feat: OS Bot v9.0 Professional Edition",
    "feat: implement local-ai service layer"
]

print("\n🔍 Checking for other potentially completed items...")
for item in potential_completed:
    # Check in all categories
    for category in ["high_priority", "medium_priority", "low_priority"]:
        if item in todo_data["categories"][category]:
            todo_data["categories"][category].remove(item)
            if item not in todo_data["completed"]:
                todo_data["completed"].append(item)
            print(f"✅ Marked as completed: {item[:60]}...")
            break

# Save updated todo list
with open('wholescaleos_todo.json', 'w') as f:
    json.dump(todo_data, f, indent=2)

# Show updated stats
print("\n📈 Updated Todo Statistics:")
high = len(todo_data["categories"]["high_priority"])
medium = len(todo_data["categories"]["medium_priority"])
low = len(todo_data["categories"]["low_priority"])
completed = len(todo_data["completed"])

print(f"  🔴 High Priority: {high} items")
print(f"  🟡 Medium Priority: {medium} items")
print(f"  🟢 Low Priority: {low} items")
print(f"  ✅ Completed: {completed} items")
print(f"  📈 Total: {high + medium + low + completed} items")