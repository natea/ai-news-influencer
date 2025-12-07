# 💡 Basic Development DevPod

This branch contains a ready-to-use development environment with Docker-in-Docker and Node.js support.

## 🚀 Quick Start with DevPod

```bash
# Correct syntax using @ notation (Fix for Issue #5)
devpod up https://github.com/jedarden/agentists-quickstart@workspace/basic

# Alternative: Using git URL fragment
devpod up https://github.com/jedarden/agentists-quickstart.git#workspace/basic
```

## 📦 What's Included

- **🖼️ Base Image**: Debian-based development container
- **🐳 Docker-in-Docker**: Build and run containers within your development environment
- **🟢 Node.js**: Full Node.js development environment
- **🐍 Python**: Python development environment
- **🛠️ Development Tools** (auto-installed on container creation):
  - tmux: Terminal multiplexer for managing multiple sessions
  - claude-code: Anthropic's official CLI for Claude
  - GitHub CLI (gh): Command-line interface for GitHub
  - ccdash: Claude Code dashboard for monitoring usage
  - MANA: Memory-Augmented Neural Assistant for Claude Code context injection
- **🧬 VS Code Extensions**:
  - Roo Cline: AI-powered coding assistant
  - GistFS: Access GitHub Gists directly in VS Code
  - GitHub Copilot: AI pair programming
  - GitHub Copilot Chat: Conversational AI assistance
  - Kilo Code: AI coding assistant
- **⚙️ Claude Code Configuration**:
  - Pre-configured MANA hooks in `.claude/settings.json` for enhanced context injection

## ✨ Features

- Runs with privileged access to support Docker operations
- Configured for the `vscode` user
- Persistent container (won't shutdown on disconnect)
- Automatic tool installation with graceful fallback and detailed installation report
- Installation report saved to `.devcontainer/installation-report.md` for troubleshooting
- If automatic installation fails during container startup, run manually: `bash .devcontainer/install-tools.sh`

## 📋 Requirements

- [DevPod CLI](https://devpod.sh/docs/getting-started/install)
- Docker Desktop or Docker Engine
- Active GitHub Copilot subscription (for Copilot features)

## 🛠️ Tool Installation

The development tools are automatically installed when the container starts via `.devcontainer/install-tools.sh`. However, this automatic installation may occasionally fail due to timing or permission issues during container initialization.

### Manual Installation

If any tools fail to install automatically, you can run the installation script manually:

```bash
bash .devcontainer/install-tools.sh
```

This will:
- Attempt to install all missing tools
- Generate a detailed report at `.devcontainer/installation-report.md`
- Provide manual installation instructions for any tools that fail

### Viewing Installation Status

To check which tools were successfully installed:

```bash
cat .devcontainer/installation-report.md
```

## 🔧 Manual VS Code Usage

If you prefer to use VS Code directly:

1. Clone this branch: `git clone -b workspace/basic https://github.com/jedarden/agentists-quickstart`
2. Open in VS Code
3. Install the Dev Containers extension
4. Click "Reopen in Container" when prompted

## 📚 Learn More

For more information about the Agentists project, visit the [main branch](https://github.com/jedarden/agentists-quickstart).