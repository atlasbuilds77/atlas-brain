# Practical Implementation Guide for Desktop-Scale Bipedal Robot

## Component Selection Guide

### 1. IMU Selection (Critical for Balance)

**Recommended: MPU-6050**
- Cost: $10-$15
- Features: 6-DOF (3-axis gyro + 3-axis accelerometer)
- Communication: I2C
- Libraries: MPU6050_light, MPU6050_tockn
- Alternative: MPU-9250 (adds magnetometer, $15-$20)

**Wiring:**
```
MPU-6050 → Microcontroller
VCC → 3.3V
GND → GND
SCL → SCL (A5 on Arduino Uno)
SDA → SDA (A4 on Arduino Uno)
```

### 2. Servo Motors

**Budget Option: MG996R**
- Torque: 10-12 kg·cm
- Speed: 0.17 sec/60°
- Cost: $10-$15 each
- Drawbacks: Analog, less precise, higher power consumption

**Recommended: Dynamixel AX-12A**
- Torque: 16.5 kg·cm
- Resolution: 0.29°
- Communication: TTL (daisy-chainable)
- Cost: $50-$60 each
- Advantages: Digital feedback, precise control, built-in PID

**Premium: Dynamixel MX-28**
- Torque: 23 kg·cm
- Resolution: 0.088°
- Cost: $80-$90 each
- Best for: Critical joints (ankles, hips)

### 3. Microcontroller

**Option A: Arduino Due**
- Pros: 32-bit, 84MHz, hardware FPU
- Cons: Larger, more power consumption
- Best for: Standalone implementation

**Option B: Teensy 4.0**
- Pros: 600MHz, extremely fast, small
- Cons: 3.3V only, requires level shifters for some servos
- Best for: High-performance control

**Option C: Raspberry Pi Pico**
- Pros: Dual-core, PIO for precise timing, low cost ($4)
- Cons: Less community support for robotics
- Best for: Cost-sensitive projects

### 4. Power System

**Battery: 3S LiPo 2200mAh 25C**
- Voltage: 11.1V nominal
- Capacity: 2200mAh
- Discharge: 25C continuous (55A)
- Cost: $20-$30

**Voltage Regulation:**
- Servos: Direct from battery (through power switch)
- Electronics: 5V buck converter (3A minimum)
- IMU: 3.3V linear regulator (clean power)

**Power Distribution Board:**
- Custom PCB or off-the-shelf board
- Must handle 10-20A total current
- Include fuses or polyfuses for safety

## Mechanical Design Specifications

### Frame Dimensions for 18" Robot:

```
Total Height: 457mm (18")
Torso: 150mm tall
Pelvis: 80mm tall
Thigh: 120mm long
Shin: 120mm long
Foot: 76mm long × 38mm wide (3" × 1.5")
```

### Joint Placement:
```
Hip: 80mm from pelvis center
Knee: 120mm from hip (thigh length)
Ankle: 120mm from knee (shin length)
Foot: 38mm from ankle (foot height)
```

### Weight Distribution Target:
```
Total Weight: 2000g maximum
Legs (each): 300g (600g total)
Torso/Pelvis: 800g
Arms/Head: 300g
Battery: 300g
```

### Material Selection:
- **Frame**: 3mm carbon fiber plate or 3D printed PETG/ABS
- **Joints**: Aluminum brackets with ball bearings
- **Fasteners**: M3 stainless steel screws
- **Bushings**: Oil-impregnated bronze or plastic

## Software Architecture

### 1. Sensor Fusion Code Example (Arduino + MPU6050):

```cpp
#include <MPU6050_tockn.h>
#include <Wire.h>

MPU6050 mpu6050(Wire);

// Madgwick filter variables
float beta = 0.1;  // filter gain
float q0 = 1.0, q1 = 0.0, q2 = 0.0, q3 = 0.0; // quaternion

void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu6050.begin();
  mpu6050.calcGyroOffsets(true); // Calibrate gyro
}

void madgwickUpdate(float gx, float gy, float gz, 
                    float ax, float ay, float az, float dt) {
  // Madgwick filter implementation
  // ... (full implementation available in libraries)
}

void loop() {
  mpu6050.update();
  
  float ax = mpu6050.getAccX();
  float ay = mpu6050.getAccY();
  float az = mpu6050.getAccZ();
  float gx = mpu6050.getGyroX();
  float gy = mpu6050.getGyroY();
  float gz = mpu6050.getGyroZ();
  
  float dt = 0.01; // 100Hz update rate
  madgwickUpdate(gx, gy, gz, ax, ay, az, dt);
  
  // Convert quaternion to Euler angles
  float roll = atan2(2*(q0*q1 + q2*q3), 1 - 2*(q1*q1 + q2*q2));
  float pitch = asin(2*(q0*q2 - q3*q1));
  
  // Use roll and pitch for balance control
  balanceControl(roll, pitch);
  
  delay(10); // 100Hz loop
}
```

### 2. PID Balance Controller:

```cpp
class PIDController {
private:
  float Kp, Ki, Kd;
  float integral = 0;
  float prev_error = 0;
  unsigned long prev_time = 0;
  
public:
  PIDController(float p, float i, float d) : Kp(p), Ki(i), Kd(d) {}
  
  float compute(float setpoint, float measurement) {
    unsigned long now = micros();
    float dt = (now - prev_time) / 1000000.0;
    if (dt <= 0) dt = 0.01;
    
    float error = setpoint - measurement;
    integral += error * dt;
    float derivative = (error - prev_error) / dt;
    
    float output = Kp * error + Ki * integral + Kd * derivative;
    
    // Anti-windup
    if (output > 100) output = 100;
    if (output < -100) output = -100;
    
    prev_error = error;
    prev_time = now;
    
    return output;
  }
};

// Usage for ankle control
PIDController anklePid(15.0, 0.1, 0.8);

void balanceControl(float roll, float pitch) {
  float ankle_correction = anklePid.compute(0.0, pitch); // Target 0° pitch
  
  // Convert to servo angle (example: ±30° range)
  int servo_angle = 90 + ankle_correction * 0.3;
  servo_angle = constrain(servo_angle, 60, 120);
  
  setServoAngle(ANKLE_SERVO, servo_angle);
}
```

### 3. Gait Generation (Simple Trajectory):

```cpp
// Pre-calculated gait trajectory for one step
float gait_trajectory[][3] = {
  // Time(ms), Hip Angle, Knee Angle
  {0, 0, 0},
  {500, 15, 30},
  {1000, 30, 45},
  {1500, 15, 30},
  {2000, 0, 0}
};

void executeStep(int leg) {
  unsigned long start_time = millis();
  int step_duration = 2000; // 2 seconds per step
  
  for (int i = 0; i < 5; i++) {
    float progress = (millis() - start_time) / (float)step_duration;
    int index = progress * 4;
    
    if (index < 4) {
      float hip_angle = gait_trajectory[index][1];
      float knee_angle = gait_trajectory[index][2];
      
      setServoAngle(leg * 3 + HIP_JOINT, 90 + hip_angle);
      setServoAngle(leg * 3 + KNEE_JOINT, 90 + knee_angle);
    }
  }
}
```

## Step-by-Step Build Process

### Phase 1: Single Leg Test (Week 1-2)

1. **Build one complete leg** with hip, knee, ankle joints
2. **Mount on test stand** that allows free movement
3. **Test each joint** individually with basic servo control
4. **Verify range of motion** and torque requirements

### Phase 2: Standing Balance (Week 3-4)

1. **Build complete lower body** (2 legs + pelvis)
2. **Mount IMU** in pelvis (lowest practical point)
3. **Implement sensor fusion** to get accurate orientation
4. **Tune PID controller** for standing balance
5. **Test with support** first, then try free-standing

### Phase 3: Weight Shifting (Week 5-6)

1. **Add foot pressure sensors** (FSRs)
2. **Implement weight distribution monitoring**
3. **Program controlled weight shifts** left/right
4. **Test stability** during weight shifts

### Phase 4: Static Walking (Week 7-8)

1. **Implement gait trajectory generator**
2. **Add state machine** for gait phases
3. **Test single steps** with support
4. **Implement double support phase** control

### Phase 5: Dynamic Walking (Week 9-10)

1. **Add momentum compensation**
2. **Implement capture point calculation**
3. **Test continuous walking** with spotter
4. **Add disturbance rejection**

## Tuning Guide

### PID Tuning Procedure:

1. **Start with P only** (Ki=0, Kd=0)
   - Increase Kp until robot oscillates
   - Set Kp to 50% of oscillation value

2. **Add D term** to reduce oscillation
   - Start with Kd = Kp/10
   - Increase until overshoot is minimized

3. **Add I term** to eliminate steady-state error
   - Start with very small Ki (0.001)
   - Increase slowly until error disappears

### Typical Values for 18" Robot:

```
Ankle PID (pitch): Kp=15, Ki=0.1, Kd=0.8
Hip PID (roll): Kp=12, Ki=0.05, Kd=0.6
Balance overall: Kp=20, Ki=0.2, Kd=1.0
```

### IMU Calibration:

1. **Level surface calibration**: Place robot on known level surface
2. **Gyro bias calibration**: Keep robot stationary for 5 seconds
3. **Accelerometer calibration**: Measure at 6 different orientations
4. **Magnetometer calibration** (if available): Figure-8 pattern

## Safety Considerations

### Electrical Safety:
- **Fuse all power lines** (5A fast-blow for servos)
- **Use polarized connectors** to prevent reverse polarity
- **Implement low-voltage cutoff** for LiPo batteries
- **Include emergency stop** button

### Mechanical Safety:
- **Limit joint ranges** in software and hardware
- **Use mechanical stops** to prevent over-rotation
- **Secure all fasteners** with thread locker
- **Test at low speeds** first

### Operational Safety:
- **Always have a spotter** during testing
- **Use safety tether** for first free-standing tests
- **Clear area** of obstacles and fragile items
- **Wear eye protection** during testing

## Debugging Checklist

### Robot Won't Stand:
- [ ] IMU calibrated properly
- [ ] PID gains appropriate
- [ ] Servos have sufficient torque
- [ ] Center of mass too high
- [ ] Update rate too slow (>10ms)

### Robot Oscillates:
- [ ] Reduce P gain
- [ ] Increase D gain
- [ ] Check for mechanical slop
- [ ] Verify sensor noise levels
- [ ] Increase control frequency

### Robot Drifts:
- [ ] Add I term to PID
- [ ] Recalibrate IMU
- [ ] Check for uneven weight distribution
- [ ] Verify servo centering

### Gait Unstable:
- [ ] Slow down step speed
- [ ] Increase double support time
- [ ] Adjust foot placement
- [ ] Check ground contact timing

## Cost Breakdown

### Minimum Viable Bipedal (Basic):
```
12x MG996R servos: $120
MPU-6050: $15
Arduino Due: $40
3S LiPo 2200mAh: $25
FSR sensors (8x): $40
Structure materials: $50
Miscellaneous: $50
Total: ~$340
```

### Recommended Bipedal (Good):
```
12x Dynamixel AX-12A: $600
MPU-9250: $20
Teensy 4.0: $20
3S LiPo 2200mAh: $25
FSR array: $80
Carbon fiber structure: $150
Power distribution: $50
Total: ~$945
```

### Premium Bipedal (Best):
```
20x Dynamixel MX-28: $1800
9-DOF IMU: $50
Raspberry Pi 4 + Teensy: $80
High-capacity battery: $50
Force/torque sensors: $200
Custom machined frame: $300
Professional PDB: $100
Total: ~$2580
```

## Success Milestones

### Week 2: Mechanical completion
- All joints assembled and moving freely
- Structure can support own weight

### Week 4: Sensor integration
- IMU providing stable orientation data
- All servos responding to commands

### Week 6: Standing balance
- Robot can stand with assistance
- PID controller responding to disturbances

### Week 8: Free standing
- Robot stands unassisted for 10+ seconds
- Recovers from small pushes

### Week 10: First steps
- Takes 2-3 controlled steps
- Maintains balance during step

### Week 12: Continuous walking
- Walks 5+ steps continuously
- Can turn and change direction

## Conclusion

Building a functional 18" bipedal robot is challenging but achievable with systematic approach. The keys to success are:

1. **Start simple** and build incrementally
2. **Invest in quality components** especially servos and IMU
3. **Focus on mechanical design** (low CoM, sufficient torque)
4. **Implement control algorithms** step by step
5. **Test thoroughly** at each stage
6. **Be patient** with tuning and debugging

Remember that most of the development time will be spent on software and tuning, not hardware assembly. Allocate time accordingly and celebrate small victories along the way.