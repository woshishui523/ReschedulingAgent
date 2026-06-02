function [Tr,Plat,TimeSchedule]=checkout(time,TimeSchedule,Plat,Tr)
%函数功能:检测是否有出站列车(满足最小行车间隔)，若有出站，并将站台和列车状态和站台人数置零,创建新的列车运行速度
for i=1:Tr.M
    if Tr.TrState(i)~=0 
        if (time-Tr.TrIn(i))>=Tr.TrStay(i)
            if checksafeinterval(time,i,Tr,Plat)
                TimeSchedule.TimeArrive(i,Tr.TrCir(i)*6+2*(Tr.TrPass(i)))=time;
                Tr=GetPlan2(time,i,Tr.TrState(i),TimeSchedule.TimeTable,Plat,Tr); %得到新的列车运行速度
                Plat.timelast(Tr.TrState(i))=time;
                Plat.PlatState(Tr.TrState(i))=0;
                Plat.PlatNum(Tr.TrState(i))=0;
                Tr.TrState(i)=0;
                Tr.TrIn(i)=0;
                Tr.TrStay(i)=0; 
            end
        end
    end
end