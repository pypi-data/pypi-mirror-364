from .evaluator import evaluate
from .render import render_latex, render_type
from .expression import (
    Product,
    Power,
    Sum,
    Symbol,
    Numerical,
    FunctionCall,
    MathFunction,
    is_int_or_float,
)

import numpy as np
import math
import random

# Latin letters and their relative preferences
latin_chars = {
    "x": 1.0,
    "y": 0.9,
    "z": 0.8,
    "a": 0.8,
    "b": 0.8,
    "c": 0.7,
    "d": 0.6,
    "n": 0.5,
    "m": 0.5,
    "t": 0.5,
    "u": 0.4,
    "v": 0.4,
    "w": 0.4,
    "r": 0.4,
    "s": 0.4,
    "k": 0.3,
    "p": 0.3,
    "f": 0.2,
    "g": 0.2,
    "q": 0.1,
    "j": 0.1,
    "l": 0.1,
    "h": 0.1,
    "o": 0.01,
    "i": 0.001,
    "e": 0.001,  # discouraged due to special meaning
}

# Greek letters (lowercase)
greek_chars = {
    "α": 1.0,
    "β": 0.9,
    "γ": 0.7,
    "δ": 0.6,
    "ε": 0.5,
    "ζ": 0.4,
    "η": 0.4,
    "θ": 0.5,
    "ι": 0.3,
    "κ": 0.6,
    "λ": 0.7,
    "μ": 0.5,
    "ν": 0.3,
    "ξ": 0.2,
    "ο": 0.01,
    "π": 0.01,
    "ρ": 0.4,
    "σ": 0.5,
    "τ": 0.4,
    "υ": 0.3,
    "φ": 0.3,
    "χ": 0.2,
    "ψ": 0.1,
    "ω": 0.2,
}

# Hebrew characters
hebrew_chars = {
    "א": 1.0,
    "ב": 0.8,
    "ג": 0.6,
    "ד": 0.5,
    "ה": 0.4,
    "ו": 0.3,
    "ז": 0.3,
    "ח": 0.2,
    "ט": 0.1,
    "י": 0.1,
    "כ": 0.1,
    "ל": 0.1,
    "מ": 0.1,
    "נ": 0.1,
    "ס": 0.1,
    "ע": 0.05,
    "פ": 0.05,
    "צ": 0.05,
    "ק": 0.05,
    "ר": 0.05,
    "ש": 0.05,
    "ת": 0.05,
}

# Cyrillic characters
cyrillic_chars = {
    "а": 1.0,
    "б": 0.8,
    "в": 0.7,
    "г": 0.6,
    "д": 0.6,
    "е": 0.01,
    "ж": 0.4,
    "з": 0.3,
    "и": 0.3,
    "й": 0.3,
    "к": 0.6,
    "л": 0.4,
    "м": 0.5,
    "н": 0.5,
    "о": 0.01,
    "п": 0.5,
    "р": 0.3,
    "с": 0.3,
    "т": 0.3,
    "у": 0.2,
    "ф": 0.2,
    "х": 0.2,
    "ц": 0.2,
    "ч": 0.2,
    "ш": 0.1,
    "щ": 0.1,
    "ы": 0.1,
    "э": 0.05,
    "ю": 0.05,
    "я": 0.05,
}

# Script multipliers (adjust here for influence)
script_weights = {"latin": 1.0, "greek": 0.3, "hebrew": 0.05, "cyrillic": 0.05}


# Combine all characters with adjusted weights
def build_weighted_pool(taken: set[str]) -> list[tuple[str, float]]:
    pool = []

    def add_characters(char_dict: dict[str, float], multiplier: float):
        for ch, weight in char_dict.items():
            if ch not in taken:
                pool.append((ch, weight * multiplier))

    add_characters(latin_chars, script_weights["latin"])
    add_characters(greek_chars, script_weights["greek"])
    add_characters(hebrew_chars, script_weights["hebrew"])
    add_characters(cyrillic_chars, script_weights["cyrillic"])

    return pool


# Main function
def random_variable_name(taken: set[str]) -> str:
    pool = build_weighted_pool(taken)
    if not pool:
        raise ValueError("No available variable names not already taken.")
    variables, weights = zip(*pool)
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    return random.choices(variables, weights=normalized_weights, k=1)[0]


def generate_number(
    mean=5,
    std=3,
    exponent=1.5,
    negative_probability=0.7,
    decimal_probability=0.7,
    allow_negative=True,
    allow_zero=True,
    require_integer=False,
):
    """Generates a random number with certain constraints."""
    while True:
        # Step 1: Generate magnitude using a power law
        magnitude = abs(np.random.normal(mean, std)) ** exponent

        # Step 2: Randomly make it negative or positive
        sign = 1
        if allow_negative and np.random.rand() >= negative_probability:
            sign = -1
        value = magnitude * sign

        # Step 3: Round to a certain number of decimal places
        if require_integer:
            decimal_places = 0
        else:
            # Bias toward fewer decimal places
            decimal_places = np.random.geometric(p=decimal_probability) - 1

        rounded = round(value, decimal_places)

        # Step 4: Convert to int if possible
        if decimal_places == 0 or rounded == int(rounded):
            result = int(rounded)
        else:
            result = rounded

        # Step 5: Validate against constraints
        if not allow_zero and result == 0:
            continue  # Retry if zero is not allowed

        return result


def generate_random_expression(
    max_depth=4,
    _depth=0,
    mean=5,
    std=3,
    gen_exponent=1.5,
    negative_probability=0.7,
    decimal_probability=0.7,
    allow_negative=True,
    allow_zero=True,
    require_integer=False,
):
    """
    Generates a random mathematical expression using Sum, Product, Power, and generate_number().
    Uses a while loop for building up the structure.
    """
    # Make it less likely to go deeper as we recurse
    if _depth >= max_depth or random.random() < (0.3 + _depth * 0.15):
        return generate_number(
            mean=mean,
            std=std,
            exponent=gen_exponent,
            negative_probability=negative_probability,
            decimal_probability=decimal_probability,
            allow_negative=allow_negative,
            allow_zero=allow_zero,
            require_integer=require_integer,
        )

    expr_type = random.choices(
        ["sum", "product", "power", "number"],
        weights=[4, 3, 1, 2],  # Tune these for how often each occurs
        k=1,
    )[0]

    # Pass constraints down the recursion
    recursive_args = {
        "max_depth": max_depth,
        "_depth": _depth + 1,
        "mean": mean,
        "std": std,
        "gen_exponent": gen_exponent,
        "negative_probability": negative_probability,
        "decimal_probability": decimal_probability,
        "allow_negative": allow_negative,
        "allow_zero": allow_zero,
        "require_integer": require_integer,
    }

    if expr_type == "sum":
        terms = [
            generate_random_expression(**recursive_args)
            for _ in range(random.randint(2, 3))
        ]
        return Sum(terms)
    elif expr_type == "product":
        factors = [
            generate_random_expression(**recursive_args)
            for _ in range(random.randint(2, 3))
        ]
        return Product(factors)
    elif expr_type == "power":
        # Generate the base first, with no initial constraints.
        base = generate_random_expression(**recursive_args)

        # Evaluate the base to determine the constraints for the exponent.
        evaluated_base, _ = evaluate(base)

        exponent_args = recursive_args.copy()

        if isinstance(evaluated_base, (int, float)):
            if evaluated_base < 0:
                # Negative base requires an integer exponent to avoid complex numbers.
                exponent_args["require_integer"] = True
            elif evaluated_base == 0:
                # Zero base requires a non-negative exponent to avoid division by zero.
                exponent_args["allow_negative"] = False
        # If base is positive or not a number (e.g. an unevaluated expression),
        # we don't apply special constraints for this logic path.
        # A more robust solution might handle unevaluated expressions differently.

        exponent = generate_random_expression(**exponent_args)
        return Power(base, exponent)
    else:  # number
        return generate_number(
            mean=mean,
            std=std,
            exponent=gen_exponent,
            negative_probability=negative_probability,
            decimal_probability=decimal_probability,
            allow_negative=allow_negative,
            allow_zero=allow_zero,
            require_integer=require_integer,
        )


if __name__ == "__main__":
    # for i in range(100):
    #     print(generate_number())
    for i in range(10):
        expression = generate_random_expression()
        print("Expression: $$", render_latex(expression), "$$")
        print(render_type(expression))
        answer, context = evaluate(expression)
        context.render()
        print(f"Final answer: $\\boxed{{{render_latex(answer)}}}$")
