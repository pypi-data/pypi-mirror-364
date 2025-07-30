import pytest
import os
from pprint import pprint
from rara_tools.core_formatters.core_formatter import format_keywords, format_meta
from tests.test_utils import read_json_file

ROOT_DIR = os.path.join("tests", "test_data", "formatter")
INPUT_KEYWORDS_FILE_PATHS = [
    os.path.join(ROOT_DIR, "keywords_1.json"),
    os.path.join(ROOT_DIR, "keywords_2.json")
]
INPUT_META_FILE_PATHS = [
    os.path.join(ROOT_DIR, "epub_meta.json"),
    os.path.join(ROOT_DIR, "mets_alto_meta.json"),
    os.path.join(ROOT_DIR, "pdf_meta.json")
]

INPUT_KEYWORDS = [
    read_json_file(keyword_file_path)
    for keyword_file_path in INPUT_KEYWORDS_FILE_PATHS
]

INPUT_META_DICTS = [
    read_json_file(meta_file_path)
    for meta_file_path in INPUT_META_FILE_PATHS
]

def test_formatting_keywords_for_core():
    for keyword_dict in INPUT_KEYWORDS:
        formatted_keywords = format_keywords(keyword_dict)
        #pprint(formatted_keywords)
        assert formatted_keywords
        assert isinstance(formatted_keywords, list)


def test_formatting_meta_for_core():
    for meta_dict in INPUT_META_DICTS:
        formatted_meta = format_meta(meta_dict)
        #pprint(formatted_meta)
        assert formatted_meta
        assert isinstance(formatted_meta, dict)
