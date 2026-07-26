from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class RAGChain:
    def __init__(self, config, retriever):
        self.config = config
        self.retriever = retriever
        self.llm = self._create_llm()
        self.conv_context_function = None
    
    def _create_llm(self):
        return ChatGroq(
            model=self.config.LLM_MODEL,
            temperature=self.config.LLM_TEMPERATURE,
            streaming=False
        )
    
    def set_conversation_context(self, context_func):
        """Set function to get conversation context"""
        self.conv_context_function = context_func
    
    def create_chain(self):
        prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer using ONLY the provided context.
Use conversation history to understand references.

{conv_context}

Question: {query}
Context: {context}
""")
        
        return (
            {
                "context": self.retriever,
                "query": RunnablePassthrough(),
                "conv_context": lambda _: (
                    self.conv_context_function() if self.conv_context_function else ""
                )
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )