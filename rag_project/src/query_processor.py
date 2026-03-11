#!/usr/bin/env python3
"""
Query Understanding and Preprocessing Module for Hybrid Search
Enhances search results by preprocessing and understanding user queries.
"""

import re
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# ─── Common StopWORDS ────────────────────────────────────────────────────────────
STOPWORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
    'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
    'from', 'up', 'about', 'into', 'over', 'after', 'beneath', 'under',
    'above', 'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
    'neither', 'not', 'only', 'just', 'also', 'very', 'too', 'quite',
    'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'any', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
    'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
    'itself', 'they', 'them', 'their', 'theirs', 'themselves'
}

# ─── SYNONYMS for common search terms ──────────────────────────────────────────────
SYNONYMS = {
    'benefits': ['compensation', 'salary', 'pay', 'insurance', 'health', 'vacation', 'leave'],
    'remote': ['work from home', 'wfh', 'telecommute', 'telecommuting', 'flexible'],
    'policy': ['rules', 'guidelines', 'procedures', 'guidance', 'regulations'],
    'employee': ['staff', 'worker', 'personnel', 'team member', 'teammate'],
    'customer': ['client', 'user', 'buyer', 'consumer', 'customer'],
    'product': ['item', 'goods', 'service', 'solution'],
    'launch': ['release', 'debut', 'introduce', 'rollout'],
    'meeting': ['conference', 'discussion', 'gathering', 'session'],
    'planning': ['strategy', 'roadmap', 'forecast', 'preparation'],
    'data': ['information', 'records', 'statistics', 'metrics'],
    'vault': ['storage', 'repository', 'archive', 'safe'],
    'phone': ['telephone', 'call', 'contact number', 'hotline'],
    'help': ['assist', 'support', 'aid', 'service'],
    'faq': ['question', 'questions', 'faq', 'frequently asked'],
    'pet': ['animal', 'dog', 'cat', 'companion'],
    'cloud': ['cloud computing', 'cloud sync', 'online'],
    'sync': ['synchronize', 'sync', 'backup', 'update'],
}

# ─── Query Intent Patterns ─────────────────────────────────────────────────────────
INTENT_PATTERNS = {
    'informational': [
        r'\b(what|how|why|when|where|who|which)\b',
        r'\b(explain|describe|define|tell me about)\b',
        r'\b(information|details|facts)\b'
    ],
    ' navigational': [
        r'\b(find|locate|show me|go to|open)\b',
        r'\b(link|website|url|page)\b'
    ],
    'transactional': [
        r'\b(buy|purchase|order|download|register|sign up)\b',
        r'\b(get|obtain|acquire)\b'
    ],
    'comparison': [
        r'\b(compare|difference|versus|vs|better|worse)\b',
        r'\b(advantage|disadvantage|pros|cons)\b'
    ]
}


class QueryProcessor:
    """Processes and enhances user queries for better search results."""
    
    def __init__(self):
        self.stopwords = STOPWORDS
        self.synonyms = SYNONYMS
        self.intent_patterns = INTENT_PATTERNS
        
    def preprocess(self, query: str) -> dict:
        """
        Main entry point: process query and return all analysis.
        
        Returns:
            dict with keys: original, cleaned, tokens, expanded, intent, entities
        """
        # 1. Basic cleaning
        cleaned = self._clean_query(query)
        
        # 2. Tokenize
        tokens = self._tokenize(cleaned)
        
        # 3. Remove stopwords (keep for BM25, useful for semantic)
        meaningful_tokens = [t for t in tokens if t.lower() not in self.stopwords]
        
        # 4. Expand query with synonyms
        expanded_terms = self._expand_query(tokens)
        
        # 5. Detect intent
        intent = self._detect_intent(query)
        
        # 6. Extract entities
        entities = self._extract_entities(query)
        
        return {
            'original': query,
            'cleaned': cleaned,
            'tokens': tokens,
            'meaningful_tokens': meaningful_tokens,
            'expanded_terms': expanded_terms,
            'intent': intent,
            'entities': entities,
            'query_for_bm25': ' '.join(meaningful_tokens),
            'query_for_vector': cleaned,
            'query_expanded': self._build_expanded_query(tokens, expanded_terms)
        }
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query."""
        # Lowercase
        query = query.lower()
        # Remove extra whitespace
        query = ' '.join(query.split())
        # Remove special characters but keep important punctuation
        query = re.sub(r'[^\w\s\-\'\"]', ' ', query)
        return query.strip()
    
    def _tokenize(self, query: str) -> list:
        """Tokenize query into words."""
        return query.split()
    
    def _expand_query(self, tokens: list) -> list:
        """Expand query with synonyms."""
        expanded = set()
        for token in tokens:
            token_lower = token.lower()
            if token_lower in self.synonyms:
                expanded.update(self.synonyms[token_lower])
        return list(expanded)
    
    def _build_expanded_query(self, tokens: list, expanded_terms: list) -> str:
        """Build an expanded query string combining original + synonyms."""
        expanded_tokens = list(tokens)
        expanded_tokens.extend(expanded_terms)
        return ' '.join(expanded_tokens)
    
    def _detect_intent(self, query: str) -> dict:
        """Detect the user's search intent."""
        query_lower = query.lower()
        detected_intents = []
        
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    detected_intents.append(intent_name)
                    break
        
        # Default to informational if no intent detected
        primary_intent = detected_intents[0] if detected_intents else 'informational'
        
        return {
            'primary': primary_intent,
            'all_detected': detected_intents,
            'confidence': len(detected_intents) / len(INTENT_PATTERNS) if detected_intents else 0.1
        }
    
    def _extract_entities(self, query: str) -> list:
        """Extract named entities from query."""
        entities = []
        
        # Phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities.extend(re.findall(phone_pattern, query))
        
        # Email patterns
        email_pattern = r'\b[\w.-]+@[\w.-]+\.\w+\b'
        entities.extend(re.findall(email_pattern, query))
        
        # Capitalized terms (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
        entities.extend(capitalized)
        
        # Numbers with units
        number_pattern = r'\b\d+(?:\.\d+)?\s*(?:hours?|days?|weeks?|months?|years?|employees?|users?)\b'
        entities.extend(re.findall(number_pattern, query.lower()))
        
        return entities
    
    def get_search_config(self, query_analysis: dict) -> dict:
        """
        Based on query analysis, return optimal search configuration.
        
        Returns config for hybrid search with weights and strategies.
        """
        intent = query_analysis['intent']['primary']
        has_entities = len(query_analysis['entities']) > 0
        has_expanded = len(query_analysis['expanded_terms']) > 0
        
        # Default config
        config = {
            'tfidf_weight': 0.3,
            'bm25_weight': 0.4,
            'semantic_weight': 0.3,
            'use_reranking': True,
            'top_k': 10,
            'expand_query': True,
            'description': 'Default hybrid search'
        }
        
        # Adjust based on intent
        if intent == 'informational':
            # For informational queries, semantic search helps find related concepts
            config['semantic_weight'] = 0.4
            config['bm25_weight'] = 0.35
            config['tfidf_weight'] = 0.25
            config['description'] = 'Optimized for informational queries (semantic-heavy)'
            
        elif intent == 'transactional':
            # For transactional, exact matches matter more
            config['bm25_weight'] = 0.5
            config['tfidf_weight'] = 0.3
            config['semantic_weight'] = 0.2
            config['description'] = 'Optimized for transactional queries (keyword-heavy)'
            
        elif intent == 'comparison':
            # For comparison, semantic helps find related items
            config['semantic_weight'] = 0.45
            config['bm25_weight'] = 0.3
            config['tfidf_weight'] = 0.25
            config['description'] = 'Optimized for comparison queries'
        
        # If query has specific entities, keyword search is more important
        if has_entities:
            config['bm25_weight'] += 0.15
            config['semantic_weight'] -= 0.15
            config['description'] += ' (boosted keyword for entity search)'
        
        # If we expanded the query, rely more on semantic
        if has_expanded:
            config['semantic_weight'] += 0.1
            config['tfidf_weight'] -= 0.1
            config['description'] += ' (query expansion enabled)'
        
        return config


def analyze_query(query: str) -> dict:
    """Convenience function to analyze a query."""
    processor = QueryProcessor()
    return processor.preprocess(query)


def demo():
    """Demonstrate query processing capabilities."""
    print("🔍 Query Understanding Demo")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "What is the phone 1-800-832-4267 using for?",
        "Tell me about remote work policy benefits",
        "Compare the cloud sync products",
        "How do I download the software?",
        "employee pet policy"
    ]
    
    processor = QueryProcessor()
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 50)
        
        # Analyze
        analysis = processor.preprocess(query)
        
        print(f"   Cleaned:    {analysis['cleaned']}")
        print(f"   Tokens:     {analysis['tokens']}")
        print(f"   Meaningful: {analysis['meaningful_tokens']}")
        print(f"   Expanded:   {analysis['expanded_terms']}")
        print(f"   Intent:     {analysis['intent']['primary']}")
        print(f"   Entities:   {analysis['entities']}")
        
        # Get search config
        config = processor.get_search_config(analysis)
        print(f"   Config:     {config['description']}")
        print(f"   Weights:    BM25={config['bm25_weight']}, "
              f"TF-IDF={config['tfidf_weight']}, "
              f"Semantic={config['semantic_weight']}")
    
    print("\n" + "=" * 60)
    print("✅ Query understanding demo complete!")


if __name__ == "__main__":
    demo()
