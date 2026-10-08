import sqlite3
import json
import re

db_path = '/home/mason/Trading/research_scanner/research_scanner.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT * FROM fetched_items WHERE consumed_by_curator = 0")
rows = c.fetchall()

decisions = []

for row in rows:
    text = (row['title'] + " " + (row['summary'] or "")).lower()
    item_id = row['id']
    req_id = row['request_id']
    
    promote = False
    category = ""
    reason = ""
    claim = ""
    theme_note = ""
    
    if "spacetime layout and logical compilation of color code" in text or "topological color code" in text:
        promote = True
        category = "fault-tolerant quantum computing"
        reason = "Directly addresses priority on recent breakthroughs in topological color codes and hardware-software compilation bottlenecks."
    elif "stabilizer qubit loss inference" in text:
        promote = True
        category = "fault-tolerant quantum computing"
        reason = "Directly addresses priority on stabilizer qubit loss inference."
    elif "dreamqas" in text or "vqe quantum architecture search" in text:
        promote = True
        category = "fault-tolerant quantum computing"
        reason = "Directly addresses priority on VQE quantum architecture search."
    elif "manta" in text and "multi-agent" in text:
        promote = True
        category = "autonomous llm agents"
        reason = "Directly evaluates the experimental benchmark MANTA for multi-agent topology adaptation."
    elif "agenthpobench" in text:
        promote = True
        category = "autonomous llm agents"
        reason = "Directly evaluates the AgentHPOBench benchmark for automated hyperparameter optimization."
    elif "amtfv" in text:
        promote = True
        category = "autonomous llm agents"
        reason = "Addresses agentic self-correction tool-flows (AMTFV)."
    elif "pac-man" in text and "humanoid" in text:
        promote = True
        category = "physical robotics"
        reason = "Evaluates control barrier function reinforcement learning (PAC-MAN) for humanoid balance."
    elif "fa-rdp" in text:
        promote = True
        category = "physical robotics"
        reason = "Evaluates reactive diffusion policies (FA-RDP) for contact-rich manipulation."
    elif "vision-language-action" in text or " vla " in text or " vla:" in text or " vlas " in text:
        promote = True
        category = "physical robotics"
        reason = "Tracks vision-language-action (VLA) models for physical robotics."
    elif "control barrier function" in text and "humanoid" in text:
        promote = True
        category = "physical robotics"
        reason = "Tracks control barrier function reinforcement learning for humanoid safety."
        
    if promote:
        decision = {
            "id": item_id,
            "category": category,
            "reasoning": reason
        }
        if req_id is not None:
            if category == "physical robotics":
                decision["supported_theme_note"] = "Physical Robotics & Humanoid Safety Control"
                decision["addressed_claim"] = "Advances in humanoid balance, control barrier functions, and VLA model integration."
            elif category == "autonomous llm agents":
                decision["supported_theme_note"] = "Autonomous LLM Agents & Sequential Decision Making"
                decision["addressed_claim"] = "Practical execution and reliability in automated agentic workflows."
            elif category == "fault-tolerant quantum computing":
                decision["supported_theme_note"] = "Fault-Tolerant Quantum Computing & Error Correction"
                decision["addressed_claim"] = "Hardware-software compilation bottlenecks and VQE optimizations."
        decisions.append(decision)

print(json.dumps(decisions, indent=2))
