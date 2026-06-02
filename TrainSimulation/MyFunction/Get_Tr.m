function y=Get_Tr(x,all,i)
if i==1
    if x==1
       y=all;
    else
        y=x-1;
    end
else
    if x==1
       y=2;
    elseif x==2
        y=1;
    else
        y=x-2;
    end
    
end


end