import math
import re
from .prob import factorial, permutation, combination, rand, randi
from .coordinate import rectangular_to_polar_r, rectangular_to_polar_theta, polar_to_rectangular_x, polar_to_rectangular_y

def evaluate_expression(expression: str, angle_mode: str = "rad", output_format: str = "flo", 
                       decimal_places: int = None, ans: str = "0", hyp: bool = False,
                       rand_seed=None) -> dict:
    try:
        # Check for memory storage operations (►a, ►b, etc.)
        store_match = re.search(r'►([a-e]|r)$', expression)
        store_to_memory = None
        
        if store_match:
            # Extract which memory location to store to
            store_to_memory = store_match.group(1)
            # Remove the ►letter part for evaluation
            expression = expression[:store_match.start()]
            
       # Check for conversion operators and fraction types
        convert_to_fraction = "►f↔d" in expression
        convert_fraction_format = "►A B/C↔D/E" in expression
        has_mixed_fraction = "┘" in expression
        has_simple_fraction = bool(re.search(r'^\d+/\d+$|[^\d\/]\d+/\d+', expression.replace("┘", "")))
        
        # Determine conversion directions
        convert_direction_f_d = "to_decimal" if (convert_to_fraction and has_mixed_fraction) else "to_fraction"
        convert_direction_mixed = "to_improper" if (convert_fraction_format and has_mixed_fraction) else "to_mixed"
        
        # First normalize division symbols for consistent processing
        expression = expression.replace("÷", "/")
        
        # Replace "ans" with the value of ans
        expression = expression.replace("Ans", ans)
        
        # Check for ►DMS conversion
        convert_to_dms = "►DMS" in expression
        if convert_to_dms:
            # Remove the ►DMS part for evaluation
            expression = expression.replace("►DMS", "")
        
        # Process mixed fractions in input before evaluation
        if has_mixed_fraction:
            processed_expr = parse_mixed_fractions(expression)
        else:
            processed_expr = expression
            
        # Remove conversion operators before processing
        processed_expr = processed_expr.replace("►f↔d", "").replace("►A B/C↔D/E", "")
        
        # Process the expression as before
        processed_expr = process_expression(processed_expr, angle_mode)
        processed_expr = processed_expr.replace("math.math.", "math.")
        processed_expr = balance_parentheses(processed_expr)
        
        if angle_mode != "rad" or hyp:
            processed_expr = apply_angle_mode_conversion(processed_expr, angle_mode, hyp)
        
        # Evaluate the processed expression
        eval_namespace = {
            "math": math,
            "factorial": factorial,
            "permutation": permutation,
            "combination": combination,
            "rand": lambda: rand(seed=rand_seed),
            "randi": lambda min_val=0, max_val=100: randi(min_val, max_val, seed=rand_seed)
        }
        
        eval_namespace.update({
            "dms_to_decimal": lambda d, m, s, mode: dms_to_decimal(d, m, s, mode),
            "rad_to_angle_mode": lambda v, mode: rad_to_angle_mode(v, mode),
            "grad_to_angle_mode": lambda v, mode: grad_to_angle_mode(v, mode)
        })
        
        eval_namespace.update({
            "rectangular_to_polar_r": rectangular_to_polar_r,
            "rectangular_to_polar_theta": lambda x, y, mode: rectangular_to_polar_theta(x, y, mode),
            "polar_to_rectangular_x": lambda r, theta, mode: polar_to_rectangular_x(r, theta, mode),
            "polar_to_rectangular_y": lambda r, theta, mode: polar_to_rectangular_y(r, theta, mode)
        })
        
        result = eval(processed_expr, {"__builtins__": {}}, eval_namespace)
        result = clean_floating_point_errors(result)
        
        # Apply conversions based on flags and direction
        if convert_fraction_format:
            if convert_direction_mixed == "to_improper" and has_mixed_fraction:
                return mixed_to_improper_fraction(result)
            elif convert_direction_mixed == "to_mixed" and has_simple_fraction:
                return decimal_to_mixed_fraction(result)
            elif convert_direction_mixed == "to_mixed":
                # Default case - attempt to convert to mixed fraction
                return decimal_to_mixed_fraction(result)
        elif convert_to_fraction and convert_direction_f_d == "to_fraction":
            # Convert decimal to mixed fraction
            return decimal_to_mixed_fraction(result)
        elif has_mixed_fraction and not convert_to_fraction:
            # If we had mixed fractions in input without conversion, still show result as mixed fraction
            return decimal_to_mixed_fraction(result)
        
        # Format the result based on output_format
        if output_format == "flo":
            # For integers or numbers that can be represented as integers
            if isinstance(result, int) or (isinstance(result, float) and result.is_integer()):
                int_result = int(result)
                # Check if integer has more than 10 digits - if so, use sci notation
                if len(str(abs(int_result))) > 10:
                    exponent = math.floor(math.log10(abs(int_result)))
                    mantissa = int_result / (10 ** exponent)
                    if mantissa == int(mantissa):
                        formatted_result = f"{int(mantissa)}x10^{exponent}"
                    else:
                        formatted_result = f"{mantissa:.6g}x10^{exponent}"
                else:
                    formatted_result = str(int_result)
            else:
                # Standard floating point notation for regular floats
                formatted_result = f"{result:.10g}"
                
                # If formatting produced more than 10 digits before decimal, convert to sci
                parts = formatted_result.split('.')
                if len(parts[0]) > 10:
                    exponent = math.floor(math.log10(abs(result)))
                    mantissa = result / (10 ** exponent)
                    if mantissa == int(mantissa):
                        formatted_result = f"{int(mantissa)}x10^{exponent}"
                    else:
                        formatted_result = f"{mantissa:.6g}x10^{exponent}"
                
        elif output_format == "sci":
            # Scientific notation: ALWAYS use 1-10 x 10^n format
            if result == 0:
                formatted_result = "0x10^0"  # Special case for zero
            else:
                # Get mantissa between 1 and 10 and the exponent
                exponent = math.floor(math.log10(abs(result)))
                mantissa = result / (10 ** exponent)
                
                # Format with appropriate precision
                if mantissa == int(mantissa):
                    formatted_result = f"{int(mantissa)}x10^{exponent}"
                else:
                    formatted_result = f"{mantissa:.6g}x10^{exponent}"
                    
        elif output_format == "eng":
            # Engineering notation: ALWAYS use 1-1000 x 10^(3n) format
            if result == 0:
                formatted_result = "0x10^0"  # Special case for zero
            else:
                # Get the exponent
                exponent = math.floor(math.log10(abs(result)))
                # Adjust to nearest lower multiple of 3
                eng_exponent = 3 * (exponent // 3)
                # Calculate mantissa (between 1 and 1000)
                mantissa = result / (10 ** eng_exponent)
                
                # Format with appropriate precision
                if mantissa == int(mantissa):
                    formatted_result = f"{int(mantissa)}x10^{eng_exponent}"
                else:
                    formatted_result = f"{mantissa:.6g}x10^{eng_exponent}"
        else:
            # Default to floating point if an invalid format is specified
            formatted_result = f"{result:.10g}"
        
        # Apply fixed decimal places if specified
        if decimal_places is not None:
            if output_format == "flo":
                # For integers or numbers that can be represented as integers
                if isinstance(result, int) or (isinstance(result, float) and result.is_integer()):
                    if decimal_places == 0:
                        # For FIX 0, just show the integer without decimal point
                        formatted_result = str(int(result))
                    else:
                        # Add specified number of decimal places
                        formatted_result = f"{int(result)}.{'0' * decimal_places}"
                else:
                    # Format with specified decimal places
                    formatted_result = f"{result:.{decimal_places}f}"
            
            elif output_format == "sci":
                if result == 0:
                    formatted_result = f"0.{'0' * decimal_places}x10^0"
                else:
                    exponent = math.floor(math.log10(abs(result)))
                    mantissa = result / (10 ** exponent)
                    formatted_result = f"{mantissa:.{decimal_places}f}x10^{exponent}"
                    
            elif output_format == "eng":
                if result == 0:
                    formatted_result = f"0.{'0' * decimal_places}x10^0"
                else:
                    exponent = math.floor(math.log10(abs(result)))
                    eng_exponent = 3 * (exponent // 3)
                    mantissa = result / (10 ** eng_exponent)
                    formatted_result = f"{mantissa:.{decimal_places}f}x10^{eng_exponent}"
        
        result_tuple = {
            'value': formatted_result,
            'store_to': store_to_memory,
            'raw_value': result  # The numeric value before formatting
        }
        
        if convert_to_dms:
            return {
                'value': decimal_to_dms(result, angle_mode),
                'store_to': store_to_memory,
                'raw_value': result
            }
        
        return result_tuple
            
    except Exception as e:
        return {'value': f"Error: {str(e)}", 'store_to': None, 'raw_value': None}

def apply_angle_mode_conversion(expr: str, angle_mode: str, hyp: bool = False) -> str:
    """Apply angle mode conversions to trig functions"""
    import re
    
    if hyp:
        # For hyperbolic functions, just replace trig with hyperbolic equivalents
        # NO angle conversion needed for hyperbolic functions
        expr = re.sub(r'math\.sin\((.*?)\)', r'math.sinh(\1)', expr)
        expr = re.sub(r'math\.cos\((.*?)\)', r'math.cosh(\1)', expr)
        expr = re.sub(r'math\.tan\((.*?)\)', r'math.tanh(\1)', expr)
            
        # For inverse hyperbolic functions - also no angle conversion
        expr = re.sub(r'math\.asin\((.*?)\)', r'math.asinh(\1)', expr)
        expr = re.sub(r'math\.acos\((.*?)\)', r'math.acosh(\1)', expr)
        expr = re.sub(r'math\.atan\((.*?)\)', r'math.atanh(\1)', expr)
    else:
        # Standard angle mode conversions for regular trig functions
        if angle_mode == "deg":
            # Convert degrees to radians for trig functions
            expr = re.sub(r'math\.sin\((.*?)\)', r'math.sin(\1 * math.pi / 180)', expr)
            expr = re.sub(r'math\.cos\((.*?)\)', r'math.cos(\1 * math.pi / 180)', expr)
            expr = re.sub(r'math\.tan\((.*?)\)', r'math.tan(\1 * math.pi / 180)', expr)
            
            # For inverse trig functions, convert the result from radians to degrees
            expr = re.sub(r'math\.asin\((.*?)\)', r'(math.asin(\1) * 180 / math.pi)', expr)
            expr = re.sub(r'math\.acos\((.*?)\)', r'(math.acos(\1) * 180 / math.pi)', expr)
            expr = re.sub(r'math\.atan\((.*?)\)', r'(math.atan(\1) * 180 / math.pi)', expr)        
        elif angle_mode == "grd":
            # Convert gradians to radians for trig functions
            expr = re.sub(r'math\.sin\((.*?)\)', r'math.sin(\1 * math.pi / 200)', expr)
            expr = re.sub(r'math\.cos\((.*?)\)', r'math.cos(\1 * math.pi / 200)', expr)
            expr = re.sub(r'math\.tan\((.*?)\)', r'math.tan(\1 * math.pi / 200)', expr)
            
            # For inverse trig functions, convert the result from radians to gradians
            expr = re.sub(r'math\.asin\((.*?)\)', r'(math.asin(\1) * 200 / math.pi)', expr)
            expr = re.sub(r'math\.acos\((.*?)\)', r'(math.acos(\1) * 200 / math.pi)', expr)
            expr = re.sub(r'math\.atan\((.*?)\)', r'(math.atan(\1) * 200 / math.pi)', expr)
    
    return expr

def clean_floating_point_errors(result):
    if isinstance(result, float):
        # If the result is very close to zero, it's probably just zero
        if abs(result) < 1e-10:
            return 0
        # If it's very close to an integer, round it
        if abs(result - round(result)) < 1e-10:
            return round(result)
    return result

def process_expression(expression: str, angle_mode: str) -> str:    
    # Replace calculator symbols with Python equivalents
    expr = expression.replace("÷", "/").replace("π", "math.pi").replace("^", "**")
    
    # Handle percentage (%) - simply replace with division by 100
    expr = re.sub(r'(\d+(?:\.\d+)?)%', r'\1/100', expr)
    
    # Handle negation syntax (-)x
    expr = re.sub(r'\(-\)(\s*\d+|\s*\(|\s*[a-zA-Z])', r'-\1', expr)
    
    # Handle DMS notation (5°5'5")
    dms_pattern = r'(\d+)°(\d+)\'(\d+)"'
    expr = re.sub(dms_pattern, r'dms_to_decimal(\1, \2, \3, "{0}")'.format(angle_mode), expr)
    
    # Handle radian symbol (5r)
    rad_pattern = r'(\d+(?:\.\d+)?)r'
    expr = re.sub(rad_pattern, r'rad_to_angle_mode(\1, "{0}")'.format(angle_mode), expr)
    
    # Handle gradian symbol (5g)
    grad_pattern = r'(\d+(?:\.\d+)?)g'
    expr = re.sub(grad_pattern, r'grad_to_angle_mode(\1, "{0}")'.format(angle_mode), expr)
    
    # Handle coordinate conversion functions
    expr = re.sub(r'R►Pr\((.+?),(.+?)\)', r'rectangular_to_polar_r(\1, \2)', expr)
    expr = re.sub(r'R►Pθ\((.+?),(.+?)\)', r'rectangular_to_polar_theta(\1, \2, "{0}")'.format(angle_mode), expr)
    expr = re.sub(r'P►Rx\((.+?),(.+?)\)', r'polar_to_rectangular_x(\1, \2, "{0}")'.format(angle_mode), expr)
    expr = re.sub(r'P►Ry\((.+?),(.+?)\)', r'polar_to_rectangular_y(\1, \2, "{0}")'.format(angle_mode), expr)
        
    # Handle nth root (X√) with a number prefix
    nth_root_pattern = r'(\d+)X√\('  # Match only integers before X√
    i = 0
    while i < len(expr):
        match = re.search(nth_root_pattern, expr[i:])
        if not match:
            break
            
        # Adjust match positions to account for offset
        start_pos = i + match.start()
        end_pos = i + match.end()
        
        # Get the root value (n) - extract as string first
        n_str = match.group(1)
        
        # Convert to numeric value carefully
        n = int(n_str)  # Use simple integer conversion
        
        # Find the matching closing parenthesis
        open_count = 1
        close_pos = None
        
        for j in range(end_pos, len(expr)):
            if expr[j] == '(':
                open_count += 1
            elif expr[j] == ')':
                open_count -= 1
                if open_count == 0:
                    close_pos = j
                    break
                            
        if close_pos is None:
            # No closing parenthesis found, process the rest of the string
            arg_expr = expr[end_pos:]
            
            # Create the power expression using math.pow with 1.0 for floating-point division
            new_expr = f"math.pow({arg_expr}, 1.0/{n})"
            
            expr = expr[:start_pos] + new_expr
            i = len(expr)  # Move to end of string
        else:
            # Found closing parenthesis
            arg_expr = expr[end_pos:close_pos]
            
            # Create the power expression using math.pow with 1.0 for floating-point division
            new_expr = f"math.pow({arg_expr}, 1.0/{n})"
            
            expr = expr[:start_pos] + new_expr + expr[close_pos+1:]
            i = start_pos + len(new_expr)  # Continue search after replacement
    
    # NOW handle X√ without a preceding number (treat as square root)
    expr = expr.replace("X√(", "math.sqrt(")
    
    # FINALLY handle the simple square root symbol (√)
    expr = re.sub(r'√\(', 'math.sqrt(', expr)
    
    # Handle Euler's number 'e' - replace standalone 'e' with math.e
    # Use regex to avoid replacing 'e' in function names or other identifiers
    expr = re.sub(r'(?<![a-zA-Z])e(?![a-zA-Z])', 'math.e', expr)
    
    # Handle inverse trig functions with regex for more precision
    # This specifically looks for the pattern sin**(-1) followed by opening parenthesis
    expr = re.sub(r'sin\s*\*\*\s*\(\s*-\s*1\s*\)\s*\(', r'math.asin(', expr)
    expr = re.sub(r'cos\s*\*\*\s*\(\s*-\s*1\s*\)\s*\(', r'math.acos(', expr)
    expr = re.sub(r'tan\s*\*\*\s*\(\s*-\s*1\s*\)\s*\(', r'math.atan(', expr)
    
    # Also handle the compact form without spaces
    expr = re.sub(r'sin\*\*\(-1\)\(', r'math.asin(', expr)
    expr = re.sub(r'cos\*\*\(-1\)\(', r'math.acos(', expr)
    expr = re.sub(r'tan\*\*\(-1\)\(', r'math.atan(', expr)
    
    # Handle calculator-specific functions
    function_mappings = {
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
        'log': 'math.log10',
        'ln': 'math.log',
        'asin': 'math.asin',
        'acos': 'math.acos',
        'atan': 'math.atan',
        'e^': 'math.e**'
    }
    
    # Process each function
    for func_name, math_func in function_mappings.items():
        expr = replace_function(expr, func_name, math_func, angle_mode)
    
    # Basic safety check
    if any(keyword in expr for keyword in ["import", "exec", "eval", "__"]):
        raise ValueError("Invalid expression: potentially unsafe operations")
    
    # One final check for any weird combinations that might have emerged
    expr = expr.replace("math.amath.", "math.a")
    expr = expr.replace("math.math.", "math.")
    
    # Handle factorial
    expr = re.sub(r'(\d+)!', r'factorial(\1)', expr)
    
    # Handle permutation and combination
    expr = re.sub(r'(\d+|[a-zA-Z][a-zA-Z0-9]*)\s*nPr\s*(\d+|[a-zA-Z][a-zA-Z0-9]*)', r'permutation(\1, \2)', expr)
    expr = re.sub(r'(\d+|[a-zA-Z][a-zA-Z0-9]*)\s*nCr\s*(\d+|[a-zA-Z][a-zA-Z0-9]*)', r'combination(\1, \2)', expr)
    
    expr = re.sub(r'\brand\b(?!\()', r'rand()', expr)
    
    return expr

def replace_function(expression: str, func_name: str, replacement: str, angle_mode: str) -> str:
    result = expression
    i = 0
    
    while i < len(result):
        # Find function name
        func_pos = result.find(func_name + "(", i)
        if func_pos == -1:
            break
        
        # Find the opening parenthesis position
        open_paren_pos = func_pos + len(func_name)
        
        # Find matching closing parenthesis (accounting for nesting)
        paren_count = 1
        close_paren_pos = None
        
        for j in range(open_paren_pos + 1, len(result)):
            if result[j] == '(':
                paren_count += 1
            elif result[j] == ')':
                paren_count -= 1
                if paren_count == 0:
                    close_paren_pos = j
                    break
        
        # Extract function arguments
        if close_paren_pos is not None:
            # We found a matching closing parenthesis
            args = result[open_paren_pos + 1:close_paren_pos]
            
            # Process arguments recursively
            processed_args = process_expression(args, angle_mode)
            
            # Fix any double math prefixes
            processed_args = processed_args.replace("math.math.", "math.")
            
            # Create Python function call
            python_func = f"{replacement}({processed_args})"
            
            # Replace in the original expression
            result = result[:func_pos] + python_func + result[close_paren_pos + 1:]
            
            # Update search position
            i = func_pos + len(python_func)
        else:
            # No matching closing parenthesis
            args = result[open_paren_pos + 1:]
            
            # Process arguments recursively
            processed_args = process_expression(args, angle_mode)
            
            # Fix any double math prefixes
            processed_args = processed_args.replace("math.math.", "math.")
            
            # Create Python function call with closing parenthesis
            python_func = f"{replacement}({processed_args})"
            
            # Replace in the original expression
            result = result[:func_pos] + python_func
            
            # Update search position
            i = len(result)
    
    return result

def balance_parentheses(expr: str) -> str:
    open_count = 0
    
    # Count how many unclosed parentheses we have
    for char in expr:
        if char == '(':
            open_count += 1
        elif char == ')':
            open_count -= 1
    
    # If we have unclosed parentheses, add the necessary closing ones
    if open_count > 0:
        expr += ')' * open_count
        
    return expr

def decimal_to_mixed_fraction(num):
    if num == int(num):  # If it's a whole number
        return str(int(num))
        
    # Get the whole number part
    whole = int(num)
    
    # Get the fractional part as positive value
    fractional = abs(num - whole)
    
    # Convert decimal to fraction using continued fraction algorithm
    max_denominator = 1000  # Limit denominator to reasonable size
    
    # Find the best approximation with limited denominator
    from fractions import Fraction
    frac = Fraction(fractional).limit_denominator(max_denominator)
    
    # Check if the number is negative
    sign = "-" if num < 0 and whole == 0 else ""
    
    if whole == 0:
        # Just return the fraction if no whole number part
        return f"{sign}{frac.numerator}/{frac.denominator}"
    else:
        # Return mixed number format
        return f"{whole}┘{frac.numerator}/{frac.denominator}"
    
def parse_mixed_fractions(expression: str) -> str:
    """
    Parse mixed fractions like "3┘1/2" or "3┘1÷2" into decimal values.
    """
    # Use regex to find all mixed fractions in the expression
    import re
    
    # First, normalize division symbols to ensure consistent processing
    expression = expression.replace("÷", "/")
    
    # Pattern to match mixed fractions: whole number, ┘ symbol, numerator/denominator
    pattern = r'(-?\d+)┘(\d+)/(\d+)'
    
    def replace_mixed_fraction(match):
        whole = int(match.group(1))
        numerator = int(match.group(2))
        denominator = int(match.group(3))
        
        # Calculate the decimal value
        if whole < 0:
            # For negative whole numbers, we need to subtract the fraction part
            decimal_value = whole - (numerator / denominator)
        else:
            # For positive whole numbers, we add the fraction part
            decimal_value = whole + (numerator / denominator)
        
        return str(decimal_value)
    
    # Replace all mixed fractions with their decimal equivalents
    return re.sub(pattern, replace_mixed_fraction, expression)

def mixed_to_improper_fraction(num):
    """Convert a number to an improper fraction representation."""
    if num == int(num):  # If it's a whole number
        return f"{int(num)}/1"
    
    # Convert to fraction using Python's Fraction
    from fractions import Fraction
    frac = Fraction(num).limit_denominator(1000)
    
    # Return the improper fraction
    return f"{frac.numerator}/{frac.denominator}"

def dms_to_decimal(degrees, minutes=0, seconds=0, angle_mode="rad"):
    # First convert to decimal degrees
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    
    # Then convert to the target angle mode
    if angle_mode == "rad":
        return decimal_degrees * math.pi / 180
    elif angle_mode == "grd":
        return decimal_degrees * 400 / 360  # 400 gradians = 360 degrees
    else:  # Default to degrees
        return decimal_degrees

def rad_to_angle_mode(value, angle_mode="rad"):
    if angle_mode == "deg":
        return value * 180 / math.pi
    elif angle_mode == "grd":
        return value * 200 / math.pi
    else:  # Default to radians
        return value

def grad_to_angle_mode(value, angle_mode="rad"):
    if angle_mode == "rad":
        return value * math.pi / 200
    elif angle_mode == "deg":
        return value * 9 / 10  # 90° = 100 grad
    else:  # Default to gradians
        return value

def decimal_to_dms(decimal_value, angle_mode="rad"):
    # First convert to decimal degrees regardless of input mode
    if angle_mode == "rad":
        degrees_decimal = decimal_value * 180 / math.pi
    elif angle_mode == "grd":
        degrees_decimal = decimal_value * 360 / 400
    else:  # degrees
        degrees_decimal = decimal_value
    
    # Handle negative values
    sign = -1 if degrees_decimal < 0 else 1
    degrees_decimal = abs(degrees_decimal)
    
    # Extract degrees (whole part)
    degrees = int(degrees_decimal)
    
    # Extract minutes
    minutes_decimal = (degrees_decimal - degrees) * 60
    minutes = int(minutes_decimal)
    
    # Extract seconds
    seconds = round((minutes_decimal - minutes) * 60)
    
    # Handle case where seconds round to 60
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    
    # Format with sign
    if sign == -1:
        return f"-{degrees}°{minutes}'{seconds}\""
    else:
        return f"{degrees}°{minutes}'{seconds}\""