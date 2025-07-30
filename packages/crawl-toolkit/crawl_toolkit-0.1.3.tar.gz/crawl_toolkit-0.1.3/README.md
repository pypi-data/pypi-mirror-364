# Crawl Toolkit

Narzędzie do crawlowania i analizy treści, które integruje się z BrightData do crawlowania stron internetowych i OpenAI do analizy treści.

## Instalacja

```bash
pip install crawl-toolkit
```

## Wymagania

- Python 3.8+
- Klucz API BrightData (SERP i Crawler)
- Klucz API OpenAI

## Przykład użycia

```python
from crawl_toolkit import CrawlToolkit, Language, FetchType

# Inicjalizacja
toolkit = CrawlToolkit(
    brightdata_serp_key="your_serp_key",
    brightdata_serp_zone="your_serp_zone",
    brightdata_crawl_key="your_crawl_key",
    brightdata_crawl_zone="your_crawl_zone",
    openai_key="your_openai_key"
)

# Pobieranie najlepszych URL-i dla słowa kluczowego
urls = await toolkit.get_top_urls(
    keyword="python programming",
    max_results=20,
    language=Language.ENGLISH
)

# Pobieranie i czyszczenie treści (różne strategie)
contents_classic = await toolkit.fetch_and_clean_urls(
    urls=urls,
    strategy="classic"  # klasyczne czyszczenie HTML
)
contents_crawl4ai = await toolkit.fetch_and_clean_urls(
    urls=urls,
    strategy="crawl4ai"  # zaawansowane czyszczenie przez crawl4ai
)
contents_markdown = await toolkit.fetch_and_clean_urls(
    urls=urls,
    strategy="markdown"  # czyszczenie markdown
)

# Analiza słów kluczowych
analysis = await toolkit.make_keyword_analysis(
    keyword="python programming",
    max_urls=20,
    language=Language.ENGLISH
)

# Analiza z nagłówkami
analysis_with_headers = await toolkit.make_keyword_analysis_and_headers(
    keyword="python programming",
    max_urls=20,
    language=Language.ENGLISH
)
```

## Funkcjonalności

- Pobieranie najlepszych URL-i z Google dla danego słowa kluczowego
- Pobieranie i czyszczenie treści z podanych URL-i
- Analiza słów kluczowych z użyciem OpenAI
- Wyodrębnianie nagłówków z treści
- Obsługa wielu języków
- Czyszczenie treści HTML i Markdown

## Strategie czyszczenia treści

- `classic` – klasyczne czyszczenie HTML (HtmlCleaner)
- `crawl4ai` – zaawansowane czyszczenie i konwersja do markdown przez crawl4ai
- `markdown` – czyszczenie treści markdown

## Licencja

MIT 