function [Tr,TimeSchedule]=Depart(num,TimeSchedule,Plat,Tr)
%函数功能：检测是否进行发车，若发车设定发车的速度函数,返回发车函数和切换时间和发车距离

if num~=0
    syms x;
    Tr.TrB(num)=true; %发车
    Tr=GetPlan(num,TimeSchedule,Plat,Tr); %得到新的计划表
    TimeSchedule=updataTimePlan2(num,Tr,TimeSchedule,Plat);
    
end