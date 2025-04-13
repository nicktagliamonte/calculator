class NumVarMenuManager:
    def __init__(self):
        self.active = False
        self.cursor_pos = 0
        self.results = None
        
        # Define the full menu text with all number theory functions
        self.menu_text = "Fac τ σ μ rad φ λ Prm GCD LCM Bzt Inv Ord Gen QR Leg Jac DLog Per Knd CbC"
        
        # Define valid cursor positions for each function
        self.valid_positions = [0, 4, 6, 8, 10, 14, 16, 18, 22, 26, 30, 34, 38, 42, 46, 49, 53, 57, 62, 66, 70]
        
        # Map functions to their display names for easier lookup
        self.function_map = {
            0: "Fac",     # Factorization
            4: "τ",       # Divisor count
            6: "σ",       # Divisor sum
            8: "μ",       # Möbius function
            10: "rad",    # Product of distinct primes
            14: "φ",      # Euler's totient
            16: "λ",      # Carmichael function
            18: "Prm",    # Primality test
            22: "GCD",    # Greatest common divisor
            26: "LCM",    # Least common multiple
            30: "Bzt",    # Bezout coefficients
            34: "Inv",    # Modular inverse
            38: "Ord",    # Order in multiplicative group
            42: "Gen",    # Generator check
            46: "QR",     # Quadratic residues
            49: "Leg",    # Legendre symbol
            53: "Jac",    # Jacobi symbol
            57: "DLog",   # Discrete logarithm
            62: "Per",    # Pisano period
            66: "Knd",    # Knödel check
            70: "CbC"     # Cubic classes
        }
        
        # Keep track of functions requiring different inputs
        self.n_dependent = [0, 4, 6, 8, 10, 14, 16, 18]  # Fac through Prm
        self.nm_dependent = [22, 26, 30, 34, 38, 42]    # GCD through Gen
        self.m_dependent = [46, 62, 70]                 # QR, Per, CbC
        self.anm_dependent = [49, 53, 57]               # Leg, Jac, DLog
        self.an_dependent = [66]                        # Knd
        
    def activate(self, num_manager):
        self.active = True
        self.cursor_pos = 0
        self.num_manager = num_manager
        
        # Calculate all applicable number theory functions
        num_manager.calculate_all()
        self.results = num_manager.results
        
        return self.menu_text, self.get_current_value()
    
    def navigate(self, direction):
        if not self.active:
            return None, None
        
        # Find current index in valid positions
        idx = self.valid_positions.index(self.cursor_pos) if self.cursor_pos in self.valid_positions else 0
        
        if direction == 'left':
            idx = (idx - 1) % len(self.valid_positions)
        else:  # right
            idx = (idx + 1) % len(self.valid_positions)
        
        self.cursor_pos = self.valid_positions[idx]
        return self.menu_text, self.get_current_value()
    
    def get_current_value(self):
        if not self.active or self.results is None:
            return None
            
        # Get function identifier from cursor position
        pos = self.cursor_pos
        if pos not in self.function_map:
            return None
            
        # Map cursor position to result value
        if pos == 0:  # Factorization
            return self.results.factorization
        elif pos == 4:  # Divisor count
            return self.results.divisor_count
        elif pos == 6:  # Divisor sum
            return self.results.divisor_sum
        elif pos == 8:  # Möbius function
            return self.results.mobius
        elif pos == 10:  # Radical
            return self.results.radical
        elif pos == 14:  # Totient
            return self.results.totient
        elif pos == 16:  # Carmichael
            return self.results.carmichael
        elif pos == 18:  # Primality
            return "Prime" if self.results.is_prime else "Composite" if self.results.is_prime is not None else None
        elif pos == 22:  # GCD
            return self.results.gcd
        elif pos == 26:  # LCM
            return self.results.lcm
        if pos == 30:  # Bezout coefficients
            if self.results.bezout:
                x, y = self.results.bezout
                n = self.num_manager.n_value
                m = self.num_manager.m_value
                gcd = self.results.gcd
                
                # Format as complete equation with coefficients clearly labeled
                return f"{n}⋅({x}) + {m}⋅({y}) = {gcd}"
            return None
        elif pos == 34:  # Modular inverse
            return self.results.modular_inverse
        elif pos == 38:  # Order
            return self.results.order
        elif pos == 42:  # Generator
            return "Yes" if self.results.is_generator else "No" if self.results.is_generator is not None else None
        elif pos == 46:  # Quadratic residues
            if self.results.quadratic_residues:
                return f"{{{','.join(map(str, self.results.quadratic_residues))}}}"
            return None
        elif pos == 49:  # Legendre symbol
            return self.results.legendre_symbol
        elif pos == 53:  # Jacobi symbol
            return self.results.jacobi_symbol
        elif pos == 57:  # Discrete log
            return self.results.discrete_log
        elif pos == 62:  # Pisano period
            return self.results.pisano_period
        elif pos == 66:  # Knödel check
            return "Yes" if self.results.knodel_check else "No" if self.results.knodel_check is not None else None
        elif pos == 70:  # Cubic classes
            return self.results.cubic_classes
        
        return None
        
    def deactivate(self):
        current_value = self.get_current_value()
        self.active = False
        return current_value
    
    def check_dependencies_met(self):
        if not self.active:
            return False
            
        pos = self.cursor_pos
        
        # Check dependencies for the current function
        if pos in self.n_dependent:
            return self.num_manager.n_value is not None
        elif pos in self.nm_dependent:
            return self.num_manager.n_value is not None and self.num_manager.m_value is not None
        elif pos in self.m_dependent:
            return self.num_manager.m_value is not None
        elif pos in self.anm_dependent:
            return (self.num_manager.a_value is not None and 
                   self.num_manager.n_value is not None and 
                   self.num_manager.m_value is not None)
        elif pos in self.an_dependent:
            return self.num_manager.a_value is not None and self.num_manager.n_value is not None
            
        return False