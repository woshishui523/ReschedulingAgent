function noise=setnoisenum(num,M)
%函数功能：给指定数量列车加入干扰
switch num
    case 0
         noise=zeros(1,M)-1;
    case M
        noise=zeros(1,M);
    otherwise
        noise=[zeros(1,num),zeros(1,M-num)-1];
end


