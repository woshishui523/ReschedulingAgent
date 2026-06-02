function minEntropy=Get_Entropy(u,K,nvarargin)
for i = 1:K
	uh= abs(hilbert(u(i,:))); %最小包络熵计算公式！
	uhs = uh/sum(uh);
    ssum=0;
	for ii = 1:size(uhs,2)
		bb = uhs(1,ii)*log(uhs(1,ii));
        ssum=ssum+bb;
    end
    Entropy(i,:) = -ssum;%每个IMF分量的包络熵
%     disp(['IMF',num2str(i),'的包络熵为：',num2str(Entropy(i,:))])
end
if nvarargin == 1
   minEntropy = Entropy;%求取所有包络熵
else
    minEntropy = min(Entropy);%求取局部最小包络熵，一般用智能优化算法优化VMD，最为最小适应度函数使用
end


% disp(['局部最小包络熵为：',num2str(minEntropy)])
end
