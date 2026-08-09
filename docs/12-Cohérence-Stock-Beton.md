# Stock béton : article et lots

Le stock article est un total par emplacement. Le stock lot en est le détail.

Toute modification d’un lot applique uniquement son delta au total article.

Cela évite le double comptage et permet aux réservations de contrôler le lot
réellement disponible.
