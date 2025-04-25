# This file makes the 'schemas' directory a Python package.

# Make schemas available when importing the package
from .user import User, UserUpdate
from .token import Token, TokenData
