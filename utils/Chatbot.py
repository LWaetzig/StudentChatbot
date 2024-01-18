from langchain import HuggingFaceHub, LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class Chatbot:
    def __init__(self, **kgwars):
        self.llm = HuggingFaceHub(
            repo_id="tiiuae/falcon-7b-instruct", model_kwargs=kgwars
        )
        self.prompt = PromptTemplate(
            input_variables=["question", "context"],
            template="You are a professor teaching a class. A student asks you '{question}'. You respons based on your knowledge: '{context}'",
        )
        self.chain = LLMChain(prompt=self.prompt, llm=self.llm, verbose=True)

    def generate_answer(self, question: str, context: str) -> str:
        input = {"question": question, "context": context}
        answer = self.chain.run(input)
        return answer
