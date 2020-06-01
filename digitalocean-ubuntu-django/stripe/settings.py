INSTALLED_APPS +=(
    "djstripe",
)

STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "<your publishable key>")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "<your secret key>")


DJSTRIPE_PLANS = {
    "monthly": {
        "stripe_plan_id": "pro-monthly",
        "name": "Web App Pro ($24.99/month)",
        "description": "The monthly subscription plan to WebApp",
        "price": 2499,  # $24.99
        "currency": "usd",
        "interval": "month"
    },
    "yearly": {
        "stripe_plan_id": "pro-yearly",
        "name": "Web App Pro ($199/year)",
        "description": "The annual subscription plan to WebApp",
        "price": 19900,  # $199.00
        "currency": "usd",
        "interval": "year"
    }
}