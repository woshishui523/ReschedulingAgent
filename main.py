from tools.nlp_parser_tool import parse_dispatch_text
from services.unified_dispatch_service import unified_process_delay


def dispatch_input_processor(dispatch_text: str) -> str:
    """
    调度员输入处理函数

    流程：
    1. 使用 LLM 解析自然语言输入
    2. 提取结构化数据
    3. 意图分析 → 三算法选择（反馈控制/ILC/RMPC）
    4. 执行选定算法
    5. 返回区间运行时间调整调度命令

    参数:
        dispatch_text: 调度员的口头描述或文本输入

    返回:
        生成的调度命令字符串
    """
    print("=" * 60)
    print("Train Delay Intelligent Rescheduling System")
    print("=" * 60)
    print("\nSupported algorithms:")
    print("   * Feedback Control (urgent)")
    print("   * ILC (passenger surge)")
    print("   * RMPC (regular)")
    print("=" * 60)

    # Step 1: LLM parsing
    print("\nStep 1: Parsing dispatcher input...")
    print(f"   Input: {dispatch_text}")

    parsed_data = parse_dispatch_text(dispatch_text)

    if "error" in parsed_data:
        print(f"\nParse failed: {parsed_data['error']}")
        raise ValueError("Cannot parse dispatcher input, check format")

    print("\nParse succeeded! Extracted info:")
    for key, value in parsed_data.items():
        print(f"   * {key}: {value}")

    # Step 2: Unified dispatch (three algorithms)
    print("\nStep 2: Intent analysis + algorithm selection + computation...")

    try:
        command, diagram_path = unified_process_delay(
            target_train_number=parsed_data["train_number"],
            target_station_name=parsed_data["station_name"],
            delay_minutes=parsed_data["delay_duration"],
            reason_text=parsed_data["delay_reason"],
            original_text=dispatch_text,
        )

        print("\nProcessing done!")
        print("\n" + "=" * 60)
        print("Generated dispatch command:")
        print("=" * 60)
        print(command)
        print("=" * 60)

        return command

    except ValueError as e:
        print(f"\nProcessing failed: {e}")
        raise e


if __name__ == "__main__":
    dispatch_input = "C2503 次列车在北京南站因设备故障晚点 5 分钟"

    try:
        result = dispatch_input_processor(dispatch_input)
        print("\nDispatch command generated and saved!")
    except Exception as e:
        print(f"\nSystem error: {e}")
