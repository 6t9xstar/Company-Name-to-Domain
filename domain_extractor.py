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
import queue

class CompanyDomainExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Company Name to Domain Extractor")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.results = []
        self.is_searching = False
        self.companies_to_process = []
        self.current_batch_index = 0
        self.total_companies = 0
        self.executor = None
        self.result_queue = queue.Queue()
        self.max_workers = 6  # Reduced for better stability with StartPage
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        title_label = Label(main_frame, text="Company Name to Domain Extractor", 
                           font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 20))
        
        # Input section with file upload
        input_frame = Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(fill=X, pady=(0, 20))
        
        # Single company input
        Label(input_frame, text="Company Name:", font=('Arial', 12), bg='#f0f0f0').pack(anchor=W)
        single_input_frame = Frame(input_frame, bg='#f0f0f0')
        single_input_frame.pack(fill=X, pady=(5, 10))
        
        self.company_entry = Entry(single_input_frame, font=('Arial', 12), width=50)
        self.company_entry.pack(side=LEFT, fill=X, expand=True)
        
        self.search_button = Button(single_input_frame, text="Search", 
                                   command=self.start_search,
                                   font=('Arial', 10), bg='#4CAF50', fg='white',
                                   padx=15, pady=5)
        self.search_button.pack(side=RIGHT, padx=(10, 0))
        
        # File upload section
        file_frame = Frame(input_frame, bg='#f0f0f0')
        file_frame.pack(fill=X, pady=(10, 0))
        
        Label(file_frame, text="Or upload company names file (CSV/TXT):", 
              font=('Arial', 12), bg='#f0f0f0').pack(anchor=W)
        
        upload_frame = Frame(file_frame, bg='#f0f0f0')
        upload_frame.pack(fill=X, pady=(5, 0))
        
        self.file_label = Label(upload_frame, text="No file selected", 
                               font=('Arial', 10), bg='#f0f0f0', fg='gray')
        self.file_label.pack(side=LEFT, fill=X, expand=True)
        
        self.upload_button = Button(upload_frame, text="Browse File", 
                                  command=self.upload_file,
                                  font=('Arial', 10), bg='#FF9800', fg='white',
                                  padx=15, pady=5)
        self.upload_button.pack(side=RIGHT, padx=(10, 0))
        
        self.batch_button = Button(upload_frame, text="Process All Companies", 
                                  command=self.start_batch_search,
                                  font=('Arial', 10), bg='#9C27B0', fg='white',
                                  state=DISABLED, padx=15, pady=5)
        self.batch_button.pack(side=RIGHT)
        
        # Progress bar with status
        progress_frame = Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill=X, pady=(0, 20))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=X)
        
        self.status_label = Label(progress_frame, text="Ready", 
                                 font=('Arial', 10), bg='#f0f0f0')
        self.status_label.pack(pady=(5, 0))
        
        # Results section
        results_frame = Frame(main_frame, bg='#f0f0f0')
        results_frame.pack(fill=BOTH, expand=True)
        
        Label(results_frame, text="Results:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor=W)
        
        # Treeview for results
        columns = ('Company', 'Domain', 'Source', 'Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == 'Company':
                self.results_tree.column(col, width=150)
            elif col == 'Domain':
                self.results_tree.column(col, width=200)
            elif col == 'Source':
                self.results_tree.column(col, width=150)
            else:
                self.results_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Export buttons
        button_frame = Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=X, pady=(20, 0))
        
        self.export_button = Button(button_frame, text="Export to CSV", 
                                   command=self.export_to_csv,
                                   font=('Arial', 10), bg='#2196F3', fg='white',
                                   state=DISABLED, padx=15, pady=8)
        self.export_button.pack(side=LEFT, padx=(0, 10))
        
        self.clear_button = Button(button_frame, text="Clear Results", 
                                  command=self.clear_results,
                                  font=('Arial', 10), bg='#f44336', fg='white',
                                  padx=15, pady=8)
        self.clear_button.pack(side=LEFT, padx=(0, 10))
        
        self.stop_button = Button(button_frame, text="Stop Batch", 
                                 command=self.stop_batch,
                                 font=('Arial', 10), bg='#795548', fg='white',
                                 state=DISABLED, padx=15, pady=8)
        self.stop_button.pack(side=LEFT)
        
        # Speed control with Super Fast mode
        speed_frame = Frame(button_frame, bg='#f0f0f0')
        speed_frame.pack(side=RIGHT, padx=(10, 0))
        
        Label(speed_frame, text="Speed:", font=('Arial', 9), bg='#f0f0f0').pack(side=LEFT)
        self.speed_var = StringVar(value="Fast")
        self.speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                       values=["Super Fast", "Fast", "Medium", "Slow"], width=10, state="readonly")
        self.speed_combo.pack(side=LEFT, padx=(5, 0))
        self.speed_combo.bind("<<ComboboxSelected>>", self.update_speed)
    
    def start_search(self):
        if self.is_searching:
            messagebox.showwarning("Warning", "Search already in progress!")
            return
        
        company_name = self.company_entry.get().strip()
        if not company_name:
            messagebox.showwarning("Warning", "Please enter a company name!")
            return
        
        self.is_searching = True
        self.search_button.config(state=DISABLED, text="Searching...")
        self.progress.config(mode='indeterminate')
        self.progress.start()
        self.status_label.config(text=f"Searching for {company_name}...")
        
        # Run search in separate thread
        thread = threading.Thread(target=self.search_company, args=(company_name,))
        thread.daemon = True
        thread.start()
    
    def search_company(self, company_name):
        try:
            domains = self.extract_domains_from_search(company_name)
            
            # Update UI in main thread
            self.root.after(0, self.update_results, company_name, domains)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.finish_search)
    
    def extract_domains_from_search(self, company_name):
        domains = []
        
        # Comprehensive search queries for Alaska-style companies
        search_queries = [
            f"{company_name} official website",
            f"{company_name} .com",
            f"{company_name} .net",
            f"{company_name} LLC",
            f"{company_name} Inc",
            f"{company_name} Alaska",
            f"www.{company_name.lower().replace(' ', '')}",
            f"{company_name.lower().replace(' ', '')}.com",
            f"{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}",
            f"{company_name.replace(',', '').replace('.', '')}"
        ]
        
        # Try direct domain patterns first (fastest)
        direct_domains = self.generate_direct_domains(company_name)
        domains.extend(direct_domains)
        
        # Use all CAPTCHA-free search engines for maximum coverage
        search_engines = [
            "https://www.startpage.com/do/search?query=",
            "https://duckduckgo.com/html/?q=",
            "https://search.brave.com/search?q=",
            "https://searx.be/search?q=",
            "https://swisscows.com/en/web?query=",
            "https://yandex.com/search/?text="
        ]
        
        # Concurrent search execution with maximum workers for super fast mode
        max_search_workers = 8 if self.speed_var.get() == "Fast" else 6
        with ThreadPoolExecutor(max_workers=max_search_workers) as executor:
            futures = []
            
            for query in search_queries:
                for engine in search_engines:
                    future = executor.submit(self.search_single_engine, engine, query)
                    futures.append(future)
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    found_domains = future.result(timeout=8)
                    if found_domains:
                        domains.extend(found_domains)
                except Exception:
                    continue
        
        # Remove duplicates and validate domains
        unique_domains = []
        seen = set()
        
        for domain, source in domains:
            if domain not in seen and self.is_valid_domain(domain):
                seen.add(domain)
                unique_domains.append((domain, source))
        
        return unique_domains[:25]  # Increased limit for comprehensive results
    
    def search_single_engine(self, engine, query):
        try:
            search_url = engine + requests.utils.quote(query)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                found_domains = self.extract_domains_from_html(soup)
                
                # Enhanced domain extraction for StartPage
                if 'startpage.com' in engine:
                    found_domains.extend(self.extract_startpage_domains(soup))
                
                return [(domain, f"Search: {engine.split('/')[2]}") for domain in found_domains]
        except Exception:
            pass
        return []
    
    def extract_startpage_domains(self, soup):
        """Enhanced domain extraction specifically for StartPage results"""
        domains = []
        
        # Look for StartPage specific result containers
        results = soup.find_all('div', class_='w-gl__result')
        if not results:
            results = soup.find_all('div', {'class': lambda x: x and 'result' in x.lower()})
        
        for result in results:
            # Extract from main link
            link = result.find('a', href=True)
            if link:
                href = link['href']
                domain = self.extract_domain_from_url(href)
                if domain and domain not in domains:
                    domains.append(domain)
            
            # Extract from citation URLs (often contain domains)
            cite = result.find('cite')
            if cite:
                cite_text = cite.get_text()
                # Extract domain from citation text
                domain_match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', cite_text)
                if domain_match:
                    domain = domain_match.group(1).lower()
                    if domain not in domains and self.is_valid_domain(domain):
                        domains.append(domain)
        
        # Fallback: look for any text that looks like URLs
        text_content = soup.get_text()
        url_patterns = [
            r'\bhttps?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            r'\bwww\.([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            r'\b([a-zA-Z0-9.-]+\.(com|org|net|edu|gov|io|co|us|uk|ca|au|de|fr|jp|cn|in|br|mx))\b'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    domain = match[0] if match[0] else match[1]
                else:
                    domain = match
                
                domain = domain.lower()
                if domain not in domains and self.is_valid_domain(domain):
                    domains.append(domain)
        
        return domains
    
    def generate_direct_domains(self, company_name):
        domains = []
        # Enhanced domain pattern generation for Alaska-style companies
        name_parts = company_name.lower().replace('&', '').replace(',', '').replace('.', '').replace('llc', '').replace('inc', '').replace('the', '').split()
        name_parts = [part for part in name_parts if part]  # Remove empty strings
        
        if not name_parts:
            return domains
        
        # Comprehensive domain patterns based on your examples
        patterns = []
        
        # Basic patterns
        base_name = ''.join(name_parts)
        hyphen_name = '-'.join(name_parts)
        
        # Alaska-specific patterns (from your examples)
        if 'alaska' in company_name.lower():
            patterns.extend([
                f"{base_name}ak.com",
                f"{hyphen_name}ak.com",
                f"alaska{base_name}.com",
                f"{base_name}alaska.com"
            ])
        
        # Electric/Contractor specific patterns
        if any(word in company_name.lower() for word in ['electric', 'electrical', 'contractor']):
            patterns.extend([
                f"{base_name}electric.com",
                f"{hyphen_name}electric.com",
                f"{base_name}electrical.com",
                f"{base_name}contractors.com",
                f"{base_name}llc.com",
                f"{base_name}inc.com"
            ])
        
        # Standard patterns
        patterns.extend([
            f"{base_name}.com",
            f"{hyphen_name}.com",
            f"{base_name}.net",
            f"{hyphen_name}.net",
            f"{base_name}.org",
            f"{hyphen_name}.org"
        ])
        
        # Number patterns (like 907 Electric)
        number_match = re.search(r'\b(\d{3})\b', company_name)
        if number_match:
            number = number_match.group(1)
            remaining_name = company_name.lower().replace(number, '').strip()
            remaining_parts = remaining_name.replace('&', '').replace(',', '').replace('.', '').split()
            remaining_parts = [part for part in remaining_parts if part]
            
            if remaining_parts:
                remaining_base = ''.join(remaining_parts)
                patterns.extend([
                    f"{number}{remaining_base}.com",
                    f"{number}{remaining_base}ak.com"
                ])
        
        # Remove duplicates and check concurrently
        unique_patterns = list(set(patterns))
        
        # Fast concurrent domain checking
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self.check_domain_exists_fast, pattern): pattern for pattern in unique_patterns}
            
            for future in as_completed(futures):
                pattern = futures[future]
                try:
                    if future.result(timeout=2):
                        domains.append((pattern, "Direct Pattern"))
                except Exception:
                    continue
        
        return domains
    
    def check_domain_exists_fast(self, domain):
        """Ultra-fast domain existence check"""
        try:
            # Try HTTPS first (faster for modern sites)
            url = f"https://{domain}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.head(url, headers=headers, timeout=1.5, allow_redirects=True)
            if response.status_code in [200, 301, 302, 403, 404]:
                return True
            
            # Fallback to HTTP if HTTPS fails
            url = f"http://{domain}"
            response = requests.head(url, headers=headers, timeout=1.5, allow_redirects=True)
            return response.status_code in [200, 301, 302, 403, 404]
            
        except:
            return False
    
    def check_domain_exists(self, domain):
        try:
            # Fast HTTP check with optimized headers
            url = f"https://{domain}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Connection': 'keep-alive'
            }
            
            response = requests.head(url, headers=headers, timeout=2, allow_redirects=True)
            return response.status_code in [200, 301, 302, 403, 404]  # 404 might mean domain exists but no website
            
        except:
            return False
    
    def extract_domains_from_html(self, soup):
        domains = []
        
        # Enhanced link extraction
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            domain = self.extract_domain_from_url(href)
            if domain and domain not in domains:
                domains.append(domain)
        
        # Enhanced text extraction with more patterns
        text_content = soup.get_text()
        
        # Comprehensive domain patterns
        domain_patterns = [
            r'\b[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|io|co|us|uk|ca|au|de|fr|jp|cn|in|br|mx|info|biz|online|site|tech|store|app)\b',
            r'\bwww\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            r'\bhttps?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        ]
        
        for pattern in domain_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    domain = match[0] if match[0] else match[1]
                else:
                    domain = match
                
                domain = domain.lower()
                if domain not in domains and self.is_valid_domain(domain):
                    domains.append(domain)
        
        # Look for structured data and meta tags
        meta_tags = soup.find_all('meta', property=True)
        for meta in meta_tags:
            if meta.get('property') in ['og:url', 'twitter:url', 'al:web:url']:
                content = meta.get('content', '')
                domain = self.extract_domain_from_url(content)
                if domain and domain not in domains:
                    domains.append(domain)
        
        # Look for script tags that might contain URLs
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string
                url_matches = re.findall(r'"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"', script_content)
                for match in url_matches:
                    domain = match.lower()
                    if domain not in domains and self.is_valid_domain(domain):
                        domains.append(domain)
        
        return domains
    
    def extract_domain_from_url(self, url):
        try:
            if url.startswith('http'):
                parsed = urlparse(url)
                return parsed.netloc.lower()
            elif '.' in url and '/' not in url:
                return url.lower()
            return None
        except:
            return None
    
    def is_valid_domain(self, domain):
        if not domain:
            return False
        
        # Basic domain validation
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain)) and len(domain) <= 253
    
    def update_results(self, company_name, domains):
        # Clear previous results for this company
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Add new results
        for domain, source in domains:
            self.results_tree.insert('', 'end', values=(company_name, domain, source, "Found"))
            self.results.append({'Company': company_name, 'Domain': domain, 'Source': source, 'Status': 'Found'})
        
        self.export_button.config(state=NORMAL if domains else DISABLED)
    
    def show_error(self, error_message):
        messagebox.showerror("Error", f"An error occurred: {error_message}")
    
    def finish_search(self):
        self.is_searching = False
        self.search_button.config(state=NORMAL, text="Search")
        self.progress.stop()
        self.status_label.config(text="Ready")
    
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select Company Names File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                companies = self.read_company_file(filename)
                if companies:
                    self.companies_to_process = companies
                    self.file_label.config(text=f"{len(companies)} companies loaded")
                    self.batch_button.config(state=NORMAL)
                    messagebox.showinfo("Success", f"Loaded {len(companies)} companies from file")
                else:
                    messagebox.showwarning("Warning", "No valid company names found in file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def read_company_file(self, filename):
        companies = []
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
                # Try common column names
                for col in ['company', 'Company', 'name', 'Name', 'company_name', 'Company Name']:
                    if col in df.columns:
                        companies = [str(name).strip() for name in df[col].dropna() if str(name).strip()]
                        break
                
                # If no named columns found, use first column
                if not companies and len(df.columns) > 0:
                    companies = [str(name).strip() for name in df.iloc[:, 0].dropna() if str(name).strip()]
            else:
                # Text file - one company per line
                with open(filename, 'r', encoding='utf-8') as f:
                    companies = [line.strip() for line in f if line.strip()]
            
            # Filter out empty strings and clean up
            companies = [company for company in companies if company and len(company) > 1]
            
        except Exception as e:
            print(f"Error reading file: {e}")
            
        return companies
    
    def start_batch_search(self):
        if not self.companies_to_process:
            messagebox.showwarning("Warning", "No companies loaded!")
            return
        
        if self.is_searching:
            messagebox.showwarning("Warning", "Search already in progress!")
            return
        
        self.is_searching = True
        self.current_batch_index = 0
        self.total_companies = len(self.companies_to_process)
        
        # Disable buttons during batch processing
        self.search_button.config(state=DISABLED)
        self.batch_button.config(state=DISABLED)
        self.upload_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        
        # Configure progress bar for batch
        self.progress.config(mode='determinate', maximum=self.total_companies)
        self.progress['value'] = 0
        
        # Start batch processing
        thread = threading.Thread(target=self.process_batch_companies)
        thread.daemon = True
        thread.start()
    
    def process_batch_companies(self):
        try:
            # Get speed setting
            speed_delay = {'Fast': 0.5, 'Medium': 1.0, 'Slow': 2.0}.get(self.speed_var.get(), 1.0)
            
            # Use ThreadPoolExecutor for concurrent processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all companies for processing
                future_to_company = {
                    executor.submit(self.search_company_safe, company_name): company_name 
                    for company_name in self.companies_to_process
                }
                
                completed = 0
                # Process results as they complete
                for future in as_completed(future_to_company):
                    if not self.is_searching:  # Check if stopped
                        break
                    
                    company_name = future_to_company[future]
                    completed += 1
                    
                    # Update progress
                    self.root.after(0, self.update_batch_progress, completed, company_name)
                    
                    try:
                        domains = future.result(timeout=15)
                        self.root.after(0, self.add_batch_results, company_name, domains)
                    except Exception as e:
                        self.root.after(0, self.add_batch_error, company_name, str(e))
                    
                    # Dynamic rate limiting based on speed setting
                    if speed_delay > 0:
                        time.sleep(speed_delay / self.max_workers)
            
            # Batch completed
            self.root.after(0, self.finish_batch_search)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def search_company_safe(self, company_name):
        """Thread-safe version of search_company"""
        try:
            return self.extract_domains_from_search(company_name)
        except Exception as e:
            print(f"Error searching {company_name}: {e}")
            return []
    
    def update_batch_progress(self, current, company_name):
        self.progress['value'] = current
        self.status_label.config(text=f"Processing {current}/{self.total_companies}: {company_name}")
    
    def add_batch_results(self, company_name, domains):
        if domains:
            for domain, source in domains:
                self.results_tree.insert('', 'end', values=(company_name, domain, source, "Found"))
                self.results.append({'Company': company_name, 'Domain': domain, 'Source': source, 'Status': 'Found'})
        else:
            self.results_tree.insert('', 'end', values=(company_name, "No domains found", "N/A", "Not Found"))
            self.results.append({'Company': company_name, 'Domain': 'No domains found', 'Source': 'N/A', 'Status': 'Not Found'})
        
        self.export_button.config(state=NORMAL)
    
    def add_batch_error(self, company_name, error):
        self.results_tree.insert('', 'end', values=(company_name, f"Error: {error}", "N/A", "Error"))
        self.results.append({'Company': company_name, 'Domain': f"Error: {error}", 'Source': 'N/A', 'Status': 'Error'})
    
    def finish_batch_search(self):
        self.is_searching = False
        self.search_button.config(state=NORMAL)
        self.batch_button.config(state=NORMAL)
        self.upload_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)
        self.status_label.config(text=f"Batch completed: {self.total_companies} companies processed")
        messagebox.showinfo("Batch Complete", f"Processed {self.total_companies} companies")
    
    def stop_batch(self):
        self.is_searching = False
        if self.executor:
            self.executor.shutdown(wait=False)
        self.finish_batch_search()
        self.status_label.config(text="Batch stopped by user")
    
    def update_speed(self, event=None):
        # Adjust max workers based on speed setting
        speed = self.speed_var.get()
        if speed == "Super Fast":
            self.max_workers = 15  # Maximum concurrency
        elif speed == "Fast":
            self.max_workers = 10
        elif speed == "Medium":
            self.max_workers = 6
        else:  # Slow
            self.max_workers = 4
    
    def export_to_csv(self):
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
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def clear_results(self):
        self.results_tree.delete(*self.results_tree.get_children())
        self.results = []
        self.export_button.config(state=DISABLED)
        self.company_entry.delete(0, END)
        self.companies_to_process = []
        self.file_label.config(text="No file selected")
        self.batch_button.config(state=DISABLED)
        self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = Tk()
    app = CompanyDomainExtractor(root)
    root.mainloop()
