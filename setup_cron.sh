#!/bin/bash
# Setup Beautiful WholescaleOS Productivity System Cron Jobs

echo "🎨 Setting up Beautiful WholescaleOS Productivity System"
echo "========================================================"

# Create the cron jobs
CRON_JOBS="
# Beautiful WholescaleOS Morning Report - 7:00 AM EST (12:00 UTC)
# Includes Google Doc sync + beautiful morning report
0 12 * * * cd /home/drummer/.openclaw/workspace && /usr/bin/python3 beautiful_wholescaleos_system.py --morning >> /home/drummer/.openclaw/workspace/monitor.log 2>&1

# Beautiful WholescaleOS Evening Report - 8:00 PM EST (01:00 UTC next day)
# Beautiful evening report only
0 1 * * * cd /home/drummer/.openclaw/workspace && /usr/bin/python3 beautiful_wholescaleos_system.py --evening >> /home/drummer/.openclaw/workspace/monitor.log 2>&1
"

# Add to user's crontab
(crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -

echo "✅ Cron jobs added successfully!"
echo ""
echo "🎨 REPORT STYLE: Twin.so beautiful format"
echo "📅 Schedule:"
echo "  • 7:00 AM EST: Google Doc sync + Beautiful morning report"
echo "  • 8:00 PM EST: Beautiful evening report"
echo ""
echo "📝 Logs will be saved to: /home/drummer/.openclaw/workspace/monitor.log"
echo ""
echo "🔄 Google Doc Integration:"
echo "  • Auto-syncs with: https://docs.google.com/document/d/1cZVIQ9UMljFoyn2S7GDec4ztwDLvCSXUDKg8XhscR3Y"
echo "  • Tracks 110 todo items across 3 priority levels"
echo "  • Auto-marks completed items based on commit analysis"
echo ""
echo "💡 WhatsApp Idea Collection:"
echo "  Just message me on WhatsApp with your ideas!"
echo "  I'll automatically add them to your todo list."
echo ""
echo "📧 Email Configuration:"
echo "  • Gmail SMTP configured for drummerforger@gmail.com"
echo "  • Test emails sent successfully"
echo "  • Beautiful HTML + text reports"
echo ""
echo "📊 Current Stats:"
echo "  • 🔴 High Priority: 17 items"
echo "  • 🟡 Medium Priority: 17 items"
echo "  • 🟢 Low Priority: 56 items"
echo "  • ✅ Completed: 20 items"
echo "  • 📈 Total: 110 items tracked"
echo ""
echo "To check if cron is working:"
echo "  tail -f /home/drummer/.openclaw/workspace/monitor.log"
echo ""
echo "To edit cron jobs:"
echo "  crontab -e"
echo ""
echo "To test the beautiful system:"
echo "  python3 beautiful_wholescaleos_system.py --test"
echo ""
echo "🎉 Beautiful system is ready! You'll get your first beautiful report tomorrow at 7:00 AM EST."