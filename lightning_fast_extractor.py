import requests
import re
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class LightningFastExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Lightning Fast Domain Extractor")
        self.root.geometry("900x650")
        self.root.configure(bg='#f0f0f0')
        
        # Core variables
        self.results = []
        self.is_running = False
        self.companies = []
        
        # Fast search engines only
        self.engines = [
            {'name': 'DuckDuckGo', 'url': 'https://duckduckgo.com/html/?q='},
            {'name': 'Brave', 'url': 'https://search.brave.com/search?q='}
        ]
        
        # Simple headers for speed
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        Label(main_frame, text="⚡ Lightning Fast Domain Extractor", 
              font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=(0, 15))
        
        # Input section
        input_frame = Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(fill=X, pady=(0, 15))
        
        Label(input_frame, text="Company Name:", 
              font=('Arial', 12), bg='#f0f0f0').pack(anchor=W)
        
        single_frame = Frame(input_frame, bg='#f0f0f0')
        single_frame.pack(fill=X, pady=(5, 10))
        
        self.company_entry = Entry(single_frame, font=('Arial', 12), width=60)
        self.company_entry.pack(side=LEFT, fill=X, expand=True)
        
        self.search_btn = Button(single_frame, text="Search", 
                                command=self.search_single,
                                font=('Arial', 11), bg='#4CAF50', fg='white',
                                padx=15, pady=5)
        self.search_btn.pack(side=RIGHT, padx=(10, 0))
        
        # File section
        file_frame = Frame(input_frame, bg='#f0f0f0')
        file_frame.pack(fill=X)
        
        Label(file_frame, text="Or upload file:", 
              font=('Arial', 12), bg='#f0f0f0').pack(anchor=W)
        
        file_controls = Frame(file_frame, bg='#f0f0f0')
        file_controls.pack(fill=X, pady=(5, 0))
        
        self.file_label = Label(file_controls, text="No file selected", 
                               font=('Arial', 10), bg='#f0f0f0', fg='gray')
        self.file_label.pack(side=LEFT, fill=X, expand=True)
        
        self.upload_btn = Button(file_controls, text="Browse", 
                                command=self.upload_file,
                                font=('Arial', 10), bg='#2196F3', fg='white',
                                padx=12, pady=4)
        self.upload_btn.pack(side=RIGHT, padx=(10, 5))
        
        self.batch_btn = Button(file_controls, text="Process All", 
                               command=self.process_batch,
                               font=('Arial', 10, 'bold'), bg='#9C27B0', fg='white',
                               state=DISABLED, padx=12, pady=4)
        self.batch_btn.pack(side=RIGHT)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=X, pady=(0, 15))
        
        self.status_label = Label(main_frame, text="Ready", 
                                 font=('Arial', 10), bg='#f0f0f0')
        self.status_label.pack()
        
        # Results
        results_frame = Frame(main_frame, bg='#f0f0f0')
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        Label(results_frame, text="Results:", 
              font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor=W)
        
        # Treeview
        columns = ('Company', 'Domain', 'Source')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=250)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Buttons
        button_frame = Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=X)
        
        self.export_btn = Button(button_frame, text="Export CSV", 
                               command=self.export_csv,
                               font=('Arial', 11), bg='#2196F3', fg='white',
                               state=DISABLED, padx=15, pady=8)
        self.export_btn.pack(side=LEFT)
        
        self.clear_btn = Button(button_frame, text="Clear", 
                              command=self.clear_results,
                              font=('Arial', 11), bg='#f44336', fg='white',
                              padx=15, pady=8)
        self.clear_btn.pack(side=LEFT, padx=(10, 0))
        
        self.stop_btn = Button(button_frame, text="Stop", 
                             command=self.stop_processing,
                             font=('Arial', 11), bg='#FF9800', fg='white',
                             state=DISABLED, padx=15, pady=8)
        self.stop_btn.pack(side=RIGHT)
    
    def search_single(self):
        if self.is_running:
            return
        
        company = self.company_entry.get().strip()
        if not company:
            messagebox.showwarning("Warning", "Enter company name!")
            return
        
        self.is_running = True
        self.search_btn.config(state=DISABLED, text="Searching...")
        self.status_label.config(text=f"Searching {company}...")
        
        thread = threading.Thread(target=self._search_company, args=(company,))
        thread.daemon = True
        thread.start()
    
    def _search_company(self, company):
        try:
            domains = self.extract_domains(company)
            self.root.after(0, self._add_results, company, domains)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._finish_search)
    
    def extract_domains(self, company):
        """Fast domain extraction"""
        domains = []
        
        # Direct patterns first (fastest)
        direct = self._direct_patterns(company)
        domains.extend(direct)
        
        # Search engines if needed
        if len(domains) < 5:
            search_domains = self._search_engines(company)
            domains.extend(search_domains)
        
        # Remove duplicates
        seen = set()
        unique = []
        for domain, source in domains:
            if domain not in seen and self._is_valid(domain):
                seen.add(domain)
                unique.append((domain, source))
        
        return unique[:10]  # Top 10
    
    def _direct_patterns(self, company):
        """Generate and check direct patterns"""
        patterns = []
        
        # Clean name
        clean = company.lower()
        clean = re.sub(r'[^\w\s]', '', clean)
        clean = re.sub(r'\b(llc|inc|ltd|corp|the|and|&)\b', '', clean)
        words = clean.split()
        
        if not words:
            return patterns
        
        # Generate patterns
        base = ''.join(words)
        hyphen = '-'.join(words)
        
        test_domains = [
            f"{base}.com",
            f"{hyphen}.com",
            f"{base}.net",
            f"{hyphen}.net",
            f"{base}.org",
            f"{hyphen}.org"
        ]
        
        # Alaska specific
        if 'alaska' in company.lower():
            test_domains.extend([f"{base}ak.com", f"{hyphen}ak.com"])
        
        # Electric specific
        if any(word in company.lower() for word in ['electric', 'electrical']):
            test_domains.extend([f"{base}electric.com", f"{hyphen}electric.com"])
        
        # Number patterns
        number_match = re.search(r'\b(\d{3})\b', company)
        if number_match:
            number = number_match.group(1)
            remaining = company.lower().replace(number, '').strip()
            remaining_clean = re.sub(r'[^\w\s]', '', remaining).split()
            if remaining_clean:
                test_domains.append(f"{number}{''.join(remaining_clean)}.com")
        
        # Check domains fast
        valid = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self._check_domain, domain): domain for domain in test_domains}
            
            for future in as_completed(futures):
                domain = futures[future]
                try:
                    if future.result(timeout=1):
                        valid.append((domain, "Direct"))
                except:
                    continue
        
        return valid
    
    def _check_domain(self, domain):
        """Fast domain check"""
        try:
            url = f"https://{domain}"
            response = requests.head(url, headers=self.headers, timeout=1, allow_redirects=True)
            return response.status_code in [200, 301, 302, 403, 404]
        except:
            try:
                url = f"http://{domain}"
                response = requests.head(url, headers=self.headers, timeout=1, allow_redirects=True)
                return response.status_code in [200, 301, 302, 403, 404]
            except:
                return False
    
    def _search_engines(self, company):
        """Fast search engine extraction"""
        domains = []
        
        # Simple queries
        queries = [f"{company} official website", f"{company} .com"]
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for engine in self.engines:
                for query in queries:
                    future = executor.submit(self._search_engine, engine, query)
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    found = future.result(timeout=3)
                    domains.extend(found)
                except:
                    continue
        
        return domains
    
    def _search_engine(self, engine, query):
        """Single engine search"""
        try:
            url = engine['url'] + requests.utils.quote(query)
            response = requests.get(url, headers=self.headers, timeout=3)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                found = self._extract_from_html(soup)
                return [(domain, f"Search: {engine['name']}") for domain in found[:5]]
        except:
            pass
        return []
    
    def _extract_from_html(self, soup):
        """Extract domains from HTML"""
        domains = []
        
        # From links
        links = soup.find_all('a', href=True)
        for link in links[:20]:  # First 20 links
            href = link['href']
            domain = self._get_domain(href)
            if domain and domain not in domains:
                domains.append(domain)
        
        # From text
        text = soup.get_text()[:2000]  # First 2000 chars
        matches = re.findall(r'\b[a-zA-Z0-9.-]+\.(com|org|net|io|gov|edu|co|us|uk|ca|au)\b', text, re.IGNORECASE)
        
        for match in matches[:10]:  # First 10 matches
            domain = match.lower()
            if domain not in domains and self._is_valid(domain):
                domains.append(domain)
        
        return domains[:8]  # Top 8
    
    def _get_domain(self, url):
        """Get domain from URL"""
        try:
            if url.startswith('http'):
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                if domain.startswith('www.'):
                    domain = domain[4:]
                return domain
            elif '.' in url and '/' not in url:
                return url.lower()
        except:
            pass
        return None
    
    def _is_valid(self, domain):
        """Validate domain"""
        if not domain or len(domain) > 253:
            return False
        
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def _add_results(self, company, domains):
        # Clear previous results for this company
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == company:
                self.tree.delete(item)
        
        # Add new results
        for domain, source in domains:
            self.tree.insert('', 'end', values=(company, domain, source))
            self.results.append({'Company': company, 'Domain': domain, 'Source': source})
        
        self.export_btn.config(state=NORMAL)
    
    def _finish_search(self):
        self.is_running = False
        self.search_btn.config(state=NORMAL, text="Search")
        self.status_label.config(text="Ready")
    
    def _show_error(self, error):
        messagebox.showerror("Error", f"Error: {error}")
    
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                companies = self._read_file(filename)
                if companies:
                    self.companies = companies
                    self.file_label.config(text=f"{len(companies)} companies loaded", fg='green')
                    self.batch_btn.config(state=NORMAL)
                else:
                    messagebox.showwarning("Warning", "No companies found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")
    
    def _read_file(self, filename):
        companies = []
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
                # Try columns
                for col in ['company', 'Company', 'name', 'Name']:
                    if col in df.columns:
                        companies = [str(name).strip() for name in df[col].dropna() if str(name).strip()]
                        break
                
                # First column fallback
                if not companies and len(df.columns) > 0:
                    companies = [str(name).strip() for name in df.iloc[:, 0].dropna() if str(name).strip()]
            else:
                # Text file
                with open(filename, 'r', encoding='utf-8') as f:
                    companies = [line.strip() for line in f if line.strip()]
            
            # Clean up
            companies = [c for c in companies if c and len(c) > 1]
            
        except Exception as e:
            print(f"Read error: {e}")
            
        return companies
    
    def process_batch(self):
        if not self.companies or self.is_running:
            return
        
        self.is_running = True
        self.total = len(self.companies)
        self.processed = 0
        
        # Update UI
        self.batch_btn.config(state=DISABLED)
        self.upload_btn.config(state=DISABLED)
        self.search_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        
        # Progress
        self.progress.config(mode='determinate', maximum=self.total)
        self.progress['value'] = 0
        
        self.status_label.config(text=f"Processing {self.total} companies...")
        
        thread = threading.Thread(target=self._batch_process)
        thread.daemon = True
        thread.start()
    
    def _batch_process(self):
        """Fast batch processing"""
        with ThreadPoolExecutor(max_workers=15) as executor:
            # Submit all
            future_to_company = {
                executor.submit(self.extract_domains, company): company 
                for company in self.companies
            }
            
            # Process results
            for future in as_completed(future_to_company):
                if not self.is_running:
                    break
                
                company = future_to_company[future]
                self.processed += 1
                
                # Update progress
                self.root.after(0, self._update_progress, self.processed, company)
                
                try:
                    domains = future.result(timeout=5)
                    self.root.after(0, self._add_results, company, domains)
                except Exception as e:
                    self.root.after(0, self._add_error, company, str(e))
        
        # Done
        self.root.after(0, self._finish_batch)
    
    def _update_progress(self, current, company):
        self.progress['value'] = current
        self.status_label.config(text=f"Processing {current}/{self.total}: {company}")
    
    def _add_error(self, company, error):
        self.tree.insert('', 'end', values=(company, f"Error: {error}", "Error"))
    
    def _finish_batch(self):
        self.is_running = False
        self.batch_btn.config(state=NORMAL)
        self.upload_btn.config(state=NORMAL)
        self.search_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status_label.config(text=f"Completed {self.total} companies")
    
    def stop_processing(self):
        self.is_running = False
        self._finish_batch()
    
    def export_csv(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Exported {len(self.results)} results")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.results = []
        self.companies = []
        self.processed = 0
        self.progress['value'] = 0
        
        self.export_btn.config(state=DISABLED)
        self.file_label.config(text="No file selected", fg='gray')
        self.batch_btn.config(state=DISABLED)
        self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = Tk()
    app = LightningFastExtractor(root)
    root.mainloop()
