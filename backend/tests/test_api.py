"""Quick smoke-test for the Wings API (server must be running on :8000)."""
import json
import urllib.request

BASE = "http://localhost:8000"

PAYLOAD = {
    "mentors": [
        {
            "id": "m1", "name": "Alice",
            "skills": ["python", "machine-learning"], "expertise": ["mlops"],
            "industry": "technology", "years_experience": 10,
            "experience_level": "senior", "mentoring_topics": ["career-growth"],
            "availability": ["weekday-evenings"], "timezone": "PST", "max_mentees": 2,
        },
        {
            "id": "m2", "name": "Bob",
            "skills": ["java", "spring"], "expertise": ["backend"],
            "industry": "finance", "years_experience": 8,
            "experience_level": "senior", "mentoring_topics": ["system-design"],
            "availability": ["weekends"], "timezone": "EST", "max_mentees": 1,
        },
        {
            "id": "m3", "name": "Carol",
            "skills": ["python", "data-science"], "expertise": ["ml", "statistics"],
            "industry": "technology", "years_experience": 12,
            "experience_level": "principal", "mentoring_topics": ["research", "ml"],
            "availability": ["weekday-evenings"], "timezone": "PST", "max_mentees": 3,
        },
    ],
    "mentees": [
        {
            "id": "e1", "name": "Dave",
            "skills": ["python"], "skills_to_learn": ["machine-learning", "mlops"],
            "industry": "technology", "years_experience": 1,
            "experience_level": "junior", "availability": ["weekday-evenings"],
            "timezone": "PST",
        },
        {
            "id": "e2", "name": "Eva",
            "skills": ["java"], "skills_to_learn": ["system-design", "backend"],
            "industry": "finance", "years_experience": 2,
            "experience_level": "junior", "availability": ["weekends"],
            "timezone": "EST",
        },
    ],
}


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def sep(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ── health ────────────────────────────────────────────────────
sep("GET /health")
with urllib.request.urlopen(f"{BASE}/health") as r:
    print(json.loads(r.read()))

# ── match ─────────────────────────────────────────────────────
sep("POST /api/v1/match")
result = post("/api/v1/match", PAYLOAD)
print(f"Total matches: {result['total']}")
for m in result["matches"]:
    print(f"  {m['mentor_id']} -> {m['mentee_id']}  score={m['score']}")
    for reason in m["reasons"]:
        print(f"    * {reason}")

# ── recommend ─────────────────────────────────────────────────
sep("POST /api/v1/recommend  (top_k=3)")
result = post("/api/v1/recommend", {**PAYLOAD, "top_k": 3})
print(f"Mentees with recommendations: {result['mentee_count']}")
for mentee_id, recs in result["recommendations"].items():
    print(f"\n  {mentee_id}:")
    for i, m in enumerate(recs, 1):
        print(f"    #{i}  mentor={m['mentor_id']}  score={m['score']}")
        for reason in m["reasons"]:
            print(f"        * {reason}")

