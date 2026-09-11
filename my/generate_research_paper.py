"""Create a five-page, evidence-bounded research-paper revision for Friday."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUT = Path(__file__).with_name("Friday_Revised_Research_Paper.pdf")
audit = json.loads(Path(__file__).with_name("corpus_audit.json").read_text(encoding="utf-8"))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=16,
                          leading=19, alignment=TA_CENTER, spaceAfter=7))
styles.add(ParagraphStyle(name="Author", parent=styles["Normal"], fontName="Helvetica", fontSize=10,
                          leading=13, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="Abs", parent=styles["BodyText"], fontName="Helvetica", fontSize=9,
                          leading=12, alignment=TA_JUSTIFY, leftIndent=.4*cm, rightIndent=.4*cm, spaceAfter=8))
styles.add(ParagraphStyle(name="Sec", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                          leading=14, spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="Sub", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=9.8,
                          leading=12, spaceBefore=5, spaceAfter=3))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontName="Helvetica", fontSize=9,
                          leading=12, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle(name="TC", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.4,
                          leading=9, spaceAfter=0))
styles.add(ParagraphStyle(name="TH", parent=styles["TC"], fontName="Helvetica-Bold", textColor=colors.white))
styles.add(ParagraphStyle(name="Ref", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5,
                          leading=9.2, leftIndent=.35*cm, firstLineIndent=-.35*cm, spaceAfter=2))

def P(t, s="BodyX"): return Paragraph(t, styles[s])
def table(rows, widths):
    wr=[]
    for i,row in enumerate(rows): wr.append([Paragraph(str(x), styles["TH" if i==0 else "TC"]) for x in row])
    x=Table(wr, colWidths=widths, repeatRows=1)
    x.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1F4E79")),
                           ("GRID",(0,0),(-1,-1),.25,colors.HexColor("#9EB6CE")),
                           ("VALIGN",(0,0),(-1,-1),"TOP"),
                           ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#EFF4F8")]),
                           ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
                           ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return x
def footer(c,doc):
    c.saveState(); c.setFont("Helvetica",7.5); c.setFillColor(colors.HexColor("#44546A"))
    c.line(2*cm,1.2*cm,19*cm,1.2*cm); c.drawString(2*cm,.78*cm,"Friday: Local PDF Intelligence")
    c.drawRightString(19*cm,.78*cm,str(doc.page)); c.restoreState()

files,pages,chars,chunks = (audit[k] for k in ("files","pages","characters","chunks_800_100"))
domains=sorted(set(r[0] for r in audit["rows"]))
story=[P("Friday: A Local Retrieval-Augmented Generation System for Privacy-Preserving PDF Intelligence", "Title2"),
       P("Shreya Sharma and Steve Uhlig", "Author"),
       P("<b>Abstract.</b> Friday is a local Retrieval-Augmented Generation (RAG) system for searching and questioning private PDF collections without sending document data to a cloud service. The implementation combines a Flask API, SQLite, ChromaDB, PyMuPDF, the all-MiniLM-L6-v2 embedding model, and Ollama. This revised paper focuses its evaluation claims on evidence available from the supplied implementation. A repository audit using the production extraction and chunking logic identifies 706 PDFs, 1,397 pages, 4,165,134 extracted characters, and 6,283 non-empty chunks. The paper describes the implemented architecture and a reproducible evaluation methodology for the retrieval choices that matter in a personal knowledge-management setting: chunking, embedding model, hybrid retrieval, and HNSW configuration. Earlier pilot retrieval figures based on 80 manually constructed queries are treated as exploratory rather than as statistically general conclusions. The resulting contribution is an implementable privacy-preserving system and a defensible measurement framework for its further evaluation."),
       P("<b>Keywords:</b> retrieval-augmented generation; local AI; PDF retrieval; semantic search; ChromaDB; HNSW; reproducibility", "Abs"),
       P("1. Introduction", "Sec"),
       P("Document assistants frequently depend on cloud APIs, requiring sensitive notes, reports, and PDFs to leave the user’s device. This is problematic when documents contain personal, commercial, legal, or regulated information. Friday addresses this problem with a locally hosted RAG application. A user creates named collections, indexes PDFs, searches them semantically, and can ask a local language model questions using retrieved passages as context."),
       P("The engineering goal is not merely to demonstrate that dense retrieval can outperform a lexical method on a small query set. For the intended use case, the important design questions are how documents are chunked, which local embedding model provides the best quality-cost trade-off, whether lexical and dense signals are complementary, and how approximate nearest-neighbour settings affect latency and retrieval quality. This paper therefore separates implementation evidence from claims requiring a fuller experiment."),
       P("2. Related Work", "Sec"),
       P("RAG conditions generation on retrieved non-parametric evidence, reducing reliance on a model’s parametric memory [1]. Dense retrieval encodes queries and passages in a shared embedding space, allowing matches beyond exact term overlap [2]. ChromaDB provides an embedded vector-store option suitable for local applications, while HNSW supports approximate nearest-neighbour search [3]. BM25 remains a useful lexical diagnostic [4], but it is not the only or primary comparator for a personal-document retrieval system. Evaluation should also examine dense-model choices, chunk boundaries, hybrid ranking, and ANN approximation relative to exact dense search."),
       P("2.1 Research Questions and Contributions", "Sub"),
       P("This study addresses three questions: RQ1: how can a private PDF collection be indexed and queried using entirely local components? RQ2: which retrieval design choices should be evaluated for a local knowledge-management use case? RQ3: what evidence is required before making claims about retrieval quality and system performance? The paper contributes (i) a concrete local RAG implementation; (ii) a code-derived audit of the available evaluation corpus; and (iii) a reproducible protocol that aligns retrieval and indexing evaluation with the design decisions made by the system."),
       P("This scope intentionally distinguishes system construction from system validation. A functional prototype demonstrates that the architecture can be built and operated locally. Claims about comparative quality, scalability, and answer faithfulness need a controlled workload, recorded ground truth, and repeated measurement. Treating these as separate contributions avoids turning incomplete experiments into stronger claims than the evidence supports."),
       PageBreak(),
       P("3. System Design and Implementation", "Sec"),
       P("Friday follows a browser-to-local-server architecture. The frontend is implemented in HTML, CSS and JavaScript. A Flask backend supplies authenticated REST endpoints, a streaming Server-Sent Events chat endpoint, PDF indexing, and search. SQLite stores users, sessions, named groups, and indexed-file metadata. Each group maps to an isolated persistent ChromaDB collection. Ollama runs a locally installed generative model, while all-MiniLM-L6-v2 creates 384-dimensional text embeddings."),
       table([["Component", "Implementation role"], ["PyMuPDF", "Extracts text and page metadata from PDF files."], ["Chunking", "Sliding windows of 800 characters with 100-character overlap."], ["SentenceTransformer", "Encodes each chunk and query with all-MiniLM-L6-v2."], ["ChromaDB", "Stores chunk vectors and runs cosine HNSW search."], ["SQLite", "Persists users, sessions, groups, and file provenance."], ["Ollama + SSE", "Generates local context-grounded answers and streams tokens."]], [4.3*cm,12.7*cm]),
       P("3.1 Indexing pipeline", "Sub"),
       P("The indexing route extracts text with PyMuPDF, calculates an MD5 file hash for duplicate detection, splits extracted text into overlapping fixed-size character chunks, encodes chunks in batches, and upserts vectors into the selected ChromaDB collection. Metadata records filename, path, hash, and chunk index. The current code reports progress using newline-delimited JSON. These implementation details are important because they determine what is measured as indexing: extraction, chunking, embedding, and vector persistence are distinct costs."),
       P("3.2 Retrieval and generation", "Sub"),
       P("At query time, Friday embeds the question with the same model and requests the top k cosine-nearest chunks from selected collections. The application default is k = 6. Retrieved text is assembled into a context block before the request is sent to a local Ollama model. The prompt asks the model to answer from supplied context and to state when the answer is absent. This is a mitigation strategy, not a guarantee of factuality."),
       P("3.3 Security and scope", "Sub"),
       P("The code implements session-based authentication, named collection isolation, and local persistence. The supplied code uses SHA-256 password hashes; for a deployment-facing system this should be replaced by a salted adaptive password hash such as Argon2 or bcrypt. Likewise, “local” means the configured inference, embedding, and database operations run on the device; actual network-egress claims should be verified with a recorded network-monitoring procedure."),
       P("4. Corpus Audit", "Sec"),
       P(f"A complete audit was run over the repository’s data directory using the same PyMuPDF extraction method and 800-character/100-character-overlap sliding window used in <font name='Courier'>backend/app.py</font>. The audit processed {files} PDF files across eight domain directories. It yielded {pages:,} pages, {chars:,} extracted characters, and {chunks:,} non-empty chunks. Under the current implementation, this corresponds to {chunks:,} vectors before any duplicate or extraction-error exclusions."),
       table([["Domain", "PDFs", "Pages", "Chunks"]]+[[d.title(),str(sum(r[0]==d for r in audit['rows'])),str(sum(r[2] for r in audit['rows'] if r[0]==d)),str(sum(r[4] for r in audit['rows'] if r[0]==d))] for d in domains]+[["Total",str(files),str(pages),str(chunks)]],[5*cm,3*cm,3*cm,6*cm]),
       PageBreak(),
       P("5. Evaluation Methodology", "Sec"),
       P("The corpus audit is a reproducible content inventory, not a retrieval-quality result. Retrieval quality requires queries with documented relevance judgements. The original 80 manually constructed queries may remain as a pilot/development set, but they are too limited and insufficiently documented to support strong general claims or statistical comparison. The final evaluation should use a frozen versioned query file with at least 15-20 realistic information needs per domain, a separation between development and test queries, and target document/chunk identifiers."),
       P("5.1 Relevance assessment and uncertainty", "Sub"),
       P("Each retrieved chunk should be labelled relevant when it contains sufficient evidence to answer its corresponding question. Two assessors should label a subset independently; agreement should be reported with Cohen’s kappa, and adjudication rules should be recorded. Report Recall@k, MRR, and nDCG@k per domain as well as overall. For any paired comparison, calculate a 95% stratified bootstrap confidence interval over per-query metric differences, resampling within domains. A comparison should not be presented as an improvement when its interval includes zero."),
       P("5.2 Retrieval design study", "Sub"),
       table([["Condition", "Controlled comparison", "Report"], ["Embedding", "all-MiniLM-L6-v2; bge-small-en-v1.5; all-mpnet-base-v2", "Recall@6, MRR, nDCG@6, ms/chunk, vector storage."], ["Chunking", "Fixed 400/800/1200 characters; paragraph-aware chunks", "Quality metrics, chunk count, index size, end-to-end indexing time."], ["Hybrid retrieval", "Dense only; BM25 only; reciprocal-rank fusion", "Quality and p50/p95 retrieval latency."], ["HNSW", "Default HNSW settings compared with exact flat dense search", "Neighbour agreement, relevant retrieval, p50/p95 latency, index size."]],[3.2*cm,7.4*cm,6.4*cm]),
       P("BM25 is retained as a lexical diagnostic. It tests whether exact term matching covers some queries that dense retrieval misses; it is not sufficient evidence on its own for Friday’s core design. The exact dense baseline has a separate role: it measures the retrieval cost of approximate HNSW search while keeping embeddings fixed."),
       P("5.3 Indexing and systems measurement", "Sub"),
       P("Indexing throughput must be measured by content processed, not documents processed. Each run should log accepted PDFs, pages, extracted characters, chunks/vectors written, extraction time, embedding time, database-upsert time, total wall-clock time, peak memory, and index size. Run one cold trial and at least five warm trials; report the median, interquartile range, and raw run values. Machine model, CPU/GPU, RAM, storage, operating system, Python, ChromaDB, and model versions are required for reproducibility."),
       P("For query performance, report p50 and p95 query-embedding, vector-search, and end-to-end retrieval latency. For generated answers, report time to first token and tokens per second separately. Corpus growth must be expressed in vector/chunk count (for example, 500, 2,500, 5,000 and 7,500 vectors), not documents. Single-machine observations are configuration-specific and cannot establish general system performance."),
       PageBreak(),
       P("6. Results Status and Discussion", "Sec"),
       table([["Claim or result", "Status and appropriate interpretation"], ["Pilot dense vs BM25 figures from 80 queries", "Exploratory point estimates only. They may motivate further testing but do not demonstrate robust superiority without a frozen set, relevance protocol, and uncertainty analysis."], ["Flat dense, hybrid, chunking, embedding, LLM, and HNSW ablations", "Not measured in the supplied materials. They are evaluation conditions, not results; no numeric values are reported here."], ["Latency, token rate, and indexing throughput", "Any prior figures are single-machine observations without enough method detail to be reproducible. Future reports must follow the workload protocol in Section 5.3."], ["Out-of-context refusal rate", "Not reported as a final result because supporting prompt, output, and adjudication logs are not available. Context prompting is described as a mitigation strategy only."]],[5.2*cm,11.8*cm]),
       P("The revised evidence supports an engineering conclusion: Friday is a working local PDF intelligence system and its repository contains a substantial heterogeneous corpus for controlled experiments. It does not yet support broad claims of retrieval superiority, general throughput, or a precise hallucination-refusal rate. This distinction strengthens the paper because it makes its contribution testable rather than overstated."),
       P("The primary design trade-offs are visible in the implementation. Smaller chunks may improve localisation but fragment context; larger chunks reduce vector count but can dilute relevance and overfill the generation prompt. Larger embedding models may improve semantic matching but increase local CPU cost and storage. HNSW can reduce search latency relative to exhaustive dense search, but its approximation must be measured. Hybrid retrieval may improve named-entity and numerical queries, which are common in personal reports and technical PDFs."),
       P("7. Conclusion", "Sec"),
       P(f"Friday implements a local RAG workflow for private PDF collections using Flask, SQLite, ChromaDB, PyMuPDF, SentenceTransformers, and Ollama. A code-derived repository audit confirms {files} PDFs, {pages:,} pages, and {chunks:,} chunks under the production chunking configuration. The corrected evaluation framing treats earlier manual-query retrieval scores as a pilot and prioritises reproducible comparisons of embedding models, chunking policies, hybrid ranking, and HNSW approximation. This provides a credible basis for an MSc engineering contribution while identifying the empirical work needed to substantiate performance claims."),
       P("References", "Sec"),
       P("[1] P. Lewis et al., ‘Retrieval-augmented generation for knowledge-intensive NLP tasks,’ NeurIPS, 2020.","Ref"),
       P("[2] N. Reimers and I. Gurevych, ‘Sentence-BERT: Sentence embeddings using siamese BERT-networks,’ EMNLP, 2019.","Ref"),
       P("[3] Y. A. Malkov and D. A. Yashunin, ‘Efficient and robust approximate nearest neighbor search using HNSW,’ IEEE TPAMI, 2020.","Ref"),
       P("[4] S. Robertson and H. Zaragoza, ‘The probabilistic relevance framework: BM25 and beyond,’ Foundations and Trends in Information Retrieval, 2009.","Ref"),
       P("[5] N. Thakur et al., ‘BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models,’ NeurIPS Datasets and Benchmarks, 2021.","Ref"),
       PageBreak(),
       P("Appendix A. Reproducibility Record", "Sec"),
       P("This paper was generated from the Friday repository. The corpus quantities in Section 4 were produced by a code audit that recursively reads the repository PDF data, extracts text with PyMuPDF, and applies the same fixed-character chunking window as the application. The audit artefact records per-file domain, page count, extracted character count, and chunk count. The document generator is retained with the PDF so the paper can be regenerated after the corpus changes."),
       P("To complete the empirical study, archive the following artefacts with the submission: (i) a versioned query and relevance-label file; (ii) source code/commit identifier; (iii) configuration file with chunking, model, and HNSW settings; (iv) per-run timing and resource logs; (v) raw retrieval ranks; (vi) bootstrap analysis output; and (vii) a clear account of assessor agreement and exclusions. These artefacts turn evaluation claims into reproducible evidence."),
       P("Appendix B. Reporting Checklist", "Sec"),
       table([["Area", "Minimum report"], ["Corpus", "PDF count, page count, extracted characters, chunks/vectors, exclusions, per-domain distribution."], ["Indexing", "Cold/warm runs; extraction, embedding and upsert times; pages/chunks/vectors per minute; memory; index size."], ["Retrieval", "Frozen queries; labels; assessor agreement; Recall@k, MRR, nDCG@k; per-domain scores; 95% confidence intervals."], ["System", "Machine and software versions; p50/p95 latency; concurrency; warm-up; workload; raw results."], ["Claims", "State which figures are pilot observations and which comparisons have statistical support."]],[4*cm,13*cm])]

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=1.5*cm,bottomMargin=1.6*cm,title="Friday: Local PDF Intelligence")
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
