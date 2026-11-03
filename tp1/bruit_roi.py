import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

chemin = r"C:\Users\Administrator\Desktop\Data_TP1\Data_TP0\IRM\Brain\t1.nii"
d = nib.load(chemin).get_fdata()
roi = d[0:25, 0:25, 88].ravel()
#roi = d[5:31, 225:246, 88].ravel()      # meme ROI de bruit que --noise-roi 5 30 225 245 88 88

print("moyenne :", roi.mean())
print("ecart-type :", roi.std())
print("minimum :", roi.min())
print("moyenne / ecart-type :", roi.mean() / roi.std())

plt.hist(roi, bins=40)
plt.title("Histogramme de la ROI de bruit")
plt.xlabel("intensite")
plt.ylabel("nombre de voxels")
plt.savefig("hist_bruit_t1.png", dpi=130)
plt.show()