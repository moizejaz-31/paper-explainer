---
name: paper-explainer
description: >-
  Explains, digests, and analyzes scientific research papers (such as NeurIPS, ICML,
  ICLR, CVPR, arXiv, or general academic publications). Translates complex research
  into plain-English easy-to-understand explanations, provides an intuitive breakdown
  of how the method works, lists the paper's core contributions, and explicitly extracts
  all future work and limitations outlined by the authors. Use whenever asked to explain,
  summarize, read, or break down a research paper, arXiv link, conference paper, or PDF.
---

# Paper Explainer (Research Paper Deconstructed)

Deconstructs academic research papers into intuitive, highly understandable explanations. Specifically tailored for AI/ML conference papers (e.g., NeurIPS, ICML, ICLR, CVPR) and preprints (arXiv), this skill translates dense math and academic jargon into clear conceptual models, lists core contributions, and surfaces explicit future research directions.

---

## When to Activate

Trigger this skill whenever the user:
- Asks to understand, summarize, or explain a research paper (e.g. *"Can you explain this NeurIPS paper to me?"*).
- Provides an arXiv link, arXiv ID, or paper URL (e.g. `https://arxiv.org/abs/...` or OpenReview).
- Shares a local PDF file path or pastes paper text/abstract.
- Asks *"What does this paper do in simple terms?"*, *"What are the main contributions?"*, or *"What is the future work listed in this paper?"*.

---

## Core Deliverables

Every paper analysis produced by this skill must follow the structured template in [output_template.md](references/output_template.md), providing these 4 essential sections:

1. **💡 In Plain English (ELI5 Overview)**:
   - A 1-sentence one-liner.
   - An elevator pitch (2-3 sentences) avoiding dense jargon.
   - A real-world intuitive analogy that helps anyone grasp the core idea immediately.

2. **🧠 How It Works (Intuitive Deep-Dive)**:
   - The specific problem or bottleneck with previous methods.
   - Step-by-step walkthrough of the new mechanism or pipeline.
   - A visual workflow or architecture diagram (`mermaid`).
   - Demystified math/concepts: explaining what variables and equations actually represent in plain language.

3. **🏆 Main Contributions**:
   - Structured breakdown: Algorithmic novelty, theoretical insights, empirical benchmark gains, and released artifacts (datasets/code).

4. **🔭 Future Work & Limitations**:
   - Explicit future directions mentioned by the authors (from Conclusion, Discussion, or Future Work sections).
   - Acknowledged bottlenecks, failure modes, computational costs, and open questions.

---

## Workflow

### Step 1: Extract the Paper Content

Use the helper script `scripts/extract_paper.py` to extract text, sections, and targeted excerpts from the paper.

#### For an arXiv paper:
```bash
uv run --with pypdf python scripts/extract_paper.py \
  --arxiv "<arxiv_id_or_url>" \
  --output "<scratch_dir>/paper_summary.json"
```

#### For a local PDF file:
```bash
uv run --with pypdf python scripts/extract_paper.py \
  --pdf "<path_to_pdf>" \
  --output "<scratch_dir>/paper_summary.json"
```

#### For an arbitrary paper URL (e.g. OpenReview, NeurIPS proceedings):
```bash
uv run --with pypdf python scripts/extract_paper.py \
  --url "<pdf_url>" \
  --output "<scratch_dir>/paper_summary.json"
```

#### For raw text or pasted markdown:
```bash
uv run --with pypdf python scripts/extract_paper.py \
  --text "<path_to_text_file>" \
  --output "<scratch_dir>/paper_summary.json"
```

> **Note**: The script produces both a structured `paper_summary.json` (containing the abstract, contributions, future work excerpts, and section signals) and a `<output_name>_full.txt` containing the full text with page markers for deep reading.

---

### Step 2: Read Extracted Signals

1. Read `paper_summary.json` using `read_file`.
2. Inspect:
   - `abstract`: Core premise.
   - `contributions_excerpts`: Author's claimed novelties.
   - `future_work_excerpts`: Passages mentioning future work, next steps, open problems.
   - `limitations_excerpts`: Acknowledged limitations, bottlenecks, or failure cases.
   - `conclusion_section`: The concluding thoughts and outlook.
3. If more detail on the methodology is required, read the relevant page ranges from `full_text_file`.

---

### Step 3: Synthesize and Present the Explanation

Format the final response according to [references/output_template.md](references/output_template.md).

#### Key Guidelines for the Explanation:
- **No Unexplained Jargon**: Never quote dense mathematical jargon (e.g., *"manifold hypothesis"*, *"non-asymptotic Lipschitz constant"*, *"stochastic differential equation"*) without immediately explaining the physical intuition behind it.
- **Use Real Analogies**: Relate the paper's mechanism to everyday concepts (e.g., explaining attention as *"a student highlighting key words in a textbook rather than memorizing the whole page"*).
- **Be Truthful to the Paper's Claims**: Do not invent future work. Specifically quote or cite what the authors themselves stated they plan to investigate or left as open problems.
- **Include Visuals**: Use a clear `flowchart LR` or `flowchart TD` mermaid diagram to visualize the model/system pipeline.

---

## Common Pitfalls to Avoid

- **Regurgitating the Abstract**: The abstract is written for specialized peer reviewers. Do NOT simply paraphrase the abstract. Break it down so that someone without a PhD in that exact subfield can understand it.
- **Skipping Limitations/Future Work**: Many summaries stop at results. Always check the Discussion, Limitations, and Conclusion sections to extract open questions and future work.
- **Overlooking Negative Results / Constraints**: Note if the method requires massive compute, only works on toy datasets, or has high latency.
