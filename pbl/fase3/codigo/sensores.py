"""
FarmTech Solutions – Simulador de Sensores Agrícolas
Fase 3 – PBL Inteligência Artificial / FIAP

Simula a leitura de sensores de campo e exporta os dados para CSV,
prontos para importação no Oracle SQL Developer.

Sensores simulados:
  - Umidade do solo (%)
  - Fósforo disponível (ppm)
  - Potássio disponível (ppm)
  - pH do solo
  - Temperatura ambiente (°C)
  - Precipitação (mm)
  - Status da irrigação (0 = desligada, 1 = ligada)
"""

import csv
import random
import os
from datetime import datetime, timedelta

# ──────────────────────────────────────────────
# Configurações
# ──────────────────────────────────────────────
ARQUIVO_SAIDA = "dados/sensores_fase2.csv"
DIAS_SIMULADOS = 7
LEITURAS_POR_DIA = 4          # a cada 6 horas
UMIDADE_IRRIGACAO = 40.0      # aciona irrigação abaixo deste valor
UMIDADE_ALVO = 60.0           # umidade desejada após irrigação

COLUNAS = [
    "data_hora",
    "umidade_solo",
    "fosforo",
    "potassio",
    "pH",
    "irrigacao_ativa",
    "temperatura",
    "chuva_mm",
]


# ──────────────────────────────────────────────
# Funções auxiliares
# ──────────────────────────────────────────────
def simular_leitura(dt: datetime, umidade_anterior: float) -> dict:
    """Gera uma leitura de sensores para o instante dt."""

    hora = dt.hour

    # Temperatura varia com a hora do dia
    if 6 <= hora < 12:
        temp = round(random.uniform(20, 27), 1)
    elif 12 <= hora < 18:
        temp = round(random.uniform(27, 33), 1)
    else:
        temp = round(random.uniform(18, 22), 1)

    # Chuva ocorre com 20 % de chance no período noturno/vespertino
    chuva = round(random.uniform(2, 12), 1) if (hora >= 16 and random.random() < 0.2) else 0.0

    # Umidade do solo — evapora durante o dia, aumenta com chuva
    evapotranspiracao = random.uniform(1.5, 4.0) if 10 <= hora < 18 else random.uniform(0.2, 1.0)
    umidade = max(20.0, umidade_anterior - evapotranspiracao + chuva * 0.5)

    # Lógica de irrigação
    irrigacao = 0
    if umidade < UMIDADE_IRRIGACAO:
        irrigacao = 1
        umidade = UMIDADE_ALVO + random.uniform(-2, 2)

    return {
        "data_hora": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "umidade_solo": round(umidade, 1),
        "fosforo": random.randint(25, 35),
        "potassio": random.randint(30, 42),
        "pH": round(random.uniform(5.8, 7.0), 1),
        "irrigacao_ativa": irrigacao,
        "temperatura": temp,
        "chuva_mm": chuva,
    }


def gerar_csv(caminho: str, dias: int, leituras_dia: int) -> None:
    """Gera o arquivo CSV com todas as leituras simuladas."""

    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    inicio = datetime(2025, 4, 1, 6, 0, 0)
    intervalo = timedelta(hours=24 // leituras_dia)

    umidade_atual = 55.0
    registros = []

    dt = inicio
    for _ in range(dias * leituras_dia):
        leitura = simular_leitura(dt, umidade_atual)
        umidade_atual = leitura["umidade_solo"]
        registros.append(leitura)
        dt += intervalo

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS)
        writer.writeheader()
        writer.writerows(registros)

    print(f"✅  {len(registros)} leituras salvas em '{caminho}'")
    print(f"    Período: {registros[0]['data_hora']} → {registros[-1]['data_hora']}")


def exibir_resumo(caminho: str) -> None:
    """Exibe as primeiras linhas e estatísticas básicas do CSV gerado."""

    with open(caminho, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    print(f"\n{'─'*55}")
    print(f"  Resumo do arquivo: {caminho}")
    print(f"{'─'*55}")
    print(f"  Total de registros : {len(linhas)}")

    umidades = [float(l["umidade_solo"]) for l in linhas]
    irrigacoes = sum(1 for l in linhas if l["irrigacao_ativa"] == "1")

    print(f"  Umidade média      : {sum(umidades)/len(umidades):.1f} %")
    print(f"  Umidade mín/máx    : {min(umidades):.1f} % / {max(umidades):.1f} %")
    print(f"  Irrigações acionadas: {irrigacoes} vez(es)")
    print(f"{'─'*55}\n")

    print("  Primeiras 5 leituras:")
    print(f"  {'DATA/HORA':<20} {'UMID':>5} {'P':>4} {'K':>4} {'pH':>5} {'IRR':>4} {'TEMP':>6} {'CHUVA':>6}")
    for l in linhas[:5]:
        print(
            f"  {l['data_hora']:<20} "
            f"{l['umidade_solo']:>5} "
            f"{l['fosforo']:>4} "
            f"{l['potassio']:>4} "
            f"{l['pH']:>5} "
            f"{'SIM' if l['irrigacao_ativa']=='1' else 'NÃO':>4} "
            f"{l['temperatura']:>6} "
            f"{l['chuva_mm']:>6}"
        )
    print()


# ──────────────────────────────────────────────
# Execução principal
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🌱  FarmTech Solutions – Gerador de Dados de Sensores\n")
    gerar_csv(ARQUIVO_SAIDA, DIAS_SIMULADOS, LEITURAS_POR_DIA)
    exibir_resumo(ARQUIVO_SAIDA)
