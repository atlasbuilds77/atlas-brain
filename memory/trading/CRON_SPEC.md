# Cron Job Specification for Atlas Trading Intelligence System

## Overview
This document specifies the cron jobs needed to maintain the Atlas Trading Intelligence System. These jobs automate daily updates and ensure the memory structure stays current.

## Prerequisites
1. Ensure you have necessary API keys and data sources configured
2. Install required Python/R packages for data collection
3. Set up proper permissions for script execution

## Daily Schedule (EST Timezone)

### Pre-Market (7:00 AM)
**Job**: Update Macro State
```bash
# Macro data collection and template population
0 7 * * 1-5 /Users/atlasbuilds/clawd/scripts/update_macro.sh
```

**Script**: `update_macro.sh`
```bash
#!/bin/bash
cd /Users/atlasbuilds/clawd/memory/trading
DATE=$(date +%Y-%m-%d)
# Create macro file from template
cp templates/macro-state-template.md macro/$DATE-macro.md
# Run macro data collection script
python3 /Users/atlasbuilds/clawd/scripts/collect_macro_data.py --date $DATE
# Update placeholders with actual data
# ... data processing logic ...
```

### Market Open (9:30 AM)
**Job**: Initial Gamma Check
```bash
# Initial gamma exposure snapshot
30 9 * * 1-5 /Users/atlasbuilds/clawd/scripts/update_gamma.sh --initial
```

### Mid-Morning (9:45 AM)
**Job**: Options Flow Scan
```bash
# Scan for unusual options activity
45 9 * * 1-5 /Users/atlasbuilds/clawd/scripts/scan_options_flow.py
```

### Late Morning (11:00 AM)
**Job**: News Feed Update
```bash
# Morning news aggregation
0 11 * * 1-5 /Users/atlasbuilds/clawd/scripts/update_news.sh --morning
```

### Mid-Day (12:00 PM)
**Job**: Gamma Update & Opportunity Scan
```bash
# Mid-day gamma update and opportunity identification
0 12 * * 1-5 /Users/atlasbuilds/clawd/scripts/midday_update.sh
```

### Early Afternoon (2:00 PM)
**Job**: News Feed Refresh
```bash
# Afternoon news update
0 14 * * 1-5 /Users/atlasbuilds/clawd/scripts/update_news.sh --afternoon
```

### Market Close (4:00 PM)
**Job**: End-of-Day Data Collection
```bash
# Collect final market data
0 16 * * 1-5 /Users/atlasbuilds/clawd/scripts/eod_collection.sh
```

### Post-Market (4:15 PM)
**Job**: Daily Summary & Cleanup
```bash
# Generate daily summary and prepare for next day
15 16 * * 1-5 /Users/atlasbuilds/clawd/scripts/daily_summary.sh
```

### Evening (8:00 PM)
**Job**: Next Day Preview
```bash
# Prepare for next trading day
0 20 * * 1-5 /Users/atlasbuilds/clawd/scripts/next_day_preview.sh
```

## Weekly Schedule

### Sunday Evening (8:00 PM)
**Job**: Weekly Macro Preview
```bash
# Weekly economic calendar and preview
0 20 * * 0 /Users/atlasbuilds/clawd/scripts/weekly_preview.sh
```

### Friday Close (4:30 PM)
**Job**: Weekly Performance Review
```bash
# Weekly summary and performance analysis
30 16 * * 5 /Users/atlasbuilds/clawd/scripts/weekly_review.sh
```

## Monthly Schedule

### Last Trading Day (5:00 PM)
**Job**: Monthly Archive
```bash
# Archive current month's files and create monthly summary
0 17 28-31 * 1-5 [ $(date +\%d -d tomorrow) = 01 ] && /Users/atlasbuilds/clawd/scripts/monthly_archive.sh
```

## Script Specifications

### 1. update_macro.sh
```bash
#!/bin/bash
# Purpose: Update daily macro state
# Input: Date (optional, defaults to today)
# Output: Updated macro file in macro/ directory
# Dependencies: Python with pandas, requests, yfinance
```

### 2. update_gamma.sh
```bash
#!/bin/bash
# Purpose: Update gamma exposure levels
# Input: --initial for morning, --update for intraday
# Output: Updated gamma file in gamma/ directory
# Dependencies: Options data API access
```

### 3. update_news.sh
```bash
#!/bin/bash
# Purpose: Aggregate and categorize news
# Input: --morning, --afternoon, or --evening
# Output: Updated news file in news/ directory
# Dependencies: News API, sentiment analysis tools
```

### 4. scan_options_flow.py
```python
#!/usr/bin/env python3
# Purpose: Scan for unusual options flow
# Input: Real-time options data
# Output: Flow pattern files in flow/ directory
# Dependencies: Options data stream, pattern detection library
```

### 5. midday_update.sh
```bash
#!/bin/bash
# Purpose: Mid-day system update
# Tasks:
#   - Update gamma levels
#   - Scan for new opportunities
#   - Refresh technical analyses
# Output: Various updated files
```

### 6. daily_summary.sh
```bash
#!/bin/bash
# Purpose: Generate end-of-day summary
# Tasks:
#   - Finalize all daily files
#   - Generate performance metrics
#   - Prepare next day's templates
# Output: Daily summary report
```

### 7. weekly_preview.sh
```bash
#!/bin/bash
# Purpose: Weekly economic preview
# Tasks:
#   - Analyze upcoming economic events
#   - Set weekly themes
#   - Prepare watchlist
# Output: Weekly preview document
```

### 8. weekly_review.sh
```bash
#!/bin/bash
# Purpose: Weekly performance review
# Tasks:
#   - Analyze weekly performance
#   - Review opportunity success rate
#   - Identify improvement areas
# Output: Weekly review report
```

### 9. monthly_archive.sh
```bash
#!/bin/bash
# Purpose: Monthly archiving and cleanup
# Tasks:
#   - Archive completed files
#   - Generate monthly summary
#   - Clean up temporary files
# Output: Archived monthly directory
```

## Installation Instructions

### Step 1: Create Scripts Directory
```bash
mkdir -p /Users/atlasbuilds/clawd/scripts
```

### Step 2: Create Script Files
```bash
# Copy template scripts to scripts directory
cp /path/to/templates/*.sh /Users/atlasbuilds/clawd/scripts/
cp /path/to/templates/*.py /Users/atlasbuilds/clawd/scripts/
chmod +x /Users/atlasbuilds/clawd/scripts/*.sh
```

### Step 3: Install Dependencies
```bash
# Python dependencies
pip install pandas requests yfinance numpy scipy

# R dependencies (if using R)
Rscript -e "install.packages(c('quantmod', 'TTR', 'PerformanceAnalytics'))"
```

### Step 4: Configure API Keys
```bash
# Create configuration file
cat > /Users/atlasbuilds/clawd/config/api_keys.env << EOF
NEWS_API_KEY=your_news_api_key
OPTIONS_API_KEY=your_options_api_key
MACRO_API_KEY=your_macro_api_key
EOF
```

### Step 5: Set Up Cron Jobs
```bash
# Edit crontab
crontab -e

# Add all cron jobs from this specification
# Use appropriate paths for your system
```

### Step 6: Test Installation
```bash
# Test macro update
/Users/atlasbuilds/clawd/scripts/update_macro.sh

# Test news update
/Users/atlasbuilds/clawd/scripts/update_news.sh --test

# Verify file creation
ls -la /Users/atlasbuilds/clawd/memory/trading/
```

## Monitoring & Maintenance

### Logging
Each script should implement logging:
```bash
LOG_FILE="/Users/atlasbuilds/clawd/logs/$(basename $0 .sh)_$(date +%Y%m%d).log"
exec >> "$LOG_FILE" 2>&1
echo "$(date): Starting $0"
```

### Error Handling
```bash
# Set error handling
set -euo pipefail

# Trap errors
trap 'echo "Error at line $LINENO"; exit 1' ERR
```

### Notification
Configure email/Slack notifications for:
- Script failures
- Data collection issues
- System warnings

### Performance Monitoring
- Monitor script execution times
- Track data collection success rates
- Alert on abnormal conditions

## Troubleshooting

### Common Issues

1. **Script Permission Denied**
   ```bash
   chmod +x /path/to/script.sh
   ```

2. **Python Module Not Found**
   ```bash
   pip install missing_module
   ```

3. **API Key Issues**
   - Verify API keys in config file
   - Check API rate limits
   - Confirm network connectivity

4. **Cron Job Not Running**
   ```bash
   # Check cron service
   systemctl status cron
   
   # Check cron logs
   grep CRON /var/log/syslog
   
   # Test command manually
   /path/to/script.sh
   ```

### Debug Mode
Add debug flag to scripts:
```bash
#!/bin/bash
DEBUG=${DEBUG:-false}
if [ "$DEBUG" = true ]; then
    set -x
fi
```

Run with debug:
```bash
DEBUG=true /path/to/script.sh
```

## Security Considerations

1. **API Keys**: Store in environment variables, not in scripts
2. **Permissions**: Restrict script access to necessary users
3. **Logging**: Avoid logging sensitive data
4. **Network**: Use secure connections (HTTPS, SSH)
5. **Updates**: Regularly update dependencies

## Backup Strategy

### Daily Backups
```bash
# Backup trading memory
0 18 * * 1-5 /Users/atlasbuilds/clawd/scripts/backup_trading.sh
```

### Weekly Backups
```bash
# Full system backup
0 2 * * 0 /Users/atlasbuilds/clawd/scripts/full_backup.sh
```

### Cloud Sync
Consider syncing to cloud storage for redundancy.

## Version Control
```bash
# Initialize git repo
cd /Users/atlasbuilds/clawd/memory/trading
git init
git add .
git commit -m "Initial trading memory structure"

# Daily commits via cron
0 19 * * 1-5 cd /Users/atlasbuilds/clawd/memory/trading && git add . && git commit -m "Daily update $(date +%Y-%m-%d)"
```

## Performance Optimization

### Caching
- Cache frequently accessed data
- Implement data validation
- Use incremental updates

### Parallel Processing
- Run independent scripts in parallel
- Use job queues for heavy processing
- Implement load balancing

### Resource Management
- Monitor memory usage
- Implement timeouts
- Clean up temporary files

---

*Last Updated: {{DATE}}*
*Cron Spec Version: 1.0*