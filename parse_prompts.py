import os
import re

with open("research_scanner/research_scanner_multiagent_architecture.md", "r") as f:
    content = f.read()

# Extract parts using regex
builds = []
for i in range(1, 6):
    pattern = f"## Build {i}:.*?\n```\n(.*?)\n```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        builds.append(match.group(1).strip())
    else:
        print(f"Could not find Build {i}")

out_dir = "/home/mason/.gemini/antigravity/brain/15ea63bd-3a40-4e09-a2aa-1137e6a2b6b6/scratch"
os.makedirs(out_dir, exist_ok=True)

for i, b in enumerate(builds, 1):
    with open(os.path.join(out_dir, f"build_{i}.md"), "w") as f:
        f.write(b)
    print(f"Wrote build_{i}.md")

