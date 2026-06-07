function [z, X, cvar]=CostFunction(X, model)
z=0; 
cij=model.cij; 
bi=model.bi; 
aij=model.aij; 
I=model.I; 
J=model.J;
DIS=model.DIS; 
F=model.F; 
%% Check the feasibility 
cvar=zeros(I,1); 
count=zeros(I,1); 
for i=1:I
   for j=1:J
       count(i)=X(i,j)*aij(i,j)+count(i); 
   end
   cvar(i)=bi(i)-count(i);
end

%% Objective function 
if sum(cvar<0) > 0
    z = inf;
else

 % Objective
    c1=0;
    for i=1:I
        for j=1:J
            c1=c1+cij(i,j)*X(i,j);
        end
    end

    c2=0;
    for i=1:I
        for j=1:J
            for k=1:I
                for l=1:J
                    c2=c2+F(j,l)*DIS(i,k)*X(i,j)*X(k,l);
                end
            end
        end
    end

    z=c1+c2;

cvar = sum(cvar<0);
end

