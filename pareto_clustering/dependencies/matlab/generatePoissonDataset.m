function output = generatePoissonDataset(lambda,dimension,num_points,varargin)
    if nargin==3
        noise=0;
    else
        noise=varargin{1};
    end
    dtot=0;
    while dtot<dimension
        d=poissrnd(lambda)+2;
        
        if dtot+d >= dimension-2
            d = dimension - dtot
        elseif dtot+d > dimension
            d = dtot - dimension
        end
       
        if exist('A','var');
            A=[A,sample_points_in_simplex_noise(rand(d+1,d),num_points,noise)];
            div=[div,d];
        else 
            A=sample_points_in_simplex_noise(rand(d+1,d),num_points,noise);
            div = d;
        end
        
        dtot=dtot+d;
    end
    output={A,div};
end

