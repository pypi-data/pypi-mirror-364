# Bazarr LLM Translate

Advanced subtitle translator with LLM support and web API. Converts SRT subtitle files to styled ASS format with bilingual or monolingual translations using OpenAI, Google Gemini, or DeepSeek APIs.

## Features

- **Web API**: FastAPI-based REST API for subtitle translation
- **CLI Tool**: Command-line interface for batch processing
- **Multiple AI Providers**: OpenAI, Google Gemini, DeepSeek support
- **Bilingual Mode**: Displays original text on top and translated text below
- **Monolingual Mode**: Replaces original text with translation
- **Smart Translation**: Full text or selective difficulty translation modes
- **Resumable**: Automatically saves progress and can resume if interrupted
- **Batch Processing**: Processes subtitles in batches for efficient API usage
- **Containerized**: Docker support with multi-platform builds

## Quick Start

### Using Docker (Recommended)

1. **Pull the image:**
   ```bash
   docker pull ghcr.io/yanp/llm-subtitle-translator:latest
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e DEEPSEEK_API_KEY=your_api_key_here \
     ghcr.io/yanp/llm-subtitle-translator:latest
   ```

3. **Access the API:**
   - Web interface: http://localhost:8080/docs
   - Health check: http://localhost:8080/health

### Using Docker Compose

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yanp/llm-subtitle-translator.git
   cd llm-subtitle-translator
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the service:**
   ```bash
   docker-compose up -d
   ```

### Local Development

1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies:**
   ```bash
   uv venv
   uv pip install -e .
   ```

3. **Set environment variables:**
   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

4. **Run the API:**
   ```bash
   uv run fastapi dev src/llm_subtitle_translator/app.py
   ```

5. **Or use the CLI:**
   ```bash
   uv run translate-subtitles input.srt --translation-mode bilingual
   ```

## API Usage

### Translate Subtitle File

**POST** `/translate`

Supports two modes: file upload or file path processing.

#### Mode 1: File Upload (Web Interface)
Upload an SRT file and get back a translated ASS file.

**Parameters:**
- `file`: SRT subtitle file to upload
- `provider`: AI provider (`openai`, `gemini`, `deepseek`) - default: `deepseek`
- `model`: Specific model name (optional)
- `translation_mode`: `bilingual` or `monolingual` - default: `bilingual`
- `prompt_template`: `full_text` or `selective_difficulty` - default: `selective_difficulty`
- `batch_size`: Number of lines per API call - default: `50`

**Example:**
```bash
curl -X POST "http://localhost:8080/translate" \
  -F "file=@subtitle.srt" \
  -F "provider=deepseek" \
  -F "translation_mode=bilingual" \
  -F "prompt_template=selective_difficulty" \
  -o translated_subtitle.ass
```

#### Mode 2: File Path (Bazarr Hook)
Process files on the server filesystem (ideal for Bazarr hooks).

**Parameters:**
- `input_path`: Path to SRT subtitle file on server
- `output_path`: Output path for translated file (optional, defaults to same directory with .en-zh.ass extension)
- `provider`: AI provider (`openai`, `gemini`, `deepseek`) - default: `deepseek`
- `model`: Specific model name (optional)
- `translation_mode`: `bilingual` or `monolingual` - default: `bilingual`
- `prompt_template`: `full_text` or `selective_difficulty` - default: `selective_difficulty`
- `batch_size`: Number of lines per API call - default: `50`

**Example:**
```bash
curl -X POST "http://localhost:8080/translate" \
  -F "input_path=/media/subtitles/movie.srt" \
  -F "output_path=/media/subtitles/movie.en-zh.ass" \
  -F "provider=deepseek" \
  -F "translation_mode=bilingual"
```

### Get Available Providers

**GET** `/providers`

Returns available AI providers and their configuration status.

## CLI Usage

```bash
uv run translate-subtitles input.srt [options]
```

**Options:**
- `-o, --output`: Output file path
- `--translation-mode`: `bilingual` or `monolingual`
- `--prompt-template`: `full_text` or `selective_difficulty`
- `-p, --provider`: AI provider (`openai`, `gemini`, `deepseek`)
- `-m, --model`: Specific model name
- `--batch-size`: Batch size for API calls

**Example:**
```bash
uv run translate-subtitles movie.srt \
  --translation-mode bilingual \
  --prompt-template selective_difficulty \
  --provider deepseek \
  --batch-size 50
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI provider |
| `GEMINI_API_KEY` | Google Gemini API key | For Gemini provider |
| `DEEPSEEK_API_KEY` | DeepSeek API key | For DeepSeek provider |

### Translation Modes

- **Bilingual**: Shows original text on top, translation below
- **Monolingual**: Replaces original text with translation

### Prompt Templates

- **Full Text**: Translates every subtitle line
- **Selective Difficulty**: Only translates complex phrases, slang, or cultural references

## Development

### Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv venv
uv pip install -e ".[dev]"

# Activate virtual environment
source .venv/bin/activate
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## Docker

### Build locally

```bash
docker build -t llm-subtitle-translator .
```

### Multi-platform build

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t llm-subtitle-translator .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- Open an issue on GitHub
- Check the API documentation at `/docs` when running the server
- Review the example files in the repository