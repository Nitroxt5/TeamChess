def settingsCheck(settings):
    """Checks SETTINGS dict for correctness"""
    if not isinstance(settings, dict):
        return False
    if len(settings) != 2:
        return False
    if not ("sounds" in settings and "language" in settings):
        return False
    if not (isinstance(settings["sounds"], bool) and isinstance(settings["language"], bool)):
        return False
    return True
