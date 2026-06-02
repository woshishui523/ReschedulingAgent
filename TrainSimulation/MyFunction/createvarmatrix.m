function y=createvarmatrix(m,n)
%函数功能：根据输入的维度生成一个变量矩阵
y= sym(zeros(m,n));
for i=1:m
    for j=1:n
        cmd = sprintf('sym(''X%i%i'')',i,j);
        y(i,j) = eval(cmd);
    end
end