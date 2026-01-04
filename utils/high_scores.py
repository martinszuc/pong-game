"""
high_scores.py - High score tracking

This file manages the high score leaderboard. Scores are saved to a JSON file
so they persist even after you close the game.
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

# where to save high scores
SCORES_FILE = "high_scores.json"

# how many top scores to keep (only the top 5)
MAX_SCORES_KEPT = 5


class HighScoreManager:
    """
    manages the high score leaderboard
    
    stores player names and scores, keeps only the top 5,
    and saves them to disk so they persist between game sessions
    """
    
    def __init__(self, scores_file=SCORES_FILE):
        """create the high score manager and load existing scores"""
        self.scores_file = os.path.abspath(scores_file)
        self.scores = []  # list of {'name': str, 'score': int} dictionaries
        self.load_scores()
    
    def load_scores(self):
        """
        load high scores from the JSON file
        if the file doesn't exist or is corrupted, start with an empty list
        """
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    self.scores = json.load(f)
                
                # sort by score (highest first)
                self.scores.sort(key=lambda x: x['score'], reverse=True)
                
                logger.info(f"Loaded {len(self.scores)} high scores from {self.scores_file}")
            except Exception as e:
                logger.error(f"Error loading scores: {e}")
                self.scores = []
        else:
            # no scores file exists yet - start fresh
            self.scores = []
    
    def save_scores(self):
        """save the current scores to the JSON file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
            logger.info(f"Saved {len(self.scores)} high scores to {self.scores_file}")
            logger.debug(f"Scores saved: {self.scores}")
        except Exception as e:
            logger.error(f"Error saving scores: {e}", exc_info=True)
    
    def is_high_score(self, score):
        """
        check if a score qualifies for the leaderboard
        
        returns True if:
        - the leaderboard is empty, OR
        - this score is higher than the current #1 score
        """
        if score <= 0:
            return False
        if len(self.scores) == 0:
            return True
        return score > self.scores[0]['score']
    
    def add_score(self, name, score):
        """
        add a new score to the leaderboard
        
        the score is inserted, then the list is sorted and trimmed
        to keep only the top MAX_SCORES_KEPT scores
        """
        self.scores.append({'name': name, 'score': score})
        
        # sort by score (highest first)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # keep only the top scores
        self.scores = self.scores[:MAX_SCORES_KEPT]
        
        # save to disk
        self.save_scores()
    
    def get_top_scores(self, count=MAX_SCORES_KEPT):
        """get the top N scores (default: all stored scores)"""
        return self.scores[:count]
    
    def get_highest_score(self):
        """get the highest score ever achieved (returns 0 if no scores)"""
        if len(self.scores) == 0:
            return 0
        return self.scores[0]['score']

