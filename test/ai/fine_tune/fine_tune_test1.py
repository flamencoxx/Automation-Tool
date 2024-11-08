import unittest

from transformers import AutoModelForSequenceClassification
from datasets import load_dataset


class MyTestCase(unittest.TestCase):

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test1(self):
        dataset = load_dataset("yelp_review_full")
        arg0 = dataset["train"][100]
        print(arg0)

    def test2(self):
        model = AutoModelForSequenceClassification.from_pretrained("google-bert/bert-base-cased", num_labels=5)


if __name__ == '__main__':
    unittest.main()
