"""
RBA statistical terms glossary and definitions
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup
from .exceptions import RBADataError
from .config import get_headers


class Glossary:
    """
    Access RBA statistical terms and definitions.
    
    Provides programmatic access to RBA's glossary of economic and
    financial terms used in their statistical publications.
    
    Examples
    --------
    >>> glossary = Glossary()
    >>> # Look up a specific term
    >>> definition = glossary.get_definition("CPI")
    
    >>> # Search for terms
    >>> inflation_terms = glossary.search("inflation")
    
    >>> # Get all terms
    >>> all_terms = glossary.get_all_terms()
    """
    
    def __init__(self):
        """Initialize Glossary instance."""
        self._terms = self._load_default_glossary()
        self._categories = self._build_categories()
    
    def get_definition(self, term: str) -> Dict[str, str]:
        """
        Get definition for a specific term.
        
        Parameters
        ----------
        term : str
            Term to look up (case-insensitive)
            
        Returns
        -------
        dict
            Dictionary with term information including definition
            
        Examples
        --------
        >>> glossary.get_definition("GDP")
        {'term': 'GDP', 'definition': 'Gross Domestic Product...', ...}
        """
        term_upper = term.upper()
        
        # Check common abbreviations
        if term_upper in self._terms:
            result = self._terms[term_upper].copy()
            result["term"] = term_upper
            return result
        
        # Check full term names
        for key, value in self._terms.items():
            if term.lower() in value.get("full_name", "").lower():
                result = value.copy()
                result["term"] = key
                return result
        
        raise RBADataError(f"Term '{term}' not found in glossary")
    
    def search(self, query: str) -> pd.DataFrame:
        """
        Search for terms containing the query string.
        
        Parameters
        ----------
        query : str
            Search query (case-insensitive)
            
        Returns
        -------
        pd.DataFrame
            DataFrame of matching terms
        """
        query_lower = query.lower()
        matches = []
        
        for term, info in self._terms.items():
            # Search in term, full name, and definition
            if (query_lower in term.lower() or
                query_lower in info.get("full_name", "").lower() or
                query_lower in info.get("definition", "").lower()):
                
                match = info.copy()
                match["term"] = term
                matches.append(match)
        
        if not matches:
            return pd.DataFrame()
        
        return pd.DataFrame(matches)
    
    def get_all_terms(self) -> pd.DataFrame:
        """
        Get all terms in the glossary.
        
        Returns
        -------
        pd.DataFrame
            DataFrame of all terms and definitions
        """
        terms_list = []
        
        for term, info in self._terms.items():
            term_info = info.copy()
            term_info["term"] = term
            terms_list.append(term_info)
        
        return pd.DataFrame(terms_list)
    
    def get_categories(self) -> List[str]:
        """
        Get available term categories.
        
        Returns
        -------
        list of str
            Available categories
        """
        return list(self._categories.keys())
    
    def get_terms_by_category(self, category: str) -> pd.DataFrame:
        """
        Get all terms in a specific category.
        
        Parameters
        ----------
        category : str
            Category name
            
        Returns
        -------
        pd.DataFrame
            Terms in the specified category
        """
        if category not in self._categories:
            raise RBADataError(
                f"Category '{category}' not found. "
                f"Available: {list(self._categories.keys())}"
            )
        
        terms = self._categories[category]
        
        results = []
        for term in terms:
            if term in self._terms:
                info = self._terms[term].copy()
                info["term"] = term
                results.append(info)
        
        return pd.DataFrame(results)
    
    def add_custom_term(
        self,
        term: str,
        definition: str,
        full_name: Optional[str] = None,
        category: Optional[str] = None,
        related_terms: Optional[List[str]] = None
    ):
        """
        Add a custom term to the glossary.
        
        Parameters
        ----------
        term : str
            Term abbreviation or short form
        definition : str
            Term definition
        full_name : str, optional
            Full name of the term
        category : str, optional
            Category for the term
        related_terms : list of str, optional
            Related terms
        """
        self._terms[term.upper()] = {
            "definition": definition,
            "full_name": full_name or "",
            "category": category or "Custom",
            "related_terms": related_terms or [],
            "source": "User defined"
        }
        
        # Update categories
        if category:
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(term.upper())
    
    def export_glossary(self, output_path: str):
        """
        Export glossary to JSON file.
        
        Parameters
        ----------
        output_path : str
            Path to save the glossary
        """
        with open(output_path, "w") as f:
            json.dump(self._terms, f, indent=2)
    
    def _load_default_glossary(self) -> Dict[str, Dict[str, str]]:
        """Load default glossary terms."""
        # Core RBA/economic terms
        glossary = {
            "CPI": {
                "full_name": "Consumer Price Index",
                "definition": "A measure of inflation that tracks the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services.",
                "category": "Inflation",
                "related_terms": ["Inflation", "Price Index"],
                "source": "RBA"
            },
            "GDP": {
                "full_name": "Gross Domestic Product",
                "definition": "The total monetary or market value of all the finished goods and services produced within a country's borders in a specific time period.",
                "category": "Economic Activity",
                "related_terms": ["Economic Growth", "National Accounts"],
                "source": "RBA"
            },
            "OCR": {
                "full_name": "Official Cash Rate",
                "definition": "The interest rate set by the Reserve Bank of Australia for overnight loans between banks.",
                "category": "Monetary Policy",
                "related_terms": ["Cash Rate", "Interest Rates", "Monetary Policy"],
                "source": "RBA"
            },
            "TWI": {
                "full_name": "Trade Weighted Index",
                "definition": "An index that measures the value of Australia's currency against a basket of foreign currencies of major trading partners.",
                "category": "Exchange Rates",
                "related_terms": ["Exchange Rate", "AUD"],
                "source": "RBA"
            },
            "M3": {
                "full_name": "Broad Money",
                "definition": "A measure of the money supply that includes cash, checking deposits, and easily convertible near money.",
                "category": "Money Supply",
                "related_terms": ["Money Supply", "Monetary Aggregates"],
                "source": "RBA"
            },
            "BBSW": {
                "full_name": "Bank Bill Swap Rate",
                "definition": "The interest rate used as a benchmark for pricing Australian dollar derivatives and securities.",
                "category": "Interest Rates",
                "related_terms": ["Interest Rates", "Money Market"],
                "source": "RBA"
            },
            "SMP": {
                "full_name": "Statement on Monetary Policy",
                "definition": "The Reserve Bank's quarterly report on economic and financial conditions and the outlook for inflation and economic growth.",
                "category": "RBA Publications",
                "related_terms": ["Monetary Policy", "Economic Outlook"],
                "source": "RBA"
            },
            "ESA": {
                "full_name": "Exchange Settlement Account",
                "definition": "Accounts held at the Reserve Bank by financial institutions to settle payment obligations.",
                "category": "Banking",
                "related_terms": ["Banking System", "Settlements"],
                "source": "RBA"
            },
            "ADI": {
                "full_name": "Authorised Deposit-taking Institution",
                "definition": "Financial institutions authorized by APRA to accept deposits from the public.",
                "category": "Banking",
                "related_terms": ["Banks", "Financial Institutions"],
                "source": "RBA"
            },
            "RITS": {
                "full_name": "Reserve Bank Information and Transfer System",
                "definition": "The Reserve Bank's system for settling high-value payments between financial institutions.",
                "category": "Payment Systems",
                "related_terms": ["Payments", "Settlement"],
                "source": "RBA"
            },
            "NAIRU": {
                "full_name": "Non-Accelerating Inflation Rate of Unemployment",
                "definition": "The level of unemployment below which inflation rises.",
                "category": "Labour Market",
                "related_terms": ["Unemployment", "Inflation", "Phillips Curve"],
                "source": "RBA"
            },
            "REPO": {
                "full_name": "Repurchase Agreement",
                "definition": "A form of short-term borrowing where securities are sold with an agreement to repurchase them at a specified date and price.",
                "category": "Money Market",
                "related_terms": ["Money Market", "Liquidity"],
                "source": "RBA"
            }
        }
        
        return glossary
    
    def _build_categories(self) -> Dict[str, List[str]]:
        """Build category mapping from terms."""
        categories = {}
        
        for term, info in self._terms.items():
            category = info.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(term)
        
        return categories


def get_glossary() -> Glossary:
    """
    Get a Glossary instance for accessing RBA terms.
    
    Returns
    -------
    Glossary
        Glossary instance
        
    Examples
    --------
    >>> glossary = get_glossary()
    >>> cpi_def = glossary.get_definition("CPI")
    """
    return Glossary()


def define(term: str) -> str:
    """
    Convenience function to get a term definition.
    
    Parameters
    ----------
    term : str
        Term to define
        
    Returns
    -------
    str
        Term definition
        
    Examples
    --------
    >>> define("GDP")
    'The total monetary or market value of all the finished goods...'
    """
    glossary = Glossary()
    result = glossary.get_definition(term)
    return result["definition"]