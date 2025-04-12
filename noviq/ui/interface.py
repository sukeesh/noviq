import threading
from noviq.ui.terminal_ui import TerminalUI, Colors
from noviq.models.model_selector import ModelSelector
from noviq.research.research_manager import ResearchManager
import time
import shutil
import random
import sys
import re

def suggest_alternative_queries(query, user_intent):
    """
    Generate alternative search queries when original searches fail
    """
    # Remove quotes and special characters
    clean_query = re.sub(r'["\'+]', '', query).strip()
    
    # Basic transformations to create alternative queries
    suggestions = []
    
    # 1. Remove specific terms
    terms = clean_query.split()
    if len(terms) > 3:
        suggestions.append(' '.join(terms[:3]))
    
    # 2. Add "beginner" or "overview" for more general results
    suggestions.append(f"{clean_query} overview")
    suggestions.append(f"{clean_query} basics")
    
    # 3. Add "latest" or "recent" for more current information
    suggestions.append(f"latest {clean_query}")
    suggestions.append(f"recent {clean_query} trends")
    
    # 4. Create a more focused version using the user intent
    intent_terms = user_intent.split()
    main_terms = [t for t in intent_terms if len(t) > 3 and t.lower() not in ('the', 'and', 'for', 'with')]
    if main_terms:
        suggestions.append(f"{main_terms[0]} {clean_query}")
    
    # Return 2-3 unique suggestions
    unique_suggestions = list(set(suggestions))
    return random.sample(unique_suggestions, min(3, len(unique_suggestions)))

def beautiful_research():
    """
    Conduct research with beautiful terminal animations and formatting
    """
    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns
    
    # Clear terminal and show welcome message
    TerminalUI.clear_screen()
    TerminalUI.print_heading("Welcome to Noviq Research")
    TerminalUI.animate_typing("Your AI-powered research assistant that helps you dive deep into any topic.")
    
    # Model selection
    TerminalUI.print_subheading("Model Selection")
    loading_event = threading.Event()
    loading_thread = TerminalUI.start_loading_animation("Loading available models", loading_event)
    selected_model = ModelSelector.select_model()
    loading_event.set()
    loading_thread.join()
    TerminalUI.print_success(f"Using model: {selected_model}")
    
    # Initialize research manager
    loading_event = threading.Event()
    loading_thread = TerminalUI.start_loading_animation("Initializing research capabilities", loading_event)
    research_manager = ResearchManager(selected_model)
    loading_event.set()
    loading_thread.join()
    
    # Get user intent
    TerminalUI.print_subheading("Research Intent")
    TerminalUI.print_info("What would you like to research today?")
    print(f"{Colors.BRIGHT_GREEN}> {Colors.RESET}", end="")
    user_intent = input()
    TerminalUI.print_research_query(user_intent)
    
    # Get clarifying questions
    TerminalUI.print_subheading("Understanding Your Needs")
    TerminalUI.animate_typing("Let me ask a few questions to better understand your research goals...", color=Colors.BRIGHT_CYAN)
    qa_pairs = research_manager.get_clarifying_questions(user_intent)
    
    # Get research plan
    TerminalUI.print_subheading("Developing Research Strategy")
    loading_event = threading.Event()
    loading_thread = TerminalUI.start_loading_animation("Creating a comprehensive research plan", loading_event)
    research_plan = research_manager.get_research_plan(user_intent, qa_pairs)
    loading_event.set()
    loading_thread.join()
    
    # Show research plan
    TerminalUI.print_info("Research Plan:")
    for i, step in enumerate(research_plan, 1):
        TerminalUI.print_step(i, len(research_plan), step)
    
    # Execute research plan
    TerminalUI.print_subheading("Executing Research")
    TerminalUI.animate_typing("Now conducting in-depth research based on your requirements...", color=Colors.BRIGHT_MAGENTA)
    
    # Execute each step in the research plan
    scraped_webpage_texts = []
    total_steps = len(research_plan)
    
    for step_num, step in enumerate(research_plan, 1):
        # Display step header with a numbered badge
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE} STEP {step_num}/{total_steps} {Colors.RESET} {Colors.BOLD}{Colors.CYAN}{step}{Colors.RESET}")
        TerminalUI.print_divider()
        
        # Generate search queries
        loading_event = threading.Event()
        loading_thread = TerminalUI.start_loading_animation(f"Generating search queries for step {step_num}", loading_event)
        web_search_queries = research_manager.generate_web_search_queries(
            user_intent=user_intent,
            qa_pairs=qa_pairs,
            overall_research_plan=research_plan,
            research_plan_step=step
        )
        loading_event.set()
        loading_thread.join()
        
        # Display queries
        queries = web_search_queries.web_search_queries
        TerminalUI.print_info(f"Generated {len(queries)} search queries:")
        
        border_line = "─" * (terminal_width - 2)
        print(f"{Colors.BRIGHT_BLACK}┌{border_line}┐{Colors.RESET}")
        for i, query in enumerate(queries, 1):
            padding = max(0, terminal_width - len(query) - 7)
            padding_spaces = " " * padding
            print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.YELLOW}{i}.{Colors.RESET} {Colors.BOLD}\"{query}\"{Colors.RESET}{padding_spaces}{Colors.BRIGHT_BLACK}│{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}└{border_line}┘{Colors.RESET}")
        print()
        
        # Execute each query
        query_results_found = 0
        consecutive_failures = 0
        for query_num, query in enumerate(queries, 1):
            # Remove any unnecessary quotes from the query display
            display_query = query.strip('"')
            
            # Create a formatted query badge
            print(f"{Colors.BG_YELLOW}{Colors.BLACK} QUERY {query_num}/{len(queries)} {Colors.RESET} {Colors.BOLD}{display_query}{Colors.RESET}")
            
            # Search for results
            loading_event = threading.Event()
            loading_thread = TerminalUI.start_loading_animation("Searching for information", loading_event)
            
            # Add a small random delay to simulate search time
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                results = research_manager.execute_search_query(query, user_intent)
                loading_event.set()
                loading_thread.join()
                
                # Check if we have meaningful results
                if results and results != "No relevant content found." and results != "No relevant content was extracted due to website restrictions.":
                    query_results_found += 1
                    consecutive_failures = 0
                    scraped_webpage_texts.append(results)
                    
                    # Show success with source indication
                    print(f"  {Colors.BRIGHT_GREEN}✅ Found relevant information{Colors.RESET}")
                    
                    # Try to extract the URL from search results if available
                    if hasattr(research_manager, 'sources') and research_manager.sources:
                        latest_source = research_manager.sources[-1]
                        if isinstance(latest_source, tuple) and len(latest_source) >= 2:
                            title, url = latest_source
                            print(f"  {Colors.BRIGHT_BLUE}🌐 Source: {title}{Colors.RESET}")
                            print(f"  {Colors.BRIGHT_BLACK}🔗 {url}{Colors.RESET}")
                    
                    # Show a snippet of the information
                    cleaned_snippet = results.replace('\n', ' ').strip()
                    snippet = cleaned_snippet[:100] + "..." if len(cleaned_snippet) > 100 else cleaned_snippet
                    print(f"  {Colors.BRIGHT_BLACK}📄 Preview: \"{Colors.RESET}{snippet}{Colors.BRIGHT_BLACK}\"{Colors.RESET}")
                else:
                    consecutive_failures += 1
                    # Determine the specific error type
                    if not results:
                        error_message = "No results returned from search"
                    elif "website restrictions" in results:
                        error_message = "Website access restricted"
                    else:
                        error_message = "No relevant information found"
                    
                    print(f"  {Colors.BRIGHT_RED}❌ {error_message}{Colors.RESET}")
                    
                    # Show URL if available
                    if hasattr(research_manager, 'sources') and research_manager.sources:
                        latest_source = research_manager.sources[-1]
                        if isinstance(latest_source, tuple) and len(latest_source) >= 2:
                            title, url = latest_source
                            print(f"  {Colors.BRIGHT_YELLOW}📄 {title}{Colors.RESET}")
                            print(f"  {Colors.BRIGHT_YELLOW}🔗 {url}{Colors.RESET}")
                    
                    # Suggest alternative searches if multiple failures occur
                    if consecutive_failures >= 2:
                        print(f"\n  {Colors.BRIGHT_YELLOW}💡 Tip: Try different search terms or approaches.{Colors.RESET}")
                        
                        # Generate alternative queries
                        alternative_queries = suggest_alternative_queries(query, user_intent)
                        if alternative_queries:
                            print(f"  {Colors.BRIGHT_CYAN}🔄 Suggested alternative queries:{Colors.RESET}")
                            for i, alt_query in enumerate(alternative_queries, 1):
                                print(f"     {Colors.BRIGHT_WHITE}{i}.{Colors.RESET} \"{alt_query}\"")
                            print()
            except Exception as e:
                loading_event.set()
                loading_thread.join()
                consecutive_failures += 1
                print(f"  {Colors.BRIGHT_RED}❌ Error during search: {str(e)}{Colors.RESET}")
            
            # Add spacing between queries
            print() 
        
        # Show step summary
        if query_results_found > 0:
            TerminalUI.print_success(f"Step {step_num} complete: Found information from {query_results_found} search results")
        else:
            TerminalUI.print_warning(f"Step {step_num} complete: No relevant information found")
            print(f"\n{Colors.BRIGHT_YELLOW}💡 Suggestion: This topic may need a different approach or more specific search terms.{Colors.RESET}")
        
        # Add visual separator between steps
        if step_num < total_steps:
            dotted_line = "┄" * terminal_width
            print(f"\n{Colors.BRIGHT_BLACK}{dotted_line}{Colors.RESET}\n")
    
    # Save the scraped webpage texts to a file
    with open("scraped_webpage_texts.txt", "w") as f:
        for text in scraped_webpage_texts:
            f.write(text + "\n\n")
    
    # Generate report
    TerminalUI.print_subheading("Synthesizing Findings")
    
    # Animation for "thinking"
    thinking_chars = ["🧠", "💭", "🔍", "📊", "📝"]
    for _ in range(10):
        char = random.choice(thinking_chars)
        sys.stdout.write(f"\r{Colors.BRIGHT_MAGENTA}Analyzing and synthesizing information {char}{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(0.3)
    print("\n")
    
    loading_event = threading.Event()
    loading_thread = TerminalUI.start_loading_animation("Generating comprehensive research report", loading_event)
    research_report_text = research_manager.generate_report(user_intent, qa_pairs, scraped_webpage_texts)
    loading_event.set()
    loading_thread.join()
    
    # Save report
    TerminalUI.print_subheading("Saving Research Report")
    file_name = "report.html"
    
    TerminalUI.progress_bar(0, 100, prefix='Saving:', suffix='Complete', length=50)
    for i in range(101):
        time.sleep(0.01)
        TerminalUI.progress_bar(i, 100, prefix='Saving:', suffix='Complete', length=50)
    
    with open(file_name, "w") as f:
        f.write(research_report_text)
    
    # Show completion message
    TerminalUI.print_heading("Research Complete!")
    TerminalUI.print_success(f"Research report saved to {file_name}")
    TerminalUI.animate_typing("Thank you for using Noviq Research Assistant. Happy learning!", color=Colors.BRIGHT_GREEN)
    
    return file_name 