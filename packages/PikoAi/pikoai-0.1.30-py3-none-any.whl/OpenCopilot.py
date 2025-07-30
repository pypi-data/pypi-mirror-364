import os
import sys
import json
import re
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app

from Tools.file_task import file_reader
from Agents.Executor.executor import executor

# File size and token limits configuration
MAX_FILE_SIZE_MB = 5  # Maximum file size in MB
MAX_TOKENS = 50000    # Maximum tokens (roughly 4 characters per token)
MAX_LINES = 1000      # Maximum lines for large files

# Custom key bindings for handling Enter key
kb = KeyBindings()

@kb.add('enter')
def handle_enter(event):
    """Handle Enter key press based on completion state"""
    buff = event.current_buffer
    app = get_app()
    
    # If completion menu is open, select the current completion
    if app.current_buffer.complete_state:
        # Get the current completion
        current_completion = app.current_buffer.complete_state.current_completion
        if current_completion:
            # Get the text before cursor
            text_before_cursor = buff.text[:buff.cursor_position]
            # Find the last @ symbol
            last_at_pos = text_before_cursor.rindex('@')
            # Delete text from @ to cursor position
            buff.delete_before_cursor(count=buff.cursor_position - last_at_pos - 1)
            # Insert the completion
            buff.insert_text(current_completion.text)
        # Close the completion menu
        buff.complete_state = None
    else:
        # If no completion menu, submit the command
        buff.validate_and_handle()

class FilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        path_match = self._find_at_path(text_before_cursor)
        if not path_match:
            return
        current_path = path_match.group(1)
        # Only consider files/dirs in current working directory
        # Support completion for subdirectories and deeper paths
        # Split current_path into directory and base name
        dir_path, base_name = os.path.split(current_path)
        if not dir_path:
            dir_path = os.getcwd()
        else:
            # Expand user home and make absolute
            dir_path = os.path.expanduser(dir_path)
            if not os.path.isabs(dir_path):
                dir_path = os.path.abspath(dir_path)
        try:
            items = os.listdir(dir_path)
            # Filter out hidden files and folders (those starting with .)
            visible_items = [item for item in items if not item.startswith('.')]
            matching_items = [item for item in visible_items if item.lower().startswith(base_name.lower())]
            matching_items.sort(key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
            for item in matching_items:
                yield self._create_completion(text_before_cursor,dir_path, item)
        except (OSError, PermissionError):
            pass

    def _find_at_path(self, text):
        """Find the last @ symbol after whitespace and the path after it"""
        return re.search(r'@([^@\s]*)$', text)

    def _create_completion(self, text_before_cursor, dir_path, item):
        """Create a Completion object for a given item in the current directory."""
        full_path = os.path.join(dir_path, item)
        # Get relative path from current working directory
        rel_path = os.path.relpath(full_path)
        
        # Only the completed path after '@' should be inserted
        if os.path.isdir(full_path):
            completion_text = f"{rel_path}/"
            display_text = f"{item}/ (directory)"
        else:
            _, ext = os.path.splitext(item)
            completion_text = f"{rel_path}"
            if ext:
                display_text = f"{item} ({ext[1:]} file)"
            else:
                display_text = f"{item}"
                
        # if '/' in text_before_cursor[text_before_cursor.rindex('@'):]:
        #     start_position = -(len(text_before_cursor) - text_before_cursor.rindex('/') - 1)
        # else:
        start_position = -(len(text_before_cursor) - text_before_cursor.rindex('@') - 1)
            
        return Completion(
            text=completion_text,
            start_position=start_position,
            display=display_text
        )

class OpenCopilot:
    def __init__(self):
        self.e1 = None  # Initialize as None, will be set in run()
        # Initialize session with custom key bindings
        self.session = PromptSession(
            completer=FilePathCompleter(),
            key_bindings=kb,  # Add custom key bindings
            complete_while_typing=True  # Enable completion while typing
        )

    def extract_files_and_process_prompt(self, user_input):
        """Extract file paths from @ commands and process the prompt."""
        # Find all @file patterns
        file_patterns = re.findall(r'@(\S+)', user_input)
        file_contents = []
        processed_prompt = user_input
        
        for file_path in file_patterns:
            # Expand user home directory if needed
            expanded_path = os.path.expanduser(file_path)
            
            # Convert to absolute path if it's relative
            if not os.path.isabs(expanded_path):
                expanded_path = os.path.abspath(expanded_path)
            
            if os.path.exists(expanded_path):
                if os.path.isfile(expanded_path):
                    # Check file size before reading
                    file_size_mb = os.path.getsize(expanded_path) / (1024 * 1024)
                    
                    if file_size_mb > MAX_FILE_SIZE_MB:
                        # File is too large, provide summary instead
                        file_contents.append(f"=== Large file detected: {expanded_path} ===\n")
                        file_contents.append(f"File size: {file_size_mb:.2f} MB (exceeds {MAX_FILE_SIZE_MB} MB limit)\n")
                        file_contents.append(f"Please use specific line ranges or ask for file analysis instead.\n")
                        file_contents.append(f"=== End of file info: {expanded_path} ===\n")
                        processed_prompt = processed_prompt.replace(f"@{file_path}", "")
                        
                        print_formatted_text(FormattedText([
                            ('class:warning', f"⚠ Large file detected: {expanded_path} ({file_size_mb:.2f} MB)")
                        ]))
                        print_formatted_text(FormattedText([
                            ('class:info', f"💡 Tip: Use '@file:start-end' for specific line ranges or ask for file analysis")
                        ]))
                        continue
                    
                    # Call file_reader to get file content
                    file_read_result = file_reader(file_path=expanded_path)
                    
                    if file_read_result["success"]:
                        content = file_read_result["output"]
                        
                        # Check content length (rough token estimation)
                        content_length = len(content)
                        estimated_tokens = content_length // 4  # Rough estimation
                        line_count = content.count('\n') + 1
                        
                        if estimated_tokens > MAX_TOKENS or line_count > MAX_LINES:
                            # Content is too large, provide truncated version with warning
                            truncated_content = self._truncate_content(content, line_count)
                            file_contents.append(f"=== Content of file: {expanded_path} (TRUNCATED) ===\n")
                            file_contents.append(f"File size: {file_size_mb:.2f} MB | Lines: {line_count} | Estimated tokens: {estimated_tokens}\n")
                            file_contents.append(f"Showing first {MAX_LINES} lines due to size limits.\n")
                            file_contents.append(f"Use '@file:start-end' for specific line ranges.\n\n")
                            file_contents.append(truncated_content)
                            file_contents.append(f"\n=== End of file: {expanded_path} ===\n")
                            
                            print_formatted_text(FormattedText([
                                ('class:warning', f"⚠ Large file truncated: {expanded_path}")
                            ]))
                            print_formatted_text(FormattedText([
                                ('class:info', f"📊 File stats: {line_count} lines, ~{estimated_tokens} tokens")
                            ]))
                        else:
                            # File is within limits, add full content
                            file_contents.append(f"=== Content of file: {expanded_path} ===\n{content}\n=== End of file: {expanded_path} ===\n")
                            print_formatted_text(FormattedText([
                                ('class:success', f"✓ Loaded file: {expanded_path}")
                            ]))
                        
                        # Remove the @file pattern from the processed prompt
                        processed_prompt = processed_prompt.replace(f"@{file_path}", "")
                        
                    else:
                        error_message = file_read_result["output"]
                        print_formatted_text(FormattedText([
                            ('class:error', f"✗ Error reading file {expanded_path}: {error_message}")
                        ]))
                else:
                    # For directories, just append the path to the processed prompt
                    processed_prompt = processed_prompt.replace(f"@{file_path}", expanded_path)
                    print_formatted_text(FormattedText([
                        ('class:success', f"✓ Added directory path: {expanded_path}")
                    ]))
            else:
                print_formatted_text(FormattedText([
                    ('class:warning', f"⚠ Path not found: {expanded_path}")
                ]))
        
        # Combine file contents with the processed prompt. will have the files first content and then the user prompt
        if file_contents:
            final_prompt = "\n".join(file_contents) + "\n" + processed_prompt.strip()
            print_formatted_text(FormattedText([
                ('class:info', f"📁 Loaded {len(file_contents)} file(s) into context")
            ]))
        else:
            final_prompt = processed_prompt.strip()
        
        return final_prompt

    def _truncate_content(self, content, total_lines):
        """Truncate content to show first MAX_LINES lines with ellipsis."""
        lines = content.split('\n')
        if len(lines) <= MAX_LINES:
            return content
        
        # Show first MAX_LINES lines
        truncated_lines = lines[:MAX_LINES]
        truncated_content = '\n'.join(truncated_lines)
        truncated_content += f"\n\n... (truncated, showing {MAX_LINES} of {total_lines} lines) ..."
        
        return truncated_content

    def display_help(self):
        """Display help information about available commands."""
        help_text = f"""
🚀 TaskAutomator OpenCopilot Help

Available Commands:
  @<file_path>    - Include file content in your prompt
                   Example: @config.json analyze this configuration
                   Supports: relative paths, absolute paths, ~ for home directory
                   Multiple files: @file1.py @file2.txt compare these files
  
  quit           - Exit the application
  help           - Show this help message

File Size Limits:
  - Maximum file size: {MAX_FILE_SIZE_MB} MB
  - Maximum tokens: {MAX_TOKENS:,} (estimated)
  - Maximum lines: {MAX_LINES:,}
  - Large files will be truncated with a warning
  - Use specific line ranges for large files

File Path Completion:
  - Type @ followed by a file path
  - Use arrow keys to navigate suggestions
  - Press Tab or Enter to autocomplete
  - Supports directories (shows with /) and files
  - Case-insensitive matching

Examples:
  @src/main.py explain this code
  @~/documents/data.csv @analysis.py analyze this data using this script
  @config.json @logs/error.log debug the issue in these files

Large File Handling:
  - Files exceeding {MAX_FILE_SIZE_MB} MB will show file info instead of content
  - Files with >{MAX_LINES:,} lines will be truncated
  - Use '@file:start-end' for specific line ranges (coming soon)
  - Ask for file analysis instead of full content for large files
"""
        print_formatted_text(FormattedText([('class:info', help_text)]))

    def run(self):
        """Main conversation loop with enhanced @ command support."""
        print_formatted_text(FormattedText([
            ('class:title', '🚀PikoAi: Your AI Terminal Companion'),
            ('class:subtitle', '\nUse @<file_path> to include files in your context.\n')
        ]))
        
        try:
            # Get initial prompt
            user_input = self.session.prompt(HTML("<b>Piko></b>"))
            
            # Handle special commands
            if user_input.lower() == 'help':
                self.display_help()
                user_input = self.session.prompt(HTML("<b>Piko></b>"))
            elif user_input.lower() == 'quit':
                print("Goodbye!")
                return
            
            # Process the initial prompt
            final_prompt = self.extract_files_and_process_prompt(user_input)
            
            # Initialize executor with the processed prompt
            self.e1 = executor(final_prompt)
            self.e1.executor_prompt_init()
            self.e1.run()

            # Continue conversation loop
            while True:
                try:
                    user_input = self.session.prompt(HTML("<b>\nPiko></b>"))
                    
                    # Handle special commands
                    if user_input.lower() == 'quit':
                        print("Goodbye!")
                        break
                    elif user_input.lower() == 'help':
                        self.display_help()
                        continue
                    
                    # Process the prompt and extract files
                    final_prompt = self.extract_files_and_process_prompt(user_input)
                    
                    # Add to conversation
                    self.e1.message.append({"role": "user", "content": final_prompt})
                    self.e1.run()
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print_formatted_text(FormattedText([
                        ('class:error', f"An error occurred: {e}")
                    ]))
                    continue
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print_formatted_text(FormattedText([
                ('class:error', f"Failed to start OpenCopilot: {e.__class__.__name__}: {e}")
            ]))
            import traceback
            print_formatted_text(FormattedText([
                ('class:error', f"Error occurred at: {traceback.format_exc()}")
            ]))

    def run_task(self, user_prompt, max_iter=10):
        """One-shot task execution with @ command support."""
        # Process @ commands in the prompt
        final_prompt = self.extract_files_and_process_prompt(user_prompt)
        
        e1 = executor(final_prompt, max_iter=max_iter)
        e1.executor_prompt_init()
        e1.run()

    @staticmethod
    def list_available_tools():
        """List all available tools."""
        try:
            import pkg_resources
            tool_dir_path = pkg_resources.resource_filename('Tools', 'tool_dir.json')
            with open(tool_dir_path, 'r') as f:
                tools = json.load(f)
            return tools
        except FileNotFoundError:
            print("Tools directory not found.")
            return {}
        except json.JSONDecodeError:
            print("Error reading tools configuration.")
            return {}

# To run the copilot
if __name__ == "__main__":
    copilot = OpenCopilot()
    copilot.run()



    
