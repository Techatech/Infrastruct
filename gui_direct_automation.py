#!/usr/bin/env python3
"""
GUI Integration for Direct Nova-Act Automation
Shows real-time progress of browser automation
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from direct_nova_act_automation import deploy_with_direct_automation

class DirectAutomationGUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.automation_running = False
        
    def create_automation_panel(self):
        """Create the direct automation panel"""
        # Automation frame
        automation_frame = ttk.LabelFrame(self.parent_frame, text="🤖 Direct Nova-Act Automation", padding=10)
        automation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        automation_frame.columnconfigure(0, weight=1)
        
        # Progress display
        self.progress_display = tk.Text(automation_frame, height=15, width=80, wrap=tk.WORD)
        progress_scrollbar = ttk.Scrollbar(automation_frame, orient="vertical", command=self.progress_display.yview)
        self.progress_display.configure(yscrollcommand=progress_scrollbar.set)
        
        self.progress_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(automation_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(automation_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Start Direct Automation", 
                                   command=self.start_direct_automation)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Automation", 
                                  command=self.stop_automation, state='disabled')
        self.stop_btn.pack(side=tk.LEFT)
        
        return automation_frame
    
    def add_progress_message(self, message: str, message_type: str = "info"):
        """Add a progress message to the display"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "info": "blue",
            "success": "green", 
            "warning": "orange",
            "error": "red"
        }
        
        color = colors.get(message_type, "black")
        
        self.progress_display.config(state='normal')
        self.progress_display.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Apply color to the last line
        line_start = self.progress_display.index("end-2c linestart")
        line_end = self.progress_display.index("end-2c lineend")
        self.progress_display.tag_add(message_type, line_start, line_end)
        self.progress_display.tag_config(message_type, foreground=color)
        
        self.progress_display.config(state='disabled')
        self.progress_display.see(tk.END)
    
    def start_direct_automation(self):
        """Start the direct Nova-Act automation"""
        if self.automation_running:
            return
        
        # Get deployment details (you'll need to pass these from your main GUI)
        template_url = "https://infrastruct.s3.us-east-1.amazonaws.com/test-template.yaml"
        stack_name = "direct-automation-test"
        
        self.automation_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_bar.start()
        
        # Clear previous messages
        self.progress_display.config(state='normal')
        self.progress_display.delete(1.0, tk.END)
        self.progress_display.config(state='disabled')
        
        # Start automation in background thread
        threading.Thread(target=self.run_automation, 
                        args=(template_url, stack_name), daemon=True).start()
    
    def run_automation(self, template_url: str, stack_name: str):
        """Run the automation in background thread"""
        try:
            def progress_callback(message):
                # Update GUI from background thread
                self.parent_frame.after(0, lambda: self.add_progress_message(message, "info"))
            
            self.add_progress_message("🚀 Starting direct Nova-Act automation...", "info")
            self.add_progress_message(f"📋 Stack: {stack_name}", "info")
            self.add_progress_message(f"🌐 Template: {template_url}", "info")
            
            # Run the automation
            result = deploy_with_direct_automation(template_url, stack_name, progress_callback)
            
            # Handle result
            if result['success']:
                self.add_progress_message("✅ Automation completed successfully!", "success")
                self.add_progress_message(f"Status: {result['status']}", "success")
                self.add_progress_message(f"Message: {result['message']}", "success")
            else:
                self.add_progress_message("❌ Automation failed", "error")
                self.add_progress_message(f"Error: {result.get('error', 'Unknown error')}", "error")
                
        except Exception as e:
            self.add_progress_message(f"❌ Automation exception: {str(e)}", "error")
        
        finally:
            # Reset UI state
            self.parent_frame.after(0, self.automation_completed)
    
    def automation_completed(self):
        """Reset UI after automation completes"""
        self.automation_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_bar.stop()
        self.add_progress_message("🏁 Automation session completed", "info")
    
    def stop_automation(self):
        """Stop the automation (placeholder - actual implementation would need to interrupt Nova-Act)"""
        self.add_progress_message("⏹️ Stopping automation...", "warning")
        self.automation_completed()

# Example usage function
def create_direct_automation_window():
    """Create a standalone window for direct automation testing"""
    root = tk.Tk()
    root.title("Direct Nova-Act Automation")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)
    
    # Create automation GUI
    automation_gui = DirectAutomationGUI(main_frame)
    automation_gui.create_automation_panel()
    
    # Configure root window
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    return root, automation_gui

if __name__ == "__main__":
    root, gui = create_direct_automation_window()
    root.mainloop()