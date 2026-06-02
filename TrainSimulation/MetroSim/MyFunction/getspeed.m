function Tr=getspeed(t,Tr,k)
%函数功能：得到当前时刻列车运行速度
t=t+1/k;%预测的是下一步的速度，同时避免速度为0与更新位移中起冲突
for i=1:Tr.M
    if Tr.TrB(i)==false
         Tr.TrV(i)=0;
         continue
    end
    if t<Tr.TrCh(1,i)
        Tr.TrV(i)=Tr.TrFuc(1,i)*(t-Tr.TrBT(1,i));
    elseif t>=Tr.TrCh(1,i)&&t<=Tr.TrCh(2,i)
        Tr.TrV(i)=Tr.TrFuc(2,i);
    else
        Tr.TrV(i)=Tr.TrFuc(3,i)*(t-Tr.TrBT(1,i))+Tr.TrFuc(4,i);
    end
    if  Tr.TrV(i)<0
        Tr.TrV(i)=0;
    end
    %限制速度不能大于巡航速度不能低于0
    if Tr.TrV(i)>Tr.TrFuc(2,i)
        Tr.TrV(i)=Tr.TrFuc(2,i);
    end
    if Tr.TrV(i)<0
        Tr.TrV(i)=0;
    end
end

    


