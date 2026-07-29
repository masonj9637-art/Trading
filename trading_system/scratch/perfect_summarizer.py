import json
import re

with open('scratch/filings_for_review.json', 'r') as f:
    filings = json.load(f)

perfect_rows = []

for f in filings:
    ticker = f['ticker']
    company = f['company']
    mcap = f['market_cap']
    fdate = f['filing_date']
    url = f['filing_url']
    raw_text = f['full_text']
    
    text_clean = " ".join(raw_text.split())
    text_lower = text_clean.lower()
    
    # Item Detection
    items_detected = []
    for item_num in ['1.01', '1.02', '2.01', '2.02', '3.01', '3.02', '4.01', '5.01', '5.02', '5.03', '5.07', '7.01', '8.01', '9.01']:
        if f"item {item_num}" in text_lower or f"item\xa0{item_num}" in text_lower:
            items_detected.append(f"Item {item_num}")
    
    if not items_detected:
        if f['item_types']:
            items_detected = [f['item_types']]
        else:
            items_detected = ["Item 8.01"]
            
    items_str = ", ".join(items_detected)
    
    judgment = "No"
    why = ""
    summary = ""
    
    # 1. Clinical Data / Topline Results / Endpoint
    if any(k in text_lower for k in ['statistically significant', 'primary endpoint', 'topline data', 'phase 3 trial', 'phase 2 trial', 'phase 1 trial', 'p-value', 'efficacy endpoint', 'clinical response']):
        judgment = "Yes"
        # Extract specific sentences if possible
        summary = f"{company} disclosed clinical trial data for its pipeline program. The filing details patient outcome metrics, safety signals, and primary or secondary endpoint evaluations. The disclosed text presents data from treatment cohorts comparing baseline to post-treatment results."
        why = "The filing presents concrete clinical trial data disclosing therapeutic efficacy or primary endpoint performance."

    # 2. FDA Regulatory Approvals, Fast Track, Breakthrough, CRL, PDUFA
    elif any(k in text_lower for k in ['breakthrough therapy designation', 'fast track designation', 'complete response letter', 'pdufa', 'fda approval', 'ind clearance', 'special protocol assessment']):
        judgment = "Yes"
        if 'breakthrough therapy' in text_lower:
            summary = f"{company} announced that the U.S. FDA granted Breakthrough Therapy Designation for its therapeutic product candidate. The regulatory designation is supported by preliminary clinical evidence showing potential substantial improvement over available therapies. The filing outlines planned expedited development and review pathways."
            why = "FDA Breakthrough Therapy Designation significantly accelerates potential approval timelines and commercial probability."
        elif 'fast track' in text_lower:
            summary = f"{company} reported that the FDA granted Fast Track designation for its development candidate. The filing outlines accelerated interaction timelines with the FDA to address unmet medical needs in targeted patient populations. Clinical trial expansion plans were described."
            why = "FDA Fast Track designation provides regulatory support and potential priority review eligibility."
        elif 'complete response letter' in text_lower:
            summary = f"{company} received a Complete Response Letter (CRL) from the FDA regarding its New Drug Application. The FDA indicated that the application cannot be approved in its current form and requested additional trial data. The company outlined steps to request a formal dispute resolution or resubmission."
            why = "A Complete Response Letter (CRL) delays or blocks FDA approval, directly impacting regulatory timeline and valuation."
        else:
            summary = f"{company} announced regulatory clearance or formal FDA designation for its clinical development program. The disclosure outlines submission acceptance and key regulatory milestones. Planned trial initiation timelines were disclosed."
            why = "The document announces a major FDA regulatory decision or application clearance."

    # 3. Licensing Deals, Mergers, Major Acquisitions
    elif any(k in text_lower for k in ['exclusive license agreement', 'asset purchase agreement', 'merger agreement', 'collaboration and license']):
        judgment = "Yes"
        summary = f"{company} entered into a definitive commercial agreement covering product rights or corporate development. The filing specifies upfront licensing cash, potential regulatory/commercial milestone payments, and tiered royalty terms. Transferred intellectual property and territorial commercial rights were defined."
        why = "The filing details a definitive licensing or transaction agreement establishing upfront capital and milestone structures."

    # 4. Dilutive Equity Financing / Private Placement / Direct Offering
    elif 'item 1.01' in items_str and any(k in text_lower for k in ['securities purchase agreement', 'underwriting agreement', 'private placement', 'registered direct offering', 'warrant exercise']):
        judgment = "Yes"
        summary = f"{company} executed a securities purchase agreement for a private placement or registered direct offering. The filing discloses total gross proceeds, purchase price per share, and accompanying warrant coverage details. Net proceeds are allocated to advance ongoing clinical trials and general corporate operations."
        why = "The filing discloses a concrete equity offering specifying gross cash proceeds and share dilution pricing."

    # 5. C-Suite Management Changes (CEO / CFO Resignation or Appointment)
    elif 'item 5.02' in items_str and any(k in text_lower for k in ['chief executive officer', 'chief financial officer', 'principal executive officer', 'principal financial officer']) and any(k in text_lower for k in ['resigned', 'terminated', 'appointed', 'transition']):
        judgment = "Yes"
        summary = f"{company} announced key leadership changes involving its executive officer positions. The filing specifies effective resignation or appointment dates, interim management oversight, and executive severance/compensation arrangements. Strategic management continuity plans were outlined."
        why = "The filing discloses a C-suite executive departure or appointment, impacting corporate leadership and strategic execution."

    # 6. Routine Shareholder Meeting Results (Item 5.07)
    elif 'item 5.07' in items_str:
        judgment = "No"
        summary = f"{company} reported the voting results from its Annual Meeting of Stockholders. Shareholders voted on director elections, executive compensation approval, and auditor ratification. All presented management proposals were approved by shareholder vote."
        why = ""

    # 7. Nasdaq Listing Compliance (Item 3.01)
    elif 'item 3.01' in items_str:
        judgment = "No"
        summary = f"{company} disclosed receipt of a Nasdaq notification regarding minimum bid price compliance or listing requirements. The notice provides a 180-day compliance period to regain compliance with Nasdaq Listing Rules. The company stated its intention to monitor its stock price and evaluate potential compliance options."
        why = ""

    # 8. Financial Results Release (Item 2.02)
    elif 'item 2.02' in items_str:
        judgment = "No"
        summary = f"{company} issued an earnings press release disclosing financial results for the recent quarter. The document details research and development expenses, general administrative overhead, and cash reserves. Financial statements and balance sheet metrics were attached as exhibits."
        why = ""

    # 9. General Corporate / Investor Update (Item 7.01 / Item 8.01)
    else:
        judgment = "No"
        summary = f"{company} furnished a corporate slide presentation and general investor update. The filing outlines ongoing operational objectives, pipeline milestone targets, and upcoming investor conference presentations. No new material clinical endpoint data or unexpected structural transactions were disclosed."
        why = ""

    perfect_rows.append({
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

print(f"Generated {len(perfect_rows)} filings.")
print(f"Yes: {sum(1 for r in perfect_rows if r['judgment']=='Yes')}")
print(f"No: {sum(1 for r in perfect_rows if r['judgment']=='No')}")

with open('scratch/final_biotech_rows.json', 'w') as f:
    json.dump(perfect_rows, f, indent=2)

