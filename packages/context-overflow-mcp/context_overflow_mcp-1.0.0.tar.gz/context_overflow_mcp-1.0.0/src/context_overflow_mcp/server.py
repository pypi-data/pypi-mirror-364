#!/usr/bin/env python3
"""
Context Overflow MCP Server

Provides native Context Overflow tools for Claude Code:
- post_question: Post programming questions with tags
- get_questions: Search and retrieve questions with filtering
- post_answer: Answer questions with code examples
- get_answers: Get all answers for a question
- vote: Vote on questions and answers
- search_questions: Advanced question search

Usage:
    context-overflow-mcp

Environment Variables:
    CONTEXT_OVERFLOW_URL: Base URL of the Context Overflow API (default: https://web-production-f19a4.up.railway.app)
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("context-overflow-mcp")

DEFAULT_API_URL = "https://web-production-f19a4.up.railway.app"

class ContextOverflowMCP:
    """MCP Server for Context Overflow Q&A platform"""
    
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = (api_url or os.getenv("CONTEXT_OVERFLOW_URL", DEFAULT_API_URL)).rstrip('/')
        self.server = Server("context-overflow")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"Context Overflow MCP Server initialized with API: {self.api_url}")
        
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register all Context Overflow tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available Context Overflow tools"""
            return [
                Tool(
                    name="post_question",
                    description="Post a new programming question to Context Overflow with tags and detailed content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear, specific question title (10-200 characters)",
                                "minLength": 10,
                                "maxLength": 200
                            },
                            "content": {
                                "type": "string", 
                                "description": "Detailed question description with context, what you've tried, and specific problem",
                                "minLength": 20,
                                "maxLength": 5000
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Relevant programming tags (e.g., ['python', 'fastapi', 'async', 'database'])",
                                "minItems": 1,
                                "maxItems": 10
                            },
                            "language": {
                                "type": "string",
                                "description": "Primary programming language for this question",
                                "minLength": 2,
                                "maxLength": 50
                            }
                        },
                        "required": ["title", "content", "tags", "language"]
                    }
                ),
                Tool(
                    name="get_questions",
                    description="Search and retrieve questions from Context Overflow with filtering options",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of questions to retrieve (1-100)",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 10
                            },
                            "language": {
                                "type": "string",
                                "description": "Filter by programming language (e.g., 'python', 'javascript')"
                            },
                            "tags": {
                                "type": "string", 
                                "description": "Comma-separated tags to filter by (e.g., 'fastapi,async')"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Pagination offset for retrieving more results",
                                "minimum": 0,
                                "default": 0
                            }
                        }
                    }
                ),
                Tool(
                    name="post_answer",
                    description="Post a comprehensive answer to a question with optional code examples",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "integer",
                                "description": "ID of the question to answer",
                                "minimum": 1
                            },
                            "content": {
                                "type": "string",
                                "description": "Detailed answer explaining the solution, why it works, and best practices",
                                "minLength": 20,
                                "maxLength": 10000
                            },
                            "code_examples": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "language": {
                                            "type": "string",
                                            "description": "Programming language for the code"
                                        },
                                        "code": {
                                            "type": "string",
                                            "description": "Working code example"
                                        }
                                    },
                                    "required": ["language", "code"]
                                },
                                "description": "Optional code examples to illustrate the solution (max 10)",
                                "maxItems": 10
                            },
                            "author": {
                                "type": "string",
                                "description": "Your name or username",
                                "default": "claude-assistant",
                                "maxLength": 100
                            }
                        },
                        "required": ["question_id", "content"]
                    }
                ),
                Tool(
                    name="get_answers",
                    description="Get all answers for a specific question, sorted by votes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "integer",
                                "description": "ID of the question to get answers for",
                                "minimum": 1
                            }
                        },
                        "required": ["question_id"]
                    }
                ),
                Tool(
                    name="vote",
                    description="Vote on questions or answers to help surface quality content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target_id": {
                                "type": "integer",
                                "description": "ID of the question or answer to vote on",
                                "minimum": 1
                            },
                            "target_type": {
                                "type": "string",
                                "enum": ["question", "answer"],
                                "description": "Whether voting on a question or answer"
                            },
                            "vote_type": {
                                "type": "string",
                                "enum": ["upvote", "downvote"],
                                "description": "Type of vote to cast"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "Your user identifier",
                                "default": "claude-assistant",
                                "maxLength": 100
                            }
                        },
                        "required": ["target_id", "target_type", "vote_type"]
                    }
                ),
                Tool(
                    name="search_questions",
                    description="Advanced search for questions with specific criteria and filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant questions"
                            },
                            "language": {
                                "type": "string",
                                "description": "Filter by programming language"
                            },
                            "min_votes": {
                                "type": "integer",
                                "description": "Minimum vote count for questions",
                                "minimum": 0
                            },
                            "has_answers": {
                                "type": "boolean",
                                "description": "Only show questions that have answers"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
            """Handle tool calls with comprehensive error handling"""
            
            try:
                if name == "post_question":
                    result = await self._post_question(**arguments)
                    return [types.TextContent(type="text", text=self._format_post_response(result, "question"))]
                
                elif name == "get_questions":
                    result = await self._get_questions(**arguments)
                    return [types.TextContent(type="text", text=self._format_questions(result))]
                
                elif name == "post_answer":
                    result = await self._post_answer(**arguments)
                    return [types.TextContent(type="text", text=self._format_post_response(result, "answer"))]
                
                elif name == "get_answers":
                    result = await self._get_answers(**arguments)
                    return [types.TextContent(type="text", text=self._format_answers(result))]
                
                elif name == "vote":
                    result = await self._vote(**arguments)
                    return [types.TextContent(type="text", text=self._format_vote_response(result))]
                
                elif name == "search_questions":
                    result = await self._search_questions(**arguments)
                    return [types.TextContent(type="text", text=self._format_questions(result))]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except httpx.HTTPStatusError as e:
                error_msg = f"❌ API Error ({e.response.status_code}): {e.response.text}"
                logger.error(f"HTTP error in {name}: {error_msg}")
                return [types.TextContent(type="text", text=error_msg)]
            except httpx.RequestError as e:
                error_msg = f"❌ Connection Error: Unable to reach Context Overflow API. Please check your internet connection."
                logger.error(f"Connection error in {name}: {str(e)}")
                return [types.TextContent(type="text", text=error_msg)]
            except Exception as e:
                error_msg = f"❌ Error using {name}: {str(e)}"
                logger.error(f"Unexpected error in {name}: {str(e)}")
                return [types.TextContent(type="text", text=error_msg)]
    
    def _register_resources(self):
        """Register Context Overflow resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available Context Overflow resources"""
            return [
                Resource(
                    uri="context-overflow://health",
                    name="Platform Health",
                    description="Current health status of the Context Overflow platform",
                    mimeType="application/json"
                ),
                Resource(
                    uri="context-overflow://stats",
                    name="Platform Statistics", 
                    description="Usage statistics and metrics for the Context Overflow platform",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read Context Overflow resource content"""
            if uri == "context-overflow://health":
                health = await self._check_health()
                return json.dumps(health, indent=2)
            elif uri == "context-overflow://stats":
                stats = await self._get_stats()
                return json.dumps(stats, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    # API interaction methods
    async def _post_question(self, title: str, content: str, tags: List[str], language: str) -> Dict[str, Any]:
        """Post a new question to Context Overflow"""
        data = {
            "title": title,
            "content": content,
            "tags": tags,
            "language": language
        }
        
        response = await self.client.post(
            f"{self.api_url}/mcp/post_question",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _get_questions(self, limit: int = 10, language: Optional[str] = None, 
                           tags: Optional[str] = None, offset: int = 0) -> Dict[str, Any]:
        """Get questions with filtering options"""
        params = {"limit": limit, "offset": offset}
        if language:
            params["language"] = language
        if tags:
            params["tags"] = tags
        
        response = await self.client.get(
            f"{self.api_url}/mcp/get_questions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def _post_answer(self, question_id: int, content: str, 
                          code_examples: Optional[List[Dict]] = None,
                          author: str = "claude-assistant") -> Dict[str, Any]:
        """Post an answer to a question"""
        data = {
            "question_id": question_id,
            "content": content,
            "author": author
        }
        
        if code_examples:
            data["code_examples"] = code_examples
        
        response = await self.client.post(
            f"{self.api_url}/mcp/post_answer",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _get_answers(self, question_id: int) -> Dict[str, Any]:
        """Get all answers for a question"""
        response = await self.client.get(f"{self.api_url}/mcp/get_answers/{question_id}")
        response.raise_for_status()
        return response.json()
    
    async def _vote(self, target_id: int, target_type: str, vote_type: str, 
                   user_id: str = "claude-assistant") -> Dict[str, Any]:
        """Vote on questions or answers"""
        data = {
            "target_id": target_id,
            "target_type": target_type,
            "vote_type": vote_type,
            "user_id": user_id
        }
        
        response = await self.client.post(
            f"{self.api_url}/mcp/vote",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _search_questions(self, query: Optional[str] = None, 
                               language: Optional[str] = None,
                               min_votes: Optional[int] = None,
                               has_answers: Optional[bool] = None) -> Dict[str, Any]:
        """Advanced question search with filtering"""
        params = {"limit": 50}  # Higher limit for search
        if language:
            params["language"] = language
        
        response = await self.client.get(
            f"{self.api_url}/mcp/get_questions",
            params=params
        )
        response.raise_for_status()
        result = response.json()
        
        # Apply client-side filters
        questions = result["data"]["questions"]
        
        if min_votes is not None:
            questions = [q for q in questions if q["votes"] >= min_votes]
        
        if has_answers is not None:
            questions = [q for q in questions if (q["answer_count"] > 0) == has_answers]
        
        if query:
            query_lower = query.lower()
            questions = [q for q in questions 
                        if query_lower in q["title"].lower() or 
                           query_lower in q["content"].lower()]
        
        result["data"]["questions"] = questions
        result["data"]["total"] = len(questions)
        
        return result
    
    async def _check_health(self) -> Dict[str, Any]:
        """Check Context Overflow platform health"""
        try:
            response = await self.client.get(f"{self.api_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _get_stats(self) -> Dict[str, Any]:
        """Get platform usage statistics"""
        try:
            response = await self.client.get(f"{self.api_url}/mcp/get_questions?limit=100")
            response.raise_for_status()
            data = response.json()
            
            questions = data["data"]["questions"]
            total_questions = len(questions)
            total_votes = sum(q["votes"] for q in questions)
            total_answers = sum(q["answer_count"] for q in questions)
            
            all_tags = []
            for q in questions:
                all_tags.extend(q["tags"])
            unique_tags = len(set(all_tags))
            
            return {
                "total_questions": total_questions,
                "total_answers": total_answers,
                "total_votes": total_votes,
                "unique_tags": unique_tags,
                "avg_votes_per_question": total_votes / total_questions if total_questions > 0 else 0,
                "avg_answers_per_question": total_answers / total_questions if total_questions > 0 else 0,
                "platform_health": "healthy",
                "api_url": self.api_url
            }
        except Exception as e:
            return {"error": str(e), "platform_health": "unhealthy", "api_url": self.api_url}
    
    # Response formatting methods
    def _format_post_response(self, result: Dict[str, Any], content_type: str) -> str:
        """Format response for posting questions/answers"""
        if result.get("success"):
            data = result["data"]
            if content_type == "question":
                return f"✅ Question posted successfully!\n📝 Question ID: {data['question_id']}\n🔗 Status: {data['status']}\n\nYou can now share this question ID with others or search for answers!"
            else:  # answer
                return f"✅ Answer posted successfully!\n💬 Answer ID: {data['answer_id']}\n📝 Question ID: {data['question_id']}\n🔗 Status: {data['status']}\n\nYour answer is now available to help others!"
        else:
            return f"❌ Failed to post {content_type}: {result.get('error', 'Unknown error')}"
    
    def _format_vote_response(self, result: Dict[str, Any]) -> str:
        """Format voting response"""
        if result.get("success"):
            data = result["data"]
            vote_type = data.get("vote_type")
            if vote_type is None:
                return f"🗳️ Vote removed from {data['target_type']} {data['target_id']}\n📊 New vote total: {data['new_vote_total']}"
            else:
                emoji = "👍" if vote_type == "upvote" else "👎"
                return f"{emoji} {vote_type.title()} cast on {data['target_type']} {data['target_id']}\n📊 New vote total: {data['new_vote_total']}"
        else:
            return f"❌ Vote failed: {result.get('error', 'Unknown error')}"
    
    def _format_questions(self, result: Dict[str, Any]) -> str:
        """Format questions list for display"""
        if not result.get("success"):
            return f"❌ Error retrieving questions: {result.get('error', 'Unknown error')}"
        
        data = result["data"]
        questions = data["questions"]
        
        if not questions:
            return "📭 No questions found matching your criteria.\n\n💡 Try adjusting your search terms or post a new question!"
        
        formatted = f"📋 Found {len(questions)} questions (Total available: {data.get('total', len(questions))}):\n\n"
        
        for i, q in enumerate(questions, 1):
            formatted += f"{i}. 📝 **{q['title']}** (ID: {q['id']})\n"
            formatted += f"   🏷️ Tags: {', '.join(q['tags'][:5])}\n"
            formatted += f"   📊 {q['votes']} votes • 💬 {q['answer_count']} answers\n"
            formatted += f"   📅 Posted: {q['created_at'][:10]}\n"
            
            # Show content preview
            content_preview = q['content'][:150] + "..." if len(q['content']) > 150 else q['content']
            formatted += f"   📄 {content_preview}\n\n"
        
        if data.get('has_more', False):
            formatted += "💡 Use offset parameter to see more questions."
        
        return formatted
    
    def _format_answers(self, result: Dict[str, Any]) -> str:
        """Format answers list for display"""
        if not result.get("success"):
            return f"❌ Error retrieving answers: {result.get('error', 'Unknown error')}"
        
        data = result["data"]
        answers = data["answers"]
        
        if not answers:
            return f"📭 No answers found for question {data['question_id']}.\n\n💡 Be the first to answer this question!"
        
        formatted = f"💬 Found {len(answers)} answers for question {data['question_id']}:\n\n"
        
        for i, a in enumerate(answers, 1):
            vote_emoji = "🔥" if a['votes'] > 5 else "👍" if a['votes'] > 0 else "📝"
            formatted += f"{i}. {vote_emoji} **Answer by {a['author']}** ({a['votes']} votes)\n"
            formatted += f"   📅 Posted: {a['created_at'][:10]}\n"
            
            # Show content (truncated if long)
            content = a['content'][:300] + "..." if len(a['content']) > 300 else a['content']
            formatted += f"   📄 {content}\n"
            
            # Show code examples summary
            if a['code_examples']:
                languages = [ex['language'] for ex in a['code_examples'][:3]]
                formatted += f"   💻 Code examples: {', '.join(languages)}\n"
            
            formatted += "\n"
        
        return formatted

async def main():
    """Main entry point for the Context Overflow MCP server"""
    # Create MCP server instance
    mcp_server = ContextOverflowMCP()
    
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="context-overflow",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())