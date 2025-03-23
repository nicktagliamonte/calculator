import random
import math

def factorial(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("Factorial requires a non-negative integer")
    if n > 500:
        raise ValueError("Factorial too large to compute")
    return math.factorial(n)

def permutation(n, r):
    if not (isinstance(n, int) and isinstance(r, int)):
        raise ValueError("Permutation requires integers")
    if n < 0 or r < 0:
        raise ValueError("Permutation requires non-negative values")
    if r > n:
        raise ValueError("r cannot be greater than n in permutation")
    
    return math.factorial(n) // math.factorial(n - r)

def combination(n, r):
    if not (isinstance(n, int) and isinstance(r, int)):
        raise ValueError("Combination requires integers")
    if n < 0 or r < 0:
        raise ValueError("Combination requires non-negative values")
    if r > n:
        raise ValueError("r cannot be greater than n in combination")
    
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))

def rand(seed=None):
    if seed is not None and seed != 0:
        random.seed(int(seed))
    return random.random()

def randi(min_val=0, max_val=100, seed=None):
    if seed is not None and seed != 0:
        random.seed(int(seed))
    return random.randint(int(min_val), int(max_val))