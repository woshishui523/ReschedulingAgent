function y=structToarray(x)
%可将solve求解之后的的结构体转化为解的数组
fileds = fieldnames(x);
for i=1:length(fileds)
    k = fileds(i);
    key = k{1};
    value = x.(key);
    y(1,i)=value;
end