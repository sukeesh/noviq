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
    """Extract and structure the relevant content from raw webpage text.
    
    Rules:
    1. Remove all navigation elements, ads, and website chrome
    2. Remove all notification prompts and website settings
    3. Keep only the main article/content
    4. Format the content in clean markdown with proper headers and sections
    5. Preserve all factual information from the main content
    6. Do not add any commentary or analysis
    """

    user_intent: str = dspy.InputField(
        description="The user's research intent to help focus the content extraction."
    )
    
    webpage_text: str = dspy.InputField(
        description="Raw webpage text that needs cleaning. Contains the main content mixed with navigation, ads, and website elements."
    )
    
    cleaned_webpage_text: str = dspy.OutputField(
        description="""The extracted main content in markdown format. Must:
        - Remove all navigation, ads, footers, notification prompts
        - Keep only the actual article/content
        - Format with proper markdown headers (##, ###)
        - Preserve all facts and information
        - Use bullet points for lists
        - Include any relevant dates, numbers, statistics
        Do not add any commentary or analysis."""
    )
    
    category: str = dspy.OutputField(
        description="""A single specific category that best describes the content."""
    )


class GenerateFinalResearchReport(dspy.Signature):
    """Generate a final research report based on the user's intent and the cleaned webpage text.
    The research report should be well detailed and include all the steps needed to get the best answer."""

    user_intent: str = dspy.InputField(description="The user's intent for the query.")
    qa_pairs: list[tuple[str, str]] = dspy.InputField(description="A list of qa pairs.")
    cleaned_webpage_text: list[str] = dspy.InputField(description="A list of cleaned webpage text for reference.")
    research_report: str = dspy.OutputField(description="A final research report formatted in markdown. Explain in super detail by taking all the qa pairs and the cleaned webpage text into account.")
