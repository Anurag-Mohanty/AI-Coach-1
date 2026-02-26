def recommend_learning_path(parsed_resume,
                            aspiration_result,
                            role_ladder,
                            confirmed_tools,
                            domain_jump=None):
    persona = estimate_persona(parsed_resume, aspiration_result, role_ladder,
                               confirmed_tools, domain_jump)
    similar_patterns = lookup_peer_patterns(persona)

    profile = {
        'matched_persona':
        persona,
        'top_tools':
        similar_patterns.get('tools', []),
        'added_skills':
        similar_patterns.get('skills', []),
        'learning_paths':
        similar_patterns.get('paths', []),
        'confidence_score':
        estimate_confidence_score(parsed_resume, similar_patterns),
        'summary_insight':
        generate_summary_insight(persona, similar_patterns)
    }

    return profile


def estimate_persona(parsed_resume, aspiration_result, role_ladder,
                     confirmed_tools, domain_jump):
    title = parsed_resume.get("title", "PM")
    domain = parsed_resume.get("domain", "unknown")
    aspiration = aspiration_result.get("target_role", "advanced role")
    level = role_ladder.get("current_level", "mid-level")
    return f"{level} {title} in {domain} aiming for {aspiration}"


def lookup_peer_patterns(persona):
    # Simulate peer benchmark lookup
    return {
        'tools': ['Replit', 'LangChain', 'Pinecone'],
        'skills': ['Prompt chaining', 'RAG', 'Fine-tuning'],
        'paths': ['LangChain cookbook', 'RAG Quickstart on Replit']
    }


def estimate_confidence_score(parsed_resume, peer_data):
    overlap = len(
        set(peer_data['skills']) & set(parsed_resume.get("skills", [])))
    return "high" if overlap >= 2 else "medium"


def generate_summary_insight(persona, peer_data):
    return (
        f"Others like you — {persona} — have often adopted tools like {', '.join(peer_data['tools'])} "
        f"and focused on skills such as {', '.join(peer_data['skills'])}. "
        "You're on a proven path!")
