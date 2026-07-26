from auditor.fetcher import fetch_page
from auditor.reporter import print_report
from auditor.runner import run_all_checks
from auditor.exporter import export_results
from auditor.scoring import calculate_score
from auditor.html_reporter import export_html_report

APP_NAME = "SEO Auditor"
VERSION = "0.1.0"

print(f"{APP_NAME} {VERSION}")
print("Select your URL")
user_url = input(" ").strip()
print("You selected:", user_url)

if not user_url.startswith(("http://", "https://")):
    user_url = "https://" + user_url

page = fetch_page(user_url)

response = page["response"]
soup = page["soup"]
html = page["html"]

print(f"Status Code: {response.status_code}")

results = run_all_checks(soup)

print_report(results)

score = calculate_score(results)

json_output_path = export_results(
    results=results,
    score=score,
    url=user_url,
)

html_output_path = export_html_report(
    results=results,
    score=score,
    url=user_url,
)

print()
print(f"JSON report saved to: {json_output_path}")
print(f"HTML report saved to: {html_output_path}")