function S = ComputeSimilarityMat(X,maxSize)

% Set algorithm parameters
maxRuns = 1;
numIter = 1;
Sdim = size(X,2);

S = zeros(Sdim,Sdim)

% Create subsets and one empty matrix for each length-class
for i = 2:maxSize
    subsets{i-1} = nchoosek(1:Sdim, i);
    S_sizes{i-1} = zeros(Sdim,Sdim);
end

% Loop though each subset length-class
for i = 1:length(subsets)
    subset_len_i = subsets{i};
    % Loop through each subset j in length-class i
    for j = 1:size(subset_len_i,1)
        subset = subset_len_i(j,:);
        featpairs = nchoosek(subset,2);
        Tratio = CalculateSimplexTratiosPCHA(X(:,subset),length(subset)+1,maxRuns,numIter);
        for fp_k = 1:size(featpairs,1)
            fp = featpairs(fp_k,:);
            S_sizes{i}(fp(1),fp(2)) = S_sizes{i}(fp(1),fp(2)) + Tratio;
            S_sizes{i}
        end
    end
    non_zero_i = nonzeros(reshape(S_sizes{i},1,Sdim*Sdim));
    mean_i = mean(non_zero_i);
    std_i = std(non_zero_i);
    
    S_sizes{i} = (S_sizes{i})/mean_i
    
    S = S + S_sizes{i}/(maxSize-1)
    
end




