"""
Content Generator for Instructional Design
Generates training materials based on retrieved content
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from collections import Counter


class InstructionalContentGenerator:
    """Generate instructional design content using RAG results"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # Template structures for different content types
        self.templates = {
            'training_module': {
                'sections': ['introduction', 'learning_objectives', 'content', 'activities', 'assessment', 'conclusion'],
                'duration_guide': {
                    '5_min': {'intro': 1, 'content': 3, 'activities': 0, 'assessment': 1},
                    '15_min': {'intro': 2, 'content': 8, 'activities': 3, 'assessment': 2},
                    '30_min': {'intro': 3, 'content': 15, 'activities': 8, 'assessment': 4},
                    '60_min': {'intro': 5, 'content': 30, 'activities': 18, 'assessment': 7},
                    '90_min': {'intro': 7, 'content': 45, 'activities': 25, 'assessment': 12}
                }
            },
            'assessment': {
                'types': ['multiple_choice', 'true_false', 'short_answer', 'scenario_based'],
                'difficulty_levels': ['beginner', 'intermediate', 'advanced']
            },
            'presentation': {
                'slide_types': ['title', 'content', 'bullet_points', 'image', 'quote', 'conclusion']
            }
        }

        # Common noise markers to suppress repeated legal disclaimers and boilerplate
        self.noise_signatures = {
            'confidentialtoamericanexpress',
            'identialtoamericanexpress',
            'cannotbesharedwiththirdparties',
            'cannotshared',
            'sharedthird',
            'thirdarties',
            'donotdistribute',
            'donotdis t',
            'withoutamericanexpresswrittenconsent',
            'withoutamerican',
            'forinternaluseonly',
            'allrightsreserved',
            'ndm_refresh_module2'
        }
    
    def generate_training_module(self, 
                               topic: str,
                               duration_minutes: int,
                               retrieved_content: List[Dict[str, Any]],
                               learning_level: str = 'intermediate',
                               format_type: str = 'presentation') -> Dict[str, Any]:
        """
        Generate a complete training module
        
        Args:
            topic: Training topic
            duration_minutes: Duration in minutes
            retrieved_content: Content from RAG search
            learning_level: beginner, intermediate, or advanced
            format_type: presentation, document, or interactive
            
        Returns:
            Structured training module content
        """
        
        # Determine duration category
        duration_key = self._get_duration_key(duration_minutes)
        duration_guide = self.templates['training_module']['duration_guide'][duration_key]
        
        # Extract and synthesize content from retrieved documents
        synthesized_content = self._synthesize_content(retrieved_content, topic)
        focus_topic_entries = self._select_focus_topics(synthesized_content, duration_minutes)
        synthesized_content['focus_topics'] = focus_topic_entries
        focus_topic_titles = [entry['title'] for entry in focus_topic_entries if entry.get('title')]
        
        # Generate module structure
        module = {
            'metadata': {
                'title': f"Training Module: {topic}",
                'duration_minutes': duration_minutes,
                'learning_level': learning_level,
                'format_type': format_type,
                'created_date': datetime.now().isoformat(),
                'estimated_slides': self._calculate_slides(duration_minutes, format_type),
                'focus_topics': focus_topic_titles,
                'source_documents': synthesized_content.get('source_files', [])
            },
            'learning_objectives': self._generate_learning_objectives(
                topic,
                learning_level,
                synthesized_content,
                duration_minutes
            ),
            'content_outline': self._create_content_outline(
                topic,
                duration_guide,
                synthesized_content,
                duration_minutes
            ),
            'detailed_content': self._generate_detailed_content(
                topic,
                synthesized_content,
                duration_guide,
                duration_minutes
            ),
            'activities': self._generate_activities(
                topic,
                duration_guide['activities'],
                duration_minutes,
                learning_level,
                focus_topic_titles
            ),
            'assessment': self._generate_assessment(
                topic,
                learning_level,
                synthesized_content,
                duration_minutes
            ),
            'resources': self._extract_resources(retrieved_content)
        }

        return module
    
    def generate_presentation_content(self, 
                                    module_data: Dict[str, Any],
                                    slide_style: str = 'professional') -> List[Dict[str, Any]]:
        """
        Generate slides content for presentation
        
        Args:
            module_data: Training module data
            slide_style: Visual style preference
            
        Returns:
            List of slide dictionaries
        """
        slides = []
        
        # Title slide
        slides.append({
            'slide_number': 1,
            'type': 'title',
            'title': module_data['metadata']['title'],
            'subtitle': f"Duration: {module_data['metadata']['duration_minutes']} minutes",
            'content': {
                'main_title': module_data['metadata']['title'],
                'subtitle': f"Learning Level: {module_data['metadata']['learning_level'].title()}",
                'duration': f"{module_data['metadata']['duration_minutes']} minutes",
                'date': datetime.now().strftime("%B %d, %Y")
            }
        })
        
        # Learning objectives slide
        slides.append({
            'slide_number': 2,
            'type': 'bullet_points',
            'title': 'Learning Objectives',
            'content': {
                'title': 'By the end of this module, you will be able to:',
                'bullet_points': module_data['learning_objectives']
            }
        })
        
        # Content slides
        slide_num = 3
        for section in module_data['detailed_content']:
            if section['type'] == 'main_content':
                # Create content slides
                content_slides = self._create_content_slides(section, slide_num)
                slides.extend(content_slides)
                slide_num += len(content_slides)
            
            elif section['type'] == 'activity':
                slides.append({
                    'slide_number': slide_num,
                    'type': 'activity',
                    'title': section['title'],
                    'content': section['content']
                })
                slide_num += 1
        
        # Assessment slide
        if module_data['assessment']:
            slides.append({
                'slide_number': slide_num,
                'type': 'assessment',
                'title': 'Knowledge Check',
                'content': module_data['assessment']
            })
            slide_num += 1
        
        # Conclusion slide
        slides.append({
            'slide_number': slide_num,
            'type': 'conclusion',
            'title': 'Summary & Next Steps',
            'content': {
                'key_takeaways': self._generate_key_takeaways(module_data),
                'next_steps': self._generate_next_steps(module_data),
                'resources': module_data['resources'][:3]  # Top 3 resources
            }
        })
        
        return slides
    
    def _synthesize_content(self, retrieved_content: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Synthesize retrieved content into coherent information"""
        
        # Combine all text content
        all_text = []
        source_files = []

        for doc_group in retrieved_content:
            source_files.append(doc_group['filename'])
            for chunk in doc_group['chunks']:
                all_text.append(chunk['text'])

        heading_candidates = self._extract_heading_candidates(retrieved_content)
        combined_text = ' '.join(all_text)

        # Extract key concepts and richer topic candidates
        key_concepts = self._extract_key_concepts(combined_text, topic)
        top_topics = self._derive_topics(combined_text, heading_candidates, key_concepts)

        # Identify main themes; fall back to topic titles when sentence themes are sparse
        themes = self._identify_themes(combined_text, topic)
        if not themes and top_topics:
            themes = [topic_info['summary'] for topic_info in top_topics if topic_info['summary']][:5]

        return {
            'combined_text': combined_text,
            'key_concepts': key_concepts,
            'themes': themes,
            'top_topics': top_topics,
            'source_files': list(set(source_files)),
            'content_length': len(combined_text)
        }

    def _determine_topic_count(self, duration_minutes: int) -> int:
        """Decide how many focus topics to highlight based on duration"""

        if duration_minutes <= 10:
            return 2
        if duration_minutes <= 20:
            return 3
        if duration_minutes <= 35:
            return 4
        if duration_minutes <= 60:
            return 5
        return 6

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def _is_noise_text(self, text: str) -> bool:
        if not text:
            return True

        compact = re.sub(r'[^a-z0-9]+', '', text.lower())
        for signature in self.noise_signatures:
            if signature and signature in compact:
                return True

        # Treat very short or heavily repeated tokens as noise
        tokens = [tok for tok in re.findall(r'\b\w+\b', text.lower()) if tok]
        if not tokens:
            return True

        unique_tokens = set(tokens)
        if len(unique_tokens) == 1 and len(tokens) > 1:
            return True

        if len(self._normalize_text(text)) <= 3:
            return True

        return False

    def _select_focus_topics(
        self,
        synthesized_content: Dict[str, Any],
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Pick the most relevant topic entries for the module length"""

        desired_count = self._determine_topic_count(duration_minutes)
        topic_entries = [
            entry for entry in synthesized_content.get('top_topics', [])
            if entry.get('title') and not self._is_noise_text(entry.get('title'))
        ]

        selected: List[Dict[str, Any]] = topic_entries[:desired_count]

        if len(selected) < desired_count:
            existing_titles = {entry['title'].lower() for entry in selected}
            for concept in synthesized_content.get('key_concepts', []):
                normalized = concept.lower()
                if normalized in existing_titles or self._is_noise_text(concept):
                    continue
                selected.append({
                    'title': concept,
                    'summary': '',
                    'sentences': []
                })
                existing_titles.add(normalized)
                if len(selected) >= desired_count:
                    break

        return selected

    def _extract_heading_candidates(self, retrieved_content: List[Dict[str, Any]], max_candidates: int = 20) -> List[str]:
        """Detect potential section headings from retrieved chunks"""

        candidates: List[str] = []
        seen: set[str] = set()

        for doc_group in retrieved_content:
            for chunk in doc_group.get('chunks', []):
                for raw_line in chunk['text'].splitlines():
                    stripped = raw_line.strip()

                    if not stripped or len(stripped) > 120:
                        continue

                    cleaned = re.sub(r'^[\d\-\.\)]+\s*', '', stripped)
                    cleaned = cleaned.strip(':-•* ')

                    if len(cleaned) < 4:
                        continue

                    normalized = cleaned.lower()
                    if normalized in seen:
                        continue

                    heading_like = (
                        stripped.isupper()
                        or bool(re.match(r'^\d+([\.\)])?\s', stripped))
                        or bool(re.match(r'^(topic|lesson|section|module|step|part|chapter)\b', normalized))
                    )

                    if heading_like and not self._is_noise_text(cleaned):
                        candidates.append(cleaned)
                        seen.add(normalized)

                        if len(candidates) >= max_candidates:
                            return candidates

        return candidates

    def _derive_topics(
        self,
        text: str,
        heading_candidates: List[str],
        key_concepts: List[str],
        max_topics: int = 8
    ) -> List[Dict[str, Any]]:
        """Build a ranked list of topics with supporting context"""

        sentences = self._split_into_sentences(text)
        topics: List[Dict[str, Any]] = []
        seen: set[str] = set()

        def add_topic(title: str) -> bool:
            cleaned_title = self._normalize_text(title)
            if not cleaned_title:
                return False

            normalized = cleaned_title.lower()
            if normalized in seen:
                return False

            if self._is_noise_text(cleaned_title):
                return False

            supporting = self._collect_supporting_sentences(cleaned_title, sentences)
            if not supporting and sentences:
                for sentence in sentences:
                    cleaned_sentence = sentence.strip()
                    if cleaned_sentence and not self._is_noise_text(cleaned_sentence):
                        supporting = [cleaned_sentence]
                        break

            if not supporting:
                return False

            summary = ' '.join(supporting).strip()
            topics.append({
                'title': cleaned_title,
                'sentences': supporting,
                'summary': summary
            })
            seen.add(normalized)
            return True

        for heading in heading_candidates:
            if add_topic(heading) and len(topics) >= max_topics:
                return topics

        for concept in key_concepts:
            if len(topics) >= max_topics:
                break
            add_topic(concept)

        if not topics and sentences:
            topics.append({
                'title': 'Overview',
                'sentences': sentences[:2],
                'summary': ' '.join(sentences[:2]).strip()
            })

        return topics

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""

        if not text:
            return []

        raw_sentences = re.split(r'(?<=[.!?])\s+', text)
        return [sentence.strip() for sentence in raw_sentences if sentence.strip()]

    def _collect_supporting_sentences(
        self,
        topic: str,
        sentences: List[str],
        max_sentences: int = 2
    ) -> List[str]:
        """Return representative sentences mentioning the topic"""

        keywords = [kw for kw in re.findall(r'\b\w+\b', topic.lower()) if len(kw) > 2]
        if not keywords:
            keywords = [topic.lower()]

        collected: List[str] = []

        for sentence in sentences:
            lowered = sentence.lower()

            if any(keyword in lowered for keyword in keywords):
                cleaned = sentence.strip()
                if cleaned and not self._is_noise_text(cleaned) and cleaned not in collected:
                    collected.append(cleaned)

            if len(collected) >= max_sentences:
                break

        return collected

    def _extract_key_concepts(self, text: str, topic: str) -> List[str]:
        """Extract key concepts from text using simple NLP"""

        if not text:
            return []

        # Tokenize text
        tokens = re.findall(r'\b[a-zA-Z][\w-]*\b', text)
        stop_words = {
            'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'your', 'their',
            'have', 'has', 'been', 'will', 'shall', 'should', 'would', 'could', 'might',
            'can', 'are', 'were', 'was', 'is', 'be', 'being', 'been', 'using', 'use',
            'about', 'around', 'over', 'through', 'between', 'among', 'after', 'before',
            'training', 'module', 'course', 'lesson', 'presentation', 'section', 'topic',
            'chapter', 'learning', 'minutes', 'minute', 'hour', 'hours'
        }

        filtered_tokens = [token for token in tokens if token.lower() not in stop_words and len(token) > 2]

        # Count individual words and bigrams
        word_counter = Counter()
        bigram_counter = Counter()

        for token in filtered_tokens:
            normalized = token.lower()
            if normalized != topic.lower():
                word_counter[token.title()] += 1

        for first, second in zip(filtered_tokens, filtered_tokens[1:]):
            if first.lower() in stop_words or second.lower() in stop_words:
                continue
            bigram = f"{first} {second}".title()
            bigram_counter[bigram] += 1

        # Include proper nouns (keeps original formatting like "American Express")
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for noun in proper_nouns:
            cleaned = noun.strip()
            if cleaned and cleaned.lower() != topic.lower():
                word_counter[cleaned] += 1

        concepts: List[str] = []
        seen: set[str] = set()

        for phrase, _ in bigram_counter.most_common(12):
            normalized = phrase.lower()
            if normalized in seen:
                continue
            if self._is_noise_text(phrase):
                continue
            cleaned_phrase = self._normalize_text(phrase)
            concepts.append(cleaned_phrase)
            seen.add(normalized)
            if len(concepts) >= 10:
                return concepts

        for word, _ in word_counter.most_common(20):
            normalized = word.lower()
            if normalized in seen:
                continue
            if self._is_noise_text(word):
                continue
            cleaned_word = self._normalize_text(word)
            concepts.append(cleaned_word)
            seen.add(normalized)
            if len(concepts) >= 10:
                break

        return concepts
    
    def _identify_themes(self, text: str, topic: str) -> List[str]:
        """Identify main themes in the content"""
        
        # Simple theme identification based on sentence patterns
        sentences = text.split('.')
        
        themes = []
        theme_keywords = ['principle', 'method', 'approach', 'strategy', 'technique', 'process', 'step']
        
        for sentence in sentences:
            for keyword in theme_keywords:
                if keyword in sentence.lower() and len(sentence.strip()) > 20:
                    theme = sentence.strip()[:100] + '...' if len(sentence) > 100 else sentence.strip()
                    if theme not in themes:
                        themes.append(theme)
                    break
        
        return themes[:5]  # Top 5 themes
    
    def _get_duration_key(self, minutes: int) -> str:
        """Get duration category key"""
        if minutes <= 5:
            return '5_min'
        elif minutes <= 15:
            return '15_min'
        elif minutes <= 30:
            return '30_min'
        elif minutes <= 60:
            return '60_min'
        elif minutes <= 90 and '90_min' in self.templates['training_module']['duration_guide']:
            return '90_min'
        else:
            # Fallback to the largest configured duration bucket
            available = self.templates['training_module']['duration_guide']
            if '90_min' in available:
                return '90_min'
            return '60_min'
    
    def _calculate_slides(self, duration_minutes: int, format_type: str) -> int:
        """Calculate estimated number of slides"""
        if format_type == 'presentation':
            # Scale slides with duration while keeping an upper bound
            estimated = int(duration_minutes * 0.6) + 3
            return max(5, min(estimated, 50))
        return 0
    
    def _generate_learning_objectives(
        self,
        topic: str,
        level: str,
        content: Dict[str, Any],
        duration_minutes: int
    ) -> List[str]:
        """Generate learning objectives based on surfaced topics and level"""

        focus_topics = [
            entry['title']
            for entry in (content.get('focus_topics') or content.get('top_topics', []))
            if entry.get('title')
        ]
        if not focus_topics:
            focus_topics = [topic]

        objectives: List[str] = []

        # Core objectives anchored to the surfaced topics
        objectives.append(f"Summarize the key insights from {focus_topics[0]}.")

        if len(focus_topics) > 1:
            objectives.append(
                f"Compare how {focus_topics[1]} relates to {focus_topics[0]} within the module context."
            )

        if len(focus_topics) > 2:
            objectives.append(
                f"Prioritize takeaways from {', '.join(focus_topics[:3])} for learner application."
            )

        # Level-specific emphasis
        if level == 'beginner':
            objectives.append(f"Define essential terminology associated with {focus_topics[0]}.")
        elif level == 'intermediate':
            objectives.append(f"Apply {focus_topics[0]} in scenario-based discussions.")
        elif level == 'advanced':
            objectives.append(f"Design an implementation approach that leverages {focus_topics[0]}.")

        if duration_minutes >= 45:
            objectives.append(
                f"Facilitate extended practice sessions that reinforce {focus_topics[0]} and related themes."
            )

        objectives.append(f"Connect the documented practices to your organization’s instructional goals.")

        unique_objectives: List[str] = []
        seen: set[str] = set()

        for objective in objectives:
            normalized = objective.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_objectives.append(objective)

        return unique_objectives[:5]
    
    def _create_content_outline(
        self,
        topic: str,
        duration_guide: Dict,
        content: Dict[str, Any],
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Create content outline based on surfaced topics and duration"""

        focus_topics = [
            entry['title']
            for entry in (content.get('focus_topics') or content.get('top_topics', []))
            if entry.get('title')
        ]
        if not focus_topics:
            focus_topics = content.get('key_concepts', [])[:5] or [topic]

        intro_focus = ', '.join(focus_topics[:3])
        core_points = focus_topics[:min(3, len(focus_topics))]
        extended_points = focus_topics[min(3, len(focus_topics)):]

        outline = [
            {
                'section': 'Introduction',
                'duration_minutes': duration_guide['intro'],
                'key_points': [
                    f"Module focus: {intro_focus}",
                    "Why these themes matter for learners",
                    f"Session roadmap for {duration_minutes} minutes"
                ]
            },
            {
                'section': 'Core Content',
                'duration_minutes': duration_guide['content'],
                'key_points': core_points or focus_topics[:5]
            }
        ]

        if extended_points:
            outline.append({
                'section': 'Extended Applications',
                'duration_minutes': max(5, duration_guide['content'] // 2),
                'key_points': extended_points[:4]
            })

        if duration_guide['activities'] > 0:
            outline.append({
                'section': 'Interactive Activities',
                'duration_minutes': duration_guide['activities'],
                'key_points': [
                    f"Apply {focus_topics[0]} in a scenario" if focus_topics else "Hands-on practice",
                    "Group discussion",
                    "Case study analysis"
                ]
            })

        outline.append({
            'section': 'Assessment & Wrap-up',
            'duration_minutes': duration_guide['assessment'],
            'key_points': [
                "Knowledge check",
                "Key takeaways",
                "Next steps"
            ]
        })

        return outline
    
    def _generate_detailed_content(
        self,
        topic: str,
        content: Dict[str, Any],
        duration_guide: Dict,
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Generate detailed content sections grounded in retrieved topics"""

        detailed_content: List[Dict[str, Any]] = []

        focus_topics = [
            entry for entry in (content.get('focus_topics') or content.get('top_topics', []))
            if entry.get('title') and not self._is_noise_text(entry['title'])
        ]
        focus_titles = [entry['title'] for entry in focus_topics]

        def shorten(text: str, limit: int = 180) -> str:
            text = text.strip()
            if len(text) <= limit:
                return text
            truncated = text[:limit].rsplit(' ', 1)[0]
            return f"{truncated}…"

        # Introduction section highlights surfaced topics
        intro_summary = ', '.join(focus_titles[:3]) if focus_titles else topic
        detailed_content.append({
            'type': 'introduction',
            'title': f"Introduction to {topic}",
            'duration_minutes': duration_guide['intro'],
            'content': {
                'overview': f"This module spotlights {intro_summary} drawn from the uploaded materials.",
                'importance': f"These themes shape the guidance presented for {topic}.",
                'preview': "We'll examine documented practices, examples, and discussion points to help learners apply them."
            }
        })

        topics_to_use = focus_topics
        if not topics_to_use:
            topics_to_use = [
                {
                    'title': concept,
                    'summary': '',
                    'sentences': []
                }
                for concept in content.get('key_concepts', [])[:3]
            ]

        content_sections = max(1, len(topics_to_use))
        content_per_topic = max(2, duration_guide['content'] // content_sections) if duration_guide['content'] else 2
        max_examples = max(2, min(6, 2 + duration_minutes // 20))

        for topic_info in topics_to_use:
            title = topic_info.get('title') or topic
            sentences = topic_info.get('sentences', [])
            summary = topic_info.get('summary') or (sentences[0] if sentences else f"Overview of {title}.")

            example_points: List[str] = []
            for sentence in sentences:
                if len(example_points) >= max_examples:
                    break
                cleaned_sentence = shorten(sentence)
                if self._is_noise_text(cleaned_sentence):
                    continue
                if cleaned_sentence in example_points:
                    continue
                example_points.append(cleaned_sentence)

            if not example_points:
                example_points = [
                    f"Highlight where {title} appears in the workflow described in the module.",
                    f"Capture learner-facing guidance related to {title}."
                ]

            best_practices = [
                f"Connect {title} back to real scenarios highlighted in the module materials.",
                f"Invite participants to discuss how {title} appears in their context.",
                f"Document success indicators for applying {title} effectively."
            ]
            if duration_minutes >= 45:
                best_practices.append(
                    f"Facilitate peer review or coaching moments centered on {title}."
                )

            detailed_content.append({
                'type': 'main_content',
                'title': title,
                'duration_minutes': content_per_topic,
                'content': {
                    'theme': title,
                    'explanation': shorten(summary),
                    'examples': example_points,
                    'best_practices': best_practices
                }
            })

        # Activities if time allows
        if duration_guide['activities'] > 0:
            focus_reference = focus_titles[0] if focus_titles else topic
            detailed_content.append({
                'type': 'activity',
                'title': f"Hands-on Activity: {focus_reference} in Practice",
                'duration_minutes': duration_guide['activities'],
                'content': {
                    'activity_type': 'group_exercise',
                    'instructions': [
                        f"Review the documentation excerpts related to {focus_reference}.",
                        "Identify challenges or opportunities described.",
                        "Draft actions learners can take to address them."
                    ],
                    'materials_needed': ["Excerpt handout", "Discussion guide"],
                    'expected_outcome': f"Participants outline how {focus_reference} applies to their work."
                }
            })

        return detailed_content
    
    def _generate_activities(
        self,
        topic: str,
        segment_minutes: int,
        total_minutes: int,
        level: str,
        focus_topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate interactive activities"""
        
        if segment_minutes == 0:
            return []
        
        activities = []
        primary_topics = focus_topics or [topic]
        max_activities = 1
        if segment_minutes >= 10:
            max_activities = 2
        if segment_minutes >= 20:
            max_activities = 3

        activity_topics = [title for title in primary_topics if not self._is_noise_text(title)][:max_activities]
        if not activity_topics:
            activity_topics = [topic]
        per_activity_minutes = max(3, segment_minutes // max(1, len(activity_topics)))

        for index, focus_title in enumerate(activity_topics):
            if level == 'beginner':
                if index == 0:
                    activities.append({
                        'type': 'discussion',
                        'title': f"Discussion: {focus_title} Examples",
                        'duration_minutes': min(per_activity_minutes, segment_minutes),
                        'description': f"Share examples of {focus_title} from your experience",
                        'instructions': [
                            f"Recall where {focus_title} shows up in the module",
                            "Share with a partner or small group",
                            "Identify key learning points"
                        ]
                    })
                else:
                    activities.append({
                        'type': 'reflection',
                        'title': f"Reflection: Applying {focus_title}",
                        'duration_minutes': min(per_activity_minutes, segment_minutes),
                        'description': f"Capture personal action steps for {focus_title}",
                        'instructions': [
                            "List two everyday scenarios where it fits",
                            "Write one question to bring back to the group",
                            "Pair-share insights"
                        ]
                    })

            elif level == 'intermediate':
                if index == 0:
                    activities.append({
                        'type': 'case_study',
                        'title': f"Case Study: {focus_title} Application",
                        'duration_minutes': min(per_activity_minutes, segment_minutes),
                        'description': f"Analyze a documented {focus_title} scenario",
                        'instructions': [
                            f"Review excerpts describing {focus_title}",
                            "Identify key challenges and opportunities",
                            "Propose solutions using course concepts",
                            "Present findings to the group"
                        ]
                    })
                else:
                    activities.append({
                        'type': 'role_play',
                        'title': f"Role Play: Coaching on {focus_title}",
                        'duration_minutes': min(per_activity_minutes, segment_minutes),
                        'description': f"Simulate a coaching conversation featuring {focus_title}",
                        'instructions': [
                            "Assign facilitator, learner, observer roles",
                            "Run a 5-minute micro-coaching demo",
                            "Debrief on what reinforced the concept"
                        ]
                    })

            else:  # advanced
                if index == 0:
                    activities.append({
                        'type': 'project',
                        'title': f"Mini-Project: {focus_title} Implementation Plan",
                        'duration_minutes': min(per_activity_minutes, segment_minutes),
                        'description': f"Create an implementation plan for {focus_title}",
                        'instructions': [
                            f"Define how {focus_title} impacts the project scope",
                            "Identify resources and constraints",
                            "Develop step-by-step implementation plan",
                            "Present plan with justification"
                        ]
                    })
                else:
                    activities.append({
                        'type': 'peer_review',
                        'title': f"Peer Review: Stress-test {focus_title}",
                        'duration_minutes': min(per_activity_minutes, segment_minutes),
                        'description': f"Evaluate another team’s approach to {focus_title}",
                        'instructions': [
                            "Swap draft plans across teams",
                            "Score using success criteria from the documentation",
                            "Capture improvement recommendations"
                        ]
                    })

        # If time allows, add a closing synthesis activity for longer sessions
        if total_minutes >= 45:
            activities.append({
                'type': 'synthesis',
                'title': 'Learning Gallery Walk',
                'duration_minutes': max(5, min(10, segment_minutes)),
                'description': 'Teams rotate to review artefacts created for each focus topic.',
                'instructions': [
                    'Post key artefacts or takeaways for each topic',
                    'Rotate every two minutes to digest insights',
                    'Close with a full-group synthesis of cross-topic themes'
                ]
            })

        return activities
    
    def _generate_assessment(
        self,
        topic: str,
        level: str,
        content: Dict[str, Any],
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Generate assessment questions"""

        assessment = {
            'type': 'knowledge_check',
            'questions': []
        }

        focus_topics = [
            entry for entry in (content.get('focus_topics') or content.get('top_topics', []))
            if entry.get('title') and not self._is_noise_text(entry['title'])
        ]
        primary_topic_title = focus_topics[0]['title'] if focus_topics else topic

        def shorten(text: str, limit: int = 140) -> str:
            text = text.strip()
            if len(text) <= limit:
                return text
            truncated = text[:limit].rsplit(' ', 1)[0]
            return f"{truncated}…"

        primary_support = []
        if focus_topics:
            primary_support = [shorten(sentence) for sentence in focus_topics[0].get('sentences', [])[:3]]

        # Generate different types of questions based on level
        if level == 'beginner':
            assessment['questions'].extend([
                {
                    'type': 'multiple_choice',
                    'question': f"What is the primary purpose of {primary_topic_title}?",
                    'options': [
                        f"To improve {primary_topic_title} effectiveness",
                        "To complicate processes",
                        "To reduce efficiency",
                        "None of the above"
                    ],
                    'correct_answer': 0
                },
                {
                    'type': 'true_false',
                    'question': f"{primary_topic_title} is an important aspect of instructional design.",
                    'correct_answer': True
                }
            ])

        elif level == 'intermediate':
            assessment['questions'].extend([
                {
                    'type': 'short_answer',
                    'question': f"Describe three key takeaways about {primary_topic_title} from the source material.",
                    'expected_elements': primary_support if primary_support else [
                        f"Reinforce why {primary_topic_title} matters",
                        f"Explain where {primary_topic_title} appears in the module",
                        "Link to learner application"
                    ]
                },
                {
                    'type': 'scenario',
                    'question': f"You are designing a course that requires {primary_topic_title}. What steps would you take?",
                    'evaluation_criteria': [
                        "Systematic approach",
                        "Consideration of learner needs",
                        f"Application of documented practices for {primary_topic_title}"
                    ]
                }
            ])

        # Additional questions for extended modules
        additional_topics = focus_topics[1:]
        for topic_info in additional_topics:
            title = topic_info['title']
            evidence = [shorten(sentence) for sentence in topic_info.get('sentences', [])[:2]]
            if level == 'beginner':
                assessment['questions'].append({
                    'type': 'true_false',
                    'question': f"{title} directly supports the main objectives of {primary_topic_title}.",
                    'correct_answer': True
                })
            elif level == 'intermediate':
                assessment['questions'].append({
                    'type': 'short_answer',
                    'question': f"Summarize how {title} complements {primary_topic_title}.",
                    'expected_elements': evidence if evidence else [f"Highlight alignment between {title} and module goals"]
                })
            else:
                assessment['questions'].append({
                    'type': 'scenario',
                    'question': f"Design an evaluation metric for {title} that fits this module.",
                    'evaluation_criteria': [
                        'Ties back to learner outcomes',
                        'Leverages documented practices',
                        f"Shows alignment between {title} and {primary_topic_title}"
                    ]
                })

        if level == 'advanced' and duration_minutes >= 45:
            assessment['questions'].append({
                'type': 'project_plan',
                'question': f"Outline a capstone deliverable that integrates {', '.join([entry['title'] for entry in focus_topics[:3]])}.",
                'evaluation_criteria': [
                    'Clear sequencing of module components',
                    'Evidence of stakeholder considerations',
                    'Measurable success indicators'
                ]
            })

        return assessment
    
    def _create_content_slides(self, section: Dict[str, Any], start_slide_num: int) -> List[Dict[str, Any]]:
        """Create multiple slides for content section"""
        
        slides = []
        slide_num = start_slide_num
        
        # Main concept slide
        slides.append({
            'slide_number': slide_num,
            'type': 'content',
            'title': section['title'],
            'content': {
                'main_concept': section['content']['theme'],
                'explanation': section['content']['explanation']
            }
        })
        slide_num += 1
        
        # Examples slide if available
        if section['content'].get('examples'):
            slides.append({
                'slide_number': slide_num,
                'type': 'bullet_points',
                'title': f"{section['title']} - Examples",
                'content': {
                    'title': 'Examples',
                    'bullet_points': section['content']['examples']
                }
            })
            slide_num += 1
        
        # Best practices slide if available
        if section['content'].get('best_practices'):
            slides.append({
                'slide_number': slide_num,
                'type': 'bullet_points',
                'title': f"{section['title']} - Best Practices",
                'content': {
                    'title': 'Best Practices',
                    'bullet_points': section['content']['best_practices']
                }
            })
        
        return slides
    
    def _generate_key_takeaways(self, module_data: Dict[str, Any]) -> List[str]:
        """Generate key takeaways from module"""
        
        takeaways = [
            f"Understanding of {module_data['metadata']['title'].split(': ')[1]} fundamentals",
            "Practical application strategies",
            "Best practices for implementation"
        ]
        
        # Add specific takeaways from learning objectives
        takeaways.extend(module_data['learning_objectives'][:2])
        
        return takeaways[:5]
    
    def _generate_next_steps(self, module_data: Dict[str, Any]) -> List[str]:
        """Generate next steps for learners"""
        
        next_steps = [
            "Apply concepts in your current projects",
            "Practice with additional examples",
            "Seek feedback on implementation",
            "Explore advanced topics in this area"
        ]
        
        return next_steps
    
    def _extract_resources(self, retrieved_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract resources from retrieved content"""
        
        resources = []
        
        for doc_group in retrieved_content:
            resource = {
                'title': doc_group['filename'],
                'type': doc_group['file_type'],
                'relevance_score': doc_group['max_similarity'],
                'description': f"Source material from {doc_group['filename']}"
            }
            resources.append(resource)
        
        # Sort by relevance
        resources.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return resources
