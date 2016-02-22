function ShufToOrigRatio = CalculateSimplexTratiosPCHA_mod(Xs, shuffInd)

% Xs is the data subset
% shuffInd is the index-array that governs the order of shuffling

N = size(Xs,1); M = size(Xs,2);
%numArch = M + 1;

% Make a shuffled version of X
for i=1:M
    X_shuff(:,i)=Xs(shuffInd(i,:),i);
end

% PCHA algorithm init params
%delta = 0;
%I = 1:N; U = 1:N;

% PCHA for shuffled and non-shuffled



% Calculating the volumes of simplices
%[Arch3Shuf,~,~,~,varexplShuf]=PCHA1(X_shuff',numArch,I,U,delta);
%ArchShufRed = bsxfun(@minus,Arch3Shuf,Arch3Shuf(:,numArch));
%VolArchShuf = abs(det(ArchShufRed(:,1:end-1))/factorial(M));
%[Arch3Orig,~,~,~,varexplOrig]=PCHA1(Xs',numArch,I,U,delta);
%ArchOrigRed = bsxfun(@minus,Arch3Orig,Arch3Orig(:,numArch));
%VolArchOrig = abs(det(ArchOrigRed(:,1:end-1))/factorial(M));

%ShufToOrigArcRatio =VolArchShuf./VolArchOrig

scatterplot(Xs)
scatterplot(X_shuff)

ShufToOrigRatio = ConvexHull(X_shuff) / ConvexHull(Xs);
