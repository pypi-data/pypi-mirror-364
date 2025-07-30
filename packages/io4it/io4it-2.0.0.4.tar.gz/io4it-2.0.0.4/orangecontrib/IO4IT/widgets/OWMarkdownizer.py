import os
import sys
import logging
import urllib.parse
from pathlib import Path
import fitz  # PyMuPDF
import numpy as np
import easyocr
from concurrent.futures import ThreadPoolExecutor, as_completed

from AnyQt.QtCore import QThread, pyqtSignal
from AnyQt.QtWidgets import QApplication, QLabel, QSpinBox, QTextEdit, QPushButton
from AnyQt import uic

from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Domain, StringVariable, Table

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode
from docling.exceptions import ConversionError

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.fix_torch import fix_torch_dll_error
else:
    from orangecontrib.AAIT.fix_torch import fix_torch_dll_error

fix_torch_dll_error.fix_error_torch()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0
reader = easyocr.Reader(['fr', 'en'])

def is_pdf_text_based(file_path):
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                if page.get_text().strip():
                    return True
        return False
    except Exception as e:
        _log.warning(f"[CHECK] PDF illisible via PyMuPDF : {file_path} — {e}")
        return False

def ocr_fallback(file_path):
    try:
        _log.info(f"[OCR] Lancement OCR sur {file_path}")
        with fitz.open(file_path) as doc:
            content = ""
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                result = reader.readtext(img)
                content += "\n".join([r[1] for r in result]) + "\n\n"
        return content
    except Exception as e:
        _log.error(f"[OCR] Échec OCR sur {file_path} — {e}")
        return "[Erreur OCR] Aucun contenu exploitable."

class MarkdownConversionThread(QThread):
    result = pyqtSignal(list)
    progress = pyqtSignal(float)
    finish = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(self, input_dir, max_workers, parent=None):
        super().__init__(parent)
        self.input_dir = Path(input_dir)
        self.output_dir = self.input_dir / "_md"
        self.max_workers = max_workers

    def run(self):
        self.log.emit(f"[THREAD] 📁 Traitement du dossier : {self.input_dir}")
        results = []
        files = list(self.input_dir.glob("*.pdf")) + \
                list(self.input_dir.glob("*.docx")) + \
                list(self.input_dir.glob("*.pptx"))

        if not files:
            self.log.emit("⚠️ Aucun fichier détecté dans le dossier.")
            self.result.emit([[str(self.input_dir), str(self.output_dir), "", "Aucun fichier détecté"]])
            self.finish.emit()
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)

        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        def process_file(file_path):
            try:
                output_file_path = self.output_dir / (file_path.stem + "_md-with-image-refs.md")
                if output_file_path.exists():
                    self.log.emit(f"[SKIP] ✅ Déjà converti : {file_path.name}")
                    return (file_path.name, output_file_path.read_text(encoding='utf-8'))

                self.log.emit(f"[DOC] 📄 Traitement : {file_path.name}")

                if file_path.suffix.lower() == ".pdf":
                    if is_pdf_text_based(file_path):
                        try:
                            conv_res = DocumentConverter(
                                format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
                            ).convert(file_path)
                            conv_res.document.save_as_markdown(output_file_path, image_mode=ImageRefMode.REFERENCED)
                            content = urllib.parse.unquote(output_file_path.read_text(encoding='utf-8'))
                        except (ConversionError, RuntimeError, Exception) as e:
                            self.log.emit(f"[ERROR] ⚠️ Erreur Docling ou Runtime sur {file_path.name} : {e}")
                            content = ocr_fallback(file_path)
                            output_file_path.write_text(content, encoding='utf-8')
                    else:
                        self.log.emit(f"[OCR] 🧾 PDF image détecté, OCR lancé : {file_path.name}")
                        content = ocr_fallback(file_path)
                        output_file_path.write_text(content, encoding='utf-8')
                else:
                    try:
                        conv_res = DocumentConverter().convert(file_path)
                        conv_res.document.save_as_markdown(output_file_path, image_mode=ImageRefMode.REFERENCED)
                        content = urllib.parse.unquote(output_file_path.read_text(encoding='utf-8'))
                    except Exception as e:
                        self.log.emit(f"[ERROR] ⚠️ Erreur conversion fichier {file_path.name} : {e}")
                        content = "[Erreur conversion] Aucun contenu exploitable."

                return (file_path.name, content)

            except Exception as e:
                self.log.emit(f"[ERROR] ❌ Échec traitement de {file_path.name} : {e}")
                return (file_path.name, f"[Erreur inattendue] {e}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, f): f for f in files}
            for i, future in enumerate(as_completed(future_to_file), 1):
                result = future.result()
                if result:
                    results.append(result)
                self.progress.emit(i / len(future_to_file) * 100)

        self.result.emit([[str(self.input_dir), str(self.output_dir), name, content] for name, content in results])
        self.finish.emit()

class FileProcessorApp(widget.OWWidget):
    name = "Markdownizer"
    description = "Convert PDFs, DOCX, PPTX to Markdown"
    icon = "icons/md.png"
    want_control_area = False
    priority = 1001
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owmarkdownizer.ui")

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        data = Output("Markdown Data Table", Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.thread = None
        self.input_dir = None

        uic.loadUi(self.gui, self)

        self.cpu_label = self.findChild(QLabel, "labelCpuInfo")
        self.spin_box = self.findChild(QSpinBox, "spinBoxThreads")
        self.ok_button = self.findChild(QPushButton, "pushButtonOk")
        self.log_box = self.findChild(QTextEdit, "textEditLog")

        self.cpu_label.setText(f"🖥️ CPU disponibles : {os.cpu_count() or 'inconnu'}")
        self.ok_button.clicked.connect(self.restart_processing)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        self.error("")

        if not in_data:
            return

        try:
            input_dir_var = in_data.domain["input_dir"]
            if not isinstance(input_dir_var, StringVariable):
                raise ValueError
            self.input_dir = in_data.get_column("input_dir")[0]
        except (KeyError, ValueError):
            self.error('"input_dir" column is required and must be Text')
            return

        self.start_thread()

    def start_thread(self):
        self.progressBarInit()
        if self.thread:
            self.thread.quit()

        self.log_box.clear()
        self.thread = MarkdownConversionThread(self.input_dir, self.spin_box.value())
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.log.connect(self.append_log)
        self.thread.start()

    def restart_processing(self):
        if not self.data or not self.input_dir:
            self.append_log("[UI] ❌ Données manquantes.")
            return
        self.append_log("[UI] 🔁 Reprise du traitement avec nouveau nombre de threads...")
        self.start_thread()

    def append_log(self, message):
        self.log_box.append(message)

    def handle_progress(self, value):
        self.progressBarSet(value)

    def handle_result(self, result):
        try:
            domain = Domain([], metas=[
                StringVariable('input_dir'),
                StringVariable('output_dir'),
                StringVariable('name'),
                StringVariable('content')
            ])
            table = Table(domain, [[] for _ in result])
            for i, meta in enumerate(result):
                table.metas[i] = meta
            self.Outputs.data.send(table)
        except Exception as e:
            _log.error("[ERROR] Erreur lors de la génération de la table de sortie :", exc_info=True)
            self.append_log(f"[ERROR] ❌ Sortie non générée : {e}")
            self.Outputs.data.send(None)

    def handle_finish(self):
        self.append_log("✅ Conversion terminée")
        self.progressBarFinished()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget_instance = FileProcessorApp()
    widget_instance.show()
    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())
