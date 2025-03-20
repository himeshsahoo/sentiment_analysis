from operator import index
import numpy as np
from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import mimetypes
from scipy.special import softmax
from decouple import config
from collections import Counter

app = Flask(__name__)
HUGGINGFACE_CACHE_DIR = config("HUGGINGFACE_CACHE_DIR", '')
TORCH_CACHE_DIR = config("TORCH_CACHE_DIR", '')
os.environ['TORCH_HOME'] = TORCH_CACHE_DIR

SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
token = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")

    elif request.method == "POST":
        input_type = request.form.get("type")
        input_text = ""

        if input_type == "text":
            input_text = request.form.get("input")
        elif input_type == "media":
            file = request.files.get("input")
            input_label = request.form.get
            9
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.root_path, 'static', 'files', filename)
                file.save(file_path)
                input_text = process_files(file_path)

        sentiment_analysis = find_text_sentiment_analysis(input_text)
        return jsonify(sentiment_analysis)


def process_files(file_path):
    mime_type, encoding = mimetypes.guess_type(file_path)
    if mime_type:
        type, subtype = mime_type.split('/', 1)
        return f"Processed file of type {type}/{subtype}"
    return "Unknown file type"


def chunk_text(text, max_len=510):
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_len:
            if current_chunk:
                current_chunk += " "
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def find_text_sentiment_analysis(input_text):
    chunks = chunk_text(input_text)
    sentiment_dicts = []

    for chunk in chunks:
        encoded_text = token(chunk, return_tensors="pt", padding=True, truncation=True)
        output = model(**encoded_text)
        scores = output.logits.detach().numpy()[0]
        scores = softmax(scores)

        val_neg = float(scores[0])
        val_neu = float(scores[1])
        val_pos = float(scores[2])

        if val_neg > val_pos and val_neg > val_neu:
            prominent_sentiment = "NEGATIVE"
        elif val_pos > val_neg and val_pos > val_neu:
            prominent_sentiment = "POSITIVE"
        else:
            prominent_sentiment = "NEUTRAL"

        sentiment_dicts.append({
            "score_negative": val_neg,
            "score_neutral": val_neu,
            "score_positive": val_pos,
            "prominent_sentiment": prominent_sentiment
        })

    avg_sentiment_dict = {
        "score_negative": str(np.mean([d["score_negative"] for d in sentiment_dicts])),
        "score_neutral": str(np.mean([d["score_neutral"] for d in sentiment_dicts])),
        "score_positive": str(np.mean([d["score_positive"] for d in sentiment_dicts])),
        "prominent_sentiment": Counter([d["prominent_sentiment"] for d in sentiment_dicts]).most_common(1)[0][0]
    }

    return avg_sentiment_dict




if __name__ == "__main__":
    app.run(debug=True)
