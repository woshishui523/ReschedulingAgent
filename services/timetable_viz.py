"""
时刻表可视化模块

生成论文格式的时空运行图，对标 MATLAB MetroSim2 输出格式。
支持中文、PNG/SVG/PDF导出。
"""

import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import base64
from io import BytesIO
from typing import Optional, Tuple

from models.timetable_snapshot import TimetableSnapshot


# ============================================================
# 中文字体配置
# ============================================================
def _setup_chinese_fonts():
    """配置matplotlib中文字体"""
    # 优先使用论文中的字体
    font_candidates = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
    available = {f.name for f in fm.fontManager.ttflist}

    for font_name in font_candidates:
        if font_name in available:
            plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            return font_name

    # Fallback: 注册论文目录下的字体
    thesis_font_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '毕业论文_KJJ'
    )
    if os.path.exists(thesis_font_dir):
        for fn in os.listdir(thesis_font_dir):
            if fn.lower().endswith(('.ttf', '.ttc')):
                font_path = os.path.join(thesis_font_dir, fn)
                try:
                    fm.fontManager.addfont(font_path)
                    prop = fm.FontProperties(fname=font_path)
                    plt.rcParams['font.sans-serif'] = [prop.get_name(), 'DejaVu Sans']
                    plt.rcParams['axes.unicode_minus'] = False
                    return prop.get_name()
                except Exception:
                    pass

    return 'DejaVu Sans'


FONT_NAME = _setup_chinese_fonts()

# 15种区分颜色（色盲友好调色板）
TRAIN_COLORS = plt.cm.tab20(np.linspace(0, 1, 15))


def _station_positions(N: int) -> np.ndarray:
    """车站纵轴位置（等间距，从0到N-1）"""
    return np.arange(N)


def generate_time_distance_diagram(
    snapshot: TimetableSnapshot,
    output_path: Optional[str] = None,
    title: str = "列车运行图",
    show_planned: bool = True,
    show_fcfs: bool = False,
    show_controlled: bool = True,
    dpi: int = 150,
    figsize: Tuple[float, float] = (16, 10),
    format: str = 'png',
) -> str:
    """
    生成时空运行图（时间-距离图）

    对标论文格式：横轴=时间(min)，纵轴=车站，虚线=计划，实线=实际

    参数:
        snapshot: 时刻表快照
        output_path: 输出文件路径（None则返回base64）
        title: 图标题
        show_planned: 是否显示计划时刻表
        show_fcfs: 是否显示FCFS（无控制）
        show_controlled: 是否显示受控时刻表
        dpi: 分辨率
        figsize: 图尺寸
        format: 输出格式 ('png' | 'svg' | 'pdf')

    返回:
        base64字符串或文件路径
    """
    M = snapshot.M
    total_visits = snapshot.projection_steps
    station_names = snapshot.station_names
    N_real = len(station_names)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # 纵轴：车站位置（从上到下 = 运行方向）
    y_positions = _station_positions(N_real)

    # 横轴范围
    planned = snapshot.planned_times
    max_time = np.max(planned[:, :2 * total_visits]) * 1.05

    # 绘制每列车的运行线
    for i in range(M):
        color = TRAIN_COLORS[i % len(TRAIN_COLORS)]

        # 提取各站出发时刻对应的 (time, station) 坐标
        times_planned = []
        times_actual = []
        stations = []

        for j in range(total_visits):
            station_idx = j % N_real
            dep_time_planned = planned[i, 2 * j]

            if dep_time_planned <= max_time:
                times_planned.append(dep_time_planned)
                stations.append(station_idx)

                if show_controlled and snapshot.controlled_times is not None:
                    times_actual.append(snapshot.controlled_times[i, 2 * j])
                elif show_fcfs and snapshot.fcfs_times is not None:
                    times_actual.append(snapshot.fcfs_times[i, 2 * j])

        # 计划时刻表（虚线）
        if show_planned and len(times_planned) > 1:
            ax.plot(times_planned, stations, '--', color=color, alpha=0.5,
                    linewidth=0.8, label='_nolegend_')

        # 实际时刻表（实线）
        if len(times_actual) > 1:
            line, = ax.plot(times_actual, stations, '-', color=color,
                           linewidth=1.5, alpha=0.9)
            if i < 5:  # 只标注前5列车避免图例过长
                line.set_label(f'列车{i+1}')

    # 标注晚点发生位置
    trigger_station_idx = snapshot.trigger_station % N_real
    trigger_time = snapshot.planned_times[
        snapshot.trigger_train, 2 * snapshot.trigger_station
    ]
    ax.plot(trigger_time, trigger_station_idx, 'rx', markersize=10,
            markeredgewidth=2, zorder=5, label='晚点位置')

    # 坐标轴设置
    ax.set_yticks(y_positions)
    ax.set_yticklabels(station_names, fontsize=9)
    ax.set_xlabel('时间 (min)', fontsize=12, fontproperties=fm.FontProperties(fname=None))
    ax.set_ylabel('车站', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlim(0, max_time)
    ax.invert_yaxis()  # 第一站在上方
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper right', fontsize=8, ncol=2)

    # 添加信息文本框
    info_text = (
        f"列车数: M={M}  车站数: N={N_real}\n"
        f"晚点: {snapshot.initial_delay:.1f} min  "
        f"控制量: {snapshot.control_signal:.1f} min\n"
        f"算法: {snapshot.algorithm_used.upper()}  "
        f"c={snapshot.c_parameter:.2f}\n"
        f"FCFS总延误: {snapshot.total_delay_fcfs:.1f} min\n"
        f"受控总延误: {snapshot.total_delay_controlled:.1f} min\n"
        f"延误减少: {snapshot.delay_reduction():.1f} min "
        f"({snapshot.delay_reduction_pct():.1f}%)"
    )
    ax.text(0.98, 0.97, info_text, transform=ax.transAxes,
            fontsize=8, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    fig.tight_layout()

    # 输出
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        fig.savefig(output_path, dpi=dpi, format=format, bbox_inches='tight')
        plt.close(fig)
        return output_path
    else:
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')


def generate_delay_comparison_chart(
    snapshot: TimetableSnapshot,
    output_path: Optional[str] = None,
    dpi: int = 150,
    figsize: Tuple[float, float] = (14, 6),
) -> str:
    """
    生成延误对比图：各站FCFS vs 受控总延误柱状图

    参数:
        snapshot: 时刻表快照
        output_path: 输出文件路径
        dpi: 分辨率
        figsize: 图尺寸

    返回:
        base64字符串或文件路径
    """
    total_visits = snapshot.projection_steps
    N_real = len(snapshot.station_names)

    # 汇总各站总延误
    stations_display = []
    fcfs_delays = []
    ctrl_delays = []

    for j in range(total_visits):
        station_name = snapshot.station_names[j % N_real]
        fcfs_sum = np.sum(snapshot.delay_fcfs[:, j]) if snapshot.delay_fcfs is not None else 0
        ctrl_sum = np.sum(snapshot.delay_controlled[:, j]) if snapshot.delay_controlled is not None else 0
        stations_display.append(f"{station_name}\n(站{j+1})")
        fcfs_delays.append(fcfs_sum)
        ctrl_delays.append(ctrl_sum)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    x = np.arange(len(stations_display))
    width = 0.35

    bars1 = ax.bar(x - width/2, fcfs_delays, width, label='FCFS (无控制)',
                   color='#E74C3C', alpha=0.8)
    bars2 = ax.bar(x + width/2, ctrl_delays, width, label=f'受控 ({snapshot.algorithm_used.upper()})',
                   color='#2ECC71', alpha=0.8)

    ax.set_xlabel('车站', fontsize=12)
    ax.set_ylabel('总延误 (min)', fontsize=12)
    ax.set_title(f'各站总延误对比 (初始晚点 {snapshot.initial_delay:.1f} min, '
                 f'控制量 {snapshot.control_signal:.1f} min)',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(stations_display, fontsize=8, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # 数值标注
    for bar in bars1:
        if bar.get_height() > 0.1:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                    f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=7)
    for bar in bars2:
        if bar.get_height() > 0.1:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                    f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=7)

    fig.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return output_path
    else:
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')


def save_thesis_figures(snapshot: TimetableSnapshot, output_dir: str) -> dict:
    """
    生成论文用图，保存到指定目录

    返回:
        {'diagram': path, 'comparison': path} 字典
    """
    os.makedirs(output_dir, exist_ok=True)

    diagram_path = os.path.join(output_dir, 'timetable_diagram.png')
    comparison_path = os.path.join(output_dir, 'delay_comparison.png')

    generate_time_distance_diagram(
        snapshot, output_path=diagram_path,
        title=f"列车运行图 — {snapshot.algorithm_used.upper()}控制效果对比",
        show_planned=True, show_controlled=True, show_fcfs=False,
        dpi=300, figsize=(18, 11), format='png',
    )

    generate_delay_comparison_chart(
        snapshot, output_path=comparison_path,
        dpi=300, figsize=(16, 7),
    )

    # 同时保存SVG版本用于论文排版
    svg_path = os.path.join(output_dir, 'timetable_diagram.svg')
    generate_time_distance_diagram(
        snapshot, output_path=svg_path,
        title=f"列车运行图 — {snapshot.algorithm_used.upper()}控制效果对比",
        show_planned=True, show_controlled=True, show_fcfs=False,
        dpi=150, figsize=(18, 11), format='svg',
    )

    return {
        'diagram_png': diagram_path,
        'comparison_png': comparison_path,
        'diagram_svg': svg_path,
    }


# ============================================================
# 测试代码
# ============================================================
if __name__ == "__main__":
    from services.timetable_projector import project_timetable

    print("=" * 60)
    print("时刻表可视化测试")
    print(f"使用字体: {FONT_NAME}")
    print("=" * 60)

    # 生成测试数据
    snapshot = project_timetable(
        delay_train_idx=4,
        delay_station_idx=2,
        delay_minutes=5.0,
        control_signal=2.5,
        algorithm="rmpc",
        c_param=0.8,
        total_circles=2,
    )

    print(f"\nFCFS总延误: {snapshot.total_delay_fcfs:.2f} min")
    print(f"受控总延误: {snapshot.total_delay_controlled:.2f} min")
    print(f"延误减少: {snapshot.delay_reduction():.2f} min "
          f"({snapshot.delay_reduction_pct():.1f}%)")

    # 生成图表
    output_dir = "static/output"
    os.makedirs(output_dir, exist_ok=True)

    paths = save_thesis_figures(snapshot, output_dir)
    print(f"\n生成的图片:")
    for name, path in paths.items():
        size_kb = os.path.getsize(path) / 1024
        print(f"  {name}: {path} ({size_kb:.1f} KB)")

    print("\n测试通过!")
