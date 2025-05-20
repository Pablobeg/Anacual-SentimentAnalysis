import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,wordpunct_tokenize,sent_tokenize
from nltk import SnowballStemmer

palabras_vacias=set(stopwords.words("spanish"))


#Arreglo de caracteres
caracteresP = ['\(','\)','¿','\?','/',',','"','"','\$','¡','!','\.','\–','_','#',':','-','\...','\--',';']
adicionales=["ser","estar","tener","haber","él"]


def limpieza(linea):
    # for para recorrer lista de caracteres especiales
    for expresion in caracteresP:
    # quitando caracteres especiales
        linea = re.sub(expresion, "", linea)
    # pasando texto a minusculas
    linea = linea.lower()
    # quitando palabras vacias
    linea = " ".join([palabra for palabra in linea.split(' ') if palabra not in palabras_vacias])
    # lista de palabras vacias adicionales
    linea = " ".join([palabra for palabra in linea.split(' ') if palabra not in adicionales])
    # quitando expresion regular de risa
    linea = re.sub(r'(\b(j+a+)+j*|\b(a+j+)+a*)', 'jaja', linea)
    # quitando arroba

    linea = re.sub(r'@[a-zA-Z]\w*', ' ', linea)
    
    # escribiendo de nuevo en el archivo el texto limpio
    return linea

