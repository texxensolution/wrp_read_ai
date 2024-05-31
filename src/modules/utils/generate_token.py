from src.modules.jwt import JWTGenerator

def generate_token():
    jwt = JWTGenerator()

    generated_token = jwt.generate()

    print(f"Generated token: {generated_token}")