"""
Optional Claude Agent SDK integration for the assessment.

The primary runtime supports Ollama because the assignment requires a local-model demo.
This module demonstrates how the Claude Agent SDK can be used for an agentic workflow
without coupling the rest of the application to Claude.
"""

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient


async def run_claude_agent(prompt: str, cwd: str | None = None) -> str:
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=(
            "You are a product-growth research agent. "
            "Only use evidence supplied by the application. "
            "Do not browse or modify files for this task."
        ),
        allowed_tools=[],
        max_turns=1,
        cwd=cwd,
    )
    async with ClaudeSDKClient(options=options) as agent:
        await agent.query(prompt)
        parts = []
        async for message in agent.receive_response():
            for block in getattr(message, "content", []):
                if getattr(block, "text", None):
                    parts.append(block.text)
        return "\n".join(parts)
