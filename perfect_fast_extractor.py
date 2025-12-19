import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse

import pandas as pd
import requests

try:
    # Preferred new package name
    from ddgs import DDGS
except ImportError:  # pragma: no cover - fallback for older installs
    from duckduckgo_search import DDGS


class PerfectFastExtractor:
    """Link-Gopher style domain extractor powered by DuckDuckGo."""

    BLACKLIST = {
        "facebook.com",
        "linkedin.com",
        "youtube.com",
        "yelp.com",
        "bbb.org",
        "yellowpages.com",
        "instagram.com",
        "twitter.com",
        "en.wikipedia.org",
        "maps.google.com",
        "google.com",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Perfect Fast Domain Extractor")
        self.root.geometry("1100x720")
        self.root.configure(bg="#f5f7fb")

        self.results = []
        self.is_running = False
        self.companies = []
        self.domain_cache = {}
        self.validation_executor = ThreadPoolExecutor(max_workers=6)

        self.session_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----------------------------- UI SETUP -----------------------------
    def _setup_ui(self):
        main_frame = Frame(self.root, bg="#f5f7fb", padx=24, pady=24)
        main_frame.pack(fill=BOTH, expand=True)

        title_frame = Frame(main_frame, bg="#f5f7fb")
        title_frame.pack(fill=X, pady=(0, 18))

        Label(
            title_frame,
            text="⚡ Perfect Fast Domain Extractor",
            font=("Arial", 20, "bold"),
            bg="#f5f7fb",
            fg="#1f2d3d",
        ).pack(side=LEFT)

        self.export_btn = Button(
            title_frame,
            text="💾 Export CSV",
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=18,
            pady=10,
            relief=RAISED,
            bd=3,
            state=DISABLED,
            command=self.export_csv,
        )
        self.export_btn.pack(side=RIGHT)

        input_frame = Frame(main_frame, bg="#f5f7fb")
        input_frame.pack(fill=X, pady=(0, 16))

        Label(
            input_frame,
            text="Company Name:",
            font=("Arial", 12, "bold"),
            bg="#f5f7fb",
        ).pack(anchor=W, pady=(0, 6))

        single_frame = Frame(input_frame, bg="#f5f7fb")
        single_frame.pack(fill=X)

        self.company_entry = Entry(single_frame, font=("Arial", 12), relief=FLAT)
        self.company_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

        self.search_btn = Button(
            single_frame,
            text="🔍 Search",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=16,
            pady=8,
            relief=FLAT,
            command=self.search_single,
        )
        self.search_btn.pack(side=RIGHT)

        Label(
            input_frame,
            text="Or upload file:",
            font=("Arial", 12, "bold"),
            bg="#f5f7fb",
        ).pack(anchor=W, pady=(12, 6))

        file_frame = Frame(input_frame, bg="#f5f7fb")
        file_frame.pack(fill=X)

        self.file_label = Label(
            file_frame,
            text="📄 No file selected",
            font=("Arial", 11),
            bg="#f5f7fb",
            fg="#7f8c8d",
        )
        self.file_label.pack(side=LEFT, fill=X, expand=True)

        self.batch_btn = Button(
            file_frame,
            text="⚡ Process All",
            font=("Arial", 10, "bold"),
            bg="#9b59b6",
            fg="white",
            padx=14,
            pady=6,
            relief=FLAT,
            state=DISABLED,
            command=self.process_batch,
        )
        self.batch_btn.pack(side=RIGHT)

        self.upload_btn = Button(
            file_frame,
            text="📂 Browse",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            padx=14,
            pady=6,
            relief=FLAT,
            command=self.upload_file,
        )
        self.upload_btn.pack(side=RIGHT, padx=(12, 0))

        progress_frame = Frame(main_frame, bg="#f5f7fb")
        progress_frame.pack(fill=X, pady=(0, 18))

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill=X, pady=(0, 8))

        self.status_label = Label(
            progress_frame,
            text="🚀 Ready for ultra-fast extraction",
            font=("Arial", 11, "bold"),
            bg="#f5f7fb",
            fg="#27ae60",
        )
        self.status_label.pack()

        results_frame = Frame(main_frame, bg="#f5f7fb")
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 18))

        Label(
            results_frame,
            text="📊 Extraction Results",
            font=("Arial", 14, "bold"),
            bg="#f5f7fb",
        ).pack(anchor=W, pady=(0, 8))

        columns = ("Company", "Best Match", "All Page 1 Domains", "Status")
        self.tree = ttk.Treeview(
            results_frame, columns=columns, show="headings", height=16
        )
        self.tree.heading("Company", text="Company")
        self.tree.heading("Best Match", text="Best Match")
        self.tree.heading("All Page 1 Domains", text="All Page 1 Domains")
        self.tree.heading("Status", text="Status")
        self.tree.column("Company", width=220, anchor=W)
        self.tree.column("Best Match", width=220, anchor=W)
        self.tree.column("All Page 1 Domains", width=460, anchor=W)
        self.tree.column("Status", width=120, anchor=W)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground="#1f2d3d",
            fieldbackground="white",
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background="#34495e",
            foreground="white",
            font=("Arial", 11, "bold"),
        )
        style.map("Treeview", background=[("selected", "#16a085")], foreground=[("selected", "white")])

        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        button_frame = Frame(main_frame, bg="#f5f7fb")
        button_frame.pack(fill=X)

        self.clear_btn = Button(
            button_frame,
            text="🗑️ Clear",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=18,
            pady=8,
            relief=FLAT,
            command=self.clear_results,
        )
        self.clear_btn.pack(side=LEFT)

        self.stop_btn = Button(
            button_frame,
            text="⏹️ Stop",
            font=("Arial", 11, "bold"),
            bg="#f39c12",
            fg="white",
            padx=18,
            pady=8,
            relief=FLAT,
            state=DISABLED,
            command=self.stop_processing,
        )
        self.stop_btn.pack(side=RIGHT)

    # -------------------------- CORE ACTIONS ---------------------------
    def search_single(self):
        if self.is_running:
            return

        company = self.company_entry.get().strip()
        if not company:
            messagebox.showwarning("Warning", "Enter company name!")
            return

        self.is_running = True
        self.search_btn.config(state=DISABLED, text="🔄 Searching…")
        self.status_label.config(text=f"🔍 Searching for {company}…")

        thread = threading.Thread(target=self._search_company, args=(company,))
        thread.daemon = True
        thread.start()

    def _search_company(self, company):
        try:
            result = self._extract_domains(company)
            self.root.after(0, lambda: self._record_result(company, result))
        except Exception as exc:
            self.root.after(0, lambda: self._add_error(company, str(exc)))
        finally:
            self.root.after(0, self._finish_single)

    def _finish_single(self):
        self.is_running = False
        self.search_btn.config(state=NORMAL, text="🔍 Search")
        self.status_label.config(text="✅ Ready for the next company")

    # --------------------- DUCKDUCKGO EXTRACTION -----------------------
    def _extract_domains(self, company_name):
        """Fetch Link-Gopher style results from DuckDuckGo."""
        query = f"{company_name} official website"
        domains = []

        with DDGS() as ddgs:
            for entry in ddgs.text(query, max_results=20):
                url = entry.get("href") or entry.get("url")
                if not url:
                    continue
                domain = self._clean_domain(url)
                if domain and domain not in domains:
                    domains.append(domain)

        live_domains = self._validate_domains(domains)
        best_match = self._select_best_domain(live_domains)
        status = "✅ Live domain found" if best_match else "⚠️ No live domain"

        return {
            "company": company_name,
            "best_match": best_match or "Not Found",
            "all_domains": ", ".join(domains) if domains else "No domains detected",
            "status": status,
        }

    def _validate_domains(self, domains):
        validated = []
        futures = {}

        for domain in domains:
            if not self._is_valid_domain(domain):
                continue

            cached = self.domain_cache.get(domain)
            if cached is not None:
                if cached:
                    validated.append(domain)
                continue

            future = self.validation_executor.submit(self._is_domain_live, domain)
            futures[future] = domain

        for future, domain in futures.items():
            alive = future.result()
            self.domain_cache[domain] = alive
            if alive:
                validated.append(domain)

        return validated

    def _select_best_domain(self, domains):
        for domain in domains:
            if self._is_blacklisted(domain):
                continue
            return domain
        return domains[0] if domains else None

    def _is_domain_live(self, domain):
        try:
            response = requests.head(
                f"https://{domain}",
                headers=self.session_headers,
                timeout=3,
                allow_redirects=True,
            )
            if response.ok or response.status_code in (301, 302, 403):
                return True
            response = requests.head(
                f"http://{domain}",
                headers=self.session_headers,
                timeout=3,
                allow_redirects=True,
            )
            return response.ok or response.status_code in (301, 302, 403)
        except Exception:
            return False

    @staticmethod
    def _clean_domain(url):
        parsed = urlparse(url)
        domain = parsed.netloc or url
        domain = domain.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.split("/")[0]

    @staticmethod
    def _is_valid_domain(domain):
        if not domain or "." not in domain:
            return False
        return len(domain) <= 253

    def _is_blacklisted(self, domain):
        return any(domain.endswith(bad) for bad in self.BLACKLIST)

    # --------------------- RESULT + TABLE MANAGEMENT -------------------
    def _record_result(self, company, result):
        self._remove_existing(company)

        self.tree.insert(
            "",
            "end",
            values=(result["company"], result["best_match"], result["all_domains"], result["status"]),
        )

        self.results.append(
            {
                "Company": result["company"],
                "Best Match": result["best_match"],
                "All Page 1 Domains": result["all_domains"],
                "Status": result["status"],
            }
        )

        self.export_btn.config(state=NORMAL)

    def _remove_existing(self, company):
        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == company:
                self.tree.delete(item)

    def _add_error(self, company, error):
        self.tree.insert("", "end", values=(company, "-", "-", f"❌ {error}"))

    # -------------------------- FILE HANDLING ---------------------------
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select companies file",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            companies = self._read_companies(filename)
            if not companies:
                messagebox.showwarning("Warning", "No companies found in file")
                return
            self.companies = companies
            self.file_label.config(text=f"📄 {len(companies)} companies loaded", fg="#27ae60")
            self.batch_btn.config(state=NORMAL)
            self.status_label.config(text=f"📁 Ready to process {len(companies)} companies")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to read file: {exc}")

    @staticmethod
    def _read_companies(path):
        companies = []
        if path.lower().endswith(".csv"):
            df = pd.read_csv(path)
            for column in ("company", "Company", "name", "Name"):
                if column in df.columns:
                    companies = [str(value).strip() for value in df[column].dropna() if str(value).strip()]
                    break
            if not companies and not df.empty:
                companies = [str(value).strip() for value in df.iloc[:, 0].dropna() if str(value).strip()]
        else:
            with open(path, "r", encoding="utf-8") as handle:
                companies = [line.strip() for line in handle if line.strip()]
        return companies

    # ------------------------------ BATCH ------------------------------
    def process_batch(self):
        if not self.companies or self.is_running:
            return

        self.is_running = True
        self.total = len(self.companies)
        self.progress.config(mode="determinate", maximum=self.total, value=0)
        self.status_label.config(text=f"⚡ Processing {self.total} companies…")
        self.search_btn.config(state=DISABLED)
        self.batch_btn.config(state=DISABLED)
        self.upload_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)

        thread = threading.Thread(target=self._batch_worker)
        thread.daemon = True
        thread.start()

    def _batch_worker(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_company = {
                executor.submit(self._extract_domains, company): company for company in self.companies
            }

            processed = 0
            for future in as_completed(future_to_company):
                company = future_to_company[future]
                processed += 1
                self.root.after(0, lambda c=company, p=processed: self._update_progress(c, p))
                try:
                    result = future.result()
                    self.root.after(0, lambda r=result: self._record_result(r["company"], r))
                except Exception as exc:
                    self.root.after(0, lambda c=company, e=str(exc): self._add_error(c, e))

        self.root.after(0, self._finish_batch)

    def _update_progress(self, company, processed):
        self.progress["value"] = processed
        self.status_label.config(text=f"⚡ Processing {processed}/{self.total}: {company}")

    def _finish_batch(self):
        self.is_running = False
        self.batch_btn.config(state=NORMAL)
        self.upload_btn.config(state=NORMAL)
        self.search_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status_label.config(text="✅ Batch completed")

    def stop_processing(self):
        self.is_running = False
        self.status_label.config(text="⏹️ Processing stopped by user")

    # ---------------------------- UTILITIES ----------------------------
    def export_csv(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export")
            return

        filename = f"perfect_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pd.DataFrame(self.results).to_csv(filename, index=False)
        full_path = os.path.abspath(filename)
        messagebox.showinfo(
            "Export Complete",
            f"Saved {len(self.results)} records to:\n{full_path}",
        )

    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.results = []
        self.companies = []
        self.progress["value"] = 0
        self.status_label.config(text="🚀 Ready for ultra-fast extraction")
        self.file_label.config(text="📄 No file selected", fg="#7f8c8d")
        self.batch_btn.config(state=DISABLED)
        self.export_btn.config(state=DISABLED)

    def _on_close(self):
        if self.validation_executor:
            self.validation_executor.shutdown(wait=False)
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    app = PerfectFastExtractor(root)
    root.mainloop()
