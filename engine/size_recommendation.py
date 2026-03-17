# ==========================================================
# RECOMENDAÇÃO DE TAMANHO PARA BERMUDA
# ==========================================================
# Regra mais coerente para bermuda:
# o tamanho depende principalmente da cintura.
#
# Tabela base de demo:
# P  -> até 72 cm
# M  -> até 80 cm
# G  -> até 88 cm
# GG -> até 96 cm
# G1 -> até 104 cm
# G2 -> acima disso
# ==========================================================

def recommend_size(waist_cm, hip_cm):
    """
    Recomenda tamanho com base principalmente na cintura.
    O quadril fica como apoio, mas não domina a decisão.
    """

    if waist_cm <= 72:
        return "P"
    elif waist_cm <= 80:
        return "M"
    elif waist_cm <= 88:
        return "G"
    elif waist_cm <= 96:
        return "GG"
    elif waist_cm <= 104:
        return "G1"
    else:
        return "G2"