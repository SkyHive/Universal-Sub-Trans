# Universal-Sub-Trans 产品开发文档 (PRD & System Design)

## 1. 项目概述

**Universal-Sub-Trans** 是一款基于 AI 的跨平台通用字幕生成工具。它利用 `faster-whisper` 进行高精度语音识别（STT），并通过兼容 OpenAI 协议的 LLM（如 Ollama, DeepSeek）进行语境感知翻译。

## 2. 技术栈选型

| 模块     | 技术实现                     | 关键库/SDK                                          |
|--------|--------------------------|--------------------------------------------------|
| GUI 容器 | PyWebView                | 轻量化，利用系统原生 WebView2 (Win) / WebKit (Linux)       |
| 前端界面   | Vue 3 + Vite + Shadcn UI | 响应式设计，极佳的用户交互体验                                  |
| 后端逻辑   | Python 3.10+             | AI 生态最丰富的语言                                      |
| 语音转文字  | Faster-Whisper           | CTranslate2 优化版，支持 CPU/GPU 自动切换                  |
| AI 翻译  | OpenAI Python SDK        | 适配 Ollama, OpenAI, DeepSeek, SiliconFlow 等所有兼容接口 |
| 数据持久化  | Pydantic-Settings        | 基于 Type-Hint 的配置管理，支持 JSON/Env                   |
| 音频预处理  | FFmpeg-Python            | 调用静态 FFmpeg 二进制文件处理流                             |
| 打包工具   | Nuitka                   | 编译为 C 二进制，保护源码并优化性能                              |

## 3. 核心模块设计

### 3.1 数据持久化 (Config Module)

使用 `pydantic-settings` 结合 `appdirs` 实现跨平台路径自动定位。

* 存储位置：
  * Windows: C:\Users\<User>\AppData\Local\UniversalSub\config.json
  * Linux: ~/.config/universal-sub/config.json
* 设计要点：
  * 支持配置热加载。
  * 分离 `AppConfig` (基础设置) 与 ModelConfig (AI 参数)。

### 3.2 日志模块 (Log Module)

采用 Python 标准库 `logging` 的 `RotatingFileHandler`

* 设计要点：
  * 限制体积：单个日志文件最大 10MB，保留最近 5 个文件。
  * 多端输出：同时输出到标准输出 (Stdout) 和本地文件，方便 DevOps 调试。

### 3.3 AI 翻译客户端 (AI Client)

通过封装 `openai` SDK 实现。

* 设计要点：
  * 统一协议：通过 `base_url` 切换 Ollama (<http://localhost:11434/v1>) 或云端 API。
  * 批处理机制：将多行字幕合并成一个 Prompt 发送，保留上下文语境，降低 Token 消耗。

### 3.4 Faster-Whisper 转录服务

负责音频提取、VAD (静音检测) 与识别。

* 设计要点：
  * 设备自适应：初始化时自动检测 CUDA。若无 GPU，则强制开启 `compute_type="int8`" 进行 CPU 加速。
  * 模型热加载：首次运行自动下载模型，并缓存至用户数据目录

## 4. 跨平台实现方案

### 4.1 FFmpeg 静态资源集成

不要求用户安装 FFmpeg，直接随包分发。

* 分发逻辑：在项目根目录设立 `bin/` 文件夹，根据平台放置 `ffmpeg.exe` (Win) 或 `ffmpeg` (Linux)。
* 代码调用：

    ```python
    import os, platform

    def get_ffmpeg_path():
        curr_os = platform.system().lower()
        return os.path.join(os.getcwd(), 'bin', curr_os, 'ffmpeg')
    ```

### 4.2 计算库依赖处理

Faster-Whisper 依赖 `zlib` 和 `cuDNN` (Windows)。在打包时需将这些动态链接库 (.dll/.so) 加入 Nuitka 的 `include-data` 路径。

## 5. 代码结构设计

```plaintext
universal-sub/
├── backend/
│   ├── api/                # PyWebView 暴露给 JS 的桥接类
│   │   └── bridge.py       # 统一接口层
│   ├── core/
│   │   ├── ai_engine.py    # OpenAI SDK 封装
│   │   ├── whisper_svc.py  # Faster-Whisper 逻辑
│   │   └── audio_proc.py   # FFmpeg 提取音频逻辑
│   ├── models/
│   │   └── schema.py       # Pydantic 数据模型
│   └── services/
│       ├── config_mgr.py   # 配置读写 (pydantic-settings)
│       └── logger.py       # 日志初始化 (RotatingFile)
├── frontend/               # Vue 3 项目目录
│   ├── src/
│   │   ├── api/            # 封装 window.pywebview.api 调用
│   │   ├── views/          # 转录页、设置页、编辑页
│   │   └── store/          # Pinia 状态管理
├── bin/                    # 静态二进制文件 (FFmpeg)
├── main.py                 # 程序入口，初始化 PyWebView
└── pyproject.toml          # uv 依赖管理
```

## 6. 通信与流控设计 (IPC)

由于 Python 的计算任务是阻塞的，而 WebView 要求响应迅速，必须采用异步架构：

1. Frontend -> Backend (调用)： Vue 调用 `window.pywebview.api.start_task(params)`，Python 立即返回 `{"status": "started"}`。
2. Backend -> Frontend (回调)： Python 开启独立线程处理 AI 逻辑，通过 `window.evaluate_js()` 定时回传进度：

    ```python
    # Python 线程内

    def progress_callback(p):
        window.evaluate_js(f"updateProgress({p})")
    ```

## 7. 打包工作流

1. 前端构建：`cd frontend && npm run build` (产物输出到 `backend/dist`)。

2. 依赖同步：`uv sync`。

3. Nuitka 编译：
    * Windows: 使用 `--standalone` 并包含 `bin/` 目录。
    * Linux: 额外注意 `AppImage` 或 `deb` 包的构建规范。
