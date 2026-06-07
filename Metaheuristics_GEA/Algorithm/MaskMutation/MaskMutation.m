function Ans=MaskMutation(Index,q,mask,Model)
switch(Index)
    case 1
    Ans=MaskMutation_Swap(q,mask,Model);
    case 2
    Ans=MaskMutation_BigSwap(q,mask,Model);
    case 3
    Ans=MaskMutation_Inversion(q,mask,Model);
    case 4
    Ans=MaskMutation_Displacement(q,mask,Model);
    case 5
    Ans=MaskMutation_Perturbation(q,mask,Model);
end
end
