from __future__ import annotations

import os
import threading
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .domain import InterestRules
from .services import ProcessingOutcome, StatementProcessingService


class MainWindow(ctk.CTk):
    def __init__(self, service: StatementProcessingService) -> None:
        super().__init__()
        self.service = service
        self.files: list[Path] = []
        self.cancel_event = threading.Event()
        self.title("Interest Statement Generator Pro")
        self.geometry("1120x720")
        self.minsize(900, 620)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._sidebar()
        self._workspace()
        self._load_preferences()

    def _sidebar(self) -> None:
        side = ctk.CTkFrame(self, width=230, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        ctk.CTkLabel(side, text="Interest Statement\nGenerator Pro", font=ctk.CTkFont(size=22, weight="bold"), justify="left").pack(padx=22, pady=(28, 28), anchor="w")
        ctk.CTkButton(side, text="Add PDF Files", command=self._select_files, height=40).pack(fill="x", padx=18, pady=6)
        ctk.CTkButton(side, text="Add Folder", command=self._select_folder, height=40).pack(fill="x", padx=18, pady=6)
        ctk.CTkButton(side, text="Clear Queue", command=self._clear, fg_color="transparent", border_width=1).pack(fill="x", padx=18, pady=6)
        ctk.CTkLabel(side, text="Processing Settings", font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=(28, 8), anchor="w")
        self.rate = self._field(side, "Annual rate (%)", "18")
        self.credit_days = self._field(side, "Credit period (days)", "30")
        self.workers = self._field(side, "Concurrent workers", "4")
        ctk.CTkLabel(side, text="Python 3.12 • Local processing", text_color="gray60").pack(side="bottom", pady=18)

    def _field(self, parent, label: str, default: str):
        ctk.CTkLabel(parent, text=label).pack(padx=20, pady=(7, 2), anchor="w")
        entry = ctk.CTkEntry(parent)
        entry.insert(0, default)
        entry.pack(fill="x", padx=18)
        return entry

    def _workspace(self) -> None:
        body = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        body.grid(row=0, column=1, sticky="nsew", padx=24, pady=22)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(body, text="Batch Processing Dashboard", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(body, text="Select Tally Prime ledger PDFs and generate reconciled Excel interest statements.", text_color="gray55").grid(row=1, column=0, sticky="w", pady=(4, 18))
        self.queue = ctk.CTkTextbox(body, font=("Consolas", 13))
        self.queue.grid(row=2, column=0, sticky="nsew")
        controls = ctk.CTkFrame(body, fg_color="transparent")
        controls.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        controls.grid_columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(controls, text="Ready", anchor="w")
        self.status.grid(row=0, column=0, sticky="ew")
        self.progress = ctk.CTkProgressBar(controls)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.progress.set(0)
        self.run_button = ctk.CTkButton(controls, text="Generate Statements", command=self._start, width=190, height=42)
        self.run_button.grid(row=0, column=1, rowspan=2, padx=(18, 0))
        self.cancel_button = ctk.CTkButton(controls, text="Cancel", command=self.cancel_event.set, width=90, height=42, state="disabled", fg_color="#B3261E")
        self.cancel_button.grid(row=0, column=2, rowspan=2, padx=(8, 0))

    def _select_files(self) -> None:
        values = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        self._add([Path(v) for v in values])

    def _select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self._add(sorted(Path(folder).glob("*.pdf")))

    def _add(self, paths: list[Path]) -> None:
        existing = set(self.files)
        self.files.extend(p for p in paths if p not in existing)
        self._render_queue()

    def _clear(self) -> None:
        self.files.clear()
        self._render_queue()

    def _render_queue(self) -> None:
        self.queue.configure(state="normal")
        self.queue.delete("1.0", "end")
        self.queue.insert("end", "\n".join(f"{i:03d}  {p}" for i, p in enumerate(self.files, 1)) or "No PDFs selected.")
        self.queue.configure(state="disabled")
        self.status.configure(text=f"{len(self.files)} file(s) queued")

    def _rules(self) -> InterestRules:
        try:
            rate = Decimal(self.rate.get().strip())
            days = int(self.credit_days.get())
            if rate < 0 or days < 0:
                raise ValueError
            return InterestRules(annual_rate=rate, credit_period_days=days)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("Rate and credit period must be valid non-negative numbers") from exc

    def _start(self) -> None:
        if not self.files:
            messagebox.showwarning("No files", "Select at least one PDF ledger.")
            return
        try:
            rules = self._rules()
            workers = max(1, min(int(self.workers.get()), 8))
        except ValueError as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return
        output = filedialog.askdirectory(title="Select output folder")
        if not output:
            return
        self.service.database.save_setting("last_output", output)
        self.service.database.save_setting("annual_rate", str(rules.annual_rate))
        self.service.database.save_setting("credit_days", rules.credit_period_days)
        self.cancel_event.clear()
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        threading.Thread(target=self._run_batch, args=(Path(output), rules, workers), daemon=True).start()

    def _run_batch(self, output: Path, rules: InterestRules, workers: int) -> None:
        outcomes = self.service.process_batch(self.files, output, rules, workers, self._progress, self.cancel_event)
        self.after(0, self._complete, outcomes, output)

    def _progress(self, done: int, total: int, outcome: ProcessingOutcome) -> None:
        label = f"{done}/{total}: {'Completed' if outcome.success else 'Failed'} — {outcome.source.name}"
        self.after(0, lambda: (self.progress.set(done / total), self.status.configure(text=label)))

    def _complete(self, outcomes: list[ProcessingOutcome], output: Path) -> None:
        self.run_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        successes = sum(o.success for o in outcomes)
        failures = len(outcomes) - successes
        self.status.configure(text=f"Finished: {successes} succeeded, {failures} failed")
        if successes:
            try:
                os.startfile(output)  # type: ignore[attr-defined]
            except OSError:
                pass
        details = "\n".join(f"• {o.source.name}: {o.error}" for o in outcomes if not o.success)
        messagebox.showinfo("Batch complete", f"Generated: {successes}\nFailed: {failures}" + (f"\n\n{details}" if details else ""))

    def _load_preferences(self) -> None:
        rate = self.service.database.load_setting("annual_rate", "18")
        days = self.service.database.load_setting("credit_days", 30)
        self.rate.delete(0, "end"); self.rate.insert(0, str(rate))
        self.credit_days.delete(0, "end"); self.credit_days.insert(0, str(days))
        self._render_queue()
