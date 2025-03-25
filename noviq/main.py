import dspy
from noviq.signatures import (
    GenerateClarifyingQuestions, 
    PrepareForResearch, 
    GenerateWebSearchQueries, 
    CleanAndClassifyWebpageText
)
import ollama
import inquirer

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

questions = clarifying_question(user_intent=user_intent)

qa_pairs = []

print("Clarifying Questions:")
for question in questions.clarifying_questions:
    answer = input(question + "  ")
    qa_pairs.append((question, answer))

plan = research_plan(user_intent=user_intent, qa_pairs=qa_pairs)

def get_search_queries(search_query) -> list[tuple[str, str]]:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import quote

    # DuckDuckGo HTML search
    url = f"https://html.duckduckgo.com/html/?q={quote(search_query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:5]:  # Get top 5 results
            title_elem = result.select_one('.result__title')
            link_elem = result.select_one('.result__url')
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href')
                if link:
                    results.append((title, link))
        
        return results
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []

def get_webpage_text(url: str) -> str:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Error fetching webpage content: {e}")
        return ""

print("Research Plan:")
for step in plan.research_plan:
    web_search_queries = generate_web_search_queries(user_intent=user_intent, qa_pairs=qa_pairs, overall_research_plan=plan.research_plan, research_plan_step=step)
    queries = web_search_queries.web_search_queries
    print(step, queries)

    for query in queries:
        results = get_search_queries(query)
        print(f"\nResults for query: {query}")
        for text, url in results:
            print(f"Title: {text}, URL: {url}\n")
            content = get_webpage_text(url)
            print("Content: ", content)

            cleaned_content = clean_webpage_text(user_intent=user_intent, webpage_text=content)
            print("Cleaned Content: ", cleaned_content)
            category = cleaned_content.category
            cleaned_text = cleaned_content.cleaned_webpage_text

            print("Category: ", category)
            print("Cleaned Text: ", cleaned_text)
            exit(0)
        exit(0)
