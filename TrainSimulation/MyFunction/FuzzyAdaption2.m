clear all;
close all;
warning off;

%读取创建的自适应模型
a = readfis('fuzzpid'); 

%创建传递函数模型
sys = tf(133,[1,25,0]);

%将连续时间模型转换为离散时间模型
ts = 0.001;     %离散的采样时间
dsys = c2d(sys,ts,'z'); %z变换进行离散化为传函
[num,den] = tfdata(dsys,'v'); %访问传递函数数据
%num为分子系数的行向量 den为分母系数的行向量 【0 1】为 1为常数项 

%定义输入输出变量，误差变量，误差变化速度
u_1 = 0;
u_2 = 0;
y_1 = 0;
y_2 = 0;
e_1 = 0;
ec_1 = 0;

%定义比例系数
kp0 = 0;    

for k = 1:1:1000
    time(k) = k *ts;  %记录时间
    r(k) = 1;  %目标输出
    k_pid = evalfis([e_1,ec_1],a);%模糊化e_1,ec_1得到?kp,?ki 
    kp(k) = kp0 + k_pid(1);%修正kp,计算kp
    u(k) = kp(k)*e_1;%控制器输入
    y(k) = -den(2)*y_1-den(3)*y_2+ num(2)*u_1 + num(3)* u_2;%离散系统传递函数输出有时滞
    e(k) = r(k) - y(k);%获取误差
    u_2 = u_1;
    u_1 = u(k);
    y_2 = y_1;
    y_1 = y(k);
    ec(k) = e(k) - e_1;
    e_1 = e(k);
    ec_1 = ec(k);
end
%初始化并固定kp值
u_1 = 0;
u_2 = 0;
y_1 = 0;
y_2 = 0;
e_1 = 0;
ec_1 = 0;
kp0=kp(k);
kp2=kp0*ones(1,k);
for k = 1:1:1000
    time2(k) = k *ts;  %记录时间
    r(k) = 1;  %目标输出
    u2(k) = kp0*e_1;%控制器输入
    y2(k) = -den(2)*y_1-den(3)*y_2+ num(2)*u_1 + num(3)* u_2;%离散系统传递函数输出有时滞
    e(k) = r(k) - y(k);%获取误差
    u_2 = u_1;
    u_1 = u(k);
    y_2 = y_1;
    y_1 = y(k);
    ec(k) = e(k) - e_1;
    e_1 = e(k);
    ec_1 = ec(k);
end

%模糊自适应pid图像
figure(1);
subplot(3,1,1);
plot(time,r,'r',time,y,'b:','linewidth',2);
xlabel('time(s)');
ylabel('r,y');
legend('Ideal position','Practical position');
subplot(3,1,2);
plot(time,kp,'r','linewidth',2);
xlabel('time(s)');
ylabel('kp');
subplot(3,1,3);
plot(time,u,'r','linewidth',2);
xlabel('time(s)');
ylabel('Control input');

%直接采用自适应结果图像
figure(2);
subplot(3,1,1);
plot(time2,r,'r',time,y2,'b:','linewidth',2);
xlabel('time(s)');
ylabel('r,y');
legend('Ideal position','Practical position');
subplot(3,1,2);
plot(time2,kp2,'r','linewidth',2);
xlabel('time(s)');
ylabel('kp');
subplot(3,1,3);
plot(time2,u2,'r','linewidth',2);
xlabel('time(s)');
ylabel('Control input');
