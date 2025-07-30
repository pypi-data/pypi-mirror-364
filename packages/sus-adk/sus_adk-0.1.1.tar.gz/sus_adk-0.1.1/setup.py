from setuptools import setup, find_packages

setup(
    name="sus-adk",
    version="0.1.1",
    description="A modular sus-adk for LLM interaction via cookies, inspired by LangChain and Google-ADK.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    python_requires=">=3.7",
    url="https://github.com/yourusername/agentic-framework",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 