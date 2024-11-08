from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import torch
from transformers import LongformerTokenizer, LongformerModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import logging
from functools import lru_cache

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载预训练的Longformer模型
MODEL_NAME = "allenai/longformer-base-4096"
tokenizer = LongformerTokenizer.from_pretrained(MODEL_NAME)
model = LongformerModel.from_pretrained(MODEL_NAME)
model.eval()  # 设置为评估模式

# 初始化TF-IDF向量化器和LDA
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
lda = LatentDirichletAllocation(n_components=5, random_state=42)

@lru_cache(maxsize=100)
def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return ' '.join(soup.stripped_strings)

def extract_topics(text, num_topics=5):
    tfidf_matrix = vectorizer.fit_transform([text])
    lda.fit(tfidf_matrix)
    terms = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_terms = [terms[i] for i in topic.argsort()[:-4:-1]]
        topics.append(" ".join(top_terms))
    return topics[:num_topics]

def generate_embedding(text):
    # 将文本分成多个chunk，每个chunk最多4000个token
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    embeddings = []

    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", max_length=4096, truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        chunk_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings.append(chunk_embedding)

    # 取所有chunk嵌入的平均值
    final_embedding = np.mean(embeddings, axis=0)
    return final_embedding.tolist()

@app.route('/process', methods=['POST'])
def process_content():
    data = request.json
    html_content = data.get('content', '')
    url = data.get('url', '')

    try:
        cleaned_content = clean_html_content(html_content)
        logger.info(f"Cleaned content length: {len(cleaned_content)}")

        topics = extract_topics(cleaned_content)
        logger.info(f"Topics extracted: {topics}")

        embedding = generate_embedding(cleaned_content)
        logger.info(f"Embedding generated, length: {len(embedding)}")

        result = {
            'url': url,
            'topics': topics,
            'embedding': embedding
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing content for URL {url}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
