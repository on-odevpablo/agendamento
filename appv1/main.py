import schedule
import time
import requests
import json
import tokenaut
from datetime import datetime

def carregar_dados_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{caminho_arquivo}' está mal formatado.")
        return None

def buscar_carro_por_id(lista_carros, id_carro):
    for carro in lista_carros:
        if carro["veiculo_suporte_id"] == id_carro:
            return carro["placa_veiculo_suporte"], carro["filial_origem_veiculo"]
    return None, None

def enviar_webhook(id_servico, id_carro, horario, placa_api, nome_locatario, placa_suporte, filial):
    avisourl = "https://webhookbot.c-toss.com/api/bot/webhooks/089ba974-a14d-4291-9eb4-1623a402214e"
    agd = {
        "ids_servico": [id_servico],
        "id_carro": id_carro,
        "horario": horario,
        "placa_api": placa_api,
        "nome_locatario": nome_locatario,
        "placa_suporte": placa_suporte,
        "filial": filial,
        "text": f"Serviço da placa {placa_api} ({nome_locatario}) foi agendado para o carro {placa_suporte} ({filial}) às {horario}"
    }

    response = requests.post(
        avisourl,
        json=agd,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        print(f"Webhook enviado com sucesso para o serviço da placa {placa_api}.")
    else:
        print(f"Erro ao enviar webhook: {response.status_code} - {response.text}")

def dadosends(id_servico):
    try:
        endp = f"https://backend-monitor.mottu.cloud/api/v1/servico/{id_servico}/ObterServicoPainel"
        headers = {
            "Authorization": f"Bearer {tokenaut.token}",  
            "Accept": "application/json",
        }
        response = requests.get(endp, headers=headers)
        response.raise_for_status()
        dados = response.json()
        return dados
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao acessar o serviço {id_servico}: {http_err}")
    except Exception as e:
        print(f"Erro geral ao buscar dados para o serviço {id_servico}: {e}")
    return None

def agendamento(id_servico, id_carro, horario, placa_suporte, filial, placa_api, nome_locatario):
    headers = {
        "Authorization": f"Bearer {tokenaut.token}",
        "Referer": "https://monitor.mottu.cloud/",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
    data = {
        "ids_servico": [id_servico],
        "id_carro": id_carro,
        "horario": horario
    }
    try:
        endp = f"https://backend-monitor.mottu.cloud/api/v1/Servico/{id_servico}/encaminhar?veiculoSuporteId={id_carro}&ordem=0"
        response = requests.post(endp, json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"[{horario}] Serviço da placa {placa_api} ({nome_locatario}) foi agendado para o carro {placa_suporte} ({filial}).")
            enviar_webhook(id_servico, id_carro, horario, placa_api, nome_locatario, placa_suporte, filial)
        else:
            print(f"[{horario}] Erro ao processar o serviço {id_servico}. Código: {response.status_code}")
    except Exception as e:
        print(f"[{horario}] Erro serviço:{id_servico} - {str(e)}")
    
    executados.append((id_servico, id_carro, horario, placa_suporte, filial, placa_api, nome_locatario))

# Carregar dados dos carros do arquivo JSON
caminho_json = "idcarros.json"
lista_carros = carregar_dados_json(caminho_json)
if not lista_carros:
    print("Não foi possível carregar os dados dos carros.")
    exit()

lista = []
while True:
    id_servico = input("Digite o ID do serviço (ou pressione Enter para finalizar): ").strip()
    if not id_servico:
        break

    # Busca os dados do serviço via API para obter as informações do cliente
    dados_api = dadosends(id_servico)
    if not dados_api:
        print("Não foi possível buscar os dados do serviço da API.")
        continue

    # Extraindo as informações desejadas: veiculoPlaca e locatarioNome
    locatario = dados_api.get("dataResult", {}).get("locatario", {})
    placa_api = locatario.get("veiculoPlaca")
    nome_locatario = locatario.get("locatarioNome")
    if not placa_api or not nome_locatario:
        print("Informações do cliente não encontradas na resposta da API.")
        continue

    print(f"Placa do cliente obtida: {placa_api}")
    print(f"Nome do cliente obtido: {nome_locatario}")

    # Solicita o ID do carro de suporte e busca os dados correspondentes no JSON
    id_carro = input(f"Digite o ID do carro para o serviço da placa {placa_api}: ").strip()
    placa_suporte, filial = buscar_carro_por_id(lista_carros, id_carro)
    if not placa_suporte:
        print(f"Carro com ID {id_carro} não encontrado. Verifique o ID digitado.")
        continue

    # Solicita o horário para o agendamento
    horario = input(f"Digite o horário para o serviço da placa {placa_api} com o carro {placa_suporte} ({filial}) (formato HH:MM): ").strip()
    lista.append((id_servico, id_carro, horario, placa_suporte, filial, placa_api, nome_locatario))

executados = []

# Configura os agendamentos
for id_servico, id_carro, horario, placa_suporte, filial, placa_api, nome_locatario in lista:
    schedule.every().day.at(horario).do(agendamento,
                                         id_servico=id_servico,
                                         id_carro=id_carro,
                                         horario=horario,
                                         placa_suporte=placa_suporte,
                                         filial=filial,
                                         placa_api=placa_api,
                                         nome_locatario=nome_locatario)
    print(f"Agendamento: Serviço da placa {placa_api} ({nome_locatario}), Carro {placa_suporte} ({filial}) às {horario}")

print("Aguardando agendamentos...")

# Loop principal de execução dos agendamentos
while True:
    schedule.run_pending()
    time.sleep(1)
    if len(executados) == len(lista):
        print("Todos os agendamentos foram concluídos. Finalizando o aplicativo...")
        break
