# Contributing to AI Stock Advisor

We love your input! We want to make contributing to AI Stock Advisor as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests Process

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/yourusername/ai-stock-advisor/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/ai-stock-advisor/issues/new).

### Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. Clone your fork of the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Download spaCy model: `python -m spacy download en_core_web_sm`
6. Set up your NewsAPI key: `export NEWS_API_KEY="your_key"`
7. Run the app: `streamlit run app.py`

## Coding Style

- We use Python's PEP 8 style guide
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Use type hints where appropriate

Example:
```python
def analyze_sentiment(self, ticker: str, company_name: str) -> Dict[str, Any]:
    """
    Analyze sentiment for a stock using news data.
    
    Args:
        ticker: Stock ticker symbol
        company_name: Full company name
        
    Returns:
        Dictionary containing sentiment analysis results
    """
    # Implementation here
```

## Project Structure Guidelines

- **agents/**: Core analysis agents (screening, fundamental, sentiment, aggregator)
- **utils/**: Utility classes (cache manager, data normalizer)
- **tests/**: Unit tests (when we add them)
- **docs/**: Additional documentation

## Adding New Features

### New Sectors
1. Add sector to the sectors dictionary in `app.py`
2. Ensure stock tickers are valid for Indian market (add .NS suffix if needed)
3. Test with different stock counts

### New Analysis Metrics
1. Add metric calculation to appropriate agent
2. Update data normalizer if score normalization is needed
3. Add metric to display in results cards
4. Update documentation

### New Data Sources
1. Create new agent if it's a major data source
2. Add to utils if it's a supporting function
3. Implement caching for API calls
4. Add error handling and fallbacks

## Testing

While we don't have comprehensive tests yet, please ensure:

- Your code doesn't break existing functionality
- All agents return expected data structures
- Error handling works for API failures
- Cache system functions properly

## Code Review Process

1. All changes must be made through pull requests
2. Maintainers will review for:
   - Code quality and style
   - Performance implications
   - Security considerations
   - Documentation completeness
3. At least one approval required before merge

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for questions about contributing!