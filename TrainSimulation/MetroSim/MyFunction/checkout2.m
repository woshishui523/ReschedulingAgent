function [Tr,Plat,TimeSchedule,ylast]=checkout2(time,TimeSchedule,Plat,Tr,control,ylast)
%函数功能:检测是否有出站列车(满足最小行车间隔)，若有出站，并将站台和列车状态和站台人数置零,创建新的列车运行速度
for i=1:Tr.M
    if Tr.TrState(i)~=0 
        if (time-Tr.TrIn(i))>=Tr.TrStay(i)
            if checksafeinterval(time,i,Tr,Plat)
                if Tr.TrPass(i)==2&&i==1              
                    Tr.firstcircle=true;
                end
                Plat.timelast(Tr.TrState(i))=time;
                TimeSchedule.TimeArrive(i,Tr.TrCir(i)*Plat.N*2+2*(Tr.TrPass(i)))=time;
                TimeSchedule.TimeError(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))=time-TimeSchedule.BeginTimeTable(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i));
                if i==1 %第一圈列车一间隔误差为0，第二圈开始计数
                    if Tr.TrCir(i)==0
                        TimeSchedule.TimeHError(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))=0;
                    else
                        TimeSchedule.TimeHError(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))=time-TimeSchedule.BeginTimeTable(Tr.M,(Tr.TrCir(i)-1)*Plat.N+Tr.TrPass(i))-Plat.DepartInter;
                    end
                else 
                    TimeSchedule.TimeHError(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))=time-TimeSchedule.BeginTimeTable(i-1,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))-Plat.DepartInter;
                end
                if control.sort==0 %有时刻表控制
                    TimeSchedule=updataTimeTable2(i,Tr.TrPass(i),TimeSchedule,Tr,Plat,control);
                end
                if control.sort==1 %无时刻表控制
                    TimeSchedule=updataTimeTable3(i,Tr.TrPass(i),TimeSchedule,Tr,Plat,control);
                end
                [Tr,TimeSchedule]=GetPlan2(TimeSchedule,time,i,Tr.TrState(i),TimeSchedule.TimeTable,Plat,Tr); %得到新的列车运行速度
                Plat.PlatState(Tr.TrState(i))=0;
                Plat.PlatNum(Tr.TrState(i))=0;
                Tr.TrState(i)=0;
                Tr.TrIn(i)=0;
                Tr.TrStay(i)=0; 
%                 [ylast,ylast2,judge]=checkOver(Tr,ylast);6
%                 if judge==1
%                    disp('出现越行')
%                    ylast2
%                    ylast
%                 end
            end
        end
    end
end