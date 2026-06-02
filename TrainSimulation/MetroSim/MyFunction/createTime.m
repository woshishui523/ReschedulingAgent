function y=createTime(x,n)
%函数功能：创建车站序列用于画图（11 22 33）到达和发车
cir=0; %当前圈数
num=0; %当前序号
anum=0; %实际序号
for i=1:x/2
    num=mod(i,n);
    if num==0
        anum=2;
    else
        if num<=n/2+1
            anum=num;
        else
            anum=n/2+1-mod(num,n/2+1) ;
        end
    end
    y(2*(i-1)+1)=anum;
    y(2*i)=anum;
    
end