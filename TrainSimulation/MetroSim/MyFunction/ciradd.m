function y=ciradd(a,b)
%函数功能：实现环状数列的加法，当加到最后一个数时回到1
if a==b
    y=1;
else
    y=a+1;
end