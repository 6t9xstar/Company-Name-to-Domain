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
import json
import os

class ProfessionalDomainExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Domain Extractor - Ultra Fast")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Professional color scheme
        self.colors = {
            'bg': '#2c3e50',
            'fg': '#ecf0f1',
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'accent': '#9b59b6'
        }
        
        # Core variables
        self.results = []
        self.is_searching = False
        self.companies_to_process = []
        self.total_companies = 0
        self.processed_companies = 0
        self.session_stats = {
            'total_searched': 0,
            'domains_found': 0,
            'start_time': None,
            'errors': 0
        }
        
        # Performance settings
        self.speed_settings = {
            'Ultra Fast': {'workers': 20, 'timeout': 1, 'delay': 0.1},
            'Super Fast': {'workers': 15, 'timeout': 1.5, 'delay': 0.2},
            'Fast': {'workers': 10, 'timeout': 2, 'delay': 0.5},
            'Medium': {'workers': 6, 'timeout': 3, 'delay': 1},
            'Slow': {'workers': 4, 'timeout': 5, 'delay': 2}
        }
        
        self.current_speed = 'Fast'
        
        # Optimized search engines (reliable and fast)
        self.search_engines = [
            {'name': 'DuckDuckGo', 'url': 'https://duckduckgo.com/html/?q=', 'priority': 1},
            {'name': 'Brave', 'url': 'https://search.brave.com/search?q=', 'priority': 2},
            {'name': 'StartPage', 'url': 'https://www.startpage.com/do/search?query=', 'priority': 3}
        ]
        
        self.setup_professional_ui()
        
    def setup_professional_ui(self):
        # Main container
        main_frame = Frame(self.root, bg=self.colors['bg'], padx=30, pady=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Control section
        self.create_control_section(main_frame)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self, parent):
        header_frame = Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        title_label = Label(header_frame, 
                          text="🚀 PROFESSIONAL DOMAIN EXTRACTOR", 
                          font=('Arial', 18, 'bold'),
                          bg=self.colors['bg'], fg=self.colors['primary'])
        title_label.pack(side=LEFT)
        
        # Stats display
        self.stats_label = Label(header_frame, 
                               text="Ready | 0 processed | 0 domains found",
                               font=('Arial', 10),
                               bg=self.colors['bg'], fg=self.colors['fg'])
        self.stats_label.pack(side=RIGHT)
    
    def create_input_section(self, parent):
        input_frame = Frame(parent, bg=self.colors['bg'])
        input_frame.pack(fill=X, pady=(0, 20))
        
        # Single company input
        Label(input_frame, text="Company Name:", 
              font=('Arial', 12, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=W)
        
        single_input = Frame(input_frame, bg=self.colors['bg'])
        single_input.pack(fill=X, pady=(5, 10))
        
        self.company_entry = Entry(single_input, 
                                 font=('Arial', 12),
                                 bg='#34495e', fg=self.colors['fg'],
                                 insertbackground=self.colors['fg'])
        self.company_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        self.search_single_btn = Button(single_input, 
                                       text="🔍 Search",
                                       command=self.search_single_company,
                                       font=('Arial', 10, 'bold'),
                                       bg=self.colors['primary'], fg='white',
                                       padx=20, pady=8)
        self.search_single_btn.pack(side=RIGHT)
        
        # File upload section
        file_frame = Frame(input_frame, bg=self.colors['bg'])
        file_frame.pack(fill=X)
        
        Label(file_frame, text="📁 Batch Processing:", 
              font=('Arial', 12, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=W)
        
        file_controls = Frame(file_frame, bg=self.colors['bg'])
        file_controls.pack(fill=X, pady=(5, 0))
        
        self.file_label = Label(file_controls, 
                               text="No file selected",
                               font=('Arial', 10),
                               bg=self.colors['bg'], fg=self.colors['warning'])
        self.file_label.pack(side=LEFT, fill=X, expand=True)
        
        self.upload_btn = Button(file_controls, 
                                text="📂 Upload File",
                                command=self.upload_file,
                                font=('Arial', 10, 'bold'),
                                bg=self.colors['accent'], fg='white',
                                padx=15, pady=6)
        self.upload_btn.pack(side=RIGHT, padx=(10, 5))
        
        self.batch_btn = Button(file_controls, 
                               text="⚡ Process All",
                               command=self.start_batch_processing,
                               font=('Arial', 10, 'bold'),
                               bg=self.colors['success'], fg='white',
                               state=DISABLED, padx=15, pady=6)
        self.batch_btn.pack(side=RIGHT)
    
    def create_progress_section(self, parent):
        progress_frame = Frame(parent, bg=self.colors['bg'])
        progress_frame.pack(fill=X, pady=(0, 20))
        
        # Speed control
        speed_frame = Frame(progress_frame, bg=self.colors['bg'])
        speed_frame.pack(fill=X, pady=(0, 10))
        
        Label(speed_frame, text="⚡ Speed:", 
              font=('Arial', 11, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(side=LEFT)
        
        self.speed_var = StringVar(value='Fast')
        speeds = ['Ultra Fast', 'Super Fast', 'Fast', 'Medium', 'Slow']
        
        for speed in speeds:
            rb = Radiobutton(speed_frame, text=speed, variable=self.speed_var, 
                           value=speed, command=self.update_speed,
                           bg=self.colors['bg'], fg=self.colors['fg'],
                           selectcolor=self.colors['bg'],
                           activebackground=self.colors['bg'])
            rb.pack(side=LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=X, pady=(5, 0))
        
        # Status label
        self.status_label = Label(progress_frame, text="Ready", 
                                font=('Arial', 10),
                                bg=self.colors['bg'], fg=self.colors['fg'])
        self.status_label.pack()
    
    def create_results_section(self, parent):
        results_frame = Frame(parent, bg=self.colors['bg'])
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # Results header
        Label(results_frame, text="📊 Results", 
              font=('Arial', 14, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=W)
        
        # Treeview with scrollbar
        tree_frame = Frame(results_frame, bg=self.colors['bg'])
        tree_frame.pack(fill=BOTH, expand=True)
        
        columns = ('Company', 'Domain', 'Source', 'Status', 'Confidence')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = {'Company': 200, 'Domain': 250, 'Source': 150, 'Status': 100, 'Confidence': 100}
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths.get(col, 150))
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background='#34495e', foreground=self.colors['fg'], 
                       fieldbackground='#34495e', bordercolor='#2c3e50')
        style.configure("Treeview.Heading", background=self.colors['primary'], 
                       foreground='white', font=('Arial', 10, 'bold'))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def create_control_section(self, parent):
        control_frame = Frame(parent, bg=self.colors['bg'])
        control_frame.pack(fill=X)
        
        # Left buttons
        left_frame = Frame(control_frame, bg=self.colors['bg'])
        left_frame.pack(side=LEFT)
        
        self.export_btn = Button(left_frame, 
                                text="💾 Export CSV",
                                command=self.export_results,
                                font=('Arial', 10, 'bold'),
                                bg=self.colors['success'], fg='white',
                                state=DISABLED, padx=15, pady=8)
        self.export_btn.pack(side=LEFT, padx=(0, 10))
        
        self.clear_btn = Button(left_frame, 
                               text="🗑️ Clear",
                               command=self.clear_results,
                               font=('Arial', 10, 'bold'),
                               bg=self.colors['danger'], fg='white',
                               padx=15, pady=8)
        self.clear_btn.pack(side=LEFT)
        
        # Right buttons
        right_frame = Frame(control_frame, bg=self.colors['bg'])
        right_frame.pack(side=RIGHT)
        
        self.stop_btn = Button(right_frame, 
                              text="⏹️ Stop",
                              command=self.stop_processing,
                              font=('Arial', 10, 'bold'),
                              bg=self.colors['warning'], fg='white',
                              state=DISABLED, padx=15, pady=8)
        self.stop_btn.pack(side=RIGHT)
    
    def create_status_bar(self):
        status_frame = Frame(self.root, bg='#1a252f', height=30)
        status_frame.pack(fill=X, side=BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_bar = Label(status_frame, text="Professional Domain Extractor Ready", 
                               font=('Arial', 9),
                               bg='#1a252f', fg='#7f8c8d')
        self.status_bar.pack(fill=X, padx=10, pady=5)
    
    def update_speed(self):
        self.current_speed = self.speed_var.get()
        self.update_status(f"Speed changed to {self.current_speed}")
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def update_stats(self):
        stats_text = f"Processed: {self.processed_companies} | Domains: {self.session_stats['domains_found']} | Errors: {self.session_stats['errors']}"
        self.stats_label.config(text=stats_text)
    
    def search_single_company(self):
        if self.is_searching:
            messagebox.showwarning("Warning", "Search already in progress!")
            return
        
        company_name = self.company_entry.get().strip()
        if not company_name:
            messagebox.showwarning("Warning", "Please enter a company name!")
            return
        
        self.is_searching = True
        self.search_single_btn.config(state=DISABLED, text="🔄 Searching...")
        self.update_status(f"Searching for {company_name}...")
        
        # Run in thread
        thread = threading.Thread(target=self._search_company_thread, args=(company_name,))
        thread.daemon = True
        thread.start()
    
    def _search_company_thread(self, company_name):
        try:
            domains = self.extract_domains_ultra_fast(company_name)
            self.root.after(0, self._add_single_results, company_name, domains)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._finish_single_search)
    
    def _add_single_results(self, company_name, domains):
        # Clear previous single search results
        for item in self.results_tree.get_children():
            if self.results_tree.item(item)['values'][0] == company_name:
                self.results_tree.delete(item)
        
        # Add new results
        for domain, source, confidence in domains:
            self.results_tree.insert('', 'end', values=(company_name, domain, source, "Found", f"{confidence}%"))
            self.results.append({
                'Company': company_name, 
                'Domain': domain, 
                'Source': source, 
                'Status': 'Found',
                'Confidence': confidence
            })
        
        self.session_stats['domains_found'] += len(domains)
        self.update_stats()
        self.export_btn.config(state=NORMAL)
    
    def _finish_single_search(self):
        self.is_searching = False
        self.search_single_btn.config(state=NORMAL, text="🔍 Search")
        self.update_status("Single search completed")
    
    def _show_error(self, error):
        messagebox.showerror("Error", f"An error occurred: {error}")
        self.session_stats['errors'] += 1
        self.update_stats()
    
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select Company Names File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                companies = self._read_company_file(filename)
                if companies:
                    self.companies_to_process = companies
                    self.file_label.config(text=f"📄 {len(companies)} companies loaded", fg=self.colors['success'])
                    self.batch_btn.config(state=NORMAL)
                    self.update_status(f"Loaded {len(companies)} companies from {os.path.basename(filename)}")
                else:
                    messagebox.showwarning("Warning", "No valid company names found in file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def _read_company_file(self, filename):
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
    
    def start_batch_processing(self):
        if not self.companies_to_process:
            messagebox.showwarning("Warning", "No companies loaded!")
            return
        
        if self.is_searching:
            messagebox.showwarning("Warning", "Processing already in progress!")
            return
        
        self.is_searching = True
        self.total_companies = len(self.companies_to_process)
        self.processed_companies = 0
        self.session_stats['start_time'] = time.time()
        
        # Update UI
        self.batch_btn.config(state=DISABLED)
        self.upload_btn.config(state=DISABLED)
        self.search_single_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        
        # Configure progress bar
        self.progress.config(mode='determinate', maximum=self.total_companies)
        self.progress['value'] = 0
        
        self.update_status(f"Starting batch processing of {self.total_companies} companies...")
        
        # Start processing
        thread = threading.Thread(target=self._batch_processing_thread)
        thread.daemon = True
        thread.start()
    
    def _batch_processing_thread(self):
        settings = self.speed_settings[self.current_speed]
        
        with ThreadPoolExecutor(max_workers=settings['workers']) as executor:
            # Submit all companies
            future_to_company = {
                executor.submit(self.extract_domains_ultra_fast, company): company 
                for company in self.companies_to_process
            }
            
            # Process results as they complete
            for future in as_completed(future_to_company):
                if not self.is_searching:
                    break
                
                company_name = future_to_company[future]
                self.processed_companies += 1
                
                # Update progress
                self.root.after(0, self._update_batch_progress, self.processed_companies, company_name)
                
                try:
                    domains = future.result(timeout=settings['timeout'] * 3)
                    self.root.after(0, self._add_batch_results, company_name, domains)
                except Exception as e:
                    self.root.after(0, self._add_batch_error, company_name, str(e))
                
                # Rate limiting
                if settings['delay'] > 0:
                    time.sleep(settings['delay'])
        
        # Batch completed
        self.root.after(0, self._finish_batch_processing)
    
    def _update_batch_progress(self, current, company_name):
        self.progress['value'] = current
        self.status_label.config(text=f"Processing {current}/{self.total_companies}: {company_name}")
        self.update_stats()
    
    def _add_batch_results(self, company_name, domains):
        if domains:
            for domain, source, confidence in domains:
                self.results_tree.insert('', 'end', values=(company_name, domain, source, "Found", f"{confidence}%"))
                self.results.append({
                    'Company': company_name, 
                    'Domain': domain, 
                    'Source': source, 
                    'Status': 'Found',
                    'Confidence': confidence
                })
            self.session_stats['domains_found'] += len(domains)
        else:
            self.results_tree.insert('', 'end', values=(company_name, "No domains found", "N/A", "Not Found", "0%"))
            self.results.append({
                'Company': company_name, 
                'Domain': 'No domains found', 
                'Source': 'N/A', 
                'Status': 'Not Found',
                'Confidence': 0
            })
        
        self.export_btn.config(state=NORMAL)
    
    def _add_batch_error(self, company_name, error):
        self.results_tree.insert('', 'end', values=(company_name, f"Error: {error}", "N/A", "Error", "0%"))
        self.results.append({
            'Company': company_name, 
            'Domain': f"Error: {error}", 
            'Source': 'N/A', 
            'Status': 'Error',
            'Confidence': 0
        })
        self.session_stats['errors'] += 1
    
    def _finish_batch_processing(self):
        self.is_searching = False
        self.batch_btn.config(state=NORMAL)
        self.upload_btn.config(state=NORMAL)
        self.search_single_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
        elapsed_time = time.time() - self.session_stats['start_time'] if self.session_stats['start_time'] else 0
        self.update_status(f"Batch completed in {elapsed_time:.1f}s | {self.total_companies} companies processed")
        messagebox.showinfo("Batch Complete", f"Processed {self.total_companies} companies\\nFound {self.session_stats['domains_found']} domains\\nTime: {elapsed_time:.1f} seconds")
    
    def stop_processing(self):
        self.is_searching = False
        self._finish_batch_processing()
        self.update_status("Processing stopped by user")
    
    def extract_domains_ultra_fast(self, company_name):
        """Ultra-fast domain extraction with optimized patterns"""
        domains = []
        
        # Generate direct domain patterns (fastest method)
        direct_domains = self._generate_smart_patterns(company_name)
        domains.extend(direct_domains)
        
        # Search engines only if no direct domains found
        if len(domains) < 3:
            search_domains = self._search_engines_fast(company_name)
            domains.extend(search_domains)
        
        # Remove duplicates and add confidence scores
        unique_domains = []
        seen = set()
        
        for domain_data in domains:
            if isinstance(domain_data, tuple):
                domain, source = domain_data
                confidence = 95 if source == "Direct Pattern" else 80
            else:
                domain = domain_data
                source = "Unknown"
                confidence = 70
            
            if domain not in seen and self._is_valid_domain(domain):
                seen.add(domain)
                unique_domains.append((domain, source, confidence))
        
        return unique_domains[:15]  # Top 15 results
    
    def _generate_smart_patterns(self, company_name):
        """Generate intelligent domain patterns based on company name"""
        patterns = []
        
        # Clean company name
        clean_name = company_name.lower()
        clean_name = re.sub(r'[^\w\s]', '', clean_name)  # Remove special chars
        clean_name = re.sub(r'\b(llc|inc|ltd|corp|corporation|the|and|&)\b', '', clean_name)  # Remove common words
        clean_name = ' '.join(clean_name.split())  # Normalize spaces
        
        words = clean_name.split()
        if not words:
            return patterns
        
        # Generate patterns
        base_patterns = [
            ''.join(words),  # companyname
            '-'.join(words),  # company-name
            words[0],  # company
        ]
        
        # Add common suffixes
        suffixes = ['.com', '.net', '.org', '.io']
        
        # Special patterns for Alaska/electric companies
        if 'alaska' in company_name.lower():
            for base in base_patterns:
                patterns.append(f"{base}ak.com")
                patterns.append(f"alaska{base}.com")
        
        if any(word in company_name.lower() for word in ['electric', 'electrical', 'contractor']):
            for base in base_patterns:
                patterns.append(f"{base}electric.com")
                patterns.append(f"{base}electrical.com")
        
        # Number patterns (like 907 Electric)
        number_match = re.search(r'\b(\d{3})\b', company_name)
        if number_match:
            number = number_match.group(1)
            remaining = company_name.lower().replace(number, '').strip()
            remaining_clean = re.sub(r'[^\w\s]', '', remaining).split()
            if remaining_clean:
                patterns.append(f"{number}{''.join(remaining_clean)}.com")
        
        # Standard patterns
        for base in base_patterns:
            for suffix in suffixes:
                patterns.append(base + suffix)
        
        # Check domains concurrently
        valid_domains = []
        settings = self.speed_settings[self.current_speed]
        
        with ThreadPoolExecutor(max_workers=min(10, settings['workers'])) as executor:
            future_to_pattern = {
                executor.submit(self._check_domain_fast, pattern): pattern 
                for pattern in patterns
            }
            
            for future in as_completed(future_to_pattern):
                pattern = future_to_pattern[future]
                try:
                    if future.result(timeout=settings['timeout']):
                        valid_domains.append((pattern, "Direct Pattern"))
                except:
                    continue
        
        return valid_domains
    
    def _check_domain_fast(self, domain):
        """Ultra-fast domain existence check"""
        try:
            settings = self.speed_settings[self.current_speed]
            
            # Try HTTPS first
            url = f"https://{domain}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Connection': 'keep-alive'
            }
            
            response = requests.head(url, headers=headers, timeout=settings['timeout'], allow_redirects=True)
            if response.status_code in [200, 301, 302, 403, 404]:
                return True
            
            # Fallback to HTTP
            url = f"http://{domain}"
            response = requests.head(url, headers=headers, timeout=settings['timeout'], allow_redirects=True)
            return response.status_code in [200, 301, 302, 403, 404]
            
        except:
            return False
    
    def _search_engines_fast(self, company_name):
        """Fast search engine extraction"""
        domains = []
        settings = self.speed_settings[self.current_speed]
        
        # Simple queries only
        queries = [f"{company_name} official website", f"{company_name} .com"]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for engine in self.search_engines[:2]:  # Use only top 2 engines for speed
                for query in queries:
                    future = executor.submit(self._search_single_engine, engine, query, settings['timeout'])
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    found = future.result(timeout=settings['timeout'] * 2)
                    domains.extend(found)
                except:
                    continue
        
        return domains
    
    def _search_single_engine(self, engine, query, timeout):
        """Single engine search with timeout"""
        try:
            url = engine['url'] + requests.utils.quote(query)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                found_domains = self._extract_domains_from_html(soup)
                return [(domain, f"Search: {engine['name']}") for domain in found_domains[:5]]
        except:
            pass
        return []
    
    def _extract_domains_from_html(self, soup):
        """Extract domains from HTML content"""
        domains = []
        
        # Extract from links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            domain = self._extract_domain_from_url(href)
            if domain and domain not in domains:
                domains.append(domain)
        
        # Extract from text
        text = soup.get_text()
        domain_pattern = r'\b[a-zA-Z0-9.-]+\.(com|org|net|io|gov|edu|co|us|uk|ca|au)\b'
        matches = re.findall(domain_pattern, text, re.IGNORECASE)
        
        for match in matches:
            if isinstance(match, tuple):
                domain = match[0]
            else:
                domain = match
            
            domain = domain.lower()
            if domain not in domains and self._is_valid_domain(domain):
                domains.append(domain)
        
        return domains[:10]
    
    def _extract_domain_from_url(self, url):
        """Extract domain from URL"""
        try:
            if url.startswith('http'):
                parsed = urlparse(url)
                return parsed.netloc.lower()
            elif '.' in url and '/' not in url:
                return url.lower()
        except:
            pass
        return None
    
    def _is_valid_domain(self, domain):
        """Validate domain format"""
        if not domain or len(domain) > 253:
            return False
        
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def export_results(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"domains_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Results exported to {filename}")
                self.update_status(f"Exported {len(self.results)} results to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def clear_results(self):
        self.results_tree.delete(*self.results_tree.get_children())
        self.results = []
        self.companies_to_process = []
        self.processed_companies = 0
        self.session_stats = {
            'total_searched': 0,
            'domains_found': 0,
            'start_time': None,
            'errors': 0
        }
        
        self.export_btn.config(state=DISABLED)
        self.file_label.config(text="No file selected", fg=self.colors['warning'])
        self.batch_btn.config(state=DISABLED)
        self.progress['value'] = 0
        self.update_stats()
        self.update_status("Results cleared")

if __name__ == "__main__":
    root = Tk()
    app = ProfessionalDomainExtractor(root)
    root.mainloop()
