from django.shortcuts import render,redirect

def index(request):
    return render(request, 'convert_aram/index.html')

def resultat(request):
    
    if request.method == 'POST':
        valeur = request.POST.get('valeur')
        taux = request.POST.get('taux')

        try:
            valeur_float = float(valeur)
            taux_float = float(taux)
            resultat = valeur_float * taux_float
        except (ValueError, TypeError):
            resultat = "Entrée invalide."
            return render(request, 'convert_aram/results.html', {
                'resultat': resultat,
                'error': True
            })

        return render(request, 'convert_aram/results.html', {
            'valeur': valeur,
            'taux': taux,
            'resultat': resultat,
            'error': False
        })
    else:
        return redirect('index')
