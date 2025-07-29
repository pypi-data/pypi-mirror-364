# Installation Guide - IPC Framework

This guide covers installation for **Node.js ↔ Python** backend IPC communication.

## 🚨 **IMPORTANT: Version 1.1.0 Update**

**If you have Python IPC Framework installed, please upgrade immediately:**

```bash
pip install --upgrade ipc-framework
```

**Version 1.0.0 had critical bugs making it largely non-functional. Version 1.1.0 fixes all major issues.**

## Python Server Installation

### Basic Installation

```bash
pip install --upgrade ipc-framework  # Gets v1.1.0 with bug fixes
```

### With Optional Dependencies

```bash
# Install with example dependencies (includes psutil for monitoring examples)
pip install ipc-framework[examples]

# Install with development dependencies
pip install ipc-framework[dev]

# Install everything
pip install ipc-framework[all]
```

### Requirements

- Python 3.7+
- No external dependencies for core functionality

## Node.js Client Installation

### Basic Installation

```bash
npm install @ifesol/ipc-framework-nodejs
```

### Requirements

- Node.js 14+ 
- No external dependencies (uses built-in `net` module for TCP)

### Verify Installation

```python
from ipc_framework import FrameworkServer, FrameworkClient
print("IPC Framework installed successfully!")
```

## JavaScript/TypeScript Package Installation

### Node.js Projects

```bash
# Install the IPC client
npm install @ifesol/ipc-framework-js

# Also install WebSocket dependency for Node.js
npm install ws
npm install --save-dev @types/ws  # If using TypeScript
```

### Browser Projects (Bundled)

```bash
# For projects using Webpack, Rollup, Vite, etc.
npm install @ifesol/ipc-framework-js
# No additional dependencies needed
```

### CDN (Direct Browser Usage)

```html
<!-- UMD Bundle -->
<script src="https://unpkg.com/@ifesol/ipc-framework-js@1.0.0/dist/browser/index.js"></script>

<!-- ES Module -->
<script type="module">
  import { IPCClient } from 'https://unpkg.com/@ifesol/ipc-framework-js@1.0.0/dist/browser/index.esm.js';
</script>
```

### Verify Installation

#### Node.js

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-js');
console.log('IPC Framework JS installed successfully!');
```

#### ES Modules

```javascript
import { IPCClient } from '@ifesol/ipc-framework-js';
console.log('IPC Framework JS installed successfully!');
```

#### Browser (UMD)

```html
<script src="https://unpkg.com/@ifesol/ipc-framework-js@1.0.0/dist/browser/index.js"></script>
<script>
  console.log('IPC Framework available:', typeof IPCFramework !== 'undefined');
</script>
```

## Development Setup

### Python Development

```bash
# Clone repository
git clone https://github.com/ifesol/ipc-framework.git
cd ipc-framework

# Install in development mode
pip install -e ".[dev,examples]"

# Run tests
pytest tests/

# Run examples
python examples/basic_server.py
```

### JavaScript Development

```bash
# Clone repository
git clone https://github.com/ifesol/ipc-framework-js.git
cd ipc-framework-js

# Install dependencies
npm install

# Build packages
npm run build

# Run tests
npm test

# Start development mode
npm run dev
```

## Environment-Specific Configuration

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2020", "DOM"],
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true
  }
}
```

### Webpack Configuration

```javascript
// webpack.config.js
module.exports = {
  resolve: {
    fallback: {
      // For browser builds, exclude Node.js modules
      "crypto": false,
      "stream": false,
      "util": false
    }
  }
};
```

### Vite Configuration

```javascript
// vite.config.js
export default {
  define: {
    global: 'globalThis',
  },
  resolve: {
    alias: {
      '@ifesol/ipc-framework-js': '@ifesol/ipc-framework-js/dist/browser/index.esm.js'
    }
  }
};
```

## Version Compatibility

### Python Package Versions

| Version | Python Support | Features |
|---------|---------------|----------|
| 1.0.0   | 3.7+         | Core IPC, Examples, CLI tools |

### JavaScript Package Versions

| Version | Node.js | Browser | Features |
|---------|---------|---------|----------|
| 1.0.0   | 16+     | Modern  | Core IPC, TypeScript, Dual builds |

## Troubleshooting

### Common Installation Issues

#### Python: "No module named 'ipc_framework'"

```bash
# Ensure you're in the correct virtual environment
which python
pip list | grep ipc-framework

# Reinstall if necessary
pip uninstall ipc-framework
pip install ipc-framework
```

#### Node.js: "Cannot find module 'ws'"

```bash
# Install WebSocket dependency for Node.js
npm install ws
npm install --save-dev @types/ws  # For TypeScript
```

#### Browser: "WebSocket implementation not available"

This error occurs when:
1. Using Node.js build in browser
2. Missing WebSocket polyfill

**Solution:**
```html
<!-- Use browser build -->
<script src="https://unpkg.com/@ifesol/ipc-framework-js/dist/browser/index.js"></script>
```

#### Bundler: "Module not found" errors

For Webpack/Rollup/Vite:
```javascript
// Ensure proper module resolution
resolve: {
  alias: {
    '@ifesol/ipc-framework-js': '@ifesol/ipc-framework-js/dist/browser/index.esm.js'
  }
}
```

### Performance Considerations

#### Python

- Use virtual environments to avoid conflicts
- Consider `uvloop` for better async performance
- Use connection pooling for high-load scenarios

#### JavaScript

- Use ES modules for better tree-shaking
- Enable gzip compression for browser builds
- Consider connection pooling for Node.js servers

## Next Steps

After installation:

1. **Read the API Documentation**: See [Python API](./python-api.md) and [JavaScript API](./javascript-api.md)
2. **Try the Examples**: Check out [Examples](./examples.md)
3. **Integration Guides**: See [Integration](./integration.md) for framework-specific guides 