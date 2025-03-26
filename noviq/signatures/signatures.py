import dspy


class GenerateClarifyingQuestions(dspy.Signature):
    """Generate clarifying questions to better understand the user's research context and preferences.
    
    Rules:
    1. Focus on gathering context about user's preferences, constraints, and specific interests
    2. Do NOT ask the user to explain their research topic - that's what we're here to research
    3. Questions should help narrow down the scope and focus of the research
    4. Each question should be specific and focused on one aspect
    5. Questions should be easy to answer with a short response
    6. Avoid yes/no questions unless absolutely necessary
    7. Questions should help understand:
       - Time period of interest
       - Specific aspects or angles they're interested in
       - Any constraints or preferences
       - Their level of expertise in the topic
       - Any specific sources they trust
    """

    user_intent: str = dspy.InputField(
        description="""The user's research query or topic they want to explore.
        This is the main topic we'll be researching, so don't ask them to explain it."""
    )
    
    clarifying_questions: list[str] = dspy.OutputField(
        description="""A list of 2-3 focused clarifying questions that will help:
        1. Understand the user's specific interests within the topic
        2. Identify any constraints or preferences
        3. Determine the appropriate depth and scope of research
        4. Gather context about their expertise level
        5. Learn about trusted sources or perspectives
        
        Each question should:
        - Be specific and focused
        - Be easy to answer briefly
        - Help narrow down the research scope
        - NOT ask them to explain their topic
        - NOT be a yes/no question unless necessary"""
    )



class PrepareForResearch(dspy.Signature):
    """Generate a detailed, actionable research plan based on user intent and clarifying answers.
    
    Rules:
    1. Each step should be specific and actionable
    2. Steps should be ordered from broad to specific
    3. Each step should be convertible to search queries
    4. Include specific aspects mentioned in clarifying answers
    5. Consider time periods, expertise levels, and preferences from QA pairs
    6. Focus on gathering comprehensive information
    7. Include steps for:
       - Core topic understanding
       - Specific aspects mentioned
       - Current developments/trends
       - Expert opinions/analysis
       - Practical applications
       - Historical context (if relevant)
    """

    user_intent: str = dspy.InputField(
        description="""The user's research query or topic they want to explore.
        This is the main topic we'll be researching."""
    )
    
    qa_pairs: list[tuple[str, str]] = dspy.InputField(
        description="""List of (question, answer) pairs from clarifying questions.
        Use these to tailor the research plan to user's specific interests and needs."""
    )
    
    research_plan: list[str] = dspy.OutputField(
        description="""A list of 4-6 specific, actionable research steps. Each step should:
        1. Be specific enough to generate targeted search queries
        2. Focus on one aspect of the research
        3. Include relevant context from QA pairs
        4. Be phrased to yield good search results
        5. Follow a logical progression
        
        Example format for each step:
        "Research [specific aspect] of [topic] focusing on [context from QA]"
        
        The steps should cover:
        - Core understanding
        - Specific interests
        - Current developments
        - Expert perspectives
        - Practical applications
        - Historical context (if relevant)"""
    )



class GenerateWebSearchQueries(dspy.Signature):
    """Generate focused, concrete web search queries based on the research plan step.
    
    Rules:
    1. Generate 4-5 highly targeted queries per research step
    2. Include specific details from user intent and QA pairs
    3. Focus on recent and relevant information
    4. Use proper search operators (+, quotes) for precision
    5. Make queries specific and actionable
    """

    user_intent: str = dspy.InputField(
        description="""The user's research query or topic they want to explore.
        Use this to ensure queries align with the user's goals."""
    )
    
    qa_pairs: list[tuple[str, str]] = dspy.InputField(
        description="""List of (question, answer) pairs from clarifying questions.
        Use these to add specific context and requirements to the queries."""
    )
    
    overall_research_plan: list[str] = dspy.InputField(
        description="""The complete research plan.
        Use this to ensure queries align with the overall research direction."""
    )
    
    research_plan_step: str = dspy.InputField(
        description="""The specific research step to generate queries for.
        Focus on creating queries that directly address this step's goals."""
    )
    
    web_search_queries: list[str] = dspy.OutputField(
        description="""A list of 4-5 focused, concrete web search queries. Each query should:
        1. Include relevant details from user intent and QA pairs
        2. Use proper search operators (+, quotes) for precision
        3. Focus on recent information (last 1-2 years)
        4. Be specific enough to yield targeted results
        5. Combine related terms effectively
        
        Example format:
        "specific topic" + "relevant context" + "additional details"
        
        Guidelines:
        - Keep queries focused and specific
        - Include important details from QA pairs
        - Use quotes for exact phrases
        - Use + operator to combine related terms
        - Avoid too many variations of the same query"""
    )


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
    research_report: str = dspy.OutputField(description="A final research report formatted in markdown. Do not output any sort of HTML tags. Explain in super detail by taking all the qa pairs and the cleaned webpage text into account.")
