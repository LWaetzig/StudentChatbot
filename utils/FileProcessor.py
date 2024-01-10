import logging as logger
import math
import os
import sqlite3

import fitz
import matplotlib.pyplot as plt
import numpy as np
from langdetect import detect
from rake_nltk import Rake
from scipy.signal import argrelextrema
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger.basicConfig(level=logger.INFO)
# TODO: add logging to file
# TODO: check for syntax and formatting
# TODO: add comments


class FileProcessor:
    def __init__(self, pdf_file_path: os.path):
        logger.info("Initializing FileProcessor")
        # read in pdf document
        try:
            self.document = fitz.open(pdf_file_path)
            logger.info("PDF document loaded")
        except Exception as e:
            logger.error(f"Could not open PDF file: {e}")
        self.document_content = {"text": str(), "images": dict()}

    @staticmethod
    def extract_text(
        document: fitz.fitz.Document, extract_text_from_image: bool = False
    ) -> str:
        """extract text from a pdf page
        Args:
            page (fitz.fitz.Page): page from pdf document
            extract_from_image (bool, optional): extract text from image using OCR (not possible yet). Defaults to False.
        Returns:
            str: text from page
        """

        if extract_text_from_image:
            logger.info("Extracting text from image")
            pass

        else:
            logger.info("Extracting text from pages")
            text = str()
            for page in document:
                try:
                    text += page.get_text() + " "
                except Exception as e:
                    print(f"Error processing file on page {page.number}: {e}")
                    continue
            return text

    @staticmethod
    def extract_images(
        document: fitz.fitz.Document, page: fitz.fitz.Page, save_images=False, **kwargs
    ) -> list:
        """extract images from a pdf page
        Args:
            document (fitz.fitz.Document): pdf document read in using pymupdf (fitz)
            page (fitz.fitz.Page): page from pdf document
            save_images (bool, optional): decide whether to save images. Defaults to False.
            **kwargs: add "path" to kwargs if save_images=True
        Returns:
            list: list of extracted images as dictionary with image (binary) and extension
        """
        extracted_images = list()
        image_list = page.get_images()

        if len(image_list) == 0:
            logger.info("No images found on page")
            return []
        else:
            logger.info(f"Found {len(image_list)} images on page")
            for i, image in enumerate(image_list):
                xref = image[0]
                base_image = document.extract_image(xref)
                image_ext = base_image["ext"]
                extracted_images.append({"image_xreference": xref, "ext": image_ext})
                if save_images:
                    if os.path.exists(kwargs["path"]):
                        image.save(
                            open(kwargs["path"] + f"image_{i}.{image_ext}", "wb")
                        )
                    else:
                        logger.error("Path does not exist")

            return extracted_images

    @staticmethod
    def calc_rev_sigmoid(x: float) -> float:
        """calculate reverse sigmoid function

        Args:
            x (float): input value

        Returns:
            float: output value
        """
        return 1 / (1 + math.exp(0.5 * x))

    @staticmethod
    def activate_similarities(similarities: np.array, p_size=10) -> np.array:
        """calculate activated similarities using reverse sigmoid function

        Args:
            similarities (np.array): similarities between sentences
            p_size (int, optional): size of sigmoid function. Defaults to 10.

        Returns:
            np.array: activated similarities
        """
        x = np.linspace(-10, 10, p_size)
        y = np.vectorize(FileProcessor.calc_rev_sigmoid)
        activation_weights = np.pad(y(x), (0, similarities.shape[0] - p_size))
        diagonals = [
            similarities.diagonal(each) for each in range(0, similarities.shape[0])
        ]
        diagonals = [
            np.pad(each, (0, similarities.shape[0] - len(each))) for each in diagonals
        ]
        diagonals = np.stack(diagonals)
        diagonals = diagonals * activation_weights.reshape(-1, 1)
        activated_similarities = np.sum(diagonals, axis=0)
        return activated_similarities

    @staticmethod
    def plot_chunk_points(activated_similarities: np.array, split_points: list) -> None:
        """Plot chunk points in document using activted similarities

        Args:
            activated_similarities (np.array): activated similarities
            split_points (list): split points in document to create chunks
        """
        fig, axes = plt.subplots(figsize=(12, 6))
        axes.plot(activated_similarities, label="Activated Similarities")
        axes.scatter(
            split_points,
            [activated_similarities[i] for i in split_points],
            color="red",
            label="Split points",
        )
        axes.set_xlabel("Sentence Index")
        axes.set_ylabel("Activated Similarity Value")
        axes.set_title("Change Points in Document based on activated similarities")
        axes.legend()
        fig.tight_layout()

    def split_text_into_chunks(
        self,
        text: str,
        filename: str,
        visualize_splitting: bool = False,
        db_path: str = "chunks.db",
    ) -> None:
        doc_lang = detect(text)
        rake = Rake(language="german" if doc_lang == "de" else "en")

        logger.info("Loading model")
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        sentences = text.split(". ")

        logger.info("Encoding sentences")
        embeddings = model.encode(sentences)
        similarities = cosine_similarity(embeddings, embeddings)
        logger.info("Calculating activated similarities")
        activated_similarities = self.activate_similarities(similarities, p_size=5)
        minima = argrelextrema(activated_similarities, np.less, order=2)
        split_points = [each for each in minima[0]]

        if visualize_splitting:
            self.plot_chunk_points(activated_similarities, split_points)

        logger.info("Storing chunks in database")
        db_connect = sqlite3.connect(db_path)
        db_cursor = db_connect.cursor()
        db_cursor.execute(
            """CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                chunk_text TEXT UNIQUE,
                keywords TEXT)"""
        )
        text_chunk = str()
        for split_point, sentence in enumerate(sentences):
            text_chunk += sentence + ". "
            if split_point in split_points:
                rake.extract_keywords_from_text(text_chunk)
                extracted_keywords = rake.get_ranked_phrases()[:5]
                keywords = ", ".join(extracted_keywords)
                db_cursor.execute(
                    """INSERT OR IGNORE INTO chunks (file_name, chunk_text, keywords) 
                        VALUES (?, ?, ?)""",
                    (filename, text_chunk, keywords),
                )
                db_connect.commit()
                text_chunk = str()
        if text_chunk != str():
            rake.extract_keywords_from_text(text_chunk)
            extracted_keywords = rake.get_ranked_phrases()[:5]
            keywords = ", ".join(extracted_keywords)
            db_cursor.execute(
                """INSERT OR IGNORE INTO chunks (file_name, chunk_text, keywords) 
                        VALUES (?, ?, ?)""",
                (filename, text_chunk, keywords),
            )
            db_connect.commit()
        db_connect.close()
        logger.info("Chunks stored in database")

    def process_pdf(self, **kwargs) -> dict:
        """wrapper function to handle processing of pdf document
        Args:
            **kwargs: extract_text_from_image (bool), save_images (bool), image_save_path (str), visualize_splitting (bool), db_path (str)
        Returns:
            dict: extracted content from document page by page
        """
        logger.info("Processing PDF")

        extract_text_from_images = (
            False
            if "extract_text_from_image" not in kwargs
            else kwargs["extract_text_from_image"]
        )
        save_images = False if "save_images" not in kwargs else kwargs["save_images"]
        image_save_path = (
            "" if "image_save_path" not in kwargs else kwargs["image_save_path"]
        )
        visualize_splitting = (
            False
            if "visualize_splitting" not in kwargs
            else kwargs["visualize_splitting"]
        )
        db_path = "chunks.db" if "db_path" not in kwargs else kwargs["db_path"]

        if self.document == None:
            raise ValueError("No PDF document loaded")

        logger.info("Extracting content from PDF")
        self.document_content["text"] = self.extract_text(
            self.document, extract_text_from_image=extract_text_from_images
        )
        for i, page in enumerate(self.document):
            # get images from pages
            images = self.extract_images(
                document=self.document,
                page=page,
                save_images=save_images,
                path=image_save_path,
            )
            self.document_content["images"][i] = images

        logger.info("Splitting text into chunks")
        try:
            self.split_text_into_chunks(
                text=self.document_content["text"],
                filename=os.path.basename(self.document.name),
                visualize_splitting=visualize_splitting,
                db_path=db_path,
            )

        except Exception as e:
            logger.error(f"Error splittin text into chunks: {e}")
