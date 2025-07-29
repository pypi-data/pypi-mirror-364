from sympy import Matrix

def compute_determinant(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.det()

def compute_inverse(matrix_list):
    matrix = Matrix(matrix_list)
    if matrix.det() == 0:
        return "Matrix is singular; no inverse exists."
    return matrix.inv()

def compute_rank(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.rank()

def compute_eigenvalues(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.eigenvals()
