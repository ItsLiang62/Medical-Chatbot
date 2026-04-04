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
        "type1_diabetes": 20,
        "type2_diabetes": 20,
        "insulin": 20,
        "hyperglycemia": 20,
        "hypoglycemia": 20,
        "glucose": 20,
        "metabolism": 20,
        "endocrine": 20,
        "pancreas": 20,
        "insulin_resistance": 20,
        "blood_sugar": 20,
        "hba1c": 20,
        "neuropathy": 20,
        "retinopathy": 20,
        "nephropathy": 20,
        "cancer": 20,
        "tumor": 20,
        "malignancy": 20,
        "carcinoma": 20,
        "sarcoma": 20,
        "leukemia": 20,
        "lymphoma": 20,
        "metastasis": 20,
        "oncology": 20,
        "chemotherapy": 20,
        "radiotherapy": 20,
        "immunotherapy": 20,
        "biopsy": 20,
        "oncogene": 20,
        "tumor_suppressor": 20,
        "angiogenesis": 20,
        "symptoms": 20,
        "diagnosis": 20,
        "treatment": 20,
        "therapy": 20,
        "prevention": 20,
        "risk_factors": 20,
        "complications": 20,
        "prognosis": 20,
        "screening": 20,
        "clinical": 20,
        "pathophysiology": 20,
        "etiology": 20,
        "epidemiology": 20,
        "chronic": 20,
        "acute": 20,
        "cardiovascular": 20,
        "hypertension": 20,
        "atherosclerosis": 20,
        "stroke": 20,
        "heart_disease": 20,
        "renal": 20,
        "kidney_disease": 20,
        "liver": 20,
        "hepatitis": 20,
        "respiratory": 20,
        "asthma": 20,
        "copd": 20,
        "infection": 20,
        "bacteria": 20,
        "virus": 20,
        "immune": 20
    }
    main(to_ingest)