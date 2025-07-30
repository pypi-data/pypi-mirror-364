"""
SingleAgent class for Metis Agent.

This module provides the main agent class that orchestrates all components.
Now uses enhanced analysis-driven architecture.
"""
import os
import time
from typing import Dict, List, Any, Optional, Union
import json

from ..core.advanced_analyzer import AdvancedQueryAnalyzer
from ..core.smart_orchestrator import SmartOrchestrator
from ..core.response_synthesizer import ResponseSynthesizer
from ..core.models import QueryComplexity, ExecutionStrategy
from ..core.llm_interface import get_llm
from ..tools.registry import initialize_tools
from ..memory.sqlite_store import SQLiteMemory
from ..memory.titans.titans_adapter import TitansMemoryAdapter


class SingleAgent:
    """
    Main agent class that orchestrates all components using enhanced architecture.
    """
    
    def __init__(
        self,
        use_titans_memory: bool = True,
        tools: Optional[List[Any]] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        memory_path: Optional[str] = None,
        enhanced_processing: bool = True,
        config=None
    ):
        """
        Initialize the agent with enhanced architecture.
        
        Args:
            use_titans_memory: Whether to use Titans memory
            tools: List of tool instances to use (if None, uses all available tools)
            llm_provider: LLM provider to use (if None, uses config or auto-detects)
            llm_model: LLM model to use
            memory_path: Path to memory database
            enhanced_processing: Whether to use enhanced analysis-driven processing
            config: AgentConfig instance for configuration
        """
        # Store config for later use
        self.config = config
        
        # Set up LLM with config support
        from ..core.llm_interface import configure_llm, reset_llm
        
        # Reset LLM to ensure fresh configuration
        reset_llm()
        
        if llm_provider:
            # User specified a provider directly
            if llm_model:
                configure_llm(llm_provider, llm_model)
            else:
                configure_llm(llm_provider)
        # If no provider specified, get_llm() will use config or auto-detect
            
        self.llm = get_llm(config)
        
        # Set up system message from identity
        self.system_message = None
        if config and hasattr(config, 'agent_identity'):
            self.system_message = config.agent_identity.get_full_system_message()
        
        # Set up enhanced processing flag
        self.enhanced_processing = enhanced_processing
        
        # Set up enhanced components
        if self.enhanced_processing:
            self.analyzer = AdvancedQueryAnalyzer()
            self.orchestrator = SmartOrchestrator()
            self.synthesizer = ResponseSynthesizer()
            print("+ Enhanced analysis-driven processing enabled")
        
        # Set up memory
        if memory_path is None:
            memory_dir = os.path.join(os.getcwd(), "memory")
            os.makedirs(memory_dir, exist_ok=True)
            self.memory_path = os.path.join(memory_dir, "memory.db")
        else:
            self.memory_path = memory_path
            
        self.memory = SQLiteMemory(self.memory_path)
        
        # Set up Titans memory if enabled
        self.titans_memory_enabled = use_titans_memory
        self.titans_adapter = None
        
        if self.titans_memory_enabled:
            try:
                self.titans_adapter = TitansMemoryAdapter(self)
                print("+ Titans memory initialized")
            except Exception as e:
                print(f"- Error initializing Titans memory: {e}")
                self.titans_memory_enabled = False
        
        # Set up tools
        if tools is None:
            self.tools = initialize_tools()
        else:
            self.tools = {tool.__class__.__name__: tool for tool in tools}
            
        # Set up agent identity from config or defaults
        self.version = "0.2.0-enhanced"
        self.agent_version = self.version  # For backward compatibility
        
        if config and hasattr(config, 'agent_identity'):
            # Use identity system
            self.agent_name = config.agent_identity.agent_name
            self.agent_id = config.agent_identity.agent_id
            self.agent_creation_date = config.agent_identity.creation_timestamp
            print(f"+ {self.agent_name} ({self.agent_id}) v{self.version} initialized")
        else:
            # Fallback to defaults
            self.agent_name = "Metis Agent"
            self.agent_id = "metis-default"
            self.agent_creation_date = time.strftime("%Y-%m-%d")
            print(f"+ {self.agent_name} v{self.version} initialized")
        
    def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process a user query using enhanced architecture.
        
        Args:
            query: User query
            session_id: Session identifier
            tool_name: Name of tool to use (if None, selects automatically)
            
        Returns:
            Response as string or dictionary
        """
        if not query.strip():
            return "Query cannot be empty."
            
        # Generate session ID if not provided
        if session_id is None:
            session_id = f"session_{int(time.time())}"
            
        # Store query in memory
        self.memory.store_input(session_id, query)
        
        # Use enhanced processing if enabled
        if self.enhanced_processing:
            return self._process_with_enhanced_architecture(query, session_id, tool_name)
        else:
            # Fallback to basic processing (for backward compatibility)
            return self._process_basic(query, session_id, tool_name)
    
    def _process_with_enhanced_architecture(
        self,
        query: str,
        session_id: str,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process query using enhanced analysis-driven architecture.
        """
        try:
            # Step 1: Analyze query with available tools and registry
            available_tools = list(self.tools.keys())
            analysis = self.analyzer.analyze_query(
                query, 
                available_tools=available_tools, 
                tools_registry=self.tools
            )
            print(f"+ Query analysis: {analysis.complexity.value} complexity, {analysis.strategy.value} strategy")
            
            # Step 2: Get memory context (both basic and Titans)
            memory_context = ""
            
            # Get basic conversation history
            try:
                conversation_context = self.memory.get_context(session_id, query, limit=5)
                if conversation_context.strip():
                    memory_context += f"Recent conversation:\n{conversation_context}\n"
            except Exception as e:
                print(f"- Error getting conversation context: {e}")
            
            # Get Titans memory enhancement if enabled
            if self.titans_memory_enabled and self.titans_adapter:
                try:
                    enhancement = self.titans_adapter.enhance_query_processing(query, session_id)
                    titans_context = enhancement.get("enhanced_context", "")
                    if titans_context:
                        memory_context += f"\nAdaptive insights:\n{titans_context}"
                        print(f"+ Enhanced with {len(enhancement.get('relevant_memories', []))} memories")
                except Exception as e:
                    print(f"- Error enhancing with Titans memory: {e}")
            
            # Show context info
            if memory_context.strip():
                context_lines = len(memory_context.strip().split('\n'))
                print(f"+ Using conversation context ({context_lines} lines)")
                
            # Step 3: Execute using unified orchestrator
            system_message = self.get_system_message()
            execution_result = self.orchestrator.execute(
                analysis=analysis,
                tools=self.tools,
                llm=self.llm,
                memory_context=memory_context,
                session_id=session_id,
                query=query,
                system_message=system_message
            )
            
            # Step 4: Synthesize response
            final_response = self.synthesizer.synthesize_response(
                query=query,
                analysis=analysis,
                execution_result=execution_result,
                llm=self.llm,
                memory_context=memory_context,
                system_message=system_message
            )
            
            # Store response in memory
            response_text = final_response.get("response", str(final_response))
            self.memory.store_output(session_id, response_text)
            
            # Store in Titans memory if enabled
            if self.titans_memory_enabled and self.titans_adapter:
                try:
                    self.titans_adapter.store_response(query, response_text, session_id)
                except Exception as e:
                    print(f"Warning: Error storing in Titans memory: {e}")
            
            return final_response
            
        except Exception as e:
            print(f"Error in enhanced processing: {e}")
            # Fallback to basic processing
            return self._process_basic(query, session_id, tool_name)
    
    def _process_basic(
        self,
        query: str,
        session_id: str,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Basic processing for backward compatibility.
        """
        # Simple direct response using LLM
        conversation_context = self.memory.get_context(session_id)
        
        system_message = self.get_system_message()
        if conversation_context:
            system_content = f"{system_message}\n\nConversation history:\n{conversation_context}"
        else:
            system_content = system_message
            
        prompt = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.chat(prompt)
        self.memory.store_output(session_id, response)
        
        return response
    
    def set_system_message(self, message: str, layer: str = "custom"):
        """
        Set a system message for the agent.
        
        Args:
            message: System message content
            layer: Which layer to update ('base' or 'custom')
        """
        if self.config and hasattr(self.config, 'agent_identity'):
            # Use identity system
            if layer == "base":
                self.config.agent_identity.update_base_system_message(message)
            else:
                self.config.agent_identity.update_custom_system_message(message)
            # Update cached system message
            self.system_message = self.config.agent_identity.get_full_system_message()
        else:
            # Fallback to old method
            self.system_message = message
            if self.config:
                self.config.set("system_message", message)
    
    def get_system_message(self) -> str:
        """
        Get the current system message.
        
        Returns:
            Current system message
        """
        if self.system_message:
            return self.system_message
        
        # Fallback to identity system if available
        if self.config and hasattr(self.config, 'agent_identity'):
            return self.config.agent_identity.get_full_system_message()
        
        # Final fallback
        return f"You are {self.agent_name}, an advanced AI assistant. Answer questions accurately, concisely, and helpfully."
        
    def get_agent_identity(self) -> Dict[str, Any]:
        """
        Get agent identity information.
        
        Returns:
            Dictionary with agent identity information
        """
        identity_info = {
            "name": self.agent_name,
            "agent_id": getattr(self, 'agent_id', 'metis-default'),
            "version": self.agent_version,
            "creation_date": self.agent_creation_date,
            "capabilities": [
                "Question answering",
                "Task planning and execution",
                "Code generation",
                "Content creation",
                "Web search",
                "Web scraping"
            ],
            "tools": list(self.tools.keys()),
            "memory_enabled": True,
            "titans_memory_enabled": self.titans_memory_enabled
        }
        
        # Add full identity info if available
        if self.config and hasattr(self.config, 'agent_identity'):
            identity_info.update({
                "full_identity": self.config.agent_identity.get_identity_info(),
                "system_message_layers": {
                    "base": self.config.agent_identity.base_system_message[:100] + "..." if len(self.config.agent_identity.base_system_message) > 100 else self.config.agent_identity.base_system_message,
                    "custom": self.config.agent_identity.custom_system_message[:100] + "..." if self.config.agent_identity.custom_system_message and len(self.config.agent_identity.custom_system_message) > 100 else self.config.agent_identity.custom_system_message or "(not set)"
                }
            })
        
        return identity_info
        
    def get_memory_insights(self) -> Dict[str, Any]:
        """
        Get insights about the agent's memory.
        
        Returns:
            Dictionary with memory insights
        """
        insights = {
            "basic_memory": {
                "type": "SQLite",
                "path": self.memory_path
            }
        }
        
        if self.titans_memory_enabled and self.titans_adapter:
            try:
                titans_insights = self.titans_adapter.get_insights()
                insights["adaptive_memory"] = {
                    "type": "Titans",
                    "enabled": True,
                    "insights": titans_insights
                }
            except Exception as e:
                insights["adaptive_memory"] = {
                    "type": "Titans",
                    "enabled": True,
                    "error": str(e)
                }
        else:
            insights["adaptive_memory"] = {
                "type": "Titans",
                "enabled": False
            }
            
        return insights