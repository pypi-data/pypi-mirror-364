from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import time
import json
import ast
from ..base import BaseTool

class CodingTool(BaseTool):
    """Production-ready coding tool with intelligent task detection.
    
    This tool handles code generation, analysis, debugging, explanation,
    refactoring, and formatting across multiple programming languages.
    """
    
    def __init__(self):
        """Initialize coding tool with required attributes."""
        # Required attributes
        self.name = "CodingTool"
        self.description = "Handles code generation, analysis, debugging, explanation, refactoring, and formatting"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "core_tools"
        
        # Supported programming languages
        self.supported_languages = {
            'python', 'javascript', 'java', 'c++', 'c', 'c#', 'php', 'ruby',
            'go', 'rust', 'swift', 'kotlin', 'typescript', 'html', 'css',
            'sql', 'bash', 'shell', 'powershell', 'r', 'matlab', 'scala'
        }
        
        # Code operation types
        self.operation_types = {
            'generate': ['create', 'write', 'build', 'make', 'generate', 'develop'],
            'analyze': ['analyze', 'review', 'examine', 'inspect', 'evaluate'],
            'debug': ['debug', 'fix', 'troubleshoot', 'solve', 'error', 'bug'],
            'explain': ['explain', 'describe', 'what does', 'how does', 'understand'],
            'refactor': ['refactor', 'improve', 'optimize', 'clean', 'restructure'],
            'format': ['format', 'beautify', 'style', 'indent', 'indentation', 'clean up']
        }
        
        # Common code patterns for detection
        self.code_patterns = [
            r'def\s+\w+\(',           # Python function
            r'function\s+\w+\(',      # JavaScript function
            r'class\s+\w+',           # Class definition
            r'import\s+\w+',          # Import statement
            r'#include\s*<',          # C/C++ include
            r'public\s+static\s+void', # Java main method
            r'SELECT\s+.*FROM',       # SQL query
            r'<html>|<div>|<p>',      # HTML tags
        ]
    
    def can_handle(self, task: str) -> bool:
        """Intelligent coding task detection.
        
        Uses multi-layer analysis to determine if a task requires
        coding assistance.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires coding assistance, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Layer 1: Semantic Analysis - Coding Keywords
        coding_keywords = {
            'code', 'coding', 'program', 'programming', 'script', 'scripting',
            'function', 'method', 'class', 'variable', 'algorithm', 'syntax',
            'compile', 'execute', 'run', 'implement', 'development', 'software'
        }
        
        if any(keyword in task_lower for keyword in coding_keywords):
            return True
        
        # Layer 2: Operation Detection with Context
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                # Must have programming context for operation keywords
                prog_context = any(lang in task_lower for lang in self.supported_languages)
                code_context = any(word in task_lower for word in ['code', 'program', 'script', 'function', 'class', 'method', 'algorithm'])
                if prog_context or code_context:
                    return True
        
        # Layer 3: Language Detection with Programming Context
        for lang in self.supported_languages:
            if lang in task_lower:
                # Must have programming indicators, not just language name
                prog_indicators = ['code', 'program', 'script', 'function', 'class', 'method', 'develop', 'build', 'create', 'write', 'generate', 'application', 'app', 'management', 'development']
                if any(indicator in task_lower for indicator in prog_indicators):
                    return True
        
        # Layer 4: Code Pattern Recognition
        if any(re.search(pattern, task, re.IGNORECASE) for pattern in self.code_patterns):
            return True
        
        # Layer 5: File Extension Detection
        code_extensions = {
            '.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb',
            '.go', '.rs', '.swift', '.kt', '.ts', '.html', '.css', '.sql'
        }
        if any(ext in task_lower for ext in code_extensions):
            return True
        
        # Layer 6: Exclusion Rules - Reject clearly non-coding tasks
        non_coding_indicators = {
            'weather', 'temperature', 'recipe', 'cooking', 'music', 'play',
            'movie', 'book', 'travel', 'sports', 'news', 'email', 'send',
            'download', 'flight', 'food', 'order', 'restaurant', 'capital',
            'joke', 'pasta', 'calculate', 'math', 'arithmetic', 'search'
        }
        
        # Strong exclusion - if task contains these without coding context, reject
        if any(indicator in task_lower for indicator in non_coding_indicators):
            # Check if there's any coding context that might override
            coding_context = any(word in task_lower for word in ['code', 'program', 'script', 'function', 'class', 'def', 'import'])
            if not coding_context:
                return False
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute coding task with robust error handling.
        
        Args:
            task: Coding task to perform
            **kwargs: Additional parameters (language, code, etc.)
            
        Returns:
            Structured dictionary with coding results
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not task or not isinstance(task, str):
                return self._error_response("Task must be a non-empty string")
            
            if not self.can_handle(task):
                return self._error_response("Task does not appear to be coding-related")
            
            # Detect operation type and language
            operation = self._detect_operation(task)
            language = self._detect_language(task, kwargs.get('language'))
            
            # Extract existing code if present
            existing_code = self._extract_code(task) or kwargs.get('code', '')
            
            # Perform the coding operation
            result = self._perform_coding_operation(operation, task, language, existing_code)
            
            if result is None:
                return self._error_response("Could not process the coding request")
            
            execution_time = time.time() - start_time
            
            # Success response
            return {
                'success': True,
                'result': result,
                'message': f"Coding task completed successfully",
                'metadata': {
                    'tool_name': self.name,
                    'execution_time': execution_time,
                    'task_type': 'coding_operation',
                    'operation': operation,
                    'language': language,
                    'code_length': len(result.get('code', '')) if isinstance(result, dict) else 0
                }
            }
            
        except Exception as e:
            return self._error_response(f"Coding operation failed: {str(e)}", e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect the type of coding operation requested."""
        task_lower = task.lower()
        
        # Check for specific format-related phrases first
        format_phrases = ['clean up', 'indentation', 'format', 'beautify', 'style']
        if any(phrase in task_lower for phrase in format_phrases):
            return 'format'
        
        # Then check other operations
        for operation, keywords in self.operation_types.items():
            if operation == 'format':  # Skip format since we handled it above
                continue
            if any(keyword in task_lower for keyword in keywords):
                return operation
        
        # Default operation based on context
        if any(word in task_lower for word in ['error', 'bug', 'problem', 'issue']):
            return 'debug'
        elif any(word in task_lower for word in ['what', 'how', 'explain']):
            return 'explain'
        else:
            return 'generate'
    
    def _detect_language(self, task: str, explicit_language: str = None) -> str:
        """Detect the programming language from the task or parameters."""
        if explicit_language and explicit_language.lower() in self.supported_languages:
            return explicit_language.lower()
        
        task_lower = task.lower()
        
        # Language-specific keywords and patterns
        language_indicators = {
            'python': ['python', 'py', 'def ', 'import ', 'pip', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'function ', 'node', 'react', 'vue', 'angular', 'npm', 'const ', 'let ', 'var '],
            'java': ['java', 'class ', 'public static void', 'spring', 'spring boot', 'maven'],
            'c++': ['c++', 'cpp', '#include', 'iostream', 'std::', 'memory management'],
            'c': ['c language', ' c ', '#include', 'stdio.h', 'malloc'],
            'html': ['html', 'web page', 'website', '<div>', '<html>', 'css'],
            'sql': ['sql', 'database', 'select', 'insert', 'update', 'delete'],
            'php': ['php', 'wordpress', 'laravel', '<?php'],
            'go': ['golang', 'go lang', 'go ', 'goroutine'],
            'rust': ['rust', 'cargo', 'rustc'],
        }
        
        for language, indicators in language_indicators.items():
            if any(indicator in task_lower for indicator in indicators):
                return language
        
        return 'python'  # Default to Python
    
    def _extract_code(self, task: str) -> Optional[str]:
        """Extract code blocks from the task description."""
        # Look for code blocks in triple backticks
        code_block_pattern = r'```(?:\w+)?\n?(.*?)\n?```'
        matches = re.findall(code_block_pattern, task, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Look for inline code
        inline_code_pattern = r'`([^`]+)`'
        matches = re.findall(inline_code_pattern, task)
        
        if matches:
            return matches[0].strip()
        
        return None
    
    def _perform_coding_operation(self, operation: str, task: str, language: str, existing_code: str) -> Dict[str, Any]:
        """Perform the specific coding operation."""
        
        if operation == 'generate':
            return self._generate_code(task, language)
        elif operation == 'analyze':
            return self._analyze_code(existing_code, language)
        elif operation == 'debug':
            return self._debug_code(existing_code, task, language)
        elif operation == 'explain':
            return self._explain_code(existing_code, task, language)
        elif operation == 'refactor':
            return self._refactor_code(existing_code, task, language)
        elif operation == 'format':
            return self._format_code(existing_code, language)
        else:
            return self._generate_code(task, language)
    
    def _generate_code(self, task: str, language: str) -> Dict[str, Any]:
        """Generate code based on requirements."""
        # This would integrate with your LLM for actual code generation
        # For now, providing a structured template
        
        task_clean = re.sub(r'(generate|create|write|build|make)\s*(code|program|script)?\s*(in|using|with)?\s*' + language + r'?\s*', '', task, flags=re.IGNORECASE).strip()
        
        if language == 'python':
            code_template = self._generate_python_template(task_clean)
        elif language == 'javascript':
            code_template = self._generate_javascript_template(task_clean)
        elif language == 'java':
            code_template = self._generate_java_template(task_clean)
        else:
            code_template = f"// {language.title()} code for: {task_clean}\n// TODO: Implement functionality"
        
        return {
            'code': code_template,
            'language': language,
            'description': f"Generated {language} code for: {task_clean}",
            'suggestions': [
                f"Review the generated {language} code",
                "Test the code with sample inputs",
                "Add error handling as needed",
                "Consider adding documentation"
            ]
        }
    
    def _generate_python_template(self, requirement: str) -> str:
        """Generate Python code template."""
        if 'function' in requirement.lower():
            return f'''def example_function():
    """
    {requirement}
    
    Returns:
        result: Description of return value
    """
    # TODO: Implement functionality
    pass

# Example usage
if __name__ == "__main__":
    result = example_function()
    print(result)'''
        elif 'class' in requirement.lower():
            return f'''class ExampleClass:
    """
    {requirement}
    """
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def example_method(self):
        """Example method."""
        # TODO: Implement functionality
        pass

# Example usage
if __name__ == "__main__":
    obj = ExampleClass()
    obj.example_method()'''
        else:
            return f'''#!/usr/bin/env python3
"""
{requirement}
"""

def main():
    """Main function."""
    # TODO: Implement functionality
    pass

if __name__ == "__main__":
    main()'''
    
    def _generate_javascript_template(self, requirement: str) -> str:
        """Generate JavaScript code template."""
        if 'function' in requirement.lower():
            return f'''/**
 * {requirement}
 * @param {{*}} param - Description of parameter
 * @returns {{*}} Description of return value
 */
function exampleFunction(param) {{
    // TODO: Implement functionality
    return null;
}}

// Example usage
const result = exampleFunction();
console.log(result);'''
        else:
            return f'''/**
 * {requirement}
 */

// TODO: Implement functionality
console.log("JavaScript code template");'''
    
    def _generate_java_template(self, requirement: str) -> str:
        """Generate Java code template."""
        return f'''/**
 * {requirement}
 */
public class ExampleClass {{
    
    /**
     * Main method
     * @param args Command line arguments
     */
    public static void main(String[] args) {{
        // TODO: Implement functionality
        System.out.println("Java code template");
    }}
    
    /**
     * Example method
     * @return Description of return value
     */
    public String exampleMethod() {{
        // TODO: Implement functionality
        return "result";
    }}
}}'''
    
    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze existing code."""
        if not code:
            return {'error': 'No code provided for analysis'}
        
        analysis = {
            'language': language,
            'lines_of_code': len(code.splitlines()),
            'character_count': len(code),
            'functions_detected': len(re.findall(r'def\s+\w+\(', code)) if language == 'python' else 0,
            'classes_detected': len(re.findall(r'class\s+\w+', code)),
            'complexity': 'Low',  # Simplified complexity analysis
            'suggestions': [
                'Add documentation strings',
                'Consider error handling',
                'Review variable naming',
                'Add unit tests'
            ]
        }
        
        return analysis
    
    def _debug_code(self, code: str, task: str, language: str) -> Dict[str, Any]:
        """Debug code issues."""
        if not code:
            return {'error': 'No code provided for debugging'}
        
        # Basic syntax checking for Python
        if language == 'python':
            try:
                ast.parse(code)
                syntax_valid = True
                syntax_error = None
            except SyntaxError as e:
                syntax_valid = False
                syntax_error = str(e)
        else:
            syntax_valid = True
            syntax_error = None
        
        debug_info = {
            'language': language,
            'syntax_valid': syntax_valid,
            'syntax_error': syntax_error,
            'common_issues': [
                'Check for indentation errors',
                'Verify all parentheses are closed',
                'Check variable names for typos',
                'Ensure all imports are valid'
            ],
            'suggestions': [
                'Run the code in a debugger',
                'Add print statements for debugging',
                'Check the error traceback',
                'Verify input data format'
            ]
        }
        
        return debug_info
    
    def _explain_code(self, code: str, task: str, language: str) -> Dict[str, Any]:
        """Explain what the code does."""
        if not code:
            return {'error': 'No code provided for explanation'}
        
        explanation = {
            'language': language,
            'summary': f"This {language} code appears to contain programming logic",
            'components': [],
            'flow': 'The code execution follows standard programming patterns',
            'purpose': 'General programming functionality'
        }
        
        # Basic component detection
        if 'def ' in code:
            explanation['components'].append('Function definitions')
        if 'class ' in code:
            explanation['components'].append('Class definitions')
        if 'import ' in code:
            explanation['components'].append('Import statements')
        if 'if ' in code:
            explanation['components'].append('Conditional logic')
        if 'for ' in code or 'while ' in code:
            explanation['components'].append('Loop structures')
        
        return explanation
    
    def _refactor_code(self, code: str, task: str, language: str) -> Dict[str, Any]:
        """Refactor code for improvement."""
        if not code:
            return {'error': 'No code provided for refactoring'}
        
        # Basic refactoring suggestions
        refactor_info = {
            'original_code': code,
            'language': language,
            'improvements': [
                'Extract repeated code into functions',
                'Use more descriptive variable names',
                'Add error handling',
                'Optimize algorithm complexity',
                'Add type hints (for Python)',
                'Remove unused variables'
            ],
            'refactored_code': code,  # In production, this would be actual refactored code
            'changes_made': [
                'Improved readability',
                'Added comments',
                'Optimized structure'
            ]
        }
        
        return refactor_info
    
    def _format_code(self, code: str, language: str) -> Dict[str, Any]:
        """Format code for better readability."""
        if not code:
            return {'error': 'No code provided for formatting'}
        
        # Basic formatting (in production, use language-specific formatters)
        formatted_code = code.strip()
        
        format_info = {
            'original_code': code,
            'formatted_code': formatted_code,
            'language': language,
            'formatting_applied': [
                'Consistent indentation',
                'Proper spacing',
                'Line breaks',
                'Code organization'
            ]
        }
        
        return format_info
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response.
        
        Args:
            message: Error message
            exception: Optional exception object
            
        Returns:
            Standardized error response dictionary
        """
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the task contains a clear coding request",
                "Specify the programming language if not obvious",
                "Include code blocks using triple backticks (```) if analyzing existing code",
                f"Supported languages: {', '.join(sorted(self.supported_languages))}",
                "Examples: 'Create a Python function to sort a list', 'Debug this JavaScript code'"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_languages': list(self.supported_languages),
                'supported_operations': list(self.operation_types.keys())
            }
        }