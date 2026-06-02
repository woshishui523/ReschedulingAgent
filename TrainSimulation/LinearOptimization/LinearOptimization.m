function y=LinearOptimization(delay,timetable)
%% 参数初始化
[firstTimetable,firstMPRT,firstPM,Ts,Tz,conInformM,delayM]=GetTimeTable(timetable,delay);
Ar_Station_Delay = delayM(:,delayM(5,:)==1);
Ar_Station_Delay_Train = Ar_Station_Delay(2,:);
Ar_Station_Delay_Time = Ar_Station_Delay(1,:);
Ar_Station_Delay_TraNum = size(Ar_Station_Delay,2);
ActArSta_Time = firstTimetable(1,:);
ActArSta_Time(1,Ar_Station_Delay_Train) = firstTimetable(1,Ar_Station_Delay_Train) + Ar_Station_Delay_Time;
ActArFirstSta_Time = ActArSta_Time;
[m,train_num] = size(firstTimetable);
station_num = (m+1)/2;
M = 2000000;
sec_num = station_num-1;
T_max = Tz;
T_min = 1;

% 创建决策变量
depart_time = sdpvar(sec_num,train_num); % 发车时间 xij表示第i站第j个列车的发车时间
arrive_time = sdpvar(sec_num,train_num);  % 到站时间 yij表示第i+1站第j个列车的到站时间
isStop = binvar(sec_num,train_num,'full'); %区间*列车 判断各站是否到站晚点
depart_order = binvar(train_num,train_num,sec_num,'full');% 表示i站列车的发车顺序变量：depart_order（i,j,k）=1时，车站k的列车i先于j发车
adorder = binvar(train_num,train_num,sec_num,'full');% 决策变量sita 表示同一车站两辆列车间的到发顺序：adorder（i,j,k）i从车站（k+1）发车早于j到达车站（k+1）
isDelay = binvar(sec_num,train_num,'full'); %判断各站是否到站晚点：isDelay（j,i）=1,列车i到达j+1站晚点
%track_nums = [2,3,4,2,5, 2, 2, 3, 2, 3, 5];  % 此处需要根据场景车站进行修改，测试场景是7站，所以是7个元素
%track_nums = [1,1,1,1,1, 1, 1, 1, 1, 1, 1];
%track_nums = [10,10,10,10,10, 10, 10, 10, 10, 10, 10];
track_nums = [2,2,2,2,2, 2, 2,2, 2, 2, 2];
max_track_num = max(track_nums);%定义线路中最大车站的到发线（侧线）数量
T_su = 4;
T_sd = 2;
z=binvar(station_num,max_track_num,train_num,'full'); %车站*列车*股道数量 每辆列车在每个车站使用的股道
overrunbin = binvar(sec_num,train_num*(train_num-1)/2,'full');
% overrunbin(列车越行关系01变量):等于1车1在车2前
% 区间1:Trian1*2 Train1*3 Train1*4…(车1与其他车越行约束)Train2*3 Train2*4…（车2与除1外的其他车）…
% 区间2: Trian1*2 Train1*3 Train1*4…(车1与其他车越行约束)Train2*3 Train2*4…（车2与除1外的其他车）…
% …
C = [];


for i=1:train_num
    % 发车时间约束:a1i>=a1i*+delaytime
    C = [C,depart_time(1,i)>=(ActArFirstSta_Time(1,i)+firstPM(1,i)*Ts)];
    for j=1:sec_num
        %计划发车时间约束
        C = [C,depart_time(j,i)>=firstTimetable(2*j,i)];
        %最小停站时间约束（缺少第一站）
        if j>1
            C = [C,depart_time(j,i)-arrive_time(j-1,i)>=firstPM(j,i)*Ts];
        end
        %区间运行时间约束:dij-aij>=qi
        C = [C,arrive_time(j,i)-depart_time(j,i)>=firstMPRT(1,j)];
        %到发时间变量取值约束
        C = [C,arrive_time(j,i)<=1440];
        C = [C,depart_time(j,i)<=1440];
        %是否晚点约束
         C = [C,arrive_time(j,i)-isDelay(j,i)+M*(1-isDelay(j,i))>=firstTimetable(2*(j+1)-1,i)];
         C = [C,arrive_time(j,i)+M*(1-isDelay(j,i))<=firstTimetable(2*(j+1)-1,i)+M];
    end
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%到发时间间隔（不区分停车）%%%%%%%%%%%%%%%%%%%
for i=1:(sec_num-1)
    for j=1:train_num
        for k=1:train_num
            if j~=k
                C = [C,depart_time(i+1,k)-arrive_time(i,j)+M*adorder(k,j,i+1)>=Tz];
                C = [C,depart_time(i+1,k)-arrive_time(i,j)+M*adorder(k,j,i+1)>=1];
                C = [C,depart_time(i+1,k)-arrive_time(i,j)-M*(1-adorder(k,j,i+1))<=-Tz];
            end
        end
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%到发时间间隔（区分停车）%%%%%%%%%%%%%%%%%%%
% for i=1:(sec_num-1)
%     for j=1:train_num
%         for k=1:train_num
%             if j~=k
%                 C = [C,depart_time(i+1,k)-arrive_time(i,j)+M*(2-departorder(k,j,i)-isStop(i+1,k))>=Tz];
%             end
%         end
%     end
% end
% 
% %停站时间约束
% for i=1:train_num
%     for j=1:(sec_num-1)
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)>=Ts*isStop(j+1,i)]; 
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)<=M*isStop(j+1,i)]; 
%     end
% end
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%停站计划约束%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% for i=1:train_num
%     for j=1:sec_num
% 
%         C = [C,isStop(j,i)==firstPM(j,i)];
% 
%     end
% end
% 
% %停站时间约束
% for i=1:train_num
%     for j=1:(sec_num-1)
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)>=Ts*isStop(j+1,i)]; 
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)<=M*isStop(j+1,i)]; 
%     end
% end
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%起停附加时分约束%%%%%%%%%%%%%%%%%%%%%%
% for i=1:train_num
%     for j=2:(sec_num-1)
% 
%         %区间运行时间约束:dij-aij>=qi
%         C = [C,arrive_time(j,i)-depart_time(j,i)>=firstMPRT(1,j)+isStop(j,i)*T_su+isStop(j+1,i)*T_sd];
% 
%     end
% end
% %停站时间约束
% for i=1:train_num
%     for j=1:(sec_num-1)
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)>=Ts*isStop(j+1,i)]; 
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)<=M*isStop(j+1,i)]; 
%     end
% end
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%到到发发时间间隔约束半矩阵(不区分两辆列车是否停车)%%%%%%%%%%%%%%%%%
% for i = 1:sec_num
%     lefttrain_num = train_num-1;
%     accumulatetrain_num = 0;
%     for j = 1:train_num
%         for k=1:lefttrain_num
%             C = [C,depart_time(i,j)-depart_time(i,j+k)>=Tz-(1-overrunbin(i,accumulatetrain_num+k))*M];
%             C = [C,depart_time(i,j+k)-depart_time(i,j)>=Tz-overrunbin(i,accumulatetrain_num+k)*M];
%             C = [C,arrive_time(i,j)-arrive_time(i,j+k)>=Tz-(1-overrunbin(i,accumulatetrain_num+k))*M];
%             C = [C,arrive_time(i,j+k)-arrive_time(i,j)>=Tz-overrunbin(i,accumulatetrain_num+k)*M];    
%         end
%         accumulatetrain_num = accumulatetrain_num+lefttrain_num;
%         lefttrain_num = lefttrain_num-1;
%     end
% end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%到到发发时间间隔约束半矩阵(不区分两辆列车是否停车)%%%%%%%%%%%%%%%%
% for i = 1:sec_num
%     for j = 1:train_num
%         for k = (j+1):train_num            
%             C = [C,depart_time(i,j)-depart_time(i,k)>=Tz-(1-depart_order(k,j,i))*M];
%             C = [C,depart_time(i,k)-depart_time(i,j)>=Tz-depart_order(k,j,i)*M];
%             C = [C,arrive_time(i,j)-arrive_time(i,k)>=Tz-(1-depart_order(k,j,i))*M];
%             C = [C,arrive_time(i,k)-arrive_time(i,j)>=Tz-depart_order(k,j,i)*M];
%         end 
%     end
% end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%到到发发时间间隔约束全矩阵(不区分两辆列车是否停车)%%%%%%%%%%%%%%%%%
for i = 1:sec_num
    for j = 1:train_num
        for k = 1:train_num
            if j~=k
                C = [C,depart_order(j,k,i)+depart_order(k,j,i)==1];
                C = [C,depart_time(i,j)-depart_time(i,k)>=Tz-(1-depart_order(k,j,i))*M];
                C = [C,arrive_time(i,j)-arrive_time(i,k)>=Tz-(1-depart_order(k,j,i))*M];
            end
        end
    end
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%%%%%%%%%%%%%%%%%%%%%%到到发发时间间隔约束全矩阵(区分两辆列车是否停车到达时间间隔约束)%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% for i = 1:(sec_num-1)
%     for j = 1:train_num
%         for k = 1:train_num
%             if j~=k
%                 C = [C,depart_order(j,k,i)+depart_order(k,j,i)==1];
%                 C = [C,depart_time(i+1,k)-depart_time(i+1,j)>=T_max-(2-depart_order(j,k,i+1)-isStop(i+1,j))*M];
%                 C = [C,abs(depart_time(i+1,k)-depart_time(i+1,j))>=T_min-(1-abs(depart_order(j,k,i+1)-isStop(i+1,j)))*M];
%                 C = [C,arrive_time(i,k)-arrive_time(i,j)>=T_max-(2-depart_order(j,k,i)-isStop(i+1,j))*M];
%                 C = [C,abs(arrive_time(i,k)-arrive_time(i,j))>=T_min-(1-abs(depart_order(j,k,i)-isStop(i+1,j)))*M];
%             end
%         end
%     end
% end
% 
% 
% %到到发发时间间隔约束全矩阵(区分两辆列车是否停车首站发车时间间隔约束)
% for i = 1:1
%     for j = 1:train_num
%         for k = 1:train_num
%             if j~=k
%                 C = [C,depart_time(i,j)-depart_time(i,k)>=Tz-(1-depart_order(k,j,i))*M];
%             end
%         end
%     end
% end
% %到到发发时间间隔约束全矩阵(区分两辆列车是否停车末站到达时间间隔约束)
% for i = sec_num:sec_num
%     for j = 1:train_num
%         for k = 1:train_num
%             if j~=k
%                 C = [C,depart_order(j,k,i)+depart_order(k,j,i)==1];
%                 C = [C,arrive_time(i,j)-arrive_time(i,k)>=Tz-(1-depart_order(k,j,i))*M];
%             end
%         end
%     end
% end
% 
% %越行约束
% for i = 1:sec_num
%     for j = 1:train_num
%         for k = 1:train_num
%             if j~=k
%                 C = [C,depart_time(i,j)-depart_time(i,k)>0-(1-depart_order(k,j,i))*M];
%                 C = [C,arrive_time(i,j)-arrive_time(i,k)>0-(1-depart_order(k,j,i))*M];
%             end
%         end
%     end
% end
% 
% %是否停站约束
% for i=1:train_num
%     for j=1:(sec_num-1)
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)>=Ts*isStop(j+1,i)]; 
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)<=M*isStop(j+1,i)]; 
%     end
% end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%车站容量约束(不含股道分配)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% for i=1:(sec_num-1)
%     for j=1:train_num
%         %车站容量约束
% %         x=0;
% %         y=0;
%         C = [C,sum(depart_order(:,j,i))-depart_order(j,j,i)-(sum(adorder(:,j,i+1))-adorder(j,j,i+1))+isStop(i+1,j)<=track_nums(i+1)];
%         %C = [C,sum(depart_order(:,j,i))-depart_order(j,j,i)-(sum(adorder(:,j,i+1))-adorder(j,j,i+1))+1<=track_nums(i+1)];
%         for k=1:train_num
%             if j~=k
%                 %C = [C,adorder(j,k,i+1)+adorder(k,j,i+1)==1];%添加后行车顺序不变
%                 C = [C,arrive_time(i,j)-depart_time(i+1,k)+M*(1-adorder(k,j,i+1))>=Tz];
%                 C = [C,depart_time(i+1,k)-arrive_time(i,j)+M*adorder(k,j,i+1)>0];
% %                 x=x+depart_order(k,j,i);
% %                 y=y+adorder(k,j,i+1);
%             end
%         end
% %        C = [C,x-y+isStop(i+1,j)<=track_nums(i+1)];
%     end
% end
% 
% %停站时间约束
% for i=1:train_num
%     for j=1:(sec_num-1)
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)>=Ts*isStop(j+1,i)]; 
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)<=M*isStop(j+1,i)]; 
%     end
% end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%车站容量约束包含股道分配%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% for i=1:(sec_num-1)
%     itrack_num = track_nums(i+1);
%     for j=1:train_num
%         C = [C,sum(sum(z(i+1,1:itrack_num,j)))==1];
%         for k=1:train_num
%             if j~=k
%                 for ii=1: itrack_num
%                 C = [C,arrive_time(i,j)-depart_time(i+1,k)+M*(3-depart_order(k,j,i)-z(i+1,ii,j)-z(i+1,ii,k))>=Tz];    
%                 end
%             end
%         end
%     end
% end
% % 
% %停站时间与正线通过约束
% for i=1:train_num
%     for j=1:(sec_num-1)
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)>=Ts*isStop(j+1,i)]; 
%         C = [C,depart_time(j+1,i)-arrive_time(j,i)<=M*isStop(j+1,i)]; 
%         C = [C,1-isStop(j+1,i)<=z(j+1,1,i)]; 
%         C = [C,z(j+1,1,i)<=1-isStop(j+1,i)]; 
%     end
% end
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% 配置
ops = sdpsettings('verbose',0,'solver','cplex');
%% 目标函数，总晚点时间最小
DelayFa = sum(sum(depart_time-firstTimetable(2:2:end,:))); % 发车时间
%DelayDao = sum(sum(arrive_time-firstTimetable(3:2:end,:))); % 发车时间
DelayDao = sum(sum((arrive_time-firstTimetable(3:2:end,:)).*isDelay))+sum(sum((arrive_time-firstTimetable(3:2:end,:)).*(0.3*(isDelay-1)))); % 到站时间
J = DelayFa + DelayDao;
saveampl(C,J,'mymodel');
result = solvesdp(C,J,ops);%默认求解目标函数最小值
if result.problem ~= 0 % problem =0 代表求解成功
    disp('求解出错');
end
depart_time=value(depart_time);%通过value函数获取决策变量最优解取值
arrive_time=value(arrive_time);
adorder = value(adorder);
departorder = value(depart_order);
isDelay=value(isDelay);
isStop=value(isStop);
track = value(z);
toc
%求解完整调度时刻表
train_list=zeros(sec_num*2,train_num);
train_list(1:2:end,:)=depart_time;
train_list(2:2:end,:)=arrive_time;
train_list = round(train_list);
Plot_Timetabel( train_list)

h = floor(train_list/60);
m = train_list - h*60;


output=cell(size(h));
for i = 1:size(h,1)
    for j = 1:size(h,2)
        output{i,j}=char(datetime(strcat(num2str(h(i,j)),':',num2str(m(i,j))),'Format','HH:mm'));       
    end
end
xlswrite('output1.xlsx',output)
end
