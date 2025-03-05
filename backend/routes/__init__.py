"""Routes package for the Decision Points API."""
from flask import Blueprint

# Import route modules to register them
from . import auth, market, business, features, deployment, cashflow

__all__ = ['auth', 'market', 'business', 'features', 'deployment', 'cashflow']