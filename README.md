# NEW_HYBRID_RAG

A hybrid Retrieval-Augmented Generation (RAG) system that combines multiple retrieval strategies to enhance LLM-powered question answering capabilities.

## Overview

This project implements a sophisticated RAG pipeline that leverages hybrid search techniques to provide more accurate and contextually relevant responses. It processes PDF documents, extracts relevant information, and uses intelligent retrieval mechanisms to augment LLM responses with factual, cited context.

## Features

- **Hybrid Retrieval**: Combines multiple search strategies for improved context retrieval
- **PDF Processing**: Efficient handling and processing of PDF documents
- **Vector Search**: Semantic search using embeddings
- **Smart Caching**: Cached results for improved performance
- **LLM Integration**: Seamless integration with language models for response generation

## Project Structure

```
NEW_HYBRID_RAG/
├── src/                    # Source code modules
├── data/
│   └── pdfs/              # PDF documents for RAG
├── cache/                  # Cached embeddings and results
├── main.py                # Main entry point
├── pyproject.toml         # Project configuration (uv)
├── requirements.txt       # Dependencies list
├── uv.lock               # Lock file for reproducible builds
├── .python-version       # Python version specification
└── README.md            # This file
```

## Prerequisites

- Python 3.11+ (specified in `.python-version`)
- [uv package manager](https://docs.astral.sh/uv/) installed on your system

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nkushwanth/NEW_HYBRID_RAG.git
cd NEW_HYBRID_RAG
```

### 2. Install Python (if needed)

If you don't have Python 3.11+ installed, uv can manage it for you:

```bash
uv python install
```

### 3. Sync Dependencies

Using uv, sync all dependencies to a local virtual environment:

```bash
uv sync
```

This command will:
- Create a `.venv` directory with a virtual environment
- Install all dependencies specified in `pyproject.toml`
- Lock versions according to `uv.lock`

## Usage

### Running the Application

Execute the main script using uv:

```bash
uv run main.py
```

Or if you prefer to activate the virtual environment manually:

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the script
python main.py
```

### Adding PDFs

Place your PDF documents in the `data/pdfs/` directory:

```bash
cp path/to/your/document.pdf data/pdfs/
```

### Cache Management

The `cache/` directory stores:
- Processed embeddings
- Cached search results
- Intermediate computations

Clear the cache to force reprocessing:

```bash
rm -rf cache/*
```

## Configuration

Edit `pyproject.toml` to modify:
- Project metadata (name, version, description)
- Python version requirements
- Dependency specifications

Example `pyproject.toml` structure:

```toml
[project]
name = "new-hybrid-rag"
version = "0.1.0"
description = "Hybrid RAG system for intelligent document retrieval"
requires-python = ">=3.11"

[dependencies]
# Core dependencies listed here
```

## Development

### Code Structure

The `src/` directory contains the core modules:
- RAG retrieval logic
- LLM integration
- PDF processing utilities
- Embedding generation

### Best Practices

- Use `uv sync` to maintain consistent environments across team members

## Performance Tips

1. **Pre-cache Embeddings**: First run will be slower as embeddings are generated and cached
2. **Batch Processing**: Process multiple PDFs efficiently using the caching system
3. **Memory Management**: Clear cache periodically for large document sets
4. **Vector Search**: Adjust search parameters in configuration for speed/accuracy tradeoff

## Troubleshooting

### Issue: Dependencies not installing
```bash
# Clear cache and resync
rm uv.lock
uv sync
```

### Issue: Python version mismatch
```bash
# Check current Python version
python --version

# Install the correct version
uv python install 3.11
```

### Issue: Cache corruption
```bash
# Clear the cache directory
rm -rf cache/*

# Resync dependencies
uv sync
```

## API Keys and Environment Variables

If your project requires API keys (OpenAI, Anthropic, etc.), create a `.env` file    I PERSONALLY USED GROQ_API_KEY:

```bash
# Create .env file
cp .env.example .env

# Add your API keys
#GROQ_API_KEY=your_key_ere
```

**Note**: Add `.env` to `.gitignore` to avoid committing secrets.

## Performance Benchmarks

The system is optimized for:
- Processing up to 100+ PDF documents
- Vector search with millisecond latency (with caching)
- Batch query processing for scalability


## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Virtual Environments](https://docs.python.org/3/library/venv.html)
- [RAG Best Practices](https://docs.langchain.com/docs/use_cases/q_and_a/)

## Acknowledgments

This project uses modern Python tooling and industry-standard libraries for RAG implementation.

---

**Last Updated**: 2026  
**Maintainer**: nkushwanth
