# TP1 IMN530 - mode d'emploi

## Installation (Windows, invite de commandes dans le dossier TP1)
    python -m venv tp1_env
    tp1_env\Scripts\activate
    pip install -r requirements.txt

## 0. Convertir les formats non NIfTI (une seule fois)
    python convert_to_nifti.py "C:\TP1\Data_TP0\CT\Epaule.pgm" epaule.nii.gz
    python convert_to_nifti.py "C:\TP1\Data_TP0\CT\rat111.vff" rat111.nii.gz
    python convert_to_nifti.py "C:\TP1\Data_TP0\IRM\Heart\PetitAxe" heart.nii.gz
- vff : si l'image est du bruit/illisible, essayez `--vff-endian little` ou `--vff-dtype u1` / `f4`
  (regardez `bits=` dans l'en-tete affiche). Verifiez `--zooms` avec l'en-tete.
- fdf : la taille des voxels est deduite de `roi` (cm) / `matrix`. A VERIFIER dans le procpar.
- us.nii, t1.nii, flair.nii : deja NIfTI, rien a convertir.

## 1. Viewer (Q1a)
    python view_image.py "C:\TP1\Data_TP0\IRM\Brain\t1.nii"
    python view_image.py us.nii --view axial
    python view_image.py heart.nii.gz --mode mean      (4D : moyenne des echos ; sans --mode : slider de volume)

## 2. MIP / mIP (Q1b)
    python compute_mIP_MIP.py t1.nii --axis 2 --mode max --out mip_t1.png
    python compute_mIP_MIP.py t1.nii --axis 1 --mode min --start 40 --end 120 --out mIP_t1.png

## 3. Statistiques (Q2)
    python show_image_stats.py t1.nii --plots stats_t1.png
    (a refaire pour epaule.nii.gz, rat111.nii.gz, flair.nii, heart.nii.gz, us.nii)
Utilisez le viewer pour choisir de bonnes ROIs puis passez --signal-roi / --noise-roi.

## 4. Debruitage (Q3)
    python denoise_image.py flair.nii --slice 80 --out flair_den.png
    python denoise_image.py t1.nii --full --save-prefix t1_den --out t1_den.png

## Orientation (Q1c)
`show_image_stats.py` affiche les codes d'orientation du fichier sur disque (ex. LPS, RAS).
Le viewer reoriente en RAS pour afficher.

