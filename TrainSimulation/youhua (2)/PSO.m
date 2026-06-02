%{
时间：2023.1.17
代码功能：
采用粒子群算法计算VMD的超参数alpha和K
适应度函数为包络熵

%}
%% 载入数据（数据取消掉了时间列仅保留了数据列）
clc
clear 
close all
data=xlsread('pso.xlsx');
data=data(1:300)
%% 粒子群算法中的预设参数（参数的设置不是固定的，可以适当修改）
n = 30; % 粒子数量
narvs = 2; % 变量个数
c1 = 2;  % 每个粒子的个体学习因子，也称为个体加速常数
c2 = 2;  % 每个粒子的社会学习因子，也称为社会加速常数
ws = 0.9;  % 惯性权重最大值
we = 0.2;  % 惯性权重最小值
K = 30;  % 迭代的次数
% x1为 alpha x2为 K  x1 x2 为第一维度 第二维度 只能为整数
vmax = [10 0.8]; % 粒子的最大速度 由于范围不同速度也不同
x_lb = [1000 1]; % x的下界 
x_ub = [3000 10]; % x的上界

%% 初始化粒子的位置和速度
x = zeros(n,narvs);
for i = 1: narvs
    x(:,i) = x_lb(i) + (x_ub(i)-x_lb(i))*rand(n,1);    % 随机初始化粒子所在的位置在定义域内
    x=round(x);
end
v = -vmax + 2*vmax .* rand(n,narvs);  % 随机初始化粒子的速度（这里我们设置为[-vmax,vmax]）

%% 计算适应度(注意，因为是最小化问题，所以适应度越小越好)
fit = zeros(n,1);  % 初始化这n个粒子的适应度全为0
for i = 1:n  % 循环整个粒子群，计算每一个粒子的适应度
    fit(i) = Get_fitness(data,x(i,1),x(i,2));   % 调用Get_fitness函数来计算适应度
end 
pbest = x;   % 初始化这n个粒子迄今为止找到的最佳位置（是一个n*narvs的向量）
ind = find(fit == min(fit), 1);  % 找到适应度最小的那个粒子的下标
gbest = x(ind,:);  % 定义所有粒子迄今为止找到的最佳位置（是一个1*narvs的向量）

%% 迭代K次来更新速度与位置
fitnessbest = ones(K,1);  % 初始化每次迭代得到的最佳的适应度
for d = 1:K  % 开始迭代，一共迭代K次
    for i = 1:n   % 依次更新第i个粒子的速度与位置
        w = ws-(ws-we)*(d/K); %采用线性递减权重，开始利于全局搜索，后来利于局部搜索
        v(i,:) = w*v(i,:) + c1*rand(1)*(pbest(i,:) - x(i,:)) + c2*rand(1)*(gbest - x(i,:));  % 更新第i个粒子的速度
        % 如果粒子的速度超过了最大速度限制，就对其进行调整
        for j = 1: narvs
            if v(i,j) < -vmax(j)
                v(i,j) = -vmax(j);
            elseif v(i,j) > vmax(j)
                v(i,j) = vmax(j);
            end
        end
        x(i,:) = x(i,:) + v(i,:); % 更新第i个粒子的位置
        x=round(x);
        % 如果粒子的位置超出了定义域，就对其进行调整
        for j = 1: narvs
            if x(i,j) < x_lb(j)
                x(i,j) = x_lb(j);
            elseif x(i,j) > x_ub(j)
                x(i,j) = x_ub(j);
            end
        end
        fit(i) = Get_fitness(data,x(i,1),x(i,2));  % 重新计算第i个粒子的适应度
        if fit(i) < Get_fitness(data,pbest(i,1),pbest(i,2))   % 如果第i个粒子的适应度小于这个粒子迄今为止找到的最佳位置对应的适应度
           pbest(i,:) = x(i,:);   % 那就更新第i个粒子迄今为止找到的最佳位置
        end
        if  fit(i) < Get_fitness(data,gbest(1),gbest(2))  % 如果第i个粒子的适应度小于所有的粒子迄今为止找到的最佳位置对应的适应度
            gbest = pbest(i,:);   % 那就更新所有粒子迄今为止找到的最佳位置
        end
    end
    fitnessbest(d) = Get_fitness(data,gbest(1),gbest(2));  % 更新第d次迭代得到的最佳的适应度

end
%% 计算结果 当粒子群30 迭代次数10 时 alpha为1172 K为7
figure(2) 
plot(fitnessbest)  % 绘制出每次迭代最佳适应度的变化图
xlabel('迭代次数');
disp('最佳的位置是：'); disp(gbest)
disp('此时最优值是：'); Get_fitness(data,gbest(1),gbest(2))
disp('所有包络熵为：'); Get_fitness(data,gbest(1),gbest(2),1)


