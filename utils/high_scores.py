import json
import os
import logging

logger = logging.getLogger(__name__)

SCORES_FILE = "high_scores.json"
MAX_SCORES_KEPT = 5


class HighScoreManager:
    def __init__(self, scores_file=SCORES_FILE):
        self.scores_file = os.path.abspath(scores_file)
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
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
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
            logger.info(f"Saved {len(self.scores)} high scores to {self.scores_file}")
            logger.debug(f"Scores saved: {self.scores}")
        except Exception as e:
            logger.error(f"Error saving scores: {e}", exc_info=True)
    
    def is_high_score(self, score):
        if score <= 0:
            return False
        if len(self.scores) == 0:
            return True
        return score > self.scores[0]['score']
    
    def add_score(self, name, score):
        self.scores.append({'name': name, 'score': score})
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:MAX_SCORES_KEPT]
        self.save_scores()
    
    def get_top_scores(self, count=MAX_SCORES_KEPT):
        return self.scores[:count]
    
    def get_highest_score(self):
        if len(self.scores) == 0:
            return 0
        return self.scores[0]['score']

