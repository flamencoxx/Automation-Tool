import tiktoken


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def split_text(text: str, max_tokens: int = 1024, encoding_name: str = "cl100k_base") -> list:
    """Split the text into chunks, each with at most max_tokens."""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunks.append(encoding.decode(chunk))

    return chunks

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



if __name__ == "__main__":
    # 使用示例
    text = "Your long text here..."
    max_tokens = 1024

    # 计算总token数
    total_tokens = num_tokens_from_string(ARTICLE1)
    print(f"Total tokens: {total_tokens}")

    # 分割文本
    chunks = split_text(ARTICLE1, max_tokens)
    print(f"Number of chunks: {len(chunks)}")

    # 处理每个chunk
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}")
        # 这里可以添加您的处理逻辑，例如发送到AI模型