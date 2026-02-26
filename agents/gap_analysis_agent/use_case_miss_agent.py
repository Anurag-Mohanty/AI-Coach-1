
def identify_ai_opportunities_from_tasks(role_details, confirmed_tools, parsed_resume, industry, aspiration):
    missed_use_cases = []
    high_freq_tasks = []

    task_clusters = role_details.get('task_clusters', {})
    if isinstance(task_clusters, str):
        task_clusters = json.loads(task_clusters)
        
    for cluster in task_clusters if isinstance(task_clusters, list) else []:
        task_name = cluster.get('name') if isinstance(cluster, dict) else str(cluster)
        task_frequency = cluster.get('frequency', 'unknown') if isinstance(cluster, dict) else 'unknown'
        task_effort = cluster.get('effort', 'medium') if isinstance(cluster, dict) else 'medium'

        ai_opportunities = determine_ai_opportunities(task_name, industry)
        ai_used = any(is_ai_enabled_tool(tool, task_name) for tool in confirmed_tools)

        if not ai_used:
            for opportunity in ai_opportunities:
                suggested_ai_use = opportunity.get('use_case', 'AI assistance')
                impact = estimate_impact(task_effort, task_frequency)
                ease_of_adoption = estimate_adoption_ease(parsed_resume.get('seniority', ''), aspiration)

                if is_high_frequency_task(task_frequency):
                    high_freq_tasks.append(task_name)

                missed_use_cases.append({
                    "task": task_name,
                    "suggested_ai_use": suggested_ai_use,
                    "impact": impact,
                    "ease_of_adoption": ease_of_adoption,
                    "reason": f"No AI tool detected for {task_name}"
                })

    summary_insight = summarize_insight(len(high_freq_tasks), len(role_details.get('task_clusters', [])))

    return {
        "missed_use_cases": missed_use_cases,
        "summary_insight": summary_insight
    }

def determine_ai_opportunities(task_name, industry):
    task_keywords = task_name.lower()
    suggestions = []

    if "plan" in task_keywords:
        suggestions.append({"use_case": "AI-powered scenario simulation"})
    if "report" in task_keywords or "status" in task_keywords:
        suggestions.append({"use_case": "Automated status report generator"})
    if "email" in task_keywords or "communication" in task_keywords:
        suggestions.append({"use_case": "AI draft assistant (e.g., Grammarly, Copilot)"})
    if not suggestions:
        suggestions.append({"use_case": "General task automation"})

    return suggestions

def is_ai_enabled_tool(tool, task_name):
    return tool.get("ai_related", False)

def estimate_impact(task_effort, task_frequency):
    if task_effort == "high" or task_frequency == "daily":
        return "high"
    elif task_effort == "medium" or task_frequency == "weekly":
        return "medium"
    else:
        return "low"

def estimate_adoption_ease(seniority, aspiration):
    if "lead" in seniority.lower() or "promote" in aspiration.lower():
        return "easy"
    elif "manager" in seniority.lower():
        return "moderate"
    else:
        return "low"

def is_high_frequency_task(task_frequency):
    return task_frequency.lower() in ["daily", "multiple times a day"]

def summarize_insight(high_freq_task_count, total_task_count):
    if total_task_count > 0:
        percentage = (high_freq_task_count / total_task_count) * 100
        return f"You are missing AI opportunities in {int(percentage)}% of your high-frequency tasks."
    else:
        return "Could not detect enough tasks to analyze."
