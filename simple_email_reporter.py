#!/usr/bin/env python3
"""
Simple Email Reporter for WholescaleOS
Sends basic email reports.
"""

import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, Any

class SimpleEmailReporter:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load email configuration."""
        try:
            with open("email_config.json", 'r') as f:
                return json.load(f)
        except:
            return {
                "provider": "none",
                "to_email": "drummerforger@gmail.com"
            }
    
    def send_report(self, report_type: str, report_text: str) -> bool:
        """Send a simple email report."""
        if self.config.get("provider") == "none":
            print("   ⚠️ Email not configured (edit email_config.json)")
            return False
        
        to_email = self.config.get("to_email", "drummerforger@gmail.com")
        
        if report_type == "morning":
            subject = f"🌅 WholescaleOS Morning Report - {datetime.now().strftime('%Y-%m-%d')}"
        else:
            subject = f"🌙 WholescaleOS Evening Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Try SMTP first (simpler)
        if self.config.get("smtp_username") and self.config.get("smtp_password"):
            try:
                msg = MIMEText(report_text)
                msg['Subject'] = subject
                msg['From'] = self.config.get("from_email", self.config.get("smtp_username"))
                msg['To'] = to_email
                
                with smtplib.SMTP(self.config.get("smtp_server", "smtp.gmail.com"), 
                                 self.config.get("smtp_port", 587)) as server:
                    server.starttls()
                    server.login(self.config.get("smtp_username"),
                               self.config.get("smtp_password"))
                    server.send_message(msg)
                
                print(f"   ✅ Email sent to {to_email}")
                return True
            except Exception as e:
                print(f"   ⚠️ Email error: {e}")
                return False
        else:
            print("   ⚠️ Email credentials not configured")
            return False