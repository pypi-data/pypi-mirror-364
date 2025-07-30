# Autostartx - Turn Any Command into a Service

Transform any command-line program into an auto-restarting background service with a single command. Simple, fast, zero configuration.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[中文文档](README_zh.md) | [English](README.md)

## Quick Start

**Option 1: One-time use with uvx**
```bash
# Turn long-running commands into services
uvx --from git+https://github.com/faker2048/autostartx.git autostartx add "python -m http.server 8000" --name web
uvx --from git+https://github.com/faker2048/autostartx.git autostartx add "npm run dev" --name frontend
```

**Option 2: Install to system**
```bash
# Install once, use anywhere
uvx --from git+https://github.com/faker2048/autostartx.git autostartx install
autostartx add "python -m http.server 8000" --name web
autostartx add "tailscale up --ssh" --name vpn
```

**Option 3: Traditional install**
```bash
git clone https://github.com/faker2048/autostartx.git && cd autostartx && pip install .
```

**Check your services**
```bash
autostartx list        # Show all services
autostartx logs web -f # View logs
```

## Commands

```bash
autostartx add "command"           # Add service
autostartx list                   # Show services
autostartx start/stop/restart     # Control services  
autostartx logs <name> -f         # View logs
autostartx daemon --action start  # Auto-restart daemon
```

## Why Autostartx?

- **Simple**: One command to turn any long-running process into a service
- **Reliable**: Automatic restarts when processes crash
- **Cross-platform**: Works on Windows, Linux, macOS
- **Zero config**: No setup files needed

Perfect for dev servers, background daemons, monitoring tools, proxy services.

## License

MIT License