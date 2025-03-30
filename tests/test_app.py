"""Tests for the Code Assistant application."""

import os
from pathlib import Path

import pytest
import streamlit as st

from code_assistant.config import Settings, get_settings


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock config file for testing."""
    config_content = """
google_vertex_ai:
  project: "test-project"
  location: "us-central1"
  model: "gemini-2.0-flash-001"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    return str(config_file)


def test_settings_load(mock_config):
    """Test that settings can be loaded from config file."""
    settings = Settings.load(mock_config)
    assert settings.google_vertex_ai.project == "test-project"
    assert settings.google_vertex_ai.location == "us-central1"
    assert settings.google_vertex_ai.model == "gemini-2.0-flash-001"


def test_get_settings(mock_config, monkeypatch):
    """Test that global settings can be retrieved."""
    monkeypatch.setattr("code_assistant.config.settings.settings", None)
    settings = get_settings(mock_config)
    assert settings.google_vertex_ai.project == "test-project"


def test_app_imports():
    """Test that all app modules can be imported without errors."""
    from code_assistant.app import app
    from code_assistant.app.agent import agent
    from code_assistant.app.crew.crew import DevCrew

    assert app is not None
    assert agent is not None
    assert DevCrew is not None
