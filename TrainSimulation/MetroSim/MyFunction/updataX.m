function [Tr,Plat,TimeSchedule]=updataX(time,k,TimeSchedule,Tr,Plat,control,noise)
%更新车辆的位置，包括判断是否到达车站，是否已到达总里程数

for i=1:Tr.M
    %更新位置
    
    Tr.TrX(i)=Tr.TrV(i)/k+Tr.TrX(i);
    if Tr.TrX(i)~=0
        Tr.first(i)=1;
    end
    if Tr.TrV(i)==0&&Tr.TrB(i)==true&&Tr.first(i)==1&&Tr.TrState(i)==0
        Tr.TrX(i)=getNearone(i,Tr,Plat);
    end
    
    %判断是否到达终点，若到达更新经过车站
    if Tr.TrX(i)>=Plat.Distance&&Tr.TrPass(i)==Plat.N
        
        if Plat.PlatState(1)~=0
            Tr.TrV(i)=0;  %将速度置为0
            Tr.TrFuc(1:4,i)=0;  %将车辆加速度置为0
        else
            [time,Tr]=putnoise(i,time,Tr,noise);
            Tr.TrX(i)=0;
            Tr.TrPass(i)=1;
            Plat.PlatState(1)=i;
            Tr.TrCir(i)=Tr.TrCir(i)+1;
            TimeSchedule.TimeTable(i,Tr.TrCir(i)*3+Tr.TrPass(i))=time;
            TimeSchedule.TimeArrive(i,Tr.TrCir(i)*6+2*Tr.TrPass(i)-1)=time;
            TimeSchedule.TimeError(i,Tr.TrCir(i)*3+Tr.TrPass(i))=time-TimeSchedule.TimeTable(i,Tr.TrCir(i)*3+1);
            TimeSchedule=updataTimeTable(i,Tr.TrPass(i),TimeSchedule,Tr,control);
            Tr.TrState(i)=1;
            Tr.TrIn(i)=time;
            Tr.TrV(i)=0;  %将速度置为0
            Tr.TrFuc(1:4,i)=0;  %将车辆加速度置为0
            %清空乘客，设定停站时间
            Tr.TrStay(i)=Plat.PlatNum(Tr.TrState(i))*Plat.P+Tr.Tmin;
            Plat.PlatNum(Tr.TrState(i))=0;
            TimeSchedule=updataTimePlan(i,Tr,TimeSchedule,Plat);

            continue;
        end
    end
    if Tr.TrPass(i)~=Plat.N     
        if Tr.TrX(i)>=Plat.PlatX(Tr.TrPass(i)+1)
            if Plat.PlatState(Tr.TrPass(i)+1)~=0
                Tr.TrV(i)=0;  %将速度置为0d
                Tr.TrFuc(1:4,i)=0;  %将车辆加速度置为0
            else
                [time,Tr]=putnoise(i,time,Tr,noise);
                Tr.TrX(i)=Plat.PlatX(Tr.TrPass(i)+1);
                Tr.TrPass(i)=Tr.TrPass(i)+1;
                Plat.PlatState(Tr.TrPass(i))=i;
                TimeSchedule.TimeError(i,Tr.TrCir(i)*3+Tr.TrPass(i))=time-TimeSchedule.TimeTable(i,Tr.TrCir(i)*3+Tr.TrPass(i));
                TimeSchedule.TimeTable(i,Tr.TrCir(i)*3+Tr.TrPass(i))=time;
                TimeSchedule.TimeArrive(i,Tr.TrCir(i)*6+2*Tr.TrPass(i)-1)=time;
                TimeSchedule=updataTimeTable(i,Tr.TrPass(i),TimeSchedule,Tr,control);
                
                Tr.TrState(i)=Tr.TrPass(i);
                Tr.TrIn(i)=time;
                Tr.TrV(i)=0;   %将速度置为0
                Tr.TrFuc(1:4,i)=0;   %将车辆加速度置为0 
                %设定停站时间(包括预测在站台期间来的乘客)
                Tr.TrStay(i)=(Plat.PlatNum(Tr.TrState(i))*Plat.P+Tr.Tmin)/(1-Plat.ck(Tr.TrPass(i))*Plat.P);
                TimeSchedule=updataTimePlan(i,Tr,TimeSchedule,Plat);

            end
        end
    end
end
