function [time]=createRunTime(oritime)
%函数功能：用于创建用于列车运行的时间间隔时刻表
%加入控制即在时间间隔上进行修改
for i=1:((size(oritime,2)-1)/2)
    time(:,i)=oritime(:,2*i+1)-oritime(:,2*i) ;
end