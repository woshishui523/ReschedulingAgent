function y=checkBegin(t,T,Tr)
%函数功能:检测是否有应该发车的车，并返回车序列号，若无，则返回0；
y=0;
for i=1:Tr.M
    if t>=(i-1)*T&&t<i*T&&Tr.TrB(i)==false
        y=i;
        break;
    end
end

