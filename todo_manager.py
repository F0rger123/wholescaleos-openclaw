#!/usr/bin/env python3
"""
Todo List Manager for GitHub Productivity Monitor
Manages the todo list JSON file and provides utilities for updating and querying.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class TodoManager:
    def __init__(self, todo_file: str = "data/todo_list.json"):
        self.todo_file = todo_file
        self.todo_data = self.load_todo_list()
    
    def load_todo_list(self) -> Dict[str, Any]:
        """Load todo list from JSON file."""
        if not os.path.exists(self.todo_file):
            return self.create_default_todo_list()
        
        try:
            with open(self.todo_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading todo list: {e}")
            return self.create_default_todo_list()
    
    def create_default_todo_list(self) -> Dict[str, Any]:
        """Create a default todo list structure."""
        return {
            "categories": {
                "high_priority": [],
                "medium_priority": [],
                "low_priority": []
            },
            "completed": [],
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def save_todo_list(self):
        """Save todo list to JSON file."""
        self.todo_data["last_updated"] = datetime.now().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.todo_file), exist_ok=True)
        
        with open(self.todo_file, 'w') as f:
            json.dump(self.todo_data, f, indent=2)
    
    def add_todo_item(self, item: str, category: str = "medium_priority"):
        """Add a new todo item to the specified category."""
        if category not in self.todo_data["categories"]:
            print(f"Invalid category: {category}. Using 'medium_priority'.")
            category = "medium_priority"
        
        if item not in self.todo_data["categories"][category]:
            self.todo_data["categories"][category].append(item)
            self.save_todo_list()
            print(f"Added '{item}' to {category}")
        else:
            print(f"Item '{item}' already exists in {category}")
    
    def mark_completed(self, item: str):
        """Mark a todo item as completed."""
        found = False
        
        # Remove from all categories
        for category in self.todo_data["categories"]:
            if item in self.todo_data["categories"][category]:
                self.todo_data["categories"][category].remove(item)
                found = True
        
        # Add to completed list if found
        if found and item not in self.todo_data["completed"]:
            self.todo_data["completed"].append(item)
            self.save_todo_list()
            print(f"Marked '{item}' as completed")
        elif not found:
            print(f"Item '{item}' not found in todo list")
    
    def get_all_todos(self) -> List[str]:
        """Get all todo items from all categories."""
        all_todos = []
        for category in self.todo_data["categories"].values():
            all_todos.extend(category)
        return all_todos
    
    def get_todos_by_category(self, category: str) -> List[str]:
        """Get todo items from a specific category."""
        return self.todo_data["categories"].get(category, [])
    
    def get_completed_todos(self) -> List[str]:
        """Get all completed todo items."""
        return self.todo_data.get("completed", [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the todo list."""
        total_todos = len(self.get_all_todos())
        completed_todos = len(self.get_completed_todos())
        
        return {
            "total_todos": total_todos,
            "completed_todos": completed_todos,
            "pending_todos": total_todos - completed_todos,
            "completion_rate": (completed_todos / total_todos * 100) if total_todos > 0 else 0,
            "by_category": {
                category: len(items)
                for category, items in self.todo_data["categories"].items()
            }
        }
    
    def import_from_text(self, text: str):
        """
        Import todo items from plain text.
        Expected format:
        ## Category
        - [ ] Item 1
        - [ ] Item 2
        - [x] Item 3 (completed)
        """
        current_category = "medium_priority"
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Detect category headers
            if line.startswith('##'):
                category_name = line[2:].strip().lower()
                if 'high' in category_name or 'priority' in category_name:
                    current_category = "high_priority"
                elif 'medium' in category_name:
                    current_category = "medium_priority"
                elif 'low' in category_name:
                    current_category = "low_priority"
                elif 'complete' in category_name:
                    current_category = "completed"
            
            # Detect todo items
            elif line.startswith('- ['):
                # Extract item text
                item_text = line[line.find(']') + 1:].strip()
                
                # Check if completed
                if '[x]' in line or '[X]' in line:
                    self.mark_completed(item_text)
                else:
                    self.add_todo_item(item_text, current_category)
    
    def export_to_text(self) -> str:
        """Export todo list to plain text format."""
        output = []
        
        # High priority
        if self.todo_data["categories"]["high_priority"]:
            output.append("## High Priority")
            for item in self.todo_data["categories"]["high_priority"]:
                output.append(f"- [ ] {item}")
            output.append("")
        
        # Medium priority
        if self.todo_data["categories"]["medium_priority"]:
            output.append("## Medium Priority")
            for item in self.todo_data["categories"]["medium_priority"]:
                output.append(f"- [ ] {item}")
            output.append("")
        
        # Low priority
        if self.todo_data["categories"]["low_priority"]:
            output.append("## Low Priority")
            for item in self.todo_data["categories"]["low_priority"]:
                output.append(f"- [ ] {item}")
            output.append("")
        
        # Completed
        if self.todo_data["completed"]:
            output.append("## Completed")
            for item in self.todo_data["completed"]:
                output.append(f"- [x] {item}")
        
        return '\n'.join(output)


def main():
    """Command-line interface for todo manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage todo list for productivity reports")
    parser.add_argument("--import", dest="import_file", help="Import todo items from text file")
    parser.add_argument("--export", action="store_true", help="Export todo list to text format")
    parser.add_argument("--add", help="Add a new todo item")
    parser.add_argument("--category", choices=["high", "medium", "low"], default="medium",
                       help="Category for new item (default: medium)")
    parser.add_argument("--complete", help="Mark a todo item as completed")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    manager = TodoManager()
    
    if args.import_file:
        with open(args.import_file, 'r') as f:
            manager.import_from_text(f.read())
        print(f"Imported todo items from {args.import_file}")
    
    if args.add:
        category_map = {
            "high": "high_priority",
            "medium": "medium_priority",
            "low": "low_priority"
        }
        manager.add_todo_item(args.add, category_map[args.category])
    
    if args.complete:
        manager.mark_completed(args.complete)
    
    if args.export:
        print(manager.export_to_text())
    
    if args.stats:
        stats = manager.get_statistics()
        print(f"Total todos: {stats['total_todos']}")
        print(f"Completed: {stats['completed_todos']}")
        print(f"Pending: {stats['pending_todos']}")
        print(f"Completion rate: {stats['completion_rate']:.1f}%")
        print("\nBy category:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")


if __name__ == "__main__":
    main()