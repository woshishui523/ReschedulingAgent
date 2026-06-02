% 定义x轴数据点，这里以分钟为单位，从6:00(360分钟)到22:00(1320分钟)
start_time = 6*60; % 开始时间为6:00，转换成分钟
end_time = 22*60;  % 结束时间为22:00，转换成分钟
time_interval = 0.1*60; % 时间间隔保持为0.1小时(即6分钟)，转换成分钟

time_x = start_time:time_interval:end_time; % 使用分钟计算x轴数据点
x = time_x / 60; % 将分钟转换回小时表示，以便于绘图

% 定义七个隶属度函数的参数（与之前相同）
mf_params = {
    [6 6 9];     % NB - 最左边的水平线 + 三角形
    [6 9 12];    % NM
    [9 12 16];   % NS
    [12 16 19];   % PS
    [16 19 22];   % PM
    [19 22 22];   % PB
};

labels = {'NB', 'NM', 'NS', 'PS', 'PM', 'PB'};

figure;
hold on;

for i = 1:length(mf_params)
    mf = mf_params{i};
    y = trimf(x, mf);
    
    if i == 1
        y(x <= mf(2)) = 1;
    elseif i == length(mf_params)
        y(x >= mf(2)) = 1;
    end
    
    p = plot(x, y, 'LineWidth', 2);
    lineColor = get(p, 'Color');
    
    [~, idx] = max(y);
    
    if i == 1
        % NB 标签下移
        text(6.4, 1.02, labels{i}, ...
             'HorizontalAlignment','center',...
             'VerticalAlignment','bottom',...
             'FontSize',12,'Color',lineColor);
    else
        % 其他标签也统一设在下方固定高度
        if i==6
            text(x(idx)-0.4, 1.02, labels{i}, ...
             'HorizontalAlignment','center',...
             'VerticalAlignment','bottom',...
             'FontSize',12,'Color',lineColor);
        else
            text(x(idx), 1.02, labels{i}, ...
             'HorizontalAlignment','center',...
             'VerticalAlignment','bottom',...
             'FontSize',12,'Color',lineColor);
        end
        
    end
end

% 设置图形属性
xlabel('Time', 'FontSize', 14);         % 增大x轴标签字体
ylabel('Membership degree', 'FontSize', 14);  % 增大y轴标签字体

% 格式化x轴标签为时间格式
xticks(6:1:22); % 设置x轴刻度从6到22，每小时一个刻度
xticklabels(arrayfun(@(t) sprintf('%d:00', t), 6:1:22, 'UniformOutput', false)); % x轴标签格式化为时间

% 设置x轴刻度字体大小
ax = gca;
ax.FontSize = 8; % 整体字体变小，包括x轴和y轴数字
% 如果只想改x轴字体：
% ax.XAxis.FontSize = 10;

grid on;
ylim([-0.1 1.1]);
hold off;