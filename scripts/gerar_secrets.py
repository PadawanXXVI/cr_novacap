import secrets

def gerar_chave_secreta():
    chave = secrets.token_hex(32)
    print(f"\nSECRET_KEY gerada com sucesso:\n\nSECRET_KEY={chave}\n")

if __name__ == "__main__":
    gerar_chave_secreta()
