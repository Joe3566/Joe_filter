#!/usr/bin/env python3
"""
Generate PNG/SVG images from PlantUML diagrams in markdown files.

This script extracts PlantUML code blocks from markdown files and generates
visual diagrams using the PlantUML online service.

Usage:
    python generate_diagrams.py
"""

import os
import re
import requests
import base64
import zlib
from pathlib import Path

def plantuml_encode(plantuml_text):
    """Encode PlantUML text for URL."""
    # Remove @startuml and @enduml lines
    lines = plantuml_text.strip().split('\n')
    if lines[0].strip().startswith('@startuml'):
        lines = lines[1:]
    if lines[-1].strip().startswith('@enduml'):
        lines = lines[:-1]
    
    text = '\n'.join(lines)
    
    # Compress and encode
    compressed = zlib.compress(text.encode('utf-8'), 9)
    encoded = base64.b64encode(compressed).decode('ascii')
    
    # URL-safe encoding
    encoded = encoded.replace('+', '-').replace('/', '_')
    
    return encoded

def extract_plantuml_blocks(markdown_content):
    """Extract PlantUML code blocks from markdown content."""
    pattern = r'```plantuml\n(.*?)\n```'
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    return matches

def generate_diagram_urls(docs_dir):
    """Generate diagram URLs for all markdown files."""
    docs_path = Path(docs_dir)
    diagram_info = []
    
    for md_file in docs_path.glob('*.md'):
        print(f"\n📄 Processing: {md_file.name}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        plantuml_blocks = extract_plantuml_blocks(content)
        
        for i, block in enumerate(plantuml_blocks):
            try:
                encoded = plantuml_encode(block)
                diagram_name = f"{md_file.stem}_diagram_{i+1}"
                
                # URLs for different formats
                png_url = f"http://www.plantuml.com/plantuml/png/{encoded}"
                svg_url = f"http://www.plantuml.com/plantuml/svg/{encoded}"
                
                diagram_info.append({
                    'file': md_file.name,
                    'diagram': diagram_name,
                    'png_url': png_url,
                    'svg_url': svg_url
                })
                
                print(f"  ✅ {diagram_name}")
                
            except Exception as e:
                print(f"  ❌ Error processing diagram {i+1}: {e}")
    
    return diagram_info

def create_diagram_index(diagram_info):
    """Create an HTML index of all diagrams."""
    import datetime
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total = len(diagram_info)
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LLM Compliance Filter - UML Diagrams</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .diagram {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; }}
        .diagram h3 {{ color: #333; margin-top: 0; }}
        .links {{ margin: 10px 0; }}
        .links a {{ margin-right: 10px; padding: 5px 10px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }}
        .links a:hover {{ background: #0056b3; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #eee; }}
    </style>
</head>
<body>
    <h1>🛡️ LLM Compliance Filter - UML Diagrams</h1>
    <p>Generated on: <strong>{timestamp}</strong></p>
    <p>Total Diagrams: <strong>{total}</strong></p>
    
    <div class="diagrams">
"""
    
    current_file = None
    for info in diagram_info:
        if info['file'] != current_file:
            if current_file is not None:
                html_content += "</div>\n"
            html_content += f'<h2>📄 {info["file"]}</h2>\n<div class="file-diagrams">\n'
            current_file = info['file']
        
        html_content += f'''
        <div class="diagram">
            <h3>{info["diagram"]}</h3>
            <div class="links">
                <a href="{info['png_url']}" target="_blank">View PNG</a>
                <a href="{info['svg_url']}" target="_blank">View SVG</a>
            </div>
            <img src="{info['png_url']}" alt="{info['diagram']}" loading="lazy">
        </div>
        '''
    
    if current_file is not None:
        html_content += "</div>\n"
    
    html_content += """
    </div>
</body>
</html>
    """
    
    return html_content

def main():
    """Main function to generate diagram index."""
    docs_dir = "docs"
    
    if not os.path.exists(docs_dir):
        print("❌ docs/ directory not found!")
        return
    
    print("🚀 Generating UML diagram index...")
    
    # Generate diagram URLs
    diagram_info = generate_diagram_urls(docs_dir)
    
    # Create HTML index
    html_content = create_diagram_index(diagram_info)
    
    # Save HTML file
    output_file = "uml_diagrams.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Generated: {output_file}")
    print(f"📊 Total diagrams: {len(diagram_info)}")
    print(f"\n🌐 Open {output_file} in your browser to view all diagrams!")
    
    # Try to open the file
    try:
        os.system(f"start {output_file}")
    except:
        pass

if __name__ == "__main__":
    main()
