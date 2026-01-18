import os

# Credentials
# Use environment variables for security or default to placeholders for testing
USERNAME = os.getenv("PROTHEUS_USER", "usuario_exemplo")
PASSWORD = os.getenv("PROTHEUS_PASSWORD", "senha_exemplo")

# URLs
LOGIN_URL = os.getenv("PROTHEUS_URL", "https://exemplo-protheus.cloudtotvs.com.br/webapp/")
