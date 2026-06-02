function [data,order]=getmax(TrX,num,dis)
%函数功能：将大于第一车的车辆序号按距离由大到小排列
data=[];
order=[];
for i=2:length(num)
   if TrX(i)>dis
       data(length(data)+1)=TrX(i);
       order(length(order)+1)=num(i);
   end
end

for i=1:length(order)-1
   for j=i+1:length(order)
       if data(j-1)<data(j)
          z=data(j-1);
          data(j-1)=data(j);
          data(j-1)=z;
          z=order(j-1);
          order(j-1)=order(j);
          order(j)=z;
       end
   end
end