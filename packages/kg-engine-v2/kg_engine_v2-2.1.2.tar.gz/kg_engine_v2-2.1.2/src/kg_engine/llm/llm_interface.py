"""
LLM interface for Knowledge Graph Engine v2
"""
import json
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from ..models import ExtractedInfo, ParsedQuery, SearchType
from ..utils import DateParser

DEFAULT_MODEL = "gpt-4.1-nano"  # Default model for OpenAI
class LLMInterface:
    """Interface for LLM-powered entity and relationship extraction"""
    
    def __init__(self, api_key: str = "ollama", model: str = DEFAULT_MODEL, base_url: str = None, bearer_token: str = None):
        # Support for Ollama and OpenAI
        if base_url or api_key == "ollama":
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
                    api_key=api_key,
                    default_headers={"Authorization": f"Bearer {bearer_token}"}
                )
            else:
                # Use standard API key authentication
                self.client = OpenAI(api_key=api_key)
            self.model = model
            
        self.date_parser = DateParser()
        print(f"🤖 LLM Interface initialized: {self.model} via {base_url or 'OpenAI'}")
    
    def extract_entities_relationships(self, text: str) -> List[ExtractedInfo]:
        """Extract entities and relationships from text using LLM"""
        
        # First extract dates
        extracted_date, clean_text = self.date_parser.extract_date_from_text(text)
        
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

Examples:
"Emma speaks English" -> 
[{{
  "subject": "Emma",
  "relationship": "SPEAKS",
  "object": "English", 
  "summary": "Emma speaks English",
  "is_negation": false,
  "confidence": 0.95
}}]

"Company A was founded" ->
[{{
  "subject": "Company A",
  "relationship": "HAS_STATUS",
  "object": "founded",
  "summary": "Company A was founded",
  "is_negation": false,
  "confidence": 0.9
}}]

"Project X began" ->
[{{
  "subject": "Project X",
  "relationship": "HAS_STATUS",
  "object": "active",
  "summary": "Project X began",
  "is_negation": false,
  "confidence": 0.9
}}]

"Company B started operations" ->
[{{
  "subject": "Company B",
  "relationship": "HAS_STATUS",
  "object": "operational",
  "summary": "Company B started operations",
  "is_negation": false,
  "confidence": 0.9
}}]

"John moved to Paris from London" ->
[{{
  "subject": "John",
  "relationship": "LIVES_IN", 
  "object": "Paris",
  "summary": "John lives in Paris",
  "is_negation": false,
  "confidence": 0.9
}},
{{
  "subject": "John",
  "relationship": "MOVED_FROM",
  "object": "London", 
  "summary": "John moved from London",
  "is_negation": false,
  "confidence": 0.85
}}]

"Emma no longer works at TechCorp" ->
[{{
  "subject": "Emma",
  "relationship": "WORKS_AT",
  "object": "TechCorp",
  "summary": "Emma no longer works at TechCorp", 
  "is_negation": true,
  "confidence": 0.9
}}]

Text to analyze: "{clean_text}"

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
                    confidence=rel.get('confidence', 1.0)
                )
                extracted.append(info)
            
            return extracted
            
        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            return self._fallback_extraction(clean_text)
    
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
- search_type: "direct" for exact graph matches, "semantic" for similarity search, "both" for hybrid
- query_intent: "search", "count", "exists", "list", "compare"
- temporal_context: null or "current", "historical", "all"

Examples:

"Where does Emma live?" ->
{{
  "entities": ["Emma"],
  "relationships": ["LIVES_IN", "RESIDES_IN"],
  "search_type": "both", 
  "query_intent": "search",
  "temporal_context": "current"
}}

"Who works at TechCorp?" ->
{{
  "entities": ["TechCorp"],
  "relationships": ["WORKS_AT", "EMPLOYED_BY"],
  "search_type": "both",
  "query_intent": "list", 
  "temporal_context": "current"
}}

"What languages does John speak?" ->
{{
  "entities": ["John"],
  "relationships": ["SPEAKS", "LANGUAGE"],
  "search_type": "both",
  "query_intent": "list",
  "temporal_context": "current"
}}

Return only valid JSON, no other text:
"""
        
        try:
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
                    return self._fallback_query_parse(query)
            
            return ParsedQuery(
                entities=parsed.get('entities', []),
                relationships=parsed.get('relationships', []),
                search_type=SearchType(parsed.get('search_type', 'both')),
                query_intent=parsed.get('query_intent', 'search'),
                temporal_context=parsed.get('temporal_context')
            )
            
        except Exception as e:
            print(f"Error in query parsing: {e}")
            return self._fallback_query_parse(query)
    
    def generate_answer(self, query: str, search_results: List[Dict]) -> str:
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
    
    def _fallback_query_parse(self, query: str) -> ParsedQuery:
        """Simple fallback query parsing"""
        query_lower = query.lower()
        
        entities = []
        relationships = []
        
        # Extract capitalized words as potential entities
        words = query.split()
        for word in words:
            clean_word = word.strip('?.,!')
            if clean_word[0].isupper() and len(clean_word) > 1:
                entities.append(clean_word)
        
        # Infer relationships from question patterns
        if "where" in query_lower and "live" in query_lower:
            relationships = ["LIVES_IN", "RESIDES_IN"]
        elif "work" in query_lower:
            relationships = ["WORKS_AT", "WORKS_AS", "EMPLOYED_BY"]
        elif "speak" in query_lower:
            relationships = ["SPEAKS", "LANGUAGE"]
        
        return ParsedQuery(
            entities=entities,
            relationships=relationships,
            search_type=SearchType.BOTH,
            query_intent="search"
        )