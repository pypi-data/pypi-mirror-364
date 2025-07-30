# import requests
# import json

# OLLAMA_URL = "http://localhost:11434/api/generate"

# SYSTEM_PROMPT = """
# You are a helpful AI assistant that translates natural language requests into safe, minimal Linux shell commands. Only output the command, nothing else.
# """

# def get_command_from_llm(query, model):
#     payload = {
#         "model": model,
#         "prompt": f"{SYSTEM_PROMPT}\nUser: {query}\nCommand:",
#         "stream": False
#     }
#     try:
#         resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
#         resp.raise_for_status()
#         data = resp.json()
#         # Ollama returns { 'response': '...' }
#         return data.get("response", "").strip().split("\n")[0]
#     except Exception as e:
#         return f"echo 'Ollama error: {e}'" 




# agent.py
"""
Command translation agent that converts natural language to Ubuntu commands using Ollama only.
"""

import os
import json
import logging
import requests
from typing import Dict, Any
from pathlib import Path

from .config import get_model

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

class CommandTranslator:
    """Handles translation of natural language to Ubuntu commands via Ollama."""

    def __init__(self):
        self.model = get_model()
        if not self.model:
            raise ValueError("[aish] No model set. Use `aish use <model>` to set one.")

    def _get_system_context(self) -> Dict[str, str]:
        """Get current system context for better command translation."""
        try:
            context = {
                'current_dir': os.getcwd(),
                'user': os.getenv('USER', 'unknown'),
                'home': os.getenv('HOME', '/home/unknown'),
                'shell': os.getenv('SHELL', '/bin/bash'),
                'os_type': 'Ubuntu/Debian'
            }
            if Path('.git').exists():
                context['git_repo'] = True
            if Path('requirements.txt').exists():
                context['python_project'] = True
            elif Path('package.json').exists():
                context['node_project'] = True
            elif Path('Makefile').exists():
                context['make_project'] = True
            elif Path('Cargo.toml').exists():
                context['rust_project'] = True
            elif Path('go.mod').exists():
                context['go_project'] = True
            return context
        except Exception as e:
            logger.warning(f"Failed to get system context: {e}")
            return {'current_dir': 'unknown', 'user': 'unknown', 'os_type': 'Ubuntu/Debian'}

    def _build_prompt(self, natural_input: str) -> str:
        context = self._get_system_context()
        context_str = f"""Current directory: {context['current_dir']}
User: {context['user']}
OS: {context['os_type']}"""
        project_hints = []
        if context.get('git_repo'): project_hints.append("Git repository detected")
        if context.get('python_project'): project_hints.append("Python project detected")
        if context.get('node_project'): project_hints.append("Node.js project detected")
        if context.get('rust_project'): project_hints.append("Rust project detected")
        if context.get('go_project'): project_hints.append("Go project detected")
        if project_hints:
            context_str += f"\nProject context: {', '.join(project_hints)}"

        return f"""You are an expert Ubuntu/Linux/macOS system administrator assistant. Convert natural language requests into safe, appropriate Ubuntu terminal commands.

SYSTEM CONTEXT:
{context_str}

STRICT RULES:
1. Return ONLY valid Ubuntu/Linux/macOS commands that are safe to execute
2. Use modern command syntax (prefer 'apt' over 'apt-get', use long-form flags when clearer)
3. Never suggest destructive commands (rm -rf /, format commands, shutdown, etc.)
4. For package installation, always include 'sudo apt update &&' before 'sudo apt install'
5. Use relative paths and current directory context when appropriate
6. If request is ambiguous, choose the safest, most common interpretation
7. For file operations, be explicit about paths and permissions
8. Consider the detected project context when suggesting commands

RESPONSE FORMAT (JSON):
{{
    "command": "exact command to execute",
    "explanation": "clear explanation of what the command does",
    "safety_level": "safe|warning|dangerous"
}}

REQUEST: "{natural_input}"

Provide your response:"""

    def translate_with_ollama(self, natural_input: str) -> Dict[str, Any]:
        prompt = self._build_prompt(natural_input)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            content = data.get("response", "").strip()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Ollama returned non-JSON response, falling back")
                return {
                    "command": content,
                    "explanation": "Ollama generated raw command (non-JSON fallback)",
                    "safety_level": "unknown"
                }
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            return {
                "command": f"echo 'Ollama error: {e}'",
                "explanation": "Error during command translation",
                "safety_level": "warning"
            }

_translator = None

def get_translator() -> CommandTranslator:
    global _translator
    if _translator is None:
        _translator = CommandTranslator()
    return _translator

def translate_to_command(natural_input: str) -> Dict[str, Any]:
    translator = get_translator()
    return translator.translate_with_ollama(natural_input)
