
def analyze_domain_jump(parsed_resume, aspiration_result, role_ladder=None):
    # Safely extract source and target domains
    current_domain = parsed_resume.get("domain", "unknown")
    target_domain = aspiration_result.get("target_domain", "unknown")

    # Step 1: Identify transferable capabilities
    transferable_capabilities = [
        "Cross-functional collaboration",
        "Stakeholder management",
        "Product thinking",
        "Data-driven decision making"
    ] if current_domain != "unknown" else []

    # Step 2: Identify missing knowledge
    missing_domain_knowledge = []
    if target_domain != "unknown":
        if target_domain == "advertising":
            missing_domain_knowledge = [
                "Programmatic ad systems",
                "Attribution modeling",
                "Ad targeting and audience segmentation"
            ]
        elif target_domain == "fintech":
            missing_domain_knowledge = [
                "Regulatory compliance (e.g., KYC/AML)",
                "Payment systems",
                "Credit risk modeling"
            ]
        elif target_domain == "healthcare":
            missing_domain_knowledge = [
                "HIPAA and data privacy",
                "Clinical workflows",
                "Payer-provider ecosystem"
            ]

    # Step 3: Highlight AI usage differences (simple v1)
    ai_opportunity_differences = []
    if current_domain != target_domain:
        ai_opportunity_differences = [
            f"In {target_domain}, AI is commonly applied in recommendation systems, targeting, and real-time decisioning.",
            f"In {current_domain}, AI may be more focused on process automation or clinical triage (if healthcare)."
        ]

    # Step 4: Recommend learning paths (starter)
    learning_recommendations = []
    if target_domain == "advertising":
        learning_recommendations = [
            "Take a Coursera course on digital advertising fundamentals",
            "Study case studies from Meta Ads or Google Ads APIs"
        ]
    elif target_domain == "fintech":
        learning_recommendations = [
            "Follow a Fintech 101 course on Udemy",
            "Learn how AI is applied in fraud detection"
        ]
    elif target_domain == "healthcare":
        learning_recommendations = [
            "Take a HIPAA compliance primer",
            "Explore how NLP is used in medical coding or summarization"
        ]

    # Step 5: Generate a summary
    summary = f"You're coming from {current_domain} and targeting {target_domain}. You already have strong transferable skills like {', '.join(transferable_capabilities[:2])}. To accelerate your transition, focus on learning: {', '.join(missing_domain_knowledge[:2])}."

    return {
        "current_domain": current_domain,
        "target_domain": target_domain,
        "transferable_capabilities": transferable_capabilities,
        "missing_domain_knowledge": missing_domain_knowledge,
        "ai_opportunity_differences": ai_opportunity_differences,
        "learning_recommendations": learning_recommendations,
        "summary": summary
    }
