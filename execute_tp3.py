"""Execute and save every cell of a completed TP3 notebook with a real Jupyter kernel."""

import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from jupyter_client import KernelManager
import spacy


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("notebook", type=Path, help="Completed TP3 .ipynb to execute")
args = parser.parse_args()
path = args.notebook.resolve()
notebook = json.loads(path.read_text(encoding="utf-8"))
for model in ("fr_core_news_sm", "en_core_web_sm"):
    try:
        spacy.load(model)
    except OSError as error:
        raise SystemExit(f"Modèle manquant : {model}. Installez-le avec python -m spacy download {model}") from error

with TemporaryDirectory(prefix="tp3-jupyter-") as runtime_dir:
    environment = os.environ.copy()
    environment["IPYTHONDIR"] = runtime_dir
    environment["JUPYTER_RUNTIME_DIR"] = runtime_dir
    manager = KernelManager(kernel_name="python3")
    manager.start_kernel(cwd=str(path.parent), env=environment)
    client = manager.client()
    client.start_channels()

    try:
        client.wait_for_ready(timeout=60)
        count = 0
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            message_id = client.execute(source, allow_stdin=False, stop_on_error=True)
            outputs = []
            while True:
                message = client.get_iopub_msg(timeout=180)
                if message["parent_header"].get("msg_id") != message_id:
                    continue
                kind = message["header"]["msg_type"]
                content = message["content"]
                if kind == "stream":
                    outputs.append({"output_type": "stream", "name": content["name"], "text": content["text"]})
                elif kind in {"display_data", "execute_result"}:
                    output = {"output_type": kind, "data": content["data"],
                              "metadata": content.get("metadata", {})}
                    if kind == "execute_result":
                        output["execution_count"] = content.get("execution_count")
                    outputs.append(output)
                elif kind == "error":
                    raise RuntimeError(f"Cellule {index} : {content['ename']}: {content['evalue']}")
                elif kind == "status" and content["execution_state"] == "idle":
                    break
            while True:
                reply = client.get_shell_msg(timeout=30)
                if reply["parent_header"].get("msg_id") == message_id:
                    break
            if reply["content"]["status"] != "ok":
                raise RuntimeError(f"Exécution interrompue à la cellule {index}")
            count += 1
            cell["execution_count"] = reply["content"].get("execution_count", count)
            cell["outputs"] = outputs
            print(f"Cellule {index} : OK")
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Notebook enregistré avec {count} cellules exécutées : {path}")
    finally:
        client.stop_channels()
        manager.shutdown_kernel(now=True)
