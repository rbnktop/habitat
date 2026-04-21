# logic.py

class RabbitLogic:
    """
    Core business logic for the Fuzzy Rabbit tool.
    Decoupled from the GUI to ensure Separation of Concerns.
    """
    def process_data(self, input_text):
        if not input_text:
            return "Error: No text provided."
        # Simple example logic: simulate a 'fuzzy' transform
        return f"Result: {input_text.upper()} (Fuzzified)"