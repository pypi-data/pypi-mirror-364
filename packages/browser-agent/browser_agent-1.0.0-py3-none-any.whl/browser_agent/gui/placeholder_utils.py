"""
CustomTkinter Placeholder Text Utilities

This module provides compatible placeholder text functionality for CustomTkinter widgets
that don't natively support placeholder_text parameter.
"""

import customtkinter as ctk


class PlaceholderTextbox(ctk.CTkTextbox):
    """CTkTextbox with placeholder text functionality"""
    
    def __init__(self, master, placeholder_text="", **kwargs):
        # Remove placeholder_text from kwargs to avoid error
        self.placeholder_text = placeholder_text
        if 'placeholder_text' in kwargs:
            del kwargs['placeholder_text']
            
        super().__init__(master, **kwargs)
        
        self.placeholder_color = "#666666"
        self.default_color = self.cget("text_color") if hasattr(self, 'cget') else "#FFFFFF"
        self.placeholder_active = False
        
        if self.placeholder_text:
            self.show_placeholder()
            self.bind("<FocusIn>", self.on_focus_in)
            self.bind("<FocusOut>", self.on_focus_out)
            self.bind("<Button-1>", self.on_click)
    
    def show_placeholder(self):
        """Show placeholder text"""
        if not self.get("1.0", "end-1c").strip():
            self.delete("1.0", "end")
            self.insert("1.0", self.placeholder_text)
            self.configure(text_color=self.placeholder_color)
            self.placeholder_active = True
    
    def hide_placeholder(self):
        """Hide placeholder text"""
        if self.placeholder_active:
            self.delete("1.0", "end")
            self.configure(text_color=self.default_color)
            self.placeholder_active = False
    
    def on_focus_in(self, event):
        """Handle focus in event"""
        if self.placeholder_active:
            self.hide_placeholder()
    
    def on_focus_out(self, event):
        """Handle focus out event"""
        content = self.get("1.0", "end-1c").strip()
        if not content or content == self.placeholder_text:
            self.show_placeholder()
    
    def on_click(self, event):
        """Handle click event"""
        if self.placeholder_active:
            self.hide_placeholder()
            self.focus_set()
    
    def get_actual_text(self):
        """Get actual text without placeholder"""
        if self.placeholder_active:
            return ""
        return self.get("1.0", "end-1c")
    
    def set_text(self, text):
        """Set text and handle placeholder state"""
        self.delete("1.0", "end")
        if text:
            self.insert("1.0", text)
            self.configure(text_color=self.default_color)
            self.placeholder_active = False
        else:
            self.show_placeholder()


class SafeCTkEntry(ctk.CTkEntry):
    """CTkEntry with safe placeholder_text handling"""
    
    def __init__(self, master, **kwargs):
        # Check if placeholder_text is supported by trying to create widget
        placeholder_text = kwargs.get('placeholder_text', '')
        
        try:
            # Try with placeholder_text first
            super().__init__(master, **kwargs)
        except (ValueError, TypeError) as e:
            if 'placeholder_text' in str(e):
                # Remove placeholder_text and create without it
                kwargs_safe = kwargs.copy()
                kwargs_safe.pop('placeholder_text', None)
                super().__init__(master, **kwargs_safe)
                
                # Add placeholder functionality manually if needed
                if placeholder_text:
                    self._add_placeholder_functionality(placeholder_text)
            else:
                raise e
    
    def _add_placeholder_functionality(self, placeholder_text):
        """Add manual placeholder functionality"""
        self.placeholder_text = placeholder_text
        self.placeholder_color = "#666666"
        self.default_color = "#FFFFFF"
        self.placeholder_active = True
        
        # Set initial placeholder
        self.insert(0, placeholder_text)
        self.configure(text_color=self.placeholder_color)
        
        # Bind events
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Handle focus in"""
        if self.placeholder_active and self.get() == self.placeholder_text:
            self.delete(0, "end")
            self.configure(text_color=self.default_color)
            self.placeholder_active = False
    
    def _on_focus_out(self, event):
        """Handle focus out"""
        if not self.get():
            self.insert(0, self.placeholder_text)
            self.configure(text_color=self.placeholder_color)
            self.placeholder_active = True


def create_safe_textbox(master, placeholder_text="", **kwargs):
    """Create a safe textbox that handles placeholder_text properly"""
    return PlaceholderTextbox(master, placeholder_text=placeholder_text, **kwargs)


def create_safe_entry(master, **kwargs):
    """Create a safe entry that handles placeholder_text properly"""
    return SafeCTkEntry(master, **kwargs)