function [z, X, cvar]= Heuristic2(model)
z=0; 
cij=model.cij; 
bi=model.bi; 
aij=model.aij; 
I=model.I; 
J=model.J;
DIS=model.DIS;
F=model.F;
%% Solution design 
X=zeros(I,J);       % Creating the form for the decision variables   
count=zeros(I, 1);  % Creating the form for the used capacity for agents 
CT=zeros(I,J); 
for i=1:I
    for j=1:J
        CT(i,j)=cij(i,j)+sum(DIS(i,:))+sum(F(j,:));
    end
end
for j=1:J
    [a, b]=min(CT(:,j)); 
    if count(b)<=bi(b)
    X(b,j)=1; 
    count(b)=count(b)+aij(b,j); 
    else
        [c, d]=max(max(CT));
        CT(b,j)=c; 
        [a, b]=min(CT(:,j));
        if count(b)<=bi(b)
        X(b,j)=1; 
        count(b)=count(b)+aij(b,j);
        else
            [c, d]=max(max(CT));
            CT(b,j)=c;
            [a, b]=min(CT(:,j));
            X(b,j)=1; 
        count(b)=count(b)+aij(b,j);
        end
    end
end
% Check the feasibility 
Wij=zeros(I,J);    %Integer varilabes for the main binary varibales 
cvar=zeros(I,1);   % Check the feasibility of capacity 
for i=1:I
   cvar(i)=bi(i)-count(i);
   for j=1:J
    Wij(i,j)=X(i,j)*aij(i,j); 
   end
end
 % Make the solution to be feasible 
 while min(cvar)<0
 for i=1:I
   while cvar(i)<0
    % Removing this j
    [a, b]=max(Wij(i,:)); 
    count(i)=count(i)-aij(i,b);
    cvar(i)=bi(i)-count(i);
    X(i,b)=0; 
    Wij(i,b)=0;
    % Reasigning this j to another i which has enough capacity 
    [c, d]=min(aij(:,b));
    if d==i
        [c, d]=max(cvar); 
    end
    count(d)=count(d)+aij(d,b);
    cvar(d)=bi(d)-count(d);
    X(d,b)=1; 
    Wij(d,b)=aij(d,b);
   end 
 end
 end

%% Objective function 
cij=model.cij; 
for i=1:I
    for j=1:J
        for k=1:I
            for l=1:j
        z=z+cij(i,j)*X(i,j)+X(i,j)*X(k,l)*DIS(i,k)*F(j,l);
            end
        end
    end
end
end

