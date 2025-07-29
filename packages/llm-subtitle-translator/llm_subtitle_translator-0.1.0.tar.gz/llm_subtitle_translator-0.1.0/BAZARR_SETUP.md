# Bazarr Integration Setup Guide

This guide shows how to set up the LLM Subtitle Translator as a Bazarr custom post-processing hook.

## Quick Start

### 1. Docker Setup with Volume Mounting

Create `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add: DEEPSEEK_API_KEY=your_actual_api_key_here
```

Start the service:
```bash
docker compose up -d
```

### 2. Bazarr Hook Configuration

In Bazarr Settings → General → Post-Processing, add a custom script:

**Script Path**: `/usr/local/bin/curl`
**Arguments**:
```bash
-X POST "http://subtitle-translator:8000/translate" 
-F "input_path={{subtitle}}" 
-F "provider=deepseek" 
-F "translation_mode=bilingual" 
-F "prompt_template=selective_difficulty"
```

### 3. Docker Compose for Bazarr Integration

```yaml
version: '3.8'
services:
  bazarr:
    image: linuxserver/bazarr:latest
    volumes:
      - /path/to/config:/config
      - /path/to/media:/media
    networks:
      - media-network

  subtitle-translator:
    build:
      context: .
      args:
        PUID: ${PUID:-1000}
        PGID: ${PGID:-1000}
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - /path/to/media:/media  # Same mount as Bazarr
    networks:
      - media-network
    restart: unless-stopped

networks:
  media-network:
```

## API Endpoints

### File Path Mode (Recommended for Bazarr)
```bash
curl -X POST "http://localhost:8000/translate" \\
  -F "input_path=/media/subtitles/movie.srt" \\
  -F "provider=deepseek" \\
  -F "translation_mode=bilingual"
```

**Response**:
```json
{
  "success": true,
  "message": "✅ Translation completed successfully",
  "output_filename": "/media/subtitles/movie.en-zh.ass"
}
```

### Available Parameters

- `input_path`: Path to SRT file (required)
- `output_path`: Output path (optional, defaults to same directory)
- `provider`: `deepseek`, `openai`, or `gemini` (default: `deepseek`)
- `model`: Specific model name (optional)
- `translation_mode`: `bilingual` or `monolingual` (default: `bilingual`)
- `prompt_template`: `full_text` or `selective_difficulty` (default: `selective_difficulty`)
- `batch_size`: Lines per API call (default: 50)

## Translation Modes

### Bilingual Mode
- Shows original English text on top
- Shows translated Chinese text below
- Uses different colors and fonts for distinction
- Output format: `.en-zh.ass`

### Monolingual Mode  
- Replaces original text with translation only
- Maintains original timing and styling
- Output format: `.zh.ass`

## Prompt Templates

### Selective Difficulty (Recommended)
- Only translates complex phrases and cultural references
- Keeps simple English words untranslated
- Balances comprehension with language learning

### Full Text
- Translates every subtitle line completely
- Provides complete Chinese translation
- Best for full immersion

## Environment Variables

Required:
- `DEEPSEEK_API_KEY`: Your DeepSeek API key

Optional:
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `GEMINI_API_KEY`: Google Gemini API key
- `DEFAULT_PROVIDER`: Default AI provider (default: deepseek)
- `PUID`: User ID for file permissions (default: 1000)
- `PGID`: Group ID for file permissions (default: 1000)

### PUID/PGID Usage
Set these to match your host user to avoid permission issues:
```bash
# Find your user/group IDs
id

# Set in .env file
PUID=1001
PGID=1001

# Or set when running
PUID=1001 PGID=1001 docker-compose up
```

## File Processing

1. **Input**: `.srt` subtitle files
2. **Output**: `.ass` subtitle files with bilingual text
3. **Location**: Same directory as input file (or custom path)
4. **Styling**: Configured colors, fonts, and positioning

## Health Monitoring

Check service health:
```bash
curl http://localhost:8000/health
```

Check available providers:
```bash
curl http://localhost:8000/providers
```

## Troubleshooting

### Common Issues

1. **Translation Failed**: Check API key configuration
2. **File Not Found**: Verify volume mounts match between Bazarr and translator
3. **Permission Denied**: Ensure container has write access to subtitle directory

### Logs
```bash
docker compose logs subtitle-translator
```

### Testing
```bash
# Test with sample file
curl -X POST "http://localhost:8000/translate" \\
  -F "input_path=/media/test.srt" \\
  -F "provider=deepseek"
```

## Performance

- **Translation Speed**: ~5-30 seconds per file (depends on length)
- **API Costs**: ~$0.001-0.01 per subtitle file
- **Batch Processing**: Optimized for efficiency

## Security

- API keys stored in environment variables
- No file uploads required (uses file paths)
- Read/write access only to mounted subtitle directories