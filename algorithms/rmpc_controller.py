"""
鲁棒模型预测控制 (RMPC) 算法
基于LMI约束的最小化线性目标优化

功能：在LMI约束下最小化线性目标
参数：
    M: 系统状态维度
    N: 控制输入维度
    x_real: 实际状态向量
    control: 控制参数字典，包含ckd, d, ckpoint等
返回：
    u_real: 实际控制量
"""

import numpy as np
from scipy.linalg import inv
import cvxpy as cp


def lmi_solve(M, N, x_real, control):
    """
    在LMI约束下最小化线性目标

    参数:
        M: 系统状态维度
        N: 控制输入维度
        x_real: 实际状态向量 (M维)
        control: 控制参数字典
            - ckd: 乘客到达速率变化范围
            - d: 乘客到达速率与停站时间关系
            - ckpoint: 乘客到达速率中心点

    返回:
        u_real: 实际控制量 (N维)
    """

    # ==================== 已知变量 ====================
    # 修复：正确获取参数，如果 control 中没有则使用默认值
    d_param = control.get('ckd', 0) if isinstance(control, dict) else 0
    za = control.get('d', 0.2) if isinstance(control, dict) else 0.2
    lamda = control.get('ckpoint', 0.4) if isinstance(control, dict) else 0.4

    # 计算中间变量
    c1 = 0.5 * ((-za * (lamda + d_param) / (1 - za * (lamda + d_param))) +
                (-za * (lamda - d_param) / (1 - za * (lamda - d_param))))
    d1 = 0.5 * ((-za * (lamda - d_param) / (1 - za * (lamda - d_param))) -
                (-za * (lamda + d_param) / (1 - za * (lamda + d_param))))
    c2 = 0.5 * ((1 / (1 - za * (lamda - d_param))) +
                (1 / (1 - za * (lamda + d_param))))
    d2 = 0.5 * ((1 / (1 - za * (lamda + d_param))) -
                (1 / (1 - za * (lamda - d_param))))

    q = 10   # 目标函数中误差的权重
    r = 1    # 目标函数中控制量的权重

    # ==================== 构建系统矩阵 ====================
    # A矩阵 (M x M)
    A11 = np.diag(np.ones(M - N - 1), 1)
    A12 = np.zeros((M - N, N))
    A12[M - N - 1, 0] = 1  # Python索引从0开始
    A21 = np.zeros((N, M - N))
    A21[N - 1, 0] = c2
    A22 = np.diag(c1 * np.ones(N)) + np.diag(c2 * np.ones(N - 1), 1)
    A = np.vstack([np.hstack([A11, A12]),
                   np.hstack([A21, A22])])

    # B矩阵 (M x N)
    B1 = np.zeros((M - N, N))
    B2 = np.diag(c1 * np.ones(N))
    B = np.vstack([B1, B2])

    # C1矩阵 (M x M)
    C11 = np.zeros((M - N, M))
    C121 = np.zeros((N, M - N))
    C122 = np.diag(d1 * np.ones(N))
    C1 = np.vstack([C11, np.hstack([C121, C122])])

    # C2矩阵 (M x M)
    C21 = np.zeros((M - N, M))
    C221 = np.zeros((N, M - N))
    C222 = np.diag(d2 * np.ones(N - 1), 1)
    C2 = np.vstack([C21, np.hstack([C221, C222])])

    # C3矩阵 (N x N)
    C3 = np.diag(d1 * np.ones(N))

    # L矩阵 (M x N)
    L1 = np.zeros((M - N, N))
    L2 = np.diag(np.ones(N))
    L = np.vstack([L1, L2])

    # 权重矩阵
    Q = np.diag(q * np.ones(M))
    Q[0:N, 0:N] = np.diag(0.01 * q * np.ones(N))
    R = np.diag(r * np.ones(N))

    I1 = np.eye(M)
    IM = np.eye(M)
    IN = np.eye(N)
    P = np.eye(M)
    beta = P + Q

    # 当前状态
    X = x_real

    # 控制量上下限
    U1 = 20  # 上限
    U2 = 20  # 下限
    Ul = (U1/2 + U2/2) - abs(U1/2 - U2/2)

    # ==================== CVXPY优化问题 ====================
    # 定义优化变量
    a_var = cp.Variable(1, name='a')
    K = cp.Variable((N, M), name='K')
    Z = cp.Variable((M, M), name='Z')
    Y = cp.Variable((N, M), name='Y')
    H = cp.Variable((N, N), name='H')

    theta1_var = cp.Variable(1, name='theta1')
    theta2_var = cp.Variable(1, name='theta2')
    theta3_var = cp.Variable(1, name='theta3')

    theta1 = a_var * theta1_var
    theta2 = a_var * theta2_var
    theta3 = a_var * theta3_var

    # ==================== LMI约束 ====================
    constraints = []

    # 构建零填充辅助函数，将 N×M 矩阵填充为 M×M
    def pad_nm_to_mm(expr_nm):
        """将 N×M 的 CVXPY 表达式上下填充零，变为 M×M"""
        top = cp.reshape(expr_nm, (N, M))
        bottom = np.zeros((M - N, M))
        return cp.vstack([top, bottom])

    def pad_nn_to_mm(expr_nn):
        """将 N×N 的 CVXPY 表达式四周填充零，变为 M×M"""
        inner = cp.reshape(expr_nn, (N, N))
        top = cp.hstack([inner, np.zeros((N, M - N))])
        bottom = np.zeros((M - N, M))
        return cp.vstack([top, bottom])

    block_11 = -Z
    block_12 = A @ Z + B @ Y
    block_13 = C1 @ Z
    block_14 = C2 @ Z
    block_15 = pad_nm_to_mm(-C3 @ Y)
    block_16 = Z
    block_17 = pad_nm_to_mm(-Y)

    # 第二行
    block_22 = -Z + theta1 * (I1 @ I1.T) + theta2 * (I1 @ I1.T) + theta3 * (L @ L.T)

    # 第三行
    block_33 = -theta1 * IM

    # 第四行
    block_44 = -theta2 * IM

    # 第五行
    block_55 = pad_nn_to_mm(-theta3 * IN)

    # 第六行
    block_66 = -a_var * inv(Q)

    # 第七行
    block_77 = pad_nn_to_mm(-a_var * inv(R))

    # 构建完整的LMI矩阵 (所有块均为 M×M，整体为 7M×7M)
    # 使用显式零矩阵代替 None，避免 CVXPY 1.9+ 的 bmat 兼容性问题
    Z_MM = np.zeros((M, M))
    lmi_matrix_1 = cp.bmat([
        [block_11,     block_12,       block_13,       block_14,       block_15,       block_16,       block_17],
        [Z_MM,         block_22,       Z_MM,           Z_MM,           Z_MM,           Z_MM,           Z_MM],
        [Z_MM,         Z_MM,           block_33,       Z_MM,           Z_MM,           Z_MM,           Z_MM],
        [Z_MM,         Z_MM,           Z_MM,           block_44,       Z_MM,           Z_MM,           Z_MM],
        [block_15.T,   Z_MM,           Z_MM,           Z_MM,           block_55,       Z_MM,           Z_MM],
        [Z_MM,         Z_MM,           Z_MM,           Z_MM,           Z_MM,           block_66,       Z_MM],
        [block_17.T,   Z_MM,           Z_MM,           Z_MM,           Z_MM,           Z_MM,           block_77]
    ])

    constraints.append(lmi_matrix_1 << 0)

    # 矩阵2: 状态相关约束
    # 修复：确保X向量正确转换为CVXPY兼容的列向量（提前转换）
    if isinstance(X, np.ndarray):
        X_col = X.reshape(M, 1)
    else:
        X_col = cp.reshape(X, (M, 1))
    
    lmi_matrix_2 = cp.bmat([
        [Z,             X_col],
        [X_col.T,       np.eye(1)]
    ])
    constraints.append(lmi_matrix_2 >> 0)

    # 矩阵3: H矩阵约束
    lmi_matrix_3 = cp.bmat([
        [H,             Y],
        [Y.T,           Z]
    ])
    constraints.append(lmi_matrix_3 >> 0)

    # 变量非负约束 (CVXPY 使用 >= 表示半定约束)
    constraints.append(a_var >= 0)
    constraints.append(theta1_var >= 0)
    constraints.append(theta2_var >= 0)
    constraints.append(theta3_var >= 0)
    constraints.append(Z >> 0)
    constraints.append(H >> 0)

    # 控制量约束
    for i in range(N):
        constraints.append(Z[i, i] <= Ul**2)

    # ==================== 目标函数 ====================
    objective = cp.Minimize(a_var)

    # ==================== 求解优化问题 ====================
    prob = cp.Problem(objective, constraints)

    try:
        prob.solve(solver=cp.SCS, verbose=False)

        if prob.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
            raise ValueError(f"优化问题未收敛，状态: {prob.status}")

        # 提取结果
        a_opt = a_var.value
        Z_opt = Z.value
        Y_opt = Y.value

        # 计算增益矩阵 K = Y * Z^(-1)
        K_opt = Y_opt @ inv(Z_opt)

        # 计算控制量 U = K * X
        # 修复：使用之前已转换的X_col，避免重复转换
        U = K_opt @ X_col

        # 对控制量进行四舍五入（保留1位小数）
        u_real = np.round(U, 1)

        return u_real.flatten()

    except Exception as e:
        print(f"LMI求解失败: {e}")
        raise


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试参数
    M = 18  # 状态维度
    N = 14  # 控制维度

    # 随机生成状态向量
    x_real = np.random.randn(M)

    # 控制参数
    control = {
        'ckd': 0,
        'd': 0.2,
        'ckpoint': 0.4
    }

    # 调用LMI求解器
    u_result = lmi_solve(M, N, x_real, control)

    print("实际控制量 u_real:")
    print(u_result)
    print(f"控制量维度: {u_result.shape}")