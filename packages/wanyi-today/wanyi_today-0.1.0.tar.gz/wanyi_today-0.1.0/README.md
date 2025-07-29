# Today

A FastMCP demo server that provides basic tools and resources for demonstration purposes.

## Features

- **Addition Tool**: Add two numbers together
- **Greeting Resource**: Get personalized greetings
- **Greeting Prompt**: Generate greeting prompts with different styles

## Installation

```bash
pip install today
```

## Usage

Run the server:

```bash
today-server
```

Or run directly with Python:

```bash
python -m today.main
```

## Development

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m today.main
```

## License

MIT License