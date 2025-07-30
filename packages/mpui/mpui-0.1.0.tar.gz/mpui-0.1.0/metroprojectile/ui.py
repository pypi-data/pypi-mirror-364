import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Callable

class Theme:
    LIGHT = {
        'bg': '#f5f5f5',
        'fg': '#333333',
        'accent': '#0078d7',
        'hover': '#e5f1fb',
        'press': '#cce4f7',
    }
    
    DARK = {
        'bg': '#202020',
        'fg': '#ffffff',
        'accent': '#0078d7',
        'hover': '#383838',
        'press': '#4a4a4a',
    }

_current_theme = Theme.LIGHT

def set_theme(theme: dict):
    """Set the current theme for all MPUI widgets"""
    global _current_theme
    _current_theme = theme

class Window(tk.Tk):
    def __init__(self, title: str = "MPUI Window", size: Tuple[int, int] = (800, 600)):
        super().__init__()
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.configure(bg=_current_theme['bg'])
        
        self.style = ttk.Style()
        self._update_theme()
        
    def _update_theme(self):
        self.configure(bg=_current_theme['bg'])
        self.style.theme_use('clam')
        
        self.style.configure('.', 
                           background=_current_theme['bg'],
                           foreground=_current_theme['fg'],
                           font=('Segoe UI', 10))
        
        self.style.map('TButton',
                     background=[('active', _current_theme['hover']),
                                ('pressed', _current_theme['press'])],
                     foreground=[('active', _current_theme['fg']),
                                ('pressed', _current_theme['fg'])])

class Button(ttk.Button):
    def __init__(self, master, text: str = "Button", command: Optional[Callable] = None):
        super().__init__(master, text=text, command=command)
        self._style = ttk.Style()
        self._configure_style()
        
    def _configure_style(self):
        self._style.configure('MPUI.TButton',
                            background=_current_theme['accent'],
                            foreground=_current_theme['fg'],
                            borderwidth=0,
                            focuscolor=_current_theme['bg'],
                            font=('Segoe UI', 10, 'bold'),
                            padding=10)
        self.configure(style='MPUI.TButton')

class TextBox(ttk.Entry):
    def __init__(self, master, placeholder: str = ""):
        self._placeholder = placeholder
        super().__init__(master)
        self._setup_placeholder()
        
    def _setup_placeholder(self):
        if self._placeholder:
            self.insert(0, self._placeholder)
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._restore_placeholder)
            
    def _clear_placeholder(self, event):
        if self.get() == self._placeholder:
            self.delete(0, tk.END)
            
    def _restore_placeholder(self, event):
        if not self.get():
            self.insert(0, self._placeholder)
