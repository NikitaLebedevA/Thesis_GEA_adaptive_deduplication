clc; clear all; close all; warning off;
%%
addpath('.././');
AddPaths('.././');

%% Parameter
Info.Iteration=100;
Info.Npop=350;
Info.PCrossover=0.1;
Info.PMutation=0.1;
% Info.MutationIndex=2;
% Info.CrossoverIndex=1;
Info.MaskMutationIndex=2;

Info.NCrossover_Scenario=0.1;
% Info.NMutation_Scenario=0.3;

Info.PFixedX=0.9;

% Info.NGap=1000;     % rate of Continuous to Discrete
Info.PScenario1=0.3;
Info.PScenario2=0.3;
% Info.PScenario3=0.1;
Info.Instraction=[1,1,1];

%% Run Ga
Repeat=20;
MyStruct.MinCost=[];
MyStruct.BestCost=[];
Ans=repmat(MyStruct,Repeat,4);
model=c201575();  %Select the data set
model_name = 'c201575';
% model=c302055();  %Select the data set
Info.Model=model;

%% Call the heuristic
tic;  % This solution is very optimal and feasible 
[z, X, cvar]=Heuristic2(model);   %Provides the best local optimum 
Heuristic2.Cost=z;
Heuristic2.Solution=X;
Heuristic2.Feasibility=cvar; 
Heuristic2.CPU=toc; 

% model=T1();

for j = 1:Repeat
    Solution=Heuristic2;

    display('.........run GEA_3_1.........');
    Info.PScenario3=0.1;
    Info.NMutation_Scenario=0.1;
    [Ans(j,1).MinCost, Ans(j,1).BestCost, pop_GEA3_1, time, Contribution_Rate]=Algorithm_GA_Quadratic(Solution, Info, [0,0,1]);
    Ans(j,1).CPU=time
    Ans(j,1).Gap_GEA3=(Heuristic2.Cost-Ans(j,1).MinCost)/Heuristic2.Cost

    display('.........run GEA_3_2.........');
    Info.PScenario3=0.2;
    Info.NMutation_Scenario=0.3;
    [Ans(j,2).MinCost, Ans(j,2).BestCost, pop_GEA3_2, time, Contribution_Rate]=Algorithm_GA_Quadratic(Solution, Info, [0,0,1]);
    Ans(j,2).CPU=time
    Ans(j,2).Gap_GEA3=(Heuristic2.Cost-Ans(j,2).MinCost)/Heuristic2.Cost

    display('.........run GEA_3_3.........');
    Info.PScenario3=0.3;
    Info.NMutation_Scenario=0.5;
    [Ans(j,3).MinCost, Ans(j,3).BestCost, pop_GEA3_3, time, Contribution_Rate]=Algorithm_GA_Quadratic(Solution, Info, [0,0,1]);
    Ans(j,3).CPU=time
    Ans(j,3).Gap_GEA3=(Heuristic2.Cost-Ans(j,3).MinCost)/Heuristic2.Cost

    display('.........run GEA_3_4.........');
    Info.PScenario3=0.4;
    Info.NMutation_Scenario=0.7;
    [Ans(j,4).MinCost, Ans(j,4).BestCost, pop_GEA3_4, time, Contribution_Rate]=Algorithm_GA_Quadratic(Solution, Info, [0,0,1]);
    Ans(j,4).CPU=time
    Ans(j,4).Gap_GEA3=(Heuristic2.Cost-Ans(j,4).MinCost)/Heuristic2.Cost

%% mean
save(['Saved_Data_Quadratic_Scen3_Sensitivity_' model_name]);
end