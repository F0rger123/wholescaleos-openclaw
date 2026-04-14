#!/usr/bin/env python3
"""
Main entry point for generating productivity reports.
Called by GitHub Actions workflow.
"""

import argparse
import sys
import os
from report_generator import GitHubCommitMonitor

def main():
    parser = argparse.ArgumentParser(description="Generate productivity report")
    parser.add_argument("--type", choices=["morning", "evening"], required=True,
                       help="Type of report to generate")
    parser.add_argument("--config", default="config/secrets.json",
                       help="Path to configuration file")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate report without sending email")
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = GitHubCommitMonitor(args.config)
    
    # Generate report
    if args.type == "morning":
        report_data = monitor.generate_morning_report()
        print("Generated morning report")
    else:
        report_data = monitor.generate_evening_report()
        print("Generated evening report")
    
    # Add repo info to report data
    report_data['repo_owner'] = monitor.repo_owner
    report_data['repo_name'] = monitor.repo_name
    
    # Print report summary
    print(f"\nReport Summary:")
    print(f"Type: {report_data['report_type']}")
    print(f"Date: {report_data['date']}")
    
    if args.type == "morning":
        print(f"Yesterday's commits: {len(report_data['yesterday_commits'])}")
        print(f"Completed todos: {len(report_data['todo_analysis']['completed'])}")
        print(f"Remaining todos: {len(report_data['todo_analysis']['remaining'])}")
    else:
        print(f"Today's commits: {len(report_data['today_commits'])}")
        print(f"Productivity score: {report_data['productivity']['score']:.1f}%")
    
    # Send email unless dry-run
    if not args.dry_run:
        print("\nSending email...")
        success = monitor.send_email(report_data)
        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email", file=sys.stderr)
            sys.exit(1)
    else:
        print("\nDry run - email not sent")
    
    # Save report to file for debugging
    import json
    os.makedirs("reports", exist_ok=True)
    report_file = f"reports/{report_data['report_type']}_{report_data['date']}.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    main()