function Ans=MaskMutation_Swap(q,mask,Model)
maskPosition=find(~mask);
n=numel(maskPosition);
if(n>1)
    newq=q(maskPosition);
    Point=randsample(1:n-1,1);
    newq([Point , Point+1])=newq([Point+1 , Point]);
    q(maskPosition)=newq;
end
Ans.Position=q;
Ans.Cost=Cost(q,Model);
end
