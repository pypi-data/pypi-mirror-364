# mypackage_anshita

`mypackage_anshita` is a Python package built with Ollama models to provide:

- Prompt-based text generation using models like `gemma:2b`, `llama2`, and others.
- Vector-based document embedding and semantic search with FAISS.
- Flexibility to use different models for generation and embeddings.

## Installation

Install the package via PyPI:

```bash
pip install mypackage-anshita
Features

PromptRunner: Run prompts on various Ollama models.
DocumentEmbedder: Embed documents and perform vector search.
Integration with Ollama, FAISS, and NumPy.
Supports multiple Ollama models, including Gemma and LLaMA2.

Usage Example

Generate Text
from mypackage_anshita import PromptRunner

runner = PromptRunner(model='gemma:2b')
response = runner.run_prompt("What is the theory of relativity?")
print(response)
from mypackage_anshita import DocumentEmbedder

docs = [
    "Marie Curie won two Nobel Prizes.",
    "Einstein created the theory of relativity."
]

embedder = DocumentEmbedder()
embedder.embed_text(docs)

results = embedder.search("radioactivity")
print(results)
Author

Anshita Bhatnagar
Built during internship using LangChain, Ollama, FAISS, and Streamlit.

License

MIT License
