function [firstTimetable,firstMPRT,firstPM,Ts,Tz,conInformM,delayM]=GetTimeTable(timetable,delay)

% 任务1：完成timetable结构设计
% 任务2：输出根据我所使用站台进行修改
% 任务3：
%{ 

转化方法：
将整数转化为日期


%}
%168 x 1
timetable=timetable';
[row_num,train_num] = size(timetable);
station_num = (row_num+1)/2;
firstTimetable=zeros(row_num,train_num);
firstTimetable=timetable;
 
firstMPRT=[14 7 8 10 10 8 7 14];    % 区间最小纯运行时分
departure = firstTimetable(2:2:end,:);
arrive = firstTimetable(1:2:end-1,:);
firstPM = departure-arrive;
firstPM(firstPM>0)=1;  % 停车矩阵 0：不停车 1：停车
during = firstTimetable(3:2:end,:)-departure;

Ts=1;                      % 最小停靠站时间
Tz=4;                      % 最小追踪间隔2
Tqs=2;                     % 列车的起车附加时分
Tts=1;                     % 停车附加时分


delayM=[
    130   % 晚点时长
    1   % 晚点列车
    1   % 晚点车站
    1   % 调度区段标识
    1   %晚点类型：1到站晚点；2站间晚点
];
delayM=delay; %导入时间
% 接续信息矩阵
% 接续上一个调度区段，0：该区段始发列车，1：接续第一个调度区段，2：接续第二个调度区段
% 接续上一个调度区段对应上一个区段的列车号，0：该区段始发列车
conInformM=[
    2 2 0 1 0 1 1 2 1 1 2
    1 2 0 3 0 4 5 6 6 7 7
];

end