import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch

# 1. Load the pre-tokenized dataset
def load_pre_tokenized_data(csv_path):
    # read the CSV
    df = pd.read_csv(csv_path)
    # Converts the columns into lists
    df['input_ids'] = df['input_ids'].apply(eval)  # Converts the string into a list (input_ids)
    df['attention_mask'] = df['attention_mask'].apply(eval)  # Converts the string into a list (attention_mask)
    if 'label' in df.columns:
        df['label'] = df['label'].apply(eval if str(df['label']).startswith('[') else int)
    # Create the dataset Hugging Face
    dataset = Dataset.from_pandas(df)
    return dataset

# 2. Prepare the model
def prepare_model(num_labels):
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=num_labels)
    return model

#3. define a function to compute the evaluation metrics (accuracy in our case)
def compute_metrics(eval_pred): 
    logits, labels = eval_pred
    predictions = torch.argmax(torch.tensor(logits), dim=-1)  # Get the predicted class
    accuracy = accuracy_score(labels, predictions)  # Compute accuracy
    return {"accuracy": accuracy}

# 4. Training of the model
def train_model(train_dataset, val_dataset, model, output_dir):
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
        tokenizer=None,  # No need for tokenizer since the dataset is already tokenized
        compute_metrics=compute_metrics,  # Pass the function to compute evaluation metrics
    )

    trainer.train()

    eval_results = trainer.evaluate()
    print("Evaluation Results:", eval_results)  # This will include the accuracy


# 4. Main
def main():
    csv_path = "./tokenized_dataset_train.csv"  # path to the tokenized dataset
    dataset = load_pre_tokenized_data(csv_path)

    # split in training e validation set
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = dataset["train"]
    val_dataset = dataset["test"]

    # calculate the number of classes
    num_labels = len(set(train_dataset['label']))  # for multi-class
    model = prepare_model(num_labels)

    # training
    train_model(train_dataset, val_dataset, model, output_dir="./bert_model")

    

if __name__ == "__main__":
    main()
