from typing import List

from langchain.schema import BaseRetriever, Document


class ElasticRetriever(BaseRetriever):
    async def aget_relevant_documents(self, query: str) -> List[Document]:

        pass

    def get_relevant_documents(self, query: str) -> List[Document]:
        #因为继承了langchain的父类，所以灵活的部分只能在es里面操作了

        pass