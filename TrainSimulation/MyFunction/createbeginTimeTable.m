function BeginTimeTable=createbeginTimeTable(interval,time,steps,Plat,Tr)
%函数功能：根据安全时间间隔和第一辆车到达时间
stime=ceil(time*Plat.ck(1)*Plat.P/(1-Plat.ck(1)*Plat.P)+Tr.Tmin);
for i=1:Tr.M
    for j=1:steps
        if j==1
            BeginTimeTable(i,j)=interval*(i-1);
        else
            BeginTimeTable(i,j)=interval*(i-1)+stime+time*(j-1);
        end
    end
end
