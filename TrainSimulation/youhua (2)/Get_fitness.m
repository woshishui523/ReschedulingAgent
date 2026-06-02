function minEntropy=Get_fitness(data,alpha_0,K_0,varargin)
% 适应度函数,最小化各VMD分量的局部包络熵
% 对于VMD样品参数进行设置
nvarargin = length(varargin);
alpha = alpha_0; % 适度的带宽约束/惩罚因子
tau = 0; % 噪声容限（没有严格的保真度执行）
K = K_0; % 分解的模态数，
DC = 1; % 无直流部分
init = 1; % omegas的均匀初始化
tol = 1e-7;  %收敛准则，可以适当调低 

[u,~,~]=VMD(data, alpha, tau, K, DC, init, tol); %计算VMD

minEntropy=Get_Entropy(u,K,nvarargin); %计算包络熵

  

end