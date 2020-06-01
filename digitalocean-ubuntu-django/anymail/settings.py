

INSTALLED_APPS +=(
    "anymail",
)
ANYMAIL = {
    "MANDRILL_API_KEY": "<your Mandrill key>",
}

EMAIL_BACKEND = "anymail.backends.mandrill.MandrillBackend"
