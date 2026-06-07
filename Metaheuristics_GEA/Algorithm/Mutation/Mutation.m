function Ans=Mutation(q,Model)

Index = randi([1, 5]);

switch(Index)
    case 1
        Ans=Mutation_Swap(q,Model);
    case 2
        Ans=Mutation_Reversion(q,Model);
    case 3
        Ans=Mutation_Insertion(q,Model);
    case 4
        Ans=Mutation_Random(q,Model);
    case 5
        Ans=Mutation_BigSwap(q,Model);
end
end