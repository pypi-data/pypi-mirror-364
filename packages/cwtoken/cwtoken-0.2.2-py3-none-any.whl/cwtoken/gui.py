import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from . import key_manager
import os
from datetime import datetime, timedelta

# --- Tkinter root ---
root = tk.Tk()

# --- Shared state ---
login_data = {
    "logged_in": False,
    "clubcode": None,
    "api_token": None,
    "token": None
}
save_cred = tk.IntVar()
save_csv = tk.IntVar()
save_query = tk.IntVar()
clubcode_entry = None
token_entry = None
data_text = None
df = None

# --- Buttons ---

# --- Login check function ---
def try_login():
    clubcode = clubcode_entry.get()
    api_token = token_entry.get()
    save_credentials = save_cred.get()

    token = key_manager.get_access_token(api_token, clubcode)
    if token is not None:
        login_data["logged_in"] = True
        login_data["clubcode"] = clubcode
        login_data["api_token"] = api_token
        login_data["token"] = token

        if save_credentials == 1:
            with open("static_api.txt", "w") as f:
                f.write(f"{clubcode},{api_token}\n")

        show_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid clubcode or API token.")

# --- Save query function ---
def run_query():
    global df
    
    today = datetime.today().date()
    keywords = {
        "today": today,
        "tomorrow": today + timedelta(days=1),
        "yesterday": today - timedelta(days=1),
        "beginning_of_month": today.replace(day=1)
    }
    
    query = data_text.get("1.0", "end").strip()
    query_keywords = query.format(**keywords)
    query_url_fmt = query_keywords.replace('\n', '').replace('\r', '')
    if not query_url_fmt:
        messagebox.showerror("Input Error", "Please enter a query URL.")
        return
    if not login_data["token"]:
        messagebox.showerror("Error", "Access token missing. Please login again.")
        return
    # TODO: fetch data and display or save
    print(f"Running query: {query_url_fmt}")
    df = key_manager.fetch(request=query_url_fmt, api_token=login_data["api_token"], access_token=login_data["token"])
    if df is None:
        messagebox.showerror("Error", "Invalid query")
        return
    finish = 1
    if save_query.get():
        while finish:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("TXT files", "*.txt")],
                title="Save Query As"
            )
            dir_path = os.path.dirname(file_path)
            if not file_path:
                return  # user cancelled
            if os.path.isdir(dir_path):
                with open(f'{file_path}', 'w') as file:
                    file.write(f'{query}')
                finish = 0
            else:
                print("Error: file path doesn't exist")
    
    
    show_results()

def load_query():
    finish = 1
    while finish:
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("TXT files", "*.txt")],
            title="Open query file"
        )
        dir_path = os.path.dirname(file_path)
        if not file_path:
            return  # user cancelled
        if os.path.isdir(dir_path):
            finish = 0
            with open(f'{file_path}', 'r') as file:
                file_content = file.read()
        else:
            print("Error: file path doesn't exist")
    data_text.insert('1.0', file_content)
# --- Pages ---

def show_results():
    for widget in root.winfo_children():
        widget.destroy()

    root.geometry("800x600")
    root.title("Query Results")

    if not df.empty:
        # Outer frame to hold everything
        container = tk.Frame(root)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Label frame to group the table visually
        display_df = tk.LabelFrame(container, text="Your query results")
        display_df.pack(fill="both", expand=True)

        # Treeview inside the label frame
        tv1 = ttk.Treeview(display_df)
        tv1.pack(side="left", fill="both", expand=True)

        # Scrollbars
        treescrolly = tk.Scrollbar(display_df, orient="vertical", command=tv1.yview)
        treescrollx = tk.Scrollbar(container, orient="horizontal", command=tv1.xview)
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)

        treescrolly.pack(side="right", fill="y")
        treescrollx.pack(side="bottom", fill="x")

        # Setup columns
        tv1["columns"] = list(df.columns)
        tv1["show"] = "headings"

        for column in tv1["columns"]:
            tv1.heading(column, text=column)

        # Insert rows
        df_rows = df.to_numpy().tolist()
        tv1["displaycolumns"] = ()
        for row in df_rows:
            tv1.insert("", "end", values=row)
        tv1["displaycolumns"] = list(df.columns)
    else:
        tk.Label(root, text="Query returned empty array!", font=("Arial", 14)).grid(row=0, column=0, pady=10, sticky="w", padx=10)

    # --- Bottom Buttons (Side-by-side)
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Save to CSV", command=save_file).pack(side="left", padx=20)
    tk.Button(button_frame, text="Back to Query Creator", command=show_main_app).pack(side="left", padx=20)

    
def save_file():
    finish = 1
    while finish:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV As"
        )
        dir_path = os.path.dirname(file_path)
        if not file_path:
            return  # user cancelled
        if os.path.isdir(dir_path):
            df.to_csv(f"{file_path}")
            finish = 0
        else:
            print("Error: file path doesn't exist")
            
def show_main_app():
    global data_text, save_csv, save_query
    for widget in root.winfo_children():
        widget.destroy()
    
    root.geometry("800x600")
    root.title("POSTGREST data request")

    # Configure root grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(3, weight=1)  # Make the Text widget row expandable

    tk.Label(root, text=f"Welcome! Clubcode: {login_data['clubcode']}", font=("Arial", 14)).grid(row=0, column=0, pady=10, sticky="w", padx=10)

    desc_text = (
        "Enter your PostgREST API URL string below.\n"
        "This should be the endpoint you want to query, including any filters or parameters.\n\n"
        "Example:\n"
        "member?select=member_no,first_name,surname\n"
        "&first_name=eq.John\n\n"
        "Make sure your URL is valid and accessible with your API token."
    )
    tk.Label(root, text=desc_text, justify="left", wraplength=600).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    # Row for checkbox + Load query button
    options_frame = tk.Frame(root)
    options_frame.grid(row=2, column=0, sticky="w", padx=10)

    save_query = tk.IntVar()
    tk.Checkbutton(options_frame, text="Save query?", variable=save_query).pack(side="left")

    tk.Button(options_frame, text="Load query!", command=load_query).pack(side="left", padx=10)

    # Text widget inside a Frame with Scrollbar (optional)
    text_frame = tk.Frame(root)
    text_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)

    data_text = tk.Text(text_frame, wrap="word")
    data_text.grid(row=0, column=0, sticky="nsew")

    scroll = tk.Scrollbar(text_frame, command=data_text.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    data_text.config(yscrollcommand=scroll.set)

    # Bottom button for running the query
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=4, column=0, sticky="ew", pady=10)
    tk.Button(bottom_frame, text="Run query!", command=run_query).pack(side="left", padx=10)


def setup_login_screen():
    global clubcode_entry, token_entry
    root.title("Clubwise Login")
    root.geometry("300x220")

    tk.Label(root, text="Enter Clubcode:").pack(pady=5)
    clubcode_entry = tk.Entry(root)
    clubcode_entry.pack()

    tk.Label(root, text="Enter API Token:").pack(pady=5)
    token_entry = tk.Entry(root, show="*")
    token_entry.pack()

    tk.Checkbutton(root, text="Save credentials?", variable=save_cred).pack()

    if os.path.exists('static_api.txt'):
        with open('static_api.txt', 'r') as f:
            line = f.readline().strip()
            clubcode, api_token = line.split(',')
            clubcode_entry.insert(0, clubcode)
            token_entry.insert(0, api_token)

    tk.Button(root, text="Login", command=try_login).pack(pady=20)

# --- Initialise ---

def main():
    setup_login_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
