function y=GetDis(PlatX,Distance)
%函数功能：根据站台位置计算出站台间距离
y(1)=PlatX(2)-0;
for i=2:length(PlatX)-1
    y(i)=PlatX(i+1)-PlatX(i);
end
y(length(PlatX))=Distance-PlatX(length(PlatX));
