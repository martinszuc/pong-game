"""High score management with JSON storage"""

import json
import os
import logging

logger = logging.getLogger(__name__)

SCORES_FILE = "high_scores.json"


class HighScoreManager:
    """Manages high scores stored in JSON file"""
    
    def __init__(self, scores_file=SCORES_FILE):
        # Convert to absolute path to ensure consistent file location
        self.scores_file = os.path.abspath(scores_file)
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
        """Load scores from JSON file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    self.scores = json.load(f)
                self.scores.sort(key=lambda x: x['score'], reverse=True)
                logger.info(f"Loaded {len(self.scores)} high scores from {self.scores_file}")
            except Exception as e:
                logger.error(f"Error loading scores: {e}")
                self.scores = []
        else:
            self.scores = []
    
    def save_scores(self):
        """Save scores to JSON file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
            logger.info(f"Saved {len(self.scores)} high scores to {self.scores_file}")
            logger.debug(f"Scores saved: {self.scores}")
        except Exception as e:
            logger.error(f"Error saving scores: {e}", exc_info=True)
    
    def is_high_score(self, score):
        """Check if score is a new highest score"""
        # Score must be greater than 0 to qualify
        if score <= 0:
            return False
        # If no scores exist, any positive score is a new highest
        if len(self.scores) == 0:
            return True
        # Score must beat the current highest score
        return score > self.scores[0]['score']
    
    def add_score(self, name, score):
        """Add a new high score"""
        self.scores.append({'name': name, 'score': score})
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        # Keep only top 5 scores
        self.scores = self.scores[:5]
        self.save_scores()
    
    def get_top_scores(self, count=5):
        """Get top N scores"""
        return self.scores[:count]
    
    def get_highest_score(self):
        """Get the highest score, or 0 if no scores exist"""
        if len(self.scores) == 0:
            return 0
        return self.scores[0]['score']

