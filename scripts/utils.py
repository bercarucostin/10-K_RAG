# useful item patterns to split 10-K into meaningful sections
ITEM_PATTERNS = {
    "item_1":   r"ITEM\s+1\.\s*(?:BUSINESS)?",
    "item_1a":  r"ITEM\s+1A\.\s*(?:RISK\s+FACTORS)?",
    "item_1b":  r"ITEM\s+1B\.\s*(?:UNRESOLVED\s+STAFF\s+COMMENTS)?",
    "item_2":   r"ITEM\s+2\.\s*(?:PROPERTIES)?",
    "item_3":   r"ITEM\s+3\.\s*(?:LEGAL\s+PROCEEDINGS)?",
    "item_4":   r"ITEM\s+4\.\s*(?:MINE\s+SAFETY\s+DISCLOSURES)?",
    "item_5":   r"ITEM\s+5\.\s*(?:MARKET\s+FOR\s+REGISTRANT['']S\s+COMMON\s+EQUITY)?",
    "item_6":   r"ITEM\s+6\.\s*(?:SELECTED\s+FINANCIAL\s+DATA)?",
    "item_7":   r"ITEM\s+7\.\s*(?:MANAGEMENT['']S\s+DISCUSSION\s+AND\s+ANALYSIS)?",
    "item_7a":  r"ITEM\s+7A\.\s*(?:QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES)?",
    "item_8":   r"ITEM\s+8\.\s*(?:FINANCIAL\s+STATEMENTS\s+AND\s+SUPPLEMENTARY\s+DATA)?",
    "item_9":   r"ITEM\s+9\.\s*(?:CHANGES\s+IN\s+AND\s+DISAGREEMENTS)?",
    "item_9a":  r"ITEM\s+9A\.\s*(?:CONTROLS\s+AND\s+PROCEDURES)?",
    "item_9b":  r"ITEM\s+9B\.\s*(?:OTHER\s+INFORMATION)?",
    "item_10":  r"ITEM\s+10\.\s*(?:DIRECTORS,\s*EXECUTIVE\s+OFFICERS)?",
    "item_11":  r"ITEM\s+11\.\s*(?:EXECUTIVE\s+COMPENSATION)?",
    "item_12":  r"ITEM\s+12\.\s*(?:SECURITY\s+OWNERSHIP)?",
    "item_13":  r"ITEM\s+13\.\s*(?:CERTAIN\s+RELATIONSHIPS)?",
    "item_14":  r"ITEM\s+14\.\s*(?:PRINCIPAL\s+ACCOUNTANT\s+FEES)?",
    "item_15":  r"ITEM\s+15\.\s*(?:EXHIBITS,\s*FINANCIAL\s+STATEMENT\s+SCHEDULES)?"
}

# intuitive names about what acctually is in every section
ITEM_NAMES = {
    "item_1": "Item 1 Business",
    "item_1a": "Item 1A Risk Factors",
    "item_1b": "Item 1B Unresolved Staff Comments",
    "item_2": "Item 2 Properties",
    "item_3": "Item 3 Legal Proceedings",
    "item_4": "Item 4 Mine Safety Disclosures",
    "item_5": "Item 5 Market for Registrant's Common Equity",
    "item_6": "Item 6 Selected Financial Data",
    "item_7": "Item 7 Management's Discussion and Analysis",
    "item_7a": "Item 7A Quantitative and Qualitative Disclosures",
    "item_8": "Item 8 Financial Statements and Supplementary Data",
    "item_9": "Item 9 Changes in and Disagreements",
    "item_9a": "Item 9A Controls and Procedures",
    "item_9b": "Item 9B Other Information",
    "item_10": "Item 10 Directors and Executive Officers",
    "item_11": "Item 11 Executive Compensation",
    "item_12": "Item 12 Security Ownership",
    "item_13": "Item 13 Certain Relationships",
    "item_14": "Item 14 Principal Accountant Fees",
    "item_15": "Item 15 Exhibits and Financial Statement Schedules"
}
