# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Recursively extracts the text from a Google Doc.
"""
from __future__ import print_function

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import re

SCOPES = 'https://www.googleapis.com/auth/documents.readonly'
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'
DOCUMENT_ID = 'Your Document ID'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage('token.json')

    try:
        credentials = store.get()
    except:
        credentials = False

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    
    return credentials

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    
    return text_run.get('content')


def read_strucutural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:print(chapter_text)
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_strucutural_elements(cell.get('content'))
        
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_strucutural_elements(toc.get('content'))
    
    return text

def count_words_from_book(book_title):
    chapters = {}

    with open(book_title, 'r') as text:
        # count lines of book
        chapter_text = ''
        chapter_number = None
        for line in text:
            line = line.rstrip()
            
            # sees if a start of new chapter and defines new chapter_number
            pattern = re.compile('Prólogo|Capítulo \w+')
            match = pattern.match(line)

            if match:
                # check how many words per chapter
                if chapter_number is not None:
                    chapter_text_list = chapter_text.split()
                    chapters[chapter_number] = len(chapter_text_list)

                    chapter_text = ""

                # define new chapter_number
                verify_if_chapter_exists = chapters.get(line, 0)
                chapter_number = line

                if not verify_if_chapter_exists:
                    chapters[line] = 0

            else:
                for letters in line:
                    chapter_text += letters
        
        chapter_text_list = chapter_text.split()
        chapters[chapter_number] = len(chapter_text_list)
    
    return chapters


def average_words_per_chapter(chapters: dict):
    how_many_chapters = 0
    words_in_book = 0

    for chapter, words in chapters.items():
        if chapter == "Prólogo":
            pass
        else:
            how_many_chapters += 1
            words_in_book += words
    
    average = words_in_book / how_many_chapters
    return average
    

def print_word_counter(chapters: dict):
    average_words = average_words_per_chapter(chapters)

    for chapter, words in chapters.items():
        print(f'{chapter:<15}: {words:>2} palavras')
    
    print(f"MÉDIA DE PALAVRAS POR CAPÍTULO: {average_words:.2f}")


def main():
    """Uses the Docs API to print out the text of a document."""
    credentials = get_credentials()
    http = credentials.authorize(Http())

    docs_service = build('docs', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)
    doc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
    
    doc_title = doc.get('title')
    doc_content = doc.get('body').get('content')
    
    with open(doc_title, 'w') as book:
        book.write(read_strucutural_elements(doc_content))
        
    
    chapter_dict = count_words_from_book(doc_title)
    print_word_counter(chapter_dict)

if __name__ == '__main__':
    main()