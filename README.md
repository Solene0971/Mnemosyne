pour ajouter le code du bouton à une page admin qui sera dans app/templates/ :

ajouter ce code dans le page admin :

{% include 'includes/_panel_synchro.html' %}
{% endblock %}

dans le fichier app/controllers/SynchroController.py :

retirer la première route vers setup qui a la method 'GET'.

ajouter un controller AdminController.py avec une route qui redirige vers admin.html.

ainsi le code des bouton de synchro seront utilisables sur la page admin finale.
