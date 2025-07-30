from django.shortcuts import render
from .forms import CountryForm
from .data import PHONE_CODES

def phonecode_view(request):
    result = None
    if request.method == "POST":
        form = CountryForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data["country"]
            code = PHONE_CODES.get(country)
            if code:
                result = f"L’indicatif de {country} est : {code}"
            else:
                result = f"Aucun indicatif trouvé pour {country}"
    else:
        form = CountryForm()
    return render(request, "package_phonecode/index.html", {"form": form, "result": result})
