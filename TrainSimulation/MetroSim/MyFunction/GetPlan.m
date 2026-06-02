function [Tr,TimeSchedule]=GetPlan(num,TimeSchedule,Plat,Tr)
%函数功能：用于初始状态发车运行
syms tx;

aTr=Tr.TraTr;
T=TimeSchedule.TimeTable(num,2)-TimeSchedule.BeginTimeTable(num,1);
t=double(solve((aTr*tx*(T-tx)-Plat.PlatDis(1)),tx));
t1=t(1,1);
t2=t(2,1);
v=aTr*t1;
b2=aTr*T;
Tr.TrFuc(2,num)=v;
Tr.TrFuc(4,num)=b2;
Tr.TrFuc(1,num)=aTr;
Tr.TrFuc(3,num)=-aTr;
Tr.TrCh(1,num)=t1+TimeSchedule.BeginTimeTable(num,1);
Tr.TrCh(2,num)=t2+TimeSchedule.BeginTimeTable(num,1);
Tr.TrBT(1,num)=TimeSchedule.BeginTimeTable(num,1);
TimeSchedule.TimePlan(num,3)=TimeSchedule.TimeTable(num,2);
TimeSchedule.TimePlan(num,4)=TimeSchedule.BeginTimeTable(num,2);
Tr.TrPass(1,num)=1;