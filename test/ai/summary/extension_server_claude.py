import re
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, pipeline

app = Flask(__name__)
CORS(app)

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

summarizer_model_name = "sshleifer/distilbart-cnn-12-6"
summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_model_name)
summarizer = pipeline("summarization", model=summarizer_model, tokenizer=summarizer_tokenizer)


def split_into_chunks(text, max_length=512):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    current_chunk = []
    chunks = []
    for sentence in sentences:
        if len(tokenizer.encode(" ".join(current_chunk + [sentence]))) <= max_length:
            current_chunk.append(sentence)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def process_chunk(chunk):
    if len(tokenizer.encode(chunk)) > 512:
        chunk = tokenizer.decode(tokenizer.encode(chunk)[:512])
    result = classifier(chunk)
    if result[0]['label'] == 'POSITIVE' and result[0]['score'] > 0.7:
        return chunk
    return None


def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style", "nav", "footer", "header", "link"]):
        script.extract()

    sentences = list(soup.stripped_strings)
    chunks = split_into_chunks(" ".join(sentences))

    with ThreadPoolExecutor() as executor:
        cleaned_chunks = list(executor.map(process_chunk, chunks))

    cleaned_chunks = [chunk for chunk in cleaned_chunks if chunk is not None]
    return " ".join(cleaned_chunks)


@app.route('/clean', methods=['POST'])
def clean_content():
    data = request.json
    html_content = data.get('content', '')
    cleaned_content = clean_html_content(html_content)
    return jsonify({'cleaned_content': cleaned_content})


@app.route('/summarize', methods=['POST'])
def summarize_content():
    data = request.json
    content = data.get('content', '')

    if len(content) <= 1024:
        summary = summarizer(content, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    else:
        chunks = split_into_chunks(content, 1024)
        with ThreadPoolExecutor() as executor:
            summaries = list(
                executor.map(lambda x: summarizer(x, max_length=150, min_length=30, do_sample=False)[0]['summary_text'],
                             chunks))
        summary = ' '.join(summaries)

    return jsonify({'summary': summary})


if __name__ == '__main__':
    app.run(debug=True)
