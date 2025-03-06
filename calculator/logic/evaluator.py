# calculator/logic/evaluator.py
def evaluate_expression(expression: str) -> float:
    # You can use eval for basic operations or a safer method later
    try:
        return eval(expression)
    except Exception as e:
        return str(e)  # Handle errors
