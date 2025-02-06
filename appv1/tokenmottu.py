import requests
import json

def token_mottu():
    url = "https://sso.mottu.cloud/realms/Internal/protocol/openid-connect/token"
    payload = (
        "username=pablo.caique@mottu.com.br&password=PMTUZQX7@"
        "&client_id=mottu-admin&grant_type=password"
    )
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.content.decode()
    result_dict = json.loads(result)
    token = result_dict["access_token"]
    print(token)
    return token

token = token_mottu()