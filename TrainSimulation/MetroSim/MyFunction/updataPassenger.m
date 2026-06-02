function Plat=updataPassenger(Plat,k)
for i=1:Plat.N
   Plat.PlatNum(i)=Plat.PlatNum(i)+Plat.ck(i)/k; 
end


