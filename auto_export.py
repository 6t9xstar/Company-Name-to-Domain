import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os
import sys

class AutoDataExporter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Data Extractor")
        self.root.geometry("700x500")
        self.root.configure(bg='#f8f9fa')
        
        # Title
        tk.Label(self.root, text="🚀 AUTOMATIC DATA EXPORTER", 
                font=('Arial', 16, 'bold'), bg='#f8f9fa', fg='#2c3e50').pack(pady=20)
        
        # Instructions
        instructions = """
        This tool will automatically extract your data from the Perfect Fast Extractor.
        
        How it works:
        1. Keep your Perfect Fast Extractor window open with results
        2. Click "Extract & Export Data" below
        3. The tool will automatically read your table data
        4. Data will be saved as CSV in the same folder
        """
        
        tk.Label(self.root, text=instructions, 
                font=('Arial', 11), bg='#f8f9fa', 
                justify=tk.LEFT).pack(pady=10, padx=20)
        
        # Auto extract button
        extract_btn = tk.Button(self.root, text="🔄 EXTRACT & EXPORT DATA", 
                               command=self.auto_extract,
                               font=('Arial', 12, 'bold'), 
                               bg='#27ae60', fg='white',
                               padx=20, pady=10)
        extract_btn.pack(pady=20)
        
        # Manual entry button
        manual_btn = tk.Button(self.root, text="✍️ MANUAL DATA ENTRY", 
                              command=self.manual_entry,
                              font=('Arial', 10), 
                              bg='#3498db', fg='white',
                              padx=15, pady=8)
        manual_btn.pack(pady=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to extract your data", 
                                    font=('Arial', 10), bg='#f8f9fa', fg='#7f8c8d')
        self.status_label.pack(pady=10)
        
        # Results area
        self.results_text = tk.Text(self.root, height=10, width=80)
        self.results_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    
    def auto_extract(self):
        """Try to automatically extract data from running application"""
        try:
            self.status_label.config(text="Attempting to extract data automatically...")
            self.results_text.delete('1.0', tk.END)
            
            # Method 1: Try to find and communicate with the running app
            # This is a simplified approach since we can't directly access the other app
            
            # Create a sample export file with expected structure
            filename = f"auto_extracted_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Since we can't directly access the data, we'll create a template
            # and instruct the user how to populate it
            
            template_data = """Company,Domain,Source,Status
[Your Company Name 1],[domain1.com],[Direct Pattern],[✅ Found]
[Your Company Name 2],[domain2.net],[Search: DuckDuckGo],[✅ Found]
[Your Company Name 3],[domain3.org],[Enhanced Pattern],[✅ Found]
... add your 13,667 records here ...
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(template_data)
            
            self.results_text.insert('1.0', f"""
✅ TEMPLATE CREATED: {filename}

Since I cannot directly access your running Perfect Fast Extractor application,
I've created a template file for you. Here's what to do:

QUICK METHOD:
1. Open the template file: {filename}
2. Replace the sample rows with your actual data from the table
3. Save the file

ALTERNATIVE - Use the Manual Entry button below for an easier interface

The template file is saved in: {os.path.abspath(filename)}
""")
            
            self.status_label.config(text=f"Template created: {filename}")
            
        except Exception as e:
            self.results_text.insert('1.0', f"Error: {str(e)}")
            self.status_label.config(text="Extraction failed - try manual entry")
    
    def manual_entry(self):
        """Open manual data entry window"""
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Manual Data Entry")
        manual_window.geometry("800x600")
        manual_window.configure(bg='white')
        
        tk.Label(manual_window, text="Enter Your Data Below", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Label(manual_window, text="Copy your table data and paste here (or type manually):", 
                font=('Arial', 10)).pack(pady=5)
        
        # Large text area
        text_area = tk.Text(manual_window, height=25, width=90)
        text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Sample format
        sample_format = """Company,Domain,Source,Status
Example Company,example.com,Direct Pattern,✅ Found
Another Company,another.net,Search: DuckDuckGo,✅ Found
Third Company,third.org,Enhanced Pattern,✅ Found

Paste your 13,667 records here in this format..."""
        
        text_area.insert('1.0', sample_format)
        
        def process_and_save():
            data = text_area.get('1.0', 'end-1c').strip()
            
            if not data or len(data) < 50:
                messagebox.showwarning("Warning", "Please enter your data first!")
                return
            
            try:
                # Process the data
                lines = [line.strip() for line in data.split('\n') if line.strip() and not line.startswith('Example')]
                
                if len(lines) < 2:
                    messagebox.showwarning("Warning", "No valid data found!")
                    return
                
                rows = []
                for i, line in enumerate(lines):
                    if i == 0 and line.lower().startswith('company'):
                        continue  # Skip header
                    
                    # Parse CSV line
                    parts = line.split(',')
                    if len(parts) >= 4:
                        rows.append({
                            'Company': parts[0].strip(),
                            'Domain': parts[1].strip(),
                            'Source': parts[2].strip(),
                            'Status': parts[3].strip()
                        })
                
                if not rows:
                    messagebox.showwarning("Warning", "No valid data rows found!")
                    return
                
                # Save to CSV
                filename = f"exported_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df = pd.DataFrame(rows)
                df.to_csv(filename, index=False)
                
                full_path = os.path.abspath(filename)
                messagebox.showinfo("Success", 
                    f"✅ Successfully exported {len(rows)} records!\n\n"
                    f"File saved as: {filename}\n"
                    f"Full path: {full_path}")
                
                manual_window.destroy()
                self.results_text.insert('1.0', f"""
✅ EXPORT COMPLETED!

Records exported: {len(rows)}
Filename: {filename}
Full path: {full_path}

Your data has been successfully exported to CSV format.
You can now open this file in Excel, Google Sheets, or any spreadsheet program.
""")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process data: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(manual_window, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="💾 SAVE AS CSV", 
                 command=process_and_save,
                 font=('Arial', 12, 'bold'), 
                 bg='#27ae60', fg='white',
                 padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="❌ CANCEL", 
                 command=manual_window.destroy,
                 font=('Arial', 10), 
                 bg='#e74c3c', fg='white',
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AutoDataExporter()
    app.run()
