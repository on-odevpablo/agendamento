import requests

def token_mottu():
    global token
    url = "https://sso.mottu.cloud/realms/Internal/protocol/openid-connect/token"
    payload = (
        "username=pablo.caique@mottu.com.br&password=PMTUZQX7@"
        "&client_id=mottu-admin&grant_type=password"
    )
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Enviando a requisição POST diretamente
    response = requests.post(url, headers=headers, data=payload)

    # Verificando se a resposta foi bem-sucedida
    if response.status_code == 200:
        result = response.json()
        token = result.get("access_token")
        return token
    else:
        print(f"Erro ao obter o token: {response.status_code} - {response.text}")
        return None
# Chama a função para obter o token
token_mottu()
