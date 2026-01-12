### Ajouter les boutons de synchronisation dans la page Admin finale

Dans le dossier des templates :

Ajouter la page `admin.html` avec le code suivant en plus :

```jinja
{% include 'includes/bouton_includes.html' %}
{% endblock %}
```

Dans `app/controllers/SynchroController.py` :

Retirer la première route pointant vers setup. Cette route utilise la méthode GET.

ajouter cette route :

```python
@app.route("/admin")
def admin():
    return render_template("admin.html")
```
