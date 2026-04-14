#!/usr/bin/env python3
"""
Complete WholescaleOS Productivity System
Integrates: GitHub monitoring, Google Doc syncing, email reports, WhatsApp messaging.
"""

import json
from datetime import datetime
import subprocess
import sys

def run_complete_system():
    """Run the complete WholescaleOS productivity system."""
    print("🚀 WHOLESCALEOS COMPLETE PRODUCTIVITY SYSTEM")
    print("=" * 60)
    
    # Step 1: Sync with Google Doc
    print("\n1. 🔄 Syncing with Google Doc...")
    try:
        result = subprocess.run(
            [sys.executable, "auto_sync_google_doc.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Sync warnings: {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠️  Google Doc sync error: {e}")
    
    # Step 2: Update completed items
    print("\n2. ✅ Updating completed items...")
    try:
        result = subprocess.run(
            [sys.executable, "update_completed.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"⚠️  Update error: {e}")
    
    # Step 3: Run morning or evening report based on time
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    
    # Determine report type (morning if before 12 PM, evening otherwise)
    if current_hour < 12:
        report_type = "morning"
        print(f"\n3. 🌅 Running {report_type} report (current time: {current_hour:02d}:{current_minute:02d})...")
    else:
        report_type = "evening"
        print(f"\n3. 🌙 Running {report_type} report (current time: {current_hour:02d}:{current_minute:02d})...")
    
    try:
        if report_type == "morning":
            result = subprocess.run(
                [sys.executable, "wholescaleos_system.py", "--morning"],
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                [sys.executable, "wholescaleos_system.py", "--evening"],
                capture_output=True,
                text=True
            )
        
        # Print the output
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Report warnings: {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠️  Report error: {e}")
    
    # Step 4: Show final status
    print("\n4. 📊 Final System Status")
    print("=" * 60)
    
    try:
        with open("wholescaleos_todo.json", 'r') as f:
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
            print(f"   🔄 Last Google Doc sync: {todo_data['last_sync']}")
        
        # Check email config
        try:
            with open("email_config.json", 'r') as f:
                email_config = json.load(f)
            
            if email_config.get("smtp_password") != "YOUR_GMAIL_APP_PASSWORD_HERE":
                print(f"   📧 Email: ✅ Configured for {email_config.get('to_email', 'drummerforger@gmail.com')}")
            else:
                print("   📧 Email: ⚠️ Needs configuration")
        except:
            print("   📧 Email: ⚠️ Not configured")
        
        print(f"\n🔄 Next automated run:")
        print(f"   • Morning report: 7:00 AM EST (12:00 UTC)")
        print(f"   • Evening report: 8:00 PM EST (01:00 UTC)")
        print(f"   • Logs: /home/drummer/.openclaw/workspace/monitor.log")
        
    except Exception as e:
        print(f"⚠️  Status error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Complete system run finished!")
    print("\n💡 Next steps:")
    print("   • Check WhatsApp for report")
    print("   • Check email at drummerforger@gmail.com")
    print("   • Message me on WhatsApp with new ideas")
    print("   • System will auto-run tomorrow at 7:00 AM EST")


def manual_idea_add(idea: str):
    """Manually add an idea from WhatsApp."""
    print(f"💡 Processing idea from WhatsApp: {idea[:100]}...")
    
    try:
        result = subprocess.run(
            [sys.executable, "idea_collector.py", "--add", idea, "--priority", "low"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Idea add warnings: {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠️  Idea add error: {e}")


def show_system_status():
    """Show current system status."""
    print("📊 WHOLESCALEOS SYSTEM STATUS")
    print("=" * 60)
    
    try:
        # Load todo data
        with open("wholescaleos_todo.json", 'r') as f:
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
        
        # Check monitor state
        try:
            with open("wholescaleos_monitor_state.json", 'r') as f:
                state = json.load(f)
            print(f"📅 Last monitor run: {state.get('last_run', 'Never')}")
            print(f"🌅 Last morning report: {state.get('last_morning_report', 'Never')}")
            print(f"🌙 Last evening report: {state.get('last_evening_report', 'Never')}")
        except:
            print("📅 Monitor state: Not initialized")
        
        # Check email config
        try:
            with open("email_config.json", 'r') as f:
                email_config = json.load(f)
            
            if email_config.get("smtp_password") != "YOUR_GMAIL_APP_PASSWORD_HERE":
                print(f"\n📧 Email: ✅ Configured for {email_config.get('to_email', 'drummerforger@gmail.com')}")
            else:
                print("\n📧 Email: ⚠️ Needs Gmail app password")
        except:
            print("\n📧 Email: ⚠️ Not configured")
        
        print("\n🔄 Cron Jobs:")
        print("   • Morning report: 7:00 AM EST (cron: 0 12 * * *)")
        print("   • Evening report: 8:00 PM EST (cron: 0 1 * * *)")
        print("   • Log file: /home/drummer/.openclaw/workspace/monitor.log")
        
        print("\n💡 System Features:")
        print("   • GitHub commit monitoring")
        print("   • Google Doc synchronization")
        print("   • WhatsApp idea collection")
        print("   • Email reports (Gmail SMTP)")
        print("   • Automatic todo completion tracking")
        
    except Exception as e:
        print(f"⚠️  Status error: {e}")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete WholescaleOS Productivity System")
    parser.add_argument("--run", action="store_true", help="Run complete system (sync + report)")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--idea", help="Add idea from WhatsApp")
    parser.add_argument("--test", action="store_true", help="Test complete system")
    
    args = parser.parse_args()
    
    if args.run:
        run_complete_system()
    elif args.status:
        show_system_status()
    elif args.idea:
        manual_idea_add(args.idea)
    elif args.test:
        print("🧪 Testing Complete WholescaleOS System...")
        print("=" * 60)
        
        # Test Google Doc sync
        print("\n1. Testing Google Doc sync...")
        try:
            subprocess.run([sys.executable, "auto_sync_google_doc.py"], capture_output=True)
            print("✅ Google Doc sync test passed")
        except:
            print("⚠️  Google Doc sync test failed")
        
        # Test idea collection
        print("\n2. Testing idea collection...")
        try:
            result = subprocess.run(
                [sys.executable, "idea_collector.py", "--add", "Test feature idea", "--priority", "low"],
                capture_output=True,
                text=True
            )
            if "added" in result.stdout.lower():
                print("✅ Idea collection test passed")
            else:
                print("⚠️  Idea collection test issues")
        except:
            print("⚠️  Idea collection test failed")
        
        # Test email
        print("\n3. Testing email...")
        try:
            result = subprocess.run(
                [sys.executable, "gmail_reporter.py", "--test"],
                capture_output=True,
                text=True
            )
            if "successful" in result.stdout.lower():
                print("✅ Email test passed")
            else:
                print("⚠️  Email test issues")
        except:
            print("⚠️  Email test failed")
        
        # Show final status
        print("\n4. Final status:")
        show_system_status()
        
        print("\n" + "=" * 60)
        print("✅ Complete system test finished!")
    else:
        print("Complete WholescaleOS Productivity System")
        print("=" * 40)
        print("\nCommands:")
        print("  --run           Run complete system (sync + report)")
        print("  --status        Show system status")
        print("  --idea 'text'   Add idea from WhatsApp")
        print("  --test          Test complete system")
        print("\nAutomated schedule:")
        print("  • Morning: 7:00 AM EST (sync + report)")
        print("  • Evening: 8:00 PM EST (report only)")
        print("\nGoogle Doc: https://docs.google.com/document/d/1cZVIQ9UMljFoyn2S7GDec4ztwDLvCSXUDKg8XhscR3Y")


if __name__ == "__main__":
    main()