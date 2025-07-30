import time
from datetime import datetime
import yaml

class PipelineTrace:
    def __init__(self, step_name, input_data, output, duration, tokens_used=0):
        self.step_name = step_name
        self.input = input_data
        self.output = output
        self.duration = duration
        self.tokens_used = tokens_used
        self.human_rating = None
        self.human_comment = None

class PipelineStep:
    def __init__(self, name, step_type, config, func):
        self.name = name
        self.type = step_type
        self.config = config
        self.func = func

class PipelineRun:
    def __init__(self, run_id, timestamp, steps, total_duration, total_tokens=None):
        self.id = run_id
        self.timestamp = timestamp
        self.steps = steps
        self.total_duration = total_duration
        self.total_tokens = total_tokens

class Pipeline:
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps
        self.traces = []

    def run(self, inputs, human_feedback=False):
        start_time = time.time()
        current_input = inputs
        run_traces = {}
        total_tokens = 0
        
        for step in self.steps:
            step_start = time.time()
            output = step.func(current_input)
            duration = time.time() - step_start
            
            if isinstance(output, str):
                tokens = len(output.split())
            else:
                tokens = 0
            total_tokens += tokens
            
            trace = PipelineTrace(
                step_name=step.name,
                input_data=current_input,
                output=output,
                duration=duration,
                tokens_used=tokens
            )
            
            if human_feedback:
                print(f"\nStep '{step.name}' output: {output}")
                rating = input("Rate this output (1-5, or skip): ")
                if rating.isdigit():
                    rating_num = int(rating)
                    if 1 <= rating_num <= 5:
                        trace.human_rating = rating_num
                        comment = input("Optional comment: ")
                        if comment.strip():
                            trace.human_comment = comment
            
            run_traces[step.name] = trace
            current_input = output
        
        total_duration = time.time() - start_time
        timestamp = datetime.now().isoformat()
        run_id = f"run_{timestamp}"
        
        step_data = []
        for trace in run_traces.values():
            step_data.append(trace.__dict__)
        
        run = PipelineRun(run_id, timestamp, step_data, total_duration, total_tokens)
        
        self.traces.append(run_traces)
        
        trace_file = f"{self.name}_traces.yaml"
        with open(trace_file, "a") as f:
            yaml.dump([run.__dict__], f)
        
        return run