from sqlalchemy.orm import Session
from database.db_session import get_session, close_session
from database.db_models import Post, Platform, Embedding
import argparse
import numpy as np

from intelligence.intelligence_config import IntelligenceConfig
from intelligence.embedding import get_text_embedding

from typing import Optional, List
import re
from time import sleep


def handle_search(args) -> None:
    """Handle the search command.

    Args:
        args (list[str]): The arguments for the command.
    """
    print("search posts by keyword string")
    parser = argparse.ArgumentParser(prog="search", description="Search posts by keyword string")
    
    parser.add_argument("query", help="Search term")
    parser.add_argument("--platform", help="Optional platform filter")
    parser.add_argument("--limit", type=int, default=100)
    
    
    try:
        parsed = parser.parse_args(args)
        session = get_session()
    
        query = session.query(Post)
        if parsed.platform:
            # get platform_id from platform name
            platform_id = session.query(Platform.platform_id).filter(Platform.name == parsed.platform).first()
            if platform_id is None:
                print(f"[Search Error] Platform '{parsed.platform}' not found.")
                return
            query = query.filter(Post.platform_id == platform_id[0])
        query_text = parsed.query.strip("\"'")
        query = query.filter(Post.content.ilike(f"%{query_text}%"))
        results = query.order_by(Post.timestamp.desc()).limit(parsed.limit).all()
        

        for post in results:
            platform_name = session.query(Platform.name).filter(Platform.platform_id == post.platform_id).first()
            if platform_name:
                print(f"[{post.post_id}] {post.timestamp} | {platform_name[0]} | {post.content[:80]}...")
            else:
                print(f"[{post.post_id}] {post.timestamp} | Unknown Platform | {post.content[:80]}...")
        print(f"Found {len(results)} posts matching '{parsed.query}'")

    except Exception as e:
        print(f"[Search Error] {e}")

    finally:
        try:
            close_session()
        except:
            pass  # In case session was never created




def handle_search_similar(args) -> None:
    parser = argparse.ArgumentParser(prog="search_similar", description="Search for similar posts based on content embedding")
    parser.add_argument("text", nargs="?", help="Semantic query string")
    parser.add_argument("--post_id", type=int, help="Find similar posts to this post ID")
    parser.add_argument("--limit", type=int, help="Number of similar posts to return")
    parser.add_argument("--min_similarity", type=float, help="Minimum similarity score to consider a post similar")
    parser.add_argument("--platform", nargs="+", help="Filter by platform name")
    
    try:
        parsed = parser.parse_args(args)
    except SystemExit as e:
        print("[Search Similar Parsing Error] Invalid arguments provided.")
        return
    except Exception as e:
        print(f"[Search Similar Parsing Error] {e}")
        return

    if not parsed.text and not parsed.post_id:
        print("[Search Similar Error] You must provide either a text query or a post ID to search for similar posts.")
        return
    if parsed.text and parsed.post_id:
        print("[Search Similar Error] You cannot provide both a text query and a post ID. Please choose one.")
        return
    
    
    session = get_session()
    
    
    try:    
        embedding_model = IntelligenceConfig.get_embedding_model_name()
        if not embedding_model:
            print("[Search Similar Error] No embedding model specified. Please set the EMBEDDING_PROVIDER.")
            return
        
        sorted_results = search_similar(session, text=parsed.text, post_id=parsed.post_id, 
                                       limit=parsed.limit, min_similarity=parsed.min_similarity, 
                                       platform=parsed.platform)
        
        
        
        if parsed.post_id:
            print(f"Found {len(sorted_results)} similar posts to post ID {parsed.post_id} with model {embedding_model}:")
        else:
            print(f"Found {len(sorted_results)} similar posts to the text query '{parsed.text}' with model {embedding_model}:")
        for embedding_record, similarity in sorted_results:
            print(f"[{embedding_record.post_id}] Similarity: {similarity:.4f}")
                
    except Exception as e:
        print(f"[Search Similar Error] {e}")
    finally:
        close_session()
        
        
def handle_search_hybrid(args: list[str]) -> None:
    print("search posts by keyword string and semantic similarity")
    parser = argparse.ArgumentParser(prog="search_hybrid", description="Search posts by keyword string and semantic similarity")
    parser.add_argument("keyword", help="Keyword to search for")
    parser.add_argument("--semantic_weight", type=float, default=0.7, help="Weight for semantic similarity (0 to 1), defaults to 0.7")
    parser.add_argument("--limit", type=int, help="Number of posts to return")
    
    try:
        parsed = parser.parse_args(args)
        session = get_session()
        
        # semantic part
        semantic_results = search_similar(session, text=parsed.keyword)
        if not semantic_results:
            print(f"[Search Hybrid Error] No semantic results found for keyword '{parsed.keyword}'.")
            return
        
        results = [(r[0].post_id, r[1]) for r in semantic_results]  # convert to (post_id, similarity)

        # keyword part
        post_ids = [r[0] for r in results]
        keyword_query = session.query(Post).filter(Post.post_id.in_(post_ids))
        keyword_posts = keyword_query.all()
        
        # calculate keyword similarity
        keyword_results = []
        
        for post in keyword_posts:
            _content = post.content.lower() if post.translated_content == None else post.translated_content.lower()
            keyword_similarity = calculate_keyword_similarity(_content, parsed.keyword)
            keyword_results.append((post.post_id, keyword_similarity))

            

            
        # combine results
        combined_results = []
        # to ensure post_id matches in both results
        keyword_score_dict = {k: v for k, v in keyword_results}
        
        for post_id, semantic_score in results:
            keyword_score = keyword_score_dict.get(post_id)
            if keyword_score:
                combined_score = (semantic_score * parsed.semantic_weight) + (keyword_score * (1 - parsed.semantic_weight))
                combined_results.append((post_id, combined_score))
            else:
                combined_results.append((post_id, semantic_score))  # if no keyword score, just use semantic score
                
        # sort by combined score
        combined_results.sort(key=lambda x: x[1], reverse=True)
        if not combined_results:
            print(f"[Search Hybrid Error] No combined results found for keyword '{parsed.keyword}'.")
            return
        
        # check limit
        if parsed.limit:
            combined_results = combined_results[:parsed.limit]
            
        # output results
        print(f"Found {len(combined_results)} posts matching keyword '{parsed.keyword}':")

        # count = 0
        # for post_id, score in combined_results:
        #     count += 1
        #     print(f"[{post_id}] Hybrid Score: {score:.4f}")
        
        
        # this is weird
        # using test data, searching "game crashing", when the limit is 10, the first element is not outputed
        # other limits may also have similar issues of not outputting some elements
        
        for i in range(len(combined_results)):
            post_id, score = combined_results[i]
            print(f"[{post_id}] Hybrid Score: {score:.4f}")

    
    except SystemExit as e:
        print("[Search Hybrid Parsing Error] Invalid arguments provided.")
        return
    except Exception as e:
        print(f"[Search Hybrid Parsing Error] {e}")
        return
    
    
    
def search_similar(session: Session, text: str = None, post_id: int = None, limit: Optional[int] = None, 
                   min_similarity: Optional[float] = None, platform: Optional[List[str]] = None) -> list[tuple[Embedding, float]]:
    """Search for similar posts based on content embedding.

    Args:
        session (Session): The database session.
        text (str): The semantic query string.
        post_id (int, optional): Find similar posts to this post ID.
        limit (int, optional): Number of similar posts to return. Defaults to 100.
        min_similarity (float, optional): Minimum similarity score to consider a post similar. Defaults to 0.5.
        platform_ids (list[int], optional): Filter by platform IDs. Defaults to None.

    Returns:
        list[tuple[int, float]]: List of tuples containing post ID and similarity score.
    """
    # if platform is specified, retrieve platform ids for later use
    if platform:
        platform_ids = session.query(Platform.platform_id).filter(Platform.name.in_(platform)).all()
        if not platform_ids:
            print(f"[Search Similar Error] No platforms found for names: {platform}")
            return
        platform_ids = [p[0] for p in platform_ids]
    

    # post_id
    if post_id:
        # get post embedding for the given post ID
            embedding_model = IntelligenceConfig.get_embedding_model_name()
            if not embedding_model:
                print("[Search Similar Error] No embedding model specified. Please set the EMBEDDING_PROVIDER.")
                return
            
            embedding = session.query(Embedding).filter(Embedding.post_id == post_id, Embedding.model == embedding_model).first()
            if not embedding:
                print(f"[Search Similar Error] No embedding found for post ID {post_id} with model {embedding_model}.")
                return
            
            embedding_vector = embedding.embedding
            if embedding_vector is None or len(embedding_vector) == 0:
                print(f"[Search Similar Error] Post ID {post_id} has no embedding vector.")
                return
            
            rows_query = session.query(Embedding).join(Post, Embedding.post_id == Post.post_id).filter(
                Embedding.embedding != None,
                Embedding.model == embedding_model,
                Post.post_id != post_id
            )
            
            if platform:
                rows_query = rows_query.filter(Post.platform_id.in_(platform_ids))

            rows = rows_query.all()
            
            if not rows:
                print(f"[Search Similar Error] No available posts found for post ID {post_id}.")
                return
        
    else:
        # text query
        if not text:
            print("[Search Similar Error] No text query provided.")
            return
        
        _, embedding_vector = get_text_embedding(text)
        if not embedding_vector:
            print("[Search Similar Error] Failed to generate embedding for the provided text query.")
            return
        
        embedding_model = IntelligenceConfig.get_embedding_model_name()
        if not embedding_model:
            print("[Search Similar Error] No embedding model specified. Please set the EMBEDDING_PROVIDER.")
            return
        
        rows_query = session.query(Embedding).join(Post, Embedding.post_id == Post.post_id).filter(
            Embedding.embedding != None,
            Embedding.model == embedding_model
        )
        if platform:
            rows_query = rows_query.filter(Post.platform_id.in_(platform_ids))

        rows = rows_query.all()

        if not rows:
            print(f"[Search Similar Error] No available posts found for the text query. {text}")
            return

    # Compute cosine similarity between the query embedding and all other post embeddings
    similarities = []
    query_vector = np.array(embedding_vector, dtype=np.float32)
    matrix = np.stack([np.array(row.embedding, dtype=np.float32) for row in rows])
    similarities = np.dot(matrix, query_vector) / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vector))
    sorted_results = sorted(zip(rows, similarities), key=lambda x: x[1], reverse=True)
    
    # Filter by minimum similarity if specified
    if min_similarity is not None:
        sorted_results = [(embedding_record, similarity) for embedding_record, similarity in sorted_results if similarity >= min_similarity]
    
    if limit != None:
        sorted_results = sorted_results[:limit]
        
    return sorted_results
    



def calculate_keyword_similarity(content: str, keyword: str) -> float:
    """Calculate the similarity between the content and a keyword.
    Should return a score between 0 and 1, where 1 means the keyword is fully contained in the content.

    Args:
        content (str): The content to search within.
        keyword (str): The keyword to search for.

    Returns:
        float: The similarity score between the content and keyword.
    """
    if not keyword or not content:
        return 0.0

    # tokenize the content and keyword
    # pre-process the content and keyword, removing punctuation and converting to lowercase
    content_tokens = set(re.findall(r"\w+", content.lower()))
    keyword_tokens = set(re.findall(r"\w+", keyword.lower()))

    if not keyword or not content:
        return 0.0
    
    overlap = content_tokens.intersection(keyword_tokens)
    if not overlap:
        return 0.0
    
    
    # calculate the weighted score based on the overlap, exponentially weighted by the length of the keyword and content
    # but let length of content to be neutral
    alpha = 0.5  # weight for the keyword match ratio
    match_ratio = len(overlap) / len(keyword_tokens)
    score = match_ratio ** alpha
    return round(min(score, 1.0), 4)