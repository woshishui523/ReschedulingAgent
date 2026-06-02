function y=mod2(x,n)
    if mod(x,n)==0
        y=n;
    else
        y=mod(x,n);
    end
end