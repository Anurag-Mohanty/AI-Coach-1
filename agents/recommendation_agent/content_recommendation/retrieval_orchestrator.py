import asyncio
import httpx
from typing import List, Dict, Tuple, Any
from .query_planner_agent import generate_search_queries
from .research_agent import run_research_agent
from .youtube_retriever_agent import search_youtube_for_task
from .github_retriever_agent import search_github_for_task
from .linkedin_retriever_agent import run_linkedin_retriever
from .reflection_agent import reflect_on_relevance
from .perplexity_search import search_perplexity
from agent_core.content_cache import ContentCache
from agent_core.timing_utils import timed_function
from aiohttp import ClientSession, ClientTimeout
import backoff

@timed_function("Retrieval Orchestration", display=True)
async def run_retrieval_orchestrator(subtask: str,
                                   context: Dict[str, Any],
                                   user_id: str = "test_user",
                                   session_id: str = "default_session",
                                   print_debug: bool = False,
                                   return_queries: bool = False) -> Tuple[List[Dict], List[Dict], List[str]]:

    # Initialize shared HTTP client with proper configuration
    timeout = ClientTimeout(total=30, connect=10)
    content_cache = ContentCache()

    async with ClientSession(timeout=timeout) as session:
        # Run initial operations concurrently
        cache_task = content_cache.search_cached_content(context)
        query_task = generate_search_queries(subtask, context)

        # Wait for both operations
        cached_results, queries = await asyncio.gather(cache_task, query_task)

        if cached_results and print_debug:
            print(f"\n📦 Found {len(cached_results)} relevant cached items")
        if print_debug:
            print(f"\n📝 Generated {len(queries)} search queries")

        # Define retrieval functions with retry logic
        @backoff.on_exception(backoff.expo, Exception, max_tries=3)
        async def fetch_with_retry(source_fn, query: str) -> List[Dict]:
            try:
                print(f"\n🔍 Trying {source_fn.__name__} with query: {query}")
                results = await source_fn(query, context)
                if results:
                    print(f"✓ {source_fn.__name__} returned {len(results)} results")
                    return [{"source": source_fn.__name__, "query": query, **item} for item in results]
                else:
                    print(f"✗ {source_fn.__name__} returned no results")
            except Exception as e:
                if print_debug:
                    print(f"❌ Error in {source_fn.__name__}: {str(e)}")
            return []

        # Create tasks for each source
        tasks = []
        for query in queries:
            for source_fn in [search_perplexity, search_youtube_for_task, 
                            search_github_for_task, run_linkedin_retriever]:
                tasks.append(fetch_with_retry(source_fn, query))

        # Process in smaller chunks to avoid overwhelming connections
        chunk_size = 4
        all_results = []
        seen_content = set()  # Track unique content
        source_counts = {}

        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i:i + chunk_size]
            try:
                chunk_results = await asyncio.gather(*chunk, return_exceptions=True)
                for result in chunk_results:
                    if isinstance(result, list):
                        # Deduplicate based on title and source
                        for item in result:
                            content_key = f"{item.get('source', '')}:{item.get('title', '')}"
                            if content_key not in seen_content:
                                seen_content.add(content_key)
                                all_results.append(item)
                                # Track source counts
                                source = item.get("source", "unknown")
                                source_counts[source] = source_counts.get(source, 0) + 1
                # Small delay between chunks
                await asyncio.sleep(0.5)
            except Exception as e:
                if print_debug:
                    print(f"Chunk processing error: {str(e)}")

        # Run reflection and scoring
        reflection_result = await reflect_on_relevance(all_results, subtask, context)
        curated_items, reflection_log = reflection_result

        # Store in cache
        await content_cache.store_content(curated_items, context)

        # Combine with cached results
        final_results = curated_items + [item for item in cached_results 
                                       if item["title"] not in [x["title"] for x in curated_items]]

        # Print summary
        print("\n📈 Results Summary:")
        print(f"- Initial queries generated: {len(queries)}")
        print("- Results by source:")
        for source, count in source_counts.items():
            print(f"  • {source}: {count} results")
        print(f"- Total results before reflection: {len(all_results)}")
        print(f"- Results from cache: {len([x for x in final_results if x.get('cached')])}")
        print(f"- New curated results: {len([x for x in final_results if not x.get('cached')])}")
        print(f"- Final total results: {len(final_results)}")

        if return_queries:
            return final_results, reflection_log, queries
        return final_results, reflection_log, []