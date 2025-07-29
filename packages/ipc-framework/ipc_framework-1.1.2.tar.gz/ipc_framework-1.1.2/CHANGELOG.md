# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.3] - 2024-01-XX

### Documentation Distribution
- **FIXED**: Documentation now included in published NPM package
- **ADDED**: `docs/`, `examples/`, `test/` directories to NPM package files
- **FIXED**: Documentation now included in Python package via updated MANIFEST.in
- **PACKAGE SIZE**: NPM package now ~265KB (vs 25KB) with full documentation
- **DISTRIBUTION**: Users can now access docs offline after `npm install`

## [1.1.2] - 2024-01-XX

### Fixed (PyPI Documentation)
- **CRITICAL**: Fixed PyPI documentation to correctly describe Python TCP server (not WebSocket)
- **CRITICAL**: Updated package references from `@ifesol/ipc-framework-js` to `@ifesol/ipc-framework-nodejs`
- **CRITICAL**: Removed incorrect WebSocket architecture descriptions
- **CRITICAL**: Updated to focus on Python server capabilities with Node.js client integration
- **IMPROVED**: Added correct TCP-based performance characteristics and use cases

### Changed (Documentation)
- **BREAKING**: Documentation now correctly represents this as Python server package
- **ARCHITECTURE**: Properly describes TCP socket communication (not WebSocket)
- **EXAMPLES**: Python-focused examples with correct Node.js client integration
- **METADATA**: Updated package description and keywords for better discoverability

### Package Contents
**NPM Package now includes:**
- Core implementation (`index.js`, `src/tcp-client.js`)
- **Full documentation** (`docs/nodejs-package.md`, `docs/api-reference.md`, etc.)
- **Working examples** (`examples/basic-usage.js`, `examples/express-integration.js`)
- **Tests** (`test/basic-test.js`)

**Python Package now includes:**
- All Python source code and examples
- **Full documentation** (`docs/` directory with all .md files)
- **CHANGELOG.md** for version history

## [1.1.2] - 2024-01-XX

### Documentation
- **UPDATED**: Comprehensive `docs/nodejs-package.md` documentation with v1.1.1 fixes
- **ADDED**: Complete API reference with TCP implementation details
- **ADDED**: Express.js integration examples and patterns
- **ADDED**: Microservices architecture examples
- **ADDED**: Advanced usage patterns (connection pooling, message queuing)
- **ADDED**: Performance optimization techniques
- **ADDED**: Migration guide from broken v1.1.0
- **ADDED**: Troubleshooting section with common issues
- **REMOVED**: All outdated WebSocket/browser references

### Changes
- No code changes - documentation-only release
- Package includes updated comprehensive documentation

## [1.1.1] - 2024-01-XX

### CRITICAL FIXES
- **FIXED**: Replaced broken WebSocket implementation with TCP socket communication
- **FIXED**: Removed module system conflicts (CommonJS/ESM) that caused require() errors
- **FIXED**: Eliminated WebSocket dependency resolution issues  
- **FIXED**: Removed complex Rollup/TypeScript build system causing distribution problems
- **FIXED**: Context-dependent behavior that made package work from CLI but fail in scripts

### Changed
- **BREAKING**: Now uses TCP sockets instead of WebSockets for Python server communication
- **ARCHITECTURE**: Simplified to pure CommonJS module (removed ESM complexity)
- **BUILD**: Removed Rollup, TypeScript, and complex build pipeline 
- **DEPENDENCIES**: Removed all external dependencies - now uses only Node.js built-ins
- **PACKAGE**: Simplified structure with direct `index.js` entry point

### Added
- Full TCP message framing with proper buffering for reliable communication
- Automatic reconnection with configurable attempts and delays
- Heartbeat system for connection health monitoring
- Express.js middleware integration helper
- Comprehensive error handling and logging
- Server-Sent Events example for real-time browser updates

### Technical Details
- Uses `net` module for raw TCP socket communication (matches Python server protocol)
- Implements 4-byte length headers for proper message framing
- Fixed message field names to match Python server (`message_id` vs `messageId`)
- Added connection pooling support for high-throughput applications
- Improved memory management with proper buffer cleanup

### Migration from 1.1.0
The v1.1.0 package was fundamentally broken. v1.1.1 is a complete rewrite:

```javascript
// OLD (v1.1.0) - BROKEN
const { IPCClient } = require('@ifesol/ipc-framework-nodejs'); // Failed to load

// NEW (v1.1.1) - WORKING  
const { IPCClient } = require('@ifesol/ipc-framework-nodejs'); // ✅ Works correctly
const client = new IPCClient('my-app');
await client.connect(); // ✅ TCP connection to Python server
```

## [1.1.0] - 2024-01-XX

### Fixed (Python Package Only)
- **CRITICAL**: Fixed missing `create_response()` method in Message class
- **CRITICAL**: Fixed socket timeout deadlock in client after successful handshake  
- **CRITICAL**: Fixed threading deadlock in receive operations causing eternal hangs
- **PERFORMANCE**: Optimized message handling and reduced memory usage
- **STABILITY**: Improved error handling and connection resilience

### Added (Python Package Only)
- Enhanced logging for better debugging
- Connection state validation
- Automatic cleanup of failed connections
- Performance monitoring capabilities

### Technical Details (Python Package Only)
- Removed socket timeout after successful connection establishment
- Removed socket lock from `_receive_message()` method to prevent deadlocks
- Added proper message creation API matching documentation
- Fixed notification delivery mechanism

## [1.0.0] - 2024-01-XX

### Added
- Initial release of IPC Framework
- WebSocket-based communication (later found to be incompatible with Python servers)
- Basic client-server messaging
- Channel subscription system
- Real-time notifications

### Known Issues (Fixed in 1.1.1)
- ❌ Used WebSocket instead of TCP (incompatible with Python servers)
- ❌ Module system conflicts preventing package loading
- ❌ Complex build system causing distribution issues
- ❌ Dependency resolution problems with 'ws' package 