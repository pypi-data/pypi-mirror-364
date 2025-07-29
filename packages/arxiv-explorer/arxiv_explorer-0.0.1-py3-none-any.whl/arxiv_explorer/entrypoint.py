import yaml
import arxiv
import argparse
import arxiv_explorer
from pathlib import Path


def search_arxiv(topics: list) -> list:
    results = []
    client = arxiv.Client()

    for topic in topics:
        search = arxiv.Search(
            query=topic, max_results=5, sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results.extend(list(client.results(search)))

    return [
        [
            r.title,
            r.summary,
            r.published,
            r.get_short_id(),
            r.primary_category,
            r.pdf_url,
        ]
        for r in results
    ]


def main():
    parser = argparse.ArgumentParser(
        description="arXiv Explorer: A tool to search and summarize arXiv."
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to the simulation configuration YAML file (default: config.yaml)",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    config_text = config_path.read_text(encoding="utf-8")
    config_data = yaml.safe_load(config_text).get("arxiv-explorer", {})
    config_topics = config_data.get("topics", [])

    # config_provider = config_data.get("provider", "openrouter")
    # config_model = config_data.get("model", "moonshotai/kimi-k2")

    # api_key, base_url = arxiv_summarizer.providers.get(config_provider)
    # client = openai.Client(api_key=api_key, base_url=base_url)

    results = search_arxiv(config_topics)

    # for i in range(len(results)):
    #     result = results[i]
    #     message = [
    #         {
    #             "role": "user",
    #             "content": f"Summarize the following text in 2 sentences: {result[1]}",
    #         }
    #     ]
    #     summary = client.chat.completions.create(
    #         model=config_model,
    #         messages=message,
    #     )
    #     results[i][1] = summary.choices[0].message.content

    arxiv_explorer.tui.splash.arXivExplorer(results).run()


if __name__ == "__main__":
    main()
