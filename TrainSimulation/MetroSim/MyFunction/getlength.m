function y=getlength(x)
%函数功能：求解画出图像需要矩阵
y(1,1:size(x,1))=2;
for i=1:size(x,1)
    for j=3:size(x,2)
        if x(i,j)==0
           break 
        end 
        y(i)=y(i)+1;
    end
end

