"""
Smart Orchestrator for Metis Agent.

This module provides intelligent execution coordination using multiple
strategies for optimal query processing. Works with any LLM provider
through the existing LLM interface.
"""
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from .models import (
    QueryAnalysis, ExecutionResult, ToolExecutionResult, 
    ExecutionStrategy, ExecutionError
)
from .llm_interface import get_llm
from ..tools.registry import get_tool


class SmartOrchestrator:
    """Orchestrator using existing LLM interface for intelligent execution coordination."""
    
    def __init__(self, tools_registry: Dict[str, Any] = None):
        """
        Initialize the orchestrator.
        
        Args:
            tools_registry: Registry of available tools (optional)
        """
        self.tools_registry = tools_registry or {}
    
    def _get_api_keys(self, config: Any) -> Dict[str, str]:
        """Get all available API keys from config."""
        api_keys = {}
        if config and hasattr(config, 'get_api_key'):
            # Common API key providers
            providers = ['google', 'openai', 'groq', 'anthropic', 'firecrawl', 'GOOGLE_SEARCH_ENGINE']
            for provider in providers:
                try:
                    key = config.get_api_key(provider)
                    if key:
                        api_keys[provider] = key
                        # Also add common variations
                        if provider == 'google':
                            api_keys['google_api_key'] = key
                        elif provider == 'GOOGLE_SEARCH_ENGINE':
                            api_keys['google_cx'] = key
                            api_keys['cx'] = key
                except Exception:
                    continue
        return api_keys
        
    def execute(
        self,
        analysis: QueryAnalysis,
        tools: Dict[str, Any],
        llm: Any,
        memory_context: str = "",
        session_id: Optional[str] = None,
        query: Optional[str] = None,
        system_message: Optional[str] = None,
        config: Optional[Any] = None
    ) -> ExecutionResult:
        """
        Execute query based on analysis results.
        
        Args:
            analysis: Query analysis with strategy and metadata
            tools: Available tools dictionary
            llm: LLM instance for direct responses
            memory_context: Memory context for enhanced responses
            session_id: Session identifier
            query: Original user query (extracted from analysis if not provided)
            
        Returns:
            ExecutionResult with response and metadata
        """
        start_time = time.time()
        
        # Extract query from analysis if not provided
        if query is None:
            query = getattr(analysis, 'query', 'Unknown query')
        
        # Set up context
        context = {
            'tools': tools or {},
            'llm': llm,
            'memory_context': memory_context,
            'session_id': session_id,
            'system_message': system_message,
            'config': config
        }
        
        # Generate planning files for complex queries
        planning_files = None
        
        # Handle both enum and string values
        complexity_value = analysis.complexity
        if hasattr(complexity_value, 'value'):
            complexity_value = complexity_value.value
        
        if hasattr(analysis, 'complexity') and complexity_value in ['complex', 'research']:
            try:
                planning_files = self._generate_planning_files(query, analysis, session_id)
                context['planning_files'] = planning_files
                # Initialize task tracking
                context['task_tracker'] = {
                    'planning_file': planning_files[0] if planning_files else None,
                    'task_file': planning_files[1] if planning_files else None,
                    'completed_tasks': [],
                    'current_step': 0
                }
            except Exception as e:
                # Don't fail execution if planning file generation fails
                context['planning_error'] = str(e)
        
        try:
            if analysis.strategy == ExecutionStrategy.DIRECT_RESPONSE:
                result = self._direct_response(query, context)
            elif analysis.strategy == ExecutionStrategy.SINGLE_TOOL:
                result = self._single_tool_execution(query, analysis, context)
            elif analysis.strategy == ExecutionStrategy.SEQUENTIAL:
                result = self._sequential_execution(query, analysis, context)
            elif analysis.strategy == ExecutionStrategy.PARALLEL:
                result = self._parallel_execution(query, analysis, context)
            elif analysis.strategy == ExecutionStrategy.ITERATIVE:
                result = self._iterative_execution(query, analysis, context)
            else:
                result = self._direct_response(query, context)
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                response=f"Execution error: {str(e)}",
                strategy_used='error_fallback',
                tools_used=[],
                execution_time=execution_time,
                confidence=0.1,
                metadata={'error': True, 'error_message': str(e)},
                error=str(e)
            )
    
    def _direct_response(self, query: str, context: Dict) -> ExecutionResult:
        """Direct response using existing LLM interface."""
        llm = get_llm()
        
        system_prompt = "You are a helpful AI assistant. Provide clear, accurate, and concise responses to user queries."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = llm.chat(messages)
        
        return ExecutionResult(
            response=response,
            strategy_used='direct_response',
            tools_used=[],
            execution_time=0.0,  # Will be set by caller
            confidence=0.9,
            metadata={'strategy': 'direct_response'}
        )
    
    def _single_tool_execution(
        self, 
        query: str, 
        analysis: QueryAnalysis, 
        context: Dict
    ) -> ExecutionResult:
        """Execute with single tool."""
        if not analysis.required_tools:
            return self._direct_response(query, context)
        
        tool_name = analysis.required_tools[0]
        
        # Get tool from registry
        try:
            if tool_name in self.tools_registry:
                tool = self.tools_registry[tool_name]
            else:
                tool_class = get_tool(tool_name)
                if tool_class:
                    tool = tool_class()  # Instantiate the tool class
                else:
                    tool = None
            
            if tool is None:
                return ExecutionResult(
                    response=f"Tool '{tool_name}' not found",
                    strategy_used='single_tool_error',
                    tools_used=[],
                    execution_time=0.0,
                    confidence=0.1,
                    metadata={'error': True, 'tool_error': 'Tool not found'},
                    error='Tool not found'
                )
        except Exception as e:
            return ExecutionResult(
                response=f"Tool '{tool_name}' not found: {str(e)}",
                strategy_used='single_tool_error',
                tools_used=[],
                execution_time=0.0,
                confidence=0.1,
                metadata={'error': True, 'tool_error': str(e)},
                error=str(e)
            )
        
        # Execute tool with API keys
        try:
            if hasattr(tool, 'execute'):
                # Get API keys from config
                api_keys = self._get_api_keys(context.get('config'))
                tool_result = tool.execute(query, **api_keys)
            else:
                tool_result = str(tool)  # Fallback
        except Exception as e:
            tool_result = f"Tool execution failed: {str(e)}"
        
        # Synthesize with LLM
        llm = get_llm()
        synthesis_prompt = f"""
        User Query: "{query}"
        Tool Used: {tool_name}
        Tool Result: {tool_result}
        
        Synthesize this information into a comprehensive, helpful response for the user.
        Focus on directly answering their question using the tool results.
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that synthesizes tool results into clear responses."},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        final_response = llm.chat(messages)
        
        return ExecutionResult(
            response=final_response,
            strategy_used='single_tool',
            tools_used=[tool_name],
            execution_time=0.0,
            confidence=analysis.confidence,
            metadata={
                'strategy': 'single_tool',
                'tool_results': {tool_name: tool_result}
            }
        )
    
    def _sequential_execution(
        self, 
        query: str, 
        analysis: QueryAnalysis, 
        context: Dict
    ) -> ExecutionResult:
        """Execute tools in sequence."""
        results = {}
        execution_log = []
        tools_used = []
        
        # Update planning status
        self._update_planning_status(context, "Starting sequential execution", f"Processing {len(analysis.required_tools)} tools")
        
        for i, tool_name in enumerate(analysis.required_tools):
            try:
                # Get tool
                if tool_name in self.tools_registry:
                    tool = self.tools_registry[tool_name]
                else:
                    tool_class = get_tool(tool_name)
                    if tool_class:
                        tool = tool_class()  # Instantiate the tool class
                    else:
                        tool = None
                
                if tool is None:
                    results[tool_name] = f"Error: Tool '{tool_name}' not found"
                    execution_log.append(f"Step {i+1}: {tool_name} not found")
                    self._update_task_progress(context, f"Execute {tool_name}", "failed - tool not found")
                    continue
                
                # Get planning guidance for current step
                planning_guidance = self._reference_planning_file(context, f"Step {i+1}: Execute {tool_name}")
                next_task = self._get_next_task(context)
                
                # Update task status - starting
                self._update_task_progress(context, f"Execute {tool_name}", "started")
                
                # Modify query based on previous results and planning guidance
                if i > 0:
                    context_prompt = f"Previous results: {json.dumps(results, indent=2)}\n\nPlanning guidance: {planning_guidance}\n\nNext task: {next_task}\n\nContinue with original query: {query}"
                else:
                    context_prompt = f"Planning guidance: {planning_guidance}\n\nNext task: {next_task}\n\nOriginal query: {query}"
                
                # Execute tool
                if hasattr(tool, 'execute'):
                    tool_result = tool.execute(context_prompt)
                else:
                    tool_result = str(tool)
                
                results[tool_name] = tool_result
                tools_used.append(tool_name)
                execution_log.append(f"Step {i+1}: Used {tool_name}")
                
                # Update task status - completed
                self._update_task_progress(context, f"Execute {tool_name}", "completed")
                self._update_task_progress(context, f"Process {tool_name} results", "completed")
                
            except Exception as e:
                results[tool_name] = f"Error: {str(e)}"
                execution_log.append(f"Step {i+1}: {tool_name} failed - {str(e)}")
                # Update task status - failed
                self._update_task_progress(context, f"Execute {tool_name}", f"failed - {str(e)}")
        
        # Update final synthesis task
        self._update_task_progress(context, "Integrate multiple tool outputs", "started")
        
        # Final synthesis
        llm = get_llm()
        synthesis_prompt = f"""
        User Query: "{query}"
        Execution Log: {execution_log}
        Tool Results: {json.dumps(results, indent=2)}
        
        Synthesize all these results into a comprehensive final response.
        Address the user's original query using insights from all tool executions.
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that synthesizes multiple tool results into coherent responses."},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        final_response = llm.chat(messages)
        
        # Update completion tasks
        self._update_task_progress(context, "Integrate multiple tool outputs", "completed")
        self._update_task_progress(context, "Generate final response", "completed")
        self._update_task_progress(context, "Quality check and validation", "completed")
        
        # Update final planning status
        self._update_planning_status(context, "Sequential execution completed", f"Successfully processed {len(tools_used)} tools")
        
        return ExecutionResult(
            response=final_response,
            strategy_used='sequential',
            tools_used=tools_used,
            execution_time=0.0,
            confidence=analysis.confidence,
            metadata={
                'strategy': 'sequential',
                'tool_results': results,
                'execution_log': execution_log
            }
        )
    
    def _parallel_execution(
        self, 
        query: str, 
        analysis: QueryAnalysis, 
        context: Dict
    ) -> ExecutionResult:
        """
        Execute tools in parallel (simulated since current architecture is sync).
        In future, this can be enhanced with actual async execution.
        """
        results = {}
        tools_used = []
        
        # For now, execute sequentially but treat as parallel conceptually
        for tool_name in analysis.required_tools:
            try:
                if tool_name in self.tools_registry:
                    tool = self.tools_registry[tool_name]
                else:
                    tool_class = get_tool(tool_name)
                    if tool_class:
                        tool = tool_class()  # Instantiate the tool class
                    else:
                        tool = None
                
                if hasattr(tool, 'execute'):
                    tool_result = tool.execute(query)
                else:
                    tool_result = str(tool)
                
                results[tool_name] = tool_result
                tools_used.append(tool_name)
                
            except Exception as e:
                results[tool_name] = f"Error: {str(e)}"
        
        # Synthesize results
        llm = get_llm()
        synthesis_prompt = f"""
        User Query: "{query}"
        Parallel Tool Results: {json.dumps(results, indent=2)}
        
        Synthesize these parallel results into a coherent, comprehensive response.
        Address any conflicts or redundancies in the results.
        Provide a unified answer to the user's query.
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that synthesizes parallel tool results into unified responses."},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        final_response = llm.chat(messages)
        
        return ExecutionResult(
            response=final_response,
            strategy_used='parallel',
            tools_used=tools_used,
            execution_time=0.0,
            confidence=analysis.confidence,
            metadata={
                'strategy': 'parallel',
                'tool_results': results
            }
        )
    
    def _iterative_execution(
        self, 
        query: str, 
        analysis: QueryAnalysis, 
        context: Dict
    ) -> ExecutionResult:
        """Iterative ReAct-style execution."""
        max_iterations = 3
        conversation_history = []
        tools_used = []
        llm = get_llm()
        
        current_query = query
        
        for iteration in range(max_iterations):
            # Reasoning step
            reasoning_prompt = f"""
            Original Query: {query}
            Current Task: {current_query}
            History: {conversation_history[-2:] if conversation_history else "None"}
            Available Tools: {analysis.required_tools}
            
            Think step by step:
            1. What have I accomplished so far?
            2. What do I still need to do?
            3. Should I use a tool or provide the final answer?
            4. If using a tool, which one and with what query?
            
            Respond in JSON format:
            {{
              "action": "use_tool" or "final_answer",
              "tool_name": "tool name if using tool",
              "tool_query": "query for tool if using tool",
              "reasoning": "your thinking process",
              "ready_for_final": true/false
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that reasons step by step and decides on actions."},
                {"role": "user", "content": reasoning_prompt}
            ]
            
            reasoning_response = llm.chat(messages)
            
            # Try to parse JSON response
            try:
                import re
                json_match = re.search(r'\{.*\}', reasoning_response, re.DOTALL)
                if json_match:
                    reasoning_result = json.loads(json_match.group())
                else:
                    reasoning_result = {"action": "final_answer", "reasoning": reasoning_response}
            except:
                reasoning_result = {"action": "final_answer", "reasoning": reasoning_response}
            
            conversation_history.append(f"Iteration {iteration + 1}: {reasoning_result.get('reasoning', 'Thinking...')}")
            
            if reasoning_result.get('action') == 'final_answer' or reasoning_result.get('ready_for_final'):
                # Generate final response
                final_prompt = f"""
                Original Query: "{query}"
                Conversation History: {conversation_history}
                Tools Used: {tools_used}
                
                Provide a comprehensive final answer to the original query.
                """
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant providing final answers based on reasoning and tool usage."},
                    {"role": "user", "content": final_prompt}
                ]
                
                final_response = llm.chat(messages)
                break
            
            elif reasoning_result.get('action') == 'use_tool':
                # Use the specified tool
                tool_name = reasoning_result.get('tool_name')
                tool_query = reasoning_result.get('tool_query', current_query)
                
                if tool_name in analysis.required_tools:
                    try:
                        if tool_name in self.tools_registry:
                            tool = self.tools_registry[tool_name]
                        else:
                            tool_class = get_tool(tool_name)
                            if tool_class:
                                tool = tool_class()  # Instantiate the tool class
                            else:
                                tool = None
                        
                        if hasattr(tool, 'execute'):
                            # Get API keys from config
                            api_keys = self._get_api_keys(context.get('config'))
                            tool_result = tool.execute(tool_query, **api_keys)
                        else:
                            tool_result = str(tool)
                        
                        tools_used.append(tool_name)
                        conversation_history.append(f"Tool {tool_name}: {tool_result[:200]}...")
                        current_query = f"Continue with: {query}. Latest info: {tool_result}"
                        
                    except Exception as e:
                        conversation_history.append(f"Tool {tool_name} failed: {str(e)}")
            
            else:
                # Fallback
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": current_query}
                ]
                final_response = llm.chat(messages)
                break
        
        else:
            # Max iterations reached
            final_prompt = f"Based on our analysis: {conversation_history}, provide final answer for: {query}"
            messages = [
                {"role": "system", "content": "You are a helpful assistant providing final answers."},
                {"role": "user", "content": final_prompt}
            ]
            final_response = llm.chat(messages)
        
        return ExecutionResult(
            response=final_response,
            strategy_used='iterative',
            tools_used=tools_used,
            execution_time=0.0,
            confidence=analysis.confidence * 0.9,
            metadata={
                'strategy': 'iterative',
                'conversation_history': conversation_history,
                'iterations': iteration + 1
            }
        )
    
    def _generate_planning_files(self, query: str, analysis: QueryAnalysis, session_id: str = None) -> tuple:
        """Generate planning and task MD files for complex queries."""
        # Create planning directory
        planning_dir = "planning_docs"
        os.makedirs(planning_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_prefix = f"{session_id}_" if session_id else ""
        
        # Generate planning file
        planning_file = f"{planning_dir}/{session_prefix}plan_{timestamp}.md"
        task_file = f"{planning_dir}/{session_prefix}tasks_{timestamp}.md"
        
        # Planning content
        planning_content = f"""# Query Planning Document
Generated: {datetime.now().isoformat()}
Session: {session_id or 'N/A'}

## Original Query
{query}

## Analysis Results
- **Complexity**: {analysis.complexity}
- **Strategy**: {analysis.strategy.value}
- **Confidence**: {analysis.confidence:.2f}
- **Required Tools**: {', '.join(analysis.required_tools)}

## Execution Plan
{self._generate_execution_plan(analysis)}

## Expected Outcomes
{self._generate_expected_outcomes(analysis)}
"""
        
        # Task breakdown
        task_content = f"""# Task Breakdown
Generated: {datetime.now().isoformat()}

## Main Objective
{query}

## Task List
{self._generate_task_list(analysis)}

## Tool Requirements
{self._generate_tool_requirements(analysis)}

## Success Criteria
{self._generate_success_criteria(analysis)}
"""
        
        # Write files
        with open(planning_file, 'w', encoding='utf-8') as f:
            f.write(planning_content)
        
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        
        return planning_file, task_file
    
    def _generate_execution_plan(self, analysis: QueryAnalysis) -> str:
        """Generate execution plan based on strategy."""
        strategy_plans = {
            ExecutionStrategy.DIRECT_RESPONSE: "Direct LLM response without tool usage",
            ExecutionStrategy.SINGLE_TOOL: f"Execute single tool: {analysis.required_tools[0] if analysis.required_tools else 'Unknown'}",
            ExecutionStrategy.SEQUENTIAL: f"Execute tools sequentially: {' -> '.join(analysis.required_tools)}",
            ExecutionStrategy.PARALLEL: f"Execute tools in parallel: {', '.join(analysis.required_tools)}",
            ExecutionStrategy.ITERATIVE: f"Iterative execution with tools: {', '.join(analysis.required_tools)}"
        }
        
        base_plan = strategy_plans.get(analysis.strategy, "Unknown execution strategy")
        
        return f"""### Strategy: {analysis.strategy.value}
{base_plan}

### Steps:
{self._generate_execution_steps(analysis)}
"""
    
    def _generate_execution_steps(self, analysis: QueryAnalysis) -> str:
        """Generate detailed execution steps."""
        if analysis.strategy == ExecutionStrategy.DIRECT_RESPONSE:
            return "1. Process query with LLM\n2. Return direct response"
        elif analysis.strategy == ExecutionStrategy.SINGLE_TOOL:
            tool_name = analysis.required_tools[0] if analysis.required_tools else "Unknown"
            return f"1. Initialize {tool_name}\n2. Execute tool with query\n3. Process and return results"
        elif analysis.strategy == ExecutionStrategy.SEQUENTIAL:
            steps = []
            for i, tool in enumerate(analysis.required_tools, 1):
                steps.append(f"{i}. Execute {tool}")
            steps.append(f"{len(steps) + 1}. Combine and synthesize results")
            return "\n".join(steps)
        elif analysis.strategy == ExecutionStrategy.PARALLEL:
            return f"1. Initialize all tools: {', '.join(analysis.required_tools)}\n2. Execute tools concurrently\n3. Collect and merge results\n4. Synthesize final response"
        elif analysis.strategy == ExecutionStrategy.ITERATIVE:
            return "1. Analyze query and determine first action\n2. Execute tool if needed\n3. Evaluate results and plan next step\n4. Repeat until completion\n5. Generate final response"
        else:
            return "1. Fallback to direct response"
    
    def _generate_expected_outcomes(self, analysis: QueryAnalysis) -> str:
        """Generate expected outcomes based on complexity and tools."""
        outcomes = []
        
        if analysis.complexity == 'complex':
            outcomes.append("- Comprehensive analysis with multiple data points")
            outcomes.append("- Detailed explanations and reasoning")
            outcomes.append("- Integration of multiple tool outputs")
        elif analysis.complexity == 'research':
            outcomes.append("- In-depth research findings")
            outcomes.append("- Multiple source validation")
            outcomes.append("- Structured research summary")
        else:
            outcomes.append("- Clear and concise response")
            outcomes.append("- Relevant information extraction")
        
        if 'GoogleSearchTool' in analysis.required_tools:
            outcomes.append("- Current web-based information")
        if 'CodeGenerationTool' in analysis.required_tools:
            outcomes.append("- Generated code solutions")
        if 'ContentGenerationTool' in analysis.required_tools:
            outcomes.append("- Generated content/documentation")
        
        return "\n".join(outcomes) if outcomes else "- Standard response output"
    
    def _generate_task_list(self, analysis: QueryAnalysis) -> str:
        """Generate task breakdown list."""
        tasks = []
        
        # Add analysis tasks
        tasks.append("- [ ] Query analysis and complexity assessment")
        tasks.append("- [ ] Strategy selection and tool identification")
        
        # Add tool-specific tasks
        for tool in analysis.required_tools:
            tasks.append(f"- [ ] Execute {tool}")
            tasks.append(f"- [ ] Process {tool} results")
        
        # Add synthesis tasks
        if len(analysis.required_tools) > 1:
            tasks.append("- [ ] Integrate multiple tool outputs")
        
        tasks.append("- [ ] Generate final response")
        tasks.append("- [ ] Quality check and validation")
        
        return "\n".join(tasks)
    
    def _generate_tool_requirements(self, analysis: QueryAnalysis) -> str:
        """Generate tool requirements and dependencies."""
        if not analysis.required_tools:
            return "No external tools required - direct LLM response"
        
        requirements = []
        for tool in analysis.required_tools:
            requirements.append(f"### {tool}")
            
            # Add tool-specific requirements
            if tool == 'GoogleSearchTool':
                requirements.append("- Internet connectivity required")
                requirements.append("- Google Custom Search API access")
            elif tool == 'CodeGenerationTool':
                requirements.append("- LLM access for code generation")
                requirements.append("- Programming language context")
            elif tool == 'ContentGenerationTool':
                requirements.append("- LLM access for content creation")
                requirements.append("- Content type specifications")
            elif tool == 'EnhancedProjectGeneratorTool':
                requirements.append("- File system write permissions")
                requirements.append("- Project template access")
            else:
                requirements.append("- Tool-specific configuration")
            
            requirements.append("")  # Add spacing
        
        return "\n".join(requirements)
    
    def _generate_success_criteria(self, analysis: QueryAnalysis) -> str:
        """Generate success criteria for the task."""
        criteria = [
            "- Query fully addressed and answered",
            "- All required information provided",
            "- Response is clear and well-structured"
        ]
        
        if analysis.complexity in ['complex', 'research']:
            criteria.append("- Multiple perspectives considered")
            criteria.append("- Comprehensive analysis provided")
        
        if len(analysis.required_tools) > 1:
            criteria.append("- All tool outputs successfully integrated")
        
        if 'GoogleSearchTool' in analysis.required_tools:
            criteria.append("- Current and relevant information included")
        
        if any(tool in analysis.required_tools for tool in ['CodeGenerationTool', 'ContentGenerationTool']):
            criteria.append("- Generated content meets quality standards")
        
        return "\n".join(criteria)
    
    def _update_task_progress(self, context: Dict, task_description: str, status: str = "completed"):
        """Update task progress in the task file."""
        task_tracker = context.get('task_tracker')
        if not task_tracker or not task_tracker.get('task_file'):
            return
        
        task_file = task_tracker['task_file']
        if not os.path.exists(task_file):
            return
        
        try:
            # Read current task file
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find and update the specific task
            lines = content.split('\n')
            updated_lines = []
            
            for line in lines:
                if task_description.lower() in line.lower() and '- [ ]' in line:
                    # Mark task as completed
                    updated_line = line.replace('- [ ]', '- [x]')
                    updated_lines.append(updated_line)
                    task_tracker['completed_tasks'].append(task_description)
                else:
                    updated_lines.append(line)
            
            # Add progress timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            progress_section = f"\n\n## Progress Updates\n- {timestamp}: {task_description} - {status}"
            
            # Check if progress section exists
            if "## Progress Updates" not in content:
                updated_lines.append(progress_section)
            else:
                # Add to existing progress section
                for i, line in enumerate(updated_lines):
                    if "## Progress Updates" in line:
                        updated_lines.insert(i + 1, f"- {timestamp}: {task_description} - {status}")
                        break
            
            # Write updated content
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            
            print(f"[TASK UPDATE] {task_description} - {status}")
            
        except Exception as e:
            print(f"[TASK UPDATE ERROR] Failed to update task progress: {e}")
    
    def _reference_planning_file(self, context: Dict, current_step: str) -> str:
        """Reference the planning file for current step guidance."""
        task_tracker = context.get('task_tracker')
        if not task_tracker or not task_tracker.get('planning_file'):
            return ""
        
        planning_file = task_tracker['planning_file']
        if not os.path.exists(planning_file):
            return ""
        
        try:
            with open(planning_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract relevant sections for current step
            guidance = f"\n=== PLANNING REFERENCE ===\n"
            guidance += f"Current Step: {current_step}\n"
            
            # Extract execution plan section
            if "## Execution Plan" in content:
                plan_start = content.find("## Execution Plan")
                plan_end = content.find("##", plan_start + 1)
                if plan_end == -1:
                    plan_section = content[plan_start:]
                else:
                    plan_section = content[plan_start:plan_end]
                guidance += f"\nExecution Plan:\n{plan_section}\n"
            
            # Extract expected outcomes
            if "## Expected Outcomes" in content:
                outcomes_start = content.find("## Expected Outcomes")
                outcomes_end = content.find("##", outcomes_start + 1)
                if outcomes_end == -1:
                    outcomes_section = content[outcomes_start:]
                else:
                    outcomes_section = content[outcomes_start:outcomes_end]
                guidance += f"\nExpected Outcomes:\n{outcomes_section}\n"
            
            guidance += "=== END PLANNING REFERENCE ===\n"
            return guidance
            
        except Exception as e:
            print(f"[PLANNING REFERENCE ERROR] Failed to read planning file: {e}")
            return ""
    
    def _get_next_task(self, context: Dict) -> str:
        """Get the next task from the task file."""
        task_tracker = context.get('task_tracker')
        if not task_tracker or not task_tracker.get('task_file'):
            return "Continue with execution"
        
        task_file = task_tracker['task_file']
        if not os.path.exists(task_file):
            return "Continue with execution"
        
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the first uncompleted task
            lines = content.split('\n')
            for line in lines:
                if '- [ ]' in line:
                    # Extract task description
                    task = line.replace('- [ ]', '').strip()
                    return task
            
            return "All tasks completed"
            
        except Exception as e:
            print(f"[NEXT TASK ERROR] Failed to get next task: {e}")
            return "Continue with execution"
    
    def _update_planning_status(self, context: Dict, status: str, details: str = ""):
        """Update the planning file with current execution status."""
        task_tracker = context.get('task_tracker')
        if not task_tracker or not task_tracker.get('planning_file'):
            return
        
        planning_file = task_tracker['planning_file']
        if not os.path.exists(planning_file):
            return
        
        try:
            # Read current planning file
            with open(planning_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add execution status section
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_update = f"\n\n## Execution Status\n- {timestamp}: {status}"
            if details:
                status_update += f"\n  Details: {details}"
            
            # Check if execution status section exists
            if "## Execution Status" not in content:
                content += status_update
            else:
                # Add to existing status section
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "## Execution Status" in line:
                        lines.insert(i + 1, f"- {timestamp}: {status}")
                        if details:
                            lines.insert(i + 2, f"  Details: {details}")
                        break
                content = '\n'.join(lines)
            
            # Write updated content
            with open(planning_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[PLANNING UPDATE] {status}")
            
        except Exception as e:
            print(f"[PLANNING UPDATE ERROR] Failed to update planning status: {e}")
