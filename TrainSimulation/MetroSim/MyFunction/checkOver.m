function [y,ylast,judge]=checkOver(Tr,ylast)
%检测是否发生越行judge 1为发生越行
    y1=sortline(Tr);
    if ~isequal(y1,ylast)
        judge=1;
    else
        judge=0;
    end
    y=y1;
