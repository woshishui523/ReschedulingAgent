function u_real = LMIsolve1(M, N, x_real, control)
% 程序功能：在LMI约束下最小化线性目标

% 已知变量
d = control.ckd; % 目标到达速度变化范围
a = control.d; % 目标到达速度与停站时间关系
lamda = control.ckpoint; % 目标到达速度中心点
c1 = (1/2) * ((-a * (lamda + d) / (1 - a * (lamda + d))) + (-a * (lamda - d) / (1 - a * (lamda - d))));
d1 = (1/2) * ((-a * (lamda - d) / (1 - a * (lamda - d))) - (-a * (lamda + d) / (1 - a * (lamda + d))));
c2 = (1/2) * ((1 / (1 - a * (lamda + d))) + (1 / (1 - a * (lamda - d))));
d2 = (1/2) * ((1 / (1 - a * (lamda - d))) - (1 / (1 - a * (lamda + d))));
q = 0.1; % 目标函数中误差的权重
r = 0.1; % 目标函数中控制量的权重

%LMI中已知变量
%A M x M
A11=diag(ones(1,M-N-1),1);
A12=zeros(M-N,N);
A12(M-N,1)=1;
A21=zeros(N,M-N);
A21(N,1)=c2;
A22=diag(c1*ones(1,N))+diag(c2*ones(1,N-1),1);
A=[A11 A12;A21 A22];
%B M x N
B1=zeros(M-N,N);
B2=diag(c1.*ones(1,N));
B=[B1;B2];
%C1 M x M
C11=zeros(M-N,M);
C121=zeros(N,M-N);
C122=diag(d1*ones(1,N));
C1=[C11;C121 C122];
%C2 M x M
C21=zeros(M-N,M);
C221=zeros(N,M-N);
C222=diag(d2*ones(1,N-1),1);
C2=[C21; C221 C222];
%C3 N x N
C3=diag(d1.*ones(1,N));
%L M x N
L1=zeros(M-N,N);
L2=diag(1.*ones(1,N));
L=[L1;L2];
%常数定义
Q=diag(q.*ones(1,M));
R=diag(r.*ones(1,N));
I1=diag(ones(1,M));
IM=diag(ones(1,M));
IN=diag(ones(1,N));
P=diag(ones(1,M));
X=x_real;
% YALMIP 变量定义
Y = sdpvar(N, M, 'full');
Z = sdpvar(M, M, 'symmetric');
theta1 = sdpvar(1,1);
theta2 = sdpvar(1,1);
theta3 = sdpvar(1,1);
alpha = sdpvar(1, 1);

% 定义 LMI 约束
LMI = [];

% 主 LMI 约束
Phi1 = Z * A' + Y' * B';
Phi2 = -Z + alpha*theta1 * (I1 * I1') + alpha*theta2 * (I1 * I1') + alpha*theta3 * (L * L');
LMI = [LMI, [ -Z, Phi1, Z*C1', Z*C2', Y'*C3', Z, Y'; ...
               Phi1', Phi2, zeros(M, 4*M+N+2); ...
               C1*Z, zeros(M, M), -alpha*theta1*eye(M), zeros(M, 4*M+N+2); ...
               C2*Z, zeros(M, 2*M), -alpha*theta1*eye(M), zeros(M, 3*M+N+2); ...
               C3*Y, zeros(N, 3*M), -alpha*theta1*eye(N), zeros(N, 2*M+N+2); ...
               Z, zeros(M, 4*M), -alpha*inv(Q), zeros(M, N+1); ...
               Y, zeros(N, 4*M+M), -alpha*inv(R)] < 0];

% 额外的 LMI 约束
LMI = [LMI, [1, X'; X, Z] >= 0];
LMI = [LMI, [Ul^2, Y; Y', Z] >= 0];

% 设置求解器和选项
options = sdpsettings('solver', 'sedumi', 'verbose', 1);

% 求解 LMI 问题
sol = optimize(LMI, alpha, options);

% 检查求解结果
if sol.problem == 0
    % 提取解
    Y_opt = value(Y);
    Z_opt = value(Z);
    alpha_opt = value(alpha);
    
    % 计算状态反馈增益 K
    K = Y_opt / Z_opt;
    
    disp('求解成功！');
    disp('状态反馈增益矩阵 K:');
    disp(K);
else
    disp('求解失败，LMI 问题无解。');
    sol.info
end