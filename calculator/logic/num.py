from dataclasses import dataclass, field
import math
from typing import Dict, List, Tuple, Optional, Any

@dataclass
class NumberTheoryResults:
    # Single value results (n-dependent)
    factorization: Optional[str] = None               # Fac
    divisor_count: Optional[int] = None               # τ(n)
    divisor_sum: Optional[int] = None                 # σ(n)
    mobius: Optional[int] = None                      # μ(n)
    radical: Optional[int] = None                     # rad(n)
    totient: Optional[int] = None                     # φ(n)
    carmichael: Optional[int] = None                  # λ(n)
    is_prime: Optional[bool] = None                   # Prm(n)
    
    # Two-number results (n,m-dependent)
    gcd: Optional[int] = None                         # GCD(n,m)
    lcm: Optional[int] = None                         # LCM(n,m)
    bezout: Optional[Tuple[int, int]] = None          # Bezout(n,m) -> (x,y)
    modular_inverse: Optional[int] = None             # Inv(n mod m)
    order: Optional[int] = None                       # Ord(n mod m)
    is_generator: Optional[bool] = None               # Gen(n mod m)
    
    # m-dependent results
    quadratic_residues: Optional[List[int]] = None    # QR(m)
    
    # a,n,m-dependent results
    legendre_symbol: Optional[int] = None             # (a/p)
    jacobi_symbol: Optional[int] = None               # (a/n)
    discrete_log: Optional[int] = None                # log_n(a) mod m
    
    # Special functions
    pisano_period: Optional[int] = None               # Period of Fibonacci mod m
    knodel_check: Optional[bool] = None               # Knödel check
    cubic_classes: Optional[int] = None               # CubCls(m)

class NumberTheoryManager:
    def __init__(self):
        self.in_data_entry = False
        self.n_value = None
        self.m_value = None  # modulus
        self.a_value = None  # optional
        self.current_field = "n"
        self.current_value = ""
        
        self.results = NumberTheoryResults()
        
    def reset_results(self):
        self.results = NumberTheoryResults()
    
    def start_data_entry(self, default_mod=None):
        self.in_data_entry = True
        self.current_field = "n"
        self.current_value = ""
        
        # Use default modulus if provided
        if default_mod:
            self.m_value = default_mod
        
        # Show existing n value if already set
        if self.n_value is not None:
            return True, f"n={self.n_value}"
        
        # Return success and the prompt to display
        return True, "n="
    
    def update_current_value(self, value_str):
        value_str = value_str.replace("<u>", "").replace("</u>", "")
        self.current_value = value_str
        
        try:
            # Handle empty input separately
            if not value_str:
                if self.current_field == "a":  # a is optional
                    self.a_value = None
                    return True, ""
                else:  # n and m are required
                    return False, f"{self.current_field} is required"
                
            if '.' in value_str:
                return False, f"{self.current_field} must be an integer"
            
            # Convert to integer
            value = int(value_str)
            
            # Apply constraints based on field
            if self.current_field == "n":
                if value <= 0:
                    return False, "n must be a natural number"
                self.n_value = value
            
            elif self.current_field == "m":
                if value < 2:
                    return False, "m must be ≥ 2"
                self.m_value = value
            
            elif self.current_field == "a":
                # a can be any integer (ℤ)
                self.a_value = value
                
            return True, ""
    
        except ValueError:
            return False, f"Invalid input for {self.current_field}"
    
    def navigate_up(self):
        if not self.in_data_entry:
            return False, ""
        
        # Save current value before navigating
        if hasattr(self, 'current_value') and self.current_value:
            self.update_current_value(self.current_value)
        
        # Move to previous field
        if self.current_field == "n":
            self.current_field = "a"
        elif self.current_field == "m":
            self.current_field = "n"
        elif self.current_field == "a":
            self.current_field = "m"
        
        # Build prompt based on current field
        value = ""
        if self.current_field == "n" and self.n_value is not None:
            value = str(self.n_value)
        elif self.current_field == "m" and self.m_value is not None:
            value = str(self.m_value)
        elif self.current_field == "a" and self.a_value is not None:
            value = str(self.a_value)
        
        self.current_value = ""
        return True, f"{self.current_field}={value}"
    
    def navigate_down(self):
        if not self.in_data_entry:
            return False, ""
        
        # Save current value before navigating
        if hasattr(self, 'current_value') and self.current_value:
            self.update_current_value(self.current_value)
        
        # Cannot proceed from n without a value
        if self.current_field == "n" and self.n_value is None and not self.current_value:
            return False, "n="
        
        # Move to next field
        if self.current_field == "n":
            self.current_field = "m"
        elif self.current_field == "m":
            self.current_field = "a"
        elif self.current_field == "a":
            self.current_field = "n"
        
        # Build prompt based on current field
        value = ""
        if self.current_field == "n" and self.n_value is not None:
            value = str(self.n_value)
        elif self.current_field == "m" and self.m_value is not None:
            value = str(self.m_value)
        elif self.current_field == "a" and self.a_value is not None:
            value = str(self.a_value)
        
        self.current_value = ""
        return True, f"{self.current_field}={value}"
    
    def get_current_prompt(self):
        if not self.in_data_entry:
            return False, ""
            
        value = ""
        if self.current_field == "n" and self.n_value is not None:
            value = str(self.n_value)
        elif self.current_field == "m" and self.m_value is not None:
            value = str(self.m_value)
        elif self.current_field == "a" and self.a_value is not None:
            value = str(self.a_value)
            
        return True, f"{self.current_field}={value}"
    
    def clear_current_field(self):
        if not self.in_data_entry:
            return False, ""
        
        # Check if current field already has a value to clear
        if self.current_field == "n" and self.n_value is not None:
            self.n_value = None
            return True, "n="
        elif self.current_field == "m" and self.m_value is not None:
            self.m_value = None
            return True, "m="
        elif self.current_field == "a" and self.a_value is not None:
            self.a_value = None
            return True, "a="
        
        # If we get here, the field is already empty, so exit data entry mode
        self.in_data_entry = False
        return False, "0"  # Return 0 as default calculator display
    
    def clear_all_data(self):        
        self.n_value = None
        self.m_value = None
        self.a_value = None
        
        if self.in_data_entry:
            self.in_data_entry = False

        self.reset_results()
    
    def calculate_all(self):
        # Clear previous results
        self.reset_results()
        
        # Skip if n is not set
        if self.n_value is None:
            return
        
        # Calculate n-dependent functions
        self.calculate_n_dependent()
        
        # If m is set, calculate n,m-dependent and m-dependent functions
        if self.m_value is not None:
            self.calculate_m_dependent()
            self.calculate_nm_dependent()
            
        # If a is set, calculate a,n,m-dependent functions
        if self.a_value is not None and self.m_value is not None:
            self.calculate_anm_dependent()
    
    # Helper methods for calculations
    def is_prime(self, num):
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True  
    
    def calculate_n_dependent(self):
        n = self.n_value
        if n is None or n <= 0:
            return
        
        # Special case for n=1
        if n == 1:
            self.results.factorization = "1"
            self.results.is_prime = False
            self.results.divisor_count = 1
            self.results.divisor_sum = 1
            self.results.mobius = 1
            self.results.radical = 1
            self.results.totient = 1
            self.results.carmichael = 1
            return
        
        # Calculate prime factorization (Fac)
        factors = []
        prime_powers = {}  # Store prime factors and their exponents
        i = 2
        num = n
        while i * i <= num:
            if num % i:
                i += 1
            else:
                count = 0
                while num % i == 0:
                    num //= i
                    count += 1
                prime_powers[i] = count
                if count > 1:
                    superscript = str(count).translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
                    factors.append(f"{i}{superscript}")
                else:
                    factors.append(f"{i}")
        if num > 1:
            prime_powers[num] = 1
            factors.append(f"{num}")        
        self.results.factorization = " · ".join(factors)
        
        # Calculate primality of n
        self.results.is_prime = (len(factors) == 1 and all(c.isdigit() for c in factors[0]))
        
        # Calculate divisor count τ(n) = (e₁+1)(e₂+1)...(eₖ+1) where eᵢ are the exponents in the prime factorization
        divisor_count = 1
        for exponent in prime_powers.values():
            divisor_count *= (exponent + 1)
        self.results.divisor_count = divisor_count
        
        # Calculate divisor sum σ(n) = (p₁^(e₁+1)-1)/(p₁-1) × ... × (pₖ^(eₖ+1)-1)/(pₖ-1) where pᵢ are the prime factors and eᵢ their exponents
        divisor_sum = 1
        for prime, exponent in prime_powers.items():
            factor_sum = (pow(prime, exponent + 1) - 1) // (prime - 1)
            divisor_sum *= factor_sum
        self.results.divisor_sum = divisor_sum
        
        # Check if n is divisible by a square
        has_square_factor = any(exponent > 1 for exponent in prime_powers.values())
        if has_square_factor:
            self.results.mobius = 0
        else:
            num_prime_factors = len(prime_powers)
            self.results.mobius = -1 if num_prime_factors % 2 == 1 else 1
            
        # Calculate radical rad(n) = p₁ × p₂ × ... × pₖ where pᵢ are the distinct prime factors
        self.results.radical = 1
        for prime in prime_powers.keys():
            self.results.radical *= prime
            
        # Calculate totient φ(n) = n × (1 - 1/p₁) × (1 - 1/p₂) × ... × (1 - 1/pₖ)
        totient = n
        for prime in prime_powers.keys():
            totient *= (prime - 1) / prime
        self.results.totient = int(totient)
        
        # Calculate Carmichael function λ(n)
        def lcm(a, b):
            return a * b // math.gcd(a, b)
        carmichael_values = []
        for prime, exponent in prime_powers.items():
            if prime == 2 and exponent >= 3:
                carmichael_values.append(2**(exponent-2))
            elif prime == 2 and exponent == 2:
                carmichael_values.append(2)
            elif prime == 2 and exponent == 1:
                carmichael_values.append(1)
            else:
                carmichael_values.append((prime - 1) * prime**(exponent - 1))
        result = 1
        for val in carmichael_values:
            result = lcm(result, val)
        self.results.carmichael = result
        
        # Calculate Knödel check
        if self.results.is_prime:
            self.results.knodel_check = True
            return
        for a in range(2, n):
            if math.gcd(a, n) == 1:
                if pow(a, (n - 1), n) != 1:
                    self.results.knodel_check = False
                    return
        self.results.knodel_check = True
    
    def calculate_m_dependent(self):
        m = self.m_value
        if m is None or m <= 1:
            return
        
        # Calculate quadratic residues q mod m (QR) where q ≡ x² (mod m) for some x
        qr_set = set()
        for x in range(m):
            residue = (x * x) % m
            qr_set.add(residue)
        qr_list = sorted(qr_set)
        self.results.quadratic_residues = qr_list
        
        # Calculate Pisano period for Fibonacci mod m
        if m <= 0:
            self.results.pisano_period = None
            return
        if m == 1:
            self.results.pisano_period = 1
            return
        a, b = 0, 1
        period = 0
        while True:
            period += 1
            a, b = b, (a + b) % m
            if a == 0 and b == 1:
                break
            if period > m * m:
                self.results.pisano_period = None
                return
        self.results.pisano_period = period
        
        # Calculate cubic classes (CubCls) for m -- it's complex enough to break it out into its own function
        self.results.cubic_classes = self.calculate_cubic_classes(m)
    
    def calculate_nm_dependent(self):
        n = self.n_value
        m = self.m_value
        
        if n is None or m is None or n <= 0 or m <= 1:
            return
            
        # Calculate GCD(n, m)
        self.results.gcd = math.gcd(n, m)
        
        # Calculate LCM(n, m)
        self.results.lcm = (n * m) // self.results.gcd
        
        # Calculate Bezout coefficients - Find x, y where nx + my = gcd(n,m) using Extended Euclidean Algorithm
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            else:
                g, x, y = extended_gcd(b % a, a)
                return g, y - (b // a) * x, x        
        gcd, x, y = extended_gcd(n, m)
        if x != 0:
            k = round(x * gcd / m)
            new_x = x - k * (m // gcd)
            new_y = y + k * (n // gcd)
            if abs(new_x) + abs(new_y) < abs(x) + abs(y):
                x, y = new_x, new_y        
        self.results.bezout = (x, y)
        
        # Calculate modular inverse of n mod m - only exists if gcd(n, m) = 1
        if self.results.gcd == 1:
            # Ensure x is positive
            inv = x % m
            self.results.modular_inverse = inv
        else:
            self.results.modular_inverse = None
            
        if self.results.gcd == 1:
            # Calculate order of n in the multiplicative group mod m
            order = 1
            value = n % m
            while value != 1:
                value = (value * n) % m
                order += 1
                if order > m:
                    self.results.order = None
                    break
            else:
                self.results.order = order
            
            # Calculate if n is a generator
            phi_m = m
            i = 2
            temp_m = m
            while i * i <= temp_m:
                if temp_m % i == 0:
                    phi_m = phi_m // i * (i - 1)
                    while temp_m % i == 0:
                        temp_m //= i
                i += 1
            if temp_m > 1:
                phi_m = phi_m // temp_m * (temp_m - 1)
            if self.results.order is not None:
                self.results.is_generator = (self.results.order == phi_m)
            else:
                self.results.is_generator = False
        else:
            self.results.order = None
            self.results.is_generator = False
            
        # Calculate Legendre Symbol (n/m)              
        if not self.is_prime(m):
            self.results.legendre_symbol = None
            return
        if n % m == 0:
            self.results.legendre_symbol = 0
            return
        exponent = (m - 1) // 2
        result = pow(n, exponent, m)
        if result == m - 1:
            self.results.legendre_symbol = -1
        else:
            self.results.legendre_symbol = result
            
        # Calculate Jacobi Symbol (a/n)
        if m % 2 == 0 or m < 3:
            self.results.jacobi_symbol = None
            return
        def jacobi(n, m):
            n = n % m
            if n == 0:
                return 0 if m > 1 else 1
            if n == 1:
                return 1
            e = 0
            n1 = n
            while n1 % 2 == 0:
                e += 1
                n1 //= 2
            if e % 2 == 0:
                s = 1
            else:
                if m % 8 in [1, 7]:
                    s = 1
                else:
                    s = -1
            if n1 == 1:
                return s
            if m % 4 == 3 and n1 % 4 == 3:
                s = -s
            return s * jacobi(m % n1, n1)
        self.results.jacobi_symbol = jacobi(n, m)        
    
    def calculate_anm_dependent(self):
        a = self.a_value
        n = self.n_value
        m = self.m_value
        
        if a is None or n is None or m is None:
            return
            
        # Ensure values are within proper ranges
        a = a % m
        n = n % m
        
        # Special cases
        if a == 0:
            self.results.discrete_log = 0 if n == 0 else None
            return
        if n == 0:
            self.results.discrete_log = None
            return
        if n == 1:
            self.results.discrete_log = 0 if a == 1 else None
            return
            
        # We need gcd(n,m) = 1 for discrete log to be well-defined
        if math.gcd(n, m) != 1:
            # If gcd(n,m) > 1 but it doesn't divide a, no solution exists
            if a % math.gcd(n, m) != 0:
                self.results.discrete_log = None
                return
            # Otherwise, it's a more complex case - we'll return None for simplicity
            self.results.discrete_log = None
            return
        
        # Implement Baby-step Giant-step algorithm
        
        # Compute N = ceiling(sqrt(m))
        N = int(math.ceil(math.sqrt(m)))
        
        # Baby steps: Compute a·n^j mod m for j = 0,1,2,...,N-1
        baby_steps = {}
        for j in range(N):
            # Calculate a * n^j mod m
            value = (a * pow(n, j, m)) % m
            baby_steps[value] = j        
        # Compute n^(-N) mod m using modular multiplicative inverse. Since gcd(n,m) = 1, we can use FLT if m is prime, or extended Euclidean algorithm otherwise
        n_inv = pow(n, m - 2, m) if self.is_prime(m) else pow(n, -1, m)
        c = pow(n_inv, N, m)
        
        # Giant steps: Compute n^(-N·i) mod m for i = 0,1,2,...,N
        value = 1
        for i in range(N + 1):
            # Check if this giant step matches any baby step
            if value in baby_steps:
                # If we find n^(-N·i) ≡ a·n^j (mod m), then x = N·i + j
                self.results.discrete_log = (i * N + baby_steps[value]) % m
                return
            # Update for next iteration: value = value * c % m
            value = (value * c) % m
        
        # If we get here, no solution was found
        self.results.discrete_log = None
    
    def calculate_cubic_classes(self, m):
        # For m=1, there's only one class (the zero form)
        if m == 1:
            return 1
        
        # Prime factorization of m
        factors = {}
        temp_m = m
        i = 2
        while i * i <= temp_m:
            if temp_m % i == 0:
                count = 0
                while temp_m % i == 0:
                    temp_m //= i
                    count += 1
                factors[i] = count
            i += 1
        if temp_m > 1:
            factors[temp_m] = 1
        
        # Result will be product of cubic classes for each prime power
        result = 1
        
        for p, k in factors.items():
            prime_power = p**k
            
            # Formula for p^k depends on p mod 9 and the exponent k
            if p == 2:
                # Special case for p=2
                if k == 1:
                    prime_result = 8
                else:
                    # For 2^k where k≥2
                    prime_result = 8 * (4**(k-1))
            elif p == 3:
                # Special case for p=3
                if k == 1:
                    prime_result = 24
                else:
                    # For 3^k where k≥2
                    prime_result = 24 * (9**(k-1))
            else:
                # For other primes p
                # The formula depends on p mod 9
                p_mod_9 = p % 9
                
                if p_mod_9 in [1, 8]:  # p ≡ 1 or 8 (mod 9)
                    base_count = (p-1)*(p+1)*p
                elif p_mod_9 in [2, 5]:  # p ≡ 2 or 5 (mod 9)
                    base_count = (p+1)*p*p
                elif p_mod_9 in [4, 7]:  # p ≡ 4 or 7 (mod 9)
                    base_count = (p-1)*p*p
                else:  # p ≡ 3 or 6 (mod 9)
                    base_count = p*p*p
                
                # For p^k, multiply by p^(2(k-1))
                prime_result = base_count * (p**(2*(k-1)))
            
            # Multiply into the total result
            result *= prime_result
        
        return result