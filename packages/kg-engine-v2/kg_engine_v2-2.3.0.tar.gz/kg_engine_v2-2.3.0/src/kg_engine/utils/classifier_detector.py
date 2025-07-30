"""
Classifier Detection - Maps predicates to categories and standardizes edge names
"""
from typing import List, Dict, Optional
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ..models import ExtractedInfo
from ..models.classifier_map import ClassifierMap

logger = logging.getLogger(__name__)


class ClassifierDetector:
    """
    Detects and assigns classifiers to extracted relationships.
    Maps predicates to categories and standardizes edge names.
    """
    
    def __init__(self, classifier_map: ClassifierMap, embedder=None):
        self.classifier_map = classifier_map
        self.embedder = embedder  # Sentence transformer for vector similarity
        
        # Embedding cache for normalized names
        self.category_embeddings: Dict[str, np.ndarray] = {}
        self.edge_embeddings: Dict[str, Dict[str, np.ndarray]] = {}
        self.normalized_to_original: Dict[str, str] = {}  # Map normalized back to original
        
        # Initialize embedding cache if embedder is available
        if self.embedder:
            self._build_embedding_cache()
        
        # Predefined category patterns for common predicates
        self.category_patterns = {
            'location': [
                'LIVES_IN', 'STAY_IN', 'RESIDES_IN', 'LOCATED_IN', 'BORN_IN',
                'MOVED_TO', 'MOVED_FROM', 'TRAVELED_TO', 'VISITED'
            ],
            'business': [
                'WORKS_AT', 'EMPLOYED_BY', 'WORKS_AS', 'LOOKING_FOR', 
                'HIRING', 'FOUNDED', 'MANAGES', 'LEADS', 'OWNS'
            ],
            'relations': [
                'SON_OF', 'DAUGHTER_OF', 'FRIEND_OF', 'MARRIED_TO',
                'PARENT_OF', 'SIBLING_OF', 'KNOWS', 'MENTOR_OF'
            ],
            'preference': [
                'LIKES', 'PREFERS', 'ENJOYS', 'AVOIDS', 'DISLIKES',
                'INTERESTED_IN', 'HOBBIES', 'HOBBY_IS'
            ],
            'emotions': [
                'LOVES', 'HATES', 'FEARS', 'ADMIRES', 'RESPECTS'
            ],
            'skills': [
                'SPEAKS', 'LANGUAGE', 'SKILLED_IN', 'KNOWS_LANGUAGE',
                'PROGRAMMING_LANGUAGE', 'EXPERTISE_IN'
            ],
            'education': [
                'STUDIED_AT', 'GRADUATED_FROM', 'TEACHES_AT', 'LEARNED',
                'DEGREE_IN', 'MAJOR_IN'
            ],
            'status': [
                'HAS_STATUS', 'IS', 'BECAME', 'STATUS_IS'
            ]
        }
    
    def detect_and_classify_relationships(self, extracted_infos: List[ExtractedInfo]) -> List[ExtractedInfo]:
        """
        Process extracted relationships and assign categories.
        
        Args:
            extracted_infos: List of ExtractedInfo from LLM extraction
            
        Returns:
            List of ExtractedInfo with category field populated
        """
        classified_relationships = []
        
        for info in extracted_infos:
            # Detect category for the predicate
            category = self._detect_category(info.relationship)
            
            # Find best standardized edge name
            standardized_edge = self._find_or_create_standardized_edge(
                category, info.relationship
            )
            
            # Create new ExtractedInfo with category and standardized edge
            classified_info = ExtractedInfo(
                subject=info.subject,
                relationship=standardized_edge,
                object=info.object,
                summary=info.summary,
                is_negation=info.is_negation,
                confidence=info.confidence,
                from_date=info.from_date,
                to_date=info.to_date,
                category=category
            )
            
            classified_relationships.append(classified_info)
            logger.debug(f"Classified: {info.relationship} -> {standardized_edge} (category: {category})")
        
        return classified_relationships
    
    def _detect_category(self, predicate: str) -> str:
        """
        Detect the most appropriate category for a predicate using LLM-enhanced logic.
        
        Args:
            predicate: The relationship type to classify
            
        Returns:
            Category name
        """
        predicate_upper = predicate.upper()
        
        # First check if predicate already exists in classifier map
        existing_category = self.classifier_map.get_category_for_edge(predicate_upper)
        if existing_category:
            logger.debug(f"Found existing category for {predicate}: {existing_category}")
            return existing_category
        
        # Use vector similarity for intelligent category detection if available
        if self.embedder:
            vector_category = self._vector_detect_category(predicate_upper)
            if vector_category:
                logger.debug(f"Vector detected category for {predicate}: {vector_category}")
                return vector_category
        
        # Fallback to pattern-based detection
        # Check predefined patterns
        for category, patterns in self.category_patterns.items():
            if predicate_upper in patterns:
                logger.debug(f"Matched pattern for {predicate}: {category}")
                return category
        
        # Semantic matching with existing categories
        best_category = self._semantic_category_match(predicate_upper)
        if best_category:
            logger.debug(f"Semantic match for {predicate}: {best_category}")
            return best_category
        
        # Default fallback category
        default_category = self._get_default_category(predicate_upper)
        logger.debug(f"Using default category for {predicate}: {default_category}")
        return default_category
    
    def _semantic_category_match(self, predicate: str) -> Optional[str]:
        """
        Find semantically similar category based on word similarity.
        
        Args:
            predicate: The relationship type to match
            
        Returns:
            Best matching category or None
        """
        predicate_words = set(predicate.lower().split('_'))
        best_category = None
        best_score = 0.0
        
        # Check similarity with existing edges in categories
        for category in self.classifier_map.get_all_categories():
            category_edges = self.classifier_map.get_edges_by_classifier(category)
            
            for edge in category_edges:
                edge_words = set(edge.lower().split('_'))
                common_words = len(predicate_words & edge_words)
                total_words = len(predicate_words | edge_words)
                
                if total_words > 0:
                    similarity = common_words / total_words
                    if similarity > best_score and similarity >= 0.3:  # Minimum threshold
                        best_score = similarity
                        best_category = category
        
        # Also check against predefined patterns
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                pattern_words = set(pattern.lower().split('_'))
                common_words = len(predicate_words & pattern_words)
                total_words = len(predicate_words | pattern_words)
                
                if total_words > 0:
                    similarity = common_words / total_words
                    if similarity > best_score and similarity >= 0.4:  # Higher threshold for patterns
                        best_score = similarity
                        best_category = category
        
        return best_category if best_score >= 0.3 else None
    
    def _get_default_category(self, predicate: str) -> str:
        """
        Determine default category based on predicate characteristics.
        
        Args:
            predicate: The relationship type
            
        Returns:
            Default category name
        """
        predicate_lower = predicate.lower()
        
        # Location indicators
        if any(word in predicate_lower for word in ['in', 'at', 'from', 'to', 'location']):
            return 'location'
        
        # Business/work indicators
        if any(word in predicate_lower for word in ['work', 'job', 'employ', 'business', 'company']):
            return 'business'
        
        # Relationship indicators
        if any(word in predicate_lower for word in ['of', 'with', 'friend', 'family', 'relation']):
            return 'relations'
        
        # Status indicators
        if any(word in predicate_lower for word in ['is', 'has', 'status', 'state']):
            return 'status'
        
        # Default to general
        return 'general'
    
    def _find_or_create_standardized_edge(self, category: str, proposed_edge: str) -> str:
        """
        Find best existing edge in category or create new standardized one using LLM intelligence.
        
        Args:
            category: The detected category
            proposed_edge: The original relationship from LLM
            
        Returns:
            Standardized edge name
        """
        # Use vector similarity for intelligent edge matching if available
        if self.embedder:
            vector_best_edge = self._vector_find_best_edge(category, proposed_edge)
            if vector_best_edge:
                logger.debug(f"Vector selected existing edge: {proposed_edge} -> {vector_best_edge}")
                return vector_best_edge
        
        # Fallback to traditional similarity matching with higher threshold
        best_existing = self.classifier_map.get_best_edge_for_category(
            category, proposed_edge, similarity_threshold=0.85  # Match vector threshold
        )
        
        if best_existing:
            logger.debug(f"Using existing edge (high similarity): {proposed_edge} -> {best_existing}")
            return best_existing
        
        # Standardize the proposed edge name and create new
        standardized = self._standardize_edge_name(proposed_edge)
        
        # Add to classifier map
        self.classifier_map.get_or_create_edge(category, standardized)
        
        logger.debug(f"Created new standardized edge: {proposed_edge} -> {standardized} (category: {category})")
        return standardized
    
    def _standardize_edge_name(self, edge_name: str) -> str:
        """
        Standardize edge name to follow conventions.
        
        Args:
            edge_name: Original edge name
            
        Returns:
            Standardized edge name
        """
        # Convert to uppercase with underscores
        standardized = edge_name.upper().replace(' ', '_').replace('-', '_')
        
        # Remove multiple underscores
        while '__' in standardized:
            standardized = standardized.replace('__', '_')
        
        # Remove leading/trailing underscores
        standardized = standardized.strip('_')

        return standardized
    
    def _vector_detect_category(self, predicate: str) -> Optional[str]:
        """
        Use vector similarity to detect the most suitable category for a predicate.
        Only returns a category if similarity >= 85%.
        
        Args:
            predicate: The relationship type to classify
            
        Returns:
            Category name if similarity >= 85%, None otherwise
        """
        if not self.embedder or not self.category_embeddings:
            return None
            
        try:
            # Create embedding for the predicate
            embedding_text = self._normalize_for_embedding(predicate, "category")
            predicate_embedding = self.embedder.encode([embedding_text])[0]
            
            best_category = None
            best_similarity = 0.0
            
            # Compare against all category embeddings
            for normalized_category, category_embedding in self.category_embeddings.items():
                similarity = self._calculate_similarity(predicate_embedding, category_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_category = normalized_category
            
            # Apply 85% threshold
            if best_similarity >= 0.85:
                original_category = self.normalized_to_original.get(best_category, best_category)
                logger.debug(f"Vector detected category for '{predicate}': '{original_category}' (similarity: {best_similarity:.3f})")
                return original_category
            else:
                logger.debug(f"No category found for '{predicate}' above 85% threshold (best: {best_similarity:.3f})")
                return None
                
        except Exception as e:
            logger.warning(f"Vector category detection failed for '{predicate}': {e}")
            return None
    
    def _vector_find_best_edge(self, category: str, proposed_edge: str) -> Optional[str]:
        """
        Use vector similarity to find the best existing edge in a category.
        Only returns existing edge if similarity >= 85%.
        
        Args:
            category: The category to search in
            proposed_edge: The proposed edge name
            
        Returns:
            Best existing edge name if >= 85% similar, None to create new edge
        """
        if not self.embedder or not self.edge_embeddings:
            return None
            
        try:
            # Normalize category and proposed edge
            normalized_category = self._normalize_edge_name(category)

            # Get edge embeddings for this category  
            category_edges = self.edge_embeddings.get(normalized_category, {})
            if not category_edges:
                logger.debug(f"No existing edges found in category '{category}'")
                return None
            
            # Create embedding for the proposed edge
            embedding_text = self._normalize_for_embedding(proposed_edge, "relationship")
            proposed_embedding = self.embedder.encode([embedding_text])[0]
            
            best_edge = None
            best_similarity = 0.0
            
            # Compare against all edges in the category
            for normalized_edge, edge_embedding in category_edges.items():
                similarity = self._calculate_similarity(proposed_embedding, edge_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_edge = normalized_edge
            
            # Apply 85% threshold
            if best_similarity >= 0.85:
                original_edge = self.normalized_to_original.get(best_edge, best_edge)
                logger.debug(f"Vector found best edge for '{proposed_edge}' in '{category}': '{original_edge}' (similarity: {best_similarity:.3f})")
                return original_edge
            else:
                logger.debug(f"No edge found for '{proposed_edge}' in '{category}' above 85% threshold (best: {best_similarity:.3f})")
                return None
                
        except Exception as e:
            logger.warning(f"Vector edge matching failed for '{proposed_edge}' in '{category}': {e}")
            return None
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics about categories and their edges."""
        return self.classifier_map.get_stats()
    
    def _normalize_edge_name(self, edge_name: str) -> str:
        """
        Normalize edge name for better similarity matching.
        Removes underscores, converts to lowercase, cleans spaces.
        
        Args:
            edge_name: Original edge name (e.g., 'WORKS_AT', 'IS_EMPLOYED_BY')
            
        Returns:
            Normalized edge name (e.g., 'works at', 'is employed by')
        """
        if not edge_name:
            return ""
            
        # Convert to lowercase and replace underscores with spaces
        normalized = edge_name.lower().replace('_', ' ')
        
        # # Remove common prefixes that add noise
        # prefixes_to_remove = ['is ', 'has ', 'was ', 'were ', 'be ', 'been ']
        # for prefix in prefixes_to_remove:
        #     if normalized.startswith(prefix):
        #         normalized = normalized[len(prefix):]
        #         break
        #
        # # Clean up multiple spaces
        # normalized = ' '.join(normalized.split())
        #
        return normalized.strip()
    
    def _normalize_for_embedding(self, text: str, context_type: str = "relationship") -> str:
        """
        Prepare text for embedding with context to improve similarity.
        
        Args:
            text: The text to normalize
            context_type: Type of context ('relationship', 'category')
            
        Returns:
            Context-aware text for embedding
        """
        normalized = self._normalize_edge_name(text)
        
        if context_type == "relationship":
            return f"relationship type: {normalized}"
        elif context_type == "category":
            return f"category: {normalized}"
        else:
            return normalized
    
    def _get_original_edge_name(self, normalized_name: str) -> str:
        """
        Map normalized edge name back to original format.
        
        Args:
            normalized_name: The normalized edge name
            
        Returns:
            Original edge name or standardized version if not found
        """
        return self.normalized_to_original.get(normalized_name, normalized_name.upper().replace(' ', '_'))
    
    def _build_embedding_cache(self) -> None:
        """Build embedding cache for all categories and edges with normalization."""
        if not self.embedder:
            return
            
        logger.debug("Building normalized embedding cache...")
        
        # Build category embeddings
        self._build_category_embeddings()
        
        # Build edge embeddings by category
        self._build_edge_embeddings()
        
        logger.debug(f"Built embedding cache: {len(self.category_embeddings)} categories, "
                    f"{sum(len(edges) for edges in self.edge_embeddings.values())} edges")
    
    def _build_category_embeddings(self) -> None:
        """Create embeddings for normalized category names."""
        if not self.embedder:
            return
            
        categories = self.classifier_map.get_all_categories()
        
        for category in categories:
            # Normalize category name
            normalized_category = self._normalize_edge_name(category)
            
            # Store mapping
            self.normalized_to_original[normalized_category] = category
            
            # Create context-aware text for embedding
            embedding_text = self._normalize_for_embedding(category, "category")
            
            # Generate embedding
            try:
                embedding = self.embedder.encode([embedding_text])[0]
                self.category_embeddings[normalized_category] = embedding
                logger.debug(f"Created category embedding for: '{category}' -> '{normalized_category}'")
            except Exception as e:
                logger.warning(f"Failed to create embedding for category '{category}': {e}")
    
    def _build_edge_embeddings(self) -> None:
        """Create embeddings for normalized edge names within each category."""
        if not self.embedder:
            return
            
        for category in self.classifier_map.get_all_categories():
            normalized_category = self._normalize_edge_name(category)
            self.edge_embeddings[normalized_category] = {}
            
            edges = self.classifier_map.get_edges_by_classifier(category)
            
            for edge in edges:
                # Normalize edge name
                normalized_edge = self._normalize_edge_name(edge)
                
                # Store mapping
                self.normalized_to_original[normalized_edge] = edge
                
                # Create context-aware text for embedding
                embedding_text = self._normalize_for_embedding(edge, "relationship")
                
                # Generate embedding
                try:
                    embedding = self.embedder.encode([embedding_text])[0]
                    self.edge_embeddings[normalized_category][normalized_edge] = embedding
                    logger.debug(f"Created edge embedding for: '{edge}' -> '{normalized_edge}' in '{category}'")
                except Exception as e:
                    logger.warning(f"Failed to create embedding for edge '{edge}': {e}")
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Reshape for sklearn cosine_similarity
            emb1 = embedding1.reshape(1, -1)
            emb2 = embedding2.reshape(1, -1)
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            
            # Convert to 0-1 range (cosine similarity is -1 to 1)
            return (similarity + 1) / 2
            
        except Exception as e:
            logger.warning(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def refresh_classifier_map(self) -> None:
        """Refresh the classifier map from Neo4j and rebuild embedding cache."""
        self.classifier_map.refresh()
        
        # Rebuild embedding cache with updated data
        if self.embedder:
            self.category_embeddings.clear()
            self.edge_embeddings.clear()
            self.normalized_to_original.clear()
            self._build_embedding_cache()