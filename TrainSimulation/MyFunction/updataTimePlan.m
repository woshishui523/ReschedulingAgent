function TimeSchedule=updataTimePlan(i,Tr,TimeSchedule,Plat)
%函数功能：更新计划发车时刻表，考虑前一辆车，并且遵循最小安全时间间隔规则设计
num=cirsub(i,Tr.M);
%检测在本区段前面是否有别的车
%% 如果前方本区段有车并且在区段运行 最终要检测前方车的发车与本车的发车间隔与安全间距
if Tr.TrPass(i)==Tr.TrPass(num)&&Tr.TrB(num)==true&&Tr.TrX(i)<Tr.TrX(num)%此情况为前方列车在区段运行
    %如果前面有车（计划发车时间=计划到达时间+(计划到达时间-上一辆车预测下一站台计划发车时间)*人数增长速度*人数与时间关系+最小停留时间）/（1-人数增长速度*人数与时间关系）
    %最后进行取整
    TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)-1)+...
        ((TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)-1)-TimeSchedule.TimePlan(num,Tr.TrCir(num)*6+2*(Tr.TrPass(num)+1)))*Plat.P*Plat.ck(ciradd(Tr.TrPass(i),Plat.N))+Tr.Tmin)/...
        (1-Plat.ck(ciradd(Tr.TrPass(i),Plat.N))*Plat.P);
    TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=ceil(TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)));
    if TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))-TimeSchedule.TimePlan(num,Tr.TrCir(num)*6+2*(Tr.TrPass(num)+1))<Plat.Tinterval
        TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=TimeSchedule.TimePlan(num,Tr.TrCir(num)*6+2*(Tr.TrPass(num)+1))+Plat.Tinterval;
    end
    return
end
%% 如果前方车站有车并且在站台停车 最终要检测前方车的发车与本车的发车间隔与安全间距
if ciradd(Tr.TrPass(i),Plat.N)==Tr.TrPass(num)&&Tr.TrB(num)==true&&Tr.TrX(i)<Tr.TrX(num)&&Tr.Trstate==1%此情况为前方列车在站台停车
    %如果站台有车（计划发车时间=计划到达时间+(计划到达时间-上一辆车当前站台计划发车时间)*人数增长速度*人数与时间关系+最小停留时间）/（1-人数增长速度*人数与时间关系）
    %最后进行取整
    TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)-1)+...
        ((TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)-1)-TimeSchedule.TimePlan(num,Tr.TrCir(num)*6+2*Tr.TrPass(num)))*Plat.P*Plat.ck(ciradd(Tr.TrPass(i),Plat.N))+Tr.Tmin)/...
        (1-Plat.ck(ciradd(Tr.TrPass(i),Plat.N))*Plat.P);
    TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=ceil(TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)));
    if TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))-TimeSchedule.TimePlan(num,Tr.TrCir(num)*6+2*Tr.TrPass(num))<Plat.Tinterval
        TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=TimeSchedule.TimePlan(num,Tr.TrCir(num)*6+2*Tr.TrPass(num))+Plat.Tinterval;
    end
    return
end
%% 如果前方区段无车 最终要检测站台已过车辆与本车的发车间隔与安全间距做对比
TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)-1)+...
    (((TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)-1)-Tr.TrIn(i))*Plat.ck(ciradd(Tr.TrPass(i),Plat.N))+Plat.PlatNum(ciradd(Tr.TrPass(i),Plat.N)))*Plat.P+Tr.Tmin)/...
    (1-Plat.ck(ciradd(Tr.TrPass(i),Plat.N))*Plat.P);
%向上取整，发车时间只能取整
TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=ceil(TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1)));
if TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))-Plat.timelast(ciradd(Tr.TrPass(i),Plat.N))<Plat.Tinterval 
    TimeSchedule.TimePlan(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)+1))=Plat.timelast(ciradd(Tr.TrPass(i),Plat.N))+Plat.Tinterval;
end

