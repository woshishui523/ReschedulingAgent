"""
迭代学习控制 (Iterative Learning Control, ILC) 算法
基于上一批次的控制率、输出量以及状态偏差量计算当前时刻的控制率
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import time


class ILCController:
    """迭代学习控制器"""

    def __init__(self, M: int = 16, N: int = 8, p: int = 2, m: int = 2):
        """
        初始化 ILC 控制器

        参数:
            M: 列车总数 (默认 16)
            N: 站台数量 (默认 8)
            p: 预测范围/批次数量 (默认 2)
            m: 控制范围 (默认 2)
        """
        self.M = M
        self.N = N
        self.p = p
        self.m = m

        # 权重参数
        self.q = 3  # 误差大小权重
        self.r = 1  # 控制率大小权重

        # 预计算矩阵 (性能优化)
        self._precomputed_matrices = {}

    def mod2(self, value: int, modulus: int) -> int:
        """
        MATLAB 风格的 mod 运算 (结果始终为正)

        参数:
            value: 输入值
            modulus: 模数

        返回:
            取模后的结果 (1-based indexing)
        """
        result = ((value - 1) % modulus) + 1
        return result

    def get_c_parameters(self, c: float) -> Tuple[float, float]:
        """
        根据客流参数 c 计算 c1 和 c2

        参数:
            c: 客流与停车时间关系参数

        返回:
            (c1, c2) 元组
        """
        c1 = -c / (1 - c)
        c2 = 1 / (1 - c)
        return c1, c2

    def build_system_matrices(self, c: float) -> Dict[str, np.ndarray]:
        """
        构建系统矩阵 A, B, G, F

        参数:
            c: 客流参数

        返回:
            包含 A, B, G, F 矩阵的字典
        """
        M, N, p, m = self.M, self.N, self.p, self.m
        c1, c2 = self.get_c_parameters(c)

        # 构建 A 矩阵 (M x M)
        A11 = np.diag(np.ones(M - N - 1), 1)
        A12 = np.zeros((M - N, N))
        A12[M - N - 1, 0] = 1  # Python 索引从 0 开始
        A21 = np.zeros((N, M - N))
        A21[N - 1, 0] = c2
        A22 = np.diag(c1 * np.ones(N)) + np.diag(c2 * np.ones(N - 1), 1)
        A = np.vstack([np.hstack([A11, A12]),
                       np.hstack([A21, A22])])

        # 构建 B 矩阵 (M x N)
        B1 = np.zeros((M - N, N))
        B2 = np.diag(c1 * np.ones(N))
        B = np.vstack([B1, B2])

        # 构建 G 矩阵 (p*M x m*N)
        G = np.zeros((p * M, m * N))
        for i in range(1, m + 1):
            for j in range(1, p - i + 2):  # p-i+1:-1:1 转换为 1-based
                row_start = (i - 1 + j - 1) * M
                row_end = (i - 1 + j) * M
                col_start = (i - 1) * N
                col_end = i * N
                G[row_start:row_end, col_start:col_end] = np.linalg.matrix_power(A, j - 1) @ B

        # 构建 F 矩阵
        F = A.copy()
        for i in range(2, p + 1):
            F = np.vstack([F, np.linalg.matrix_power(A, i)])

        return {'A': A, 'B': B, 'G': G, 'F': F}

    def build_weight_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        构建权重矩阵 Q 和 R

        返回:
            (Q, R) 元组
        """
        M, N, p, m = self.M, self.N, self.p, self.m
        q, r = self.q, self.r

        # 构建 Q 矩阵
        Q1 = np.concatenate([np.zeros(M - N), np.full(N, q)])
        Q = np.diag(np.tile(Q1, p))

        # 构建 R 矩阵
        R = r * np.eye(m * N)

        return Q, R

    def compute_control_gain(self, c: float) -> np.ndarray:
        """
        预计算控制增益矩阵 H1

        参数:
            c: 客流参数

        返回:
            H1 增益矩阵
        """
        matrices = self.build_system_matrices(c)
        G = matrices['G']

        Q, R = self.build_weight_matrices()

        # 计算 H = inv(G'*Q*G + R) * G' * Q
        try:
            H = np.linalg.inv(G.T @ Q @ G + R) @ G.T @ Q
        except np.linalg.LinAlgError:
            # 如果矩阵不可逆，使用伪逆
            H = np.linalg.pinv(G.T @ Q @ G + R) @ G.T @ Q

        # 提取 H1 - 取前 N 行（对应第一个控制步）
        H1 = H[:self.N, :]

        return H1

    def extract_state_vector(self,
                             train_num: int,
                             platform_num: int,
                             time_schedule: Dict,
                             is_first_circle: bool) -> np.ndarray:
        """
        从时间调度表中提取状态向量 Xk

        参数:
            train_num: 当前列车序号 Tnum
            platform_num: 当前站台序号 Pnum
            time_schedule: 时间调度表 (包含 TimeError 等信息)
            is_first_circle: 是否为第一圈

        返回:
            状态向量 Xk (M维)
        """
        M, N = self.M, self.N
        Tr_Cir = time_schedule.get('TrCir', {})
        TimeError = time_schedule.get('TimeError', {})

        tr_cir_current = Tr_Cir.get(train_num, 0)

        Xk = []

        if is_first_circle:
            # 第一部分：列车 M 到 N+1
            for i in range(M, N, -1):
                trnum = self.mod2(train_num - i + N - 1, M)
                station_idx = platform_num + N * tr_cir_current + 1
                error = TimeError.get((trnum, station_idx), 0)
                Xk.append(error)

            # 第二部分：列车 N 到 1
            j = 0
            for i in range(N, 0, -1):
                trnum = self.mod2(train_num - i + N - 1, M)
                plnum = self.mod2(platform_num - j + 1, N)
                station_idx = plnum + N * tr_cir_current
                error = TimeError.get((trnum, station_idx), 0)
                Xk.append(error)
                j += 1
        else:
            # 非第一圈的逻辑类似，但索引不同
            for i in range(M, N, -1):
                trnum = self.mod2(train_num - i + N - 1, M)
                station_idx = platform_num + N * tr_cir_current
                error = TimeError.get((trnum, station_idx), 0)
                Xk.append(error)

            j = 0
            for i in range(N, 0, -1):
                trnum = self.mod2(train_num - i + N - 1, M)
                plnum = self.mod2(platform_num - j + 1, N)
                station_idx = plnum + N * tr_cir_current
                error = TimeError.get((trnum, station_idx), 0)
                Xk.append(error)
                j += 1

        return np.array(Xk).reshape(-1, 1)

    def extract_previous_state(self,
                               train_num: int,
                               platform_num: int,
                               time_schedule: Dict) -> np.ndarray:
        """
        提取上一批次的状态向量 Xk1

        参数:
            train_num: 当前列车序号
            platform_num: 当前站台序号
            time_schedule: 时间调度表

        返回:
            上一批次状态向量 Xk1 (M维)
        """
        M, N = self.M, self.N
        Tr_Cir = time_schedule.get('TrCir', {})
        TimeError = time_schedule.get('TimeError', {})

        tr_cir_current = Tr_Cir.get(train_num, 0)
        tr_cir_previous = tr_cir_current - 1

        Xk1 = []

        # 第一部分：列车 M 到 N+1
        for i in range(M, N, -1):
            trnum = self.mod2(train_num - i + N - 1, M)
            station_idx = platform_num + N * tr_cir_previous
            error = TimeError.get((trnum, station_idx), 0)
            Xk1.append(error)

        # 第二部分：列车 N 到 1
        j = 0
        for i in range(N, 0, -1):
            trnum = self.mod2(train_num - i + N - 1, M)
            plnum = self.mod2(platform_num - j + 1, N)
            station_idx = plnum + N * tr_cir_previous
            error = TimeError.get((trnum, station_idx), 0)
            Xk1.append(error)
            j += 1

        return np.array(Xk1).reshape(-1, 1)

    def extract_previous_control(self,
                                 train_num: int,
                                 platform_num: int,
                                 time_schedule: Dict) -> np.ndarray:
        """
        提取上一批次的控制率 uik1

        参数:
            train_num: 当前列车序号
            platform_num: 当前站台序号
            time_schedule: 时间调度表

        返回:
            上一批次控制率 uik1 (N维)
        """
        N = self.N
        Tr_Cir = time_schedule.get('TrCir', {})
        TimeUk = time_schedule.get('TimeUk', {})

        tr_cir_previous = Tr_Cir.get(train_num, 0) - 1

        uik1 = []
        j = 1
        for i in range(N - 1, -1, -1):
            trnum = self.mod2(train_num - i + N - 1, self.M)
            plnum = self.mod2(platform_num - j + 1, N)
            station_idx = plnum + N * tr_cir_previous
            uk = TimeUk.get((trnum, station_idx), 0)
            uik1.append(uk)
            j += 1

        return np.array(uik1).reshape(-1, 1)

    def extract_prediction_horizon(self,
                                   train_num: int,
                                   platform_num: int,
                                   time_schedule: Dict) -> np.ndarray:
        """
        提取预测范围 p 内的所有状态向量 yP_k1

        参数:
            train_num: 当前列车序号
            platform_num: 当前站台序号
            time_schedule: 时间调度表

        返回:
            预测状态向量 yP_k1 (p*M 维)
        """
        M, N, p = self.M, self.N, self.p
        Tr_Cir = time_schedule.get('TrCir', {})
        TimeError = time_schedule.get('TimeError', {})

        tr_cir_previous = Tr_Cir.get(train_num, 0) - 1

        yP_k1 = []

        for z in range(1, p + 1):
            Tnump = self.mod2(train_num + z, M)

            # 第一部分：列车 M 到 N+1
            for i in range(M, N, -1):
                trnum = self.mod2(Tnump - i, M)
                station_idx = platform_num + N * tr_cir_previous
                error = TimeError.get((trnum, station_idx), 0)
                yP_k1.append(error)

            # 第二部分：列车 N 到 1
            j = 0
            for i in range(N, 0, -1):
                trnum = self.mod2(Tnump - i, M)
                plnum = self.mod2(platform_num - j, N)
                station_idx = plnum + N * tr_cir_previous
                error = TimeError.get((trnum, station_idx), 0)
                yP_k1.append(error)
                j += 1

        return np.array(yP_k1).reshape(-1, 1)

    def compute_control(self,
                       train_num: int,
                       platform_num: int,
                       time_schedule: Dict,
                       c: float = 0.4) -> Dict:
        """
        计算当前时刻的控制率

        参数:
            train_num: 当前列车序号 Tnum
            platform_num: 当前站台序号 Pnum
            time_schedule: 时间调度表
            c: 客流与停车时间关系参数

        返回:
            包含控制结果的字典
        """
        start_time = time.time()

        M, N = self.M, self.N
        Tr_Cir = time_schedule.get('TrCir', {})

        # 判断是否为第一圈
        is_first_circle = (Tr_Cir.get(train_num, 0) == 0)

        # 提取状态向量
        Xk = self.extract_state_vector(train_num, platform_num, time_schedule, is_first_circle)

        if is_first_circle:
            # 第一圈：没有历史数据
            Xk1 = np.zeros((M, 1))
            uik1 = np.zeros((N, 1))
            yP_k1 = np.zeros((self.p * M, 1))
        else:
            # 非第一圈：提取历史数据
            Xk1 = self.extract_previous_state(train_num, platform_num, time_schedule)
            uik1 = self.extract_previous_control(train_num, platform_num, time_schedule)
            yP_k1 = self.extract_prediction_horizon(train_num, platform_num, time_schedule)

        # 构建系统矩阵并计算控制增益
        H1 = self.compute_control_gain(c)

        # 计算状态偏差
        AXk = Xk - Xk1

        # 获取系统矩阵 F
        matrices = self.build_system_matrices(c)
        F = matrices['F']

        # 计算控制率: uik = uik1 + H1 * (yP_k1 + F * AXk)
        uik = uik1 + H1 @ (yP_k1 + F @ AXk)

        # 提取第一个控制量作为最终输出
        Uik = float(uik[0, 0])

        # 计算耗时
        elapsed_time = time.time() - start_time

        return {
            'Uik': Uik,
            'uik_full': uik.flatten().tolist(),
            'Xk': Xk.flatten().tolist(),
            'Xk1': Xk1.flatten().tolist(),
            'AXk': AXk.flatten().tolist(),
            'uik1': uik1.flatten().tolist(),
            'yP_k1': yP_k1.flatten().tolist(),
            'elapsed_time': elapsed_time,
            'is_first_circle': is_first_circle
        }


def ilc_compute_control(train_num: int,
                        platform_num: int,
                        time_schedule: Dict,
                        c: float = 0.4,
                        M: int = 16,
                        N: int = 8) -> Dict:
    """
    便捷函数：计算迭代学习控制率

    参数:
        train_num: 当前列车序号
        platform_num: 当前站台序号
        time_schedule: 时间调度表 (包含 TrCir, TimeError, TimeUk)
        c: 客流参数
        M: 列车总数
        N: 站台数量

    返回:
        控制结果字典
    """
    controller = ILCController(M=M, N=N)
    return controller.compute_control(train_num, platform_num, time_schedule, c)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ILC 控制器测试")
    print("=" * 60)

    # 构造测试数据
    test_time_schedule = {
        'TrCir': {1: 1, 2: 1, 3: 1},
        'TimeError': {
            (1, 9): 5.0,   # 列车1在第9站晚点5分钟
            (2, 9): 3.0,   # 列车2在第9站晚点3分钟
            (1, 10): 4.0,
        },
        'TimeUk': {
            (1, 1): 0.5,
            (2, 1): 0.3,
        }
    }

    # 测试控制计算
    result = ilc_compute_control(
        train_num=1,
        platform_num=1,
        time_schedule=test_time_schedule,
        c=0.4,
        M=16,
        N=8
    )

    print(f"\n✅ 控制计算完成:")
    print(f"   控制量 Uik: {result['Uik']:.4f}")
    print(f"   是否第一圈: {result['is_first_circle']}")
    print(f"   计算耗时: {result['elapsed_time']:.6f} 秒")
    print(f"   状态向量维度: {len(result['Xk'])}")
    print(f"   完整控制向量: {result['uik_full'][:5]}...")  # 只显示前5个
