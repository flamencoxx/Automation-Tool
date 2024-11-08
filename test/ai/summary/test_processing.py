import unittest
import time

from test.ai.summary.extension_server_9_18 import generate_embedding, extract_topics, clean_html_content


class TestProcessingMethods(unittest.TestCase):

    def setUp(self):
        self.sample_html = """
        <html>
            <head>
                <title>Sample Page</title>
            </head>
            <body>
                <h1>Welcome to the Sample Page</h1>
                <p>This is a paragraph about artificial intelligence and machine learning. 
                These technologies are revolutionizing various industries.</p>
                <script>console.log("This should be removed");</script>
                <p>Another paragraph about data science and its applications in business analytics.</p>
            </body>
        </html>
        """
        self.sample_text = "Artificial intelligence and machine learning are transforming industries. " \
                           "Data science is being applied in business analytics to derive insights. " \
                           "Natural language processing is a key component of modern AI systems. " \
                           "Deep learning models are achieving state-of-the-art results in various tasks. " \
                           "The ethical implications of AI are being widely discussed in academia and industry."

    def time_method(self, method, *args):
        start_time = time.time()
        result = method(*args)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{method.__name__} execution time: {execution_time:.4f} seconds")
        return result, execution_time

    def test_clean_html_content(self):
        cleaned_content, execution_time = self.time_method(clean_html_content, self.sample_html)
        self.assertIn("Welcome to the Sample Page", cleaned_content)
        self.assertNotIn("<script>", cleaned_content)
        self.assertLess(execution_time, 0.1, "HTML cleaning took too long")

    def test_extract_topics(self):
        topics, execution_time = self.time_method(extract_topics, self.sample_text)
        self.assertEqual(len(topics), 5)
        self.assertIn("learning", ' '.join(topics))
        self.assertLess(execution_time, 1.0, "Topic extraction took too long")

    def test_generate_embedding(self):
        embedding, execution_time = self.time_method(generate_embedding, self.sample_text)
        self.assertEqual(len(embedding), 300)  # Assuming FastText model with 300 dimensions
        self.assertIsInstance(embedding[0], float)
        self.assertLess(execution_time, 0.1, "Embedding generation took too long")

if __name__ == '__main__':
    unittest.main()
