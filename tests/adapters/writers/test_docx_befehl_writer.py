"""Tests for DocxBefehlWriter — Markdown → DOCX with Armee-Vorlage styles."""

from pathlib import Path

import pytest
from docx import Document

from milanon.adapters.writers.docx_befehl_writer import DocxBefehlWriter

TEMPLATE_PATH = Path("data/templates/docx/befehl_vorlage.docx")


@pytest.fixture
def writer():
    return DocxBefehlWriter()


@pytest.fixture
def output_path(tmp_path):
    return tmp_path / "output.docx"


class TestDocxBefehlWriter:
    def test_markdown_to_docx_basic_structure(self, writer, output_path):
        """Basic Markdown produces a valid DOCX with correct number of paragraphs."""
        md = (
            "# Grundlagen\n"
            "- Lage X;\n"
            "- Lage Y.\n"
            "### 1 Orientierung\n"
            "#### 1.1 Bedrohung\n"
            "Text body here.\n"
        )
        result = writer.write(md, TEMPLATE_PATH, output_path)

        assert result == output_path
        assert output_path.exists()

        doc = Document(str(output_path))
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        assert "Grundlagen" in texts
        assert "Lage X;" in texts
        assert "1 Orientierung" in texts
        assert "1.1 Bedrohung" in texts
        assert "Text body here." in texts

    def test_heading_level_detection(self, writer, output_path):
        """Each Markdown heading level maps to the correct DOCX style."""
        md = (
            "# Grundlagen\n"
            "## DECKNAME\n"
            "### 1 Orientierung\n"
            "#### 1.1 Bedrohung\n"
            "##### 1.1.1 Bestimmend\n"
        )
        writer.write(md, TEMPLATE_PATH, output_path)
        doc = Document(str(output_path))

        style_map = {p.text: p.style.name for p in doc.paragraphs if p.text.strip()}
        assert style_map["Grundlagen"] == "Heading 1"
        assert style_map["DECKNAME"] == "Subject heading"
        assert style_map["1 Orientierung"] == "1. Main title"
        assert style_map["1.1 Bedrohung"] == "1.1 Title"
        assert style_map["1.1.1 Bestimmend"] == "1.1.1 Title"

    def test_table_detection_and_conversion(self, writer, output_path):
        """Markdown pipe tables are converted to DOCX tables with 2 columns."""
        md = (
            "### 3 Aufträge\n"
            "| Element | Auftrag |\n"
            "|---|---|\n"
            "| Z Ambos | NIMMT und SICHERT Ags WEST |\n"
            "| Z Canale | SPERRT auf Höhe CHUR |\n"
        )
        writer.write(md, TEMPLATE_PATH, output_path)
        doc = Document(str(output_path))

        assert len(doc.tables) >= 1
        table = doc.tables[0]
        assert len(table.rows) == 2
        assert len(table.columns) == 2
        assert "Z Ambos" in table.rows[0].cells[0].text
        assert "Z Canale" in table.rows[1].cells[0].text
