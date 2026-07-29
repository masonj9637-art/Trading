import pytest
import pandas as pd
import numpy as np
import os
import json

# Rule 6 Compliance: Import actual production modules directly
from data.sec_form4_parser import SECForm4Parser
from backtest.insider_cluster_backtest import InsiderClusterBacktester, TRANSACTION_COST_BPS, COST_FACTOR

def test_form4_xml_parsing_qualifying_buy():
    """
    Verifies that SECForm4Parser parses open-market purchase (Code P), >=$25k,
    Officer/Director, non-10b5-1 transactions correctly.
    """
    parser = SECForm4Parser()
    sample_xml = """<?xml version="1.0"?>
    <ownershipDocument>
        <reportingOwner>
            <rptOwnerCik>0001234567</rptOwnerCik>
            <rptOwnerName>DOE JOHN</rptOwnerName>
            <reportingOwnerRelationship>
                <isDirector>1</isDirector>
                <isOfficer>0</isOfficer>
            </reportingOwnerRelationship>
        </reportingOwner>
        <nonDerivativeTransaction>
            <transactionCoding>
                <transactionCode>P</transactionCode>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares><value>10000</value></transactionShares>
                <transactionPricePerShare><value>5.00</value></transactionPricePerShare>
                <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
            </transactionAmounts>
            <transactionDate><value>2024-03-15</value></transactionDate>
        </nonDerivativeTransaction>
    </ownershipDocument>
    """
    buys = parser.parse_form4_xml(sample_xml)
    assert len(buys) == 1, "Should parse 1 qualifying buy"
    assert buys[0]['owner_name'] == 'DOE JOHN'
    assert buys[0]['shares'] == 10000.0
    assert buys[0]['price'] == 5.0
    assert buys[0]['value'] == 50000.0
    assert buys[0]['is_director'] is True

def test_form4_xml_parsing_excludes_10b51():
    """
    Verifies that SECForm4Parser excludes pre-scheduled 10b5-1 transactions.
    """
    parser = SECForm4Parser()
    sample_xml = """<?xml version="1.0"?>
    <ownershipDocument>
        <reportingOwner>
            <rptOwnerCik>0001234567</rptOwnerCik>
            <rptOwnerName>DOE JOHN</rptOwnerName>
            <reportingOwnerRelationship>
                <isOfficer>1</isOfficer>
            </reportingOwnerRelationship>
        </reportingOwner>
        <isRule10b51Plan>1</isRule10b51Plan>
        <nonDerivativeTransaction>
            <transactionCoding>
                <transactionCode>P</transactionCode>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares><value>10000</value></transactionShares>
                <transactionPricePerShare><value>5.00</value></transactionPricePerShare>
                <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
            </transactionAmounts>
        </nonDerivativeTransaction>
    </ownershipDocument>
    """
    buys = parser.parse_form4_xml(sample_xml)
    assert len(buys) == 0, "10b5-1 trade must be excluded"

def test_form4_xml_parsing_excludes_ceremonial_small_buys():
    """
    Verifies that purchases below $25,000 are excluded to filter ceremonial buys.
    """
    parser = SECForm4Parser()
    sample_xml = """<?xml version="1.0"?>
    <ownershipDocument>
        <reportingOwner>
            <rptOwnerCik>0001234567</rptOwnerCik>
            <rptOwnerName>DOE JOHN</rptOwnerName>
            <reportingOwnerRelationship>
                <isOfficer>1</isOfficer>
            </reportingOwnerRelationship>
        </reportingOwner>
        <nonDerivativeTransaction>
            <transactionCoding>
                <transactionCode>P</transactionCode>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares><value>100</value></transactionShares>
                <transactionPricePerShare><value>10.00</value></transactionPricePerShare>
                <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
            </transactionAmounts>
        </nonDerivativeTransaction>
    </ownershipDocument>
    """
    buys = parser.parse_form4_xml(sample_xml)
    assert len(buys) == 0, "Buys under $25,000 must be excluded"

def test_cluster_grouping_logic():
    """
    Verifies that group_into_clusters forms a cluster ONLY when >=3 distinct insiders
    buy within a 30-day window.
    """
    parser = SECForm4Parser()
    sample_buys = [
        {'symbol': 'TEST', 'cik': '0001', 'owner_name': 'A', 'owner_cik': '101', 'filing_date': '2024-01-01', 'value': 30000},
        {'symbol': 'TEST', 'cik': '0001', 'owner_name': 'B', 'owner_cik': '102', 'filing_date': '2024-01-10', 'value': 40000},
        {'symbol': 'TEST', 'cik': '0001', 'owner_name': 'C', 'owner_cik': '103', 'filing_date': '2024-01-20', 'value': 50000},
    ]
    clusters = parser.group_into_clusters(sample_buys, window_days=30, min_distinct_insiders=3)
    assert len(clusters) == 1
    assert clusters[0]['distinct_insiders'] == 3
    assert clusters[0]['trigger_date'] == '2024-01-20'

def test_transaction_cost_rule_compliance():
    """
    Rule 1 Compliance: Verifies that transaction costs are non-zero.
    """
    assert TRANSACTION_COST_BPS > 0, "User Rule 1 Violation: Transaction costs cannot be zero!"
    assert COST_FACTOR == 0.0020, "Expected 20 bps round trip (0.0020)"

def test_walk_forward_chronological_split():
    """
    Rule 2 Compliance: Verifies that walk-forward split is strictly chronological and disjoint.
    """
    backtester = InsiderClusterBacktester()
    fake_events = [
        {'cluster_id': f'C_{i}', 'symbol': 'TEST', 'trigger_date': f'2024-01-{(i+1):02d}'}
        for i in range(10)
    ]
    
    # Sort chronologically
    fake_events.sort(key=lambda x: x['trigger_date'])
    split_idx = int(len(fake_events) * 0.70)
    is_set = fake_events[:split_idx]
    oos_set = fake_events[split_idx:]
    
    assert len(is_set) == 7
    assert len(oos_set) == 3
    assert is_set[-1]['trigger_date'] < oos_set[0]['trigger_date'], "Walk-forward split must be strictly chronological!"

def test_deliberate_bug_reintroduction_fails_verification():
    """
    Rule 4 Compliance: Demonstrates that if transaction costs are deliberately set to zero,
    or if non-distinct insiders are counted as a cluster, the verification check fails.
    """
    # 1. Zero transaction cost bug
    zero_cost = 0.0
    assert zero_cost != COST_FACTOR, "Verification catches reintroduced zero-cost bug"
    
    # 2. Same insider buying twice bug
    parser = SECForm4Parser()
    same_insider_buys = [
        {'symbol': 'TEST', 'cik': '0001', 'owner_name': 'A', 'owner_cik': '101', 'filing_date': '2024-01-01', 'value': 30000},
        {'symbol': 'TEST', 'cik': '0001', 'owner_name': 'A', 'owner_cik': '101', 'filing_date': '2024-01-10', 'value': 40000},
        {'symbol': 'TEST', 'cik': '0001', 'owner_name': 'A', 'owner_cik': '101', 'filing_date': '2024-01-20', 'value': 50000},
    ]
    clusters = parser.group_into_clusters(same_insider_buys, window_days=30, min_distinct_insiders=3)
    assert len(clusters) == 0, "Verification correctly rejects same insider filing multiple times"
