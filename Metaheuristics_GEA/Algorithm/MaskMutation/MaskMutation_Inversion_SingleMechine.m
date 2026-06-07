function Ans=MaskMutation_Inversion_SingleMechine(q,mask,Model)
    maskPosition=find(~mask);
    n=numel(maskPosition);
    if(n>1)
        newq=q(maskPosition);
        Point=sort(randsample(n,2));
        newq(Point(1):Point(2))=newq(Point(2):-1:Point(1));
        q(maskPosition)=newq;
    end
    Ans.Position=q;
    [Ans.Cost Ans.Sol]=costfun(q,Model);
end
