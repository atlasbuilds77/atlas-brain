# ATLAS V1 - Build Specifications

**Desktop Robot Platform**
- Height: 18 inches
- Base: Tracked platform (stable, maneuverable)
- Arms: 2x articulated with grippers
- Eyes: LED matrix (8x8)
- Brain: Raspberry Pi 4
- Power: LiPo battery system

---

## 📦 COMPLETE PARTS LIST

### Electronics & Compute
| Part | Qty | Est. Cost | Link/Notes |
|------|-----|-----------|------------|
| Raspberry Pi 4 (4GB) | 1 | $55 | [Adafruit](https://www.adafruit.com/product/4296) |
| MicroSD Card (64GB) | 1 | $12 | Any Class 10+ |
| PCA9685 16-Ch PWM Driver | 1 | $15 | [Adafruit #815](https://www.adafruit.com/product/815) |
| Arduino Nano (track control) | 1 | $8 | Generic clone OK |
| 8x8 LED Matrix (MAX7219) | 2 | $10 | For eyes |
| Mini Speaker (3W, 8Ω) | 1 | $5 | For voice output |
| USB Audio Adapter | 1 | $8 | For speaker connection |

### Servos & Motors
| Part | Qty | Est. Cost | Link/Notes |
|------|-----|-----------|------------|
| MG996R Servo (shoulder) | 2 | $16 | High torque (~10kg-cm) |
| SG90 Micro Servo (elbow) | 2 | $6 | Standard size |
| SG90 Micro Servo (gripper) | 2 | $6 | For claw mechanism |
| DC Geared Motor (6V, 200 RPM) | 2 | $16 | For tracks |
| L298N Motor Driver | 1 | $5 | H-bridge for DC motors |

### Power System
| Part | Qty | Est. Cost | Link/Notes |
|------|-----|-----------|------------|
| 11.1V 2200mAh LiPo Battery | 1 | $25 | 3S battery |
| XT60 Connectors | 2 | $3 | Battery connector |
| 5V 5A Buck Converter | 1 | $8 | For Pi + servos |
| Power Switch (toggle) | 1 | $3 | Main power |
| Battery Alarm (3S) | 1 | $5 | Voltage monitor |

### Mechanical Hardware
| Part | Qty | Est. Cost | Link/Notes |
|------|-----|-----------|------------|
| M3 Screws Kit (assorted) | 1 | $12 | 6-30mm lengths |
| M3 Nuts & Standoffs | 1 | $8 | Assorted |
| Servo Horns & Screws | 1 | $8 | Usually included |
| Rubber Tracks (3" wide) | 2 | $20 | Custom cut from sheet |
| Acrylic Sheets (3mm, black) | 3 | $15 | 12"x12" sheets |
| Aluminum Channel (1" sq) | 2ft | $10 | For structure |
| Zip Ties & Velcro | 1 | $8 | Cable management |

### Tools Required (You may already have)
- Soldering iron & solder
- Wire cutters/strippers
- Drill with bits (3mm, 4mm)
- Hot glue gun
- Multimeter
- Small screwdriver set

---

## 💰 COST BREAKDOWN

| Category | Subtotal |
|----------|----------|
| Electronics & Compute | $113 |
| Servos & Motors | $49 |
| Power System | $44 |
| Mechanical Hardware | $81 |
| **TOTAL** | **$287** |

**Well under $500 budget! 🔥**

---

## 🔧 ASSEMBLY INSTRUCTIONS

### Phase 1: Chassis Assembly (2-3 hours)

**Step 1: Cut Acrylic Base**
- Cut main chassis: 8" x 6" rectangle
- Cut side panels: 2x (6" x 3")
- Drill mounting holes for motors (4mm)
- Drill holes for standoffs (3mm)

**Step 2: Mount Motors**
- Attach DC motors to side panels
- Mount side panels to chassis base
- Route wires through center cutout

**Step 3: Track Installation**
- Cut rubber sheet into 2x tracks (10" long, 3" wide)
- Form loop around motor shaft & idler
- Secure with hot glue at joints

**Step 4: Electronics Mounting**
- Mount Pi on standoffs (center chassis)
- Mount Arduino next to Pi
- Mount motor driver near motors
- Mount buck converter near battery spot

---

### Phase 2: Torso & Arms (3-4 hours)

**Step 5: Torso Structure**
- Cut torso panels from aluminum channel
- Mount to chassis using L-brackets
- Create servo mounting points at shoulders

**Step 6: Shoulder Assembly**
- Mount MG996R servos at shoulder points
- Create simple arm from aluminum strip
- Add servo horn attachment point

**Step 7: Elbow & Forearm**
- Mount SG90 at elbow point
- Attach forearm section (aluminum strip)
- Mount gripper servo at wrist

**Step 8: Gripper Construction**
- Cut 2x gripper claws from acrylic
- Attach to servo horn (opens/closes)
- Add rubber pads for grip

---

### Phase 3: Head & Eyes (1-2 hours)

**Step 9: Head Box**
- Cut head panels from black acrylic (3" cube)
- Cut eye holes for LED matrices
- Mount matrices inside box
- Wire matrices to Pi (SPI)

**Step 10: Speaker Mount**
- Mount speaker in head cavity
- Wire to USB audio adapter → Pi
- Add acoustic foam for better sound

---

### Phase 4: Electronics & Wiring (2-3 hours)

**Step 11: Power Distribution**
```
LiPo Battery (11.1V)
  ├─> Buck Converter (5V, 5A)
  │     ├─> Raspberry Pi
  │     ├─> PCA9685 (servo controller)
  │     └─> LED Matrices
  └─> L298N Motor Driver (6V to motors)
```

**Step 12: Servo Wiring**
- Connect all servos to PCA9685:
  - CH0: Left shoulder
  - CH1: Left elbow  
  - CH2: Left gripper
  - CH3: Right shoulder
  - CH4: Right elbow
  - CH5: Right gripper
- PCA9685 connects to Pi via I2C

**Step 13: Motor Wiring**
- Connect DC motors to L298N
- Connect L298N control pins to Arduino
- Arduino connects to Pi via USB (serial)

**Step 14: Sensor Wiring**
- Wire LED matrices to Pi SPI
- Connect speaker via USB audio
- Add battery voltage monitor

---

### Phase 5: Software Setup (1-2 hours)

**Step 15: Raspberry Pi Setup**
```bash
# Flash Raspberry Pi OS Lite
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-rpi.gpio i2c-tools

# Install Python libraries
pip3 install adafruit-circuitpython-pca9685
pip3 install luma.led_matrix
pip3 install pyserial
pip3 install pygame  # For audio
```

**Step 16: Test Each Component**
```python
# Test servos (servo_test.py)
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
kit.servo[0].angle = 90  # Test shoulder

# Test LED eyes (eyes_test.py)
from luma.core.interface.serial import spi
from luma.led_matrix.device import max7219
device = max7219(spi(port=0, device=0))
# Display pattern

# Test motors (motor_test.py)
import serial
ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.write(b'FORWARD\n')
```

**Step 17: Main Control Software**
```python
# atlas_brain.py (simplified)
import time
from servo_control import ServoController
from motor_control import MotorController  
from eyes import EyeDisplay
from voice import VoiceOutput

class Atlas:
    def __init__(self):
        self.servos = ServoController()
        self.motors = MotorController()
        self.eyes = EyeDisplay()
        self.voice = VoiceOutput()
    
    def wave_hello(self):
        """Wave right arm"""
        self.servos.move_servo('right_shoulder', 90)
        time.sleep(0.5)
        self.servos.move_servo('right_elbow', 45)
        # Wave motion
        for i in range(3):
            self.servos.move_servo('right_shoulder', 60)
            time.sleep(0.3)
            self.servos.move_servo('right_shoulder', 120)
            time.sleep(0.3)
    
    def move_forward(self, duration=2):
        """Drive forward"""
        self.motors.forward(speed=150)
        time.sleep(duration)
        self.motors.stop()
    
    def show_emotion(self, emotion='happy'):
        """Display emotion on LED eyes"""
        patterns = {
            'happy': [[1,1,0,0,0,0,1,1], ...],
            'thinking': [[0,1,1,1,1,1,1,0], ...],
        }
        self.eyes.display_pattern(patterns[emotion])

if __name__ == '__main__':
    atlas = Atlas()
    atlas.eyes.power_on_sequence()
    atlas.voice.say("Atlas online")
    atlas.wave_hello()
```

---

## 🎯 ASSEMBLY TIPS

### Critical Measurements
- **Balance point:** Center of gravity over tracks
- **Arm reach:** 10-12 inches from shoulder
- **Gripper opening:** 2-3 inches (adjustable)
- **Ground clearance:** 0.5 inches

### Common Issues & Fixes

**Issue:** Servos jittering
- **Fix:** Add capacitors (100µF) across power rails

**Issue:** Motors drawing too much current
- **Fix:** Use separate battery for motors, or limit PWM duty cycle

**Issue:** Pi brownout/rebooting
- **Fix:** Ensure buck converter can supply 3A minimum

**Issue:** Tracks slipping
- **Fix:** Add texture to track surface (hot glue ridges)

---

## 🚀 NEXT STEPS (After Basic Build)

### Upgrades to Consider
1. **Add sensors:**
   - Ultrasonic distance sensor (HC-SR04) - $3
   - Camera module (Pi Camera V2) - $25
   - IMU for balance (MPU6050) - $5

2. **Improved arms:**
   - Add wrist rotation servo
   - Upgrade to metal gear servos
   - Add force-sensitive gripper pads

3. **Better mobility:**
   - Upgrade to brushless motors
   - Add encoders for precise movement
   - Implement PID control

4. **Software:**
   - Add voice recognition (speech-to-text)
   - Integrate with Clawdbot (remote control)
   - Computer vision for object detection
   - Autonomous navigation

5. **Aesthetics:**
   - 3D print custom parts for cleaner look
   - Add RGB LED strips for accents
   - Custom laser-cut panels
   - Atlas logo decals

---

## 📚 RESOURCES

### Tutorials & References
- [Adafruit ServoKit Guide](https://learn.adafruit.com/16-channel-pwm-servo-driver)
- [Raspberry Pi GPIO](https://pinout.xyz/)
- [Motor Control Basics](https://learn.adafruit.com/adafruit-motor-selection-guide)
- [LED Matrix Programming](https://luma-led-matrix.readthedocs.io/)

### Recommended Suppliers
- **Electronics:** Adafruit, Sparkfun, DigiKey
- **Mechanical:** Amazon, eBay (for generic parts)
- **Custom fabrication:** Send2News, Ponoko (laser cutting)

---

## ⚠️ SAFETY NOTES

1. **LiPo batteries are dangerous** - never puncture, over-discharge, or over-charge
2. **Add fuses** - 5A fuse on main power line
3. **Heat management** - Pi can get hot, consider small heatsink
4. **Moving parts** - Keep fingers away from servos/grippers during testing
5. **Voltage check** - Always verify polarity before powering on

---

## 🎉 BUILD TIMELINE

**Total estimated build time: 10-14 hours**

| Phase | Time | Difficulty |
|-------|------|------------|
| Chassis assembly | 2-3h | Easy |
| Torso & arms | 3-4h | Medium |
| Head & eyes | 1-2h | Easy |
| Electronics wiring | 2-3h | Medium |
| Software setup | 1-2h | Medium |
| Testing & debug | 1-2h | Variable |

---

**Ready to build? Order parts and let's make Atlas real! ⚡🤖**

Questions? Ping me anytime during the build process.
