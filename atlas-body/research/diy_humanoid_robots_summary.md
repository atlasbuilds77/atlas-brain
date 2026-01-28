# DIY Humanoid Robotics Research Summary

## Overview
This document summarizes research on DIY humanoid robot projects, focusing on buildable designs under $500, practical components, and assembly considerations for desktop-scale (12-24") humanoids.

## Focus Projects Analysis

### 1. InMoov - Open Source 3D Printed Humanoid
**Key Characteristics:**
- Life-size humanoid robot (adult human scale)
- Fully 3D printable on standard 12x12x12cm printers
- Open source under Creative Commons (CC-BY-NC) license
- Designed as development platform for makers, universities, hobbyists

**Bill of Materials (Estimated):**
- **Servos:** 20-30 standard hobby servos (MG996R/MG90S type)
- **Controllers:** Arduino Mega or multiple Arduino Nanos with servo shields
- **Sensors:** Optional cameras, ultrasonic, IMU
- **Power:** 12V battery pack with voltage regulators
- **Structural:** 100% 3D printed parts (PLA/ABS/PETG)
- **Electronics:** Motor drivers, power distribution boards

**Cost Breakdown:**
- Servos (20x MG996R): $100-$200 ($5-$10 each)
- Electronics (Arduino, shields): $50-$100
- 3D printing material: $50-$100 (2-3kg filament)
- Hardware (screws, bearings): $20-$50
- Battery/power: $30-$50
- **Total Estimated Cost:** $250-$500 (life-size)

**Assembly Complexity:**
- **Build Time:** 100-200 hours (printing + assembly)
- **Skill Level:** Intermediate to Advanced
- **Tools Required:** 3D printer, basic electronics tools, screwdrivers

**Common Failure Points:**
- Servo gear stripping under load
- Power supply insufficient for multiple servos
- 3D printed joint wear over time
- Wiring complexity leading to connection issues

### 2. Poppy Project - Modular Humanoid Platform
**Key Characteristics:**
- Research/education focused platform
- Uses Robotis Dynamixel actuators (MX-28, MX-64, AX-12)
- Modular design with interchangeable parts
- Professional-grade but expensive

**Bill of Materials:**
- **Actuators:** 25x Dynamixel servos (8x MX28, 3x MX64, etc.)
- **Controller:** Raspberry Pi 3/4 with USB2AX interface
- **Power:** Multiple 12V power supplies with SMPS2Dynamixel
- **Structural:** Mix of 3D printed and machined parts

**Cost Breakdown:**
- Dynamixel servos: $4,000-$6,000 (60-70% of total cost)
- Electronics: $500-$1,000
- 3D printing: $100-$200
- **Total Cost:** $8,000-$9,000 (not budget-friendly)

**Practical Notes:**
- Too expensive for <$500 budget
- Professional actuators not suitable for budget builds
- Good reference for modular design principles

### 3. OpenBot - Smartphone-Powered Robots
**Key Characteristics:**
- Uses Android smartphone as "brain"
- Arduino Nano for low-level motor control
- Extremely low cost ($50 estimate)
- Originally designed for wheeled robots but adaptable

**Bill of Materials:**
- **Controller:** Arduino Nano ($5-$10)
- **Smartphone:** Existing Android device (no cost)
- **Motors:** 4x DC gear motors with wheels
- **Motor Driver:** L298N or similar ($5)
- **Chassis:** 3D printed or laser cut ($5)
- **Battery:** 7.4V LiPo ($15)

**Cost Breakdown:**
- Electronics: $15-$25
- Mechanical parts: $10-$20
- Battery: $10-$20
- **Total Cost:** $35-$65

**Adaptation to Humanoid:**
- Could use smartphone for vision/processing
- Arduino controls servo motors instead of DC motors
- Would need additional servo controllers
- **Estimated Humanoid Adaptation Cost:** $150-$300

### 4. Jimmy Robot / Desktop Humanoids
**Note:** "Jimmy Robot" search didn't yield specific results, but several desktop-scale projects exist:

**Common Desktop Humanoid Characteristics:**
- Height: 12-24 inches (30-60cm)
- DOF: 12-20 degrees of freedom
- Weight: 1-3kg
- Typical uses: Education, hobby, research

**Example Project: ALANA (Under $70)**
- Life-size but demonstrates cost principles
- Uses modified windshield wiper motors
- Custom servo controllers
- 3D printed structure
- Shows extreme cost optimization is possible

### 5. MARK Humanoid Robot Kit
**Note:** Specific "MARK" kit not found, but similar kits exist:

**Rapiro-like Kits ($200-$400 range):**
- 12 servo motors included
- Arduino-compatible main board
- Designed for Raspberry Pi
- Pre-designed movements
- Good for beginners

**Common Kit Features:**
- Pre-cut acrylic/laser cut parts
- Pre-assembled electronics
- Detailed instructions
- Limited customization

### 6. Arduino/Raspberry Pi Humanoid Projects
**Most Practical for <$500 Budget:**

**Typical Specifications:**
- **Height:** 12-18 inches optimal for desktop
- **DOF:** 16-20 (8 per leg, 2-4 per arm, 2 for head)
- **Servos:** MG996R or MG90S (torque vs size trade-off)
- **Controller:** Arduino Mega (54 I/O pins) or multiple Nanos
- **Power:** 7.4V-12V LiPo with voltage regulators
- **Sensors:** Optional IMU, ultrasonic, camera

## Cost-Effective Design Patterns

### 1. Servo Motor Selection Strategy
**Budget Servo Options:**
- **MG996R:** ~$8-10 each, 10-15kg·cm torque, metal gears
- **MG90S:** ~$4-6 each, 1.8-2.2kg·cm torque, metal gears
- **SG90:** ~$2-3 each, 1.2-1.8kg·cm torque, plastic gears

**Recommendation for 16-DOF Humanoid:**
- **Legs (8x):** MG996R for weight support ($80)
- **Arms (4x):** MG90S for lighter duty ($20)
- **Head/waist (4x):** SG90 for minimal load ($12)
- **Total Servo Cost:** ~$112

### 2. Control System Architecture
**Option A: Centralized (Simpler)**
- Arduino Mega + 16-channel PWM servo shield
- Single point of control
- Limited by Arduino processing power
- **Cost:** $40-$60

**Option B: Distributed (More Robust)**
- Multiple Arduino Nanos (one per limb)
- I2C communication between controllers
- Better load distribution
- **Cost:** $50-$80

**Option C: Hybrid**
- Raspberry Pi for high-level processing
- Arduino for real-time servo control
- Serial or I2C communication
- **Cost:** $70-$100

### 3. Power System Design
**Critical Considerations:**
- Peak current draw: 16 servos × 1A = 16A peak
- Continuous current: 16 servos × 0.3A = 4.8A average
- Voltage: 6V for SG90, 7.4V for MG90S, 7.4-8.4V for MG996R

**Recommended Setup:**
- **Battery:** 3S LiPo (11.1V) 2200-3000mAh ($25)
- **Voltage Regulators:**
  - 5V buck converter for logic/Arduino ($5)
  - Adjustable buck converter for servos (set to 7.4V) ($8)
- **Power Distribution:** Custom PCB or terminal blocks ($10)
- **Total Power System Cost:** ~$48

### 4. Structural Design Approaches
**Option 1: 100% 3D Printed**
- **Pros:** Maximum customization, no special tools
- **Cons:** Print time (50-100 hours), material cost ($30-$50)
- **Strength:** Moderate, depends on infill/orientation

**Option 2: Laser Cut Acrylic/Wood**
- **Pros:** Fast production, consistent quality
- **Cons:** Requires laser cutter access, less 3D complexity
- **Cost:** $20-$40 for materials

**Option 3: Hybrid Approach**
- 3D printed joints/brackets
- Aluminum/acrylic structural members
- Best strength-to-weight ratio
- **Cost:** $40-$60

## Realistic <$500 Build Plan

### Target Specifications:
- **Height:** 18 inches (45cm)
- **Weight:** 1.5-2kg
- **DOF:** 16 (8 legs, 4 arms, 2 waist, 2 head)
- **Capabilities:** Walking, basic gestures, object tracking

### Detailed Cost Breakdown:

**1. Actuation System ($150)**
- 8x MG996R servos (legs): $80
- 4x MG90S servos (arms): $24
- 4x SG90 servos (head/waist): $12
- Servo horns/extensions: $15
- Screws/hardware: $19

**2. Control System ($80)**
- Arduino Mega 2560: $35
- 16-channel PWM servo shield: $20
- Raspberry Pi Zero 2W (optional): $20
- Cables/connectors: $5

**3. Power System ($60)**
- 3S 2200mAh LiPo battery: $25
- Dual voltage buck converters: $15
- Battery charger: $15
- Power switch/wiring: $5

**4. Structural System ($70)**
- 3D printing filament (1kg PLA+): $25
- Laser cut acrylic sheets: $30
- Bearings/bushings: $10
- Adhesives/fasteners: $5

**5. Sensors (Optional, $40)**
- MPU6050 IMU: $5
- HC-SR04 ultrasonic: $3
- Raspberry Pi Camera V2: $25
- Miscellaneous sensors: $7

**6. Tools/Consumables ($40)**
- Basic electronics toolkit: $20
- 3D printer maintenance: $10
- Soldering supplies: $10

**Total Estimated Cost: $440**
*(With contingency: $500)*

## Assembly Complexity & Timeline

### Phase 1: Design & Planning (1-2 weeks)
- CAD modeling of parts
- Circuit design
- Bill of materials finalization
- Ordering components

### Phase 2: Fabrication (2-3 weeks)
- 3D printing structural parts: 50-80 hours
- Laser cutting (if applicable): 2-4 hours
- PCB fabrication (optional): 1 week

### Phase 3: Electronics Assembly (1 week)
- Soldering connections
- Testing individual components
- Power system verification

### Phase 4: Mechanical Assembly (1-2 weeks)
- Servo mounting and alignment
- Structural assembly
- Cable management

### Phase 5: Programming & Testing (2-3 weeks)
- Basic servo control
- Gait development
- Sensor integration
- Iterative testing and refinement

**Total Realistic Build Time: 6-10 weeks**
*(Assuming 10-15 hours per week)*

## Common Failure Points & Mitigation

### 1. Servo Motor Issues
**Problem:** Gear stripping, overheating, jitter
**Solutions:**
- Use metal-gear servos for load-bearing joints
- Add heat sinks to servos
- Implement current limiting in software
- Use separate power supplies for different limb groups

### 2. Power System Problems
**Problem:** Brownouts, voltage drops, insufficient current
**Solutions:**
- Overspecify battery capacity by 30-50%
- Use large capacitors near servo clusters
- Implement soft-start for servo initialization
- Monitor battery voltage in software

### 3. Structural Weaknesses
**Problem:** Joint failure, flexing, vibration
**Solutions:**
- Design with generous fillets and ribs
- Use higher infill percentages (30-40%) for load-bearing parts
- Consider hybrid metal/plastic joints
- Implement mechanical limits to prevent over-rotation

### 4. Control System Limitations
**Problem:** Latency, jitter, communication errors
**Solutions:**
- Use hardware PWM where possible
- Implement watchdog timers
- Add error checking in communication protocols
- Consider real-time operating system for complex gaits

### 5. Balance & Gait Issues
**Problem:** Falling, unstable walking, energy inefficiency
**Solutions:**
- Start with static poses, then slow movements
- Implement IMU feedback for balance
- Use reinforcement learning for gait optimization
- Add mechanical compliance (springs/dampers)

## Practical Building Tips

### 1. Start Simple
- Begin with 2-4 DOF leg segments
- Master basic servo control before full assembly
- Test each joint individually

### 2. Modular Design
- Design limbs as separate modules
- Use standardized connectors
- Allow for easy replacement of components

### 3. Documentation
- Photograph each assembly step
- Label all cables and connectors
- Keep detailed notes on calibration values

### 4. Testing Protocol
- Power test without servos connected
- Test each servo individually
- Test limb groups before full assembly
- Implement gradual load increase

### 5. Safety Considerations
- Always disconnect power when making changes
- Use fuses or polyfuses in power lines
- Implement emergency stop functionality
- Wear eye protection during testing

## Recommended Resources & Next Steps

### Open Source Projects to Study:
1. **InMoov** - Comprehensive life-size reference
2. **RoboPrime** - 21 DOF under $100 design
3. **ALANA** - Extreme cost optimization example
4. **YouMakeRobots** - Modular kit design

### Learning Path:
1. **Beginner:** Assemble a pre-designed kit (Rapiro-like)
2. **Intermediate:** Modify existing designs, add sensors
3. **Advanced:** Design from scratch, implement custom gaits

### Tools to Master:
- **CAD:** Fusion 360 (free for hobbyists)
- **Electronics:** KiCAD for PCB design
- **Programming:** Arduino IDE, Python for Raspberry Pi
- **Simulation:** Webots, Gazebo (for advanced users)

## Conclusion

Building a functional desktop humanoid robot under $500 is achievable with careful planning and component selection. The key is to balance performance with cost, focusing on:

1. **Strategic servo selection** - Mix high-torque and standard servos
2. **Efficient power design** - Proper current capacity and regulation
3. **Smart structural design** - Hybrid materials for strength/weight balance
4. **Modular architecture** - For easier debugging and upgrades

The most realistic approach starts with a 12-16 DOF design using MG996R servos for legs, MG90S for arms, and SG90 for head/waist, controlled by an Arduino Mega with PWM shield. Total build time of 6-10 weeks is realistic for someone dedicating 10-15 hours per week.

Remember: The first build will have challenges—view it as a learning platform. Document everything, test incrementally, and don't hesitate to iterate on the design based on what you learn.