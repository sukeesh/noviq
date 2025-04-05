import dspy
from typing import List, Tuple, Dict, Any
import ollama
from noviq.signatures.signatures import (
    GenerateClarifyingQuestions, 
    PrepareForResearch, 
    GenerateWebSearchQueries, 
    CleanAndClassifyWebpageText,
    GenerateFinalResearchReport
)
from noviq.scrape.scrape import BeautifulSoupScrape
from noviq.tools.tools import get_search_queries
from urllib.parse import urlparse
import logging
import time
import datetime
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("noviq_research.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger("noviq")

class ResearchSession:
    """
    Class to handle the research session and workflow
    """
    def __init__(self, model_name: str = None):
        """Initialize the research session with the given model"""
        self.model_name = model_name
        self.lm = None
        self.user_intent = None
        self.qa_pairs = []
        self.research_plan = []
        self.sources = []
        self.search_queries = {}
        self.scraped_texts = []
        self.search_results = {}
        self.research_report = None
        self.current_step = "init"  # Track the current step in the workflow
        self.step_logs = {}
        self.session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        logger.info(f"[{self.session_id}] New research session created")
        
        if model_name:
            self.configure_model(model_name)
    
    def configure_model(self, model_name: str) -> None:
        """Configure the DSPy model"""
        start = time.time()
        logger.info(f"[{self.session_id}] Configuring model: {model_name}")
        try:
            self.model_name = model_name
            
            # Configure DSPy with proper Ollama settings
            from dspy.teleprompt import BootstrapFewShot
            from dspy.predict import BootstrappedPredictor
            
            # Configure the language model with proper settings
            self.lm = dspy.LM(
                model=model_name,  # Use just the model name without ollama_chat/ prefix
                api_base='http://localhost:11434',
                model_type='chat',  # Specify it's a chat model
                api_provider='ollama'  # Specify the provider
            )
            
            # Configure DSPy with the language model
            dspy.configure(lm=self.lm)
            
            logger.info(f"[{self.session_id}] Model configured successfully in {time.time() - start:.2f}s")
        except Exception as e:
            logger.error(f"[{self.session_id}] Error configuring model: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get a list of available models from Ollama"""
        start = time.time()
        logger.info(f"[{self.session_id}] Getting available models")
        try:
            list_of_models = ollama.list()
            models = [model['model'] for model in list_of_models['models']]
            logger.info(f"[{self.session_id}] Found {len(models)} models in {time.time() - start:.2f}s")
            return models
        except Exception as e:
            logger.error(f"[{self.session_id}] Error getting models: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            return []
    
    def set_user_intent(self, intent: str) -> None:
        """Set the user's research intent"""
        logger.info(f"[{self.session_id}] Setting user intent: {intent[:50]}...")
        self.user_intent = intent
        self.current_step = "intent_set"
        logger.info(f"[{self.session_id}] User intent set, current step: {self.current_step}")
    
    def generate_clarifying_questions(self) -> List[str]:
        """Generate clarifying questions based on user intent"""
        start = time.time()
        logger.info(f"[{self.session_id}] Generating clarifying questions")
        
        if not self.user_intent:
            logger.error(f"[{self.session_id}] Cannot generate questions: user intent not set")
            raise ValueError("User intent must be set before generating questions")
        
        try:
            logger.info(f"[{self.session_id}] Creating GenerateClarifyingQuestions instance")
            clarifying_question = dspy.ChainOfThought(GenerateClarifyingQuestions)
            
            logger.info(f"[{self.session_id}] Calling LLM to generate questions")
            questions_result = clarifying_question(user_intent=self.user_intent)
            self.current_step = "questions_generated"
            
            # Store in step logs
            self.step_logs["clarifying_questions"] = questions_result.clarifying_questions
            
            logger.info(f"[{self.session_id}] Generated {len(questions_result.clarifying_questions)} questions in {time.time() - start:.2f}s")
            logger.info(f"[{self.session_id}] Questions: {', '.join([q[:30] + '...' for q in questions_result.clarifying_questions])}")
            
            return questions_result.clarifying_questions
        except Exception as e:
            logger.error(f"[{self.session_id}] Error generating questions: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
    
    def set_qa_pairs(self, qa_pairs: List[Tuple[str, str]]) -> None:
        """Set the question-answer pairs"""
        logger.info(f"[{self.session_id}] Setting {len(qa_pairs)} QA pairs")
        for q, a in qa_pairs:
            logger.info(f"[{self.session_id}] Q: {q[:30]}..., A: {a[:30]}...")
        
        self.qa_pairs = qa_pairs
        self.current_step = "qa_pairs_set"
        logger.info(f"[{self.session_id}] QA pairs set, current step: {self.current_step}")
    
    def generate_research_plan(self) -> List[str]:
        """Generate a research plan based on user intent and QA pairs"""
        start = time.time()
        logger.info(f"[{self.session_id}] Generating research plan")
        
        if not self.user_intent:
            logger.error(f"[{self.session_id}] Cannot generate plan: user intent not set")
            raise ValueError("User intent must be set before generating a research plan")
            
        if not self.qa_pairs:
            logger.error(f"[{self.session_id}] Cannot generate plan: QA pairs not set")
            raise ValueError("QA pairs must be set before generating a research plan")
        
        try:
            logger.info(f"[{self.session_id}] Creating PrepareForResearch instance")
            research_plan_module = dspy.ChainOfThought(PrepareForResearch)
            
            logger.info(f"[{self.session_id}] Calling LLM to generate research plan with {len(self.qa_pairs)} QA pairs")
            plan_result = research_plan_module(user_intent=self.user_intent, qa_pairs=self.qa_pairs)
            self.research_plan = plan_result.research_plan
            self.current_step = "plan_generated"
            
            # Store in step logs
            self.step_logs["research_plan"] = self.research_plan
            
            logger.info(f"[{self.session_id}] Generated research plan with {len(self.research_plan)} steps in {time.time() - start:.2f}s")
            for idx, step in enumerate(self.research_plan):
                logger.info(f"[{self.session_id}] Step {idx+1}: {step[:50]}...")
            
            return self.research_plan
        except Exception as e:
            logger.error(f"[{self.session_id}] Error generating research plan: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
    
    def generate_search_queries_for_step(self, step_idx: int) -> List[str]:
        """Generate search queries for a specific research plan step"""
        start = time.time()
        logger.info(f"[{self.session_id}] Generating search queries for step {step_idx+1}")
        
        if not self.research_plan or step_idx >= len(self.research_plan):
            logger.error(f"[{self.session_id}] Invalid research plan step index: {step_idx}")
            raise ValueError("Invalid research plan step index")
        
        step = self.research_plan[step_idx]
        logger.info(f"[{self.session_id}] Step {step_idx+1}: {step}")
        
        try:
            logger.info(f"[{self.session_id}] Creating GenerateWebSearchQueries instance")
            generate_web_search_queries_module = dspy.ChainOfThought(GenerateWebSearchQueries)
            
            logger.info(f"[{self.session_id}] Calling LLM to generate search queries")
            queries_result = generate_web_search_queries_module(
                user_intent=self.user_intent,
                qa_pairs=self.qa_pairs,
                overall_research_plan=self.research_plan,
                research_plan_step=step
            )
            
            queries = queries_result.web_search_queries
            self.search_queries[step_idx] = queries
            
            # Update step logs
            if "search_queries" not in self.step_logs:
                self.step_logs["search_queries"] = {}
            self.step_logs["search_queries"][step_idx] = queries
            
            logger.info(f"[{self.session_id}] Generated {len(queries)} search queries in {time.time() - start:.2f}s")
            for idx, query in enumerate(queries):
                logger.info(f"[{self.session_id}] Query {idx+1}: {query}")
            
            return queries
        except Exception as e:
            logger.error(f"[{self.session_id}] Error generating search queries: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
    
    def execute_search_for_query(self, query: str) -> List[Tuple[str, str]]:
        """Execute a search for a given query and return results"""
        start = time.time()
        logger.info(f"[{self.session_id}] Executing search for query: {query}")
        
        try:
            logger.info(f"[{self.session_id}] Calling get_search_queries function")
            results = get_search_queries(query)
            
            # Store results
            if query not in self.search_results:
                self.search_results[query] = results
                
            # Update step logs
            if "search_results" not in self.step_logs:
                self.step_logs["search_results"] = {}
            self.step_logs["search_results"][query] = results
            
            logger.info(f"[{self.session_id}] Found {len(results)} results in {time.time() - start:.2f}s")
            for idx, (title, url) in enumerate(results):
                logger.info(f"[{self.session_id}] Result {idx+1}: {title[:40]}... - {url}")
                
            return results
        except Exception as e:
            logger.error(f"[{self.session_id}] Error executing search: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
    
    def scrape_and_process_url(self, url: str) -> Dict[str, Any]:
        """Scrape and process a URL, returning the cleaned content"""
        start = time.time()
        logger.info(f"[{self.session_id}] Scraping and processing URL: {url}")
        
        if not self.user_intent:
            logger.error(f"[{self.session_id}] Cannot scrape URL: user intent not set")
            raise ValueError("User intent must be set before scraping and processing URLs")
        
        try:
            logger.info(f"[{self.session_id}] Creating BeautifulSoupScrape instance")
            scrape = BeautifulSoupScrape(url)
            
            logger.info(f"[{self.session_id}] Scraping URL")
            content = scrape.scrape()
            logger.info(f"[{self.session_id}] Scraped {len(content)} characters")
            
            logger.info(f"[{self.session_id}] Creating CleanAndClassifyWebpageText instance")
            clean_webpage_text_module = dspy.ChainOfThought(CleanAndClassifyWebpageText)
            
            logger.info(f"[{self.session_id}] Calling LLM to clean and classify text")
            cleaned_content = clean_webpage_text_module(user_intent=self.user_intent, webpage_text=content)
            
            result = {
                "url": url,
                "category": cleaned_content.category,
                "cleaned_text": cleaned_content.cleaned_webpage_text
            }
            
            logger.info(f"[{self.session_id}] Category: {cleaned_content.category}")
            logger.info(f"[{self.session_id}] Cleaned text length: {len(cleaned_content.cleaned_webpage_text)} characters")
            
            self.scraped_texts.append(cleaned_content.cleaned_webpage_text)
            
            # Update step logs
            if "scraped_content" not in self.step_logs:
                self.step_logs["scraped_content"] = []
            self.step_logs["scraped_content"].append(result)
            
            logger.info(f"[{self.session_id}] Processed URL in {time.time() - start:.2f}s")
            
            return result
        except Exception as e:
            logger.error(f"[{self.session_id}] Error scraping and processing URL {url}: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            return {"url": url, "error": str(e)}
    
    def generate_final_report(self) -> str:
        """Generate the final research report"""
        start = time.time()
        logger.info(f"[{self.session_id}] Generating final research report")
        
        if not self.user_intent:
            logger.error(f"[{self.session_id}] Cannot generate report: user intent not set")
            raise ValueError("User intent must be set before generating the report")
            
        if not self.qa_pairs:
            logger.error(f"[{self.session_id}] Cannot generate report: QA pairs not set")
            raise ValueError("QA pairs must be set before generating the report")
            
        if not self.scraped_texts:
            logger.error(f"[{self.session_id}] Cannot generate report: no scraped texts")
            raise ValueError("Scraped texts must be set before generating the report")
        
        try:
            logger.info(f"[{self.session_id}] Creating GenerateFinalResearchReport instance")
            generate_final_research_report_module = dspy.ChainOfThought(GenerateFinalResearchReport)
            
            logger.info(f"[{self.session_id}] Calling LLM to generate report with {len(self.scraped_texts)} texts")
            report_result = generate_final_research_report_module(
                user_intent=self.user_intent,
                qa_pairs=self.qa_pairs,
                cleaned_webpage_text=self.scraped_texts
            )
            
            self.research_report = report_result.research_report
            self.current_step = "report_generated"
            
            # Add sources to the HTML report
            if self.sources:
                logger.info(f"[{self.session_id}] Adding {len(self.sources)} citations to report")
                self.research_report = self.add_citations_to_report(self.research_report, self.sources)
            
            logger.info(f"[{self.session_id}] Generated report of {len(self.research_report)} characters in {time.time() - start:.2f}s")
            
            return self.research_report
        except Exception as e:
            logger.error(f"[{self.session_id}] Error generating report: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
    
    def add_sources(self, title: str, url: str) -> None:
        """Add a source to the sources list"""
        logger.info(f"[{self.session_id}] Adding source: {title[:40]}... - {url}")
        self.sources.append((title, url))
    
    def save_report_to_file(self) -> str:
        """Save the research report to a file"""
        import os
        start = time.time()
        logger.info(f"[{self.session_id}] Saving research report to file")
        
        if not self.research_report:
            logger.error(f"[{self.session_id}] Cannot save report: no report generated")
            raise ValueError("Research report must be generated before saving to file")
        
        try:
            # Make sure the reports directory exists
            if not os.path.exists("reports"):
                os.makedirs("reports")
            
            # Generate a filename based on the current time
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/research_report_{timestamp}.html"
            
            # Write the report to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.research_report)
            
            logger.info(f"[{self.session_id}] Saved report to {filename} in {time.time() - start:.2f}s")
            
            return filename
        except Exception as e:
            logger.error(f"[{self.session_id}] Error saving report to file: {str(e)}")
            logger.error(f"[{self.session_id}] {traceback.format_exc()}")
            raise
            
    def add_citations_to_report(self, report_html: str, sources: List[Tuple[str, str]]) -> str:
        """Add citations section to the HTML report"""
        if not sources:
            return report_html
            
        citations_html = """
        <section id="references" style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
            <h2 style="color: #333; font-size: 1.5em; margin-bottom: 15px;">References</h2>
            <ol style="list-style-type: none; padding-left: 0;">
        """
        
        for title, url in sources:
            # Extract domain for favicon
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            favicon_url = f"{domain}/favicon.ico"
            
            # Alternative favicon URLs if the standard one doesn't work
            google_favicon = f"https://www.google.com/s2/favicons?domain={domain}"
            
            # Extract domain name for display
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
        
        # Check if the HTML has a body closing tag to insert before
        if "</body>" in report_html:
            report_html = report_html.replace("</body>", f"{citations_html}</body>")
        else:
            # If no body tag, just append to the end
            report_html += citations_html
        
        return report_html 