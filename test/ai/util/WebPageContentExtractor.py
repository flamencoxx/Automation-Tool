import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


class WebPageContentExtractor:
    def __init__(self, n_topics=3, min_length=80, max_gap=40):
        self.n_topics = n_topics
        self.min_length = min_length
        self.max_gap = max_gap

    def preprocess(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else ''
        blocks = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 0:
                blocks.append({
                    'text': text,
                    'len': len(text),
                    'pos': p.sourceline
                })
        return title, blocks

    def identify_topic(self, title, blocks):
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform([b['text'] for b in blocks])
        kmeans = KMeans(n_clusters=self.n_topics, random_state=42)
        kmeans.fit(X)
        terms = vectorizer.get_feature_names_out()
        topic_keywords = []
        for i in range(self.n_topics):
            topic_terms = [terms[j] for j in kmeans.cluster_centers_[i].argsort()[::-1][:10]]
            topic_keywords.append(topic_terms)
        main_topic = 0
        max_overlap = 0
        for i, keywords in enumerate(topic_keywords):
            overlap = sum([1 for k in keywords if k in title])
            if overlap > max_overlap:
                max_overlap = overlap
                main_topic = i
        return topic_keywords[main_topic]

    def score_block(self, block, topic_keywords):
        len_score = min(1.0, block['len'] / 100)
        pos_score = 1.0 - (block['pos'] / 1000)
        topic_score = sum([1 for k in topic_keywords if k in block['text']]) / len(topic_keywords)
        score = 0.2 * len_score + 0.3 * pos_score + 0.5 * topic_score
        return score

    def find_main_blocks(self, blocks, topic_keywords):
        scores = [self.score_block(b, topic_keywords) for b in blocks]
        main_blocks = []
        start = 0
        while start < len(blocks):
            if scores[start] > 0.5:
                end = start + 1
                while end < len(blocks) and scores[end] > 0.5 and blocks[end]['pos'] - blocks[end - 1][
                    'pos'] <= self.max_gap:
                    end += 1
                if sum([b['len'] for b in blocks[start:end]]) >= self.min_length:
                    main_blocks.append(blocks[start:end])
                start = end
            else:
                start += 1
        return main_blocks

    def postprocess(self, main_blocks):
        main_content = '\n'.join(['\n'.join([b['text'] for b in bs]) for bs in main_blocks])
        main_content = re.sub(r'\n+', '\n', main_content).strip()
        return main_content

    def extract(self, html):
        title, blocks = self.preprocess(html)
        topic_keywords = self.identify_topic(title, blocks)
        main_blocks = self.find_main_blocks(blocks, topic_keywords)
        main_content = self.postprocess(main_blocks)
        return main_content
