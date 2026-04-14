#!/usr/bin/env python3
"""
Sync Google Doc with WholescaleOS Todo List
Reads from Google Doc export and updates local todo list.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any
import requests

class GoogleDocSync:
    def __init__(self):
        self.doc_url = "https://docs.google.com/document/d/1cZVIQ9UMljFoyn2S7GDec4ztwDLvCSXUDKg8XhscR3Y/export?format=txt"
        self.todo_file = "wholescaleos_todo.json"
        self.todo_data = self.load_todo_list()
    
    def load_todo_list(self) -> Dict[str, Any]:
        """Load current todo list."""
        try:
            with open(self.todo_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "categories": {
                    "high_priority": [],
                    "medium_priority": [],
                    "low_priority": []
                },
                "completed": [],
                "last_sync": None,
                "source": "google_doc"
            }
    
    def save_todo_list(self):
        """Save todo list."""
        self.todo_data["last_sync"] = datetime.now().isoformat()
        with open(self.todo_file, 'w') as f:
            json.dump(self.todo_data, f, indent=2)
    
    def fetch_google_doc(self) -> str:
        """Fetch content from Google Doc."""
        try:
            response = requests.get(self.doc_url)
            response.raise_for_status()
            
            # Extract content between the markers
            content = response.text
            # Find the actual content (after security notice)
            if "<<<EXTERNAL_UNTRUSTED_CONTENT" in content:
                # Extract between markers
                start = content.find("<<<EXTERNAL_UNTRUSTED_CONTENT")
                end = content.find("<<<END_EXTERNAL_UNTRUSTED_CONTENT")
                if start != -1 and end != -1:
                    # Find the actual content after the marker
                    content_start = content.find("---\n", start) + 4
                    content = content[content_start:end].strip()
            
            return content
        except Exception as e:
            print(f"Error fetching Google Doc: {e}")
            return ""
    
    def parse_google_doc(self, content: str) -> Dict[str, List[str]]:
        """Parse Google Doc content into categorized todo items."""
        categories = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "new_ideas": []
        }
        
        current_category = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip empty lines
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
            
            # Parse todo items (lines with numbers like "4.", "30.", etc.)
            match = re.match(r'^(\d+\.|🔄\s*\d+\.)\s*(.+)$', line)
            if match and current_category:
                item_text = match.group(2).strip()
                
                # Clean up the item text
                # Remove update notes in brackets
                item_text = re.sub(r'\[Updated.*?\]', '', item_text)
                item_text = item_text.strip()
                
                if item_text and item_text not in categories[current_category]:
                    categories[current_category].append(item_text)
            
            # Also catch items without numbers but with emoji indicators
            elif current_category and len(line) > 10 and not line.startswith("Currently"):
                # Check if it looks like a todo item
                if any(indicator in line for indicator in [". ", ": ", " - "]):
                    if line not in categories[current_category]:
                        categories[current_category].append(line)
        
        return categories
    
    def sync_with_local(self, google_categories: Dict[str, List[str]]):
        """Sync Google Doc categories with local todo list."""
        print("🔄 Syncing Google Doc with local todo list...")
        
        # Track changes
        changes = {
            "added": 0,
            "removed": 0,
            "updated": 0
        }
        
        # Sync each category
        for category, google_items in google_categories.items():
            if category == "new_ideas":
                # New ideas go to low priority by default
                target_category = "low_priority"
            else:
                target_category = category
            
            local_items = self.todo_data["categories"].get(target_category, [])
            
            # Convert to sets for comparison
            google_set = set(google_items)
            local_set = set(local_items)
            
            # Find items to add (in Google but not local)
            to_add = google_set - local_set
            # Find items to remove (in local but not Google)
            to_remove = local_set - google_set
            
            # Update local list
            if to_add:
                for item in to_add:
                    if item not in local_items:
                        local_items.append(item)
                        changes["added"] += 1
                        print(f"  ➕ Added to {target_category}: {item[:60]}...")
            
            if to_remove:
                # Only remove if not marked as completed
                for item in to_remove:
                    if item in local_items and item not in self.todo_data["completed"]:
                        local_items.remove(item)
                        changes["removed"] += 1
                        print(f"  ➖ Removed from {target_category}: {item[:60]}...")
            
            # Update the category
            self.todo_data["categories"][target_category] = local_items
        
        # Check for items that might be completed
        print("\n🔍 Checking for completed items...")
        
        # Look for update notes in the Google Doc that might indicate completion
        content = self.fetch_google_doc()
        for line in content.split('\n'):
            if "[Updated" in line and "commits" in line.lower():
                # Extract the item number
                match = re.search(r'(\d+)\.', line)
                if match:
                    item_num = match.group(1)
                    # Find the corresponding item
                    for category in ["high_priority", "medium_priority", "low_priority"]:
                        for item in self.todo_data["categories"].get(category, []):
                            if item.startswith(f"{item_num}.") or f"{item_num}. " in item:
                                # Check if it's not already completed
                                if item not in self.todo_data["completed"]:
                                    self.todo_data["completed"].append(item)
                                    # Remove from active category
                                    self.todo_data["categories"][category].remove(item)
                                    changes["updated"] += 1
                                    print(f"  ✅ Marked as completed: {item[:60]}...")
                                break
        
        self.save_todo_list()
        
        print(f"\n📊 Sync Summary:")
        print(f"  ➕ Added: {changes['added']} items")
        print(f"  ➖ Removed: {changes['removed']} items")
        print(f"  ✅ Marked completed: {changes['updated']} items")
        
        return changes
    
    def show_comparison(self, google_categories: Dict[str, List[str]]):
        """Show comparison between Google Doc and local list."""
        print("📊 Comparison: Google Doc vs Local Todo List")
        print("=" * 60)
        
        for category in ["high_priority", "medium_priority", "low_priority"]:
            google_items = google_categories.get(category, [])
            local_items = self.todo_data["categories"].get(category, [])
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  Google Doc: {len(google_items)} items")
            print(f"  Local: {len(local_items)} items")
            
            # Show differences
            google_set = set(google_items)
            local_set = set(local_items)
            
            missing_in_local = google_set - local_set
            extra_in_local = local_set - google_set
            
            if missing_in_local:
                print(f"  ⚠️  Missing in local ({len(missing_in_local)}):")
                for item in list(missing_in_local)[:3]:
                    print(f"    • {item[:50]}...")
                if len(missing_in_local) > 3:
                    print(f"    ... and {len(missing_in_local) - 3} more")
            
            if extra_in_local:
                print(f"  ⚠️  Extra in local ({len(extra_in_local)}):")
                for item in list(extra_in_local)[:3]:
                    print(f"    • {item[:50]}...")
                if len(extra_in_local) > 3:
                    print(f"    ... and {len(extra_in_local) - 3} more")
        
        print(f"\n✅ Completed items: {len(self.todo_data.get('completed', []))}")
        print(f"📅 Last sync: {self.todo_data.get('last_sync', 'Never')}")
    
    def run_sync(self):
        """Run complete sync process."""
        print("🔄 Syncing with Google Doc...")
        print(f"📄 Google Doc: {self.doc_url}")
        
        # Fetch Google Doc
        content = self.fetch_google_doc()
        if not content:
            print("❌ Failed to fetch Google Doc")
            return
        
        print(f"📝 Fetched {len(content)} characters from Google Doc")
        
        # Parse content
        google_categories = self.parse_google_doc(content)
        
        print("\n📊 Google Doc Categories:")
        for category, items in google_categories.items():
            print(f"  {category}: {len(items)} items")
        
        # Show comparison
        self.show_comparison(google_categories)
        
        # Ask for confirmation
        print("\n" + "=" * 60)
        response = input("Sync with local todo list? (y/n): ").strip().lower()
        
        if response == 'y':
            changes = self.sync_with_local(google_categories)
            
            if any(changes.values()):
                print(f"\n✅ Sync completed with {sum(changes.values())} changes")
            else:
                print("\n✅ Already in sync - no changes needed")
        else:
            print("\n⏸️  Sync cancelled")
        
        # Show final stats
        print("\n" + "=" * 60)
        print("📈 Final Todo Statistics:")
        high = len(self.todo_data["categories"].get("high_priority", []))
        medium = len(self.todo_data["categories"].get("medium_priority", []))
        low = len(self.todo_data["categories"].get("low_priority", []))
        completed = len(self.todo_data.get("completed", []))
        
        print(f"  🔴 High Priority: {high} items")
        print(f"  🟡 Medium Priority: {medium} items")
        print(f"  🟢 Low Priority: {low} items")
        print(f"  ✅ Completed: {completed} items")
        print(f"  📈 Total: {high + medium + low + completed} items")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Google Doc with WholescaleOS Todo List")
    parser.add_argument("--sync", action="store_true", help="Run sync with Google Doc")
    parser.add_argument("--compare", action="store_true", help="Show comparison only")
    parser.add_argument("--stats", action="store_true", help="Show current stats")
    parser.add_argument("--fetch", action="store_true", help="Fetch and show Google Doc content")
    
    args = parser.parse_args()
    
    sync = GoogleDocSync()
    
    if args.sync:
        sync.run_sync()
    elif args.compare:
        content = sync.fetch_google_doc()
        if content:
            google_categories = sync.parse_google_doc(content)
            sync.show_comparison(google_categories)
    elif args.stats:
        high = len(sync.todo_data["categories"].get("high_priority", []))
        medium = len(sync.todo_data["categories"].get("medium_priority", []))
        low = len(sync.todo_data["categories"].get("low_priority", []))
        completed = len(sync.todo_data.get("completed", []))
        
        print("📊 Current Todo Statistics:")
        print(f"  🔴 High Priority: {high} items")
        print(f"  🟡 Medium Priority: {medium} items")
        print(f"  🟢 Low Priority: {low} items")
        print(f"  ✅ Completed: {completed} items")
        print(f"  📈 Total: {high + medium + low + completed} items")
        print(f"  📅 Last sync: {sync.todo_data.get('last_sync', 'Never')}")
    elif args.fetch:
        content = sync.fetch_google_doc()
        if content:
            print("📄 Google Doc Content (first 1000 chars):")
            print("=" * 60)
            print(content[:1000])
            print("..." if len(content) > 1000 else "")
            print("=" * 60)
            print(f"Total length: {len(content)} characters")
    else:
        print("Google Doc Sync for WholescaleOS")
        print("Usage:")
        print("  --sync      Run sync with Google Doc")
        print("  --compare   Show comparison only")
        print("  --stats     Show current stats")
        print("  --fetch     Fetch and show Google Doc content")


if __name__ == "__main__":
    main()