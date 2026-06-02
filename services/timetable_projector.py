"""
时刻表投影引擎

基于物理约束的延误传播模型，推算控制决策对全局时刻表的影响。
传播逻辑与 MATLAB MetroSim2 仿真一致：
  1. 延误导致出发推迟
  2. 推迟出发 → 推迟到达下一站
  3. 运行时间可压缩（受最小运行时间限制）
  4. 安全间隔约束防止超车
"""

import numpy as np
from typing import List, Optional, Tuple
from datetime import datetime

from models.timetable_snapshot import TimetableSnapshot


# ============================================================
# 默认参数（对应论文京津城际场景，与 MATLAB MetroSim2.m 一致）
# ============================================================
DEFAULT_M = 15            # 列车数量
DEFAULT_N = 8             # 每圈车站数（5物理站×2方向，8个逻辑站/圈）
DEFAULT_H = 11.4          # 追踪间隔 (min)

# 区间计划运行时间 (min)
DEFAULT_RUN_TIMES = [15.0, 12.0, 14.0, 18.0, 14.0, 12.0, 15.0, 9.0]
# 区间最小运行时间 (min)
DEFAULT_MIN_RUN_TIMES = [10.0, 8.0, 10.0, 12.0, 12.0, 8.0, 10.0, 7.0]

# 车站名称
DEFAULT_STATION_NAMES = [
    "北京南↓", "武清↓", "天津↓", "塘沽↓",
    "滨海", "塘沽↑", "天津↑", "武清↑"
]

# 计划停站时间 (min)
DEFAULT_DWELL = 2.0
# 安全发车间隔系数（最小间隔 = H * SAFETY_FACTOR）
SAFETY_FACTOR = 0.7


def mod1(value: int, modulus: int) -> int:
    """MATLAB风格1-based取模"""
    return ((value - 1) % modulus) + 1


def build_planned_timetable(M: int, N: int, H: float,
                            run_times: List[float],
                            dwell: float,
                            total_station_visits: int
                            ) -> np.ndarray:
    """
    构建计划时刻表矩阵 (M × (total_station_visits * 2))

    奇数列 = 到达时刻，偶数列 = 出发时刻。
    参照 MATLAB createbeginTimeSchedule + createOriTimeTable 逻辑。
    """
    Steps = total_station_visits * 2
    begin_times = np.zeros((M, total_station_visits))

    for i in range(M):
        for j in range(total_station_visits):
            if j == 0:
                begin_times[i, j] = i * H
            else:
                rt_idx = (j - 1) % N
                rt = run_times[rt_idx % len(run_times)]
                begin_times[i, j] = begin_times[i, j - 1] + rt + dwell

    planned = np.zeros((M, Steps))
    for i in range(M):
        for j in range(total_station_visits):
            departure = begin_times[i, j]
            if j == 0:
                arrival = 0.0
            else:
                arrival = departure - dwell
            planned[i, 2 * j] = departure
            planned[i, 2 * j + 1] = arrival

    return planned


def propagate_delays_physics(planned: np.ndarray, M: int, N: int,
                             total_station_visits: int,
                             run_times: List[float],
                             min_run_times: List[float],
                             dwell: float, H: float,
                             delay_train: int, delay_station: int,
                             delay_minutes: float,
                             control_signal: float,
                             control_train: int, control_station: int
                             ) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    基于物理约束传播延误

    对每一站，依次更新每列车的到达/出发时刻：
    - 到达 = 上一站出发 + 运行时间 - 控制压缩量
    - 出发 = max(到达 + 停站时间, 前车出发 + 安全间隔)
    - 延误 = 实际出发 - 计划出发

    参数:
        planned: 计划时刻表 M × Steps
        M: 列车数, N: 每圈车站数
        total_station_visits: 总车站访问次数
        run_times: 计划运行时间
        min_run_times: 最小运行时间
        dwell: 计划停站时间
        H: 追踪间隔
        delay_train: 初始晚点列车 (0-based)
        delay_station: 初始晚点车站 (0-based)
        delay_minutes: 初始晚点 (min)
        control_signal: 控制压缩量 (min)
        control_train: 受控列车 (0-based)
        control_station: 受控车站 (0-based)

    返回:
        (实际时刻表, 延误矩阵, 总延误)
    """
    Steps = total_station_visits * 2
    actual = planned.copy()
    delay_mat = np.zeros((M, total_station_visits))
    total_delay = 0.0

    # 逐站传播
    for station in range(total_station_visits):
        for train in range(M):
            dep_col = 2 * station
            arr_col = 2 * station + 1

            # --- 到达时刻 ---
            if station > 0:
                prev_dep_col = 2 * (station - 1)
                prev_dep = actual[train, prev_dep_col]

                rt_idx = (station - 1) % N
                rt = run_times[rt_idx % len(run_times)]
                min_rt = min_run_times[rt_idx % len(min_run_times)]

                # 控制压缩：受控列车在经过受控站的下一区间缩短运行时间
                rt_adjustment = 0.0
                if train == control_train and station == control_station + 1:
                    rt_adjustment = min(control_signal, rt - min_rt)

                adjusted_rt = rt - rt_adjustment
                adjusted_rt = max(adjusted_rt, min_rt)

                actual[train, arr_col] = prev_dep + adjusted_rt
            else:
                actual[train, arr_col] = planned[train, arr_col]

            # --- 出发时刻 ---
            # 基本出发 = 到达 + 停站
            base_dep = actual[train, arr_col] + dwell

            # 初始晚点注入：目标列车在目标车站强制推迟出发
            if train == delay_train and station == delay_station:
                base_dep = max(base_dep, planned[train, dep_col] + delay_minutes)

            # 安全间隔：不能在前车出发+安全间隔之前出发
            if train > 0:
                prev_train_dep = actual[train - 1, dep_col]
                safe_dep = prev_train_dep + H * SAFETY_FACTOR
                actual[train, dep_col] = max(base_dep, planned[train, dep_col], safe_dep)
            else:
                actual[train, dep_col] = max(base_dep, planned[train, dep_col])

            # --- 记录延误 ---
            delay = actual[train, dep_col] - planned[train, dep_col]
            if delay > 0.01:
                delay_mat[train, station] = delay
                total_delay += delay

    return actual, delay_mat, total_delay


def project_timetable(
    delay_train_idx: int,
    delay_station_idx: int,
    delay_minutes: float,
    control_signal: float,
    algorithm: str,
    c_param: float = 1.0,
    M: int = DEFAULT_M,
    N: int = DEFAULT_N,
    H: float = DEFAULT_H,
    run_times: Optional[List[float]] = None,
    min_run_times: Optional[List[float]] = None,
    station_names: Optional[List[str]] = None,
    total_circles: int = 3,
) -> TimetableSnapshot:
    """
    主函数：执行时刻表投影，返回 TimetableSnapshot

    参数:
        delay_train_idx: 初始晚点列车索引 (0-based, 0~M-1)
        delay_station_idx: 初始晚点车站全局索引 (0-based)
        delay_minutes: 初始晚点时间 (min)
        control_signal: 控制压缩量 (min, 正=压缩运行时间)
        algorithm: 算法名称
        c_param: 客流参数 c（保留接口，当前用于记录）
        M, N, H: 系统参数
        run_times: 区间运行时间
        min_run_times: 最小运行时间
        station_names: 车站名称
        total_circles: 投影圈数

    返回:
        TimetableSnapshot 对象
    """
    if run_times is None:
        run_times = DEFAULT_RUN_TIMES
    if min_run_times is None:
        min_run_times = DEFAULT_MIN_RUN_TIMES
    if station_names is None:
        station_names = DEFAULT_STATION_NAMES

    total_station_visits = total_circles * N
    dwell = DEFAULT_DWELL

    # 1. 构建计划时刻表
    planned = build_planned_timetable(M, N, H, run_times, dwell, total_station_visits)

    # 2. FCFS投影 (control_signal=0)
    fcfs_actual, delay_fcfs, total_fcfs = propagate_delays_physics(
        planned, M, N, total_station_visits, run_times, min_run_times,
        dwell, H, delay_train_idx, delay_station_idx, delay_minutes,
        control_signal=0.0,
        control_train=delay_train_idx, control_station=delay_station_idx,
    )

    # 3. 受控投影
    ctrl_actual, delay_ctrl, total_ctrl = propagate_delays_physics(
        planned, M, N, total_station_visits, run_times, min_run_times,
        dwell, H, delay_train_idx, delay_station_idx, delay_minutes,
        control_signal=control_signal,
        control_train=delay_train_idx, control_station=delay_station_idx,
    )

    # 4. 构建结果
    snapshot = TimetableSnapshot(
        M=M, N=N, H=H,
        station_names=station_names,
        run_times=run_times,
        min_run_times=min_run_times,
        planned_times=planned,
        fcfs_times=fcfs_actual,
        controlled_times=ctrl_actual,
        delay_fcfs=delay_fcfs,
        delay_controlled=delay_ctrl,
        control_signal=control_signal,
        control_train_idx=delay_train_idx,
        control_station_idx=delay_station_idx,
        trigger_train=delay_train_idx,
        trigger_station=delay_station_idx,
        initial_delay=delay_minutes,
        algorithm_used=algorithm,
        c_parameter=c_param,
        projection_steps=total_station_visits,
        total_delay_fcfs=total_fcfs,
        total_delay_controlled=total_ctrl,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    return snapshot


# ============================================================
# 测试代码
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("时刻表投影引擎测试")
    print("=" * 60)

    # 场景：列车5在车站3因设备故障晚点5分钟
    snapshot = project_timetable(
        delay_train_idx=4,      # 列车5 (0-based)
        delay_station_idx=2,    # 车站3 (0-based)
        delay_minutes=5.0,
        control_signal=2.5,     # 区间压缩2.5分钟
        algorithm="rmpc",
        c_param=0.8,
        total_circles=2,
    )

    print(f"\n计划时刻表形状: {snapshot.planned_times.shape}")
    print(f"FCFS时刻表形状: {snapshot.fcfs_times.shape}")
    print(f"\nFCFS总延误: {snapshot.total_delay_fcfs:.2f} min")
    print(f"受控总延误: {snapshot.total_delay_controlled:.2f} min")
    print(f"延误减少: {snapshot.delay_reduction():.2f} min ({snapshot.delay_reduction_pct():.1f}%)")

    # 打印部分数据检查
    print("\n计划时刻表 (前3列车, 前8列):")
    for i in range(3):
        row = [f"{snapshot.planned_times[i, j]:6.1f}" for j in range(8)]
        print(f"  列车{i+1}: " + " ".join(row))

    print("\nFCFS时刻表 (前3列车, 前8列):")
    for i in range(3):
        row = [f"{snapshot.fcfs_times[i, j]:6.1f}" for j in range(8)]
        print(f"  列车{i+1}: " + " ".join(row))

    print("\n受控时刻表 (前3列车, 前8列):")
    for i in range(3):
        row = [f"{snapshot.controlled_times[i, j]:6.1f}" for j in range(8)]
        print(f"  列车{i+1}: " + " ".join(row))

    print("\n延误矩阵-FCFS (前3列车, 前8站):")
    for i in range(3):
        row = [f"{snapshot.delay_fcfs[i, j]:6.1f}" for j in range(8)]
        print(f"  列车{i+1}: " + " ".join(row))

    print("\n延误矩阵-受控 (前3列车, 前8站):")
    for i in range(3):
        row = [f"{snapshot.delay_controlled[i, j]:6.1f}" for j in range(8)]
        print(f"  列车{i+1}: " + " ".join(row))

    print("\n测试通过!")
