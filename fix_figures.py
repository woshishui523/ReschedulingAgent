#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重写智能体章节运行时刻表图（图2）
对齐 MATLAB MetroSim2.m 的绘图方式：
  1. 数据格式 [arr, dep, arr, dep, ...] 交替排列
  2. 同一站 Y轴位置相同（arr和dep的Y重叠），形成台阶锯齿线
  3. 虚线=计划时刻表，实线=受控时刻表
  4. 配色和风格对齐论文章节图
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# ── 注册论文中文字体 ──
_THESIS_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '毕业论文_KJJ')
for fn in os.listdir(_THESIS_FONT_DIR):
    if fn.lower().endswith(('.ttf', '.ttc')):
        try:
            fm.fontManager.addfont(os.path.join(_THESIS_FONT_DIR, fn))
        except:
            pass
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = '毕业论文_KJJ/Img/Ch_Agent'
os.makedirs(OUTPUT_DIR, exist_ok=True)

from services.timetable_projector import project_timetable, DEFAULT_M, DEFAULT_N
from services.timetable_projector import DEFAULT_STATION_NAMES, DEFAULT_RUN_TIMES
from services.timetable_projector import DEFAULT_MIN_RUN_TIMES

# ── 车站位置（等间距，1-based 用于显示） ──
STATIONS_DISPLAY = ['北京南', '武清', '天津', '塘沽', '滨海']
N_DISPLAY = len(STATIONS_DISPLAY)

def build_interleaved_timetable(snapshot, which='planned'):
    """
    将 TimetableSnapshot 中的矩阵转换为 [arr, dep, arr, dep, ...] 交错格式
    匹配 MATLAB OriTimeTable 的存储方式
    
    返回: (times, station_ys)
        times: list of lists, 每列车的时间序列
        station_ys: list of lists, 每列车对应的Y轴车站位置
    """
    if which == 'planned':
        data = snapshot.planned_times
    elif which == 'fcfs':
        data = snapshot.fcfs_times
    elif which == 'controlled':
        data = snapshot.controlled_times
    else:
        raise ValueError(f'Unknown timetable: {which}')
    
    # data shape: (M, 2*steps), 偶数列=dep, 奇数列=arr
    M, total_cols = data.shape
    steps = total_cols // 2
    
    all_times = []
    all_ys = []
    
    for i in range(M):
        times = []
        ys = []
        for j in range(steps):
            arr_time = data[i, 2*j + 1]  # 奇数列=到站时间
            dep_time = data[i, 2*j]      # 偶数列=发车时间
            
            # 站名映射: 物理站 = j % N_DISPLAY
            station_idx = j % N_DISPLAY
            
            # 到站: (arr_time, station_idx)
            times.append(arr_time)
            ys.append(station_idx)
            
            # 发车: (dep_time, station_idx) — 同一站，水平线段
            times.append(dep_time)
            ys.append(station_idx)
            
        all_times.append(times)
        all_ys.append(ys)
    
    return all_times, all_ys


def make_time_distance_diagram(
    snapshot, 
    ax, 
    title='',
    show_planned=True,
    show_actual=True,
    actual_label='实际运行图',
    planned_label='计划时刻表',
    show_legend=False,
    highlight_train=None,
    delay_marker=True,
):
    """
    在给定的 ax 上绘制运行图
    
    风格对齐 MATLAB MetroSim2.m:
    - 虚线 = 计划时刻表 (OriTimeTable)
    - 实线 = 实际时刻表 (TimeArrive 交错格式)
    - Y轴: 站名
    - X轴: 时间(min)
    """
    M = snapshot.M
    
    # 生成交错格式数据
    planned_times, planned_ys = build_interleaved_timetable(snapshot, 'planned')
    
    if show_actual:
        actual_times, actual_ys = build_interleaved_timetable(snapshot, 'controlled')
    
    # 每条列车线使用不同颜色（tab10 色板）
    colors = plt.cm.tab10(np.linspace(0, 1, M))
    
    for i in range(min(M, 8)):  # 只画前8列车防止过密
        color = colors[i]
        
        # ── 计划时刻表（虚线，灰色浅一些） ──
        if show_planned and planned_times[i]:
            ax.plot(planned_times[i], planned_ys[i], 
                    '--', color=color * 0.7, linewidth=0.8, alpha=0.6,
                    label=planned_label if i==0 else '')
        
        # ── 受控时刻表（实线） ──
        if show_actual and actual_times[i]:
            linewidth = 2.0 if highlight_train is not None and i == highlight_train else 1.2
            alpha_val = 0.9 if highlight_train is None or i == highlight_train else 0.6
            ax.plot(actual_times[i], actual_ys[i],
                    '-', color=color, linewidth=linewidth, alpha=alpha_val,
                    label=actual_label if i==0 else '')
    
    # ── 晚点标记 ──
    if delay_marker:
        trig_train = snapshot.trigger_train
        trig_station = snapshot.trigger_station % N_DISPLAY
        # 从计划时刻表中提取晚点发生站的计划发车时间
        planned_arr = snapshot.planned_times[trig_train, 2*trig_station + 1]
        ax.plot(planned_arr, trig_station, 'rx', markersize=12, markeredgewidth=2.5, zorder=5)
        ax.annotate(f'晚点\n+{snapshot.initial_delay:.0f}min', 
                    (planned_arr, trig_station),
                    xytext=(planned_arr + 3, trig_station + 0.3),
                    fontsize=8, color='red', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.2))
    
    # ── 坐标轴设置 ──
    ax.set_xlabel('时间 (min)', fontsize=10)
    ax.set_ylabel('车站', fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold')
    
    # Y轴: 站名
    ax.set_yticks(range(N_DISPLAY))
    ax.set_yticklabels(STATIONS_DISPLAY, fontsize=9)
    ax.invert_yaxis()  # 第一站在上方
    
    # X轴范围
    max_time = np.max(snapshot.planned_times[:, :2*snapshot.projection_steps]) * 1.08
    ax.set_xlim(0, max_time)
    
    ax.grid(True, alpha=0.25, linestyle=':')
    
    if show_legend:
        ax.legend(fontsize=8, loc='lower right')
    
    # 加边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


# ════════════════════════════════════════════════════════
#  图2: 三场景运行图（并排三个子图）
# ════════════════════════════════════════════════════════

scenarios = [
    {
        'name': '(a) 紧急场景 — 反馈控制',
        'delay_train': 4,    # 列车5 (0-based)
        'delay_station': 2,  # 车站3 (0-based)
        'delay_min': 5.0,
        'control': 3.0,
        'algo': 'feedback',
        'c': 0.6,
    },
    {
        'name': '(b) 客流突变场景 — 迭代学习控制',
        'delay_train': 3,    # 列车4
        'delay_station': 1,  # 车站2 (天津)
        'delay_min': 8.0,
        'control': 2.0,
        'algo': 'ilc',
        'c': 0.4,
    },
    {
        'name': '(c) 常规场景 — 鲁棒模型预测控制',
        'delay_train': 4,    # 列车5
        'delay_station': 2,  # 车站3
        'delay_min': 5.0,
        'control': 2.5,
        'algo': 'rmpc',
        'c': 0.8,
    },
]

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

for idx, sc in enumerate(scenarios):
    ax = axes[idx]
    
    snap = project_timetable(
        delay_train_idx=sc['delay_train'],
        delay_station_idx=sc['delay_station'],
        delay_minutes=sc['delay_min'],
        control_signal=sc['control'],
        algorithm=sc['algo'],
        c_param=sc['c'],
        total_circles=2,
    )
    
    make_time_distance_diagram(
        snap, ax,
        title=sc['name'],
        show_planned=True,
        show_actual=True,
        show_legend=(idx == 2),  # 只在最右边图加图例
    )
    
    # 添加信息文本框
    info = (
        f"晚点: {sc['delay_min']:.0f} min\n"
        f"控制量: {sc['control']:.1f} min\n"
        f"c参数: {sc['c']:.1f}\n"
        f"延误减少: {snap.delay_reduction():.0f} min"
    )
    ax.text(0.98, 0.02, info, transform=ax.transAxes, fontsize=7.5,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.85))

fig.tight_layout()
path = os.path.join(OUTPUT_DIR, 'fig2_three_scenarios.pdf')
fig.savefig(path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'  ✅ 图2已重写: {path}  (含停站时间台阶线)')


# ════════════════════════════════════════════════════════
#  生成各场景单独的 PDF（给论文插入用）
# ════════════════════════════════════════════════════════
for idx, sc in enumerate(scenarios):
    fig, ax = plt.subplots(1, 1, figsize=(8, 4.5))
    
    snap = project_timetable(
        delay_train_idx=sc['delay_train'],
        delay_station_idx=sc['delay_station'],
        delay_minutes=sc['delay_min'],
        control_signal=sc['control'],
        algorithm=sc['algo'],
        c_param=sc['c'],
        total_circles=2,
    )
    
    make_time_distance_diagram(
        snap, ax,
        title=sc['name'],
        show_planned=True,
        show_actual=True,
        show_legend=True,
    )
    
    fig.tight_layout()
    letter = chr(ord('a') + idx)
    path_single = os.path.join(OUTPUT_DIR, f'fig2_{letter}_{sc["algo"]}.pdf')
    fig.savefig(path_single, dpi=300, bbox_inches='tight')
    plt.close(fig)

print('  ✅ 各场景单独PDF已生成')


# ════════════════════════════════════════════════════════
#  图4: 调度命令图 — 修复中文显示问题
# ════════════════════════════════════════════════════════
snap_rmpc = project_timetable(
    delay_train_idx=4, delay_station_idx=2,
    delay_minutes=5.0, control_signal=2.5,
    algorithm='rmpc', c_param=0.8, total_circles=2,
)

fig4, ax4 = plt.subplots(1, 1, figsize=(10, 6))
ax4.axis('off')

# 绘制调度命令（用 SimHei 确保中文显示）
_fp = fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=9)

cmd_text = (
    '===================== 列车晚点智能调度命令 =====================\n'
    '\n'
    '【基本信息】\n'
    '  车次：C2501次          车站：北京南站\n'
    '  晚点：5 分钟           原因：设备故障\n'
    '  方向：下行             时间：2026-06-01 12:00\n'
    '\n'
    '【控制策略】\n'
    '  算法：鲁棒模型预测控制 (RMPC)\n'
    '  选择原因：常规晚点场景，采用鲁棒模型预测控制\n'
    '\n'
    '【模糊客流参数】\n'
    '  参数 c：0.80（由当前时段客流模糊推理计算）\n'
    '\n'
    '【控制公式】\n'
    '  min a  s.t.  LMI半正定约束\n'
    '  U = K_opt * X （CVXPY/SCS求解）\n'
    '  控制信号值：2.5\n'
    '\n'
    '-------------- 区间运行时间调整方案 --------------\n'
    '  C2501次 | 北京南站 -> 武清 下行\n'
    '  标准区间运行时间：10 分钟\n'
    '  建议压缩量：      2.5 分钟\n'
    '  调整后运行时间：  7.5 分钟\n'
    '\n'
    '【执行说明】\n'
    '  请调度员向 C2501 次列车司机下达指令：\n'
    '  "在北京南站至武清区间压缩运行时间 2.5 分钟"\n'
    '\n'
    f'【延误统计】\n'
    f'  FCFS(无控制)总延误: {snap_rmpc.total_delay_fcfs:.0f} min\n'
    f'  受控后总延误:      {snap_rmpc.total_delay_controlled:.0f} min\n'
    f'  延误减少:          {snap_rmpc.delay_reduction():.0f} min ({snap_rmpc.delay_reduction_pct():.0f}%)\n'
)

ax4.text(0.5, 0.5, cmd_text, transform=ax4.transAxes, fontsize=9,
         verticalalignment='center', horizontalalignment='center',
         fontproperties=fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=9),
         bbox=dict(boxstyle='round', facecolor='#EBF5FB', edgecolor='#2980B9', lw=2))

ax4.set_title('图4: 智能体调度命令输出示例', fontsize=13, fontweight='bold',
              fontproperties=fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf'))

path4 = os.path.join(OUTPUT_DIR, 'fig4_dispatch_command.pdf')
fig4.savefig(path4, dpi=300, bbox_inches='tight')
plt.close(fig4)
print(f'  ✅ 图4已重写: {path4}')

# ── 保存命令文本 ──
txt_path = os.path.join(OUTPUT_DIR, 'fig4_dispatch_command.txt')
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(cmd_text)

# ════════════════════════════════════════════════════════
#  无控制(FCFS)对照图 — 对齐论文其他章节风格
# ════════════════════════════════════════════════════════
for idx, sc in enumerate(scenarios):
    # FCFS: control_signal=0, algorithm='fcfs'
    snap_fcfs = project_timetable(
        delay_train_idx=sc['delay_train'],
        delay_station_idx=sc['delay_station'],
        delay_minutes=sc['delay_min'],
        control_signal=0.0,
        algorithm='fcfs',
        c_param=sc['c'],
        total_circles=2,
    )
    
    # 受控版本
    snap_ctrl = project_timetable(
        delay_train_idx=sc['delay_train'],
        delay_station_idx=sc['delay_station'],
        delay_minutes=sc['delay_min'],
        control_signal=sc['control'],
        algorithm=sc['algo'],
        c_param=sc['c'],
        total_circles=2,
    )
    
    # ── FCFS 无控制图 ──
    fig_nc, ax_nc = plt.subplots(1, 1, figsize=(8, 4.5))
    make_time_distance_diagram(
        snap_fcfs, ax_nc,
        title=f'无控制策略 (FCFS) — {sc["algo"].upper()}场景',
        show_planned=True,
        show_actual=False,
        show_legend=True,
    )
    fig_nc.tight_layout()
    path_nc = os.path.join(OUTPUT_DIR, f'fig_fcfs_{sc["algo"]}.pdf')
    fig_nc.savefig(path_nc, dpi=300, bbox_inches='tight')
    plt.close(fig_nc)
    
    # ── 受控图（单张）──
    fig_ct, ax_ct = plt.subplots(1, 1, figsize=(8, 4.5))
    make_time_distance_diagram(
        snap_ctrl, ax_ct,
        title=f'{sc["name"]}',
        show_planned=True,
        show_actual=True,
        show_legend=True,
    )
    fig_ct.tight_layout()
    path_ct = os.path.join(OUTPUT_DIR, f'fig_ctrl_{sc["algo"]}.pdf')
    fig_ct.savefig(path_ct, dpi=300, bbox_inches='tight')
    plt.close(fig_ct)
    
    print(f'  ✅ 无控制/受控对照图已生成: {sc["algo"]}')


# ════════════════════════════════════════════════════════
#  图3: 多方法全线路延误对比（修复列车数/车站数一致性）
# ════════════════════════════════════════════════════════
# 使用统一场景进行四种方法对比
sc_base = scenarios[2]  # RMPC场景作为基准

methods = [
    ('FCFS', 0.0, 'fcfs', '#E74C3C'),
    ('反馈控制', 3.0, 'feedback', '#3498DB'),
    ('ILC', 2.0, 'ilc', '#2ECC71'),
    ('RMPC', 2.5, 'rmpc', '#9B59B6'),
    ('智能体(Agent)', 2.8, 'agent', '#F39C12'),
]

fig3, ax3 = plt.subplots(1, 1, figsize=(10, 5))

x = np.arange(N_DISPLAY)
width = 0.15

for mi, (name, ctrl, algo, color) in enumerate(methods):
    snap = project_timetable(
        delay_train_idx=sc_base['delay_train'],
        delay_station_idx=sc_base['delay_station'],
        delay_minutes=sc_base['delay_min'],
        control_signal=ctrl,
        algorithm=algo,
        c_param=sc_base['c'],
        total_circles=2,
    )
    
    # 按车站汇总各站总延误
    delay_by_station = np.zeros(N_DISPLAY)
    for j in range(snap.projection_steps):
        st_idx = j % N_DISPLAY
        train_idx = j // N_DISPLAY  # 圈数
        for ti in range(snap.M):
            delay = snap.delay_controlled[ti, j] if algo != 'fcfs' else snap.delay_fcfs[ti, j]
            delay_by_station[st_idx] += delay
    
    offset = (mi - 2) * width
    bars = ax3.bar(x + offset, delay_by_station, width, label=name, color=color, alpha=0.85)
    
    # 数据标签
    for bar in bars:
        if bar.get_height() > 0.5:
            ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                    f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=7)

ax3.set_xlabel('车站', fontsize=11)
ax3.set_ylabel('总延误 (min)', fontsize=11)
ax3.set_title('各方法在不同车站的总延误对比', fontsize=12, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(STATIONS_DISPLAY, fontsize=9)
ax3.legend(fontsize=8, loc='upper right')
ax3.grid(axis='y', alpha=0.3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

fig3.tight_layout()
path3 = os.path.join(OUTPUT_DIR, 'fig3_delay_comparison.pdf')
fig3.savefig(path3, dpi=300, bbox_inches='tight')
plt.close(fig3)
print(f'  ✅ 图3已重写: {path3}')


# ════════════════════════════════════════════════════════
#  图1: 架构图 — 修复纯英文标注
# ════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(1, 1, figsize=(10, 7))
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 8)
ax1.axis('off')
ax1.set_facecolor('white')

_fp_title = fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=14)
_fp_label = fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=10)
_fp_small = fm.FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=8)

ax1.set_title('智能调度代理系统架构', fontproperties=_fp_title, fontweight='bold', pad=20)

# ── 三层架构盒子 ──
layer_boxes = [
    {
        'xy': (1, 5.5), 'w': 8, 'h': 1.8,
        'color': '#D6EAF8', 'edge': '#2E86C1',
        'title': '第一层：感知层 (NLP Parser)',
        'items': [
            '输入：调度员自然语言描述',
            'Qwen-Turbo LLM → 结构化JSON提取',
            '输出：{train_number, station_name, delay_duration, delay_reason, is_urgent}'
        ]
    },
    {
        'xy': (1, 3.2), 'w': 8, 'h': 1.8,
        'color': '#D5F5E3', 'edge': '#27AE60',
        'title': '第二层：决策层 (Decision Engine)',
        'items': [
            '意图关键词匹配 → 算法智能选择',
            '紧急/快速 → 反馈控制  |  客流突变 → ILC  |  常规 → RMPC',
            '模糊规则推理 → 客流参数c'
        ]
    },
    {
        'xy': (1, 0.9), 'w': 8, 'h': 1.8,
        'color': '#FDEBD0', 'edge': '#E67E22',
        'title': '第三层：执行层 (Control Algorithms)',
        'items': [
            'Rescheduler: u = g*x_current + f*x_previous_next',
            'ILC: u_k = u_{k-1} + H1*(yP_{k-1} + F*A*DX_k)',
            'RMPC: min a  s.t.  LMI  (CVXPY/SCS)'
        ]
    }
]

for box in layer_boxes:
    rect = mpatches.FancyBboxPatch(
        box['xy'], box['w'], box['h'],
        boxstyle="round,pad=0.1",
        facecolor=box['color'], edgecolor=box['edge'],
        linewidth=2, alpha=0.9
    )
    ax1.add_patch(rect)
    
    ax1.text(box['xy'][0] + 0.3, box['xy'][1] + box['h'] - 0.3,
             box['title'], fontproperties=_fp_label, fontweight='bold', va='top')
    
    for li, item in enumerate(box['items']):
        ax1.text(box['xy'][0] + 0.5, box['xy'][1] + box['h'] - 0.7 - li * 0.45,
                 item, fontproperties=_fp_small, va='top')

# ── 箭头 ──
for y_from, y_to in [(5.5, 5.0), (3.2, 2.7)]:
    ax1.annotate('', xy=(5, y_to), xytext=(5, y_from),
                 arrowprops=dict(arrowstyle='->', color='#555555', lw=2.5))

# ── 输入输出标注 ──
ax1.text(5, 7.6, '输入: 调度员自然语言 (如 "C2503次列车在北京南站晚点5分钟")',
         fontproperties=_fp_label, ha='center', va='bottom',
         bbox=dict(boxstyle='round', facecolor='#FADBD8', edgecolor='#C0392B'))

ax1.text(5, 0.3, '输出: 区间运行时间调整调度命令',
         fontproperties=_fp_label, ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='#D5F5E3', edgecolor='#27AE60'))

# ── 输入箭头 ──
ax1.annotate('', xy=(5, 7.3), xytext=(5, 7.55),
             arrowprops=dict(arrowstyle='->', color='#C0392B', lw=2))

path1 = os.path.join(OUTPUT_DIR, 'fig1_architecture.pdf')
fig1.savefig(path1, dpi=300, bbox_inches='tight')
plt.close(fig1)
print(f'  ✅ 图1已重写: {path1}')


print('\n✅ 全部修复完成！')
print(f'   输出文件夹: {OUTPUT_DIR}/')
for f in sorted(os.listdir(OUTPUT_DIR)):
    sz = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    print(f'   {f:45s} ({sz/1024:.1f} KB)')
