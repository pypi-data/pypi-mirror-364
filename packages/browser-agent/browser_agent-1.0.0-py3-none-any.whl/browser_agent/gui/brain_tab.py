import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, Optional
import threading

from ..core.multi_llm_processor import LLMProvider, LLMModel


class BrainTab:
    """Brain/LLM management tab for selecting and configuring AI models"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.available_models = []
        
        self.create_widgets()
        self.setup_layout()
    
    def create_widgets(self):
        """Create brain tab widgets"""
        # Main container
        self.main_container = ctk.CTkScrollableFrame(self.parent)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_container)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🧠 AI Brain Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Select and configure your AI model for optimal performance",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        
        # API Keys Section
        self.api_keys_frame = ctk.CTkFrame(self.main_container)
        self.create_api_keys_section()
        
        # Model Selection Section
        self.model_selection_frame = ctk.CTkFrame(self.main_container)
        self.create_model_selection_section()
        
        # Model Configuration Section
        self.model_config_frame = ctk.CTkFrame(self.main_container)
        self.create_model_config_section()
        
        # Performance Metrics Section
        self.metrics_frame = ctk.CTkFrame(self.main_container)
        self.create_metrics_section()
        
        # Test Section
        self.test_frame = ctk.CTkFrame(self.main_container)
        self.create_test_section()
    
    def create_api_keys_section(self):
        """Create API keys configuration section"""
        # Section header
        api_header = ctk.CTkLabel(
            self.api_keys_frame,
            text="🔑 API Keys Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        api_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # OpenAI API Key
        openai_frame = ctk.CTkFrame(self.api_keys_frame, fg_color="transparent")
        openai_frame.pack(fill="x", padx=20, pady=5)
        
        openai_label = ctk.CTkLabel(
            openai_frame,
            text="OpenAI API Key:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        openai_label.pack(side="left", padx=(0, 10))
        
        self.openai_key_entry = ctk.CTkEntry(
            openai_frame,
            placeholder_text="sk-...",
            show="*",
            width=300
        )
        self.openai_key_entry.pack(side="left", padx=(0, 10))
        
        self.openai_status = ctk.CTkLabel(
            openai_frame,
            text="❌ Not configured",
            font=ctk.CTkFont(size=10)
        )
        self.openai_status.pack(side="left")
        
        # Claude API Key
        claude_frame = ctk.CTkFrame(self.api_keys_frame, fg_color="transparent")
        claude_frame.pack(fill="x", padx=20, pady=5)
        
        claude_label = ctk.CTkLabel(
            claude_frame,
            text="Claude API Key:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        claude_label.pack(side="left", padx=(0, 10))
        
        self.claude_key_entry = ctk.CTkEntry(
            claude_frame,
            placeholder_text="sk-ant-...",
            show="*",
            width=300
        )
        self.claude_key_entry.pack(side="left", padx=(0, 10))
        
        self.claude_status = ctk.CTkLabel(
            claude_frame,
            text="❌ Not configured",
            font=ctk.CTkFont(size=10)
        )
        self.claude_status.pack(side="left")
        
        # Gemini API Key
        gemini_frame = ctk.CTkFrame(self.api_keys_frame, fg_color="transparent")
        gemini_frame.pack(fill="x", padx=20, pady=5)
        
        gemini_label = ctk.CTkLabel(
            gemini_frame,
            text="Gemini API Key:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        gemini_label.pack(side="left", padx=(0, 10))
        
        self.gemini_key_entry = ctk.CTkEntry(
            gemini_frame,
            placeholder_text="AI...",
            show="*",
            width=300
        )
        self.gemini_key_entry.pack(side="left", padx=(0, 10))
        
        self.gemini_status = ctk.CTkLabel(
            gemini_frame,
            text="❌ Not configured",
            font=ctk.CTkFont(size=10)
        )
        self.gemini_status.pack(side="left")
        
        # Save button
        self.save_keys_button = ctk.CTkButton(
            self.api_keys_frame,
            text="💾 Save API Keys",
            command=self.save_api_keys,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.save_keys_button.pack(pady=(10, 20))
    
    def create_model_selection_section(self):
        """Create model selection section"""
        # Section header
        model_header = ctk.CTkLabel(
            self.model_selection_frame,
            text="🎯 Model Selection",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        model_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Current model display
        current_frame = ctk.CTkFrame(self.model_selection_frame, fg_color="transparent")
        current_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        current_label = ctk.CTkLabel(
            current_frame,
            text="Current Model:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        current_label.pack(side="left")
        
        self.current_model_label = ctk.CTkLabel(
            current_frame,
            text="Not selected",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.current_model_label.pack(side="left", padx=(10, 0))
        
        # Model selection grid
        self.models_container = ctk.CTkFrame(self.model_selection_frame)
        self.models_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Will be populated by refresh_models()
    
    def create_model_config_section(self):
        """Create model configuration section"""
        # Section header
        config_header = ctk.CTkLabel(
            self.model_config_frame,
            text="⚙️ Model Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        config_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Temperature setting
        temp_frame = ctk.CTkFrame(self.model_config_frame, fg_color="transparent")
        temp_frame.pack(fill="x", padx=20, pady=5)
        
        temp_label = ctk.CTkLabel(
            temp_frame,
            text="Temperature (Creativity):",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=200
        )
        temp_label.pack(side="left")
        
        self.temperature_slider = ctk.CTkSlider(
            temp_frame,
            from_=0.0,
            to=2.0,
            number_of_steps=20,
            width=200
        )
        self.temperature_slider.pack(side="left", padx=10)
        self.temperature_slider.set(0.1)
        
        self.temp_value_label = ctk.CTkLabel(
            temp_frame,
            text="0.1",
            font=ctk.CTkFont(size=11)
        )
        self.temp_value_label.pack(side="left", padx=(10, 0))
        
        # Bind slider change
        self.temperature_slider.configure(command=self.on_temperature_change)
        
        # Max tokens setting
        tokens_frame = ctk.CTkFrame(self.model_config_frame, fg_color="transparent")
        tokens_frame.pack(fill="x", padx=20, pady=5)
        
        tokens_label = ctk.CTkLabel(
            tokens_frame,
            text="Max Tokens:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=200
        )
        tokens_label.pack(side="left")
        
        self.max_tokens_entry = ctk.CTkEntry(
            tokens_frame,
            placeholder_text="2000",
            width=100
        )
        self.max_tokens_entry.pack(side="left", padx=10)
        self.max_tokens_entry.insert(0, "2000")
        
        # Apply button
        self.apply_config_button = ctk.CTkButton(
            self.model_config_frame,
            text="✅ Apply Configuration",
            command=self.apply_model_config,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.apply_config_button.pack(pady=(10, 20))
    
    def create_metrics_section(self):
        """Create performance metrics section"""
        # Section header
        metrics_header = ctk.CTkLabel(
            self.metrics_frame,
            text="📊 Performance Metrics",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        metrics_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Metrics grid
        metrics_grid = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        metrics_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        # Response time
        response_frame = ctk.CTkFrame(metrics_grid)
        response_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        response_title = ctk.CTkLabel(
            response_frame,
            text="⚡ Avg Response Time",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        response_title.pack(pady=(10, 5))
        
        self.response_time_label = ctk.CTkLabel(
            response_frame,
            text="-- ms",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        self.response_time_label.pack(pady=(0, 10))
        
        # Success rate
        success_frame = ctk.CTkFrame(metrics_grid)
        success_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        success_title = ctk.CTkLabel(
            success_frame,
            text="✅ Success Rate",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        success_title.pack(pady=(10, 5))
        
        self.success_rate_label = ctk.CTkLabel(
            success_frame,
            text="--%",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        )
        self.success_rate_label.pack(pady=(0, 10))
        
        # Cost estimate
        cost_frame = ctk.CTkFrame(metrics_grid)
        cost_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        cost_title = ctk.CTkLabel(
            cost_frame,
            text="💰 Est. Cost/1k tokens",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cost_title.pack(pady=(10, 5))
        
        self.cost_label = ctk.CTkLabel(
            cost_frame,
            text="$0.000",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FF9800"
        )
        self.cost_label.pack(pady=(0, 10))
    
    def create_test_section(self):
        """Create model testing section"""
        # Section header
        test_header = ctk.CTkLabel(
            self.test_frame,
            text="🧪 Test AI Model",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        test_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Test input
        test_input_frame = ctk.CTkFrame(self.test_frame, fg_color="transparent")
        test_input_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        test_label = ctk.CTkLabel(
            test_input_frame,
            text="Test Prompt:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        test_label.pack(anchor="w")
        
        self.test_input = ctk.CTkTextbox(
            test_input_frame,
            height=60,
            font=ctk.CTkFont(size=11)
        )
        self.test_input.pack(fill="x", pady=(5, 0))
        self.test_input.insert("1.0", "Hello! Can you help me search for Python tutorials?")
        
        # Test button
        self.test_button = ctk.CTkButton(
            self.test_frame,
            text="🚀 Test Model",
            command=self.test_model,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.test_button.pack(pady=10)
        
        # Test result
        self.test_result = ctk.CTkTextbox(
            self.test_frame,
            height=100,
            font=ctk.CTkFont(size=11)
        )
        self.test_result.pack(fill="x", padx=20, pady=(0, 20))
        self.test_result.configure(state="disabled")
    
    def setup_layout(self):
        """Setup the layout"""
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pack sections
        self.header_frame.pack(fill="x", pady=(0, 20))
        self.title_label.pack(anchor="w", padx=20, pady=(20, 5))
        self.subtitle_label.pack(anchor="w", padx=20, pady=(0, 20))
        
        self.api_keys_frame.pack(fill="x", pady=(0, 20))
        self.model_selection_frame.pack(fill="both", expand=True, pady=(0, 20))
        self.model_config_frame.pack(fill="x", pady=(0, 20))
        self.metrics_frame.pack(fill="x", pady=(0, 20))
        self.test_frame.pack(fill="x", pady=(0, 20))
        
        # Load current configuration
        self.load_current_config()
    
    def load_current_config(self):
        """Load current configuration into UI"""
        if self.main_window.config:
            config = self.main_window.config
            
            # Load API keys (masked)
            if config.openai_api_key:
                self.openai_key_entry.insert(0, "sk-" + "*" * 20)
                self.openai_status.configure(text="✅ Configured", text_color="#4CAF50")
            
            if config.claude_api_key:
                self.claude_key_entry.insert(0, "sk-ant-" + "*" * 20)
                self.claude_status.configure(text="✅ Configured", text_color="#4CAF50")
            
            if config.gemini_api_key:
                self.gemini_key_entry.insert(0, "AI" + "*" * 20)
                self.gemini_status.configure(text="✅ Configured", text_color="#4CAF50")
            
            # Load model configuration
            self.temperature_slider.set(config.temperature)
            self.temp_value_label.configure(text=f"{config.temperature:.1f}")
            self.max_tokens_entry.delete(0, "end")
            self.max_tokens_entry.insert(0, str(config.max_tokens))
    
    def refresh_models(self):
        """Refresh available models list"""
        if not self.main_window.llm_processor:
            return
        
        # Clear existing model widgets
        for widget in self.models_container.winfo_children():
            widget.destroy()
        
        # Get available models
        self.available_models = self.main_window.llm_processor.get_available_models()
        
        if not self.available_models:
            no_models_label = ctk.CTkLabel(
                self.models_container,
                text="No models available. Please configure API keys first.",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            no_models_label.pack(pady=20)
            return
        
        # Create model selection cards
        for i, model in enumerate(self.available_models):
            row = i // 2
            col = i % 2
            
            if col == 0:
                row_frame = ctk.CTkFrame(self.models_container, fg_color="transparent")
                row_frame.pack(fill="x", padx=10, pady=5)
            
            model_card = self.create_model_card(row_frame, model)
            model_card.pack(side="left", fill="both", expand=True, padx=(0, 10 if col == 0 else 0))
        
        # Update current model display
        current_model = self.main_window.llm_processor.get_current_model()
        if current_model:
            self.current_model_label.configure(text=f"{current_model.display_name}")
    
    def create_model_card(self, parent, model: LLMModel):
        """Create a model selection card"""
        card = ctk.CTkFrame(parent)
        
        # Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Provider icon
        provider_icons = {
            LLMProvider.OPENAI: "🔥",
            LLMProvider.CLAUDE: "🤖",
            LLMProvider.GEMINI: "💎"
        }
        
        icon = ctk.CTkLabel(
            header_frame,
            text=provider_icons.get(model.provider, "🤖"),
            font=ctk.CTkFont(size=20)
        )
        icon.pack(side="left")
        
        title = ctk.CTkLabel(
            header_frame,
            text=model.display_name,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(side="left", padx=(10, 0))
        
        # Description
        desc = ctk.CTkLabel(
            card,
            text=model.description,
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            wraplength=200
        )
        desc.pack(padx=15, pady=(0, 5))
        
        # Specs
        specs_frame = ctk.CTkFrame(card, fg_color="transparent")
        specs_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        max_tokens_spec = ctk.CTkLabel(
            specs_frame,
            text=f"Max: {model.max_tokens:,} tokens",
            font=ctk.CTkFont(size=9),
            text_color="#666666"
        )
        max_tokens_spec.pack(side="left")
        
        cost_spec = ctk.CTkLabel(
            specs_frame,
            text=f"${model.cost_per_1k_tokens:.4f}/1k",
            font=ctk.CTkFont(size=9),
            text_color="#666666"
        )
        cost_spec.pack(side="right")
        
        # Select button
        select_btn = ctk.CTkButton(
            card,
            text="Select",
            command=lambda m=model: self.select_model(m),
            height=30,
            font=ctk.CTkFont(size=11)
        )
        select_btn.pack(padx=15, pady=(0, 15))
        
        return card
    
    def select_model(self, model: LLMModel):
        """Select a model"""
        if self.main_window.llm_processor:
            self.main_window.llm_processor.set_model(model.provider, model.model_name)
            self.current_model_label.configure(text=f"{model.display_name}")
            
            # Update metrics
            self.cost_label.configure(text=f"${model.cost_per_1k_tokens:.4f}")
            
            # Update main window status
            self.main_window.update_ai_status("Ready", model.display_name)
    
    def on_temperature_change(self, value):
        """Handle temperature slider change"""
        self.temp_value_label.configure(text=f"{value:.1f}")
    
    def save_api_keys(self):
        """Save API keys to configuration"""
        # Note: In production, these should be saved securely
        openai_key = self.openai_key_entry.get()
        claude_key = self.claude_key_entry.get()
        gemini_key = self.gemini_key_entry.get()
        
        # Update configuration
        if openai_key and not openai_key.startswith("sk-*"):
            self.main_window.config.openai_api_key = openai_key
        if claude_key and not claude_key.startswith("sk-ant-*"):
            self.main_window.config.claude_api_key = claude_key
        if gemini_key and not gemini_key.startswith("AI*"):
            self.main_window.config.gemini_api_key = gemini_key
        
        # Reinitialize LLM processor
        self.main_window.llm_processor = MultiLLMProcessor(self.main_window.config)
        
        # Refresh models
        self.refresh_models()
        
        # Show success message
        self.main_window.show_info_dialog("Success", "API keys saved successfully!")
    
    def apply_model_config(self):
        """Apply model configuration"""
        temperature = self.temperature_slider.get()
        max_tokens = self.max_tokens_entry.get()
        
        try:
            max_tokens_int = int(max_tokens)
            
            # Update configuration
            self.main_window.config.temperature = temperature
            self.main_window.config.max_tokens = max_tokens_int
            
            # Show success message
            self.main_window.show_info_dialog("Success", "Model configuration applied!")
            
        except ValueError:
            self.main_window.show_error_dialog("Error", "Invalid max tokens value. Please enter a number.")
    
    def test_model(self):
        """Test the current model"""
        if not self.main_window.llm_processor:
            self.main_window.show_error_dialog("Error", "No AI model configured.")
            return
        
        test_prompt = self.test_input.get("1.0", "end-1c").strip()
        if not test_prompt:
            self.main_window.show_error_dialog("Error", "Please enter a test prompt.")
            return
        
        def test_worker():
            try:
                self.parent.after(0, lambda: self.test_button.configure(text="🔄 Testing...", state="disabled"))
                self.parent.after(0, lambda: self.test_result.configure(state="normal"))
                self.parent.after(0, lambda: self.test_result.delete("1.0", "end"))
                self.parent.after(0, lambda: self.test_result.insert("1.0", "Testing model..."))
                self.parent.after(0, lambda: self.test_result.configure(state="disabled"))
                
                import asyncio
                response = asyncio.run(self.main_window.llm_processor.generate_response(test_prompt))
                
                self.parent.after(0, lambda: self.test_result.configure(state="normal"))
                self.parent.after(0, lambda: self.test_result.delete("1.0", "end"))
                self.parent.after(0, lambda: self.test_result.insert("1.0", response))
                self.parent.after(0, lambda: self.test_result.configure(state="disabled"))
                
            except Exception as e:
                self.parent.after(0, lambda: self.test_result.configure(state="normal"))
                self.parent.after(0, lambda: self.test_result.delete("1.0", "end"))
                self.parent.after(0, lambda: self.test_result.insert("1.0", f"Error: {str(e)}"))
                self.parent.after(0, lambda: self.test_result.configure(state="disabled"))
            finally:
                self.parent.after(0, lambda: self.test_button.configure(text="🚀 Test Model", state="normal"))
        
        threading.Thread(target=test_worker, daemon=True).start()