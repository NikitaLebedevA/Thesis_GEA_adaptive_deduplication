function Ans=MaskMutation_Perturbation(q,mask,Model)
maskPosition=find(~mask);
if(size(maskPosition,2)~=0)
    Point=randsample(maskPosition,1);
    q(Point)=q(Point)+(1/Model.m);
    if (q(Point)>=1)
        q(Point)=q(Point)-1;
    end
end
Ans.Position=q;
Ans.Cost=Cost(q,Model);
end
