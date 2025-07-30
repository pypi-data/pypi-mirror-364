# login_activity/cli.py
import os

def main():
    print("🔐 Bienvenue dans django-login-activity !")
    print("Ce package se configure comme une app Django classique.")
    print("\nÉtapes à suivre :")
    print("1. Ajouter 'login_activity' à INSTALLED_APPS dans settings.py")
    print("2. Ajouter path('login-activity/', include('login_activity.urls')) dans urls.py")
    print("3. Appliquer les migrations avec : python manage.py migrate")
    print("4. Accéder à la vue sur /login-activity/ (connexion requise)")

if __name__ == '__main__':
    main()
