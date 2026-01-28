# Atlas Trading Intelligence System - Structure & Workflow

## Overview
The Atlas Trading Intelligence System is a structured memory system for organizing trading research, analysis, and opportunities. It provides a consistent framework for capturing market intelligence across multiple dimensions.

## Directory Structure

```
~/clawd/memory/trading/
├── concepts/              # Trading education & concepts
├── macro/                 # Daily macro state analysis
├── flow/                  # Options flow patterns
├── gamma/                 # Gamma exposure tracking
├── news/                  # Categorized news feed
├── opportunities/         # Daily play ideas
├── chart-analyses/        # Saved chart reviews
├── templates/             # Template files (symlinked)
│   ├── macro-state-template.md
│   ├── flow-pattern-template.md
│   ├── gamma-levels-template.md
│   ├── news-feed-template.md
│   ├── opportunity-template.md
│   └── chart-analysis-template.md
└── STRUCTURE.md          # This file
```

## Component Descriptions

### 1. Concepts/ (Trading Education)
- **Purpose**: Store trading concepts, strategies, and educational materials
- **Format**: Markdown files organized by topic
- **Examples**: 
  - `options-greeks.md`
  - `market-microstructure.md`
  - `risk-management-framework.md`
- **Usage**: Reference library for trading knowledge

### 2. Macro/ (Daily Macro State)
- **Purpose**: Track daily macroeconomic conditions
- **Format**: Daily files named `YYYY-MM-DD-macro.md`
- **Template**: `macro-state-template.md`
- **Update Frequency**: Daily (pre-market)
- **Key Sections**:
  - Economic indicators
  - Central bank watch
  - Yield curves & bonds
  - Commodities
  - Market internals
  - Sector performance

### 3. Flow/ (Options Flow Patterns)
- **Purpose**: Record unusual options activity and flow patterns
- **Format**: Files named `YYYY-MM-DD-TICKER-flow.md` or `YYYY-MM-DD-pattern-type.md`
- **Template**: `flow-pattern-template.md`
- **Update Frequency**: As detected
- **Key Sections**:
  - Flow details
  - Smart money indicators
  - Pattern analysis
  - Risk management

### 4. Gamma/ (Gamma Exposure Tracking)
- **Purpose**: Monitor gamma exposure and dealer positioning
- **Format**: Daily files named `YYYY-MM-DD-gamma.md`
- **Template**: `gamma-levels-template.md`
- **Update Frequency**: Daily (market hours)
- **Key Sections**:
  - Gamma profile
  - Dealer positioning
  - Volatility analysis
  - Expiration analysis

### 5. News/ (Categorized News Feed)
- **Purpose**: Organize market-moving news
- **Format**: Daily files named `YYYY-MM-DD-news.md`
- **Template**: `news-feed-template.md`
- **Update Frequency**: Multiple times daily
- **Key Sections**:
  - Top stories by category
  - Sentiment analysis
  - News flow timeline
  - Trading implications

### 6. Opportunities/ (Daily Play Ideas)
- **Purpose**: Document trading opportunities
- **Format**: Files named `YYYY-MM-DD-TICKER-opportunity.md`
- **Template**: `opportunity-template.md`
- **Update Frequency**: As identified
- **Key Sections**:
  - Thesis
  - Multi-factor analysis
  - Risk assessment
  - Execution plan
  - Post-trade review

### 7. Chart-analyses/ (Saved Chart Reviews)
- **Purpose**: Store technical analysis reviews
- **Format**: Files named `YYYY-MM-DD-TICKER-chart.md`
- **Template**: `chart-analysis-template.md`
- **Update Frequency**: Weekly or as needed
- **Key Sections**:
  - Multi-timeframe analysis
  - Technical indicators
  - Pattern recognition
  - Trading implications

## Workflow

### Daily Routine
1. **Pre-Market (7:00 AM EST)**
   - Create new macro file using template
   - Update gamma exposure
   - Scan overnight news

2. **Market Open (9:30 AM EST)**
   - Monitor options flow
   - Update news feed
   - Identify initial opportunities

3. **Mid-Day (12:00 PM EST)**
   - Update gamma levels
   - Add to news feed
   - Refine opportunities

4. **Market Close (4:00 PM EST)**
   - Finalize daily files
   - Document flow patterns
   - Prepare next day's watchlist

### Weekly Routine
- **Sunday Evening**: Weekly macro preview
- **Friday Close**: Weekly performance review
- **Monthly**: Archive and summarize

## File Naming Convention
- Dates: `YYYY-MM-DD`
- Tickers: Uppercase (e.g., `AAPL`, `SPY`)
- Types: `-macro`, `-flow`, `-gamma`, `-news`, `-opportunity`, `-chart`
- Examples:
  - `2024-01-15-macro.md`
  - `2024-01-15-AAPL-flow.md`
  - `2024-01-15-gamma.md`
  - `2024-01-15-news.md`
  - `2024-01-15-NVDA-opportunity.md`
  - `2024-01-15-SPY-chart.md`

## Template Usage
1. Copy template to appropriate directory
2. Replace `{{PLACEHOLDERS}}` with actual data
3. Save with proper naming convention
4. Update as new information arrives

## Search & Retrieval
The system is designed to be searchable via `memory_search()` function. Key search patterns:

```bash
# Search for specific ticker
memory_search("AAPL opportunities")

# Search by date
memory_search("2024-01-15 macro")

# Search by concept
memory_search("gamma exposure SPY")

# Search by pattern type
memory_search("unusual options flow")
```

## Cron Job Specification

### Daily Updates
```bash
# Pre-market macro update (7:00 AM EST)
0 7 * * 1-5 /path/to/scripts/update_macro.sh

# Morning gamma check (9:45 AM EST)
45 9 * * 1-5 /path/to/scripts/update_gamma.sh

# Mid-day news update (12:00 PM EST)
0 12 * * 1-5 /path/to/scripts/update_news.sh

# End-of-day summary (4:15 PM EST)
15 16 * * 1-5 /path/to/scripts/daily_summary.sh
```

### Weekly Tasks
```bash
# Sunday evening weekly preview (8:00 PM EST)
0 20 * * 0 /path/to/scripts/weekly_preview.sh

# Friday close weekly review (4:30 PM EST)
30 16 * * 5 /path/to/scripts/weekly_review.sh
```

### Monthly Tasks
```bash
# Month-end archive (last trading day, 5:00 PM EST)
0 17 28-31 * 1-5 [ $(date +\%d -d tomorrow) = 01 ] && /path/to/scripts/monthly_archive.sh
```

## Maintenance

### Archiving
- Monthly: Move files to `archive/YYYY-MM/`
- Quarterly: Compress archive directories
- Yearly: Create annual summary

### Cleanup
- Remove empty template files
- Archive completed opportunities
- Consolidate similar analyses

### Backup
- Daily sync to cloud storage
- Weekly git commit of changes
- Monthly full backup

## Integration Points

### Data Sources
- Macro: Bloomberg, Reuters, FRED
- Flow: CBOE, options exchanges
- Gamma: OptionMetrics, SpotGamma
- News: Bloomberg, Reuters, Twitter
- Charts: TradingView, Thinkorswim

### Tools
- Analysis: Python/R scripts
- Visualization: Jupyter notebooks
- Automation: Bash scripts
- Monitoring: Alert systems

## Best Practices

1. **Consistency**: Use templates consistently
2. **Timeliness**: Update files promptly
3. **Completeness**: Fill all relevant sections
4. **Objectivity**: Separate facts from opinions
5. **Traceability**: Document data sources
6. **Review**: Regularly review and refine

## Getting Started

1. **Initial Setup**:
   ```bash
   cd ~/clawd/memory/trading
   cp templates/*.md ./
   ```

2. **First Day**:
   - Create macro file for today
   - Set up news feed
   - Initialize gamma tracking

3. **Ongoing**:
   - Follow daily workflow
   - Use templates for consistency
   - Regular search and review

## Troubleshooting

### Common Issues
1. **Missing templates**: Copy from `templates/` directory
2. **Search not working**: Check file naming conventions
3. **Outdated data**: Verify cron jobs are running
4. **Storage issues**: Implement archiving schedule

### Support
- Check `STRUCTURE.md` for guidance
- Review template examples
- Consult trading system documentation

---

*Last Updated: {{DATE}}*
*System Version: 1.0*