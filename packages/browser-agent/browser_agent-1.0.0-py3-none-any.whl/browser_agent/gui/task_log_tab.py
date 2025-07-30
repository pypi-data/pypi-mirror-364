import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


class TaskLogTab:
    """Task log and history management interface"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.filtered_tasks = []
        self.current_filter = "all"
        self.sort_order = "newest"
        
        self.create_widgets()
        self.setup_layout()
        self.refresh_history()
    
    def create_widgets(self):
        """Create task log tab widgets"""
        # Main container
        self.main_container = ctk.CTkFrame(self.parent)
        
        # Header section
        self.header_section = ctk.CTkFrame(self.main_container)
        self.create_header()
        
        # Filter and search section
        self.filter_section = ctk.CTkFrame(self.main_container)
        self.create_filters()
        
        # Statistics section
        self.stats_section = ctk.CTkFrame(self.main_container)
        self.create_statistics()
        
        # Task list section
        self.list_section = ctk.CTkFrame(self.main_container)
        self.create_task_list()
        
        # Details section
        self.details_section = ctk.CTkFrame(self.main_container)
        self.create_details_panel()
    
    def create_header(self):
        """Create header section"""
        title_label = ctk.CTkLabel(
            self.header_section,
            text="📜 Task History & Logs",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle_label = ctk.CTkLabel(
            self.header_section,
            text="Track and analyze your automation tasks and interactions",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle_label.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_filters(self):
        """Create filter and search controls"""
        # Filter controls
        filter_frame = ctk.CTkFrame(self.filter_section, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Status filter
        status_label = ctk.CTkLabel(
            filter_frame,
            text="Filter:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.pack(side="left")
        
        self.status_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Completed", "Failed", "In Progress"],
            command=self.on_filter_change,
            width=120
        )
        self.status_filter.pack(side="left", padx=(10, 20))
        
        # Time filter
        time_label = ctk.CTkLabel(
            filter_frame,
            text="Time:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        time_label.pack(side="left")
        
        self.time_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Time", "Today", "This Week", "This Month"],
            command=self.on_time_filter_change,
            width=120
        )
        self.time_filter.pack(side="left", padx=(10, 20))
        
        # Sort order
        sort_label = ctk.CTkLabel(
            filter_frame,
            text="Sort:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        sort_label.pack(side="left")
        
        self.sort_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["Newest First", "Oldest First", "By Status"],
            command=self.on_sort_change,
            width=120
        )
        self.sort_filter.pack(side="left", padx=(10, 20))
        
        # Search
        search_frame = ctk.CTkFrame(self.filter_section, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(side="left")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search tasks by prompt or response...",
            font=ctk.CTkFont(size=11)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Clear/Export buttons
        buttons_frame = ctk.CTkFrame(self.filter_section, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.clear_button = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Clear History",
            command=self.clear_history,
            width=120,
            height=30,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.clear_button.pack(side="left")
        
        self.export_button = ctk.CTkButton(
            buttons_frame,
            text="📁 Export",
            command=self.export_history,
            width=100,
            height=30
        )
        self.export_button.pack(side="left", padx=(10, 0))
        
        self.refresh_button = ctk.CTkButton(
            buttons_frame,
            text="🔄 Refresh",
            command=self.refresh_history,
            width=100,
            height=30
        )
        self.refresh_button.pack(side="right")
    
    def create_statistics(self):
        """Create statistics section"""
        stats_label = ctk.CTkLabel(
            self.stats_section,
            text="📊 Statistics",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Stats grid
        stats_grid = ctk.CTkFrame(self.stats_section, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        # Total tasks
        total_frame = ctk.CTkFrame(stats_grid)
        total_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        total_title = ctk.CTkLabel(
            total_frame,
            text="📋 Total Tasks",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        total_title.pack(pady=(10, 2))
        
        self.total_tasks_label = ctk.CTkLabel(
            total_frame,
            text="0",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_tasks_label.pack(pady=(0, 10))
        
        # Success rate
        success_frame = ctk.CTkFrame(stats_grid)
        success_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        success_title = ctk.CTkLabel(
            success_frame,
            text="✅ Success Rate",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        success_title.pack(pady=(10, 2))
        
        self.success_rate_label = ctk.CTkLabel(
            success_frame,
            text="0%",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        self.success_rate_label.pack(pady=(0, 10))
        
        # Average time
        time_frame = ctk.CTkFrame(stats_grid)
        time_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        time_title = ctk.CTkLabel(
            time_frame,
            text="⏱️ Avg Time",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        time_title.pack(pady=(10, 2))
        
        self.avg_time_label = ctk.CTkLabel(
            time_frame,
            text="0s",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF9800"
        )
        self.avg_time_label.pack(pady=(0, 10))
    
    def create_task_list(self):
        """Create task list section"""
        list_label = ctk.CTkLabel(
            self.list_section,
            text="📝 Task History",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Task list with scrollbar
        list_frame = ctk.CTkFrame(self.list_section)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create scrollable frame for tasks
        self.tasks_scroll = ctk.CTkScrollableFrame(list_frame)
        self.tasks_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Will be populated by refresh_history()
    
    def create_details_panel(self):
        """Create task details panel"""
        details_label = ctk.CTkLabel(
            self.details_section,
            text="🔍 Task Details",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        details_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Details display
        self.details_display = ctk.CTkTextbox(
            self.details_section,
            height=150,
            font=ctk.CTkFont(size=11, family="monospace")
        )
        self.details_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.details_display.configure(state="disabled")
        
        # Initially show placeholder
        self.show_placeholder_details()
    
    def setup_layout(self):
        """Setup the layout"""
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.header_section.pack(fill="x")
        self.filter_section.pack(fill="x", pady=(0, 10))
        self.stats_section.pack(fill="x", pady=(0, 10))
        self.list_section.pack(fill="both", expand=True, pady=(0, 10))
        self.details_section.pack(fill="x")
    
    def refresh_history(self):
        """Refresh the task history display"""
        # Get tasks from main window
        all_tasks = self.main_window.task_history if hasattr(self.main_window, 'task_history') else []
        
        # Apply filters
        self.filtered_tasks = self.apply_filters(all_tasks)
        
        # Update statistics
        self.update_statistics(all_tasks)
        
        # Update task list
        self.update_task_list()
    
    def apply_filters(self, tasks: List[Dict]) -> List[Dict]:
        """Apply current filters to task list"""
        filtered = tasks.copy()
        
        # Status filter
        if self.current_filter != "all":
            if self.current_filter == "completed":
                filtered = [t for t in filtered if t.get('status') == 'completed']
            elif self.current_filter == "failed":
                filtered = [t for t in filtered if t.get('status') == 'failed']
            elif self.current_filter == "in_progress":
                filtered = [t for t in filtered if t.get('status') == 'in_progress']
        
        # Time filter
        time_filter = self.time_filter.get().lower().replace(" ", "_")
        if time_filter != "all_time":
            now = datetime.now()
            if time_filter == "today":
                cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_filter == "this_week":
                cutoff = now - timedelta(days=7)
            elif time_filter == "this_month":
                cutoff = now - timedelta(days=30)
            else:
                cutoff = None
            
            if cutoff:
                filtered = [
                    t for t in filtered 
                    if datetime.fromisoformat(t['timestamp']) >= cutoff
                ]
        
        # Search filter
        search_term = self.search_entry.get().lower().strip()
        if search_term:
            filtered = [
                t for t in filtered
                if (search_term in t.get('user_prompt', '').lower() or
                    search_term in t.get('ai_response', '').lower())
            ]
        
        # Sort
        if self.sort_order == "newest":
            filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        elif self.sort_order == "oldest":
            filtered.sort(key=lambda x: x['timestamp'])
        elif self.sort_order == "status":
            filtered.sort(key=lambda x: x.get('status', ''))
        
        return filtered
    
    def update_statistics(self, tasks: List[Dict]):
        """Update statistics display"""
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        
        # Calculate success rate
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average execution time
        execution_times = []
        for task in tasks:
            if task.get('execution_result') and hasattr(task['execution_result'], 'execution_time'):
                execution_times.append(task['execution_result'].execution_time)
            elif isinstance(task.get('execution_result'), dict) and 'execution_time' in task['execution_result']:
                execution_times.append(task['execution_result']['execution_time'])
        
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Update labels
        self.total_tasks_label.configure(text=str(total_tasks))
        self.success_rate_label.configure(text=f"{success_rate:.1f}%")
        self.avg_time_label.configure(text=f"{avg_time:.1f}s")
    
    def update_task_list(self):
        """Update the task list display"""
        # Clear existing task widgets
        for widget in self.tasks_scroll.winfo_children():
            widget.destroy()
        
        if not self.filtered_tasks:
            no_tasks_label = ctk.CTkLabel(
                self.tasks_scroll,
                text="No tasks found matching current filters.",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            no_tasks_label.pack(pady=50)
            return
        
        # Create task cards
        for i, task in enumerate(self.filtered_tasks):
            self.create_task_card(task, i)
    
    def create_task_card(self, task: Dict, index: int):
        """Create a task card widget"""
        card = ctk.CTkFrame(self.tasks_scroll)
        card.pack(fill="x", padx=5, pady=5)
        
        # Header with timestamp and status
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Timestamp
        timestamp = datetime.fromisoformat(task['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        time_label = ctk.CTkLabel(
            header_frame,
            text=f"🕐 {timestamp}",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        time_label.pack(side="left")
        
        # Status
        status = task.get('status', 'unknown')
        status_colors = {
            'completed': '#4CAF50',
            'failed': '#e74c3c',
            'in_progress': '#FF9800',
            'unknown': '#888888'
        }
        
        status_icons = {
            'completed': '✅',
            'failed': '❌',
            'in_progress': '🔄',
            'unknown': '❓'
        }
        
        status_label = ctk.CTkLabel(
            header_frame,
            text=f"{status_icons.get(status, '❓')} {status.title()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_colors.get(status, '#888888')
        )
        status_label.pack(side="right")
        
        # User prompt
        prompt_text = task.get('user_prompt', 'No prompt')
        if len(prompt_text) > 100:
            prompt_text = prompt_text[:100] + "..."
        
        prompt_label = ctk.CTkLabel(
            card,
            text=f"👤 {prompt_text}",
            font=ctk.CTkFont(size=11),
            wraplength=400,
            justify="left"
        )
        prompt_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # AI response (truncated)
        response_text = task.get('ai_response', 'No response')
        if len(response_text) > 80:
            response_text = response_text[:80] + "..."
        
        response_label = ctk.CTkLabel(
            card,
            text=f"🤖 {response_text}",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            wraplength=400,
            justify="left"
        )
        response_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # View details button
        details_button = ctk.CTkButton(
            card,
            text="👁️ View Details",
            command=lambda t=task: self.show_task_details(t),
            height=25,
            width=100,
            font=ctk.CTkFont(size=10)
        )
        details_button.pack(side="right", padx=15, pady=(0, 15))
    
    def show_task_details(self, task: Dict):
        """Show detailed information for a task"""
        details = f"""Task Details
{'=' * 50}

Timestamp: {task.get('timestamp', 'Unknown')}
Status: {task.get('status', 'Unknown')}

User Prompt:
{task.get('user_prompt', 'No prompt provided')}

AI Response:
{task.get('ai_response', 'No response provided')}

"""
        
        # Add execution details if available
        if task.get('execution_result'):
            result = task['execution_result']
            if isinstance(result, dict):
                details += f"""Execution Results:
Success: {result.get('success', 'Unknown')}
Execution Time: {result.get('execution_time', 'Unknown')} seconds
Steps Executed: {len(result.get('step_results', []))}
"""
                if result.get('error_message'):
                    details += f"Error: {result['error_message']}\n"
                
                if result.get('screenshots'):
                    details += f"Screenshots: {len(result['screenshots'])}\n"
                    for screenshot in result['screenshots']:
                        details += f"  - {screenshot}\n"
        
        # Show in details panel
        self.details_display.configure(state="normal")
        self.details_display.delete("1.0", "end")
        self.details_display.insert("1.0", details)
        self.details_display.configure(state="disabled")
    
    def show_placeholder_details(self):
        """Show placeholder text in details panel"""
        placeholder = """Task Details Panel

Select a task from the list above to view detailed information including:
• Full user prompt and AI response
• Execution results and timing
• Step-by-step automation logs
• Screenshots and error details
• Status and completion information

Click on "View Details" for any task to see its complete information here."""
        
        self.details_display.configure(state="normal")
        self.details_display.delete("1.0", "end")
        self.details_display.insert("1.0", placeholder)
        self.details_display.configure(state="disabled")
    
    def on_filter_change(self, value):
        """Handle filter change"""
        self.current_filter = value.lower().replace(" ", "_")
        self.refresh_history()
    
    def on_time_filter_change(self, value):
        """Handle time filter change"""
        self.refresh_history()
    
    def on_sort_change(self, value):
        """Handle sort order change"""
        sort_map = {
            "Newest First": "newest",
            "Oldest First": "oldest", 
            "By Status": "status"
        }
        self.sort_order = sort_map.get(value, "newest")
        self.refresh_history()
    
    def on_search_change(self, event):
        """Handle search text change"""
        # Debounce search - refresh after brief delay
        if hasattr(self, '_search_after_id'):
            self.parent.after_cancel(self._search_after_id)
        
        self._search_after_id = self.parent.after(500, self.refresh_history)
    
    def clear_history(self):
        """Clear all task history"""
        # Confirm dialog
        result = tk.messagebox.askyesno(
            "Confirm Clear History",
            "Are you sure you want to clear all task history? This cannot be undone."
        )
        
        if result:
            self.main_window.task_history.clear()
            self.main_window.save_task_history()
            self.refresh_history()
            self.show_placeholder_details()
    
    def export_history(self):
        """Export task history to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Task History",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.main_window.task_history, f, indent=2, default=str)
                else:
                    # Export as readable text
                    with open(filename, 'w') as f:
                        f.write("Browser Agent Task History\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for task in self.main_window.task_history:
                            f.write(f"Timestamp: {task.get('timestamp', 'Unknown')}\n")
                            f.write(f"Status: {task.get('status', 'Unknown')}\n")
                            f.write(f"User Prompt: {task.get('user_prompt', 'None')}\n")
                            f.write(f"AI Response: {task.get('ai_response', 'None')}\n")
                            f.write("-" * 30 + "\n\n")
                
                self.main_window.show_info_dialog("Export Complete", f"Task history exported to {filename}")
                
        except Exception as e:
            self.main_window.show_error_dialog("Export Error", f"Failed to export history: {str(e)}")