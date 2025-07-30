# cloud-diff

# yaml-json-diff - YAML & JSON Diff Tool with AI Explanations

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Last Commit](https://badgen.net/github/last-commit/pooya-rostami/yaml-json-diff)](https://github.com/pooya-rostami/yaml-json-diff/commits/)
[![PyPI](https://img.shields.io/pypi/v/yaml-json-diff.svg)](https://pypi.org/project/yaml-json-diff/)

`yaml-json-diff` is a Python CLI tool and library based on [DeepDiff](https://github.com/seperman/deepdiff) for computing the difference between YAML and JSON files.
It also offers optional **AI-powered explanations** of the diffs using local language models via [Ollama](https://ollama.com).

---

## Features

- Compare two `.yaml`, `.yml`, or `.json` files
- Human-readable or JSON-formatted diff outputs
- Optional AI-generated summary of changes (`--explain`) using LLMs like Mistral, LLaMA via Ollama
- Clean CLI interface via [Typer](https://github.com/tiangolo/typer)
- Docker support

---

## Installation

### From PyPI

```bash
pip install yaml-json-diff
```

### From GitHub (latest)

```bash
pip install git+https://github.com/pooya-rostami/yaml-json-diff.git
```

### Poetry (local dev)

```bash
git clone https://github.com/pooya-rostami/yaml-json-diff.git
cd yaml-json-diff
poetry install --only main
```

---

## Usage

### CLI

```bash
yaml-json-diff FILE1 FILE2 [OPTIONS]
```

**Options:**

| Option          | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| `--explain, -e` | Generate an AI explanation of the diff using a local LLM (via Ollama) |
| `--model, -m`   | Model to use for explanation (default: `mistral`)                     |

---

## Examples

Basic diff:

```bash
yaml-json-diff config-v1.yaml config-v2.json
```

With AI Explanation:

```bash
yaml-json-diff config-old.json config-new.json --explain
```

Using a Custom Ollama Model:

```bash
yaml-json-diff file1.yaml file2.yaml --explain --model llama3
```

---

## AI Support via Ollama

To use the `--explain` feature:

1. Install Ollama from https://ollama.com

2. Ensure Ollama is running:
```bash
ollama run mistral
```

3. Use the `--explain` flag in the CLI

By default, the tool uses the **mistral** model. You can switch to another model like **llama3**, **codellama**, etc.

---

## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.

---

## License

This tool is distributed under [GNU Lesser General Public License v3](https://github.com/pooya-rostami/gawd/blob/main/LICENSE.txt).
