function [Tr,Plat,TimeSchedule]=updataX2(time,k,TimeSchedule,Tr,Plat,control,noise)
%更新车辆的位置，包括判断是否到达车站，是否已到达总里程数
time=time/k;
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
            
            Tr.TrX(i)=0;
            Tr.TrPass(i)=1;
            Plat.PlatState(1)=i;
            Tr.TrCir(i)=Tr.TrCir(i)+1;
            [ptime,Tr]=putnoise(i,Tr.TrPass(i)+Plat.N*Tr.TrCir(i),k,time,Tr,noise);
            TimeSchedule.TimeTable(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))=ptime;
            TimeSchedule.TimeArrive(i,Tr.TrCir(i)*Plat.N*2+2*Tr.TrPass(i)-1)=ptime;
            Tr.TrState(i)=1;
            Tr.TrIn(i)=ptime;
            Tr.TrV(i)=0;  %将速度置为0
            Tr.TrFuc(1:4,i)=0;  %将车辆加速度置为0
            %清空乘客，设定停站时间
            Tr.TrStay(i)=Plat.PlatNum(Tr.TrState(i))*Plat.P+Tr.Tmin;
            
            if i==1&&Tr.TrCir(1)==0
                Tr.TrStay(i)=TimeSchedule.BeginTimeTable(i,Tr.TrPass(i))-TimeSchedule.TimeTable(i,Tr.TrPass(i));
            end
            continue;
        end
    end
    if Tr.TrPass(i)~=Plat.N     
        if Tr.TrX(i)>=Plat.PlatX(Tr.TrPass(i)+1)
            if Plat.PlatState(Tr.TrPass(i)+1)~=0
                Tr.TrV(i)=0;  %将速度置为0d
                Tr.TrFuc(1:4,i)=0;  %将车辆加速度置为0
            else
                
                Tr.TrX(i)=Plat.PlatX(Tr.TrPass(i)+1);
                Tr.TrPass(i)=Tr.TrPass(i)+1;
                Plat.PlatState(Tr.TrPass(i))=i;
                [ptime,Tr]=putnoise(i,Tr.TrPass(i)+Plat.N*Tr.TrCir(i),k,time,Tr,noise);
                TimeSchedule.TimeTable(i,Tr.TrCir(i)*Plat.N+Tr.TrPass(i))=ptime;
                TimeSchedule.TimeArrive(i,Tr.TrCir(i)*Plat.N*2+2*Tr.TrPass(i)-1)=ptime;
                Tr.TrState(i)=Tr.TrPass(i);
                Tr.TrIn(i)=ptime;
                Tr.TrV(i)=0;   %将速度置为0
                Tr.TrFuc(1:4,i)=0;   %将车辆加速度置为0 
                %设定停站时间(包括预测在站台期间来的乘客)
                Tr.TrStay(i)=(Plat.PlatNum(Tr.TrState(i))*Plat.P+Tr.Tmin)/(1-Plat.ck(Tr.TrPass(i))*Plat.P);

                if i==1&&Tr.TrCir(1)==0
                    Tr.TrStay(i)=TimeSchedule.BeginTimeTable(i,Tr.TrPass(i))-TimeSchedule.TimeTable(i,Tr.TrPass(i));
                end
            end
        end
    end
end
