"""Full text-only pipeline workflow.

Runs: fetch -> index -> answer -> validate

Usage:
    python configs/workflows/text_pipeline.py
"""

from kohakuengine import Config, Script, Flow

# Shared paths
METADATA = "data/test/metadata.csv"
DB = "artifacts/test_text_only.db"
TABLE_PREFIX = "test"

# Stage configs
fetch_config = Config(
    globals_dict={
        "metadata": METADATA,
        "pdf_dir": "artifacts/test_pdf",
        "output_dir": "artifacts/test_docs",
        "force_download": False,
        "limit": 0,
    }
)

index_config = Config(
    globals_dict={
        "metadata": METADATA,
        "docs_dir": "artifacts/test_docs",
        "db": DB,
        "table_prefix": TABLE_PREFIX,
        "use_citations": False,
    }
)

bm25_config = Config(
    globals_dict={
        "db": DB,
        "table_prefix": TABLE_PREFIX,
    }
)

answer_config = Config(
    globals_dict={
        "db": DB,
        "table_prefix": TABLE_PREFIX,
        "questions": "data/test/test_Q.csv",
        "output": "artifacts/test_preds.csv",
        "metadata": METADATA,
        "llm_provider" : "openai",
        "model": "deepseek-chat",
        "openai_api_key" : "sk-19c364480ac44532a22a18dcab35795c",
        "openai_base_url" : "https://api.deepseek.com/v1",
        "top_k": 8,
        #"bm25_top_k" : 4, 
        "planner_model": "deepseek-chat",
        "planner_max_queries": 4,
        "max_retries": 3,
        "max_concurrent": 10,
        "with_images": False,
        "top_k_images": 0,
        "single_run_debug": False,
        "question_id": None,
        "deduplicate_retrieval" : True,  # Remove duplicate nodes by node_id
        "rerank_strategy" : "combined",  # Options: None, "frequency", "score", "combined"
        "tree_dedup" : True,  # Useful when retrieval targets multiple node levels
        "ignore_blank" : True,
        "top_k_final" : 15,  # Truncate to top-20 after dedup+rerank (None = no truncation)
    }
)

validate_config = Config(
    globals_dict={
        "truth": "data/train_QA.csv",
        "pred": "artifacts/text_pipeline_preds.csv",
        "show_errors": 5,
        "verbose": True,
    }
)


if __name__ == "__main__":
    scripts = [
        Script("scripts/wattbot_fetch_docs.py", config=fetch_config),
        Script("scripts/wattbot_build_index.py", config=index_config),
        #Script("scripts/wattbot_build_bm25_index.py", config=bm25_config),
        Script("scripts/wattbot_answer.py", config=answer_config),
        #Script("scripts/wattbot_validate.py", config=validate_config),
    ]

    flow = Flow(scripts, mode="sequential")
    results = flow.run()

    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
