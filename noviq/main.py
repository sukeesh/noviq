import dspy
from noviq.signatures.signatures import (
    GenerateClarifyingQuestions, 
    PrepareForResearch, 
    GenerateWebSearchQueries, 
    CleanAndClassifyWebpageText,
    GenerateFinalResearchReport
)
import ollama
import inquirer
from noviq.scrape.scrape import Scrape, BeautifulSoupScrape, HTTPScrape
from noviq.tools.tools import get_search_queries
from urllib.parse import urlparse


def select_model():
    list_of_models = ollama.list()
    choices = [model['model'] for model in list_of_models['models']]
    
    questions = [
        inquirer.List('model',
                     message="Select the model you want to use",
                     choices=choices,
                     carousel=True)
    ]
    
    answers = inquirer.prompt(questions)
    return answers['model']

# Get user selected model
selected_model = select_model()
print(f"Selected model: {selected_model}")

# Configure DSPy with selected model
lm = dspy.LM(f'ollama_chat/{selected_model}', api_base='http://localhost:11434')
dspy.configure(lm=lm)

user_intent = input("Enter your research intent: ")

clarifying_question = dspy.ChainOfThought(GenerateClarifyingQuestions)
research_plan = dspy.ChainOfThought(PrepareForResearch)
generate_web_search_queries = dspy.ChainOfThought(GenerateWebSearchQueries)
clean_webpage_text = dspy.ChainOfThought(CleanAndClassifyWebpageText)
generate_final_research_report = dspy.ChainOfThought(GenerateFinalResearchReport)

questions = clarifying_question(user_intent=user_intent)

qa_pairs = []

print("Clarifying Questions:")
for question in questions.clarifying_questions:
    answer = input(question + "  ")
    qa_pairs.append((question, answer))

plan = research_plan(user_intent=user_intent, qa_pairs=qa_pairs)
sources = []

print("Research Plan:")
for step in plan.research_plan:
    web_search_queries = generate_web_search_queries(user_intent=user_intent, qa_pairs=qa_pairs, overall_research_plan=plan.research_plan, research_plan_step=step)
    print("Generating web search queries for: " + step + "\n")
    print(web_search_queries.web_search_queries)

    queries = web_search_queries.web_search_queries[:1]  # Take only first query

    scraped_webpage_texts = []

    for query in queries:
        results = get_search_queries(query)
        print(f"\nResults for query: {query}")
        # Take only first result
        if results:
            text, url = results[0]
            print(f"Title: {text}\nURL: {url}\n")
            
            # Append both title and URL as a tuple
            sources.append((text, url))
            
            scrape = BeautifulSoupScrape(url)
            content = scrape.scrape()

            cleaned_content = clean_webpage_text(user_intent=user_intent, webpage_text=content)

            category = cleaned_content.category
            cleaned_text = cleaned_content.cleaned_webpage_text
            scraped_webpage_texts.append(cleaned_text)

            print("Category: ", category)
            print("Cleaned Text: ", cleaned_text)

research_report = generate_final_research_report(
    user_intent=user_intent, 
    qa_pairs=qa_pairs, 
    cleaned_webpage_text=scraped_webpage_texts
)

research_report_text = research_report.research_report

# Programmatically add citations section to the HTML
if sources:
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
    if "</body>" in research_report_text:
        research_report_text = research_report_text.replace("</body>", f"{citations_html}</body>")
    else:
        # If no body tag, just append to the end
        research_report_text += citations_html

file_name = "report.html"
with open(file_name, "w") as f:
    f.write(research_report_text)

print(f"Research report saved to {file_name}")
