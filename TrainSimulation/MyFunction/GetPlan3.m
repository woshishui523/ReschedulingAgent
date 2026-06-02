function [Tr,TimeSchedule]=GetPlan3(TimeSchedule,time,Tnum,Pnum,Plat,Tr)
syms tx;

aTr=Tr.TraTr;
T=TimeSchedule.RunTime(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum));
t=double(solve((aTr*tx*(T-tx)-Plat.PlatDis(Pnum)),tx));
t1=t(1,1);
t2=t(2,1);
v=aTr*t1;
b2=aTr*T;
Tr.TrFuc(1,Tnum)=aTr;
Tr.TrFuc(3,Tnum)=-aTr;
Tr.TrFuc(2,Tnum)=v;
Tr.TrFuc(4,Tnum)=b2;
Tr.TrCh(1,Tnum)=t1+time;
Tr.TrCh(2,Tnum)=t2+time;
Tr.TrBT(1,Tnum)=time;


end