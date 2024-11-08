import unittest
import json
from extension_server_9_18 import app, clean_html_content, extract_topics, generate_embedding

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_clean_html_content(self):
        html = "<html><body><h1>Test</h1><script>alert('test');</script><p>Content</p></body></html>"
        cleaned = clean_html_content(html)
        self.assertEqual(cleaned, "Test Content")

    def test_extract_topics(self):
        text = "This is a test about artificial intelligence and machine learning. " \
               "AI and ML are important fields in computer science."
        topics = extract_topics(text)
        self.assertEqual(len(topics), 5)
        self.assertTrue(any("intelligence" in topic for topic in topics))

    def test_generate_embedding(self):
        text = "这是一个测试句子"
        embedding = generate_embedding(text)
        self.assertEqual(len(embedding), 300)  # FastText模型的维度是300

    def test_process_content(self):
        data = {
            'content': "<html><body><h1>测试</h1><p>这是一个人工智能的测试。</p></body></html>",
            'url': 'http://test.com'
        }
        response = self.app.post('/process',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('url', result)
        self.assertIn('topics', result)
        self.assertIn('embedding', result)
        self.assertEqual(len(result['embedding']), 300)

if __name__ == '__main__':
    unittest.main()
