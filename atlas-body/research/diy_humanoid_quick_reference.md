# DIY Humanoid Robot - Quick Reference Guide

## Budget Target: Under $500
**Achievable with careful component selection and design optimization**

## Optimal Desktop Scale
- **Height:** 12-18 inches (30-45cm)
- **Weight:** 1.5-2kg
- **DOF:** 16-20 degrees of freedom

## Recommended Component Selection

### Servo Motors (Most Critical Cost)
| Joint Type | Servo Model | Qty | Unit Cost | Total | Torque | Notes |
|-----------|-------------|-----|-----------|-------|--------|-------|
| Legs (load-bearing) | MG996R | 8 | $8-10 | $64-80 | 10-15kg·cm | Metal gears essential |
| Arms (medium load) | MG90S | 4 | $4-6 | $16-24 | 1.8-2.2kg·cm | Metal gears preferred |
| Head/Waist (light) | SG90 | 4 | $2-3 | $8-12 | 1.2-1.8kg·cm | Plastic gears OK |
| **Total Servo Cost** | | **16** | | **$88-116** | | |

### Control System
- **Primary Controller:** Arduino Mega 2560 ($35)
- **Servo Control:** 16-channel PWM shield ($20)
- **Optional:** Raspberry Pi Zero 2W for vision/AI ($20)
- **Total Control Cost:** $55-75

### Power System
- **Battery:** 3S 2200mAh LiPo ($25)
- **Voltage Regulation:** Dual buck converters ($15)
- **Charger:** Balance charger ($15)
- **Total Power Cost:** $55

### Structural System
- **3D Printing:** 1kg PLA+ filament ($25)
- **Laser Cut Parts:** Acrylic sheets ($30)
- **Hardware:** Screws, bearings, connectors ($15)
- **Total Structural Cost:** $70

### Sensors (Optional)
- **IMU:** MPU6050 ($5)
- **Vision:** Raspberry Pi Camera V2 ($25)
- **Distance:** HC-SR04 ultrasonic ($3)
- **Total Sensors:** $33

## Total Estimated Cost: $301-349
*(Without sensors: $268-316)*

## Assembly Timeline (Realistic)
- **Design & Planning:** 1-2 weeks
- **Fabrication:** 2-3 weeks (50-80h printing)
- **Electronics:** 1 week
- **Mechanical Assembly:** 1-2 weeks
- **Programming & Testing:** 2-3 weeks
- **Total:** 6-10 weeks @ 10-15h/week

## Critical Success Factors

### 1. Power Management
- Peak current: 16A (16 servos × 1A each)
- Use large capacitors near servo clusters
- Separate power for different limb groups
- Monitor battery voltage in software

### 2. Structural Integrity
- 30-40% infill for load-bearing 3D prints
- Add ribs and fillets to stress points
- Consider metal inserts for high-stress joints
- Test each joint before full assembly

### 3. Control Strategy
- Start with static poses
- Implement gradual movement sequences
- Add IMU feedback for balance
- Use inverse kinematics for natural movement

### 4. Testing Protocol
1. Test each servo individually
2. Test limb groups separately
3. Test with reduced power/load
4. Implement incremental gait development

## Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| Servo jitter/overheating | Add capacitors, heat sinks, current limiting |
| Structural flexing | Increase infill, add ribs, use hybrid materials |
| Power brownouts | Oversize battery, use separate regulators |
| Unstable walking | Lower center of gravity, wider stance, slower movements |
| Programming complexity | Start with pre-written libraries, modular code |

## Recommended First Project Steps

1. **Learn Basics:** Assemble a 2-DOF leg segment
2. **Test Control:** Program basic servo movements
3. **Build One Limb:** Complete leg with 4 DOF
4. **Test Balance:** Get single limb working properly
5. **Scale Up:** Duplicate for other limbs
6. **Integrate:** Combine limbs into full robot
7. **Refine:** Add sensors, improve gait

## Key Design Principles

1. **Modularity:** Design limbs as separate, interchangeable modules
2. **Serviceability:** Make all components easily accessible/replaceable
3. **Documentation:** Label everything, photograph assembly steps
4. **Safety:** Include emergency stop, fuses, mechanical limits
5. **Iteration:** Expect to rebuild/improve components

## Cost-Saving Tips

1. **Buy in bulk** from Chinese suppliers (AliExpress, Banggood)
2. **Salvage parts** from old electronics (power supplies, connectors)
3. **Share resources** with local makerspace or community
4. **3D print** instead of buying machined parts
5. **Use open-source** designs and software

## When to Spend More

1. **Load-bearing servos** (legs) - don't cheap out here
2. **Power system** - reliable power prevents damage
3. **Structural joints** - failure here can destroy other components
4. **Controller** - Arduino Mega provides enough I/O for expansion

## Next Steps After Basic Build

1. Add computer vision for object tracking
2. Implement voice control
3. Add wireless control (Bluetooth/WiFi)
4. Experiment with different gait algorithms
5. Add manipulators/grippers to arms

## Resources
- **InMoov:** Reference for life-scale design principles
- **RoboPrime:** Example of ultra-low-cost design
- **Arduino Forum:** Community support and troubleshooting
- **Thingiverse:** 3D printable robot parts and designs

**Remember:** The goal is learning and iteration. Your first robot won't be perfect, but each build teaches valuable lessons for the next version.