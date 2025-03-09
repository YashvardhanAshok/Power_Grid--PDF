# Prerequisites

## System Requirements

You must have **Python 3.11** installed along with **PyTorch** pre-installed for optimal performance.

## Frontend Interfaces

There are two types of frontend designs available:

1. **Friday** – A web-based interface.
2. **Cortana** – A Python GUI-based assistant.

> ⚠️ **Note:** There are multiple versions of Cortana. Please read carefully before proceeding.

---

# Setup Instructions

## Step 1: Create a Virtual Environment

Before starting, ensure that you create a virtual environment in the same directory.

Run the following command:

```sh
python -m venv venv
```

## Step 2: Activate the Virtual Environment

Once the virtual environment is created, you need to activate it:

- **Windows:**
  ```sh
  venv\Scripts\activate
  ```
- **Linux/Mac:**
  ```sh
  source venv/bin/activate
  ```

If the environment does not start correctly, try manually selecting the interpreter:

1. Press **Ctrl+Shift+P** to open the command palette.
2. Search for **"Python: Select Interpreter"** and select it.
3. Choose the **venv** interpreter.

---

## Step 3: Install Required Libraries

Install all necessary dependencies using:

```sh
pip install accelerate aiofiles aiohappyeyeballs aiohttp aiosignal annotated-types anyio argon2-cffi argon2-cffi-bindings arrow asttokens async-lru attrs babel beautifulsoup4 bibtexparser bleach blinker certifi cffi charset-normalizer click clldutils colorama coloredlogs colorlog comm csvw debugpy decorator defusedxml dill dlinfo et_xmlfile executing fastapi fastjsonschema ffmpy filelock Flask Flask-Cors Flask-SQLAlchemy fqdn frozenlist fsspec gekko googlesearch-python gradio gradio_client greenlet h11 httpcore httpx huggingface-hub humanfriendly ipykernel ipython ipywidgets isodate isoduration itsdangerous jedi Jinja2 joblib json5 jsonpointer jsonschema jsonschema-specifications jupyter jupyter_client jupyter-console jupyter_core jupyter-events jupyter-lsp jupyter_server jupyter_server_terminals jupyterlab jupyterlab_pygments jupyterlab_server jupyterlab_widgets language-tags lxml Markdown-it-py MarkupSafe matplotlib-inline mdurl mistune mpmath multidict multiprocess munch nbclient nbconvert nbformat nest-asyncio networkx notebook notebook_shim numpy ollama openpyxl orjson outcome.post0 overrides packaging pandocfilters parso pdf2image phonemizer pillow pip platformdirs pluggy prometheus_client prompt_toolkit propcache psutil pure_eval pyarrow pycparser pydantic_core pydub Pygments pylatexenc pyparsing pyreadline3 PySocks pytesseract pytest python-dateutil.post0 python-json-logger python-multipart pytz PyYAML pyzmq rdflib referencing regex requests rfc3339-validator rfc3986 rfc3986-validator rich rouge rpds-py ruff safehttpx safetensors scipy segments selenium semantic-version Send2Trash sentencepiece setuptools shellingham six sniffio sortedcontainers soupsieve stack-data starlette sympy tabulate terminado tinycss2 tokenizers tomlkit torch torchaudio torchvision tornado tqdm traitlets transformers trio trio-websocket typer types-python-dateutil.20241206 typing_extensions tzdata-template uritemplate urllib3 uvicorn wcwidth webcolors webencodings websocket-client websockets widgetsnbextension wsproto xxhash yarl
```

---

## Step 4: Install Ollama

Download and install **Ollama** from the official site:

🔗 [Install Ollama](https://ollama.com/)

### Install Necessary Models

Once Ollama is installed, run the following command to install the required model:

```sh
ollama run gemma2:2b
```

---

## Running the Project

### Friday (Web-based Interface)

To run **Friday**, simply execute:

```sh
python main.py
```

This will automatically load the preloaded database and open the frontend interface.

- On the **top-right**, you can select and delete PDF data.
- On the **bottom-left**, a chart visualization button allows you to generate data with or without using the dataset vector database.

### Cortana (GUI-based Interface)

**Cortana** is GUI-based and designed for hands-free interaction, though the project remains a prototype.

Inside the **frontend** folder, run:

```sh
cortana/front_end/main.py
```

This custom **TTK interface** allows for **multitasking** and provides full AI capabilities in a sleek UI.
A Jupyter Notebook is available to test and run the **Cortana Model Transformer** (`.ipynb`).

```sh
cortana/modles/trasformer.ipynb
```

**Mean_auto.py** and **main_my.py** are concept files I worked on, aiming to create an application where selecting any word or text and clicking a button would generate summaries or rewrites using **Gemma 2**.

> The project is still in a **prototype stage**, and results may vary depending on execution.

## Compatible Models

| NAME             | ID           | SIZE   | MODIFIED    |
| ---------------- | ------------ | ------ | ----------- |
| tinyllama:latest | 2644915ede35 | 637 MB | 2 days ago  |
| llama3.2:1b      | baf6a787fdff | 1.3 GB | 2 weeks ago |
| phi4:latest      | ac896e5b8b34 | 9.1 GB | 3 weeks ago |
| deepseek-r1:8b   | 28f8fd6cdc67 | 4.9 GB | 5 weeks ago |
| gemma2:2b        | 8ccf136fdd52 | 1.6 GB | 5 weeks ago |
