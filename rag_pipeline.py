"""
Main RAG Pipeline for Instructional Design System
Orchestrates document processing, vector search, content generation, and file creation
"""

import os
import json
import tempfile
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
import re

from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from content_generator import InstructionalContentGenerator
from file_generators import PowerPointGenerator, PDFGenerator


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstructionalDesignRAG:
    """Main RAG pipeline for instructional design content generation"""
    
    def __init__(self, 
                 storage_dir: str = "storage",
                 model_name: str = "nomic-embed-text",
                 ollama_url: Optional[str] = None):
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.doc_processor = DocumentProcessor(str(self.storage_dir / "uploads"))
        self.vector_store = VectorStoreManager(
            model_name=model_name,
            persist_directory=str(self.storage_dir / "vector_db"),
            ollama_url=ollama_url
        )
        self.content_generator = InstructionalContentGenerator()
        self.ppt_generator = PowerPointGenerator()
        self.pdf_generator = PDFGenerator()
        
        # Output directories
        self.outputs_dir = self.storage_dir / "outputs"
        self.outputs_dir.mkdir(exist_ok=True)
        
        logger.info("Instructional Design RAG pipeline initialized")
    
    def upload_document(self, file_path: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload and process a document for the knowledge base
        
        Args:
            file_path: Path to the file to upload
            file_name: Optional custom filename
            
        Returns:
            Processing result with document ID and metadata
        """
        try:
            # Copy file to uploads directory if not already there
            if not file_path.startswith(str(self.storage_dir / "uploads")):
                upload_path = self.storage_dir / "uploads" / (file_name or Path(file_path).name)
                shutil.copy2(file_path, upload_path)
                file_path = str(upload_path)
            
            # Process document
            logger.info(f"Processing document: {file_path}")
            processed_doc = self.doc_processor.process_document(file_path)
            
            # Add to vector store
            doc_id = self.vector_store.add_document(processed_doc)
            
            result = {
                'success': True,
                'document_id': doc_id,
                'filename': processed_doc['metadata']['filename'],
                'file_type': processed_doc['metadata']['file_type'],
                'content_length': processed_doc['metadata']['content_length'],
                'chunks_created': len(processed_doc['metadata']['chunks']),
                'message': f"Document '{processed_doc['metadata']['filename']}' processed successfully"
            }
            
            logger.info(f"Document processed: {doc_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to process document: {str(e)}"
            }
    
    def batch_upload_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Upload multiple documents in batch"""
        results = []
        
        for file_path in file_paths:
            result = self.upload_document(file_path)
            results.append(result)
        
        return results
    
    def generate_training_content(self, 
                                prompt: str,
                                output_format: str = 'ppt',
                                duration_minutes: int = 15,
                                learning_level: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate training content based on user prompt
        
        Args:
            prompt: User's request (e.g., "Create a 15-minute training on project management")
            output_format: 'ppt', 'pdf', or 'both'
            duration_minutes: Duration of the training
            learning_level: 'beginner', 'intermediate', or 'advanced'
            
        Returns:
            Result with generated file paths and metadata
        """
        try:
            # Extract topic from prompt
            topic = self._extract_topic_from_prompt(prompt)
            logger.info(f"Generating training content for topic: {topic}")
            
            # Search for relevant content
            search_query = f"{prompt} | {topic} instructional design"
            search_results = self.vector_store.semantic_search(
                query=search_query,
                context_type='training',
                n_results=12
            )
            
            if not search_results:
                return {
                    'success': False,
                    'error': 'No relevant content found in knowledge base',
                    'message': 'Please upload relevant documents first'
                }
            
            # Generate training module
            logger.info("Generating training module content")
            module_data = self.content_generator.generate_training_module(
                topic=topic,
                duration_minutes=duration_minutes,
                retrieved_content=search_results,
                learning_level=learning_level,
                format_type='presentation' if output_format in ['ppt', 'both'] else 'document'
            )
            
            # Generate output files
            output_files = []
            
            if output_format in ['ppt', 'both']:
                ppt_path = self._generate_powerpoint(module_data, topic)
                if ppt_path:
                    output_files.append({
                        'type': 'powerpoint',
                        'path': ppt_path,
                        'filename': Path(ppt_path).name
                    })
            
            if output_format in ['pdf', 'both']:
                pdf_path = self._generate_pdf(module_data, topic)
                if pdf_path:
                    output_files.append({
                        'type': 'pdf',
                        'path': pdf_path,
                        'filename': Path(pdf_path).name
                    })
            
            result = {
                'success': True,
                'topic': topic,
                'duration_minutes': duration_minutes,
                'learning_level': learning_level,
                'output_files': output_files,
                'module_metadata': module_data['metadata'],
                'sources_used': len(search_results),
                'message': f"Training content generated successfully for '{topic}'"
            }
            
            logger.info(f"Training content generated successfully: {len(output_files)} files created")
            return result
            
        except Exception as e:
            logger.error(f"Error generating training content: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to generate training content: {str(e)}"
            }
    
    def _extract_topic_from_prompt(self, prompt: str) -> str:
        """Extract the main topic from user prompt"""
        # Simple topic extraction - in a real system, use more sophisticated NLP
        prompt_lower = prompt.lower()

        # Expanded stop word list to keep meaningful subject words
        stop_words = {
            'make', 'create', 'generate', 'training', 'course', 'lesson',
            'presentation', 'ppt', 'pdf', 'minutes', 'minute', 'hour', 'hours', 'on',
            'about', 'for', 'a', 'an', 'the', 'this', 'that', 'these', 'those', 'please',
            'kindly', 'could', 'would', 'should', 'need', 'with', 'into', 'and', 'to',
            'of', 'in', 'cover', 'covered', 'covering', 'focus', 'focusing',
            'develop', 'build', 'assemble', 'design', 'craft', 'master', 'class',
            'module', 'session', 'interactive', 'blended', 'minutes', 'minute',
            'masterclass'
        }

        def clean_topic_phrase(phrase: str) -> str:
            phrase = phrase.strip(" .:-")
            if not phrase:
                return ""

            # Remove trailing directives such as "with ..." or "including ..."
            for splitter in (' with ', ' including ', ' featuring ', ' plus ', ' and '):
                if splitter in phrase:
                    phrase = phrase.split(splitter, 1)[0]
            phrase = phrase.strip(" .:-")

            if not phrase:
                return ""

            tokens = [tok for tok in re.findall(r"\b[\w'-]+\b", phrase) if tok.lower() not in stop_words]
            if not tokens:
                tokens = re.findall(r"\b[\w'-]+\b", phrase)

            cleaned = ' '.join(tokens[:12]).strip()
            return cleaned.title()

        focus_patterns = [
            r'(?:on|about|regarding|covering|focused on|focusing on|featuring|highlighting|walks through|walking through|examining|exploring|around|concerning)\s+([^.,;]+)',
            r'(?:through|for)\s+([^.,;]+?)(?:\s+with|\s+including|\s+and|\s*$)'
        ]

        for pattern in focus_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                candidate = clean_topic_phrase(match.group(1))
                if candidate and len(candidate) >= 3:
                    return candidate

        tokens = []
        for raw_token in re.findall(r"\b[\w'-]+\b", prompt):
            token = raw_token.strip("'\"")
            lower_token = token.lower()

            if not token:
                continue

            if lower_token in stop_words:
                continue

            # Keep numeric hints like "3" or "2"
            tokens.append(token)

        if tokens:
            candidate = clean_topic_phrase(' '.join(tokens))
            if candidate and len(candidate) >= 3:
                return candidate

        # Final fallback
        fallback = clean_topic_phrase(prompt)
        return fallback or "General Training"
    
    def _generate_powerpoint(self, module_data: Dict[str, Any], topic: str) -> Optional[str]:
        """Generate PowerPoint presentation"""
        try:
            # Generate slides content
            slides_data = self.content_generator.generate_presentation_content(module_data)
            
            # Create output filename
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_topic.replace(' ', '_')}_training.pptx"
            output_path = str(self.outputs_dir / filename)
            
            # Generate PowerPoint
            ppt_path = self.ppt_generator.create_presentation(
                slides_data=slides_data,
                output_path=output_path,
                theme='professional'
            )
            
            logger.info(f"PowerPoint generated: {ppt_path}")
            return ppt_path
            
        except Exception as e:
            logger.error(f"Error generating PowerPoint: {str(e)}")
            return None
    
    def _generate_pdf(self, module_data: Dict[str, Any], topic: str) -> Optional[str]:
        """Generate PDF document"""
        try:
            # Create output filename
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_topic.replace(' ', '_')}_manual.pdf"
            output_path = str(self.outputs_dir / filename)
            
            # Generate PDF
            pdf_path = self.pdf_generator.create_training_manual(
                module_data=module_data,
                output_path=output_path,
                include_charts=True
            )
            
            logger.info(f"PDF generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
    
    def search_content(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for content in the knowledge base"""
        try:
            results = self.vector_store.search(query, n_results)
            
            return {
                'success': True,
                'query': query,
                'results': results['results'],
                'total_results': results['total_results']
            }
            
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Search failed: {str(e)}"
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            stats = self.vector_store.get_collection_stats()
            
            # Add additional information
            stats['upload_directory'] = str(self.storage_dir / "uploads")
            stats['outputs_directory'] = str(self.outputs_dir)
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the knowledge base"""
        try:
            success = self.vector_store.delete_document(document_id)
            
            if success:
                return {
                    'success': True,
                    'message': f"Document {document_id} deleted successfully"
                }
            else:
                return {
                    'success': False,
                    'message': f"Document {document_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to delete document: {str(e)}"
            }
    
    def list_documents(self) -> Dict[str, Any]:
        """List all documents in the knowledge base"""
        try:
            # Get documents by type to organize them
            all_docs = {}
            file_types = ['.pdf', '.docx', '.txt', '.xlsx', '.csv']
            
            for file_type in file_types:
                docs = self.vector_store.get_documents_by_type(file_type)
                if docs:
                    all_docs[file_type] = docs
            
            return {
                'success': True,
                'documents': all_docs,
                'total_documents': sum(len(docs) for docs in all_docs.values())
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_generated_files(self) -> List[Dict[str, Any]]:
        """Get list of generated training files"""
        try:
            files = []
            
            for file_path in self.outputs_dir.glob("*"):
                if file_path.is_file():
                    files.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'created': file_path.stat().st_mtime,
                        'type': file_path.suffix.lower()
                    })
            
            # Sort by creation time (newest first)
            files.sort(key=lambda x: x['created'], reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting generated files: {str(e)}")
            return []


def create_sample_rag_system():
    """Create a sample RAG system with example data"""
    
    # Initialize RAG system
    rag = InstructionalDesignRAG()
    
    # Create sample documents directory
    sample_docs_dir = Path("sample_documents")
    sample_docs_dir.mkdir(exist_ok=True)
    
    # Create sample instructional design documents
    sample_docs = {
        "adult_learning_principles.txt": """
Adult Learning Principles for Instructional Design

1. Adult Readiness to Learn
Adults are ready to learn when they perceive a need to know or do something to perform more effectively. This readiness is often triggered by real-life situations or work requirements.

2. Experiential Learning
Adults learn best when they can connect new information to their existing knowledge and experience. They bring a wealth of life experiences that serve as resources for learning.

3. Self-Direction
Adult learners prefer to take responsibility for their own learning. They want to be involved in planning and evaluating their learning experiences.

4. Problem-Centered Learning
Adults learn best when the content is problem-centered rather than subject-centered. They prefer learning that helps them solve immediate problems.

5. Internal Motivation
While adults respond to external motivators, internal motivators such as self-esteem, recognition, and better quality of life are more powerful.

Best Practices for Adult Learning:
- Create relevant, practical content
- Encourage participation and interaction
- Respect learners' experience and knowledge
- Provide immediate application opportunities
- Use varied instructional methods
- Create a supportive learning environment
""",

        "instructional_design_models.txt": """
Instructional Design Models and Frameworks

ADDIE Model:
- Analysis: Identify learning needs, goals, and audience characteristics
- Design: Create learning objectives, assessments, and instructional strategies
- Development: Create and produce learning materials and content
- Implementation: Deliver the instruction to learners
- Evaluation: Assess the effectiveness of the instruction

SAM (Successive Approximation Model):
- Preparation: Gather information and define project scope
- Iterative Design: Create prototypes and refine through cycles
- Iterative Development: Build and test small portions repeatedly

Bloom's Taxonomy:
- Remember: Recall facts and basic concepts
- Understand: Explain ideas or concepts
- Apply: Use information in new situations
- Analyze: Draw connections among ideas
- Evaluate: Justify a stand or decision
- Create: Produce new or original work

Gagne's Nine Events of Instruction:
1. Gain attention
2. Inform learners of objectives
3. Stimulate recall of prior learning
4. Present the content
5. Provide learning guidance
6. Elicit performance
7. Provide feedback
8. Assess performance
9. Enhance retention and transfer

Learning Objectives Guidelines:
- Use action verbs (Bloom's taxonomy)
- Be specific and measurable
- Include conditions and criteria
- Align with assessments and activities
""",

        "assessment_strategies.txt": """
Assessment Strategies in Instructional Design

Types of Assessments:

Formative Assessment:
- Conducted during the learning process
- Provides ongoing feedback
- Helps adjust instruction
- Examples: quizzes, polls, discussions, observations

Summative Assessment:
- Conducted at the end of instruction
- Measures learning achievement
- Examples: final exams, projects, portfolios

Authentic Assessment:
- Real-world applications
- Performance-based
- Examples: case studies, simulations, portfolios

Assessment Design Principles:
- Align with learning objectives
- Use varied assessment methods
- Provide clear criteria and rubrics
- Give timely and specific feedback
- Consider different learning styles

Question Types:
- Multiple choice: Quick assessment of knowledge
- True/false: Simple fact checking
- Short answer: Brief explanations
- Essay: Complex thinking and analysis
- Practical: Hands-on demonstration

Feedback Best Practices:
- Be specific and actionable
- Focus on the learning, not the learner
- Provide both positive and constructive feedback
- Offer suggestions for improvement
- Give feedback promptly
"""
    }
    
    # Write sample documents
    for filename, content in sample_docs.items():
        with open(sample_docs_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Upload sample documents to RAG system
    print("Setting up sample RAG system...")
    for filename in sample_docs.keys():
        file_path = str(sample_docs_dir / filename)
        result = rag.upload_document(file_path)
        print(f"Uploaded {filename}: {result['message']}")
    
    return rag


if __name__ == "__main__":
    # Demo usage
    rag = create_sample_rag_system()
    
    # Generate sample training content
    print("\nGenerating sample training content...")
    result = rag.generate_training_content(
        prompt="Create a 15-minute training module on adult learning principles",
        output_format='both',
        duration_minutes=15,
        learning_level='intermediate'
    )
    
    if result['success']:
        print(f"✓ Generated training content for: {result['topic']}")
        for file_info in result['output_files']:
            print(f"  - {file_info['type']}: {file_info['filename']}")
    else:
        print(f"✗ Error: {result['message']}")
    
    # Show knowledge base stats
    stats = rag.get_knowledge_base_stats()
    if stats['success']:
        print(f"\nKnowledge Base Stats:")
        print(f"  - Total chunks: {stats['stats']['total_chunks']}")
        print(f"  - Unique documents: {stats['stats']['unique_documents']}")
        print(f"  - File types: {stats['stats']['file_types']}")
