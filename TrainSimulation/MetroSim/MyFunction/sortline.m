function y=sortline(Tr)
    dis=Tr.TrX(1);
    num=linspace(1,Tr.M,5);
    [data1,order1]=getmin(Tr.TrX,num,dis);
    [data2,order2]=getmax(Tr.TrX,num,dis);
    y=[1 order1 order2];

