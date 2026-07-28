from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
import os
from dotenv import load_dotenv
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from apps.prompt import get_prompt
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

embedding_model = MistralAIEmbeddings()
llm_model = ChatMistralAI(model_name="mistral-small-latest")
PERSIST_DIR = "ai-db"
parser = StrOutputParser()

def rag_split_embedding_vector_store(ext, file_path):

    try:

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported extension: {ext}")

        docs = loader.load()
 
        #text to split
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

         #chunks
        chunks = splitter.split_documents(docs)
    
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            # store already exists: add this file's chunks to it
            vectorstore = Chroma(
                persist_directory = PERSIST_DIR,
                embedding_function= embedding_model
            )
            vectorstore.add_documents(chunks)
        else:
            # first upload ever: create the store from these chunks
            vectorstore = Chroma.from_documents(
                documents = chunks,
                embedding = embedding_model,
                persist_directory = PERSIST_DIR
            )
    
        return {
            "chunks": len(chunks),
            "collection_count": vectorstore._collection.count()
        }

    except Exception as e:
            return e

def get_answer_from_llm_vectorstore(query, feature):

    try:
        vectorstore = Chroma(
            persist_directory = PERSIST_DIR,
            embedding_function = embedding_model
        )

        vector_retriever = vectorstore.as_retriever(
            search_type = "mmr",
            seach_kwargs = {
                "k":5,
                "fetch_k": 20,
                "lambds_mult":0.5
            }
        )

        multi_query = MultiQueryRetriever.from_llm(
            retriever = vector_retriever,
            llm = llm_model
        )

        docs = multi_query.invoke(query)

        context = "\n\n" . join([doc.page_content for doc in docs])

        prompt = get_prompt(feature)

        rag_prompt = prompt | llm_model | parser               # this chain    ------> runnable

        final_prompt =  rag_prompt.invoke({
            "resume_text": context,
            "job_description": query,
            "target_role":""
        })

        respoonse = llm_model.invoke(final_prompt)

        return respoonse.content

    except Exception as e:
                return e
     
