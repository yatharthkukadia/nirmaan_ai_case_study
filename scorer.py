import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import language_tool_python
from collections import Counter
import textstat

class TranscriptScorer:
    def __init__(self):
        # Load sentence transformer model for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize grammar checker
        try:
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
        except:
            self.grammar_tool = None
        
        # Define rubric criteria
        self.rubric = self._initialize_rubric()
    
    def _initialize_rubric(self):
        """Initialize the scoring rubric based on the Excel sheet"""
        return {
            'salutation': {
                'weight': 5,
                'keywords': ['hi', 'hello', 'good morning', 'good afternoon', 'good evening', 'good day'],
                'description': 'Proper greeting and salutation at the beginning'
            },
            'content_structure': {
                'weight': 20,
                'keywords': {
                    'name': ['name', 'i am', "i'm", 'myself'],
                    'school_class': ['school', 'class', 'grade', 'studying', 'student'],
                    'family': ['family', 'father', 'mother', 'parents', 'brother', 'sister', 'siblings'],
                    'location': ['from', 'live', 'city', 'town', 'village', 'place'],
                    'hobbies': ['hobby', 'hobbies', 'enjoy', 'love', 'like', 'interest', 'passion', 'free time']
                },
                'order_keywords': ['first', 'firstly', 'second', 'secondly', 'then', 'next', 'finally', 'lastly'],
                'description': 'Includes name, age, school/class, family, location, and hobbies with good structure'
            },
            'speech_rate': {
                'weight': 10,
                'ideal_wpm': 130,
                'min_wpm': 111,
                'max_wpm': 160,
                'description': 'Speech rate in words per minute (ideal: 130 WPM)'
            },
            'language_grammar': {
                'weight': 10,
                'description': 'Grammar correctness and vocabulary richness'
            },
            'clarity': {
                'weight': 15,
                'filler_words': ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'right', 'i mean', 'well', 'kind of', 'sort of'],
                'description': 'Minimal use of filler words'
            },
            'engagement': {
                'weight': 15,
                'positive_words': ['happy', 'excited', 'passionate', 'love', 'enjoy', 'great', 'wonderful', 'amazing', 'excellent', 'enthusiastic'],
                'description': 'Positive and engaging tone'
            }
        }
    
    def _to_python_type(self, value):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        return value
    
    def score_transcript(self, transcript, duration_minutes=1.5):
        """Main scoring function"""
        transcript = transcript.strip()
        word_count = len(transcript.split())
        
        results = {
            'overall_score': 0,
            'word_count': word_count,
            'criteria': []
        }
        
        # Score each criterion
        total_weighted_score = 0
        total_weight = sum([criteria['weight'] for criteria in self.rubric.values()])
        
        # 1. Salutation
        salutation_result = self._score_salutation(transcript)
        results['criteria'].append(salutation_result)
        total_weighted_score += salutation_result['score']
        
        # 2. Content & Structure
        content_result = self._score_content_structure(transcript)
        results['criteria'].append(content_result)
        total_weighted_score += content_result['score']
        
        # 3. Speech Rate
        speech_rate_result = self._score_speech_rate(transcript, duration_minutes)
        results['criteria'].append(speech_rate_result)
        total_weighted_score += speech_rate_result['score']
        if 'wpm' in speech_rate_result:
            results['wpm'] = float(speech_rate_result['wpm'])
        
        # 4. Language & Grammar
        grammar_result = self._score_grammar(transcript)
        results['criteria'].append(grammar_result)
        total_weighted_score += grammar_result['score']
        
        # 5. Clarity (Filler words)
        clarity_result = self._score_clarity(transcript)
        results['criteria'].append(clarity_result)
        total_weighted_score += clarity_result['score']
        
        # 6. Engagement
        engagement_result = self._score_engagement(transcript)
        results['criteria'].append(engagement_result)
        total_weighted_score += engagement_result['score']
        
        # Calculate overall score (normalized to 100)
        results['overall_score'] = float((total_weighted_score / total_weight) * 100)
        
        return results
    
    def _score_salutation(self, transcript):
        """Score salutation/greeting"""
        criteria = self.rubric['salutation']
        max_score = criteria['weight']
        
        # Check for keywords in the first 50 words
        first_part = ' '.join(transcript.split()[:50]).lower()
        
        found_keywords = []
        for keyword in criteria['keywords']:
            if keyword in first_part:
                found_keywords.append(keyword)
        
        # Scoring: 0-5 based on number and quality of greetings
        if len(found_keywords) >= 3:
            score = max_score
            feedback = "Excellent greeting with multiple salutations."
        elif len(found_keywords) == 2:
            score = max_score * 0.8
            feedback = "Good greeting present."
        elif len(found_keywords) == 1:
            score = max_score * 0.6
            feedback = "Basic greeting present."
        else:
            score = 0
            feedback = "No clear greeting found. Consider starting with 'Hello' or 'Good morning'."
        
        return {
            'name': 'Salutation',
            'score': float(score),
            'max_score': float(max_score),
            'feedback': feedback,
            'keywords_found': found_keywords
        }
    
    def _score_content_structure(self, transcript):
        """Score content completeness and structure"""
        criteria = self.rubric['content_structure']
        max_score = criteria['weight']
        
        transcript_lower = transcript.lower()
        
        # Check for each key element
        elements_found = {}
        all_keywords_found = []
        
        for element, keywords in criteria['keywords'].items():
            found = any(kw in transcript_lower for kw in keywords)
            elements_found[element] = found
            if found:
                matched = [kw for kw in keywords if kw in transcript_lower]
                all_keywords_found.extend(matched)
        
        # Check for structural flow
        order_words = [word for word in criteria['order_keywords'] if word in transcript_lower]
        has_structure = len(order_words) > 0
        
        # Calculate score
        elements_count = sum(elements_found.values())
        element_score = (elements_count / len(criteria['keywords'])) * 0.7  # 70% for elements
        structure_score = 0.3 if has_structure else 0.1  # 30% for structure
        
        # Semantic similarity with ideal introduction
        ideal_intro = "My name is [name], I am [age] years old studying in [class]. I come from [location]. My family consists of my parents and siblings. In my free time, I enjoy [hobbies]."
        semantic_score = self._calculate_semantic_similarity(transcript, ideal_intro)
        
        # Combined score
        final_ratio = (element_score + structure_score + semantic_score * 0.2) / 1.2
        score = final_ratio * max_score
        
        # Feedback
        missing_elements = [k for k, v in elements_found.items() if not v]
        if elements_count >= 4:
            feedback = f"Excellent content coverage! Includes {elements_count}/5 key elements."
        elif elements_count >= 3:
            feedback = f"Good content. Consider adding: {', '.join(missing_elements)}."
        else:
            feedback = f"Content needs improvement. Missing: {', '.join(missing_elements)}."
        
        return {
            'name': 'Content & Structure',
            'score': float(score),
            'max_score': float(max_score),
            'feedback': feedback,
            'keywords_found': all_keywords_found[:10],  # Limit to 10 for display
            'details': {
                'Elements found': f"{elements_count}/5",
                'Has structure': 'Yes' if has_structure else 'No',
                'Semantic similarity': f"{semantic_score:.2%}"
            }
        }
    
    def _score_speech_rate(self, transcript, duration_minutes):
        """Score speech rate (WPM)"""
        criteria = self.rubric['speech_rate']
        max_score = criteria['weight']
        
        word_count = len(transcript.split())
        wpm = word_count / duration_minutes
        
        ideal_wpm = criteria['ideal_wpm']
        min_wpm = criteria['min_wpm']
        max_wpm = criteria['max_wpm']
        
        # Score based on WPM range
        if min_wpm <= wpm <= max_wpm:
            # Within ideal range
            deviation = abs(wpm - ideal_wpm) / ideal_wpm
            score = max_score * (1 - deviation * 0.5)
            feedback = f"Good speech rate at {wpm:.0f} WPM."
        elif wpm < min_wpm:
            # Too slow
            ratio = wpm / min_wpm
            score = max_score * ratio * 0.7
            feedback = f"Speech rate is slow ({wpm:.0f} WPM). Try to speak a bit faster."
        else:
            # Too fast
            ratio = max_wpm / wpm
            score = max_score * ratio * 0.7
            feedback = f"Speech rate is fast ({wpm:.0f} WPM). Try to slow down slightly."
        
        return {
            'name': 'Speech Rate',
            'score': float(score),
            'max_score': float(max_score),
            'feedback': feedback,
            'wpm': float(wpm),
            'details': {
                'Words per minute': f"{wpm:.0f}",
                'Ideal range': f"{min_wpm}-{max_wpm} WPM"
            }
        }
    
    def _score_grammar(self, transcript):
        """Score grammar and vocabulary"""
        criteria = self.rubric['language_grammar']
        max_score = criteria['weight']
        
        word_count = len(transcript.split())
        
        # Grammar check
        grammar_score = max_score * 0.6  # Default if tool not available
        grammar_errors = 0
        
        if self.grammar_tool:
            try:
                matches = self.grammar_tool.check(transcript)
                grammar_errors = len(matches)
                
                # Score based on errors per 100 words
                error_rate = (grammar_errors / word_count) * 100 if word_count > 0 else 0
                
                if error_rate < 3:
                    grammar_score = max_score * 0.6
                elif error_rate < 5:
                    grammar_score = max_score * 0.5
                elif error_rate < 10:
                    grammar_score = max_score * 0.4
                else:
                    grammar_score = max_score * 0.3
            except:
                pass
        
        # Vocabulary richness (TTR - Type-Token Ratio)
        words = re.findall(r'\b\w+\b', transcript.lower())
        unique_words = set(words)
        ttr = len(unique_words) / len(words) if words else 0
        
        # TTR scoring
        if ttr > 0.7:
            vocab_score = max_score * 0.4
        elif ttr > 0.5:
            vocab_score = max_score * 0.35
        elif ttr > 0.3:
            vocab_score = max_score * 0.3
        else:
            vocab_score = max_score * 0.2
        
        score = grammar_score + vocab_score
        
        # Feedback
        if grammar_errors == 0:
            grammar_feedback = "No grammar errors detected."
        elif grammar_errors <= 2:
            grammar_feedback = f"{grammar_errors} minor grammar issues found."
        else:
            grammar_feedback = f"{grammar_errors} grammar errors detected. Review and correct."
        
        vocab_feedback = f"Vocabulary richness: {ttr:.2%}"
        
        return {
            'name': 'Language & Grammar',
            'score': float(score),
            'max_score': float(max_score),
            'feedback': f"{grammar_feedback} {vocab_feedback}",
            'details': {
                'Grammar errors': int(grammar_errors),
                'Vocabulary richness (TTR)': f"{ttr:.2%}",
                'Unique words': int(len(unique_words))
            }
        }
    
    def _score_clarity(self, transcript):
        """Score clarity based on filler words"""
        criteria = self.rubric['clarity']
        max_score = criteria['weight']
        
        transcript_lower = transcript.lower()
        word_count = len(transcript.split())
        
        # Count filler words
        filler_count = 0
        found_fillers = []
        
        for filler in criteria['filler_words']:
            count = transcript_lower.count(filler)
            if count > 0:
                filler_count += count
                found_fillers.append(filler)
        
        # Calculate filler word ratio
        filler_ratio = (filler_count / word_count * 100) if word_count > 0 else 0
        
        # Score based on filler word ratio
        if filler_ratio < 2:
            score = max_score
            feedback = "Excellent clarity with minimal filler words."
        elif filler_ratio < 5:
            score = max_score * 0.8
            feedback = "Good clarity. Some filler words present."
        elif filler_ratio < 10:
            score = max_score * 0.6
            feedback = f"Moderate use of filler words ({filler_count} found). Try to reduce them."
        else:
            score = max_score * 0.4
            feedback = f"High use of filler words ({filler_count} found). Practice reducing them for better clarity."
        
        return {
            'name': 'Clarity',
            'score': float(score),
            'max_score': float(max_score),
            'feedback': feedback,
            'details': {
                'Filler words count': int(filler_count),
                'Filler word ratio': f"{filler_ratio:.1f}%",
                'Fillers found': ', '.join(found_fillers) if found_fillers else 'None'
            }
        }
    
    def _score_engagement(self, transcript):
        """Score engagement based on positive/enthusiastic tone"""
        criteria = self.rubric['engagement']
        max_score = criteria['weight']
        
        transcript_lower = transcript.lower()
        
        # Count positive words
        positive_count = sum(1 for word in criteria['positive_words'] if word in transcript_lower)
        found_positive = [word for word in criteria['positive_words'] if word in transcript_lower]
        
        # Sentiment/emotion keywords
        emotion_keywords = ['feel', 'excited', 'passionate', 'enthusiastic', 'proud', 'grateful', 'thankful']
        has_emotion = any(word in transcript_lower for word in emotion_keywords)
        
        # Calculate engagement score
        positive_score = min(positive_count / 3, 1.0) * 0.7  # Up to 70% for positive words
        emotion_score = 0.3 if has_emotion else 0.1  # 30% for emotional expression
        
        final_ratio = positive_score + emotion_score
        score = final_ratio * max_score
        
        # Feedback
        if positive_count >= 3 and has_emotion:
            feedback = "Highly engaging with positive and enthusiastic tone!"
        elif positive_count >= 2:
            feedback = "Good engagement. Shows positive tone."
        elif positive_count >= 1:
            feedback = "Some engagement present. Consider expressing more enthusiasm."
        else:
            feedback = "Low engagement. Try to show more enthusiasm and positivity."
        
        return {
            'name': 'Engagement',
            'score': float(score),
            'max_score': float(max_score),
            'feedback': feedback,
            'keywords_found': found_positive,
            'details': {
                'Positive words': int(positive_count),
                'Shows emotion': 'Yes' if has_emotion else 'No'
            }
        }
    
    def _calculate_semantic_similarity(self, text1, text2):
        """Calculate semantic similarity between two texts"""
        try:
            embeddings = self.model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(max(0, similarity))  # Ensure non-negative and Python float
        except:
            return 0.5  # Default similarity if calculation fails
