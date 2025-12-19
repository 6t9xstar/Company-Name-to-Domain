import requests
import re
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json
import os
from urllib.robotparser import RobotFileParser
import random

class FinalPerfectDomainExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("🏗️ Final Perfect Domain Extractor - Construction Industry")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Professional construction theme
        self.colors = {
            'bg': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#e94560',
            'primary': '#0f3460',
            'success': '#00adb5',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'fg': '#eeeeee',
            'light': '#f5f5f5'
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
            'urls_extracted': 0,
            'start_time': None,
            'errors': 0
        }
        
        # Construction industry keywords for better extraction
        self.construction_keywords = [
            'construction', 'contractor', 'builders', 'building', 'remodeling',
            'electric', 'electrical', 'plumbing', 'hvac', 'roofing', 'concrete',
            'excavation', 'demolition', 'framing', 'carpentry', 'painting',
            'landscaping', 'foundation', 'structural', 'civil', 'industrial',
            'commercial', 'residential', 'general', 'specialty', 'subcontractor'
        ]
        
        # Performance settings
        self.speed_settings = {
            'Ultra Fast': {'workers': 25, 'timeout': 2, 'delay': 0.1, 'searches': 2},
            'Super Fast': {'workers': 20, 'timeout': 3, 'delay': 0.2, 'searches': 3},
            'Fast': {'workers': 15, 'timeout': 4, 'delay': 0.5, 'searches': 3},
            'Medium': {'workers': 10, 'timeout': 6, 'delay': 1, 'searches': 4},
            'Slow': {'workers': 6, 'timeout': 8, 'delay': 2, 'searches': 4}
        }
        
        self.current_speed = 'Fast'
        
        # Premium search engines for construction industry
        self.search_engines = [
            {
                'name': 'DuckDuckGo',
                'url': 'https://duckduckgo.com/html/?q=',
                'result_selector': 'div.result',
                'link_selector': 'a.result__a',
                'priority': 1
            },
            {
                'name': 'Brave Search',
                'url': 'https://search.brave.com/search?q=',
                'result_selector': 'div.web-result',
                'link_selector': 'a.web-result-header',
                'priority': 2
            },
            {
                'name': 'StartPage',
                'url': 'https://www.startpage.com/do/search?query=',
                'result_selector': 'div.w-gl__result',
                'link_selector': 'h3 a',
                'priority': 3
            },
            {
                'name': 'SearX',
                'url': 'https://searx.be/search?q=',
                'result_selector': 'div.result',
                'link_selector': 'h3 a',
                'priority': 4
            }
        ]
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        
        self.setup_final_ui()
        
    def setup_final_ui(self):
        # Main container
        main_frame = Frame(self.root, bg=self.colors['bg'], padx=40, pady=40)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Header
        self.create_final_header(main_frame)
        
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
    
    def create_final_header(self, parent):
        header_frame = Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=X, pady=(0, 25))
        
        # Title with construction theme
        title_frame = Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side=LEFT)
        
        title_label = Label(title_frame, 
                          text="🏗️ FINAL PERFECT DOMAIN EXTRACTOR", 
                          font=('Arial', 20, 'bold'),
                          bg=self.colors['bg'], fg=self.colors['accent'])
        title_label.pack()
        
        subtitle_label = Label(title_frame, 
                              text="Construction Industry - Real-time Search Engine Extraction",
                              font=('Arial', 11),
                              bg=self.colors['bg'], fg=self.colors['success'])
        subtitle_label.pack()
        
        # Real-time stats
        self.stats_label = Label(header_frame, 
                               text="🏗️ Ready | 0 processed | 0 domains | 0 URLs extracted",
                               font=('Arial', 11, 'bold'),
                               bg=self.colors['bg'], fg=self.colors['success'])
        self.stats_label.pack(side=RIGHT)
    
    def create_input_section(self, parent):
        input_frame = Frame(parent, bg=self.colors['bg'])
        input_frame.pack(fill=X, pady=(0, 25))
        
        # Single company input
        Label(input_frame, text="🏢 Construction Company Name:", 
              font=('Arial', 14, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=W, pady=(0, 10))
        
        single_input = Frame(input_frame, bg=self.colors['bg'])
        single_input.pack(fill=X, pady=(0, 15))
        
        self.company_entry = Entry(single_input, 
                                 font=('Arial', 13),
                                 bg=self.colors['secondary'], fg=self.colors['fg'],
                                 insertbackground=self.colors['fg'],
                                 relief=FLAT, bd=15)
        self.company_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 15))
        
        self.search_single_btn = Button(single_input, 
                                       text="🔍 EXTRACT DOMAINS",
                                       command=self.search_single_company,
                                       font=('Arial', 12, 'bold'),
                                       bg=self.colors['accent'], fg='white',
                                       relief=FLAT, padx=25, pady=12)
        self.search_single_btn.pack(side=RIGHT)
        
        # File upload section
        file_frame = Frame(input_frame, bg=self.colors['bg'])
        file_frame.pack(fill=X)
        
        Label(file_frame, text="📁 Batch Processing (CSV/TXT):", 
              font=('Arial', 14, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=W, pady=(0, 10))
        
        file_controls = Frame(file_frame, bg=self.colors['bg'])
        file_controls.pack(fill=X)
        
        self.file_label = Label(file_controls, 
                               text="📄 No file selected",
                               font=('Arial', 11),
                               bg=self.colors['bg'], fg=self.colors['warning'])
        self.file_label.pack(side=LEFT, fill=X, expand=True)
        
        self.upload_btn = Button(file_controls, 
                                text="📂 UPLOAD FILE",
                                command=self.upload_file,
                                font=('Arial', 11, 'bold'),
                                bg=self.colors['primary'], fg='white',
                                relief=FLAT, padx=20, pady=8)
        self.upload_btn.pack(side=RIGHT, padx=(15, 10))
        
        self.batch_btn = Button(file_controls, 
                               text="⚡ PROCESS ALL COMPANIES",
                               command=self.start_batch_processing,
                               font=('Arial', 11, 'bold'),
                               bg=self.colors['success'], fg='white',
                               state=DISABLED, relief=FLAT, padx=20, pady=8)
        self.batch_btn.pack(side=RIGHT)
    
    def create_progress_section(self, parent):
        progress_frame = Frame(parent, bg=self.colors['bg'])
        progress_frame.pack(fill=X, pady=(0, 25))
        
        # Speed control with construction theme
        speed_frame = Frame(progress_frame, bg=self.colors['bg'])
        speed_frame.pack(fill=X, pady=(0, 15))
        
        Label(speed_frame, text="⚡ Processing Speed:", 
              font=('Arial', 12, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(side=LEFT)
        
        self.speed_var = StringVar(value='Fast')
        speeds = ['Ultra Fast', 'Super Fast', 'Fast', 'Medium', 'Slow']
        
        for i, speed in enumerate(speeds):
            rb = Radiobutton(speed_frame, text=speed, variable=self.speed_var, 
                           value=speed, command=self.update_speed,
                           bg=self.colors['bg'], fg=self.colors['fg'],
                           selectcolor=self.colors['secondary'],
                           activebackground=self.colors['bg'],
                           font=('Arial', 10, 'bold'))
            rb.pack(side=LEFT, padx=(15 if i > 0 else 10, 0))
        
        # Progress bar with custom styling
        progress_container = Frame(progress_frame, bg=self.colors['bg'])
        progress_container.pack(fill=X, pady=(10, 0))
        
        Label(progress_container, text="📊 Processing Progress:", 
              font=('Arial', 11, 'bold'),
              bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=W)
        
        self.progress = ttk.Progressbar(progress_container, mode='determinate', length=400)
        self.progress.pack(fill=X, pady=(5, 0))
        
        # Status label
        self.status_label = Label(progress_container, text="🏗️ Ready for domain extraction", 
                                font=('Arial', 11),
                                bg=self.colors['bg'], fg=self.colors['success'])
        self.status_label.pack()
    
    def create_results_section(self, parent):
        results_frame = Frame(parent, bg=self.colors['bg'])
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 25))
        
        # Results header with stats
        results_header = Frame(results_frame, bg=self.colors['bg'])
        results_header.pack(fill=X, pady=(0, 10))
        
        Label(results_header, text="📊 REAL-TIME EXTRACTION RESULTS", 
              font=('Arial', 16, 'bold'),
              bg=self.colors['bg'], fg=self.colors['accent']).pack(side=LEFT)
        
        self.results_count = Label(results_header, text="0 results", 
                                  font=('Arial', 12, 'bold'),
                                  bg=self.colors['bg'], fg=self.colors['success'])
        self.results_count.pack(side=RIGHT)
        
        # Treeview with enhanced styling
        tree_frame = Frame(results_frame, bg=self.colors['bg'])
        tree_frame.pack(fill=BOTH, expand=True)
        
        columns = ('Company', 'Domain', 'URL', 'Source', 'Category', 'Status', 'Confidence')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)
        
        # Configure columns with construction industry focus
        column_configs = {
            'Company': {'width': 200, 'anchor': W},
            'Domain': {'width': 200, 'anchor': W},
            'URL': {'width': 300, 'anchor': W},
            'Source': {'width': 120, 'anchor': CENTER},
            'Category': {'width': 120, 'anchor': CENTER},
            'Status': {'width': 100, 'anchor': CENTER},
            'Confidence': {'width': 100, 'anchor': CENTER}
        }
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            config = column_configs.get(col, {'width': 150, 'anchor': W})
            self.results_tree.column(col, width=config['width'], anchor=config['anchor'])
        
        # Professional dark theme styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background=self.colors['secondary'], 
                       foreground=self.colors['fg'], 
                       fieldbackground=self.colors['secondary'],
                       bordercolor=self.colors['bg'],
                       relief=FLAT)
        style.configure("Treeview.Heading", 
                       background=self.colors['primary'], 
                       foreground=self.colors['fg'],
                       font=('Arial', 11, 'bold'),
                       relief=FLAT)
        style.map("Treeview", 
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        # Scrollbar
        scrollbar_v = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.results_tree.yview)
        scrollbar_h = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def create_control_section(self, parent):
        control_frame = Frame(parent, bg=self.colors['bg'])
        control_frame.pack(fill=X)
        
        # Left side - export controls
        left_frame = Frame(control_frame, bg=self.colors['bg'])
        left_frame.pack(side=LEFT)
        
        self.export_btn = Button(left_frame, 
                                text="💾 EXPORT TO CSV",
                                command=self.export_results,
                                font=('Arial', 12, 'bold'),
                                bg=self.colors['success'], fg='white',
                                state=DISABLED, relief=FLAT, padx=20, pady=10)
        self.export_btn.pack(side=LEFT, padx=(0, 15))
        
        self.clear_btn = Button(left_frame, 
                               text="🗑️ CLEAR RESULTS",
                               command=self.clear_results,
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['danger'], fg='white',
                               relief=FLAT, padx=20, pady=10)
        self.clear_btn.pack(side=LEFT)
        
        # Right side - processing controls
        right_frame = Frame(control_frame, bg=self.colors['bg'])
        right_frame.pack(side=RIGHT)
        
        self.stop_btn = Button(right_frame, 
                              text="⏹️ STOP PROCESSING",
                              command=self.stop_processing,
                              font=('Arial', 12, 'bold'),
                              bg=self.colors['warning'], fg='white',
                              state=DISABLED, relief=FLAT, padx=20, pady=10)
        self.stop_btn.pack(side=RIGHT)
    
    def create_status_bar(self):
        status_frame = Frame(self.root, bg=self.colors['secondary'], height=35)
        status_frame.pack(fill=X, side=BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_bar = Label(status_frame, 
                               text="🏗️ Final Perfect Domain Extractor - Construction Industry Ready | Real-time Search Engine Extraction Active", 
                               font=('Arial', 10),
                               bg=self.colors['secondary'], fg=self.colors['success'])
        self.status_bar.pack(fill=X, padx=15, pady=8)
    
    def update_speed(self):
        self.current_speed = self.speed_var.get()
        self.update_status(f"⚡ Speed changed to {self.current_speed}")
    
    def update_status(self, message):
        self.status_bar.config(text=f"🏗️ {message}")
        self.root.update_idletasks()
    
    def update_stats(self):
        stats_text = f"🏢 Processed: {self.processed_companies} | 🌐 Domains: {self.session_stats['domains_found']} | 🔗 URLs: {self.session_stats['urls_extracted']} | ❌ Errors: {self.session_stats['errors']}"
        self.stats_label.config(text=stats_text)
        self.results_count.config(text=f"{len(self.results)} results")
    
    def search_single_company(self):
        if self.is_searching:
            messagebox.showwarning("Warning", "Extraction already in progress!")
            return
        
        company_name = self.company_entry.get().strip()
        if not company_name:
            messagebox.showwarning("Warning", "Please enter a construction company name!")
            return
        
        self.is_searching = True
        self.search_single_btn.config(state=DISABLED, text="🔄 EXTRACTING...")
        self.update_status(f"🔍 Extracting domains for {company_name}...")
        
        # Run in thread
        thread = threading.Thread(target=self._extract_company_domains, args=(company_name,))
        thread.daemon = True
        thread.start()
    
    def _extract_company_domains(self, company_name):
        try:
            domains_data = self.extract_real_time_domains(company_name)
            self.root.after(0, self._add_single_results, company_name, domains_data)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._finish_single_search)
    
    def extract_real_time_domains(self, company_name):
        """Extract real-time domains from search engine first pages"""
        domains_data = []
        settings = self.speed_settings[self.current_speed]
        
        # Generate construction-specific search queries
        search_queries = self._generate_construction_queries(company_name)
        
        # Search engines with real-time extraction
        with ThreadPoolExecutor(max_workers=settings['searches']) as executor:
            futures = []
            
            for engine in self.search_engines:
                for query in search_queries[:2]:  # Use top 2 queries for speed
                    future = executor.submit(self._search_engine_realtime, engine, query, settings['timeout'])
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    results = future.result(timeout=settings['timeout'] * 2)
                    domains_data.extend(results)
                except Exception as e:
                    print(f"Search error: {e}")
                    continue
        
        # Remove duplicates and add confidence scores
        unique_domains = []
        seen = set()
        
        for domain_data in domains_data:
            domain = domain_data.get('domain', '')
            if domain and domain not in seen and self._is_valid_domain(domain):
                seen.add(domain)
                unique_domains.append(domain_data)
        
        return unique_domains[:20]  # Top 20 results
    
    def _generate_construction_queries(self, company_name):
        """Generate construction-specific search queries"""
        base_queries = [
            f"{company_name} official website",
            f"{company_name} construction company",
            f"{company_name} contractor website",
            f"{company_name} .com",
            f"www.{company_name.lower().replace(' ', '')}"
        ]
        
        # Add construction-specific queries
        for keyword in ['construction', 'contractor', 'builders']:
            base_queries.append(f"{company_name} {keyword}")
        
        return base_queries
    
    def _search_engine_realtime(self, engine, query, timeout):
        """Real-time search engine extraction"""
        try:
            url = engine['url'] + requests.utils.quote(query)
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._extract_domains_from_search_results(soup, engine, query)
        except Exception as e:
            print(f"Engine {engine['name']} error: {e}")
        return []
    
    def _extract_domains_from_search_results(self, soup, engine, query):
        """Extract domains from search engine results page"""
        domains_data = []
        
        # Try different selectors based on search engine
        results = []
        if engine['name'] == 'DuckDuckGo':
            results = soup.find_all('div', class_='result')
        elif engine['name'] == 'Brave Search':
            results = soup.find_all('div', class_='web-result')
        elif engine['name'] == 'StartPage':
            results = soup.find_all('div', class_='w-gl__result')
        else:
            results = soup.find_all('div', class_='result')
        
        # Extract domains from first page results
        for result in results[:10]:  # First 10 results from first page
            try:
                # Extract URL
                link = result.find('a', href=True)
                if link:
                    url = link['href']
                    domain = self._extract_domain_from_url(url)
                    
                    if domain and self._is_valid_domain(domain):
                        # Extract title and description
                        title = link.get_text(strip=True)
                        description = ""
                        desc_elem = result.find('div', class_='result__snippet') or result.find('p')
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)
                        
                        # Categorize construction type
                        category = self._categorize_construction_type(title, description, domain)
                        
                        # Calculate confidence
                        confidence = self._calculate_confidence(title, description, domain, query)
                        
                        domains_data.append({
                            'domain': domain,
                            'url': url,
                            'title': title,
                            'description': description,
                            'source': f"Search: {engine['name']}",
                            'category': category,
                            'confidence': confidence,
                            'query': query
                        })
            except Exception as e:
                print(f"Result extraction error: {e}")
                continue
        
        return domains_data
    
    def _categorize_construction_type(self, title, description, domain):
        """Categorize construction company type"""
        text = f"{title} {description} {domain}".lower()
        
        categories = {
            'Electrical': ['electric', 'electrical', 'wiring', 'power', 'lighting'],
            'Plumbing': ['plumb', 'pipe', 'drain', 'sewer', 'water'],
            'HVAC': ['hvac', 'heating', 'cooling', 'air', 'ventilation'],
            'Roofing': ['roof', 'shingle', 'gutter', 'waterproof'],
            'Concrete': ['concrete', 'cement', 'foundation', 'paving'],
            'General': ['general', 'building', 'construction', 'contractor'],
            'Specialty': ['specialty', 'demolition', 'excavation', 'insulation']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def _calculate_confidence(self, title, description, domain, query):
        """Calculate confidence score for domain"""
        confidence = 50  # Base confidence
        
        # Boost for exact company name match
        query_lower = query.lower()
        title_lower = title.lower()
        desc_lower = description.lower()
        domain_lower = domain.lower()
        
        if any(word in title_lower for word in query_lower.split()[:2]):
            confidence += 20
        
        if any(word in desc_lower for word in query_lower.split()[:2]):
            confidence += 15
        
        # Construction keywords boost
        if any(keyword in desc_lower for keyword in self.construction_keywords):
            confidence += 10
        
        # Official website indicators
        if any(indicator in title_lower for indicator in ['official', 'website', 'home']):
            confidence += 15
        
        # Clean domain boost
        if not any(char in domain for char in ['-', '_', '.']):
            confidence += 10
        
        return min(confidence, 95)
    
    def _extract_domain_from_url(self, url):
        """Extract domain from URL"""
        try:
            if url.startswith('http'):
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                # Remove www. prefix
                if domain.startswith('www.'):
                    domain = domain[4:]
                return domain
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
    
    def _add_single_results(self, company_name, domains_data):
        # Clear previous single search results
        for item in self.results_tree.get_children():
            if self.results_tree.item(item)['values'][0] == company_name:
                self.results_tree.delete(item)
        
        # Add new results
        for domain_data in domains_data:
            self.results_tree.insert('', 'end', values=(
                company_name,
                domain_data['domain'],
                domain_data['url'][:50] + '...' if len(domain_data['url']) > 50 else domain_data['url'],
                domain_data['source'],
                domain_data['category'],
                "Found",
                f"{domain_data['confidence']}%"
            ))
            
            self.results.append({
                'Company': company_name,
                'Domain': domain_data['domain'],
                'URL': domain_data['url'],
                'Title': domain_data.get('title', ''),
                'Description': domain_data.get('description', ''),
                'Source': domain_data['source'],
                'Category': domain_data['category'],
                'Status': 'Found',
                'Confidence': domain_data['confidence']
            })
        
        self.session_stats['domains_found'] += len(domains_data)
        self.session_stats['urls_extracted'] += len(domains_data)
        self.update_stats()
        self.export_btn.config(state=NORMAL)
    
    def _finish_single_search(self):
        self.is_searching = False
        self.search_single_btn.config(state=NORMAL, text="🔍 EXTRACT DOMAINS")
        self.update_status("✅ Domain extraction completed")
    
    def _show_error(self, error):
        messagebox.showerror("Error", f"An error occurred: {error}")
        self.session_stats['errors'] += 1
        self.update_stats()
    
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select Construction Companies File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                companies = self._read_company_file(filename)
                if companies:
                    self.companies_to_process = companies
                    self.file_label.config(text=f"📄 {len(companies)} construction companies loaded", fg=self.colors['success'])
                    self.batch_btn.config(state=NORMAL)
                    self.update_status(f"📁 Loaded {len(companies)} construction companies from {os.path.basename(filename)}")
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
        
        self.update_status(f"🏗️ Starting batch processing of {self.total_companies} construction companies...")
        
        # Start processing
        thread = threading.Thread(target=self._batch_processing_thread)
        thread.daemon = True
        thread.start()
    
    def _batch_processing_thread(self):
        settings = self.speed_settings[self.current_speed]
        
        with ThreadPoolExecutor(max_workers=settings['workers']) as executor:
            # Submit all companies
            future_to_company = {
                executor.submit(self.extract_real_time_domains, company): company 
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
                    domains_data = future.result(timeout=settings['timeout'] * 3)
                    self.root.after(0, self._add_batch_results, company_name, domains_data)
                except Exception as e:
                    self.root.after(0, self._add_batch_error, company_name, str(e))
                
                # Rate limiting
                if settings['delay'] > 0:
                    time.sleep(settings['delay'])
        
        # Batch completed
        self.root.after(0, self._finish_batch_processing)
    
    def _update_batch_progress(self, current, company_name):
        self.progress['value'] = current
        self.status_label.config(text=f"🏗️ Processing {current}/{self.total_companies}: {company_name}")
        self.update_stats()
    
    def _add_batch_results(self, company_name, domains_data):
        if domains_data:
            for domain_data in domains_data:
                self.results_tree.insert('', 'end', values=(
                    company_name,
                    domain_data['domain'],
                    domain_data['url'][:50] + '...' if len(domain_data['url']) > 50 else domain_data['url'],
                    domain_data['source'],
                    domain_data['category'],
                    "Found",
                    f"{domain_data['confidence']}%"
                ))
                
                self.results.append({
                    'Company': company_name,
                    'Domain': domain_data['domain'],
                    'URL': domain_data['url'],
                    'Title': domain_data.get('title', ''),
                    'Description': domain_data.get('description', ''),
                    'Source': domain_data['source'],
                    'Category': domain_data['category'],
                    'Status': 'Found',
                    'Confidence': domain_data['confidence']
                })
            
            self.session_stats['domains_found'] += len(domains_data)
            self.session_stats['urls_extracted'] += len(domains_data)
        else:
            self.results_tree.insert('', 'end', values=(company_name, "No domains found", "N/A", "N/A", "N/A", "Not Found", "0%"))
            self.results.append({
                'Company': company_name,
                'Domain': 'No domains found',
                'URL': 'N/A',
                'Title': '',
                'Description': '',
                'Source': 'N/A',
                'Category': 'N/A',
                'Status': 'Not Found',
                'Confidence': 0
            })
        
        self.export_btn.config(state=NORMAL)
    
    def _add_batch_error(self, company_name, error):
        self.results_tree.insert('', 'end', values=(company_name, f"Error: {error}", "N/A", "N/A", "N/A", "Error", "0%"))
        self.results.append({
            'Company': company_name,
            'Domain': f"Error: {error}",
            'URL': 'N/A',
            'Title': '',
            'Description': '',
            'Source': 'N/A',
            'Category': 'N/A',
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
        self.update_status(f"✅ Batch completed in {elapsed_time:.1f}s | {self.total_companies} construction companies processed")
        messagebox.showinfo("Batch Complete", 
                           f"🏗️ Processing Complete!\\n\\n"
                           f"Companies Processed: {self.total_companies}\\n"
                           f"Domains Found: {self.session_stats['domains_found']}\\n"
                           f"URLs Extracted: {self.session_stats['urls_extracted']}\\n"
                           f"Processing Time: {elapsed_time:.1f} seconds\\n"
                           f"Average Speed: {self.total_companies/elapsed_time:.1f} companies/second")
    
    def stop_processing(self):
        self.is_searching = False
        self._finish_batch_processing()
        self.update_status("⏹️ Processing stopped by user")
    
    def export_results(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"construction_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                # Create comprehensive DataFrame
                df = pd.DataFrame(self.results)
                
                # Add metadata
                metadata = {
                    'Export_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Total_Companies': self.total_companies,
                    'Domains_Found': self.session_stats['domains_found'],
                    'URLs_Extracted': self.session_stats['urls_extracted'],
                    'Processing_Speed': self.current_speed
                }
                
                # Export main data
                df.to_csv(filename, index=False)
                
                # Create metadata file
                metadata_filename = filename.replace('.csv', '_metadata.json')
                with open(metadata_filename, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to {filename}\\nMetadata saved to {metadata_filename}")
                self.update_status(f"💾 Exported {len(self.results)} results to {os.path.basename(filename)}")
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
            'urls_extracted': 0,
            'start_time': None,
            'errors': 0
        }
        
        self.export_btn.config(state=DISABLED)
        self.file_label.config(text="📄 No file selected", fg=self.colors['warning'])
        self.batch_btn.config(state=DISABLED)
        self.progress['value'] = 0
        self.update_stats()
        self.update_status("🏗️ Results cleared - Ready for construction company extraction")

if __name__ == "__main__":
    root = Tk()
    app = FinalPerfectDomainExtractor(root)
    root.mainloop()
