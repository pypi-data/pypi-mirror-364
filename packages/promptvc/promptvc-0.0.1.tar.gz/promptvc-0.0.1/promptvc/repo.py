import os
import hashlib
from datetime import datetime
from ruamel.yaml import YAML
from promptvc.diff import PromptDiff

class PromptVersion:
    def __init__(self, id, text, commit_msg, timestamp, hash):
        self.id = id
        self.text = text
        self.commit_msg = commit_msg
        self.timestamp = timestamp
        self.hash = hash

class PromptRepo:
    def __init__(self, path="."):
        self.repo_path = os.path.join(path, ".promptvc")
        self.prompts_dir = os.path.join(self.repo_path, "prompts")
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)
        self.yaml = YAML()
        self.diff_engine = PromptDiff()
        

    def _prompt_file(self, name):
        return os.path.join(self.prompts_dir, f"{name}.yaml")

    def _load_versions(self, name):
        file_path = self._prompt_file(name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = self.yaml.load(f)
            return data.get("versions", [])
        return []

    def _save_versions(self, name, versions):
        file_path = self._prompt_file(name)
        with open(file_path, "w") as f:
            self.yaml.dump({"versions": versions}, f)

    def add(self, name, text):
        if not text.strip():
            raise ValueError("Empty prompt text")
        versions = self._load_versions(name)
        new_id = len(versions) + 1
        hash_val = hashlib.sha1(text.encode()).hexdigest()
        versions.append({
            "id": new_id,
            "text": text,
            "commit_msg": "",
            "timestamp": datetime.now().isoformat(),
            "hash": hash_val
        })
        self._save_versions(name, versions)

    def commit(self, name, msg):
        versions = self._load_versions(name)
        if not versions:
            raise ValueError("No versions found")
        
        if versions[-1]["commit_msg"]:
            raise ValueError("Already committed")
        
        versions[-1]["commit_msg"] = msg
        self._save_versions(name, versions)

    def history(self, name):
        versions = self._load_versions(name)
        history = []
        for v in versions:
            version = PromptVersion(
                id=v["id"],
                text=v["text"], 
                commit_msg=v["commit_msg"],
                timestamp=v["timestamp"],
                hash=v["hash"]
            )
            history.append(version)
        return history

    def checkout(self, name, version_id):
        versions = self._load_versions(name)
        for v in versions:
            if v["id"] == version_id:
                return v["text"]
        return None

    def diff(self, name, v1_id, v2_id):
        versions = self._load_versions(name)
        v1 = None
        v2 = None

        for v in versions:
            if v["id"] == v1_id:
                v1 = v["text"]
            if v["id"] == v2_id:
                v2 = v["text"]
        if v1 is None or v2 is None:
            raise ValueError("Invalid version IDs.")
        
        diff = self.diff_engine.text_diff(v1, v2)
        similarity = self.diff_engine.semantic_diff(v1, v2)
        return {"text_diff": diff, "semantic_similarity": similarity}

    def eval_versions(self, name, version_ids, samples, llm_func=None):
        versions = self._load_versions(name)
        results = {}
        
        for vid in version_ids:
            prompt_text = None
            for v in versions:
                if v["id"] == vid:
                    prompt_text = v["text"]
                    break
            
            if not prompt_text:
                continue
            
            outputs = []
            for sample in samples:
                try:
                    formatted_prompt = prompt_text.format(input=sample.get("input", ""))
                except KeyError:
                    formatted_prompt = f"{prompt_text}\n\nInput: {sample.get('input', '')}"
                
                if llm_func:
                    output = llm_func(formatted_prompt)
                else:
                    output = formatted_prompt
                
                outputs.append({
                    "input": sample["input"],
                    "formatted_prompt": formatted_prompt,
                    "output": output
                })
            
            total_length = 0
            for o in outputs:
                total_length += len(o["output"])
            avg_length = total_length / len(outputs) if outputs else 0
            
            results[vid] = {
                "outputs": outputs,
                "avg_length": avg_length
            }
        
        return results
    
    def length_ratio(self, old, new):
        if len(old) == 0 and len(new) == 0:
            return 1.0
        if len(old) == 0:
            return 0.0
        
        ratio = len(new) / len(old)
        return 1.0 - abs(1.0 - ratio)
    
    def set_baseline(self, name, version_id, samples, llm_func):
        results = self.eval_versions(name, [version_id], samples, llm_func)
        baseline_data = {
            "version_id": version_id,
            "outputs": results[version_id]["outputs"]
        }
        
        baseline_file = os.path.join(self.prompts_dir, f"{name}_baseline.yaml")
        with open(baseline_file, "w") as f:
            self.yaml.dump(baseline_data, f)

    def compare_to_baseline(self, name, version_id, samples, llm_func):
        baseline_file = os.path.join(self.prompts_dir, f"{name}_baseline.yaml")
        if not os.path.exists(baseline_file):
            raise ValueError("No baseline set")
        
        with open(baseline_file, "r") as f:
            baseline_data = self.yaml.load(f)
        
        new_results = self.eval_versions(name, [version_id], samples, llm_func)
        
        comparisons = []
        baseline_outputs = baseline_data["outputs"]
        new_outputs = new_results[version_id]["outputs"]
        
        for baseline, new in zip(baseline_outputs, new_outputs):
            similarity = self.diff_engine.semantic_diff(baseline["output"], new["output"])
            comparison = {
                "input": baseline["input"],
                "baseline_output": baseline["output"],
                "new_output": new["output"],
                "similarity": similarity
            }
            comparisons.append(comparison)
        
        total_similarity = 0
        for c in comparisons:
            total_similarity += c["similarity"]
        avg_similarity = total_similarity / len(comparisons) if comparisons else 0
        
        result = {
            "baseline_version": baseline_data["version_id"],
            "new_version": version_id,
            "avg_similarity": avg_similarity,
            "comparisons": comparisons
        }

        return result