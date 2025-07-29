import argparse
import time
import json
from typing import Optional

from octotools.models.initializer import Initializer
from octotools.models.planner import Planner
from octotools.models.memory import Memory
from octotools.models.executor import Executor
from octotools.models.utils import make_json_serializable_truncated

class Solver:
    def __init__(
        self,
        planner,
        memory,
        executor,
        output_types: str = "base,final,direct",
        max_steps: int = 10,
        max_time: int = 300,
        max_tokens: int = 4000,
        root_cache_dir: str = "cache",
        verbose: bool = True
    ):
        self.planner = planner
        self.memory = memory
        self.executor = executor
        self.max_steps = max_steps
        self.max_time = max_time
        self.max_tokens = max_tokens
        self.root_cache_dir = root_cache_dir
        self.output_types = output_types.lower().split(',')
        assert all(output_type in ["base", "final", "direct"] for output_type in self.output_types), "Invalid output type. Supported types are 'base', 'final', 'direct'."
        self.verbose = verbose
    def solve(self, question: str, image_path: Optional[str] = None):
        """
        Solve a single problem from the benchmark dataset.
        
        Args:
            index (int): Index of the problem to solve
        """
        # Update cache directory for the executor
        self.executor.set_query_cache_dir(self.root_cache_dir)

        # Initialize json_data with basic problem information
        json_data = {
            "query": question,
            "image": image_path
        }
        if self.verbose:
            print(f"\n==> 🔍 Received Query: {question}")
            if image_path:
                print(f"\n==> 🖼️ Received Image: {image_path}")

        # Generate base response if requested
        if 'base' in self.output_types:
            base_response = self.planner.generate_base_response(question, image_path, self.max_tokens)
            json_data["base_response"] = base_response
            if self.verbose:
                print(f"\n==> 📝 Base Response from LLM:\n\n{base_response}")

        # If only base response is needed, save and return
        if set(self.output_types) == {'base'}:
            return json_data
    
        # Continue with query analysis and tool execution if final or direct responses are needed
        if {'final', 'direct'} & set(self.output_types):
            if self.verbose:
                print(f"\n==> 🐙 Reasoning Steps from OctoTools (Deep Thinking...)")

            # [1] Analyze query
            query_start_time = time.time()
            query_analysis = self.planner.analyze_query(question, image_path)
            json_data["query_analysis"] = query_analysis
            if self.verbose:
                print(f"\n==> 🔍 Step 0: Query Analysis\n")
                print(f"{query_analysis}")
                print(f"[Time]: {round(time.time() - query_start_time, 2)}s")

            # Main execution loop
            step_count = 0
            action_times = []
            while step_count < self.max_steps and (time.time() - query_start_time) < self.max_time:
                step_count += 1
                step_start_time = time.time()

                # [2] Generate next step
                local_start_time = time.time()
                next_step = self.planner.generate_next_step(
                    question, 
                    image_path, 
                    query_analysis, 
                    self.memory, 
                    step_count, 
                    self.max_steps
                )
                context, sub_goal, tool_name = self.planner.extract_context_subgoal_and_tool(next_step)
                if self.verbose:
                    print(f"\n==> 🎯 Step {step_count}: Action Prediction ({tool_name})\n")
                    print(f"[Context]: {context}\n[Sub Goal]: {sub_goal}\n[Tool]: {tool_name}")
                    print(f"[Time]: {round(time.time() - local_start_time, 2)}s")

                if tool_name is None or tool_name not in self.planner.available_tools:
                    print(f"\n==> 🚫 Error: Tool '{tool_name}' is not available or not found.")
                    command = "No command was generated because the tool was not found."
                    result = "No result was generated because the tool was not found."

                else:
                    # [3] Generate the tool command
                    local_start_time = time.time()
                    tool_command = self.executor.generate_tool_command(
                        question, 
                        image_path, 
                        context, 
                        sub_goal, 
                        tool_name, 
                        self.planner.toolbox_metadata[tool_name]
                    )
                    analysis, explanation, command = self.executor.extract_explanation_and_command(tool_command)
                    if self.verbose:
                        print(f"\n==> 📝 Step {step_count}: Command Generation ({tool_name})\n")
                        print(f"[Analysis]: {analysis}\n[Explanation]: {explanation}\n[Command]: {command}")
                        print(f"[Time]: {round(time.time() - local_start_time, 2)}s")
                    
                    # [4] Execute the tool command
                    local_start_time = time.time()
                    result = self.executor.execute_tool_command(tool_name, command)
                    result = make_json_serializable_truncated(result) # Convert to JSON serializable format
                    if self.verbose:
                        print(f"\n==> 🛠️ Step {step_count}: Command Execution ({tool_name})\n")
                        print(f"[Result]:\n{json.dumps(result, indent=4)}")
                        print(f"[Time]: {round(time.time() - local_start_time, 2)}s")
                
                # Track execution time for the current step
                execution_time_step = round(time.time() - step_start_time, 2)
                action_times.append(execution_time_step)

                # Update memory
                self.memory.add_action(step_count, tool_name, sub_goal, command, result)
                memory_actions = self.memory.get_actions()

                # [5] Verify memory (context verification)
                local_start_time = time.time()
                stop_verification = self.planner.verificate_context(
                    question, 
                    image_path, 
                    query_analysis, 
                    self.memory
                )
                context_verification, conclusion = self.planner.extract_conclusion(stop_verification)
                if self.verbose:
                    conclusion_emoji = "✅" if conclusion == 'STOP' else "🛑"
                    print(f"\n==> 🤖 Step {step_count}: Context Verification\n")
                    print(f"[Analysis]: {context_verification}\n[Conclusion]: {conclusion} {conclusion_emoji}")
                    print(f"[Time]: {round(time.time() - local_start_time, 2)}s")
                
                # Break the loop if the context is verified
                if conclusion == 'STOP':
                    break

            # Add memory and statistics to json_data
            json_data.update({
                "memory": memory_actions,
                "step_count": step_count,
                "execution_time": round(time.time() - query_start_time, 2),
            })

            # Generate final output if requested
            if 'final' in self.output_types:
                final_output = self.planner.generate_final_output(question, image_path, self.memory)
                json_data["final_output"] = final_output
                print(f"\n==> 🐙 Detailed Solution:\n\n{final_output}")

            # Generate direct output if requested
            if 'direct' in self.output_types:
                direct_output = self.planner.generate_direct_output(question, image_path, self.memory)
                json_data["direct_output"] = direct_output
                print(f"\n==> 🐙 Final Answer:\n\n{direct_output}")

            print(f"\n[Total Time]: {round(time.time() - query_start_time, 2)}s")
            print(f"\n==> ✅ Query Solved!")

        return json_data

def construct_solver(llm_engine_name : str = "gpt-4o",
                     enabled_tools : list[str] = ["all"],
                     output_types : str = "final,direct",
                     max_steps : int = 10,
                     max_time : int = 300,
                     max_tokens : int = 4000,
                     root_cache_dir : str = "solver_cache",
                     verbose : bool = True,
                     vllm_config_path : str = None):
    
    # Instantiate Initializer
    initializer = Initializer(
        enabled_tools=enabled_tools,
        model_string=llm_engine_name,
        verbose=verbose,
        vllm_config_path=vllm_config_path,
    )

    # Instantiate Planner
    planner = Planner(
        llm_engine_name=llm_engine_name,
        toolbox_metadata=initializer.toolbox_metadata,
        available_tools=initializer.available_tools,
        verbose=verbose,
    )

    # Instantiate Memory
    memory = Memory()

    # Instantiate Executor
    executor = Executor(
        llm_engine_name=llm_engine_name,
        root_cache_dir=root_cache_dir,
        verbose=verbose,
    )

    # Instantiate Solver
    solver = Solver(
        planner=planner,
        memory=memory,
        executor=executor,
        output_types=output_types,
        max_steps=max_steps,
        max_time=max_time,
        max_tokens=max_tokens,
        root_cache_dir=root_cache_dir,
        verbose=verbose,
    )
    return solver

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the octotools demo with specified parameters.")
    parser.add_argument("--llm_engine_name", default="gpt-4o", help="LLM engine name.")
    parser.add_argument(
        "--output_types",
        default="base,final,direct",
        help="Comma-separated list of required outputs (base,final,direct)"
    )
    parser.add_argument("--enabled_tools", default="Generalist_Solution_Generator_Tool", help="List of enabled tools.")
    parser.add_argument("--root_cache_dir", default="solver_cache", help="Path to solver cache directory.")
    parser.add_argument("--max_tokens", type=int, default=4000, help="Maximum tokens for LLM generation.")
    parser.add_argument("--max_steps", type=int, default=10, help="Maximum number of steps to execute.")
    parser.add_argument("--max_time", type=int, default=300, help="Maximum time allowed in seconds.")
    parser.add_argument("--verbose", type=bool, default=True, help="Enable verbose output.")
    return parser.parse_args()
    
def main(args):
    solver = construct_solver(llm_engine_name=args.llm_engine_name, 
                              enabled_tools=args.enabled_tools, 
                              output_types=args.output_types, 
                              max_steps=args.max_steps, 
                              max_time=args.max_time, 
                              max_tokens=args.max_tokens, 
                              root_cache_dir=args.root_cache_dir,
                              verbose=args.verbose)

    # Solve the task or problem
    solver.solve("What is the capital of France?")

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
