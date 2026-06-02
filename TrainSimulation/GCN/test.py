import numpy as np

# 创建三个示例矩阵
matrix1 = np.array([[1, 2, 3],
                    [4, 5, 6]])

matrix2 = np.array([[7, 8, 9],
                    [10, 11, 12]])

matrix3 = np.array([[13, 14, 15],
                    [16, 17, 18]])

# 合并多个矩阵按行（垂直合并）
combined_matrix_row = np.concatenate((matrix1, matrix2, matrix3))

# 合并多个矩阵按列（水平合并）
combined_matrix_col = np.concatenate((matrix1, matrix2, matrix3), axis=1)

# 打印合并后的矩阵
x1 = np.linspace(0, 7, 8)
x2 = np.sort(np.tile(np.linspace(8, 15, 8), (1, 2)))[0]
x3 = np.tile(np.linspace(8, 15, 8), (1, 2))[0]
matrix1 = np.concatenate((x1, x2), axis=0)
print("按行合并的矩阵:")
print(combined_matrix_row)

print("\n按列合并的矩阵:")
print(combined_matrix_col)
