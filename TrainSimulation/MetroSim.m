%{
作者：亢佳俊
代码功能：实现位置触发的环线地铁功能仿真
参考论文：Traffic Modeling and State Feedback Control for Metro Lines 
%}

%{
时间：2021.4.19 22.04 
待修改内容：增加平台等待时间，updataX中10行一辆车到站后连续进入 (已解决)
时间：2021.4.20 15.34
待修改内容：增加列车等车等待，修改可能的到500停止问题，减少乘客的影响（已解决）
时间：2021.4.21  9.45
待修改内容：车辆在403时刻时，列车进站后不再出站，并且进站距离过小为1500（已解决）
时间：2021 4.21  16.02
待修改内容：增加到站时间制作整体时刻表（已解决）
时间：2021 4.21  19.22
待修改内容；增加预计时间制作整体时刻比较表，增加随机扰动，询问师兄（已解决）
时间：2021 4.21  23.01
待修改内容：在对未来进行时刻表进行调节时出现下面情况，怀疑，updataTimeTable迭代公式有问题（已解决）
ans =

     0   101   201   301   401   504   600   700


ans =

     0   101   201   301   401   504   799   700
时间：2021 4.22
待修改内容：预测时刻表出现预测到达时间在发车时间之后情况，实际运行中添加最小停车时间,修改计划到站时间，加入干扰（未加入干扰）
时间：2021.4.29
待修改内容：时刻表出现在第三站迭代的问题，考虑可能是顺序和位置的转换问题
时间：2021.5.10
待修改内容：增加车辆之间安全距离限制，并设计达到安全距离如果运行，将误差加在运行过程中，运行验证结果(已解决)
时间：2021.5.11
待修改内容：增加车辆初始运行图，修改预测发车规则，修改人数清空时间
时间：2021.5.17
待修改内容：取消列车间安全距离，（以车站人数传播晚点），修改为改变发车时间。
思路：
1.怎么通过发车时间确定车辆速度
2.怎么预测发车时间
%}
clc
clear all;
%% 变量初始化部分

%系统的变量初始化,3个站台，5辆地铁
%可随自己使用情况进行修改
%此模型为M>N的情况。
N=3;  %车站数量 
M=5;  %列车数量 
P=0.01;  %设定车站人数与停留时间关系 
L=10000; %仿真步数
k=1; %仿真步数与秒之间相差倍数
aTr=5;  %列车固定加速度
Tmin=5; %列车在站台停留最小时间
noisetime=7; %设定列车收到干扰几站后进行下一次干扰
noisenum=1; %设定几辆车收到随机扰动
fisttrainT=100; %第一辆列车到达时间
internal=0; %此模型中车辆安全间隔为0，晚点通过车站人数来传播
ckspeed=2; %乘客增长速度
%车站初始化
Plat.N=N; %车站数量
Plat.P=P; %设定车站人数与停留时间关系
Plat.Distance=1600; %环线总距离 (需要自己输入)
Plat.PlatX=[1600 500 1100]; %车站位置 (需要自己输入)
Plat.ck=ckspeed*ones(1,Plat.N); %每个车站的乘客增加速度(需要自己输入)
Plat.PlatState=zeros(1,N); %车站状态（是否有车在站台,若有则为车序列号，若无则为0）
Plat.PlatNum=zeros(1,N); %车站等待人数
Plat.PlatDis=GetDis(Plat.PlatX,Plat.Distance);%车站间距离
Plat.timelast=zeros(1,N); %车站上一辆车离开时间
Plat.Tinterval=internal;%车辆之间发车安全间隔

%控制率参数设计
control.p=5; %时间延误的评价系数
control.q=6; %调度大小的评价系数
control.ck=Plat.ck; %每个车站的乘客增加速度

%地铁车辆初始化
Tr.M=M;
Tr.Tmin=Tmin; %地铁停留最短时间
Tr.TraTr=aTr; %地铁加速度
Tr.TrX=zeros(1,M);%地铁所在位置
Tr.TrV=zeros(1,M);%地铁当前速度
Tr.TrA=zeros(1,M);%地铁当前加速度
Tr.TrB=false(1,M);%地铁是否发车
Tr.TrFuc=zeros(4,M);%地铁运行的函数 y=a1x;y=k;y=a2x+b2;
Tr.TrCh=zeros(2,M);%地铁加速、匀速、减速切换时间
Tr.TrBT=zeros(1,M);%地铁的发车时间,相对于前一个车站
Tr.TrPass=ones(1,M);%地铁经过的上一个车站，若未发车为0
Tr.TrCir=zeros(1,M);%地铁已跑圈数
Tr.TrState=zeros(1,M);%地铁状态是否在在站内1为在站内，0为在站外
Tr.TrStay=zeros(1,M);%地铁在站内停留时间
Tr.TrIn=zeros(1,M);%地铁进站时间，若未进站为0
Tr.first=zeros(1,M);%地铁是否刚离开车站
Tr.noisetime=noisetime;%设定收到干扰几站后进行下一次干扰
Tr.noise=setnoisenum(noisenum,Tr.M);%地铁是否进行干扰(-1为不加干扰，0为加入干扰)

%时刻表初始化
Steps=L/k;
TimeSchedule.TimeTable=[
0:100:100*Steps;  %0 100 + 20 120 100 220 + 23 243   L 500  100   
10:100:10+100*Steps;
20:100:20+100*Steps;
30:100:30+100*Steps;
40:100:40+100*Steps;
];%用于确定列车在每段的速度,一行为一辆列车
TimeSchedule.OriTimeTable=createOriTimeTable(Plat.Tinterval,fisttrainT,Steps,Plat,Tr); %创建计划运行图
TimeSchedule.TimeArrive=[zeros(5,1),TimeSchedule.TimeTable(:,1),zeros(M,Steps-1)];%记录列车实际到达
TimeSchedule.TimePlan=[zeros(5,1),TimeSchedule.TimeTable(:,1:2),zeros(M,Steps-2)];%记录列车预计到达时间
TimeSchedule.TimeError=zeros(M,Steps);%[TimeSchedule.TimeTable(:,1),zeros(M,Steps-1)];%记录时间误差
TimeSchedule.TimeUk=zeros(M,Steps);%记录调节时间

Tr.TrFuc(1,:)=aTr;
Tr.TrFuc(3,:)=-aTr;%设定列车加速度 
H=100; %车辆之间相距的安全距离
T=10;  %车辆发车之间的相距时间

%白噪声序列
noise=abs(sqrt(10)*randn(1,L));%白噪声序列,均值为0,方差为10
%% 仿真模拟过程

for i=1:L
    time(i)=i;
    if i==107
        y=1;
    end
    Plat=updataPassenger(Plat); %更新车站人数
    [Tr,Plat,TimeSchedule]=updataX(i,k,TimeSchedule,Tr,Plat,control,noise); %更新列车当前位置
    if checkallout(Tr) %初始车站发车操作
        num=checkBegin(k*i,T,Tr); %获取出站列车
        [Tr,TimeSchedule]=Depart(num,TimeSchedule,Plat,Tr); %进行发车
    end
    [Tr,Plat,TimeSchedule]=checkout(k*i,TimeSchedule,Plat,Tr);
    Tr=getspeed(k*i,Tr);
    
end


%% 单个列车运行展示部分展示部分

ArriveNum=getlength(TimeSchedule.TimeArrive);
for i=1:M
    figure(i);
    time=createTime(ArriveNum(i));
    plot(TimeSchedule.TimeArrive(i,1:length(time)),time,'r-');
    hold on
    plot(TimeSchedule.TimePlan(i,1:length(time)),time,'g-');
    xlabel('t'); ylabel('x(t)');    
end
%% 实际运行图与实时调度运行图对比展示部分

    cm = colormap('Lines');
    mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'|';'-'];
    figure('name','Train Time-Distance Diagram');
    xlabel('Time (s)'); ylabel('Location x(t)');
    title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i));
    plot(TimeSchedule.TimeArrive(i,1:length(time)),time,...
          'Color', cm(i,:),'LineWidth', 2);
    
    plot(TimeSchedule.TimePlan(i,1:length(time)),time,...
        'Color', cm(i,:).*[0.8, 0.8, 0.8], 'LineWidth', 1, ...
        'LineStyle','--', 'Marker', mkr(mod(i,14)+1));
end

%% 实际运行图与初始计划调度运行图对比展示部分
    figure('name','Train Time-Distance BeginDiagram');
    xlabel('Time (s)'); ylabel('Location x(t)');
    title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i));
    plot(TimeSchedule.TimeArrive(i,1:length(time)),time,...
          'Color', cm(i,:),'LineWidth', 2);
    
    plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
        'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
        'LineStyle','-.', 'Marker', mkr(mod(i,14)+2));
end

%% 列车运行误差展示部分
   
    figure('name','Delays');
    xlabel('Location x(t)'); ylabel('Delay (s)');
    title('Delays');
    subplot(M,1,1);
for i=1:M
    subplot(M,1,i);
    title(['Delays (train = ' num2str(i) '), solid Departure, dash Arrival']);
    hold on;
    time=createTime(ArriveNum(i));
    % actual arrival 
    arrdepAct=TimeSchedule.TimeArrive(i,1:length(time));
    % planned arrival
    arrdepPlan=TimeSchedule.TimePlan(i,1:length(time));
    delayDep=arrdepAct(1:2:end-1)-arrdepPlan(1:2:end-1);
    delayArr=arrdepAct(2:2:end)-arrdepPlan(2:2:end);
    plot(time(1:2:end-1), delayDep,'-',  'Color', cm(i,:), 'Marker', mkr(mod(i,14)+1));
    plot(time(2:2:end), delayArr,'--','Color', cm(i,:),'Marker', mkr(mod(i,14)+1),...
        'LineWidth', 1.25);
end



