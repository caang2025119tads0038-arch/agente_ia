import pandas as pd
import os

def recomendar_por_ml(busca_usuario):
    # Procura o arquivo na raiz do projeto
    caminho_csv = 'livros.csv'
    if not os.path.exists(caminho_csv):
        return None
        
    # 1. Carrega a base de livros
    df = pd.read_csv(caminho_csv)
    
    # 2. Imports locais para o servidor não travar ao ligar
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # 3. Transforma o texto em vetores numéricos (Machine Learning)
    vectorizer = TfidfVectorizer()
    matriz_sinopses = vectorizer.fit_transform(df['sinopse'] + " " + df['genero'])
    vetor_busca = vectorizer.transform([busca_usuario])
    
    # 4. Calcula a similaridade matemática entre a busca e os livros
    similaridade = cosine_similarity(vetor_busca, matriz_sinopses).flatten()
    
    # 5. Pega o livro com maior score matemático
    indice_melhor_livro = similaridade.argmax()
    
    if list(similaridade)[indice_melhor_livro] > 0:
        return df.iloc[indice_melhor_livro].to_dict()
    return None