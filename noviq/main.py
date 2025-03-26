import dspy
from noviq.signatures import (
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

for step in plan.research_plan:
    print(step + "\n")

# exit()

print("Research Plan:")
for step in plan.research_plan[:2]:  # Limit to first 2 steps
    print(f"\nExecuting step: {step}")
    web_search_queries = generate_web_search_queries(user_intent=user_intent, qa_pairs=qa_pairs, overall_research_plan=plan.research_plan, research_plan_step=step)
    queries = web_search_queries.web_search_queries[:1]  # Take only first query

    scraped_webpage_texts = []

    for query in queries:
        results = get_search_queries(query)
        print(f"\nResults for query: {query}")
        # Take only first result
        if results:
            text, url = results[0]
            print(f"Title: {text}\nURL: {url}\n")
            
            scrape = BeautifulSoupScrape(url)
            content = scrape.scrape()

            cleaned_content = clean_webpage_text(user_intent=user_intent, webpage_text=content)

            category = cleaned_content.category
            cleaned_text = cleaned_content.cleaned_webpage_text
            scraped_webpage_texts.append(cleaned_text)

            print("Category: ", category)
            print("Cleaned Text: ", cleaned_text)

research_report = generate_final_research_report(user_intent=user_intent, qa_pairs=qa_pairs, cleaned_webpage_text=scraped_webpage_texts)

research_report_text = research_report.research_report

file_name = "report.md"
with open(file_name, "w") as f:
    import markdown
    f.write(markdown.markdown(research_report_text)) 

print(f"Research report saved to {file_name}")
