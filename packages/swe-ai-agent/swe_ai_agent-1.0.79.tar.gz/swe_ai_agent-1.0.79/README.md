# SWE Agent - AI Coding Assistant

An AI Coding Agent that helps you write, analyze, and improve code in any programming language.

## Why Use SWE Agent?

**Save time writing code** - Tell it what you want to build, and it writes the code for you. No more staring at blank files or wrestling with syntax.

**Fix bugs faster** - It reads your code, finds problems, and suggests fixes. Like having an experienced developer review your work instantly.

**Learn while you code** - Watch how it solves problems step by step. You'll pick up new techniques and best practices naturally.

**Work in any language** - Python, JavaScript, Go, Rust, C++ - it understands them all. Switch between projects without missing a beat.

**Stay secure** - Automatically scans your code for security issues before you deploy. Catch vulnerabilities early.

## Installation

```bash
pip install swe-ai-agent
```

## Getting Started

Please add ANTHROPIC_API_KEY in environment variable for using this:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"

# Chat with your AI coding partner
swe-agent --pair

# Run one-time tasks
swe-agent --task "create a todo app with React"

# Work interactively on multiple tasks
swe-agent --interactive

# Use the modern terminal interface
swe-agent --warp

# Enable advanced features with external services
swe-agent --enable-mcp --interactive
```

## New: Visual Diff Display ✨

See exactly what changes SWE Agent makes to your code with beautiful diff visualization:

```bash
# Enable visual diffs (default: enabled)
swe-agent --task "refactor my code" --show-diffs

# Debug mode for detailed operation logs
swe-agent --task "fix the bug" --debug-mode
```

**Visual Features:**
- 🟢 **Green borders** for file creation
- 🔵 **Blue borders** for file edits  
- 🟡 **Yellow borders** for content replacement
- 🔴 **Red borders** for file rewrites
- **Line-by-line diffs** with syntax highlighting
- **Before/after comparisons** for all file operations

## What It Can Do

### Write Code for You
- Build complete applications from a simple description
- Generate functions and classes that actually work
- Create tests for your existing code
- Write documentation that makes sense

### Improve Existing Code
- Find and fix bugs before they cause problems
- Refactor messy code into clean, readable functions
- Add features to existing projects without breaking things
- Optimize performance bottlenecks

### Keep You Secure
- Scan for vulnerabilities in real-time
- Suggest security fixes with clear explanations
- Check dependencies for known issues
- Follow security best practices automatically

### Speed Up Your Workflow
- Search through large codebases instantly
- Navigate complex projects with ease
- Track changes and see what was modified
- Integrate with git seamlessly

## How It Works

You have four ways to work with SWE Agent:

**Pair Programming (--pair)** - Like having a coding buddy next to you. Chat naturally about what you want to build, and watch as it writes code, explains decisions, and helps you learn.

**Quick Tasks (--task)** - Perfect for one-off jobs. "Create a REST API for user management" or "Add authentication to my app" - just describe what you need.

**Interactive Sessions (--interactive)** - Work on multiple tasks in one session. Great for exploring ideas, iterating on features, and building complex projects step by step.

**Terminal Interface (--warp)** - A modern coding environment that feels like using advanced developer tools. See your project status, git changes, and AI suggestions all in one place.

## Advanced Features

### MCP Integration (--enable-mcp)
Enable Model Context Protocol for enhanced capabilities:

- Advanced security scanning with Semgrep integration
- AI-powered documentation search with DeepWiki
- Extended tool ecosystem for specialized tasks
- Real-time vulnerability detection and remediation

## Real Benefits

**For Beginners**: Learn by watching an expert work. See how real applications are built, from planning to deployment.

**For Experienced Developers**: Focus on architecture and business logic while the AI handles boilerplate, documentation, and testing.

**For Teams**: Maintain consistent code quality and catch issues before they reach production.

**For Everyone**: Spend less time debugging and more time building features that matter.

## Languages Supported

Works with any programming language - Python, JavaScript, TypeScript, Go, Rust, C++, Java, C#, PHP, Ruby, and more. It adapts to your project's style and conventions automatically.

## Safety Features

- **Secure by default** - Scans every change for security issues
- **Ask before running** - Requests permission for potentially dangerous operations
- **Complete audit trail** - Logs everything for transparency
- **Sandboxed execution** - Runs code safely without affecting your system

## Getting Help

```bash
# See all options
swe-agent --help

# Check if everything is working
swe-agent --status
```

Start with `swe-agent --pair` for the best experience. It's like having a senior developer helping you code.

## License

Apache 2.0

Stop fighting with code. Start building what you actually want to create.

Built with ❤️ by Harish Santhanalakshmi Ganesan and his Coding AI agents

**Thanks and Credits:** Terminal interfaces inspired by Aider and Warp