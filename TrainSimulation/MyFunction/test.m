A=[1 1.5];  
B=[0.7 -1.4];   
C=[1 0.85];%对象的参数A B C向量
d=5;
na=length(A)-1;
nb=length(B)-1;
nc=length(C)-1;%na,nb,nc为多项式A B C阶次,C中已经包含P
nf=d-1;
ng=max([na-1,nc-d]);%根据阶次限制求出各多项式阶次
nmax=max([nc,nf+na,ng+d]);
%将B转为常用z-d形式，用于求解丢番图方程
B=zeros(1,nmax);
B(1,d+1)=1;

%建立矩阵
F=sym('x',[1 nf+1]);
G=sym('y',[1 ng+1]);
p1=convar(A,F);
p2=convar(B,G);
%将矩阵整定到相同阶次
if(length(p1)<nmax+1)
    p1(1,nmax+1)=0;
end
if(length(p2)<nmax+1)
    p2(1,nmax+1)=0;
end
if(length(C)<nmax+1)
    C(1,nmax+1)=0;
end
%联立p1 p2 C求解方程
epns=p1+p2-C;
vars=[F,G];
H=sym('h',[1 nf+1+ng+1]);
H=solve(epns,vars);
H=structToarray(H);
F=H(1,1:length(F));
G=H(1,length(F)+1:length(F)+length(G));

