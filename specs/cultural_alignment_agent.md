Agent Purpose
The Cultural Alignment Agent is designed to understand and evolve a user’s preferred communication, collaboration, and learning tone based on cultural, behavioral, and professional signals. Its goal is to shape how content, learning paths, nudges, and feedback are delivered across the platform — not just what is delivered.

This agent helps ensure that learning feels aligned, human, and motivational, building deep trust and long-term engagement.

🌍 3. Core Responsibilities

Responsibility	Description
Cultural tone profiling	Identify tone, analogy style, and content delivery preference
Behavioral prompt elicitation	Present user with realistic, personalized micro-scenarios to infer style
Cultural delta inference	Compare current vs. aspirational communication environment
Downstream style propagation	Inform how other agents communicate and recommend
Tone evolution tracking	Adapt over time based on user feedback and cross-agent context
🧩 4. Inputs Consumed
Structured Inputs

Source Agent	Fields Used
persona_context.py	ethnicity, location, language, self-rated style
aspiration_agent.py	future org type, tone preference
resume_agent.py	industry type, role function, stability
role_detail_agent.py	task clusters, cross-functional scope
linkedin_agent.py	recent post themes, voice tone
global_agent_memory.py	past tone feedback, corrections, delta patterns
Optional Raw Inputs
Regionally specified tone override (if manually entered)

Cultural cues from chat transcripts (later phase)

📤 5. Outputs Produced

Field	Description	Example
cultural_profile_tag	Short label for user’s inferred tone & collaboration style	“Directive async soloist”
working_style_summary	Sentence summary of preferred team and learning dynamic	“Prefers solo async learning with direct, goal-oriented language.”
cultural_delta	Contrast between current and desired environments	“Wants to shift from blunt IC to collaborative team builder”
collaboration_score	0–100 proxy for team-oriented behavior (from task clusters)	72
org_fit_flags	Pointers like “prefers async-first” or “thrives in flat teams”	“Best fit: Flat async org with mentorship culture”
learning_tone_profile	Inferred preferred tone, analogy style, and example phrasing	See below
tone_example_phrases	How a lesson or feedback should be phrased	“Let’s break it into 3 clear goals and hit each one fast.”
🗣️ 6. Tone Learning Model
A hybrid logic layer (tone_profile_engine.py) will:

Use Hofstede/psychology-informed priors (region, role)

Use LLM to hypothesize tone/analogy/feedback style

Be refined via user behavioral validation (prompt selections)

Output Format
json
Copy
Edit
{
  "tone_style": "directive",
  "analogy_style": "engineering metaphors",
  "feedback_style": "straightforward and goal-oriented",
  "tone_phrases": [
    "Let’s simplify this down to steps.",
    "Here’s the fastest way to improve.",
    "Start with what matters — ignore fluff."
  ]
}
🎯 7. Behavioral Prompting Mechanism
Instead of dropdowns, show the user 3–4 realistic micro-scenarios, tailored using persona_context and role_context. Let them choose the phrasing that resonates most.

Example:
"Imagine you're stuck on a new concept. How would you prefer your mentor to explain it?"

Option A: “Here’s a structured breakdown with examples and diagrams.”
Option B: “Think of it like tuning an engine — we’re adjusting torque.”
Option C: “Let’s just hit this step by step. First, do this...”
Option D: “You’ve got this! Let’s break through together 💪”

🧠 Their selection tunes:

tone_style

analogy_style

feedback_style

🛠️ Use LLM + trust_explainability.py to explain tone inference and confidence.

🧠 8. Learning & Feedback Integration

Mechanism	Tool	Behavior
Thumbs up/down on output	feedback_utils.py	Track accuracy of tone prediction
Corrections (text-based)	feedback_utils.py + self_learning.py	Retrain internal tone profile model
New signal integration	global_agent_memory.py	Evolve over time with context shifts
Explain reasoning	trust_explainability.py	Show why a tone or analogy style was suggested
🔁 9. Downstream Usage

Agent	How It Uses Tone Output
learning_path_agent	Preface learning content in preferred tone
content_recommender	Filters for tone-aligned materials if metadata exists
experiment_agent	Assigns projects with tone-matching mentorship or peer dynamics
follow_up_agent	Nudges or pings in matching tone (e.g., blunt vs. warm)
meta_agent	Segments tone types to power social learning and clustering
dashboard_agent	Visualizes tone evolution and cultural delta over time
🎛️ 10. Utilities Used

Utility	Purpose
agent_logger.py	Track inputs, tone scores, prompt selections
feedback_utils.py	Store user selections, corrections, thumbs
global_agent_memory.py	Recall profile, track tone evolution
downstream_formatter.py	Tag outputs with downstream compatibility
self_learning.py	Refine tone model over time
trust_explainability.py	Explain model decisions and tone suggestions
input_evaluation.py	Ensure complete persona context
compliance_utils.py	Avoid unwanted profiling based on region/ethnicity
🧑‍🎨 11. UI View Design (cultural_alignment_view.py)
Features:
Load structured context from session_state

Present tone selection scenarios with text radio buttons

Show inferred tone preview in a stylized output panel

Let users edit or re-run the profiler

Store preferences using store_user_selected_tone_profile()

✅ 12. Success Metrics

Metric	Goal
Profile engagement rate	80% of users complete tone scenario
Feedback alignment	>75% thumbs up on phrasing or tone match
Downstream usage	>4 downstream agents using output
Tone evolution accuracy	Reduced overrides over time
Persona delta visualization	Highlight tone journey in dashboard
🧬 13. Moat-Building Differentiators
No other platform dynamically adapts communication tone

Learns over time, adjusting based on emotional engagement

Makes every piece of guidance feel human and thoughtful

Paves the way for emotionally intelligent AI coaching