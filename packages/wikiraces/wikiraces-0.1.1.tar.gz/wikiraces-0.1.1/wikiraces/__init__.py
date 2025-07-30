import wikipedia
from wikiraces.embed import most_similar, most_similar_with_scores
from wikiraces.rerank import rerank_by_summary_similarity
from tqdm import tqdm

class WikiBot:
    def __init__(self, source: str, destination: str, limit: int = 15):
        self.source = source
        self.destination = destination
        self.path = [self.source]

        if not self.exists(self.source):
            raise ValueError(f"Source page '{self.source}' does not exist.")

        if not self.exists(self.destination):
            raise ValueError(f"Destination page '{self.destination}' does not exist.")

        self.limit = limit

    def exists(self, page: str) -> bool:
        """Check if a Wikipedia page exists."""
        try:
            wikipedia.page(page, auto_suggest=False)
            return True
        except wikipedia.exceptions.PageError:
            return False
        except wikipedia.exceptions.DisambiguationError:
            return True  # Disambiguation pages do exist

    def links(self, page: str) -> list[str]:
        """Get the links from a Wikipedia page."""
        if not page or not page.strip():
            return []
        try:    
            page_links = wikipedia.page(page, auto_suggest=False).links
            # Filter out empty or None links
            return [link for link in page_links if link and link.strip()]
        except wikipedia.exceptions.PageError:
            return []
        except wikipedia.exceptions.DisambiguationError as e:
            return []


    def run(self) -> bool:
        print(f"{self.source} -> {self.destination}")

        """Run the WikiBot (loop version)."""
        pbar = tqdm(total=1.0, ncols=80)
        last_progress = 0.0
        try:
            while True:
                title = self.path[-1]
                pbar.bar_format = f'Progress: |{{bar}}| {{n:.2%}} - {title}'
                pbar.refresh()
                title_links = self.links(title)

                if title == self.destination:
                    pbar.update(1.0 - last_progress)
                    return True

                if self.destination in title_links:
                    pbar.update(1.0 - last_progress)
                    return True

                if not title_links:
                    pbar.bar_format = f'Progress: |{{bar}}| {{n:.2%}} - Article "{title}" has no links. Stopping.'
                    pbar.refresh()
                    return False

                links = most_similar_with_scores(self.destination, title_links)[:self.limit]

                # Filter out links that don't have any outgoing links (dead ends)
                viable_links = []
                for link, _ in links:
                    link_links = self.links(link)
                    if link_links:  # Only keep links that have outgoing links
                        viable_links.append(link)

                # Remove links that are already in the path
                filtered_links = [l for l in viable_links if l not in self.path]
                if not filtered_links:
                    pbar.bar_format = f'Progress: |{{bar}}| {{n:.2%}} - No new links to move to. Stopping.'
                    pbar.refresh()
                    return False

                link, score = rerank_by_summary_similarity(self.destination, filtered_links)

                norm_score = float(min(max(score, 0.0), 1.0))
                pbar.update(norm_score - last_progress)
                last_progress = norm_score

                self.path.append(link)
        finally:
            pbar.close()
            print(f"\nPath taken: {' -> '.join(self.path)}")
            print(f"Total steps: {len(self.path) - 1}")