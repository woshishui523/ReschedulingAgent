function yi2k=predictHError(Tnum,Pnum,TimeSchedule,Tr,Plat)
if Tnum==1
    Tnum1=Tr.M;
    Pnum1=Pnum-Plat.N;
else
    Tnum1=Tnum-1;
    Pnum1=Pnum;
end
if TimeSchedule.TimeArrive(Tnum1,2*Pnum1)==0
    yi2k=TimeAriPredict(Tnum,Pnum,TimeSchedule)-TimeAriPredict(Tnum1,Pnum1,TimeSchedule)-Plat.DepartInter;
elseif TimeSchedule.TimeArrive(Tnum,2*Pnum)==0
    yi2k=TimeAriPredict(Tnum,Pnum,TimeSchedule)-TimeSchedule.TimeArrive(Tnum1,2*Pnum1)-Plat.DepartInter;
else
    yi2k=0;
end