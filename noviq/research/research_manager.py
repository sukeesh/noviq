import dspy
from urllib.parse import urlparse, urldefrag
from noviq.signatures.signatures import (
    GenerateClarifyingQuestions,
    PrepareForResearch,
    GenerateWebSearchQueries,
    CleanAndClassifyWebpageText,
    GenerateWebpageSummary,
    GenerateFinalResearchReport
)
from noviq.scrape.scrape import BeautifulSoupScrape
from noviq.tools.tools import get_search_queries

MAX_TOKENS = 32000  # Increased to allow for more detailed output
TEMPERATURE = 0.05  # Reduced to make output more factual and deterministic

class ResearchManager:
    def __init__(self, model_name):
        """
        Initialize the research manager with the selected model
        Args:
            model_name (str): Name of the selected model
        """
        lm = dspy.LM(model=f'ollama_chat/{model_name}', api_base='http://localhost:11434', max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
        dspy.configure(lm=lm)
        
        self.clarifying_question = dspy.ChainOfThought(GenerateClarifyingQuestions)
        self.research_plan = dspy.ChainOfThought(PrepareForResearch)
        self.generate_web_search_queries = dspy.ChainOfThought(GenerateWebSearchQueries)
        self.clean_webpage_text = dspy.ChainOfThought(CleanAndClassifyWebpageText)
        self.generate_webpage_summary = dspy.ChainOfThought(GenerateWebpageSummary)
        self.generate_final_research_report = dspy.ChainOfThought(GenerateFinalResearchReport)
        
        self.sources = []
        self.raw_webpage_contents = []  # Store the raw webpage contents
        self.webpage_summaries = []     # Store the webpage summaries
        self.processed_urls = set()     # Track URLs that have already been processed
        self.duplicate_count = 0        # Track number of duplicates for analytics
        self.search_stats = {           # Track search statistics
            'total_queries': 0,
            'successful_queries': 0,
            'duplicate_urls': 0,
            'empty_results': 0
        }
        
    def normalize_url(self, url):
        """
        Normalize a URL to help prevent duplicate processing of the same content
        Removes fragments and normalizes the domain
        """
        # Remove URL fragments
        url_without_fragment = urldefrag(url)[0]
        
        # Parse the URL
        parsed = urlparse(url_without_fragment)
        
        # Normalize the domain (remove www. if present)
        netloc = parsed.netloc
        if netloc.startswith('www.'):
            netloc = netloc[4:]
            
        # Reconstruct the URL with normalized domain
        normalized_url = f"{parsed.scheme}://{netloc}{parsed.path}"
        
        # Add query parameters if they exist
        if parsed.query:
            normalized_url += f"?{parsed.query}"
            
        return normalized_url
        
    def get_clarifying_questions(self, user_intent):
        """
        Get clarifying questions based on user intent
        """
        questions = self.clarifying_question(user_intent=user_intent)
        qa_pairs = []
        
        print("\nClarifying Questions:")
        for question in questions.clarifying_questions:
            answer = input(question + "  ")
            qa_pairs.append((question, answer))
            
        return qa_pairs
        
    def get_research_plan(self, user_intent, qa_pairs):
        """
        Get the research plan from the LLM
        """
        plan = self.research_plan(user_intent=user_intent, qa_pairs=qa_pairs)
        return plan.research_plan
        
    def execute_search_query(self, query, user_intent):
        """
        Execute a search query and return the extracted text from the URL
        """
        self.search_stats['total_queries'] += 1
        results = get_search_queries(query)
        
        if not results:
            self.search_stats['empty_results'] += 1
            print(f"No results found for query: {query}")
            return None
            
        # Try the top 3 results until we find one that hasn't been processed yet
        for title, url in results[:3]:
            # Normalize the URL to avoid duplicates with slightly different formats
            normalized_url = self.normalize_url(url)
            
            # Skip if we've already processed this URL
            if normalized_url in self.processed_urls:
                print(f"Skipping duplicate URL: {url}")
                self.search_stats['duplicate_urls'] += 1
                self.duplicate_count += 1
                continue
                
            print(f"Title: {title}\nURL: {url}\n")
            
            # Add to processed URLs
            self.processed_urls.add(normalized_url)
            self.sources.append((title, url))
            
            try:
                scrape = BeautifulSoupScrape(url)
                content = scrape.scrape()
                
                # Skip if content is too short or contains error messages
                if len(content) < 200 or "Skipped due to" in content:
                    print(f"Skipping URL due to insufficient content: {url}")
                    continue
                
                # Store the raw content
                self.raw_webpage_contents.append((title, url, content))
                
                # Generate a 7-sentence summary of the webpage
                summary = self.generate_webpage_summary(
                    user_intent=user_intent,
                    webpage_text=content,
                    webpage_title=title,
                    webpage_url=url
                )
                
                self.webpage_summaries.append(summary.summary)
                self.search_stats['successful_queries'] += 1
                
                print("\nWebpage Summary (7 sentences):", summary.summary)
                
                return summary.summary
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
            
        # If all top results are duplicates or failed, return None
        print("All search results have already been processed or failed.")
        return None
        
    def execute_research_plan(self, research_plan, user_intent, qa_pairs):
        """
        Execute the research plan and gather information
        """
        scraped_webpage_texts = []
        min_sources_needed = 5  # Minimum number of sources we want to collect
        
        print("\nResearch Plan:")
        for step in research_plan:
            web_search_queries = self.generate_web_search_queries(
                user_intent=user_intent,
                qa_pairs=qa_pairs,
                overall_research_plan=research_plan,
                research_plan_step=step
            )
            print("Generating web search queries for: " + step + "\n")
            print(web_search_queries.web_search_queries)
            
            queries = web_search_queries.web_search_queries
            
            # Limit to first 2 queries per step to avoid too many API calls
            for query in queries[:2]:
                # Skip more queries once we have enough sources
                if len(self.webpage_summaries) >= min_sources_needed:
                    print(f"\nCollected {len(self.webpage_summaries)} sources, which meets our minimum requirement.")
                    break
                
                print(f"\nResults for query: {query}")
                cleaned_text = self.execute_search_query(query, user_intent)
                if cleaned_text:
                    scraped_webpage_texts.append(cleaned_text)
            
            # Break early if we have enough sources
            if len(self.webpage_summaries) >= min_sources_needed:
                break
        
        # Print statistics
        print(f"\n--- Search Statistics ---")
        print(f"Total queries executed: {self.search_stats['total_queries']}")
        print(f"Successful queries: {self.search_stats['successful_queries']}")
        print(f"Duplicate URLs skipped: {self.search_stats['duplicate_urls']}")
        print(f"Queries with no results: {self.search_stats['empty_results']}")
        print(f"Total sources collected: {len(self.webpage_summaries)}")
        print(f"-------------------------")
        
        return scraped_webpage_texts
    
    def generate_report(self, user_intent, qa_pairs, scraped_webpage_texts):
        """
        Generate the final research report
        """
        print("\nGenerating detailed research report from all webpage summaries and content...")
        print(f"Using {len(self.webpage_summaries)} webpage summaries and {len(scraped_webpage_texts)} scraped contents.")
        
        # Verify we have enough content to generate a meaningful report
        if len(self.webpage_summaries) < 3:
            print("\n⚠️  WARNING: Limited webpage data available (only {len(self.webpage_summaries)} sources).")
            print("The report may lack comprehensive information or factual accuracy.")
            
            # Try to get more sources if we don't have enough
            if len(self.research_plan) > 0 and len(self.webpage_summaries) < 3:
                print("\nAttempting to collect additional sources...")
                backup_queries = [
                    f"{user_intent} facts",
                    f"{user_intent} overview",
                    f"{user_intent} details"
                ]
                
                for query in backup_queries:
                    if len(self.webpage_summaries) >= 3:
                        break
                    print(f"\nTrying backup query: {query}")
                    cleaned_text = self.execute_search_query(query, user_intent)
                    if cleaned_text:
                        scraped_webpage_texts.append(cleaned_text)
        
        # Create a summary of the research to help guide the report generation
        research_topics = f"Research about: {user_intent}\n\n"
        for i, summary in enumerate(self.webpage_summaries):
            research_topics += f"Source {i+1}: {summary}\n\n"
        
        print(f"Passing {len(research_topics)} characters of summarized content to generate report...")
        
        # Generate the research report
        research_report = self.generate_final_research_report(
            user_intent=user_intent,
            qa_pairs=qa_pairs,
            cleaned_webpage_text=scraped_webpage_texts,
            webpage_summaries=self.webpage_summaries
        )
        
        research_report_text = research_report.research_report
        
        # Validate that the output is proper HTML
        if not research_report_text.strip().startswith("<!DOCTYPE html>") and "<html" not in research_report_text:
            print("⚠️  Warning: Generated report is not in proper HTML format. Attempting to convert...")
            # Wrap the content in basic HTML tags if it's not already in HTML format
            research_report_text = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Research Report: {user_intent}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; max-width: 1200px; margin: 0 auto; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #3498db; margin-top: 30px; }}
                    h3 {{ color: #2980b9; }}
                    .container {{ padding: 20px; }}
                    .toc {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
                    .section {{ margin-bottom: 40px; }}
                    .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Research Report: {user_intent}</h1>
                    <div class="content">
                        {research_report_text}
                    </div>
                </div>
            </body>
            </html>
            """
        
        # Add table of contents if not present
        if "<div class=\"toc\"" not in research_report_text and "</body>" in research_report_text:
            print("Adding table of contents to the report...")
            toc_html = """
            <div class="toc">
                <h2>Table of Contents</h2>
                <ul>
                    <li><a href="#introduction">Introduction</a></li>
                    <li><a href="#overview">Overview</a></li>
                    <li><a href="#details">Key Details</a></li>
                    <li><a href="#analysis">Analysis</a></li>
                    <li><a href="#conclusion">Conclusion</a></li>
                </ul>
            </div>
            """
            # Insert after the opening body tag or after the first h1
            if "<body>" in research_report_text:
                research_report_text = research_report_text.replace("<body>", f"<body>\n{toc_html}")
            elif "</h1>" in research_report_text:
                research_report_text = research_report_text.replace("</h1>", f"</h1>\n{toc_html}")
        
        # Check if the report seems too short
        if len(research_report_text.split()) < 500:  # Roughly checking if less than 500 words
            print("⚠️  Warning: Generated report appears to be too short. It may not be comprehensive enough.")
        
        if self.sources:
            citations_html = self._generate_citations_html()
            
            if "</body>" in research_report_text:
                research_report_text = research_report_text.replace("</body>", f"{citations_html}</body>")
            else:
                research_report_text += citations_html
        
        print("\n✅ Research report generation complete!")
        return research_report_text
    
    def _generate_citations_html(self):
        """
        Generate HTML for citations section
        """
        citations_html = """
        <section id="references" style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
            <h2 style="color: #333; font-size: 1.5em; margin-bottom: 15px;">References</h2>
            <ol style="list-style-type: none; padding-left: 0;">
        """
        
        for title, url in self.sources:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            favicon_url = f"{domain}/favicon.ico"
            google_favicon = f"https://www.google.com/s2/favicons?domain={domain}"
            domain_name = parsed_url.netloc.replace("www.", "")
            
            citations_html += f'''
            <li style="margin-bottom: 15px; display: flex; align-items: center; padding: 8px; border-radius: 4px; background-color: #f8f9fa;">
                <img src="{google_favicon}" alt="favicon" style="width: 16px; height: 16px; margin-right: 10px;" onerror="this.onerror=null; this.src='{favicon_url}';">
                <div>
                    <a href="{url}" target="_blank" style="color: #1a0dab; text-decoration: none; font-weight: 500;">{title}</a>
                    <div style="color: #006621; font-size: 0.8em; margin-top: 3px;">{domain_name}</div>
                </div>
            </li>
            '''
        
        citations_html += """
            </ol>
        </section>
        """
        
        return citations_html 