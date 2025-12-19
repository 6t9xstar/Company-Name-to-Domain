import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime
import json
import os

class DataExporter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Export Your Data")
        self.root.geometry("500x400")
        self.root.configure(bg='#f8f9fa')
        
        # Instructions
        instructions = """
        ⚡ DATA EXPORT TOOL ⚡
        
        Since the export button is missing from the main application,
        this tool will help you export your extracted data.
        
        Steps:
        1. Keep your Perfect Fast Extractor running with results
        2. Click 'Export Data' below
        3. Choose save location
        4. Your data will be saved as CSV
        """
        
        tk.Label(self.root, text=instructions, 
                font=('Arial', 11), bg='#f8f9fa', 
                justify=tk.LEFT).pack(pady=20, padx=20)
        
        # Export button
        export_btn = tk.Button(self.root, text="💾 EXPORT DATA NOW", 
                              command=self.export_data,
                              font=('Arial', 12, 'bold'), 
                              bg='#27ae60', fg='white',
                              padx=20, pady=10)
        export_btn.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready to export your data", 
                                    font=('Arial', 10), bg='#f8f9fa', fg='#7f8c8d')
        self.status_label.pack(pady=10)
    
    def export_data(self):
        try:
            # Try to get data from the running application
            # Since we can't directly access the other app's data,
            # we'll create a manual data entry option
            
            self.status_label.config(text="Opening data entry window...")
            
            # Create a new window for data entry
            data_window = tk.Toplevel(self.root)
            data_window.title("Enter Your Data")
            data_window.geometry("600x500")
            data_window.configure(bg='white')
            
            tk.Label(data_window, text="Copy/paste your data here (CSV format):", 
                    font=('Arial', 11, 'bold')).pack(pady=10)
            
            # Text area for data
            text_area = tk.Text(data_window, height=20, width=70)
            text_area.pack(pady=10, padx=10)
            
            # Instructions
            instructions_text = """
            Format your data like this (copy from the application table):
            
            Company,Domain,Source,Status
            Company1,domain1.com,Direct Pattern,✅ Found
            Company2,domain2.com,Search: DuckDuckGo,✅ Found
            ...
            """
            
            text_area.insert('1.0', instructions_text)
            
            def save_data():
                data = text_area.get('1.0', 'end-1c').strip()
                if not data or data == instructions_text.strip():
                    messagebox.showwarning("Warning", "Please enter your data first!")
                    return
                
                try:
                    # Parse the data
                    lines = data.split('\n')
                    rows = []
                    for line in lines:
                        if line.strip() and not line.startswith('Format'):
                            # Simple CSV parsing
                            parts = line.split(',')
                            if len(parts) >= 4:
                                rows.append({
                                    'Company': parts[0].strip(),
                                    'Domain': parts[1].strip(), 
                                    'Source': parts[2].strip(),
                                    'Status': parts[3].strip()
                                })
                    
                    if not rows:
                        messagebox.showwarning("Warning", "No valid data found!")
                        return
                    
                    # Save to CSV
                    filename = f"exported_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    df = pd.DataFrame(rows)
                    df.to_csv(filename, index=False)
                    
                    messagebox.showinfo("Success", f"✅ Exported {len(rows)} records to {filename}")
                    data_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed: {str(e)}")
            
            tk.Button(data_window, text="💾 Save CSV", 
                     command=save_data,
                     font=('Arial', 11, 'bold'), 
                     bg='#3498db', fg='white').pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open export window: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    exporter = DataExporter()
    exporter.run()
