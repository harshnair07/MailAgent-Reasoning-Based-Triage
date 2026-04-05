import datetime

def check_calendar(proposed_time_str: str) -> str:
    """
    Checks if the user's calendar is free for a proposed time.
    
    IMPORTANT: You must pass the time exactly in the format 'Day at Time'. 
    Example: 'Monday at 9 AM', 'Wednesday at 2 PM'.
    """
    try:
        # Normalize the input to lowercase to prevent minor formatting errors
        normalized_input = proposed_time_str.strip().lower()
        
        # Mock existing meetings (normalized to lowercase)
        busy_slots = [
            "monday at 9 am",
            "thursday at 2 pm",
            "friday at 10 am"
        ]
        
        if normalized_input in busy_slots:
            return f"[Tool Output: Conflict detected. You are already booked for '{proposed_time_str}'.]"
        else:
            return f"[Tool Output: Your calendar is clear for '{proposed_time_str}'.]"
            
    except Exception as e:
        return f"[Tool Error: Could not parse time '{proposed_time_str}'. Please use 'Day at Time' format.]"


def check_crm(sender_email: str) -> str:
    """
    Queries the CRM to see if the sender is a high-value client or active prospect.
    Pass the sender's exact email address as the argument.
    """
    try:
        active_clients = [
            "procurement@global-logistics.com",
            "client.smith@bigbank.com",
            "sales@enterprise-prospect.com",
            "vp.sales@company.com" # Treating internal sales VP as high-value context
        ]
        
        if sender_email.strip().lower() in active_clients:
            return f"[Tool Output: {sender_email} is an ACTIVE Tier 1 Client/Lead. Deal size: High.]"
        else:
            return f"[Tool Output: {sender_email} not found in CRM. No active deals.]"
            
    except Exception as e:
        return f"[Tool Error: CRM lookup failed for {sender_email}]"


def scan_link(sender_email: str) -> str:
    """
    Scans the sender's email domain for phishing, spam, or malicious reputation.
    """
    try:
        suspicious_domains = [
            "discount-software.com",
            "b2bleads.net",
            "web3scam.com",
            "industry-group.org",
            "compmay-security.com", # Typo domain
            "stealth-startup.com",
            "tax.gov.phishing.com",
            "scam-link.net"
        ]
        
        # Extract domain from email
        domain = sender_email.split('@')[-1].lower()
        
        if domain in suspicious_domains:
            return f"[Tool Output: MALICIOUS DOMAIN DETECTED. Do not trust this sender.]"
        else:
            return f"[Tool Output: Domain {domain} is clean.]"
            
    except Exception as e:
        return "[Tool Error: Security scanner failed.]"


def get_reporting_chain(sender_email: str) -> str:
    """
    Checks the org chart to see if the sender is an internal VIP, Manager, or Executive.
    """
    try:
        vips = [
            "ceo@company.com",
            "cfo@company.com",
            "vp.sales@company.com",
            "board-member@company.com",
            "boss@company.com",
            "board-of-directors@company.com"
        ]
        
        if sender_email.strip().lower() in vips:
            return f"[Tool Output: VIP DETECTED. {sender_email} is above the user in the org chart.]"
        else:
            return f"[Tool Output: {sender_email} is a standard employee or external.]"
            
    except Exception as e:
        return "[Tool Error: Org chart lookup failed.]"