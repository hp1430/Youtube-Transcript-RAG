from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.configs.settings import get_settings
from app.repositories.vector_store_repository import VectorStoreRepository
from app.utils import get_logger

logger = get_logger(__name__)

RAG_PROMPT = """You are a helpful assistant. Answer the question based on the provided context.

If you cannot answer from the context, say "I don't have enough information to answer that question."
Do not make up information.

Context:
{context}

Question: {question}

Answer:"""


class RAGQueryService:
    def __init__(self, vector_store: VectorStoreRepository | None = None):
        settings = get_settings()
        self.vector_store = vector_store or VectorStoreRepository()
        self.retriever = self.vector_store.get_retriever()
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )

        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

        self.chain = (
            {
                "context": self.retriever,
                "question": RunnablePassthrough()
            }
        ) | prompt | self.llm | StrOutputParser()

    def _format_source(self, docs: list[Document]) -> list[dict]:
        sources = []

        for doc in docs:
            content = doc.page_content
            if len(content) > 500:
                content = content[:500] + "..."
            sources.append({
                "content": content,
                "metadata": doc.metadata
            })

        return sources

    async def aquery(self, question: str) -> dict:
        answer = await self.chain.ainvoke(question)
        return {
            "answer": answer
        }

    async def aquery_with_source(self, question: str) -> dict:
        answer = await self.chain.ainvoke(question)
        source = await self.retriever.ainvoke(question)
        return {
            "answer": answer,
            "source": self._format_source(source)
        }

    def stream(self, question: str):
        yield from self.chain.stream(question)