function TimeSchedule=updataTimeTable(Tnum,Pnum,TimeSchedule,Tr,control)
%更新到达车辆的时刻表，函数追求的目标是与目标
g=(control.q+2*control.p)/((control.ck(Pnum)-1)*(control.p+control.q+1));
f=control.ck(Pnum)*(control.p+control.q)/((control.ck(Pnum)-1)*(control.p+control.q+1));
if Tnum-1==0
    uik=-g*TimeSchedule.TimeError(Tnum,Pnum+3*Tr.TrCir(Tnum));
else
    if TimeSchedule.TimeError(Tnum-1,Pnum+1+3*Tr.TrCir(Tnum))~=0 %如果以满足算法计算要求
        uik=-g*TimeSchedule.TimeError(Tnum,Pnum+3*Tr.TrCir(Tnum))+f*TimeSchedule.TimeError(Tnum-1,Pnum+1+3*Tr.TrCir(Tnum));
    else %未满足需进行预测误差
        uik=-g*TimeSchedule.TimeError(Tnum,Pnum+3*Tr.TrCir(Tnum))+f*TimePredict(Tnum-1,Pnum+1+3*Tr.TrCir(Tnum),TimeSchedule);
    end
end
TimeSchedule.TimeTable(Tnum,Pnum+3*Tr.TrCir(Tnum)+1)=TimeSchedule.TimeTable(Tnum,Pnum+3*Tr.TrCir(Tnum)+1)+uik;
TimeSchedule.TimePlan(Tnum,2*(Pnum+1)-1+6*Tr.TrCir(Tnum))=TimeSchedule.TimeTable(Tnum,Pnum+3*Tr.TrCir(Tnum)+1);
TimeSchedule.TimeUk(Tnum,Pnum+Tr.TrCir(Tnum))=uik;
    