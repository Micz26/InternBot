import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import EvaluationDataset
from ragas.metrics import (
    AnswerRelevancy,
    Faithfulness,
    ResponseRelevancy,
)
from typing import Any

from intern_bot.settings import Settings
from intern_bot.agent import agent  # Twój LangGraph agent
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

settings = Settings()

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY.get_secret_value()

questions = [
    'Jestem studentem informatyki i szukam stażu w Sii', 
    'Pokaż praktyki marketingowe', 
    'Szukam stażu jako python developer w Nokia', 
    'Szukam praktyk posiadam rok doświadczenia w programowaniu w Java. Umiem gita i docker.', 
    'Szukam stażu w sektorze bankowym', 
    'czy są dostępne oferty stażowe jako AI/ML developer', 
    'Studiuje budownictwo na 3 roku i szukam stażu w firmie budowlanej', 
    'Studiuje Inżynierie Zarządzania, szukam oferty praktyk na lato',
    'Szukam stażu w sektorze IT', 
    ('Jestem studentem na politechnice wrocławskiej studiuje na kierunku '
     'Mechanika i Budowa Maszyn, czy znasz oferty które mogłby mnie zainteresować?'), 
    'Pokaż mi 8 najlepszych ofert jako backend developer', 
    'Szukam pracy jako CAD designer',
    'Szukam oferty jako JS developer ale nie w Nokii', 
    'Szukam pracy jako analityk danych. umiem Power BI, Tableau oraz SQL', 
    'Studiuje AiR i szukam stażu z obszaru robotyki, czy masz coś dla mnie?',
    'Szukam stażu jako elektryk. Posiadam doświadczenie w instalacji i naprawie instalacji elektrycznych.', 
    'Czy możesz polecić staże dla studentów cyberbezpieczeństwa?', 
    'Szukam praktyk HR w dużych korporacjach w Polsce', 
    'Interesuje mnie staż jako DevOps lub Cloud Engineer, czy są dostępne takie oferty?', 
    'Czy znajdziesz dla mnie staże związane z embedded systems w automotive?', 
]

async def run_evaluation(questions: list[str]):
    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            model='gpt-4o-mini',
            temperature=0,
        )
    )

    ragas_dataset = []
    for q in questions:
        initial_state = {"query": q, "messages": []}
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = await agent.ainvoke(initial_state, config=config)
        messages = result["messages"]

        response = None
        for m in reversed(messages):
            if hasattr(m, "content"):
                response = m.content
                break

        retrieved_contexts = []
        for m in messages:
            if isinstance(m, ToolMessage):
                retrieved_contexts.append(m.content)

        ragas_dataset.append({
            "id": str(uuid.uuid4()),  
            "user_input": q,
            "response": response,
            "retrieved_contexts": retrieved_contexts,
        })

    eval_dataset = EvaluationDataset.from_list(ragas_dataset)

    metrics = [
        Faithfulness(llm=evaluator_llm),  # Czy odpowiedź jest oparta na kontekście (zapobiega halucynacjom)
        AnswerRelevancy(llm=evaluator_llm),  # Trafność odpowiedzi dla zapytania (jak dobrze odpowiada na pytanie)
    ]

    results_df = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
    )

    return results_df, ragas_dataset, metrics


def calculate_average_scores(combined_results: list[dict[str, Any]]) -> dict[str, float]:
    """
    Oblicza średnie wyniki dla wszystkich metryk ze wszystkich sample'ów.

    Args:
        combined_results: Lista wyników z scores dla każdego sample'a

    Returns:
        Słownik ze średnimi wynikami dla każdej metryki
    """
    if not combined_results:
        return {}
    all_metric_keys = set()
    for result in combined_results:
        if 'scores' in result and isinstance(result['scores'], dict):
            all_metric_keys.update(result['scores'].keys())

    average_scores = {}
    for metric_key in all_metric_keys:
        values = []
        for result in combined_results:
            if 'scores' in result and isinstance(result['scores'], dict):
                value = result['scores'].get(metric_key)
                if value is not None and isinstance(value, (int, float)):
                    values.append(float(value))

        if values:
            average_scores[metric_key] = round(sum(values) / len(values), 4)

    return average_scores


def print_average_scores(average_scores: dict[str, float]):
    """
    Wyświetla średnie wyniki metryk w czytelnej formie.

    Args:
        average_scores: Słownik ze średnimi wynikami
    """
    if not average_scores:
        print("\n  No average scores available")
        return

    print("\n" + "="*80)
    print("ŚREDNIE WYNIKI Z WSZYSTKICH SAMPLE'ÓW")
    print("="*80)
    for metric_name, avg_score in sorted(average_scores.items()):
        formatted_name = metric_name.replace('_', ' ').title()
        print(f"  {formatted_name}: {avg_score:.4f}")

    if average_scores:
        overall_avg = sum(average_scores.values()) / len(average_scores)
        print("-"*80)
        print(f"  Overall Average: {overall_avg:.4f}")
    print("="*80)


def save_results_to_json(
    results_df,
    dataset: list,
    metrics: list,
    output_dir: Path | None = None,
    filename: str | None = None,
) -> Path:
    if output_dir is None:
        script_dir = Path(__file__).parent
        output_dir = script_dir / 'evaluation_results'
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'evaluation_results_{timestamp}.json'

    output_file = output_dir / filename

    if hasattr(results_df, 'to_dict'):
        results_list = results_df.to_dict(orient='records')
    elif hasattr(results_df, 'to_pandas'):
        results_df = results_df.to_pandas()
        results_list = results_df.to_dict(orient='records')
    else:
        results_list = list(results_df) if hasattr(results_df, '__iter__') else [results_df]

    dataset_columns = ['id', 'user_input', 'response', 'retrieved_contexts']

    combined_results = []
    for idx, (sample, result_row) in enumerate(zip(dataset, results_list)):
        combined_result = {
            'sample_id': sample.get('id', f'sample_{idx}'),
            'question': sample['user_input'],
            'response': sample['response'],
            'retrieved_contexts_count': len(sample['retrieved_contexts']),
            'scores': {}
        }

        if isinstance(result_row, dict):
            for key, value in result_row.items():
                if key not in dataset_columns:
                    if isinstance(value, (int, float)):
                        combined_result['scores'][key] = round(float(value), 4)
                    else:
                        combined_result['scores'][key] = value
        else:
            combined_result['scores'] = {'raw_result': str(result_row)}

        combined_results.append(combined_result)

    average_scores = calculate_average_scores(combined_results)

    output_data = {
        'metadata': {
            'evaluation_timestamp': datetime.now().isoformat(),
            'total_questions': len(dataset),
            'evaluator_model': 'gpt-4o-mini',
            'metrics_used': [m.__class__.__name__ for m in metrics],
            'average_scores': average_scores,
        },
        'results': combined_results,
        'raw_results': results_list,
        'dataset': dataset,
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

    print(f'\n✓ Results saved to: {output_file.absolute()}')
    print(f'  File size: {output_file.stat().st_size / 1024:.2f} KB')
    return output_file


if __name__ == "__main__":
    questions_to_eval = questions
    results_df, dataset, metrics = asyncio.run(run_evaluation(questions_to_eval))

    print("\n" + "="*80)
    print("Wyniki ewaluacji (per sample):")
    print("="*80)

    print(f"\nResults DataFrame type: {type(results_df)}")
    if hasattr(results_df, 'shape'):
        print(f"Results DataFrame shape: {results_df.shape}")
        print(f"Results DataFrame columns: {list(results_df.columns)}")
        print(f"\nResults DataFrame head:\n{results_df.head()}")

    if hasattr(results_df, 'to_dict'):
        results_dict = results_df.to_dict(orient='records')
    elif hasattr(results_df, 'to_pandas'):
        results_df = results_df.to_pandas()
        results_dict = results_df.to_dict(orient='records')
    else:
        results_dict = list(results_df) if hasattr(results_df, '__iter__') else [results_df]

    print(f"\nResults dict length: {len(results_dict)}")
    if results_dict and isinstance(results_dict[0], dict):
        print(f"First result keys: {list(results_dict[0].keys())}")

    dataset_columns = ['id', 'user_input', 'response', 'retrieved_contexts']

    for idx, (sample, result_row) in enumerate(zip(dataset, results_dict)):
        print(f"\nSample {idx + 1} - Question: {sample['user_input'][:60]}...")
        if isinstance(result_row, dict):
            metric_scores = {k: v for k, v in result_row.items() 
                           if k not in dataset_columns}
            if metric_scores:
                for key, value in metric_scores.items():
                    if isinstance(value, (int, float)):
                        print(f"  {key}: {value:.4f}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  No metric scores found. All keys: {list(result_row.keys())}")
        else:
            print(f"  Result type: {type(result_row)}, value: {result_row}")
        print("-"*60)

    if results_dict and isinstance(results_dict[0], dict):
        dataset_columns = ['id', 'user_input', 'response', 'retrieved_contexts']
        combined_results_for_avg = []
        for idx, (sample, result_row) in enumerate(zip(dataset, results_dict)):
            if isinstance(result_row, dict):
                scores = {k: v for k, v in result_row.items() 
                         if k not in dataset_columns and isinstance(v, (int, float))}
                if scores:
                    combined_results_for_avg.append({'scores': scores})
        if combined_results_for_avg:
            average_scores = calculate_average_scores(combined_results_for_avg)
            print_average_scores(average_scores)

    saved_file = save_results_to_json(results_df, dataset, metrics)
    print(f'\nEvaluation complete! Results saved to: {saved_file.absolute()}')
