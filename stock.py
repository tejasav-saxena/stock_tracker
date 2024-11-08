import tkinter as tk
from tkinter import ttk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import mplcursors

# Function to fetch stock price for a single symbol and display the latest price
def get_single_stock_price():
    stock_symbol = single_stock_var.get()
    stock = yf.Ticker(stock_symbol)
    
    try:
        stock_price = stock.history(period="1d")['Close'][0]
        single_stock_result_label.config(text=f"The latest stock price of {stock_symbol} is: ${stock_price:.2f}", fg='#43A047')
    except IndexError:
        single_stock_result_label.config(text=f"Error: Could not retrieve data for symbol '{stock_symbol}'.", fg='#E53935')

# Function to fetch stock price data for multiple symbols and display a comparison graph
def get_stock_prices():
    selected_symbols = stock_var.curselection()
    symbols = [stock_symbols[i] for i in selected_symbols]

    if len(symbols) < 2 or len(symbols) > 3:
        multi_stock_result_label.config(text="Please select 2 or 3 stocks to compare.", fg='#E53935')
        return

    stock_data_dict = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        stock_data = stock.history(start=start_date, end=end_date)
        stock_data_dict[symbol] = stock_data

    multi_stock_result_label.config(text=f"Comparing stock prices for: {', '.join(symbols)}", fg='#43A047')
    plot_comparison_graph(stock_data_dict)

# Function to plot comparison graph
def plot_comparison_graph(stock_data_dict):
    for widget in graph_frame.winfo_children():
        widget.destroy()
    
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    
    for symbol, stock_data in stock_data_dict.items():
        line, = ax.plot(stock_data.index, stock_data['Close'], marker='o', markersize=5, label=symbol)
        mplcursors.cursor(line, hover=True).connect("add", lambda sel: sel.annotation.set_text(
            f"{stock_data.index[sel.index].date()}\n${stock_data['Close'].iloc[sel.index]:.2f}"))
    
    ax.set_title("Stock Price Comparison (Past 30 Days)", fontsize=14, color='#333333')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.grid(True)
    
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    fig.autofmt_xdate()
    ax.legend()
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Create a gradient background for any canvas
def create_gradient(canvas, color1, color2):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    gradient = canvas.create_rectangle(0, 0, width, height, outline="", fill=color1)
    for i in range(height):
        r = int(color1[1:3], 16) + i * (int(color2[1:3], 16) - int(color1[1:3], 16)) // height
        g = int(color1[3:5], 16) + i * (int(color2[3:5], 16) - int(color1[3:5], 16)) // height
        b = int(color1[5:7], 16) + i * (int(color2[5:7], 16) - int(color1[5:7], 16)) // height
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color)

# Toggle Full-Screen Mode
def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)
    
    if fullscreen:
        resize_graph()
    else:
        reset_graph()

def resize_graph():
    for widget in graph_frame.winfo_children():
        widget.destroy()
    
    graph_frame.config(width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    create_gradient(graph_frame, "#1c1c1c", "#333333")
    
    fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def reset_graph():
    pass  # This can be further refined if necessary.

def end_fullscreen(event=None):
    global fullscreen
    fullscreen = False
    root.attributes("-fullscreen", False)

# List of 20 stock symbols for the dropdown
stock_symbols = [
    'AAPL', 'TSLA', 'GOOGL', 'AMZN', 'MSFT', 'NFLX', 'META', 
    'NVDA', 'DIS', 'INTC', 'BA', 'JPM', 'V', 'PYPL', 'ADBE', 
    'ORCL', 'CSCO', 'IBM', 'BABA', 'KO'
]

# Set up the main window
root = tk.Tk()
root.title("Stock Price Tracker")
root.geometry("800x700")
fullscreen = False
root.attributes("-fullscreen", fullscreen)

# Add a gradient canvas background
gradient_canvas = tk.Canvas(root, width=800, height=700)
gradient_canvas.pack(fill='both', expand=True)

# Call gradient background creation function
create_gradient(gradient_canvas, "#1c1c1c", "#333333")

# Add a title label
title_label = tk.Label(gradient_canvas, text="Stock Price Tracker", font=("Helvetica", 18, "bold"), 
                       bg='#333333', fg='#ffffff', padx=10, pady=5)
title_label.place(relx=0.5, rely=0.03, anchor='center')

# Section for getting single stock price
single_stock_label = tk.Label(gradient_canvas, text="Get Single Stock Price:", font=("Helvetica", 14), 
                              bg='#333333', fg='#ffffff')
single_stock_label.place(relx=0.2, rely=0.1, anchor='center')

# Dropdown menu for single stock symbol
single_stock_var = tk.StringVar()
single_stock_var.set(stock_symbols[0])

single_stock_dropdown = ttk.Combobox(gradient_canvas, textvariable=single_stock_var, values=stock_symbols, font=("Helvetica", 10))
single_stock_dropdown.place(relx=0.2, rely=0.17, anchor='center', width=150)

# Button to fetch single stock price
single_stock_button = tk.Button(gradient_canvas, text="Get Price", command=get_single_stock_price, font=("Helvetica", 12, "bold"), 
                                bg='#2196F3', fg='white', bd=0, padx=20, pady=8)
single_stock_button.place(relx=0.2, rely=0.25, anchor='center')

# Label to display single stock result
single_stock_result_label = tk.Label(gradient_canvas, text="", font=("Helvetica", 12), bg='#333333', fg='#ffffff', padx=10, pady=5)
single_stock_result_label.place(relx=0.2, rely=0.35, anchor='center')

# Section for comparing multiple stocks
multi_stock_label = tk.Label(gradient_canvas, text="Compare Multiple Stocks:", font=("Helvetica", 14), 
                             bg='#333333', fg='#ffffff')
multi_stock_label.place(relx=0.75, rely=0.1, anchor='center')

# Listbox for selecting multiple stock symbols
stock_var = tk.Listbox(gradient_canvas, selectmode='multiple', font=("Helvetica", 10), height=6, exportselection=0)
for symbol in stock_symbols:
    stock_var.insert(tk.END, symbol)
stock_var.place(relx=0.75, rely=0.17, anchor='center', width=200)

# Button to fetch multiple stock prices and compare
fetch_button = tk.Button(gradient_canvas, text="Compare Stocks", command=get_stock_prices, font=("Helvetica", 12, "bold"), 
                         bg='#2196F3', fg='white', bd=0, padx=20, pady=8)
fetch_button.place(relx=0.75, rely=0.27, anchor='center')

# Label to display multiple stock result
multi_stock_result_label = tk.Label(gradient_canvas, text="", font=("Helvetica", 12), bg='#333333', fg='#ffffff', padx=10, pady=5)
multi_stock_result_label.place(relx=0.75, rely=0.37, anchor='center')

# Frame to display the graph
graph_frame = tk.Frame(gradient_canvas, bg='#ffffff')
graph_frame.place(relx=0.5, rely=0.75, anchor='center', width=600, height=300)

# Button to toggle full-screen mode
toggle_button = tk.Button(gradient_canvas, text="Toggle Full-Screen", command=toggle_fullscreen, font=("Helvetica", 12, "bold"), 
                          bg='#FF5722', fg='white', bd=0, padx=20, pady=8)
toggle_button.place(relx=0.5, rely=0.9, anchor='center')

# Bind the Escape key to exit full-screen mode
root.bind("<Escape>", end_fullscreen)

# Run the Tkinter event loop
root.mainloop()
