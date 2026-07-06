import os
import json
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments,
    DataCollatorWithPadding
)
from peft import LoraConfig, get_peft_model, TaskType

# 1. Setup paths
DATA_PATH = "data/faq_dataset.csv"
OUTPUT_DIR = "./best_model"

def load_and_prepare_data(csv_path):
    """Loads CSV dataset and sets up integer labels and label mapping dictionaries."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please run generate_data.py first.")
        
    df = pd.read_csv(csv_path)
    
    # Create label mapping
    unique_labels = sorted(df["label"].unique())
    label2id = {label: idx for idx, label in enumerate(unique_labels)}
    id2label = {idx: label for idx, label in enumerate(unique_labels)}
    
    df["label_id"] = df["label"].map(label2id)
    return df, label2id, id2label

def compute_metrics(eval_pred):
    """Computes standard classification evaluation metrics."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="weighted")
    acc = accuracy_score(labels, predictions)
    
    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

def main():
    # Detect device
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"Using device for training: {device}")

    # Load data
    df, label2id, id2label = load_and_prepare_data(DATA_PATH)
    print(f"Loaded dataset with {len(df)} samples across {len(label2id)} classes.")
    
    # Stratified split: 80% train, 10% val, 10% test
    train_df, temp_df = train_test_split(
        df, 
        test_size=0.2, 
        random_state=42, 
        stratify=df["label_id"]
    )
    val_df, test_df = train_test_split(
        temp_df, 
        test_size=0.5, 
        random_state=42, 
        stratify=temp_df["label_id"]
    )
    
    print(f"Splits - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    # Load tokenizer
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Convert to HuggingFace Dataset
    def convert_to_dataset(dataframe):
        # We rename columns to fit HF Trainer expectations ('text' and 'label')
        hf_ds = Dataset.from_pandas(dataframe[["question", "label_id"]])
        hf_ds = hf_ds.rename_column("question", "text")
        hf_ds = hf_ds.rename_column("label_id", "label")
        return hf_ds

    dataset_dict = DatasetDict({
        "train": convert_to_dataset(train_df),
        "validation": convert_to_dataset(val_df),
        "test": convert_to_dataset(test_df)
    })

    # Tokenize dataset
    def preprocess_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=128)

    tokenized_datasets = dataset_dict.map(preprocess_function, batched=True)
    
    # Load base model
    print(f"Loading pretrained model: {model_name}")
    base_model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id
    )

    # Configure LoRA
    # DistilBERT target modules for self-attention are typically 'q_lin' and 'v_lin'
    peft_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        inference_mode=False,
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=["q_lin", "v_lin"],
        bias="none"
    )

    model = get_peft_model(base_model, peft_config)
    model.print_trainable_parameters()

    # Move model to device
    model.to(device)

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        learning_rate=2e-4,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_steps=10,
        warmup_ratio=0.1,
        report_to="none" # Disable logging to WandB/Tensorboard for local running
    )

    # Data collator for dynamic padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # Trainer instance
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    # Start training
    print("Starting LoRA fine-tuning...")
    trainer.train()
    print("Training complete!")

    # Evaluate on held-out test set
    print("\n--- Evaluating on Held-Out Test Set ---")
    test_results = trainer.evaluate(tokenized_datasets["test"])
    print(f"Test Accuracy: {test_results['eval_accuracy'] * 100:.2f}%")
    print(f"Test Weighted F1 Score: {test_results['eval_f1'] * 100:.2f}%")
    print(f"Test Precision: {test_results['eval_precision'] * 100:.2f}%")
    print(f"Test Recall: {test_results['eval_recall'] * 100:.2f}%")

    # Generate Confusion Matrix
    test_preds_output = trainer.predict(tokenized_datasets["test"])
    test_preds = np.argmax(test_preds_output.predictions, axis=-1)
    test_labels = test_preds_output.label_ids
    
    cm = confusion_matrix(test_labels, test_preds)
    print("\nConfusion Matrix:")
    print(cm)
    
    # Save the fine-tuned adapter weights
    print(f"\nSaving fine-tuned LoRA adapter model to: {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    # Save label mappings for inference mapping
    mapping = {
        "label2id": label2id,
        "id2label": id2label
    }
    with open(os.path.join(OUTPUT_DIR, "label_mapping.json"), "w") as f:
        json.dump(mapping, f, indent=4)
        
    # Check save file sizes to demonstrate the LoRA parameter savings
    adapter_weights_path = os.path.join(OUTPUT_DIR, "adapter_model.safetensors")
    if os.path.exists(adapter_weights_path):
        size_mb = os.path.getsize(adapter_weights_path) / (1024 * 1024)
        print(f"LoRA Adapter Weights file size: {size_mb:.2f} MB")
    else:
        # Check bin files if safetensors isn't default
        bin_path = os.path.join(OUTPUT_DIR, "adapter_model.bin")
        if os.path.exists(bin_path):
            size_mb = os.path.getsize(bin_path) / (1024 * 1024)
            print(f"LoRA Adapter Weights file size: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()
