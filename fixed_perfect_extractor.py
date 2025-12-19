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

class PerfectFastExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Perfect Fast Domain Extractor")
        self.root.geometry("950x700")
        self.root.configure(bg='#f8f9fa')
        
        # Core variables
        self.results = []
        self.is_running = False
        self.companies = []
        
        # Ultra-fast search engines with selectors
        self.engines = [
            {'name': 'DuckDuckGo', 'url': 'https://duckduckgo.com/html/?q=', 'selector': 'div.result', 'link': 'a.result__a'},
            {'name': 'Brave', 'url': 'https://search.brave.com/search?q=', 'selector': 'div.web-result', 'link': 'a.web-result-header'},
            {'name': 'StartPage', 'url': 'https://www.startpage.com/do/search?query=', 'selector': 'div.w-gl__result', 'link': 'h3 a'}
        ]
        
        # Optimized headers for speed
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = Frame(self.root, bg='#f8f9fa', padx=25, pady=25)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        Label(main_frame, text="⚡ Perfect Fast Domain Extractor", 
              font=('Arial', 18, 'bold'), bg='#f8f9fa', fg='#2c3e50').pack(pady=(0, 20))
        
        # Input section
        input_frame = Frame(main_frame, bg='#f8f9fa')
        input_frame.pack(fill=X, pady=(0, 20))
        
        Label(input_frame, text="Company Name:", 
              font=('Arial', 13, 'bold'), bg='#f8f9fa').pack(anchor=W, pady=(0, 8))
        
        single_frame = Frame(input_frame, bg='#f8f9fa')
        single_frame.pack(fill=X, pady=(0, 12))
        
        self.company_entry = Entry(single_frame, font=('Arial', 12), width=65, relief=FLAT, bd=2)
        self.company_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 12))
        
        self.search_btn = Button(single_frame, text="🔍 Search", 
                                command=self.search_single,
                                font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                                relief=FLAT, padx=18, pady=8)
        self.search_btn.pack(side=RIGHT)
        
        # File section
        file_frame = Frame(input_frame, bg='#f8f9fa')
        file_frame.pack(fill=X)
        
        Label(file_frame, text="Or upload file:", 
              font=('Arial', 13, 'bold'), bg='#f8f9fa').pack(anchor=W, pady=(0, 8))
        
        file_controls = Frame(file_frame, bg='#f8f9fa')
        file_controls.pack(fill=X)
        
        self.file_label = Label(file_controls, text="📄 No file selected", 
                               font=('Arial', 11), bg='#f8f9fa', fg='#7f8c8d')
        self.file_label.pack(side=LEFT, fill=X, expand=True)
        
        self.upload_btn = Button(file_controls, text="📂 Browse", 
                                command=self.upload_file,
                                font=('Arial', 10, 'bold'), bg='#3498db', fg='white',
                                relief=FLAT, padx=15, pady=6)
        self.upload_btn.pack(side=RIGHT, padx=(12, 8))
        
        self.batch_btn = Button(file_controls, text="⚡ Process All", 
                               command=self.process_batch,
                               font=('Arial', 10, 'bold'), bg='#9b59b6', fg='white',
                               state=DISABLED, relief=FLAT, padx=15, pady=6)
        self.batch_btn.pack(side=RIGHT)
        
        # Progress
        progress_frame = Frame(main_frame, bg='#f8f9fa')
        progress_frame.pack(fill=X, pady=(0, 20))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=X, pady=(0, 8))
        
        self.status_label = Label(progress_frame, text="🚀 Ready for ultra-fast extraction", 
                                 font=('Arial', 11, 'bold'), bg='#f8f9fa', fg='#27ae60')
        self.status_label.pack()
        
        # Results
        results_frame = Frame(main_frame, bg='#f8f9fa')
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        Label(results_frame, text="📊 Extraction Results:", 
              font=('Arial', 14, 'bold'), bg='#f8f9fa').pack(anchor=W, pady=(0, 10))
        
        # Treeview with better styling
        columns = ('Company', 'Domain', 'Source', 'Status')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=16)
        
        column_widths = {'Company': 220, 'Domain': 280, 'Source': 150, 'Status': 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 200), anchor=W)
        
        # Modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background='white', foreground='#2c3e50', 
                       fieldbackground='white', bordercolor='#ddd', relief=FLAT)
        style.configure("Treeview.Heading", background='#34495e', foreground='white',
                       font=('Arial', 11, 'bold'), relief=FLAT)
        style.map("Treeview", background=[('selected', '#3498db')], 
                 foreground=[('selected', 'white')])
        
        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Buttons
        button_frame = Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=X)
        
        # Enhanced export button - more visible and functional
        self.export_btn = Button(button_frame, text="💾 EXPORT CSV DATA", 
                               command=self.export_csv,
                               font=('Arial', 14, 'bold'), bg='#27ae60', fg='white',
                               state=DISABLED, relief=RAISED, padx=25, pady=15, bd=3,
                               cursor='hand2') 
                               command=self.export_csv,
                               font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                               state=DISABLED, relief=FLAT, padx=18, pady=10)
        self.export_btn.pack(side=LEFT)
        
        self.clear_btn = Button(button_frame, text="🗑️ Clear", 
                              command=self.clear_results,
                              font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                              relief=FLAT, padx=18, pady=10)
        self.clear_btn.pack(side=LEFT, padx=(15, 0))
        
        self.stop_btn = Button(button_frame, text="⏹️ Stop", 
                             command=self.stop_processing,
                             font=('Arial', 11, 'bold'), bg='#f39c12', fg='white',
                             state=DISABLED, relief=FLAT, padx=18, pady=10)
        self.stop_btn.pack(side=RIGHT)
    
    def search_single(self):
        if self.is_running:
            return
        
        company = self.company_entry.get().strip()
        if not company:
            messagebox.showwarning("Warning", "Enter company name!")
            return
        
        self.is_running = True
        self.search_btn.config(state=DISABLED, text="🔄 Searching...")
        self.status_label.config(text=f"🔍 Extracting domains for {company}...")
        
        thread = threading.Thread(target=self._search_company, args=(company,))
        thread.daemon = True
        thread.start()
    
    def _search_company(self, company):
        try:
            domains = self.extract_domains_perfect(company)
            self.root.after(0, self._add_results, company, domains)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._finish_search)
    
    def extract_domains_perfect(self, company):
        """Perfect domain extraction with multiple methods"""
        domains = []
        
        # Method 1: Direct patterns (fastest)
        direct = self._direct_patterns_perfect(company)
        domains.extend(direct)
        
        # Method 2: Smart search if not enough domains
        if len(domains) < 8:
            search_domains = self._smart_search(company)
            domains.extend(search_domains)
        
        # Method 3: Enhanced patterns for construction companies
        if len(domains) < 12:
            enhanced = self._enhanced_patterns(company)
            domains.extend(enhanced)
        
        # Remove duplicates and validate
        seen = set()
        unique = []
        for domain, source in domains:
            if domain not in seen and self._is_valid(domain):
                seen.add(domain)
                unique.append((domain, source))
        
        return unique[:15]  # Top 15 results
    
    def _direct_patterns_perfect(self, company):
        """Generate and check direct patterns perfectly"""
        patterns = []
        
        # Enhanced cleaning
        clean = company.lower()
        clean = re.sub(r'[^\w\s]', ' ', clean)  # Replace with space
        clean = re.sub(r'\b(llc|inc|ltd|corp|corporation|the|and|&|co|company|contractors|construction)\b', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()  # Normalize spaces
        words = [w for w in clean.split() if w]  # Remove empty
        
        if not words:
            return patterns
        
        # Generate comprehensive patterns
        base = ''.join(words)
        hyphen = '-'.join(words)
        underscore = '_'.join(words)
        
        test_domains = []
        
        # Standard patterns
        test_domains.extend([
            f"{base}.com", f"{hyphen}.com", f"{underscore}.com",
            f"{base}.net", f"{hyphen}.net", f"{base}.org",
            f"{hyphen}.org", f"{base}.io", f"{hyphen}.io"
        ])
        
        # Alaska specific patterns
        if 'alaska' in company.lower() or 'ak' in company.lower():
            test_domains.extend([
                f"{base}ak.com", f"{hyphen}ak.com", f"{base}alaska.com",
                f"{hyphen}alaska.com", f"alaska{base}.com", f"alaska{hyphen}.com"
            ])
        
        # Electric/Construction specific
        electric_keywords = ['electric', 'electrical', 'power', 'wiring', 'lighting']
        construction_keywords = ['construction', 'builder', 'contractor', 'building']
        
        if any(word in company.lower() for word in electric_keywords):
            test_domains.extend([
                f"{base}electric.com", f"{hyphen}electric.com",
                f"{base}electrical.com", f"{hyphen}electrical.com",
                f"{base}power.com", f"{hyphen}power.com"
            ])
        
        if any(word in company.lower() for word in construction_keywords):
            test_domains.extend([
                f"{base}construction.com", f"{hyphen}construction.com",
                f"{base}builders.com", f"{hyphen}builders.com",
                f"{base}contractors.com", f"{hyphen}contractors.com"
            ])
        
        # Number patterns (like 907 Electric)
        number_match = re.search(r'\b(\d{3,4})\b', company)
        if number_match:
            number = number_match.group(1)
            remaining = company.lower().replace(number, '').strip()
            remaining_clean = re.sub(r'[^\w\s]', ' ', remaining)
            remaining_clean = re.sub(r'\b(llc|inc|ltd|corp|the|and|&)\b', '', remaining_clean)
            remaining_words = [w for w in remaining_clean.split() if w]
            
            if remaining_words:
                remaining_base = ''.join(remaining_words)
                test_domains.extend([
                    f"{number}{remaining_base}.com", f"{number}{remaining_base}ak.com",
                    f"{remaining_base}{number}.com", f"{remaining_base}{number}ak.com"
                ])
        
        # Location-based patterns
        if any(loc in company.lower() for loc in ['anchorage', 'fairbanks', 'juneau', 'wasilla', 'palmer']):
            for loc in ['anchorage', 'fairbanks', 'juneau']:
                if loc in company.lower():
                    test_domains.extend([f"{base}{loc}.com", f"{hyphen}{loc}.com"])
        
        # Remove duplicates and check domains fast
        unique_domains = list(set(test_domains))
        valid = []
        
        # Ultra-fast concurrent domain checking
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(self._check_domain_ultra_fast, domain): domain for domain in unique_domains}
            
            for future in as_completed(futures):
                domain = futures[future]
                try:
                    if future.result(timeout=0.6):  # Ultra-fast timeout
                        valid.append((domain, "Direct Pattern"))
                except:
                    continue
        
        return valid
    
    def _check_domain_ultra_fast(self, domain):
        """Ultra-fast domain existence check"""
        try:
            # Try HTTPS first (faster for modern sites)
            url = f"https://{domain}"
            response = requests.head(url, headers=self.headers, timeout=0.6, allow_redirects=True)
            if response.status_code in [200, 301, 302, 403, 404]:
                return True
            
            # Quick HTTP fallback
            url = f"http://{domain}"
            response = requests.head(url, headers=self.headers, timeout=0.6, allow_redirects=True)
            return response.status_code in [200, 301, 302, 403, 404]
        except:
            return False
    
    def _smart_search(self, company):
        """Smart search engine extraction"""
        domains = []
        
        # Intelligent queries based on company type
        queries = self._generate_smart_queries(company)
        
        # Concurrent search with optimized workers
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            for engine in self.engines:
                for query in queries[:2]:  # Top 2 queries per engine
                    future = executor.submit(self._search_engine_smart, engine, query)
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    found = future.result(timeout=2.0)  # Faster timeout
                    domains.extend(found)
                except:
                    continue
        
        return domains
    
    def _generate_smart_queries(self, company):
        """Generate intelligent search queries"""
        queries = []
        company_lower = company.lower()
        
        # Base queries
        queries.extend([
            f"{company} official website",
            f"{company} .com",
            f"www.{company.lower().replace(' ', '')}"
        ])
        
        # Industry-specific queries
        if any(word in company_lower for word in ['electric', 'electrical']):
            queries.extend([
                f"{company} electric company",
                f"{company} electrical contractor"
            ])
        
        if any(word in company_lower for word in ['construction', 'builder', 'contractor']):
            queries.extend([
                f"{company} construction company",
                f"{company} building contractor"
            ])
        
        if 'alaska' in company_lower or 'ak' in company_lower:
            queries.extend([
                f"{company} alaska",
                f"{company} anchorage"
            ])
        
        return queries[:4]  # Top 4 queries
    
    def _search_engine_smart(self, engine, query):
        """Smart single engine search"""
        try:
            url = engine['url'] + requests.utils.quote(query)
            response = requests.get(url, headers=self.headers, timeout=2.0)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                found = self._extract_smart_domains(soup, engine)
                return [(domain, f"Search: {engine['name']}") for domain in found[:6]]
        except Exception as e:
            pass
        return []
    
    def _extract_smart_domains(self, soup, engine):
        """Smart domain extraction from search results"""
        domains = []
        
        # Use engine-specific selectors for better results
        results = soup.find_all('div', class_=engine.get('selector', 'result'))
        
        # Extract from first 15 results (more comprehensive)
        for result in results[:15]:
            try:
                # Extract from main link
                link = result.find('a', href=True)
                
                if link:
                    href = link['href']
                    domain = self._get_domain(href)
                    
                    if domain and domain not in domains and self._is_valid(domain):
                        domains.append(domain)
                
                # Extract from citation/URL text
                cite = result.find('cite') or result.find('span', class_='url')
                if cite:
                    cite_text = cite.get_text()
                    domain_match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', cite_text)
                    if domain_match:
                        domain = domain_match.group(1).lower()
                        if domain not in domains and self._is_valid(domain):
                            domains.append(domain)
            except:
                continue
        
        # Fallback: extract from text (limited for speed)
        text = soup.get_text()[:1500]  # First 1500 chars
        matches = re.findall(r'\b[a-zA-Z0-9.-]+\.(com|org|net|io|gov|edu|co|us|uk|ca|au|info|biz|online)\b', text, re.IGNORECASE)
        
        for match in matches[:8]:  # First 8 matches
            domain = match.lower()
            if domain not in domains and self._is_valid(domain):
                domains.append(domain)
        
        return domains[:10]  # Top 10 domains
    
    def _enhanced_patterns(self, company):
        """Generate enhanced patterns for construction companies"""
        patterns = []
        company_lower = company.lower()
        
        # Common construction abbreviations
        abbreviations = {
            'electrical': ['elec', 'electric'],
            'construction': ['const', 'construct', 'building'],
            'contractors': ['contractor', 'contr'],
            'services': ['svc', 'service'],
            'systems': ['sys', 'system']
        }
        
        # Generate abbreviation patterns
        for word, abbrs in abbreviations.items():
            if word in company_lower:
                clean_name = company_lower.replace(word, '')
                clean_name = re.sub(r'[^\w\s]', ' ', clean_name).strip()
                words = [w for w in clean_name.split() if w]
                
                if words:
                    base = ''.join(words)
                    for abbr in abbrs:
                        patterns.extend([
                            f"{base}{abbr}.com",
                            f"{base}{abbr}s.com",
                            f"{abbr}{base}.com"
                        ])
        
        # Location-based enhanced patterns
        locations = ['ak', 'alaska', 'anchorage', 'fairbanks', 'wasilla']
        for loc in locations:
            if loc in company_lower:
                clean_name = company_lower.replace(loc, '').strip()
                clean_name = re.sub(r'[^\w\s]', ' ', clean_name).strip()
                words = [w for w in clean_name.split() if w]
                
                if words:
                    base = ''.join(words)
                    patterns.extend([
                        f"{base}{loc}.com",
                        f"{loc}{base}.com",
                        f"{base}-{loc}.com"
                    ])
        
        # Check patterns fast
        valid = []
        if patterns:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(self._check_domain_ultra_fast, pattern): pattern for pattern in patterns}
                
                for future in as_completed(futures):
                    pattern = futures[future]
                    try:
                        if future.result(timeout=0.6):
                            valid.append((pattern, "Enhanced Pattern"))
                    except:
                        continue
        
        return valid
    
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
            status = "✅ Found" if source != "Error" else "❌ Error"
            self.tree.insert('', 'end', values=(company, domain, source, status))
            self.results.append({'Company': company, 'Domain': domain, 'Source': source, 'Status': status})
        
        self.export_btn.config(state=NORMAL)
    
    def _finish_search(self):
        self.is_running = False
        self.search_btn.config(state=NORMAL, text="🔍 Search")
        self.status_label.config(text="✅ Extraction completed successfully")
    
    def _show_error(self, error):
        messagebox.showerror("Error", f"Error: {error}")
    
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select companies file",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                companies = self._read_file(filename)
                if companies:
                    self.companies = companies
                    self.file_label.config(text=f"📄 {len(companies)} companies loaded", fg='#27ae60')
                    self.batch_btn.config(state=NORMAL)
                    self.status_label.config(text=f"📁 Loaded {len(companies)} companies")
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
        
        self.status_label.config(text=f"⚡ Processing {self.total} companies at ultra speed...")
        
        thread = threading.Thread(target=self._batch_process)
        thread.daemon = True
        thread.start()
    
    def _batch_process(self):
        """Ultra-fast batch processing"""
        with ThreadPoolExecutor(max_workers=25) as executor:
            # Submit all
            future_to_company = {
                executor.submit(self.extract_domains_perfect, company): company 
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
                    domains = future.result(timeout=2.5)  # Faster timeout
                    self.root.after(0, self._add_results, company, domains)
                except Exception as e:
                    self.root.after(0, self._add_error, company, str(e))
        
        # Done
        self.root.after(0, self._finish_batch)
    
    def _update_progress(self, current, company):
        self.progress['value'] = current
        self.status_label.config(text=f"⚡ Processing {current}/{self.total}: {company}")
    
    def _add_error(self, company, error):
        self.tree.insert('', 'end', values=(company, f"Error: {error}", "Error", "❌ Error"))
    
    def _finish_batch(self):
        self.is_running = False
        self.batch_btn.config(state=NORMAL)
        self.upload_btn.config(state=NORMAL)
        self.search_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status_label.config(text=f"✅ Completed {self.total} companies successfully")
    
    def stop_processing(self):
        self.is_running = False
        self._finish_batch()
        self.status_label.config(text="⏹️ Processing stopped by user")
    
    def export_csv(self):
        """Enhanced export function with better feedback"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        # Auto-generate filename with timestamp
        filename = f"extracted_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False)
            
            # Show success message with file location
            full_path = os.path.abspath(filename)
            messagebox.showinfo("✅ EXPORT SUCCESSFUL!", 
                f"Successfully exported {len(self.results)} records!\n\n"
                f"Filename: {filename}\n"
                f"Full path: {full_path}\n\n"
                f"Your data has been saved! You can now open this file in Excel.")
            
            self.status_label.config(text=f"💾 Exported {len(self.results)} records to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def 
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"perfect_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"✅ Exported {len(self.results)} results successfully")
                self.status_label.config(text=f"💾 Exported {len(self.results)} results to CSV")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.results = []
        self.companies = []
        self.processed = 0
        self.progress['value'] = 0
        
        self.export_btn.config(state=DISABLED)
        self.file_label.config(text="📄 No file selected", fg='#7f8c8d')
        self.batch_btn.config(state=DISABLED)
        self.status_label.config(text="🚀 Ready for ultra-fast extraction")

if __name__ == "__main__":
    root = Tk()
    app = PerfectFastExtractor(root)
    root.mainloop()
