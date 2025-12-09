import re
import os
import time

from PIL import Image
import pytesseract

class UdemyCertificateScraper:
    """
    Class to scrape text from images using OCR tessaract libary
    """
    def __init__(self, image_path: str) -> None:
        self.image_path = image_path
        self._parsed_text = None

    def parse_image_text(self, config = ('-l eng --oem 1 --psm 3')) -> str:
        with Image.open(self.image_path) as image:
            self._parsed_text = pytesseract.image_to_string(image, config=config)
        #print(self._parsed_text)
        return self._parsed_text

    def use_regex(self, regex: str) -> str:
        regex_object = re.compile(regex, re.DOTALL)
        match = regex_object.search(self._parsed_text)
        if match is not None:
          return match.group(0)
        return None

    def clean_text(self, text: str) -> str:

        if text is None or text == "" or text == " ":
          return None

        clean_text = text \
                .replace(".jpg", "") \
                .replace("COMPLETION", "") \
                .replace("udemy", "") \
                .replace("Instructors", "") \
                .replace("CERTIFICATE", "") \
                .replace("Number:", "") \
                .replace("Date", "") \
                .replace("Length", "") \
                .replace("total hours", "") \
                .replace("«", "") \
                .replace("\n", " ") \
                .replace(" " * 2, " ") \
                .replace(" " * 3, " ") \
                .replace(" " * 4, " ") \
                .replace(" " * 5, " ") \
                .strip()
        return clean_text

    def get_certificate_id(self) -> str:
        certificate_id = self.image_path.split("/")[-1]
        return self.clean_text(certificate_id)

    def get_owner(self) -> str:
        regex = r"Instructors(.*)Date"
        owner = self.use_regex(regex)
        owner = owner.split("\n")[-3]
        return self.clean_text(owner)

    def get_instructors(self) -> str:
        regex = r"Instructors(.*)Date"
        instructors = self.use_regex(regex)
        instructors = instructors.split("\n")[0]
        return self.clean_text(instructors)

    def get_reference_number(self) -> str:
        regex = r"Number:(.*)CERTIFICATE"
        reference_number = self.use_regex(regex)
        return self.clean_text(reference_number)

    def get_course_end(self) -> str:
        regex = r"Date(.*)Length"
        course_end = self.use_regex(regex)
        return self.clean_text(course_end)

    def get_course_length(self) -> str:
        regex = r"Length(.*)total hours"
        length = self.use_regex(regex)
        return self.clean_text(length)

    def get_title(self) -> str:
        regex = r"COMPLETION(.*)Instructors"
        course = self.use_regex(regex)
        if course is None:
            regex = r"udemy(.*)Instructors"
            course = self.use_regex(regex)
        return self.clean_text(course)

if __name__ == "__main__":

    path="/home/xl/projects/udemy_scraper/src/image_scraper/test/"
    files = os.listdir(path)
    images = [ path + file for file in files if file.endswith(".jpg") ]

    for image in images:

        certificate = UdemyCertificateScraper(image)
        certificate.parse_image_text()
        data = {
          "owner": certificate.get_owner(),
          "certificate_id": certificate.get_certificate_id(),
          "instructors": certificate.get_instructors(),
          "title": certificate.get_title(),
          "course_length": certificate.get_course_length(),
          "course_end": certificate.get_course_end(),
          "reference_number": certificate.get_reference_number(),
          "created": str( time.strftime("%Y-%m-%d") ),
        }
        print(data)