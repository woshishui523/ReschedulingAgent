M=5;%列车数量
N=3;%站台数
syms p;
syms q;
syms z;
syms c;
a=-c/(1-c);
b=1/(1-c);
Im=eye(3);
Bl=[
zeros(M-N,N);    
eye(N);
];
Al=[
zeros(M-N,1) eye(M-N) zeros(M-N,N-1);    
[
0 0 a b 0;
0 0 0 a b;
b 0 0 0 a;
] 
];
SN=[
0 1 0 0 0;
0 0 1 0 0;
0 0 0 1 0;
0 0 0 0 1;
1 0 0 0 0;
];
x=createvarmatrix(1,M);%生成x矩阵
u=createvarmatrix(1,N);%生成u矩阵
answer1=inv(Im+Bl'*(p+q)*Bl)*(Bl'*(p+q)*Al-Bl'*q*SN);
answer2=answer1*x';