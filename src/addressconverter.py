def email_to_localpart(email: str):
    """The returned localpart can be appended with a @ or #
    depending on usage."""
    return "mailkill_"+email.replace("@", "__")