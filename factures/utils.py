# factures/utils.py

def nombre_en_lettres(nombre):
    """Convertit un nombre (float) en toutes lettres (euros et centimes)"""
    if nombre is None:
        return "zéro CFA"
    
    parts = str(nombre).split('.')
    euros = int(parts[0])
    centimes = int(parts[1]) if len(parts) > 1 else 0
    
    def nombre_lettres(n):
        if n == 0:
            return "zéro"
        units = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
                 "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize",
                 "dix-sept", "dix-huit", "dix-neuf"]
        tens = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
        
        if n < 20:
            return units[n]
        elif n < 70:
            return tens[n // 10] + ("-" + units[n % 10] if n % 10 != 0 else "")
        elif n < 100:
            if n == 71:
                return "soixante-et-onze"
            elif n == 80:
                return "quatre-vingts"
            elif n == 90:
                return "quatre-vingt-dix"
            elif n > 90:
                return "quatre-vingt-" + units[n - 80] if n - 80 < 20 else "quatre-vingt-" + tens[(n - 80) // 10] + ("-" + units[(n - 80) % 10] if (n - 80) % 10 != 0 else "")
            else:
                return tens[n // 10] + ("-" + units[n % 10] if n % 10 != 0 else "")
        return str(n)
    
    def entier_lettres(n):
        if n == 0:
            return ""
        millions = n // 1000000
        reste = n % 1000000
        mille = reste // 1000
        cent = reste % 1000
        
        result = ""
        if millions > 0:
            result += entier_lettres(millions) + " million" + ("s" if millions > 1 else "") + " "
        if mille > 0:
            if mille == 1:
                result += "mille "
            else:
                result += entier_lettres(mille) + " mille "
        if cent > 0:
            if cent < 100:
                result += nombre_lettres(cent)
            else:
                c = cent // 100
                r = cent % 100
                if c == 1:
                    result += "cent "
                else:
                    result += nombre_lettres(c) + " cents "
                if r > 0:
                    result += nombre_lettres(r)
        return result.strip()
    
    if euros == 0 and centimes == 0:
        return "zéro CFA"
    
    phrase = ""
    if euros > 0:
        phrase += entier_lettres(euros) + " FRANC CFA" #+ ("s" if euros > 1 else "")
    if centimes > 0:
        if euros > 0:
            phrase += " et "
        phrase += entier_lettres(centimes) + " centime" + ("s" if centimes > 1 else "")
    phrase += "."
    return phrase.capitalize()