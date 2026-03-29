import arxiv
import json
import time

from pathlib import Path
from loguru import logger
from tqdm import tqdm

class FetchPaper:
    def __init__(self):
        self.category : list[str] = ["cs.AI"] 
        self.num_papers: int = 5000
        self.output_path:  Path = Path("data/raw/papers.json")
        self.page_size : int = 100
        self.delay_seconds : int = 3
        self.num_retries: int = 3
    
    def fetch_papers(self):

        if self.output_path.exists():
            logger.info(f"Loading papers from {self.output_path}")
            return json.loads(self.output_path.read_text())

        logger.info(f"Fetching {self.num_papers} papers from {self.category}")
        
        search = arxiv.Search(
            query = " OR ".join(f"cat:{c}" for c in self.category),
            max_results = self.num_papers,
            sort_by = arxiv.SortCriterion.SubmittedDate,
            sort_order= arxiv.SortOrder.Descending,
        )

        papers = []
        client = arxiv.Client(
            page_size=self.page_size,
            delay_seconds=self.delay_seconds,
            num_retries=self.num_retries)

        try:
            for result in tqdm(client.results(search), total=self.num_papers, desc="Fetching"):
                papers.append({
                "arxiv_id": result.entry_id.split("/")[-1],
                "title": result.title,
                "abstract": result.summary,
                "authors": [a.name for a in result.authors],
                "published": result.published.isoformat(),
                "categories": result.categories,
                "pdf_url": result.pdf_url,
                })
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Fetched failed {e}")
            raise

        self.output_path.parents.mkdir(parents=True, exist_ok = True)
        self.output_path.write_text(json.dumps(papers, indent=2))
        logger.success(f"Saved {len(papers)} papers to {self.output_path}")

        return papers



