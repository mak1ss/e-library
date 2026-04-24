"""
Phase 2: Book Review Relevance Scoring System
Data Analysis Script: Tasks 2.1 & 2.3

Analyzes real database data to design:
- Task 2.1: Book metadata aggregation strategies  
- Task 2.3: Review text preprocessing pipeline
"""

import mysql.connector
from pymongo import MongoClient
import json
import re
import statistics
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Any
import html
from datetime import datetime

# ============================================================================
# TASK 2.1: BOOK METADATA AGGREGATION ANALYSIS
# ============================================================================

class BookAggregationAnalyzer:
    """Analyzes book metadata aggregation strategies on real data."""
    
    def __init__(self, host='localhost', port=3307, user='root', password='070809az'):
        """Initialize MySQL connection."""
        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='book_service'
        )
        self.cursor = self.connection.cursor(dictionary=True)
    
    def query_books(self, limit=150):
        """Query real books from bookService database."""
        query = """
        SELECT b.id, b.title, b.description, b.ISBN, a.name as author_name,
               GROUP_CONCAT(g.name) as genres, c.name as category_name,
               b.release_date, p.name as publisher_name
        FROM book b
        LEFT JOIN author a ON b.author_id = a.id
        LEFT JOIN book_genre bg ON b.id = bg.book_id
        LEFT JOIN genre g ON bg.genre_id = g.id
        LEFT JOIN category c ON b.category_id = c.id
        LEFT JOIN publisher p ON b.publisher_id = p.id
        WHERE b.archived = 0
        GROUP BY b.id
        LIMIT %s
        """
        self.cursor.execute(query, (limit,))
        books = self.cursor.fetchall()
        return books
    
    def test_aggregation_strategies(self, books: List[Dict]) -> Dict[str, Any]:
        """Test three aggregation strategies on real data."""
        results = {
            'strategy_a': [],
            'strategy_b': [],
            'strategy_c': [],
            'metadata_stats': {}
        }
        
        # Analyze metadata completeness
        metadata_analysis = {
            'null_description': 0,
            'null_author': 0,
            'null_genres': 0,
            'null_category': 0,
            'null_all_metadata': 0,
            'total_books': len(books)
        }
        
        for book in books:
            # Strategy A: Simple "{title} {description}"
            strategy_a_text = f"{book['title'] or ''} {book['description'] or ''}".strip()
            results['strategy_a'].append({
                'book_id': book['id'],
                'text': strategy_a_text,
                'length': len(strategy_a_text)
            })
            
            # Strategy B: Labeled fields
            author = book['author_name'] or 'Unknown'
            genres = book['genres'] or 'Untagged'
            category = book['category_name'] or 'Uncategorized'
            description = book['description'] or 'No description'
            
            strategy_b_text = f"Title: {book['title']}\nAuthor: {author}\nGenre: {genres}\nCategory: {category}\nDescription: {description}"
            results['strategy_b'].append({
                'book_id': book['id'],
                'text': strategy_b_text,
                'length': len(strategy_b_text)
            })
            
            # Strategy C: Selective (non-NULL fields, priority to description)
            parts = []
            if book['title']:
                parts.append(f"Title: {book['title']}")
            if book['author_name']:
                parts.append(f"Author: {book['author_name']}")
            if book['genres']:
                parts.append(f"Genres: {book['genres']}")
            if book['category_name']:
                parts.append(f"Category: {book['category_name']}")
            if book['description']:
                parts.append(f"Description: {book['description']}")
            
            strategy_c_text = "\n".join(parts) if parts else "No metadata available"
            results['strategy_c'].append({
                'book_id': book['id'],
                'text': strategy_c_text,
                'length': len(strategy_c_text)
            })
            
            # Metadata analysis
            if not book['description']:
                metadata_analysis['null_description'] += 1
            if not book['author_name']:
                metadata_analysis['null_author'] += 1
            if not book['genres']:
                metadata_analysis['null_genres'] += 1
            if not book['category_name']:
                metadata_analysis['null_category'] += 1
            
            if not (book['title'] and (book['description'] or book['genres'] or book['category_name'])):
                metadata_analysis['null_all_metadata'] += 1
        
        results['metadata_stats'] = metadata_analysis
        return results
    
    def analyze_edge_cases(self, books: List[Dict]) -> Dict[str, Any]:
        """Identify and measure edge cases from real data."""
        edge_cases = {
            'null_description_pct': 0,
            'description_too_short': 0,  # < 20 chars
            'description_too_long': 0,   # > 500 chars
            'incomplete_metadata': 0,     # title only
            'null_title': 0,
            'description_lengths': []
        }
        
        for book in books:
            if not book['description']:
                edge_cases['null_description_pct'] += 1
            else:
                edge_cases['description_lengths'].append(len(book['description']))
                if len(book['description']) < 20:
                    edge_cases['description_too_short'] += 1
                if len(book['description']) > 500:
                    edge_cases['description_too_long'] += 1
            
            if not book['title']:
                edge_cases['null_title'] += 1
            
            # Incomplete: only title, no other fields
            has_other_fields = bool(book['description'] or book['author_name'] or 
                                   book['genres'] or book['category_name'])
            if book['title'] and not has_other_fields:
                edge_cases['incomplete_metadata'] += 1
        
        total = len(books)
        edge_cases['null_description_pct'] = (edge_cases['null_description_pct'] / total) * 100
        edge_cases['description_too_short_pct'] = (edge_cases['description_too_short'] / total) * 100
        edge_cases['description_too_long_pct'] = (edge_cases['description_too_long'] / total) * 100
        edge_cases['incomplete_metadata_pct'] = (edge_cases['incomplete_metadata'] / total) * 100
        edge_cases['null_title_pct'] = (edge_cases['null_title'] / total) * 100
        
        if edge_cases['description_lengths']:
            edge_cases['avg_description_length'] = statistics.mean(edge_cases['description_lengths'])
            edge_cases['median_description_length'] = statistics.median(edge_cases['description_lengths'])
            edge_cases['max_description_length'] = max(edge_cases['description_lengths'])
            edge_cases['min_description_length'] = min(edge_cases['description_lengths'])
        
        return edge_cases
    
    def compute_strategy_stats(self, strategy_results: List[Dict]) -> Dict[str, Any]:
        """Compute statistics for aggregation strategy results."""
        lengths = [item['length'] for item in strategy_results]
        
        return {
            'avg_length': statistics.mean(lengths) if lengths else 0,
            'median_length': statistics.median(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'total_books': len(strategy_results)
        }
    
    def close(self):
        """Close database connection."""
        self.cursor.close()
        self.connection.close()


# ============================================================================
# TASK 2.3: REVIEW TEXT PREPROCESSING ANALYSIS
# ============================================================================

class ReviewPreprocessingAnalyzer:
    """Analyzes review text characteristics and preprocessing needs."""
    
    def __init__(self, host='localhost', port=27018, db='review_db'):
        """Initialize MongoDB connection."""
        self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client[db]
        self.reviews_collection = self.db['reviews']
    
    def query_reviews(self, limit=500):
        """Query real reviews from reviewService MongoDB."""
        reviews = list(self.reviews_collection.find().limit(limit))
        return reviews
    
    def analyze_text_distribution(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Measure review text distribution characteristics."""
        text_lengths = []
        has_html = 0
        has_emojis = 0
        empty_reviews = 0
        special_char_patterns = defaultdict(int)
        
        for review in reviews:
            text = review.get('text', '')
            
            if not text or text.strip() == '':
                empty_reviews += 1
                continue
            
            text_lengths.append(len(text))
            
            # Check for HTML tags
            if bool(re.search(r'<[^>]+>', text)):
                has_html += 1
            
            # Check for emojis (basic detection)
            if bool(re.search(r'[^\x00-\x7F]', text)):  # Non-ASCII
                has_emojis += 1
            
            # Check for special patterns
            if bool(re.search(r'[!]{2,}', text)):
                special_char_patterns['repeated_exclamation'] += 1
            if bool(re.search(r'[?]{2,}', text)):
                special_char_patterns['repeated_question'] += 1
            if bool(re.search(r'SPOILER|spoiler', text)):
                special_char_patterns['spoiler_marker'] += 1
            if bool(re.search(r'[*_~]{2,}', text)):
                special_char_patterns['markdown_formatting'] += 1
        
        analysis = {
            'total_reviews': len(reviews),
            'empty_reviews': empty_reviews,
            'empty_reviews_pct': (empty_reviews / len(reviews)) * 100 if reviews else 0,
            'reviews_with_text': len(text_lengths),
            'has_html': has_html,
            'has_html_pct': (has_html / len(text_lengths)) * 100 if text_lengths else 0,
            'has_emojis_or_unicode': has_emojis,
            'has_emojis_pct': (has_emojis / len(text_lengths)) * 100 if text_lengths else 0,
            'special_patterns': dict(special_char_patterns)
        }
        
        if text_lengths:
            analysis['length_min'] = min(text_lengths)
            analysis['length_max'] = max(text_lengths)
            analysis['length_mean'] = statistics.mean(text_lengths)
            analysis['length_median'] = statistics.median(text_lengths)
            analysis['length_stdev'] = statistics.stdev(text_lengths) if len(text_lengths) > 1 else 0
            analysis['length_95th_percentile'] = sorted(text_lengths)[int(len(text_lengths) * 0.95)]
        
        return analysis
    
    def estimate_token_count(self, text: str, chars_per_token: float = 4.0) -> int:
        """Estimate token count using character-to-token ratio."""
        return max(1, int(len(text) / chars_per_token))
    
    def test_preprocessing_steps(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Test impact of preprocessing steps on real reviews."""
        results = {
            'html_decode_impact': {'affected_reviews': 0, 'total_reviews': 0},
            'lowercase_impact': {'affected_reviews': 0, 'total_reviews': 0},
            'emoji_handling': {'found_in_reviews': 0, 'total_reviews': 0},
            'whitespace_normalization': {'affected_reviews': 0, 'total_reviews': 0},
            'token_distribution': defaultdict(int),
            'preprocessing_examples': []
        }
        
        for i, review in enumerate(reviews[:10]):  # Sample for before/after
            text = review.get('text', '')
            if not text or text.strip() == '':
                continue
            
            results['total_reviews'] = len(reviews)
            
            # HTML decode test
            decoded = html.unescape(text)
            if decoded != text:
                results['html_decode_impact']['affected_reviews'] += 1
            results['html_decode_impact']['total_reviews'] += 1
            
            # Lowercase test
            lowercased = text.lower()
            if lowercased != text:
                results['lowercase_impact']['affected_reviews'] += 1
            results['lowercase_impact']['total_reviews'] += 1
            
            # Emoji/Unicode test
            if bool(re.search(r'[^\x00-\x7F]', text)):
                results['emoji_handling']['found_in_reviews'] += 1
            results['emoji_handling']['total_reviews'] += 1
            
            # Whitespace normalization test
            normalized = ' '.join(text.split())
            if normalized != text:
                results['whitespace_normalization']['affected_reviews'] += 1
            results['whitespace_normalization']['total_reviews'] += 1
            
            # Token count distribution
            tokens = self.estimate_token_count(text)
            results['token_distribution'][f'{(tokens // 50) * 50}-{((tokens // 50) + 1) * 50 - 1}'] += 1
            
            # Collect preprocessing examples (first 10)
            if len(results['preprocessing_examples']) < 10:
                results['preprocessing_examples'].append({
                    'review_id': str(review.get('_id', 'N/A')),
                    'original': text[:100],
                    'lowercased': lowercased[:100],
                    'html_decoded': decoded[:100],
                    'normalized': normalized[:100],
                    'estimated_tokens': tokens,
                    'rating': review.get('rating', 'N/A')
                })
        
        return results
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def print_section(title: str, width: int = 80):
    """Print formatted section header."""
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width)

def print_subsection(title: str, width: int = 80):
    """Print formatted subsection header."""
    print(f"\n{title}")
    print("-" * width)

def format_percentage(value: float) -> str:
    """Format percentage for display."""
    return f"{value:.2f}%"

def main():
    """Execute Phase 2 analysis."""
    print_section("PHASE 2: BOOK REVIEW RELEVANCE SCORING SYSTEM")
    print("Data Analysis: Tasks 2.1 & 2.3")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # ========================================================================
    # TASK 2.1: BOOK METADATA AGGREGATION STRATEGY
    # ========================================================================
    print_section("TASK 2.1: BOOK METADATA AGGREGATION STRATEGY ANALYSIS")
    
    try:
        book_analyzer = BookAggregationAnalyzer()
        print("\n✓ Connected to bookService MySQL database")
        
        # Query real books
        books = book_analyzer.query_books(limit=150)
        print(f"✓ Queried {len(books)} real books from database")
        
        if not books:
            print("⚠ No books found in database. Ensure databases are populated.")
            return
        
        # Test aggregation strategies
        print_subsection("Testing Aggregation Strategies on Real Data")
        strategy_results = book_analyzer.test_aggregation_strategies(books)
        
        # Compute statistics for each strategy
        strategy_a_stats = book_analyzer.compute_strategy_stats(strategy_results['strategy_a'])
        strategy_b_stats = book_analyzer.compute_strategy_stats(strategy_results['strategy_b'])
        strategy_c_stats = book_analyzer.compute_strategy_stats(strategy_results['strategy_c'])
        
        print(f"\nStrategy A (Simple): 'Title Description'")
        print(f"  - Average length: {strategy_a_stats['avg_length']:.0f} chars")
        print(f"  - Median length: {strategy_a_stats['median_length']:.0f} chars")
        print(f"  - Max length: {strategy_a_stats['max_length']:.0f} chars")
        print(f"  - Min length: {strategy_a_stats['min_length']:.0f} chars")
        
        print(f"\nStrategy B (Labeled): 'Title: ... Author: ... Genre: ... Description: ...'")
        print(f"  - Average length: {strategy_b_stats['avg_length']:.0f} chars")
        print(f"  - Median length: {strategy_b_stats['median_length']:.0f} chars")
        print(f"  - Max length: {strategy_b_stats['max_length']:.0f} chars")
        print(f"  - Min length: {strategy_b_stats['min_length']:.0f} chars")
        
        print(f"\nStrategy C (Selective): Only non-NULL fields, description priority")
        print(f"  - Average length: {strategy_c_stats['avg_length']:.0f} chars")
        print(f"  - Median length: {strategy_c_stats['median_length']:.0f} chars")
        print(f"  - Max length: {strategy_c_stats['max_length']:.0f} chars")
        print(f"  - Min length: {strategy_c_stats['min_length']:.0f} chars")
        
        # Edge case analysis
        print_subsection("Edge Case Analysis from Real Database")
        edge_cases = book_analyzer.analyze_edge_cases(books)
        
        print(f"\nBooks with NULL description: {format_percentage(edge_cases['null_description_pct'])}")
        print(f"Books with description < 20 chars: {format_percentage(edge_cases['description_too_short_pct'])}")
        print(f"Books with description > 500 chars: {format_percentage(edge_cases['description_too_long_pct'])}")
        print(f"Books with incomplete metadata (title only): {format_percentage(edge_cases['incomplete_metadata_pct'])}")
        print(f"Books with NULL title: {format_percentage(edge_cases['null_title_pct'])}")
        
        if edge_cases['description_lengths']:
            print(f"\nDescription Length Statistics (from {len(edge_cases['description_lengths'])} books):")
            print(f"  - Average: {edge_cases['avg_description_length']:.0f} chars")
            print(f"  - Median: {edge_cases['median_description_length']:.0f} chars")
            print(f"  - Min: {edge_cases['min_description_length']:.0f} chars")
            print(f"  - Max: {edge_cases['max_description_length']:.0f} chars")
        
        # Metadata completeness
        metadata = strategy_results['metadata_stats']
        print(f"\nMetadata Completeness Analysis:")
        print(f"  - Books with NULL author: {format_percentage((metadata['null_author'] / metadata['total_books']) * 100)}")
        print(f"  - Books with NULL genres: {format_percentage((metadata['null_genres'] / metadata['total_books']) * 100)}")
        print(f"  - Books with NULL category: {format_percentage((metadata['null_category'] / metadata['total_books']) * 100)}")
        
        # Sample books for each strategy
        print_subsection("Sample Aggregated Text from Real Books (Strategy Examples)")
        sample_count = min(5, len(books))
        for idx in range(sample_count):
            book = books[idx]
            print(f"\nBook {idx + 1}: {book['title']}")
            print(f"  Strategy A: {strategy_results['strategy_a'][idx]['text'][:80]}...")
            print(f"  Strategy B: {strategy_results['strategy_b'][idx]['text'][:80]}...")
            print(f"  Strategy C: {strategy_results['strategy_c'][idx]['text'][:80]}...")
        
        book_analyzer.close()
        
    except Exception as e:
        print(f"✗ Error in Task 2.1: {e}")
        import traceback
        traceback.print_exc()
    
    # ========================================================================
    # TASK 2.3: REVIEW TEXT PREPROCESSING ANALYSIS
    # ========================================================================
    print_section("TASK 2.3: REVIEW TEXT PREPROCESSING PIPELINE ANALYSIS")
    
    try:
        review_analyzer = ReviewPreprocessingAnalyzer()
        print("\n✓ Connected to reviewService MongoDB")
        
        # Query real reviews
        reviews = review_analyzer.query_reviews(limit=500)
        print(f"✓ Queried {len(reviews)} reviews from MongoDB")
        
        if not reviews:
            print("⚠ No reviews found in database. Ensure MongoDB is populated.")
            return
        
        # Analyze text characteristics
        print_subsection("Review Text Characteristics")
        text_analysis = review_analyzer.analyze_text_distribution(reviews)
        
        print(f"\nText Distribution Statistics (from {text_analysis['total_reviews']} reviews):")
        print(f"  - Empty/blank reviews: {text_analysis['empty_reviews']} ({format_percentage(text_analysis['empty_reviews_pct'])})")
        print(f"  - Reviews with actual text: {text_analysis['reviews_with_text']}")
        print(f"  - Reviews with HTML tags: {text_analysis['has_html']} ({format_percentage(text_analysis['has_html_pct'])})")
        print(f"  - Reviews with emojis/unicode: {text_analysis['has_emojis_or_unicode']} ({format_percentage(text_analysis['has_emojis_pct'])})")
        
        print(f"\nText Length Distribution (from {text_analysis['reviews_with_text']} non-empty reviews):")
        print(f"  - Minimum: {text_analysis.get('length_min', 'N/A')} chars")
        print(f"  - Maximum: {text_analysis.get('length_max', 'N/A')} chars")
        print(f"  - Mean: {text_analysis.get('length_mean', 'N/A'):.0f} chars")
        print(f"  - Median: {text_analysis.get('length_median', 'N/A'):.0f} chars")
        print(f"  - 95th percentile: {text_analysis.get('length_95th_percentile', 'N/A')} chars")
        
        if text_analysis['special_patterns']:
            print(f"\nSpecial Patterns Found:")
            for pattern, count in text_analysis['special_patterns'].items():
                pct = (count / text_analysis['reviews_with_text']) * 100
                print(f"  - {pattern}: {count} reviews ({format_percentage(pct)})")
        
        # Test preprocessing steps
        print_subsection("Preprocessing Step Impact Analysis")
        preprocessing = review_analyzer.test_preprocessing_steps(reviews)
        
        html_affected = preprocessing['html_decode_impact']['affected_reviews']
        html_total = preprocessing['html_decode_impact']['total_reviews']
        print(f"\n1. HTML Decode: {html_affected} reviews contain HTML ({format_percentage((html_affected / html_total) * 100) if html_total else 'N/A'})")
        
        lower_affected = preprocessing['lowercase_impact']['affected_reviews']
        lower_total = preprocessing['lowercase_impact']['total_reviews']
        print(f"2. Lowercase: {lower_affected} reviews have uppercase chars ({format_percentage((lower_affected / lower_total) * 100) if lower_total else 'N/A'})")
        
        emoji_affected = preprocessing['emoji_handling']['found_in_reviews']
        emoji_total = preprocessing['emoji_handling']['total_reviews']
        print(f"3. Emoji/Unicode Handling: {emoji_affected} reviews contain special chars ({format_percentage((emoji_affected / emoji_total) * 100) if emoji_total else 'N/A'})")
        
        ws_affected = preprocessing['whitespace_normalization']['affected_reviews']
        ws_total = preprocessing['whitespace_normalization']['total_reviews']
        print(f"4. Whitespace Normalization: {ws_affected} reviews need normalization ({format_percentage((ws_affected / ws_total) * 100) if ws_total else 'N/A'})")
        
        # Token limit analysis
        print_subsection("Token Count Distribution & Truncation Analysis")
        print(f"\nEstimated tokens per review (using 4 chars/token ratio):")
        if preprocessing.get('preprocessing_examples'):
            sample = preprocessing['preprocessing_examples'][0]
            median_tokens = statistics.median([ex['estimated_tokens'] for ex in preprocessing['preprocessing_examples']])
            print(f"  - Median tokens (from sample): {median_tokens:.0f}")
            
            # Sentence Transformer token limit is ~512
            reviews_exceeding_limit = sum(1 for ex in preprocessing['preprocessing_examples'] if ex['estimated_tokens'] > 512)
            print(f"  - Reviews exceeding 512 token limit: {reviews_exceeding_limit}/10 in sample")
        
        # Before/after examples
        print_subsection("Before/After Preprocessing Examples (First 10 Reviews)")
        for i, example in enumerate(preprocessing.get('preprocessing_examples', [])[:10], 1):
            print(f"\n[Review {i}] Rating: {example['rating']}, Tokens: {example['estimated_tokens']}")
            print(f"  Original: {example['original'][:70]}")
            print(f"  Lowercased: {example['lowercased'][:70]}")
            print(f"  HTML Decoded: {example['html_decoded'][:70]}")
            print(f"  Whitespace Normalized: {example['normalized'][:70]}")
        
        review_analyzer.close()
        
    except Exception as e:
        print(f"✗ Error in Task 2.3: {e}")
        import traceback
        traceback.print_exc()
    
    print_section("ANALYSIS COMPLETE")
    print("\nGenerated comprehensive data analysis for Phase 2 tasks 2.1 and 2.3")
    print("Review the findings above to determine aggregation strategy and preprocessing pipeline.")

if __name__ == '__main__':
    main()
