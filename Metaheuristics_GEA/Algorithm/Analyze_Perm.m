function [DominantGenes, Mask, DominantChromosome, Mask_Dominant]=Analyze_Perm(pop,Info)
%% Data Definition
Npop=size(pop,1);
n=size(pop(1).Position1,2);
NFixedX=floor(Info.PFixedX*Npop);
Mask=zeros(Info.PScenario1*Info.Npop, n);
%% Find Dominant Gene
row=1;
while(row<=Npop)
    col=1;
    while(col<n)
        row_inner=1;
        temp=0;
        while(row_inner<=Npop)
            if (row==row_inner)
                row_inner=row_inner+1;
                continue
            end

            if (pop(row).Position1(1,col) == pop(row_inner).Position1(1,col))
                if (pop(row).Position1(1,col+1) == pop(row_inner).Position1(1,col+1))
                    temp=temp+1;
                end
            end
            row_inner=row_inner+1;
        end

        if (temp>=NFixedX)
            Mask(row, col) = 1;
            Mask(row, col+1) = 1;
            col=col+2;
        else
            col=col+1;
        end
    end
    row=row+1;
end

%% Create Ans :
count = 0;
Domin = [];
Mask_Dominant = [];
for i=1:Npop
    temp=sum(Mask(i,:)==1);
    % Mask(i,:);
    if (temp>=count)
        if (size(Domin,2)==0)
            Domin=pop(i).Position1;
            Mask_Dominant=Mask(i,:);
        else
            decision = rand(1);
            if (decision>0.5)
                Domin=pop(i).Position1;
                Mask_Dominant=Mask(i,:);
            end
        end
        count = temp;
    end
end

DominantChromosome.Position1=Domin;
[DominantChromosome(1).Position1, DominantChromosome(1).Xij] = CreateXij(DominantChromosome(1).Position1, Info.Model);
% evaluate
[DominantChromosome(1).Cost, DominantChromosome(1).Xij, DominantChromosome(1).CVAR]=CostFunction(DominantChromosome(1).Xij, Info.Model);
DominantGenes.Position1 = DominantChromosome;
end
