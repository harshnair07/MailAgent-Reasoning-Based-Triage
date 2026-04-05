import requests

BASE_URL = "http://localhost:8000"

def run_triage():
    print("🚀 Starting Mini RL Mail Triage (70 Emails)...")
    
    # 1. Use a Session to automatically handle server cookies/state
    client = requests.Session()
    
    # 2. Reset and capture the Episode ID
    response = client.post(f"{BASE_URL}/reset")
    data = response.json()
    
    # Find the episode ID so we can remind the server who we are
    episode_id = data.get("episode_id")
    if not episode_id and "state" in data:
        episode_id = data["state"].get("episode_id")
        
    observation = data.get("observation") if "observation" in data else data
    
    total_reward = 0.0
    email_count = 0

    while observation and observation.get("email_text") != "No more emails in inbox.":
        email_count += 1
        
        sender = observation.get("sender") or "Unknown"
        subject = observation.get("subject") or "No Subject"
        body = observation.get("email_text") or ""
        is_vip = observation.get("is_vip") or False

        # 3. Decision Logic
        action_data = decide_folder(sender, subject, body, is_vip)

        # 4. Step the environment (NOW WITH EPISODE ID)
        payload = {"action": action_data}
        if episode_id:
            payload["episode_id"] = episode_id
            
        step_response = client.post(f"{BASE_URL}/step", json=payload)
        result = step_response.json()
        
        # Safety catch for server crashes
        if "detail" in result and len(result) == 1:
            print(f"❌ SERVER ERROR: {result['detail']}")
            break
            
        reward = result.get("reward", 0.0)
        total_reward += reward
        observation = result.get("observation")

        # 5. Print Progress
        status = "✅" if reward > 0 else "❌"
        print(f"[{email_count}/70] {status} Sender: {sender[:20]:<20} | Reward: {reward:>4.1f} | Total: {total_reward:>5.1f}")
        
        # Infinite Loop Protection
        if email_count >= 100:
            print("⚠️ Infinite loop detected! Force stopping.")
            break

    print("\n" + "="*40)
    print(f"✅ TRIAGE COMPLETE")
    print(f"Final Score: {total_reward}")
    print("="*40)

def decide_folder(sender, subject, body, is_vip):
    sender_lower = (sender or "").lower()
    subject_lower = (subject or "").lower()
    body_lower = (body or "").lower()

    # Priority 1: VIP Status
    if is_vip:
        return {"folder": "Urgent", "reasoning": "VIP sender flag is true."}

    # Priority 2: Blatant Spam / Scam Senders (High accuracy based on sender domain/name)
    spam_senders = ["scam", "deals", "b2bleads", "promo", "discount", "donations"]
    if any(k in sender_lower for k in spam_senders):
        return {"folder": "Spam", "reasoning": "Suspicious sender address."}

    # Priority 3: Social, Personal, & Culture Emails
    social_senders = ["club", "fitness", "gym", "mom", "wife", "alumni", "personal", "event", "cafe"]
    if any(k in sender_lower for k in social_senders) or "lunch" in subject_lower or "weekend" in subject_lower:
        return {"folder": "Social", "reasoning": "Personal, family, or extracurricular keywords."}

    # Priority 4: Urgent / Critical Senders & Keywords
    urgent_senders = ["boss", "ceo", "cfo", "vp", "security", "alert", "aws", "it-support", "compliance", "board"]
    urgent_keywords = ["urgent", "critical", "asap", "action required", "outage"]
    
    if any(k in sender_lower for k in urgent_senders) or any(k in subject_lower for k in urgent_keywords):
        # Edge case: The boss might just be sending a casual email
        if "lunch" in body_lower or "casual" in subject_lower:
            return {"folder": "Social", "reasoning": "Casual topic from leadership."}
        return {"folder": "Urgent", "reasoning": "High-priority sender or urgent keywords."}

    # Priority 5: Spam/Marketing Keywords in Body or Subject
    spam_keywords = ["offer", "unsubscribe", "promo", "free trial", "click here", "buy now", "newsletter"]
    if any(k in body_lower or k in subject_lower for k in spam_keywords):
        return {"folder": "Spam", "reasoning": "Marketing or spam keywords found in text."}

    # Priority 6: Default fallback
    return {"folder": "Work", "reasoning": "Standard workplace mail."}

if __name__ == "__main__":
    run_triage()