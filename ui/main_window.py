"""
Main Window Module

This module contains the main window UI for the voice assistant.
"""
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import Optional, Dict, Any

import config
from voice_assistant.assistant_manager import AssistantManager

logger = logging.getLogger(__name__)

class MainWindow:
    """
    Main window UI for the voice assistant.
    """
    
    def __init__(self, assistant_manager: AssistantManager):
        """
        Initialize the main window.
        
        Args:
            assistant_manager: The assistant manager instance.
        """
        self.assistant_manager = assistant_manager
        
        # Set up callbacks
        self.assistant_manager.set_callbacks(
            on_listening_start=self.on_listening_start,
            on_listening_end=self.on_listening_end,
            on_speaking_start=self.on_speaking_start,
            on_speaking_end=self.on_speaking_end,
            on_response=self.on_response,
            on_user_info_change=self.on_user_info_change
        )
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("AI Voice Assistant")
        self.root.geometry(f"{config.UI_WINDOW_WIDTH}x{config.UI_WINDOW_HEIGHT}")
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use(config.UI_THEME)
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the conversation display
        self.create_conversation_display()
        
        # Create the input area
        self.create_input_area()
        
        # Create the control buttons
        self.create_control_buttons()
        
        # Create the status bar
        self.create_status_bar()
        
        # Create the user info frame
        self.create_user_info_frame()
        
        # Set up hotkey
        self.root.bind(config.UI_HOTKEY, self.on_hotkey)
        
        # Initialize status
        self.update_status("Ready")
        
        # Get initial user info
        user_info = self.assistant_manager.get_user_info()
        self.user_name_var.set(user_info['user_name'])
        self.user_type_var.set(user_info['user_type'])
        
        logger.info("Main window initialized")
    
    def create_conversation_display(self):
        """Create the conversation display area."""
        conversation_frame = ttk.LabelFrame(self.main_frame, text="Conversation", padding="5")
        conversation_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.conversation_text = scrolledtext.ScrolledText(
            conversation_frame,
            wrap=tk.WORD,
            width=50,
            height=15,
            font=("TkDefaultFont", 10)
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.config(state=tk.DISABLED)
    
    def create_input_area(self):
        """Create the text input area."""
        input_frame = ttk.Frame(self.main_frame, padding="5")
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Text Input:").pack(side=tk.LEFT, padx=5)
        
        self.input_text = ttk.Entry(input_frame, width=50)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_text.bind("<Return>", self.on_send_text)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.on_send_text)
        send_button.pack(side=tk.RIGHT, padx=5)
    
    def create_control_buttons(self):
        """Create the control buttons."""
        button_frame = ttk.Frame(self.main_frame, padding="5")
        button_frame.pack(fill=tk.X, pady=5)
        
        self.listen_button = ttk.Button(
            button_frame,
            text="Listen (Press Space)",
            command=self.on_listen_button
        )
        self.listen_button.pack(side=tk.LEFT, padx=5)
        
        self.repeat_button = ttk.Button(
            button_frame,
            text="Repeat Last",
            command=self.on_repeat_button
        )
        self.repeat_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear History",
            command=self.on_clear_button
        )
        self.clear_button.pack(side=tk.RIGHT, padx=5)
    
    def create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.main_frame, padding="5")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
    
    def create_user_info_frame(self):
        """Create the user information frame."""
        user_frame = ttk.LabelFrame(self.main_frame, text="User Information", padding="5")
        user_frame.pack(fill=tk.X, pady=5)
        
        # User name
        name_frame = ttk.Frame(user_frame)
        name_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT, padx=5)
        
        self.user_name_var = tk.StringVar()
        self.user_name_entry = ttk.Entry(name_frame, textvariable=self.user_name_var, width=20)
        self.user_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # User type
        type_frame = ttk.Frame(user_frame)
        type_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        
        self.user_type_var = tk.StringVar()
        self.user_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.user_type_var,
            values=["staff", "student"],
            state="readonly",
            width=20
        )
        self.user_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Update button
        update_button = ttk.Button(
            user_frame,
            text="Update User Info",
            command=self.on_update_user_info
        )
        update_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def run(self):
        """Run the main window loop."""
        self.root.mainloop()
    
    def update_status(self, status: str):
        """
        Update the status bar.
        
        Args:
            status: The status text to display.
        """
        self.status_label.config(text=status)
    
    def add_to_conversation(self, speaker: str, text: str):
        """
        Add a message to the conversation display.
        
        Args:
            speaker: The speaker name.
            text: The message text.
        """
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.insert(tk.END, f"{speaker}: {text}\n\n")
        self.conversation_text.see(tk.END)
        self.conversation_text.config(state=tk.DISABLED)
    
    def on_hotkey(self, event):
        """
        Handle the hotkey press event.
        
        Args:
            event: The key event.
        """
        self.on_listen_button()
    
    def on_listen_button(self):
        """Handle the listen button click."""
        if not self.assistant_manager.is_listening:
            self.update_status("Listening...")
            self.listen_button.config(state=tk.DISABLED)
            self.assistant_manager.listen_and_respond()
    
    def on_send_text(self, event=None):
        """
        Handle the send text button click or Enter key.
        
        Args:
            event: The event that triggered this (optional).
        """
        text = self.input_text.get().strip()
        if text:
            self.add_to_conversation("You", text)
            self.input_text.delete(0, tk.END)
            
            # Process in a separate thread to avoid blocking the UI
            threading.Thread(
                target=self.assistant_manager.process_text_input,
                args=(text,),
                daemon=True
            ).start()
    
    def on_repeat_button(self):
        """Handle the repeat button click."""
        self.assistant_manager.repeat_last_response()
    
    def on_clear_button(self):
        """Handle the clear button click."""
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.delete(1.0, tk.END)
        self.conversation_text.config(state=tk.DISABLED)
        self.assistant_manager.clear_conversation_history()
    
    def on_update_user_info(self):
        """Handle the update user info button click."""
        user_name = self.user_name_var.get().strip()
        user_type = self.user_type_var.get()
        
        if not user_name:
            messagebox.showerror("Error", "User name cannot be empty")
            return
        
        if not user_type:
            messagebox.showerror("Error", "Please select a user type")
            return
        
        self.assistant_manager.set_user_info(user_name=user_name, user_type=user_type)
        messagebox.showinfo("Success", "User information updated")
    
    def on_listening_start(self):
        """Handle the listening start event."""
        self.update_status("Listening...")
        self.listen_button.config(state=tk.DISABLED)
    
    def on_listening_end(self):
        """Handle the listening end event."""
        self.update_status("Processing...")
        self.listen_button.config(state=tk.NORMAL)
    
    def on_speaking_start(self):
        """Handle the speaking start event."""
        self.update_status("Speaking...")
    
    def on_speaking_end(self):
        """Handle the speaking end event."""
        self.update_status("Ready")
    
    def on_response(self, response_data: Dict[str, Any]):
        """
        Handle the response event.
        
        Args:
            response_data: The response data.
        """
        query = response_data.get('query', '')
        response = response_data.get('response', '')
        
        if query and not response_data.get('is_command', False):
            self.add_to_conversation("You", query)
        
        if response:
            self.add_to_conversation("Assistant", response)
    
    def on_user_info_change(self, user_name: str, user_type: str):
        """
        Handle the user info change event.
        
        Args:
            user_name: The new user name.
            user_type: The new user type.
        """
        self.user_name_var.set(user_name)
        self.user_type_var.set(user_type)
        self.update_status(f"User info updated: {user_name} ({user_type})")