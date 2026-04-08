# Sprint Mode Guide

Loaded when: `sprint.active` is true in schedule.yaml.

## When to Activate

The learner has a deadline: trip, work event, meeting, date, family visit.

## Placement Validation Collision

If `placement_validation.active` is true when sprint mode is requested:

- **Sessions 2-4 (validation window):** Placement validation takes priority. Sprint preparation runs as secondary focus only — the tutor can orient vocabulary toward the sprint goal during validation exercises, but validation spot-checks are not displaced.
- **After validation completes:** Sprint mode takes full control of concept selection and activity routing.
- **Rationale:** An incorrect placement will undermine sprint preparation. Validating the learner's actual level first ensures sprint activities are appropriately calibrated.

## Protocol

1. Set `sprint.active: true` in schedule.yaml with:
   - `goal`: what they need to do (e.g., "travel to Mexico City", "work presentation in Spanish")
   - `target_date`: when it happens
   - `focus_areas`: what skills matter most for this goal

2. Temporarily reprioritize:
   - Survival vocabulary for the specific scenario
   - Practice conversations simulating the real situation
   - Communication repair phrases (must be automatic)
   - Reduce normal curriculum advancement

3. Each sprint session:
   - Open with scenario practice: "Let's practice ordering at a restaurant" / "Let's practice your presentation opening"
   - Focus on the most likely interactions they'll have
   - Build confidence through repetition of realistic scenarios
   - Assign homework targeting sprint goals (relevant vocabulary, listening to content from the destination region)

4. After the event — Debrief:
   - "How did it go? What worked? What did you wish you knew?"
   - This debrief is a high-value learning moment
   - Turn gaps into focused practice for future encounters
   - Record as milestone if it's a first

5. Deactivate sprint:
   - Set `sprint.active: false`
   - Resume normal curriculum
   - Note any new vocabulary or situations discovered during the real-world use
