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
  - **一键部署**：业内首创“自剥离”技术，一键从 PyPI 官方渠道部署 CUDA/cuDNN 运行环境。
  - **无管理员运行**：所有依赖库自动下发至用户目录（User Data），彻底解决 Windows `Program Files` 权限锁死问题，无需管理员权限即可享受 GPU 加速。

- 🧠 **聪明过人的 AI 翻译**：
  - **上下文关联**：采用 Batch 批处理技术，让 LLM 在翻译时感知视频前后的语境，彻底告别单句翻译的僵硬感。
  - **错误熔断机制**：任何 AI 请求异常（如网络超时、Token 不足）将即时反馈，杜绝无效任务空跑。
  - **多模型支持**：无缝对接 OpenAI、DeepSeek、Ollama、Sakura 等主流 LLM 接口。

- 🎨 **高级视觉体验 & 系统管理**：
  - **透明化管理**：内置“系统状态”面板，一键查看并打开配置文件、日志文件及 GPU 依赖库所在目录。
  - **状态持久化**：全局状态管理，页面切换不丢失任务进度。
  - **毛玻璃设计**：基于现代审美设计的深色模式界面，支持流畅的微交互动画。

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

UniSub 提供了一个全自动化打包脚本，集成了 **Nuitka** 编译与 **Inno Setup** 安装包生成：

```bash
# 执行打包脚本 (推荐，Windows下将自动生成安装包)
uv run python scripts/package_app.py
```

- **自动化构建**：脚本会自动编译前端、打包 Python 后端。
- **安装包生成**：在 Windows 环境下，如检测到 Inno Setup 编译器，将自动生成标准的 Windows 安装程序 (`.exe`)，支持**可选卸载清理**（日志/配置/依赖）。
- **资源修正**：自动处理 `faster-whisper` 等库的隐式数据文件依赖（如 VAD 模型）。

> [!IMPORTANT]
> **Windows .exe 说明**：由于 Nuitka 不支持跨平台交叉编译，如果您需要生成 Windows 可执行文件 (`.exe`)，**必须**在 Windows 环境（如 CMD 或 PowerShell）中运行上述命令。

---

## ⚙️ 依赖说明

UniSub 通过一种极其轻量化的方式管理庞大的显卡驱动库：

- 默认不包含 `cublas64_12.dll` / `cudnn64_9.dll` 等 (约 1.4GB)。
- **按需下载**：通过前端界面的“系统状态”页发起下载，支持**断点续传**与**任务取消**。
- **存储位置**：所有大体积依赖均存储于系统的 `%LOCALAPPDATA%\UniversalSub\libs` (Windows) 或 `~/.local/share/UniversalSub/libs` (Linux)，不占用软件安装目录空间。

基于 **MIT** 协议发布。

> 🤖 **Note**: 本项目代码均由 AI 生成。
