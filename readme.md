# SEO Auditor

A modular Python command-line application for auditing websites for common technical SEO issues. The project supports single-page audits, multi-page website crawls, weighted SEO scoring, interactive HTML dashboards, CSV exports, and internal link graph generation.

---

## Features

### Single-page audits

Audit an individual page for common technical SEO issues, including:

- Title tag
- Meta description
- Canonical URL
- H1 tags
- Heading hierarchy
- Robots meta tags
- Images
- Open Graph metadata
- Twitter Cards
- Structured data
- Internal and external links
- HTTP headers
- Performance metrics
- robots.txt
- Sitemap

---

### Website crawl mode

- Breadth-first website crawler
- Configurable crawl depth
- Concurrent page auditing
- Weighted SEO scoring
- Crawl summary
- Failed-page reporting

---

### Reporting

The auditor can generate:

- Console reports
- JSON exports
- CSV exports
- Interactive HTML dashboard
- Graphviz DOT site graph

---

## Example

Single page audit

```bash
python main.py https://example.com
```

Website crawl

```bash
python main.py https://example.com --crawl
```

Crawl with HTML dashboard

```bash
python main.py https://example.com \
    --crawl \
    --html
```

Generate every report

```bash
python main.py https://example.com \
    --crawl \
    --csv \
    --html \
    --graph
```

---

## Dashboard

The HTML dashboard includes:

- Overall SEO score
- Crawl summary
- Warning and failure counts
- Expandable issue groups
- Highest scoring pages
- Lowest scoring pages
- Sortable page table
- Search/filter
- Failed-page summary

---

## Project Structure

```
auditor/

├── checks/
│   ├── title.py
│   ├── headings.py
│   ├── links.py
│   ├── performance.py
│   └── ...

├── application.py
├── cli.py
├── crawler.py
├── runner.py
├── scoring.py
├── scoring_weights.py

├── exporter.py
├── crawl_csv_exporter.py
├── crawl_html_exporter.py
├── graphviz_exporter.py

├── reporter.py
├── site_reporter.py

tests/

main.py
```

---

## Design Goals

This project emphasizes:

- Modular architecture
- Separation of responsibilities
- Type hints
- Dataclasses
- Testability
- Extensibility
- Clean command-line interface

---

## Technologies

- Python
- BeautifulSoup
- Requests
- ThreadPoolExecutor
- HTML/CSS/JavaScript
- Graphviz

---

## Future Improvements

Potential future enhancements include:

- XML sitemap generation
- robots.txt validation
- PageSpeed Insights integration
- Lighthouse integration
- Accessibility audits
- JSON crawl export
- Async crawling
- Plugin system

---

## Running Tests

```bash
python -m pytest
```

---

## License

MIT License


## Why I Built This

I built this project to deepen my understanding of Python application architecture while exploring technical SEO auditing.

Rather than focusing only on extracting SEO information, I wanted to practice designing a maintainable application with clear separation of concerns, concurrent execution, automated testing, multiple export formats, and an interactive reporting interface.

The project evolved from a simple single-page auditor into a multi-page crawler with weighted scoring, interactive HTML reporting, and internal link visualization.