import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
from joblib import load

app = Flask(__name__)
CORS(app)

class DistilBertInferencer:
    def __init__(self, trained_model_dir):
        # Carica il modello addestrato e il tokenizer dalla cartella fornita
        self.model = DistilBertForSequenceClassification.from_pretrained(trained_model_dir)
        self.tokenizer = DistilBertTokenizer.from_pretrained(trained_model_dir)
        
        # Inizializza il device (GPU se disponibile, altrimenti CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Carica l'encoder per decodificare le etichette
        self.label_encoder = LabelEncoder()
        self.load_label_encoder(trained_model_dir)  # Carica l'encoder dalla directory del modello

    def load_label_encoder(self, model_dir):
        # Il LabelEncoder viene salvato nella directory del modello
        encoder_path = os.path.join(model_dir, "label_encoder.pkl")
        if os.path.exists(encoder_path):
            self.label_encoder = load(encoder_path)
            print("LabelEncoder caricato correttamente.")
        else:
            print(f"Warning: Label encoder not found at {encoder_path}. Inference may be incorrect.")
            # Fallback per allenare un nuovo LabelEncoder con etichette predefinite
            all_possible_labels = [...]
            self.label_encoder.fit(all_possible_labels)
            print("LabelEncoder allenato con etichette predefinite.")

    def predict(self, text):
        # Preprocessing del testo
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        
        # Ottieni le predizioni
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Ottieni i primi 3 indici con le probabilità più alte
        topk_values, topk_indices = torch.topk(torch.softmax(outputs.logits, dim=-1), k=3)
        
        # Decodifica gli indici nei rispettivi subreddit
        predicted_subreddits = self.label_encoder.inverse_transform(topk_indices.cpu().numpy().flatten())
        
        # Converte le probabilità in una lista leggibile
        confidences = topk_values.cpu().numpy().flatten().tolist()
        
        # Restituisce un dizionario con subreddit e relative probabilità
        return [{"subreddit": subreddit, "confidence": confidence} for subreddit, confidence in zip(predicted_subreddits, confidences)]


# Inizializza il modello per l'inferenza
trained_model_dir = './results_bs_8_lr_5e-05_run1'  # Inserisci il percorso corretto della cartella del modello
inferencer = DistilBertInferencer(trained_model_dir)

@app.route('/predict', methods=['POST'])
def predict():
    # Ottieni i dati dal corpo della richiesta (JSON)
    data = request.get_json()
    
    # Controlla se 'title' è presente nella richiesta
    if 'title' not in data:
        return jsonify({'error': 'Title not provided'}), 400
    
    title = data['title']
    
    # Fai la previsione
    predicted_subreddits = inferencer.predict(title)
    print(predicted_subreddits)
    
    # Restituisci il risultato come JSON
    return jsonify({'predicted_subreddits': predicted_subreddits})


if __name__ == "__main__":
    app.run(debug=True)
