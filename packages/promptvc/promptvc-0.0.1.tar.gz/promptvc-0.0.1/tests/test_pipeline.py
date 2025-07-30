import pytest
import tempfile
import shutil
import os
import yaml
from unittest.mock import patch
from promptvc.pipeline import Pipeline, PipelineStep, PipelineTrace, PipelineRun

class TestPipelineTrace:
    def test_init(self):
        trace = PipelineTrace(
            step_name="test_step",
            input_data="input",
            output="output", 
            duration=1.5,
            tokens_used=10
        )
        
        assert trace.step_name == "test_step"
        assert trace.input == "input"
        assert trace.output == "output"
        assert trace.duration == 1.5
        assert trace.tokens_used == 10
        assert trace.human_rating is None
        assert trace.human_comment is None
    
    def test_init_default_tokens(self):
        trace = PipelineTrace("step", "input", "output", 1.0)
        
        assert trace.tokens_used == 0
        assert trace.human_rating is None
        assert trace.human_comment is None

class TestPipelineStep:
    def test_init(self):
        def dummy_func(x):
            return f"processed_{x}"
        
        config = {"param1": "value1"}
        step = PipelineStep("test_step", "transform", config, dummy_func)
        
        assert step.name == "test_step"
        assert step.type == "transform"
        assert step.config == config
        assert step.func == dummy_func
        assert step.func("test") == "processed_test"

class TestPipelineRun:
    def test_init(self):
        steps = [{"step": "data"}]
        run = PipelineRun("run_123", "2025-01-01T10:00:00", steps, 5.0, 100)
        
        assert run.id == "run_123"
        assert run.timestamp == "2025-01-01T10:00:00"
        assert run.steps == steps
        assert run.total_duration == 5.0
        assert run.total_tokens == 100
    
    def test_init_default_tokens(self):
        run = PipelineRun("run_123", "2025-01-01T10:00:00", [], 1.0)
        
        assert run.total_tokens is None


class TestPipeline:
    def setup(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown(self):
        os.chdir(self.original_dir)
        # os.makedirs(self.test_dir, exist_ok=True)
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        def step1_func(x):
            return f"step1_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.steps) == 1
        assert pipeline.steps[0] == step1
        assert pipeline.traces == []
    
    def test_single_step(self):
        def step1_func(x):
            return f"processed_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run({"input": "test_data"})
        
        assert isinstance(result, PipelineRun)
        assert result.id.startswith("run_")
        assert result.total_duration > 0
        assert result.total_tokens == 2  ### processed_test_data has 2 words when split
        assert len(result.steps) == 1
        
        step_data = result.steps[0]
        assert step_data["step_name"] == "step1"
        assert step_data["input"] == {"input": "test_data"}
        assert step_data["output"] == "processed_{'input': 'test_data'}"
        assert step_data["duration"] > 0
        assert step_data["tokens_used"] == 2
    
    def test_multiple_steps(self):
        def step1_func(x):
            return f"step1_{x}"
        
        def step2_func(x):
            return f"step2_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        step2 = PipelineStep("step2", "transform", {}, step2_func)
        pipeline = Pipeline("test_pipeline", [step1, step2])
        
        result = pipeline.run("initial_input")
        
        assert isinstance(result, PipelineRun)
        assert len(result.steps) == 2
        
        step1_data = result.steps[0]
        step2_data = result.steps[1]
        
        assert step1_data["step_name"] == "step1"
        assert step1_data["input"] == "initial_input"
        assert step1_data["output"] == "step1_initial_input"
        
        assert step2_data["step_name"] == "step2"
        assert step2_data["input"] == "step1_initial_input"
        assert step2_data["output"] == "step2_step1_initial_input"
    
    def test_non_string_output(self):
        def step1_func(x):
            return 12345
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input")
        
        step_data = result.steps[0]
        assert step_data["output"] == 12345
        assert step_data["tokens_used"] == 0
    
    def test_trace_storage(self):
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        assert len(pipeline.traces) == 0
        
        pipeline.run("input1")
        assert len(pipeline.traces) == 1
        
        pipeline.run("input2")
        assert len(pipeline.traces)== 2
    
    def test_save_trace_file(self):
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        pipeline.run("input")
        
        trace_file = "test_pipeline_traces.yaml"
        assert os.path.exists(trace_file)
        
        with open(trace_file, "r") as f:
            content = yaml.safe_load(f)
        
        assert isinstance(content, list)
        assert len(content) == 1
        
        trace_data = content[0]
        assert "id" in trace_data
        assert "timestamp" in trace_data
        assert "steps" in trace_data
        assert "total_duration" in trace_data
    
    def test_run_appends_to_trace_file(self):
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        pipeline.run("input1")
        pipeline.run("input2")
        
        trace_file = "test_pipeline_traces.yaml"
        with open(trace_file, "r") as f:
            content = f.read()
        
        lines = content.split('\n')
        run_count = 0
        for line in lines:
            if line.strip().startswith('- id:'):
                run_count += 1
        assert run_count == 2
    
    @patch('builtins.input')
    def test_feedback_valid_rating(self, mock_input):
        mock_input.side_effect = ["4", "Good output"]
        
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input", human_feedback=True)
        
        step_data = result.steps[0]
        assert step_data["human_rating"] == 4
        assert step_data["human_comment"] == "Good output"
    
    @patch('builtins.input')
    def test_feedback_invalid_rating(self, mock_input):
        ## dont accept empty comments
        mock_input.side_effect = ["invalid", ""]
        
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input", human_feedback=True)
        
        step_data = result.steps[0]
        assert step_data["human_rating"] is None
        assert step_data["human_comment"] is None
    
    @patch('builtins.input')
    def test_feedback_skip_comment(self, mock_input):
        mock_input.side_effect = ["3", ""]
        
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input", human_feedback=True)
        
        step_data = result.steps[0]
        assert step_data["human_rating"] == 3
        assert step_data["human_comment"] is None
    
    @patch('builtins.input')
    def test_rating_out_of_range(self, mock_input):
        mock_input.side_effect = ["6", ""]
        
        def step1_func(x):
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, step1_func)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input", human_feedback=True)
        
        step_data = result.steps[0]
        assert step_data["human_rating"] is None
        assert step_data["human_comment"] is None
    
    def test_run_timing(self):
        def slow_step(x):
            import time
            time.sleep(0.01)
            return f"output_{x}"
        
        step1 = PipelineStep("step1", "transform", {}, slow_step)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input")
        
        assert result.total_duration >= 0.01
        
        step_data = result.steps[0]
        assert step_data["duration"] >= 0.01
    
    def test_token_counting_empty_string(self):
        def empty_step(x):
            return ""
        
        step1 = PipelineStep("step1", "transform", {}, empty_step)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input")
        
        step_data = result.steps[0]
        assert step_data["tokens_used"] == 0
        assert result.total_tokens == 0
    
    def test_token_counting_multiword_output(self):
        def multiword_step(x):
            return "This is a test output with multiple words"
        
        step1 = PipelineStep("step1", "transform", {}, multiword_step)
        pipeline = Pipeline("test_pipeline", [step1])
        
        result = pipeline.run("input")
        
        step_data = result.steps[0]
        assert step_data["tokens_used"] == 8
        assert result.total_tokens == 8

if __name__ == "__main__":
    pytest.main([__file__])