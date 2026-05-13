# QQ-Ollama-Robot

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange.svg)
![NapCat](https://img.shields.io/badge/NapCat-OneBot%2011-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个基于 **Ollama** 本地大模型运行的智能 QQ 机器人。通过 **Python WebSocket** 模块与 **NapCat (OneBot 11)** 框架建立连接，实现低延迟、高灵活性的群聊娱乐与个人私聊互动。

---

## ✨ 项目特性

- **本地运行**：基于 Ollama 框架，支持多种主流开源大模型（如 Llama 3, Qwen, Gemma 等），保护隐私且完全免费。
- **高效连接**：利用 WebSocket 协议实现与 NapCat 的双向实时通信，响应速度极快。
- **多场景适用**：支持群聊 @ 触发、关键词触发以及个人私聊等多种交互模式。
- **易于扩展**：纯 Python 编写，代码逻辑清晰，方便添加自定义插件或功能。

---

## 🛠️ 技术栈

* **核心框架**: [Ollama](https://ollama.com/) (本地大模型引擎)
* **机器人框架**: [NapCatQQ](https://github.com/NapNeko/NapCatQQ) (基于 OneBot 11 标准)
* **编程语言**: Python 3.8+
* **通信协议**: WebSocket (Client)

---

## 🚀 快速开始

### 1. 环境准备
* 安装并运行 [Ollama](https://ollama.com/)，拉取模型：`ollama pull qwen2`
* 部署 [NapCatQQ](https://github.com/NapNeko/NapCatQQ)，开启 **正向 WebSocket 服务**（默认端口 3001）。

### 2. 安装与运行
```bash
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的仓库名
pip install -r requirements.txt
python main.py
