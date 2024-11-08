import unittest

from transformers import pipeline
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test1(self):
        classifier = pipeline("sentiment-analysis")
        classifier("We are very happy to show you the 🤗 Transformers library.")

    def test2(self):
        tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

        inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits

        predicted_class_id = logits.argmax().item()
        var = model.config.id2label[predicted_class_id]
        print(var)
        



if __name__ == '__main__':
    unittest.main()
