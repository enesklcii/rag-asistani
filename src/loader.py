import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP

def load_and_split_documents():
    """data/ klasöründeki tüm PDF, DOCX ve TXT dosyalarını okur ve parçalara böler."""
    documents = []
    
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        return []

    supported_extensions = (".pdf", ".docx", ".txt")
    files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith(supported_extensions)]
    
    if not files:
        print(f"UYARI: '{DATA_PATH}' klasöründe desteklenen dosya bulunamadı!")
        return []

    for file in files:
        file_path = os.path.join(DATA_PATH, file)
        ext = os.path.splitext(file)[1].lower()
        print(f"Okunuyor: {file}...")
        
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
            
        documents.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Toplam {len(files)} dosya, {len(chunks)} parçaya bölündü.")
    return chunks
