
from database.db_models import Post, Embedding, Analysis, Platform
from intelligence.language import detect_language, translate_text, LANGUAGE_MAPPING
from intelligence.sentiment import get_text_sentiment
from intelligence.priority_score import get_priority_score_from_post_analysis
from intelligence.embedding import get_text_embedding
from intelligence.intelligence_config import IntelligenceConfig
from datetime import datetime

def process_post(session, post: Post, lang_detection=True, translation=True, sentiment_analysis=True, priority_score=True, embedding_generation=True, 
                 explain=False, rewrite=True) -> None:
    """Process a post: perform language detection, translation, sentiment analysis, priority score calculation, and embedding generation.
    Write the results to post, analysis, and embedding tables in the database.

    Args:
        session (Session): _sqlalchemy session to interact with the database.
        post (Post): The post to process.
        lang_detection (bool, optional): Whether to perform language detection. Defaults to True.
        translation (bool, optional): Whether to perform translation. Defaults to True.
        sentiment_analysis (bool, optional): Whether to perform sentiment analysis. Defaults to True.
        priority_score (bool, optional): Whether to calculate priority score. Defaults to True.
        embedding_generation (bool, optional): Whether to generate embeddings. Defaults to True.
        explain (bool, optional): Whether to explain the processing steps. Defaults to False.
        rewrite (bool, optional): Whether to rewrite the post content. Defaults to True.
        
    Raises:
        Exception: If any processing step fails, an exception is raised with an error message.
    """
    if lang_detection is False and translation is False and sentiment_analysis is False and priority_score is False and embedding_generation is False:
        print("[Process Error] No processing steps selected. At least one step must be enabled.")
        raise Exception("No processing steps selected. At least one step must be enabled.")
    
    # Check if post_id is provided
    if post.post_id is None:
        print("[Process Error] No post_id provided.")
        return

    # process = language detection, translation, sentiment analysis, priority_score calculation, embedding generation
    
    if explain:
        print(f"[Process] Processing post {post.post_id}...")
    
    
    
    # 1. Language Detection
    if lang_detection:
        if rewrite or not post.language:
            if explain:
                print(f"[Process] Detecting language for post {post.post_id}...")
            try:
                # Assuming we have a function to detect language
                language, language_confidence = detect_language(post.content)
            
                post.language = language
                post.language_confidence = language_confidence
                session.commit()
                if explain:
                    print(f"[Process] Detected language {language} with confidence {language_confidence:.2f} for post {post.post_id}.")
            except Exception as e:
                session.rollback()
                print(f"[Process Error] Failed to detect language for post {post.post_id}: {e}")
                raise Exception(f"Failed to detect language for post {post.post_id}: {e}")
        else:
            # already detected
            print(f"[Process] Post {post.post_id} already has language {post.language} with confidence {post.language_confidence:.2f}, skipping detection.")
            
            
    # 2. Translation
    if translation:
        if rewrite or not post.translated_content:
            if explain:
                print(f"[Process] Translating post {post.post_id}...")
            try:
                target_language = IntelligenceConfig.DEFAULT_LANGUAGE
                post_language = post.language
                if post_language and post_language == IntelligenceConfig.DEFAULT_LANGUAGE:
                    if explain:
                        print(f"[Process] Post {post.post_id} is already in the default language ({IntelligenceConfig.DEFAULT_LANGUAGE}), skipping translation.")
                else:
                    if target_language not in LANGUAGE_MAPPING:
                        print(f"[Process Warning] target language {target_language} is not in LANGUAGE_MAPPING, using its ISO 639-1 code as target language.")
                    else:
                        target_language = LANGUAGE_MAPPING[target_language]
                    translated_text = translate_text(post.content, target_language)
                    post.translated_content = translated_text
                    session.commit()
                    if explain:
                        print(f"[Process] Translated post {post.post_id} to {target_language}.")
            except Exception as e:
                session.rollback()
                print(f"[Process Error] Failed to translate post {post.post_id}: {e}")
                raise Exception(f"Failed to translate post {post.post_id}: {e}")
        else:
            # already translated
            print(f"[Process] Post {post.post_id} already has translated content, skipping translation.")
            
    
    # pre-check if post has its corresponding analysis
    analysis_entry = None
    if sentiment_analysis or priority_score:
        try:
            analysis_entry = session.query(Analysis).filter(Analysis.post_id == post.post_id).first()
        except Exception as e:
            print(f"[Process Error] Failed to query analysis for post {post.post_id}: {e}")
            raise Exception(f"Failed to query analysis for post {post.post_id}: {e}")
        
        
    # 3. Sentiment Analysis
    if sentiment_analysis:
        if rewrite or not analysis_entry or (analysis_entry and not analysis_entry.sentiment_label):
            if explain:
                print(f"[Process] Analyzing sentiment for post {post.post_id}...")
            try:
                _content = post.content
                if post.translated_content:
                    _content = post.translated_content
                sentiment, sentiment_confidence = get_text_sentiment(_content)

                if analysis_entry is None:
                    analysis_entry = Analysis(
                        post_id=post.post_id,
                        sentiment_label=sentiment,
                        sentiment_score=sentiment_confidence
                    )
                    session.add(analysis_entry)
                else:
                    analysis_entry.sentiment_label = sentiment
                    analysis_entry.sentiment_score = sentiment_confidence
                session.commit()
                if explain:
                    print(f"[Process] Analyzed sentiment for post {post.post_id}: {sentiment} (confidence: {sentiment_confidence:.2f})")
            except Exception as e:
                session.rollback()
                print(f"[Process Error] Failed to analyze sentiment for post {post.post_id}: {e}")
                raise Exception(f"Failed to analyze sentiment for post {post.post_id}: {e}")
        else:
            # already analyzed
            print(f"[Process] Post {post.post_id} already has sentiment analysis, skipping.")
            

    # 4. Priority Score Calculation
    if priority_score:
        if analysis_entry is None:
            # should not happen, but just in case
            print(f"[Process Error] No analysis found for post {post.post_id}. Cannot calculate priority score.")
            raise Exception(f"No analysis found for post {post.post_id}. Cannot calculate priority score.")
        if rewrite or analysis_entry.priority_score is None:
            if explain:
                print(f"[Process] Calculating priority score for post {post.post_id}...")
            try:
                # get platform name from post
                platform_name = session.query(Platform.name).filter(Platform.platform_id == post.platform_id).scalar()
                if not platform_name:
                    print(f"[Process Error] No platform found for post {post.post_id}. Cannot calculate priority score.")
                    raise Exception(f"No platform found for post {post.post_id}. Cannot calculate priority score.")

                scores = get_priority_score_from_post_analysis(post, analysis_entry, platform_name)
                analysis_entry.priority_score = scores[0]
                session.add(analysis_entry)  # Ensure the analysis entry is added to the session
                session.commit()
                
                if explain:
                    print(f"[Process] Calculated priority score for post {post.post_id}: {scores[0]}")
                    print(f"[Process] Sentiment score: {scores[1]}, Engagement score: {scores[2]}, Critical keywords score: {scores[3]}, Recency score: {scores[4]}, Author score: {scores[5]}")
            
            except Exception as e:
                session.rollback()
                print(f"[Process Error] Failed to calculate priority score for post {post.post_id}: {e}")
                raise Exception(f"Failed to calculate priority score for post {post.post_id}: {e}")
        else:
            # already calculated
            print(f"[Process] Post {post.post_id} already has priority score, skipping.")
            
            
    # 5. Embedding Generation
    if embedding_generation:
        embedding_entry = session.query(Embedding).filter(Embedding.post_id == post.post_id).first()
        if rewrite or (embedding_entry is None or not embedding_entry.embedding):
            if explain:
                print(f"[Process] Generating embedding for post {post.post_id}...")
            try:
                _content = post.content
                if post.translated_content:
                    _content = post.translated_content
                model_name, embedding_vector = get_text_embedding(_content)
                if embedding_vector is None or len(embedding_vector) == 0:
                    print(f"[Process Error] Failed to generate embedding for post {post.post_id}.")
                    raise Exception(f"Failed to generate embedding for post {post.post_id}.")

                if embedding_entry is None:
                    embedding_entry = Embedding(
                        post_id=post.post_id,
                        model=model_name,
                        embedding=embedding_vector,
                        content=post.translated_content if post.translated_content else post.content
                    )
                    session.add(embedding_entry)
                else:
                    embedding_entry.model = model_name
                    embedding_entry.embedding = embedding_vector
                    embedding_entry.created_at = datetime.utcnow()
                session.commit()
                if explain:
                    print(f"[Process] Generated embedding for post {post.post_id} using model {model_name}.")
            except Exception as e:
                session.rollback()
                print(f"[Process Error] Failed to generate embedding for post {post.post_id}: {e}")
                raise Exception(f"Failed to generate embedding for post {post.post_id}: {e}")
        else:
            # already generated
            print(f"[Process] Post {post.post_id} already has embedding, skipping.")
        
    # If we reach here, all processing steps were successful
    print(f"[Process] Successfully processed post {post.post_id}.")
    if explain:
        print(f"[Process] Post {post.post_id} processing complete. "
              f"Language: {post.language}, "
              f"Translated: {bool(post.translated_content)}, "
              f"Sentiment: {analysis_entry.sentiment_label if analysis_entry else 'N/A'}, "
              f"Priority Score: {analysis_entry.priority_score if analysis_entry else 'N/A'}, "
              f"Embedding: {'Yes' if embedding_entry and embedding_entry.embedding is not None and len(embedding_entry.embedding) > 0 else 'No'}")
        
