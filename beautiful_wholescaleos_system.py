#!/usr/bin/env python3
"""
Beautiful WholescaleOS Productivity System
Uses Twin.so style reports for maximum visual appeal.
"""

import json
import subprocess
import sys
from datetime import datetime
import os

class BeautifulWholescaleOSSystem:
    def __init__(self):
        self.workspace = "/home/drummer/.openclaw/workspace"
        
    def run_complete_system(self, report_type="morning"):
        """Run complete system with beautiful reports."""
        print("🎨 BEAUTIFUL WHOLESCALEOS PRODUCTIVITY SYSTEM")
        print("=" * 60)
        
        if report_type == "morning":
            # Morning: Sync + Update + Report
            print("\n1. 🔄 Syncing with Google Doc...")
            self.run_script("auto_sync_google_doc.py")
            
            print("\n2. ✅ Updating completed items...")
            self.run_script("update_completed.py")
            
            print("\n3. 🌅 Generating beautiful morning report...")
            report = self.generate_morning_report()
            
        else:  # evening
            print("\n1. 🌙 Generating beautiful evening report...")
            report = self.generate_evening_report()
        
        # Send via email
        print("\n4. 📧 Sending email report...")
        self.send_email_report(report, report_type)
        
        # Show final status
        print("\n5. 📊 Final System Status")
        print("=" * 60)
        self.show_status()
        
        return report
    
    def run_script(self, script_name):
        """Run a Python script."""
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(self.workspace, script_name)],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            print(result.stdout[:500])  # Show first 500 chars
            if result.stderr:
                print(f"⚠️  Warnings: {result.stderr[:200]}")
            return True
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return False
    
    def generate_morning_report(self):
        """Generate beautiful morning report."""
        try:
            result = subprocess.run(
                [sys.executable, "twin_style_morning_report.py"],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            return result.stdout
        except:
            # Fallback to simple report
            return "🧠 WholescaleOS Morning Report\n[Report generation failed - using fallback]"
    
    def generate_evening_report(self):
        """Generate beautiful evening report."""
        try:
            result = subprocess.run(
                [sys.executable, "twin_style_evening_report.py"],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            return result.stdout
        except:
            # Fallback to simple report
            return "🌙 WholescaleOS Evening Report\n[Report generation failed - using fallback]"
    
    def send_email_report(self, report, report_type):
        """Send report via email."""
        try:
            # Save report to file
            report_file = f"{report_type}_report.txt"
            with open(os.path.join(self.workspace, report_file), 'w') as f:
                f.write(report)
            
            # Use gmail_reporter to send
            result = subprocess.run(
                [sys.executable, "gmail_reporter.py", f"--{report_type}", "--text", report_file],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            
            if "successful" in result.stdout.lower():
                print("✅ Email sent successfully!")
            else:
                print(f"⚠️  Email issues: {result.stdout[:200]}")
                
        except Exception as e:
            print(f"⚠️  Email error: {e}")
    
    def show_status(self):
        """Show system status."""
        try:
            with open(os.path.join(self.workspace, "wholescaleos_todo.json"), 'r') as f:
                todo_data = json.load(f)
            
            high = len(todo_data["categories"]["high_priority"])
            medium = len(todo_data["categories"]["medium_priority"])
            low = len(todo_data["categories"]["low_priority"])
            completed = len(todo_data["completed"])
            
            print("✅ Todo Statistics:")
            print(f"   🔴 High Priority: {high} items")
            print(f"   🟡 Medium Priority: {medium} items")
            print(f"   🟢 Low Priority: {low} items")
            print(f"   ✅ Completed: {completed} items")
            print(f"   📈 Total: {high + medium + low + completed} items")
            
            if "last_sync" in todo_data:
                print(f"\n🔄 Last Google Doc sync: {todo_data['last_sync']}")
            
            print(f"\n🎨 Report Style: Twin.so beautiful format")
            print(f"📧 Email: Configured for drummerforger@gmail.com")
            print(f"\n🔄 Next automated run:")
            print(f"   • 7:00 AM EST: Beautiful morning report")
            print(f"   • 8:00 PM EST: Beautiful evening report")
            
        except Exception as e:
            print(f"⚠️  Status error: {e}")
    
    def test_system(self):
        """Test the complete beautiful system."""
        print("🧪 TESTING BEAUTIFUL WHOLESCALEOS SYSTEM")
        print("=" * 60)
        
        tests = [
            ("Google Doc sync", "auto_sync_google_doc.py"),
            ("Todo completion update", "update_completed.py"),
            ("Morning report generation", "twin_style_morning_report.py"),
            ("Evening report generation", "twin_style_evening_report.py"),
            ("Email sending", "gmail_reporter.py --test")
        ]
        
        for test_name, command in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                if "--test" in command:
                    cmd_parts = command.split()
                    result = subprocess.run(
                        [sys.executable, cmd_parts[0], cmd_parts[1]],
                        capture_output=True,
                        text=True,
                        cwd=self.workspace
                    )
                else:
                    result = subprocess.run(
                        [sys.executable, command],
                        capture_output=True,
                        text=True,
                        cwd=self.workspace
                    )
                
                if result.returncode == 0:
                    print(f"✅ {test_name} passed")
                else:
                    print(f"⚠️  {test_name} issues: {result.stderr[:100]}")
            except Exception as e:
                print(f"❌ {test_name} failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Beautiful system test complete!")
        print("\n💡 The system will now send reports in the beautiful Twin.so format!")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Beautiful WholescaleOS Productivity System")
    parser.add_argument("--morning", action="store_true", help="Run morning system (sync + report)")
    parser.add_argument("--evening", action="store_true", help="Run evening system (report only)")
    parser.add_argument("--test", action="store_true", help="Test beautiful system")
    parser.add_argument("--status", action="store_true", help="Show system status")
    
    args = parser.parse_args()
    
    system = BeautifulWholescaleOSSystem()
    
    if args.morning:
        system.run_complete_system("morning")
    elif args.evening:
        system.run_complete_system("evening")
    elif args.test:
        system.test_system()
    elif args.status:
        system.show_status()
    else:
        print("🎨 Beautiful WholescaleOS Productivity System")
        print("=" * 40)
        print("\nCommands:")
        print("  --morning    Run morning system (sync + beautiful report)")
        print("  --evening    Run evening system (beautiful report)")
        print("  --test       Test beautiful system")
        print("  --status     Show system status")
        print("\nFeatures:")
        print("  • Twin.so style beautiful reports")
        print("  • Google Doc auto-sync")
        print("  • Gmail email delivery")
        print("  • WhatsApp idea collection")
        print("\nSchedule:")
        print("  • 7:00 AM EST: Morning report (sync + update)")
        print("  • 8:00 PM EST: Evening report")


if __name__ == "__main__":
    main()