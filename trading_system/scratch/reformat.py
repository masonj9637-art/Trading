import json
import re

transcript_path = "/home/mason/.gemini/antigravity-ide/brain/21e7a835-a541-46f0-a688-a8efe4674baf/.system_generated/logs/transcript_full.jsonl"

diff_text = ""

# Find the diff block in the transcript
with open(transcript_path, 'r') as f:
    lines = f.readlines()
    for line in reversed(lines):
        data = json.loads(line)
        if "content" in data and "Intraday Algorithmic Trading Architecture.md" in data["content"] and "[diff_block_start]" in data["content"]:
            # extract the diff text
            content = data["content"]
            start_idx = content.find("[diff_block_start]")
            end_idx = content.find("[diff_block_end]")
            if start_idx != -1 and end_idx != -1:
                diff_block = content[start_idx:end_idx]
                # extract lines starting with +
                diff_lines = []
                for dl in diff_block.split('\n'):
                    if dl.startswith('+'):
                        diff_lines.append(dl[1:])
                diff_text = " ".join(diff_lines)
                break

if not diff_text:
    print("Could not find the diff text in transcript.")
    exit(1)

# Now let's reformat diff_text
# 1. Add spaces/newlines after periods where paragraphs merged: e.g. "risk.Transitioning" -> "risk.\n\nTransitioning"
# Be careful with floats or initials.
# Match a period, then an optional quote, then a Capital letter (A-Z)
formatted = re.sub(r'\.([A-Z])', r'.\n\n\1', diff_text)

# 2. Section headers like "1. ", "2. ", "3.1 "
formatted = re.sub(r'(\d+\.\d*\s+[A-Z][^\n]{3,60}?)(?=[a-z]|$)', r'\n\n# \1\n\n', formatted)
# The above regex is a bit risky. Let's explicitly target the known headers:
known_headers = [
    r'(\d\.\s+[A-Z].*?)', # "1. The Paradigm Shift..."
    r'(\d\.\d\s+[A-Z].*?)' # "3.1 Time-Series..."
]
# Actually, since it's hard to distinguish header from numbered list, let's just insert newlines before "1. ", "2. ", "3.1 "
formatted = re.sub(r'(?<!\d)(\d+\.\d*\s+[A-Z])', r'\n\n## \1', formatted)

# Ensure "Architecting the Transition..." is a main header
formatted = re.sub(r'^(Architecting.*?)(?=## 1\.)', r'# \1\n\n', formatted)

# 3. Newlines for Options and Approaches
formatted = re.sub(r'(Option [A-Z]:|Approach [A-Z]:)', r'\n\n### \1', formatted)

# 4. Newlines for math blocks
formatted = formatted.replace('$$', '\n$$\n')

# 5. Fix bullet points or other missing spaces
# Words stuck together like "time-series data akin to language, utilizing transformer architectures"
# If there are any missing spaces between lowercase and uppercase: "gap risk.The" -> "gap risk. \n\nThe"
formatted = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted)

# Fix some known issues in the specific text:
formatted = formatted.replace("## 1. ", "\n\n## 1. ")
formatted = formatted.replace("## 2. ", "\n\n## 2. ")
formatted = formatted.replace("## 3. ", "\n\n## 3. ")
formatted = formatted.replace("## 4. ", "\n\n## 4. ")
formatted = formatted.replace("## 5. ", "\n\n## 5. ")
formatted = formatted.replace("## 6. ", "\n\n## 6. ")
formatted = formatted.replace("## 7. ", "\n\n## 7. ")
formatted = formatted.replace("## 8. ", "\n\n## 8. ")

# Write out to the file
target_path = "/home/mason/Trading/Deep Research/Intraday Algorithmic Trading Architecture.md"
with open(target_path, 'w') as f:
    f.write(formatted)

print("Successfully reformatted and wrote to the file.")
