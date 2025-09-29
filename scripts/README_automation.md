# Daily Automation Setup

This directory contains scripts for automating the daily execution of experiment overview updates.

## Files

### `daily_update.sh`
Main automation script that:
1. Executes `run.sh` to update experiment data and visualizations
2. Commits all changes to git with date as the commit message
3. Pushes changes to the repository
4. Logs all activities with timestamps

### `setup_cron.sh` 
Setup script that installs the daily cron job. Run once to set up automation.

## Cron Job Schedule

The cron job runs daily at **2:00 AM** with the following command:
```
0 2 * * * /groups/cellmap/cellmap/zouinkhim/exp-overview/scripts/daily_update.sh
```

## Monitoring

### View Logs
```bash
# View latest log entries
tail -f /groups/cellmap/cellmap/zouinkhim/exp-overview/logs/daily_update.log

# View all logs
cat /groups/cellmap/cellmap/zouinkhim/exp-overview/logs/daily_update.log
```

### Check Cron Jobs
```bash
# List all cron jobs
crontab -l

# Check if the daily update job exists
crontab -l | grep daily_update.sh
```

## Management Commands

### Remove Cron Job
```bash
crontab -l | grep -v '/groups/cellmap/cellmap/zouinkhim/exp-overview/scripts/daily_update.sh' | crontab -
```

### Manual Execution
```bash
# Test the daily update script manually
cd /groups/cellmap/cellmap/zouinkhim/exp-overview
./scripts/daily_update.sh
```

### Re-setup Cron Job
```bash
# Run the setup script again
./scripts/setup_cron.sh
```

## Log Format

The log file contains timestamped entries for each step:
- Script start/completion
- run.sh execution
- Git operations (add, commit, push)
- Error messages if any step fails

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure scripts are executable
   ```bash
   chmod +x scripts/daily_update.sh scripts/setup_cron.sh
   ```

2. **Git authentication**: Make sure SSH keys are set up for automatic git push

3. **Path issues**: Cron jobs run with minimal environment, all paths in the script are absolute

4. **Environment variables**: The script activates the conda environment as needed

### Manual Testing

Before relying on the cron job, test manually:
```bash
cd /groups/cellmap/cellmap/zouinkhim/exp-overview
./scripts/daily_update.sh
```

Check the log file after execution to ensure everything worked correctly.