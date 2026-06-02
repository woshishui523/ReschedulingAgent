%% 电阻型负载
x=0:0.01:150;
y=0.675*(1+cos(pi/6+x*pi/180));
x1=[0 30 60 90 120];
ud=[145.30 128.02 80.88 43.21 9.51];
u2=129.03;
ux=ud/u2;
p=polyfit(x1,ux,3);  
yi=polyval(p,x);  
figure(1);
plot(x,yi);
hold on
plot(x,y);
xlabel('α/(o)');
ylabel('Ud/U2');
legend('实际拟合曲线','理论曲线');
%% 阻感性负载
x=0:0.01:90;
y=1.17*cos(x*pi/180);
x1=[0 30 60 90];
ud=[145.31 129.88 75.45 23.76];
u2=129.03;
ux=ud/u2;
p=polyfit(x1,ux,3);  
yi=polyval(p,x);  
figure(2);
plot(x,yi);
hold on
plot(x,y);
xlabel('α/(o)');
ylabel('Ud/U2');
legend('实际拟合曲线','理论曲线');