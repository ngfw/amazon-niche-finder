#!/usr/bin/env python3
"""
Amazon Niche Finder - Discover profitable low-competition niches on Amazon.
Author: Nick G.
Version: 2.0
Website: gm-sunshine.com
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random
import logging
import re
import argparse
import json
import csv
from typing import List, Dict, Tuple, Optional, Set
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

# Configuration Constants
MAX_RETRIES = 3
BACKOFF_FACTOR = 1
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
REQUEST_TIMEOUT = 10
MIN_DELAY = 2
MAX_DELAY = 7
LOW_COMPETITION_THRESHOLD = 2000
DEFAULT_EXPLORATION_DEPTH = 2  # How many levels deep to explore
MIN_PRODUCTS_TO_ANALYZE = 5  # Minimum products to analyze for price/review data
MAX_PRODUCTS_TO_ANALYZE = 20  # Maximum products to analyze

# Niche scoring weights
SCORE_WEIGHTS = {
    'competition': 0.35,      # Lower competition is better
    'price': 0.25,            # Higher price is better (more revenue potential)
    'reviews': 0.20,          # Moderate reviews is best (demand exists, not saturated)
    'specificity': 0.20       # More specific keywords are better
}

# Amazon categories to explore
CATEGORIES = {
    'books': 'stripbooks',
    'home': 'garden',
    'kitchen': 'kitchen',
    'toys': 'toys-and-games',
    'sports': 'sporting-goods',
    'electronics': 'electronics',
    'beauty': 'beauty',
    'pet': 'pet-supplies',
    'office': 'office-products',
    'arts': 'arts-crafts',
    'all': 'aps'
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('amazon_niche_finder.log')
    ]
)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}

@dataclass
class ProductData:
    """Data structure for individual product information"""
    price: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_bestseller: bool = False
    is_sponsored: bool = False
    title: Optional[str] = None

@dataclass
class NicheData:
    """Comprehensive data structure for a niche"""
    keyword: str
    result_count: int
    avg_price: Optional[float] = None
    price_range: Optional[Tuple[float, float]] = None
    avg_reviews: Optional[int] = None
    avg_rating: Optional[float] = None
    bestseller_count: int = 0
    sponsored_count: int = 0
    specificity_score: float = 0.0
    competition_score: float = 0.0
    price_score: float = 0.0
    demand_score: float = 0.0
    overall_score: float = 0.0
    depth_level: int = 1
    parent_keyword: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for export"""
        data = asdict(self)
        if self.price_range:
            data['price_range'] = f"${self.price_range[0]:.2f} - ${self.price_range[1]:.2f}"
        return data

class NicheFinder:
    """Main class for finding and analyzing Amazon niches"""

    def __init__(self, category: str = 'books', depth: int = DEFAULT_EXPLORATION_DEPTH,
                 min_price: float = 0, max_price: float = float('inf'),
                 competition_threshold: int = LOW_COMPETITION_THRESHOLD):
        self.category = CATEGORIES.get(category, 'stripbooks')
        self.category_name = category
        self.depth = depth
        self.min_price = min_price
        self.max_price = max_price
        self.competition_threshold = competition_threshold
        self.session = self._create_session()
        self.explored_keywords: Set[str] = set()
        self.all_niches: List[NicheData] = []
        self.stats = {
            'keywords_explored': 0,
            'api_calls': 0,
            'products_analyzed': 0,
            'start_time': None,
            'end_time': None
        }

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_CODES
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(HEADERS)
        return session

    def _delay(self):
        """Random delay to avoid rate limiting"""
        time.sleep(MIN_DELAY + random.random() * (MAX_DELAY - MIN_DELAY))

    def get_suggestions(self, seed: str) -> List[str]:
        """Get keyword suggestions from Amazon autocomplete"""
        try:
            url = "https://completion.amazon.com/api/2017/suggestions"
            params = {
                "limit": "11",
                "prefix": seed,
                "suggestion-type[]": ["WIDGET", "KEYWORD"],
                "page-type": "Detail",
                "alias": self.category,
                "site-variant": "desktop",
                "version": "3",
                "event": "onkeypress",
                "wc": "",
                "lop": "en_US",
                "last-prefix": "",
                "avg-ks-time": "1989",
                "fb": "1",
                "session-id": "137-1927523-7967027",
                "client-info": "search-ui",
                "mid": "ATVPDKIKX0DER",
                "plain-mid": "1",
            }

            # Build URL with array parameters
            param_parts = []
            for key, value in params.items():
                if isinstance(value, list):
                    for v in value:
                        param_parts.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(v)}")
                else:
                    param_parts.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(str(value))}")

            full_url = f"{url}?{'&'.join(param_parts)}"
            response = self.session.get(full_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self.stats['api_calls'] += 1

            data = response.json()
            if isinstance(data, dict) and "suggestions" in data:
                return [item["value"] for item in data["suggestions"] if "value" in item]
            return []

        except Exception as e:
            logger.error(f"Error fetching suggestions for '{seed}': {str(e)}")
            return []

    def analyze_products(self, keyword: str, soup: BeautifulSoup) -> List[ProductData]:
        """Extract product data from search results page"""
        products = []

        try:
            # Find all product cards
            product_cards = soup.find_all("div", {"data-component-type": "s-search-result"})

            for card in product_cards[:MAX_PRODUCTS_TO_ANALYZE]:
                product = ProductData()

                # Extract title
                title_elem = card.find("h2", {"class": "s-line-clamp-2"})
                if title_elem:
                    product.title = title_elem.get_text(strip=True)

                # Extract price
                price_whole = card.find("span", {"class": "a-price-whole"})
                price_fraction = card.find("span", {"class": "a-price-fraction"})
                if price_whole:
                    try:
                        whole = price_whole.get_text(strip=True).replace(',', '').replace('.', '')
                        fraction = price_fraction.get_text(strip=True) if price_fraction else '00'
                        product.price = float(f"{whole}.{fraction}")
                    except (ValueError, AttributeError):
                        pass

                # Extract rating
                rating_elem = card.find("span", {"class": "a-icon-alt"})
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    match = re.search(r'(\d+\.?\d*)\s+out of', rating_text)
                    if match:
                        product.rating = float(match.group(1))

                # Extract review count
                review_elem = card.find("span", {"class": "a-size-base", "dir": "auto"})
                if review_elem:
                    review_text = review_elem.get_text(strip=True).replace(',', '')
                    match = re.search(r'(\d+)', review_text)
                    if match:
                        product.review_count = int(match.group(1))

                # Check for bestseller badge
                bestseller = card.find("span", string=re.compile(r'Best Seller', re.I))
                product.is_bestseller = bool(bestseller)

                # Check for sponsored
                sponsored = card.find("span", string=re.compile(r'Sponsored', re.I))
                product.is_sponsored = bool(sponsored)

                products.append(product)
                self.stats['products_analyzed'] += 1

        except Exception as e:
            logger.error(f"Error analyzing products for '{keyword}': {str(e)}")

        return products

    def get_result_count(self, soup: BeautifulSoup) -> int:
        """Extract result count from search page"""
        try:
            selectors = [
                ("span", {"data-component-type": "s-result-info-bar"}),
                ("div", {"class": "sg-col-inner"}),
                ("div", {"class": "a-section a-spacing-small a-spacing-top-small"})
            ]

            for tag, attrs in selectors:
                result_text = soup.find(tag, attrs)
                if result_text:
                    text = result_text.get_text()
                    patterns = [
                        r'(\d[\d,]*)\s+results',
                        r'(\d[\d,]*)\s+Results',
                        r'over\s+(\d[\d,]*)',
                        r'(\d[\d,]*)\s+product'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, text)
                        if match:
                            return int(match.group(1).replace(',', ''))
            return -1

        except Exception as e:
            logger.error(f"Error extracting result count: {str(e)}")
            return -1

    def analyze_niche(self, keyword: str, depth: int = 1, parent: Optional[str] = None) -> Optional[NicheData]:
        """Comprehensive analysis of a niche keyword"""

        # Skip if already explored
        if keyword in self.explored_keywords:
            return None

        self.explored_keywords.add(keyword)
        self.stats['keywords_explored'] += 1

        try:
            # Fetch search results page
            search_url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(keyword)}"
            if self.category != 'aps':
                search_url += f"&i={self.category}"

            response = self.session.get(search_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self.stats['api_calls'] += 1

            soup = BeautifulSoup(response.text, 'html.parser')

            # Get result count
            result_count = self.get_result_count(soup)
            if result_count == -1:
                logger.warning(f"Could not get result count for: {keyword}")
                return None

            # Analyze products
            products = self.analyze_products(keyword, soup)

            # Calculate niche metrics
            niche = NicheData(
                keyword=keyword,
                result_count=result_count,
                depth_level=depth,
                parent_keyword=parent
            )

            # Price analysis
            prices = [p.price for p in products if p.price and self.min_price <= p.price <= self.max_price]
            if prices:
                niche.avg_price = sum(prices) / len(prices)
                niche.price_range = (min(prices), max(prices))

            # Review analysis
            reviews = [p.review_count for p in products if p.review_count]
            if reviews:
                niche.avg_reviews = int(sum(reviews) / len(reviews))

            # Rating analysis
            ratings = [p.rating for p in products if p.rating]
            if ratings:
                niche.avg_rating = sum(ratings) / len(ratings)

            # Bestseller and sponsored counts
            niche.bestseller_count = sum(1 for p in products if p.is_bestseller)
            niche.sponsored_count = sum(1 for p in products if p.is_sponsored)

            # Calculate scores
            niche.specificity_score = self._calculate_specificity_score(keyword)
            niche.competition_score = self._calculate_competition_score(result_count)
            niche.price_score = self._calculate_price_score(niche.avg_price)
            niche.demand_score = self._calculate_demand_score(niche.avg_reviews, niche.bestseller_count)
            niche.overall_score = self._calculate_overall_score(niche)

            return niche

        except Exception as e:
            logger.error(f"Error analyzing niche '{keyword}': {str(e)}")
            return None

    def _calculate_specificity_score(self, keyword: str) -> float:
        """Calculate how specific/niche a keyword is (longer = more specific)"""
        words = keyword.split()
        word_count = len(words)
        char_count = len(keyword)

        # More words and longer keywords are more specific
        score = min(100, (word_count * 15) + (char_count * 0.5))
        return score

    def _calculate_competition_score(self, result_count: int) -> float:
        """Calculate competition score (lower results = higher score)"""
        if result_count <= 0:
            return 0

        # Logarithmic scale - sweet spot is 100-2000 results
        if result_count < 100:
            return 40  # Too niche, might not have demand
        elif result_count < 500:
            return 100
        elif result_count < 1000:
            return 95
        elif result_count < 2000:
            return 85
        elif result_count < 5000:
            return 70
        elif result_count < 10000:
            return 50
        else:
            return max(0, 50 - (result_count - 10000) / 500)

    def _calculate_price_score(self, avg_price: Optional[float]) -> float:
        """Calculate price score (higher price = better revenue potential)"""
        if not avg_price:
            return 50  # Neutral score if no price data

        # Higher prices are better for revenue, but diminishing returns
        if avg_price < 10:
            return 30
        elif avg_price < 20:
            return 60
        elif avg_price < 30:
            return 80
        elif avg_price < 50:
            return 95
        else:
            return 100

    def _calculate_demand_score(self, avg_reviews: Optional[int], bestseller_count: int) -> float:
        """Calculate demand score (reviews indicate sales)"""
        score = 50  # Base score

        # Review count indicates demand
        if avg_reviews:
            if avg_reviews < 10:
                score = 20  # Very low demand
            elif avg_reviews < 50:
                score = 50
            elif avg_reviews < 200:
                score = 80  # Sweet spot
            elif avg_reviews < 500:
                score = 90
            else:
                score = 70  # High demand but might be saturated

        # Bestseller badges boost demand score
        if bestseller_count > 0:
            score = min(100, score + (bestseller_count * 5))

        return score

    def _calculate_overall_score(self, niche: NicheData) -> float:
        """Calculate weighted overall score"""
        score = (
            niche.competition_score * SCORE_WEIGHTS['competition'] +
            niche.price_score * SCORE_WEIGHTS['price'] +
            niche.demand_score * SCORE_WEIGHTS['reviews'] +
            niche.specificity_score * SCORE_WEIGHTS['specificity']
        )
        return round(score, 2)

    def explore_recursive(self, seed: str, current_depth: int = 1, parent: Optional[str] = None):
        """Recursively explore keywords to specified depth"""

        if current_depth > self.depth:
            return

        # Progress indicator
        indent = "  " * (current_depth - 1)
        print(f"{indent}{'🔍' if current_depth == 1 else '↳'} Exploring: {seed} (depth {current_depth}/{self.depth})")

        # Analyze current keyword
        self._delay()
        niche = self.analyze_niche(seed, current_depth, parent)

        if niche:
            self.all_niches.append(niche)

            # Display quick info
            score_emoji = "🟢" if niche.overall_score >= 75 else "🟡" if niche.overall_score >= 50 else "🔴"
            print(f"{indent}  {score_emoji} Score: {niche.overall_score:.1f} | Results: {niche.result_count:,} | "
                  f"Price: ${niche.avg_price:.2f if niche.avg_price else 0:.2f} | "
                  f"Reviews: {niche.avg_reviews if niche.avg_reviews else 0}")

        # Get suggestions for next level (only if competition is promising)
        if current_depth < self.depth and (not niche or niche.result_count < self.competition_threshold * 10):
            self._delay()
            suggestions = self.get_suggestions(seed)

            # Explore top suggestions
            for suggestion in suggestions[:5]:  # Limit to top 5 to avoid explosion
                if suggestion not in self.explored_keywords:
                    self.explore_recursive(suggestion, current_depth + 1, seed)

    def find_niches(self, seed_keywords: List[str]):
        """Main method to find niches from seed keywords"""
        self.stats['start_time'] = datetime.now()

        print(f"\n{'='*80}")
        print(f"🎯 Amazon Niche Finder v2.0")
        print(f"{'='*80}")
        print(f"Category: {self.category_name}")
        print(f"Exploration Depth: {self.depth} levels")
        print(f"Competition Threshold: {self.competition_threshold:,} results")
        print(f"Price Range: ${self.min_price:.2f} - ${self.max_price:.2f}")
        print(f"{'='*80}\n")

        for seed in seed_keywords:
            self.explore_recursive(seed)

        self.stats['end_time'] = datetime.now()

    def get_top_niches(self, limit: int = 20, min_score: float = 60) -> List[NicheData]:
        """Get top scoring niches"""
        filtered = [n for n in self.all_niches if n.overall_score >= min_score]
        return sorted(filtered, key=lambda x: x.overall_score, reverse=True)[:limit]

    def export_csv(self, filename: str, niches: Optional[List[NicheData]] = None):
        """Export niches to CSV file"""
        if niches is None:
            niches = self.all_niches

        if not niches:
            logger.warning("No niches to export")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'keyword', 'overall_score', 'result_count', 'avg_price', 'price_range',
                'avg_reviews', 'avg_rating', 'bestseller_count', 'competition_score',
                'price_score', 'demand_score', 'specificity_score', 'depth_level', 'parent_keyword'
            ])
            writer.writeheader()
            for niche in niches:
                writer.writerow(niche.to_dict())

        logger.info(f"Exported {len(niches)} niches to {filename}")

    def export_json(self, filename: str, niches: Optional[List[NicheData]] = None):
        """Export niches to JSON file"""
        if niches is None:
            niches = self.all_niches

        if not niches:
            logger.warning("No niches to export")
            return

        data = {
            'timestamp': datetime.now().isoformat(),
            'category': self.category_name,
            'stats': self.stats,
            'niches': [niche.to_dict() for niche in niches]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Exported {len(niches)} niches to {filename}")

    def print_report(self, top_niches: List[NicheData]):
        """Print a comprehensive report"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        print(f"\n{'='*80}")
        print(f"📊 DISCOVERY REPORT")
        print(f"{'='*80}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"🔍 Keywords Explored: {self.stats['keywords_explored']}")
        print(f"📦 Products Analyzed: {self.stats['products_analyzed']}")
        print(f"🌐 API Calls: {self.stats['api_calls']}")
        print(f"💎 Total Niches Found: {len(self.all_niches)}")
        print(f"🏆 High-Quality Niches (score ≥ 60): {len([n for n in self.all_niches if n.overall_score >= 60])}")
        print(f"{'='*80}\n")

        if not top_niches:
            print("❌ No high-quality niches found. Try:")
            print("   - Different seed keywords")
            print("   - Lower the minimum score threshold")
            print("   - Increase exploration depth")
            print("   - Try a different category")
            return

        print(f"🏆 TOP {len(top_niches)} NICHES (Ranked by Overall Score)\n")
        print(f"{'='*80}\n")

        for i, niche in enumerate(top_niches, 1):
            score_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "💎"

            print(f"{score_emoji} #{i}: {niche.keyword}")
            print(f"   {'─'*76}")
            print(f"   Overall Score: {niche.overall_score:.1f}/100")
            print(f"   Competition: {niche.result_count:,} results (score: {niche.competition_score:.1f})")

            if niche.avg_price:
                print(f"   Price: ${niche.avg_price:.2f} avg (range: ${niche.price_range[0]:.2f}-${niche.price_range[1]:.2f}) (score: {niche.price_score:.1f})")
            else:
                print(f"   Price: No data available")

            if niche.avg_reviews:
                print(f"   Demand: {niche.avg_reviews} avg reviews (score: {niche.demand_score:.1f})")
            else:
                print(f"   Demand: Limited data (score: {niche.demand_score:.1f})")

            if niche.avg_rating:
                print(f"   Rating: {niche.avg_rating:.1f}/5.0 stars")

            if niche.bestseller_count > 0:
                print(f"   🏆 {niche.bestseller_count} bestseller(s) in results")

            print(f"   Specificity: {niche.specificity_score:.1f} (more specific = better niche)")
            print(f"   Depth: Level {niche.depth_level}")

            if niche.parent_keyword:
                print(f"   Parent: {niche.parent_keyword}")

            print()

        print(f"{'='*80}\n")
        print("💡 RECOMMENDATIONS:")
        print()

        # Best by category
        best_price = max(top_niches, key=lambda x: x.price_score)
        print(f"   💰 Best Revenue Potential: {best_price.keyword}")
        print(f"      └─ ${best_price.avg_price:.2f} avg price")
        print()

        best_competition = max(top_niches, key=lambda x: x.competition_score)
        print(f"   🎯 Lowest Competition: {best_competition.keyword}")
        print(f"      └─ {best_competition.result_count:,} results")
        print()

        best_demand = max(top_niches, key=lambda x: x.demand_score)
        print(f"   🔥 Best Demand Indicators: {best_demand.keyword}")
        print(f"      └─ {best_demand.avg_reviews} avg reviews, {best_demand.bestseller_count} bestsellers")
        print()

        # Suggestions
        print("📋 NEXT STEPS:")
        print("   1. Research top niches on Amazon manually to validate")
        print("   2. Check Google Trends for search volume and seasonality")
        print("   3. Analyze top competitors' products and reviews")
        print("   4. Calculate profit margins with your costs")
        print("   5. Consider starting with the highest-scored niche")
        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Find profitable low-competition niches on Amazon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python amazon_search.py --seed "coloring book for" --category books
  python amazon_search.py --seed "yoga mat" "resistance bands" --category sports --depth 3
  python amazon_search.py --seed "coffee mug" --min-price 15 --max-price 50 --category kitchen
  python amazon_search.py --seed "pet toy" --category pet --export-csv results.csv
        """
    )

    parser.add_argument('--seed', nargs='+', default=['coloring book for'],
                       help='Seed keyword(s) to search for (can provide multiple)')
    parser.add_argument('--category', choices=list(CATEGORIES.keys()), default='books',
                       help='Amazon category to search in')
    parser.add_argument('--depth', type=int, default=DEFAULT_EXPLORATION_DEPTH,
                       help=f'Exploration depth (default: {DEFAULT_EXPLORATION_DEPTH})')
    parser.add_argument('--threshold', type=int, default=LOW_COMPETITION_THRESHOLD,
                       help=f'Competition threshold (default: {LOW_COMPETITION_THRESHOLD})')
    parser.add_argument('--min-price', type=float, default=0,
                       help='Minimum average price filter (default: 0)')
    parser.add_argument('--max-price', type=float, default=float('inf'),
                       help='Maximum average price filter (default: unlimited)')
    parser.add_argument('--min-score', type=float, default=60,
                       help='Minimum overall score to display (default: 60)')
    parser.add_argument('--top', type=int, default=20,
                       help='Number of top niches to display (default: 20)')
    parser.add_argument('--export-csv', type=str,
                       help='Export results to CSV file')
    parser.add_argument('--export-json', type=str,
                       help='Export results to JSON file')

    args = parser.parse_args()

    try:
        # Initialize finder
        finder = NicheFinder(
            category=args.category,
            depth=args.depth,
            min_price=args.min_price,
            max_price=args.max_price,
            competition_threshold=args.threshold
        )

        # Find niches
        finder.find_niches(args.seed)

        # Get top niches
        top_niches = finder.get_top_niches(limit=args.top, min_score=args.min_score)

        # Print report
        finder.print_report(top_niches)

        # Export if requested
        if args.export_csv:
            finder.export_csv(args.export_csv, top_niches)
            print(f"✅ Results exported to {args.export_csv}")

        if args.export_json:
            finder.export_json(args.export_json, top_niches)
            print(f"✅ Results exported to {args.export_json}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        exit(0)
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        exit(1)


if __name__ == "__main__":
    main()
