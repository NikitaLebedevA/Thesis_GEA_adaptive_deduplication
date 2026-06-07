function Ans=MaskMutation_BigSwap(q,mask,Model)
maskPosition=find(~mask);
n=numel(maskPosition);
if(n>1)
    newq=q(maskPosition);
    Point=randsample(1:n,2);
    newq([Point(2) , Point(1)])=newq([Point(1) , Point(2)]);
    q(maskPosition)=newq;
end
Ans=q;
% [Ans.Position1, Ans.Xij, Ans.CVAR] = CreateXij(Ans.Position1, Model);
% Ans.Cost=CostFunction(Ans.Xij,Model);
end
