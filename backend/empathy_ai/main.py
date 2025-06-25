from .emotion_detector import EmotionDetector
from .response_generator import ResponseGenerator
from .utils import log_conversation
from collections import Counter

def summarize_emotional_journey(history):
    """
    Summarizes the user's emotional journey so far based on the conversation history.
    """
    emotions = [turn["emotion"] for turn in history if turn["role"] == "user" and "emotion" in turn]
    if not emotions:
        return ""
    emotion_counts = Counter(emotions)
    most_common = emotion_counts.most_common(2)
    if len(most_common) == 1:
        return f"So far, you've mostly been feeling {most_common[0][0]}."
    else:
        return (
            f"So far, you've mostly been feeling {most_common[0][0]}, "
            f"but also had moments of {most_common[1][0]}."
        )

def main():
    """
    Main function to run the Empathy AI conversational loop.
    """
    print("✨ Hello, I am Empathy AI, your conversational companion. ✨")
    print("I'm here to listen to you without judgment.")
    print('Type your message below, or type "quit" to exit.\n')

    try:
        emotion_detector = EmotionDetector()
        response_generator = ResponseGenerator()
    except Exception as e:
        print(f"Error initializing AI components: {e}")
        print("Please ensure all models are downloaded and accessible.")
        return

    conversation_history = []

    while True:
        user_message = input("You: ")

        if user_message.lower() in ["quit", "exit"]:
            print("\nThank you for talking with me. Take care. Goodbye! 👋")
            break

        if not user_message.strip():
            print("AI: Please say something. I'm here to listen.")
            continue

        try:
            # 1. Detect emotion
            emotion_data = emotion_detector.detect_emotion(user_message)
            detected_emotion = emotion_data["emotion"]

            # 2. Add user turn to history
            conversation_history.append({
                "role": "user",
                "content": user_message,
                "emotion": detected_emotion
            })

            # 3. Summarize emotional journey
            emotion_summary = summarize_emotional_journey(conversation_history)

            # 4. Build recent context (last 4 turns)
            recent_context = conversation_history[-4:]

            # 5. Generate response with context and emotion summary
            ai_response = response_generator.generate_response(
                detected_emotion, user_message, recent_context, emotion_summary
            )

            # 6. Add assistant turn to history
            conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })

            # 7. Print response and log conversation
            print(f"AI: {ai_response}")
            log_conversation(user_message, emotion_data, ai_response)

        except Exception as e:
            print(f"AI: I'm sorry, I encountered an error. Let's try again. ({e})")

if __name__ == "__main__":
    main()
