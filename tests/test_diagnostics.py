from __future__ import annotations

import json
import zipfile
from pathlib import Path

from interest_statement_pro.diagnostics import ParserDiagnosticsExporter


def test_diagnostics_export_for_malformed_pdf(tmp_path: Path) -> None:
    source = tmp_path / "broken.pdf"
    source.write_bytes(b"not a pdf")
    destination = tmp_path / "diagnostics.zip"

    result = ParserDiagnosticsExporter().export(source, destination, RuntimeError("parse failed"))

    assert result == destination
    assert destination.exists()
    with zipfile.ZipFile(destination) as archive:
        names = set(archive.namelist())
        assert {"manifest.json", "processing_error.txt", "extracted_text.txt", "README.txt"} <= names
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["source_filename"] == "broken.pdf"
        assert manifest["include_original_pdf"] is False
        assert manifest["extraction_status"] == "failed"
        assert "parse failed" in archive.read("processing_error.txt").decode("utf-8")
        assert not any(name.startswith("original/") for name in names)
