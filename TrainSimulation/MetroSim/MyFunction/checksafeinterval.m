function judge=checksafeinterval(time,i,Tr,Plat)
%函数功能：检测是否车辆之间满足最小发车时间间距，如果没有则以最小时间间隔发车
if time-Plat.timelast(Tr.TrState(i))>=Plat.Tinterval
    judge=1;
else
    judge=0;
end

