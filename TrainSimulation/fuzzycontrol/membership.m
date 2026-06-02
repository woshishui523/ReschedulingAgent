% 定义x轴数据点
x = 6:2:22;

% 对于最左边的隶属度函数，我们用一个左无限函数(linsmf)连接到一个三角形函数(trimf)
left_membership = [0 0 1]; % 左无限函数的参数
left_triangle = [6 8 10]; % 三角形函数的参数

% 对于最右边的隶属度函数，我们先定义一个三角形函数，然后在其右侧添加一个水平线
right_triangle = [16 18 20];
right_membership_value = ones(size(x)); % 右侧水平线

% 中间的五个三角形隶属度函数
middle_triangles = {[8 10 12], [10 12 14], [12 14 16], [14 16 18], [16 18 20]};

% 绘制图形
figure;
hold on;
plot(x, linsmf(x, left_membership), 'LineWidth', 2); % 最左边的函数
for i = 1:length(middle_triangles)
    plot(x, trimf(x, middle_triangles{i}), 'LineWidth', 2); % 中间的三角形函数
end
% 绘制最右边的函数
plot([right_triangle(2) : 2 : x(end)], right_membership_value(1:length([right_triangle(2):2:x(end)])), 'LineWidth', 2);

% 设置图形属性
xlabel('X-axis');
ylabel('Membership');
title('Membership Functions');
grid on;
ylim([0 1.2]);
legend('Left Infinite to Triangle', 'Middle Triangles', 'Right Horizontal Line', 'Location', 'NorthWest');
hold off;