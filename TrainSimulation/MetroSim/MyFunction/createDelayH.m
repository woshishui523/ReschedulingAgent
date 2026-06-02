function [timeDelayH]=createDelayH(Tnum,Pnum,timeschedule,H)
%函数功能：根据给定的到站时刻表计算时间偏差误差
timeDelayH=zeros(Pnum,1);
for i=1:Pnum
   for j=1:Tnum-1
       if i==9
          q=1; 
       end
       timeDelayH(i)=timeDelayH(i)+abs(timeschedule(j+1,2*i)-timeschedule(j,2*i)-H);
   end
end
end