function y=linesub(x)
long=size(x,1);
line=size(x,2);
y=zeros(long,line);
    for j=1:line
        for z=1:j
            y(:,j)=y(:,j)+x(:,z);
        end
    end
end