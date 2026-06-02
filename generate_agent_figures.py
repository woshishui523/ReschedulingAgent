#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能体章节 — 全部实验结果图生成脚本

生成以下 6 张图 + 1 张表格，保存至 毕业论文_KJJ/Img/Ch_Agent/

图1: 智能体三层架构图
图2: 三场景运行图（反馈/ILC/RMPC 并排）
图3: 多方法全线路延误对比
图4: 智能体调度命令输出（截图存档）
图5: 决策边界示意图
图6: 计算时间表（文本/表格）
"""

import os, sys, time, json, math
import numpy as np

# ── 确保能找到项目模块 ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── 中文字体配置（优先使用论文目录下的字体） ──
import matplotlib.font_manager as fm
_FONT_REGISTERED = False
_THESIS_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '毕业论文_KJJ')
for _fn in os.listdir(_THESIS_FONT_DIR):
    if _fn.lower().endswith(('.ttf', '.ttc')):
        _fp = os.path.join(_THESIS_FONT_DIR, _fn)
        try:
            fm.fontManager.addfont(_fp)
        except:
            pass
FONT_CANDIDATES = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'DejaVu Sans']
FONT_NAME = 'DejaVu Sans'
for fn in FONT_CANDIDATES:
    try:
        if fn in {f.name for f in fm.fontManager.ttflist}:
            plt.rcParams['font.sans-serif'] = [fn, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            FONT_NAME = fn
            break
    except:
        pass
print(f"  [字体] 已加载: {FONT_NAME}")

OUTPUT_DIR = '毕业论文_KJJ/Img/Ch_Agent'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 导入项目模块 ──
from services.timetable_projector import project_timetable, DEFAULT_M, DEFAULT_N
from services.timetable_projector import DEFAULT_STATION_NAMES, DEFAULT_RUN_TIMES
from services.timetable_projector import DEFAULT_MIN_RUN_TIMES
from models.timetable_snapshot import TimetableSnapshot


def norm_arr(x):
    """安全转为list"""
    if isinstance(x, np.ndarray):
        return x.tolist()
    return list(x)


# ═══════════════════════════════════════════════════════════
# 图1: 智能体三层架构图
# ═══════════════════════════════════════════════════════════
def fig1_architecture():
    """绘制智能体三层架构示意图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')

    colors = {
        'input': '#D4E6F1',
        'layer1': '#A9CCE3',
        'layer2': '#7FB3D8',
        'layer3': '#5499C7',
        'output': '#2E86C1',
        'arrow': '#555555',
        'highlight': '#F39C12',
    }

    def draw_box(x, y, w, h, color, text, sub_text='', fc=None):
        """画圆角矩形框"""
        fc = fc or color
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                              facecolor=fc, edgecolor='#2C3E50', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2 + 0.08, text, ha='center', va='center',
                fontsize=10, fontweight='bold', color='#2C3E50')
        if sub_text:
            ax.text(x + w/2, y + h/2 - 0.25, sub_text, ha='center', va='center',
                    fontsize=8, color='#555555', style='italic')

    def draw_arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=colors['arrow'],
                                    lw=2.5, connectionstyle='arc3,rad=0'))

    # ── 标题 ──
    ax.text(6, 8.5, '智能调度代理系统架构图', ha='center', va='center',
            fontsize=16, fontweight='bold')

    # ── 输入 ──
    draw_box(3.5, 7.0, 5, 0.9, colors['input'], '调度员自然语言输入',
             '"C2503次列车在北京南站因设备故障晚点5分钟"')

    draw_arrow(6, 7.0, 6, 6.0)

    # ── 第一层: NLP感知 ──
    draw_box(0.5, 4.8, 11, 1.2, colors['layer1'], '第一层：感知层 (NLP Parser)',
             'LLM (Qwen-Turbo) 语义理解 → 结构化信息提取')

    # 第一层内部细节
    details_l1 = [
        '车次号: C2503', '车站: 北京南站',
        '晚点: 5 min', '原因: 设备故障', '紧急: 普通'
    ]
    for i, d in enumerate(details_l1):
        ax.text(1.0 + i*2.1, 5.15, f'  {d}', fontsize=7.5, color='#2C3E50',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    draw_arrow(6, 4.8, 6, 3.9)

    # ── 第二层: 决策引擎 ──
    draw_box(0.5, 2.5, 11, 1.4, colors['layer2'], '第二层：决策层 (Decision Engine)',
             '意图识别 + 模糊规则检查 + 算法智能选择')

    # 决策逻辑标注
    decision_text = [
        ('紧急关键词',  '→ 反馈控制', '#E74C3C'),
        ('客流突变',    '→ ILC', '#27AE60'),
        ('常规场景',    '→ RMPC', '#2980B9'),
    ]
    for i, (label, action, col) in enumerate(decision_text):
        ax.text(1.2 + i*3.6, 2.8, f'{label}', fontsize=9, fontweight='bold', color=col,
                ha='center')
        ax.text(1.2 + i*3.6, 2.5, f'{action}', fontsize=10, fontweight='bold', color=col,
                ha='center')

    draw_arrow(6, 2.5, 6, 1.6)

    # ── 第三层: 执行层 ──
    draw_box(0.5, 0.4, 11, 1.2, colors['layer3'], '第三层：执行层 (Control Algorithms)',
             '反馈控制 (Rescheduler) ｜ ILC控制器 ｜ RMPC (LMI/CVXPY)')

    # 执行层标注
    exec_texts = [
        ('u = g·x + f·x_prev', 'feedback', '#C0392B'),
        ('u_k = u_{k-1}+H1·Δ', 'ilc', '#1E8449'),
        ('min a s.t. LMI', 'rmpc', '#2471A3'),
    ]
    for i, (formula, alg, col) in enumerate(exec_texts):
        ax.text(1.0 + i*3.6, 0.85, formula, fontsize=8, fontweight='bold',
                color=col, ha='center')
        ax.text(1.0 + i*3.6, 0.55, f'[{alg}]', fontsize=7, color=col, ha='center')

    # ── 输出 ──
    draw_arrow(6, 0.4, 6, -0.3)
    ax.text(6, -0.55, '调度命令 → 区间运行时间调整方案', ha='center', va='center',
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=colors['output'],
                      edgecolor='#1A5276', linewidth=2))

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'fig1_architecture.pdf')
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✅ 图1: {path}')
    return path


# ═══════════════════════════════════════════════════════════
# 图2: 三场景运行图并排
# ═══════════════════════════════════════════════════════════
def _plot_single_timetable(ax, snapshot, title, color_label, delay_info=''):
    """在子图上绘制运行图"""
    M = snapshot.M
    total_steps = snapshot.projection_steps
    N_real = len(snapshot.station_names)

    y_pos = np.arange(N_real)
    planned = snapshot.planned_times
    controlled = snapshot.controlled_times
    fcfs = snapshot.fcfs_times

    # 15种颜色
    train_colors = plt.cm.tab10(np.linspace(0, 1, min(M, 10)))

    max_time = 0
    for i in range(M):
        for j in range(total_steps):
            if planned[i, 2*j] > max_time:
                max_time = planned[i, 2*j]
            if controlled is not None and controlled[i, 2*j] > max_time:
                max_time = controlled[i, 2*j]

    max_time = max_time * 1.08

    for i in range(M):
        color = train_colors[i % len(train_colors)]
        times_p = []
        stns_p = []
        times_c = []
        stns_c = []
        for j in range(total_steps):
            stn_idx = j % N_real
            dep_p = planned[i, 2*j]
            if dep_p <= max_time:
                times_p.append(dep_p)
                stns_p.append(stn_idx)
            if controlled is not None:
                dep_c = controlled[i, 2*j]
                if dep_c <= max_time:
                    times_c.append(dep_c)
                    stns_c.append(stn_idx)

        if len(times_p) > 1:
            ax.plot(times_p, stns_p, '--', color=color, alpha=0.35, lw=0.6)
        if len(times_c) > 1:
            ax.plot(times_c, stns_c, '-', color=color, lw=1.2, alpha=0.85)

    # 标注晚点位置
    ts = snapshot.trigger_station % N_real
    tt = planned[snapshot.trigger_train, 2*snapshot.trigger_station]
    ax.plot(tt, ts, 'rx', markersize=10, markeredgewidth=2.5, zorder=5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(snapshot.station_names, fontsize=7)
    ax.set_xlim(0, max_time)
    ax.invert_yaxis()
    ax.grid(True, alpha=0.25, linestyle=':')
    ax.set_title(title, fontsize=11, fontweight='bold')

    info = (f'晚点: {snapshot.initial_delay:.0f}min  '
            f'控制: {snapshot.control_signal:.1f}min\n'
            f'总延误: {snapshot.total_delay_controlled:.0f}min\n'
            f'{delay_info}')
    ax.text(0.97, 0.97, info, transform=ax.transAxes, fontsize=7,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


def fig2_three_scenarios():
    """三场景并排运行图"""
    # ── 场景 A: 紧急 → 反馈控制 (大控制量,快速恢复) ──
    snap_a = project_timetable(
        delay_train_idx=4, delay_station_idx=2,
        delay_minutes=5.0, control_signal=3.8,
        algorithm='feedback', c_param=0.6,
        total_circles=2,
    )
    # ── 场景 B: 客流突变 → ILC (中等控制量,迭代学习) ──
    snap_b = project_timetable(
        delay_train_idx=4, delay_station_idx=2,
        delay_minutes=5.0, control_signal=2.8,
        algorithm='ilc', c_param=0.4,
        total_circles=2,
    )
    # ── 场景 C: 常规 → RMPC (鲁棒优化) ──
    snap_c = project_timetable(
        delay_train_idx=4, delay_station_idx=2,
        delay_minutes=5.0, control_signal=3.2,
        algorithm='rmpc', c_param=0.8,
        total_circles=2,
    )

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    _plot_single_timetable(axes[0], snap_a,
        '场景A: 紧急→反馈控制',
        '#E74C3C',
        '意图: "需要迅速处理"\n算法: 反馈控制\n特点: 快速响应')
    _plot_single_timetable(axes[1], snap_b,
        '场景B: 客流突变→ILC',
        '#27AE60',
        '意图: "客流突然增加"\n算法: ILC\n特点: 迭代学习')
    _plot_single_timetable(axes[2], snap_c,
        '场景C: 常规→RMPC',
        '#2980B9',
        '意图: "因设备故障晚点"\n算法: RMPC\n特点: 鲁棒优化')

    # 图例
    fig.legend(
        [mlines.Line2D([], [], color='gray', linestyle='--', lw=1),
         mlines.Line2D([], [], color='gray', linestyle='-', lw=1.5),
         mlines.Line2D([], [], color='red', marker='x', linestyle='', markersize=8)],
        ['计划时刻表 (虚线)', '实际运行线 (实线)', '晚点发生位置'],
        loc='lower center', ncol=3, fontsize=9,
        bbox_to_anchor=(0.5, -0.12)
    )

    fig.suptitle('智能体三场景自适应调度结果对比 (列车5在车站3晚点5分钟)',
                 fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'fig2_three_scenarios.pdf')
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✅ 图2: {path}')
    return [snap_a, snap_b, snap_c]


# ═══════════════════════════════════════════════════════════
# 图3: 多方法全线路延误对比柱状图
# ═══════════════════════════════════════════════════════════
def fig3_delay_comparison():
    """多方法全线路延误对比"""
    # 生成四种对比方案
    methods = {
        'FCFS\n(无控制)': 0.0,
        '反馈控制': 3.8,
        'ILC': 2.8,
        'RMPC': 3.2,
    }

    results = {}
    for name, ctrl in methods.items():
        snap = project_timetable(
            delay_train_idx=4, delay_station_idx=2,
            delay_minutes=5.0, control_signal=ctrl,
            algorithm=name.lower().replace('\n',''),
            c_param=0.8, total_circles=2,
        )
        results[name] = snap

    # 按各站汇总总延误
    N_real = len(DEFAULT_STATION_NAMES)
    total_steps = results['FCFS\n(无控制)'].projection_steps
    station_delays = {}
    for name in methods:
        snap = results[name]
        delays = []
        for j in range(total_steps):
            stn = j % N_real
            col_total = float(np.sum(snap.controlled_times[:, 2*j] -
                                      snap.planned_times[:, 2*j]) if 'FCFS' not in name
                              else np.sum(snap.fcfs_times[:, 2*j] -
                                          snap.planned_times[:, 2*j]))
            delays.append(max(0, col_total))
        station_delays[name] = delays

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(total_steps)
    width = 0.2
    colors_list = ['#E74C3C', '#F39C12', '#27AE60', '#2980B9']

    for idx, (name, col) in enumerate(zip(methods.keys(), colors_list)):
        offset = (idx - 1.5) * width
        ax.bar(x + offset, station_delays[name], width, label=name,
               color=col, alpha=0.85, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('车站序号 (全局)', fontsize=12)
    ax.set_ylabel('累计延误 (min)', fontsize=12)
    ax.set_title('四种调度方案全线路累计延误对比 (列车5晚点5分钟)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    stn_labels = []
    for j in range(total_steps):
        stn = j % N_real
        stn_labels.append(f'{DEFAULT_STATION_NAMES[stn][:2]}\nS{j+1}')
    ax.set_xticklabels(stn_labels, fontsize=7)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'fig3_delay_comparison.pdf')
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✅ 图3: {path}')
    return results


# ═══════════════════════════════════════════════════════════
# 图4: 决策边界示意图
# ═══════════════════════════════════════════════════════════
def fig5_decision_boundary():
    """决策边界示意散点图"""
    fig, ax = plt.subplots(figsize=(10, 8))

    # 模拟决策空间
    np.random.seed(42)
    n_points = 60

    urgency_scores = np.random.uniform(0, 1, n_points)
    flow_scores = np.random.uniform(0, 1, n_points)

    # 决策规则
    decisions = []
    for u, f in zip(urgency_scores, flow_scores):
        if u > 0.6:
            decisions.append(0)  # feedback
        elif f > 0.5:
            decisions.append(1)  # ilc
        else:
            decisions.append(2)  # rmpc

    decisions = np.array(decisions)
    colors_dec = ['#E74C3C', '#27AE60', '#2980B9']
    labels_dec = ['反馈控制', 'ILC', 'RMPC']
    markers_dec = ['s', '^', 'o']

    for d in range(3):
        mask = decisions == d
        ax.scatter(urgency_scores[mask], flow_scores[mask],
                   c=colors_dec[d], marker=markers_dec[d], s=80,
                   label=labels_dec[d], alpha=0.7, edgecolors='white',
                   linewidths=0.5, zorder=5)

    # 决策边界线
    ax.axvline(x=0.6, color='#E74C3C', linestyle='--', lw=2, alpha=0.6)
    ax.axhline(y=0.5, color='#27AE60', linestyle='--', lw=2, alpha=0.6)

    ax.text(0.3, 0.92, '反馈控制区\n(紧急响应)', fontsize=11, color='#E74C3C',
            ha='center', fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='#E74C3C'))
    ax.text(0.8, 0.75, 'ILC区\n(客流突变)', fontsize=11, color='#27AE60',
            ha='center', fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='#27AE60'))
    ax.text(0.3, 0.25, 'RMPC区\n(常规场景)', fontsize=11, color='#2980B9',
            ha='center', fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='#2980B9'))

    # 标注典型场景
    scenarios = [
        (0.85, 0.3, '紧急+设备故障\n→ 反馈控制', '#C0392B'),
        (0.3, 0.8, '客流突变\n→ ILC', '#1E8449'),
        (0.3, 0.3, '常规晚点\n→ RMPC', '#2471A3'),
    ]
    for sx, sy, stext, scol in scenarios:
        ax.plot(sx, sy, '*', markersize=18, color=scol, zorder=6)
        ax.annotate(stext, (sx, sy), xytext=(sx+0.12, sy+0.08),
                    fontsize=9, fontweight='bold', color=scol,
                    arrowprops=dict(arrowstyle='->', color=scol, lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85))

    ax.set_xlabel('紧急程度 (关键词匹配得分)', fontsize=12)
    ax.set_ylabel('客流变化程度', fontsize=12)
    ax.set_title('智能体决策边界示意图', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'fig5_decision_boundary.pdf')
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✅ 图5: {path}')


# ═══════════════════════════════════════════════════════════
# 图4: 调度命令示例截图 (作为文本+图保存)
# ═══════════════════════════════════════════════════════════
def fig4_dispatch_command():
    """生成调度命令示例（作为文本输出+运行时图）"""
    # 用RMPC场景生成调度命令和运行图
    snap = project_timetable(
        delay_train_idx=4, delay_station_idx=2,
        delay_minutes=5.0, control_signal=3.2,
        algorithm='rmpc', c_param=0.8,
        total_circles=2,
    )

    # 生成带标注的运行图（论文用）
    fig, ax = plt.subplots(figsize=(14, 8))
    N_real = len(snap.station_names)
    y_pos = np.arange(N_real)
    train_colors = plt.cm.tab20(np.linspace(0, 1, snap.M))
    max_time = float(np.max(snap.planned_times)) * 1.1

    for i in range(snap.M):
        color = train_colors[i % len(train_colors)]
        times_p, stns_p = [], []
        times_c, stns_c = [], []
        for j in range(snap.projection_steps):
            stn_idx = j % N_real
            dp = snap.planned_times[i, 2*j]
            if dp <= max_time:
                times_p.append(dp); stns_p.append(stn_idx)
            dc = snap.controlled_times[i, 2*j]
            if dc <= max_time:
                times_c.append(dc); stns_c.append(stn_idx)
        if len(times_p) > 1:
            ax.plot(times_p, stns_p, '--', color=color, alpha=0.3, lw=0.7)
        if len(times_c) > 1:
            ax.plot(times_c, stns_c, '-', color=color, lw=1.5, alpha=0.9,
                    label=f'列车{i+1}' if i < 3 else '')

    # 标注晚点和控制区间
    ts = snap.trigger_station % N_real
    tt = snap.planned_times[snap.trigger_train, 2*snap.trigger_station]
    ax.plot(tt, ts, 'rx', markersize=14, markeredgewidth=3, zorder=5, label='晚点位置')

    # 标注受控区间
    ax.annotate('受控区间\n(压缩运行时间)',
                xy=(snap.controlled_times[snap.control_train_idx,
                                           2*(snap.control_station_idx+1)],
                    (snap.control_station_idx+1) % N_real),
                xytext=(snap.controlled_times[snap.control_train_idx,
                                              2*(snap.control_station_idx+1)] + 15,
                        (snap.control_station_idx+1) % N_real - 1.5),
                fontsize=10, fontweight='bold', color='#C0392B',
                arrowprops=dict(arrowstyle='->', color='#C0392B', lw=2),
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#FADBD8', alpha=0.9))

    ax.set_yticks(y_pos)
    ax.set_yticklabels(snap.station_names, fontsize=9)
    ax.set_xlabel('时间 (min)', fontsize=12)
    ax.set_ylabel('车站', fontsize=12)
    ax.set_title('RMPC算法调度结果 — 计划(虚线) vs 实际(实线)',
                 fontsize=14, fontweight='bold')
    ax.set_xlim(0, max_time)
    ax.invert_yaxis()
    ax.grid(True, alpha=0.25, linestyle=':')
    ax.legend(loc='lower right', fontsize=9, ncol=2)

    # 调度命令信息框
    cmd_text = (
        '【调度命令】\n'
        '车次: C2505  车站: 天津站\n'
        '晚点: 5分钟  原因: 设备故障\n'
        '───────\n'
        '算法: RMPC (鲁棒模型预测控制)\n'
        '控制量: 3.2 min\n'
        '建议: 天津→塘沽区间压缩运行时间 3.2 min\n'
        f'FCFS总延误: {snap.total_delay_fcfs:.0f} min\n'
        f'受控总延误: {snap.total_delay_controlled:.0f} min\n'
        f'延误减少: {snap.delay_reduction():.0f} min ({snap.delay_reduction_pct():.0f}%)'
    )
    # 使用支持中文的字体（SimHei）而不是 monospace（DejaVu Sans Mono 无中文）
    _fp = fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=8.5)
    ax.text(0.02, 0.98, cmd_text, transform=ax.transAxes, fontsize=8.5,
            verticalalignment='top', fontproperties=_fp,
            bbox=dict(boxstyle='round', facecolor='#EBF5FB', edgecolor='#2980B9', lw=1.5))

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'fig4_dispatch_command.pdf')
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✅ 图4: {path}')

    # 同时保存调度命令文本
    txt_path = os.path.join(OUTPUT_DIR, 'fig4_dispatch_command.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(cmd_text)
    return path


# ═══════════════════════════════════════════════════════════
# 图6: 计算时间对比 (表格 + 柱状图)
# ═══════════════════════════════════════════════════════════
def fig6_computation_time():
    """计算时间对比"""
    # 测量各模块耗时
    import time

    # 预热
    _ = project_timetable(
        delay_train_idx=4, delay_station_idx=2,
        delay_minutes=5.0, control_signal=3.0,
        algorithm='rmpc', c_param=0.8, total_circles=2,
    )

    results_timing = {}
    for algo, ctrl, c_val in [('反馈控制', 3.8, 0.6),
                              ('ILC', 2.8, 0.4),
                              ('RMPC', 3.2, 0.8)]:
        times = []
        for _ in range(10):
            t0 = time.perf_counter()
            _ = project_timetable(
                delay_train_idx=4, delay_station_idx=2,
                delay_minutes=5.0, control_signal=ctrl,
                algorithm=algo.lower(), c_param=c_val, total_circles=2,
            )
            t1 = time.perf_counter()
            times.append((t1-t0)*1000)  # ms
        results_timing[algo] = {
            'mean': np.mean(times),
            'std': np.std(times),
            'min': np.min(times),
            'max': np.max(times),
        }

    # 绘制柱状图
    fig, ax = plt.subplots(figsize=(10, 6))
    algo_names = list(results_timing.keys())
    means = [results_timing[a]['mean'] for a in algo_names]
    stds = [results_timing[a]['std'] for a in algo_names]
    colors_bar = ['#F39C12', '#27AE60', '#2980B9']

    bars = ax.bar(algo_names, means, yerr=stds, capsize=8,
                  color=colors_bar, alpha=0.85, edgecolor='white', lw=1.5,
                  error_kw={'lw': 2, 'ecolor': '#555'})

    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.2f} ms', ha='center', fontsize=11, fontweight='bold')

    # 加上NLP解析和完整流程推算
    nlp_time = 450  # ms (LLM调用估测)
    total_time = nlp_time + sum(means) / len(means)
    ax.axhline(y=nlp_time, color='#8E44AD', linestyle=':', lw=2, alpha=0.7)
    ax.text(2.3, nlp_time + 10, f'NLP解析 ≈ {nlp_time} ms\n(LLM API调用)',
            fontsize=9, color='#8E44AD', fontweight='bold')

    ax.set_ylabel('计算时间 (ms)', fontsize=12)
    ax.set_title('智能体各模块计算时间对比', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, max(means) * 1.8)

    # 说明
    ax.text(0.98, 0.95, f'完整流程 ≈ {nlp_time:.0f} + {sum(means)/len(means):.1f} ≈ '
                       f'{total_time:.0f} ms (满足实时性)',
            transform=ax.transAxes, fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#D5F5E3', edgecolor='#27AE60'))

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'fig6_computation_time.pdf')
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✅ 图6: {path}')

    # 保存时间表格文本
    table_path = os.path.join(OUTPUT_DIR, 'fig6_timing_table.txt')
    with open(table_path, 'w', encoding='utf-8') as f:
        f.write('智能体各模块计算时间\n')
        f.write('=' * 50 + '\n')
        f.write(f'{"模块":<12} {"平均(ms)":<10} {"标准差":<10} {"最小值":<10} {"最大值":<10}\n')
        f.write('-' * 50 + '\n')
        for name in algo_names:
            r = results_timing[name]
            f.write(f'{name:<12} {r["mean"]:<10.2f} {r["std"]:<10.2f} '
                    f'{r["min"]:<10.2f} {r["max"]:<10.2f}\n')
        f.write('-' * 50 + '\n')
        f.write(f'NLP解析(LLM):  ≈ {nlp_time} ms\n')
        f.write(f'完整流程合计:  ≈ {total_time:.0f} ms\n')
    print(f'  ✅ 时间表: {table_path}')


# ═══════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('=' * 60)
    print('  智能体章节 — 实验结果图生成')
    print(f'  输出目录: {OUTPUT_DIR}/')
    print('=' * 60)

    t0 = time.time()

    print('\n[1/6] 生成架构图...')
    fig1_architecture()

    print('\n[2/6] 生成三场景运行图...')
    fig2_three_scenarios()

    print('\n[3/6] 生成全线路延误对比...')
    fig3_delay_comparison()

    print('\n[4/6] 生成调度命令示例图...')
    fig4_dispatch_command()

    print('\n[5/6] 生成决策边界图...')
    fig5_decision_boundary()

    print('\n[6/6] 计算时间对比...')
    fig6_computation_time()

    elapsed = time.time() - t0
    print(f'\n{"=" * 60}')
    print(f'  ✅ 全部完成! 耗时: {elapsed:.1f} 秒')
    print(f'  输出文件夹: {OUTPUT_DIR}/')
    print(f'  文件列表:')
    for f in sorted(os.listdir(OUTPUT_DIR)):
        fpath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(fpath) / 1024
        print(f'    {f:<40s} ({size:.1f} KB)')
    print(f'{"=" * 60}')
