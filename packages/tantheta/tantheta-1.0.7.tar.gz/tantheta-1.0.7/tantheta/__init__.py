# Core operations
from .core import add, subtract, multiply, divide

# Algebra module
from .algebra import (
    dot_product,
    cross_product,
    classify_conic,
    factor_expression,
    expand_expression,
    solve_linear_equation,
    solve_linear_system,
    is_polynomial,
    degree_of_polynomial,
)

# Calculus module
from .calculus import (
    differentiate,
    integration,
    find_limit,
    definite_integral,
    partial_derivative,
    second_derivative,
    taylor_series,
    find_critical_points,
)

# Probability module
from .probability import (
    nPr,
    nCr,
    basic_probability,
)

# Statistics module
from .stats import (
    mean,
    median,
    variance,
    standard_deviation,
)

# Trigonometry module
from .trigonometry import (
    solve_trig_equation,
    simplify_trig_expression,
    expand_trig_expression,
    factor_trig_expression,
    evaluate_trig_identity,
    verify_trig_identity,
    is_trig_identity,
)
from tantheta.linear_algebra import compute_determinant, compute_inverse, compute_rank, compute_eigenvalues
from tantheta.geometry import angle_between_lines, angle_between_vectors
from tantheta.plot import plot_expression
from tantheta.algebra import symbolic_gcd, symbolic_lcm

#Chemistry
from tantheta.chemistry import balance_equation, ideal_gas_law

# Physics module
from tantheta.physics import (
    solve_kinematics,
    projectile_motion,
    convert_units,
    lens_formula,
)

# Maths module
from tantheta.maths import (
    ap_nth_term,
    gp_sum,
    triangle_area,
    is_prime,
    prime_factors,
)
