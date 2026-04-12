## CASO PRÁCTICO TEMA 4

Script de consola en Python que permite lanzar una pregunta a un modelo de Claude, con control del tipo de modelo, el número
de tokens, el coste, el nivel de creatividad...
Se muestra una información de costes antes de enviar la consulta para que la información sea usable y no se quede en una mera información

## FLUJO DEL CÓDIGO

    A([Inicio]) --> B[Introducir pregunta]
    B --> C[Contar tokens de entrada]
    C --> D[Seleccionar modelo. Muestra coste de entrada por modelo]
    D --> E[Definir límite de tokens de salida]
    E --> F[Mostrar resumen de costes]
    F --> G{¿Confirmar?}
    G -->|Confirmar| H[Seleccionar nivel de creatividad]
    G -->|Cambiar pregunta| B
    G -->|Cambiar modelo| D
    G -->|Cambiar tokens de salida| E
    H --> I[Llamar al modelo]
    I --> J[Mostrar respuesta]
    J --> K([Fin])

## ARQUITECTURA
main()
 get_client()                  inicializa el cliente Anthropic
 obtener_pregunta()            paso 1: entrada de texto
 mostrar_tokens()              paso 2: conteo con count_tokens API
 seleccionar_modelo()          paso 3: selector con coste de entrada
 obtener_limite_tokens()       paso 4: límite de tokens de salida
 mostrar_resumen_coste()       desglose: entrada + salida máx + total
 confirmar_o_volver()          el usuario confirma o ajusta parámetros
 seleccionar_creatividad()     paso 5: selector de temperatura
 llamar_modelo()               paso 6: llamada a la API

## DECISIONES

**Tokenización con count_tokens**
Se usa client.messages.count_tokens() de Anthropic, que devuelve el conteo exacto del tokenizador real del modelo.

**Coste de entrada y salida antes de confirmar**
Cada modelo tiene precio de entrada y de salida por millón de tokens. El coste de salida se calcula sobre el límite máximo definido por el usuario, lo que representa el peor caso posible. El coste real será igual o menor, dependiendo de cuántos tokens genere el modelo.

**max_tokens obligatorio en Anthropic**
La API de Anthropic requiere siempre `max_tokens`. Si el usuario elige sin límite, se pasa el máximo que admite el modelo.

**Bucle de confirmación**
Tras mostrar el resumen de costes, el usuario puede confirmar o volver a cualquiera de los pasos previos. Cambiar la pregunta reinicia desde el paso 1; cambiar el modelo mantiene el texto pero permite re-elegir desde el paso 3; cambiar los tokens vuelve solo al paso 4.

**Creatividad mediante temperatura**
Cinco niveles con nombres comprensibles, mapeados a valores entre 0.0 y 1.0 (rango oficial de Anthropic).

## INSTALACIÓN

python -m venv venv
venv\Scripts\activate  
pip install -r requirements.txt

## API KEY
La API Key de Anthropic es proporcionada por el máster en el Tema 4. Una vez obtenida, copiar en el archivo .env:

copy .env.example .env

y sustituye el valor:

ANTHROPIC_API_KEY=sk-ant-tu-clave-aquí

Si no existe el `.env`, el script pide la clave de forma segura al arrancar.

## EJECUCIÓN

python use_case_1.py