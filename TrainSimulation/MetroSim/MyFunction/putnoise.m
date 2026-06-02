function [ptime,Tr]=putnoise(i,j,k,time,Tr,noise)
%函数功能：给到达时间添加干扰
ptime=time;
if i==2&&j==10
    ptime=time+15;
    fprintf("列车%d在站台%d干扰量为%f",i,j,8);
end
end

% if Tr.noise(i)==1 %已达到干扰列车
%     if ~(i==1&&Tr.TrCir(1)==0)
%         fprintf("列车%d在站台%d干扰量为%f",i,j,noise(time*k));
% %         time=time+3.5;
%         Tr.noise(i)=-1; %在进行一次干扰之后暂停干扰
%     else
%         time=time;
%     end
% else
%     time=time;
% end
% if Tr.noise(i)~=-1 %干扰项存在
%     Tr.noise(i)=ciradd(Tr.noise(i),Tr.noisetime);
% end
% time=round(time);