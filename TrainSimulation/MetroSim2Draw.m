function MetroSim2Draw(keep)
% 待修改内容：修改为柱状图

%% (有计划时刻表)七辆列车 八个站台 误差图
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
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keep.TimeEr2(beginTr:endTr,beginPlat:endPlat);
grid on
colormap('Lines')
ribbon(y,z')
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
%% (有计划时刻表)七辆列车 八个站台 控制量图
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Running Time Adjustment Diagram With Timetable');
time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keep.TimeUk2(beginTr:endTr,beginPlat:endPlat);
ribbon(y,z')
set(gca,'FontSize',15);
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Train Arrival Time Adjustment (min)','FontSize',25);
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
%% (无计划时刻表)七辆列车 八个站台 H误差图
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Internal Error Diagram Without Timetable');
time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keep.TimeHEr3(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z')
set(gca,'FontSize',15);
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Deviations of Train Arrival Intervals (min)','FontSize',25)
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
%% (无计划时刻表)七辆列车 八个站台 控制量图
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Running Time Adjustment Diagram Without Timetable');
time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keep.TimeUk3(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z')
set(gca,'FontSize',15);
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Train Arrival Time Adjustment(min)','FontSize',25)
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
%% (鲁棒模型预测控制)七辆列车 八个站台 误差图
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
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keep.TimeEr4(beginTr:endTr,beginPlat:endPlat);
grid on
colormap('Lines')
ribbon(y,z')
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

%% （鲁棒模型预测控制）七辆列车 八个站台 控制量图
beginTr=1;
endTr=8;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Running Time Adjustment Diagram Without Timetable');
time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);
[x,y]=meshgrid(beginTr:1:endTr,beginPlat:1:endPlat);
z=keep.TimeUk4(beginTr:endTr,beginPlat:endPlat);
grid on
ribbon(y,z')
set(gca,'FontSize',15);
set(gca,'YLim',[beginPlatt endPlatt]);
set(gca,'XLim',[beginTr endTr]);
set(gca,'ydir','reverse');
set(gca,'YTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)'},'FontSize',15);
ylabel('Station ID','FontSize',25); 
xlabel('Train ID','FontSize',25);
zlabel('Train Arrival Time Adjustment(min)','FontSize',25)
javaFrame = get(gcf,'javaFrame');
set(javaFrame,'Maximized',1);
end
