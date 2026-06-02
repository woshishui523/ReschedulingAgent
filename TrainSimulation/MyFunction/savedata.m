function savedata(obj)
%函数功能：保存到本地matlab源文件zhuodu.txt
    out=fread(obj,50,'char'); %读取数据
    fid=fopen('zhuodu.txt','a+'); %打开zhuodu.txt
    fprintf(fid,'%s',out); %向文件中写入数据
    fclose(fid); %关闭文件
    d=textscan('G1.txt','%s'); %读取数据
    plot(d); %画出图像
    disp('saveok!'); %输出saveok！