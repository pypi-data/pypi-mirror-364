from setuptools import setup, find_packages

setup(
    name='mypackage_anshita',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'ollama',
        'faiss-cpu',
        'numpy'
    ],
    author='Anshita Bhatnagar',
    author_email='your_email@example.com',
    description='A flexible chatbot package with vector embeddings and prompt handling using Ollama and FAISS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mypackage_anshita',  # Replace if you have GitHub repo
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)

