import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score
from transformers import AlbertForSequenceClassification, AlbertTokenizer, Trainer, TrainingArguments
import torch

# 1. Load the pre-tokenized dataset
def load_pre_tokenized_data(csv_path):
    # Read the CSV
    df = pd.read_csv(csv_path)
    # Converts the columns into lists
    df['input_ids'] = df['input_ids'].apply(eval)  # Converts the string into a list (input_ids)
    df['attention_mask'] = df['attention_mask'].apply(eval)  # Converts the string into a list (attention_mask)
    if 'label' in df.columns:
        df['label'] = df['label'].apply(eval if str(df['label']).startswith('[') else int)
    df['max_token_id'] = df['input_ids'].apply(lambda x: max(x))
    print("--------------------------------------------")
    print("Max token ID in dataset:", df['max_token_id'].max())
    print("--------------------------------------------")

    # Create the Hugging Face dataset
    dataset = Dataset.from_pandas(df)
    return dataset

# 2. Prepare the tokenizer and model
def prepare_model_and_tokenizer(num_labels):
    tokenizer = AlbertTokenizer.from_pretrained("albert-base-v2")
    model = AlbertForSequenceClassification.from_pretrained("albert-base-v2", num_labels=num_labels)
    return model, tokenizer

# 3. Define a function to compute the evaluation metrics (accuracy in our case)
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = torch.argmax(torch.tensor(logits), dim=-1)  # Get the predicted class
    accuracy = accuracy_score(labels, predictions)  # Compute accuracy
    return {"accuracy": accuracy}

# 4. Training of the model
def train_model(train_dataset, val_dataset, model, tokenizer, output_dir):
    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2,
        logging_dir="./logs",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,  # Pass the tokenizer for validation and decoding
        compute_metrics=compute_metrics,  # Pass the function to compute evaluation metrics
    )

    trainer.train()

    eval_results = trainer.evaluate()
    print("Evaluation Results:", eval_results)  # This will include the accuracy

# 5. Main
def main():
    csv_path = "./tokenized_dataset_train.csv"  # Path to the tokenized dataset
    dataset = load_pre_tokenized_data(csv_path)

    # Split into training and validation sets
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = dataset["train"]
    val_dataset = dataset["test"]

    # Calculate the number of classes
    num_labels = len(set(train_dataset['label']))  # For multi-class
    model, tokenizer = prepare_model_and_tokenizer(num_labels)

    # Training
    train_model(train_dataset, val_dataset, model, tokenizer, output_dir="./albert_model")

if __name__ == "__main__":
    main()
