Outils de traitement de corpus: Sentiment
=========================================

Exercices d'application de la librairie [Pattern](https://www.clips.uantwerpen.be/pages/pattern) pour le français

Les exercices sont inspirés d'un [tutoriel](http://fabelier.org/sentiment-analysis-for-french-by-tom-de-smedt/) par Tom de Smedt

Les étudiants ont obtenu des scores de sentiment sur des tweets (au sujet des élections en Belgique) et sur des reviews de livres sur Amazon. On avait donc deux corpus, et un script pour chaque corpus: 

|Script|Jeu de données|
|--|--|
|[sentiment_reviews.py](./scripts/sentiment_reviews.py)|[books-fr.test-aligned.csv](./données/books-fr.test-aligned.csv)|
|[sentiment_tweets.py](./scripts/sentiment_tweets.py)|[harvest_11-6-2010.txt](./données/harvest_11-6-2010.txt)|

_**Note:** il s'agit de scripts pour un public qui ne maîtrise pas Python et les constructions optimisées ont été écartées en faveur de formulations plus lisibles (ex. compréhensions de listes écartées en faveur des boucles `for`, ou concaténation de chaînes effectuée avec `+=` au lieu d'avec la méthode `join`, pour faciliter la compréhension des étudiants)_

Les instructions sur comment installer la librairie Pattern, et comment éxécuter les scripts Python étaient disponibles sur le moodle du cours. Un PDF avec le contenu des instructions se trouve [ici](./instructions_sur_moodle.pdf).

Les sorties attendues ont aussi été fournies aux étudiants, [ici](./solutions). Les sorties en format délimité (CSV) créés par les scripts ont également été importés dans des tableurs pour un affichage plus convivial et coloration des scores de sentiment. 
