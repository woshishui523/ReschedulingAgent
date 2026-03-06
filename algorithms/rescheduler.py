def compute_reschedule(train_id, station_id, delay_minutes):
    """
    简化版调度算法（后续可替换为MPC）
    输入：
        train_id: 列车ID
        station_id: 车站ID
        delay_minutes: 晚点时间
    输出：
        调度调整量
    """

    # 简单策略：晚点传播 + 缓冲吸收
    if delay_minutes <= 5:
        adjustment = 0  # 小晚点，不调整
    elif delay_minutes <= 20:
        adjustment = delay_minutes * 0.5  # 吸收一半延误
    else:
        adjustment = delay_minutes * 0.8  # 大晚点，强调整

    result = {
        "train_id": train_id,
        "station_id": station_id,
        "original_delay": delay_minutes,
        "adjusted_departure_delay": round(adjustment, 2),
        "reschedule_strategy": "延后发车 + 压缩停站时间"
    }

    return result