import math


class StatisticsManager:
    def __init__(self):
        self.in_stat_mode = False
        self.stat_mode = None  # '1-var' or '2-var'
        self.in_data_entry = False
        self.data_1var = []  # List of (value, frequency) tuples
        self.data_2var = []  # List of (x, y) tuples for 2-var mode
        self.current_x_index = 1
        self.current_freq = 1
        self.viewing_freq = False  # Whether currently viewing X or frequency (for 1-var)
        self.viewing_y = False     # Whether currently viewing X or Y (for 2-var)
        
    def update_current_value(self, value_str):
        value_str = value_str.replace("<u>", "").replace("</u>", "")
        self.current_value = value_str
        
        # Try to convert to appropriate numeric type 
        try:
            # Handle 1-var mode
            if self.stat_mode == '1-var':
                if self.viewing_freq:
                    # Update frequency (must be positive integer)
                    freq = max(1, int(float(value_str))) if value_str else 1
                    
                    # Make sure we have an X value to associate with this frequency
                    while len(self.data_1var) < self.current_x_index:
                        self.data_1var.append((0, 1))
                    
                    # Get the current X value
                    x_value = self.data_1var[self.current_x_index-1][0]
                    
                    # Update the frequency
                    self.data_1var[self.current_x_index-1] = (x_value, freq)
                    self.current_freq = freq
                else:
                    # Update X value
                    x_value = float(value_str) if value_str else 0
                    
                    # Ensure we have space in our data structure
                    while len(self.data_1var) < self.current_x_index:
                        self.data_1var.append((0, 1))
                    
                    # Get existing frequency or use default
                    freq = self.data_1var[self.current_x_index-1][1] if self.current_x_index <= len(self.data_1var) else 1
                    
                    # Update the X value
                    self.data_1var[self.current_x_index-1] = (x_value, freq)
            
            # Handle 2-var mode
            elif self.stat_mode == '2-var':
                if self.viewing_y:
                    # Update Y value
                    y_value = float(value_str) if value_str else 0
                    
                    # Make sure we have an X value to associate with this Y
                    while len(self.data_2var) < self.current_x_index:
                        self.data_2var.append((0, 0))
                    
                    # Get the current X value
                    x_value = self.data_2var[self.current_x_index-1][0]
                    
                    # Update the Y value
                    self.data_2var[self.current_x_index-1] = (x_value, y_value)
                else:
                    # Update X value
                    x_value = float(value_str) if value_str else 0
                    
                    # Ensure we have space in our data structure
                    while len(self.data_2var) < self.current_x_index:
                        self.data_2var.append((0, 0))
                    
                    # Get existing Y value or use default
                    y_value = self.data_2var[self.current_x_index-1][1] if self.current_x_index <= len(self.data_2var) else 0
                    
                    # Update the X value
                    self.data_2var[self.current_x_index-1] = (x_value, y_value)
            return True
        except (ValueError, TypeError):
            # Invalid numeric input
            print(f"Invalid numeric input: {value_str}")
            return False
    
    def enter_stat_mode(self, mode):
        if mode not in ['1-var', '2-var']:
            return False
        
        self.in_stat_mode = True
        self.stat_mode = mode
        
        # Reset data structures when entering stat mode
        if mode == '1-var':
            self.data_1var = []
            # Reset 1-var navigation indices
            self.current_x_index = 1
            self.current_freq = 1
            self.viewing_freq = False
        elif mode == '2-var':
            self.data_2var = []
            # Reset 2-var navigation indices
            self.current_x_index = 1
            self.viewing_y = False
        
        # Not in data entry mode yet - that happens when DATA button is pressed
        self.in_data_entry = False
        
        return True
    
    def exit_stat_mode(self):
        # Exit from stat mode
        self.in_stat_mode = False
        
        # Exit from data entry if we're in it
        self.in_data_entry = False
        
        # Reset navigation indices
        self.current_x_index = 1
        self.current_freq = 1
        self.viewing_freq = False
        
        # Keep the data but clear the mode
        self.stat_mode = None
        
        return True
    
    def start_data_entry(self):
        if not self.in_stat_mode:
            return False, ""
        
        # Enter data entry mode
        self.in_data_entry = True
        
        # Handle 1-var mode
        if self.stat_mode == '1-var':
            # Initialize for first data point if we don't already have data
            if not self.data_1var:
                self.current_x_index = 1
                self.current_freq = 1
                self.viewing_freq = False
                prompt = f"X{self.current_x_index}="
            else:
                # If we already have data, show the first X value
                self.current_x_index = 1
                self.viewing_freq = False
                x_value = self.data_1var[0][0]
                prompt = f"X{self.current_x_index}={x_value}"
        
        # Handle 2-var mode
        elif self.stat_mode == '2-var':
            # Initialize for first data point if we don't already have data
            if not self.data_2var:
                self.current_x_index = 1
                self.viewing_y = False
                prompt = f"X{self.current_x_index}="
            else:
                # If we already have data, show the first X value
                self.current_x_index = 1
                self.viewing_y = False
                x_value = self.data_2var[0][0]
                prompt = f"X{self.current_x_index}={x_value}"
        
        # Reset current value
        self.current_value = ""
        
        return True, prompt
    
    def navigate_up(self):
        if not self.in_stat_mode or not self.in_data_entry:
            return False, ""
        
        # Always save current value before navigating
        if hasattr(self, 'current_value') and self.current_value:
            self.update_current_value(self.current_value)
        
        # Handle 1-var mode
        if self.stat_mode == '1-var':
            if self.viewing_freq:
                # If viewing frequency, go back to the X value
                self.viewing_freq = False
                
                # Get the stored X value if it exists
                x_value = ""
                if self.current_x_index <= len(self.data_1var):
                    x_value = str(self.data_1var[self.current_x_index-1][0])
                
                prompt = f"X{self.current_x_index}=" + x_value
            
            elif self.current_x_index > 1:
                # If viewing X value (not the first one), go to previous freq
                self.current_x_index -= 1
                self.viewing_freq = True
                
                # Get the stored frequency if it exists
                freq_value = ""
                if self.current_x_index <= len(self.data_1var):
                    freq_value = str(self.data_1var[self.current_x_index-1][1])
                
                prompt = f"freq=" + freq_value
            
            else:
                # Can't go up from X1, just stay and show current value
                x_value = ""
                if self.current_x_index <= len(self.data_1var):
                    x_value = str(self.data_1var[self.current_x_index-1][0])
                
                prompt = f"X{self.current_x_index}=" + x_value
        
        # Handle 2-var mode
        elif self.stat_mode == '2-var':
            if self.viewing_y:
                # If viewing Y, go back to X (same index)
                self.viewing_y = False
                
                # Get the stored X value if it exists
                x_value = ""
                if self.current_x_index <= len(self.data_2var):
                    x_value = str(self.data_2var[self.current_x_index-1][0])
                
                prompt = f"X{self.current_x_index}=" + x_value
            
            elif self.current_x_index > 1:
                # If at X (not X1), go to previous Y
                self.current_x_index -= 1
                self.viewing_y = True
                
                # Get the stored Y value if it exists
                y_value = ""
                if self.current_x_index <= len(self.data_2var):
                    y_value = str(self.data_2var[self.current_x_index-1][1])
                
                prompt = f"Y{self.current_x_index}=" + y_value
            
            else:
                # Can't go up from X1, just stay there
                x_value = ""
                if self.current_x_index <= len(self.data_2var):
                    x_value = str(self.data_2var[self.current_x_index-1][0])
                
                prompt = f"X{self.current_x_index}=" + x_value
        
        # Reset current_value for new field
        self.current_value = ""
        return True, prompt
    
    def navigate_down(self):
        if not self.in_stat_mode or not self.in_data_entry:
            return False, ""
        
        # Always save current value before navigating
        if hasattr(self, 'current_value') and self.current_value:
            self.update_current_value(self.current_value)
        
        # Handle 1-var mode
        if self.stat_mode == '1-var':
            if not self.viewing_freq:
                # If viewing X value, we can go to frequency only if X has a value
                # Either from current_value or from data_1var
                has_x_value = bool(self.current_value) or (
                    self.current_x_index <= len(self.data_1var) and 
                    self.data_1var[self.current_x_index-1][0] != 0)
                
                if has_x_value:
                    # If viewing X value, go to frequency
                    self.viewing_freq = True
                    
                    # Get the stored frequency if it exists
                    freq_value = ""
                    if self.current_x_index <= len(self.data_1var):
                        freq_value = str(self.data_1var[self.current_x_index-1][1])
                    
                    prompt = f"freq=" + freq_value
                    
                    # Reset current_value for new field
                    self.current_value = ""
                    return True, prompt
                else:
                    # Can't go down without a valid X value
                    return False, f"X{self.current_x_index}="
            else:
                # If viewing frequency, we can go to next X value only if this freq has a value
                # Either from current_value or from data_1var
                has_freq_value = bool(self.current_value) or (
                    self.current_x_index <= len(self.data_1var) and 
                    self.data_1var[self.current_x_index-1][1] > 0)
                
                if has_freq_value:
                    # Move to next X value (only one more)
                    next_x_index = self.current_x_index + 1
                    
                    # Only go to next X if it's within one position of our data
                    can_move_to_next = (next_x_index <= len(self.data_1var) + 1)
                    
                    if can_move_to_next:
                        self.current_x_index = next_x_index
                        self.viewing_freq = False
                        
                        # Get the stored X value if it exists
                        x_value = ""
                        if self.current_x_index <= len(self.data_1var):
                            x_value = str(self.data_1var[self.current_x_index-1][0])
                        
                        prompt = f"X{self.current_x_index}=" + x_value
                        
                        # Reset current_value for new field
                        self.current_value = ""
                        return True, prompt
                    else:
                        # Can't go past the end of data + 1
                        return False, f"freq=" + (self.current_value or "1")
                else:
                    # Can't go down without a valid frequency value
                    return False, f"freq=" + (self.current_value or "1")
        
        # Handle 2-var mode
        elif self.stat_mode == '2-var':
            if not self.viewing_y:
                # If viewing X value, we can go to Y only if X has a value
                has_x_value = bool(self.current_value) or (
                    self.current_x_index <= len(self.data_2var) and 
                    self.data_2var[self.current_x_index-1][0] != 0)
                
                if has_x_value:
                    # If viewing X value, go to Y
                    self.viewing_y = True
                    
                    # Get the stored Y value if it exists
                    y_value = ""
                    if self.current_x_index <= len(self.data_2var):
                        y_value = str(self.data_2var[self.current_x_index-1][1])
                    
                    prompt = f"Y{self.current_x_index}=" + y_value
                    
                    # Reset current_value for new field
                    self.current_value = ""
                    return True, prompt
                else:
                    # Can't go down without a valid X value
                    return False, f"X{self.current_x_index}="
            else:
                # If viewing Y, we can go to next X value only if this Y has a value
                has_y_value = bool(self.current_value) or (
                    self.current_x_index <= len(self.data_2var) and 
                    self.data_2var[self.current_x_index-1][1] != 0)
                
                if has_y_value:
                    # Move to next X value (only one more)
                    next_x_index = self.current_x_index + 1
                    
                    # Only go to next X if it's within one position of our data
                    can_move_to_next = (next_x_index <= len(self.data_2var) + 1)
                    
                    if can_move_to_next:
                        self.current_x_index = next_x_index
                        self.viewing_y = False
                        
                        # Get the stored X value if it exists
                        x_value = ""
                        if self.current_x_index <= len(self.data_2var):
                            x_value = str(self.data_2var[self.current_x_index-1][0])
                        
                        prompt = f"X{self.current_x_index}=" + x_value
                        
                        # Reset current_value for new field
                        self.current_value = ""
                        return True, prompt
                    else:
                        # Can't go past the end of data + 1
                        return False, f"Y{self.current_x_index}=" + (self.current_value or "0")
                else:
                    # Can't go down without a valid Y value
                    return False, f"Y{self.current_x_index}=" + (self.current_value or "0")
        
        # Should never reach here
        return False, self.get_current_prompt()[1]
    
    def add_data_point(self, value):
        if not self.in_stat_mode or not self.in_data_entry:
            return False, ""
        
        try:
            # Handle 1-var mode
            if self.stat_mode == '1-var':
                if self.viewing_freq:
                    # Frequency must be a positive integer
                    freq = int(float(value))
                    if freq <= 0:
                        return False, f"freq={self.current_freq}"
                    
                    # We're updating frequency - ensure the X value exists
                    while len(self.data_1var) < self.current_x_index:
                        # Add placeholder values if needed
                        self.data_1var.append((0, 1))
                    
                    # Update the frequency
                    x_value = self.data_1var[self.current_x_index-1][0]
                    self.data_1var[self.current_x_index-1] = (x_value, freq)
                    self.current_freq = freq
                    
                    # Move to next X value after setting frequency
                    self.current_x_index += 1
                    self.viewing_freq = False
                    return True, f"X{self.current_x_index}="
                else:
                    # Add X value
                    x_value = float(value)
                    
                    # Ensure we have space in our data structure
                    while len(self.data_1var) < self.current_x_index:
                        self.data_1var.append((0, 1))
                    
                    # Set X value (with default freq=1 initially)
                    self.data_1var[self.current_x_index-1] = (x_value, 1)
                    
                    # Move to frequency input
                    self.viewing_freq = True
                    return True, f"freq=1"
            
            # Handle 2-var mode
            elif self.stat_mode == '2-var':
                if self.viewing_y:
                    # Add Y value
                    y_value = float(value)
                    
                    # We're updating Y - ensure the X value exists
                    while len(self.data_2var) < self.current_x_index:
                        # Add placeholder values if needed
                        self.data_2var.append((0, 0))
                    
                    # Update the Y value (preserving X)
                    x_value = self.data_2var[self.current_x_index-1][0]
                    self.data_2var[self.current_x_index-1] = (x_value, y_value)
                    
                    # Move to next X value after setting Y
                    self.current_x_index += 1
                    self.viewing_y = False
                    return True, f"X{self.current_x_index}="
                else:
                    # Add X value
                    x_value = float(value)
                    
                    # Ensure we have space in our data structure
                    while len(self.data_2var) < self.current_x_index:
                        self.data_2var.append((0, 0))
                    
                    # Set X value (with default Y=0 initially)
                    self.data_2var[self.current_x_index-1] = (x_value, 0)
                    
                    # Move to Y input
                    self.viewing_y = True
                    return True, f"Y{self.current_x_index}="
                    
        except (ValueError, TypeError):
            # Invalid input
            if self.stat_mode == '1-var':
                if self.viewing_freq:
                    return False, f"freq={self.current_freq}"
                else:
                    return False, f"X{self.current_x_index}="
            elif self.stat_mode == '2-var':
                if self.viewing_y:
                    return False, f"Y{self.current_x_index}="
                else:
                    return False, f"X{self.current_x_index}="
        
        return False, self.get_current_prompt()[1]
    
    def get_current_prompt(self):
        if not self.in_stat_mode or not self.in_data_entry:
            return False, ""
        
        # Handle 1-var mode
        if self.stat_mode == '1-var':
            if self.viewing_freq:
                # Get current frequency value if it exists
                freq_value = ""
                if self.current_x_index <= len(self.data_1var):
                    freq_value = str(self.data_1var[self.current_x_index-1][1])
                
                return True, f"freq=" + freq_value
            else:
                # Get current X value if it exists
                x_value = ""
                if self.current_x_index <= len(self.data_1var):
                    x_value = str(self.data_1var[self.current_x_index-1][0])
                
                return True, f"X{self.current_x_index}=" + x_value
        
        # Handle 2-var mode
        elif self.stat_mode == '2-var':
            if self.viewing_y:
                # Get current Y value if it exists
                y_value = ""
                if self.current_x_index <= len(self.data_2var):
                    y_value = str(self.data_2var[self.current_x_index-1][1])
                
                return True, f"Y{self.current_x_index}=" + y_value
            else:
                # Get current X value if it exists
                x_value = ""
                if self.current_x_index <= len(self.data_2var):
                    x_value = str(self.data_2var[self.current_x_index-1][0])
                
                return True, f"X{self.current_x_index}=" + x_value
        
        # Should never reach here
        return False, ""
    
    def clear_all_data(self):
        # Check if there's any data to clear
        had_data = len(self.data_1var) > 0 or len(self.data_2var) > 0
        
        # Reset data structures
        self.data_1var = []
        self.data_2var = []
        
        # Reset navigation indices
        self.current_x_index = 1
        self.current_freq = 1
        self.viewing_freq = False
        self.viewing_y = False
        
        # Exit data entry mode if we're in it
        if self.in_data_entry:
            self.in_data_entry = False
        
        # Return whether any data was actually cleared
        return had_data
    
    def calculate_1var_statistics(self):
        if not self.data_1var:
            return {
                'n': 0, 'mean': 0, 'sx': 0, 'sigmax': 0, 'sum_x': 0, 'sum_x_squared': 0
            }
        
        # Calculate n (sum of frequencies)
        n = sum(freq for _, freq in self.data_1var)
        
        # Calculate mean (weighted)
        weighted_sum = sum(x * freq for x, freq in self.data_1var)
        mean = weighted_sum / n if n > 0 else 0
        
        # Calculate sum of squares (for std dev)
        sum_squares = sum((x - mean)**2 * freq for x, freq in self.data_1var)
        
        # Sample standard deviation (n-1 denominator)
        sx = (sum_squares / (n - 1))**0.5 if n > 1 else 0
        
        # Population standard deviation (n denominator)
        sigmax = (sum_squares / n)**0.5 if n > 0 else 0
        
        # Sum of x values (weighted)
        sum_x = weighted_sum
        
        # Sum of x² values (weighted)
        sum_x_squared = sum(x**2 * freq for x, freq in self.data_1var)
        
        return {
            'n': n,
            'mean': mean,
            'sx': sx,
            'sigmax': sigmax,
            'sum_x': sum_x,
            'sum_x_squared': sum_x_squared
        }
    
    def calculate_2var_statistics(self):
        if not self.data_2var:
            return {
                'n': 0, 'mean_x': 0, 'sx': 0, 'sigmax': 0, 'mean_y': 0, 'sy': 0, 
                'sigmay': 0, 'sum_x': 0, 'sum_x_squared': 0, 'sum_y': 0, 
                'sum_y_squared': 0, 'sum_xy': 0, 'a': 0, 'b': 0, 'r': 0,
                'x_prime': 0, 'y_prime': 0
            }
            
        # Calculate n (number of data points)
        n = len(self.data_2var)
        
        # Calculate mean X value
        sum_x = sum(x for x, _ in self.data_2var)
        mean_x = sum_x / n
        
        # Calculate sum of X² values
        sum_x_squared = sum(x**2 for x, _ in self.data_2var)
        
        # Calculate variance then take square root for standard deviation
        # Sample variance (n-1 denominator)
        x_variance = (sum_x_squared - n * mean_x**2) / (n - 1)
        # Sample standard deviation (Sx)
        sx = math.sqrt(x_variance) if x_variance > 0 else 0
        
        # Population variance (n denominator)
        x_pop_variance = (sum_x_squared - n * mean_x**2) / n
        # Population standard deviation (σx)
        sigmax = math.sqrt(x_pop_variance) if x_pop_variance > 0 else 0
        
        # Calculate mean Y value
        sum_y = sum(y for _, y in self.data_2var)
        mean_y = sum_y / n
        
        # Calculate sum of Y² values
        sum_y_squared = sum(y**2 for _, y in self.data_2var)
        
        # Calculate variance then take square root for standard deviation
        # Sample variance (n-1 denominator)
        y_variance = (sum_y_squared - n * mean_y**2) / (n - 1)
        # Sample standard deviation (Sy)
        sy = math.sqrt(y_variance) if y_variance > 0 else 0
        
        # Population variance (n denominator)
        y_pop_variance = (sum_y_squared - n * mean_y**2) / n
        # Population standard deviation (σy)
        sigmay = math.sqrt(y_pop_variance) if y_pop_variance > 0 else 0
        
        # Calculate sum of XY products
        sum_xy = sum(x * y for x, y in self.data_2var)
        
        # Calculate y-intercept (a) and slope (b) of regression line
        a = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x**2)
        b = mean_y - a * mean_x
        
        # Calculate correlation coefficient (r)
        r = (n * sum_xy - sum_x * sum_y) / ((n * sum_x_squared - sum_x**2)**0.5 * (n * sum_y_squared - sum_y**2)**0.5)
        
        # Calculate x' and y' (mean-centered values)
        x_prime = [x - mean_x for x, _ in self.data_2var]
        y_prime = [y - mean_y for _, y in self.data_2var]
        
        return {
            'n': n,
            'mean_x': mean_x,
            'sx': sx,
            'sigmax': sigmax,
            'mean_y': mean_y,
            'sy': sy,
            'sigmay': sigmay,
            'sum_x': sum_x,
            'sum_x_squared': sum_x_squared,
            'sum_y': sum_y,
            'sum_y_squared': sum_y_squared,
            'sum_xy': sum_xy,
            'a': a,
            'b': b,
            'r': r,
            'x\'': x_prime,
            'y\'': y_prime
        }
        
    def calculate_x_prime(self, y_value):
        if not self.data_2var or len(self.data_2var) < 2:
            return 0
        
        stats = self.calculate_2var_statistics()
        
        # Using the regression equation: y = a + bx
        # x = (y - a) / b
        if stats['b'] == 0:  # Avoid division by zero
            return 0
        
        return (y_value - stats['a']) / stats['b']

    def calculate_y_prime(self, x_value):
        if not self.data_2var or len(self.data_2var) < 2:
            return 0
        
        stats = self.calculate_2var_statistics()
        
        # Using the regression equation: y = a + bx
        return stats['a'] + stats['b'] * x_value