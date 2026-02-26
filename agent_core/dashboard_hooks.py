# dashboard_hooks.py
# Located in: /agent_core/
"""
📊 Metrics Dashboard Hooks
---------------------------
Purpose: Enable agent activity tracking, status checks, and confidence insights
for use in admin + user dashboards.

Used by:
- Admin dashboard → Tracks run frequency, success rate
- Meta agent → Scores agent performance over time
- Developer view → Flags agents with declining trust/confidence

"""

import os
import json
from datetime import datetime

STATS_FOLDER = "logs/agent_stats"


def get_agent_health_snapshot(agent_name):
    path = os.path.join(STATS_FOLDER, f"{agent_name}_runs.jsonl")
    if not os.path.exists(path):
        return {"last_run": None, "runs": 0, "avg_confidence": None}

    runs = []
    with open(path, "r") as f:
        for line in f:
            runs.append(json.loads(line.strip()))

    last_run = runs[-1]["timestamp"] if runs else None
    avg_conf = round(sum(r["confidence"]
                         for r in runs) / len(runs), 2) if runs else None

    return {
        "last_run": last_run,
        "runs": len(runs),
        "avg_confidence": avg_conf
    }


def return_last_run_timestamp(agent_name):
    snapshot = get_agent_health_snapshot(agent_name)
    return snapshot["last_run"]


def return_feedback_score_avg(agent_name):
    path = os.path.join("logs", f"{agent_name}_feedback.jsonl")
    if not os.path.exists(path):
        return 0.0
    thumbs = 0
    total = 0
    with open(path, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            thumbs += len(entry.get("thumbs_up", []))
            total += 1
    return round(thumbs / total, 2) if total > 0 else 0.0


def flag_if_confidence_dropping(agent_name, drop_threshold=0.2):
    path = os.path.join(STATS_FOLDER, f"{agent_name}_runs.jsonl")
    if not os.path.exists(path):
        return False

    last_5 = []
    with open(path, "r") as f:
        for line in f:
            last_5.append(json.loads(line.strip()))
    last_5 = last_5[-5:]

    if len(last_5) < 5:
        return False

    first_avg = sum([x["confidence"] for x in last_5[:2]]) / 2
    last_avg = sum([x["confidence"] for x in last_5[-2:]]) / 2
    return (first_avg - last_avg) >= drop_threshold
