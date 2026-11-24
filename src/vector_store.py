import os
import gc
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import GOOGLE_API_KEY, CHROMA_DB_PATH

def get_embeddings():
    """Metinleri sayısal vektörlere çeviren Google Embedding modelini döndürür."""
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

def clear_vector_store():
    """Windows dosya kilidine takılmadan ChromaDB koleksiyonunu güvenli şekilde sıfırlar."""
    if os.path.exists(CHROMA_DB_PATH):
        try:
            embeddings = get_embeddings()
            db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
            db.delete_collection()
            del db
            gc.collect()
            return True
        except Exception as e:
            print(f"Koleksiyon temizleme uyarısı: {e}")
    return False

def create_vector_store(chunks):
    """Eski koleksiyonu temizler, yeni parçaları vektöre çevirip ChromaDB'ye kaydeder."""
    if not chunks:
        return None
        
    clear_vector_store()
    
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    return vector_store

def load_vector_store():
    """Daha önce oluşturulmuş ChromaDB veritabanını diskten yükler."""
    if not os.path.exists(CHROMA_DB_PATH):
        return None
        
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings
    )
