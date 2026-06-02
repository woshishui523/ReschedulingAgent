"""
时刻表快照数据模型

TimetableSnapshot: 内存中传递的时刻表投影结果
TimetableSnapshotORM: 数据库持久化模型
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from datetime import datetime
from config.database import Base


@dataclass
class TimetableSnapshot:
    """时刻表投影快照，包含计划/无控制/受控三种时刻表"""

    M: int                              # 列车数量 (15)
    N: int                              # 每圈车站数 (8逻辑站)
    H: float                            # 追踪间隔 (11.4 min)
    station_names: List[str]            # 车站名称列表
    run_times: List[float]              # 区间计划运行时间 (min)
    min_run_times: List[float]          # 区间最小运行时间 (min)

    # 核心时刻表矩阵 (M × Steps, 奇数列=到达, 偶数列=出发)
    planned_times: Optional[np.ndarray] = None     # 计划时刻表 OriTimeTable
    fcfs_times: Optional[np.ndarray] = None        # FCFS(无控制)时刻表
    controlled_times: Optional[np.ndarray] = None  # 受控时刻表

    # 延误矩阵
    delay_fcfs: Optional[np.ndarray] = None        # FCFS各步延误
    delay_controlled: Optional[np.ndarray] = None  # 受控各步延误

    # 控制量
    control_signal: float = 0.0         # 施加的控制量 (min)
    control_train_idx: int = 0          # 受控列车索引 (1-based)
    control_station_idx: int = 0        # 受控车站全局索引

    # 元数据
    trigger_train: int = 0              # 初始晚点列车
    trigger_station: int = 0            # 初始晚点车站
    initial_delay: float = 0.0          # 初始晚点 (min)
    algorithm_used: str = ""            # 'feedback' | 'ilc' | 'rmpc'
    c_parameter: float = 1.0            # 客流参数 c
    projection_steps: int = 0           # 投影步数
    total_delay_fcfs: float = 0.0       # FCFS总延误
    total_delay_controlled: float = 0.0 # 受控总延误
    generated_at: str = ""

    def delay_reduction(self) -> float:
        """延误减少量"""
        return self.total_delay_fcfs - self.total_delay_controlled

    def delay_reduction_pct(self) -> float:
        """延误减少百分比"""
        if self.total_delay_fcfs > 0:
            return (self.delay_reduction() / self.total_delay_fcfs) * 100
        return 0.0

    def to_summary_dict(self) -> dict:
        """转为前端可用的摘要字典"""
        return {
            "M": self.M, "N": self.N, "H": self.H,
            "station_names": self.station_names,
            "trigger_train": self.trigger_train,
            "trigger_station": self.trigger_station,
            "initial_delay": self.initial_delay,
            "control_signal": self.control_signal,
            "algorithm_used": self.algorithm_used,
            "c_parameter": self.c_parameter,
            "projection_steps": self.projection_steps,
            "total_delay_fcfs": round(self.total_delay_fcfs, 2),
            "total_delay_controlled": round(self.total_delay_controlled, 2),
            "delay_reduction": round(self.delay_reduction(), 2),
            "delay_reduction_pct": round(self.delay_reduction_pct(), 1),
            "generated_at": self.generated_at,
        }


class TimetableSnapshotORM(Base):
    """时刻表快照数据库模型"""

    __tablename__ = "timetable_snapshots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispatch_record_id = Column(Integer, ForeignKey("dispatch_records.dispatch_id"), nullable=True)
    algorithm_used = Column(String(30), nullable=False)
    trigger_train = Column(Integer, nullable=False)
    trigger_station = Column(Integer, nullable=False)
    initial_delay = Column(Float, nullable=False)
    control_signal = Column(Float, nullable=False)
    c_parameter = Column(Float, default=1.0)
    total_delay_fcfs = Column(Float, default=0.0)
    total_delay_controlled = Column(Float, default=0.0)
    projection_steps = Column(Integer, default=0)
    snapshot_json = Column(Text, nullable=True)   # JSON序列化的摘要数据
    diagram_path = Column(String(500), nullable=True)  # 生成的图片路径
    generated_at = Column(DateTime, default=datetime.utcnow)
