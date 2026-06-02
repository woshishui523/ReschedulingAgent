function RoutingStation=findRoute(Pnum,PNUM,Plat)
PlatAdd=Plat.N/2;
if Pnum<=PlatAdd+1
    RoutingStation=PlatAdd+1-Pnum+1;
else
    RoutingStation=PlataAdd*2+1-Pnum+1;
end
RoutingNow=RoutingStation;
RoutingStation=[];
for i=1:1000
    RoutingStation=[RoutingStation RoutingNow];
    RoutingNow=RoutingNow+PlatAdd;
    if RoutingNow>PNUM
       break 
    end
    
end
end