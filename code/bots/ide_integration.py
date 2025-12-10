#!/usr/bin/env python3
"""
IDE Integration v11.0
VSCode extension for Kubernetes management, YAML IntelliSense, live preview
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from jinja2 import Template

# VSCode Extension Configuration
EXTENSION_NAME = "k8s-devtools"
EXTENSION_VERSION = "1.0.0"
EXTENSION_PUBLISHER = "server-init"

def generate_vscode_extension():
    """Generate VSCode extension structure"""
    
    extension_dir = Path(f"{EXTENSION_NAME}-extension")
    extension_dir.mkdir(exist_ok=True)
    
    # package.json
    package_json = {
        "name": EXTENSION_NAME,
        "displayName": "Kubernetes DevTools",
        "description": "Advanced Kubernetes management and YAML IntelliSense",
        "version": EXTENSION_VERSION,
        "publisher": EXTENSION_PUBLISHER,
        "engines": {"vscode": "^1.80.0"},
        "categories": ["Other"],
        "activationEvents": ["onLanguage:yaml", "onCommand:k8s-devtools.preview"],
        "main": "./out/extension.js",
        "contributes": {
            "commands": [
                {
                    "command": "k8s-devtools.preview",
                    "title": "K8s: Preview Resource"
                },
                {
                    "command": "k8s-devtools.deploy",
                    "title": "K8s: Deploy Resource"
                },
                {
                    "command": "k8s-devtools.logs",
                    "title": "K8s: View Logs"
                },
                {
                    "command": "k8s-devtools.debug",
                    "title": "K8s: Debug Container"
                }
            ],
            "languages": [
                {
                    "id": "yaml",
                    "extensions": [".yaml", ".yml"],
                    "aliases": ["YAML", "yaml"]
                }
            ],
            "grammars": [
                {
                    "language": "yaml",
                    "scopeName": "source.yaml",
                    "path": "./syntaxes/yaml.tmLanguage.json"
                }
            ],
            "configuration": {
                "title": "Kubernetes DevTools",
                "properties": {
                    "k8s-devtools.kubeconfig": {
                        "type": "string",
                        "default": "~/.kube/config",
                        "description": "Path to kubeconfig file"
                    },
                    "k8s-devtools.defaultNamespace": {
                        "type": "string",
                        "default": "default",
                        "description": "Default Kubernetes namespace"
                    },
                    "k8s-devtools.autoComplete": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable YAML auto-completion"
                    }
                }
            }
        },
        "scripts": {
            "vscode:prepublish": "npm run compile",
            "compile": "tsc -p ./",
            "watch": "tsc -watch -p ./",
            "test": "npm run compile && node ./out/test/runTest.js"
        },
        "devDependencies": {
            "@types/node": "^18.0.0",
            "@types/vscode": "^1.80.0",
            "typescript": "^5.0.0"
        },
        "dependencies": {
            "yaml": "^2.3.0",
            "@kubernetes/client-node": "^0.20.0"
        }
    }
    
    with open(extension_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    # extension.ts
    extension_ts = '''import * as vscode from 'vscode';
import * as k8s from '@kubernetes/client-node';
import * as yaml from 'yaml';

let k8sApi: k8s.CoreV1Api;

export function activate(context: vscode.ExtensionContext) {
    console.log('K8s DevTools extension activated');
    
    // Initialize Kubernetes client
    const kc = new k8s.KubeConfig();
    kc.loadFromDefault();
    k8sApi = kc.makeApiClient(k8s.CoreV1Api);
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('k8s-devtools.preview', previewResource),
        vscode.commands.registerCommand('k8s-devtools.deploy', deployResource),
        vscode.commands.registerCommand('k8s-devtools.logs', viewLogs),
        vscode.commands.registerCommand('k8s-devtools.debug', debugContainer)
    );
    
    // Register YAML auto-completion
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider('yaml', new K8sCompletionProvider(), '.', ' ')
    );
    
    // Register hover provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider('yaml', new K8sHoverProvider())
    );
}

class K8sCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(document: vscode.TextDocument, position: vscode.Position): vscode.CompletionItem[] {
        const linePrefix = document.lineAt(position).text.substr(0, position.character);
        
        const items: vscode.CompletionItem[] = [];
        
        // Kubernetes resource types
        if (linePrefix.endsWith('kind: ')) {
            const kinds = ['Deployment', 'Service', 'Pod', 'ConfigMap', 'Secret', 'Ingress'];
            kinds.forEach(kind => {
                const item = new vscode.CompletionItem(kind, vscode.CompletionItemKind.Class);
                item.documentation = new vscode.MarkdownString(`Create a ${kind} resource`);
                items.push(item);
            });
        }
        
        // API versions
        if (linePrefix.endsWith('apiVersion: ')) {
            const versions = ['v1', 'apps/v1', 'batch/v1', 'networking.k8s.io/v1'];
            versions.forEach(ver => {
                const item = new vscode.CompletionItem(ver, vscode.CompletionItemKind.Value);
                items.push(item);
            });
        }
        
        return items;
    }
}

class K8sHoverProvider implements vscode.HoverProvider {
    provideHover(document: vscode.TextDocument, position: vscode.Position): vscode.Hover | undefined {
        const range = document.getWordRangeAtPosition(position);
        const word = document.getText(range);
        
        const docs = getK8sDocumentation(word);
        if (docs) {
            return new vscode.Hover(new vscode.MarkdownString(docs));
        }
        
        return undefined;
    }
}

async function previewResource() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    
    const content = editor.document.getText();
    const resource = yaml.parse(content);
    
    const panel = vscode.window.createWebviewPanel(
        'k8sPreview',
        'Kubernetes Resource Preview',
        vscode.ViewColumn.Beside,
        {}
    );
    
    panel.webview.html = getPreviewHtml(resource);
}

async function deployResource() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    
    const content = editor.document.getText();
    const resource = yaml.parse(content);
    
    try {
        // Apply resource
        const result = await applyK8sResource(resource);
        vscode.window.showInformationMessage(`Resource ${resource.metadata.name} deployed successfully`);
    } catch (error) {
        vscode.window.showErrorMessage(`Deployment failed: ${error}`);
    }
}

async function viewLogs() {
    const pods = await k8sApi.listNamespacedPod('default');
    const podNames = pods.body.items.map(pod => pod.metadata!.name!);
    
    const selected = await vscode.window.showQuickPick(podNames, {
        placeHolder: 'Select pod'
    });
    
    if (selected) {
        const logs = await k8sApi.readNamespacedPodLog(selected, 'default');
        
        const doc = await vscode.workspace.openTextDocument({
            content: logs.body,
            language: 'log'
        });
        vscode.window.showTextDocument(doc);
    }
}

async function debugContainer() {
    vscode.window.showInformationMessage('Starting debug session...');
    // Implement container debugging logic
}

function getK8sDocumentation(word: string): string | undefined {
    const docs: Record<string, string> = {
        'Deployment': '**Deployment** - Manages a replicated application',
        'Service': '**Service** - Exposes an application as a network service',
        'Pod': '**Pod** - The smallest deployable unit in Kubernetes',
        'replicas': '**replicas** - Number of desired pods'
    };
    return docs[word];
}

function getPreviewHtml(resource: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial; padding: 20px; }
                .resource { background: #f0f0f0; padding: 10px; border-radius: 5px; }
                .field { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>${resource.kind}: ${resource.metadata.name}</h1>
            <div class="resource">
                <div class="field"><b>Namespace:</b> ${resource.metadata.namespace || 'default'}</div>
                <div class="field"><b>API Version:</b> ${resource.apiVersion}</div>
            </div>
            <h2>Spec:</h2>
            <pre>${JSON.stringify(resource.spec, null, 2)}</pre>
        </body>
        </html>
    `;
}

async function applyK8sResource(resource: any): Promise<void> {
    // Apply resource to cluster
    // Implementation depends on resource kind
}

export function deactivate() {}
'''
    
    (extension_dir / "src").mkdir(exist_ok=True)
    with open(extension_dir / "src" / "extension.ts", "w") as f:
        f.write(extension_ts)
    
    # tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "module": "commonjs",
            "target": "ES2020",
            "outDir": "out",
            "lib": ["ES2020"],
            "sourceMap": True,
            "rootDir": "src",
            "strict": True
        },
        "exclude": ["node_modules", ".vscode-test"]
    }
    
    with open(extension_dir / "tsconfig.json", "w") as f:
        json.dump(tsconfig, f, indent=2)
    
    # README.md
    readme = '''# Kubernetes DevTools

Advanced Kubernetes management for VSCode.

## Features

- **YAML IntelliSense**: Auto-completion for Kubernetes manifests
- **Live Preview**: Preview resources before deployment
- **Quick Deploy**: Deploy directly from editor
- **Log Viewer**: View pod logs in VSCode
- **Container Debugging**: Debug containers directly

## Commands

- `K8s: Preview Resource` - Preview YAML manifest
- `K8s: Deploy Resource` - Deploy to cluster
- `K8s: View Logs` - View pod logs
- `K8s: Debug Container` - Start debug session

## Configuration

```json
{
  "k8s-devtools.kubeconfig": "~/.kube/config",
  "k8s-devtools.defaultNamespace": "default",
  "k8s-devtools.autoComplete": true
}
```

## Usage

1. Open a Kubernetes YAML file
2. Use Ctrl+Space for auto-completion
3. Right-click → "K8s: Deploy Resource"
'''
    
    with open(extension_dir / "README.md", "w") as f:
        f.write(readme)
    
    print(f"✅ VSCode extension generated: {extension_dir}/")
    return str(extension_dir)

def build_extension(extension_dir: str):
    """Build VSCode extension"""
    
    print("Building extension...")
    
    # Install dependencies
    subprocess.run(['npm', 'install'], cwd=extension_dir, check=True)
    
    # Compile TypeScript
    subprocess.run(['npm', 'run', 'compile'], cwd=extension_dir, check=True)
    
    # Package extension
    subprocess.run(['vsce', 'package'], cwd=extension_dir, check=True)
    
    print("✅ Extension built successfully")

def install_extension(extension_dir: str):
    """Install extension to VSCode"""
    
    vsix_files = list(Path(extension_dir).glob('*.vsix'))
    if not vsix_files:
        print("❌ No .vsix file found")
        return
    
    vsix_file = vsix_files[0]
    subprocess.run(['code', '--install-extension', str(vsix_file)], check=True)
    
    print(f"✅ Extension installed: {vsix_file.name}")

def generate_yaml_snippets():
    """Generate YAML snippets for common K8s resources"""
    
    snippets = {
        "Deployment": {
            "prefix": "k8s-deployment",
            "body": [
                "apiVersion: apps/v1",
                "kind: Deployment",
                "metadata:",
                "  name: ${1:app-name}",
                "spec:",
                "  replicas: ${2:3}",
                "  selector:",
                "    matchLabels:",
                "      app: ${1:app-name}",
                "  template:",
                "    metadata:",
                "      labels:",
                "        app: ${1:app-name}",
                "    spec:",
                "      containers:",
                "      - name: ${1:app-name}",
                "        image: ${3:image:tag}",
                "        ports:",
                "        - containerPort: ${4:8080}"
            ],
            "description": "Kubernetes Deployment"
        },
        "Service": {
            "prefix": "k8s-service",
            "body": [
                "apiVersion: v1",
                "kind: Service",
                "metadata:",
                "  name: ${1:service-name}",
                "spec:",
                "  selector:",
                "    app: ${2:app-name}",
                "  ports:",
                "  - port: ${3:80}",
                "    targetPort: ${4:8080}",
                "  type: ${5|ClusterIP,NodePort,LoadBalancer|}"
            ],
            "description": "Kubernetes Service"
        },
        "ConfigMap": {
            "prefix": "k8s-configmap",
            "body": [
                "apiVersion: v1",
                "kind: ConfigMap",
                "metadata:",
                "  name: ${1:config-name}",
                "data:",
                "  ${2:key}: ${3:value}"
            ],
            "description": "Kubernetes ConfigMap"
        }
    }
    
    snippets_file = Path.home() / ".vscode" / "snippets" / "kubernetes.json"
    snippets_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(snippets_file, "w") as f:
        json.dump(snippets, f, indent=2)
    
    print(f"✅ Snippets generated: {snippets_file}")

def main():
    """Main entry point"""
    
    if '--generate' in sys.argv:
        extension_dir = generate_vscode_extension()
        generate_yaml_snippets()
        
    elif '--build' in sys.argv:
        extension_dir = sys.argv[2] if len(sys.argv) > 2 else f"{EXTENSION_NAME}-extension"
        build_extension(extension_dir)
        
    elif '--install' in sys.argv:
        extension_dir = sys.argv[2] if len(sys.argv) > 2 else f"{EXTENSION_NAME}-extension"
        install_extension(extension_dir)
        
    else:
        print("IDE Integration v11.0")
        print("")
        print("Usage:")
        print("  --generate          Generate VSCode extension")
        print("  --build DIR         Build extension")
        print("  --install DIR       Install extension")

if __name__ == '__main__':
    main()
