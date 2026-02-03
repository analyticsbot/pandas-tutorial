# jupyter_book_pipeline_prometheus.py


import logging
from pathlib import Path
import re
import io
import base64
import matplotlib.pyplot as plt
import pdfplumber
import time
# from airllm import AutoTokenizer
# from airllm import AutoModel
from autogen import Agent
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json
from monitoring import call_llm  # Prometheus wrapper

# ---------------- Logging Setup ----------------
logging.basicConfig(filename="agent_logs.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

summary_file = Path("agent_summary.csv")
summary_file.write_text("chapter,file,agent,success,notes\n")  # CSV header
current_state_file = Path("current_state.json")

def set_agent_state(chapter, file, agent_name, status):
    state = {"chapter": chapter, "file": file, "agent": agent_name, "status": status, "time": time.time()}
    current_state_file.write_text(json.dumps(state))

# ---------------- Load PDFs ----------------
pdf_folder = Path("/Users/dks0790796/Downloads/Personal/pandas-tutorial/pandas_pdf")
pdf_files = sorted(pdf_folder.glob("part_*.pdf"))
pdf_pages, pdf_page_texts = [], []

for file in pdf_files:
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pdf_pages.append((file.name, i+1))
                pdf_page_texts.append(text)

logging.info(f"Loaded {len(pdf_page_texts)} PDF pages for reference.")

# ---------------- Embeddings for Intelligent PDF Retrieval ----------------
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
page_embeddings = embed_model.encode(pdf_page_texts, convert_to_numpy=True)
d = page_embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(d)
faiss_index.add(page_embeddings)

def retrieve_relevant_pages(query, top_k=5):
    query_emb = embed_model.encode([query], convert_to_numpy=True)
    D, I = faiss_index.search(query_emb, top_k)
    results = []
    for idx in I[0]:
        file, page_num = pdf_pages[idx]
        text = pdf_page_texts[idx]
        results.append(f"{file} page {page_num}: {text[:500]}...")
    return results

# ---------------- Load Jupyter Book ----------------
book_root = Path("/Users/dks0790796/Downloads/Personal/pandas-tutorial/book/chapters")
chapter_dirs = sorted([d for d in book_root.iterdir() if d.is_dir() and d.name.startswith("chapter")])
chapters = []
for chapter_dir in chapter_dirs:
    md_files = list(chapter_dir.glob("*.md"))
    chapters.append({"chapter_dir": chapter_dir, "md_files": md_files})

print(f"Found {len(chapters)} chapters in the book.")
print(f"Chapters: {[c['chapter_dir'].name for c in chapters]}")
# ---------------- Agents ----------------
class SequencerAgent(Agent):
    def __init__(self):
        super().__init__(name="SequencerAgent")
        self.memory = {}

    def run(self):
        # md_files = self.memory["md_files"]  # list of Path objects
        md_files = [
            f for f in self.memory["md_files"]
            if not f.name.startswith("polished_")
        ]
        chapter_name = self.memory["chapter_name"]

        # Read all file contents
        file_contents = {f.name: f.read_text() for f in md_files}

        # Build prompt with content
        prompt = """ 
        You are organizing Markdown files into a teaching sequence for absolute beginners.

        For each file:
        - Identify its primary concept
        - Decide prerequisite relationships

        Then output ONLY the filenames in correct reading order.
        Do not explain.

        """
        for name, text in file_contents.items():
            snippet = text[:500].replace("\n", " ")  # first 500 chars to avoid huge prompt
            prompt += f"{name}: {snippet}\n"

        set_agent_state(chapter_name, "?", "SequencerAgent", "running")
        sequenced_text = call_llm("SequencerAgent", prompt, max_tokens=1000)

        # Extract filenames
        sequenced_names = [
            line.strip() for line in sequenced_text.replace(",", "\n").splitlines() if line.strip()
        ]

        # Map to Path objects
        filename_map = {f.name: f for f in md_files}
        sequenced_files = [filename_map[name] for name in sequenced_names if name in filename_map]
        print("SequencerAgent ordered files:", sequenced_names)

        self.memory["sequenced_files"] = sequenced_files
        set_agent_state(chapter_name, "?", "SequencerAgent", "done")
        with open(summary_file, "a") as f:
            f.write(f"{chapter_name},?,SequencerAgent,success,sequenced {len(sequenced_files)} files\n")

        print("Sequenced files:", [f.name for f in sequenced_files])
        return sequenced_files


class ReaderAgent(Agent):
    def __init__(self):
        super().__init__(name="ReaderAgent")
        self.memory = {}

    def run(self):
        chapter = self.memory  # use memory instead of argument
        set_agent_state(chapter["chapter_name"], chapter["filename"], "ReaderAgent", "running")
        self.memory["chapter_text"] = chapter["chapter_text"]
        set_agent_state(chapter["chapter_name"], chapter["filename"], "ReaderAgent", "done")
        logging.info(f"ReaderAgent read {chapter['filename']}")
        return f"Read {chapter['filename']}"


class AnalystAgent(Agent):
    def __init__(self):
        super().__init__(name="AnalystAgent")
        self.memory = {}

    def run(self):
        chapter_name = self.memory.get("chapter_name","?")
        filename = self.memory.get("filename","?")
        set_agent_state(chapter_name, filename, "AnalystAgent", "running")
        chapter_text = self.memory["chapter_text"]
        prompt = f"""
        You are reviewing a Pandas tutorial for beginners.

        Identify:
        1. Concepts assumed but not explained
        2. Missing step-by-step examples
        3. Sections that are too dense
        4. Opportunities for visuals or tables

        Return bullet points grouped by section.

        Chapter:
        {chapter_text}
            """
        suggestions = call_llm("AnalystAgent", prompt, max_tokens=300)
        self.memory["suggestions"] = suggestions
        set_agent_state(chapter_name, filename, "AnalystAgent", "done")
        with open(summary_file, "a") as f:
            f.write(f"{chapter_name},{filename},AnalystAgent,success,suggestions length {len(suggestions)}\n")
        logging.info(f"AnalystAgent suggestions length {len(suggestions)}")
        return suggestions

class PlannerAgent(Agent):
    def __init__(self):
        super().__init__(name="PlannerAgent")
        self.memory = {}

    def run(self):
        text = self.memory["chapter_text"]
        prompt = f"""
        You are planning an EXPANSION of a beginner Pandas chapter.

        Given this content:
        {text}

        Given the content, produce a plan with:
        - Section-by-section expansion goals
        - New examples to add (describe inputs + outputs)
        - Where plots would help understanding
        - Which Pandas APIs should be introduced and why

        Output a numbered plan. Be concrete.
        """
        plan = call_llm("PlannerAgent", prompt, max_tokens=600)
        self.memory["plan"] = plan
        return plan


def split_md_semantic(text, max_chars=3000):
    sections = re.split(r'(?=\n#{1,3}\s)', text)
    chunks = []
    buf = ""

    for sec in sections:
        candidate = buf + sec

        # 🔒 guard: don't split inside code blocks
        if candidate.count("```") % 2 != 0:
            buf = candidate
            continue

        if len(candidate) > max_chars and buf:
            chunks.append(buf)
            buf = sec
        else:
            buf = candidate

    if buf:
        chunks.append(buf)

    return chunks



class WriterAgent(Agent):
    def __init__(self):
        super().__init__(name="Agent")
        self.memory = {}

    def run(self):
        chapter_name = self.memory.get("chapter_name","?")
        filename = self.memory.get("filename","?")
        set_agent_state(chapter_name, filename, "WriterAgent", "running")
        chapter_text = self.memory["chapter_text"]
        chunks = split_md_semantic(chapter_text)
        expanded_chunks = []

        suggestions = self.memory.get("suggestions", "")
        plan = self.memory.get("plan", "")

        for i, chunk in enumerate(chunks):
            relevant_pdfs = retrieve_relevant_pages(chunk, top_k=10)
            self.memory["pdf_references"] = relevant_pdfs
            prompt = f"""
                You are expanding (not summarizing) a Pandas tutorial for beginners.

                Follow this plan exactly:
                {plan}

                Rules:
                - Never remove existing content
                - Add explanations, intuition, and examples
                - Code must be runnable
                - Explain outputs in plain English

                Use these references only when relevant:
                {relevant_pdfs}

                Consider these suggestions for improvement:
                {suggestions}

                Section to expand:
                {chunk}
            """
            expanded = call_llm("WriterAgent", prompt, max_tokens=1200)
            expanded_chunks.append(expanded)
        refined_text = "\n\n".join(expanded_chunks)
        self.memory["refined_text"] = refined_text
        set_agent_state(chapter_name, filename, "WriterAgent", "done")
        with open(summary_file, "a") as f:
            f.write(f"{chapter_name},{filename},WriterAgent,success,refined text length {len(refined_text)}\n")
        logging.info(f"WriterAgent polished {filename}, top 200 chars:\n{refined_text[:200]}")
        return refined_text

class CodeVerifierAgent(Agent):
    def __init__(self):
        super().__init__(name="CodeVerifierAgent")
        self.memory = {}

    def run(self):
        text = self.memory["refined_text"]
        chapter = self.memory.get("chapter_name", "?")
        filename = self.memory.get("filename", "?")

        code_blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
        verified_blocks = []

        for code in code_blocks:
            try:
                exec(code, {}, {})
                verified_blocks.append(code)
                notes = "ran successfully"

            except Exception as e:
                prompt = f"""
                Fix this Python code so it runs correctly and is beginner-friendly.
                Only output valid Python code. No explanations.

                ```python
                {code}
                ```"""
                fixed_code = call_llm("CodeVerifierAgent", prompt, max_tokens=150)
                verified_blocks.append(fixed_code.strip())
                notes = "fixed by LLM"
            logging.info(f"CodeVerifierAgent: {notes}")
            with open(summary_file, "a") as f:
                f.write(f"{chapter},{filename},CodeVerifierAgent,success,{notes}\n")

        for original, verified in zip(code_blocks, verified_blocks):
            text = text.replace(
                f"```python\n{original}```",
                f"```python\n{verified}```"
            )

        self.memory["refined_text"] = text
        return text



class PlotAgent(Agent):
    def __init__(self):
        super().__init__(name="PlotAgent")
        self.memory = {}

    def run(self):
        text = self.memory["refined_text"]
        code_blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
        for code in code_blocks:
            if "# plot_example" in code.lower() or "plt." in code:
                try:
                    local_vars = {}
                    exec(code, {}, local_vars)
                    fig = plt.gcf()
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png")
                    plt.close(fig)
                    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    text = text.replace(f"```python\n{code}```",
                                        f"```python\n{code}```\n\n![plot](data:image/png;base64,{img_base64})")
                    notes = "plot embedded"
                except Exception as e:
                    logging.warning(f"PlotAgent failed: {e}")
                    notes = f"plot failed: {e}"
                with open(summary_file, "a") as f:
                    f.write(f"{self.memory.get('chapter_name','?')},{self.memory.get('filename','?')},PlotAgent,success,{notes}\n")
        self.memory["refined_text"] = text
        return text
    
class EditorAgent(Agent):
    def __init__(self):
        super().__init__(name="EditorAgent")
        self.memory = {}

    def run(self):
        chapter_name = self.memory.get("chapter_name", "?")
        filename = self.memory.get("filename", "?")

        set_agent_state(chapter_name, filename, "EditorAgent", "running")

        text = self.memory["refined_text"]
        prompt = (
            "Polish the chapter for clarity, flow, consistency, and beginner-friendliness.\n\n"
            f"{text}"
        )

        polished_text = call_llm(
            agent_name="EditorAgent",
            prompt=prompt,
            max_tokens=500
        )

        self.memory["polished_text"] = polished_text

        set_agent_state(chapter_name, filename, "EditorAgent", "done")

        logging.info(f"EditorAgent polished {filename}, first 200 chars:\n{polished_text[:200]}")

        with open(summary_file, "a") as f:
            f.write(
                f"{chapter_name},{filename},EditorAgent,success,polished length {len(polished_text)}\n"
            )

        return polished_text


# ---------------- CodeVerifierAgent, PlotAgent, EditorAgent ----------------
# These remain same as before but add set_agent_state at start/end
# Inside any LLM call inside them, replace with call_llm(...)

# ---------------- Initialize World ----------------
sequencer_agent = SequencerAgent()
agents = [ReaderAgent(), PlannerAgent(), AnalystAgent(), WriterAgent(), CodeVerifierAgent(), PlotAgent(), EditorAgent()]

# ---------------- Run Pipeline ----------------
toc_lines = ["format: jb-book", "root: intro", "chapters:"]

for chapter in chapters:
    chapter_name = chapter["chapter_dir"].name
    
    # Sequencer Agent to order markdown files
    sequencer_agent.memory["chapter_name"] = chapter_name
    sequencer_agent.memory["md_files"] = chapter["md_files"]
    sequencer_agent.run()
    sequenced_files = sequencer_agent.memory["sequenced_files"]

    # Process each markdown file sequentially with all agents
    for md_file in sequenced_files:
        md_path = chapter["chapter_dir"] / md_file
        out_file = md_path.with_name(f"polished_{md_path.name}")    
        if out_file.exists():
            logging.info(f"Skipping already polished file: {out_file}")
            toc_lines.append(f"  - file: {chapter_name}/{md_file.stem}")
            continue

        # Read markdown content
        text = md_path.read_text()

        # Sequentially run each agent
        agent_memory = {
            "chapter_name": chapter_name,
            "filename": md_path.name,
            "chapter_text": text
        }

        # List of all agents in order
        agents = [ReaderAgent(), AnalystAgent(), WriterAgent(), CodeVerifierAgent(), PlotAgent(), EditorAgent()]

        for agent in agents:
            agent.memory.update(agent_memory)
            agent.run()
            # Update memory if agent produces refined_text or suggestions
            agent_memory.update(agent.memory)

        # Save final polished text from WriterAgent / EditorAgent
        polished_text = agent_memory.get("refined_text") or agent_memory.get("polished_text") or text
        out_file.write_text(polished_text)
        logging.info(f"Saved polished file: {out_file}")
        toc_lines.append(f"  - file: {chapter_name}/{md_file.stem}")


# ---------------- Write _toc.yml ----------------
Path(book_root / "_toc.yml").write_text("\n".join(toc_lines))
logging.info("Generated _toc.yml for Jupyter Book compilation.")
