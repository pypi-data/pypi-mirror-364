# aish-local

Talk to your terminal in natural language, get safe Linux commands (Ollama LLMs only).

## Install

```bash
pip install aish-local
# or for dev
pip install -e .
```

## Usage

```bash
aish use model llama3
aish "list all files in current directory"
aish history
```

## Features
- Natural language to shell command (Ollama LLMs)
- Model selection (`aish use model ...`)
- Safety system: risk levels, confirmation before running risky commands
- Command history

## Author
MIT License  
Penumala Nani  
[pnani18dec@gmail.com](mailto:pnani18dec@gmail.com)  
[github.com/nani67](https://github.com/nani67) 