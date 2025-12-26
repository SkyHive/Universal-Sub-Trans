# UniSub: Universal-Sub-Trans 🎥🛸

**UniSub** 是一款基于 AI 驱动的次世代全能字幕生成与翻译工具。它集成了业界先进的 `Faster-Whisper` 语音识别引擎与大语言模型（LLM）上下文翻译能力，旨在为视频创作者提供极致、流畅、且高度工业化的字幕制作方案。

<p align="center">
  <img src="https://img.shields.io/badge/UI-Vue3%20%2B%20Tailwind-42b883" alt="UI">
  <img src="https://img.shields.io/badge/Backend-Python-3776ab" alt="Backend">
  <img src="https://img.shields.io/badge/Acceleration-NVIDIA%20CUDA-76b900" alt="CUDA">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License">
</p>

---

## ✨ 核心特性

- 🚀 **极致硬件加速**：
  - **智能检测**：自动识别系统 GPU 架构（NVIDIA/AMD/Intel）。
  - **一键部署**：业内首创“自剥离”技术，一键从 PyPI 官方渠道部署 CUDA/cuDNN 运行环境，无需用户手动安装复杂的显卡工具包。
  - **跨平台兼容**：完美支持 Windows (包含 WSL/UNC 路径兼容) 与 Linux。

- 🧠 **聪明过人的 AI 翻译**：
  - **上下文关联**：采用 Batch 批处理技术，让 LLM 在翻译时感知视频前后的语境，彻底告别单句翻译的僵硬感。
  - **自定义 Prompt**：内置专业级字幕翻译提示词，支持 `<L1>` 行标记系统，支持用户自定义翻译风格及兜底逻辑。
  - **多模型支持**：无缝对接 OpenAI、DeepSeek、Ollama、Sakura 等主流 LLM 接口。

- 🎨 **高级视觉体验**：
  - **毛玻璃设计**：基于现代审美设计的深色模式界面，支持流畅的微交互动画。
  - **实时反馈**：毫秒级的状态同步，精准把控识别、翻译、保存的每一个环节。

- ♻️ **断点续作系统**：
  - 智能缓存中间状态（Audio/Transcript），发生中断或想微调翻译时，可跳过耗时的语音识别步骤。

---

## 🛠️ 快速启动

### 1. 后端准备 (Backend)

项目使用 `uv` 进行高效的 Python 依赖管理：

```bash
# 同步环境并建立虚拟环境
uv sync
```

### 2. 前端构建 (Frontend)

```bash
cd frontend
npm install
npm run dev
```

### 3. 环境运行

```bash
# 开启开发模式（启用控制台及 HMR）
export DEV_MODE=true
uv run python main.py
```

---

## 📦 部署与打包

### 生产打包 (Packaging)

UniSub 提供了一个自动化打包脚本，会自动构建前端并调用 Nuitka 进行编译：

```bash
# 执行打包脚本 (推荐)
uv run python scripts/package_app.py
```

> [!IMPORTANT]
> **Windows .exe 说明**：由于 Nuitka 不支持跨平台交叉编译，如果您需要生成 Windows 可执行文件 (`.exe`)，**必须**在 Windows 环境（如 CMD 或 PowerShell）中运行上述命令。在 Linux 或 WSL 中运行只会生成 Linux 二进制文件。

---

## ⚙️ 依赖说明

UniSub 通过一种极其轻量化的方式管理庞大的显卡驱动库：

- 默认不包含 `cublas64_12.dll` / `cudnn64_9.dll` 等 (约 1.4GB)。
- 当用户环境具备 NVIDIA 显卡时，系统会提示“一键安装”，从 PyPI 下载官方 Wheel 包并精准提取所需的运行时组件到 `resources/libs` 目录下。
- 该目录已默认加入 `.gitignore`。

---

## 📜 开源协议

基于 **MIT** 协议发布。
