import unittest
from transformers import AutoTokenizer


class MyTestCase(unittest.TestCase):
    def test1(self):
        self.assertEqual(True, False)  # add assertion here

    def test3(self):
        tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
        sequence = "Testing this autoClass,Hello flamenco"
        print(tokenizer(sequence))

    def test2(self):
        tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")

        # 创建句子对
        sentence_1 = "How does the autoClass work?"
        sentence_2 = "It splits the text into tokens."

        # 使用分词器处理句子对
        encoded_input = tokenizer(sentence_1, sentence_2, padding=True, truncation=True, return_tensors="pt")
        print(encoded_input)


if __name__ == '__main__':
    unittest.main()
