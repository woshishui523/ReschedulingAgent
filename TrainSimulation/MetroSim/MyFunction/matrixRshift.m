function y=matrixRshift(x,num)
lo=size(x,1);
ln=size(x,2);
    y=zeros(lo,ln);
    for j=1:size(x,2)
       y(:,mod2(j+num,ln))=x(:,j); 
    end
end