import re
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from transformers import pipeline


class WebPageContentExtractor2:
    def __init__(self, min_length=80, max_gap=40):
        self.min_length = min_length
        self.max_gap = max_gap
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def preprocess(self, content):
        # Check if content is HTML-like
        if '<html' in content.lower() or '<body' in content.lower():
            soup = BeautifulSoup(content, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else ''

            # Remove unwanted elements
            for elem in soup.find_all(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                elem.decompose()

            # Extract body or use whole soup if no body tag
            body = soup.body if soup.body else soup

        else:
            # Treat content as plain text
            soup = BeautifulSoup(f"<html><body>{content}</body></html>", 'html.parser')
            title = ''
            body = soup.body

        # Extract and clean text
        text = body.get_text(separator='\n', strip=True)

        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip().split()) >= self.min_length]

        return title, paragraphs

    def extract_keywords(self, paragraphs, top_n=10):
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(paragraphs)
        terms = vectorizer.get_feature_names_out()
        tfidf_scores = X.sum(axis=0).A1
        top_keyword_indexes = tfidf_scores.argsort()[-top_n:][::-1]
        top_keywords = [terms[i] for i in top_keyword_indexes]

        lda = LatentDirichletAllocation(n_components=3, random_state=42)
        lda.fit(X)
        topic_keywords = lda.components_.argsort()[:, -top_n:]
        topic_keywords = [[terms[i] for i in topic] for topic in topic_keywords]

        return top_keywords, topic_keywords

    def generate_summary(self, paragraphs, min_length=60, max_length=200):
        inputs = self.summarizer.tokenizer(paragraphs, max_length=1024, truncation=True)
        summary_ids = self.summarizer.model.generate(
            inputs["input_ids"], num_beams=4, min_length=min_length,
            max_length=max_length, early_stopping=True)
        summary = self.summarizer.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary

    def extract(self, html_content):
        title, paragraphs = self.preprocess(html_content)
        top_keywords, topic_keywords = self.extract_keywords(paragraphs)
        # summary = self.generate_summary(paragraphs)

        return {
            'title': title,
            'main_content': '\n'.join(paragraphs),
            'top_keywords': top_keywords,
            'topic_keywords': topic_keywords,
            # 'summary': summary

        }

