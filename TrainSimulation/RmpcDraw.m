%{
代码功能：鲁棒模型预测控制绘图

%}

%% 多个列车晚点变化对比图
beginPlat=1;
endPlat=20;
beginPlatt=1;
endPlatt=20;
cm = colormap('Lines');
figure('name','Single platform Total Error Algorithm Comparison Diagram');
for i=2:5
    subplot(4,1,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y1=keepvar.TimeEr1(i,beginPlat:endPlat); %无控制器情况
    y2=keepvar.TimeEr2(i,beginPlat:endPlat); %晚点反馈控制器
    y3=keepvar.TimeEr4(i,beginPlat:endPlat); %RMPC反馈控制器
    plot(x,y1,'LineStyle','-','Color',cm(1,:).*[0.6 0.6 0.6],'LineWidth',0.5)
    hold on
    plot(x,y2,'LineStyle','-','Color',cm(2,:).*[0.6 0.6 0.6],'LineWidth',0.5)
    hold on
    plot(x,y3,'LineStyle','-','Color',cm(3,:).*[0.6 0.6 0.6],'LineWidth',0.5)
end

%% 多个列车晚点变化对比图
beginPlat=1;
endPlat=20;
beginPlatt=1;
endPlatt=20;
cm = colormap('Lines');
figure('name','Single platform Total Error Algorithm Comparison Diagram');
for i=2:5
    subplot(4,1,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y2=keepvar.TimeEr2(i,beginPlat:endPlat); %晚点反馈控制器
    y3=keepvar.TimeEr4(i,beginPlat:endPlat); %RMPC反馈控制器
    plot(x,y2,'LineStyle','-','LineWidth',0.5)
    hold on
    plot(x,y3,'LineStyle','--','LineWidth',0.5)
    allErrorConFeed(i-1)=sum(y2);
    allErrorVarFeed(i-1)=var(y2,1);
    allErrorConRmpc(i-1)=sum(y3);
    allErrorVarRmpc(i-1)=var(y3,1);
end

%% 反馈控制与模型预测控制对比图
%% 六格列车对比图
TimeErrorNo=keepvar.TimeEr1;
TimeErrorRmpc=keepvar.TimeEr4;
TimeErrorPerson=keepvar.TimeEr8;
beginPlat=2;
endPlat=9;
beginPlatt=2;
endPlatt=9;
allerrorNo=sum(TimeErrorNo(2:4,beginPlat:endPlat),'all');
allerrorRmpc=sum(TimeErrorRmpc(2:5,beginPlat:endPlat),'all');
allerrorPerson=sum(TimeErrorPerson(1:6,beginPlat:endPlat),'all');
errorloss=(allerrorNo-allerrorRmpc)/allerrorRmpc;
errorPersonRmpc=(allerrorPerson-allerrorRmpc)/allerrorPerson
figure();
for i=2:5
    subplot(2,2,i-1)
    x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
    y1=TimeErrorNo(i,beginPlat:endPlat);
    y2=TimeErrorRmpc(i,beginPlat:endPlat);
    y3=TimeErrorPerson(i,beginPlat:endPlat);
    bar(x,[y1',y2',y3']);
    set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
    set(gca,'XTick',[beginPlatt:1:endPlatt]);
    set(gca,'XTickLabel',{'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';},'FontSize',12);
    set(gca,'YLim',[0 9]);
    % 获取当前坐标轴句柄
    ax = gca;
        % 设置X轴刻度标签的字体大小
    ax.XAxis.FontSize = 14;

    % 设置Y轴刻度标签的字体大小
    ax.YAxis.FontSize = 12;
    if i==2||i==4
        ylabel('Delays at each  Station','FontSize',25); 
    end
    
    if i==4||i==5
        xlabel('Station ID','FontSize',25);
    end
    b=num2str(i);
    a='Train ';
    c=[a,b];
    title(c,'FontSize',25)
    lgd=legend('FCFS method','RMPC method','Terminus Time Margin method');
    lgd.FontSize=12;
end

%% 鲁棒模型预测控制与有时刻表控制总晚点对比图（客流不确定性）

beginPlat=1;
endPlat=9;
beginPlatt=1;
endPlatt=9;

figure('name','Single platform Total Error Algorithm Comparison Diagram');
x=linspace(beginPlat,endPlat,endPlat-beginPlat+1);
y1=sum(keepvar.TimeEr2(:,x));
y2=sum(keepvar.TimeEr4(:,x));
y3=sum(keepvar.TimeEr7(:,x));
bar(x,[y1',y2',y3'])
set(gca,'XLim',[beginPlatt-1 endPlatt+1]);
set(gca,'YLim',[0 100]);
set(gca,'XTick',[beginPlatt:1:endPlatt]);
set(gca,'XTickLabel',{'1(BJN)';'2(WQD)';'3(TJD)';'4(JLCBD)';'5(BH)';'6(JLCBU)';'7(TJU)';'8(WQU)';'9(BJN)';'10(WQD)';'11(TJD)';'12(JLCBD)';'13(BH)';'14(JLCBU)';'15(TJU)';'16(WQU)';'17(BJN)';'18(WQD)';'19(TJD)';'20(JLCBD)'},'FontSize',10);

lgd=legend('Feedback Control method','RMPC method','MIP method');
lgd.FontSize=20;
xlabel('Station ID','FontSize',25);
ylabel('Total Train Delays at each Station','FontSize',25);


allErrorCon=sum(y1,'all');
allErrorMCon=sum(y2,'all');
allErrorMIP=sum(y3,'all');
errorloss=(allErrorCon-allErrorMCon)/allErrorCon;

%% 

% 假设 methodAData 和 methodBData 是您的实验数据
methodAData = keepvar.TimeSumEr4;
methodBData = keepvar.TimeSumEr7;

% 绘制对比图
figure;
plot(methodAData, 'b', 'LineWidth', 1.5); % 方法A的数据
hold on;
plot(methodBData, 'r', 'LineWidth', 1.5); % 方法B的数据
hold off;

title('对比两种方法的实验结果');
xlabel('实验次数');
ylabel('实验数据');
set(gca,'XTick',[1:1:3]);
legend('RMPC', 'MANUAL');
grid on;



