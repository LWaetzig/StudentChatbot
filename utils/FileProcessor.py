import logging as logger
import math

import fitz
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from scipy.signal import argrelextrema
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger.basicConfig(level=logger.DEBUG)
# TODO: format document, add docstrings, add comments


class FileProcessor:
    def __init__(self) -> None:
        logger.info("Initializing FileProcessor")
        self.document_name = None
        self.vectordb = None

    @staticmethod
    def calc_rev_sigmoid(x: float) -> float:
        """calculate reverse sigmoid function

        Args:
            x (float): input value

        Returns:
            float: output value based on reverse sigmoid function
        """
        return 1 / (1 + math.exp(-x))

    @staticmethod
    def calc_active_similarities(similarities: np.array, p_size=5) -> np.array:
        """calculate "activated" similarities using reverse sigmoid function

        Args:
            similarities (np.array): similarities between chunks
            p_size (int, optional): range of sigmoid function . Defaults to 5.

        Returns:
            np.array: activated similarities
        """
        x = np.linspace(-10, 10, p_size)
        y = np.vectorize(FileProcessor.calc_rev_sigmoid)
        activation_weights = np.pad(y(x), (0, similarities.shape[0] - p_size))
        diagonals = [
            similarities.diagonal(each) for each in range(0, similarities.shape[0])
        ]
        padded_diagonals = [
            np.pad(each, (0, similarities.shape[0] - len(each))) for each in diagonals
        ]
        padded_diagonals = np.stack(padded_diagonals)
        weighted_diagonals = padded_diagonals * activation_weights.reshape(-1, 1)
        activated_similarities = np.sum(weighted_diagonals, axis=0)
        return activated_similarities

    def extract_text(self, document: fitz.fitz.Document) -> str:
        logger.info("Extracting text from document")
        text = str()
        for page in document:
            try:
                text += page.get_text() + " "
            except Exception as e:
                logger.error(f"Could not extract text from page {page.number}: {e}")
                continue
        return text

    def extract_images(self):
        pass

    @staticmethod
    def split_text(text: str, max_chunk_length: int = 512) -> list:
        """Split text into small chunks based on

        Args:
            text (str): text to split
            max_chunk_length (int, optional): maximum length of a single chunk. Defaults to 512.

        Returns:
            list: text splitted into chunks
        """
        logger.info("Splitting text into chunks")
        # load sentence transformer for embeddings
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        # pre split text into 100 character chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=100, chunk_overlap=20, length_function=len
        )
        pre_chunks = splitter.split_text(text)
        embeddings = model.encode(pre_chunks)
        similarities = cosine_similarity(embeddings, embeddings)
        # calculate activated similarities
        activated_similarities = FileProcessor.calc_active_similarities(
            similarities=similarities, p_size=5
        )
        # get split points
        minima = argrelextrema(activated_similarities, np.less, order=2)
        split_points = [each for each in minima[0]]

        # split text into chunks based on split points and max_chunk_length
        chunks = list()
        chunk_text = str()

        for split_point, chunk in enumerate(pre_chunks):
            if len(chunk_text) + len(chunk) <= max_chunk_length:
                chunk_text += chunk + " "
            else:
                chunks.append(chunk_text)
                chunk_text = chunk + " "

            if split_point in split_points:
                chunks.append(chunk_text)
                chunk_text = str()

        return chunks

    @staticmethod
    def init_vector_db(
        chunks: list,
    ):
        """Create vectorstore from chunks and embeddings

        Args:
            chunks (list): chunks from text

        Returns:
            vectorstore: vectorstore from faiss containing chunks
        """
        embeddings = HuggingFaceEmbeddings()
        vectorstore = FAISS.from_texts(chunks, embeddings)
        return vectorstore

    def process_pdf(self, file):
        """Wrapper function to handle processing of pdf document"""
        logger.info("Processing pdf file")
        logger.info("Extracting text from document")
        try:
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                self.document_name = file.name
                text = self.extract_text(doc)
        except Exception as e:
            logger.error(f"Cloud not open pdf file: {e}")
            return "Error reading pdf file"

        chunks = self.split_text(text)
        if chunks:
            logger.info("Successfully splitted text into chunks")
            logger.info("Initialize vector database")
            self.vectordb = FileProcessor.init_vector_db(chunks=chunks)
            print(type(self.vectordb))

        else:
            logger.error("Could not split text into chunks")

    def get_matched_documents(self, prompt: str, n_results: int = 3) -> list:
        """Get matched documents based on prompt using similarity search

        Args:
            prompt (str): prompt to search for similar documents
            n_results (int, optional): number of matched documents to return. Defaults to 3.

        Returns:
            list: matched documents
        """
        vector_store = self.vectordb

        embeddings = HuggingFaceEmbeddings()
        embedded_query = embeddings.embed_query(prompt)

        matched_documents = vector_store.similarity_search_by_vector(
            embedded_query, n_results=n_results
        )
        return matched_documents
