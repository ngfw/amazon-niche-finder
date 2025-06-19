# Amazon Niche Finder

A Python tool to discover low-competition niches on Amazon by analyzing search suggestions and result counts. Perfect for authors and sellers looking to identify underserved market segments.

## Features

- 🔍 Fetches Amazon search suggestions automatically
- 📊 Analyzes search result counts for each suggestion
- 🎯 Identifies low-competition niches (under 2000 results)
- 🛡️ Built-in rate limiting and retry mechanisms
- 📝 Detailed logging for debugging

## Installation

## Installation

```bash
# Clone the repository
git clone https://github.com/ngfw/amazon-niche-finder.git
cd amazon-niche-finder

# (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
## Usage

Basic usage with default seed keyword ("coloring book for"):
```bash
python amazon_search.py
```

Specify your own seed keyword:
```bash
python amazon_search.py --seed "bold and easy"
```

## Example Output

```
INFO - 🔍 Seed: bold and easy
INFO - bold and easy coloring book → 10000 results
INFO - bold and easy coloring book for adult → 9000 results
INFO - bold and easy mandala coloring book → 1000 results
INFO - bold and easy → 10000 results
INFO - bold and easy summer coloring book → 938 results
INFO - bold and easy coloring book for kids 2-4 → 622 results
INFO - bold and easy patterns coloring book → 1000 results
INFO - bold and easy coloring → 10000 results
INFO - hygge bold and easy coloring book → 862 results
INFO - unicorn bold and easy coloring book → 212 results
...

💡 Low Competition Niches:
unicorn bold and easy coloring book → 212 results
bold and easy coloring book for kids 2-4 → 622 results
hygge bold and easy coloring book → 862 results
bold and easy summer coloring book → 938 results
bold and easy mandala coloring book → 1,000 results
bold and easy patterns coloring book → 1,000 results
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4

## Configuration

The script includes configurable parameters:
- Rate limiting delays (2-7 seconds between requests)
- Low competition threshold (< 2000 results)
- Retry strategy for failed requests
- Custom User-Agent and headers

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Be sure to comply with Amazon's terms of service and implement appropriate rate limiting when using this tool.

There is no guarantee that any discovered niche will sell or is the right niche for you. Use this tool and any results at your own risk.
