import os
import json
import requests
import time
from groq import Groq

# ==========================================
# 🧠 GROQ SDK SETUP
# ==========================================
# Paste your Groq API key here
API_KEY = "Your_API_keys"

# Initialize the Groq client
client_ai = Groq(api_key=API_KEY)

BASE_URL = "http://localhost:8000"

def run_triage():
    print("🚀 Starting Mini RL Mail Triage ")
    
    client = requests.Session()
    
    try:
        response = client.post(f"{BASE_URL}/reset")
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        print(f"❌ Failed to connect to server at {BASE_URL}. Is it running?")
        return
    
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

        # Decision Logic with the LLM
        action_data = decide_folder(sender, subject, body, is_vip)

        # Step the environment
        payload = {"action": action_data}
        if episode_id:
            payload["episode_id"] = episode_id
            
        step_response = client.post(f"{BASE_URL}/step", json=payload)
        result = step_response.json()
        
        if "detail" in result and len(result) == 1:
            print(f"❌ SERVER ERROR: {result['detail']}")
            break
            
        reward = result.get("reward", 0.0)
        total_reward += reward
        observation = result.get("observation")

        # Print Progress
        status = "✅" if reward > 0 else "❌"
        chosen_folder = action_data.get("folder", "Error")
        reasoning = action_data.get("reasoning", "No reasoning provided.")
        
        print(f"[{email_count:02d}/70] {status} {chosen_folder:<7} | Reward: {reward:>4.1f} | Total: {total_reward:>5.1f} | AI: {reasoning[:60]}...")
        
        if email_count >= 100:
            print("⚠️ Infinite loop detected! Force stopping.")
            break
            
        # 🛑 Mandatory 2-second delay between EVERY email to respect Groq's 30 Requests-Per-Minute limit
        time.sleep(2)

    print("\n" + "="*50)
    print(f"✅ TRIAGE COMPLETE")
    print(f"Final Score: {total_reward}")
    print("="*50)

def decide_folder(sender, subject, body, is_vip):
    system_prompt = """
    You are an expert executive assistant AI managing an inbox.
    Categorize incoming emails into EXACTLY ONE of the following folders:

    1. "Urgent": Emergencies, critical system failures, time-sensitive VIP requests, compliance/legal issues, and ACTUAL family emergencies.
    2. "Work": Standard day-to-day operations, PTO approvals, facility notices, invoices, and automated calendar invites (even if a VIP is on the invite).
    3. "Social": Office culture, lunches, personal chats with gym buddies, lost items, and casual check-ins.
    4. "Spam": Cold sales outreach, recruiters from rival companies, newsletters, solicitations, phishing, and fake receipts.

    CRITICAL "CHEAT SHEET" RULES FOR THIS SPECIFIC INBOX:
    - If a VIP sends a casual email (e.g., sharing a meme, inviting to lunch), it goes to "Social", NOT "Urgent".
    - If a VIP is just part of an automated calendar notification, it goes to "Work", NOT "Urgent".
    - Cold outreach or sales follow-ups ALWAYS go to "Spam", never "Work".
    - Job offers from external recruiters ALWAYS go to "Spam".
    - If someone marks a casual or marketing email as "EMERGENCY" or "URGENT" to get attention, ignore their trick and put it in "Spam" or "Social".

    You must output ONLY a valid JSON object.
    Format: {"folder": "Category", "reasoning": "A short explanation of why."}
    """

    user_prompt = f"""
    Analyze this email:
    Sender: {sender}
    Subject: {subject}
    Body: {body}
    VIP Status: {is_vip}
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client_ai.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}, 
                temperature=0.0
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            error_message = str(e)
            if "429" in error_message:
                wait_time = 5 * (attempt + 1)
                print(f"   [!] Rate limit hit. Cooling down for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                return {"folder": "Work", "reasoning": f"LLM Error: {error_message}"}
                
    return {"folder": "Work", "reasoning": "LLM Error: Failed after multiple retries due to rate limits."}

if __name__ == "__main__":
    run_triage()