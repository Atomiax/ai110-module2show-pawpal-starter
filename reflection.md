# PawPal+ Project Reflection

## 1. System Design

** Core Actions**
- Add your pet
- Add Issues you have (whether for the pet, or constraints that interfere with caring for the pet)
- Create Plan



**a. Initial design**

- Briefly describe your initial UML design.
owner has pets and constraints, task scheduler has 1 owner and multiple tasks
- What classes did you include, and what responsibilities did you assign to each?
I chose the owner, task, pet, and scheduler classes, with subsequent ones like constraints for the owner, daily plans linked to the schedueler
**b. Design changes**
- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`Scheduler.detect_conflicts()` only flags two tasks for the same pet that share the *exact* `scheduled_time` string (e.g. both at "08:40"). It does not check whether one task's duration overlaps into another task's start time (e.g. a 30-minute walk at 08:00 running into a 08:20 feeding). This is reasonable for PawPal+ because `generate_plan()` already assigns times sequentially with no gaps or overlaps by construction, so exact-match conflicts only show up when a user (or the Streamlit UI) manually schedules tasks outside that flow. Catching true interval overlaps would need an interval-overlap check (comparing start/end ranges) instead of a simple dictionary lookup, which is more correct but adds complexity that isn't needed yet given how plans are actually generated today.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
