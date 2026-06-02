function TrInter=GetInter(TrInter,MinRuntime,Tmin,Tsmin,stayvar)
length=size(MinRuntime,2);
if stayvar.controller_list(stayvar.controller)==8
    Sub=TrInter-MinRuntime;
    for i=1:length
       if i==length/2||i==length
          Sub(i)=Sub(i)-Tsmin-1;
       else
          Sub(i)=Sub(i)-Tmin-1;
       end
    end
    TrInter=MinRuntime;
    TrInter(length/2)=TrInter(length/2)+sum(Sub(1:length/2));
    TrInter(length)=TrInter(length)+sum(Sub(length/2+1:length));
    for i=1:length
       if i==length/2||i==length
           TrInter(i)=TrInter(i)+Tsmin+1;
       else
           TrInter(i)=TrInter(i)+Tmin+1;         
       end
    end
end

end