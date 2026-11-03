# IMN530 – TP1 : Modalités d'imagerie médicale, bruit et débruitage

Ce dépôt contient mon travail pour le TP1 du cours IMN530 (Reconstruction et
analyse d'image médicale) à l'Université de Sherbrooke. Il explore la
manipulation de volumes médicaux au format NIfTI, la caractérisation du bruit
et la comparaison de méthodes de débruitage.

## Contenu

- `view_image.py` : visualiseur interactif avec sliders pour les vues axiale,
  coronale et sagittale. Supporte les images 2D, 3D et 4D.
- `compute_mIP_MIP.py` : calcul des projections d'intensité minimale (mIP) et
  maximale (MIP) selon l'axe choisi.
- `show_image_stats.py` : taille des voxels et des images, contraste de
  Michelson, contraste RMS, estimation du SNR.
- `denoise_image.py` : débruitage des IRM Flair et T1 avec NL-means et deux
  autres méthodes, avec comparaison des résultats.

## Données

Images TDM (CT), IRM (Flair, T1, cœur, épaule, rat) et ultrason.

## Installation

    pip install numpy matplotlib nibabel scipy scikit-image

## Utilisation

    python view_image.py --image chemin/image.nii.gz --axis axial
    python compute_mIP_MIP.py --image chemin/image.nii.gz --axis 2 --mode max
    python show_image_stats.py --image chemin/image.nii.gz
    python denoise_image.py --image chemin/flair.nii.gz --method nlmeans

## Rapport

Le rapport PDF détaille la démarche, les choix de paramètres et l'analyse des
résultats pour chaque étape.
