%% 
z=3;

%%
train_num=size(TimeSchedule.OriTimeTable,1);
station_num=size(TimeSchedule.OriTimeTable,2)/2;
delay1_station=2;
delay2_station=6;
ALL_timetable=TimeSchedule.OriTimeTable;
timetable_first=ALL_timetable(:,1:(delay1_station-1)*2);
timetable_second=ALL_timetable(:,delay1_station*2-1:(delay2_station)*2);
timetable_third=ALL_timetable(:,delay2_station*2-1:end);
Tnum=8;
Pnum=12;
delay=1;
if delay==3
    timetable_second=ALL_timetable(:,delay1_station*2-1:end);
end
%%
if delay==3
    [Timetable_second,~]=LinearOptimizationChange(Tnum,Pnum,delay,timetable_second);
    Timetable=[timetable_first Timetable_second];
else
    delay=1;
    [Timetable_second,~]=LinearOptimizationChange(Tnum,Pnum,delay,timetable_second);
    delay=2;
    [Timetable_third,~]=LinearOptimizationChange(Tnum,Pnum,delay,timetable_third);
    Timetable=[timetable_first Timetable_second(:,1:end-2) Timetable_third];
end

%%
figure('name','Train Time-Distance BeginDiagram');
set(gca,'FontSize',15);
set(gca,'XLim',[0 250]);
set(gca,'YLim',[0 166]);
set(gca,'YTick',[0 84 120 140 166]);% Y轴的记号点
set(gca,'YTicklabel',{'1(BJN)','2(WQ)','3(TJ)','4(JLCB)','5(BH)'});% Y轴的记号
cm = colormap('Lines');
ArriveNum=getlength(TimeSchedule.OriTimeTable);
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
xlabel('Time (min)'); ylabel('Station ID x(t)');
title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i),Plat.N,Plat.PlatX);
    plot(Timetable(i,1:length(time)),time,...
          'Color', cm(i,:),'LineWidth', 2);

    plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
        'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
        'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
end

%% 计算晚点延误和间隔延误
TimetableError=Timetable-TimeSchedule.OriTimeTable;
TimetableError=TimetableError(:,1:2:end);
for i=1:train_num
    if i==1
        TimetableHError(i,:)=zeros(1,station_num);
    else
        TimetableHError(i,:)=Timetable(i,1:2:end)-Timetable(i-1,1:2:end)-Plat.DepartInter;
    end
    
end
TimetableHError(:,1)=zeros(train_num,1);

for i=1:train_num
    if i==1        
        TimetableH(i,:)=Plat.DepartInter*ones(1,station_num);
    else
        TimetableH(i,:)=Timetable(i,1:2:end)-Timetable(i-1,1:2:end);
    end
    
end
TimetableHmeanYo=mean(TimetableH);
TimetableHvarYo=var(TimetableH);
TimetableHvarYo(1)=0;
z=keepvar.TimeHEr3+Plat.DepartInter;
TimetableHmeanCo=mean(z);
TimetableHvarCo=var(z);

%% 均匀达到目标对比图



%% 作对比图绘制
%% 有名义时刻表调度(晚点对比图)
% 晚点调节速度
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Error Diagram With Timetable');

time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
% [x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
% z1=keepvar.TimeEr2(beginTr:endTr,beginPlat:endPlat);
% z2=TimetableError(beginTr:endTr,beginPlat:endPlat);
% plot3(x,y,z1,x,y,z2,'--')
% p.LineWidth = 3;
%长的为控制
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keepvar.TimeEr2(beginTr:endTr,beginPlat:endPlat);
grid on
colormap('Lines')
ribbon(y,z')
hold on
%短的为优化时间
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=TimetableError(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z',0.35)

grid on
colormap('Lines')
colormap('Lines')
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Delays At Each Station (min)','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);

%% 有名义时刻表调度（行车间距对比图）
% 晚点调节速度
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train HError Diagram With Timetable');

time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
% [x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
% z1=keepvar.TimeEr2(beginTr:endTr,beginPlat:endPlat);
% z2=TimetableError(beginTr:endTr,beginPlat:endPlat);
% plot3(x,y,z1,x,y,z2,'--')
% p.LineWidth = 3;
%长的为控制
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keepvar.TimeHEr2(beginTr:endTr,beginPlat:endPlat);
grid on
colormap('Lines')
ribbon(y,z')
hold on
%短的为优化时间
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=TimetableHError(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z',0.35)

grid on
colormap('Lines')
colormap('Lines')
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Delays At Each Station (min)','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
%% 无名义时刻表调度（晚点对比图）
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Error Diagram With Timetable');

time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
% [x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
% z1=keepvar.TimeEr2(beginTr:endTr,beginPlat:endPlat);
% z2=TimetableError(beginTr:endTr,beginPlat:endPlat);
% plot3(x,y,z1,x,y,z2,'--')
% p.LineWidth = 3;
%长的为控制
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keepvar.TimeEr3(beginTr:endTr,beginPlat:endPlat);
grid on
colormap('Lines')
ribbon(y,z')
hold on
%短的为优化时间
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=TimetableError(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z',0.35)

grid on
colormap('Lines')
colormap('Lines')
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Delays At Each Station (min)','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);

%% 无名义时刻表调度（行车间距对比图）
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=15;
beginPlatt=1;
endPlatt=15;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train HError Diagram With Timetable');

time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
% [x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
% z1=keepvar.TimeEr2(beginTr:endTr,beginPlat:endPlat);
% z2=TimetableError(beginTr:endTr,beginPlat:endPlat);
% plot3(x,y,z1,x,y,z2,'--')
% p.LineWidth = 3;
%长的为控制
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keepvar.TimeHEr3(beginTr:endTr,beginPlat:endPlat);
grid on
colormap('Lines')
ribbon(y,z')
hold on
%短的为优化时间
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=TimetableHError(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z',0.35)

grid on
colormap('Lines')
colormap('Lines')
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'YLim',[1 15]);
set(gca,'ydir','reverse');
set(gca,'YTick',[beginPlatt:1:endPlatt]);
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',10);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Delays At Each Station (min)','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
%% 
% 计算时间
t1=332.3;
t2=0.4;

% 当个列车总晚点时间变化
figure('name','Single train Total Error Algorithm Comparison Diagram');
for i=beginTr:endTr
    y1(i)=sum(TimetableError(i,beginPlat:endPlat));
    y2(i)=sum(keepvar.TimeEr2(i,beginPlat:endPlat));
    y3(i)=sum(keepvar.TimeEr3(i,beginPlat:endPlat));
end
x=linspace(beginTr,endTr,endTr-beginTr+1);
figure 
plot(x,y1,x,y2,'*-',x,y3,'--')
grid on
colormap('Lines')
legend('optimization method','control method with nominal timetable','control method with no nominal timetable')
set(gca,'XLim',[beginTr endTr]);
set(gca,'YLim',[0 150]);

set(gca,'XTickLabel',{'1';'2';'3';'4';'5';'6';'7';'8'},'FontSize',15);
xlabel('Train ID','FontSize',25); 
ylabel('Delay Time/min','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);

%%  当个站台总晚点时间变化
figure('name','Single platform Total Error Algorithm Comparison Diagram');
for i=beginPlat:endPlat
    y4(i)=sum(TimetableError(beginTr:endTr,i));
    y5(i)=sum(keepvar.TimeEr2(beginTr:endTr,i));
    y6(i)=sum(keepvar.TimeEr3(beginTr:endTr,i));
end
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
figure 
plot(x,y4,x,y5,'*-',x,y6,'--')
grid on
colormap('Lines')
legend('optimization method','control method with nominal timetable','control method with no nominal timetable')
set(gca,'XLim',[beginPlatt endPlatt]);
set(gca,'YLim',[0 120]);

set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
xlabel('Station ID','FontSize',25); 
ylabel('Delay Time/min','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);



%%




 %% 当个列车总行车间距时间变化
figure('name','Single train Total eviations of train arrival intervals with respect to expected arrival interval Algorithm Comparison Diagram');
for i=beginTr:endTr
    y1(i)=sum(abs(TimetableHError(i,beginPlat:endPlat)));
    y2(i)=sum(abs(keepvar.TimeHEr2(i,beginPlat:endPlat)));
    y3(i)=sum(abs(keepvar.TimeHEr3(i,beginPlat:endPlat)));
end
x=linspace(beginTr,endTr,endTr-beginTr+1);
figure 
plot(x,y1,x,y2,'*-',x,y3,'--')
grid on
colormap('Lines')
legend('optimization method','control method with nominal timetable','control method with no nominal timetable')
set(gca,'XLim',[beginTr endTr]);
set(gca,'XTickLabel',{'1';'2';'3';'4';'5';'6';'7';'8'},'FontSize',15);
xlabel('Train ID','FontSize',25); 
ylabel('Delay Time/min','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);

%% 当个站台总行车间距变化
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=18;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Single platform Total eviations of train arrival intervals with respect to expected arrival interval Algorithm Comparison Diagram');
for i=beginPlat:endPlat
    y4(i)=sum(abs(TimetableHError(beginTr:endTr,i)));
    y5(i)=sum(abs(keepvar.TimeHEr2(beginTr:endTr,i)));
    y6(i)=sum(abs(keepvar.TimeHEr3(beginTr:endTr,i)));
end
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
figure 

plot(x,y4,x,y5,'*-',x,y6,'--')
grid on
colormap('Lines')
legend('optimization method','control method with nominal timetable','control method with no nominal timetable')
set(gca,'XLim',[beginPlat endPlat]);
% set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
xlabel('Station ID','FontSize',25); 
ylabel('Delay Time/min','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
 
%% 
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=18;
beginPlatt=1;
endPlatt=18;
figure('name','Single platform Total eviations of train arrival intervals with respect to expected arrival interval Algorithm Comparison Diagram');
for i=beginPlat:endPlat
    y5(i)=sum(abs(keepvar.TimeHEr2(beginTr:endTr,i)));
    y6(i)=sum(abs(keepvar.TimeHEr3(beginTr:endTr,i)));
end
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
figure 

plot(x,y5,'*-',x,y6,'*--')
grid on
colormap('Lines')
legend('control method with nominal timetable','control method with no nominal timetable')
set(gca,'XLim',[beginPlat endPlat]);
set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
xlabel('Station ID','FontSize',25); 
ylabel('Delay Time/min','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);



