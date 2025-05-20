import threading
from transformers import pipeline
import nltk
from concurrent.futures import ThreadPoolExecutor

# Clasificador de sentimientos
clasificador_sentimientos = None
executor = ThreadPoolExecutor(max_workers=4)  # Usar un thread pool para análisis paralelos


# Función para cargar el clasificador de sentimientos en un hilo separado
def cargar_clasificador():
    global clasificador_sentimientos
    clasificador_sentimientos = pipeline("sentiment-analysis", "pysentimiento/robertuito-sentiment-analysis")


# Cargar el clasificador al iniciar
if clasificador_sentimientos is None:
    cargar_clasificador()


# Función para analizar el sentimiento de un texto
def analizar_sentimiento(texto):
    global clasificador_sentimientos
    # Realizar el análisis de sentimiento si el clasificador está disponible
    if clasificador_sentimientos:
        resultado_sentimiento = clasificador_sentimientos(texto)
        clasificacion = resultado_sentimiento[0]['label']
        if clasificacion == 'POS':
            return "Positivo"
        elif clasificacion == 'NEG':
            return "Negativo"
        else:
            return "Neutro"
    else:
        return "No se pudo cargar el clasificador de sentimientos"


# Función para contar los tokens de un texto
def contar_tokens(texto):
    tokens = nltk.word_tokenize(texto)
    return len(tokens)


# Función para dividir un texto en segmentos de máximo 128 caracteres
def dividir_en_segmentos(texto, max_caracteres=128):
    tokens = nltk.word_tokenize(texto)
    segmentos = []
    segmento_actual = []

    for token in tokens:
        if len(' '.join(segmento_actual + [token])) <= max_caracteres:
            segmento_actual.append(token)
        else:
            segmentos.append(' '.join(segmento_actual))
            segmento_actual = [token]

    if segmento_actual:
        segmentos.append(' '.join(segmento_actual))

    return segmentos


# Función para contar los positivos y negativos en una lista de tokens
def contadorVarios(listadetokens):
    positivo = 0
    negativo = 0
    neutro = 0
    for lista in listadetokens:
        if lista == 'Positivo':
            positivo += 1
        elif lista == 'Negativo':
            negativo += 1
        elif lista == 'Neutro':
            neutro += 1

    recuentos = {
        'Positivo': positivo,
        'Negativo': negativo,
        'Neutro': neutro
    }
    categoria_maxima = max(recuentos, key=recuentos.get)
    return categoria_maxima


# Función principal que realiza el análisis de sentimiento completo
def completa(entrada):
    cantidad_tokens = contar_tokens(entrada)
    resultados_analisis = []

    # Si el texto tiene menos de 128 tokens, lo analiza de una vez
    if cantidad_tokens < 128:
        textolimpio = entrada
        return analizar_sentimiento(textolimpio)
    else:
        lista_seg = dividir_en_segmentos(entrada)

        # Realizar el análisis de sentimiento en paralelo
        future_results = [executor.submit(analizar_sentimiento, seg) for seg in lista_seg]

        for future in future_results:
            resultados_analisis.append(future.result())

        resultadova = contadorVarios(resultados_analisis)
        return resultadova


# Función principal para probar el análisis de sentimiento
def main():
    texto = 'estoy muy feliz ahora'
    resultado = completa(texto)
    print(resultado)


if __name__ == "__main__":
    main()
