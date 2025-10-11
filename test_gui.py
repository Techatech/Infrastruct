import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Test GUI")
    root.geometry("400x300")
    
    label = ttk.Label(root, text="Test GUI is working!")
    label.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    main()