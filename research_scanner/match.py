import json, re

with open('/home/mason/Trading/research_scanner/items.json', 'r') as f:
    items = json.load(f)

priorities = {
    "fault-tolerant quantum computing": [
        "topological color code", "spacetime layout and logical compilation of color code",
        "stabilizer qubit loss inference", "vqe quantum architecture search", "dreamqas",
        "hardware-software compilation bottleneck"
    ],
    "autonomous llm agents": [
        "multi-agent topology adaptation", "manta",
        "automated hyperparameter optimization", "agenthpobench",
        "agentic self-correction", "amtfv"
    ],
    "physical robotics & humanoid safety": [
        "vision-language-action", "vla", "reactive diffusion polic", "fa-rdp",
        "control barrier function", "pac-man", "humanoid balance", "contact-rich manipulation"
    ]
}

results = []
for item in items:
    text = (item['title'] + " " + item['summary']).lower()
    matched = False
    for category, terms in priorities.items():
        for term in terms:
            if term.lower() in text:
                results.append({
                    "id": item["id"],
                    "title": item["title"],
                    "category": category,
                    "matched_term": term,
                    "summary_snippet": item["summary"][:200]
                })
                matched = True
                break
        if matched:
            break

print(json.dumps(results, indent=2))
