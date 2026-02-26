Skill Assessment UX Specification – Screen-by-Screen

This document captures the full user journey for the Skill Assessment phase of the AI Coaching Platform. It aligns to your agents, UX goals, and backend architecture.

🎬 Scene 1: Resume Upload – “Let’s Start With Your Story”

Agent Triggered: ResumeAgent

Primary Goal: Extract job title, domain, tools, company context

UI Elements:

Drag-and-drop file

Paste resume text

Confirmation of parsed fields (Title, Domain, Tools)

LLM Applet: ❌ (not present here)

Narration: “Thanks for sharing your resume. Let’s explore your career journey so far.”

Progression: Once user confirms parsed results

Background Tasks: Resume parsed and stored in global_agent_memory

🎬 Scene 2: LinkedIn Signal Boost – “Let’s Cross-Check”

Agent Triggered: LinkedInAgent

Primary Goal: Detect AI interests, activity level, influencers, endorsements

UI Elements:

Auto-detect LinkedIn profile from resume (preferred)

Fallback: ask user to confirm or provide link

Show AI-related engagements, inferred interests

LLM Applet: ✅ For customizing profile signals or adding missing info

Narration: “Let’s see how your public profile reinforces your goals.”

Progression: Once AI signals and influencers are confirmed or edited

Background Tasks: Profile scraped or inferred, memory updated

🎬 Scene 3: Aspiration Picker – “Where Are You Headed?”

Agent Triggered: AspirationAgent

Primary Goal: Capture career goal and AI direction

UI Elements:

5–6 realistic career paths (auto-generated)

Freeform textbox for custom aspirations

LLM Applet: ✅ “Help me phrase my aspiration better”

Narration: “Here are a few realistic next steps. Or tell us your own.”

Progression: After user confirms or edits aspiration

Background Tasks: Normalize career path and store

🎬 Scene 4: Daily Role Snapshot – “What Do You Actually Do?”

Agent Triggered: RoleDetailAgent

Primary Goal: Capture real work patterns

UI Elements:

Task cluster selection (e.g., execution, strategy, research, analytics)

No time sliders

LLM Applet: ✅ “What does ‘AI Opportunity Density’ mean?”

Narration: “Let’s capture what fills your work week.”

Progression: Once task types are confirmed

Background Tasks: Role scoring for opportunity density

🎬 Scene 5: Role Context – “How Much Leverage Do You Have?”

Agent Triggered: RoleContextAgent

Primary Goal: Assess scope, org visibility, PMF stage

UI Elements:

Team size

Reporting structure

Product stage (Early, Growth, Mature)

LLM Applet: ✅ “Explain what PMF means in this context”

Narration: “Let’s understand the scope of your influence.”

Progression: On form completion

Background Tasks: Role context stored

🎬 Scene 6: Tool Familiarity Heatmap – “What’s In Your Toolkit?”

Agent Triggered: ToolFamiliarityAgent

Primary Goal: Understand confidence across tools

UI Elements:

Categories (Analytics, ModelOps, Prompting Tools)

Radio selection for confidence (e.g., Beginner / Used / Confident)

LLM Applet: ✅ “Should I learn LangChain?”

Narration: “Let’s map the tools you use and the ones you want to use.”

Progression: Once all tools rated or skipped

Background Tasks: Tool profile stored and tagged

🎬 Scene 7: Cultural Alignment – “How Do You Learn Best?”

Agent Triggered: CulturalAlignmentAgent

Primary Goal: Capture soft preferences and cultural influence

UI Elements:

Text input: cultural influences

Radio buttons: learning preference

Optional: LLM-generated scenario + learning style choices

LLM Applet: ✅ “What’s the best learning style for product managers like me?”

Narration: “We want to adapt to your natural learning rhythm.”

Progression: When learning style selected

Background Tasks: Stored to persona_context

🎬 Scene 8: Skill Summary – “Here’s What We Learned About You”

Agent Triggered: SkillAssessmentAgent

Primary Goal: Synthesize full profile into readable, editable summary

UI Elements:

LLM-generated narrative (editable)

Highlighted strengths, gaps, learning styles

Feedback thumbs on each section

Chat applet to edit/reword

Download profile option

LLM Applet: ✅ “Make this more growth-oriented”

Narration: “Here’s your skill story — fully personalized and editable.”

Progression: When confirmed

Background Tasks: Kick off GapAnalysisAgent

🎬 Scene 9: Gap Tee-up – “Let’s Bridge the Gap”

Agent Triggered: GapAnalysisAgent (background)

Primary Goal: Keep user engaged while downstream agents compute

UI Elements:

Loading spinner

Progress animation

Message: “Analyzing your profile to identify personalized learning gaps…”

LLM Applet: Optional chat explaining gap calculation logic

Narration: “Now let’s figure out what will get you there.”

Progression: Auto-route to gap insight screen

Background Tasks: Gap and recommendation tree initialized