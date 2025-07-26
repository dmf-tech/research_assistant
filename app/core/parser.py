from bs4 import BeautifulSoup
import PyPDF2
from pdfminer.high_level import extract_text
import dateparser
from pyexcel import get_sheet
import json
import jsonlines

class ResearchParser:
    def parse_html(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')
        return {
            'title': soup.title.string if soup.title else None,
            'text': soup.get_text(separator=' ', strip=True),
            'links': [a.get('href') for a in soup.find_all('a', href=True)],
            'metadata': {
                'description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None,
                'keywords': soup.find('meta', {'name': 'keywords'})['content'] if soup.find('meta', {'name': 'keywords'}) else None
            }
        }

    def parse_pdf(self, pdf_path, use_pdfminer=False):
        if use_pdfminer:
            return extract_text(pdf_path)
        else:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text

    def parse_excel(self, file_path):
        sheet = get_sheet(file_name=file_path)
        return sheet.array

    def parse_json(self, file_path, is_jsonl=False):
        if is_jsonl:
            data = []
            with jsonlines.open(file_path) as reader:
                for obj in reader:
                    data.append(obj)
            return data
        else:
            with open(file_path, 'r') as f:
                return json.load(f)

    def parse_date(self, date_string):
        return dateparser.parse(date_string) 