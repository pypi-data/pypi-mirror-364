"""
Common module for Jama integration utilities for Unit Test management.
This module provides shared functionality for connecting to Jama and managing UT operations.
"""

import logging
import os
import re
import sys
import json
import traceback
from typing import Dict, List, Optional

from dotenv import load_dotenv
from py_jama_rest_client.client import APIException, JamaClient

load_dotenv()

# Jama configuration from environment variables
JAMA_URL = os.getenv("JAMA_URL")
JAMA_CLIENT_ID = os.getenv("JAMA_CLIENT_ID")
JAMA_CLIENT_PASSWORD = os.getenv("JAMA_CLIENT_PASSWORD")
JAMA_DEFAULT_PROJECT_ID = os.getenv("JAMA_DEFAULT_PROJECT_ID")

# Constants for Jama item types and relationship types
ITEM_TYPES = {
    'FOLDER': 32,
    'UNIT_TEST': 167
}

# Relationship types (based on your Jama configuration)
RELATIONSHIP_TYPES = {
    'VERIFICATION': 16,   # As specified in your original request
    'RELATED_TO': None,   # Default - don't specify type, let Jama use default
}

# Workflow status constants
WORKFLOW_STATUS_FIELD = 'workflow_status$167'  # Jama field name for workflow status (from item type fields)
WORKFLOW_STATUS_ACCEPTED = 'Accepted'     # Target status for unit tests

# Workflow status numeric values based on pick list configuration
WORKFLOW_STATUS_IDS = {
    'Draft': 639,
    'Review': 640,
    'Accepted': 641,
    'Rework': 642,
    'Deferred': 643,
    'Obsolete': 644,
    'Admin': 645
}

def get_status_name_from_id(status_id):
    """
    Get the status name from numeric ID for logging purposes.

    Args:
        status_id: Numeric status ID

    Returns:
        str: Status name or 'Unknown' if not found
    """
    for name, id_value in WORKFLOW_STATUS_IDS.items():
        if id_value == status_id:
            return name
    return f'Unknown({status_id})'

def determine_relationship_type_for_unit_test(req_item: Dict) -> Optional[int]:
    """
    Determine the appropriate relationship type for a requirement -> Unit Test relationship
    based on the relationship tables and item type.

    Args:
        req_item: The requirement item from Jama

    Returns:
        int or None: Relationship type ID, or None to use default
    """
    # Get item type information
    req_item_type = req_item.get('itemType')
    req_type_name = req_item.get('fields', {}).get('itemType', '').upper()

    # Alternative: check document key pattern for type identification
    doc_key = req_item.get('documentKey', '').upper()

    logging.info(f"Determining relationship type for item type: {req_item_type}, name: {req_type_name}, doc_key: {doc_key}")

    # Based on relationship tables:
    # Subsystem Requirement -> Unit Test = Verification
    if ('SUBSR' in req_type_name or 'SUBSYSTEM' in req_type_name or
        'SUBSR' in doc_key or any(pattern in doc_key for pattern in ['SUBSR', 'SUB-'])):
        logging.info("Detected Subsystem Requirement - using Verification relationship")
        return RELATIONSHIP_TYPES['VERIFICATION']

    # SW Item Design -> Unit Test = Related to (use default)
    elif ('SW' in req_type_name and 'ITEM' in req_type_name) or 'SWID' in doc_key:
        logging.info("Detected SW Item Design - using default relationship type")
        return RELATIONSHIP_TYPES['RELATED_TO']  # None = use default

    # System Requirement -> Unit Test = Verification (implied from tables)
    elif ('SYSTEM' in req_type_name or 'SYS' in req_type_name or
          any(pattern in doc_key for pattern in ['SYS-', 'SYSREQ', 'SYSTEM'])):
        logging.info("Detected System Requirement - using Verification relationship")
        return RELATIONSHIP_TYPES['VERIFICATION']

    # Test Plan -> Unit Test = Related to (use default)
    elif 'TEST' in req_type_name and 'PLAN' in req_type_name:
        logging.info("Detected Test Plan - using default relationship type")
        return RELATIONSHIP_TYPES['RELATED_TO']  # None = use default

    # Default case: use verification for safety (covers most requirement types)
    else:
        logging.info(f"Unknown item type - using Verification relationship as default")
        return RELATIONSHIP_TYPES['VERIFICATION']


class JamaConnectionError(Exception):
    """Custom exception for Jama connection issues."""
    pass


class JamaUTManager:
    """
    Manager class for Jama Unit Test operations.
    Handles UT creation, folder management, and relationship establishment.
    """

    def __init__(self):
        """Initialize the JamaUTManager with environment configuration."""
        self.jama_client: Optional[JamaClient] = None
        self.project_id = int(JAMA_DEFAULT_PROJECT_ID) if JAMA_DEFAULT_PROJECT_ID else None

        # Validate required environment variables
        if not all([JAMA_URL, JAMA_CLIENT_ID, JAMA_CLIENT_PASSWORD, JAMA_DEFAULT_PROJECT_ID]):
            raise JamaConnectionError("Jama environment variables are not properly set")

    def _normalize_jama_url(self, url: str) -> str:
        """
        Normalize Jama URL to full Jama Cloud URL format.

        Args:
            url: The raw URL from environment variable

        Returns:
            str: Normalized URL in Jama Cloud format
        """
        if not url:
            return url

        # Check if URL is already a full URL
        if url.startswith(('http://', 'https://')):
            return url

        # Check if it already has .jamacloud.com
        if '.jamacloud.com' in url:
            normalized_url = f"https://{url}" if not url.startswith('https://') else url
        else:
            normalized_url = f"https://{url}.jamacloud.com"

        logging.info(f"Normalized Jama URL: {url} -> {normalized_url}")
        return normalized_url

    def init_jama_client(self) -> JamaClient:
        """
        Initialize the Jama client with OAuth authentication.

        Returns:
            JamaClient: Initialized Jama client

        Raises:
            JamaConnectionError: If client initialization fails
        """
        try:
            normalized_url = self._normalize_jama_url(JAMA_URL)

            self.jama_client = JamaClient(
                normalized_url,
                credentials=(JAMA_CLIENT_ID, JAMA_CLIENT_PASSWORD),
                oauth=True
            )
            logging.info("Jama UT client initialized successfully")
            return self.jama_client
        except APIException as e:
            logging.exception(f"Failed to initialize Jama client: {e}")
            raise JamaConnectionError(f"Failed to initialize Jama client: {e}")

    def get_client(self) -> JamaClient:
        """
        Get the Jama client, initializing if necessary.

        Returns:
            JamaClient: The Jama client instance
        """
        if self.jama_client is None:
            self.init_jama_client()
        return self.jama_client

    def get_item_by_document_key(self, document_key: str, item_type: int = None) -> Optional[Dict]:
        """
        Retrieve an item from Jama by its document key using efficient search.
        If item_type is provided, only return if the item matches the type.

        Args:
            document_key: The document key to search for
            item_type: Optional Jama item type ID to filter (e.g., ITEM_TYPES['UNIT_TEST'])

        Returns:
            Dict or None: The item if found, None otherwise

        Raises:
            JamaConnectionError: If requirement ID doesn't exist (strict validation)
        """
        try:
            client = self.get_client()
            search_results = client.get_abstract_items(
                project=self.project_id,
                contains=[document_key]
            )
            for item in search_results:
                if item.get('documentKey') == document_key:
                    if item_type is None or item.get('itemType') == item_type:
                        return item
            return None
        except APIException as e:
            logging.error(f"Error retrieving item with document key '{document_key}': {e}")
            raise JamaConnectionError(f"Error retrieving item '{document_key}': {e}")
        except Exception as e:
            logging.error(f"Error retrieving item by document key '{document_key}': {e}")
            return None

    def validate_smlprep_set_359_exists(self) -> Dict:
        """
        Validate that SmlPrep-SET-359 exists and is accessible using efficient search.
        This is the actual parent container where module folders like Richard are created.

        Returns:
            Dict: The SmlPrep-SET-359 item data

        Raises:
            JamaConnectionError: If SmlPrep-SET-359 doesn't exist
        """
        try:
            # Use efficient search for SmlPrep-SET-359
            client = self.get_client()
            search_results = client.get_abstract_items(
                project=self.project_id,
                contains=["SmlPrep-SET-359"]
            )

            # Look for exact match
            for item in search_results:
                if item.get('documentKey') == "SmlPrep-SET-359":
                    logging.info(f"Found SmlPrep-SET-359: {item['fields']['name']}")
                    return item

            raise JamaConnectionError("SmlPrep-SET-359 not found - cannot proceed with UT creation")
        except APIException as e:
            logging.error(f"Error validating SmlPrep-SET-359: {e}")
            raise JamaConnectionError("SmlPrep-SET-359 not found - cannot proceed with UT creation")

    def get_children_items(self, parent_id: int) -> Optional[List[Dict]]:
        """
        Get direct children of an item using REST API call.

        Args:
            parent_id: ID of the parent item

        Returns:
            List[Dict] or None: List of child items, or None if API call failed
        """
        try:
            client = self.get_client()
            # Access the underlying HTTP client like in IT integration code
            core = client._JamaClient__core

            # Debug: Show the URL being called
            url = f"items/{parent_id}/children"
            print(f"DEBUG: Calling REST API: GET {url}")

            response = core.get(url)

            print(f"DEBUG: Response status: {response.status_code}")

            if response.status_code == 200:
                children_data = response.json()
                print(f"DEBUG: Response keys: {list(children_data.keys())}")

                data = children_data.get('data', [])
                print(f"DEBUG: Data contains {len(data)} items")

                # Debug: Show first few items if any
                if data:
                    for i, item in enumerate(data[:3]):  # Show first 3 items
                        print(f"DEBUG: Item {i+1}: {item}")

                return data  # Return empty list if no children, but API succeeded
            else:
                print(f"DEBUG: Response text: {response.text}")
                logging.error(f"Failed to get children for item {parent_id}: {response.status_code} - {response.text}")
                return None  # Return None to indicate API failure

        except Exception as e:
            logging.error(f"Error getting children for item {parent_id} via REST API: {e}")
            print(f"DEBUG: Exception details: {e}")
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return None  # Return None to indicate API failure

    def get_children_items_by_location(self, parent_id: int) -> List[Dict]:
        """
        Get items under a parent using abstractitems search with location filtering.
        This is more reliable than the children endpoint for some Jama configurations.

        Args:
            parent_id: ID of the parent item

        Returns:
            List[Dict]: List of child items
        """
        try:
            client = self.get_client()

            print(f"DEBUG: Searching for items under parent {parent_id} using abstractitems")

            # Get all items in the project
            all_items = client.get_abstract_items(project=self.project_id)

            # Filter for items that have this parent
            children = []
            for item in all_items:
                item_parent = item.get('location', {}).get('parent')
                if item_parent == parent_id:
                    children.append(item)

            print(f"DEBUG: Found {len(children)} items under parent {parent_id}")

            return children

        except Exception as e:
            logging.error(f"Error getting children for item {parent_id} via location search: {e}")
            print(f"DEBUG: Exception details: {e}")
            return []

    def find_or_create_module_folder(self, module_name: str, parent_item: Dict) -> Dict:
        """
        Find or create a module folder under SmlPrep-SET-359 using location search.

        Args:
            module_name: Name of the module
            parent_item: SmlPrep-SET-359 container item data

        Returns:
            Dict: Module folder item data
        """
        try:
            client = self.get_client()
            parent_id = parent_item['id']

            print(f"DEBUG: Using SmlPrep-SET-359 ID {parent_id} for module folder search")

            # Try both methods: children API and location search
            children = self.get_children_items(parent_id)

            if not children:
                print("DEBUG: Children API returned 0, trying location search...")
                children = self.get_children_items_by_location(parent_id)

            # Look for existing module folder in direct children
            for child in children:
                if (child.get('fields', {}).get('name') == module_name and
                    child.get('itemType') == ITEM_TYPES['FOLDER']):
                    logging.info(f"Found existing module folder: {module_name}")
                    return child

            # Create new module folder if not found
            logging.info(f"Creating new module folder: {module_name}")

            # The issue was here - let's try different approaches
            print(f"DEBUG: Creating folder with:")
            print(f"    project: {self.project_id}")
            print(f"    item_type_id: {ITEM_TYPES['FOLDER']} (FOLDER)")
            print(f"    child_item_type_id: {ITEM_TYPES['UNIT_TEST']} (UNIT_TEST - what should go inside)")
            print(f"    location: {parent_id} (SmlPrep-SET-359)")

            result_id = client.post_item(
                project=self.project_id,
                item_type_id=ITEM_TYPES['FOLDER'],
                child_item_type_id=ITEM_TYPES['UNIT_TEST'],  # Changed: folder should contain unit tests, not folders
                location=parent_id,
                fields={
                    'name': module_name,
                    'description': f"Unit tests for {module_name} module"
                }
            )

            # Get the created item
            created_item = client.get_abstract_item(result_id)
            logging.info(f"Created module folder: {module_name} (ID: {result_id})")
            return created_item

        except APIException as e:
            logging.error(f"Error creating module folder '{module_name}': {e}")
            print(f"DEBUG: APIException details: {e}")
            raise JamaConnectionError(f"Failed to create module folder '{module_name}': {e}")

    def normalize_test_name(self, test_name: str) -> str:
        """
        Normalize test name for comparison by removing prefixes and suffixes.

        Args:
            test_name: Raw test name from parsing

        Returns:
            str: Normalized test name for comparison
        """
        # Remove "Test case: " prefix if present
        normalized = test_name
        if normalized.startswith("Test case: "):
            normalized = normalized[11:]  # Remove "Test case: "

        # Remove "Scenario: " prefix if present
        if normalized.startswith("Scenario: "):
            normalized = normalized[10:]  # Remove "Scenario: "

        # Remove status suffixes like " 🟢 PASS", " 🔴 FAIL", etc.
        # First remove emoji + status word combinations
        normalized = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', normalized)
        # Then remove lone emojis at the end
        normalized = re.sub(r'\s+[🟢🔴⚪]\s*$', '', normalized)

        # Apply general Unicode cleaning to ensure all emojis are removed
        normalized = clean_log_message(normalized)

        # Strip whitespace
        normalized = normalized.strip()

        return normalized

    def _create_test_description(self, test_content: Dict, covers_list: List[str] = None) -> str:
        """
        Create a detailed description for the unit test based on actual test content.

        Args:
            test_content: The parsed test content (scenario data)
            covers_list: List of requirement IDs that this test covers

        Returns:
            str: HTML-formatted description with actual test steps
        """
        description_parts = []

        # Handle structured test content (with Given-When-Then steps)
        if 'steps' in test_content:
            steps = test_content['steps']
            for step in steps:
                step_lines = []
                if 'given' in step:
                    # Remove status indicators from Given step
                    clean_given = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', step['given']).strip()
                    step_lines.append(f"<strong>Given:</strong> {clean_given}")
                if 'when' in step:
                    # Remove status indicators from When step
                    clean_when = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', step['when']).strip()
                    step_lines.append(f"<strong>When:</strong> {clean_when}")
                if 'then' in step:
                    # Remove status indicators from Then step
                    clean_then = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', step['then']).strip()
                    step_lines.append(f"<strong>Then:</strong> {clean_then}")

                # Add this step group to description with HTML formatting
                if step_lines:
                    description_parts.extend(step_lines)
                    description_parts.append("")  # Add blank line between step groups

        # Handle unstructured content (raw lines)
        elif 'raw_lines' in test_content:
            for line in test_content['raw_lines']:
                clean_line = line.strip()
                # Skip covers lines and empty lines
                if clean_line and not clean_line.lower().startswith('covers:'):
                    # Remove status indicators
                    clean_line = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', clean_line).strip()
                    if clean_line:
                        description_parts.append(clean_line)

        # Handle XML content
        elif 'xml_content' in test_content:
            description_parts.append("<strong>XML-based unit test</strong>")
            xml_data = test_content['xml_content']
            if isinstance(xml_data, dict):
                if 'name' in xml_data:
                    description_parts.append(f"<strong>Test Suite:</strong> {xml_data['name']}")
                if 'tests' in xml_data:
                    description_parts.append(f"<strong>Contains:</strong> {xml_data['tests']} test cases")

        # Join all parts with HTML line breaks and remove trailing empty lines
        if description_parts:
            # Remove empty trailing lines
            while description_parts and description_parts[-1] == "":
                description_parts.pop()

            # Convert to HTML with proper line breaks
            html_parts = []
            for part in description_parts:
                if part == "":
                    html_parts.append("<br><br>")  # Double line break for separation
                else:
                    html_parts.append(part)

            # Join with single line breaks
            description = "<br>".join(html_parts)
        else:
            description = "Automated unit test created from test report"

        # Add covers information if available
        if covers_list:
            description += f"<br><br><strong>Covers requirements:</strong> {', '.join(covers_list)}"

        return description

    def find_or_create_unit_test(self, test_name: str, module_folder: Dict, covers_list: List[str] = None, test_content: Dict = None) -> Dict:
        """
        Find existing unit test or create new one. Updates existing test if description has changed.
        If a UT ID is declared as the first covers_list entry but not found, raises JamaConnectionError and does not fallback to name-based search.

        Args:
            test_name: Name of the unit test
            module_folder: Module folder data from Jama
            covers_list: List of requirement document keys
            test_content: Test content for generating description

        Returns:
            Dict: Unit test item data
        Raises:
            JamaConnectionError: If a UT ID is declared but not found in Jama
        """
        try:
            covers_list = list(covers_list) if covers_list else []
            ut_id_used = False
            ut_id = None
            if covers_list and is_jama_ut_id(covers_list[0]):
                ut_id = covers_list.pop(0)
                ut_id_used = True
                logging.info(f"First covers_list entry '{ut_id}' is a Jama UT ID: searching for test by its ID instead of by name.")
                ut_item = self.get_item_by_document_key(ut_id, item_type=ITEM_TYPES['UNIT_TEST'])
                if ut_item:
                    expected_description = self._create_test_description(test_content, covers_list)
                    current_description = ut_item.get('fields', {}).get('description', '').strip()
                    clean_current = re.sub(r'<[^>]+>', '', current_description).strip()
                    clean_current = re.sub(r'\s+', ' ', clean_current).strip()
                    clean_expected = re.sub(r'<[^>]+>', '', expected_description).strip()
                    clean_expected = re.sub(r'\s+', ' ', clean_expected).strip()
                    if clean_current != clean_expected:
                        logging.info(f"UT ID {ut_id}: Description differs - updating via workflow transitions")
                        self.update_test_with_workflow_transitions(ut_item['id'], expected_description)
                        logging.info(f"UT ID {ut_id}: Description updated")
                    else:
                        logging.info(f"UT ID {ut_id}: Description matches - no update needed")
                    return ut_item
                else:
                    logging.error(f"UT ID {ut_id} declared in covers_list but not found in Jama. Skipping name-based search and raising error.")
                    raise JamaConnectionError(f"UT ID '{ut_id}' declared in covers_list but not found in Jama.")
            # Fallback to name-based search/create only if no UT ID declared
            normalized_test_name = self.normalize_test_name(test_name)
            clean_test_name = clean_log_message(test_name)
            clean_normalized_name = clean_log_message(normalized_test_name)
            logging.info(f"Looking for existing UT: '{clean_log_message(clean_normalized_name)}' (normalized from: '{clean_log_message(clean_test_name)}')")
            expected_description = self._create_test_description(test_content, covers_list)
            existing_unit_test = None
            children = self.get_children_items(module_folder['id'])
            if children is None:
                print("DEBUG: Children API failed, trying location search...")
                children = self.get_children_items_by_location(module_folder['id'])
            elif len(children) == 0:
                print(f"DEBUG: Folder is empty (no existing unit tests)")
                children = []
            for child in children:
                if child.get('itemType') == ITEM_TYPES['UNIT_TEST']:
                    existing_name = child.get('fields', {}).get('name', '').strip()
                    normalized_existing = self.normalize_test_name(existing_name)
                    print(f"Comparing: '{normalized_existing}' == '{normalized_test_name}'")
                    if normalized_existing == normalized_test_name:
                        existing_unit_test = child
                        logging.info(f"Found existing unit test: {clean_log_message(existing_name)}")
                        break
            if existing_unit_test:
                current_description = existing_unit_test.get('fields', {}).get('description', '').strip()
                clean_current = re.sub(r'<[^>]+>', '', current_description).strip()
                clean_current = re.sub(r'\s+', ' ', clean_current).strip()
                clean_expected = re.sub(r'<[^>]+>', '', expected_description).strip()
                clean_expected = re.sub(r'\s+', ' ', clean_expected).strip()
                if clean_current != clean_expected:
                    logging.info(f"Description differs - updating existing test")
                    logging.info(f"   Current (cleaned): {clean_current[:100]}...")
                    logging.info(f"   Expected (cleaned): {clean_expected[:100]}...")
                    self.update_test_with_workflow_transitions(existing_unit_test['id'], expected_description)
                    logging.info(f"Updated description for existing test: {existing_unit_test['id']}")
                    return existing_unit_test
                else:
                    logging.info(f"Description matches - no update needed")
                return existing_unit_test
            else:
                logging.info(f"Creating new unit test: {clean_log_message(normalized_test_name)}")
                client = self.get_client()
                result_id = client.post_item(
                    project=self.project_id,
                    item_type_id=ITEM_TYPES['UNIT_TEST'],
                    child_item_type_id=ITEM_TYPES['UNIT_TEST'],
                    location=module_folder['id'],
                    fields={
                        'name': normalized_test_name,
                        'description': expected_description
                    }
                )
                logging.info(f"Created unit test: {clean_log_message(normalized_test_name)} (ID: {result_id})")
                created_item = client.get_abstract_item(result_id)
                return created_item
        except Exception as e:
            logging.error(f"Error in find_or_create_unit_test: {e}")
            raise

    def create_verification_relationships(self, unit_test: Dict, covers_list: List[str]) -> bool:
        """
        Create relationships between unit test and requirements using Jama's default relationship type.
        Logs errors and continues processing. Raises exception at the end if any errors occurred.

        Args:
            unit_test: Unit test item data
            covers_list: List of requirement document keys from covers field

        Returns:
            bool: True if all valid relationships were created successfully

        Raises:
            JamaConnectionError: If any errors occurred during relationship creation
        """
        if not covers_list:
            logging.info("No covers requirements to process")
            return True

        try:
            client = self.get_client()
            unit_test_id = unit_test['id']
            successful_relationships = 0
            failed_requirements = []
            error_details = []

            logging.info(f"Creating relationships for {len(covers_list)} requirements")
            logging.info(f"Requirements list: {clean_log_message(', '.join(covers_list))}")

            for i, requirement_doc_key in enumerate(covers_list, 1):
                logging.info(f"Processing requirement {i}/{len(covers_list)}: {clean_log_message(requirement_doc_key)}")

                try:
                    # Check if requirement exists using efficient search
                    req_item = self.get_item_by_document_key(requirement_doc_key)

                    if not req_item:
                        error_msg = f"Requirement not found: {clean_log_message(requirement_doc_key)}"
                        logging.error(f"{i}/{len(covers_list)} {error_msg}")
                        failed_requirements.append(requirement_doc_key)
                        error_details.append(f"{requirement_doc_key}: not found in Jama")
                        continue

                    req_id = req_item['id']
                    req_item_type = req_item.get('itemType')
                    logging.info(f"{i}/{len(covers_list)} Found requirement {clean_log_message(requirement_doc_key)} (ID: {req_id}, Type: {req_item_type})")

                    # Determine relationship type based on item type and relationship tables
                    relationship_type = determine_relationship_type_for_unit_test(req_item)

                    relationship_params = {
                        'from_item': req_id,              # FROM: Requirement
                        'to_item': unit_test_id           # TO: Unit Test
                    }

                    # Add relationship type if specified (None means use default)
                    if relationship_type is not None:
                        relationship_params['relationship_type'] = relationship_type
                        logging.info(f"{i}/{len(covers_list)} Using relationship type: {relationship_type}")
                    else:
                        logging.info(f"{i}/{len(covers_list)} Using default relationship type")

                    # Try to create verification relationship (will fail if it already exists)
                    try:
                        # Temporarily suppress ERROR logging for "already exists" cases
                        jama_logger = logging.getLogger('py_jama_rest_client')
                        original_level = jama_logger.level
                        jama_logger.setLevel(logging.CRITICAL)

                        try:
                            relationship_id = client.post_relationship(**relationship_params)
                            jama_logger.setLevel(original_level)  # Restore logging level
                            logging.info(f"{i}/{len(covers_list)} Created relationship: {requirement_doc_key} -> UT (ID: {relationship_id})")
                            successful_relationships += 1

                        except APIException as api_e:
                            jama_logger.setLevel(original_level)  # Restore logging level

                            # Check if relationship already exists
                            if "already exists" in str(api_e).lower() or "duplicate" in str(api_e).lower():
                                logging.info(f"{i}/{len(covers_list)} Relationship already exists: {requirement_doc_key} -> UT")
                                successful_relationships += 1
                            else:
                                # Some other API error - this should be logged
                                error_msg = f"Failed to create relationship to {requirement_doc_key}: {api_e}"
                                logging.error(f"{i}/{len(covers_list)} {error_msg}")
                                failed_requirements.append(requirement_doc_key)
                                error_details.append(f"{requirement_doc_key}: API error - {str(api_e)}")
                                continue

                    except Exception as e:
                        # Restore logging level in case of unexpected exceptions
                        jama_logger.setLevel(original_level)
                        raise e

                except JamaConnectionError as e:
                    error_msg = f"Failed to process requirement {requirement_doc_key}: {e}"
                    logging.error(f"{i}/{len(covers_list)} {error_msg}")
                    failed_requirements.append(requirement_doc_key)
                    error_details.append(f"{requirement_doc_key}: connection error - {str(e)}")
                    continue

            # Summary
            total_requirements = len(covers_list)
            failed_count = len(failed_requirements)

            logging.info(f"Relationship creation summary:")
            logging.info(f"   Total requirements: {total_requirements}")
            logging.info(f"   Successful relationships: {successful_relationships}")

            if failed_count > 0:
                logging.error(f"   Failed requirements: {failed_count}")
                logging.error(f"   Failed requirement IDs: {', '.join(failed_requirements)}")

                # Create detailed error message
                error_summary = f"Failed to create relationships for {failed_count} out of {total_requirements} requirements:\n"
                for error in error_details:
                    error_summary += f"  - {error}\n"

                raise JamaConnectionError(error_summary.rstrip())

            return successful_relationships > 0 or total_requirements == 0

        except APIException as e:
            logging.error(f"Error creating verification relationships: {e}")
            raise JamaConnectionError(f"Failed to create verification relationships: {e}")

    def get_available_workflow_transitions(self, item_id: int) -> List[Dict]:
        """
        Get all available workflow transitions for a Jama item.

        Args:
            item_id: The ID of the Jama item

        Returns:
            List[Dict]: List of available transitions

        Raises:
            JamaConnectionError: If unable to retrieve transitions
        """
        try:
            client = self.get_client()
            core = client._JamaClient__core

            logging.info(f"Getting available workflow transitions for item {item_id}")
            transitions_url = f"items/{item_id}/workflowtransitionoptions"

            transitions_response = core.get(transitions_url)
            if transitions_response.status_code != 200:
                logging.error(f"Failed to get workflow transitions for item {item_id}: {transitions_response.status_code}")
                raise JamaConnectionError(f"Failed to get workflow transitions for item {item_id}: {transitions_response.status_code}")

            transitions_data = transitions_response.json()
            available_transitions = transitions_data.get('data', [])

            logging.info(f"Found {len(available_transitions)} available transitions for item {item_id}")

            # Log available transitions for debugging
            for transition in available_transitions:
                transition_id = transition.get('id')
                action = transition.get('action')
                new_status = transition.get('newStatus')
                new_status_name = get_status_name_from_id(new_status)
                logging.info(f"  Transition: {action} -> {new_status_name} (ID: {transition_id})")

            return available_transitions

        except Exception as e:
            logging.error(f"Error getting workflow transitions for item {item_id}: {e}")
            raise JamaConnectionError(f"Failed to get workflow transitions for item {item_id}: {e}")

    def change_item_status(self, item_id: int, target_status: str, comment: str = None) -> bool:
        """
        Change the workflow status of a Jama item to a target status using proper workflow transitions.

        This method uses the Jama REST API's workflow transition endpoints to properly
        respect workflow transition rules.

        Args:
            item_id: The ID of the Jama item to update
            target_status: The target status name (e.g., 'Accepted', 'Rework', 'Review', 'Draft')
            comment: Optional comment for the transition

        Returns:
            bool: True if status change was successful, False otherwise

        Raises:
            JamaConnectionError: If the status change fails
        """
        try:
            client = self.get_client()

            # First, get the current item to check its current status
            current_item = client.get_abstract_item(item_id)
            current_status_id = current_item.get('fields', {}).get(WORKFLOW_STATUS_FIELD, 'Unknown')

            current_status_name = get_status_name_from_id(current_status_id)
            logging.info(f"Current workflow status for item {item_id}: '{current_status_name}' (ID: {current_status_id})")

            # Check if target status is valid
            if target_status not in WORKFLOW_STATUS_IDS:
                raise JamaConnectionError(f"Invalid target status: {target_status}. Valid statuses: {list(WORKFLOW_STATUS_IDS.keys())}")

            target_status_id = WORKFLOW_STATUS_IDS[target_status]

            # If already in target state, no change needed
            if current_status_id == target_status_id:
                logging.info(f"Item {item_id} is already in '{target_status}' status - no change needed")
                return True

            # Get available workflow transitions
            available_transitions = self.get_available_workflow_transitions(item_id)

            # Execute transitions to reach target status
            return self._execute_transitions_to_status(item_id, target_status, available_transitions, comment)

        except APIException as e:
            logging.error(f"Failed to change workflow status for item {item_id}: {e}")
            raise JamaConnectionError(f"Failed to change workflow status for item {item_id}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error changing workflow status for item {item_id}: {e}")
            raise JamaConnectionError(f"Unexpected error changing workflow status for item {item_id}: {e}")

    def _execute_transitions_to_status(self, item_id: int, target_status: str, available_transitions: List[Dict], comment: str = None) -> bool:
        """
        Execute workflow transitions to reach a target status.

        Args:
            item_id: The ID of the Jama item
            target_status: The target status name
            available_transitions: List of available transitions from the API
            comment: Optional comment for transitions

        Returns:
            bool: True if transitions were successful

        Raises:
            JamaConnectionError: If no valid transition path is found or execution fails
        """
        # Create a map of transitions by action name for easy lookup
        transitions_by_action = {t.get('action'): t for t in available_transitions}

        # Define the transition path to reach target status
        # For Accepted: try direct transition first, then multi-step if needed
        transition_path = []

        if target_status == 'Accepted':
            # Check if we can go directly to Accepted
            if 'Accepted' in transitions_by_action:
                transition_path.append('Accepted')
            elif 'Review' in transitions_by_action:
                transition_path.append('Review')
                transition_path.append('Accepted')
        else:
            # For other statuses, try direct transition
            if target_status in transitions_by_action:
                transition_path.append(target_status)

        if not transition_path:
            logging.warning(f"No valid transition path found to reach {target_status} status for item {item_id}")
            logging.warning(f"Available transitions: {list(transitions_by_action.keys())}")
            raise JamaConnectionError(f"No valid transition path found to reach {target_status} status for item {item_id}")

        # Execute each transition in the path
        for i, action in enumerate(transition_path, 1):
            if action not in transitions_by_action:
                logging.error(f"Transition action '{action}' not available for item {item_id}")
                raise JamaConnectionError(f"Transition action '{action}' not available for item {item_id}")

            transition = transitions_by_action[action]
            transition_id = transition.get('id')

            logging.info(f"Step {i}: Executing transition '{action}' (ID: {transition_id}) for item {item_id}")

            try:
                # Execute the transition using the correct API structure
                client = self.get_client()
                core = client._JamaClient__core

                execute_url = f"items/{item_id}/workflowtransitions"
                transition_comment = comment or f"Automated transition to {action} status"
                body = {
                    "transitionId": transition_id,
                    "comment": transition_comment
                }
                headers = {'content-type': 'application/json'}

                execute_response = core.post(execute_url, data=json.dumps(body), headers=headers)

                # Accept both 200 and 201 as successful responses
                if execute_response.status_code not in [200, 201]:
                    logging.error(f"Failed to execute transition '{action}' for item {item_id}: {execute_response.status_code}")
                    logging.error(f"Response: {execute_response.text}")
                    raise JamaConnectionError(f"Failed to execute transition '{action}' for item {item_id}: {execute_response.status_code}")

                logging.info(f"Successfully executed transition '{action}' for item {item_id}")

                # If this wasn't the last transition, get updated transitions for the next step
                if i < len(transition_path):
                    logging.info(f"Getting updated transitions for next step...")
                    transitions_response = core.get(f"items/{item_id}/workflowtransitionoptions")
                    if transitions_response.status_code == 200:
                        updated_transitions_data = transitions_response.json()
                        available_transitions = updated_transitions_data.get('data', [])
                        transitions_by_action = {t.get('action'): t for t in available_transitions}

                        logging.info(f"Updated transitions available: {list(transitions_by_action.keys())}")

                        # Check if the next action in our path is still available
                        next_action = transition_path[i]
                        if next_action not in transitions_by_action:
                            logging.error(f"Next transition action '{next_action}' not available after executing '{action}'")
                            raise JamaConnectionError(f"Next transition action '{next_action}' not available after executing '{action}'")
                    else:
                        logging.warning(f"Failed to get updated transitions: {transitions_response.status_code}")
                        raise JamaConnectionError(f"Failed to get updated transitions: {transitions_response.status_code}")

            except JamaConnectionError:
                # Re-raise JamaConnectionError as-is
                raise
            except Exception as e:
                logging.error(f"Error executing transition '{action}' for item {item_id}: {e}")
                raise JamaConnectionError(f"Error executing transition '{action}' for item {item_id}: {e}")

        logging.info(f"Successfully completed all transitions to reach {target_status} status for item {item_id}")
        return True

    def change_item_status_to_accepted(self, item_id: int) -> bool:
        """
        Change the workflow status of a Jama item to 'Accepted' using proper workflow transitions.

        Args:
            item_id: The ID of the Jama item to update

        Returns:
            bool: True if status change was successful, False otherwise

        Raises:
            JamaConnectionError: If the status change fails
        """
        return self.change_item_status(item_id, 'Accepted', "Automated transition to Accepted status")

    def change_item_status_to_rework(self, item_id: int) -> bool:
        """
        Change the workflow status of a Jama item to 'Rework' using proper workflow transitions.

        Args:
            item_id: The ID of the Jama item to update

        Returns:
            bool: True if status change was successful, False otherwise

        Raises:
            JamaConnectionError: If the status change fails
        """
        return self.change_item_status(item_id, 'Rework', "Automated transition to Rework status for content update")

    def update_test_with_workflow_transitions(self, item_id: int, new_description: str) -> bool:
        """
        Update a test item following the proper workflow: Accepted -> Rework -> Update -> Accepted.

        This method handles the complete workflow for updating test content when the item
        is currently in Accepted status.

        Args:
            item_id: The ID of the Jama item to update
            new_description: The new description content

        Returns:
            bool: True if the complete workflow was successful

        Raises:
            JamaConnectionError: If any step in the workflow fails
        """
        try:
            client = self.get_client()

            # Get current item status
            current_item = client.get_abstract_item(item_id)
            current_status_id = current_item.get('fields', {}).get(WORKFLOW_STATUS_FIELD, 'Unknown')
            current_status_name = get_status_name_from_id(current_status_id)

            logging.info(f"Starting workflow update for item {item_id} (current status: {current_status_name})")

            # Step 1: If currently Accepted, transition to Rework
            if current_status_id == WORKFLOW_STATUS_IDS['Accepted']:
                logging.info(f"Item {item_id} is in Accepted status - transitioning to Rework")
                self.change_item_status_to_rework(item_id)
            elif current_status_id == WORKFLOW_STATUS_IDS['Rework']:
                logging.info(f"Item {item_id} is already in Rework status - proceeding with update")
            else:
                logging.info(f"Item {item_id} is in {current_status_name} status - proceeding with update")

            # Step 2: Update the test description
            logging.info(f"Updating description for item {item_id}")
            patch_data = [
                {
                    'op': 'replace',
                    'path': '/fields/description',
                    'value': new_description
                }
            ]

            updated_item = client.patch_item(item_id, patch_data)
            logging.info(f"Successfully updated description for item {item_id}")

            # Step 3: Transition back to Accepted status
            logging.info(f"Transitioning item {item_id} back to Accepted status")
            self.change_item_status_to_accepted(item_id)

            logging.info(f"Successfully completed workflow update for item {item_id}")
            return True

        except Exception as e:
            logging.error(f"Error in update_test_with_workflow_transitions for item {item_id}: {e}")
            raise JamaConnectionError(f"Failed to update test with workflow transitions: {e}")


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.

    Returns:
        bool: True if all variables are set, False otherwise
    """
    required_vars = [JAMA_URL, JAMA_CLIENT_ID, JAMA_CLIENT_PASSWORD, JAMA_DEFAULT_PROJECT_ID]
    if not all(required_vars):
        logging.error("Jama environment variables are not properly set")
        missing_vars = []
        if not JAMA_URL:
            missing_vars.append("JAMA_URL")
        if not JAMA_CLIENT_ID:
            missing_vars.append("JAMA_CLIENT_ID")
        if not JAMA_CLIENT_PASSWORD:
            missing_vars.append("JAMA_CLIENT_PASSWORD")
        if not JAMA_DEFAULT_PROJECT_ID:
            missing_vars.append("JAMA_DEFAULT_PROJECT_ID")

        logging.error(f"Missing variables: {', '.join(missing_vars)}")
        return False

    return True


def setup_logging(level: int = logging.INFO) -> None:
    """
    Setup logging configuration for UT operations.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def clean_log_message(message: str) -> str:
    """
    Remove Unicode characters (emojis and symbols) from log messages for CI/CD compatibility.

    Args:
        message: Original log message potentially containing Unicode characters

    Returns:
        str: Cleaned message with Unicode characters removed
    """
    # Remove common emoji and symbol Unicode ranges (more comprehensive)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs (includes 🟢🔴⚪)
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # miscellaneous symbols
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "]+",
        flags=re.UNICODE
    )

    # Remove emojis and extra whitespace
    cleaned = emoji_pattern.sub('', message).strip()

    # Remove specific status patterns that might remain
    cleaned = re.sub(r'\s+(PASS|FAIL|SKIP)\s*$', '', cleaned)

    # Remove any remaining non-ASCII characters that might cause issues
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)

    # Clean up multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return cleaned


def is_jama_ut_id(candidate: str) -> bool:
    """
    Returns True if the string matches the pattern <project>-UT-<ID> (e.g., SmlPrep-UT-213).
    """
    return bool(re.match(r"^[A-Za-z0-9]+-UT-\d+$", candidate.strip()))