import dspy
from noviq.signatures import GenerateClarifyingQuestions, PrepareForResearch, GenerateWebSearchQueries

user_intent = input("Enter your research intent: ")

lm = dspy.LM('ollama_chat/llama3.2:latest', api_base='http://localhost:11434')
dspy.configure(lm=lm)

clarifying_question = dspy.ChainOfThought(GenerateClarifyingQuestions)
questions = clarifying_question(user_intent=user_intent)

qa_pairs = []

print("Clarifying Questions:")
for question in questions.clarifying_questions:
    answer = input(question + "  ")
    qa_pairs.append((question, answer))


research_plan = dspy.ChainOfThought(PrepareForResearch)
generate_web_search_queries = dspy.ChainOfThought(GenerateWebSearchQueries)

plan = research_plan(user_intent=user_intent, qa_pairs=qa_pairs)

print("Research Plan:")
for step in plan.research_plan:
    web_search_queries = generate_web_search_queries(user_intent=user_intent, qa_pairs=qa_pairs, overall_research_plan=plan.research_plan, research_plan_step=step)
    print(step, web_search_queries.web_search_queries)