function MinRuntime=createMinRuntime(Pnum,PNUM,timetable)
minruntime=timetable.MinRunTime;
MinRuntime=zeros(1,PNUM);
for i=1:PNUM
    MinRuntime(i)=minruntime(Pnum);
    Pnum=Pnum+1;
    if Pnum>length(minruntime)
       Pnum=1; 
    end
end
end