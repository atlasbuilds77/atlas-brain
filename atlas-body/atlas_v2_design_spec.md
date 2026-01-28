# ATLAS V2 - Modular Humanoid Robot Design Specification

**Design Philosophy:** Build something that WORKS immediately, with upgrade path to full bipedal later

---

## DESIGN OVERVIEW

**Type:** Modular Humanoid with Tracked Base  
**Height:** 18 inches (45.7cm)  
**Weight Target:** 1.8-2.0 kg  
**DOF:** 16 degrees of freedom  
**Build Time:** 4-6 weeks  
**Estimated Cost:** $280-320  

---

## MECHANICAL SPECIFICATIONS

### Base Platform (Modular - Can Swap for Legs Later)
- **Type:** Tracked drive system
- **Motors:** 2x DC geared motors (6V, 200 RPM)
- **Tracks:** Custom 3D printed segments with rubber tread
- **Chassis:** 3D printed PLA+ (30% infill, reinforced)
- **Dimensions:** 8" long × 6" wide × 2" tall
- **Battery placement:** Low center of mass (<3" from ground)

### Torso
- **Structure:** 3D printed main body + laser-cut acrylic panels
- **Dimensions:** 4" wide × 3" deep × 6" tall
- **DOF:** 1 (waist rotation)
- **Servo:** 1x SG90 (waist yaw)
- **Features:**
  - Electronics bay (Pi + servo controller)
  - Cable routing channels
  - Modular mounting for legs (future upgrade)
  - Panel access doors

### Arms (2x - Mirror Design)
Each arm: 5 DOF
- **Shoulder:** 3 DOF
  - Pitch: MG90S (forward/backward)
  - Roll: MG90S (arm rotation)
  - Yaw: MG90S (lateral movement)
- **Elbow:** 1 DOF
  - Bend: MG90S
- **Wrist:** 1 DOF
  - Rotation: SG90

**Total per arm:** 5 servos (4x MG90S, 1x SG90)

### Hands/Grippers
- **Type:** Simple 2-finger gripper
- **DOF:** 1 per hand (open/close)
- **Servo:** SG90 per hand
- **Design:** Tendon-driven (servo in forearm, cables to fingers)
- **Grip strength:** 200-400g
- **Opening:** 0-3 inches adjustable

### Head
- **DOF:** 2 (pan/tilt)
- **Servos:** 2x SG90
- **Dimensions:** 3.5" wide × 3" deep × 2.5" tall
- **Features:**
  - LED matrix eyes (2x 8x8 MAX7219)
  - Camera mount (Pi Camera V2)
  - Speaker cavity (3W 8Ω)
  - Antenna/sensor mount

---

## ELECTRONIC SPECIFICATIONS

### Control System
- **Main Controller:** Arduino Mega 2560
  - 54 digital I/O pins
  - 16 analog inputs
  - 256KB flash memory
  - Cost: ~$35

- **Servo Controller:** Adafruit 16-Channel PWM Shield
  - Controls all 16 servos
  - I2C interface to Mega
  - Separate power input
  - Cost: ~$20

- **Optional AI:** Raspberry Pi Zero 2W
  - Computer vision
  - Voice processing
  - WiFi control
  - Cost: ~$20 (optional)

### Power System
- **Battery:** 3S LiPo 2200mAh (11.1V)
  - Voltage: 11.1V nominal, 12.6V full, 9.0V cutoff
  - Capacity: 2200mAh (~30-45 min runtime)
  - Weight: ~180g
  - Cost: ~$25

- **Power Distribution:**
  - Buck converter 1: 11.1V → 7.4V @ 5A (servos)
  - Buck converter 2: 11.1V → 5V @ 3A (logic)
  - Capacitors: 1000µF per servo cluster
  - Cost: ~$15

- **Monitoring:**
  - Battery voltage sensor
  - Low voltage alarm
  - Software cutoff at 9.5V

### Sensors
**Minimum (Phase 1):**
- MPU-6050 IMU (orientation, tilt detection) - $5
- 2x IR distance sensors (obstacle avoidance) - $6

**Optional (Phase 2):**
- Raspberry Pi Camera V2 (computer vision) - $25
- Force sensors in feet (balance feedback) - $15
- Microphone (voice commands) - $10

### Display/Output
- **Eyes:** 2x 8x8 LED Matrix (MAX7219)
  - Animated expressions
  - Status indicators
  - Cost: ~$10

- **Speaker:** 3W 8Ω Mini Speaker
  - Voice output (TTS)
  - Sound effects
  - Cost: ~$5

- **USB Audio:** USB sound card for speaker
  - Cost: ~$8

---

## SERVO SPECIFICATIONS & PLACEMENT

### MG90S Servos (10x) - Arms
- **Type:** Metal gear digital micro servo
- **Torque:** 1.8-2.2 kg·cm @ 6V
- **Speed:** 0.1 sec/60° @ 6V
- **Weight:** 13.4g
- **Angle:** 180° (0-180)
- **Cost:** $4-6 each ($40-60 total)
- **Mounting:** Custom 3D printed servo brackets
- **Usage:**
  - 6x shoulder joints (3 per arm)
  - 2x elbow joints
  - 2x wrist rotation

### SG90 Servos (6x) - Head/Waist/Grippers
- **Type:** Plastic gear micro servo
- **Torque:** 1.2-1.8 kg·cm @ 6V
- **Speed:** 0.1 sec/60° @ 6V
- **Weight:** 9g
- **Angle:** 180° (0-180)
- **Cost:** $2-3 each ($12-18 total)
- **Usage:**
  - 2x head pan/tilt
  - 1x waist rotation
  - 2x gripper actuators
  - 1x spare

### DC Motors (2x) - Tracks
- **Type:** 6V 200 RPM geared motor
- **Torque:** 1.5 kg·cm
- **Current:** 150mA no-load, 800mA stall
- **Encoder:** Optional (for odometry)
- **Cost:** $8 each ($16 total)
- **Driver:** L298N H-bridge motor controller ($5)

---

## 3D PRINTED PARTS LIST

All parts designed for PLA+ filament, 0.2mm layer height, 30% infill

### Structural Components
1. **Chassis base** (200mm × 150mm × 40mm)
2. **Torso front panel** (100mm × 80mm)
3. **Torso back panel** (100mm × 80mm)
4. **Torso side panels** (2x, 80mm × 60mm)
5. **Head shell** (2 pieces - front/back)
6. **Track segments** (40x, 20mm × 15mm each)
7. **Track wheels** (4x, 30mm diameter)

### Joint Components
8. **Shoulder joint assembly** (2x, 3 pieces each)
9. **Elbow joint brackets** (2x)
10. **Wrist joint housings** (2x)
11. **Hip joint mount** (torso to base connection)
12. **Waist rotation mount**

### Servo Brackets
13. **MG90S servo bracket** (10x)
14. **SG90 servo bracket** (6x)
15. **Motor mounts** (2x)

### Hand/Gripper Components
16. **Gripper finger** (4x, 2 per hand)
17. **Gripper palm** (2x)
18. **Tendon pulley** (4x, for finger actuation)

### Electronics Housing
19. **Arduino Mega case** (2 pieces)
20. **PWM shield mount**
21. **Battery tray** (with straps)
22. **Buck converter mounts** (2x)
23. **Cable management clips** (10x)

### Aesthetic Details
24. **Head antenna**
25. **Torso vent grilles** (4x)
26. **Panel line accents**
27. **Eye surrounds** (2x)

**Total Print Time:** ~50-80 hours  
**Filament Required:** ~800g PLA+ ($25)

---

## LASER CUT PARTS (Optional - Reinforcement)

**Material:** 3mm Black Acrylic

1. **Chassis bottom plate** (200mm × 150mm)
2. **Torso reinforcement ribs** (4x, 80mm × 40mm)
3. **Shoulder mounting plates** (2x, 50mm × 50mm)

**Total Cost:** ~$30 (or substitute with thicker 3D prints)

---

## BILL OF MATERIALS

### Electronics
| Component | Qty | Unit Cost | Total |
|-----------|-----|-----------|-------|
| Arduino Mega 2560 | 1 | $35 | $35 |
| 16-Ch PWM Shield | 1 | $20 | $20 |
| MPU-6050 IMU | 1 | $5 | $5 |
| 8x8 LED Matrix (MAX7219) | 2 | $5 | $10 |
| 3W Speaker | 1 | $5 | $5 |
| USB Audio Adapter | 1 | $8 | $8 |
| IR Distance Sensors | 2 | $3 | $6 |
| 3S LiPo 2200mAh | 1 | $25 | $25 |
| Buck Converters | 2 | $7.50 | $15 |
| L298N Motor Driver | 1 | $5 | $5 |
| Wiring/Connectors | 1 | $15 | $15 |
| **Electronics Subtotal** | | | **$149** |

### Servos & Motors
| Component | Qty | Unit Cost | Total |
|-----------|-----|-----------|-------|
| MG90S Servos | 10 | $5 | $50 |
| SG90 Servos | 6 | $2.50 | $15 |
| DC Geared Motors | 2 | $8 | $16 |
| **Servo/Motor Subtotal** | | | **$81** |

### Structural
| Component | Qty | Unit Cost | Total |
|-----------|-----|-----------|-------|
| PLA+ Filament (1kg) | 1 | $25 | $25 |
| Acrylic Sheets (optional) | 1 | $30 | $30 |
| M3 Screws Kit | 1 | $12 | $12 |
| M3 Nuts/Standoffs | 1 | $8 | $8 |
| Bearings (608ZZ) | 4 | $1 | $4 |
| Rubber Sheet (tracks) | 1 | $10 | $10 |
| **Structural Subtotal** | | | **$89** |

### **TOTAL COST: $319** (with acrylic)  
### **TOTAL COST: $289** (without acrylic - 3D print instead)

---

## SOFTWARE ARCHITECTURE

### Arduino Mega (Primary Controller)
- **Language:** C++
- **Framework:** Arduino IDE
- **Frequency:** 16 MHz
- **Responsibilities:**
  - Real-time servo control (16 channels via PWM shield)
  - Motor control (L298N H-bridge)
  - Sensor reading (IMU, IR sensors)
  - LED matrix display
  - Serial communication with Pi (optional)

### Control Modes
1. **Manual Control**
   - Bluetooth/WiFi remote
   - Individual servo positioning
   - Preset poses

2. **Autonomous**
   - Obstacle avoidance (IR sensors)
   - Simple walking sequences
   - Head tracking

3. **AI-Assisted** (with Raspberry Pi)
   - Computer vision
   - Voice commands
   - Advanced behaviors

### Inverse Kinematics (IK)
- **Library:** Custom IK solver or SimplIK
- **Implementation:** 5-DOF arm IK
- **Purpose:** Natural arm movements to target positions

---

## ASSEMBLY SEQUENCE

### Phase 1: Base & Chassis (Week 1)
1. Print chassis components
2. Assemble track system
3. Mount motors and motor controller
4. Test basic mobility

### Phase 2: Electronics Integration (Week 2)
5. Install Arduino Mega + PWM shield
6. Mount buck converters
7. Wire power distribution
8. Install battery tray
9. Test power system

### Phase 3: Torso & Waist (Week 3)
10. Print torso components
11. Install waist servo
12. Mount electronics in torso
13. Connect torso to base
14. Test waist rotation

### Phase 4: Arms (Week 4-5)
15. Print arm components (2 sets)
16. Assemble shoulder joints (3 DOF per side)
17. Install elbow servos
18. Add wrist rotation
19. Build grippers with tendon system
20. Test arm movement & IK

### Phase 5: Head (Week 5)
21. Print head components
22. Install LED matrices
23. Mount pan/tilt servos
24. Add speaker
25. Test expressions & head movement

### Phase 6: Integration & Testing (Week 6)
26. Final assembly
27. Cable management
28. Software integration
29. Calibration
30. Full system testing

---

## UPGRADE PATH TO BIPEDAL (Phase 2 - Future)

### What Changes
- **Remove:** Tracked base, DC motors
- **Add:** 
  - 2x legs (6 DOF each = 12 servos total)
  - Force sensors in feet (8x FSR)
  - Upgraded IMU (MPU-9250)
  - Balance control algorithms

### Additional Cost
- 12x MG996R servos (legs) - $96-120
- Force sensors - $40
- Upgraded IMU - $15
- Foot structures (3D printed) - included
- **Total Upgrade Cost:** ~$150-180

### Why Modular Design Works
- Upper body stays identical
- Torso has mounting points for legs already designed
- Electronics can handle additional servos
- Software architecture supports leg control
- No wasted components (base can be reused for other projects)

---

## DESIGN ADVANTAGES

✅ **Works immediately** (no months debugging balance)  
✅ **Under $300 budget** ($289 without optional acrylic)  
✅ **Proven technology** (tracked base is stable)  
✅ **Full humanoid appearance** (upper body is what people see)  
✅ **Real functionality** (can manipulate objects, track faces)  
✅ **Upgrade path** (swap to bipedal legs when ready)  
✅ **3D printable** (all custom parts)  
✅ **Standard servos** (easy to source)  
✅ **Reasonable build time** (4-6 weeks)  
✅ **Educational** (learn kinematics, electronics, programming)  

---

## NEXT STEPS

1. ✅ Research complete
2. ✅ Design specification documented
3. ⏳ **CREATE 3D MODEL** (Blender with proper joint mechanisms)
4. ⏳ Generate STL files for printing
5. ⏳ Write Arduino control code
6. ⏳ Create assembly instructions
7. ⏳ Order parts
8. ⏳ Build!

---

**This is Atlas V2. Let's build it.** 🤖⚡
