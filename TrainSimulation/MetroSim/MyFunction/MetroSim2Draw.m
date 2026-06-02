function MetroSim2Draw(keep)
%% 运行图



%% 误差图（一辆列车）
%测试五个场景的误差图

beginPlat=9;
endPlat=16;
beginPlatt=1;
endPlatt=8;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Error Diagram');
set(gca,'FontSize',15);
set(gca,'XLim',[beginPlatt endPlatt]);
set(gca,'YLim',[0 25]);
xlabel('Location x(t)'); ylabel('Error (min)');
title('Train Error Diagram');
time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);

for i=1:3 %改为发生误差之后的站台
    hold on;
    switch i
        case 1
            plot(time,keep.TimeEr1(2,beginPlat:endPlat),'Color',cm(i,:),'LineStyle','-.')
        case 2
            plot(time,keep.TimeEr2(2,beginPlat:endPlat),'Color',cm(i,:))
        case 3
            plot(time,keep.TimeEr3(2,beginPlat:endPlat),'Color',cm(i,:),'LineStyle','- -')
    end
end

legend('no control','control with schedule','control without schedule')
%% 误差传播图

%% 热力图

%% 列车间隔误差图

beginPlat=9;
endPlat=16;
beginPlatt=1;
endPlatt=8;
cm = colormap('Lines');
mkr=['o';'*';'.';'x';'s';'^'; 'v'; 'd';'>';'<';'p';'h';'+'];
figure('name','Train Internal Error Diagram');
set(gca,'FontSize',15);
set(gca,'XLim',[beginPlatt endPlatt]);
set(gca,'YLim',[0 50]);
xlabel('Location x(t)'); ylabel('Internal Error (min)');
title('Train Internal Error Diagram');
time=linspace(beginPlatt,endPlatt,endPlatt-beginPlatt+1);

for i=1:3 %改为发生误差之后的站台
    hold on;
    switch i
        case 1
            plot(time,keep.TimeHEr1(beginPlat:endPlat),'Color',cm(i,:),'LineStyle','-.')
        case 2
            plot(time,keep.TimeHEr2(beginPlat:endPlat),'Color',cm(i,:))
        case 3
            plot(time,keep.TimeHEr3(beginPlat:endPlat),'Color',cm(i,:),'LineStyle','- -')
    end
end

legend({'no control','control with schedule','control without schedule'})

end
