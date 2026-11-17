function ShowTLcurve(r, zr, tl_zr)
% e3_smpe IO shim (not part of upstream SMPE): headless batch runs skip the
% upstream TL-curve figure. See ShowSoundField.m in this directory.
    disp('plot the transmission loss curve at zr! (skipped by e3_smpe headless shim)');
end
