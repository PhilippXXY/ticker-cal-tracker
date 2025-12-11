#!/usr/bin/env python3
"""
Script to embed PlantUML diagrams directly into markdown files.
"""

# Disclaimer: Created by GitHub Copilot

from pathlib import Path

def embed_puml_in_markdown():
    """Embed all .puml files into their corresponding .md files."""
    uml_dir = Path("docs/uml")
    
    # Get all .puml files
    puml_files = sorted(uml_dir.glob("*.puml"))
    
    processed = 0
    for puml_file in puml_files:
        # Read the PlantUML content
        puml_content = puml_file.read_text()
        
        # Get corresponding markdown file
        md_file = puml_file.with_suffix(".md")
        
        if not md_file.exists():
            print(f"⚠️  Markdown file not found: {md_file.name}")
            continue
        
        # Read current markdown content
        md_content = md_file.read_text()
        
        # Find the header (first line before empty line)
        lines = md_content.split('\n')
        header_lines = []
        description_lines = []
        
        # Extract header and description
        in_description = False
        for i, line in enumerate(lines):
            if i == 0 and line.startswith('#'):
                header_lines.append(line)
            elif line.strip() == '' and header_lines:
                in_description = True
            elif in_description and line.strip() and not line.startswith('```'):
                description_lines.append(line)
            elif line.startswith('```'):
                break
        
        # Build new markdown content
        new_content = []
        
        # Add header
        if header_lines:
            new_content.extend(header_lines)
            new_content.append('')
        
        # Add description
        if description_lines:
            new_content.extend(description_lines)
            new_content.append('')
        
        # Add PlantUML code block with full content
        new_content.append('```puml')
        new_content.append(puml_content.rstrip())
        new_content.append('```')
        
        # Write back to file
        md_file.write_text('\n'.join(new_content) + '\n')
        
        processed += 1
        print(f"✅ {md_file.name}")
    
    print(f"\n🎉 Processed {processed} files")

if __name__ == "__main__":
    embed_puml_in_markdown()
