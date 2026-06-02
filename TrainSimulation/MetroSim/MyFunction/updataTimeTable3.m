function TimeSchedule=updataTimeTable3(Tnum,Pnum,TimeSchedule,Tr,Plat,control)
%更新到达车辆的时刻表，函数追求的目标是与目标（无名义时刻表场景）
if Tr.TrCir(Tnum)==0 %如果是第一圈的第一辆车直接将控制量设为0
    uik=0;
else
    if Pnum+Plat.N*Tr.TrCir(Tnum)==10&&Tnum==2
       z=1; 
    end
    if Tnum==1
        %Tnum1为前一辆车 Tnum2为前第二辆车
        Tnum1=Tr.M;
        Tnum2=Tr.M-1;
    elseif Tnum==2
        Tnum1=Tnum-1;
        Tnum2=Tr.M;
    else
        Tnum1=Tnum-1;
        Tnum2=Tnum-2;
    end
    if Tnum==1
        Pnum1=Pnum+1+Plat.N*(Tr.TrCir(Tnum)-1);
    else
        Pnum1=Pnum+1+Plat.N*Tr.TrCir(Tnum);
    end
    %计算控制率系数 
    h=-(1-control.ck(Pnum))^2/(control.q+(1-control.ck(Pnum))^2);
    g=-control.q/(control.q+(1-control.ck(Pnum))^2);
    f=(control.ck(Pnum)*control.q)/(control.q+(1-control.ck(Pnum))^2);
    %计算所需变量
    ui2k=TimeSchedule.TimeUk(Tnum1,Pnum1); %上一辆车的控制量
    yik=TimeSchedule.TimeHError(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum)); %时间间隔误差
    %计算前一站台
    
    yi2k=TimeSchedule.TimeHError(Tnum1,Pnum1); %前一辆车在下一个站台的误差
    if yi2k==0 %如果还未记录H误差，则进行预测
       yi2k=predictHError(Tnum1,Pnum1,TimeSchedule,Tr,Plat);
    end

    uik=(1+h)*ui2k+g*yik+f*yi2k;
end
%加入控制
begintime=ceil(TimeSchedule.BeginTimeTable(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum)+1)+uik);%此处加入+uik为加入控制
TimeSchedule.TimeTable(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum)+1)=ceil(arrivebybegin(Tr,Plat,Tnum,begintime,TimeSchedule.BeginTimeTable));
TimeSchedule.TimePlan(Tnum,2*(Pnum+1)-1+Plat.N*2*Tr.TrCir(Tnum))=TimeSchedule.TimeTable(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum)+1);
TimeSchedule.TimePlan(Tnum,2*(Pnum+1)+Plat.N*2*Tr.TrCir(Tnum))=begintime;
TimeSchedule.TimeUk(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum))=uik;
TimeSchedule.RunTime(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum))=TimeSchedule.RunTime(Tnum,Pnum+Plat.N*Tr.TrCir(Tnum))+uik;