import random

# Создание матрицы размером 10x10
def create_matrix(rows, cols):
    return [[random.randint(-50, 50) for _ in range(cols)] for _ in range(rows)]

# Сложение двух матриц
def add_matrices(matrix1, matrix2):
    return [[matrix1[i][j] + matrix2[i][j] for j in range(len(matrix1[0]))] for i in range(len(matrix1))]

# Создание двух матриц
matrix_1 = create_matrix(10, 10)
matrix_2 = create_matrix(10, 10)

# Сложение матриц
matrix_3 = add_matrices(matrix_1, matrix_2)

# Вывод матриц для проверки
print("Matrix 1:")
for row in matrix_1:
    print(row)

print("\nMatrix 2:")
for row in matrix_2:
    print(row)

print("\nMatrix 3 (Sum of Matrix 1 and Matrix 2):")
for row in matrix_3:
    print(row)
