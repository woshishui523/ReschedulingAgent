%{
作者：亢佳俊
代码功能：实现位置触发的环线城际高铁功能仿真（修改发车时间）
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
mpc

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
时间：2021.5.28
待修改内容：第五站出现过调行为，发车比到站预计时间早（可能控制率有问题）,15之后没有车到达探究原因
待修改内容：替换为我需要的时刻表，
时间：2021.6.7
待修改内容：修改后出现越行情况，考虑通过调整表，分析越行
时间：2021.9.6
待修改内容：由于初始化时第一辆列车经过各站台的时间较长积累乘客较多会对后面列车造成干扰，现采用较低级方案解决此问题
（第一辆列车停留时间在第一圈数直接采用计划停留时间），更好的解决方案待放发布论文后再提交
时间：2021.9.7
待修改内容：列车在第十站台的到站时间发生较大调换，怀疑有可能是序号问题或者调度大小问题
时间：2021.9.17
待修改内容：列车目前干扰方式为列车到站后在到达时间中添加延迟时间。
时间：2021.10.11
待修改内容：由于干扰的加入是直接修改了到站时间但是预计发车时间并没有修改，或者说那里时间出现了bug
（现在考虑先才有此系统改用较小的误差，但发车时间有问题下午考虑考虑）
时间：2021.11.6
待修改内容：将时刻表改为参考京津城际高铁线路，但运行过程出现越行，可能原因调度尺度过大，
圈之间转换出现问题
时间：2021.11.9
待修改内容；经检查控制率出现问题，控制率过大，先不知道原因，待进一步解决。
时间：2021.11.11
待修改内容：高铁时刻表指定停站时间有问题，列车运行时间反向
已解决：因为运行过程运算出现问题
待修改内容：列车时刻表出现问题，没有实现循环
时间：2021.11.12 上午
待修改内容：高铁运行出现间断运行情况，考虑可能为运行时间过短，可通过运行计划debug
时间：2021.11.12 晚20.37
修改内容：之前问题由于调度时间导致不足以设计响应的根，因此在计划设计中添加最低时间间隔要求
时间：2021.11.13 晚17。00
待修改内容；控制算法出现问题，导致控制量过大，建议进行修改。
现在：检测控制量大小
时间：2021。11.14 14.00
待修改内容：为何无控制算法误差不会传播，晚点量的添加是否有问题，重新设计误差指标
待修改内容：将目标运行改为按原有计划运行—观察误差传播—
时间：2021.11.15
添加误差检验图
参数确定：车站人数与停留时间关系  
加入不同干扰测试结果，无调度+加入调度+加入无名义时刻表调度
图像：
热力图（不同场景对应晚点情况） 误差传播图（不同场景的对应的晚点列车数量）
误差图（不同场景的误差列车的传播图像）列车间隔误差图 列车运行图（三种场景）
时间：2022.4.7
待修改内容：
1.在交路站添加多余侧站，添加运行时间计算方式（与前一列车发车时间之间间隔产生乘客所增加的停留时间）
2.分别在上下行中添加晚点，并且缩短图像覆盖时间
3.将晚点变化和间隔晚点图修改（参考程师姐的论文）
时间：2022.4.10
待修改内容：
1.修改晚点时间（改为在两个交路站发生较大延误），限定控制率的范围使慢点可以进行传播
2.修改作图程序，改为车站列车晚点和车站列车控制率以及车站列车间隔晚点和车站列车控制率
3.第一列车出现到站后不进站镜框
%}

%% 变量初始化部分
%根据京津城际高铁线路进行仿真
%本文所有仿真采用km min（方便取整，不然取小时会出现好多小数）为单位
%{
1无调度方法 2带时刻表反馈控制 3无时刻表反馈控制 4鲁棒模型预测控制 
5迭代学习模型预测控制 6优化方法控制 7人工调度
%}
controller_list=[6 4 2]; %控制器选择
times=15; %重复圈数
stayvar.controller_num=size(controller_list,2);
stayvar.controller_list=Repeat_experiment(controller_list,times);
cnum=size(stayvar.controller_list,2);
%初始化一些记录变量
keep4.TimeSumEr1=[];keep4.TimeSumEr2=[];keep4.TimeSumEr3=[];
keep4.TimeSumEr4=[];keep4.TimeSumEr5=[];keep4.TimeSumEr6=[];
keep4.TimeSumEr7=[];
for controller=1:1:cnum
%选择控制器
stayvar.controller=controller; %记录目前控制器
%进行仿真
clc
close all
%清除所要数据以外数据进行下一次循环
clearvars -except keep* z stayvar*
%系统的变量初始化,3个站台，5辆城际高铁
%可随自己使用情况进行修改
%此模型为M>N的情况。
noiseState=2; %1为列车2在站台2晚点15，不加干扰，只存在客流不确定干扰
N=8;  %车站数量 (TrInter Plat.PlatX)
M=18;  %列车数量 ()
P=0.05;  %设定车站人数与停留时间关系 
L=4000; %仿真步数
k=10; %仿真步数与分钟之间相差倍数 即现实一分钟等于k倍仿真时长
aTr=6;  %列车固定加速度 km/min^2 2km/min
modv=6; %设定巡航速度 km/min
Tmin=2; %列车在站台停留最小时间
TSmin=4; %列车在交路站最短停留时间
noisetime=3; %设定列车收到干扰几站后进行下一次干扰
noisenum=1; %设定几辆车收到随机扰动 
fisttrainT=100; %第一辆列车到达时间
internal=0; %此模型中车辆安全间隔为0，晚点通过车站人数来传播
ckpoint=0.7; %乘客增长速度变化中心点
ckd=0.35; %乘客增长速度变化范围
ckspeed=0.5; %乘客增长速度(不能取1，会影响控制率计算)
ArriveH=5; %列车的到到时间间隔 '
DepartArriveH=2; %列车的发到时间间隔
MinRunTime=[14 7 8 12 12 8 7 14]; %列车的最小运行时间
% 生成5个介于8和15之间的随机整数
% MinRunTime = randi([8, 16], 1, N/2);
% MinRunTime=[MinRunTime flip(MinRunTime,2)];
% TrInter=MinRunTime+4;
% TrInter(N/2:1:N/2+1)=TrInter(N/2:1:N/2+1)+3;
TrInter=[19 11 13 19 14 13 11 24]; %到站时间间隔（需要自己输入，在交路站添加了多余停留时间）！！！??????  
H=sum(TrInter)/M; %车辆发车时间的自然间隔
Npast=ceil(L/k/H+2); %仿真经过站台数(将环形路网拉直后的数量)

%为保证时刻表的周期性，时间间隔之和为H*列车数

stayFirst=linesub(TrInter); 
TrInter=matrixRshift(TrInter,2); % 车辆在站台间的运行时间 ???????????????????????
stayFirst=matrixRshift(stayFirst,2); % 第一辆车在第一圈站台间的运行时间
stayH=Tmin+H*P*ckspeed; % H时间间隔的停留时间
stayHS=TSmin+H*P*ckspeed; % 交路站中H时间间隔的停留时间
stayFirst=Tmin+stayFirst*P*ckspeed; %H时间间隔的停留时间
checkover=0; % 是否开启检测越行

%车站初始化
Plat.N=N; %车站数量
Plat.P=P; %设定车站人数与停留时间关系

%需要自己输入部分 ！！！！
Plat.Distance=332; %环线总距离 (需要自己输入) 
Plat.PlatX=[332 84 120 140 166 192 212 248]; %车站位置 (需要自己输入)
[Plat.ck,stayvar]=GetCk(ckpoint,ckd,N,stayvar); %每个车站的乘客增加速度(需要自己输入)
Plat.ckpoint=ckpoint; %乘客增加速度中间值
% Plat.ck=0.25*ones(1,N);

Plat.PlatState=zeros(1,N); %车站状态（是否有车在站台,若有则为车序列号，若无则为0）
Plat.PlatNum=zeros(1,N); %车站等待人数
Plat.PlatDis=GetDis(Plat.PlatX,Plat.Distance);%车站间距离
Plat.timelast=zeros(1,N); %车站上一辆车离开时间
Plat.Tinterval=internal;%车辆之间发车安全间隔
Plat.DepartInter=H; %自然发车时间间隔
Plat.TimeD=zeros(1,N); %站台最近一辆列车的发车时间
Plat.TimeA=zeros(1,N); %站台最近一辆列车的到站时间
Plat.ArriveH=ArriveH; %列车的到到时间间隔
Plat.DepartArriveH=DepartArriveH; %列车的发到时间间隔
Plat.TrWait=zeros(1,N); %站台1的等候进站列车因为遍历方向是反的

%控制率参数设计 需要自己设定
control.q=0.8; %调度大小的评价系数 保证稳定性需要q>c（1-c）
control.p=1-control.q; %时间延误的评价系数
control.ck=Plat.ck; %每个车站的乘客增加速度
control.d=P; %乘客到达速率与停站时间关系
control.ckd=ckd; %乘客到达速率变化范围
control.ckpoint=ckpoint; %乘客到达速率中心点
control.sort=stayvar.controller_list(stayvar.controller); %控制器选择
control.timeerror=control.d*ckd; %变化引起的客流变化范围
control.optimization=0; %为短暂实现优化策略只调度列车一次

%城际高铁车辆初始化
Tr.M=M; %城际高铁车辆数量 
Tr.ModV=modv; %城际高铁固定巡航速度
Tr.Tmin=Tmin; %城际高铁停留最短时间
Tr.TSmin=TSmin; %城际高铁交路停留最短时间
Tr.TraTr=aTr; %城际高铁加速度
Tr.TrX=zeros(1,M);%城际高铁所在位置
Tr.TrV=zeros(1,M);%城际高铁当前速度
Tr.TrA=zeros(1,M);%城际高铁当前加速度
Tr.TrB=false(1,M);%城际高铁是否发车
Tr.TrFuc=zeros(4,M);%城际高铁运行的函数 y=a1x;y=k;y=a2x+b2;
Tr.TrCh=zeros(2,M);%城际高铁加速、匀速、减速切换时间
Tr.TrBT=zeros(1,M);%城际高铁的发车时间,相对于前一个车站
Tr.TrPass=ones(1,M);%城际高铁经过的上一个车站，若未发车为0
Tr.TrCir=zeros(1,M);%城际高铁已跑圈数
Tr.TrState=zeros(1,M);%城际高铁状态是否在在站内,在站内显示站台数，0为在站外
Tr.TrStay=zeros(1,M);%城际高铁在站内停留时间
Tr.TrIn=zeros(1,M);%城际高铁进站时间，若未进站为0
Tr.first=zeros(1,M);%城际高铁是否刚离开车站
Tr.noisetime=noisetime;%设定收到干扰几站后进行下一次干扰
Tr.noise=setnoisenum(noisenum,Tr.M);%城际高铁是否进行干扰(-1为不加干扰，0为加入干扰)
Tr.firstcircle=false;%判断是否是第一圈需要进行预测特别操作
Tr.Staytime=zeros(1,M);%列车停留时间
Tr.TrAT=zeros(1,M);%城际高铁的预计到站时间,相对于前一个车站


%时刻表初始化
Steps=Npast*2;
TimeSchedule.H=H; %车站发车时间的自然间隔
TimeSchedule.TimeInter=TrInter; %设置车站间到的运行时间
TimeSchedule.BeginTimeTable=createbeginTimeSchedule(H,M,Npast,TimeSchedule.TimeInter,Plat.N);%createbeginTimeTable(Plat.DepartInter,fisttrainT,Steps,Plat,Tr); %创建发车时间计划表
TimeSchedule.TimeTable=createarriveTimeSchedule(Plat.N,TimeSchedule.BeginTimeTable,stayFirst,M,Npast,N,stayH,stayHS,Plat.N);%用于确定列车在每段的速度,一行为一辆列车
TimeSchedule.TimeArrive=[zeros(Tr.M,1),TimeSchedule.BeginTimeTable(:,1),zeros(M,Steps-1)];%记录列车实际到达
TimeSchedule.TimePlan=[zeros(Tr.M,1),TimeSchedule.BeginTimeTable(:,1),TimeSchedule.BeginTimeTable(:,2),zeros(M,Steps-2)];%记录列车预计到达时间（此表可变化）
TimeSchedule.OriTimeTable=createOriTimeTable(Tr.M,Plat.N,TimeSchedule.BeginTimeTable,Steps,stayH,stayHS); %创建计划运行图(保持不变)
TimeSchedule.ChangeOriTimeTable=TimeSchedule.OriTimeTable;%createbeginTimeTable(Plat.DepartInter,fisttrainT,Steps,Plat,Tr); %创建发车时间计划表
TimeSchedule.TimeError=zeros(M,Steps);%[TimeSchedule.TimeTable(:,1),zeros(M,Steps-1)];%记录时间误差
TimeSchedule.TimeYHError=zeros(M,Steps);%记录与优化后时刻表的时间误差
TimeSchedule.TimeHError=zeros(M,Steps);%记录与时间间隔偏差
TimeSchedule.TimeUk=zeros(M,Steps);%记录调节时间
TimeSchedule.RunTime=createRunTime(TimeSchedule.OriTimeTable); %列车的实际运行时间
TimeSchedule.MinRunTime=MinRunTime; %列车在各个区间的最小运行时间
TimeSchedule.Optimization=0;

Tr.TrFuc(1,:)=aTr;
Tr.TrFuc(3,:)=-aTr;%设定列车加速度
H=100; %车辆之间相距的安全距离

%白噪声序列
noise=abs(sqrt(20)*randn(1,L));%白噪声序列,均值为0,方差为10
noise=noiseState;%用于控制不同控制率场景的晚点设置情况
checktime=[700]; %测试时间点
% end
%% 仿真模拟过程（环线无名义时刻表）

for i=1:L
    checkTime(i,checktime,Tr,Plat,TimeSchedule,control)
    Plat=updataPassenger(Plat,k); %更新车站人数
    [Tr,Plat,TimeSchedule]=updataX2(i,k,TimeSchedule,Tr,Plat,control,noise); %更新列车当前位置
    if checkallout(Tr) %初始车站发车操作
        num=checkBegin(i/k,Plat.DepartInter,Tr); %获取出站列车
        [Tr,TimeSchedule,Plat]=Depart2(num,TimeSchedule,Plat,Tr); %进行发车
        ylast=sortline(Tr); %进行列车排序
    else
        %检测是否出现越行
        [ylast,ylast2,judge]=checkOver(Tr,ylast);
        if judge==1
           disp('出现越行')
        end
    end
    [Tr,Plat,TimeSchedule,ylast,control]=checkout2(i/k,TimeSchedule,Plat,Tr,control,ylast);
    Tr=getspeed(i/k,Tr,k);
end


    %% 实际运行图与初始计划调度运行图对比展示部分
figure('name','Train Time-Distance BeginDiagram');
set(gca,'FontSize',15);
set(gca,'XLim',[0 250]);
set(gca,'YLim',[0 166]);
set(gca,'YTick',[0 84 120 140 166]);% Y轴的记号点 
set(gca,'YTicklabel',{'1(BJN)','2(WQ)','3(TJ)','4(JLCB)','5(BH)'});% Y轴的记号
cm = colormap('Lines');
ArriveNum=getlength(TimeSchedule.TimeArrive);
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
xlabel('Time (min)'); ylabel('Station ID x(t)');
title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i),Plat.N,Plat.PlatX);
    plot(TimeSchedule.TimeArrive(i,1:length(time)),time,...
          'Color', cm(i,:),'LineWidth', 2);

    plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
        'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
        'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
end


    %% 采集保存数据
    
ArriveNum=floor(min(getlength(TimeSchedule.TimeArrive))/2);
TimeDelayH=createDelayH(Tr.M,ArriveNum,TimeSchedule.TimeArrive,Plat.DepartInter);
switch stayvar.controller_list(stayvar.controller)
    case 1
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-no.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-no.jpg');  %保存fig3窗口的图像
        %保存数据
        keep4.TimePnum1=ArriveNum;
        keep4.TimeUk1=TimeSchedule.TimeUk; 
        keep4.TimeEr1=TimeSchedule.TimeError;
        keep4.TimeHEr1=TimeSchedule.TimeHError;
        keep4.TimeSumEr1=[keep4.TimeSumEr4 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
    case 2
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-with.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-with.jpg');  %保存fig3窗口的图像
        keep4.TimePnum2=ArriveNum;
        keep4.TimeUk2=TimeSchedule.TimeUk;
        keep4.TimeEr2=TimeSchedule.TimeError;
        keep4.TimeHEr2=TimeSchedule.TimeHError;
        keep4.TimeSumEr2=[keep4.TimeSumEr4 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
    case 3
        keep4.TimeEr2=TimeSchedule.TimeError;
        keep4.TimeHEr2=TimeSchedule.TimeHError;
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-nowith.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-nowith.jpg');  %保存fig3窗口的图像
        keep4.TimePnum3=ArriveNum;
        keep4.TimeUk3=TimeSchedule.TimeUk;
        keep4.TimeEr3=TimeSchedule.TimeError;
        keep4.TimeHEr3=TimeSchedule.TimeHError;
        keep4.TimeSumEr3=[keep4.TimeSumEr4 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
    case 4
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-RMPC.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-RMPC.jpg');  %保存fig3窗口的图像
        keep4.TimePnum4=ArriveNum;
        keep4.TimeUk4=TimeSchedule.TimeUk;
        keep4.TimeEr4=TimeSchedule.TimeError;
        keep4.TimeHEr4=TimeSchedule.TimeHError;
        keep4.TimeSumEr4=[keep4.TimeSumEr4 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
    case 5
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-IMPC.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-IMPC.jpg');  %保存fig3窗口的图像
        keep4.TimePnum5=ArriveNum;
        keep4.TimeUk5=TimeSchedule.TimeUk;
        keep4.TimeEr5=TimeSchedule.TimeError;
        keep4.TimeHEr5=TimeSchedule.TimeHError;
        keep4.TimeSumEr5=[keep4.TimeSumEr4 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
    case 6
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-MIP.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-MIP.jpg');  %保存fig3窗口的图像
        keep4.TimePnum6=ArriveNum;
        keep4.TimeUk6=TimeSchedule.TimeUk;
        keep4.TimeEr6=TimeSchedule.TimeError;
        keep4.TimeHEr6=TimeSchedule.TimeHError;
        keep4.TimeSumEr6=[keep4.TimeSumEr4 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
    case 7
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-MIP.fig');  %保存fig3窗口的图像
        saveas(1,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\RunSit-MIP.jpg');  %保存fig3窗口的图像
        keep4.TimePnum7=ArriveNum;
        keep4.TimeUk7=TimeSchedule.TimeUk;
        keep4.TimeEr7=TimeSchedule.TimeError;
        keep4.TimeHEr7=TimeSchedule.TimeHError;
        keep4.TimeSumEr7=[keep4.TimeSumEr7 sum(TimeSchedule.TimeError(2:5,1:15),'all')];
end
    
end


% MetroSim2Draw(keep4);
% MetroSim2DrawMPC(keep4);
%反馈控制率
% saveas(2,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ErrorSitWithTimetable.fig'); 
% saveas(2,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ErrorSitWithTimetable.jpg');  
% saveas(3,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ControlSitWithTimetable.fig'); 
% saveas(3,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ControlSitWithTimetable.jpg');
% saveas(4,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\HErrorSitWithoutTimetable.fig'); 
% saveas(4,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\HErrorSitWithoutTimetable.jpg');
% saveas(5,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ControlSitWithoutTimetable.fig'); 
% saveas(5,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ControlSitWithoutTimetable.jpg');
%鲁棒模型预测
% saveas(2,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ErrorSitWithTimetable.fig'); 
% saveas(2,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ErrorSitWithTimetable.jpg');  
% saveas(3,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ControlSitWithTimetable.fig'); 
% saveas(3,'D:\Desktop\Folder\MyNASFile\CRH项目群\英文期刊\仿真结果\场景四\ControlSitWithTimetable.jpg');

%% 列车运行时间误差展示部分
   
% figure('name','Delays');
% xlabel('Location x(t)'); ylabel('Delay (s)');
% title('Delays');
% for i=1:M
%     subplot(M,1,i);
%     title(['Delays (train = ' num2str(i) '), solid Departure, dash Arrival']);
%     hold on;
%     time=createTime(ArriveNum(i),Plat.N);
%     % actual arrival 
%     arrdepAct=TimeSchedule.TimeArrive(i,1:length(time));
%     % planned arrival
%     arrdepPlan=TimeSchedule.TimePlan(i,1:length(time));
%     delayDep=arrdepAct(1:2:end-1)-arrdepPlan(1:2:end-1);
%     delayArr=arrdepAct(2:2:end)-arrdepPlan(2:2:end);
%     plot(time(1:2:end-1), delayDep,'-',  'Color', cm(i,:), 'Marker', mkr(mod(i,13)+1));
%     plot(time(2:2:end), delayArr,'--','Color', cm(i,:),'Marker', mkr(mod(i,13)+1),...
%         'LineWidth', 1.25);
%     
% end
%% 保存数据用于作图
% 场景一：一辆列车出现给定小晚点（误差图、误差传播图一个采样点、热力图对其他列车影响、列车间隔误差图）
%无控制 TimeUk为控制率大小 TimeEr为误差大小 TimeHEr为间隔误差大小
% keep1.TimePnum1=ArriveNum/2;
% keep1.TimeUk1=TimeSchedule.TimeUk;
% keep1.TimeEr1=TimeSchedule.TimeError;
% keep1.TimeHEr1=TimeDelayH;
%有控制（有名义时刻表）
% keep1.TimePnum2=ArriveNum;
% keep1.TimeUk2=TimeSchedule.TimeUk;
% keep1.TimeEr2=TimeSchedule.TimeError;
% keep1.TimeHEr2=TimeDelayH;
%有控制（无名义时刻表）
% keep1.TimePnum3=ArriveNum;
% keep1.TimeUk3=TimeSchedule.TimeUk;
% keep1.TimeEr3=TimeSchedule.TimeError;
% keep1.TimeHEr3=TimeDelayH;
% 场景二：一辆列车出现给定大晚点（误差图、误差传播图一个采样点、热力图对其他列车影响、列车间隔误差图）
%无控制 TimeUk为控制率大小 TimeEr为误差大小 TimeHEr为间隔误差大小
% keep2.TimePnum1=ArriveNum;
% keep2.TimeUk1=TimeSchedule.TimeUk;
% keep2.TimeEr1=TimeSchedule.TimeError;
% keep2.TimeHEr1=TimeDelayH;
% %有控制（有名义时刻表）
% keep2.TimePnum2=ArriveNum;
% keep2.TimeUk2=TimeSchedule.TimeUk;
% keep1.TimeEr2=TimeSchedule.TimeError;
% keep1.TimeHEr2=TimeDelayH;
% %有控制（无名义时刻表）
% keep2.TimePnum3=ArriveNum;
% keep2.TimeUk3=TimeSchedule.TimeUk;
% keep2.TimeEr3=TimeSchedule.TimeError;
% keep2.TimeHEr3=TimeDelayH;
% % 场景三：两辆列车在同一站台发生晚点（）
% %无控制 TimeUk为控制率大小 TimeEr为误差大小 TimeHEr为间隔误差大小
% keep3.TimePnum1=ArriveNum;
% keep3.TimeUk1=TimeSchedule.TimeUk;
% keep3.TimeEr1=TimeSchedule.TimeError;
% keep3.TimeHEr1=TimeDelayH;
% %有控制（有名义时刻表）
% keep3.TimePnum2=ArriveNum;
% keep3.TimeUk2=TimeSchedule.TimeUk;
% keep3.TimeEr2=TimeSchedule.TimeError;
% keep3.TimeHEr2=TimeDelayH;
% %有控制（无名义时刻表）
% keep3.TimePnum3=ArriveNum;
% keep3.TimeUk3=TimeSchedule.TimeUk;
% keep3.TimeEr3=TimeSchedule.TimeError;
% keep3.TimeHEr3=TimeDelayH;
% % 场景四：三辆列车在不同站台发生晚点
% %无控制 TimeUk为控制率大小 TimeEr为误差大小 TimeHEr为间隔误差大小
% keep4.TimePnum1=ArriveNum;
% keep4.TimeUk1=TimeSchedule.TimeUk;
% keep4.TimeEr1=TimeSchedule.TimeError;
% keep4.TimeHEr1=TimeDelayH;
% %有控制（有名义时刻表）
% keep4.TimePnum2=ArriveNum;
% keep4.TimeUk2=TimeSchedule.TimeUk;
% keep4.TimeEr2=TimeSchedule.TimeError;
% keep4.TimeHEr2=TimeDelayH;
% %有控制（无名义时刻表）
% keep4.TimePnum3=ArriveNum;
% keep4.TimeUk3=TimeSchedule.TimeUk;
% keep4.TimeEr3=TimeSchedule.TimeError;
% keep4.TimeHEr3=TimeDelayH;
% % 场景五：五辆列车有三辆在同一站台，两辆在不同站台发生晚点
% %无控制 TimeUk为控制率大小 TimeEr为误差大小 TimeHEr为间隔误差大小
% keep5.TimePnum1=ArriveNum;
% keep5.TimeUk1=TimeSchedule.TimeUk;
% keep5.TimeEr1=TimeSchedule.TimeError;
% keep5.TimeHEr1=TimeDelayH;
% %有控制（有名义时刻表）
% keep5.TimePnum2=ArriveNum;
% keep5.TimeUk2=TimeSchedule.TimeUk;
% keep5.TimeEr2=TimeSchedule.TimeError;
% keep5.TimeHEr2=TimeDelayH;
% %有控制（无名义时刻表）
% keep5.TimePnum3=ArriveNum;
% keep5.TimeUk3=TimeSchedule.TimeUk;
% keep5.TimeEr3=TimeSchedule.TimeError;
% keep5.TimeHEr3=TimeDelayH;


%% 单个列车运行展示部分展示部分
% 


% for i=1:M
%     figure(i);
%     time=createTime(ArriveNum(i));
%     plot(TimeSchedule.TimeArrive(i,1:length(time)),time,'r-');
%     hold on
%     plot(TimeSchedule.TimePlan(i,1:length(time)),time,'g-');
%     xlabel('t'); ylabel('x(t)');    
% end

%{
%% 实际运行图与实时调度运行图对比展示部分（开放线路）

    cm = colormap('Lines');
    mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
    figure('name','Train Time-Distance Diagram');
    xlabel('Time (s)'); ylabel('Location x(t)');
    title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i));
    tlength=length(time);
     plot(TimeSchedule.TimeArrive(i,1:tlength),time(1:tlength),...
          'Color', cm(i,:),'LineWidth', 2);
    
     plot(TimeSchedule.TimePlan(i,1:tlength),time(1:tlength),...
        'Color', cm(i,:).*[0.8, 0.8, 0.8], 'LineWidth', 1, ...
        'LineStyle','--', 'Marker', mkr(mod(i,13)+PN1));
    lable=Createlabel(length(time)/2,3);
    
%     set(gca,'YTickLabel',{'1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4B','4C','5A','5B','5C'});
end
%}
%% 实际运行图与实时调度运行图对比展示部分（闭环线路）
% ArriveNum=getlength(TimeSchedule.TimeArrive);
% cm = colormap('Lines');
% mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
% figure('name','Train Time-Distance Diagram');
% xlabel('Time (s)'); ylabel('Location x(t)');
% title('实际调度图');
% for i=1:M
%     hold on;
%     time=createTime(ArriveNum(i),Plat.N);%此处time代表列车数，
%     plot(TimeSchedule.TimeArrive(i,1:length(time)),time,...
%           'Color', cm(i,:),'LineWidth', 2);
%     
%     plot(TimeSchedule.TimePlan(i,1:length(time)),time,...
%         'Color', cm(i,:).*[0.8, 0.8, 0.8], 'LineWidth', 1, ...
%         'LineStyle','--', 'Marker', mkr(mod(i,13)+1));
%     lable=Createlabel(length(time)/2,3);
%     
% %     set(gca,'YTickLabel',{'1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4B','4C','5A','5B','5C'});
% end



%% 实际运行图与初始计划调度运行图对比展示部分
% figure('name','Train Time-Distance BeginDiagram');
% xlabel('Time (s)'); ylabel('Location x(t)');
% title('初始调度图');
% for i=1:M
%     hold on;
%     time=createTime(ArriveNum(i),Plat.N);
%     plot(TimeSchedule.TimeArrive(i,1:length(time)),time,...
%           'Color', cm(i,:),'LineWidth', 2);
%     
%     plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
%         'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
%         'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
%     
% end
% saveas(3,'D:\Desktop\Folder\MyNasFile\CRH项目群\英文期刊\仿真结果\场景一\RunSit-nowith.fig');  %保存fig3窗口的图像
% saveas(3,'D:\Desktop\Folder\MyNasFile\CRH项目群\英文期刊\仿真结果\场景一\RunSit-nowith.jpg');  %保存fig3窗口的图像


%% 列车时间间隔误差展示部分
% 
% figure('name','HDelays');
% xlabel('Location x(t)'); ylabel('Delay (s)');
% title('HDelays');
% time=linspace(1,ArriveNum(Tr.M),ArriveNum(Tr.M));
% timeDelayH=createDelayH(Tr.M,time,TimeSchedule.TimeArrive,Plat.DepartInter);
% plot(time,timeDelayH,'-')



%% 检查部分
% TimeSchedule.BeginTimeTable(:,1:8)
% TimeSchedule.TimeTable(:,1:8)
% TimeSchedule.TimeArrive(:,1:18)
% TimeSchedule.TimePlan(:,1:44)
% TimeSchedule.TimeError(:,1:18)
% TimeSchedule.OriTimeTable(:,1:18)
% TimeSchedule.TimeUk(:,1:18)
% TimeSchedule.RunTime(:,1:8)

