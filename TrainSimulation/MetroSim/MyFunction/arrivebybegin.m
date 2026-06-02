function arrive=arrivebybegin(Tr,Plat,train,time,begin)
%函数功能：由车辆发车时间计算车辆到达之间
pasttrain=cirsub(train,Tr.M); %上一辆列车
if Tr.TrPass(pasttrain)==Tr.TrPass(train)&&Tr.TrB(pasttrain)==1 %若同一区段前面存在列车
    stay=Tr.Tmin+Plat.P*Plat.ck(ciradd(Tr.TrPass(train),Plat.N))*(time-begin(cirsub(train,Tr.M),Tr.TrPass(train)+1+Plat.N*Tr.TrCir(pasttrain)));
    arrive=time-stay;
else
    if Tr.firstcircle==false&&train==1
        stay=Tr.Tmin+Plat.P*Plat.ck(ciradd(Tr.TrPass(train),Plat.N))*time;
        arrive=time-stay;
    else
        stay=Tr.Tmin+Plat.P*Plat.ck(ciradd(Tr.TrPass(train),Plat.N))*(time-Plat.timelast(Tr.TrPass(train)));
        arrive=time-stay;
    end
end
% if ((Tr.TrPass(train)==Tr.TrPass(cirsub(train,Tr.M))||ciradd(Tr.TrPass(train),Plat.N))==Tr.TrPass(cirsub(train,Tr.M)))&&Tr.TrB(cirsub(train,Tr.M))==1&&...
%         (Tr.TrX(cirsub(train,Tr.M))>=Tr.TrX(train))
%     stay=Tr.Tmin+Plat.P*Plat.ck(ciradd(Tr.TrPass(train),Plat.N))*(time-begin(cirsub(train,Tr.M),Tr.TrPass(train)+1+Plat.N*Tr.TrCir(train)));
%     arrive=time-stay;
% else
%     stay=Tr.Tmin+Plat.P*Plat.ck(ciradd(Tr.TrPass(train),Plat.N))*(time-Plat.timelast(ciradd(Tr.TrPass(train),Plat.N)));
%     arrive=time-stay;
% end
