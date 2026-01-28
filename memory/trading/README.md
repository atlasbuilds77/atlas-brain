# Atlas Trading Intelligence System

## Quick Start

1. **Review Structure**: Read `STRUCTURE.md` for system overview
2. **Use Templates**: Copy templates from `templates/` directory
3. **Daily Workflow**: Follow the workflow in `STRUCTURE.md`
4. **Automation**: Set up cron jobs from `CRON_SPEC.md`

## Directory Contents

- `concepts/` - Trading education materials
- `macro/` - Daily macroeconomic analysis
- `flow/` - Options flow patterns
- `gamma/` - Gamma exposure tracking
- `news/` - Categorized news feed
- `opportunities/` - Trading opportunity ideas
- `chart-analyses/` - Technical chart reviews
- `templates/` - Template files for all components
- `STRUCTURE.md` - System documentation
- `CRON_SPEC.md` - Automation specification
- `README.md` - This file

## Search Examples

```bash
# Search for AAPL opportunities
memory_search("AAPL opportunity")

# Search today's macro
memory_search("$(date +%Y-%m-%d) macro")

# Search gamma levels
memory_search("gamma exposure")

# Search news by ticker
memory_search("NVDA news")
```

## Maintenance

- Daily: Follow cron schedule
- Weekly: Review and archive
- Monthly: Backup and cleanup

## Support

Refer to `STRUCTURE.md` for detailed guidance on using the system.