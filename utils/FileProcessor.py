import os
from io import BytesIO

import fitz
from PIL import Image
import logging as logger

logger.basicConfig(level=logger.INFO)


class FileProcessor:
    def __init__(self, pdf_file_path: os.path):
        logger.info("Initializing FileProcessor")
        # read in pdf document
        try:
            self.document = fitz.open(pdf_file_path)
            logger.info("PDF document loaded")
        except Exception as e:
            logger.error(f"Could not open PDF file: {e}")
        self.document_content = dict()

    @staticmethod
    def extract_text(
        page: fitz.fitz.Page, extract_text_from_image: bool = False
    ) -> str:
        """extract text from a pdf page
        Args:
            page (fitz.fitz.Page): page from pdf document
            extract_from_image (bool, optional): extract text from image using OCR (tesseract). Defaults to False.
        Returns:
            str: text from page
        """

        if extract_text_from_image:
            logger.info("Extracting text from image")
            pass

        else:
            logger.info("Extracting text from page")
            try:
                text = page.get_text()
                if text == "":
                    logger.info("No text found on page")
                    return ""
                else:
                    return text

            except Exception as e:
                print(e)
                return ""

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

    def process_pdf(self, **kwargs) -> dict:
        """wrapper function to handle processing of pdf document
        Args:
            **kwargs: extract_text_from_image, save_images, path
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
        path = "" if "path" not in kwargs else kwargs["path"]

        if self.document == None:
            raise ValueError("No PDF document loaded")

        logger.info("Extracting content from PDF")
        for i, page in enumerate(self.document):
            # get text and images from page
            text = self.extract_text(
                page, extract_text_from_image=extract_text_from_images
            )
            images = self.extract_images(
                document=self.document, page=page, save_images=save_images, path=path
            )
            self.document_content[i] = {"text": text, "images": images}

        return self.document_content
