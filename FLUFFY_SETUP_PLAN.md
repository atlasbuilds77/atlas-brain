# Fluffy - Household Management Agent Setup Plan

## Overview
**Name:** Fluffy 🐾  
**Purpose:** Household management, family assistant, home automation  
**Model:** GPT-4o-mini (cost-optimized, $0.15/M in, $0.60/M out)  
**Location:** Same Mac Mini as Atlas, separate workspace  
**Users:** Orion, Laura, whole household  

---

## Identity & Personality

**Character:**
- Helpful household manager
- Friendly, approachable, family-oriented
- Proactive but not intrusive
- Organized, detail-oriented
- Pet-friendly (knows the dog matters!)

**Tone:**
- Warm, conversational
- Clear, concise
- Patient with everyone in household
- Gentle reminders (not nagging)

**Example interactions:**
- "Hey! Just a reminder — it's time for your evening meds. Water's in the kitchen 💊"
- "The dog hasn't been walked yet today. Want me to set a reminder for later?"
- "Flea medication is due this weekend. Should I order more from Chewy?"
- "Living room lights are on. Want me to turn them off?"

---

## Technical Setup

### Workspace Structure
```
/Users/orionsolana/fluffy/
├── IDENTITY.md (Fluffy's personality)
├── USER.md (Household info: Orion, Laura, pet details)
├── HOUSEHOLD.md (Family routines, preferences, schedules)
├── HEARTBEAT.md (Startup checklist)
├── memory/
│   ├── medicine_log.md (who took what, when)
│   ├── pet_care.md (walks, meds, vet visits)
│   ├── maintenance.md (house tasks, schedules)
│   └── shopping.md (recurring orders, inventory)
└── skills/ (custom household skills)
```

### Clawdbot Gateway Config
- **Port:** 18081 (Atlas on 18080)
- **Profile:** fluffy
- **API Key:** OpenAI (GPT-4o-mini)
- **Channels:** Telegram (household group)

### Model Selection: GPT-4o-mini
**Why:**
- ~50% cheaper than Haiku
- Perfect for simple household tasks
- Fast response times
- Estimated cost: $0.50-1/day

**You'll need:**
- OpenAI API key (create at platform.openai.com)
- Add to Fluffy's config

---

## Core Features (Phase 1)

### 1. Medicine Management
**Tracking:**
- Daily medication schedules per person
- Log when taken (voice/text confirmation)
- Low inventory alerts
- Refill reminders

**Cron Jobs:**
- Morning meds reminder (configurable time)
- Evening meds reminder (configurable time)
- Weekly refill check

**Commands:**
- "Did I take my meds?" → Check log
- "Mark meds taken" → Log entry
- "When do I need refills?" → Check schedule

### 2. Pet Care (Dog)
**Tracking:**
- Daily walks (time, who walked)
- Flea/tick medication (monthly schedule)
- Vet appointments
- Food/supply inventory

**Cron Jobs:**
- Morning walk reminder (if not logged)
- Evening walk check
- Monthly flea med reminder
- Supply reorder alerts

**Commands:**
- "Did we walk the dog?" → Check today's log
- "Mark dog walked" → Log entry
- "When's the next flea treatment?" → Check schedule
- "Order dog food" → Trigger Chewy/Amazon order

### 3. Home Automation (Lights)
**Integration:** HomeKit / Home Assistant  
**Capabilities:**
- Turn lights on/off (by room)
- Dim/brighten
- Set scenes ("movie mode", "bedtime")
- Schedule automations

**Commands:**
- "Turn off living room lights"
- "Dim bedroom lights to 50%"
- "Lights off everywhere"
- "Good night" → Bedtime scene

### 4. Household Reminders
**General:**
- Grocery shopping lists
- Bill payment reminders
- Maintenance schedules (HVAC, lawn, etc.)
- Event reminders

---

## Telegram Setup

### Household Group
1. Create Telegram group: "Our Home" (or whatever name)
2. Add: Orion, Laura, anyone else in household
3. Add Fluffy bot to group
4. Everyone can interact

### Bot Configuration
- Fluffy responds to @mentions or direct messages
- Sends proactive reminders to group
- Can DM individuals for personal reminders (meds)

### Privacy
- Medicine reminders can be private (DM only)
- General stuff (dog walks, lights) in group
- Configurable per person

---

## Implementation Phases

### Phase 1: Foundation (Day 1-2)
- [ ] Install separate Clawdbot instance
- [ ] Create Fluffy workspace structure
- [ ] Write identity files (IDENTITY.md, USER.md, HOUSEHOLD.md)
- [ ] Get OpenAI API key
- [ ] Configure gateway on port 18081
- [ ] Test basic chat interaction

### Phase 2: Telegram + Memory (Day 3)
- [ ] Create household Telegram group
- [ ] Add Fluffy to group
- [ ] Set up memory tracking files
- [ ] Test reminders and logging
- [ ] Configure cron jobs (medicine, dog walk)

### Phase 3: Home Automation (Day 4-5)
- [ ] Integrate HomeKit / Home Assistant
- [ ] Test light control
- [ ] Set up scenes
- [ ] Add voice commands (HomePod shortcuts)

### Phase 4: Advanced Features (Week 2+)
- [ ] Automatic prescription refills (pharmacy API)
- [ ] Pet supply auto-ordering (Chewy API)
- [ ] Expand to thermostat, locks, etc.
- [ ] Dashboard/web interface
- [ ] Voice wake word setup

---

## Data Structure Examples

### Medicine Log (memory/medicine_log.md)
```markdown
# Medicine Log

## Orion
- **Medication:** [Name]
- **Dosage:** [Amount]
- **Schedule:** Daily 8 AM, 8 PM
- **Last taken:** 2026-01-23 8:00 AM ✅
- **Next refill:** 2026-02-15
- **Inventory:** 45 pills remaining

## Laura
- **Medication:** [Name]
- **Schedule:** Daily 9 AM
- **Last taken:** 2026-01-23 9:00 AM ✅
```

### Pet Care Log (memory/pet_care.md)
```markdown
# Pet Care - [Dog Name]

## Today (2026-01-23)
- Morning walk: 7:30 AM ✅ (Orion)
- Evening walk: Not yet ⏳

## Medications
- Flea/tick: Last applied 2026-01-05
- Next due: 2026-02-05
- Heartworm: Monthly (due 2026-02-01)

## Inventory
- Dog food: 15 lbs remaining (reorder at 10 lbs)
- Treats: Low (order this week)
- Flea meds: 2 doses left
```

---

## Cron Job Schedule

### Daily
- **6:30 AM:** Morning medicine reminder (Orion)
- **7:00 AM:** Check if dog walked yet
- **9:00 AM:** Morning medicine reminder (Laura)
- **6:00 PM:** Evening walk check
- **8:00 PM:** Evening medicine reminder (Orion)

### Weekly
- **Sunday 10 AM:** Medication refill check
- **Sunday 6 PM:** Flea/tick medication check
- **Monday 8 AM:** Grocery/supply inventory check

### Monthly
- **1st of month:** Bill payment reminders
- **1st of month:** Pet medication reorder check

---

## Cost Estimate

**GPT-4o-mini pricing:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Estimated daily usage:**
- 10-20 interactions (500-1k tokens each): ~10k-20k tokens
- 5-10 cron reminders (300 tokens each): ~2k-3k tokens
- **Total: ~12k-23k tokens/day**

**Daily cost:** $0.01-0.02 (~$0.50-1/month)

**Atlas comparison:**
- My usage: $5-15/day (complex work)
- Fluffy: $0.50-1/day (simple tasks)
- **Total increase: minimal**

---

## Next Steps (Today)

1. **Finalize household info:**
   - Dog's name?
   - Medicine schedules (times, what meds)?
   - Preferred reminder times?

2. **Get OpenAI API key:**
   - Sign up at platform.openai.com
   - Create API key
   - $5 credit to start

3. **Create Telegram group:**
   - Name it
   - Add Orion + Laura
   - Get group ID for config

4. **I'll build:**
   - Fluffy identity files
   - Workspace structure
   - Initial cron jobs
   - Memory tracking templates

**Ready to start? What's the dog's name and what are the medicine schedules?**
