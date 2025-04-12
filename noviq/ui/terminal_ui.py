import sys
import time
import os
from threading import Thread
import shutil

terminal_width = shutil.get_terminal_size().columns

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

class TerminalUI:
    @staticmethod
    def animate_typing(text, delay=0.01, color=Colors.CYAN):
        """Type-writer animation effect for text"""
        for char in text:
            sys.stdout.write(f"{color}{char}{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        print()
    
    @staticmethod
    def print_heading(text):
        """Print a stylized heading"""
        print("\n" + "=" * terminal_width)
        padding = (terminal_width - len(text) - 2) // 2
        print(f"{Colors.BOLD}{Colors.BLUE}" + " " * padding + f"✦ {text} ✦" + f"{Colors.RESET}")
        print("=" * terminal_width + "\n")
    
    @staticmethod
    def print_subheading(text):
        """Print a stylized subheading"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}▶ {text} ◀{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}" + "-" * terminal_width + f"{Colors.RESET}")
    
    @staticmethod
    def print_info(text):
        """Print info text with a prefix"""
        print(f"{Colors.BRIGHT_CYAN}ℹ️  {text}{Colors.RESET}")
    
    @staticmethod
    def print_success(text):
        """Print success text with a prefix"""
        print(f"{Colors.BRIGHT_GREEN}✅ {text}{Colors.RESET}")
    
    @staticmethod
    def print_warning(text):
        """Print warning text with a prefix"""
        print(f"{Colors.BRIGHT_YELLOW}⚠️  {text}{Colors.RESET}")
    
    @staticmethod
    def print_error(text):
        """Print error text with a prefix"""
        print(f"{Colors.BRIGHT_RED}❌ {text}{Colors.RESET}")
    
    @staticmethod
    def print_step(step_num, total_steps, text):
        """Print a step in a process"""
        print(f"{Colors.BOLD}[{step_num}/{total_steps}]{Colors.RESET} {Colors.YELLOW}🔍 {text}{Colors.RESET}")
    
    @staticmethod
    def loading_animation(message, stop_event):
        """Display a loading animation until stop_event is set"""
        animation = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Braille spinner characters
        idx = 0
        while not stop_event.is_set():
            sys.stdout.write(f"\r{Colors.CYAN}{message} {animation[idx % len(animation)]}{Colors.RESET}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        sys.stdout.write(f"\r{Colors.GREEN}{message} ✓{Colors.RESET}" + " " * 10 + "\n")
        sys.stdout.flush()
    
    @staticmethod
    def start_loading_animation(message, stop_event):
        """Start a loading animation in a separate thread"""
        thread = Thread(target=TerminalUI.loading_animation, args=(message, stop_event))
        thread.daemon = True
        thread.start()
        return thread
    
    @staticmethod
    def print_research_query(query):
        """Print a research query in a box"""
        border_length = min(len(query) + 8, terminal_width - 10)
        print(f"\n{Colors.BRIGHT_BLUE}┌" + "─" * border_length + f"┐{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}│{Colors.RESET} {Colors.BOLD}🔎 {query}{Colors.RESET}" + " " * (border_length - len(query) - 4) + f"{Colors.BRIGHT_BLUE}│{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}└" + "─" * border_length + f"┘{Colors.RESET}\n")
    
    @staticmethod
    def print_result(title, url, success=True):
        """Print a search result"""
        if success:
            title_color = Colors.GREEN
            url_color = Colors.BRIGHT_BLUE
        else:
            title_color = Colors.BRIGHT_BLACK
            url_color = Colors.BRIGHT_BLACK
            
        print(f"\n{title_color}📄 {title}{Colors.RESET}")
        print(f"{url_color}🔗 {url}{Colors.RESET}")
    
    @staticmethod
    def print_query(query_num, total, query):
        """Print a formatted search query"""
        print(f"{Colors.YELLOW}Query {query_num}/{total}: \"{Colors.BOLD}{query}{Colors.RESET}{Colors.YELLOW}\"{Colors.RESET}")
    
    @staticmethod
    def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█', empty='░'):
        """Print a progress bar"""
        percent = f"{100 * (iteration / float(total)):.1f}"
        filled_length = int(length * iteration // total)
        bar = Colors.GREEN + fill * filled_length + Colors.BRIGHT_BLACK + empty * (length - filled_length) + Colors.RESET
        sys.stdout.write(f'\r{prefix} |{bar}| {Colors.CYAN}{percent}%{Colors.RESET} {suffix}')
        sys.stdout.flush()
        if iteration == total:
            print()
    
    @staticmethod
    def print_divider():
        """Print a divider line"""
        print(f"\n{Colors.BRIGHT_BLACK}" + "─" * terminal_width + f"{Colors.RESET}\n")
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear') 