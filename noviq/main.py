from noviq.models.model_selector import ModelSelector
from noviq.research.research_manager import ResearchManager

def main():
    # Get user selected model
    selected_model = ModelSelector.select_model()
    print(f"Selected model: {selected_model}")
    
    # Initialize research manager
    research_manager = ResearchManager(selected_model)
    
    # Get user intent
    user_intent = input("Enter your research intent: ")
    
    # Get clarifying questions and answers
    qa_pairs = research_manager.get_clarifying_questions(user_intent)
    
    # Execute research plan and gather information
    scraped_webpage_texts = research_manager.execute_research_plan(user_intent, qa_pairs)
    
    # Generate final report
    research_report_text = research_manager.generate_report(user_intent, qa_pairs, scraped_webpage_texts)
    
    # Save report to file
    file_name = "report.html"
    with open(file_name, "w") as f:
        f.write(research_report_text)
    
    print(f"\nResearch report saved to {file_name}")

if __name__ == "__main__":
    main()
