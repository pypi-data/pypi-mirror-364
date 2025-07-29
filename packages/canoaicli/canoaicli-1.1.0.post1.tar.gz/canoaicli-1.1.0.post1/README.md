![PyPI - Downloads](https://img.shields.io/pypi/dm/canoaicli)
![PyPI - Version](https://img.shields.io/pypi/v/canoaicli)

# Canoaicli – AI in your terminal

**Canoaicli** is a minimalist and intelligent command-line tool. It lets you generate terminal commands from simple natural language instructions, powered by Google Gemini AI.

---

## 🚀 Installation

Make sure you have **Python ≥ 3.11**, then install it easily from PyPI:

```bash
pip install canoaicli
```

## 🧠 Configuration

Before starting, configure your **Gemini API key** (get one from [Google AI Studio](https://makersuite.google.com/app/apikey)):

```bash
ai configure
```

This will prompt you for your API key, which will be stored securely on your system.

## 📜 History

If you want to use the history feature, you can use the following command:

**This will show you the history of your commands.**

```bash
ai history
```

**You can also search for a specific command in the history:**

```bash
ai history --search <keyword>
```

**You can also clear the history:**

```bash
ai history clear
```

---

## 💡 Usage

Once installed and configured, use AI directly in your terminal:

```bash
ai ask <your prompt>
```

Examples:

```bash
ai ask how to list all docker containers
ai ask delete all git branches except main
ai ask create a new virtual environment in python

```

The tool will show you the appropriate shell commands, clearly and ready to be copied or run.

## 🛠️ Features

- Generate bash/git/docker commands from natural language
- Fast and smooth usage
- Interactive interface (thanks to `rich` and `questionary`)
- Secure Gemini API key configuration
- Open source and extensible

---

## 📦 Local development

To contribute to the project:

```bash
git clone https://github.com/carellihoula/AssistantIACLI.git
```

```bash
cd AssistantIACLI
```

```bash
pixi shell
```

```bash
pixi install
```

---

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ✨ Demo video

_(coming soon)_ 🎥
