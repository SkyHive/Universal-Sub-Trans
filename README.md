# Universal-Sub-Trans

An AI-powered universal subtitle translation tool.

## Features

- **High-accuracy STT**: Powered by `faster-whisper`.
- **Context-aware Translation**: batch-processing via LLMs (Ollama, OpenAI, DeepSeek).
- **Premium UI**: Dark-themed Vue 3 interface with real-time progress.
- **Portable**: Designed to be bundled with FFmpeg.

## Development Setup

### 1. Backend Setup

Ensure you have `uv` installed.

```bash
uv sync
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Run Application

In a separate terminal, run:

```bash
export DEV_MODE=true
uv run python main.py
```

## Binary Placement (Required for Audio Extraction)

Place `ffmpeg` binaries in the following structure:

- `bin/linux/ffmpeg`
- `bin/windows/ffmpeg.exe`

## Packaging

Build the frontend and compile with Nuitka:

```bash
cd frontend && npm run build
nuitka --standalone --include-data-dir=bin=bin --plugin-enable=pywebview main.py
```
