# AIWand 🪄

> **One API to rule them all** - Unified OpenAI and Gemini interface with automatic provider switching and structured data extraction from anywhere.

[![PyPI version](https://img.shields.io/pypi/v/aiwand.svg)](https://pypi.org/project/aiwand/)
[![Python versions](https://img.shields.io/pypi/pyversions/aiwand.svg)](https://pypi.org/project/aiwand/)
[![License](https://img.shields.io/pypi/l/aiwand.svg)](https://github.com/onlyoneaman/aiwand/blob/main/LICENSE)
[![Coverage Status](https://img.shields.io/badge/coverage-100%25-success)](https://github.com/onlyoneaman/aiwand/actions?query=workflow%3ACI)
[![Downloads](https://pepy.tech/badge/aiwand)](https://pepy.tech/project/aiwand)
[![Downloads](https://pepy.tech/badge/aiwand/month)](https://pepy.tech/project/aiwand/month)
[![Downloads](https://pepy.tech/badge/aiwand/week)](https://pepy.tech/project/aiwand/week)

## 🎯 **Two Powerful Features, One Simple API**

### 1. **`call_ai`** - Unified AI Interface

**Drop-in replacement for OpenAI and Gemini** - Same code works with both providers, automatic model detection, and structured output magic.

```python
import aiwand
from pydantic import BaseModel

# Works with any model - provider auto-detected
response = aiwand.call_ai(
    model="gpt-4o",              # or "gemini-2.0-flash"
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

# Structured output with Pydantic - no JSON parsing needed!
class BlogPost(BaseModel):
    title: str
    content: str
    tags: list[str]

blog = aiwand.call_ai(
    model="gemini-2.0-flash",
    messages=[{"role": "user", "content": "Write a blog about AI"}],
    response_format=BlogPost    # Returns BlogPost object directly!
)
print(blog.title)  # Direct access, no parsing
```

### 2. **`extract`** - Smart Data Extraction

**Pass any content or links** - Extracts structured data from text, URLs, files, or mixed sources. Creates or uses your Pydantic models.

```python
# Extract from text
contact = aiwand.extract(content="John Doe, john@example.com, (555) 123-4567")

# Extract from URLs or files
data = aiwand.extract(links=["https://company.com/about", "resume.pdf"])

# Mix content + links with custom structure
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str

result = aiwand.extract(
    content="Meeting notes: call John tomorrow",
    links=["https://company.com/team", "business_card.txt"],
    response_format=ContactInfo  # Get ContactInfo object back
)
```

## 🚀 Quick Start

### Installation & Setup

```bash
pip install aiwand

# Set your API key (either one works)
export OPENAI_API_KEY="your-key"     # or
export GEMINI_API_KEY="your-key"     # or both
```

### Core Usage

```python
import aiwand

# 1. Basic AI calls - auto provider selection
response = aiwand.call_ai(
    model="gpt-4o",  # Uses OpenAI
    messages=[{"role": "user", "content": "Hello!"}]
)

response = aiwand.call_ai(
    model="gemini-2.0-flash",  # Uses Gemini  
    messages=[{"role": "user", "content": "Hello!"}]
)

# 2. Extract data from anywhere
contact = aiwand.extract(content="Dr. Sarah Johnson, sarah@lab.com")
webpage_data = aiwand.extract(links=["https://example.com"])
mixed_data = aiwand.extract(
    content="Meeting notes...",
    links=["document.pdf", "https://site.com"]
)
```

## ✨ **Key Benefits**

| Feature | Benefit |
|---------|---------|
| 🔄 **Provider Agnostic** | Same code works with OpenAI and Gemini |
| 🏗️ **Structured Output** | Get Pydantic objects directly, no JSON parsing |
| 🧠 **Smart Detection** | Automatic provider selection based on model |
| 📄 **Universal Extraction** | Extract from text, URLs, files - anything |
| ⚡ **Zero Configuration** | Works with just API keys |
| 🎯 **Drop-in Ready** | Minimal code changes from existing AI code |

## 🔧 **Advanced Examples**

### Smart Provider Switching

```python
# Automatic provider detection
responses = []
for model in ["gpt-4o", "gemini-2.0-flash", "o3-mini"]:
    response = aiwand.call_ai(
        model=model,  # Auto-detects OpenAI vs Gemini
        messages=[{"role": "user", "content": "Compare yourself to other AI models"}]
    )
    responses.append(f"{model}: {response}")

# Force specific provider for custom models
response = aiwand.call_ai(
    model="my-custom-model",
    provider="gemini",  # Explicit override
    messages=[{"role": "user", "content": "Test custom model"}]
)
```

### Structured Data Extraction

```python
from pydantic import BaseModel
from typing import List

class CompanyInfo(BaseModel):
    name: str
    founded: int
    employees: int
    technologies: List[str]
    headquarters: str

# Extract from company website
company = aiwand.extract(
    links=["https://company.com/about"],
    response_format=CompanyInfo
)

# Extract from mixed sources
analysis = aiwand.extract(
    content="Research on tech companies in 2024",
    links=[
        "https://techcrunch.com/company-news",
        "market_report.pdf",
        "/path/to/notes.txt"
    ],
    response_format=CompanyInfo
)
```

### Built-in Convenience Functions

```python
# High-level functions for common tasks
summary = aiwand.summarize("Long article text...", style="bullet-points")
response = aiwand.chat("What is machine learning?")
story = aiwand.generate_text("Write a poem about coding")

# Classification and grading
grader = aiwand.create_binary_classifier(criteria="correctness")
result = grader(question="What is 2+2?", answer="4", expected="4")
print(f"Score: {result.score}")
```

## 🎨 CLI Usage

```bash
# Direct chat (quoted for multi-word)
aiwand "Explain quantum computing in simple terms"

# Extract from content
aiwand extract "John Doe, john@example.com" --json

# Extract from URLs/files  
aiwand extract --links https://company.com resume.pdf

# Other functions
aiwand summarize "Long text..." --style bullet-points
aiwand chat "Hello there!"
```

## 📚 Documentation

- **[API Reference](docs/api-reference.md)** - Complete function docs
- **[CLI Guide](docs/cli.md)** - Command line usage
- **[Installation](docs/installation.md)** - Setup details
- **[Development](docs/development.md)** - Contributing guide

## 🔑 **Why AIWand?**

**Before AIWand** - Provider-specific code, manual JSON parsing, complex setup:
```python
# OpenAI specific
import openai
response = openai.chat.completions.create(...)
result = json.loads(response.choices[0].message.content)  # Manual parsing

# Gemini specific  
import google.generativeai as genai
response = genai.generate_content(...)
result = parse_json_response(response.text)  # Different API
```

**After AIWand** - One API, automatic everything:
```python
import aiwand
result = aiwand.call_ai(model="any-model", response_format=MyModel, ...)
# result is already a MyModel object! ✨
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Star this repo if you find it useful!

**Made with ❤️ by [Aman Kumar](https://x.com/onlyoneaman)** 