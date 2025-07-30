import pytest
import os
import tempfile
import shutil
from promptvc.repo import PromptRepo, PromptVersion

class TestPromptVersion:
    def test_init(self):
        version = PromptVersion(
            id=1,
            text="Hello world",
            commit_msg="Initial commit",
            timestamp="2025-01-01T10:00:00",
            hash="abc123"
        )
        
        assert version.id == 1
        assert version.text == "Hello world"
        assert version.commit_msg == "Initial commit"
        assert version.timestamp == "2025-01-01T10:00:00"
        assert version.hash == "abc123"


class TestPromptRepo:
    def setup(self):
        self.test_dir = tempfile.mkdtemp()
        self.repo = PromptRepo(self.test_dir)
    
    def teardown(self):
        shutil.rmtree(self.test_dir)
    
    def test_init_create_dir(self):
        assert os.path.exists(self.repo.repo_path)
        assert os.path.exists(self.repo.prompts_dir)
    
    def test_init_default_path(self):
        original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            repo = PromptRepo()
            assert repo.repo_path == os.path.join(".", ".promptvc")
            assert os.path.exists(repo.repo_path)
        finally:
            os.chdir(original_dir)
    
    def test_load_versions_no_file(self):
        versions = self.repo._load_versions("nonexistent")
        assert versions == []
    
    def test_add_prompt(self):
        self.repo.add("test-prompt", "Hello {input}")
        versions = self.repo._load_versions("test-prompt")
        
        assert len(versions) == 1
        assert versions[0]["text"] == "Hello {input}"
        assert versions[0]["id"] == 1
        assert versions[0]["commit_msg"] == ""
        assert "timestamp" in versions[0]
        assert "hash" in versions[0]
    
    def test_add_empty_prompt(self):
        with pytest.raises(ValueError, match="Empty prompt text"):
            self.repo.add("test-prompt", "")
        
        with pytest.raises(ValueError, match="Empty prompt text"):
            self.repo.add("test-prompt", "   ")
        
        with pytest.raises(ValueError, match="Empty prompt text"):
            self.repo.add("test-prompt", "\n\t  ")
    
    def test_add_multiple_versions(self):
        self.repo.add("test-prompt", "Version 1")
        self.repo.add("test-prompt", "Version 2")
        
        versions = self.repo._load_versions("test-prompt")
        assert len(versions) == 2
        assert versions[0]["id"] == 1
        assert versions[1]["id"] == 2
        assert versions[0]["text"] == "Version 1"
        assert versions[1]["text"] == "Version 2"
    
    def test_add_generates_hash(self):
        self.repo.add("test-prompt", "Text 1")
        self.repo.add("test-prompt", "Text 2")
        
        versions = self.repo._load_versions("test-prompt")
        assert versions[0]["hash"] != versions[1]["hash"]
        assert len(versions[0]["hash"]) == 40
        assert len(versions[1]["hash"]) == 40
    
    def test_commit_prompt(self):
        self.repo.add("test-prompt", "Hello world")
        self.repo.commit("test-prompt", "Initial version")
        
        versions = self.repo._load_versions("test-prompt")
        assert versions[0]["commit_msg"] == "Initial version"
    
    def test_commit_no_versions_fails(self):
        with pytest.raises(ValueError, match="No versions found"):
            self.repo.commit("nonexistent", "message")
    
    def test_commit_already_committed_fails(self):
        self.repo.add("test-prompt", "Hello world")
        self.repo.commit("test-prompt", "First commit")
        
        with pytest.raises(ValueError, match="Already committed"):
            self.repo.commit("test-prompt", "Second commit")
    
    def test_commit_allows_new_version_after_commit(self):
        self.repo.add("test-prompt", "Version 1")
        self.repo.commit("test-prompt", "First")
        self.repo.add("test-prompt", "Version 2")
        self.repo.commit("test-prompt", "Second")
        
        versions = self.repo._load_versions("test-prompt")
        assert len(versions) == 2
        assert versions[0]["commit_msg"] == "First"
        assert versions[1]["commit_msg"] == "Second"
    
    def test_history(self):
        self.repo.add("test-prompt", "Version 1")
        self.repo.commit("test-prompt", "First")
        self.repo.add("test-prompt", "Version 2")
        self.repo.commit("test-prompt", "Second")
        
        history = self.repo.history("test-prompt")
        
        assert len(history) == 2
        assert isinstance(history[0], PromptVersion)
        assert isinstance(history[1], PromptVersion)
        assert history[0].id == 1
        assert history[0].commit_msg == "First"
        assert history[1].id == 2
        assert history[1].commit_msg == "Second"
    
    def test_history_empty_prompt(self):
        history = self.repo.history("nonexistent")
        assert history == []
    
    def test_history_includes_uncommitted(self):
        self.repo.add("test-prompt", "Version 1")
        self.repo.commit("test-prompt", "First")
        self.repo.add("test-prompt", "Version 2")
        
        history = self.repo.history("test-prompt")
        assert len(history) == 2
        assert history[0].commit_msg == "First"
        assert history[1].commit_msg == ""
    
    def test_checkout(self):
        self.repo.add("test-prompt", "Version 1")
        self.repo.add("test-prompt", "Version 2")
        
        text = self.repo.checkout("test-prompt", 1)
        assert text == "Version 1"
        
        text = self.repo.checkout("test-prompt", 2)
        assert text == "Version 2"
    
    def test_checkout_invalid_version(self):
        self.repo.add("test-prompt", "Version 1")
        
        text = self.repo.checkout("test-prompt", 999)
        assert text is None
        
        text = self.repo.checkout("nonexistent", 1)
        assert text is None
    
    def test_diff(self):
        self.repo.add("test-prompt", "Hello world")
        self.repo.add("test-prompt", "Hello universe")
        
        result = self.repo.diff("test-prompt", 1, 2)
        
        assert "text_diff" in result
        assert "semantic_similarity" in result
        assert isinstance(result["semantic_similarity"], float)
        assert 0.0 <= result["semantic_similarity"] <= 1.1
    
    def test_diff_invalid_versions(self):
        self.repo.add("test-prompt", "Hello world")
        
        with pytest.raises(ValueError, match="Invalid version IDs"):
            self.repo.diff("test-prompt", 1, 999)
        
        with pytest.raises(ValueError, match="Invalid version IDs"):
            self.repo.diff("test-prompt", 999, 1)
        
        with pytest.raises(ValueError, match="Invalid version IDs"):
            self.repo.diff("nonexistent", 1, 2)
    
    def test_without_llm(self):
        self.repo.add("test-prompt", "Summarize: {input}")
        samples = [{"input": "Test input"}]
        
        results = self.repo.eval_versions("test-prompt", [1], samples)
        
        assert 1 in results
        assert len(results[1]["outputs"]) == 1
        assert results[1]["outputs"][0]["input"] == "Test input"
        assert results[1]["outputs"][0]["output"] == "Summarize: Test input"
        assert "avg_length" in results[1]
    
    def test_with_llm(self):
        def mock_llm(prompt):
            return f"LLM response to: {prompt}"
        
        self.repo.add("test-prompt", "Summarize: {input}")
        samples = [{"input": "Test input"}]
        
        results = self.repo.eval_versions("test-prompt", [1], samples, mock_llm)
        
        assert 1 in results
        output = results[1]["outputs"][0]["output"]
        assert output == "LLM response to: Summarize: Test input"

    def test_multiple_samples(self):
        self.repo.add("test-prompt", "Process: {input}")
        samples = [
            {"input": "Sample 1"},
            {"input": "Sample 2"},
            {"input": "Sample 3"}
        ]
        
        results = self.repo.eval_versions("test-prompt", [1], samples)
        
        assert len(results[1]["outputs"]) == 3
        assert results[1]["outputs"][0]["output"] == "Process: Sample 1"
        assert results[1]["outputs"][1]["output"] == "Process: Sample 2"
        assert results[1]["outputs"][2]["output"] == "Process: Sample 3"
    
    def test_invalid_version(self):
        self.repo.add("test-prompt", "Hello {input}")
        samples = [{"input": "Test"}]
        
        results = self.repo.eval_versions("test-prompt", [999], samples)
        
        assert results == {}
    
    def test_multiple_versions(self):
        self.repo.add("test-prompt", "V1: {input}")
        self.repo.add("test-prompt", "V2: {input}")
        samples = [{"input": "Test"}]
        
        results = self.repo.eval_versions("test-prompt", [1, 2], samples)
        
        assert 1 in results
        assert 2 in results
        assert results[1]["outputs"][0]["output"] == "V1: Test"
        assert results[2]["outputs"][0]["output"] == "V2: Test"
    
    def test_length_ratio(self):
        ratio = self.repo.length_ratio("hello", "world")
        assert ratio == 1.0
        
        ratio = self.repo.length_ratio("", "")
        assert ratio == 1.0
        
        ratio = self.repo.length_ratio("", "hello")
        assert ratio == 0.0
        
        ratio = self.repo.length_ratio("hello", "hello world")
        assert isinstance(ratio, float)
    
        expected = 1.0 - abs(1.0 - (11/5))
        assert abs(ratio - expected) < 0.001
    
    def test_multiple_prompts(self):
        self.repo.add("summarizer", "Summarize: {input}")
        self.repo.commit("summarizer", "v1")
        
        self.repo.add("translator", "Translate to French: {input}")
        self.repo.commit("translator", "v1")
        
        sum_history = self.repo.history("summarizer")
        trans_history = self.repo.history("translator")
        
        assert len(sum_history) == 1
        assert len(trans_history) == 1
        assert sum_history[0].text != trans_history[0].text
        
        sum_file = self.repo._prompt_file("summarizer")
        trans_file = self.repo._prompt_file("translator")
        assert os.path.exists(sum_file)
        assert os.path.exists(trans_file)
    
    def test_avg_length_calculation(self):
        self.repo.add("test-prompt", "Process: {input}")
        samples = [
            {"input": "short"},
            {"input": "medium length"},
            {"input": "this is a long text lmao"}
        ]
        
        results = self.repo.eval_versions("test-prompt", [1], samples)
        
        outputs = results[1]["outputs"]
        total_length = sum(len(o["output"]) for o in outputs)
        expected_avg = total_length / len(outputs)
        
        assert abs(results[1]["avg_length"] - expected_avg) < 0.001
    
    def test_empty_outputs(self):
        self.repo.add("test-prompt", "Test: {input}")
        samples = []
        
        results = self.repo.eval_versions("test-prompt", [1], samples)
        
        assert results[1]["outputs"] == []
        assert results[1]["avg_length"] == 0

if __name__ == "__main__":
    pytest.main([__file__])