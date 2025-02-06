import requests
import tokenaut



def dadosend():
    try:
        endp = f"https://backend-monitor.mottu.cloud/api/v1/servico/1084318/ObterServicoPainel"
        headers = {
            "Authorization": f"Bearer {tokenaut.token}",  
            "Accept": "application/json",
        }
        response = requests.get(endp, headers=headers)
        response.raise_for_status()  
        dados = response.json()
        print("Resposta da API:")
        print(dados)
        return dados
    except Exception as e:
        print("Erro ao buscar dados:", e)
        return None

dadosend()