#!/usr/bin/env python3
"""
Brain Visualization Server - "Jarvis Mode"
Serves the live brain visualization and streams cognitive events in real-time.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from aiohttp import web
import aiohttp

# Event queue for broadcasting to all connected clients
event_queue: asyncio.Queue = asyncio.Queue()
connected_clients: Set[web.WebSocketResponse] = set()

# Cognitive event types with colors and regions
EVENT_CONFIG = {
    "pattern_match": {
        "region": "pattern_recognition",
        "color": "#00ff88",
        "priority": "high"
    },
    "emotion": {
        "region": "emotional_processing",
        "color": "#ff4444",
        "priority": "medium"
    },
    "metacognition": {
        "region": "metacognition",
        "color": "#4488ff",
        "priority": "high"
    },
    "memory": {
        "region": "memory",
        "color": "#00bbff",
        "priority": "low"
    },
    "bias_detection": {
        "region": "bias_detection",
        "color": "#ffaa00",
        "priority": "medium"
    },
    "mode_switch": {
        "region": "core",
        "color": "#ff8800",
        "priority": "high"
    },
    "decision": {
        "region": "metacognition",
        "color": "#00ff00",
        "priority": "high"
    }
}

# Brain regions configuration
BRAIN_REGIONS = {
    "pattern_recognition": {
        "name": "Pattern Recognition",
        "position": [1.5, 0.8, 0],
        "color": "#00ff88"
    },
    "emotional_processing": {
        "name": "Emotional Processing",
        "position": [0, 1.5, -1],
        "color": "#ff4444"
    },
    "metacognition": {
        "name": "Metacognition",
        "position": [-1.5, 0.8, 0],
        "color": "#4488ff"
    },
    "memory": {
        "name": "Memory",
        "position": [0, -1.2, 1.2],
        "color": "#00bbff"
    },
    "bias_detection": {
        "name": "Bias Detection",
        "position": [1.2, -0.8, -0.8],
        "color": "#ffaa00"
    },
    "core": {
        "name": "Core",
        "position": [0, 0, 0],
        "color": "#ff8800"
    }
}


async def handle_websocket(request):
    """Handle WebSocket connections for real-time event streaming."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected_clients.add(ws)
    
    print(f"[BRAIN-VIZ] Client connected. Total clients: {len(connected_clients)}")
    
    # Send initial configuration
    await ws.send_json({
        "type": "config",
        "regions": BRAIN_REGIONS,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                # Handle incoming messages (e.g., control commands)
                try:
                    data = json.loads(msg.data)
                    if data.get("type") == "ping":
                        await ws.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    pass
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'[BRAIN-VIZ] WebSocket error: {ws.exception()}')
    finally:
        connected_clients.remove(ws)
        print(f"[BRAIN-VIZ] Client disconnected. Total clients: {len(connected_clients)}")
    
    return ws


async def broadcast_events():
    """Broadcast events from queue to all connected clients."""
    while True:
        try:
            event = await event_queue.get()
            if connected_clients:
                # Broadcast to all connected clients
                for ws in list(connected_clients):
                    try:
                        await ws.send_json(event)
                    except Exception as e:
                        print(f"[BRAIN-VIZ] Error sending to client: {e}")
                        connected_clients.discard(ws)
        except Exception as e:
            print(f"[BRAIN-VIZ] Broadcast error: {e}")
            await asyncio.sleep(0.1)


async def monitor_cognitive_events():
    """Monitor cognitive event log files and broadcast new events."""
    event_log_path = Path("logs/brain-events.jsonl")
    event_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create log file if it doesn't exist
    if not event_log_path.exists():
        event_log_path.write_text("")
    
    # Track last position in file
    last_position = 0
    
    while True:
        try:
            if event_log_path.exists():
                current_size = event_log_path.stat().st_size
                
                if current_size > last_position:
                    with open(event_log_path, 'r') as f:
                        f.seek(last_position)
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    event = json.loads(line)
                                    # Enrich event with display config
                                    event_type = event.get("event_type", "unknown")
                                    if event_type in EVENT_CONFIG:
                                        event["config"] = EVENT_CONFIG[event_type]
                                    await event_queue.put(event)
                                except json.JSONDecodeError:
                                    pass
                        last_position = f.tell()
            
            await asyncio.sleep(0.1)  # Check for new events frequently
        except Exception as e:
            print(f"[BRAIN-VIZ] Monitor error: {e}")
            await asyncio.sleep(1)


async def handle_index(request):
    """Serve the main visualization HTML."""
    html_path = Path(__file__).parent.parent / "memory" / "visuals" / "live-brain.html"
    if html_path.exists():
        return web.FileResponse(html_path)
    else:
        return web.Response(text="Visualization not found. Run setup first.", status=404)


async def handle_test_event(request):
    """Endpoint to inject test events for debugging."""
    try:
        data = await request.json()
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": data.get("event_type", "test"),
            "message": data.get("message", "Test event"),
            "intensity": data.get("intensity", 0.5)
        }
        await event_queue.put(event)
        return web.json_response({"status": "ok", "event": event})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=400)


async def handle_demo_mode(request):
    """Start demo mode with simulated cognitive events."""
    asyncio.create_task(demo_event_generator())
    return web.json_response({"status": "ok", "message": "Demo mode started"})


async def demo_event_generator():
    """Generate simulated cognitive events for demo purposes."""
    demo_events = [
        {"event_type": "pattern_match", "message": "Pattern 'FOMO trade' detected - HIGH NEGATIVE", "intensity": 0.9},
        {"event_type": "emotion", "message": "Somatic marker: anxiety response", "intensity": 0.7},
        {"event_type": "bias_detection", "message": "Confirmation bias detected", "intensity": 0.6},
        {"event_type": "metacognition", "message": "Metacognitive check: verifying claims", "intensity": 0.8},
        {"event_type": "mode_switch", "message": "Switching to DMN MODE: Creative exploration", "intensity": 1.0},
        {"event_type": "memory", "message": "Retrieving pattern: successful trade 2024-12-15", "intensity": 0.5},
        {"event_type": "decision", "message": "Decision: Execute protective stop-loss", "intensity": 0.9},
    ]
    
    while True:
        for event_data in demo_events:
            event = {
                "timestamp": datetime.now().isoformat(),
                **event_data
            }
            await event_queue.put(event)
            await asyncio.sleep(2.5)  # Delay between events


async def init_app():
    """Initialize the web application."""
    app = web.Application()
    
    # Routes
    app.router.add_get('/', handle_index)
    app.router.add_get('/ws', handle_websocket)
    app.router.add_post('/api/test-event', handle_test_event)
    app.router.add_post('/api/demo', handle_demo_mode)
    
    # Static files (for any additional assets)
    static_dir = Path(__file__).parent.parent / "memory" / "visuals"
    if static_dir.exists():
        app.router.add_static('/static/', path=static_dir, name='static')
    
    return app


async def run_server():
    """Run the server with background tasks."""
    port = int(os.getenv("BRAIN_VIZ_PORT", 8765))
    app = await init_app()
    
    # Start background tasks
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    
    # Create background tasks
    broadcast_task = asyncio.create_task(broadcast_events())
    monitor_task = asyncio.create_task(monitor_cognitive_events())
    
    try:
        await site.start()
        # Keep running forever
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down brain visualization server...")
    finally:
        broadcast_task.cancel()
        monitor_task.cancel()
        await runner.cleanup()


def main():
    """Main entry point."""
    port = int(os.getenv("BRAIN_VIZ_PORT", 8765))
    
    print(f"""
╔════════════════════════════════════════════╗
║   ATLAS BRAIN VISUALIZATION - JARVIS MODE  ║
╚════════════════════════════════════════════╝

🧠 Starting brain visualization server...
🌐 Server: http://localhost:{port}
📡 WebSocket: ws://localhost:{port}/ws
🔬 Event log: logs/brain-events.jsonl

Press Ctrl+C to stop.
    """)
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
