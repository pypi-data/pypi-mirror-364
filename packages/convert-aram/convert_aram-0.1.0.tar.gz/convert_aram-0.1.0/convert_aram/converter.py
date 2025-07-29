def convert_currency(amount, rate):
    """
    Convertit un montant avec un taux donné.
    :param amount: float, montant à convertir
    :param rate: float, taux de conversion
    :return: float, montant converti arrondi à 2 décimales
    """
    try:
        return round(amount * rate, 2)
    except Exception:
        return None
