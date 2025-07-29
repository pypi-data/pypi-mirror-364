"""
RBA Glossary Examples
=====================

This example demonstrates how to:
- Look up economic and financial terms
- Search the glossary
- Browse terms by category
- Add custom terms
- Build a reference dictionary
"""

import rbadata
import pandas as pd

def main():
    """Main function demonstrating glossary functionality."""
    
    print("rbadata Glossary Examples")
    print("=" * 50)
    
    # Example 1: Quick term lookup
    print("\n1. Quick term definitions")
    print("-" * 50)
    
    # Use the convenience function to get definitions
    terms_to_define = ["CPI", "GDP", "TWI", "BBSW"]
    
    print("Common economic terms:")
    for term in terms_to_define:
        try:
            definition = rbadata.define(term)
            print(f"\n{term}:")
            print(f"  {definition}")
        except Exception as e:
            print(f"\n{term}: Not found")
    
    
    # Example 2: Create glossary instance
    print("\n\n2. Using the Glossary class")
    print("-" * 50)
    
    # Get glossary instance
    glossary = rbadata.get_glossary()
    
    # Alternative: Create directly
    # glossary = rbadata.Glossary()
    
    print("Glossary loaded successfully")
    
    # Get detailed information about a term
    term_info = glossary.get_definition("OCR")
    
    print(f"\nDetailed information for OCR:")
    for key, value in term_info.items():
        if value and key != 'related_terms':
            print(f"  {key}: {value}")
    
    if term_info.get('related_terms'):
        print(f"  Related terms: {', '.join(term_info['related_terms'])}")
    
    
    # Example 3: Search the glossary
    print("\n\n3. Searching for terms")
    print("-" * 50)
    
    # Search for inflation-related terms
    search_query = "inflation"
    results = glossary.search(search_query)
    
    print(f"Terms related to '{search_query}':")
    if not results.empty:
        for _, term in results.iterrows():
            print(f"\n{term['term']}:")
            print(f"  {term['definition'][:100]}...")
    else:
        print("No matching terms found")
    
    # Search for other concepts
    search_terms = ["rate", "money", "bank"]
    for query in search_terms:
        results = glossary.search(query)
        print(f"\nTerms containing '{query}': {len(results)}")
    
    
    # Example 4: Browse all terms
    print("\n\n4. Browsing all glossary terms")
    print("-" * 50)
    
    # Get all terms
    all_terms = glossary.get_all_terms()
    
    print(f"Total terms in glossary: {len(all_terms)}")
    
    # Show first few terms
    print("\nSample terms:")
    print("-" * 60)
    print(f"{'Term':<10} {'Full Name':<30} {'Category'}")
    print("-" * 60)
    
    for _, term in all_terms.head(10).iterrows():
        full_name = term.get('full_name', '')[:28] + '..' if len(term.get('full_name', '')) > 30 else term.get('full_name', '')
        print(f"{term['term']:<10} {full_name:<30} {term.get('category', 'N/A')}")
    
    
    # Example 5: Browse by category
    print("\n\n5. Browsing terms by category")
    print("-" * 50)
    
    # Get available categories
    categories = glossary.get_categories()
    
    print(f"Number of categories: {len(categories)}")
    print("\nAvailable categories:")
    for category in categories:
        terms_in_category = glossary.get_terms_by_category(category)
        print(f"  {category}: {len(terms_in_category)} terms")
    
    # Show all terms in a specific category
    print("\nMonetary Policy terms:")
    monetary_terms = glossary.get_terms_by_category("Monetary Policy")
    
    for _, term in monetary_terms.iterrows():
        print(f"  • {term['term']}: {term.get('full_name', term['term'])}")
    
    
    # Example 6: Add custom terms
    print("\n\n6. Adding custom terms")
    print("-" * 50)
    
    # Add organization-specific terms
    custom_terms = [
        {
            "term": "MPC",
            "definition": "Monetary Policy Committee - A committee that meets to decide on monetary policy settings",
            "full_name": "Monetary Policy Committee",
            "category": "Custom",
            "related_terms": ["OCR", "Monetary Policy"]
        },
        {
            "term": "YCC",
            "definition": "Yield Curve Control - A monetary policy tool where the central bank targets specific government bond yields",
            "full_name": "Yield Curve Control", 
            "category": "Monetary Policy",
            "related_terms": ["Interest Rates", "Bonds"]
        }
    ]
    
    print("Adding custom terms...")
    for term_data in custom_terms:
        glossary.add_custom_term(**term_data)
        print(f"  Added: {term_data['term']}")
    
    # Verify custom terms were added
    custom_definition = glossary.get_definition("YCC")
    print(f"\nCustom term YCC:")
    print(f"  {custom_definition['definition']}")
    
    
    # Example 7: Create a reference guide
    print("\n\n7. Creating a reference guide")
    print("-" * 50)
    
    # Create a categorized reference guide
    reference_categories = ["Inflation", "Monetary Policy", "Banking", "Exchange Rates"]
    
    print("Economic Terms Reference Guide")
    print("=" * 60)
    
    for category in reference_categories:
        print(f"\n{category}")
        print("-" * len(category))
        
        try:
            category_terms = glossary.get_terms_by_category(category)
            if not category_terms.empty:
                for _, term in category_terms.iterrows():
                    print(f"\n{term['term']} ({term.get('full_name', '')})")
                    # Wrap definition text
                    definition = term['definition']
                    words = definition.split()
                    line = ""
                    for word in words:
                        if len(line + word) > 70:
                            print(f"  {line}")
                            line = word + " "
                        else:
                            line += word + " "
                    if line:
                        print(f"  {line}")
        except:
            print("  No terms in this category")
    
    
    # Example 8: Export glossary
    print("\n\n8. Exporting glossary data")
    print("-" * 50)
    
    # Export to different formats
    output_file = "rba_glossary.json"
    # glossary.export_glossary(output_file)
    print(f"Would export glossary to {output_file}")
    
    # Create a simplified glossary for documentation
    all_terms = glossary.get_all_terms()
    simplified = all_terms[['term', 'full_name', 'definition']].copy()
    
    # Export to CSV
    csv_file = "rba_terms.csv"
    # simplified.to_csv(csv_file, index=False)
    print(f"Would export {len(simplified)} terms to {csv_file}")
    
    # Create markdown documentation
    print("\nWould create markdown documentation:")
    print("```markdown")
    print("# RBA Terms Glossary\n")
    for _, term in simplified.head(3).iterrows():
        print(f"## {term['term']} - {term.get('full_name', '')}")
        print(f"{term['definition']}\n")
    print("```")
    
    
    # Example 9: Term relationships
    print("\n\n9. Exploring term relationships")
    print("-" * 50)
    
    # Find related terms
    base_term = "CPI"
    term_info = glossary.get_definition(base_term)
    
    print(f"Terms related to {base_term}:")
    if 'related_terms' in term_info and term_info['related_terms']:
        for related in term_info['related_terms']:
            print(f"  • {related}")
            try:
                related_def = glossary.get_definition(related)
                print(f"    {related_def['definition'][:80]}...")
            except:
                pass
    
    
    # Example 10: Build domain vocabulary
    print("\n\n10. Building domain-specific vocabulary")
    print("-" * 50)
    
    # Extract key terms for specific domains
    domains = {
        "Central Banking": ["OCR", "SMP", "ESA", "REPO"],
        "Economic Indicators": ["CPI", "GDP", "TWI", "NAIRU"],
        "Financial Markets": ["BBSW", "ADI", "M3"],
    }
    
    print("Domain-specific vocabularies:")
    
    for domain, terms in domains.items():
        print(f"\n{domain}:")
        for term in terms:
            try:
                definition = glossary.get_definition(term)
                print(f"  {term}: {definition['full_name']}")
            except:
                print(f"  {term}: [Definition not found]")
    
    # Statistics
    print("\n\nGlossary Statistics:")
    all_terms = glossary.get_all_terms()
    print(f"  Total terms: {len(all_terms)}")
    print(f"  Categories: {len(glossary.get_categories())}")
    
    if 'source' in all_terms.columns:
        print(f"  Sources: {all_terms['source'].nunique()}")
    
    
    print("\n\nGlossary examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()