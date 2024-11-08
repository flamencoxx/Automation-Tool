from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import logging
import nltk
import time
from functools import wraps

nltk.download('punkt', quiet=True)

app = Flask(__name__)
CORS(app)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局加载模型
classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
sentence_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} 执行时间: {end_time - start_time:.2f} 秒")
        return result

    return wrapper


@timer_decorator
def extract_topics(text, num_topics=5, num_words=3, max_length=10000):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")

    # 限制文本长度
    text = " ".join(text.split()[:max_length])

    try:
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
        doc_term_matrix = vectorizer.fit_transform([text])

        lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
        lda.fit(doc_term_matrix)

        words = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [words[i] for i in topic.argsort()[:-num_words - 1:-1]]
            topics.append(" ".join(top_words))
        return topics
    except Exception as e:
        logger.error(f"Error in extract_topics: {e}", exc_info=True)
        raise


def clean_html_content(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return ' '.join(soup.stripped_strings)


@timer_decorator
def summarize_text(text, max_length=1024, min_length=30):
    chunks = split_text(text, max_length)
    summaries = []
    for chunk in chunks:
        chunk_length = len(chunk.split())
        max_summary_length = min(150, max(30, chunk_length // 4))
        min_summary_length = min(30, max(10, chunk_length // 8))

        try:
            summary = summarizer(chunk,
                                 max_length=max_summary_length,
                                 min_length=min_summary_length,
                                 do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            logger.error(f"Error summarizing chunk: {e}")
            # 如果摘要失败，使用原始文本的前几句话
            sentences = nltk.sent_tokenize(chunk)
            summaries.append(" ".join(sentences[:3]))

    combined_summary = " ".join(summaries)

    # 如果合并后的摘要仍然太长，继续递归总结
    if len(combined_summary.split()) > max_length:
        return summarize_text(combined_summary, max_length, min_length)

    return combined_summary


@timer_decorator
def classify_text(text, categories, max_length=1000):
    chunks = split_text(text, max_length)
    all_results = []
    for chunk in chunks:
        try:
            result = classifier(chunk, categories)
            all_results.append(result)
        except Exception as e:
            logger.error(f"Error classifying chunk: {e}")

    # 合并所有结果
    if all_results:
        combined_result = {label: sum(r['scores'][i] for r in all_results) / len(all_results)
                           for i, label in enumerate(all_results[0]['labels'])}
        return list(sorted(combined_result.items(), key=lambda x: x[1], reverse=True))
    else:
        return []


@timer_decorator
def generate_embeddings(text, max_length=1000):
    chunks = split_text(text, max_length)
    embeddings = []
    for chunk in chunks:
        try:
            embedding = sentence_model.encode(chunk)
            embeddings.append(embedding)
        except Exception as e:
            logger.error(f"Error generating embedding for chunk: {e}")

    if embeddings:
        # 取平均值作为最终嵌入
        return np.mean(embeddings, axis=0).tolist()
    else:
        return []


def split_text(text, max_length=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        if current_length + len(word) > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


@app.route('/process', methods=['POST'])
def process_content():
    data = request.json
    html_content = data.get('content', '')
    url = data.get('url', '')

    try:
        cleaned_content = clean_html_content(html_content)
        logger.info(f"Cleaned content length: {len(cleaned_content)}")

        summary = summarize_text(cleaned_content)
        logger.info(f"Summary generated, length: {len(summary)}")

        dynamic_categories = extract_topics(cleaned_content)
        logger.info(f"Topics extracted: {dynamic_categories}")

        classifications = classify_text(cleaned_content, dynamic_categories)
        logger.info(f"Classification completed")

        embedding = generate_embeddings(cleaned_content)
        logger.info(f"Embedding generated, length: {len(embedding)}")

        result = {
            'url': url,
            'summary': summary,
            'classifications': classifications,
            'embedding': embedding
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing content for URL {url}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)