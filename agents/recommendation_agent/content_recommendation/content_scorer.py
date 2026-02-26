# content_scorer.py

import re

# ----------------------------------------
# 📊 Score content item for relevance
# ----------------------------------------
def score_content_item(item, use_case, tool_familiarity, missing_skills, modality_preference):
    """Calculate relevance score of content"""
    try:
        base_score = 1.0
        # Score based on content source/type
        source_scores = {
            'YouTube': 1.2,
            'GitHub': 1.1,
            'LinkedIn': 1.1  # Equal base score for LinkedIn
        }
        base_score *= source_scores.get(item.get('source', 'Other'), 0.8)

        # Special handling for LinkedIn content
        if item.get('source') == 'LinkedIn':
            # Add missing fields if needed
            if 'format' not in item:
                item['format'] = 'Post'
            if 'description' not in item and 'snippet' in item:
                item['description'] = item['snippet']

        # 🔍 Keyword Match in Title, Description, or Snippet
        all_keywords = tool_familiarity + missing_skills + [use_case]
        text_fields = [item.get("title", ""), item.get("description", ""), item.get("snippet", "")]
        match_count = sum(1 for keyword in all_keywords if any(keyword.lower() in field.lower() for field in text_fields))
        base_score += match_count * 0.1

        # 🎯 Format preference
        if item.get("format") in modality_preference:
            base_score += 0.1

        # ⏱ Duration bonus/penalty (shorter = better for fast learning)
        duration_score = score_duration(item.get("duration"))
        base_score += duration_score * 0.1

        # 🌟 Popularity (GitHub stars)
        if item.get("format") == "Code" and item.get("stars"):
            base_score += min(item["stars"] // 50, 1)  # Max 1 pt

        return base_score

    except Exception as e:
        print(f"Error scoring item: {e}")
        return 0


# ----------------------------------------
# ⏱ Duration Helper (for YouTube)
# ----------------------------------------
def score_duration(duration):
    if not duration:
        return 0
    try:
        h, m, s = 0, 0, 0
        if "h" in duration:
            h = int(re.search(r"(\d+)h", duration).group(1))
        if "m" in duration:
            m = int(re.search(r"(\d+)m", duration).group(1))
        if "s" in duration:
            s = int(re.search(r"(\d+)s", duration).group(1))
        total_minutes = h * 60 + m + s / 60
        if total_minutes < 5:
            return 5
        elif total_minutes <= 15:
            return 10
        elif total_minutes <= 30:
            return 7
        else:
            return 2
    except:
        return 0