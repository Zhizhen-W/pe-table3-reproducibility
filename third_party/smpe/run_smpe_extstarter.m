% e3_smpe batch wrapper for the documented external-starter variant
% SMPE_extstarter.m (copy of upstream SMPE.m; see its header for the changes).
% Run directory must contain input_SMPE.txt and starter_external.txt.
addpath(SMPE_SRC);
addpath(E3_SHIMS);
addpath(E3_OCTAVE_DIR);
SMPE_extstarter;
elapsed_internal_s = toc;
save('-v7', 'smpe_out.mat', 'r', 'z', 'u', 'k0', 'dr', 'freq', 'zs', 'zr', ...
     'Coll', 'np', 'ns', 'c0', 'depth', 'Layers', 'Lowerboundary', ...
     'elapsed_internal_s', 'r0');
