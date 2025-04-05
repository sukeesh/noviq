import inquirer
import ollama

class ModelSelector:
    @staticmethod
    def select_model():
        """
        Prompts user to select a model from available Ollama models
        Returns:
            str: Selected model name
        """
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