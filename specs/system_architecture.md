
# 🧠 AI Skill Coaching Platform - System Architecture

## High-Level Architecture
The platform consists of interconnected agents organized in a hierarchical structure, with shared utilities and core services supporting their operation.

## Core Agent Categories

### 1. Assessment Agents
- **Resume Agent** (`agents/resume/resume_agent.py`)
  - Parser (`resume_parser.py`)
  - Utils (`resume_utils.py`)
- **LinkedIn Agent** (`agents/linkedin/linkedin_agent.py`)
  - Feedback Handler (`linkedin_feedback.py`)
- **Role Detail Agent** (`agents/role_detail/role_detail_agent.py`)

### 2. Recommendation Agents

#### 2.1 Content Recommendation
- **Content Orchestration**
  - Retrieval Orchestrator (`retrieval_orchestrator.py`)
  - Query Planner (`query_planner_agent.py`)
  - Research Agent (`research_agent.py`)
  
- **Content Sources**
  - YouTube Retriever (`youtube_retriever_agent.py`)
  - GitHub Retriever (`github_retriever_agent.py`)
  - LinkedIn Retriever (`linkedin_retriever_agent.py`)
  - Perplexity Search (`perplexity_search.py`)
  
- **Content Processing**
  - Content Recommender (`content_recommender_agent.py`)
  - Content Segmenter (`content_segmenter.py`)
  - Content Scorer (`content_scorer.py`)
  - Content Explainer (`content_explainer.py`)
  - Reflection Agent (`reflection_agent.py`)

#### 2.2 Learning Path Generation
- **Learning Path Agent** (`learning_path_agent.py`)
  - Intro Generator (`intro_agent.py`)
  - Path Summary (`path_summary_agent.py`)
  - Gap Insight (`gap_insight_agent.py`)
  - Learning Steps (`learning_steps_agent.py`)
  - Closing CTA (`closing_cta_agent.py`)

### 3. Analysis Agents (v1 Root Level)
- **Role Context Agent** (`role_context_agent.py`)
- **Role Ladder Agent** (`role_ladder_agent.py`)
- **Skill Delta Agent** (`skill_delta_agent.py`)
- **Domain Jump Agent** (`domain_jump_agent.py`)
- **Tool Familiarity Agent** (`tool_familiarity_agent.py`)
- **Cultural Alignment Agent** (`cultural_alignment_agent.py`)
- **Tool Recommender** (`tool_recommender.py`)
- **Use Case Agent** (`use_case_agent.py`)
- **Use Case Miss Agent** (`use_case_miss_agent.py`)

### 4. Feedback & Follow-up Agents
- **Feedback Agent** (`feedback_agent.py`)
- **Follow-up Agent** (`follow_up_agent.py`)
- **Experiment Agent** (`experiment_agent.py`)
- **Meta Agent** (`meta_agent.py`)
- **Aspiration Agent** (`aspiration_agent.py`)

## Core Services (`agent_core/`)

### 1. Agent Infrastructure
- **Agent Logger** (`agent_logger.py`)
- **Global Agent Memory** (`global_agent_memory.py`)
- **Self Learning** (`self_learning.py`)
- **Persona Context** (`persona_context.py`)

### 2. Utilities
- **Input Evaluation** (`input_evaluation.py`)
- **Trust Explainability** (`trust_explainability.py`)
- **Compliance Utils** (`compliance_utils.py`)
- **Feedback Utils** (`feedback_utils.py`)
- **Downstream Formatter** (`downstream_formatter.py`)
- **Dashboard Hooks** (`dashboard_hooks.py`)

## UI Layer (`pages/`)
- Main Dashboard (`main.py`)
- Resume View (`resume_view.py`)
- LinkedIn View (`linkedin_view.py`)
- Role Detail View (`role_detail_view.py`)
- Content View (`content_view.py`)

## Testing & Development
- Test Suite (`sandbox/`)
  - Content Agent Tests
  - Learning Path Tests
  - Perplexity Tests
  - Query Planner Tests
  - Retrieval Orchestrator Tests

## Key Features
1. Hyper-personalization through interconnected agent insights
2. Self-learning from user feedback and peer patterns
3. Modular architecture allowing easy agent additions/updates
4. Compliance and privacy by design
5. Explainable AI recommendations

## Data Flow
1. User inputs → Assessment Agents
2. Assessment results → Analysis Agents
3. Analysis insights → Recommendation Agents
4. Recommendations → Feedback Loop
5. All interactions → Self-Learning System

## Architecture Principles
1. **Modularity**: Each agent has a single responsibility
2. **Extensibility**: Easy to add new agents/capabilities 
3. **Resilience**: Graceful fallbacks for each component
4. **Learning**: Every agent improves from feedback
5. **Privacy**: Built-in compliance and data protection
