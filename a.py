from dhanhq import DhanContext, MarketFeed
import tkinter as tk
from tkinter import ttk, messagebox
import json

# Define and use your dhan_context
dhan_context = DhanContext("1101812495","eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQ1MDQzNzI5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMTgxMjQ5NSJ9.VlLATxaAJxKUH6GGHHZfDw8wjxQufHzqTvyU6UckYCcRbj6dXpF0TehhmwMndIPWEf4B00N7GP7zGFzQ9XeFvQ")

class SymbolSearchApp:
    def __init__(self, root, dhan_context):
        self.root = root
        self.dhan_context = dhan_context
        self.root.title("Dhan Symbol Search")
        self.root.geometry("600x500")
        
        # Dictionary to store security info
        self.selected_symbols = {}
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Search frame
        search_frame = ttk.LabelFrame(self.root, text="Search Symbols")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        # Symbol search entry
        ttk.Label(search_frame, text="Symbol Name:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Search button
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_symbols)
        search_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.root, text="Search Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Results treeview
        self.results_tree = ttk.Treeview(results_frame, columns=("Name", "Exchange", "ID", "Type"), show="headings")
        self.results_tree.heading("Name", text="Symbol Name")
        self.results_tree.heading("Exchange", text="Exchange")
        self.results_tree.heading("ID", text="Security ID")
        self.results_tree.heading("Type", text="Type")
        
        self.results_tree.column("Name", width=150)
        self.results_tree.column("Exchange", width=80)
        self.results_tree.column("ID", width=80)
        self.results_tree.column("Type", width=100)
        
        self.results_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add button
        add_btn = ttk.Button(self.root, text="Add Selected", command=self.add_selected)
        add_btn.pack(pady=10)
        
        # Selected symbols frame
        selected_frame = ttk.LabelFrame(self.root, text="Selected Symbols")
        selected_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Selected symbols treeview
        self.selected_tree = ttk.Treeview(selected_frame, columns=("Name", "Exchange", "ID"), show="headings")
        self.selected_tree.heading("Name", text="Symbol Name")
        self.selected_tree.heading("Exchange", text="Exchange")
        self.selected_tree.heading("ID", text="Security ID")
        
        self.selected_tree.column("Name", width=150)
        self.selected_tree.column("Exchange", width=80)
        self.selected_tree.column("ID", width=80)
        
        self.selected_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Run button
        run_btn = ttk.Button(self.root, text="Start Market Feed", command=self.start_market_feed)
        run_btn.pack(pady=10)
    
    def search_symbols(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Search Error", "Please enter a symbol to search")
            return
            
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        try:
            # Use the Dhan API to search for symbols
            search_results = self.dhan_context.search_scrip(query)
            
            if not search_results:
                messagebox.showinfo("No Results", f"No symbols found for '{query}'")
                return
                
            # Display results in the treeview
            for result in search_results:
                security_id = result.get("security_id", "")
                exchange = result.get("exchange", "")
                name = result.get("trading_symbol", "")
                security_type = result.get("security_type", "")
                
                self.results_tree.insert("", "end", values=(name, exchange, security_id, security_type))
                
        except Exception as e:
            messagebox.showerror("Search Error", f"Error searching symbols: {str(e)}")

    def add_selected(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a symbol to add")
            return
        
        for item in selected_item:
            values = self.results_tree.item(item, "values")
            symbol_name = values[0]
            exchange = values[1]
            security_id = values[2]
            
            # Skip if already added
            if security_id in self.selected_symbols:
                continue
                
            # Add to selected symbols
            self.selected_symbols[security_id] = {
                "name": symbol_name,
                "exchange": exchange
            }
            
            # Add to selected tree view
            self.selected_tree.insert("", "end", values=(symbol_name, exchange, security_id))
    
    def start_market_feed(self):
        if not self.selected_symbols:
            messagebox.showwarning("Start Error", "Please select at least one symbol")
            return
        
        # Create stock names dictionary and instruments list
        stock_names = {}
        instruments = []
        
        for security_id, info in self.selected_symbols.items():
            stock_names[security_id] = info["name"]
            
            # Determine exchange segment
            exchange_segment = MarketFeed.NSE if info["exchange"] == "NSE" else (
                MarketFeed.BSE if info["exchange"] == "BSE" else MarketFeed.NSE
            )
            
            instruments.append((exchange_segment, security_id, MarketFeed.Ticker))
        
        # Close UI
        self.root.destroy()
        
        # Start market feed
        start_market_feed(self.dhan_context, stock_names, instruments)

def start_market_feed(dhan_context, stock_names, instruments):
    version = "v2"  # Mention Version and set to latest version 'v2'
    
    try:
        data = MarketFeed(dhan_context, instruments, version)
        print("Starting market feed for the following symbols:")
        for security_id, name in stock_names.items():
            print(f"- {name} (ID: {security_id})")
            
        while True:
            data.run_forever()
            response = data.get_data()
            
            # Add stock name to the response data
            if 'security_id' in response:
                security_id = response['security_id']
                if str(security_id) in stock_names:
                    response['stock_name'] = stock_names[str(security_id)]
                else:
                    response['stock_name'] = "Unknown"
                    
            print(response)

    except Exception as e:
        print(e)

# Create and start UI
if __name__ == "__main__":
    root = tk.Tk()
    app = SymbolSearchApp(root, dhan_context)
    root.mainloop()