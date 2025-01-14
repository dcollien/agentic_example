import os
import string

from nltk import word_tokenize
from nltk.corpus import stopwords

from rank_bm25 import BM25Okapi

FILENAME = "alice_in_wonderland.txt"
START = "*** START OF THE PROJECT GUTENBERG EBOOK ALICE'S ADVENTURES IN WONDERLAND ***"
END = "*** END OF THE PROJECT GUTENBERG EBOOK ALICE'S ADVENTURES IN WONDERLAND ***"
START_CHAPTERS = "CHAPTER I."
MIN_PARAGRAPH_LENGTH = 180
DIALOGUE_MARKERS = ["“", "”", '"']
PARAGRAPH_SEPARATOR = "\n\n"


def digest_book():
    path = os.path.join(os.path.dirname(__file__), FILENAME)

    with open(path) as f:
        book = f.read()

    # remove Project Gutenberg header and footer
    start = book.find(START)
    end = book.find(END)

    book = book[start + len(START) : end].strip()

    preface_and_toc, chapters_text = book.split(START_CHAPTERS, 1)

    # split the book into chapters, preserving the chapter titles
    chapters = [
        (START_CHAPTERS + chapter).strip()
        for chapter in chapters_text.split(START_CHAPTERS)
    ]

    # split each chapter into paragraphs
    all_paragraphs = [chapter.split(PARAGRAPH_SEPARATOR) for chapter in chapters]

    processed_chapters = []

    # recombine short paragraphs into longer ones
    for chapter in all_paragraphs:
        processed_chapter = []
        current_paragraph = ""
        for paragraph in chapter:
            # if the paragraph is too short or starts with a dialogue marker, add it to the previous paragraph
            if (
                len(paragraph) < MIN_PARAGRAPH_LENGTH
                or paragraph[0] in DIALOGUE_MARKERS
            ):
                current_paragraph += PARAGRAPH_SEPARATOR + paragraph
            else:
                if current_paragraph:
                    processed_chapter.append(current_paragraph)
                current_paragraph = paragraph
        processed_chapter.append(current_paragraph)
        processed_chapters.append(processed_chapter)

    corpus = [paragraph for chapter in processed_chapters for paragraph in chapter]

    # chapter mapping, each index of the corpus corresponds to a chapter
    corpus_mapping = [
        (chapter_index, paragraph_index)
        for chapter_index, chapter in enumerate(processed_chapters)
        for paragraph_index, _paragraph in enumerate(chapter)
    ]

    tokenized_corpus = [tokenize(doc) for doc in corpus]

    bm25 = BM25Okapi(tokenized_corpus)

    return bm25, processed_chapters, corpus_mapping


def tokenize(text):
    stop = set(stopwords.words("english") + list(string.punctuation))
    return [token for token in word_tokenize(text.lower()) if token not in stop]


def search(bm25, query, n=5, min_score=0.75):
    tokenized_query = tokenize(query)
    doc_scores = bm25.get_scores(tokenized_query)
    top_n_indices = sorted(
        range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True
    )[:n]

    return [
        (i, doc_scores[i]) for i in top_n_indices if doc_scores[i] > min_score
    ]  # filter out low scoring results
