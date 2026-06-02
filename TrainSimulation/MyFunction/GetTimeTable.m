function [firstTimetable,firstMPRT,firstPM,Ts,TsJ,Tz,conInformM,delayM]=GetTimeTable(Tnum,Pnum,timetable,delay)

% 任务1：完成timetable结构设计
% 任务2：输出根据我所使用站台进行修改
% 任务3：
%{ 

转化方法：
将整数转化为日期


%}
%168 x 1
if delay==1||delay==3
    fixMPRT=[7 8 12  12 8 7 14 14]; %一圈内所有站台间隔的运行时间
else
    fixMPRT=[8 7 14 14 7 8 12 12]; %一圈内所有站台间隔的运行时间
end
fixN=size(fixMPRT,2); %一圈的固定间隔数
timetable=timetable';
[row_num,train_num] = size(timetable);
station_num = (row_num+1)/2;
firstTimetable=zeros(row_num,train_num);
firstTimetable=timetable;
m=station_num/fixN;
n=mod(station_num,fixN);
firstMPRT=[];    % 区间最小纯运行时分
for i=1:m
    firstMPRT=[firstMPRT fixMPRT];
end
firstMPRT=[firstMPRT fixMPRT(1:n)];
departure = firstTimetable(2:2:end,:);
arrive = firstTimetable(1:2:end-1,:);
firstPM = departure-arrive;
firstPM(firstPM>0)=1;  % 停车矩阵 0：不停车 1：停车
during = firstTimetable(3:2:end,:)-departure(1:1:end-1,:);

Ts=2;                      % 最小停靠站时间
TsJ=6;                     % 交路站最小停站时间
Tz=1;                      % 最小追踪间隔2
Tqs=0;                     % 列车的起车附加时分
Tts=1;                     % 停车附加时分

if delay==1
    delayM=[
    15 11 8 5 2;   % 晚点时长
    2 3 4 5 6;   % 晚点列车
    1 1 1 1 1;   % 晚点车站
    1 1 1 1 1;   % 调度区段标识
    1 1 1 1 1;  %晚点类型：1到站晚点；2站间晚点
];
elseif delay==2
    delayM=[
    8 16.3 13.6 10.3 7 4;   % 晚点时长
    2 3 4 5 6 7;   % 晚点列车
    1 1 1 1 1 1;   % 晚点车站
    1 1 1 1 1 1;  % 调度区段标识
    1 1 1 1 1 1;  %晚点类型：1到站晚点；2站间晚点
];
else
    delayM=[
    50.0, 45.0, 40.0, 35.0, 30.0, 26.0, 21.0, 16.0, 11.0, 6.1,3.0;   % 晚点时长
    linspace(2,12,11);   % 晚点列车
    ones(1,11);   % 晚点车站
    ones(1,11);  % 调度区段标识
    ones(1,11);  %晚点类型：1到站晚点；2站间晚点
];

end


% 接续信息矩阵
% 接续上一个调度区段，0：该区段始发列车，1：接续第一个调度区段，2：接续第二个调度区段
% 接续上一个调度区段对应上一个区段的列车号，0：该区段始发列车
conInformM=[
    2 2 0 1 0 1 1 2 1 1 2
    1 2 0 3 0 4 5 6 6 7 7
];

end