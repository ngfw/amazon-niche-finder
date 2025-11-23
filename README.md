# Amazon Niche Finder v2.0

A powerful Python tool to discover **profitable, low-competition niches** on Amazon through intelligent multi-level exploration, comprehensive product analysis, and smart scoring algorithms. Perfect for authors, sellers, and entrepreneurs looking to identify underserved market opportunities.

## What's New in v2.0

The tool has been completely redesigned to be **actually useful** for finding profitable niches:

- **Multi-Level Recursive Exploration**: Automatically explores keyword trees 2-3 levels deep to find hidden niches
- **Comprehensive Product Analysis**: Analyzes prices, reviews, ratings, bestseller badges, and more
- **Smart Scoring System**: Ranks niches based on competition, revenue potential, demand, and specificity
- **Multiple Category Support**: Search across 10+ Amazon categories (not just books!)
- **Price & Demand Filtering**: Filter by price range and analyze actual demand indicators
- **Real-Time Progress Tracking**: See exploration progress with live updates and score previews
- **Professional Export Options**: Export results to CSV or JSON for further analysis
- **Detailed Reports**: Get actionable insights with ranked recommendations
- **Better Decision Making**: Find niches with actual profit potential, not just low competition

## Key Features

### Intelligent Exploration
- **Recursive Keyword Discovery**: Explores keywords 2-3 levels deep automatically
- **Smart Pruning**: Skips unpromising paths to save time
- **Deduplication**: Never explores the same keyword twice
- **Progress Indicators**: See exactly what's being explored in real-time

### Comprehensive Analysis
- **Competition Score**: Analyzes result counts with smart weighting (sweet spot: 100-2000 results)
- **Price Analysis**: Average price, price range, and revenue potential scoring
- **Demand Indicators**: Review counts, bestseller badges, and customer engagement
- **Product Quality**: Average ratings and review distribution
- **Specificity Score**: Rewards longer, more specific keywords (better niches)

### Advanced Scoring Algorithm
Each niche gets a weighted overall score (0-100) based on:
- **35%** Competition (lower is better, but not too low)
- **25%** Price/Revenue Potential (higher is better)
- **20%** Demand Indicators (moderate is best)
- **20%** Specificity (more specific = better niche)

### Multi-Category Support
Search across 10+ Amazon categories:
- Books (`books`)
- Home & Garden (`home`)
- Kitchen (`kitchen`)
- Toys & Games (`toys`)
- Sports & Outdoors (`sports`)
- Electronics (`electronics`)
- Beauty & Personal Care (`beauty`)
- Pet Supplies (`pet`)
- Office Products (`office`)
- Arts & Crafts (`arts`)
- All Departments (`all`)

### Professional Exports
- **CSV Export**: Spreadsheet-ready data for analysis
- **JSON Export**: Structured data with full metadata
- **Comprehensive Reports**: Detailed text reports with recommendations

## Installation

```bash
# Clone the repository
git clone https://github.com/ngfw/amazon-niche-finder.git
cd amazon-niche-finder

# (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

Search for niches in the books category:
```bash
python amazon_search.py --seed "coloring book for"
```

### Advanced Usage Examples

**Search multiple categories:**
```bash
# Kitchen products with price filtering
python amazon_search.py --seed "coffee mug" --category kitchen --min-price 15 --max-price 50

# Sports equipment with deeper exploration
python amazon_search.py --seed "yoga mat" "resistance bands" --category sports --depth 3

# Pet products with custom threshold
python amazon_search.py --seed "dog toy" --category pet --threshold 5000
```

**Export results for analysis:**
```bash
# Export to CSV
python amazon_search.py --seed "planner" --category office --export-csv results.csv

# Export to JSON with full metadata
python amazon_search.py --seed "skin care" --category beauty --export-json results.json

# Both formats
python amazon_search.py --seed "puzzle" --category toys --export-csv niches.csv --export-json niches.json
```

**Customize scoring and filtering:**
```bash
# Show top 30 niches with score ≥ 50
python amazon_search.py --seed "sticker" --min-score 50 --top 30

# Explore 3 levels deep with lower competition threshold
python amazon_search.py --seed "notebook" --depth 3 --threshold 1000
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--seed` | Seed keyword(s) to explore (can provide multiple) | `"coloring book for"` |
| `--category` | Amazon category (books, kitchen, sports, etc.) | `books` |
| `--depth` | Exploration depth (1-5 levels) | `2` |
| `--threshold` | Max results for low competition | `2000` |
| `--min-price` | Minimum average price filter | `0` |
| `--max-price` | Maximum average price filter | `unlimited` |
| `--min-score` | Minimum overall score to display | `60` |
| `--top` | Number of top niches to show | `20` |
| `--export-csv` | Export to CSV file | None |
| `--export-json` | Export to JSON file | None |

## Example Output

```
================================================================================
🎯 Amazon Niche Finder v2.0
================================================================================
Category: kitchen
Exploration Depth: 2 levels
Competition Threshold: 2,000 results
Price Range: $15.00 - $50.00
================================================================================

🔍 Exploring: coffee mug (depth 1/2)
  🟢 Score: 78.5 | Results: 1,247 | Price: $18.99 | Reviews: 156
  ↳ Exploring: coffee mug with lid (depth 2/2)
    🟢 Score: 82.3 | Results: 892 | Price: $22.50 | Reviews: 203
  ↳ Exploring: insulated coffee mug (depth 2/2)
    🟡 Score: 71.2 | Results: 3,421 | Price: $24.99 | Reviews: 412
  ...

================================================================================
📊 DISCOVERY REPORT
================================================================================
⏱️  Duration: 127.3 seconds
🔍 Keywords Explored: 23
📦 Products Analyzed: 184
🌐 API Calls: 46
💎 Total Niches Found: 23
🏆 High-Quality Niches (score ≥ 60): 12
================================================================================

🏆 TOP 12 NICHES (Ranked by Overall Score)

================================================================================

🥇 #1: personalized coffee mug for mom
   ────────────────────────────────────────────────────────────────────────────
   Overall Score: 86.7/100
   Competition: 567 results (score: 95.0)
   Price: $26.50 avg (range: $18.99-$34.99) (score: 80.0)
   Demand: 178 avg reviews (score: 80.0)
   Rating: 4.6/5.0 stars
   🏆 2 bestseller(s) in results
   Specificity: 87.5 (more specific = better niche)
   Depth: Level 2
   Parent: coffee mug for mom

🥈 #2: coffee mug with lid and handle
   ────────────────────────────────────────────────────────────────────────────
   Overall Score: 82.3/100
   Competition: 892 results (score: 95.0)
   Price: $22.50 avg (range: $16.50-$29.99) (score: 80.0)
   Demand: 203 avg reviews (score: 80.0)
   Rating: 4.5/5.0 stars
   🏆 1 bestseller(s) in results
   Specificity: 82.5 (more specific = better niche)
   Depth: Level 2
   Parent: coffee mug with lid

...

================================================================================

💡 RECOMMENDATIONS:

   💰 Best Revenue Potential: ceramic coffee mug set
      └─ $31.99 avg price

   🎯 Lowest Competition: personalized coffee mug for mom
      └─ 567 results

   🔥 Best Demand Indicators: travel coffee mug insulated
      └─ 234 avg reviews, 3 bestsellers

📋 NEXT STEPS:
   1. Research top niches on Amazon manually to validate
   2. Check Google Trends for search volume and seasonality
   3. Analyze top competitors' products and reviews
   4. Calculate profit margins with your costs
   5. Consider starting with the highest-scored niche

================================================================================
```

## Understanding the Scores

### Overall Score (0-100)
The composite score that ranks niche quality:
- **80-100**: Excellent opportunity - low competition, good demand, strong revenue potential
- **60-79**: Good opportunity - worth investigating further
- **40-59**: Moderate opportunity - might work with the right strategy
- **0-39**: Weak opportunity - probably too competitive or low demand

### Competition Score
- **90-100**: Sweet spot (100-1000 results) - low competition with proven demand
- **70-89**: Acceptable (1000-5000 results) - competitive but manageable
- **50-69**: High competition (5000-10000 results) - challenging
- **0-49**: Very high competition (>10000 results) - difficult to rank

### Price Score
Higher prices generally mean better revenue potential:
- **100**: $50+ average price
- **95**: $30-50 average price
- **80**: $20-30 average price
- **60**: $10-20 average price
- **30**: <$10 average price

### Demand Score
Based on review counts and bestseller badges:
- **90-100**: Strong proven demand (200-500 reviews, bestsellers present)
- **70-89**: Good demand (50-200 reviews)
- **50-69**: Moderate demand (10-50 reviews)
- **20-49**: Low demand (<10 reviews or no data)

### Specificity Score
Longer, more specific keywords are better niches:
- Higher word count = more specific = less competition
- Longer character count = more detailed = better targeting

## How It Works

1. **Seed Exploration**: Starts with your seed keyword(s)
2. **Suggestion Gathering**: Fetches Amazon autocomplete suggestions
3. **Product Analysis**: Scrapes search results to extract:
   - Result counts
   - Product prices
   - Review counts and ratings
   - Bestseller badges
   - Sponsored ads
4. **Scoring**: Calculates comprehensive scores for each niche
5. **Recursive Exploration**: Uses promising keywords as new seeds
6. **Reporting**: Ranks and presents the best opportunities

## Tips for Finding Great Niches

1. **Start Broad, Go Deep**: Use general seed keywords and let the tool find specific sub-niches
2. **Multiple Seeds**: Provide 2-3 related seeds for better coverage
3. **Right Depth**: Depth 2 is usually optimal; depth 3 for thorough exploration
4. **Price Matters**: Use `--min-price` to filter out low-margin products
5. **Trust the Score**: Niches scoring 75+ are usually worth investigating
6. **Validate Manually**: Always check top results on Amazon to confirm opportunity
7. **Check Trends**: Use Google Trends to verify search volume and seasonality
8. **Analyze Competition**: Look at top competitors' reviews to find improvement opportunities

## Limitations & Best Practices

- **Rate Limiting**: Built-in delays (2-7 seconds) to avoid detection - be patient!
- **Result Count Cap**: Amazon often shows "over 10,000" which caps accuracy
- **HTML Changes**: Amazon occasionally changes their page structure
- **No Guarantee**: Low competition doesn't guarantee sales - validate demand!
- **Scraping Ethics**: Use responsibly and comply with Amazon's ToS

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- urllib3

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with Amazon's terms of service and implementing appropriate rate limiting. There is no guarantee that any discovered niche will be profitable. Always conduct thorough market research before making business decisions.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Visit [gm-sunshine.com](https://gm-sunshine.com)

---

**Made with ❤️ for entrepreneurs and sellers looking for real opportunities, not just low competition.**
