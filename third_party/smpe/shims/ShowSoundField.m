function ShowSoundField(r, z, tl, tlmin, tlmax, casename)
% e3_smpe IO shim (not part of upstream SMPE): headless batch runs skip the
% upstream pcolor figure. The upstream numerical code is untouched; figures
% are produced afterwards in Python from the saved complex field.
    disp('plot the transmission loss field! (skipped by e3_smpe headless shim)');
end
