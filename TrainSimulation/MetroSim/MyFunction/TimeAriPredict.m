function predict=TimeAriPredict(Tnum,Pnum,TimeSchedule)
predict=0;
for i=Pnum:-1:1
    if TimeSchedule.TimeArrive(Tnum,2*i)~=0
        predict=TimeSchedule.OriTimeTable(Tnum,2*Pnum)+TimeSchedule.TimeError(Tnum,i)+TimeSchedule.TimeUk(Tnum,i); 
        break;
    end
end