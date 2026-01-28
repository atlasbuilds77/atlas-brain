# Humanoid Robotics Design Principles Research
*Research conducted on January 27, 2026 for Atlas body redesign project*

## Executive Summary

This research examines five leading humanoid robot platforms to extract design principles applicable to an 18" desktop-scale Atlas robot. Key findings include trade-offs between hydraulic vs. electric actuation, tendon-driven vs. direct-drive hand designs, and balance system architectures. At desktop scale, electric Series Elastic Actuators (SEAs) with tendon-driven hands and integrated IMU+force sensor balance systems appear most feasible.

## 1. Boston Dynamics Atlas

### Joint Mechanisms & Actuator Placement
- **Legacy Hydraulic Atlas (2013-2024):** 28 hydraulic actuators total (6 per leg, 6 per arm, 3 for back, 1 for neck)
- **Electric Atlas (2024+):** Fully electric with wider range of motion, stronger than hydraulic predecessor
- **Joint Design:** 20-28 degrees of freedom (varies by version)
- **Actuator Types:** Transitioned from hydraulic to electric; uses Series Elastic Actuation (SEA) principles
- **Torque Specifications:** Maximum joint torque ~450Nm, joint speed up to 720°/s

### Balance & Stability Systems
- **IMU:** Multiple inertial measurement units in body and legs
- **Foot Design:** Force/torque sensors in soles for Zero Moment Point (ZMP) calculation
- **Sensors:** LIDAR + stereo cameras in head for terrain assessment and obstacle avoidance
- **Proprioception:** Full body sensing for dynamic balance during complex maneuvers

### Torso Design
- **Electronics Housing:** Three onboard computers for control, perception, and estimation
- **Cable Routing:** Internal routing through joints and limbs (hydraulic lines in older versions)
- **Power:** Battery-powered (electric version), previously tethered to external power

### Hand/Gripper Design
- **Early Versions:** One hand by Sandia National Labs, other by iRobot
- **Current:** Multiple "gripper variations" for object manipulation
- **Capabilities:** Fine motor skills demonstrated in DARPA challenges (valve turning, tool use)

### Scale Considerations
- **Full Size:** 150-180cm tall, 47-85kg weight
- **Desktop Applicability:** Complex hydraulic systems not feasible at small scale; electric actuation more suitable

## 2. Tesla Optimus

### Joint Mechanisms & Actuator Placement
- **Degrees of Freedom:** 71 total DOF for human-like dexterity
- **Actuator Types:** Custom-designed electric actuators specifically for humanoid applications
- **Placement Strategy:** Six distinct actuator types mapped to specific positions based on kinematic/dynamic requirements
- **Joint Torque:** Maximum ~450Nm, speed up to 720°/s

### Balance & Stability Systems
- **IMU:** Integrated inertial measurement for state estimation
- **Foot Design:** Presumably force sensors for balance (details not fully public)
- **Vision System:** Camera-based perception for navigation and manipulation

### Torso Design
- **Electronics:** Centralized computing with distributed control
- **Thermal Management:** Critical for high-power electric actuators
- **Cable Routing:** Internal with emphasis on serviceability

### Hand/Gripper Design
- **Gen 1:** 11 DOF driven by 6 actuators (one per finger + two for thumb)
- **Gen 3:** 22 DOF hand, tendon-controlled with actuators in forearm
- **Design Philosophy:** "Passive intelligence" - weaker fingertip joints bend first for natural wrapping grasp
- **Actuation:** Hybrid approach - tendons for flexion/extension, mechanical linkages for abduction/adduction

### Scale Considerations
- **Full Size:** Human-scale (approx 5'8")
- **Desktop Applicability:** Tendon-driven hands scalable to small size; forearm actuator placement reduces hand mass

## 3. Unitree H1

### Joint Mechanisms & Actuator Placement
- **Leg DOF:** 5-6 per leg (Hip × 3 + Knee × 1 + Ankle × 1-2)
- **Arm DOF:** 4-7 per arm (Shoulder × 3 + Elbow × 1 + Wrist × 3)
- **Actuator Types:** Low inertia high-speed internal rotor PMSM (Permanent Magnet Synchronous Motor)
- **Torque Specifications:**
  - Knee: ~360N.m
  - Hip: ~220N.m  
  - Waist: ~220N.m
  - Ankle: 59-150N.m (75×2 for H1-2)
  - Arm: 75-120N.m
- **Peak Torque Density:** 189N.m/Kg

### Balance & Stability Systems
- **IMU:** Integrated for real-time balance control
- **Foot Design:** Force sensors for dynamic gait control
- **Perception:** 360° depth sensing with 3D LIDAR + depth camera
- **Control:** Real-time balance control algorithms

### Torso Design
- **Modular Architecture:** Designed for rapid development
- **Weight Optimization:** H1: ~47kg, H1-2: ~70kg
- **Joint Bearings:** Industrial grade crossed roller bearings (high precision, high load capacity)

### Hand/Gripper Design
- **Standard Hands:** Basic grippers for manipulation tasks
- **Optional Hands:** Available with varying DOF
- **Design Focus:** Affordability and practicality over extreme dexterity

### Scale Considerations
- **Full Size:** 178-180cm tall
- **Desktop Applicability:** High torque density motors suitable for scaling down; modular design facilitates miniaturization

## 4. Agility Robotics Digit

### Joint Mechanisms & Actuator Placement
- **Leg Design:** Evolved from Cassie bipedal platform
- **Actuation:** Electric with series/compliant elements
- **Joint Philosophy:** Decoupled actuation for agile locomotion
- **Ankle Design:** Similar to Cassie - some ankle pitch actuation required during leg length variation

### Balance & Stability Systems
- **Dynamic Stability:** Designed for "dynamic stability and reach from a biped"
- **Sensor Placement:** Optimized for upright torso operation
- **Inertial Actuation:** Balance through controlled momentum

### Torso Design
- **Upright Design:** For height, sensor placement, and arm mounting
- **Industrial Focus:** Robust and heavy-duty for material handling
- **Payload Capacity:** 35 lbs (15.9kg)

### Hand/Gripper Design
- **End Effectors:** Customizable for different tasks
- **Manipulators:** Suite of manipulators for material movement
- **Design Philosophy:** Practicality for logistics and manufacturing

### Scale Considerations
- **Full Size:** 5'9" (175cm) standing height
- **Desktop Applicability:** Simplified leg kinematics could be miniaturized; focus on practical manipulation over extreme dexterity

## 5. Sanctuary AI Phoenix

### Joint Mechanisms & Actuator Placement
- **Total DOF:** ~71 degrees of freedom
- **Hand DOF:** 20-21 active degrees of freedom per hand
- **Actuator Types:** Miniature hydraulic valve actuators for hands

### Balance & Stability Systems
- **Industrial Grade:** Designed for reliable operation in work environments
- **Sensor Integration:** Comprehensive sensing for dexterous manipulation

### Torso Design
- **General Purpose:** Designed for wide range of tasks
- **Modularity:** Both AI system (Carbon) and hands designed as modular components

### Hand/Gripper Design
- **Key Innovation:** Miniaturized hydraulic valves for high power density
- **Advantages vs. Alternatives:**
  - Order of magnitude higher power density than cable/electromechanical systems
  - Better speed, strength, controllability, cycle life, impact resistance, heat management
  - 2+ billion cycle testing without leakage/degradation
- **Capabilities:** In-hand manipulation, finger abduction, advanced dexterity
- **Sensing:** Proprietary haptic technology mimicking human touch

### Scale Considerations
- **Full Size:** Human-scale
- **Desktop Applicability:** Miniature hydraulic systems challenging at small scale; tendon-driven alternatives more feasible

## Key Design Principles & Common Patterns

### Actuator Selection Trends
1. **Transition from Hydraulic to Electric:** Boston Dynamics' shift represents industry trend toward electric actuation for reliability, efficiency, and control
2. **Series Elastic Actuation (SEA):** Common in legs for impact absorption and energy efficiency
3. **High Torque Density Motors:** Unitree's PMSM approach shows importance of power-to-weight ratio
4. **Application-Specific Actuators:** Tesla's six actuator types demonstrate optimization for different joint requirements

### Balance System Architecture
1. **Multi-Sensor Fusion:** IMU + force/torque sensors + proprioception
2. **Zero Moment Point (ZMP) Control:** Standard for dynamic walking
3. **Foot Force Sensing:** Critical for terrain adaptation and balance maintenance
4. **Centralized vs. Distributed:** Trend toward distributed sensing with centralized fusion

### Torso Design Principles
1. **Electronics Centralization:** Multiple onboard computers for real-time control
2. **Thermal Management:** Critical for high-power electric systems
3. **Serviceability:** Modular design for maintenance and upgrades
4. **Cable Management:** Internal routing with strain relief at joints

### Hand Design Philosophies
1. **Tendon-Driven vs. Direct Drive:** Tendon systems reduce hand mass (actuators in forearm)
2. **DOF vs. Practicality Trade-off:** 11-22 DOF common, with simpler designs often more reliable
3. **Passive Compliance:** Weaker distal joints for natural object wrapping
4. **Sensing Integration:** Force, tactile, and position sensing critical for manipulation

### Scale Adaptation Strategies
1. **Motor Miniaturization:** High torque density essential for small scale
2. **Simplified Kinematics:** Reduced DOF often acceptable at smaller scales
3. **Tendon Actuation:** Particularly suitable for small hands
4. **Integrated Electronics:** Space constraints drive higher integration

## Feasibility at 18" Desktop Scale

### Most Suitable Approaches
1. **Actuation:** Electric Series Elastic Actuators (SEAs) or quasi-direct drive
2. **Hands:** Tendon-driven with 6-11 DOF, actuators in forearm
3. **Balance:** IMU + simple force sensors in feet
4. **Joints:** 3 DOF hip, 1 DOF knee, 2 DOF ankle (pitch/roll)
5. **Arms:** 3 DOF shoulder, 1 DOF elbow, 3 DOF wrist

### Technical Challenges at Small Scale
1. **Torque Requirements:** High torque density motors needed for dynamic motion
2. **Power Density:** Battery technology limits operational time
3. **Sensor Miniaturization:** Force/torque sensors challenging to miniaturize
4. **Heat Dissipation:** Limited surface area for cooling

### Recommended Design Direction for Atlas Desktop
1. **Legs:** Electric SEA joints with ~5-10Nm torque, force sensing feet
2. **Arms:** Tendon-driven with forearm actuators, 6-8 DOF hands
3. **Torso:** Centralized electronics with distributed motor controllers
4. **Sensing:** IMU + camera vision system (stereo or depth)
5. **Materials:** Carbon fiber/aluminum composite for strength/weight balance

## Conclusion

Professional humanoid robots demonstrate converging design patterns: electric actuation with elastic elements, multi-sensor balance systems, and tendon-driven hands. For an 18" desktop Atlas, a simplified version of these principles is feasible using modern miniaturized components. The optimal approach combines Unitree's torque density philosophy, Tesla's tendon hand design, and Boston Dynamics' balance control principles, adapted to small-scale constraints.

*Research compiled from manufacturer specifications, technical publications, and industry analysis as of January 2026.*