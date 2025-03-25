import dspy


class GenerateClarifyingQuestions(dspy.Signature):
    """The user's intent for the query. User wants to deep research on a topic.
    We need to generate clarifying questions to help the user get the best answer."""

    user_intent: str = dspy.InputField(description="The user's intent for the query.")
    clarifying_questions: list[str] = dspy.OutputField(description="A list of 2 clarifying questions to help the user get the best answer.")



class PrepareForResearch(dspy.Signature):
    """Prepare a research plan based on the user's intent and the clarifying QA pairs.
    The research plan should be a list of steps that will help the user get the best answer.
    The research plan should be well detailed and include all the steps needed to get the best answer."""

    user_intent: str = dspy.InputField(description="The user's intent for the query.")
    qa_pairs: list[tuple[str, str]] = dspy.InputField(description="A list of qa pairs.")
    research_plan: list[str] = dspy.OutputField(description="A research plan to help the user get the best answer.")



class GenerateWebSearchQueries(dspy.Signature):
    """Generate a list of web search queries based on the research plan step.
    The web search queries should be well detailed and include all the steps needed to get the best answer."""

    user_intent: str = dspy.InputField(description="The user's intent for the query.")
    qa_pairs: list[tuple[str, str]] = dspy.InputField(description="A list of qa pairs.")
    overall_research_plan: list[str] = dspy.InputField(description="The overall research plan to help the user get the best answer.")
    research_plan_step: str = dspy.InputField(description="A research plan step for which we need to generate web search queries to help the user get the best answer.")
    web_search_queries: list[str] = dspy.OutputField(description="A list of web search queries to help the user get the best answer for this current step.")


class CleanAndClassifyWebpageText(dspy.Signature):
    """Clean the webpage text and classify it into a category to help the user get the best answer.
    Do not remove any information from the webpage text. Your job is to only clean the text and classify it into a category.
    Basically, the user is trying to research for a particular topic and the text provided is raw webpage content"""

    user_intent: str = dspy.InputField(description="The user's intent for the query.")
    webpage_text: str = dspy.InputField(description="The webpage text to clean. This text has been scraped from the web and is raw content. Some of the text might be irrelevant to the user's intent. Your job is to clean the text and classify it into a category.")
    cleaned_webpage_text: str = dspy.OutputField(description="The clean webpage content in markdown format. Return all of the sections of the webpage in markdown format. Do not remove any information from the webpage text. Your job is to only clean the text for irrelevant topics.")
    category: str = dspy.OutputField(description="The category of the webpage text to help the user get the best answer.")