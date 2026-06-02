function ans=judgeFace(tur,range)
%函数功能：判断是否到达分界面，若到达返回1，否则返回0
    turspeed=tur(length(tur))-tur(length(tur)-1); %差分计算变化率
    if turspeed>=range(1)&&turspeed<=range(2) %判断是否在范围内检测到分界面
        ans=1;
    else
        ans=0;
    end
    