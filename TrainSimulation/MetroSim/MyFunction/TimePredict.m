function predict=TimePredict(Tnum,Pnum,TimeSchedule)
%函数功能：进行未到站车辆的模型预测（预测到站的误差）
predict=0;
for i=Pnum:-1:1
    if TimeSchedule.TimeError(Tnum,i)~=0 %找到有误差那个站，向前预测一站
        predict=TimeSchedule.TimeError(Tnum,i)+TimeSchedule.TimeUk(Tnum,i); 
        break;
    end
    predict=0;
end
% predict