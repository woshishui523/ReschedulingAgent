%定义变量
x=sdpvar(2,1);
%目标函数
obj=2*x(1)+3*x(2);
%约束条件
constraint=[];
constraint=[constraint,x(1)+x(2)>350];
constraint=[constraint,x(1)>100];
constraint=[constraint,2*x(1)+x(2)<600];
constraint=[constraint,x(2)>0];
%求解
ops = sdpsettings('solver','cplex','verbose',1);
ops.cplex.display='on';
ops.cplex.timelimit=600;
ops.cplex.mip.tolerances.mipgap=0.001;
% 诊断求解可行性
disp('开始求解')
diagnostics=optimize(constraint,obj,ops);
if diagnostics.problem==0
    disp('Solver thinks it is feasible')
elseif diagnostics.problem == 1
    disp('Solver thinks it is infeasible')
    pause();
else
    disp('Timeout, Display the current optimal solution')
end