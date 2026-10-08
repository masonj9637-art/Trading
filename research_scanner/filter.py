import json

with open("unconsumed_items.json") as f:
    items = json.load(f)

priorities = [
    "color code", "stabilizer", "vqe", "quantum architecture", "hardware-software compilation",
    "multi-agent topology", "hyperparameter optimization", "self-correction", 
    "vision-language-action", "vla", "diffusion polic", "fa-rdp", 
    "control barrier function", "pac-man", "humanoid", "contact-rich",
    "agentic", "tool-flow", "sequential decision"
]

relevant = []
for item in items:
    text = (item.get("title", "") + " " + item.get("summary", "")).lower()
    if any(p.lower() in text for p in priorities):
        relevant.append({
            "id": item["id"],
            "title": item["title"],
            "summary": item["summary"],
            "request_id": item.get("request_id")
        })

print(json.dumps(relevant, indent=2))
