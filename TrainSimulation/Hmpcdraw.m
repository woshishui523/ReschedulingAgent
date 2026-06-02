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
z=keepvar.TimeHEr1(beginTr:endTr,beginPlat:endPlat);
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

 %% 当个列车总行车间距时间变化
figure('name','Single train Total eviations of train arrival intervals with respect to expected arrival interval Algorithm Comparison Diagram');
for i=beginTr:endTr
    y2(i)=sum(abs(keepvar.TimeHEr1(i,beginPlat:endPlat)));
    y3(i)=sum(abs(keepvar.TimeHEr3(i,beginPlat:endPlat)));
end
x=linspace(beginTr,endTr,endTr-beginTr+1);
figure 
plot(x,y2,'*-',x,y3,'--')
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
    y5(i)=sum(abs(keepvar.TimeHEr1(beginTr:endTr,i)));
    y6(i)=sum(abs(keepvar.TimeHEr3(beginTr:endTr,i)));
end
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
figure 

plot(x,y5,'*-',x,y6,'--')
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
endPlat=10;
beginPlatt=1;
endPlatt=10;
figure('name','Single platform Total eviations of train arrival intervals with respect to expected arrival interval Algorithm Comparison Diagram');
for i=beginPlat:endPlat
    y3(i)=sum(abs(keepvar.TimeHEr1(beginTr:endTr,i)));
    y4(i)=sum(abs(keepvar.TimeHEr2(beginTr:endTr,i)));
end
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
figure 

plot(x,y3,'*-',x,y4,'*--')
grid on
colormap('Lines')
legend('no control method','control method with no nominal timetable')
set(gca,'XLim',[beginPlat endPlat]);
set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
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
    y5(i)=sum(abs(keepvar.TimeEr1(beginTr:endTr,i)));
    y6(i)=sum(abs(keepvar.TimeEr2(beginTr:endTr,i)));
end
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
figure 

plot(x,y5,'*-',x,y6,'*--')
grid on
colormap('Lines')
legend('no control method','control method with no nominal timetable')
set(gca,'XLim',[beginPlat endPlat]);
set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
xlabel('Station ID','FontSize',25); 
ylabel('Delay Time/min','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);

%% 
beginTr = 1;
endTr = 8;
beginPlat = 1;
endPlat = 13;
beginPlatt = 1;
endPlatt = 13;

% 初始化变量
y5 = zeros(1, endPlat - beginPlat + 1);
y6 = zeros(1, endPlat - beginPlat + 1);

% 计算每个平台的总偏差
for i = beginPlat:endPlat
    y5(i) = sum(abs(keepvar.TimeHEr1(beginTr:endTr, i)));
    y6(i) = sum(abs(keepvar.TimeHEr2(beginTr:endTr, i)));
end

% 定义 x 轴范围
x = linspace(beginPlat, endPlat, endPlat - beginPlat + 1);

% 绘制柱状图
figure('name', 'Single platform Total deviations of train arrival intervals with respect to expected arrival interval Algorithm Comparison Diagram');

% 使用 bar 函数绘制两组柱状图
bar(x, [y5(beginPlat:endPlat); y6(beginPlat:endPlat)]', 'grouped')

% 添加网格和颜色映射
grid off
colormap('Lines')

% 图例
legend({'FCFS method', 'RMPC method'}, 'FontSize', 15)

% 设置坐标轴属性
set(gca, 'XLim', [beginPlat, endPlat]);
set(gca, 'XTickLabel', {'1(BJN)', '2(WQD)', '3(TJD)', '4(JLCBD)', '5(BH)', '6(JLCBU)', '7(TJU)', '8(WQU)', '9(BJN)', '10(WQD)','11(TJD)', '12(JLCBD)', '13(BH)'}, 'FontSize', 15);
xlabel('Station ID', 'FontSize', 25); 
ylabel('Train departure intervals variance', 'FontSize', 25);

% 最大化窗口
javaFrame = get(gcf, 'javaFrame');
set(javaFrame, 'Maximized', 1);
