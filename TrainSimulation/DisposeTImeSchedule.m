%{
代码功能：修改时刻表至接近现实场景
%} 

TimeDisposed = TimeSchedule.TimeArrive;
TimeError = keep4.TimeEr3;
TimeDisposed = [TimeDisposed(1,1:end) zeros(1,2);
    TimeDisposed(2:3,1:2) zeros(2,2) TimeDisposed(2:3,3:end); 
    TimeDisposed(4:end,1:end) zeros(12,2)];

TimeDisposed(2,3) = 22;
TimeDisposed(2,4) = 62;
TimeDisposed(3,3) = 25;
TimeDisposed(3,4) = 67;
for i=4:15
    TimeDisposed(i,2) = TimeDisposed(i,2) + TimeError(i,2);
end

TimeDisposed(1,17) = TimeDisposed(1,17)+TimeError(1,11);
TimeDisposed(1,18) = TimeDisposed(1,18)+TimeError(1,11);

    %% 实际运行图与初始计划调度运行图对比展示部分
figure('name','Train Time-Distance BeginDiagram');
set(gca,'FontSize',15);
set(gca,'XLim',[0 250]);
set(gca,'YLim',[0 166]);
set(gca,'YTick',[0 84 120 140 166]);% Y轴的记号点 
set(gca,'YTicklabel',{'1(BJN)','2(WQ)','3(TJ)','4(JLCB)','5(BH)'});% Y轴的记号
cm = colormap('Lines');
ArriveNum=getlength(TimeSchedule.TimeArrive);
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
xlabel('Time (min)'); ylabel('Station ID x(t)');
title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i),Plat.N,Plat.PlatX);
    if i==2||i==3
        plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
            'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
            'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
        if i==2
            time=[time(1:2) 45 45 time(3:end)]; 
            plot(TimeDisposed(i,1:length(time)),time,...
              'Color', cm(i,:),'LineWidth', 2);    
        end
        if i==3
            time=[time(1:2) 45 45 time(3:end)]; 
            plot(TimeDisposed(i,1:length(time)),time,...
              'Color', cm(i,:),'LineWidth', 2);
        end
    else
        plot(TimeDisposed(i,1:length(time)),time,...
          'Color', cm(i,:),'LineWidth', 2);

        plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
        'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
        'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
    end

end

%%  处理优化后的运行图

TimeDisposed = Timetable;
TimeError = TimetableError;
TimeDisposed = [TimeDisposed(1,1:end) zeros(1,2);
    TimeDisposed(2:3,1:2) zeros(2,2) TimeDisposed(2:3,3:end); 
    TimeDisposed(4:end,1:end) zeros(12,2)];

TimeDisposed(2,3) = 22;
TimeDisposed(2,4) = 62;
TimeDisposed(3,3) = 25;
TimeDisposed(3,4) = 67;
for i=4:15
    TimeDisposed(i,2) = TimeDisposed(i,2) + TimeError(i,2);
end

TimeDisposed(1,17) = TimeDisposed(1,17)+TimeError(1,11);
TimeDisposed(1,18) = TimeDisposed(1,18)+TimeError(1,11);

    %% 实际运行图与初始计划调度运行图对比展示部分
figure('name','Train Time-Distance BeginDiagram');
set(gca,'FontSize',15);
set(gca,'XLim',[0 250]);
set(gca,'YLim',[0 166]);
set(gca,'YTick',[0 84 120 140 166]);% Y轴的记号点 
set(gca,'YTicklabel',{'1(BJN)','2(WQ)','3(TJ)','4(JLCB)','5(BH)'});% Y轴的记号
cm = colormap('Lines');
ArriveNum=getlength(TimeSchedule.TimeArrive);
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
xlabel('Time (min)'); ylabel('Station ID x(t)');
title('Train Time-Distance Diagram');
for i=1:M
    hold on;
    time=createTime(ArriveNum(i),Plat.N,Plat.PlatX);
    if i==2||i==3
       plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
            'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
            'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
       if i==2
            time=[time(1:2) 45 45 time(3:end)]; 
            plot(TimeDisposed(i,1:length(time)),time,...
              'Color', cm(i,:),'LineWidth', 2);           
        end
        if i==3
            time=[time(1:2) 45 45 time(3:end)]; 
            plot(TimeDisposed(i,1:length(time)),time,...
              'Color', cm(i,:),'LineWidth', 2);
        end
    else 
        plot(TimeDisposed(i,1:length(time)),time,...
          'Color', cm(i,:),'LineWidth', 2);

        plot(TimeSchedule.OriTimeTable(i,1:length(time)),time,...
        'Color', cm(i,:).*[0.6 0.6 0.6], 'LineWidth',0.5, ...
        'LineStyle','-.', 'Marker', mkr(mod(i,13)+1));
    end

end

%% 六格列车对比图
TimeHerrorYou=TimetableHError;
TimeHerrorCon=keep4.TimeHEr3;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
figure();
for i=2:5
    subplot(2,2,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y1=TimeHerrorCon(i,beginPlat:endPlat);
    y2=TimeHerrorYou(i,beginPlat:endPlat);
    bar(x,[y1',y2']);
    set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
    set(gca,'XTick',[beginPlatt:1:endPlatt]);
    set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',10);
    if i==2||i==4
        ylabel('Deviations at each  Station','FontSize',20); 
    end
    
    if i==4||i==5
        xlabel('Train ID','FontSize',25);
    end
    b=num2str(i);
    a='Train ';
    c=[a,b];
    title(c,'FontSize',25)
    lgd=legend('Control method','MIP method');
    lgd.FontSize=12;
end

%% 六格列车对比图
TimeErrorYou=TimetableError;
TimeErrorCon=keep4.TimeEr2;
beginPlat=2;
endPlat=8;
beginPlatt=2;
endPlatt=8;
allerrorCon=sum(TimeErrorCon(2:5,beginPlat:endPlat),'all');
allerrorYou=sum(TimeErrorYou(2:5,beginPlat:endPlat),'all');
errorloss=(allerrorCon-allerrorYou)/allerrorCon
figure();
for i=2:5
    subplot(2,2,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y1=TimeErrorCon(i,beginPlat:endPlat);
    y2=TimeErrorYou(i,beginPlat:endPlat);
    bar(x,[y1',y2']);
    set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
    set(gca,'XTick',[beginPlatt:1:endPlatt]);
    % set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',10);
    set(gca,'XTickLabel',{'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',16);
    b=num2str(i);
    set(gca, 'FontSize', 16);
    if i==2||i==4
        ylabel('Delays at each  Station','FontSize',25); 
    end
    
    a='Train ';
    c=[a,b];
    title(c,'FontSize',25)
    lgd=legend('Control method','MIP method');
    lgd.FontSize=16;
    ylim([0 20]);
end


%% 均匀达到目标对比图

beginPlat=2;
endPlat=18;
beginPlatt=2;
endPlatt=18;
figure();

x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
y1=TimetableHvarCo(x);
y2=TimetableHvarYo(x);
bar(x,[y1',y2']);
set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
set(gca,'XTick',[beginPlatt:1:endPlatt]);
set(gca,'XTickLabel',{'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';'16(WQU)';'17(BJN)';'18(WQD)';'19(TJD)';'20(JLCBD)'},'FontSize',14);

lgd=legend('The proposed method','MIP method');
lgd.FontSize=22;
xlabel('Station ID','FontSize',25);
ylabel('Train Departure Intervals Variance','FontSize',25);


allHerrorCon=sum(y1,'all');
allHerrorYou=sum(y2,'all');

errorloss=(allHerrorCon-allHerrorYou)/allHerrorCon
% plot(length(TimetableHmeanYo),TimetableHmeanYo)


%% 鲁棒模型预测控制与有时刻表控制总晚点对比图（客流不确定性）

beginPlat=1;
endPlat=9;
beginPlatt=1;
endPlatt=9;

figure('name','Single platform Total Error Algorithm Comparison Diagram');
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
y1=sum(keep4.TimeEr2(:,x));
y2=sum(keep4.TimeEr4(:,x));
bar(x,[y1',y2'])
set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
set(gca,'XTick',[beginPlatt:1:endPlatt]);
set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';'16(WQU)';'17(BJN)';'18(WQD)';'19(TJD)';'20(JLCBD)'},'FontSize',10);

lgd=legend('Feedback Control method','RMPC method');
lgd.FontSize=12;
xlabel('Station ID','FontSize',25);
ylabel('Total Train Delays at each Station','FontSize',25);


allErrorCon=sum(y1,'all');
allErrorMCon=sum(y2,'all');

errorloss=(allErrorCon-allErrorMCon)/allErrorCon;

%% 六格列车对比图鲁棒模型预测控制与有时刻表
TimeErrorCON=keep4.TimeEr2;
TimeErrorMPC=keep4.TimeEr4;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
allerrorCON=sum(TimeErrorCON(2:5,beginPlat:endPlat),'all');
allerrorMPC=sum(TimeErrorMPC(2:5,beginPlat:endPlat),'all');
errorloss=(allerrorCON-allerrorMPC)/allerrorCON
figure();
for i=2:5
    subplot(2,2,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y2=TimeErrorMPC(i,beginPlat:endPlat);
    bar(x,y2');
    set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
    set(gca,'XTick',[beginPlatt:1:endPlatt]);
    set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',10);
    if i==2||i==4
        ylabel('Delays at each  Station','FontSize',20); 
    end
    
    if i==4||i==5
        xlabel('Train ID','FontSize',25);
    end
    b=num2str(i);
    a='Train ';
    c=[a,b];
    ylim([0 16])
    title(c,'FontSize',25)
    lgd.FontSize=12;
end
%% 六格列车对比图鲁棒模型预测控制与有时刻表
TimeErrorCON=keep4.TimeEr2;
TimeErrorMPC=keep4.TimeEr4;
beginPlat=1;
endPlat=10;
beginPlatt=1;
endPlatt=10;
allerrorCON=sum(TimeErrorCON(2:5,beginPlat:endPlat),'all');
allerrorMPC=sum(TimeErrorMPC(2:5,beginPlat:endPlat),'all');
errorloss=(allerrorCON-allerrorMPC)/allerrorCON
figure();
for i=2:5
    subplot(2,2,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y2=TimeErrorMPC(i,beginPlat:endPlat);
    bar(x,y2');
    set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
    set(gca,'XTick',[beginPlatt:1:endPlatt]);
    set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',10);
    if i==2||i==4
        ylabel('Delays at each  Station','FontSize',20); 
    end
    
    if i==4||i==5
        xlabel('Train ID','FontSize',25);
    end
    b=num2str(i);
    a='Train ';
    c=[a,b];
    ylim([0 16])
    title(c,'FontSize',25)
    lgd.FontSize=12;
end













