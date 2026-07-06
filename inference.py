import os
import time
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel

class FAQClassifier:
    def __init__(self, model_dir="./best_model"):
        self.model_dir = model_dir
        
        # 1. Load label mapping
        mapping_path = os.path.join(model_dir, "label_mapping.json")
        if not os.path.exists(mapping_path):
            raise FileNotFoundError(
                f"Label mapping not found at {mapping_path}. "
                "Make sure you have run the training pipeline (train.py) successfully."
            )
        with open(mapping_path, "r") as f:
            mapping = json.load(f)
            # Convert keys back to integers (JSON loads dict keys as strings)
            self.id2label = {int(k): v for k, v in mapping["id2label"].items()}
            self.label2id = mapping["label2id"]
            
        # 2. Determine best available device (CUDA, MPS, or CPU)
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
            
        print(f"Initializing inference on device: {self.device}")
        
        # 3. Load base model & tokenizer
        # In PEFT, we load the base model first, then layer the adapter on top.
        peft_config_path = os.path.join(model_dir, "adapter_config.json")
        if not os.path.exists(peft_config_path):
            raise FileNotFoundError(f"Adapter config not found at {peft_config_path}")
            
        with open(peft_config_path, "r") as f:
            peft_config_data = json.load(f)
            
        # Load the base model name from adapter config
        base_model_name = peft_config_data.get("base_model_name_or_path", "distilbert-base-uncased")
        
        # Load the tokenizer from model_dir (saved during training)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        
        # Load the base model
        base_model = AutoModelForSequenceClassification.from_pretrained(
            base_model_name,
            num_labels=len(self.id2label),
            id2label=self.id2label,
            label2id=self.label2id
        )
        
        # Load the PEFT model adapter on top of the base model
        self.model = PeftModel.from_pretrained(base_model, model_dir)
        self.model.to(self.device)
        self.model.eval() # Set model to evaluation mode
        print("Model initialized successfully!")
        
    def predict(self, question: str):
        """
        Runs inference on a single question and returns the predicted label,
        confidence, processing latency, and all class probabilities.
        """
        start_time = time.time()
        
        # Tokenize input
        inputs = self.tokenizer(question, return_tensors="pt", truncation=True, max_length=128)
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            
        predicted_idx = int(torch.argmax(logits, dim=-1).cpu().numpy()[0])
        predicted_label = self.id2label[predicted_idx]
        confidence = float(probabilities[predicted_idx])
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Class probabilities map
        class_probs = {self.id2label[i]: float(p) for i, p in enumerate(probabilities)}
        
        return {
            "predicted_label": predicted_label,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "class_probabilities": class_probs
        }

if __name__ == "__main__":
    # Small test loop for CLI usage
    print("Testing FAQClassifier inference module...")
    try:
        classifier = FAQClassifier(model_dir="./best_model")
        
        test_questions = [
            "How much is the B.Tech first semester fee?",
            "What is the eligibility for MCA admission?",
            "Is there Wi-Fi and laundry in the girls hostel?",
            "What is the date sheet for end-semester exams?"
        ]
        
        print("\n--- Running Test Questions ---")
        for q in test_questions:
            res = classifier.predict(q)
            print(f"\nQ: {q}")
            print(f"Pred: {res['predicted_label']} (Conf: {res['confidence'] * 100:.2f}%)")
            print(f"Latency: {res['latency_ms']:.2f} ms")
            
    except Exception as e:
        print(f"\nCould not run inference test: {e}")
        print("Note: This is expected if the model has not been trained yet.")
