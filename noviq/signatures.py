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
    research_plan: list[str] = dspy.OutputField(description="A research plan to help the user get the best answer.") #TODO: Should this be a list?



class GenerateWebSearchQueries(dspy.Signature):
    """Generate a list of web search queries based on the research plan step.
    The web search queries should be well detailed and include all the steps needed to get the best answer."""

    user_intent: str = dspy.InputField(description="The user's intent for the query.")
    qa_pairs: list[tuple[str, str]] = dspy.InputField(description="A list of qa pairs.")
    overall_research_plan: list[str] = dspy.InputField(description="The overall research plan to help the user get the best answer.")
    research_plan_step: str = dspy.InputField(description="A research plan step for which we need to generate web search queries to help the user get the best answer.")
    web_search_queries: list[str] = dspy.OutputField(description="A list of web search queries to help the user get the best answer for this current step.")

