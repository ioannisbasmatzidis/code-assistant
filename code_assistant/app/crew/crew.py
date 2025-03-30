"""Developer crew module for managing AI agents and their interactions."""

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="attr-defined"
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class DevCrew:
    """Developer crew for managing AI agents and their tasks.

    This class manages a team of AI agents including a senior engineer and QA engineer,
    along with their associated tasks for code development and evaluation.
    """

    agents_config: dict[str, Any]
    tasks_config: dict[str, Any]

    llm = "vertex_ai/gemini-2.0-flash-001"

    @agent
    def senior_engineer_agent(self) -> Agent:
        """Create and configure the senior engineer agent"""
        return Agent(
            config=self.agents_config.get("senior_engineer_agent"),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )

    @agent
    def chief_qa_engineer_agent(self) -> Agent:
        """Create and configure the chief QA engineer agent."""
        return Agent(
            config=self.agents_config.get("chief_qa_engineer_agent"),
            allow_delegation=True,
            verbose=True,
            llm=self.llm,
        )

    @task
    def code_task(self) -> Task:
        """Create a task for code development."""
        return Task(
            config=self.tasks_config.get("code_task"),
            agent=self.senior_engineer_agent(),
        )

    @task
    def evaluate_task(self) -> Task:
        """Create a task for code evaluation."""
        return Task(
            config=self.tasks_config.get("evaluate_task"),
            agent=self.chief_qa_engineer_agent(),
        )

    @crew
    def crew(self) -> Crew:
        """Create the development crew with configured agents and tasks."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
