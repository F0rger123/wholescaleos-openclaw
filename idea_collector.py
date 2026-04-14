#!/usr/bin/env python3
"""
WhatsApp Idea Collector for WholescaleOS
Listens for new ideas via WhatsApp and adds them to the todo list.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any
import os

class IdeaCollector:
    def __init__(self):
        """Initialize idea collector."""
        self.todo_file = "wholescaleos_todo.json"
        self.ideas_log = "wholescaleos_ideas.log"
        self.todo_data = self.load_todo_list()
    
    def load_todo_list(self) -> Dict[str, Any]:
        """Load the todo list."""
        try:
            with open(self.todo_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Todo file {self.todo_file} not found!")
            return {}
    
    def save_todo_list(self):
        """Save the todo list."""
        with open(self.todo_file, 'w') as f:
            json.dump(self.todo_data, f, indent=2)
    
    def log_idea(self, idea: str, source: str = "whatsapp"):
        """Log an idea to the ideas log."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "idea": idea,
            "source": source,
            "added_to_todo": False
        }
        
        # Append to log file
        with open(self.ideas_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_entry
    
    def parse_idea(self, message: str) -> Dict[str, Any]:
        """Parse an idea message and extract details."""
        # Default category
        category = "low_priority"
        priority = "🟢"
        
        # Check for priority indicators
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["urgent", "critical", "broken", "fix now", "high priority", "🔴"]):
            category = "high_priority"
            priority = "🔴"
        elif any(word in message_lower for word in ["next", "soon", "medium", "🟡", "build next"]):
            category = "medium_priority"
            priority = "🟡"
        elif any(word in message_lower for word in ["future", "later", "low", "🟢"]):
            category = "low_priority"
            priority = "🟢"
        
        # Extract clean idea text (remove priority markers)
        clean_idea = message
        clean_idea = re.sub(r'[🔴🟡🟢]', '', clean_idea)  # Remove emoji
        clean_idea = re.sub(r'\b(urgent|critical|high priority|medium|low|future)\b', '', clean_idea, flags=re.IGNORECASE)
        clean_idea = clean_idea.strip()
        
        return {
            "idea": clean_idea,
            "category": category,
            "priority": priority,
            "original_message": message
        }
    
    def add_idea_to_todo(self, idea_details: Dict[str, Any]) -> bool:
        """Add an idea to the todo list."""
        idea = idea_details["idea"]
        category = idea_details["category"]
        
        # Check if idea already exists
        all_items = []
        for cat in ["high_priority", "medium_priority", "low_priority"]:
            all_items.extend(self.todo_data.get("categories", {}).get(cat, []))
        
        all_items.extend(self.todo_data.get("completed", []))
        
        # Simple duplicate check
        for existing_item in all_items:
            if idea.lower() in existing_item.lower() or existing_item.lower() in idea.lower():
                print(f"Idea already exists: {existing_item[:50]}...")
                return False
        
        # Add to appropriate category
        if category not in self.todo_data.get("categories", {}):
            self.todo_data["categories"][category] = []
        
        self.todo_data["categories"][category].append(idea)
        self.todo_data["last_updated"] = datetime.now().isoformat()
        
        self.save_todo_list()
        return True
    
    def process_whatsapp_message(self, message: str) -> Dict[str, Any]:
        """Process a WhatsApp message as a potential idea."""
        # Check if this looks like an idea (not just conversation)
        is_idea = False
        
        # Heuristics for idea detection
        idea_indicators = [
            "we should", "what about", "add feature", "build a", "create a",
            "implement", "feature idea", "new idea", "todo:", "to do:",
            "can we", "could we", "would be cool", "suggestion"
        ]
        
        message_lower = message.lower()
        if any(indicator in message_lower for indicator in idea_indicators):
            is_idea = True
        elif len(message.split()) >= 3 and len(message) > 20:
            # Longer messages might be ideas
            is_idea = True
        
        if not is_idea:
            return {
                "processed": False,
                "reason": "Doesn't appear to be an idea",
                "message": message[:50] + "..."
            }
        
        # Parse and add the idea
        idea_details = self.parse_idea(message)
        log_entry = self.log_idea(message)
        
        added = self.add_idea_to_todo(idea_details)
        
        if added:
            log_entry["added_to_todo"] = True
            # Update log
            with open(self.ideas_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        return {
            "processed": True,
            "added": added,
            "category": idea_details["category"],
            "priority": idea_details["priority"],
            "idea": idea_details["idea"],
            "timestamp": log_entry["timestamp"]
        }
    
    def get_recent_ideas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent ideas from the log."""
        ideas = []
        try:
            with open(self.ideas_log, 'r') as f:
                lines = f.readlines()[-limit:]  # Get last N lines
                for line in lines:
                    try:
                        ideas.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return ideas
    
    def show_stats(self):
        """Show statistics about ideas and todos."""
        print("📊 WholescaleOS Idea & Todo Statistics")
        print("=" * 50)
        
        # Todo stats
        high = len(self.todo_data.get("categories", {}).get("high_priority", []))
        medium = len(self.todo_data.get("categories", {}).get("medium_priority", []))
        low = len(self.todo_data.get("categories", {}).get("low_priority", []))
        completed = len(self.todo_data.get("completed", []))
        
        print(f"🔴 High Priority: {high} items")
        print(f"🟡 Medium Priority: {medium} items")
        print(f"🟢 Low Priority: {low} items")
        print(f"✅ Completed: {completed} items")
        print(f"📈 Total: {high + medium + low + completed} items")
        print()
        
        # Idea stats
        recent_ideas = self.get_recent_ideas(5)
        print(f"💡 Recent Ideas (last 5):")
        for i, idea in enumerate(recent_ideas, 1):
            status = "✅ Added" if idea.get("added_to_todo") else "📝 Logged"
            print(f"  {i}. {idea.get('idea', '')[:60]}...")
            print(f"     {status} | {idea.get('timestamp', '')[:19]}")
        
        return {
            "todo_stats": {
                "high": high, "medium": medium, "low": low, "completed": completed
            },
            "recent_ideas": recent_ideas
        }


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WholescaleOS Idea Collector")
    parser.add_argument("--add", help="Add an idea directly")
    parser.add_argument("--priority", choices=["high", "medium", "low"], default="low",
                       help="Priority for the idea")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--recent", type=int, help="Show recent ideas (number)")
    parser.add_argument("--test", action="store_true", help="Test with sample ideas")
    
    args = parser.parse_args()
    
    collector = IdeaCollector()
    
    if args.add:
        # Add idea directly
        category_map = {
            "high": "high_priority",
            "medium": "medium_priority", 
            "low": "low_priority"
        }
        
        idea_details = {
            "idea": args.add,
            "category": category_map[args.priority],
            "priority": {"high": "🔴", "medium": "🟡", "low": "🟢"}[args.priority]
        }
        
        added = collector.add_idea_to_todo(idea_details)
        if added:
            print(f"✅ Idea added to {args.priority} priority:")
            print(f"   {args.add}")
        else:
            print("❌ Idea might already exist or couldn't be added")
    
    elif args.stats:
        collector.show_stats()
    
    elif args.recent:
        ideas = collector.get_recent_ideas(args.recent)
        print(f"💡 Recent Ideas (last {args.recent}):")
        for i, idea in enumerate(ideas, 1):
            status = "✅" if idea.get("added_to_todo") else "📝"
            print(f"{i}. {status} {idea.get('idea', '')[:70]}...")
    
    elif args.test:
        print("🧪 Testing Idea Collector...")
        print("=" * 50)
        
        test_messages = [
            "We should add a dark mode toggle to the settings",
            "URGENT: Fix the login page loading spinner",
            "What about adding AI-powered code suggestions?",
            "Medium priority: Create user onboarding tutorial",
            "Just saying hello! 👋"
        ]
        
        for msg in test_messages:
            print(f"\nMessage: {msg}")
            result = collector.process_whatsapp_message(msg)
            if result["processed"]:
                print(f"  ✅ Processed as idea")
                if result["added"]:
                    print(f"  📝 Added to {result['category']}")
            else:
                print(f"  ❌ Not processed: {result['reason']}")
        
        print("\n" + "=" * 50)
        collector.show_stats()
    
    else:
        # Show help
        print("WholescaleOS Idea Collector")
        print("Usage:")
        print("  --add 'Your idea here' --priority high|medium|low")
        print("  --stats (show statistics)")
        print("  --recent N (show recent ideas)")
        print("  --test (test with sample ideas)")


if __name__ == "__main__":
    main()