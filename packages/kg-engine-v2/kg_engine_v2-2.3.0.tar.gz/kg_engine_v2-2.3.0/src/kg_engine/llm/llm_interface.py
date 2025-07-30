"""
LLM interface for Knowledge Graph Engine v2
"""
import json
import re
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from ..models import ExtractedInfo, ParsedQuery, SearchType
# DateParser removed - using simple parse_date function instead
from ..utils.classifier_detector import ClassifierDetector
from ..models.classifier_map import ClassifierMap
import logging
DEFAULT_MODEL = "gpt-4o"

class LLMInterface:
    """Interface for LLM-powered entity and relationship extraction"""
    
    def __init__(self, api_key: str =None, model: Optional[str] =None, base_url: str = None, bearer_token: str = None, classifier_map: Optional[ClassifierMap] = None, embedder=None):
        # Support for Ollama and OpenAI
        if api_key == "ollama":
            # Use Ollama endpoint
            self.client = OpenAI(
                api_key="ollama",  # Ollama doesn't need a real API key
                base_url=base_url or "http://localhost:11434/v1"
            )
            # Default to a good lightweight model if using Ollama
            self.model = model if model != DEFAULT_MODEL else "llama3.2:3b"
        else:
            # Use OpenAI endpoint
            if bearer_token:
                # Use bearer token authentication
                self.client = OpenAI(
                    base_url=base_url,
                    api_key="dummy",
                    default_headers={"Authorization": f"Bearer {bearer_token}"}
                )
            else:
                # Use standard API key authentication
                self.client = OpenAI(api_key=api_key)
            self.model = model
            
        # Date parsing now handled by parse_date utility function
        self.classifier_detector = ClassifierDetector(classifier_map, embedder) if classifier_map else None
        print(f"🤖 LLM Interface initialized: {self.model} via {base_url or 'OpenAI'}")
    
    def extract_entities_relationships(self, text: str) -> List[ExtractedInfo]:
        """Extract entities and relationships from text using LLM"""
        
        extraction_prompt = f"""
Extract entities and relationships from the following text. 
Return a JSON array of relationships found.

Each relationship should have:
- subject: main entity (person, place, thing)
- relationship: action/state (use UPPERCASE_WITH_UNDERSCORES)
- object: target entity (for intransitive verbs or implicit objects, use the entity type or relevant noun)
- summary: brief natural language description
- is_negation: true if this negates/ends an existing fact
- confidence: 0.0-1.0 confidence score
- from_date: start date if mentioned (ISO format YYYY-MM-DD or null)
- to_date: end date if mentioned (ISO format YYYY-MM-DD or null)

Examples:
"Emma speaks English" -> 
[{{
  "subject": "Emma",
  "relationship": "SPEAKS",
  "object": "English", 
  "summary": "Emma speaks English",
  "is_negation": false,
  "confidence": 0.95,
  "from_date": null,
  "to_date": null
}}]

"Company A was founded" ->
[{{
  "subject": "Company A",
  "relationship": "HAS_STATUS",
  "object": "founded",
  "summary": "Company A was founded",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}}]

"Project X began" ->
[{{
  "subject": "Project X",
  "relationship": "HAS_STATUS",
  "object": "active",
  "summary": "Project X began",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}}]

"Company B started operations" ->
[{{
  "subject": "Company B",
  "relationship": "HAS_STATUS",
  "object": "operational",
  "summary": "Company B started operations",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}}]

"John moved to Paris from London" ->
[{{
  "subject": "John",
  "relationship": "LIVES_IN", 
  "object": "Paris",
  "summary": "John lives in Paris",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}},
{{
  "subject": "John",
  "relationship": "MOVED_FROM",
  "object": "London", 
  "summary": "John moved from London",
  "is_negation": false,
  "confidence": 0.85,
  "from_date": null,
  "to_date": null
}}]

"Emma no longer works at TechCorp" ->
[{{
  "subject": "Emma",
  "relationship": "WORKS_AT",
  "object": "TechCorp",
  "summary": "Emma no longer works at TechCorp", 
  "is_negation": true,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}}]

"Alice worked at Microsoft from 2020 to 2023" ->
[{{
  "subject": "Alice",
  "relationship": "WORKS_AT",
  "object": "Microsoft",
  "summary": "Alice worked at Microsoft from 2020 to 2023",
  "is_negation": false,
  "confidence": 0.95,
  "from_date": "2020-01-01",
  "to_date": "2023-12-31"
}}]

"Bob started at Google in January 2022" ->
[{{
  "subject": "Bob",
  "relationship": "WORKS_AT",
  "object": "Google",
  "summary": "Bob started at Google in January 2022",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": "2022-01-01",
  "to_date": null
}}]

Text to analyze: "{text}"

Return only valid JSON array, no other text:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from text. Always return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to get just the JSON
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            # Parse JSON response
            try:
                relationships = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    relationships = json.loads(json_match.group(0))
                else:
                    print(f"Failed to parse LLM response: {content}")
                    return []
            
            # Convert to ExtractedInfo objects
            extracted = []
            for rel in relationships:
                info = ExtractedInfo(
                    subject=rel['subject'],
                    relationship=rel['relationship'],
                    object=rel['object'],
                    summary=rel['summary'],
                    is_negation=rel.get('is_negation', False),
                    confidence=rel.get('confidence', 1.0),
                    from_date=rel.get('from_date'),
                    to_date=rel.get('to_date')
                )
                extracted.append(info)
            
            return extracted
            
        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            return self._fallback_extraction(text)
    
    def extract_entities_relationships_with_classifier(self, text: str) -> List[ExtractedInfo]:
        """
        Extract entities and relationships with classifier detection and edge standardization.
        
        This is the enhanced workflow that:
        1. Extracts triplets using LLM
        2. Detects categories for predicates
        3. Standardizes edge names
        4. Returns ExtractedInfo with category field populated
        
        Args:
            text: Input text to extract from
            
        Returns:
            List of ExtractedInfo with standardized relationships and categories
        """
        if not self.classifier_detector:
            # Fallback to regular extraction if no classifier detector
            return self.extract_entities_relationships(text)
        
        # Step 1: Extract triplets using regular LLM extraction
        extracted_infos = self.extract_entities_relationships(text)
        
        # Step 2: Classify and standardize relationships
        classified_infos = self.classifier_detector.detect_and_classify_relationships(extracted_infos)
        
        return classified_infos
    
    def parse_query(self, query: str, existing_relationships: List[str] = None) -> ParsedQuery:
        """Parse natural language query into structured search parameters"""
        
        if existing_relationships is None:
            existing_relationships = []
        
        query_prompt = f"""
Convert this natural language query into graph search parameters.
Available relationship types: {existing_relationships[:20]}  # Show first 20 to avoid token limits

Query: "{query}"

Return JSON with:
- entities: list of entity names mentioned or implied
- relationships: list of relationship types to search for  
- query_intent: "search", "count", "exists", "list", "compare"
- temporal_context: null or "current", "historical", "all"

Examples:

"Where does Emma live?" ->
{{
  "entities": ["Emma"],
  "relationships": ["LIVES_IN", "RESIDES_IN"],
  "query_intent": "search",
  "temporal_context": "current"
}}

"Who works at TechCorp?" ->
{{
  "entities": ["TechCorp"],
  "relationships": ["WORKS_AT", "EMPLOYED_BY"],
  "query_intent": "list", 
  "temporal_context": "current"
}}

"What languages does John speak?" ->
{{
  "entities": ["John"],
  "relationships": ["SPEAKS", "LANGUAGE"],
  "query_intent": "list",
  "temporal_context": "current"
}}

Return only valid JSON, no other text:
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at understanding search queries. Always return valid JSON."},
                {"role": "user", "content": query_prompt}
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()

        # Clean up response
        if content.startswith('```json'):
            content = content[7:-3].strip()
        elif content.startswith('```'):
            content = content[3:-3].strip()

        # Parse JSON
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
            else:
                logging.error(f"Failed to parse LLM query response: {content}")
                raise Exception(f"Failed to parse LLM query response: {content}")

        return ParsedQuery(
            entities=parsed.get('entities', []),
            relationships=parsed.get('relationships', []),
            search_type=SearchType.DIRECT, #(parsed.get('search_type', 'both')),
            query_intent=parsed.get('query_intent', 'search'),
            temporal_context=parsed.get('temporal_context')
        )
            

    
    def generate_answer(self, query: str, search_results: List[Union[Dict, str]]) -> str:
        """Generate natural language answer from search results"""
        
        if not search_results:
            return "I don't have information to answer that question."
        
        # Format results for LLM
        formatted_results = []
        for result in search_results[:5]:  # Limit to top 5 results
            if isinstance(result, dict):
                formatted_results.append(f"- {result.get('summary', 'No summary available')}")
            else:
                formatted_results.append(f"- {str(result)}")
        
        results_text = "\\n".join(formatted_results)
        
        answer_prompt = f"""
Based on the following search results, provide a clear, concise answer to the user's question.

Question: "{query}"

Search Results:
{results_text}

Guidelines:
- Be factual and direct
- If multiple answers exist, mention the most relevant ones
- If information is uncertain, say so
- Keep the answer conversational but informative
- Don't mention "search results" or "according to the data"

Answer:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on knowledge graph data."},
                    {"role": "user", "content": answer_prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            # Fallback to simple concatenation
            if search_results:
                first_result = search_results[0]
                if isinstance(first_result, dict):
                    return first_result.get('summary', 'Found relevant information.')
            return "I found some information but couldn't process it properly."
    
    def _fallback_extraction(self, text: str) -> List[ExtractedInfo]:
        """Simple fallback extraction using pattern matching"""
        extractions = []
        
        # Simple patterns for common relationships
        patterns = [
            (r'(.+?)\s+lives?\s+in\s+(.+)', "LIVES_IN", "lives in"),
            (r'(.+?)\s+resides?\s+in\s+(.+)', "LIVES_IN", "resides in"),
            (r'(.+?)\s+works?\s+at\s+(.+)', "WORKS_AT", "works at"),
            (r'(.+?)\s+works?\s+as\s+(.+)', "WORKS_AS", "works as"),
            (r'(.+?)\s+teaches?\s+at\s+(.+)', "TEACHES_AT", "teaches at"),
            (r'(.+?)\s+speaks?\s+(.+)', "SPEAKS", "speaks"),
            (r'(.+?)\s+born\s+in\s+(.+)', "BORN_IN", "born in"),
        ]
        
        # Patterns for intransitive/implicit object relationships
        intransitive_patterns = [
            (r'(.+?)\s+was\s+founded', "HAS_STATUS", "founded", "was founded"),
            (r'(.+?)\s+was\s+established', "HAS_STATUS", "established", "was established"),
            (r'(.+?)\s+started\s+operations', "HAS_STATUS", "operational", "started operations"),
            (r'(.+?)\s+began', "HAS_STATUS", "active", "began"),
            (r'(.+?)\s+occurred', "HAS_STATUS", "occurred", "occurred"),
            (r'(.+?)\s+ended', "HAS_STATUS", "ended", "ended"),
            (r'(.+?)\s+closed', "HAS_STATUS", "closed", "closed"),
        ]
        
        for pattern, rel_type, summary_template in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    subject, obj = match
                    extractions.append(ExtractedInfo(
                        subject=subject.strip(),
                        relationship=rel_type,
                        object=obj.strip(),
                        summary=f"{subject.strip()} {summary_template} {obj.strip()}",
                        confidence=0.7
                    ))
        
        # Handle intransitive patterns
        for pattern, rel_type, default_object, summary_template in intransitive_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = match
                extractions.append(ExtractedInfo(
                    subject=subject.strip(),
                    relationship=rel_type,
                    object=default_object,
                    summary=f"{subject.strip()} {summary_template}",
                    confidence=0.7
                ))
        
        return extractions
    
    def resolve_node_merge(self, node1_data: Dict[str, Any], node2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to intelligently resolve how to merge two nodes.
        
        Args:
            node1_data: First node's properties
            node2_data: Second node's properties
            
        Returns:
            Dictionary with merge decisions: name, metadata, confidence, reasoning
        """
        merge_prompt = f"""
Analyze these two nodes that represent the same entity and decide how to merge them optimally.

Node 1: {node1_data}
Node 2: {node2_data}

Return a JSON response with:
- merged_name: The best name for the merged node (choose most complete/formal)
- merged_metadata: Combined metadata with resolved conflicts
- confidence: 0.0-1.0 confidence in merge decisions
- reasoning: Brief explanation of decisions made
- name_source: "node1", "node2", or "combined" indicating name choice
- metadata_conflicts: List of any conflicting properties and how resolved

Guidelines:
- Choose the most complete, formal, or commonly used name
- Combine metadata intelligently (prefer more recent dates, higher quality data)
- For conflicts, choose the most reliable or recent information
- If names are very different, consider if they truly represent the same entity

Examples:

Input: Node 1: {{"name": "John Smith", "type": "Person", "email": "john@example.com"}}
       Node 2: {{"name": "J. Smith", "type": "Person", "phone": "555-1234"}}

Output: {{
  "merged_name": "John Smith",
  "merged_metadata": {{
    "type": "Person",
    "email": "john@example.com", 
    "phone": "555-1234"
  }},
  "confidence": 0.95,
  "reasoning": "Full name 'John Smith' is more complete than 'J. Smith'. Combined contact information.",
  "name_source": "node1",
  "metadata_conflicts": []
}}

Return only valid JSON:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at intelligent data merging. Always return valid JSON."},
                    {"role": "user", "content": merge_prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to get just the JSON
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            # Parse JSON response
            try:
                merge_result = json.loads(content)
                return merge_result
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    merge_result = json.loads(json_match.group(0))
                    return merge_result
                else:
                    print(f"Failed to parse LLM merge response: {content}")
                    return self._fallback_merge_resolution(node1_data, node2_data)
            
        except Exception as e:
            print(f"Error in LLM merge resolution: {e}")
            return self._fallback_merge_resolution(node1_data, node2_data)
    
    def _fallback_merge_resolution(self, node1_data: Dict[str, Any], node2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback merge resolution when LLM fails.
        
        Args:
            node1_data: First node's properties
            node2_data: Second node's properties
            
        Returns:
            Basic merge result
        """
        # Simple fallback: choose longer name, combine metadata
        name1 = node1_data.get("name", "")
        name2 = node2_data.get("name", "")
        merged_name = name1 if len(name1) >= len(name2) else name2
        
        # Combine metadata
        merged_metadata = {}
        merged_metadata.update(node1_data)
        merged_metadata.update(node2_data)  # node2 overwrites conflicts
        merged_metadata.pop("name", None)  # Remove name from metadata
        
        return {
            "merged_name": merged_name,
            "merged_metadata": merged_metadata,
            "confidence": 0.5,  # Low confidence for fallback
            "reasoning": "Fallback merge: chose longer name, combined metadata",
            "name_source": "node1" if len(name1) >= len(name2) else "node2",
            "metadata_conflicts": ["Used fallback resolution due to LLM error"]
        }