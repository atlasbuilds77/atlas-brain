# Bipedal vs. Wheeled/Tracked Decision Framework for 18" Desktop Robot

## Quick Decision Guide

### Choose BIPEDAL if:
- ✅ Research/education focus on locomotion & balance
- ✅ Need to navigate uneven terrain or stairs
- ✅ Human-like interaction is important
- ✅ Demonstrating advanced capabilities
- ✅ Willing to invest 6+ months development
- ✅ Budget allows for quality components ($500-$2000)

### Choose WHEELED/TRACKED if:
- ✅ Need reliable, stable operation quickly
- ✅ Operating primarily on flat surfaces
- ✅ Simplicity and lower cost are priorities
- ✅ Focus is on other capabilities (navigation, manipulation)
- ✅ Limited development time (1-3 months)
- ✅ Budget constrained ($100-$500)

## Detailed Comparison Table

| Aspect | Bipedal | Wheeled/Tracked | Winner |
|--------|---------|-----------------|--------|
| **Development Time** | 6-12 months | 1-3 months | Wheeled |
| **Cost** | $500-$2000+ | $100-$500 | Wheeled |
| **Stability** | Active control required | Inherently stable | Wheeled |
| **Terrain Adaptability** | Excellent (stairs, obstacles) | Poor (smooth surfaces only) | Bipedal |
| **Power Efficiency** | Low (high energy use) | High (efficient movement) | Wheeled |
| **Control Complexity** | Very High (advanced algorithms) | Low (simple motor control) | Wheeled |
| **Educational Value** | Excellent (complex systems) | Good (robotics fundamentals) | Bipedal |
| **Showcase/Impression** | Very High (impressive) | Moderate (common) | Bipedal |
| **Failure Rate** | High during development | Low with proper design | Wheeled |
| **Maintenance** | High (many moving parts) | Low (simple mechanics) | Wheeled |

## Bipedal Implementation Requirements (If Chosen)

### Minimum Hardware Requirements:

#### Sensors ($100-$200):
- **IMU**: MPU-6050 or MPU-9250 (6-DOF minimum) - $10-$20
- **Foot Sensors**: 4x FSRs per foot (8 total) - $40-$80
- **Joint Sensors**: Potentiometers or encoders on all 12+ joints - $50-$100

#### Actuators ($300-$1000):
- **Servos**: 12-20 DOF required
  - Minimum: 12x digital servos with 10-15 kg·cm torque
  - Recommended: Dynamixel AX/MX series or equivalent
  - Cost: $25-$80 per servo

#### Structure ($100-$300):
- **Materials**: Carbon fiber, aluminum, or reinforced plastics
- **Fasteners**: Quality screws, bearings, brackets
- **Custom parts**: 3D printed or CNC machined components

#### Electronics ($100-$200):
- **Controller**: Arduino Due, Teensy 4.0, or Raspberry Pi
- **Power**: 3S LiPo battery (2200mAh+), voltage regulators
- **Wiring**: Quality cables, connectors, power distribution

### Software Requirements:

#### Core Algorithms:
1. **Sensor Fusion**: Combine IMU data (Madgwick/Mahony filter)
2. **Balance Control**: PID controller for standing
3. **Gait Generation**: Pre-calculated trajectories or online planning
4. **State Estimation**: Kalman filter for position/velocity

#### Development Stack:
- **Real-time**: C++ on microcontroller (Arduino/Teensy)
- **Higher-level**: Python on companion computer (Raspberry Pi)
- **Simulation**: Gazebo, PyBullet, or custom simulator
- **Visualization**: ROS tools or custom GUI

### Critical Design Parameters for 18" Robot:

#### Mechanical:
- **Foot size**: 3" long × 1.5" wide (16.7% × 8.3% of height)
- **CoM height**: Target <6" from ground (<33% of height)
- **Weight**: Target 2kg maximum
- **Joint speeds**: 0.1-0.2 sec/60° for responsive control

#### Control:
- **Balance frequency**: 100-200Hz update rate
- **Sensor fusion**: 400-1000Hz IMU sampling
- **Control bandwidth**: 10-20Hz for smooth motion
- **Latency**: <10ms total sensor-to-actuator delay

## Wheeled/Tracked Implementation Requirements

### Minimum Hardware Requirements:

#### Base Platform ($50-$150):
- **Chassis**: Pre-made or custom design
- **Motors**: 2-4x DC gear motors with encoders
- **Wheels**: Omni-wheels for holonomic motion or standard wheels
- **Battery**: 2S LiPo 1500mAh+

#### Sensors ($50-$100):
- **Odometry**: Motor encoders for position tracking
- **Obstacle**: Ultrasonic or IR distance sensors
- **Optional**: IMU for orientation, camera for vision

#### Electronics ($50-$100):
- **Controller**: Arduino Uno or Raspberry Pi Pico
- **Motor Drivers**: L298N or TB6612FNG
- **Power**: Simple voltage regulation

### Software Requirements:

#### Core Functions:
1. **Motor Control**: PWM-based speed control
2. **Odometry**: Dead reckoning from encoders
3. **Navigation**: Basic path planning
4. **Obstacle Avoidance**: Simple reactive behaviors

#### Development:
- **Simple**: Arduino IDE with basic libraries
- **Intermediate**: ROS on Raspberry Pi
- **Complex**: SLAM and autonomous navigation

## Hybrid Approach Considerations

### Wheeled Biped (e.g., Boston Dynamics Handle):
- **Advantages**: Stability of wheels + leg articulation
- **Challenges**: Complex mechanical design
- **Best for**: Applications needing both mobility and manipulation

### Retractable Wheels:
- **Advantages**: Switch between modes
- **Challenges**: Added weight and complexity
- **Best for**: Research platforms exploring both modalities

## Risk Assessment

### Bipedal Risks:
1. **Technical**: Balance algorithm failures, mechanical breakdowns
2. **Schedule**: Extended development time, endless tuning
3. **Budget**: Component costs can escalate quickly
4. **Safety**: Falling robot can damage itself or surroundings

### Wheeled Risks:
1. **Technical**: Limited to smooth surfaces, traction issues
2. **Capability**: Cannot handle stairs or significant obstacles
3. **Perception**: May be seen as less advanced or impressive

## Recommendation for First-Time Builders

### Start with WHEELED if:
- This is your first robotics project
- You have limited robotics experience
- Time or budget constraints exist
- Primary goal is learning basics

### Consider BIPEDAL if:
- You have prior robotics/control systems experience
- You're part of a team with diverse skills
- Project timeline allows for iterative development
- Failure and learning are acceptable outcomes

## Success Metrics

### For Bipedal Success:
- ✅ Stands unassisted for >30 seconds
- ✅ Recovers from small pushes (5° tilt)
- ✅ Takes 3+ consecutive steps without falling
- ✅ Navigates gentle slopes (5° incline)

### For Wheeled Success:
- ✅ Smooth, controlled movement
- ✅ Accurate position tracking (±5cm over 10m)
- ✅ Obstacle avoidance at 0.5m/s
- ✅ 30+ minutes operation time

## Next Steps Based on Decision

### If Choosing Bipedal:
1. **Week 1-2**: Detailed mechanical design, component selection
2. **Week 3-4**: Order components, build test stand
3. **Week 5-8**: Implement sensor fusion, standing balance
4. **Week 9-12**: Add legs, test weight distribution
5. **Week 13-16**: Implement simple gait, test walking
6. **Week 17-20**: Refine, add features, document

### If Choosing Wheeled:
1. **Week 1**: Select platform, order components
2. **Week 2**: Assemble hardware, basic motor control
3. **Week 3**: Add sensors, implement navigation
4. **Week 4**: Test, refine, add features

## Final Recommendation

For an **18" desktop-scale robot intended for general use**, **wheeled/tracked is recommended** for most scenarios due to:

1. **Higher probability of success** within reasonable timeframe
2. **Lower cost and complexity**
3. **More reliable operation**
4. **Ability to focus on other robot capabilities** (navigation, manipulation, interaction)

**Bipedal should be chosen only when**:
- The specific goal is to study bipedal locomotion
- The team has relevant expertise
- Resources (time, budget, patience) are sufficient
- The impressive nature of bipedal motion justifies the challenges

Remember: A functional wheeled robot is better than a non-functional bipedal robot. Start simple, achieve success, then consider more complex approaches in future iterations.