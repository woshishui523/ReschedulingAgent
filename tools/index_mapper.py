import re
from typing import Dict, Tuple, Optional

# --- 1. 车站与线路拓扑定义 (单圈8站模型) ---
# 节点顺序：[1:北京南, 2:武清下行, 3:天津下行, 4:塘沽下行, 5:滨海, 6:塘沽上行, 7:天津上行, 8:武清上行]
STATION_TOPOLOGY = {
    "北京南": {"down": 1, "up": 1}, # 起点/终点，上下行共用物理位置，但逻辑上作为圈的边界
    "武清":   {"down": 2, "up": 8},
    "天津":   {"down": 3, "up": 7},
    "塘沽":   {"down": 4, "up": 6},
    "滨海":   {"down": 5, "up": 5}  # 折返点
}

N_STATIONS_PER_CIRCLE = 8

# --- 2. 列车与车底对应关系 (15辆车底，自动生成) ---
TRAIN_MAPPING = {}
NUM_TRAINS = 15

# 根据规律生成映射：
# 每个车底 k (1-15) 对应的基础车次是 2k-1 和 2k
# 扩展车次通过 +30, +60 得到 (例如: 01, 31, 61)
for k in range(1, NUM_TRAINS + 1):
    base_odd = 2 * k - 1
    base_even = 2 * k
    
    # 每个车底对应的 6 个车次号
    train_numbers = [
        f"C25{base_odd:02d}", f"C25{base_even:02d}",
        f"C25{base_odd + 30:02d}", f"C25{base_even + 30:02d}",
        f"C25{base_odd + 60:02d}", f"C25{base_even + 60:02d}"
    ]
    
    for tn in train_numbers:
        TRAIN_MAPPING[tn] = k

# --- 3. 状态追踪器 ---
class TrainStateTracker:
    def __init__(self):
        # 记录每个物理列车当前的运行状态：{train_id: {"circle": 1, "last_station_idx": 0}}
        self.train_states: Dict[int, dict] = {}

    def get_or_init_state(self, train_id: int) -> dict:
        if train_id not in self.train_states:
            self.train_states[train_id] = {"circle": 1, "last_station_idx": 0}
        return self.train_states[train_id]

    def update_progress(self, train_id: int, current_global_idx: int):
        """根据最新的全局索引更新列车的圈数和位置"""
        state = self.get_or_init_state(train_id)
        # 简单估算：如果新索引比旧索引小很多，说明跨圈了
        if current_global_idx < state["last_station_idx"]:
            state["circle"] += 1
        state["last_station_idx"] = current_global_idx

# 全局状态追踪器实例
tracker = TrainStateTracker()

def parse_command_to_index(command_string: str) -> Tuple[int, int]:
    """
    解析调度员命令，输出算法内部矩阵索引 (i, J_global)

    Args:
        command_string: 例如 "C2532次列车在天津站因设备故障晚点5分钟"

    Returns:
        (i, J_global): i为物理列车索引(1-15), J_global为全局车站索引
    """
    # --- 第一步：提取关键信息 ---
    # 提取车次号 (支持 C/G/D + 数字)
    train_match = re.search(r'([CGD]\d+)', command_string)
    if not train_match:
        raise ValueError("未识别到有效的车次号")
    train_number = train_match.group(1)

    # 提取车站名 (简化匹配，实际项目中建议使用 Trie 树或模糊匹配)
    station_name = None
    for name in STATION_TOPOLOGY.keys():
        if name in command_string:
            station_name = name
            break
    if not station_name:
        raise ValueError(f"未在命令中识别到有效车站: {command_string}")

    # --- 第二步：确定列车索引 i ---
    if train_number not in TRAIN_MAPPING:
        # 如果没有预定义映射，可以按某种规则自动生成或报错
        raise ValueError(f"车次 {train_number} 未在车底映射表中定义")

    physical_train_id = TRAIN_MAPPING[train_number]
    i = physical_train_id

    # --- 第三步：确定方向与相对车站 j ---
    # 逻辑：通过车次号奇偶性或历史状态判断方向
    # 假设：奇数为下行(Down)，偶数为上行(Up)
    train_digits = int(re.search(r'\d+', train_number).group())
    direction = "down" if train_digits % 2 != 0 else "up"

    # 获取该车站在该方向下的相对索引 (1-8)
    relative_j = STATION_TOPOLOGY[station_name][direction]

    # --- 第四步：确定圈数 k 并计算全局索引 J_global ---
    state = tracker.get_or_init_state(i)

    # 这里的圈数逻辑可以根据“当前时间”或“上一次记录的位置”来动态推断
    # 为了演示，我们假设如果车次号很大或者根据某种业务逻辑，它处于第 k 圈
    # 在实际仿真中，k 应该由仿真时钟和列车运行图实时决定
    k = state["circle"]

    # 修正逻辑：如果当前计算的相对位置 j 远小于上次记录的位置，且时间连续，则 k+1
    # 这里使用一个简单的启发式：如果这是该列车第一次被调用，默认为第1圈
    # 如果需要更精确的 k，需要结合仿真系统的 tick

    J_global = (k - 1) * N_STATIONS_PER_CIRCLE + relative_j

    # 更新追踪器状态
    tracker.update_progress(i, J_global)

    print(f"[解析成功] 命令: {command_string}")
    print(f"  -> 车次: {train_number}, 物理车底: Train_ID_{i}")
    print(f"  -> 车站: {station_name} ({direction}), 相对索引 j={relative_j}")
    print(f"  -> 圈数: k={k}, 全局索引 J_global={J_global}")

    return i, J_global

# --- 测试用例 ---
if __name__ == "__main__":
    # 模拟第一条命令：C2532 (偶数，上行) 在 天津 (上行 j=7)
    # 假设是第2圈 (因为 C2532 通常是 C2501/2 跑完一圈后的后续车次)
    # 注意：为了让测试体现 k=2，我们可以手动预设一下状态，或者调整映射逻辑
    tracker.train_states[1] = {"circle": 2, "last_station_idx": 10}

    cmd1 = "C2532次列车在天津站因设备故障晚点5分钟"
    i1, j1 = parse_command_to_index(cmd1)
    assert i1 == 1, "列车索引应为 1"
    assert j1 == 15, f"全局索引应为 15 ( (2-1)*8 + 7 ), 实际为 {j1}"

    print("-" * 30)

    # 模拟第二条命令：C2501 (奇数，下行) 在 武清 (下行 j=2)
    # 假设是第1圈
    tracker.train_states[1] = {"circle": 1, "last_station_idx": 0} # 重置状态
    cmd2 = "C2501次列车在武清站晚点3分钟"
    i2, j2 = parse_command_to_index(cmd2)
    assert i2 == 1
    assert j2 == 2, f"全局索引应为 2, 实际为 {j2}"
