function minRandArchRatio=CalculateSimplexTratiosPCHA(Xs,numArch,numRuns,numIter, shuffInd)

% Xs is the data subset
% numArch is the number of archetypes
% numRuns is the number of shuffling in the randomization bootstrapping
% numIter is the number of iterations per dataset run

dim = numArch-1; % dimension

minRandArchVol=zeros(numRuns,1);
minRandArchRatio=zeros(numRuns,1);   

for m=1:numRuns

    % Progress bar
    if mod(m,round(numRuns/10)) == 0
        fprintf('%.0f%% done\n', 100*m/numRuns);
    end    

    % Make a shuffled version of X
    for i=1:size(Xs,2) % for each dimension
        X_shuff(:,i)=Xs(shuffInd,i);
    end
    
    VolConvRand(m) = ConvexHull(X_shuff);
    VolArchRand=zeros(1,numIter);
    RandDataRatios=zeros(1,numIter);
    for k=1:numIter
        % PCHA algorithm
        delta = 0;
        U=1:size(X_shuff,1); % Entries in X used that is modelled by the AA model
        I=1:size(X_shuff,1); % Entries in X used to define archetypes
        [Arch3Rand,~,~,~,varexpl]=PCHA1(X_shuff',numArch,I,U,delta);
        % Calculating the volume of the randomized simplex
        if ~isnan(Arch3Rand)
            ArchRandRed=bsxfun(@minus,Arch3Rand,Arch3Rand(:,numArch));
            VolArchRand(k)=abs(det(ArchRandRed(:,1:end-1))/factorial(numArch-1));
            RandDataRatios(k)=VolArchRand(k)./VolConvRand(m);
        else
            VolArchRand(k)= NaN;
            RandDataRatios(k)=NaN;
        end
    end
    
    minRandArchVol(m)=max(VolArchRand);
    minRandArchRatio(m)=max(RandDataRatios);
    
end