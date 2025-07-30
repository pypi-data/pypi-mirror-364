from typing import List, Tuple, Any
from rara_tools.core_formatters.formatted_keyword import FormattedKeyword
from rara_tools.core_formatters.formatted_meta import FormattedAuthor
from rara_tools.constants.linker import MAIN_TAXONOMY_LANG, KEYWORD_TYPES_TO_IGNORE, EntityType

def get_primary_author(authors: List[dict]) -> str:
    primary_author = ""
    for author in authors:
        if author.get("is_primary", False):
            primary_author = author.get("name", "")
    return primary_author

def format_authors(authors: List[dict]) -> List[dict]:
    formatted_authors = []
    for author in authors:
        entity_type = author.get("type", EntityType.UNK)

        formatted_author = FormattedAuthor(
            object_dict=author,
            linked_doc=None,
            entity_type=entity_type
        ).to_dict()
        formatted_authors.append(formatted_author)
    return formatted_authors

def format_sections(sections: List[dict]) -> List[dict]:
    for section in sections:
        authors = section.pop("authors", [])
        titles = section.pop("titles", [])
        primary_author = get_primary_author(authors)
        if primary_author:
            for title in titles:
                title["author_from_title"] = primary_author
        section["titles"] = titles

        formatted_authors = format_authors(authors)
        section["authors"] = formatted_authors

    return sections

def format_meta(meta: dict) -> dict:
    """ Formats unlinked meta for Kata CORE.
    """

    meta_to_format = meta.get("meta")

    authors = meta_to_format.pop("authors", [])
    sections = meta_to_format.pop("sections", [])

    formatted_authors = format_authors(authors)
    formatted_sections = format_sections(sections)

    if sections and formatted_sections:
        meta_to_format["sections"] = formatted_sections
    if authors and formatted_authors:
        meta_to_format["authors"] = formatted_authors

    meta["meta"] = meta_to_format

    return meta


def format_keywords(flat_keywords: List[dict]) -> List[dict]:
    """ Formats unlinked keywords for Kata CORE.
    """
    ignored_keywords = []
    filtered_keywords = []

    for keyword_dict in flat_keywords:
        keyword_type = keyword_dict.get("entity_type")
        if keyword_type in KEYWORD_TYPES_TO_IGNORE:
            ignored_keywords.append(keyword_dict)
        else:
            filtered_keywords.append(keyword_dict)

    formatted_keywords = []

    for keyword_dict in filtered_keywords:
        formatted_keyword = FormattedKeyword(
            object_dict=keyword_dict,
            linked_doc=None,
            main_taxnomy_lang=MAIN_TAXONOMY_LANG
        ).to_dict()
        formatted_keywords.append(formatted_keyword)

    return formatted_keywords
