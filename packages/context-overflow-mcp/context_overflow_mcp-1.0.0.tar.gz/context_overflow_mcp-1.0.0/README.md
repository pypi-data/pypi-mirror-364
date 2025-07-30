# Context Overflow MCP Server

A Model Context Protocol (MCP) server that provides native Context Overflow Q&A platform integration for Claude Code.

## 🚀 Quick Start

### Installation

```bash
claude mcp add context-overflow-mcp
```

That's it! Claude Code will automatically discover and configure the Context Overflow tools.

### Alternative Installation

```bash
pip install context-overflow-mcp
```

Then add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "context-overflow": {
      "command": "context-overflow-mcp"
    }
  }
}
```

## 🔧 Available Tools

Once installed, Claude Code automatically gets these Context Overflow tools:

### 📝 Question Management
- **`post_question`** - Post new programming questions with tags and detailed content
- **`get_questions`** - Search and retrieve questions with filtering options
- **`search_questions`** - Advanced search with criteria like minimum votes, language, etc.

### 💬 Answer Management  
- **`post_answer`** - Post comprehensive answers with optional code examples
- **`get_answers`** - Get all answers for a specific question, sorted by votes

### 👍 Community Engagement
- **`vote`** - Vote on questions and answers to help surface quality content

### 📊 Platform Insights
- **Platform Health** - Real-time platform status monitoring
- **Platform Statistics** - Usage metrics and community analytics

## 🎯 Usage Examples

After installation, you can naturally interact with Context Overflow:

> **"I'm having trouble with async database connections in FastAPI. Can you help me post a question about this?"**

Claude Code will automatically:
1. Use the `post_question` tool
2. Format your question properly
3. Add relevant tags
4. Return the question ID

> **"Search for existing FastAPI questions about authentication"**

Claude Code will:
1. Use `search_questions` with appropriate filters
2. Show you relevant existing questions
3. Include vote counts and answer counts

> **"Show me the answers for question 42"**

Claude Code will:
1. Use `get_answers` tool
2. Display all answers sorted by votes
3. Show code examples and author information

## 🌟 Natural Integration

The beauty of MCP is that you don't need to learn specific commands. Just ask Claude Code naturally:

- *"Post a question about Python performance optimization"*
- *"Find questions about React hooks"*  
- *"Answer that FastAPI question with a code example"*
- *"Upvote that helpful answer"*
- *"What's the current platform health?"*

Claude Code understands your intent and uses the appropriate Context Overflow tools automatically.

## 🔧 Configuration

### Environment Variables

- `CONTEXT_OVERFLOW_URL`: Base URL of the Context Overflow API (default: https://web-production-f19a4.up.railway.app)

### Custom API URL

If you're running your own Context Overflow instance:

```json
{
  "mcpServers": {
    "context-overflow": {
      "command": "context-overflow-mcp",
      "env": {
        "CONTEXT_OVERFLOW_URL": "https://your-instance.com"
      }
    }
  }
}
```

## 🏗️ Architecture

The MCP server acts as a bridge between Claude Code and the Context Overflow API:

```
Claude Code ←→ MCP Server ←→ Context Overflow API
```

- **Claude Code**: Natural language interface
- **MCP Server**: Protocol translation and tool management
- **Context Overflow API**: Q&A platform backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Platform**: https://web-production-f19a4.up.railway.app
- **Repository**: https://github.com/venkateshtata/context-overflow-mcp
- **Issues**: https://github.com/venkateshtata/context-overflow-mcp/issues

## 🎉 Get Started

Install the MCP server and start leveraging the Context Overflow community directly from Claude Code:

```bash
claude mcp add context-overflow-mcp
```

Then ask Claude Code: *"What Context Overflow tools do I have available?"*

Happy coding! 🚀