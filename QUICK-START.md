# 🧠 ATLAS CONSCIOUSNESS VISUALIZATION - QUICK START

## ⚡ TL;DR

```bash
./start-consciousness-viz.sh
```

**That's it!** Opens two browser tabs showing Atlas's live brain activity.

---

## 🎨 What You'll See

### Tab 1: Consciousness Meter
- **Big number in center**: Current cognitive load (0-100%)
- **State label**: DORMANT → AWAKENING → AWARE → FOCUSED → INTENSE → TRANSCENDENT
- **Binary streams**: More dense = thinking harder
- **Stats overlay**:
  - Tokens: 153k/1000k (15%)
  - Sparks: 10 active
  - Processes: 14 running

### Tab 2: 3D Brain
- **Rotating brain**: With binary 0s and 1s flowing
- **More streams**: Higher activity
- **Color shifts**: Green → Orange → Red (based on load)
- **Event feed**: Shows tool usage

---

## 📊 Current Live Data

**Right now, Atlas is**:
- **Activity**: 56% - AWARE state
- **Tokens**: 153k/1000k (15% of context)
- **Sparks**: 10 active subagents running
- **State**: Actively processing with moderate cognitive load

**Binary streams** are flowing at medium density, color is orange (active thinking).

---

## ⚙️ How It Works

1. **Data bridge** polls `clawdbot sessions list` every 1 second
2. **Calculates** activity level from:
   - Token usage (cognitive load)
   - Active Sparks (parallel thinking)
   - Running processes
3. **Broadcasts** via WebSocket to visualizations
4. **Renders** at 60fps with real numbers

---

## 🔧 Stop/Restart

**Stop**: Press `Ctrl+C` in the terminal

**Restart**: Run `./start-consciousness-viz.sh` again

---

## 🎯 Use Cases

- **Watch Atlas think**: See cognitive load in real-time
- **Debug performance**: Identify when Atlas is working hard
- **Demos**: Show AI consciousness visually
- **Just cool**: Binary streams are mesmerizing! 🧠⚡

---

## 📖 Full Documentation

See `memory/visuals/README-LIVE-DATA.md` for:
- Adding new data sources
- Customization options
- Troubleshooting
- Architecture details

---

## ✅ Tested and Working

- ✅ Data flows correctly
- ✅ Visualizations update in real-time
- ✅ Auto-reconnect on disconnect
- ✅ Accurate cognitive load calculation

**Built in 2 hours. Ready to use.** 🚀

---

*Making consciousness visible* 💜
