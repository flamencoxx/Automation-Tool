import re

from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, pipeline, \
    DistilBertForSequenceClassification, DistilBertTokenizer

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

app = Flask(__name__)
CORS(app)
# DistilBART 是 BART 的一个蒸馏版本，相对于原始 BART 模型，它更小、更快，性能消耗更低，但在文本摘要生成任务中仍然能保持较高的准确性。
# 模型名称：sshleifer/distilbart-cnn-12-6
# T5 (Text-to-Text Transfer Transformer):
#
# T5 是一个通用的文本生成模型，可以用于多种任务，包括文本摘要。T5 的多种变体（如 T5-base、T5-small）提供了不同的性能和准确性平衡。
# 模型名称：t5-small, t5-base
# Pegasus:
#
# Pegasus 是 Google 开发的一种专门用于生成摘要的模型。Pegasus 在多项文本摘要任务上表现优异，但由于模型较大，性能消耗也相对较高。
# 模型名称：google/pegasus-xsum, google/pegasus-large

# 加载预训练且已微调的NLP模型

# tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
# model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

# 加载 DistilBART 模型用于摘要
summarizer_model_name = "sshleifer/distilbart-cnn-12-6"
summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_model_name)
summarizer = pipeline("summarization", model=summarizer_model, tokenizer=summarizer_tokenizer)


def split_into_sentences(text):
    """使用正则表达式将文本按句子拆分"""
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
    sentences = sentence_endings.split(text)
    # 将句子中的换行符和多余空格去除
    sentences = [re.sub(r'\s+', ' ', sentence) for sentence in sentences]
    # 将超过512个token的句子拆分
    long_sentences = [sentence for sentence in sentences if
                      len(tokenizer.encode(sentence, add_special_tokens=True)) >= 512]
    short_sentences = [sentence for sentence in sentences if
                       len(tokenizer.encode(sentence, add_special_tokens=True)) < 512]

    splitted_sentences = []
    for sentence in long_sentences:
        # long_sentence_token_size = len(tokenizer.encode(sentence, add_special_tokens=True))
        long_sentence_token_size = 4 * 512
        inputs = tokenizer.encode_plus(
            sentence,
            add_special_tokens=True,
            max_length=long_sentence_token_size,
            return_attention_mask=True,
            return_overflowing_tokens=True,
            padding='max_length',
            truncation=True
        )
        num_tokens = len(inputs['input_ids'])
        num_chunks = (num_tokens + 511) // 512  # Calculate the number of chunks
        for i in range(num_chunks):
            start = i * 512
            end = min(start + 512, num_tokens)
            chunk_ids = inputs['input_ids'][start:end]
            chunk_attention_mask = inputs['attention_mask'][start:end]
            decoded_sentence = tokenizer.decode(chunk_ids, skip_special_tokens=True)
            splitted_sentences.append(decoded_sentence)
    sentences = short_sentences + splitted_sentences
    return sentences


def process_chunk(chunk):
    """处理单个文本块"""
    result = classifier(chunk)
    if result[0]['label'] == 'POSITIVE' and result[0]['score'] > 0.7:
        return chunk
    return None


def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style", "nav", "footer", "header", "link"]):
        script.extract()

    texts = list(soup.stripped_strings)
    important_texts = []

    for text in texts:
        if len(text) > 20:  # 过滤掉过短的文本
            sentences = split_into_sentences(text)
            current_chunk = []
            current_length = 0

            for sentence in sentences:
                sentence_length = len(tokenizer.encode(sentence, add_special_tokens=True))

                # 检查加入新句子是否会超过长度限制
                if current_length + sentence_length >= 512:
                    if current_chunk:
                        chunk_text = ' '.join(current_chunk)
                        processed_chunk = process_chunk(chunk_text)
                        if processed_chunk:
                            important_texts.append(processed_chunk)
                    current_chunk = [sentence]  # 开始新块
                    current_length = sentence_length
                else:
                    current_chunk.append(sentence)
                    current_length += sentence_length

            # 处理最后一个块
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                processed_chunk = process_chunk(chunk_text)
                if processed_chunk:
                    important_texts.append(processed_chunk)

    main_content = ' '.join(important_texts)
    return main_content


@app.route('/clean', methods=['POST'])
def clean_content():
    data = request.json
    html_content = data.get('content', '')
    cleaned_content = clean_html_content(html_content)
    return jsonify({'cleaned_content': cleaned_content})


@app.route('/summarize', methods=['POST'])
def summarize_content():
    data = request.json
    content = data.get('content', '')
    if len(content) > 1024:
        # 对长内容进行分块
        chunks = [content[i:i + 1024] for i in range(0, len(content), 1024)]
        summaries = [summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text'] for chunk in
                     chunks]
        summary = ' '.join(summaries)
    else:
        summary = summarizer(content, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    return jsonify({'summary': summary})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
