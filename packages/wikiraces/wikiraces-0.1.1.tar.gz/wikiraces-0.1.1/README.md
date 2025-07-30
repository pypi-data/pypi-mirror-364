# WikiRaces

WikiRaces is an AI-powered tool for navigating Wikipedia using semantic similarity. Instead of randomly clicking links, it finds intelligent paths between Wikipedia articles by understanding their content semantically.

## Features

- **Semantic Navigation**: Uses sentence transformers to understand article content and find meaningful connections
- **Smart Path Finding**: Avoids dead ends and cycles while navigating toward the target
- **Real-time Progress**: Shows progress with confidence metrics and current article information
- **Robust Error Handling**: Gracefully handles missing pages, disambiguation pages, and network issues
- **Local AI Models**: No external API dependencies - everything runs locally

## Installation

```bash
pip install wikiraces
```

## Quick Start

```python
from wikiraces import WikiBot

# Create a bot to navigate from Python to Artificial Intelligence
bot = WikiBot("Python (programming language)", "Artificial intelligence")

# Run the navigation
success = bot.run()

if success:
    print(f"Found path in {len(bot.path) - 1} steps!")
    print(" -> ".join(bot.path))
else:
    print("Could not find a path")
```

## Advanced Usage

### Customize Search Parameters

```python
# Limit the number of candidate links to consider at each step
bot = WikiBot("Source Article", "Target Article", limit=20)

# Check if articles exist before starting
if bot.exists("Some Article"):
    print("Article exists!")

# Get links from any Wikipedia page
links = bot.links("Python (programming language)")
print(f"Found {len(links)} outgoing links")
```

### Semantic Similarity

```python
from wikiraces.embed import most_similar_with_scores

# Find most semantically similar articles
candidates = ["Machine Learning", "Data Science", "Web Development"]
similar = most_similar_with_scores("Artificial Intelligence", candidates)

for article, score in similar:
    print(f"{article}: {score:.3f}")
```

## How It Works

1. **Start** at the source Wikipedia article
2. **Extract** all outgoing links from the current article
3. **Filter** out dead ends and previously visited pages
4. **Rank** candidate links by semantic similarity to the target
5. **Rerank** using article summaries for better context understanding
6. **Move** to the most promising next article
7. **Repeat** until reaching the target or getting stuck

## API Reference

### WikiBot Class

```python
class WikiBot:
    def __init__(self, source: str, destination: str, limit: int = 15)
    def run() -> bool
    def exists(page: str) -> bool
    def links(page: str) -> list[str]
```

**Parameters:**
- `source`: Starting Wikipedia article title
- `destination`: Target Wikipedia article title  
- `limit`: Maximum number of candidate links to consider (default: 15)

**Returns:**
- `run()`: True if path found, False otherwise
- `exists()`: True if Wikipedia page exists
- `links()`: List of outgoing links from the page

## Development

```bash
# Clone the repository
git clone https://github.com/markshteyn/wikiraces.git
cd wikiraces

# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Run with verbose output
poetry run pytest -v -s
```

## Requirements

- Python 3.9+
- sentence-transformers
- wikipedia
- numpy
- tqdm

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [sentence-transformers](https://www.sbert.net/) for semantic understanding
- Uses the [wikipedia](https://pypi.org/project/wikipedia/) library for API access
- Progress bars powered by [tqdm](https://tqdm.github.io/)
