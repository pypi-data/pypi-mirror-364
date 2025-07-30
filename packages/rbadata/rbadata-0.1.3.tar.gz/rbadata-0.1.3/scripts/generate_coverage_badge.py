#!/usr/bin/env python3
"""
Generate a coverage badge locally without external services.
"""

import json
import subprocess
import sys
from pathlib import Path


def get_coverage_percentage():
    """Run pytest with coverage and extract the percentage."""
    try:
        # Run pytest with coverage
        result = subprocess.run(
            ["pytest", "tests/", "--cov=rbadata", "--cov-report=json", "--quiet"],
            capture_output=True,
            text=True
        )
        
        # Read the coverage report
        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            with open(coverage_file) as f:
                data = json.load(f)
                return data["totals"]["percent_covered"]
        else:
            print("Coverage file not found. Running tests...")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_badge_color(percentage):
    """Get badge color based on coverage percentage."""
    if percentage >= 90:
        return "brightgreen"
    elif percentage >= 80:
        return "green"
    elif percentage >= 70:
        return "yellowgreen"
    elif percentage >= 60:
        return "yellow"
    elif percentage >= 50:
        return "orange"
    else:
        return "red"


def generate_badge_url(percentage):
    """Generate shields.io badge URL."""
    color = get_badge_color(percentage)
    label = "coverage"
    message = f"{percentage:.1f}%"
    
    # URL encode spaces
    label = label.replace(" ", "%20")
    message = message.replace(" ", "%20")
    
    return f"https://img.shields.io/badge/{label}-{message}-{color}"


def update_readme_badge(badge_url):
    """Update the README with the new badge URL."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("README.md not found")
        return False
    
    # Read README
    content = readme_path.read_text()
    
    # Replace existing coverage badge or add new one
    # Look for pattern like ![Coverage](...)
    import re
    
    # Pattern for coverage badge
    pattern = r'\[!\[coverage\]\(.*?\)\]\(.*?\)'
    replacement = f'[![Coverage]({badge_url})](https://github.com/caymandev/rbadata)'
    
    if re.search(pattern, content, re.IGNORECASE):
        # Replace existing badge
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    else:
        # Add after other badges
        # Find the line with other badges
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '[![Python' in line or '[![License' in line:
                # Insert after this line
                lines.insert(i + 1, replacement)
                break
        new_content = '\n'.join(lines)
    
    # Write back
    readme_path.write_text(new_content)
    return True


def main():
    """Main function."""
    print("Generating coverage badge...")
    
    # Get coverage percentage
    percentage = get_coverage_percentage()
    if percentage is None:
        print("Failed to get coverage percentage")
        sys.exit(1)
    
    print(f"Coverage: {percentage:.1f}%")
    
    # Generate badge URL
    badge_url = generate_badge_url(percentage)
    print(f"Badge URL: {badge_url}")
    
    # Update README
    if "--update-readme" in sys.argv:
        if update_readme_badge(badge_url):
            print("README.md updated successfully")
        else:
            print("Failed to update README.md")
    else:
        print("\nTo update README.md, run with --update-readme flag")
        print(f"\nOr manually add this badge to your README:")
        print(f"[![Coverage]({badge_url})](https://github.com/caymandev/rbadata)")


if __name__ == "__main__":
    main()