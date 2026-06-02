function k=SigmoidMatch(x,y)
%函数功能：对给定数据进行拟合并返回分界面斜率范围,画出图像
    myfittype=fittype('a./(b+exp(-cx))',...
        'dependent',{'y'},'independent',{'x'},'coefficients',{'a','b','c'});
    %定义sigmoid辨识函数
    myfit=fit(x',y',myfittype);%根据给定数据进行辨识
    plot(myfit,x,y); %画出辨识方程与给定数据的图像
    d=diff(myfit,{'x'}); %对函数进行求导
    max_where=find(d==max(d));%寻找导数最大的位置
    k1=d(max_where); %导数最大值
    y1=y(max_where); %导数最大位置y值
    x1=max_where; %导数最大位置x值
    z=@(x)k1(x-x1)+y1; %定义切线函数
    plot(z,myfit); %画出切线与辨识函数
    k=[k1-5 k1+5];%返回分界面斜率范围
    
