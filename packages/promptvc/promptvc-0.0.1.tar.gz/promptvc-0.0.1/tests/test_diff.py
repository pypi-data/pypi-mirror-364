import pytest
from promptvc.diff import PromptDiff

class TestPromptDiff:
    def setup(self):
        self.diff_engine = PromptDiff()
    
    def test_text_diff_identical(self):
        old = "Hello world"
        new = "Hello world"
        
        diff = self.diff_engine.text_diff(old, new)
        
        assert "Hello world" in diff
        assert "- " not in diff
        assert "+ " not in diff
    
    def test_text_diff_simple_change(self):
        old = "Hello world"
        new = "Hello universe"
        
        diff = self.diff_engine.text_diff(old, new)
        
        assert "Hello" in diff
        assert "world" in diff
        assert "universe" in diff
        assert "- Hello world" in diff
        assert "+ Hello universe" in diff
    
    def test_text_multiline(self):
        old = "Line 1\nLine 2\nLine 3"
        new = "Line 1\nLine 2 modified\nLine 3"
        
        diff = self.diff_engine.text_diff(old, new)
        
        assert "Line 1" in diff
        assert "Line 2" in diff
        assert "modified" in diff
        assert "Line 3" in diff
    
    def test_diff_empty_strings(self):
        diff = self.diff_engine.text_diff("", "")
        assert diff == ""
        
        diff = self.diff_engine.text_diff("", "Hello")
        assert "+ Hello" in diff
        
        diff = self.diff_engine.text_diff("Hello", "")
        assert "- Hello" in diff
    
    def test_text_diff_line_addition(self):
        old = "Line 1\nLine 2"
        new = "Line 1\nLine 2\nLine 3"
        
        diff = self.diff_engine.text_diff(old, new)
        
        assert "Line 1" in diff
        assert "Line 2" in diff
        assert "+ Line 3" in diff
    
    def test_text_diff_line_removal(self):
        old = "Line 1\nLine 2\nLine 3"
        new = "Line 1\nLine 3"
        
        diff = self.diff_engine.text_diff(old, new)
        
        assert "Line 1" in diff
        assert "- Line 2" in diff
        assert "Line 3" in diff
    
    def test_identical(self):
        similarity = self.diff_engine.semantic_diff("Hello world", "Hello world")
        
        assert isinstance(similarity, float)
        assert similarity > 0.99
        assert similarity <= 1.01
    
    def test_similar_meaning(self):
        similarity = self.diff_engine.semantic_diff("Hello world", "Hi there")
        
        assert isinstance(similarity, float)
        # assert 0.0 <= similarity <= 1.01
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.3
    
    def test_opposite_meaning(self):
        similarity = self.diff_engine.semantic_diff("I love this", "I hate this")
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.8
    
    def test_completely_different(self):
        similarity = self.diff_engine.semantic_diff(
            "Hello world", 
            "12345 xyz random numbers"
        )
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.5
    
    def test_empty_strings(self):

        similarity = self.diff_engine.semantic_diff("", "")
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        
        similarity = self.diff_engine.semantic_diff("", "Hello world")
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        
        similarity = self.diff_engine.semantic_diff("Hello world", "")
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
    
    def test_long_texts(self):
        text1 = "This is a long long text about machine learning and artificial intelligence aka ai"
        text2 = "We discuss AI and ML technologies in detail"
        
        similarity = self.diff_engine.semantic_diff(text1, text2)
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.4
    
    def test_model_loading(self):
        assert self.diff_engine._model is None
        
        similarity1 = self.diff_engine.semantic_diff("Hello", "Hi")
        assert self.diff_engine._model is not None
        
        model_ref = self.diff_engine._model
        similarity2 = self.diff_engine.semantic_diff("World", "Earth")
        assert self.diff_engine._model is model_ref
        
        assert isinstance(similarity1, float)
        assert isinstance(similarity2, float)
    
    def test_special_characters(self):
        similarity = self.diff_engine.semantic_diff(
            "Hello, world! How are you?",
            "hihi, how you doing?"
        )
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5 
    
    def test_numbers(self):
        similarity = self.diff_engine.semantic_diff("The price is 100", "It costs 200")
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.3 
    
    def test_text_diff_whitespace(self):
        old = "Hello world"
        new = "Hello  world"
        
        diff = self.diff_engine.text_diff(old, new)
        
        assert "- Hello world" in diff
        assert "+ Hello  world" in diff
    
    def test_case_sensitivity(self):
        similarity1 = self.diff_engine.semantic_diff("Hello World", "hello world")
        similarity2 = self.diff_engine.semantic_diff("HELLO WORLD", "hello world")
        
        assert isinstance(similarity1, float)
        assert isinstance(similarity2, float)
        assert similarity1 > 0.9
        assert similarity2 > 0.9

if __name__ == "__main__":
    pytest.main([__file__])