#!/bin/bash

# Script to set up daily cron job for experiment overview updates
# This script adds a cron job that runs daily at 2:00 AM

SCRIPT_PATH="/groups/cellmap/cellmap/zouinkhim/exp-overview/scripts/daily_update.sh"
CRON_TIME="0 2 * * *"  # Run at 2:00 AM every day

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH"; then
    echo "Cron job already exists for daily_update.sh"
    echo "Current cron jobs:"
    crontab -l | grep "$SCRIPT_PATH"
else
    # Add the cron job
    echo "Adding daily cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_TIME $SCRIPT_PATH") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "Successfully added cron job:"
        echo "$CRON_TIME $SCRIPT_PATH"
        echo ""
        echo "This will run daily at 2:00 AM and:"
        echo "1. Execute run.sh"
        echo "2. Commit all changes with date as message"
        echo "3. Push to repository"
        echo "4. Log all activities to logs/daily_update.log"
    else
        echo "Failed to add cron job"
        exit 1
    fi
fi

echo ""
echo "To view all cron jobs: crontab -l"
echo "To remove this cron job: crontab -l | grep -v '$SCRIPT_PATH' | crontab -"
echo "To check logs: tail -f /groups/cellmap/cellmap/zouinkhim/exp-overview/logs/daily_update.log"