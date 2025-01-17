import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
import csv
import os
import joblib

class RedditDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item


class DistilBertTrainer:
    def __init__(self, train_mode=True, output_dir='./results', trained_model_dir=None, batch_size=16, epochs=3,
                 learning_rate=2e-5):
        self.df = pd.read_csv('dataset.csv')
        self.df = self.df.dropna().drop_duplicates()
        print(self.df['name'].value_counts())

        self.texts = self.df['title'].tolist()
        self.labels = self.df['name'].tolist()

        if train_mode:
            self.label_encoder = LabelEncoder()
            self.encoded_labels = self.label_encoder.fit_transform(self.labels)

            # Save LabelEncoder
            os.makedirs(output_dir, exist_ok=True)
            label_encoder_path = os.path.join(output_dir, 'label_encoder.pkl')
            joblib.dump(self.label_encoder, label_encoder_path)
            print(f"Label encoder saved to {label_encoder_path}")

            self.label_mapping = dict(zip(self.label_encoder.classes_, range(len(self.label_encoder.classes_))))
            print(self.label_mapping)

            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.texts, self.encoded_labels, test_size=0.2, random_state=42)
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

            self.train_encodings = self.tokenizer(self.X_train, truncation=True, padding=True, max_length=128)
            self.test_encodings = self.tokenizer(self.X_test, truncation=True, padding=True, max_length=128)

            self.train_dataset = RedditDataset(self.train_encodings, self.y_train)
            self.test_dataset = RedditDataset(self.test_encodings, self.y_test)

            self.num_classes = len(self.label_mapping)

            self.model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=self.num_classes)

            self.training_args = TrainingArguments(
                output_dir=output_dir,
                evaluation_strategy='epoch',
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                num_train_epochs=epochs,
                logging_dir='./logs',
                logging_steps=10,
                learning_rate=learning_rate
            )

            self.trainer = Trainer(
                model=self.model,
                args=self.training_args,
                train_dataset=self.train_dataset,
                eval_dataset=self.test_dataset,
            )

            self.trainer.train()
            self.results = self.trainer.evaluate()
            print(self.results)
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)

        else:
            if not trained_model_dir:
                raise ValueError("NO MODEL DIRECTORY PROVIDED!")

            # Load LabelEncoder
            label_encoder_path = os.path.join(trained_model_dir, 'label_encoder.pkl')
            if not os.path.exists(label_encoder_path):
                raise ValueError(f"Label encoder not found in {label_encoder_path}")
            self.label_encoder = joblib.load(label_encoder_path)
            print(f"Label encoder loaded from {label_encoder_path}")

            self.model = DistilBertForSequenceClassification.from_pretrained(trained_model_dir)
            self.tokenizer = DistilBertTokenizer.from_pretrained(trained_model_dir)

            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")

            self.model = self.model.to(self.device)

            while True:
                text = input("Enter a title: ")
                self.predict(text)

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        outputs = self.model(**inputs)
        predicted_class = torch.argmax(outputs.logits).item()
        predicted_subreddit = self.label_encoder.inverse_transform([predicted_class])
        print(f"Suggestion: {predicted_subreddit[0]}")

    # Logging for SPSS
    def log_detailed_results(self, batch_size, learning_rate, run_id):
        os.makedirs(self.training_args.output_dir, exist_ok=True)

        predictions = self.trainer.predict(self.test_dataset)
        true_labels = predictions.label_ids
        pred_probs = predictions.predictions
        pred_labels = np.argmax(pred_probs, axis=1)

        residuals = pred_probs[np.arange(len(true_labels)), true_labels] - 1

        results_df = pd.DataFrame({
            'Batch Size': [batch_size] * len(true_labels),
            'Learning Rate': [learning_rate] * len(true_labels),
            'True Label': true_labels,
            'Predicted Label': pred_labels,
            'Residual': residuals,
        })

        accuracy = (true_labels == pred_labels).mean()
        precision = precision_score(true_labels, pred_labels, average='weighted')
        recall = recall_score(true_labels, pred_labels, average='weighted')

        summary_df = pd.DataFrame([{
            'Batch Size': batch_size,
            'Learning Rate': learning_rate,
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'Mean Residual': residuals.mean(),
            'Residual Variance': residuals.var(),
        }])

        detailed_results_path = os.path.join(
            self.training_args.output_dir, 
            f'detailed_results_bs_{batch_size}_lr_{learning_rate}_run_{run_id}.csv'
        )
        results_df.to_csv(detailed_results_path, index=False)

        summary_results_path = os.path.join(
            self.training_args.output_dir,
            f'summary_results.csv'
        )
        summary_df.to_csv(summary_results_path, mode='a', index=False, header=not os.path.exists(summary_results_path))

        print(f"Detailed Results Saved to: {detailed_results_path}")
        print(f"Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")

def training():        
    batch_size = 8
    learning_rate = 5e-5
    run_id = 1

    directory = f"./results_bs_{batch_size}_lr_{learning_rate}_run{run_id}"
    print(f"Training started for batch size: {batch_size}, learning rate: {learning_rate}, run: {run_id}")
    trainer = DistilBertTrainer(output_dir=directory, batch_size=batch_size, learning_rate=learning_rate)
    trainer.log_detailed_results(batch_size, learning_rate, run_id)
    print(f"Training completed for batch size: {batch_size}, learning rate: {learning_rate}, run: {run_id}")

def inference():
    inferencer = DistilBertTrainer(train_mode=False, trained_model_dir='./subreddit_model')

if __name__ == "__main__":
    import sys
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    print("Is CUDA available?", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA Device Name:", torch.cuda.get_device_name(0))
    else:
        print("No GPU detected.")
    print("PyTorch version:", torch.__version__)
    if len(sys.argv) < 2:
        raise ValueError("Please provide mode: train or inference")
    mode = sys.argv[1]
    if mode == "train":
        training()
    elif mode == "inference":
        inference()
    else:
        raise ValueError("Invalid mode. Please provide either train or inference")
