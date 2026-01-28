#!/usr/bin/env python3
"""
Test script to verify dashboard WebSocket connection
"""
import socketio
import time

print("🧪 Testing Atlas Eyes Dashboard Connection")
print("=" * 50)

# Create Socket.IO client
sio = socketio.Client()

data_received = False
roi_received = False

@sio.on('connect')
def on_connect():
    print("✅ Connected to WebSocket server")

@sio.on('disconnect')
def on_disconnect():
    print("❌ Disconnected from server")

@sio.on('data')
def on_data(data):
    global data_received
    if not data_received:
        print(f"✅ Received motion data:")
        print(f"   - FPS: {data.get('fps', 'N/A')}")
        print(f"   - Motion Intensity: {data.get('motion_intensity', 'N/A')}")
        print(f"   - BPM: {data.get('bpm', 'N/A')}")
        print(f"   - Tremor: {data.get('tremor_freq', 'N/A')}")
        data_received = True

@sio.on('roi_data')
def on_roi_data(data):
    global roi_received
    if not roi_received:
        print(f"✅ Received ROI data:")
        rois = data.get('rois', {})
        print(f"   - Hands: {len(rois.get('hands', []))}")
        print(f"   - Face: {'Yes' if rois.get('face') else 'No'}")
        print(f"   - Chest: {'Yes' if rois.get('chest') else 'No'}")
        roi_received = True

try:
    print("\n🔌 Connecting to http://localhost:5001...")
    sio.connect('http://localhost:5001')
    
    print("⏳ Listening for data (10 seconds)...\n")
    time.sleep(10)
    
    print("\n" + "=" * 50)
    if data_received and roi_received:
        print("✅ SUCCESS! Both data and ROI data received")
        print("   Dashboard should be working now!")
    elif data_received:
        print("⚠️  Partial Success: Motion data received but NO ROI data")
        print("   Check if camera is detecting hands/face")
    else:
        print("❌ FAILED: No data received")
        print("   Check if API server is running on port 5001")
    
    sio.disconnect()
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Is API server running? Check: http://localhost:5001/api/status")
    print("   2. Camera active? Look for motion in front of camera")
    print("   3. Firewall blocking localhost connections?")
