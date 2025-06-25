import datetime

LOG_FILE = "logs/conversation.log"

def log_conversation(user_message: str, emotion_data: dict, ai_response: str):
    """
    Logs the conversation turn to a file.

    Args:
        user_message: The user's input message.
        emotion_data: The dictionary containing the detected emotion and confidence.
        ai_response: The AI's generated response.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}]\n"
        f"User: {user_message}\n"
        f"Emotion: {emotion_data['emotion']} (Confidence: {emotion_data['confidence']})\n"
        f"AI: {ai_response}\n"
        f"{'-'*40}\n"
    )
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Error: Could not write to log file {LOG_FILE}. {e}")

if __name__ == '__main__':
    # Example usage
    log_conversation(
        "I feel amazing today!",
        {"emotion": "joy", "confidence": 0.99},
        "That's wonderful to hear!"
    )
    log_conversation(
        "I'm not sure how to feel.",
        {"emotion": "neutral", "confidence": 0.85},
        "Thanks for sharing. I'm here to listen."
    )
    print(f"Check the '{LOG_FILE}' file for example logs.")
