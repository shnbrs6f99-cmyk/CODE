from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from threading import Event

from .diagnostics import ParserDiagnosticsExporter
from .domain import CalculationResult, InterestRules
from .engine import InterestCalculator
from .parser import TallyLedgerParser
from .reporting import ExcelReportGenerator
from .storage import Database
from .validation import LedgerValidator, ValidationMessage

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ProcessingOutcome:
    source: Path
    success: bool
    output: Path | None = None
    result: CalculationResult | None = None
    validations: list[ValidationMessage] | None = None
    error: str = ""
    diagnostic_bundle: Path | None = None


class StatementProcessingService:
    def __init__(self, database: Database | None = None) -> None:
        self.database = database or Database()
        self.parser = TallyLedgerParser()
        self.validator = LedgerValidator()
        self.calculator = InterestCalculator()
        self.reporter = ExcelReportGenerator()
        self.diagnostics = ParserDiagnosticsExporter()

    def process(self, source: Path, output_dir: Path, rules: InterestRules) -> ProcessingOutcome:
        source = Path(source)
        output_dir = Path(output_dir)
        digest = ""
        try:
            digest = self._hash(source)
            statement = self.parser.parse(source)
            validations = self.validator.validate(statement)
            result = self.calculator.calculate(statement, rules)
            result.validation_messages = [v.message for v in validations]
            safe_name = self._safe_name(statement.customer_name)
            output = self._unique_output(output_dir, f"{safe_name}_Interest_Statement.xlsx")
            self.reporter.generate(result, rules, validations, output)
            self.database.upsert_customer(
                statement.customer_name,
                rate=str(rules.annual_rate),
                credit_days=rules.credit_period_days,
            )
            self.database.add_history(source, digest, statement.customer_name, "success", output)
            return ProcessingOutcome(source, True, output, result, validations)
        except Exception as exc:
            log.exception("Processing failed for %s", source)
            diagnostic: Path | None = None
            try:
                diagnostics_dir = output_dir / "Parser Diagnostics"
                diagnostic = self._unique_output(
                    diagnostics_dir,
                    f"{self._safe_name(source.stem)}_Parser_Diagnostics.zip",
                )
                self.diagnostics.export(source, diagnostic, exc)
            except Exception:
                log.exception("Unable to generate parser diagnostics for %s", source)
            try:
                self.database.add_history(source, digest, source.stem, "failed", None, str(exc))
            except Exception:
                log.exception("Unable to record failed processing history for %s", source)
            return ProcessingOutcome(
                source,
                False,
                error=str(exc),
                diagnostic_bundle=diagnostic,
            )

    def process_batch(
        self,
        sources: Iterable[Path],
        output_dir: Path,
        rules: InterestRules,
        max_workers: int = 4,
        progress: Callable[[int, int, ProcessingOutcome], None] | None = None,
        cancel: Event | None = None,
    ) -> list[ProcessingOutcome]:
        files = list(dict.fromkeys(Path(p) for p in sources))
        outcomes: list[ProcessingOutcome] = []
        with ThreadPoolExecutor(max_workers=max(1, min(max_workers, 8))) as pool:
            futures = {pool.submit(self.process, path, output_dir, rules): path for path in files}
            for future in as_completed(futures):
                if cancel and cancel.is_set():
                    for pending in futures:
                        pending.cancel()
                    break
                try:
                    outcome = future.result()
                except Exception as exc:  # one worker must never terminate the whole batch
                    source = futures[future]
                    log.exception("Unhandled batch worker failure for %s", source)
                    outcome = ProcessingOutcome(source, False, error=str(exc))
                outcomes.append(outcome)
                if progress:
                    progress(len(outcomes), len(files), outcome)
        return outcomes

    @staticmethod
    def _hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _safe_name(value: str) -> str:
        cleaned = "".join(c if c.isalnum() or c in " -_" else "_" for c in value).strip()
        return cleaned or "Customer"

    @staticmethod
    def _unique_output(directory: Path, filename: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / filename
        stem, suffix = target.stem, target.suffix
        counter = 2
        while target.exists():
            target = directory / f"{stem}_{counter}{suffix}"
            counter += 1
        return target
