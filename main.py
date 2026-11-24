import os
import shutil
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from src.loader import load_and_split_documents
from src.vector_store import create_vector_store, load_vector_store, clear_vector_store
from src.llm_chain import get_rag_chain
from src.config import DATA_PATH, CHROMA_DB_PATH

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="DocuMind AI | Enterprise RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Özel Modern CSS Tasarımı
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4F8BF9, #9B51E0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #8892B0;
        margin-bottom: 1.5rem;
    }
    .info-card {
        background-color: rgba(79, 139, 249, 0.08);
        border-left: 4px solid #4F8BF9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .quote-box {
        background-color: rgba(255, 255, 255, 0.04);
        border-left: 3px solid #9B51E0;
        padding: 0.6rem 0.9rem;
        border-radius: 0.3rem;
        font-size: 0.88rem;
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 3. Yan Menü (Sidebar) - Kontrol Paneli
with st.sidebar:
    st.markdown("## 🧠 DocuMind AI")
    st.caption("Kurumsal Bilgi & Doküman Asistanı v2.0")
    st.divider()

    existing_files = []
    if os.path.exists(DATA_PATH):
        existing_files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith((".pdf", ".docx", ".txt"))]
    
    db_active = os.path.exists(CHROMA_DB_PATH)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="📁 Doküman", value=f"{len(existing_files)} Adet")
    with col2:
        st.metric(label="⚡ Hafıza", value="Aktif" if db_active else "Boş")

    if existing_files:
        with st.expander("📂 Yüklü Dosyaları Gör", expanded=False):
            for f in existing_files:
                st.markdown(f"- `{f}`")

    st.divider()
    st.subheader("📤 Yeni Doküman Ekle")
    uploaded_files = st.file_uploader(
        "PDF, DOCX veya TXT sürükleyin", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        for file in uploaded_files:
            file_path = os.path.join(DATA_PATH, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.toast(f"{len(uploaded_files)} dosya kaydedildi!", icon="✅")

    if st.button("🔄 Veritabanını Güncelle", type="primary", use_container_width=True):
        with st.spinner("Dokümanlar parçalanıyor ve vektörleştiriliyor..."):
            chunks = load_and_split_documents()
            if chunks:
                create_vector_store(chunks)
                st.success("Bilgi bankası başarıyla güncellendi!")
                st.rerun()
            else:
                st.warning("İşlenecek dosya bulunamadı.")

    st.divider()
    st.subheader("⚙️ Yönetim & Araçlar")
    
    if "messages" in st.session_state and st.session_state.messages:
        chat_export = "\n\n".join(
            [f"{'KULLANICI' if m['role']=='user' else 'ASİSTAN'}: {m['content']}" for m in st.session_state.messages]
        )
        st.download_button(
            label="📥 Sohbeti Rapor Olarak İndir",
            data=chat_export,
            file_name=f"documind_rapor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚨 Bilgi Bankasını Sıfırla", use_container_width=True):
        clear_vector_store()
        if os.path.exists(DATA_PATH):
            shutil.rmtree(DATA_PATH)
            os.makedirs(DATA_PATH)
        st.session_state.messages = []
        st.toast("Tüm dokümanlar ve veritabanı sıfırlandı!", icon="🧹")
        st.rerun()

# 4. Ana Ekran Başlığı
st.markdown('<div class="main-title">🧠 DocuMind AI Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Canlı yanıt akışı, sohbet hafızası ve birebir paragraf kaynak doğrulaması ile kurumsal doküman asistanı.</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

selected_sample_prompt = None
if not st.session_state.messages:
    st.markdown("""
    <div class="info-card">
        <strong>👋 Hoş Geldiniz!</strong> Sol menüden dokümanlarınızı yükleyip veritabanını güncelledikten sonra soru sorabilir veya aşağıdaki hazır analiz istemlerinden birini başlatabilirsiniz.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 💡 Hızlı Analiz İstemleri")
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        if st.button("📌 Dokümanın ana konusunu özetle", use_container_width=True):
            selected_sample_prompt = "Yüklenen dokümanların ana konusunu maddeler halinde özetler misin?"
    with q_col2:
        if st.button("⚠️ Temel riskler ve nedenler nelerdir?", use_container_width=True):
            selected_sample_prompt = "Dokümanda bahsedilen temel riskler ve nedenleri nelerdir?"
    with q_col3:
        if st.button("🛡️ Alınması gereken tedbirler neler?", use_container_width=True):
            selected_sample_prompt = "Dokümana göre alınması gereken önlemler ve sorumluluklar nelerdir?"

# 5. Sohbet Geçmişini Ekrana Bas
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("🔍 Doğrulanmış Kaynaklar & Alıntılar"):
                for src in message["sources"]:
                    st.markdown(src["header"])
                    st.markdown(f'<div class="quote-box">"{src["snippet"]}"</div>', unsafe_allow_html=True)

# 6. Kullanıcı Girdisi ve Canlı Streaming Akışı
user_input = st.chat_input("Dokümanlarınız hakkında bir soru yazın...")
prompt = selected_sample_prompt if selected_sample_prompt else user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    vector_store = load_vector_store()
    
    with st.chat_message("assistant", avatar="🤖"):
        if vector_store is None:
            response_text = "⚠️ **Vektör veritabanı bulunamadı.** Lütfen sol menüden dosya yükleyip **'Veritabanını Güncelle'** butonuna tıklayın."
            st.warning(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": []})
        else:
            chat_history = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history.append(AIMessage(content=msg["content"]))

            rag_chain = get_rag_chain(vector_store)
            
            # Hem canlı metin akışını (stream) hem de kaynak dokümanları yakalayan jeneratör
            # Hem canlı metin akışını (stream) hem de kaynak dokümanları yakalayan jeneratör
            retrieved_docs = []
            def response_generator():
                for chunk in rag_chain.stream({"input": prompt, "chat_history": chat_history}):
                    if "context" in chunk:
                        retrieved_docs.extend(chunk["context"])
                    if "answer" in chunk:
                        yield chunk["answer"]

            # Canlı daktilo akışıyla cevabı yazdır
            full_answer = st.write_stream(response_generator())
            
            # Kaynakları ve birebir paragraf alıntılarını (snippet) hazırla
            sources = []
            seen_snippets = set()
            for doc in retrieved_docs:
                source_name = os.path.basename(doc.metadata.get("source", "Bilinmiyor"))
                snippet = doc.page_content.strip().replace("\n", " ")[:280] + "..."
                
                if snippet not in seen_snippets:
                    seen_snippets.add(snippet)
                    if "page" in doc.metadata:
                        page_num = doc.metadata["page"] + 1
                        header = f"📄 **{source_name}** — *Sayfa {page_num}*"
                    else:
                        header = f"📄 **{source_name}**"
                    sources.append({"header": header, "snippet": snippet})
            
            if sources:
                with st.expander("🔍 Doğrulanmış Kaynaklar & Alıntılar"):
                    for src in sources:
                        st.markdown(src["header"])
                        st.markdown(f'<div class="quote-box">"{src["snippet"]}"</div>', unsafe_allow_html=True)
                        
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_answer, 
                "sources": sources
            })
            if selected_sample_prompt:
                st.rerun()
