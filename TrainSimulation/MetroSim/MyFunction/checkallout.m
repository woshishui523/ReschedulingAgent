function y=checkallout(Tr)
for i=1:Tr.M
    if Tr.TrB(i)==0
        y=1;
        return
    end
end
y=0;