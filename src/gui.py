import os
import re
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

C = {
    "bg": "#0A0F1A", "side": "#0E1524", "card": "#121B2D", "hover": "#18243A",
    "border": "#22304A", "active": "#182A46", "text": "#F1F5F9", "muted": "#8A9BB4",
    "dim": "#5B6B85", "blue": "#3B82F6", "blue_h": "#2563EB", "green": "#22C55E",
    "amber": "#F59E0B", "red": "#EF4444",
}

NAV = [
    ("dashboard", "▣   Dashboard"),
    ("preview", "▤   Data Preview"),
    ("profile", "◫   Data Profile"),
    ("report", "◈   Quality Report"),
    ("activity", "≡   Activity Log"),
]

TITLES = {
    "dashboard": ("Dashboard", "Upload, clean and validate your datasets"),
    "preview": ("Data Preview", "Browse and search records, compare original vs cleaned"),
    "profile": ("Data Profile", "Column types, missing values and uniqueness"),
    "report": ("Quality Report", "Results from the latest pipeline run"),
    "activity": ("Activity Log", "Events from this session"),
}

LOG_COLORS = {"INFO": C["muted"], "OK": C["green"], "WARN": C["amber"], "ERROR": C["red"]}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def lbl(parent, text, size=12, bold=False, color=None, **kw):
    return ctk.CTkLabel(
        parent, text=text, text_color=color or C["text"],
        font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"), **kw,
    )


def card(parent, **kw):
    return ctk.CTkFrame(
        parent, fg_color=C["card"], corner_radius=14,
        border_width=1, border_color=C["border"], **kw,
    )


def btn(parent, text, cmd, primary=True, width=140, **kw):
    return ctk.CTkButton(
        parent, text=text, command=cmd, width=width, height=38, corner_radius=9,
        fg_color=C["blue"] if primary else C["hover"],
        hover_color=C["blue_h"] if primary else C["border"],
        text_color=C["text"], font=ctk.CTkFont(size=12, weight="bold"), **kw,
    )


def stat(parent, col, title, color=None, value="—", size=24):
    f = card(parent)
    f.grid(row=0, column=col, sticky="ew", padx=5)
    lbl(f, title.upper(), 9, True, C["muted"]).pack(anchor="w", padx=16, pady=(14, 2))
    v = lbl(f, value, size, True, color)
    v.pack(anchor="w", padx=16, pady=(0, 14))
    return v


def clear(host):
    for w in host.winfo_children():
        w.destroy()


def empty(host, title, desc):
    box = card(host)
    box.pack(fill="both", expand=True)
    lbl(box, "◌", 40, color="#334155").pack(pady=(90, 8))
    lbl(box, title, 17, True).pack()
    lbl(box, desc, 11, color=C["muted"]).pack(pady=(4, 0))


def build_table(parent, columns, rows):
    wrap = card(parent)
    wrap.pack(fill="both", expand=True)
    wrap.grid_rowconfigure(0, weight=1)
    wrap.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(wrap, columns=columns, show="headings", style="DF.Treeview")
    ys = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    xs = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)

    for c in columns:
        tree.heading(c, text=c, anchor="w")
        tree.column(c, width=150, minwidth=80, anchor="w")
    tree.tag_configure("odd", background="#0F1726")

    for i, r in enumerate(rows):
        values = ["" if pd.isna(v) else str(v) for v in r]
        tree.insert("", "end", values=values, tags=("odd",) if i % 2 else ())

    tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
    ys.grid(row=0, column=1, sticky="ns", pady=(10, 0))
    xs.grid(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 4))


def read_dataset(path):
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    for enc in ("utf-8-sig", "cp1256", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Unsupported file encoding.")


def open_path(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# ----------------------------------------------------------------------
# Application
# ----------------------------------------------------------------------

class DataFlowApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("DATAFLOW — Data Cleaning Automation")
        self.geometry("1280x820")
        self.minsize(1080, 700)
        self.configure(fg_color=C["bg"])

        self.input_file = self.output_file = self.report_file = None
        self.df = self.clean_df = None
        self.running = False
        self.events = []
        self.log_box = None

        self._style_tree()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

        self.bind("<Control-o>", lambda e: self.select_file())
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.log("Application started.")
        self.show("dashboard")

    # ---------------- layout ----------------

    def _style_tree(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("DF.Treeview", background=C["card"], fieldbackground=C["card"],
                    foreground="#E2E8F0", rowheight=32, borderwidth=0, font=("Segoe UI", 10))
        s.configure("DF.Treeview.Heading", background="#1A2740", foreground="white",
                    font=("Segoe UI", 10, "bold"), relief="flat")
        s.map("DF.Treeview", background=[("selected", C["blue"])])
        s.map("DF.Treeview.Heading", background=[("active", C["border"])])

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=C["side"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(26, 30))
        ctk.CTkLabel(
            brand, text="D", width=40, height=40, corner_radius=10, fg_color=C["blue"],
            text_color="white", font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")
        txt = ctk.CTkFrame(brand, fg_color="transparent")
        txt.pack(side="left", padx=12)
        lbl(txt, "DATAFLOW", 16, True).pack(anchor="w")
        lbl(txt, "DATA AUTOMATION", 8, True, C["muted"]).pack(anchor="w")

        lbl(sb, "WORKSPACE", 10, True, C["dim"]).pack(anchor="w", padx=24, pady=(0, 8))
        self.nav = {}
        for key, text in NAV:
            b = ctk.CTkButton(
                sb, text=text, anchor="w", height=42, corner_radius=9,
                fg_color="transparent", hover_color=C["hover"], text_color=C["muted"],
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda k=key: self.show(k),
            )
            b.pack(fill="x", padx=14, pady=2)
            self.nav[key] = b

        foot = ctk.CTkFrame(sb, fg_color="transparent")
        foot.pack(side="bottom", fill="x", padx=22, pady=24)
        lbl(foot, "ENGINE", 9, True, C["dim"]).pack(anchor="w")
        lbl(foot, "CSV / XLSX", 12, True).pack(anchor="w", pady=(3, 0))
        lbl(foot, "Local processing • Private data", 9, color=C["muted"]).pack(anchor="w", pady=(3, 0))

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(main, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(22, 10))
        top.grid_columnconfigure(0, weight=1)
        self.title_lbl = lbl(top, "", 24, True)
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.sub_lbl = lbl(top, "", 11, color=C["muted"])
        self.sub_lbl.grid(row=1, column=0, sticky="w")
        self.status = ctk.CTkLabel(
            top, text="●  READY", width=120, height=30, corner_radius=15,
            fg_color=C["card"], text_color=C["green"],
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.status.grid(row=0, column=1, rowspan=2, sticky="e")

        self.stack = ctk.CTkFrame(main, fg_color="transparent")
        self.stack.grid(row=1, column=0, sticky="nsew", padx=26, pady=(0, 22))
        self.stack.grid_rowconfigure(0, weight=1)
        self.stack.grid_columnconfigure(0, weight=1)

        self.pages = {
            "dashboard": self._page_dashboard(),
            "preview": self._page_preview(),
            "profile": self._page_profile(),
            "report": self._page_report(),
            "activity": self._page_activity(),
        }

    def show(self, key):
        for k, b in self.nav.items():
            on = k == key
            b.configure(fg_color=C["active"] if on else "transparent",
                        text_color=C["text"] if on else C["muted"])
        title, sub = TITLES[key]
        self.title_lbl.configure(text=title)
        self.sub_lbl.configure(text=sub)
        for pg in self.pages.values():
            pg.grid_remove()
        self.pages[key].grid(row=0, column=0, sticky="nsew")
        {"preview": self.refresh_preview, "profile": self.refresh_profile,
         "report": self.refresh_report}.get(key, lambda: None)()

    def set_status(self, text, color):
        self.status.configure(text=f"●  {text}", text_color=color)

    # ---------------- pages ----------------

    def _page_dashboard(self):
        p = ctk.CTkScrollableFrame(self.stack, fg_color="transparent")
        p.grid_columnconfigure(0, weight=1)

        up = card(p)
        up.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        up.grid_columnconfigure(1, weight=1)
        lbl(up, "⇧", 34, color=C["blue"]).grid(row=0, column=0, rowspan=2, padx=(26, 16), pady=24)
        lbl(up, "Dataset", 16, True).grid(row=0, column=1, sticky="sw", pady=(22, 0))
        self.file_lbl = lbl(up, "No file selected — CSV or XLSX, processed locally (Ctrl+O)", 11, color=C["muted"])
        self.file_lbl.grid(row=1, column=1, sticky="nw", pady=(2, 22))
        btn(up, "Browse Dataset", self.select_file, width=170).grid(row=0, column=2, rowspan=2, padx=26)

        info = ctk.CTkFrame(p, fg_color="transparent")
        info.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for i in range(4):
            info.grid_columnconfigure(i, weight=1, uniform="a")
        self.s_rows = stat(info, 0, "Rows", size=20)
        self.s_cols = stat(info, 1, "Columns", size=20)
        self.s_size = stat(info, 2, "File size", size=20)
        self.s_miss = stat(info, 3, "Missing cells", C["amber"], size=20)

        run = ctk.CTkFrame(p, fg_color="transparent")
        run.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        run.grid_columnconfigure(1, weight=1)
        self.run_btn = btn(run, "▶   Run Cleaning Pipeline", self.start_pipeline, width=240)
        self.run_btn.configure(height=48)
        self.run_btn.grid(row=0, column=0, padx=5)
        self.progress = ctk.CTkProgressBar(run, mode="indeterminate", height=6, progress_color=C["blue"],
                                           fg_color=C["border"])
        self.progress.grid(row=0, column=1, sticky="ew", padx=20)
        self.progress.set(0)

        lbl(p, "Latest Results", 17, True).grid(row=3, column=0, sticky="w", padx=8, pady=(0, 8))
        kp = ctk.CTkFrame(p, fg_color="transparent")
        kp.grid(row=4, column=0, sticky="ew")
        for i in range(4):
            kp.grid_columnconfigure(i, weight=1, uniform="k")
        self.k_orig = stat(kp, 0, "Records", C["blue"], size=26)
        self.k_clean = stat(kp, 1, "Cleaned", C["green"], size=26)
        self.k_removed = stat(kp, 2, "Removed", C["amber"], size=26)
        self.k_score = stat(kp, 3, "Quality score", C["blue"], size=26)
        self.score_bar = ctk.CTkProgressBar(self.k_score.master, height=5, fg_color=C["border"],
                                            progress_color=C["blue"])
        self.score_bar.pack(fill="x", padx=16, pady=(0, 14))
        self.score_bar.set(0)
        lbl(self.k_score.master, "Heuristic assessment", 9, color=C["dim"]).pack(anchor="w", padx=16, pady=(0, 10))

        out = card(p)
        out.grid(row=5, column=0, sticky="ew", pady=18, padx=5)
        out.grid_columnconfigure(0, weight=1)
        lbl(out, "Output", 16, True).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 2))
        self.out_lbl = lbl(out, "Run the pipeline to generate output.", 11, color=C["muted"])
        self.out_lbl.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 16))
        self.btn_out = btn(out, "Open Output", self.open_output, False, 120, state="disabled")
        self.btn_rep = btn(out, "View Report", lambda: self.show("report"), False, 120, state="disabled")
        self.btn_dir = btn(out, "Open Folder", self.open_folder, False, 120, state="disabled")
        self.btn_out.grid(row=0, column=1, rowspan=2, padx=4)
        self.btn_rep.grid(row=0, column=2, rowspan=2, padx=4)
        self.btn_dir.grid(row=0, column=3, rowspan=2, padx=(4, 18))
        return p

    def _page_preview(self):
        p = ctk.CTkFrame(self.stack, fg_color="transparent")
        p.grid_rowconfigure(1, weight=1)
        p.grid_columnconfigure(0, weight=1)

        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.view_mode = ctk.CTkSegmentedButton(
            bar, values=["Original", "Cleaned"], command=lambda _: self.refresh_preview(),
            selected_color=C["blue"], unselected_color=C["card"],
        )
        self.view_mode.set("Original")
        self.view_mode.pack(side="left")
        self.search = ctk.CTkEntry(bar, placeholder_text="Search records…", width=300, height=34,
                                   fg_color=C["card"], border_color=C["border"])
        self.search.pack(side="left", padx=12)
        self.search.bind("<KeyRelease>", lambda e: self.refresh_preview())
        self.count_lbl = lbl(bar, "", 11, color=C["muted"])
        self.count_lbl.pack(side="right")

        self.prev_host = ctk.CTkFrame(p, fg_color="transparent")
        self.prev_host.grid(row=1, column=0, sticky="nsew")
        return p

    def _page_profile(self):
        p = ctk.CTkFrame(self.stack, fg_color="transparent")
        self.prof_host = p
        return p

    def _page_report(self):
        p = ctk.CTkFrame(self.stack, fg_color="transparent")
        self.rep_host = p
        return p

    def _page_activity(self):
        p = ctk.CTkFrame(self.stack, fg_color="transparent")
        p.grid_rowconfigure(1, weight=1)
        p.grid_columnconfigure(0, weight=1)
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="e", pady=(0, 10))
        btn(bar, "Clear Log", self.clear_log, False, 110).pack()
        self.log_box = ctk.CTkTextbox(p, fg_color=C["card"], border_width=1, border_color=C["border"],
                                      corner_radius=12, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.grid(row=1, column=0, sticky="nsew")
        for level, color in LOG_COLORS.items():
            self.log_box.tag_config(level, foreground=color)
        self.log_box.configure(state="disabled")
        return p

    # ---------------- refresh ----------------

    def refresh_preview(self):
        clear(self.prev_host)
        cleaned = self.view_mode.get() == "Cleaned"
        df = self.clean_df if cleaned else self.df
        if df is None:
            self.count_lbl.configure(text="")
            empty(self.prev_host, "Nothing to show",
                  "Run the pipeline to see cleaned data." if cleaned else "Select a dataset from the Dashboard.")
            return
        q = self.search.get().strip()
        if q:
            mask = df.astype(str).apply(
                lambda s: s.str.contains(q, case=False, regex=False, na=False)).any(axis=1)
            df = df[mask]
        shown = df.head(200)
        self.count_lbl.configure(text=f"Showing {len(shown):,} of {len(df):,} records")
        build_table(self.prev_host, [str(c) for c in df.columns], shown.itertuples(index=False))

    def refresh_profile(self):
        clear(self.prof_host)
        df = self.df
        if df is None:
            empty(self.prof_host, "No dataset selected", "Select a dataset from the Dashboard.")
            return
        n = len(df)
        rows = []
        for c in df.columns:
            miss = int(df[c].isna().sum())
            cl = self.clean_df
            cmiss = f"{int(cl[c].isna().sum()):,}" if cl is not None and c in cl.columns else "—"
            rows.append((c, str(df[c].dtype), f"{n - miss:,}", f"{miss:,}", cmiss,
                         f"{miss / n * 100:.1f}%", f"{df[c].nunique():,}"))
        build_table(self.prof_host,
                    ["Column", "Type", "Non-null", "Missing (Original)", "Missing (Cleaned)", "Missing %", "Unique"],
                    rows)

    def refresh_report(self):
        clear(self.rep_host)
        if not self.report_file or not os.path.exists(self.report_file):
            empty(self.rep_host, "No quality report yet", "Run the cleaning pipeline to generate one.")
            return
        try:
            with open(self.report_file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as exc:
            empty(self.rep_host, "Unable to load report", str(exc))
            return
        box = ctk.CTkTextbox(self.rep_host, fg_color=C["card"], border_width=1, border_color=C["border"],
                             corner_radius=12, font=ctk.CTkFont(family="Consolas", size=12))
        box.pack(fill="both", expand=True)
        box.insert("end", text)
        box.configure(state="disabled")

    # ---------------- logging ----------------

    def log(self, msg, level="INFO"):
        line = f"[{datetime.now():%H:%M:%S}]  {level:<5}  {msg}\n"
        self.events.append((line, level))
        if self.log_box is not None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", line, level)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

    def clear_log(self):
        self.events.clear()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ---------------- file selection ----------------

    def select_file(self):
        if self.running:
            return
        path = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("Supported files", "*.csv *.xlsx"), ("CSV", "*.csv"), ("Excel", "*.xlsx")],
        )
        if not path:
            return
        try:
            df = read_dataset(path)
        except Exception as exc:
            self.log(f"Failed to read {os.path.basename(path)}: {exc}", "ERROR")
            messagebox.showerror("Unable to Read Dataset", f"The file could not be opened.\n\n{exc}")
            return
        if df.empty:
            messagebox.showwarning("Empty Dataset", "The selected dataset contains no records.")
            return

        self.input_file = os.path.abspath(path)
        self.df = df
        self.clean_df = None
        name = os.path.basename(path)
        size_mb = os.path.getsize(path) / (1024 * 1024)

        self.file_lbl.configure(text=f"{name}  •  {size_mb:.2f} MB", text_color=C["text"])
        self.s_rows.configure(text=f"{len(df):,}")
        self.s_cols.configure(text=f"{len(df.columns):,}")
        self.s_size.configure(text=f"{size_mb:.2f} MB")
        self.s_miss.configure(text=f"{int(df.isna().sum().sum()):,}")
        self.log(f"Dataset loaded: {name} ({len(df):,} rows, {len(df.columns)} columns)", "OK")
        self.set_status("READY", C["green"])

    # ---------------- pipeline ----------------

    def start_pipeline(self):
        if self.running:
            return
        if not self.input_file:
            messagebox.showwarning("Dataset Required", "Please select a CSV or XLSX file first.")
            return
        self.running = True
        self.run_btn.configure(state="disabled", text="⏳   Processing...")
        self.progress.start()
        self.set_status("PROCESSING", C["amber"])
        self.log("Starting cleaning pipeline...")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, "src", "main.py"), self.input_file],
                cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            self.after(0, self._finished, r.returncode, r.stdout, r.stderr)
        except Exception as exc:
            self.after(0, self._finished, -1, "", str(exc))

    def _finished(self, code, out, err):
        self.running = False
        self.progress.stop()
        self.progress.set(0)
        self.run_btn.configure(state="normal", text="▶   Run Cleaning Pipeline")

        if code != 0:
            msg = err.strip() or out.strip() or "Unknown pipeline error."
            self.set_status("ERROR", C["red"])
            self.log(f"Pipeline failed: {msg.splitlines()[-1] if msg else ''}", "ERROR")
            messagebox.showerror("Pipeline Error", f"The pipeline could not be completed.\n\n{msg}")
            return

        original = self._num(out, r"Original rows:\s*(\d+)")
        cleaned = self._num(out, r"Final rows:\s*(\d+)")
        op = re.search(r"Output file:\s*(.+)", out)
        rp = re.search(r"Report file:\s*(.+)", out)
        if op:
            self.output_file = self._resolve(op.group(1))
        if rp:
            self.report_file = self._resolve(rp.group(1))

        self.clean_df = None
        if self.output_file and os.path.exists(self.output_file):
            try:
                self.clean_df = read_dataset(self.output_file)
            except Exception as exc:
                self.log(f"Could not load cleaned file for preview: {exc}", "WARN")

        score = self._quality_score()
        self.k_orig.configure(text=f"{original:,}")
        self.k_clean.configure(text=f"{cleaned:,}")
        self.k_removed.configure(text=f"{max(0, original - cleaned):,}")
        if score is None:
            self.k_score.configure(text="—", text_color=C["muted"])
            self.score_bar.set(0)
        else:
            color = C["green"] if score >= 90 else C["amber"] if score >= 70 else C["red"]
            self.k_score.configure(text=f"{score}%", text_color=color)
            self.score_bar.configure(progress_color=color)
            self.score_bar.set(score / 100)

        self.out_lbl.configure(text="✓ Cleaning completed • Cleaned dataset and quality report are ready.",
                               text_color=C["green"])
        for b in (self.btn_out, self.btn_rep, self.btn_dir):
            b.configure(state="normal")
        self.set_status("COMPLETED", C["green"])
        self.log(f"Rows removed (duplicates/invalid): {max(0, original - cleaned):,}")
        if self.clean_df is not None:
            self.log(f"Missing cells: {int(self.df.isna().sum().sum()):,} → {int(self.clean_df.isna().sum().sum()):,}")
            if len(self.clean_df.columns) != len(self.df.columns):
                self.log(f"Columns: {len(self.df.columns)} → {len(self.clean_df.columns)}")
        if self.output_file:
            self.log(f"Output saved: {os.path.basename(self.output_file)}")
        if score is not None:
            self.log(f"Quality score (heuristic): {score}%")
        self.log(f"Cleaning completed: {original:,} → {cleaned:,} rows.", "OK")

    def _quality_score(self):
        # Heuristic: share of original rows with no missing cell and not a duplicate.
        # Each row is counted once, so overlapping issues are never double-counted.
        df = self.df
        if df is None or df.empty:
            return None
        bad = df.isna().any(axis=1) | df.duplicated()
        return int(round(100 * (1 - bad.mean())))

    # ---------------- utils ----------------

    @staticmethod
    def _num(text, pattern):
        m = re.search(pattern, text)
        return int(m.group(1)) if m else 0

    @staticmethod
    def _resolve(path):
        path = path.strip().strip('"')
        return path if os.path.isabs(path) else os.path.abspath(os.path.join(BASE_DIR, path))

    def open_output(self):
        if self.output_file and os.path.exists(self.output_file):
            open_path(self.output_file)
        else:
            messagebox.showwarning("Output Not Found", "No output has been generated yet.")

    def open_folder(self):
        folder = os.path.dirname(self.output_file) if self.output_file else os.path.join(BASE_DIR, "data", "output")
        if os.path.isdir(folder):
            open_path(folder)
        else:
            messagebox.showwarning("Folder Not Found", "The output folder does not exist yet.")

    def on_close(self):
        if self.running and not messagebox.askyesno(
                "Processing in Progress", "A cleaning job is still running. Exit anyway?"):
            return
        self.destroy()


if __name__ == "__main__":
    DataFlowApp().mainloop()