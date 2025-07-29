import re
from sympy import Matrix, lcm, symbols
from sympy.solvers.solveset import linsolve

def parse_formula(formula):
    elements = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    atom_counts = {}
    for elem, count in elements:
        atom_counts[elem] = atom_counts.get(elem, 0) + int(count or 1)
    return atom_counts

def parse_side(side):
    return [parse_formula(comp.strip()) for comp in side.split('+')]

def extract_elements(compounds):
    elements = set()
    for comp in compounds:
        elements.update(comp.keys())
    return sorted(elements)

def construct_matrix(lhs, rhs, elements):
    matrix = []
    for elem in elements:
        row = []
        for compound in lhs:
            row.append(compound.get(elem, 0))
        for compound in rhs:
            row.append(-compound.get(elem, 0))
        matrix.append(row)
    return Matrix(matrix)

def balance_equation(equation):
    lhs_str, rhs_str = equation.split('=')
    lhs = parse_side(lhs_str)
    rhs = parse_side(rhs_str)
    elements = extract_elements(lhs + rhs)

    mat = construct_matrix(lhs, rhs, elements)
    nullspace = mat.nullspace()

    if not nullspace:
        return "No solution found."

    coeffs = nullspace[0]
    lcm_val = lcm([term.q for term in coeffs])
    final_coeffs = [int(term * lcm_val) for term in coeffs]

    lhs_comps = lhs_str.split('+')
    rhs_comps = rhs_str.split('+')

    lhs_bal = ' + '.join(f"{final_coeffs[i]}{lhs_comps[i].strip()}" for i in range(len(lhs_comps)))
    rhs_bal = ' + '.join(f"{final_coeffs[i+len(lhs_comps)]}{rhs_comps[i].strip()}" for i in range(len(rhs_comps)))

    return f"{lhs_bal} = {rhs_bal}"



def ideal_gas_law(P=None, V=None, n=None, T=None, R=0.0821):
    """
    Solves for one missing variable in the ideal gas law equation: PV = nRT

    Parameters:
    - P: Pressure in atm
    - V: Volume in liters
    - n: Number of moles
    - T: Temperature in Kelvin
    - R: Ideal gas constant (default: 0.0821 L·atm/mol·K)

    Returns:
    - Calculated value of the missing parameter
    """
    if [P, V, n, T].count(None) != 1:
        raise ValueError("Exactly one of P, V, n, T must be None.")

    if P is None:
        return (n * R * T) / V
    elif V is None:
        return (n * R * T) / P
    elif n is None:
        return (P * V) / (R * T)
    elif T is None:
        return (P * V) / (n * R)
