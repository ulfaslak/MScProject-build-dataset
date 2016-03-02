function [ output_args ] = sample_points_in_simplex_noise(simp,num_points,noise)
% Choose uniformly random points inside simplex
% simp is (d+1)xd matrix, rows are the vertices of the simplex, columns are dimensions 
    d=size(simp,2);
    A=sort(rand(d,num_points))';
    A=[zeros(num_points,1),A,ones(num_points,1)];
    A=A(:,[2:d+2])-A(:,[1:d+1]);
    output_args=A*simp+noise*(rand(num_points,d)-0.5)
end

