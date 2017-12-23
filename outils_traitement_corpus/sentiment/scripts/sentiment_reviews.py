# coding=utf-8

"""
Tests sur l'analyse du sentiment avec la librairie Pattern
(http://www.clips.ua.ac.be/pages/pattern-fr).
Les reviews amazon viennent de
http://fabelier.org/sentiment-analysis-for-french-by-tom-de-smedt/
"""

__author__ = 'Pablo Ruiz'
__date__ = '31/03/16'


import inspect
import os
import codecs
import re
import sys


here = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(here)


DEBUG = False
WRITE_METRICS = False


# 1. Needs Python 2 (2.7).
# Pour Installer pattern: cmd> easy_install pattern


# 2. Importer pattern

from pattern.fr import sentiment as sentiment_fr
from pattern.en import sentiment as sentiment_en
from pattern.fr import tag as tag_fr
from pattern.en import tag as tag_en


# On définit quelques opérations (fonctions): =================================
#  lire_textes
#  analyser_textes


def lire_textes(infi):
    """
    Lire fichier de reviews de référence 'infi' et retourner textes avec
    leur étiquette de polarité de référence ("pos" ou "neg").
    On retourne 'liste_textes' avec ces infos
    """
    print "- Lire textes du fichier '{}'".format(infi)
    liste_textes = []
    with codecs.open(infi, "r", "utf8") as infd:
        line = infd.readline()
        lnbr = 1
        while line:
            # pour enlever format CSV, diviser lignes avec '","',
            # éliminer guillemet ouvrant et fermant de la ligne
            sl = re.split('","', line.strip()[1:-1])
            # premier champ après division est le texte (champ à index 0)
            texte = sl[0]
            # deuxième champ (à index 1) est la polarité
            pol = "pos" if sl[1] == "True" else "neg"
            if DEBUG:
                print lnbr, texte, pol
            lnbr += 1
            # on ajoute à 'liste_textes'
            liste_textes.append({"texte": texte, "polarite": pol})
            line = infd.readline()
    print "  Lu {} textes".format(len(liste_textes))
    # on retourne la liste qu'on a créé
    return liste_textes


def analyser_textes(lst_textes, lan="fr", fich_sortie=None):
    """
    Appliquer sentiment de Pattern aux textes de la liste 'lst_textes',
    pour la langue indiquée dans 'lan' (par défaut, "fr")
    On écrit les résultats sur le fichier 'fich_sortie' dans un format
    délimité qui peut être ouvert avec Excel, Calc etc.
    """
    print "- Analyser {} textes".format(len(lst_textes))
    # choisir analyseurs selon la langue
    if lan == "fr":
        sentiment_analyzer = sentiment_fr
        tagger = tag_fr
    elif lan == "en":
        sentiment_analyzer = sentiment_en
        tagger = tag_en
    # traiter chaque texte
    # garder chaque analyse dans la liste 'lignes_a_ecrire'
    lignes_a_ecrire = []
    # pour évaluer avec précision, rappel, f-mesure
    # vrais positifs, faux positifs, faux négatifs
    #     pour les catégories pos et neg
    pos_vp, pos_fp, neg_vp, neg_fp, pos_fn, neg_fn = 0, 0, 0, 0, 0, 0
    ## BOUCLE POUR TRAITER LES TEXTES =========================================
    for idx, texte in enumerate(lst_textes):
        # texte avec étiquetage en parties de discours (pos-tagging)
        texte_avec_pdd = tagger(texte["texte"])
        # scores de sentiment
        polarite_texte, subjectivite_texte = sentiment_analyzer(texte["texte"])
        # détails sur les indices (mots ou séquences) qui justifient les scores
        sentiment_indices = sentiment_fr.assessments(texte_avec_pdd)
        # on va écrire ces détails dans la chaîne 'cellule_indices'
        # Attention, on ne devrait pas concatenner des chaînes comme ça (trop lent),
        # on devrait collecter tout dans une liste et faire join là-dessus,
        # mais pour ce cours c'est pas grave
        cellule_indices = '"'
        for indice in sentiment_indices:
            # Chaque indice à 4 champs. Commençant à compter par l'index 0:
            #   0: mots de l'indice, 1: polarité, 2: subjectivité, 3: 'mood' (ou rien)
            # mots de l'indice joints par des espaces
            mots_str = " ".join(indice[0])
            polarite_indice, subjectivite_indice, mood = \
                indice[1], indice[2], indice[3]
            indices_str = u"{}, {}, {}, {}".format(mots_str, polarite_indice,
                                                   subjectivite_indice, mood)
            cellule_indices += indices_str
            # on ajout saut de ligne s'il y a plus d'un indice
            if len(sentiment_indices) > 1:
                cellule_indices += "\n"
        cellule_indices += '"'
        # évaluation --------------------------------------
        #   résultat du système est positif
        if polarite_texte > 0:
            #  référence positive aussi => vrai positif pour pos
            if texte["polarite"] == "pos":
                evalu = "pos_vp"
                pos_vp += 1
            #  référence négative => faux positif pour pos
            #                        (et faux négatif pour neg)
            else:
                evalu = "pos_fp~neg_fn"
                pos_fp += 1
                neg_fn += 1
        #   résultat du système est négatif
        #   (on a assumé que exactement '0' est négatif)
        elif polarite_texte <= 0:
            #  référence négative aussi => vrai positif pour neg
            if texte["polarite"] == "neg":
                evalu = "neg_vp"
                neg_vp += 1
            #  référence positive => faux positif pour neg
            #                        et faux négatif pour pos
            else:
                evalu = "neg_fp~pos_fn"
                neg_fp += 1
                pos_fn += 1
        # on écrit tous les renseignements sur la review dans la chaîne
        # 'analyse_texte_str'
        analyse_texte_str = u"{}\t{}\t{}\t{}\t{}\t{}\n".format(
            polarite_texte, subjectivite_texte,
            texte["texte"].replace('"', ''),
            cellule_indices, texte["polarite"], evalu)
        lignes_a_ecrire.append(analyse_texte_str)
        # messages à tous les 100 lignes (opérateur modulus '%')
        if idx > 0 and not idx % 100:
            print "  - Done {} lines".format(idx)
    ## ÉCRITURE DE LA SORTIE ==================================================
    # on écrit les lignes dans un fichier de sortie
    if fich_sortie is not None:
        print "- Écriture vers {}".format(fich_sortie)
        entete = u"Polarité\tSubjectivité\tTexte\tIndices\tRéférence\tÉvaluation\n"
        with codecs.open(fich_sortie, "w", "utf8") as sortie:
            sortie.write(entete)
            for ligne in lignes_a_ecrire:
                sortie.write(ligne)
            Ppos = float(pos_vp) / (pos_vp + pos_fp)
            Rpos = float(pos_vp) / (pos_vp + pos_fn)
            Pneg = float(neg_vp) / (neg_vp + neg_fp)
            Rneg = float(neg_vp) / (neg_vp + neg_fn)
            F1pos = (2 * Ppos * Rpos) / (Ppos + Rpos)
            F1neg = (2 * Pneg * Rneg) / (Pneg + Rneg)
            assert pos_vp + neg_vp + pos_fn + neg_fn == len(lst_textes)
            ratio_corrects = (pos_vp + neg_vp) / float(len(lst_textes))
            if WRITE_METRICS:
                sortie.write(
                    "vp_pos: {}\nfp_pos: {}\nfn_pos: {}\n"
                    "vp_neg: {}\nfp_neg: {}\nfn_neg: {}\n".format(
                    pos_vp, pos_fp, pos_fn, neg_vp, neg_fp, neg_fn))
                sortie.write(u"Ppos: {}\n".format(Ppos))
                sortie.write(u"Rpos: {}\n".format(Rpos))
                sortie.write(u"F1pos: {}\n".format(F1pos))
                sortie.write(u"Pneg: {}\n".format(Pneg))
                sortie.write(u"Rneg: {}\n".format(Rneg))
                sortie.write(u"F1neg: {}\n".format(F1neg))
                sortie.write(u"Ratio_OK: {}\n".format(ratio_corrects))
    # ou on écrit sur l'écran
    else:
        for ligne in lignes_a_ecrire:
            ligne_ecran = ligne.strip().split("\t")
            print u"Pol: {} | Sub: {} | Texte: {} | Indices: {}".format(
                ligne_ecran[0], ligne_ecran[1], ligne_ecran[2],
                ligne_ecran[3].replace("\n", "~~").replace(
                    '"', '')).encode("latin1")


# Exécution ===================================================================
# On éxecute les opérations (fonctions) qu'on vient de définir,
# utilistant le ficher d'entree de la variable 'reviews_fichier_entree',
# qui pointe vers le fichier 'books-fr.test-aligned.csv' dans le dossier courant

# Le fichier de sortie s'appelera comme le fichier d'entrée + '.out.txt'

# fichiers
reviews_fichier_entree = os.path.join(here, "books-fr.test-aligned.csv")
analyses_sortie = reviews_fichier_entree + '.out.txt'

# procédure
mes_reviews_et_scores_ref = lire_textes(reviews_fichier_entree)
analyser_textes(mes_reviews_et_scores_ref, "fr", analyses_sortie)

# Si on ne donne pas de fichier de sortie, on écrira sur l'écran
#analyser_textes(mes_reviews_et_scores_ref)
# changer .encode("latin1") vers .encode("utf8") s'il y a
# des problèmes d'affichage
