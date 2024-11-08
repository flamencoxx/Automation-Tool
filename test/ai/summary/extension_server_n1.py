from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from test.ai.util.WebPageContentExtractor2 import WebPageContentExtractor2

# 加载预训练的摘要模型
summarizer_model_name = "sshleifer/distilbart-cnn-12-6"
summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_model_name)

app = Flask(__name__)
CORS(app)
extractor = WebPageContentExtractor2()


def generate_summary(text, max_length=150, min_length=30):
    inputs = summarizer_tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = summarizer_model.generate(inputs, max_length=max_length, min_length=min_length, num_beams=4,
                                            early_stopping=True)
    summary = summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


@app.route('/clean', methods=['POST'])
def clean_content():
    data = request.json
    html_content = data.get('content', '')

    # extractor = WebPageContentExtractor2()
    result = extractor.extract(html_content)
    return jsonify({'cleaned_content': result})


@app.route('/summarize', methods=['POST'])
def summarize_content():
    data = request.json
    content = data.get('content', '')

    summary = generate_summary(content)

    return jsonify({'summary': summary})


if __name__ == '__main__':
    app.run(debug=True)
