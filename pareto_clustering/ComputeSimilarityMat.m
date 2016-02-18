function S = ComputeSimilarityMat(X,maxSize)

if nargin < 2
    maxdepth = 2;
end

maxRuns = 1;
numIter = 1;
Sdim = size(X,2);

subsets = cell(maxSize-1,1);
for i = 2:maxSize
    subsets{i-1} = nchoosek(1:Sdim, i);
end


S = zeros(Sdim,Sdim);
for elm = 1:length(subsets)
    for feats = 1:size(subsets{elm},1)
        subset = subsets{elm}(feats,:);
        featcombs = nchoosek(subset,2);
        Tratio = CalculateSimplexTratiosPCHA(X(:,subset),length(subset)+1,maxRuns,numIter)
        for fc_i = 1:size(featcombs,1)
            fc = featcombs(fc_i,:);
            S(fc(1),fc(2)) = S(fc(1),fc(2)) + Tratio
        end
    end
end




