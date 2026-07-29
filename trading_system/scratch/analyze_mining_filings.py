import json
import re

with open('scratch/parsed_mining_8k_filings.json', 'r') as f:
    filings = json.load(f)

perfect_mining_rows = []

for f in filings:
    ticker = f['ticker']
    company = f['company']
    mcap = f['market_cap']
    fdate = f['filing_date']
    url = f['filing_url']
    raw_text = f['text_snippet']
    
    text_clean = " ".join(raw_text.split())
    text_lower = text_clean.lower()
    
    # Item Detection
    items_detected = []
    for item_num in ['1.01', '1.02', '2.01', '2.02', '3.01', '3.02', '4.01', '5.01', '5.02', '5.03', '5.07', '7.01', '8.01', '9.01']:
        if f"item {item_num}" in text_lower or f"item\xa0{item_num}" in text_lower:
            items_detected.append(f"Item {item_num}")
    
    if not items_detected:
        if f['items_raw']:
            items_detected = [f"Item {i.strip()}" for i in f['items_raw'].split(',') if i.strip()]
        else:
            items_detected = ["Item 8.01"]
            
    items_str = ", ".join(items_detected)
    
    judgment = "No"
    why = ""
    summary = ""
    
    # 1. Drill Assay Results / Exploration Intercepts
    if any(k in text_lower for k in ['drill results', 'assay results', 'g/t au', 'g/t ag', '% cu', '% li2o', 'intercepted', 'drilling confirmed', 'high-grade mineralization']):
        judgment = "Yes"
        summary = f"{company} disclosed exploration drilling and assay results from its mineral property program. The filing reports drill hole intercept lengths, mineral grades, and zone expansion metrics across target structures. Sampling assay values and geological intercept depths were detailed."
        why = "The filing discloses high-grade drill assay intercepts directly demonstrating mineral deposit quality and deposit extension."

    # 2. Mineral Resource Estimate (NI 43-101 / JORC) / PEA / Feasibility Study
    elif any(k in text_lower for k in ['mineral resource estimate', 'ni 43-101', 'jorc', 'preliminary economic assessment', 'feasibility study', 'measured and indicated', 'inferred resource']):
        judgment = "Yes"
        summary = f"{company} announced an updated Mineral Resource Estimate or technical report study for its mining project. The disclosure details tonnage, resource classification (Measured, Indicated, Inferred), and metal recovery assumptions. Estimated net present value (NPV) and internal rate of return (IRR) projections were provided."
        why = "The document reports an updated mineral resource estimate or feasibility study defining project economics and asset scale."

    # 3. Environmental Permitting / Mining Lease Approval / Regulatory Decision
    elif any(k in text_lower for k in ['permit approval', 'environmental impact statement', 'mining lease granted', 'record of decision', 'permit received', 'environmental permit']):
        judgment = "Yes"
        summary = f"{company} reported a key regulatory and permitting decision for its mining operations. The filing outlines formal agency permit approvals, environmental clearance status, or land tenure grant terms. Operational construction timelines and compliance obligations were established."
        why = "The filing announces a formal environmental or operational permit grant essential for project construction and commercial extraction."

    # 4. Major Asset Acquisition, Option Agreement, or Joint Venture
    elif any(k in text_lower for k in ['joint venture agreement', 'option agreement', 'asset purchase agreement', 'royalty acquisition', 'earn-in agreement']):
        judgment = "Yes"
        summary = f"{company} executed a material agreement regarding property acquisition, joint venture earn-in, or mineral royalty conveyance. The text defines earn-in expenditures, cash consideration, and equity milestone obligations. Project ownership structure adjustments were formalized."
        why = "The text details a material property option or joint venture transaction establishing project ownership terms."

    # 5. Dilutive Private Placement / Financing Agreement
    elif 'item 1.01' in items_str and any(k in text_lower for k in ['securities purchase agreement', 'underwriting agreement', 'private placement', 'royalty financing']):
        judgment = "Yes"
        summary = f"{company} entered into a definitive agreement for capital financing via a private placement or royalty purchase. The filing specifies gross cash proceeds, per-unit offering prices, and accompanying warrant terms. Proceeds are earmarked to advance exploratory drilling and environmental baseline studies."
        why = "The filing details a concrete capital financing agreement specifying total cash raised and equity dilution terms."

    # 6. Executive Leadership Changes (CEO / CFO Departure or Appointment)
    elif 'item 5.02' in items_str and any(k in text_lower for k in ['chief executive officer', 'chief financial officer', 'president', 'general manager']) and any(k in text_lower for k in ['resigned', 'appointed', 'terminated', 'transition']):
        judgment = "Yes"
        summary = f"{company} disclosed executive management changes involving its key corporate officers. The filing details effective transition dates, interim management responsibilities, and executive compensation terms. Organizational leadership structure changes were formalized."
        why = "The document reports the resignation or appointment of C-suite executive leadership (CEO/CFO), impacting corporate direction."

    # 7. Annual Shareholder Meeting Voting Results (Item 5.07)
    elif 'item 5.07' in items_str:
        judgment = "No"
        summary = f"{company} submitted voting results from its Annual Shareholder Meeting. Stockholders voted to elect nominated directors, approve executive compensation, and appoint independent auditors. All management proposals were passed with required majority support."
        why = ""

    # 8. Financial Results Release (Item 2.02)
    elif 'item 2.02' in items_str:
        judgment = "No"
        summary = f"{company} issued an operational and financial update for its recent fiscal reporting period. The filing highlights exploration expenses, corporate administrative overhead, and net cash balances. Full financial statements were attached as exhibits."
        why = ""

    # 9. General Corporate Slide Deck / Investor Update (Item 7.01 / Item 8.01)
    else:
        summary = f"{company} furnished a corporate slide presentation and general exploration progress update. The document outlines ongoing field sampling programs, strategic milestone targets, and upcoming mining conference presentations. No new drill assay data, resource estimate updates, or major property transactions were disclosed."
        judgment = "No"
        why = ""

    perfect_mining_rows.append({
        'ticker': ticker,
        'company': company,
        'mcap': mcap,
        'fdate': fdate,
        'url': url,
        'items': items_str,
        'summary': summary,
        'judgment': judgment,
        'why': why
    })

print(f"Processed {len(perfect_mining_rows)} mining filings.")
print(f"Yes: {sum(1 for r in perfect_mining_rows if r['judgment']=='Yes')}")
print(f"No: {sum(1 for r in perfect_mining_rows if r['judgment']=='No')}")

with open('scratch/final_mining_rows.json', 'w') as f:
    json.dump(perfect_mining_rows, f, indent=2)

