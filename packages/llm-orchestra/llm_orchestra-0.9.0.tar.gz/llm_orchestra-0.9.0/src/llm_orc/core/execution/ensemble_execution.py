"""Ensemble execution with agent coordination."""

import asyncio
import time
from collections.abc import AsyncGenerator, Callable
from typing import Any

from llm_orc.agents.script_agent import ScriptAgent
from llm_orc.core.auth.authentication import CredentialStorage
from llm_orc.core.config.config_manager import ConfigurationManager
from llm_orc.core.config.ensemble_config import EnsembleConfig
from llm_orc.core.config.roles import RoleDefinition
from llm_orc.core.execution.agent_execution_coordinator import AgentExecutionCoordinator
from llm_orc.core.execution.agent_executor import AgentExecutor
from llm_orc.core.execution.dependency_analyzer import DependencyAnalyzer
from llm_orc.core.execution.dependency_resolver import DependencyResolver
from llm_orc.core.execution.input_enhancer import InputEnhancer
from llm_orc.core.execution.orchestration import Agent
from llm_orc.core.execution.results_processor import ResultsProcessor
from llm_orc.core.execution.streaming_progress_tracker import StreamingProgressTracker
from llm_orc.core.execution.usage_collector import UsageCollector
from llm_orc.core.models.model_factory import ModelFactory
from llm_orc.models.base import ModelInterface


class EnsembleExecutor:
    """Executes ensembles of agents and coordinates their responses."""

    def __init__(self) -> None:
        """Initialize the ensemble executor with shared infrastructure."""
        # Share configuration and credential infrastructure across model loads
        # but keep model instances separate for independent contexts
        self._config_manager = ConfigurationManager()
        self._credential_storage = CredentialStorage(self._config_manager)

        # Load performance configuration
        self._performance_config = self._config_manager.load_performance_config()

        # Performance monitoring hooks for Issue #27 visualization integration
        self._performance_hooks: list[Callable[[str, dict[str, Any]], None]] = []

        # Initialize extracted components
        self._model_factory = ModelFactory(
            self._config_manager, self._credential_storage
        )
        self._dependency_analyzer = DependencyAnalyzer()
        self._dependency_resolver = DependencyResolver(self._get_agent_role_description)
        self._input_enhancer = InputEnhancer()
        self._usage_collector = UsageCollector()
        self._results_processor = ResultsProcessor()
        self._streaming_progress_tracker = StreamingProgressTracker(
            self.register_performance_hook, self._remove_performance_hook
        )

        # Initialize execution coordinator with agent executor function
        # Use a wrapper to avoid circular dependency with _execute_agent_with_timeout
        async def agent_executor_wrapper(
            agent_config: dict[str, Any], input_data: str
        ) -> tuple[str, ModelInterface | None]:
            return await self._execute_agent(agent_config, input_data)

        self._execution_coordinator = AgentExecutionCoordinator(
            self._performance_config, agent_executor_wrapper
        )

        # Note: AgentOrchestrator not used in current simplified implementation

        # Keep existing agent executor for backward compatibility
        self._agent_executor = AgentExecutor(
            self._performance_config,
            self._emit_performance_event,
            self._resolve_model_profile_to_config,
            self._execute_agent_with_timeout,
            self._input_enhancer.get_agent_input,
        )

    async def _load_model_from_agent_config(
        self, agent_config: dict[str, Any]
    ) -> ModelInterface:
        """Delegate to model factory."""
        return await self._model_factory.load_model_from_agent_config(agent_config)

    def register_performance_hook(
        self, hook: Callable[[str, dict[str, Any]], None]
    ) -> None:
        """Register a performance monitoring hook for Issue #27 visualization."""
        self._performance_hooks.append(hook)

    def _remove_performance_hook(
        self, hook: Callable[[str, dict[str, Any]], None]
    ) -> None:
        """Remove a performance monitoring hook."""
        if hook in self._performance_hooks:
            self._performance_hooks.remove(hook)

    def _emit_performance_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit performance monitoring events to registered hooks."""
        for hook in self._performance_hooks:
            try:
                hook(event_type, data)
            except Exception:
                # Silently ignore hook failures to avoid breaking execution
                pass

    async def execute_streaming(
        self, config: EnsembleConfig, input_data: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Execute ensemble with streaming progress updates.

        Yields progress events during execution for real-time monitoring.
        Events include: execution_started, agent_progress, execution_completed.
        """
        # Use StreamingProgressTracker for streaming execution
        start_time = time.time()
        execution_task = asyncio.create_task(self.execute(config, input_data))

        async for event in self._streaming_progress_tracker.track_execution_progress(
            config, execution_task, start_time
        ):
            yield event

    async def execute(self, config: EnsembleConfig, input_data: str) -> dict[str, Any]:
        """Execute an ensemble and return structured results."""
        start_time = time.time()

        # Store agent configs for role descriptions
        self._current_agent_configs = config.agents

        # Initialize result structure using ResultsProcessor
        result = self._results_processor.create_initial_result(
            config.name, input_data, len(config.agents)
        )
        results_dict: dict[str, Any] = result["results"]

        # Reset usage collector for this execution
        self._usage_collector.reset()

        # Execute agents in phases: script agents first, then LLM agents
        has_errors = False
        context_data: dict[str, Any] = {}

        # Phase 1: Execute script agents to gather context
        context_data, script_errors = await self._execute_script_agents(
            config, input_data, results_dict
        )
        has_errors = has_errors or script_errors

        # Phase 2: Execute LLM agents with dependency-aware phasing
        llm_agent_errors = await self._execute_llm_agents(
            config, input_data, context_data, results_dict
        )
        has_errors = has_errors or llm_agent_errors

        # Get collected usage and finalize result using ResultsProcessor
        agent_usage = self._usage_collector.get_agent_usage()
        return self._results_processor.finalize_result(
            result, agent_usage, has_errors, start_time
        )

    async def _execute_agent(
        self, agent_config: dict[str, Any], input_data: str
    ) -> tuple[str, ModelInterface | None]:
        """Execute a single agent and return its response and model instance."""
        agent_type = agent_config.get("type", "llm")

        if agent_type == "script":
            # Execute script agent
            script_agent = ScriptAgent(agent_config["name"], agent_config)
            response = await script_agent.execute(input_data)
            return response, None  # Script agents don't have model instances
        else:
            # Execute LLM agent
            # Load role and model for this agent
            role = await self._load_role_from_config(agent_config)
            model = await self._model_factory.load_model_from_agent_config(agent_config)

            # Create agent
            agent = Agent(agent_config["name"], role, model)

            # Generate response
            response = await agent.respond_to_message(input_data)
            return response, model

    async def _load_role_from_config(
        self, agent_config: dict[str, Any]
    ) -> RoleDefinition:
        """Load a role definition from agent configuration."""
        agent_name = agent_config["name"]

        # Resolve model profile to get enhanced configuration
        enhanced_config = await self._resolve_model_profile_to_config(agent_config)

        # Use system_prompt from enhanced config if available, otherwise use fallback
        if "system_prompt" in enhanced_config:
            prompt = enhanced_config["system_prompt"]
        else:
            prompt = f"You are a {agent_name}. Provide helpful analysis."

        return RoleDefinition(name=agent_name, prompt=prompt)

    async def _resolve_model_profile_to_config(
        self, agent_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolve model profile and merge with agent config.

        Agent config takes precedence over model profile defaults.
        """
        enhanced_config = agent_config.copy()

        # If model_profile is specified, get its configuration
        if "model_profile" in agent_config:
            profiles = self._config_manager.get_model_profiles()

            profile_name = agent_config["model_profile"]
            if profile_name in profiles:
                profile_config = profiles[profile_name]
                # Merge profile defaults with agent config
                # (agent config takes precedence)
                enhanced_config = {**profile_config, **agent_config}

        return enhanced_config

    async def _load_role(self, role_name: str) -> RoleDefinition:
        """Load a role definition."""
        # For now, create a simple role
        # TODO: Load from role configuration files
        return RoleDefinition(
            name=role_name, prompt=f"You are a {role_name}. Provide helpful analysis."
        )

    async def _execute_script_agents(
        self,
        config: EnsembleConfig,
        input_data: str,
        results_dict: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Execute script agents and return context data and error status."""
        context_data = {}
        has_errors = False
        script_agents = [a for a in config.agents if a.get("type") == "script"]

        for agent_config in script_agents:
            try:
                # Resolve model profile to get enhanced configuration
                enhanced_config = await self._resolve_model_profile_to_config(
                    agent_config
                )
                timeout = enhanced_config.get("timeout_seconds") or (
                    self._performance_config.get("execution", {}).get(
                        "default_timeout", 60
                    )
                )
                agent_result, model_instance = await self._execute_agent_with_timeout(
                    agent_config, input_data, timeout
                )
                results_dict[agent_config["name"]] = {
                    "response": agent_result,
                    "status": "success",
                }
                # Store script results as context for LLM agents
                context_data[agent_config["name"]] = agent_result

                # Collect usage for script agents
                self._usage_collector.collect_agent_usage(
                    agent_config["name"], model_instance
                )
            except Exception as e:
                results_dict[agent_config["name"]] = {
                    "error": str(e),
                    "status": "failed",
                }
                has_errors = True

        return context_data, has_errors

    async def _execute_llm_agents(
        self,
        config: EnsembleConfig,
        input_data: str,
        context_data: dict[str, Any],
        results_dict: dict[str, Any],
    ) -> bool:
        """Execute LLM agents with dependency-aware phasing."""
        has_errors = False
        llm_agents = [a for a in config.agents if a.get("type") != "script"]

        # Prepare enhanced input for LLM agents
        # CLI input overrides config default_task when provided
        # Fall back to config.default_task or config.task (backward compatibility)
        if input_data and input_data.strip() and input_data != "Please analyze this.":
            # Use CLI input when explicitly provided
            task_input = input_data
        else:
            # Fall back to config default task (support both new and old field names)
            task_input = (
                getattr(config, "default_task", None)
                or getattr(config, "task", None)
                or input_data
            )
        enhanced_input = task_input
        if context_data:
            context_text = "\n\n".join(
                [f"=== {name} ===\n{data}" for name, data in context_data.items()]
            )
            enhanced_input = f"{task_input}\n\n{context_text}"

        # Use enhanced dependency analysis for multi-level execution
        if llm_agents:
            # Update input enhancer with current agent configs for role descriptions
            self._input_enhancer.update_agent_configs(llm_agents)
            dependency_analysis = (
                self._dependency_analyzer.analyze_enhanced_dependency_graph(llm_agents)
            )
            phases = dependency_analysis["phases"]

            # Execute each phase sequentially, with parallelization within each phase
            for phase_index, phase_agents in enumerate(phases):
                self._emit_performance_event(
                    "phase_started",
                    {
                        "phase_index": phase_index,
                        "phase_agents": [agent["name"] for agent in phase_agents],
                        "total_phases": len(phases),
                    },
                )

                # Determine input for this phase using DependencyResolver
                if phase_index == 0:
                    # First phase uses the base enhanced input
                    phase_input: str | dict[str, str] = enhanced_input
                else:
                    # Subsequent phases get enhanced input with dependencies
                    phase_input = (
                        self._dependency_resolver.enhance_input_with_dependencies(
                            enhanced_input, phase_agents, results_dict
                        )
                    )

                # Execute agents in this phase individually with proper coordination
                for agent_config in phase_agents:
                    try:
                        agent_name = agent_config["name"]
                        agent_start_time = time.time()

                        # Emit agent started event
                        self._emit_performance_event(
                            "agent_started",
                            {"agent_name": agent_name, "timestamp": agent_start_time},
                        )

                        # Get agent input
                        agent_input = self._input_enhancer.get_agent_input(
                            phase_input, agent_name
                        )

                        # Get timeout from enhanced config (same as script agents)
                        enhanced_config = await self._resolve_model_profile_to_config(
                            agent_config
                        )
                        timeout = enhanced_config.get("timeout_seconds") or (
                            self._performance_config.get("execution", {}).get(
                                "default_timeout", 60
                            )
                        )

                        # Execute agent with timeout coordination
                        coordinator = self._execution_coordinator
                        (
                            response,
                            model_instance,
                        ) = await coordinator.execute_agent_with_timeout(
                            agent_config, agent_input, timeout
                        )

                        # Store successful result
                        results_dict[agent_name] = {
                            "response": response,
                            "status": "success",
                        }

                        # Collect usage
                        self._usage_collector.collect_agent_usage(
                            agent_name, model_instance
                        )

                        # Emit agent completed event with duration
                        agent_end_time = time.time()
                        duration_ms = int((agent_end_time - agent_start_time) * 1000)
                        self._emit_performance_event(
                            "agent_completed",
                            {
                                "agent_name": agent_name,
                                "timestamp": agent_end_time,
                                "duration_ms": duration_ms,
                            },
                        )

                    except Exception as e:
                        # Handle agent failure
                        agent_name = agent_config["name"]
                        results_dict[agent_name] = {
                            "error": str(e),
                            "status": "failed",
                        }
                        has_errors = True

                        # Emit agent completed event with error
                        agent_end_time = time.time()
                        duration_ms = int((agent_end_time - agent_start_time) * 1000)
                        self._emit_performance_event(
                            "agent_completed",
                            {
                                "agent_name": agent_name,
                                "timestamp": agent_end_time,
                                "duration_ms": duration_ms,
                                "error": str(e),
                            },
                        )

                self._emit_performance_event(
                    "phase_completed",
                    {
                        "phase_index": phase_index,
                        "successful_agents": len(
                            [
                                a
                                for a in phase_agents
                                if results_dict.get(a["name"], {}).get("status")
                                == "success"
                            ]
                        ),
                        "failed_agents": len(
                            [
                                a
                                for a in phase_agents
                                if results_dict.get(a["name"], {}).get("status")
                                == "failed"
                            ]
                        ),
                    },
                )

        return has_errors

    async def _execute_agent_with_timeout(
        self, agent_config: dict[str, Any], input_data: str, timeout_seconds: int | None
    ) -> tuple[str, ModelInterface | None]:
        """Execute agent with timeout using the extracted coordinator."""
        return await self._execution_coordinator.execute_agent_with_timeout(
            agent_config, input_data, timeout_seconds
        )

    def _analyze_dependencies(
        self, llm_agents: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Analyze agent dependencies and return independent and dependent agents."""
        independent_agents = []
        dependent_agents = []

        for agent_config in llm_agents:
            dependencies = agent_config.get("depends_on", [])
            if dependencies and len(dependencies) > 0:
                dependent_agents.append(agent_config)
            else:
                independent_agents.append(agent_config)

        return independent_agents, dependent_agents

    def _get_agent_role_description(self, agent_name: str) -> str | None:
        """Get a human-readable role description for an agent."""
        # Try to find the agent in the current ensemble config
        if hasattr(self, "_current_agent_configs"):
            for agent_config in self._current_agent_configs:
                if agent_config["name"] == agent_name:
                    # Try model_profile first, then infer from name
                    if "model_profile" in agent_config:
                        profile = str(agent_config["model_profile"])
                        # Convert kebab-case to title case
                        return profile.replace("-", " ").title()
                    else:
                        # Convert agent name to readable format
                        return agent_name.replace("-", " ").title()

        # Fallback: convert name to readable format
        return agent_name.replace("-", " ").title()
