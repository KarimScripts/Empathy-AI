from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class EmotionDetector:
    def __init__(self):
        """
        Initializes the EmotionDetector with a pre-trained text classification model.
        """
        model_name = "j-hartmann/emotion-english-distilroberta-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # We explicitly load the model to ensure safetensors is used.
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, use_safetensors=True
        )

        self.classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            top_k=None
        )

    def detect_emotion(self, text: str) -> dict:
        """
        Detects the primary emotion from the given text.

        Args:
            text: The input string from the user.

        Returns:
            A dictionary containing the detected emotion and its confidence score.
            Example: {"emotion": "sadness", "confidence": 0.92}
        """
        if not text:
            return {"emotion": "neutral", "confidence": 1.0}

        results = self.classifier(text)
        # The model with `return_all_scores=True` returns a list inside a list
        scores = results[0]
        # Find the emotion with the highest score
        top_emotion = max(scores, key=lambda x: x['score'])
        
        return {
            "emotion": top_emotion["label"],
            "confidence": round(top_emotion["score"], 2)
        }

if __name__ == '__main__':
    # Example usage
    detector = EmotionDetector()
    message = "I feel like nothing I do is good enough anymore."
    emotion_data = detector.detect_emotion(message)
    print(f"Message: '{message}'")
    print(f"Detected Emotion: {emotion_data}")

    message_joy = "I am so happy and excited about the new project!"
    emotion_data_joy = detector.detect_emotion(message_joy)
    print(f"Message: '{message_joy}'")
    print(f"Detected Emotion: {emotion_data_joy}")
