# coding=utf-8

"""
Tests sur l'analyse du sentiment avec la librairie Pattern
(http://www.clips.ua.ac.be/pages/pattern-fr).
Les tweets viennent de:
http://www.clips.ua.ac.be/media/elections2010.zip
"""

__author__ = 'Pablo Ruiz'
__date__ = '27/03/16'


import inspect
import os
import codecs
import sys

here = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(here)


# 1. Needs Python 2 (2.7).
# Pour Installer pattern: cmd> easy_install pattern


# 2. Importer pattern

from pattern.fr import sentiment as sentiment_fr
from pattern.en import sentiment as sentiment_en
from pattern.fr import tag as tag_fr
from pattern.en import tag as tag_en


# 3. Analyse 1, tweets sur les élections 2010 en Belgique

# On définit quelques opérations (fonctions): =================================
#  lire_tweets
#  analyser_tweets


def lire_tweets(infi):
    """
    Lire fichier de tweets 'infi' et retourner tweets en français selon
    langue affichée sur la 6ème colonne du fichier.
    Retourne liste de tweets
    """
    print "- Lire tweets du fichier '{}'".format(infi)
    liste_tweets = []
    with codecs.open(infi, "r", "utf8") as infd:
        line = infd.readline()
        while line:
            sl = line.strip().split("\t")
            liste_tweets.append({"texte": sl[6], "langue": sl[5],
                                 "personnage_politique": sl[2],
                                 "parti": sl[4]})
            line = infd.readline()
    print "  Lu {} tweets".format(len(liste_tweets))
    return liste_tweets


def analyser_tweets(lst_tweets, lan="fr", fich_sortie=None):
    """
    Appliquer sentiment de Pattern aux tweets de la liste 'lst_tweets',
    pour la langue indiquée dans 'lan'
    On écrit les résultats sur le fichier 'fich_sortie' dans un format
    délimité qui peut être ouvert avec Excel, Calc etc.
    """
    print "- Analyser {} tweets".format(len(lst_tweets))
    # choisir analyseurs selon la langue
    if lan == "fr":
        sentiment_analyzer = sentiment_fr
        tagger = tag_fr
    elif lan == "en":
        sentiment_analyzer = sentiment_en
        tagger = tag_en
    # sélectionner les tweets en français selon l'attribut "langue"
    tweets = [tweet for tweet in lst_tweets
              if tweet["langue"] == lan]
    # traiter chaque tweet
    # garder chaque analyse dans la liste 'lignes_a_ecrire'
    lignes_a_ecrire = []
    for tweet in tweets:
        # tweet avec étiquetage en parties de discours (pos-tagging)
        tweet_avec_pdd = tagger(tweet["texte"])
        # scores de sentiment
        polarite_tweet, subjectivite_tweet = sentiment_analyzer(tweet["texte"])
        # détails sur les indices (mots ou séquences) qui justifient les scores
        sentiment_indices = sentiment_fr.assessments(tweet_avec_pdd)
        # on va écrire ces détails dans la chaîne 'cellule_indices'
        # NOTE: ce n'est pas la façon optimisée de créer des chaînes en Python !
        #       (normalement on devrait utiliser la méthode "join" sur une liste)
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
        # on écrit tous les renseignements sur le tweet dans la chaîne
        # 'analyse_tweet_str'
        analyse_tweet_str = u"{}\t{}\t{}\t{}\n".format(
            polarite_tweet, subjectivite_tweet,
            tweet["texte"].replace('"', ''),
            cellule_indices)
        lignes_a_ecrire.append(analyse_tweet_str)
    # on écrit les lignes dans un fichier de sortie
    if fich_sortie is not None:
        print "- Écriture vers {}".format(fich_sortie)
        entete = u"Polarité\tSubjectivité\tTexte\tIndices\n"
        with codecs.open(fich_sortie, "w", "utf8") as sortie:
            sortie.write(entete)
            for ligne in lignes_a_ecrire:
                sortie.write(ligne)
    # ou on écrit sur l'écran
    else:
        for ligne in lignes_a_ecrire:
            ligne_ecran = ligne.strip().split("\t")
            print u"Pol: {} | Sub: {} | Texte: {} | Indices: {}".format(
                ligne_ecran[0], ligne_ecran[1], ligne_ecran[2],
                ligne_ecran[3].replace("\n", "~~").replace(
                    '"', ''))#.encode("utf8")


# Exécution ===================================================================
# On éxecute les opérations (fonctions) qu'on vient de définir,
# utilistant le ficher d'entree de la variable 'tweets_fichier_entree',
# qui pointe vers le fichier 'harvest_11-6-2010.txt' dans le dossier courant

# Le fichier de sortie s'appelera comme le fichier d'entrée + '.out.txt'

# fichiers
tweets_fichier_entree = os.path.join(here, "harvest_11-6-2010.txt")
analyses_sortie = tweets_fichier_entree + '.out3.txt'

# procédure
ma_liste_de_tweets = lire_tweets(tweets_fichier_entree)
analyser_tweets(ma_liste_de_tweets, "fr", analyses_sortie)

# Si on ne donne pas de fichier de sortie, on écrira sur l'écran
#analyser_tweets(ma_liste_de_tweets)
# changer .encode("latin1") vers .encode("utf8") s'il y a des problèmes
# d'affichage
