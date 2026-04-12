import getpass
import os
import sys
from anthropic import Anthropic, APIConnectionError, AuthenticationError, RateLimitError
from dotenv import load_dotenv


# Catálogo de modelos disponibles

MODELS = [
    {
        "id": "claude-opus-4-6",
        "name": "Claude Opus 4.6",
        "description": "Modelo para razonamiento complejo, agentes y tareas exigentes.",
        "input_price_per_1m": 5.00,
        "output_price_per_1m": 25.00,
        "max_output_tokens": 128000,
    },
    {
        "id": "claude-sonnet-4-6",
        "name": "Claude Sonnet 4.6",
        "description": "Mejor equilibrio entre velocidad, coste e inteligencia para uso general.",
        "input_price_per_1m": 3.00,
        "output_price_per_1m": 15.00,
        "max_output_tokens": 64000,
    },
    {
        "id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5",
        "description": "La opción más rápida y económica para alto volumen y baja latencia.",
        "input_price_per_1m": 1.00,
        "output_price_per_1m": 5.00,
        "max_output_tokens": 64000,
    },
    {
        "id": "claude-opus-4-5-20251101",
        "name": "Claude Opus 4.5",
        "description": "Modelo heredado premium, muy potente para tareas complejas especializadas.",
        "input_price_per_1m": 5.00,
        "output_price_per_1m": 25.00,
        "max_output_tokens": 128000,
    },
    {
        "id": "claude-sonnet-4-5-20250929",
        "name": "Claude Sonnet 4.5",
        "description": "Modelo heredado equilibrado, sólido para desarrollo y uso general.",
        "input_price_per_1m": 3.00,
        "output_price_per_1m": 15.00,
        "max_output_tokens": 64000,
    },
]

# Niveles de creatividad: nombre legible → temperatura (rango Anthropic: 0.0–1.0)
CREATIVITY_LEVELS = [
    {"label": "Preciso",      "description": "Respuestas deterministas, sin variación.",   "temperature": 0.0},
    {"label": "Conservador",  "description": "Respuestas fiables con mínima variación.",   "temperature": 0.3},
    {"label": "Equilibrado",  "description": "Balance entre coherencia y variedad.",        "temperature": 0.6},
    {"label": "Creativo",     "description": "Respuestas más espontáneas y expresivas.",   "temperature": 0.8},
    {"label": "Muy creativo", "description": "Máxima originalidad, menos predecible.",     "temperature": 1.0},
]

##########################################################################################################################################################################################################################################

#API key del entorno o por entrada segura.

def get_client() -> Anthropic:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY") or getpass.getpass("Introduce tu API Key de Anthropic: ")
    return Anthropic(api_key=api_key)

#Tokens de entradas

def contar_tokens(client: Anthropic, pregunta: str, model_id: str) -> int:
    respuesta = client.messages.count_tokens(
        model=model_id,
        messages=[{"role": "user", "content": pregunta}],
    )
    return respuesta.input_tokens

#Coste

def calcular_coste(tokens: int, precio_por_millon: float) -> float:
    return (tokens / 1_000_000) * precio_por_millon


##########################################################################################################################################################################################################################################
#Paso 1: Solicita la pregunta por consola.

def obtener_pregunta() -> str:
    print("\n" + "=" * 60)
    print("  Consulta personalizada a modelos Claude (Anthropic)")
    print("=" * 60)

    while True:
        pregunta = input("\nIntroduce tu pregunta:\n> ").strip()
        if pregunta:
            return pregunta
        print("La pregunta no puede estar vacía. Inténtalo de nuevo.")

#Paso 2: Muestra el número de tokens de entrada y lo devuelve.

def mostrar_tokens(client: Anthropic, pregunta: str) -> int:
    tokens = contar_tokens(client, pregunta, MODELS[0]["id"])
    print(f"\nTokens de entrada: {tokens}")
    return tokens

#Paso 3: Muestra los modelos con su coste de entrada estimado y devuelve el elegido.

def seleccionar_modelo(tokens: int) -> dict:
    print("\n" + "-" * 60)
    print("Modelos disponibles:")
    print("-" * 60)

    for i, modelo in enumerate(MODELS, start=1):
        coste_entrada = calcular_coste(tokens, modelo["input_price_per_1m"])
        print(
            f"  [{i}] {modelo['name']}\n"
            f"      {modelo['description']}\n"
            f"      Entrada: ${coste_entrada:.6f} USD  (${modelo['input_price_per_1m']:.2f}/1M tokens)\n"
        )

    while True:
        opcion = input(f"Selecciona un modelo [1-{len(MODELS)}]: ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(MODELS):
            seleccionado = MODELS[int(opcion) - 1]
            print(f"\nModelo: {seleccionado['name']}")
            return seleccionado
        print(f"Introduce un número entre 1 y {len(MODELS)}.")

#Paso 4: Solicita el límite de tokens de salida. Si el usuario deja vacío, se usa el máximo del modelo. La API de Anthropic requiere siempre

def obtener_limite_tokens(max_modelo: int) -> int:
    print("\n" + "-" * 60)
    print(f"Límite de tokens de salida (máximo del modelo: {max_modelo})")
    print("Deja vacío para sin límite (se usará el máximo del modelo).")
    print("-" * 60)

    while True:
        entrada = input("Tokens de salida (o Enter para máximo): ").strip()
        if entrada == "":
            print(f"Sin límite. Se usarán {max_modelo} tokens máximos.")
            return max_modelo
        if entrada.isdigit() and 0 < int(entrada) <= max_modelo:
            print(f"Límite: {int(entrada)} tokens.")
            return int(entrada)
        print(f"Introduce un número entre 1 y {max_modelo}, o deja vacío.")

# ** Muestra un resumen de costes estimados antes de confirmar la consulta.

def mostrar_resumen_coste(modelo: dict, tokens_entrada: int, max_tokens_salida: int) -> None:
    coste_entrada = calcular_coste(tokens_entrada, modelo["input_price_per_1m"])
    coste_salida_max = calcular_coste(max_tokens_salida, modelo["output_price_per_1m"])
    coste_total_max = coste_entrada + coste_salida_max

    print("\n" + "=" * 60)
    print("  Resumen de costes estimados")
    print("=" * 60)
    print(f"  Modelo            : {modelo['name']}")
    print(f"  Tokens entrada    : {tokens_entrada}")
    print(f"  Coste entrada     : ${coste_entrada:.6f} USD")
    print(f"  Tokens salida máx : {max_tokens_salida}")
    print(f"  Coste salida máx  : ${coste_salida_max:.6f} USD  (si se usan todos los tokens)")
    print(f"  {'─' * 44}")
    print(f"  Coste máximo total: ${coste_total_max:.6f} USD")
    print("=" * 60)
    print("  El coste real de salida depende de la longitud de la respuesta.")

# ** Solicita al usuario que confirme la consulta o vuelva a ajustar la pregunta, el modelo o el límite de tokens antes de enviar la consulta al modelo. Devuelve la decisión del usuario.

def confirmar_o_volver() -> str:
    print("\n  ¿Qué quieres hacer?")
    print("  [1] Confirmar y enviar la consulta")
    print("  [2] Cambiar la pregunta")
    print("  [3] Cambiar el modelo")
    print("  [4] Cambiar el límite de tokens de salida")

    opciones = {"1": "confirmar", "2": "pregunta", "3": "modelo", "4": "tokens"}
    while True:
        opcion = input("\n  Opción [1-4]: ").strip()
        if opcion in opciones:
            return opciones[opcion]
        print("  Introduce 1, 2, 3 o 4.")

#Paso 5: Muestra los niveles de creatividad y devuelve la temperatura elegida.

def seleccionar_creatividad() -> float:
    print("\n" + "-" * 60)
    print("Nivel de creatividad:")
    print("-" * 60)

    for i, nivel in enumerate(CREATIVITY_LEVELS, start=1):
        print(f"  [{i}] {nivel['label']} — {nivel['description']}")

    print()
    while True:
        opcion = input(f"Selecciona un nivel [1-{len(CREATIVITY_LEVELS)}]: ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(CREATIVITY_LEVELS):
            nivel = CREATIVITY_LEVELS[int(opcion) - 1]
            print(f"Creatividad: {nivel['label']} (temperatura {nivel['temperature']})")
            return nivel["temperature"]
        print(f"Introduce un número entre 1 y {len(CREATIVITY_LEVELS)}.")

#Paso 6: Envía la consulta al modelo y devuelve el texto de la respuesta.

def llamar_modelo(
    client: Anthropic,
    pregunta: str,
    model_id: str,
    max_tokens: int,
    temperature: float,
) -> str:
    print("\n" + "=" * 60)
    print("Enviando consulta… Por favor, espera.")
    print("=" * 60)

    system_prompt = (f"Tienes un límite de {max_tokens} tokens para tu respuesta. Adapta la longitud y detalle de tu respuesta a la pregunta con ese límite. ")

    respuesta = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": pregunta}],
    )

    return respuesta.content[0].text.strip()


##########################################################################################################################################################################################################################################

def main():
    client = get_client()

    pregunta = obtener_pregunta()
    tokens_entrada = mostrar_tokens(client, pregunta)

    modelo = seleccionar_modelo(tokens_entrada)

    max_tokens = obtener_limite_tokens(modelo["max_output_tokens"])

    while True:
        mostrar_resumen_coste(modelo, tokens_entrada, max_tokens)
        decision = confirmar_o_volver()

        if decision == "confirmar":
            break
        elif decision == "pregunta":
            pregunta = obtener_pregunta()
            tokens_entrada = mostrar_tokens(client, pregunta)
            modelo = seleccionar_modelo(tokens_entrada)
            max_tokens = obtener_limite_tokens(modelo["max_output_tokens"])
        elif decision == "modelo":
            modelo = seleccionar_modelo(tokens_entrada)
            max_tokens = obtener_limite_tokens(modelo["max_output_tokens"])
        elif decision == "tokens":
            max_tokens = obtener_limite_tokens(modelo["max_output_tokens"])

    temperature = seleccionar_creatividad()

    try:
        respuesta = llamar_modelo(client, pregunta, modelo["id"], max_tokens, temperature)
    except AuthenticationError:
        print("\n[ERROR] API key inválida. Revisa tu ANTHROPIC_API_KEY.")
        sys.exit(1)
    except RateLimitError:
        print("\n[ERROR] Límite de peticiones alcanzado. Espera unos segundos.")
        sys.exit(1)
    except APIConnectionError:
        print("\n[ERROR] Sin conexión con la API. Comprueba tu red.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Respuesta del modelo:")
    print("=" * 60)
    print(respuesta)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()