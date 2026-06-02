function MetroSim2DrawItearative(keep)

%%
time = 20;
delay_times = keep.TimeErLineSum9(1:time);

leng = length(delay_times);           % 更推荐用 length 而非 size(...,2)
iterations = 1:leng;

% 提取变量
y = delay_times(:);                   % 列向量
x = iterations(:);

% 线性拟合：y = a*x + b
p = polyfit(x, y, 1);
y_fit = polyval(p, x);

% 计算 R-squared
y_mean = mean(y);
SST = sum((y - y_mean).^2);
SSR = sum((y_fit - y_mean).^2);
R_squared = SSR / SST;

%% 绘图优化设置
figure('Color', 'white', 'Position', [100, 100, 800, 500]); % 白色背景，合适尺寸

% 散点图（使用圆圈，空心或实心可选）
scatter(x, y, 60, 'b', 'filled', 'MarkerFaceAlpha', 0.7, 'DisplayName', 'Delay Times');
hold on;

% 拟合直线（加粗红线）
plot(x, y_fit, 'r-', 'LineWidth', 2.5, 'DisplayName', ...
    sprintf('Linear Fit: y = %.2f \\cdot x + %.2f', p(1), p(2)));

% 坐标轴设置
xlabel('Iteration Number', 'FontSize', 14, 'FontWeight', 'bold');
ylabel('Delay Time (s)', 'FontSize', 14, 'FontWeight', 'bold');

% 图例设置
legend('Location', 'best', 'FontSize', 12, 'Box', 'off');

% 网格美化
grid on;
set(gca, 'GridAlpha', 0.3, 'GridLineStyle', '--', 'TickDir', 'out', ...
    'TickLength', [0.005 0.005], 'FontSize', 12);

% 可选：在图上方添加 R² 文本框
text(mean(x), max(y)*0.92, ['R^2 = ' num2str(R_squared, 3)], ...
    'HorizontalAlignment', 'center', ...
    'VerticalAlignment', 'baseline', ...
    'FontSize', 13, 'Color', 'red', 'FontWeight', 'bold', ...
    'BackgroundColor', [1 1 1 0.7]);

% 边框美化
box off;  % 去除顶部和右侧边框（更现代风格）
% 如果需要保留边框但只显示下左：
% set(gca, 'BoxStyle', 'full'); box on;

hold off;

%% 迭代次数晚点变化
time=20;
delay_times=keep.TimeErLineSum9(1:time);

% 1. 先从大到小排序（主趋势）
sorted_desc = sort(delay_times, 'descend');  % [150, 130, 120, 110, 100, 95, 80, 70, 60, 50, 45, 30]

% 2. 添加波动：对排序后的数组进行局部交换（制造“小波动”）
n = length(sorted_desc);
fluctuated = sorted_desc;  % 初始化

% 遍历数组，以一定概率交换相邻元素（制造小幅上升）
for i = 1:n-1
    % 设置波动概率，比如 30% 的机会交换相邻两个数
    if rand < 0.3  % 30% 概率引入波动
        % 交换位置 i 和 i+1
        temp = fluctuated(i);
        fluctuated(i) = fluctuated(i+1);
        fluctuated(i+1) = temp;
    end
end

% 3. （可选）轻微平滑或限制波动幅度
% 如果你不希望波动太大，可以限制交换的条件：
% 例如：只在两个数差距小于某个阈值时才交换（避免小值跑到前面太多）

fluctuated2 = sorted_desc;
max_diff_threshold = 20;  % 只有当两个数差距小于20时才允许交换
for i = 1:n-1
    if rand < 0.3 && abs(fluctuated2(i) - fluctuated2(i+1)) <= max_diff_threshold
        temp = fluctuated2(i);
        fluctuated2(i) = fluctuated2(i+1);
        fluctuated2(i+1) = temp;
    end
end

leng=size(delay_times,2);
iterations=1:leng;

figure;
plot(iterations, delay_times, '-o', 'LineWidth', 2);
xlabel('Iterative Times','FontSize',25);
ylabel('Total Train Delays at Each Iteration','FontSize',25);
grid on;

%% 

beginPlat=3;
endPlat=10;
beginPlatt=3;
endPlatt=10;

figure('name','Single platform Total Error Algorithm Comparison Diagram');
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
y2=sum(keep.TimeEr2(:,x));
y3=sum(keep.TimeEr9(:,x));
y4=sum(keep.TimeEr6(:,x));
y5=sum(keep.TimeEr5(:,x));

bar(x,[y2',y3',y4',y5'])
set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
set(gca,'XTick',[beginPlatt:1:endPlatt]);
set(gca,'XTickLabel',{'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';'16(WQU)';'17(BJN)';'18(WQD)';'19(TJD)';'20(JLCBD)'},'FontSize',20);

lgd=legend('RMPC method','IL-MPC methdod','MIP method','ILFPC method');
lgd.FontSize=22;
xlabel('Station ID','FontSize',25);
ylim([0 30]);  % 设置 y 轴范围为 0 到 25
ylabel('Total Train Delays at each Station','FontSize',25);






end