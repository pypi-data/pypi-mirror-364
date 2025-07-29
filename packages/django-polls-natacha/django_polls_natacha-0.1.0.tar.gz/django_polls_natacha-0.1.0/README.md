# django-polls

Une application Django réutilisable pour gérer des sondages.

## Installation

```bash
pip install django-polls-natacha



##  Configuration


#Dans settings.py :

##python
#Copier
#Modifier
#INSTALLED_APPS = [
  #  …,
  #  'polls',
# ]
#Dans urls.py :

#python
#Copier
#Modifier
#from django.urls import include, path

#urlpatterns = [
 #   …,
   # path('polls/', include('polls.urls')),
#]
#Puis :


#python manage.py migrate
#t lance le serveur.

