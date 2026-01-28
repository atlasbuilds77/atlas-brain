# Bipedal Locomotion & Balance Research for Desktop-Scale Humanoid Robots

## Executive Summary

This research examines the feasibility and requirements for implementing bipedal locomotion in an 18" (45cm) desktop-scale humanoid robot. The analysis covers key balance principles, sensor requirements, mechanical design considerations, and provides a decision framework for choosing between bipedal vs. wheeled/tracked locomotion.

## Core Balance Principles

### 1. Zero Moment Point (ZMP) Stability
- **Definition**: ZMP is the point on the ground where the sum of all moments equals zero
- **Key Insight**: For static stability, the robot's Center of Mass (CoM) must project within the support polygon (foot area)
- **Desktop Scale Challenge**: Small foot area relative to height increases balance difficulty
- **Practical Approach**: Use ZMP-based control with large enough feet for simplified balancing

### 2. Center of Mass (CoM) Control
- **Critical Factor**: Lower CoM improves stability significantly
- **Design Strategy**: Place heavy components (batteries, motors) as low as possible
- **Desktop Scale**: For 18" robot, aim for CoM below 30% of total height (≈5.4" from ground)

### 3. Foot Design Principles
- **Size Ratio**: Foot length should be 15-20% of body height
  - For 18" robot: 2.7-3.6" foot length
  - Foot width: 40-50% of foot length (1.1-1.8")
- **Sensor Integration**: Force-sensitive resistors (FSRs) or pressure sensors for ground contact detection
- **Ankle Compliance**: Flexible ankles or spring mechanisms help absorb shocks
- **Surface Area**: Larger feet simplify balance but reduce agility

## Minimum Sensor Requirements

### Essential Sensors for Balance:
1. **IMU (Inertial Measurement Unit)**
   - 6-DOF minimum (3-axis accelerometer + 3-axis gyroscope)
   - Recommended: MPU-6050 or MPU-9250
   - Sampling rate: ≥100Hz for real-time control
   - Key specifications:
     - Accelerometer range: ±8g
     - Gyroscope range: ±2000°/s
     - Communication: I2C or SPI

2. **Foot Contact Sensors**
   - Force-sensitive resistors (FSRs) at 4 corners of each foot
   - Alternative: Pressure sensor arrays
   - Purpose: Detect ground contact and weight distribution

3. **Joint Position Sensors**
   - Potentiometers or rotary encoders on each joint
   - Required for closed-loop servo control
   - Resolution: 10-12 bit minimum

### Optional Advanced Sensors:
- Magnetometer (for absolute orientation)
- Ultrasonic/rangefinder (for obstacle detection)
- Camera (for visual feedback)

## Servo Torque Requirements

### Standing Torque Calculation:
```
Torque = (Weight × Height to CoM × sin(θ)) / Number of supporting legs
```
Where:
- θ = maximum expected tilt angle (typically 10-15°)
- For 18" robot with 2kg weight and CoM at 5":
  - Standing torque per leg: ~0.43 Nm (≈4.4 kg·cm)

### Walking Torque Requirements:
- **Hip joints**: 2-3× standing torque for dynamic motion
- **Knee joints**: 1.5-2× standing torque
- **Ankle joints**: Highest torque requirements (3-4× standing) for push-off

### Recommended Servo Specifications:
- **Hip**: 12-15 kg·cm continuous torque
- **Knee**: 8-12 kg·cm continuous torque  
- **Ankle**: 15-20 kg·cm continuous torque
- **Speed**: 0.1-0.2 sec/60° for responsive control

## Mechanical Design Guidelines

### Joint Configuration (Minimum):
- **Hip**: 3 DOF (roll, pitch, yaw)
- **Knee**: 1 DOF (pitch)
- **Ankle**: 2 DOF (roll, pitch)
- **Total per leg**: 6 DOF
- **Full robot**: 12 DOF minimum

### Weight Distribution:
- **Battery placement**: In pelvis or lower torso
- **Motor placement**: As close to joints as possible to reduce moving mass
- **Electronics**: Centralized in torso for easy access
- **Target weight**: 1.5-2.5kg for 18" height

### Structural Considerations:
- **Material**: Carbon fiber, aluminum, or high-strength plastics
- **Stiffness**: Sufficient to prevent flexing under load
- **Weight-to-strength ratio**: Critical for dynamic performance

## Simple Balance Algorithms

### 1. PID Controller for Standing Balance:
```
Error = Current_angle - Desired_angle (typically 0°)
Output = Kp × Error + Ki × ∫Error dt + Kd × d(Error)/dt
```
- **Typical values for small robot**:
  - Kp: 15-30 (proportional)
  - Ki: 0.001-0.1 (integral)  
  - Kd: 0.5-2.0 (derivative)

### 2. State Machine Approach:
1. **Initialization**: Calibrate sensors, stand up sequence
2. **Balancing**: PID control on ankle/hip joints
3. **Step Planning**: Pre-calculated trajectories for walking
4. **Recovery**: Fall detection and recovery routines

### 3. Simplified ZMP Implementation:
- Calculate CoM position from joint angles
- Project CoM to ground plane
- Adjust foot placement to keep projection within support polygon
- Use inverted pendulum model for dynamic walking

### 4. Capture Point Method:
- Based on Linear Inverted Pendulum (LIP) model
- Predicts future CoM position
- Determines optimal foot placement for stability

## Battery & Power Management

### Power Requirements:
- **Standing**: 2-4W continuous
- **Walking**: 8-15W peak
- **Processing**: 1-3W for microcontroller/computer

### Battery Specifications:
- **Chemistry**: LiPo or Li-ion for high power density
- **Capacity**: 1000-2000mAh for 30-60 minutes operation
- **Voltage**: 7.4V (2S) or 11.1V (3S) for servo power
- **Placement**: Low in torso/pelvis for CoM control

### Power Distribution:
- Separate power rails for motors and electronics
- Voltage regulation for sensitive components
- Current monitoring for overload protection

## Bipedal vs. Wheeled/Tracked Decision Framework

### When to Choose BIPEDAL:

**Advantages:**
1. **Terrain adaptability**: Steps over obstacles, climbs stairs
2. **Human-like motion**: Better for human-robot interaction
3. **Compact footprint**: Can stand in small spaces
4. **Dexterous manipulation**: Free hands for tasks while standing

**Ideal Use Cases:**
- Research and education platforms
- Human-robot interaction studies
- Uneven terrain navigation
- Demonstration/showcase projects

**Requirements for Success:**
- Advanced control algorithms
- High-quality sensors
- Powerful computation
- Robust mechanical design
- Willingness to handle complexity

### When to Choose WHEELED/TRACKED:

**Advantages:**
1. **Simplicity**: Much easier to implement and control
2. **Stability**: Inherently stable on flat surfaces
3. **Energy efficiency**: Lower power consumption
4. **Speed**: Faster movement on smooth surfaces
5. **Cost**: Lower component and development costs

**Ideal Use Cases:**
- Indoor navigation on flat surfaces
- Object transportation
- Basic telepresence
- Educational projects with limited budget
- Rapid prototyping

**Hybrid Approach Consideration:**
- Wheeled feet or retractable wheels
- Best of both worlds but adds complexity
- Example: Boston Dynamics' Handle robot

### Decision Matrix for 18" Desktop Robot:

| Factor | Bipedal | Wheeled/Tracked | Notes |
|--------|---------|-----------------|-------|
| **Development Time** | 6-12 months | 1-3 months | Bipedal requires extensive tuning |
| **Cost** | $500-$2000 | $100-$500 | Bipedal needs better components |
| **Stability** | Challenging | Excellent | Bipedal requires active balancing |
| **Terrain** | Versatile | Limited to smooth | Bipedal handles obstacles better |
| **Power Use** | High | Low | Bipedal uses more energy |
| **Control Complexity** | High | Low | Bipedal needs advanced algorithms |
| **Educational Value** | Excellent | Good | Both teach different skills |
| **Showcase Potential** | High | Moderate | Bipedal is more impressive |

## Implementation Roadmap for Bipedal Approach

### Phase 1: Foundation (Weeks 1-4)
1. **Research and planning**
2. **Component selection and procurement**
3. **Basic mechanical design**
4. **Sensor testing and calibration**

### Phase 2: Standing Balance (Weeks 5-8)
1. **Build leg assemblies**
2. **Implement sensor fusion (IMU data)**
3. **Develop PID balance controller**
4. **Test standing stability**

### Phase 3: Static Walking (Weeks 9-12)
1. **Implement gait pattern generator**
2. **Add foot contact sensing**
3. **Develop simple ZMP controller**
4. **Test slow, controlled walking**

### Phase 4: Dynamic Walking (Weeks 13-16)
1. **Implement capture point method**
2. **Add disturbance rejection**
3. **Optimize energy efficiency**
4. **Test on uneven surfaces**

### Phase 5: Refinement (Weeks 17-20)
1. **Fall recovery routines**
2. **Energy optimization**
3. **User interface development**
4. **Documentation and testing**

## Critical Success Factors

### 1. Mechanical Design:
- Low center of mass
- Sufficient joint torque and speed
- Robust construction
- Proper weight distribution

### 2. Sensor Quality:
- High-quality IMU with good calibration
- Reliable joint position sensors
- Accurate force sensing
- Sufficient sampling rates

### 3. Control Algorithms:
- Well-tuned PID controllers
- Proper sensor fusion
- Robust state estimation
- Effective gait generation

### 4. Testing Methodology:
- Incremental development
- Comprehensive logging
- Systematic parameter tuning
- Safety precautions

## Recommended Components for 18" Bipedal Robot

### Electronics:
- **Controller**: Arduino Due, Teensy 4.0, or Raspberry Pi Pico
- **IMU**: MPU-6050 or MPU-9250
- **Servos**: Dynamixel AX-12A or MX-28 (or equivalent digital servos)
- **Battery**: 3S LiPo 2200mAh
- **Sensors**: FSRs for foot pressure, rotary encoders for joints

### Software Stack:
- **Firmware**: Arduino/C++ for real-time control
- **Sensor Fusion**: Madgwick or Mahony filter
- **Control**: Custom PID implementation
- **Gait Generation**: Pre-calculated trajectories or online planning
- **Communication**: Serial protocol for debugging and monitoring

## Conclusion

For an 18" desktop-scale robot, the decision between bipedal and wheeled locomotion depends primarily on project goals:

- **Choose bipedal** if: The goal is research, education about balance and locomotion, human-robot interaction, or demonstrating advanced capabilities. Be prepared for significant complexity and development time.

- **Choose wheeled/tracked** if: The goal is reliable operation, simplicity, cost-effectiveness, or focusing on other aspects like navigation or manipulation. This provides a more achievable success path.

If pursuing bipedal locomotion, start with a strong foundation in mechanical design (low CoM, sufficient torque), invest in quality sensors (especially IMU), and implement control algorithms incrementally. The recommended approach is to master standing balance before attempting walking, and to use simplified models (inverted pendulum, ZMP) before moving to more complex control strategies.

The 18" scale presents both challenges (higher center of mass relative to foot size) and opportunities (lower weight, smaller forces). With careful design and systematic development, a functional bipedal desktop robot is achievable for dedicated teams.