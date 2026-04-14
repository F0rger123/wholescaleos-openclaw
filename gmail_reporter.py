#!/usr/bin/env python3
"""
Gmail SMTP Reporter for WholescaleOS
Sends email reports via Gmail SMTP.
"""

import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, Any

class GmailReporter:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load email configuration."""
        try:
            with open("email_config.json", 'r') as f:
                config = json.load(f)
                
            # Check if password is still the placeholder
            if config.get("smtp_password") == "YOUR_GMAIL_APP_PASSWORD_HERE":
                print("⚠️  Gmail app password not configured")
                print("ℹ️  Please edit email_config.json with your app password")
                config["provider"] = "none"
            
            return config
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return {
                "provider": "none",
                "to_email": "drummerforger@gmail.com"
            }
    
    def send_report(self, report_type: str, report_text: str) -> bool:
        """Send a productivity report via Gmail SMTP."""
        if self.config.get("provider") != "smtp":
            print("   ⚠️  Gmail SMTP not configured")
            print("   ℹ️  Edit email_config.json with your Gmail app password")
            return False
        
        to_email = self.config.get("to_email", "drummerforger@gmail.com")
        from_email = self.config.get("from_email", to_email)
        smtp_username = self.config.get("smtp_username", to_email)
        smtp_password = self.config.get("smtp_password", "")
        
        if not smtp_password or smtp_password == "YOUR_GMAIL_APP_PASSWORD_HERE":
            print("   ⚠️  Gmail app password not configured")
            print("   ℹ️  Get app password from: https://myaccount.google.com/apppasswords")
            return False
        
        if report_type == "morning":
            subject = f"🌅 WholescaleOS Morning Report - {datetime.now().strftime('%Y-%m-%d')}"
        else:
            subject = f"🌙 WholescaleOS Evening Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        try:
            # Create email message
            msg = MIMEText(report_text)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            print(f"   📧 Attempting to send email to {to_email}...")
            
            # Connect to Gmail SMTP
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                
                print(f"   🔐 Logging in as {smtp_username}...")
                server.login(smtp_username, smtp_password)
                
                print("   📤 Sending email...")
                server.sendmail(from_email, to_email, msg.as_string())
            
            print(f"   ✅ Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("   ❌ Authentication failed")
            print("   ℹ️  Make sure you're using an APP PASSWORD, not your regular password")
            print("   ℹ️  Generate one at: https://myaccount.google.com/apppasswords")
            return False
            
        except Exception as e:
            print(f"   ❌ Error sending email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Gmail SMTP connection."""
        print("🧪 Testing Gmail SMTP connection...")
        
        if self.config.get("provider") != "smtp":
            print("❌ SMTP not configured in email_config.json")
            return False
        
        smtp_username = self.config.get("smtp_username", "")
        smtp_password = self.config.get("smtp_password", "")
        
        if not smtp_password or smtp_password == "YOUR_GMAIL_APP_PASSWORD_HERE":
            print("❌ Gmail app password not configured")
            print("ℹ️  Get app password from: https://myaccount.google.com/apppasswords")
            return False
        
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_username, smtp_password)
            
            print("✅ Gmail SMTP connection successful!")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed - check your app password")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gmail Reporter for WholescaleOS")
    parser.add_argument("--test", action="store_true", help="Test Gmail SMTP connection")
    parser.add_argument("--send", help="Send test email with provided text")
    
    args = parser.parse_args()
    
    reporter = GmailReporter()
    
    if args.test:
        reporter.test_connection()
    elif args.send:
        success = reporter.send_report("test", args.send)
        if success:
            print("✅ Test email sent!")
        else:
            print("❌ Failed to send test email")
    else:
        print("Gmail Reporter for WholescaleOS")
        print("Usage:")
        print("  --test          Test Gmail SMTP connection")
        print("  --send 'text'   Send test email")
        print("\nConfiguration file: email_config.json")
        print("Make sure to use Gmail APP PASSWORD, not regular password!")


if __name__ == "__main__":
    main()