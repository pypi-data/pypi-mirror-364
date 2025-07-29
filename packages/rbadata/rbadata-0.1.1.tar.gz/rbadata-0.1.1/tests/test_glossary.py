"""
Tests for glossary functionality
"""

import pytest
import pandas as pd
from rbadata import Glossary, get_glossary, define
from rbadata.exceptions import RBADataError


class TestGlossary:
    """Test the Glossary class."""
    
    def test_glossary_init(self):
        """Test glossary initialization with default terms."""
        glossary = Glossary()
        
        # Check that default terms are loaded
        assert len(glossary._terms) > 0
        assert "CPI" in glossary._terms
        assert "GDP" in glossary._terms
        
        # Check categories are built
        assert len(glossary._categories) > 0
        assert "Inflation" in glossary._categories
    
    def test_get_definition(self):
        """Test getting term definitions."""
        glossary = Glossary()
        
        # Test existing term (uppercase)
        definition = glossary.get_definition("CPI")
        assert definition["term"] == "CPI"
        assert "Consumer Price Index" in definition["full_name"]
        assert "definition" in definition
        
        # Test case insensitive
        definition = glossary.get_definition("cpi")
        assert definition["term"] == "CPI"
        
        # Test by full name
        definition = glossary.get_definition("Gross Domestic Product")
        assert definition["term"] == "GDP"
    
    def test_get_definition_not_found(self):
        """Test error when term not found."""
        glossary = Glossary()
        
        with pytest.raises(RBADataError, match="Term 'XYZ' not found"):
            glossary.get_definition("XYZ")
    
    def test_search(self):
        """Test searching for terms."""
        glossary = Glossary()
        
        # Search for inflation-related terms
        results = glossary.search("inflation")
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
        
        # CPI should be in results
        assert "CPI" in results["term"].values
        
        # Search for non-existent term
        results = glossary.search("cryptocurrency")
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 0
    
    def test_get_all_terms(self):
        """Test getting all terms."""
        glossary = Glossary()
        
        all_terms = glossary.get_all_terms()
        assert isinstance(all_terms, pd.DataFrame)
        assert len(all_terms) > 0
        assert "term" in all_terms.columns
        assert "definition" in all_terms.columns
    
    def test_get_categories(self):
        """Test getting categories."""
        glossary = Glossary()
        
        categories = glossary.get_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "Inflation" in categories
        assert "Monetary Policy" in categories
    
    def test_get_terms_by_category(self):
        """Test getting terms by category."""
        glossary = Glossary()
        
        # Get inflation terms
        inflation_terms = glossary.get_terms_by_category("Inflation")
        assert isinstance(inflation_terms, pd.DataFrame)
        assert len(inflation_terms) > 0
        assert "CPI" in inflation_terms["term"].values
        
        # Test invalid category
        with pytest.raises(RBADataError, match="Category 'Invalid' not found"):
            glossary.get_terms_by_category("Invalid")
    
    def test_add_custom_term(self):
        """Test adding custom terms."""
        glossary = Glossary()
        
        # Add a custom term
        glossary.add_custom_term(
            term="TEST",
            definition="A test term",
            full_name="Test Term",
            category="Testing",
            related_terms=["CPI", "GDP"]
        )
        
        # Verify it was added
        assert "TEST" in glossary._terms
        definition = glossary.get_definition("TEST")
        assert definition["definition"] == "A test term"
        assert definition["source"] == "User defined"
        
        # Check category was created
        assert "Testing" in glossary._categories
        assert "TEST" in glossary._categories["Testing"]
    
    def test_export_glossary(self, tmp_path):
        """Test exporting glossary to JSON."""
        glossary = Glossary()
        
        # Add a custom term
        glossary.add_custom_term("TEST", "Test definition")
        
        # Export to file
        output_file = tmp_path / "glossary.json"
        glossary.export_glossary(str(output_file))
        
        # Verify file exists
        assert output_file.exists()
        
        # Load and check content
        import json
        with open(output_file) as f:
            data = json.load(f)
        
        assert "CPI" in data
        assert "TEST" in data


class TestGlossaryConvenience:
    """Test convenience functions."""
    
    def test_get_glossary(self):
        """Test get_glossary function."""
        glossary = get_glossary()
        assert isinstance(glossary, Glossary)
    
    def test_define(self):
        """Test define convenience function."""
        # Test existing term
        definition = define("GDP")
        assert isinstance(definition, str)
        assert "Gross Domestic Product" in definition or "goods and services" in definition
        
        # Test error for non-existent term
        with pytest.raises(RBADataError):
            define("NONEXISTENT")