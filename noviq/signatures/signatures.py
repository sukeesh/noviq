import dspy


class GenerateClarifyingQuestions(dspy.Signature):
    """Generate clarifying questions to understand the user's personal context and preferences for the research.
    
    Rules:
    1. Focus ONLY on the user's PERSONAL context - their goals, preferences, and background
    2. NEVER ask the user to provide technical information about the research topic
    3. Questions should help understand the USER, not the topic
    4. Ask about the user's needs, constraints, preferences, and experience level
    5. Assume the user is asking YOU to research the topic - don't ask them to explain it
    6. Questions should be easy for anyone to answer about THEMSELVES
    
    CRITICAL: Do NOT ask questions that require domain expertise or technical knowledge about the topic!
    """

    user_intent: str = dspy.InputField(
        description="""The user's research request. Your job is to understand their personal context, 
        not to have them explain the topic to you."""
    )
    
    clarifying_questions: list[str] = dspy.OutputField(
        description="""A list of 2-3 questions focused ONLY on understanding the user's personal context.
        
        GOOD questions (about the USER, not the topic):
        - "What is your background or experience level with this subject?"
        - "What is your main goal or purpose for researching this topic?"
        - "Do you need a general overview or specific details on certain aspects?"
        - "What format or level of detail would be most helpful for you?"
        - "Is there a specific time period or geographic focus that interests you?"
        - "Are there any particular perspectives or viewpoints you want included?"
        
        BAD questions (asking for topic expertise - NEVER ASK THESE):
        - "What are the technical aspects of X that drive Y?"
        - "How does X impact Y in the industry?"
        - "What are the specific issues with X?"
        
        Each question must be about the USER's context, preferences, or constraints - NEVER about technical aspects of the topic itself.
        The user is coming to YOU for research - don't ask them to do the research!
        """
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
    1. Generate 5 highly targeted queries per research step
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
        description="""A list of 5 focused, concrete web search queries. Each query should:
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
    """Generate a comprehensive research report in HTML format based on collected information. Output is strictly in HTML Format."""

    user_intent: str = dspy.InputField(description="The user's research topic to address.")
    qa_pairs: list[tuple[str, str]] = dspy.InputField(description="Question-answer pairs to tailor the report content.")
    cleaned_webpage_text: list[str] = dspy.InputField(description="Cleaned webpage content to use as source material.")
    research_report: str = dspy.OutputField(
        description="""Complete HTML document with proper structure, semantic tags, and styling. 
        The report should be very well detailed and should be very well organized. 
        Include all relevant information organized logically. All the details should be STRICTLY in the HTML format.
        """
    )
