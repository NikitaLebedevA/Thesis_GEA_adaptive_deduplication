function Ans=MaskMutation_Displacement(q,mask,Model)
maskPosition=find(~mask);
n=numel(maskPosition);
if(n>2)
    newq=q(maskPosition);
    Point=sort(randsample(2:n,2));
    temp=q(Point(1):Point(2));
    q1=q(1:Point(1)-1);
    q2=[];
    if(Point(2)~=n)
        q2=q(Point(2)+1:n);
    end
    newq=[temp q1 q2];
    q(maskPosition)=newq;
end
Ans.Position=q;
Ans.Cost=Cost(q,Model);
end
