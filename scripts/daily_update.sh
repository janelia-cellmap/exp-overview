#!/bin/bash

# Daily experiment overview update script
# This script runs run.sh, commits changes, and pushes to repository

# Get current date for commit message
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Change to project directory
cd /groups/cellmap/cellmap/zouinkhim/exp-overview

# Activate conda environment
# source ~/miniforge3/etc/profile.d/conda.sh
conda activate fly

# Log the start of the process
echo "[$TIMESTAMP] Starting daily update process..." >> logs/daily_update.log
echo "[$TIMESTAMP] Activated conda environment: fly" >> logs/daily_update.log

# Run the main update script
echo "[$TIMESTAMP] Running run.sh..." >> logs/daily_update.log
./run.sh >> logs/daily_update.log 2>&1

# Check if run.sh executed successfully
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] run.sh completed successfully" >> logs/daily_update.log
else
    echo "[$TIMESTAMP] ERROR: run.sh failed with exit code $?" >> logs/daily_update.log
    exit 1
fi

# Add all changes to git
echo "[$TIMESTAMP] Adding changes to git..." >> logs/daily_update.log
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "[$TIMESTAMP] No changes to commit" >> logs/daily_update.log
else
    # Commit with date as message
    echo "[$TIMESTAMP] Committing changes..." >> logs/daily_update.log
    git commit -m "Daily update $DATE"
    
    # Push to repository
    echo "[$TIMESTAMP] Pushing to repository..." >> logs/daily_update.log
    git push >> logs/daily_update.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$TIMESTAMP] Successfully pushed changes to repository" >> logs/daily_update.log
    else
        echo "[$TIMESTAMP] ERROR: Failed to push to repository" >> logs/daily_update.log
        exit 1
    fi
fi

echo "[$TIMESTAMP] Daily update process completed successfully" >> logs/daily_update.log