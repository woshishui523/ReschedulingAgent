

% 参数设置
M = 16;
N = 8;
x_real = zeros(16, 1);
x_real(10) = 6;

control.ckd = 0.1;
control.d = 1;
control.ckpoint = 0.2;

% 调用函数
u_real = LMIsolve1(M, N, x_real, control);

% 显示结果
disp('解:');
disp(u_real);
