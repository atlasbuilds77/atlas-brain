# Humanoid Robot Comparison Table

## Key Specifications

| Feature | Boston Dynamics Atlas | Tesla Optimus | Unitree H1 | Agility Robotics Digit | Sanctuary AI Phoenix |
|---------|----------------------|---------------|------------|------------------------|----------------------|
| **Height** | 150-180cm | ~173cm (5'8") | 178-180cm | 175cm (5'9") | Human-scale |
| **Weight** | 47-85kg | ~55kg (est) | 47-70kg | ~70kg (est) | Not specified |
| **Total DOF** | 20-28 | 71 | 27-47 | Not specified | ~71 |
| **Leg DOF** | 6 per leg | Not specified | 5-6 per leg | Evolved from Cassie | Not specified |
| **Arm DOF** | 6 per arm | Not specified | 4-7 per arm | Customizable | Not specified |
| **Hand DOF** | Basic grippers | 11-22 per hand | Optional hands | Custom end effectors | 20-21 per hand |
| **Actuator Type** | Hydraulic → Electric | Custom electric | PMSM electric | Electric | Miniature hydraulic |
| **Max Joint Torque** | ~450Nm | ~450Nm | 360Nm (knee) | Not specified | Not specified |
| **Top Speed** | Not specified | Not specified | 3.3m/s (running) | Walking speed | Not specified |
| **Battery** | Onboard | Onboard | 864Wh, replaceable | Autonomous docking | Not specified |
| **Sensors** | LIDAR, stereo, IMU, force | Cameras, IMU | 3D LIDAR, depth, IMU | Perception system | Haptic, vision |
| **Balance System** | Full body sensing | IMU + vision | Real-time control | Dynamic stability | Industrial grade |
| **Primary Use Case** | Search/rescue, industrial | General purpose | Research, general | Logistics, manufacturing | General purpose |
| **Key Innovation** | Dynamic motion control | AI integration, hands | Affordability, speed | Practical deployment | Hydraulic dexterity |
| **Desktop Scale Feasibility** | Medium (electric version) | High (tendon hands) | High (modular design) | Medium (simplified) | Low (hydraulics) |

## Design Philosophy Comparison

### Boston Dynamics Atlas
- **Focus:** Extreme dynamic motion, parkour, industrial tasks
- **Strength:** Unmatched balance and agility
- **Weakness:** Complexity, cost
- **Desktop Relevance:** Balance algorithms, whole-body control

### Tesla Optimus
- **Focus:** Practical humanoid for real-world work
- **Strength:** AI integration, scalable manufacturing
- **Weakness:** Unproven at scale
- **Desktop Relevance:** Tendon hand design, actuator optimization

### Unitree H1
- **Focus:** Affordable research platform
- **Strength:** Price/performance, modularity
- **Weakness:** Less refined than competitors
- **Desktop Relevance:** High torque density motors, cost-effective design

### Agility Robotics Digit
- **Focus:** Logistics and material handling
- **Strength:** Practical deployment, industrial focus
- **Weakness:** Limited dexterity
- **Desktop Relevance:** Simplified kinematics for practical tasks

### Sanctuary AI Phoenix
- **Focus:** Human-like dexterity and intelligence
- **Strength:** Advanced manipulation, hydraulic hands
- **Weakness:** Complexity of hydraulic systems
- **Desktop Relevance:** Dexterity goals (though different implementation)

## Scalability Assessment (1=Poor, 5=Excellent)

| Scaling Factor | Atlas | Optimus | H1 | Digit | Phoenix |
|----------------|-------|---------|----|-------|---------|
| **Size Reduction** | 3 | 4 | 5 | 4 | 2 |
| **Cost Reduction** | 2 | 3 | 5 | 4 | 1 |
| **Complexity Management** | 2 | 3 | 4 | 4 | 1 |
| **Power Efficiency** | 3 | 4 | 4 | 4 | 2 |
| **Manufacturability** | 2 | 5 | 4 | 4 | 2 |
| **Software Reuse** | 4 | 3 | 3 | 3 | 3 |
| **Overall Desktop Fit** | 3 | 4 | 4 | 3 | 2 |

## Recommended Borrowing for Desktop Atlas

### High Priority (Directly Applicable)
1. **Tesla's tendon hand design** - Scalable, reduces hand mass
2. **Unitree's torque density focus** - Critical for small scale
3. **Boston Dynamics' balance algorithms** - Proven effectiveness

### Medium Priority (Adaptable)
1. **Digit's practical kinematics** - Simplified but effective
2. **Sanctuary's dexterity goals** - Aim for capable manipulation
3. **Optimus' actuator optimization** - Right actuator for each joint

### Low Priority (Not Scalable)
1. **Phoenix's hydraulic hands** - Too complex for small scale
2. **Atlas' extreme dynamics** - Overkill for desktop
3. **All systems' extreme DOF counts** - Simplify for small scale

## Key Takeaways for 18" Design

1. **Electric > Hydraulic** for small scale
2. **Tendon-driven > Direct-drive** for hands
3. **Simplified kinematics** often sufficient
4. **Torque density** is critical constraint
5. **Balance algorithms** transfer well across scales
6. **Modular design** enables incremental development
7. **Cost constraints** drive simplification
8. **Thermal management** becomes more challenging at small scale

*Table compiled from public specifications and technical analysis as of January 2026*