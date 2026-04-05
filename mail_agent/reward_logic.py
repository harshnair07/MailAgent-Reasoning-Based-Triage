def calculate_reward(true_category: str, predicted_category: str) -> float:
    """
    Calculates a weighted reward based on the severity of the AI's misclassification.
    """
    # Base case: The agent got it perfectly right
    if true_category == predicted_category:
        return 1.0
    
    # 🚨 Dangerous mistake: Marking an Urgent email as Spam
    if true_category == "Urgent" and predicted_category == "Spam":
        return -2.0
        
    # ⚠️ Severe mistake: Marking Work as Spam (Optional, but recommended)
    if true_category == "Work" and predicted_category == "Spam":
        return -1.5
        
    # 📉 Minor mistake: Marking Work as Social
    if true_category == "Work" and predicted_category == "Social":
        return -0.5
        
    # Default penalty for all other incorrect classifications
    return -1.0

# --- Example usage ---
# print(calculate_reward("Urgent", "Spam"))   # Returns -2.0
# print(calculate_reward("Work", "Social"))   # Returns -0.5
# print(calculate_reward("Work", "Work"))     # Returns 1.0