"""
LLM Gateway Client
==================

Client for interacting with the AI Gateway for LLM-powered features.

This module provides functionality to:
    - Generate documentation using LLM analysis
    - Parse structured JSON responses from LLM
    - Handle streaming and non-streaming completions

Example:
    >>> from src.api.llm import LLMClient
    >>> client = LLMClient()
    >>> response = client.chat([{"role": "user", "content": "Hello"}])

Author: DevOps Transformation Team
"""

import os
import json
import re
import logging
import requests
from typing import Dict, List, Optional

import urllib3

# Disable SSL warnings for internal APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure module logger
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for AI Gateway LLM interactions.
    
    Provides methods for chat completions and structured response parsing.
    Used primarily for documentation generation and analysis.
    
    Attributes:
        DEFAULT_URL (str): Default AI Gateway endpoint
        DEFAULT_MODEL (str): Default LLM model to use
        DEFAULT_USER (str): Default user identifier
        
    Example:
        >>> client = LLMClient()
        >>> response = client.chat([
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "Analyze this code..."}
        ... ])
    """
    
    # Default Configuration
    DEFAULT_URL = "https://etiv-uat-dp1-gaip-api.ikp1002h-np.cloud.hk.hsbc/etiv-ssvc-aigateway-ea-chatcompletion-uat-internal-proxy/v1/api/v1/chat/completions"
    DEFAULT_MODEL = "Qwen3-32B-AWQ"
    DEFAULT_USER = "UC0004490"
    
    def __init__(
        self, 
        url: str = None, 
        model: str = None,
        token_env: str = "AM_TOKEN",
        timeout: int = 120
    ):
        """
        Initialize LLM Gateway client.
        
        Args:
            url: API endpoint URL. Defaults to internal gateway.
            model: LLM model name. Defaults to Qwen3-32B-AWQ.
            token_env: Environment variable name for auth token.
            timeout: Request timeout in seconds.
        
        Raises:
            ValueError: If authentication token is not found.
        """
        self.url = url or self.DEFAULT_URL
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        
        # Get authentication token from environment
        self.token = os.getenv(token_env)
        if not self.token:
            logger.warning(f"LLM token not found in {token_env} environment variable")
        
        logger.info(f"LLM client initialized with model: {self.model}")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Build request headers with authentication.
        
        Returns:
            Dictionary of HTTP headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        return headers
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> str:
        """
        Send chat completion request to LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0-1). Lower = more deterministic.
            max_tokens: Maximum tokens in response.
            stream: Whether to stream response.
            
        Returns:
            LLM response text.
            
        Raises:
            Exception: If API request fails.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "user": self.DEFAULT_USER
        }
        
        try:
            logger.debug(f"Sending chat request to LLM...")
            
            response = requests.post(
                self.url,
                headers=self._get_headers(),
                json=payload,
                verify=False,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response content
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0].get('message', {}).get('content', '')
                logger.debug(f"Received response: {len(content)} characters")
                return content
            
            logger.warning("No choices in LLM response")
            return ""
            
        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            raise Exception("LLM request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            raise Exception(f"LLM request failed: {e}")
    
    def extract_json(self, response_text: str) -> Dict:
        """
        Extract JSON object from LLM response.
        
        Handles responses that may include markdown code fences
        or additional text around the JSON.
        
        Args:
            response_text: Raw LLM response text.
            
        Returns:
            Parsed JSON as dictionary.
            
        Raises:
            ValueError: If no valid JSON found in response.
        """
        cleaned = response_text.strip()
        
        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
        
        # Find JSON object in response
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("LLM response did not contain a JSON object")
        
        candidate = match.group(0)
        
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response text: {candidate[:500]}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")
    
    def analyze_repository(
        self, 
        repo_name: str,
        repo_info: Dict,
        tree_paths: List[str],
        evidence_files: List[Dict]
    ) -> Optional[Dict]:
        """
        Analyze repository using LLM for documentation generation.
        
        Sends repository metadata, file tree, and evidence files to LLM
        for analysis and returns structured summary.
        
        Args:
            repo_name: Full repository name (org/repo).
            repo_info: Repository metadata from GitHub API.
            tree_paths: List of file paths in repository.
            evidence_files: List of evidence file dicts with path and content.
            
        Returns:
            Analysis dictionary with summary, components, tech stack, etc.
            None if analysis fails.
        """
        # Build evidence text
        evidence_blocks = []
        for item in evidence_files:
            evidence_blocks.append(f"FILE: {item['path']}\n```\n{item['content']}\n```")
        
        evidence_text = "\n\n".join(evidence_blocks) if evidence_blocks else "No evidence files available."
        
        # Limit tree paths for prompt
        tree_text = "\n".join(f"- {path}" for path in tree_paths[:50])
        if len(tree_paths) > 50:
            tree_text += f"\n... and {len(tree_paths) - 50} more files"
        
        # Build analysis prompt
        prompt = f"""Analyze repository `{repo_name}` and produce a compact, evidence-backed summary for documentation generation.

Repository metadata:
- name: {repo_info.get('name', 'Unknown')}
- description: {repo_info.get('description') or 'Not provided'}
- default branch: {repo_info.get('default_branch', 'main')}
- language: {repo_info.get('language') or 'Not specified'}

Repository tree snapshot:
{tree_text}

Curated evidence files:
{evidence_text}

Guidance:
- Use only repository evidence from the metadata, tree, and files above.
- Keep the summary compact and conservative.
- Prefer short bullet-sized findings over long explanations.
- If a detail is not supported, omit it.

Return strict JSON with this shape:
{{
  "summary": "short repo summary",
  "key_components": ["component summary"],
  "interfaces": ["api or interface summary"],
  "workflows": ["workflow summary"],
  "configuration": ["config summary"],
  "tech_stack": ["technology summary"]
}}
"""
        
        try:
            response = self.chat(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a technical documentation analyst. Analyze repositories and provide evidence-backed summaries."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            return self.extract_json(response)
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            return None
    
    def generate_documentation(self, repo_name: str, analysis: Dict) -> str:
        """
        Generate documentation markdown from analysis.
        
        Args:
            repo_name: Full repository name.
            analysis: Analysis dictionary from analyze_repository.
            
        Returns:
            Formatted markdown documentation string.
        """
        from datetime import datetime
        
        sections = []
        
        # Header
        sections.append(f"# Repository Documentation\n")
        sections.append(f"**Repository**: `{repo_name}`\n")
        sections.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Overview
        if analysis.get('summary'):
            sections.append("\n## Overview\n")
            sections.append(f"{analysis['summary']}\n")
        
        # Architecture
        if analysis.get('key_components'):
            sections.append("\n## Architecture\n")
            sections.append("\n### Key Components\n")
            for component in analysis['key_components']:
                sections.append(f"- {component}\n")
        
        # Tech Stack
        if analysis.get('tech_stack'):
            sections.append("\n## Tech Stack\n")
            for tech in analysis['tech_stack']:
                sections.append(f"- {tech}\n")
        
        # Interfaces
        if analysis.get('interfaces'):
            sections.append("\n## Interfaces & APIs\n")
            for interface in analysis['interfaces']:
                sections.append(f"- {interface}\n")
        
        # Workflows
        if analysis.get('workflows'):
            sections.append("\n## Workflows\n")
            for workflow in analysis['workflows']:
                sections.append(f"- {workflow}\n")
        
        # Configuration
        if analysis.get('configuration'):
            sections.append("\n## Configuration\n")
            for config in analysis['configuration']:
                sections.append(f"- {config}\n")
        
        # Footer
        sections.append("\n---\n")
        sections.append("*This documentation was generated automatically.*\n")
        
        return "".join(sections)
