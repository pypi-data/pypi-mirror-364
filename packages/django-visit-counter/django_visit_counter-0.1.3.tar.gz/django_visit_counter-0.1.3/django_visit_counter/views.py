# django_visit_counter/views.py
from django.shortcuts import render

def personalized_visit_view(request):
    visit_count = request.session.get('visit_count', 0) + 1
    request.session['visit_count'] = visit_count

    if visit_count == 1:
        message = "Bienvenue sur notre site ! Voici un guide rapide pour bien démarrer."
        content_type = 'welcome'
    elif 2 <= visit_count <= 5:
        message = "Merci de revenir ! Voici des astuces pour mieux profiter de notre site."
        content_type = 'regular'
    else:
        message = "Vous êtes un visiteur fidèle ! Profitez de notre contenu exclusif."
        content_type = 'vip'

    return render(request, 'visit_counter/personalized.html', {
        'visit_count': visit_count,
        'message': message,
        'content_type': content_type,
    })
