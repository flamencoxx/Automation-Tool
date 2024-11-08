from transformers import pipeline
from functools import wraps
import time
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from test.ai.util.token_split import num_tokens_from_string, split_text

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

ARTICLE = """ New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York.
A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband.
Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other.
In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage.
Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the
2010 marriage license application, according to court documents.
Prosecutors said the marriages were part of an immigration scam.
On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further.
After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective
Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002.
All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say.
Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages.
Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted.
The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s
Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali.
Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force.
If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18.
"""
ARTICLE1 = """PreludeThe COVID-19 pandemic accelerated the rise of technology and the boom of the digital age. Most 
people turned to the Internet for work and school. There has never been a better time to begin a software developer 
career.I'll explore why software development is a career worth pursuing.Is it hard to become a software developer?It 
can be challenging for most, but it is achievable with the right approach and dedication. You'll require a solid 
foundation in computer science, mathematics, and a working knowledge of programming languages.Enrolling for a 
computer science degree is the most common way to achieve this. Many online courses and boot camps are teaching these 
foundations, with many teaching free of charge.You'll need strong problem-solving, communication skills, 
and creativity to lead a successful career as a softwaredeveloper. Be willing to learn continuously, as it is an 
ever-evolving field.How many hours do software developers work? The work hours of a software engineer vary depending 
on their employer,the project they're working on, or their job station. Most developers work full-time, 
averaging about 35 to 40 hoursa week. It is common to find them working longer hours, especially when their projects 
have tight deadlines or whenthey address bugs in production.Most companies allow developers to work remotely or offer 
them flexible work schedules. This means developers can work from anywhere and adjust their hours to suit their hours 
better.Why choose a software developer career?There are numerous benefits of being a software developer. These 
include:Software developers are in high demandMore businesses and industries rely on the Internet for their 
operations. They need people who can create, maintain, and improve the software solutions that power them.Great for 
those who like problem-solvingThis career entails solving real-world problems using software. You’ll use your 
analytical skills to break down vague and seemingly complex issues into bite-sized, understandable pieces. You'll 
also employ your creativity to design and implement solutions that meet the end user's needs.Climbing the career 
ladder involves continually learning and adapting to new technologies. You'll face new and unique challenges, 
providing intellectual stimulation.Creative and collaborative profession Software developers often work in teams to 
design, build, and maintain softwareapplications. This calls for effective communication, as well as continuous 
collaboration. One popular codingtechnique is pair programming, where two developers work on the same code. 
Developers may also need to work withdesigners, product managers, and QA testers. This collaboration enhances their 
creativity, exposing them to multipleperspectives and ideas.Constantly learning something new Technology is evolving 
at a rapid pace. Software developers are familiar with thelatest industry trends and techniques to remain effective. 
This may involve learning new frameworks, libraries,tools, or programming languages.Developers learn about new 
domains, APIs, and other products. These help them understand the context in which theirapplications will be used. 
This continuous learning process can be quite rewarding for your software developer careeradvancement.Project-based 
work structure The work of a software developer is usually project-based, which means they can work onvarious tasks 
ranging from simple to complex. It requires intense focus, as they are often tasked with specific goalsand 
deadlines.The nature of their work bodes well for individuals who frown upon monotony in their work. Projects can 
vary in size and scope, which helps keep the work challenging and exciting.Ability to work remotelySoftware 
developers can work from anywhere in the world. This leads to improved job satisfaction, as individuals work in the 
environments that best suit their work styles. It also saves commuting costs and time. Remote work provides time for 
family and other personal responsibilities, improving their work-life balance.Good career ladder and salary Software 
development is a high-paying career. More than half of Glassdoor's ranking ofthe top 10 best jobs in America in 2022 
is software engineering roles. Glassdoor averages the average pay for adeveloper in the US at $85,000 per year, 
with some senior roles paying upwards of $120,000 annually.This career also offers exciting opportunities for 
advancement. Most people typically start with entry-level jobs as junior developers or software engineers. With 
experience and skills, they advance to senior developers, software architects, or technical leads.Developers can also 
move into management as project managers and engineering directors. These roles call for strategic decision-making, 
personnel management, and business acumen.Visible results and satisfactionDevelopers see the fruits of their labor 
when they deploy and launch their apps and software solutions. This results in improved job satisfaction and pride in 
their work. Nurturing such feelings has been known to inspire employee loyalty to the organization.Falls in a 
low-stress category Software development is generally considered a low-stress profession. This is becausedevelopers 
have a high degree of autonomy in their work and are not typically involved in physical labor. The risk ofinjury or 
other occupational hazards is low. Most software development work can be done remotely. This helps reducestress on 
the developer team and improve their work-life balance.Should you become a software developer? Becoming a software 
developer is one of the most highly sought-afterprofessions, and the demand is only projected to grow in the coming 
years. It is well-paying and low-stress. Itprovides numerous career advancement opportunities, and developers can 
attest to high job satisfaction. Becoming asoftware developer is worth considering."""


MODEL_NAME = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# 使用模型的最大输入长度创建 pipeline
max_input_length = model.config.max_position_embeddings - 2  # 通常是 1022 for BART
summarizer = pipeline("summarization", model=MODEL_NAME, tokenizer=tokenizer, max_length=max_input_length)


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间: {end_time - start_time:.2f} 秒")
        return result

    return wrapper


def preprocess_text(text, max_length):
    return tokenizer.encode(text, max_length=max_length, truncation=True, return_tensors="pt")


def debug_input(input_ids):
    print(f"处理后的文本长度: {input_ids.shape[1]}")
    print(f"输入张量形状: {input_ids.shape}")
    print(f"输入张量最大值: {input_ids.max().item()}")
    print(f"输入张量最小值: {input_ids.min().item()}")
    print(f"模型词汇表大小: {model.config.vocab_size}")


@timer_decorator
def custom_summarizer(text, max_length=130, min_length=30, do_sample=False):
    input_ids = preprocess_text(text, max_input_length)
    debug_input(input_ids)

    try:
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=do_sample)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"生成摘要时出错: {e}")
        return ""


@timer_decorator
def test_summarizer():
    max_tokens = 1024
    total_tokens = num_tokens_from_string(ARTICLE1)
    print(f"Total tokens: {total_tokens}")

    # 分割文本
    chunks = split_text(ARTICLE1, max_tokens)
    print(f"Number of chunks: {len(chunks)}")

    # 处理每个chunk
    for i, chunk in enumerate(chunks):
        print(summarizer(chunk, max_length=130, min_length=30, do_sample=False))


if __name__ == "__main__":
    test_summarizer()
