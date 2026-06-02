function y=getNearone(num,Tr,Plat)
%寻找最近的车站
max=abs(Tr.TrX(num)-Plat.Distance);
nearone=1;
for i=2:Plat.N
    now=abs(Tr.TrX(num)-Plat.PlatX(i));
    if now<max
        max=now;
        nearone=i;
    end
end
y=Plat.PlatX(nearone);


