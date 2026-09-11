"""Generate an evidence-bounded evaluation addendum for the Friday project."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUT = Path(__file__).with_name("Friday_Evaluation_Revision.pdf")
audit = json.loads(Path(__file__).with_name("corpus_audit.json").read_text(encoding="utf-8"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="PaperTitle", parent=styles["Title"], alignment=TA_CENTER,
                          fontName="Helvetica-Bold", fontSize=18, leading=22, spaceAfter=10))
styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"], alignment=TA_CENTER,
                          textColor=colors.HexColor("#44546A"), fontSize=10, leading=14, spaceAfter=18))
styles.add(ParagraphStyle(name="H", parent=styles["Heading2"], fontName="Helvetica-Bold",
                          fontSize=12, leading=15, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontName="Helvetica",
                          fontSize=9.4, leading=13, spaceAfter=7))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica",
                          fontSize=8, leading=10, spaceAfter=4))
styles.add(ParagraphStyle(name="TableHead", parent=styles["Small"], fontName="Helvetica-Bold",
                          textColor=colors.white, spaceAfter=0))
styles.add(ParagraphStyle(name="TableCell", parent=styles["Small"], spaceAfter=0))

def P(text, style="Body2"):
    return Paragraph(text, styles[style])

def tbl(rows, widths):
    wrapped = []
    for row_i, row in enumerate(rows):
        style = "TableHead" if row_i == 0 else "TableCell"
        wrapped.append([Paragraph(str(cell), styles[style]) for cell in row])
    t = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("LEADING", (0,0), (-1,-1), 10),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#B8C4CE")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF3F8")]),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#B8C4CE")); canvas.line(2*cm, 1.35*cm, 19*cm, 1.35*cm)
    canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#44546A"))
    canvas.drawString(2*cm, .9*cm, "Friday - Evaluation revision and reproducibility appendix")
    canvas.drawRightString(19*cm, .9*cm, f"Page {doc.page}")
    canvas.restoreState()

pages = audit["pages"]; files = audit["files"]; chars = audit["characters"]; chunks = audit["chunks_800_100"]
story = [P("Friday: Evaluation Revision", "PaperTitle"),
         P("Reproducibility appendix responding to evaluation feedback | 11 August 2026", "SubTitle"),
         P("Purpose", "H"),
         P("This addendum corrects the evidential scope of the evaluation in <i>Friday: A Local Retrieval-Augmented Generation System for Privacy-Preserving Multi-Domain PDF Intelligence</i>. It is designed to accompany the preview paper, not to manufacture missing experimental results. All numerical corpus quantities below were re-derived directly from the supplied Friday repository using the same PyMuPDF extraction and fixed-character chunking logic implemented in <font name='Courier'>backend/app.py</font>."),
         P("The original retrieval figures (80 manually constructed queries) should be treated as a pilot study. They are useful for debugging and design exploration, but they do not establish robust, general performance without a frozen query set, independently checked relevance labels, and uncertainty estimates. Consequently, this revision removes any claim that the pilot establishes superiority or general behaviour."),
         P("Corrected headline claim", "H"),
         P("Friday demonstrates an end-to-end local PDF indexing and retrieval prototype over a heterogeneous 706-file corpus. Its pilot evaluation provides preliminary evidence that dense retrieval can be useful for the chosen queries. It does <b>not</b> establish statistically robust superiority over BM25, a general latency/throughput guarantee, or a negligible HNSW approximation cost. Those questions require the protocol below."),
         P("What changed", "H"),
         tbl([["Original issue", "Revision"],
              ["Unfilled result cells and unsupported ablations", "Reported as not measured; no values are inferred."],
              ["Strong claims from 80 hand-authored queries", "Reframed as descriptive pilot results; confidence intervals and label agreement are required before comparative claims."],
              ["Documents/minute throughput", "Replaced by pages, extracted characters, chunks, vectors, elapsed time and machine/software details."],
              ["BM25 presented as the key comparator", "Retained only as a lexical diagnostic; the primary comparisons are dense-model, chunking, hybrid and HNSW configurations."]], [5.0*cm, 12.0*cm]),
         PageBreak(),
         P("1. Repository-derived corpus audit", "H"),
         P(f"The repository contains {files:,} PDFs across eight directories. Running the implementation's extraction approach across the complete corpus yielded {pages:,} pages, {chars:,} extracted characters and {chunks:,} non-empty chunks using the production configuration: 800 characters per chunk with a 100-character overlap. Each chunk produces one embedding/vector in the current implementation."),
         P("The extraction-only pass completed in 18.936 seconds on the machine used to generate this appendix (approximately 4,426 pages/minute). This is <b>not</b> an indexing throughput result: it excludes embedding, ChromaDB upsert, cold-start time, I/O variation and the M1 hardware named in the preview. It must not be compared with an end-to-end indexing measurement."),
         tbl([["Domain", "PDFs", "Pages", "Chunks (800 char / 100 overlap)", "Mean pages/PDF"]] +
             [[domain.title(), str(sum(1 for r in audit["rows"] if r[0]==domain)),
               str(sum(r[2] for r in audit["rows"] if r[0]==domain)),
               str(sum(r[4] for r in audit["rows"] if r[0]==domain)),
               f"{sum(r[2] for r in audit['rows'] if r[0]==domain)/sum(1 for r in audit['rows'] if r[0]==domain):.2f}"]
              for domain in sorted(set(r[0] for r in audit["rows"]))] +
             [["Total", str(files), str(pages), str(chunks), f"{pages/files:.2f}"]],
             [3.3*cm, 2*cm, 2*cm, 5.2*cm, 3.1*cm]),
         Spacer(1, 8),
         P("Interpretation", "H"),
         P("The corpus is broad in file categories but not a standard retrieval benchmark. Its documents are short on average (1.98 pages/PDF), and its extracted content is highly uneven. Results should therefore be reported per domain and per query type rather than as a single system-wide number only."),
         P("2. Corrected indexing evaluation", "H"),
         P("Indexing should be measured per unit of content, not per document. For every measured run, report: (i) PDFs, pages and extracted characters accepted; (ii) chunks/vectors written; (iii) wall-clock elapsed time from first file read through final vector upsert; (iv) extraction, embedding and database-upsert phases separately; (v) peak resident memory; (vi) resulting collection/index size; and (vii) CPU, RAM, storage, OS, Python, ChromaDB and sentence-transformers versions. Include a cold run and at least five warm runs. Report median, interquartile range and individual-run values."),
         PageBreak(),
         P("3. Retrieval evaluation protocol", "H"),
         P("The pilot set should be frozen in a versioned CSV or JSONL file containing query id, domain, query type, target document/chunk identifiers, and relevance label. Before comparing systems, create at least 15-20 queries per domain, sampled from realistic information needs. Keep development queries separate from the final test queries. Where feasible, use two assessors who label relevance independently and report Cohen's kappa (or a comparable agreement measure); resolve disagreements using a documented rule."),
         tbl([["Comparison", "Why it is relevant to Friday", "Measures"],
              ["Embedding model: MiniLM vs bge-small vs mpnet", "Tests the semantic representation under local CPU constraints.", "Recall@k, nDCG@k, MRR, embedding ms/chunk, vector bytes."],
              ["Chunking: fixed 400/800/1200 characters and paragraph-aware", "Tests whether boundaries preserve the knowledge needed for personal documents.", "Recall@k, nDCG@k, MRR, chunks, index size, indexing time."],
              ["Dense vs hybrid RRF", "Tests lexical matching as a complement, not merely as a straw-man baseline.", "Recall@k, nDCG@k, MRR, latency."],
              ["HNSW vs exact flat dense", "Measures the quality-latency trade-off made by approximate search.", "Recall agreement with flat top-k, query p50/p95, index size."]], [4.2*cm, 7.5*cm, 3.9*cm]),
         P("Analysis", "H"),
         P("For each paired comparison, use the per-query difference in the metric and report a 95% stratified bootstrap confidence interval (resampling queries within domain). A paired randomisation or Wilcoxon signed-rank test may be reported as a secondary check. State the number of queries and relevance judgements, the random seed, and whether model/chunk settings were chosen on the held-out test set. Do not claim one method is better when the confidence interval includes zero."),
         P("Metrics", "H"),
         P("Use Recall@k, MRR and nDCG@k. Precision@k alone is sensitive to the number of relevant chunks and should not be the only ranking measure. For HNSW, report agreement with exhaustive dense retrieval as Recall@k of flat-dense neighbours, separately from answer relevance. This distinguishes ANN approximation loss from embedding quality."),
         P("4. Systems-performance methodology", "H"),
         P("Performance results describe a configuration, not general system behaviour. Record the complete environment and run a fixed workload after a documented warm-up. Report p50/p95 latency for query embedding, vector search and end-to-end retrieval; report time-to-first-token and generated tokens/s separately for each LLM. Vary corpus size by vector count (for example, 500, 2,500, 5,000 and 7,500 vectors) rather than document count. Do not label a handful of measurements as proof of O(log n) scaling; HNSW has favourable expected behaviour, but observed scaling must be demonstrated across repeated runs and configurations."),
         PageBreak(),
         P("5. Results status and replacement text", "H"),
         tbl([["Result previously shown", "Status in this revision", "Permitted wording"],
              ["Dense HNSW vs BM25: 80 queries", "Pilot point estimates only; no confidence interval or independent labels available.", "'In a small manually constructed pilot set, dense retrieval obtained higher point estimates than BM25. This finding is exploratory and requires confirmation under the preregistered protocol.'"],
              ["Flat dense / hybrid RRF cells", "Not measured in supplied materials.", "'Not evaluated; excluded from comparative conclusions.'"],
              ["Chunk, embedding, LLM and HNSW tables", "Not measured in supplied materials.", "'Planned configuration study; no result is reported until the run log and labels are available.'"],
              ["Pages/min, latency and token rate", "Preview values lack sufficient measurement detail and are single-machine observations.", "'Observed on one named test machine only; not a deployment guarantee. Methods and dispersion must accompany any figure.'"],
              ["90% refusal rate", "A claim depends on the unavailable 160-query test log and scoring rule.", "'Remove or label as an unverified pilot observation until prompts, outputs and adjudication criteria are archived.'"]], [4.0*cm, 5.7*cm, 5.9*cm]),
         P("Suggested replacement for the conclusion", "H"),
         P("Friday provides a working local RAG implementation with isolated document groups, PDF ingestion, dense vector retrieval and streamed local generation. A repository audit confirms that the current corpus contains 706 PDFs, 1,397 pages and 6,283 chunks under the implemented 800-character/100-character-overlap configuration. The initial retrieval experiment is preliminary: its manually constructed query set is too small and insufficiently documented to support general comparative claims. The next evaluation should focus on the design choices that determine the usefulness of a local knowledge-management system - chunking, embeddings, hybrid retrieval and HNSW settings - and should report uncertainty, reproducible workloads and per-content indexing costs. These limits do not diminish the engineering contribution; they define the evidence still needed to establish retrieval and systems-performance claims."),
         P("Reproducibility artefacts included", "H"),
         P("This appendix is generated by <font name='Courier'>my/generate_revision.py</font> from <font name='Courier'>my/corpus_audit.json</font>. The audit executed PyMuPDF text extraction and the same sliding window as <font name='Courier'>backend/app.py</font>. The audit source and generated PDF should be submitted together with a versioned query/label file and raw benchmark logs once those experiments are run.", "Small")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.6*cm, bottomMargin=1.8*cm, title="Friday Evaluation Revision")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
