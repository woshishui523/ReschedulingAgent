% 定义常量
d = 0.15;
a_val = 0.2; % 'a' 改名为 'a_val' 以避免与 lmivar 冲突
lamda = 0.35;

c1 = (1/2) * ((-a_val * (lamda + d) / (1 - a_val * (lamda + d))) + (-a_val * (lamda - d) / (1 - a_val * (lamda - d))));
d1 = (1/2) * ((-a_val * (lamda - d) / (1 - a_val * (lamda - d))) - (-a_val * (lamda + d) / (1 - a_val * (lamda + d))));
c2 = (1/2) * ((1 / (1 - a_val * (lamda + d))) + (1 / (1 - a_val * (lamda - d))));
d2 = (1/2) * ((1 / (1 - a_val * (lamda + d))) - (1 / (1 - a_val * (lamda - d))));

q = 1; % 目标函数中误差的权重
r = 1; % 目标函数中控制量的权重

% 定义矩阵维度
M = 16; % 总状态维度
N = 8;  % 控制输入维度

% 定义矩阵
A11 = diag(ones(1, M-N-1), 1);
A12 = zeros(M-N, N);
A12(M-N, 1) = 1;
A21 = zeros(N, M-N);
A21(N, 1) = c2;
A22 = diag(c1 * ones(1, N)) + diag(c2 * ones(1, N-1), 1);
A = [A11 A12; A21 A22];

B1 = zeros(M-N, N);
B2 = diag(c1 * ones(1, N));
B = [B1; B2];

C11 = zeros(M-N, M);
C121 = zeros(N, M-N);
C122 = diag(d1 * ones(1, N));
C1 = [C11; C121 C122];

C21 = zeros(M-N, M);
C221 = zeros(N, M-N);
C222 = diag(d2 * ones(1, N-1), 1);
C2 = [C21; C221 C222];

C3 = diag(d1 * ones(1, N));

L1 = zeros(M-N, N);
L2 = diag(ones(1, N));
L = [L1; L2];

Q = diag(q * ones(1, M));
R = diag(r * ones(1, N));
I1 = diag(ones(1, M));
IM = diag(ones(1, M));
IN = diag(ones(1, N));
P = diag(ones(1, M));

% 清除之前的LMI系统定义
setlmis([]);

% 定义LMI变量
a = lmivar(2, [1 1]); % 标量变量 'a'
Y = lmivar(2, [N M]); % 矩阵变量 'Y'
theta1 = lmivar(2, [1 1]); % 标量变量 'theta1'
theta2 = lmivar(2, [1 1]); % 标量变量 'theta2'
theta3 = lmivar(2, [1 1]); % 标量变量 'theta3'

% 定义LMI项
% 第一行
lmiterm([1 1 1 a], -1, inv(P));
lmiterm([1 1 2 a], 1, inv(P) * A'); 
lmiterm([1 1 2 -Y], 1, B');
lmiterm([1 1 3 a], 1, inv(P) * C1');
lmiterm([1 1 4 a], 1, inv(P) * C2');
lmiterm([1 1 5 -Y], 1, C3');
lmiterm([1 1 6 a], 1, inv(P));
lmiterm([1 1 7 -Y], 1, 1);

% 第二行
lmiterm([1 2 2 a], -1, inv(P)); 
lmiterm([1 2 2 theta1], 1, I1 * I1'); 
lmiterm([1 2 2 theta2], 1, I1 * I1'); 
lmiterm([1 2 2 theta3], 1, L * L');

% 第三行
lmiterm([1 3 3 theta1], -1, IM);

% 第四行
lmiterm([1 4 4 theta2], -1, IM);

% 第五行
lmiterm([1 5 5 theta3], -1, IN);

% 第六行
lmiterm([1 6 6 a], -1, inv(Q));

% 第七行
lmiterm([1 7 7 a], -1, inv(R));

% 获取LMI系统
lmisys = getlmis;

% 最小化目标函数
n = decnbr(lmisys);  % 系统决策变量个数
c = zeros(n, 1);  % 确定向量c的维数

% 构建目标函数c，使其最小化变量a
for j = 1:n
    if ismember(j, decinfo(lmisys, a))  % 检查变量a的决策变量索引
        c(j) = 1;  % 设置对应a的决策变量索引为1，其余为0
    end
end

% 最小化目标函数
[copt, xopt] = mincx(lmisys, c);

% 检查求解结果
if ~isempty(xopt)
    disp('LMI constraints are feasible.');
    % 提取解
    a_sol = dec2mat(lmisys, xopt, a);
    Y_sol = dec2mat(lmisys, xopt, Y);
    theta1_sol = dec2mat(lmisys, xopt, theta1);
    theta2_sol = dec2mat(lmisys, xopt, theta2);
    theta3_sol = dec2mat(lmisys, xopt, theta3);
    
    % 输出解
    disp('Optimal value of a:');
    disp(a_sol);
    disp('Optimal value of Y:');
    disp(Y_sol);
    disp('Optimal value of theta1:');
    disp(theta1_sol);
    disp('Optimal value of theta2:');
    disp(theta2_sol);
    disp('Optimal value of theta3:');
    disp(theta3_sol);
else
    disp('LMI constraints are infeasible.');
end
