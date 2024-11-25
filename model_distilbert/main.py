import pandas as pd
import torch

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizer
from transformers import DistilBertForSequenceClassification
from transformers import Trainer, TrainingArguments


# preprocessing
df = pd.read_csv('dataset.csv')
df = df.dropna().drop_duplicates()
print(df['name'].value_counts())

texts = df['title'].tolist()
labels = df['name'].tolist()

label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)


label_mapping = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
print(label_mapping)

X_train, X_test, y_train, y_test = train_test_split(texts, encoded_labels, test_size=0.2, random_state=42)

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

train_encodings = tokenizer(X_train, truncation=True, padding=True, max_length=128)
test_encodings = tokenizer(X_test, truncation=True, padding=True, max_length=128)


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


train_dataset = RedditDataset(train_encodings, y_train)
test_dataset = RedditDataset(test_encodings, y_test)

num_classes = len(label_mapping)

# model
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=num_classes)

training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    logging_dir='./logs',
    logging_steps=10,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

trainer.train()

results = trainer.evaluate()
print(results)

# save model
model.save_pretrained('./subreddit_model')
tokenizer.save_pretrained('./subreddit_tokenizer')


# load model
model = DistilBertForSequenceClassification.from_pretrained('./subreddit_model')
tokenizer = DistilBertTokenizer.from_pretrained('./subreddit_tokenizer')

# inference
print(torch.backends.mps.is_available())
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
model = model.to(device)


def predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs = {key: val.to(device) for key, val in inputs.items()}
    outputs = model(**inputs)
    predicted_class = torch.argmax(outputs.logits).item()
    predicted_subreddit = label_encoder.inverse_transform([predicted_class])
    print(f"Suggestion: {predicted_subreddit[0]}")


while True:
    text = input("Enter a title: ")
    predict(text)
