from django.shortcuts import render
from .operations import addition, soustraction, multiplication, division

def index(request):
    resultat = None
    erreur = None

    if request.method == 'POST':
        try:
            a = float(request.POST.get('a', 0))
            b = float(request.POST.get('b', 0))
            operation = request.POST.get('operation')

            if operation == 'add':
                resultat = addition(a, b)
            elif operation == 'sub':
                resultat = soustraction(a, b)
            elif operation == 'mul':
                resultat = multiplication(a, b)
            elif operation == 'div':
                resultat = division(a, b)
            else:
                erreur = "Opération inconnue."
        except Exception as e:
            erreur = str(e)

    return render(request, 'pycalculatrice/index.html', {
        'resultat': resultat,
        'erreur': erreur
    })
