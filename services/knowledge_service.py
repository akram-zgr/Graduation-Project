from models.knowledge_base import KnowledgeBase
from models.university import University
from difflib import SequenceMatcher
from typing import List, Dict, Optional
import re

class KnowledgeService:
    """Service for managing and retrieving university-specific knowledge"""
    
    def __init__(self):
        pass
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text for searching"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity score"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def search_knowledge(self, query: str, university_id: int, department_id: int = None, limit: int = 5) -> List[Dict]:
        """
        Search knowledge base for relevant information with hierarchical filtering
        Priority: Department-specific -> University-specific -> Global
        
        Args:
            query: Search query
            university_id: University ID to filter by
            department_id: Optional department ID for department-specific knowledge
            limit: Maximum number of results
        
        Returns:
            List of relevant knowledge entries with relevance scores
        """
        if not university_id:
            return []
        
        # Get knowledge entries with priority:
        # 1. Department-specific (if department_id provided)
        # 2. University-specific (department_id is NULL)
        entries_query = KnowledgeBase.query.filter_by(
            university_id=university_id,
            is_active=True
        )
        
        # Get all entries for this university
        all_entries = entries_query.all()
        
        if not all_entries:
            return []
        
        # Separate by priority level
        dept_entries = []
        uni_entries = []
        
        for entry in all_entries:
            if department_id and entry.department_id == department_id:
                dept_entries.append(entry)
            elif entry.department_id is None:
                uni_entries.append(entry)
        
        # Process department entries first, then university entries
        query_lower = self._preprocess_text(query)
        results = []
        
        # Helper function to score entries
        def score_entry(entry):
            # Calculate relevance score
            title_score = self._calculate_similarity(query_lower, self._preprocess_text(entry.title))
            content_score = self._calculate_similarity(query_lower, self._preprocess_text(entry.content[:500]))
            
            # Check for keyword matches
            keywords = entry.tags.split(',') if entry.tags else []
            keyword_matches = sum(1 for keyword in keywords if keyword.strip().lower() in query_lower)
            keyword_score = min(keyword_matches * 0.2, 1.0)
            
            # Combined score with priority weighting
            combined_score = (
                (title_score * 0.4) +
                (content_score * 0.3) +
                (keyword_score * 0.2) +
                (entry.priority / 10 * 0.1)
            )
            
            return combined_score
        
        # Score department entries first (higher priority)
        for entry in dept_entries:
            score = score_entry(entry)
            if score > 0.2:  # Threshold
                results.append({
                    'entry': entry,
                    'score': score + 0.3,  # Boost department-specific results
                    'title': entry.title,
                    'content': entry.content,
                    'content_ar': entry.content_ar,
                    'category': entry.category,
                    'source_url': entry.source_url,
                    'priority': entry.priority,
                    'scope': 'department'
                })
        
        # Score university entries
        for entry in uni_entries:
            score = score_entry(entry)
            if score > 0.2:
                results.append({
                    'entry': entry,
                    'score': score,
                    'title': entry.title,
                    'content': entry.content,
                    'content_ar': entry.content_ar,
                    'category': entry.category,
                    'source_url': entry.source_url,
                    'priority': entry.priority,
                    'scope': 'university'
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_knowledge_by_category(self, university_id: int, category: str) -> List[Dict]:
        """Get all knowledge entries for a specific category"""
        entries = KnowledgeBase.query.filter_by(
            university_id=university_id,
            category=category,
            is_active=True
        ).order_by(KnowledgeBase.priority.desc()).all()
        
        return [entry.to_dict() for entry in entries]
    
    def get_all_categories(self, university_id: int) -> List[str]:
        """Get all unique categories for a university"""
        result = KnowledgeBase.query.filter_by(
            university_id=university_id,
            is_active=True
        ).with_entities(KnowledgeBase.category).distinct().all()
        
        return [r[0] for r in result if r[0]]
    
    def add_knowledge(self, university_id: int, title: str, content: str,
                     category: str = None, tags: str = None, 
                     content_ar: str = None, source_url: str = None,
                     priority: int = 5, created_by: int = None, department_id: int = None) -> KnowledgeBase:
        """Add new knowledge entry"""
        from extensions import db
        
        entry = KnowledgeBase(
            university_id=university_id,
            department_id=department_id,
            title=title,
            content=content,
            content_ar=content_ar,
            category=category,
            tags=tags,
            source_url=source_url,
            priority=priority,
            created_by=created_by
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return entry
    
    def update_knowledge(self, entry_id: int, **kwargs) -> Optional[KnowledgeBase]:
        """Update existing knowledge entry"""
        from extensions import db
        
        entry = KnowledgeBase.query.get(entry_id)
        if not entry:
            return None
        
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        db.session.commit()
        return entry
    
    def delete_knowledge(self, entry_id: int) -> bool:
        """Soft delete knowledge entry"""
        from extensions import db
        
        entry = KnowledgeBase.query.get(entry_id)
        if not entry:
            return False
        
        entry.is_active = False
        db.session.commit()
        return True
    
    def get_university_context(self, university_id: int) -> str:
        """
        Generate a context summary for the university
        Used to provide context to the AI
        """
        university = University.query.get(university_id)
        if not university:
            return ""
        
        context = f"University: {university.name}"
        if university.name_ar:
            context += f" ({university.name_ar})"
        
        if university.city:
            context += f"\nLocation: {university.city}"
        
        if university.website:
            context += f"\nWebsite: {university.website}"
        
        # Get top knowledge categories
        categories = self.get_all_categories(university_id)
        if categories:
            context += f"\nAvailable information categories: {', '.join(categories[:5])}"
        
        return context


# Create singleton instance
knowledge_service = KnowledgeService()
