
# ArXiv MCP Server

A comprehensive Model Context Protocol (MCP) server for accessing and analyzing research papers from ArXiv. Provides advanced search capabilities, paper analysis, and citation management tools.

## Implemented MCP Capabilities

| Capability | Type | Description |
|------------|------|-------------|
| `search_arxiv` | Tool | Search papers by category (e.g., 'cs.AI', 'physics.astro-ph') |
| `get_recent_papers` | Tool | Get recent papers from a specific ArXiv category |
| `search_papers_by_author` | Tool | Search papers by author name |
| `search_by_title` | Tool | Search papers by title keywords |
| `search_by_abstract` | Tool | Search papers by abstract keywords |
| `search_by_subject` | Tool | Search papers by subject classification |
| `search_date_range` | Tool | Search papers within a specific date range |
| `get_paper_details` | Tool | Get detailed information about a specific paper |
| `export_to_bibtex` | Tool | Export search results to BibTeX format |
| `find_similar_papers` | Tool | Find papers similar to a reference paper |

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iowarp/scientific-mcps.git
   cd scientific-mcps/Arxiv
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Test the installation:**
   ```bash
   uv run python demo.py
   ```

### Running the Server

```bash
# Using the script
uv run arxiv-mcp

# Direct execution
uv run python src/arxiv_mcp/server.py
```

## Usage Examples

### Search by Category
```python
# Search for recent AI papers
search_arxiv("cs.AI", max_results=5)
```

### Search by Title
```python
# Find papers about machine learning
search_by_title("machine learning", max_results=10)
```

### Get Paper Details
```python
# Get details for a specific paper
get_paper_details("1706.03762")  # Attention Is All You Need
```

### Export to BibTeX
```python
# Export search results for citation
export_to_bibtex(papers_list)
```

## Common ArXiv Categories

- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CV` - Computer Vision and Pattern Recognition
- `cs.CL` - Computation and Language
- `cs.CR` - Cryptography and Security
- `physics.astro-ph` - Astrophysics
- `math.CO` - Combinatorics
- `q-bio.QM` - Quantitative Methods

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_category_search.py
uv run pytest tests/test_integration.py

# Run with verbose output
uv run pytest -v
```

## Configuration

The server supports environment variables:

- `MCP_TRANSPORT`: Transport type (`stdio` or `sse`)
- `MCP_SSE_HOST`: Host for SSE transport (default: `0.0.0.0`)
- `MCP_SSE_PORT`: Port for SSE transport (default: `8000`)

## Integration with MCP Clients

### Claude Desktop
Add to your configuration:
```json
{
  "arxiv-mcp": {
    "command": "uv",
    "args": [
      "--directory", "/path/to/scientific-mcps/Arxiv",
      "run", "arxiv-mcp"
    ]
  }
}
```

### Other MCP Clients
The server uses stdio transport by default and is compatible with any MCP client.

## Project Structure

```
Arxiv/
├── README.md
├── pyproject.toml
├── demo.py
├── docs/
│   └── basic_install.md
├── assets/
├── data/
├── src/
│   └── arxiv_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── mcp_handlers.py
│       └── capabilities/
│           ├── __init__.py
│           ├── arxiv_base.py
│           ├── category_search.py
│           ├── text_search.py
│           ├── date_search.py
│           ├── paper_details.py
│           └── export_utils.py
└── tests/
    ├── __init__.py
    ├── test_capabilities.py
    ├── test_mcp_handlers.py
    ├── test_category_search.py
    ├── test_text_search.py
    ├── test_paper_details.py
    ├── test_export_utils.py
    └── test_integration.py
```

## Features

- **Advanced Search**: Multiple search methods including category, title, abstract, author, and date range
- **Paper Analysis**: Detailed paper information and similarity detection
- **Citation Management**: BibTeX export for research bibliography
- **Comprehensive Testing**: Full test coverage with integration tests
- **Error Handling**: Robust error handling with informative messages
- **Async Support**: Fully asynchronous for optimal performance

## Documentation

- [Installation Guide](docs/basic_install.md)
- [API Documentation](src/arxiv_mcp/capabilities/)
- [Test Examples](tests/)

## License

MIT License - see the main repository for details.
