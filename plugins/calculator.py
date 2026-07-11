"""
Calculator Plugin for VANGUARD.
"""
import re
from typing import List, Dict, Any
from commands import BasePlugin


class CalculatorPlugin(BasePlugin):
    """Safely evaluates mathematical expressions."""

    @property
    def name(self) -> str:
        return "Calculator"

    @property
    def description(self) -> str:
        return "Safely parses and solves basic mathematical expressions."

    @property
    def commands(self) -> List[str]:
        return ["calculate", "calc", "solve"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        if not args:
            return "Calculation failure. Please supply a mathematical expression (e.g., 'calc 42 * 12')."

        args_clean = args.strip()
        
        # Permit only numbers, decimal points, standard arithmetic operators, and parentheses
        if not re.match(r'^[0-9+\-*/().\s]*$', args_clean):
            return "VANGUARD SECURE PARSER: Expression rejected. Unpermitted characters detected."

        try:
            # Evaluate with restricted globals/locals to prevent arbitrary code execution
            safe_globals = {"__builtins__": None}
            safe_locals = {}
            result = eval(args_clean, safe_globals, safe_locals)
            
            # Limit precision of floats for speech readability
            if isinstance(result, float):
                result = round(result, 4)
                
            return f"Calculation completed successfully: {args_clean} = {result}."
        except ZeroDivisionError:
            return "Calculation failure. Division by zero is undefined."
        except Exception as e:
            return f"Calculation failure. Expression could not be parsed: {e}."
