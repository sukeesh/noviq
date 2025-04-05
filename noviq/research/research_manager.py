import dspy
from urllib.parse import urlparse
from noviq.signatures.signatures import (
    GenerateClarifyingQuestions,
    PrepareForResearch,
    GenerateWebSearchQueries,
    CleanAndClassifyWebpageText,
    GenerateFinalResearchReport
)
from noviq.scrape.scrape import BeautifulSoupScrape
from noviq.tools.tools import get_search_queries

class ResearchManager:
    def __init__(self, model_name):
        """
        Initialize the research manager with the selected model
        Args:
            model_name (str): Name of the selected model
        """
        lm = dspy.LM(model=f'ollama_chat/{model_name}', api_base='http://localhost:11434')
        dspy.configure(lm=lm)
        
        self.clarifying_question = dspy.ChainOfThought(GenerateClarifyingQuestions)
        self.research_plan = dspy.ChainOfThought(PrepareForResearch)
        self.generate_web_search_queries = dspy.ChainOfThought(GenerateWebSearchQueries)
        self.clean_webpage_text = dspy.ChainOfThought(CleanAndClassifyWebpageText)
        self.generate_final_research_report = dspy.ChainOfThought(GenerateFinalResearchReport)
        
        self.sources = []
        
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
        
    def execute_research_plan(self, user_intent, qa_pairs):
        """
        Execute the research plan and gather information
        """
        plan = self.research_plan(user_intent=user_intent, qa_pairs=qa_pairs)
        scraped_webpage_texts = []
        
        print("\nResearch Plan:")
        for step in plan.research_plan:
            web_search_queries = self.generate_web_search_queries(
                user_intent=user_intent,
                qa_pairs=qa_pairs,
                overall_research_plan=plan.research_plan,
                research_plan_step=step
            )
            print("Generating web search queries for: " + step + "\n")
            print(web_search_queries.web_search_queries)
            
            queries = web_search_queries.web_search_queries
            
            for query in queries:
                results = get_search_queries(query)
                print(f"\nResults for query: {query}")
                
                if results:
                    text, url = results[0]
                    print(f"Title: {text}\nURL: {url}\n")
                    
                    self.sources.append((text, url))
                    
                    scrape = BeautifulSoupScrape(url)
                    content = scrape.scrape()
                    
                    cleaned_content = self.clean_webpage_text(
                        user_intent=user_intent,
                        webpage_text=content
                    )
                    
                    category = cleaned_content.category
                    cleaned_text = cleaned_content.cleaned_webpage_text
                    scraped_webpage_texts.append(cleaned_text)
                    
                    print("Category: ", category)
                    print("Cleaned Text: ", cleaned_text)
                    
        return scraped_webpage_texts
    
    def generate_report(self, user_intent, qa_pairs, scraped_webpage_texts):
        """
        Generate the final research report
        """
        research_report = self.generate_final_research_report(
            user_intent=user_intent,
            qa_pairs=qa_pairs,
            cleaned_webpage_text=scraped_webpage_texts
        )
        
        research_report_text = research_report.research_report
        
        if self.sources:
            citations_html = self._generate_citations_html()
            
            if "</body>" in research_report_text:
                research_report_text = research_report_text.replace("</body>", f"{citations_html}</body>")
            else:
                research_report_text += citations_html
                
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