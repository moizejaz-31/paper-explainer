# 📄 Paper Explainer Skill for Gemini & Antigravity

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Google Antigravity](https://img.shields.io/badge/Agent-Google%20Antigravity-orange.svg)](#)
[![Gemini CLI](https://img.shields.io/badge/Gemini-Custom%20Skill-blueviolet.svg)](#)

> **Deconstruct dense AI & ML research papers into plain English, intuitive walkthroughs, structured contributions, and extracted future work.**

`paper-explainer` is an agent skill and plugin designed for **Google Antigravity** and **Gemini**. It empowers your AI agent to thoroughly read, understand, and explain academic research papers (e.g. NeurIPS, ICML, ICLR, CVPR, arXiv) without getting lost in mathematical weeds or regurgitating dense abstracts.

---

## 🌟 What the Skill Delivers

Whenever you ask your Gemini or Antigravity assistant about a paper, it produces a structured 4-part breakdown:

1. **💡 In Plain English (ELI5 Overview)**  
   - A single-sentence summary of what the paper actually accomplishes.  
   - An intuitive elevator pitch avoiding academic jargon.  
   - A real-world analogy that makes the core idea instantly click.

2. **🧠 How It Works (Intuitive Deep-Dive)**  
   - **The Problem:** Why prior approaches failed or hit bottlenecks.  
   - **The Solution:** Step-by-step mechanics of the proposed method.  
   - **Visual Flow:** Mermaid flowcharts of the pipeline/architecture.  
   - **Demystified Math:** What equations and variables physically mean in practice.

3. **🏆 Main Contributions**  
   - Algorithmic and architectural novelties.  
   - Theoretical guarantees or proofs.  
   - Empirical benchmark gains and state-of-the-art results.  
   - Released datasets, weights, or software artifacts.

4. **🔭 Future Work & Limitations**  
   - Explicit next research steps and directions stated by the authors.  
   - Acknowledged bottlenecks, computational costs, and failure modes.  
   - Open questions for the research community.

---

## 🚀 Supported Paper Inputs

- **arXiv URLs or IDs**: e.g., `https://arxiv.org/abs/1706.03762` or `1706.03762`
- **Local PDF Files**: e.g., `C:/path/to/neurips_paper.pdf`
- **Direct Conference URLs**: OpenReview, NeurIPS proceedings, or any direct PDF link.
- **Pasted Text / Abstracts**: Simply paste sections or abstracts directly into the chat.

---

## 📦 Connecting to Your Gemini / Antigravity Assistant

### Method 1: Global Installation (Recommended)

To make `paper-explainer` available everywhere in your Gemini / Antigravity assistant:

1. Clone or download this repository:
   ```bash
   git clone https://github.com/moizejaz-31/paper-explainer.git
   ```

2. Copy or link the skill into your global Antigravity / Gemini skills directory:
   - **Windows**:
     ```powershell
     Copy-Item -Path "paper-explainer\skills\paper-explainer" -Destination "$HOME\.gemini\config\skills\paper-explainer" -Recurse -Force
     ```
   - **macOS / Linux**:
     ```bash
     mkdir -p ~/.gemini/config/skills
     cp -r paper-explainer/skills/paper-explainer ~/.gemini/config/skills/
     ```

3. Ensure `~/.gemini/config/skills.json` includes:
   ```json
   {
     "entries": [
       {
         "path": "~/.gemini/config/skills"
       }
     ]
   }
   ```

---

### Method 2: Project / Workspace-Specific Installation

If you only want this skill in a specific workspace:

1. Copy the skill into your project's `.agents/skills/` directory:
   ```bash
   mkdir -p .agents/skills
   cp -r paper-explainer/skills/paper-explainer .agents/skills/
   ```

---

## 🛠️ Standalone Python Extraction Tool

The skill includes a standalone CLI extractor in `skills/paper-explainer/scripts/extract_paper.py` that downloads papers, parses sections with `pypdf`, and extracts contributions and future work into structured JSON:

```bash
# Extract an arXiv paper
uv run --with pypdf python skills/paper-explainer/scripts/extract_paper.py \
  --arxiv 1706.03762 \
  --output summary.json

# Extract a local PDF
uv run --with pypdf python skills/paper-explainer/scripts/extract_paper.py \
  --pdf path/to/paper.pdf \
  --output summary.json
```

---

## 💬 Example Queries

Once connected, simply ask Gemini:
- *"Can you explain this NeurIPS paper to me: `https://arxiv.org/abs/2310.06825`?"*
- *"What does this paper do in simple terms, and what future work did the authors propose?"*
- *"Break down `C:/Downloads/flash_attention.pdf` using paper-explainer."*

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
