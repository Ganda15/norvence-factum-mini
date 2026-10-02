# Couverture de tests dans la CI

## Pourquoi la CI était verte pendant l'incident

- Sur le dépôt actuel, les tests ne contiennent aucun montant avec une virgule : la ligne du `if` est exécutée (73 % de lignes), mais la branche « virgule » ne l'est jamais (70 % en branches), et sans `--cov-branch` personne ne le voyait.
- Le test `test_normalize_numeric_input` n'a aucun `assert` : il ne peut pas échouer mais il compte comme couverture (sans lui, on passe de 70 % à 65 %), donc la couverture mesure le code exécuté et non le code vérifié.
- La CI ne mesurait pas la couverture et aucun seuil `fail_under` n'existait : le correctif (commit `733060e`) a modifié `app/normalize.py` sans ajouter de test, et rien ne pouvait faire passer la CI au rouge.

## Seuil retenu et commande de mesure

Le seuil est `fail_under = 85`. Il est défini dans `pyproject.toml`, section `[tool.coverage.report]`, et nulle part ailleurs : la CI et ma machine appliquent donc la même règle.

Pourquoi 85 : avec tous les tests, la couverture totale est de 90,22 %. Sans `tests/test_normalize.py`, elle tombe à 72,83 %. Le seuil doit rester vert pour un changement ordinaire et passer au rouge si les tests disparaissent, donc il se place entre les deux, avec 5 points de marge sous la valeur réelle. Je n'ai pas visé 100 % : Fowler y voit le signe de tests écrits pour le chiffre, et ce seuil sert de filet de sécurité, pas de preuve de qualité.

Preuve dans la CI :

- [PR 1](https://github.com/Ganda15/norvence-factum-mini/pull/1), verte : `Required test coverage of 85.0% reached. Total coverage: 90.22%`.
- [PR 2](https://github.com/Ganda15/norvence-factum-mini/pull/2), qui supprime le fichier de tests, rouge : `FAIL Required test coverage of 85.0% not reached. Total coverage: 72.83%`. Elle a été fermée sans fusion, car elle ne sert qu'à cette démonstration.

Commande pour mesurer en local (la même que dans la CI) :

    uv run pytest --cov=app --cov-branch

Le tableau liste les lignes non couvertes dans la colonne `Missing` (option `show_missing = true`).

Limites :

- Le seuil mesure la couverture, pas la qualité des tests.
- La couverture des conditions n'est pas mesurée (le `and` de la ligne 29 de `app/normalize.py`).
- La classe `HttpLLMClient` n'est pas testée (`llm_client.py` reste à 71 %) et je ne l'ai pas exclue de la mesure.

## Mesure initiale de `app/normalize.py` (02/10/2026)

Commande :

    python -m pytest --cov=app --cov-branch --cov-report=term-missing

| Mesure | Résultat |
|---|---|
| Couverture des lignes (sans `--cov-branch`) | 73 % |
| Couverture des branches (avec `--cov-branch`) | 70 % |

## Pourquoi la ligne du `if` est couverte alors que la branche « virgule » ne l'est pas

La ligne du `if` compte comme couverte parce que Python doit évaluer la condition à chaque appel, même quand elle est fausse, mais la branche « virgule » ne l'est pas parce qu'aucun test n'utilise un montant avec une virgule : la sortie « vrai » du `if` n'a donc jamais été prise.

Source : https://coverage.readthedocs.io/en/7.16.2/branch.html

## Le test qui ne vérifie rien

Le test `test_normalize_numeric_input` ne vérifie rien : il appelle `normalize_amount(1250)` sans aucun `assert`, donc il ne peut jamais échouer. Quand on l'enlève, la couverture des branches de `normalize.py` passe de 70 % à 65 % (la ligne 18 n'est plus exécutée), ce qui montre que la couverture mesure le code qui s'exécute et non le code qui est vérifié.

Mesure faite sans toucher au fichier de tests, avec l'option `--deselect` :

    python -m pytest --cov=app --cov-branch --cov-report=term-missing --deselect tests/test_normalize.py::test_normalize_numeric_input

## Les options `fail_under`, `omit` et `exclude_lines`

- `fail_under` : pourcentage minimum. Si la couverture totale est en dessous, la commande échoue (code 2 pour coverage.py, code 1 quand elle est lancée par pytest) et la CI passe au rouge. Elle ne change pas la mesure, elle sert de garde-fou.
- `omit` : liste de fichiers retirés de la mesure.
- `exclude_lines` : liste d'expressions régulières. Les lignes qui correspondent, et le bloc qu'elles introduisent, ne sont plus comptées comme manquantes.

`omit` et `exclude_lines` permettent de tricher : ils réduisent ce qui est mesuré, donc le pourcentage monte sans qu'aucun test ne soit ajouté.

Exclusion légitime dans ce dépôt : la classe `HttpLLMClient` (`app/llm_client.py`, lignes 29 à 49), avec un commentaire `# pragma: no cover` et la raison écrite. Elle appelle un vrai service réseau avec une clé secrète, ce que les tests unitaires de la CI ne doivent pas faire. Ce n'est qu'un exemple : aucune exclusion n'est appliquée pour l'instant.

Source : https://coverage.readthedocs.io/en/7.16.2/config.html

## Ce que dit Martin Fowler sur la couverture

Pour Fowler, il n'existe pas de bon chiffre à viser. Avec des tests écrits sérieusement, il s'attend à une couverture dans la fourchette haute des 80 % ou des 90 %, et il voit un signe de problème sous la moitié. Il se méfie d'un 100 % : cela ressemble à des tests écrits pour faire monter le chiffre, sans réfléchir. Pour lui, la couverture sert à repérer le code que personne ne teste, pas à mesurer la qualité des tests : si on en fait un objectif, les gens l'atteignent avec des tests de mauvaise qualité, comme un test sans aucune vérification. Il juge qu'on teste assez quand peu de bugs arrivent en production et qu'on n'a pas peur de modifier le code.

Source : https://martinfowler.com/bliki/TestCoverage.html