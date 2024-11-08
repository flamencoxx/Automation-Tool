import re
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import yaml
import logging

app = Flask(__name__)
CORS(app)

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 动态加载模型
def load_model(model_name, task):
    return pipeline(task, model=model_name)


summarizer = load_model(config['summarizer_model'], "summarization")
classifier = load_model(config['classifier_model'], "zero-shot-classification")
sentence_model = SentenceTransformer(config['sentence_transformer_model'])

# 配置参数
REMOVE_TAGS = config['remove_tags']
MAX_CHUNK_LENGTH = config['max_chunk_length']
SUMMARY_MAX_LENGTH = config['summary_max_length']
SUMMARY_MIN_LENGTH = config['summary_min_length']


def clean_html_content(content):
    try:
        if not content:
            return ""

        # 使用正则表达式移除多余的空白字符
        content = re.sub(r'\s+', ' ', content).strip()

        # 如果内容看起来像HTML，则使用BeautifulSoup进行进一步处理
        if '<' in content and '>' in content:
            soup = BeautifulSoup(content, "html.parser")
            for element in soup(REMOVE_TAGS):
                element.decompose()
            return ' '.join(soup.stripped_strings)

        return content
    except Exception as e:
        logger.error(f"Error cleaning content: {e}")
        return ""


def split_into_chunks(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    chunks = []
    current_chunk = []
    current_length = 0
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length <= MAX_CHUNK_LENGTH:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks


def summarize_text(text):
    chunks = split_into_chunks(text)
    with ThreadPoolExecutor() as executor:
        summaries = list(executor.map(
            lambda chunk:
            summarizer(chunk, max_length=SUMMARY_MAX_LENGTH, min_length=SUMMARY_MIN_LENGTH, do_sample=False)[0][
                'summary_text'],
            chunks
        ))
    return ' '.join(summaries)


def classify_text(text, categories):
    result = classifier(text, categories)
    return result['labels'][0], result['scores'][0]


def generate_embeddings(text):
    return sentence_model.encode(text)


def cluster_bookmarks(embeddings, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(embeddings)


@app.route('/clean', methods=['POST'])
def clean_content():
    data = request.json
    content = data.get('content', '')
    cleaned_content = clean_html_content(content)
    return jsonify({'cleaned_content': cleaned_content})


@app.route('/process', methods=['POST'])
def process_content():
    data = request.json
    html_content = data.get('content', '')
    url = data.get('url', '')
    categories = data.get('categories', config['default_categories'])

    cleaned_content = clean_html_content(html_content)
    summary = summarize_text(cleaned_content)
    category, confidence = classify_text(cleaned_content, categories)
    embedding = generate_embeddings(cleaned_content).tolist()

    result = {
        'url': url,
        'summary': summary,
        'category': category,
        'confidence': confidence,
        'embedding': embedding
    }
    return jsonify(result)


# 定义一个路由，用于接收POST请求，路径为'/cluster'
@app.route('/cluster', methods=['POST'])
def cluster_content():
    """
    对传入的书签进行聚类处理。

    该视图函数接收一个JSON格式的请求体，其中包含'embeddings'和'n_clusters'字段。
    'embeddings'字段是一个向量集合，代表待聚类的书签的嵌入表示。
    'n_clusters'字段指定需要形成的聚类数量，如果未提供，则使用配置文件中的默认值。

    返回一个JSON响应，包含聚类结果，如果输入的embeddings为空，则返回错误信息。
    """
    # 从请求体中提取数据
    data = request.json
    # 将提取的embeddings转换为NumPy数组，以便进行聚类操作
    embeddings = np.array(data.get('embeddings', []))
    # 获取聚类数量，首先尝试从请求数据中获取，如果不存在，则使用配置文件中的默认值
    n_clusters = data.get('n_clusters', config['default_n_clusters'])

    # 检查是否提供了embeddings，如果没有提供，则返回一个错误响应
    if len(embeddings) == 0:
        return jsonify({'error': 'No embeddings provided'}), 400

    # 对embeddings进行聚类，然后将结果转换为列表格式，以便于JSON序列化
    clusters = cluster_bookmarks(embeddings, n_clusters).tolist()
    # 返回聚类结果的JSON格式响应
    return jsonify({'clusters': clusters})


if __name__ == '__main__':
    app.run(debug=True)
