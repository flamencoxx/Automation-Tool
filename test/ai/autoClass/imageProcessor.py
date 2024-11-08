import unittest
from transformers import AutoImageProcessor, AutoBackbone
import torch
from PIL import Image
import requests


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test1(self):
        image_processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")

    def test2(self):
        url = "http://images.cocodataset.org/val2017/000000039769.jpg"
        image = Image.open(requests.get(url, stream=True).raw)
        processor = AutoImageProcessor.from_pretrained("microsoft/swin-tiny-patch4-window7-224")
        model = AutoBackbone.from_pretrained("microsoft/swin-tiny-patch4-window7-224", out_indices=(1,))

        inputs = processor(image, return_tensors="pt")
        outputs = model(**inputs)
        feature_maps = outputs.feature_maps
        print(list(feature_maps[0].shape))

    def test3(self):
        url = "http://images.cocodataset.org/val2017/000000039769.jpg"
        image = Image.open(requests.get(url, stream=True).raw)
        processor = AutoImageProcessor.from_pretrained("microsoft/deit-base-distilled-path-16-224")


if __name__ == '__main__':
    unittest.main()
