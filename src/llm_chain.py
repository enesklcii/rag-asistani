from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableBranch
from src.config import GOOGLE_API_KEY

def format_docs(docs):
    """Bulunan doküman parçalarını tek bir metin bloğunda birleştirir."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain(vector_store):
    """Sohbet geçmişini anlayan (History-Aware) ve çoklu yedeklemeli RAG zinciri kurar."""
    
    primary_llm = ChatGoogleGenerativeAI(
        model="gemini-3.7-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )
    backup_1 = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )
    backup_2 = ChatGoogleGenerativeAI(
        model="gemma-4-31b-it",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )
    backup_3 = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )

    llm = primary_llm.with_fallbacks([backup_1, backup_2, backup_3])

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    contextualize_q_system_prompt = (
        "Sohbet geçmişini ve kullanıcının son sorusunu dikkate alarak, "
        "sohbet geçmişi olmadan da tek başına anlaşılabilecek net bir soru oluştur. "
        "Soruyu CEVAPLAMA; sadece gerekirse yeniden formüle et, gerekmiyorsa olduğu gibi döndür."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = RunnableBranch(
        (
            lambda x: len(x.get("chat_history", [])) > 0,
            contextualize_q_prompt | llm | StrOutputParser() | retriever,
        ),
        (lambda x: x["input"]) | retriever,
    )

    qa_system_prompt = (
        "Sen kurumsal bir doküman asistanısın. Görevin, kullanıcının sorularını "
        "SADECE aşağıda verilen bağlam (context) bilgilerini kullanarak yanıtlamaktır. "
        "Eğer sorunun cevabı verilen bağlamda yoksa, kesinlikle tahmin yürütme veya "
        "kendi genel bilgini kullanma; sadece 'Bu bilgi yüklenen dokümanlarda yer almıyor.' de. "
        "Cevaplarını net, maddeli, profesyonel ve Türkçe olarak ver.\n\n"
        "Bağlam:\n{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    rag_chain = RunnableParallel(
        {
            "context": history_aware_retriever,
            "input": lambda x: x["input"],
            "chat_history": lambda x: x.get("chat_history", []),
        }
    ).assign(answer=rag_chain_from_docs)

    return rag_chain
