#!/usr/bin/env python3
"""
Interactive Documentation System v11.0
Living documentation with try-it-now examples and auto-generated API docs
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import yaml
from jinja2 import Template
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# Configuration
DOCS_DIR = Path("docs")
OUTPUT_DIR = Path("docs-site")
TEMPLATES_DIR = Path(__file__).parent / "templates"

class DocumentationGenerator:
    """Generate interactive documentation"""
    
    def __init__(self):
        DOCS_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    def generate_api_docs(self, openapi_spec: str) -> str:
        """Generate API documentation from OpenAPI spec"""
        
        with open(openapi_spec) as f:
            spec = yaml.safe_load(f)
        
        html = ["<h1>API Documentation</h1>"]
        html.append(f"<p><strong>Version:</strong> {spec.get('info', {}).get('version', 'N/A')}</p>")
        html.append(f"<p>{spec.get('info', {}).get('description', '')}</p>")
        
        # Generate endpoints
        html.append("<h2>Endpoints</h2>")
        
        for path, methods in spec.get('paths', {}).items():
            html.append(f"<h3><code>{path}</code></h3>")
            
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    html.append(f"<h4>{method.upper()}</h4>")
                    html.append(f"<p>{details.get('summary', '')}</p>")
                    
                    # Try-it-now button
                    html.append(f'''
                    <div class="try-it-now">
                        <button onclick="tryEndpoint('{method.upper()}', '{path}')">
                            Try it now
                        </button>
                        <div id="result-{method}-{path.replace('/', '-')}" class="result"></div>
                    </div>
                    ''')
        
        return '\n'.join(html)
    
    def generate_code_examples(self, language: str, code: str, description: str = "") -> str:
        """Generate code example with syntax highlighting"""
        
        lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(style='monokai', cssclass='highlight')
        highlighted = highlight(code, lexer, formatter)
        
        return f'''
        <div class="code-example">
            <p>{description}</p>
            {highlighted}
            <button onclick="copyCode(this)">Copy</button>
            <button onclick="runCode(this, '{language}')">Run</button>
        </div>
        '''
    
    def generate_architecture_diagram(self) -> str:
        """Generate architecture diagram using Mermaid"""
        
        diagram = '''
        <div class="mermaid">
        graph TB
            A[Client] -->|HTTPS| B[API Gateway]
            B --> C[Service Mesh]
            C --> D[Microservices]
            D --> E[Database]
            D --> F[Cache]
            
            style A fill:#f9f,stroke:#333
            style B fill:#bbf,stroke:#333
            style C fill:#bfb,stroke:#333
            style D fill:#fbb,stroke:#333
        </div>
        '''
        return diagram
    
    def generate_search_index(self, docs: List[Dict]) -> Dict:
        """Generate search index for fast documentation search"""
        
        index = {
            'documents': [],
            'keywords': {}
        }
        
        for doc in docs:
            doc_id = len(index['documents'])
            index['documents'].append({
                'id': doc_id,
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'content': doc.get('content', '')
            })
            
            # Extract keywords
            content = doc.get('content', '').lower()
            words = content.split()
            
            for word in set(words):
                if len(word) > 3:
                    if word not in index['keywords']:
                        index['keywords'][word] = []
                    index['keywords'][word].append(doc_id)
        
        return index
    
    def generate_html_template(self) -> str:
        """Generate HTML template with interactive features"""
        
        template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Interactive Documentation</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            background: #f5f5f5;
        }
        
        .container {
            display: grid;
            grid-template-columns: 250px 1fr;
            min-height: 100vh;
        }
        
        .sidebar {
            background: #2c3e50;
            color: white;
            padding: 20px;
            position: fixed;
            height: 100vh;
            width: 250px;
            overflow-y: auto;
        }
        
        .sidebar h2 {
            margin-bottom: 20px;
            color: #3498db;
        }
        
        .sidebar ul {
            list-style: none;
        }
        
        .sidebar li {
            margin: 10px 0;
        }
        
        .sidebar a {
            color: #ecf0f1;
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .sidebar a:hover {
            color: #3498db;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: none;
            border-radius: 5px;
            background: #34495e;
            color: white;
        }
        
        .search-box::placeholder {
            color: #95a5a6;
        }
        
        .content {
            margin-left: 250px;
            padding: 40px;
            background: white;
        }
        
        .code-example {
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .code-example p {
            padding: 10px;
            background: #f8f9fa;
            margin: 0;
        }
        
        .code-example .highlight {
            margin: 0;
            padding: 15px;
            background: #272822;
            color: #f8f8f2;
        }
        
        .code-example button {
            margin: 10px;
            padding: 8px 15px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        
        .code-example button:hover {
            background: #2980b9;
        }
        
        .try-it-now {
            margin: 20px 0;
            padding: 15px;
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            border-radius: 3px;
        }
        
        .try-it-now button {
            padding: 10px 20px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        
        .result {
            margin-top: 10px;
            padding: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 3px;
            display: none;
        }
        
        .result.show {
            display: block;
        }
        
        h1, h2, h3 { margin: 20px 0 10px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        h3 { color: #7f8c8d; }
        
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        .search-results {
            display: none;
            margin-top: 10px;
        }
        
        .search-results.show {
            display: block;
        }
        
        .search-result-item {
            padding: 10px;
            margin: 5px 0;
            background: #34495e;
            border-radius: 3px;
            cursor: pointer;
        }
        
        .search-result-item:hover {
            background: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>📚 Documentation</h2>
            <input type="text" class="search-box" placeholder="Search docs..." onkeyup="searchDocs(this.value)">
            <div class="search-results" id="searchResults"></div>
            <ul id="nav">
                {% for item in navigation %}
                <li><a href="#{{ item.id }}">{{ item.title }}</a></li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="content">
            {{ content|safe }}
        </div>
    </div>
    
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'default' });
        
        function copyCode(btn) {
            const code = btn.previousElementSibling.textContent;
            navigator.clipboard.writeText(code);
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = 'Copy', 2000);
        }
        
        async function runCode(btn, language) {
            const code = btn.previousElementSibling.previousElementSibling.textContent;
            btn.textContent = 'Running...';
            
            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code, language })
                });
                const result = await response.json();
                alert('Output: ' + result.output);
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                btn.textContent = 'Run';
            }
        }
        
        async function tryEndpoint(method, path) {
            const resultId = `result-${method}-${path.replace(/\\//g, '-')}`;
            const resultEl = document.getElementById(resultId);
            
            resultEl.textContent = 'Loading...';
            resultEl.classList.add('show');
            
            try {
                const response = await fetch(path, { method });
                const data = await response.json();
                resultEl.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultEl.textContent = 'Error: ' + error.message;
            }
        }
        
        let searchIndex = null;
        
        async function loadSearchIndex() {
            if (!searchIndex) {
                const response = await fetch('/search-index.json');
                searchIndex = await response.json();
            }
            return searchIndex;
        }
        
        async function searchDocs(query) {
            if (!query || query.length < 2) {
                document.getElementById('searchResults').classList.remove('show');
                return;
            }
            
            const index = await loadSearchIndex();
            const results = [];
            const queryLower = query.toLowerCase();
            
            // Search in keywords
            for (const [keyword, docIds] of Object.entries(index.keywords)) {
                if (keyword.includes(queryLower)) {
                    docIds.forEach(id => {
                        const doc = index.documents[id];
                        if (!results.find(r => r.id === id)) {
                            results.push(doc);
                        }
                    });
                }
            }
            
            // Display results
            const resultsEl = document.getElementById('searchResults');
            if (results.length > 0) {
                resultsEl.innerHTML = results.slice(0, 5).map(doc => 
                    `<div class="search-result-item" onclick="location.href='${doc.url}'">
                        ${doc.title}
                    </div>`
                ).join('');
                resultsEl.classList.add('show');
            } else {
                resultsEl.classList.remove('show');
            }
        }
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    </script>
</body>
</html>
        '''
        return template
    
    def build_documentation(self, docs_dir: Path = DOCS_DIR, output_dir: Path = OUTPUT_DIR):
        """Build complete documentation site"""
        
        print("Building documentation...")
        
        # Collect all markdown files
        docs = []
        for md_file in docs_dir.glob('**/*.md'):
            with open(md_file) as f:
                content = f.read()
            
            # Convert markdown to HTML
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
            
            docs.append({
                'title': md_file.stem.replace('_', ' ').title(),
                'url': f"/{md_file.stem}.html",
                'content': html_content,
                'source': str(md_file)
            })
        
        # Generate search index
        search_index = self.generate_search_index(docs)
        with open(output_dir / 'search-index.json', 'w') as f:
            json.dump(search_index, f)
        
        # Generate navigation
        navigation = [{'id': doc['title'].lower().replace(' ', '-'), 'title': doc['title']} for doc in docs]
        
        # Generate HTML template
        template = Template(self.generate_html_template())
        
        # Build each page
        for doc in docs:
            html = template.render(
                title=doc['title'],
                content=doc['content'],
                navigation=navigation
            )
            
            output_file = output_dir / f"{Path(doc['source']).stem}.html"
            with open(output_file, 'w') as f:
                f.write(html)
            
            print(f"  ✅ Generated: {output_file}")
        
        # Generate index page
        index_content = "<h1>Welcome to Interactive Documentation</h1>"
        index_content += "<ul>"
        for doc in docs:
            index_content += f"<li><a href='{doc['url']}'>{doc['title']}</a></li>"
        index_content += "</ul>"
        
        index_html = template.render(
            title="Home",
            content=index_content,
            navigation=navigation
        )
        
        with open(output_dir / 'index.html', 'w') as f:
            f.write(index_html)
        
        print(f"\n✅ Documentation built successfully: {output_dir}/")
        print(f"   Open: file://{output_dir.absolute()}/index.html")

def create_sample_docs():
    """Create sample documentation"""
    
    DOCS_DIR.mkdir(exist_ok=True)
    
    # Getting Started
    getting_started = '''
# Getting Started

Welcome to the server initialization system!

## Installation

```bash
git clone https://github.com/example/server-init
cd server-init
./install.sh
```

## Quick Start

Deploy your first service:

```bash
dev-cli new my-service --template python-microservice
cd my-service
dev-cli run
```

## Next Steps

- [Architecture Overview](architecture.html)
- [API Reference](api.html)
- [Deployment Guide](deployment.html)
'''
    
    # Architecture
    architecture = '''
# Architecture Overview

## System Components

```mermaid
graph TB
    A[Client] -->|HTTPS| B[API Gateway]
    B --> C[Service Mesh]
    C --> D[Microservices]
    D --> E[Database]
```

## Key Features

- **Auto-scaling**: 0-N scaling with Knative
- **GitOps**: Automated deployments with ArgoCD
- **Observability**: 100% coverage with APM
'''
    
    # API Reference
    api_reference = '''
# API Reference

## Health Check

**GET** `/health`

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}
```

## Metrics

**GET** `/metrics`

Prometheus metrics endpoint.
'''
    
    (DOCS_DIR / 'getting-started.md').write_text(getting_started)
    (DOCS_DIR / 'architecture.md').write_text(architecture)
    (DOCS_DIR / 'api-reference.md').write_text(api_reference)
    
    print("✅ Sample documentation created")

def main():
    """Main entry point"""
    
    generator = DocumentationGenerator()
    
    if '--create-sample' in sys.argv:
        create_sample_docs()
        
    elif '--build' in sys.argv:
        docs_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DOCS_DIR
        output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else OUTPUT_DIR
        generator.build_documentation(docs_dir, output_dir)
        
    elif '--serve' in sys.argv:
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        os.chdir(OUTPUT_DIR)
        subprocess.run(['python', '-m', 'http.server', str(port)])
        
    else:
        print("Interactive Documentation System v11.0")
        print("")
        print("Usage:")
        print("  --create-sample           Create sample documentation")
        print("  --build [DOCS] [OUTPUT]   Build documentation site")
        print("  --serve [PORT]            Serve documentation (default: 8000)")

if __name__ == '__main__':
    main()
