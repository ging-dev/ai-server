## Usage

```bash
pip install -r pyproject.toml
export QWEN_TOKEN=...
flask run
```

## Continue.dev

```json
{
  "models": [
    {
      "title": "Qwen Chat",
      "model": "qwen-max-latest",
      "provider": "ollama",
      "capabilities": {
        "tools": true
      },
      "apiBase": "http://localhost:5000"
    }
  ]
}
```
