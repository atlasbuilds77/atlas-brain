# UI Build Skill

## Purpose
Create web dashboards and interfaces for trading systems.

## Tech Stack
- FastAPI (backend)
- Jinja2 templates or React (frontend)
- WebSocket for real-time updates
- TailwindCSS for styling

## Steps
1. Define UI requirements (pages, components)
2. Create FastAPI routes
3. Build HTML templates
4. Add WebSocket for live data
5. Style with dark theme (trading standard)
6. Make mobile responsive
7. Add controls (start/stop, config reload)
8. Test all interactions

## Template Structure
```
project/
├── main.py (FastAPI app)
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   └── js/
└── requirements.txt
```

## Dark Theme Colors
- Background: #1a1a2e
- Cards: #16213e
- Accent: #0f3460
- Text: #e4e4e4
- Success: #00ff88
- Danger: #ff4757
- Warning: #ffa502

## Checklist
- [ ] Routes defined
- [ ] Templates created
- [ ] WebSocket connected
- [ ] Dark theme applied
- [ ] Mobile responsive
- [ ] Controls working
