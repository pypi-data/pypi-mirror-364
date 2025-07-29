# tantheta/physics.py
from math import radians, sin, cos

def solve_kinematics(u=None, v=None, a=None, t=None, s=None):
    """
    Solves one variable from kinematic equations if others are provided.
    Supports: s = ut + 0.5at^2, v = u + at, v^2 = u^2 + 2as
    """
    if u is not None and a is not None and t is not None:
        s = u * t + 0.5 * a * t**2
        v = u + a * t
        return {"displacement": s, "final_velocity": v}
    return "Not enough info"

def convert_units(expression):
    if "km/hr to m/s" in expression:
        val = float(expression.split()[0])
        return round(val * 1000 / 3600, 3)
    return "Conversion not supported"

def projectile_motion(u, angle):
    angle_rad = radians(angle)
    t = 2 * u * sin(angle_rad) / 9.8
    h = (u ** 2) * (sin(angle_rad) ** 2) / (2 * 9.8)
    r = (u ** 2) * sin(2 * angle_rad) / 9.8
    return {"time_of_flight": round(t, 2), "max_height": round(h, 2), "range": round(r, 2)}


def lens_formula(u, v):
    f = (u * v) / (u + v)
    return round(f, 2)

