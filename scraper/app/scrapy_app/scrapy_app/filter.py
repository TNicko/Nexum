class ContentFilter:
    def __init__(self, content: str):
        self.content = content
        self.is_valid = True

    def check_min_length(self, min_length: int = 100) -> 'ContentFilter':
        """Checks if content meets the minimum length requirement."""
        if len(self.content) < min_length:
            self.is_valid = False
        return self

    def contains_keywords(self, keywords: list) -> 'ContentFilter':
        """Checks if content contains any of the specified keywords."""
        if not any(keyword in self.content for keyword in keywords):
            self.is_valid = False
        return self

    def exclude_keywords(self, keywords: list) -> 'ContentFilter':
        """Checks if content contains any of the specified keywords and marks it as invalid if so."""
        if any(keyword in self.content for keyword in keywords):
            self.is_valid = False
        return self

    def validate(self) -> bool:
        """Returns True if content passes all filters."""
        return self.is_valid

