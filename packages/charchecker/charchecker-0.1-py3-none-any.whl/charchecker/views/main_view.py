from django.shortcuts import render

def checker_view(request):
    result = None
    char = ''
    if request.method == "POST":
        char = request.POST.get("char", "")
        if len(char) != 1:
            result = "Veuillez entrer un seul caractère."
        elif char.isalpha():
            result = "C'est une lettre."
        elif char.isdigit():
            result = "C'est un chiffre."
        else:
            result = "C'est un caractère spécial."
    return render(request, "charchecker/checker.html", {"result": result, "char": char})
