function y=convar(a,b)
%此函数可以进行两个矩阵的多项式乘法（其中一个或两个变量向量）
%a为数值或符号矩阵，b同样
na=length(a)-1;
nb=length(b)-1;
for i=1:na+1
    for j=1:nb+1
        if(i==1||(i~=1&&j==nb+1))
           y(1,i-1+j-1+1)=a(1,i)*b(1,j); 
        else
            y(1,i-1+j-1+1)=a(1,i)*b(1,j)+y(1,i-1+j-1+1);
        end
    end
end


