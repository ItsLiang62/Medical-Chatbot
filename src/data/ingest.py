from requests import get
from json import dump
from lxml import etree
from pathlib import Path

current_dir = Path.cwd()
data_dir = current_dir.parent.parent / "data"

def search_articles(query, max_results, save_filename):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance"
    }

    response = get(url, params)
    pmids = response.json()["esearchresult"]["idlist"]

    if not save_filename.endswith(".txt"):
        raise ValueError("Article PMIDs must be saved in .txt file")

    file_path = data_dir / "pmids" / save_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    open(file_path, "w").write(",".join(pmids))

    return pmids

def fetch_articles(pmids, save_filename):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = get(url, params)

    if not save_filename.endswith(".xml"):
        raise ValueError("Raw article data must be saved in .xml file")

    file_path = data_dir / "raw" / save_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    open(file_path, "wb").write(response.content)

    return response.content

def parse_articles(xml_content, save_filename):
    root = etree.fromstring(xml_content)

    articles = []

    for article in root.xpath("//PubmedArticle"):
        pmid = article.xpath(".//PMID//text()")
        title = article.xpath(".//ArticleTitle//text()")
        abstract = article.xpath(".//Abstract//text()")

        articles.append({
            "pmid": pmid[0] if pmid else None,
            "title": title[0] if title else None,
            "abstract": " ".join(abstract) if abstract else None
        })

    if not save_filename.endswith(".json"):
        raise ValueError("Parsed article data must be saved in .json file")

    file_path = data_dir / "parsed" / save_filename

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        dump(articles, f, indent=2, ensure_ascii=False)

    return articles

def main(queries_max_results):
    for query, max_results in queries_max_results.items():
        parse_articles(
            fetch_articles(
                search_articles(
                    query, max_results, query + ".txt"
                ), query + ".xml"
            ), query + ".json"
        )

if __name__ == "__main__":
    to_ingest = {
        "diabetes": 20,
        "cancer": 20
    }
    main(to_ingest)