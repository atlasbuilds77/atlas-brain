#!/bin/bash

# Atlas Eyes Auto-Start Script
# Launches API server and optionally opens the dashboard

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PORT=5001
CAMERA=0
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
API_SCRIPT="$SCRIPT_DIR/src/atlas_api.py"
DASHBOARD="$SCRIPT_DIR/examples/motion_trails_dashboard.html"

echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Atlas Eyes Auto-Start${NC}"
echo -e "${CYAN}================================${NC}\n"

# Check if API script exists
if [ ! -f "$API_SCRIPT" ]; then
    echo -e "${RED}❌ Error: API script not found at $API_SCRIPT${NC}"
    exit 1
fi

# Check if already running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use. Is the server already running?${NC}"
    read -p "Kill existing process and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Stopping existing server...${NC}"
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo -e "${RED}Aborted.${NC}"
        exit 1
    fi
fi

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${GREEN}✅ Activating virtual environment...${NC}"
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${GREEN}✅ Activating virtual environment...${NC}"
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Check dependencies
echo -e "${CYAN}Checking dependencies...${NC}"
python3 -c "import flask, flask_socketio, cv2, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Missing dependencies. Install with: pip install -r requirements.txt${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All dependencies present${NC}\n"

# Start the API server
echo -e "${CYAN}Starting Atlas Eyes API Server...${NC}"
echo -e "${CYAN}  Port: $PORT${NC}"
echo -e "${CYAN}  Camera: $CAMERA${NC}"
echo -e "${CYAN}  Auto-start: enabled${NC}\n"

# Check if we should open the dashboard
OPEN_DASHBOARD=false
if [ "$1" == "--dashboard" ] || [ "$1" == "-d" ]; then
    OPEN_DASHBOARD=true
fi

# Start server in background or foreground
if [ "$1" == "--background" ] || [ "$1" == "-b" ]; then
    echo -e "${YELLOW}Starting in background mode...${NC}"
    nohup python3 "$API_SCRIPT" --port $PORT --camera $CAMERA > "$SCRIPT_DIR/atlas_eyes.log" 2>&1 &
    SERVER_PID=$!
    echo -e "${GREEN}✅ Server started (PID: $SERVER_PID)${NC}"
    echo -e "${CYAN}   Log: $SCRIPT_DIR/atlas_eyes.log${NC}"
    
    # Wait for server to start
    echo -e "${CYAN}Waiting for server to start...${NC}"
    for i in {1..10}; do
        sleep 1
        if curl -s http://localhost:$PORT/api/status > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is responding${NC}\n"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Server failed to start. Check the log.${NC}"
            exit 1
        fi
    done
    
    # Open dashboard if requested
    if [ "$OPEN_DASHBOARD" = true ]; then
        echo -e "${CYAN}Opening dashboard...${NC}"
        open "$DASHBOARD" 2>/dev/null || xdg-open "$DASHBOARD" 2>/dev/null || echo -e "${YELLOW}⚠️  Could not open dashboard automatically. Open manually: $DASHBOARD${NC}"
    fi
    
    echo -e "\n${GREEN}🎉 Atlas Eyes is running!${NC}"
    echo -e "${CYAN}   API: http://localhost:$PORT${NC}"
    echo -e "${CYAN}   Dashboard: $DASHBOARD${NC}"
    echo -e "${CYAN}   To stop: kill $SERVER_PID${NC}\n"
else
    # Foreground mode
    echo -e "${YELLOW}Starting in foreground mode (Ctrl+C to stop)...${NC}\n"
    
    # Open dashboard if requested
    if [ "$OPEN_DASHBOARD" = true ]; then
        echo -e "${CYAN}Opening dashboard...${NC}"
        open "$DASHBOARD" 2>/dev/null || xdg-open "$DASHBOARD" 2>/dev/null || echo -e "${YELLOW}⚠️  Could not open dashboard automatically. Open manually: $DASHBOARD${NC}"
        sleep 2
    fi
    
    # Start server in foreground
    python3 "$API_SCRIPT" --port $PORT --camera $CAMERA
fi
