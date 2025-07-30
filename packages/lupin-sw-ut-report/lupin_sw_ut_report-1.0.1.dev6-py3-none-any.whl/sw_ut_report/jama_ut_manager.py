"""
Jama Unit Test Manager - Orchestrates UT creation workflow.

This module handles the complete workflow for creating unit tests in Jama:
1. Validate SmlPrep-UT-1 exists
2. Find/create module folder
3. Find/create unit tests
4. Create verification relationships
"""

import logging
from typing import Dict, List, Optional

from sw_ut_report.jama_common import JamaUTManager, JamaConnectionError, validate_environment, clean_log_message


def dry_run_unit_tests_creation(module_name: str, test_results: List[Dict]) -> bool:
    """
    Dry-run function to analyze what would be done without making changes to Jama.
    Logs errors and continues processing. Raises exception at the end if any errors occurred.

    Args:
        module_name: Name of the module (for folder creation)
        test_results: List of parsed test results from TXT/XML files

    Returns:
        bool: True if analysis succeeded

    Raises:
        JamaConnectionError: If any errors occurred during validation
    """
    logging.info(f"=== DRY-RUN: Analyzing Jama UT Creation for Module: {module_name} ===")

    # Validate environment first
    if not validate_environment():
        print("ISSUE: Jama environment not properly configured")
        return False

    try:
        # Initialize Jama manager
        jama_manager = JamaUTManager()
        print("Jama connection: OK")

        # Step 1: Check SmlPrep-SET-359 exists
        print("\n=== STEP 1: Checking SmlPrep-SET-359 ===")
        try:
            smlprep_set_359 = jama_manager.validate_smlprep_set_359_exists()
            print(f"FOUND: SmlPrep-SET-359 exists - {smlprep_set_359['fields']['name']}")
            print(f"   ID: {smlprep_set_359['id']}")
        except JamaConnectionError as e:
            print(f"ISSUE: {e}")
            return False

        # Step 2: Check module folder status
        print(f"\n=== STEP 2: Checking Module Folder: {module_name} ===")
        module_folder = _dry_run_check_module_folder(jama_manager, module_name, smlprep_set_359)

        # Rest of the analysis remains the same...
        print(f"\n=== STEP 3: Analyzing Test Cases ===")
        planned_actions = []
        total_scenarios = 0

        for test_result in test_results:
            if test_result.get('type') == 'txt':
                scenarios = test_result.get('content', [])

                for scenario in scenarios:
                    total_scenarios += 1

                    # Extract test name and covers
                    if 'test_case' in scenario:
                        test_name = scenario['test_case']
                        covers_list = scenario.get('covers_list', [])
                        source_info = f"Structured TXT: {test_result.get('filename', 'Unknown')}"
                    elif 'raw_lines' in scenario:
                        # Unstructured scenario - extract test name from first meaningful line
                        filename = test_result.get('filename', 'Unknown')

                        # Try to extract test name from first meaningful line
                        test_name = filename.replace('.txt', '') if filename.endswith('.txt') else filename  # fallback

                        if scenario.get('raw_lines'):
                            for line in scenario['raw_lines']:
                                clean_line = line.strip()
                                # Skip empty lines and covers lines
                                if clean_line and not clean_line.lower().startswith('covers:'):
                                    # Remove status indicators and use as test name
                                    import re
                                    clean_test_name = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', clean_line).strip()
                                    if clean_test_name:
                                        test_name = clean_test_name
                                        break

                        covers_list = scenario.get('covers_list', [])
                        source_info = f"Unstructured TXT: {filename}"
                    else:
                        print(f"SKIP: Unknown scenario format in {test_result.get('filename')}")
                        continue

                    # --- NEW LOGIC: Scan covers_list for UT IDs ---
                    from sw_ut_report.jama_common import is_jama_ut_id
                    ut_ids = [c for c in covers_list if is_jama_ut_id(c)]
                    covers_list_no_ut = [c for c in covers_list if not is_jama_ut_id(c)]
                    if len(ut_ids) > 1:
                        # Multiple UT IDs: skip and warn
                        name_based_ut_warnings.append({
                            'document_keys': ut_ids,
                            'name': test_name,
                            'file_name': filename,
                            'error': 'Multiple UT IDs found in covers; only one is allowed.'
                        })
                        print(f"ERROR: Multiple UT IDs found in covers for test '{test_name}' in file '{filename}': {ut_ids}")
                        continue
                    elif len(ut_ids) == 1:
                        ut_id = ut_ids[0]
                        covers_list = covers_list_no_ut
                    else:
                        ut_id = None
                        covers_list = covers_list_no_ut
                    # --- END NEW LOGIC ---

                    # Analyze this test case
                    action = _dry_run_analyze_test_case(jama_manager, test_name, covers_list, source_info, module_folder, ut_id=ut_id)
                    planned_actions.append(action)

            elif test_result.get('type') == 'xml':
                total_scenarios += 1
                content = test_result.get('content', {})
                filename = test_result.get('filename', 'Unknown')
                test_name = content.get('name', filename.replace('.xml', '') if filename.endswith('.xml') else filename)
                covers_list = []
                source_info = f"XML: {filename}"

                # Analyze XML test case
                action = _dry_run_analyze_test_case(jama_manager, test_name, covers_list, source_info, module_folder)
                planned_actions.append(action)

        # Step 4: Summary Report
        print(f"\n=== DRY-RUN SUMMARY ===")
        print(f"📊 Module: {module_name}")
        print(f"📊 Total scenarios analyzed: {total_scenarios}")

        # Count actions
        new_tests = sum(1 for a in planned_actions if a['action'] == 'CREATE_TEST')
        existing_tests = sum(1 for a in planned_actions if a['action'] == 'EXISTS_TEST')
        new_relationships = sum(len(a['new_relationships']) for a in planned_actions)
        existing_relationships = sum(len(a['existing_relationships']) for a in planned_actions)

        print(f"📊 Unit tests to CREATE: {new_tests}")
        print(f"📊 Unit tests that EXIST: {existing_tests}")
        print(f"📊 Relationships to CREATE: {new_relationships}")
        print(f"📊 Relationships that EXIST: {existing_relationships}")
        print(f"📊 Status changes to 'Accepted': {total_scenarios}")  # All tests will have status changed

        # Detailed action report
        print(f"\n=== DETAILED ACTIONS ===")
        for i, action in enumerate(planned_actions, 1):
            print(f"\n{i}. {action['test_name']}")
            if action.get('original_test_name') != action['test_name']:
                print(f"   Original: {action['original_test_name']}")
            print(f"   Source: {action['source_info']}")

            if action['action'] == 'CREATE_TEST':
                print(f"   ACTION: Create new unit test")
            else:
                print(f"   EXISTS: Unit test already exists (ID: {action.get('existing_id', 'Unknown')})")

            if action['covers_list']:
                print(f"   Covers: {', '.join(action['covers_list'])}")

                if action['new_relationships']:
                    print(f"   Will create {len(action['new_relationships'])} new relationships:")
                    for rel in action['new_relationships']:
                        print(f"      -> {rel}")

                if action['existing_relationships']:
                    print(f"   {len(action['existing_relationships'])} relationships already exist:")
                    for rel in action['existing_relationships']:
                        print(f"      -> {rel}")

                if action['invalid_requirements']:
                    print(f"   {len(action['invalid_requirements'])} invalid requirements:")
                    for req in action['invalid_requirements']:
                        print(f"      -> {req} (NOT FOUND IN JAMA)")
            else:
                print(f"   No covers requirements")

            # Status change information
            print(f"   STATUS: Will change workflow status to 'Accepted'")

        # Check for issues
        has_issues = any(a['invalid_requirements'] for a in planned_actions)

        if has_issues:
            print(f"\nISSUES DETECTED:")
            print(f"   Some requirement IDs in 'covers' fields don't exist in Jama")
            print(f"   These will cause errors during execution")

            # Collect all invalid requirements for error reporting
            all_invalid_reqs = []
            for action in planned_actions:
                all_invalid_reqs.extend(action['invalid_requirements'])

            error_msg = f"Invalid requirements found during dry-run: {', '.join(set(all_invalid_reqs))}"
            logging.error(error_msg)

            from .jama_common import JamaConnectionError
            raise JamaConnectionError(error_msg)
        else:
            print(f"\nNO ISSUES DETECTED")
            print(f"   All requirements exist and operations look good!")
            return True

    except JamaConnectionError:
        raise
    except Exception as e:
        print(f"Unexpected error in dry-run analysis: {e}")
        return False


def _dry_run_check_module_folder(jama_manager: JamaUTManager, module_name: str, parent_item: Dict) -> Optional[Dict]:
    """Check if module folder exists without creating it under SmlPrep-SET-359."""
    try:
        parent_id = parent_item['id']

        print(f"DEBUG: Using SmlPrep-SET-359 ID {parent_id} for module folder search")

        # Try both methods: children API and location search
        children = jama_manager.get_children_items(parent_id)

        if not children:
            print("DEBUG: Children API returned 0, trying location search...")
            children = jama_manager.get_children_items_by_location(parent_id)

        print(f"DEBUG: Found {len(children)} children under SmlPrep-SET-359 (ID: {parent_id})")

        # Debug: Show all children
        for i, child in enumerate(children):
            child_name = child.get('fields', {}).get('name', 'NO_NAME')
            child_type = child.get('itemType', 'NO_TYPE')
            child_id = child.get('id', 'NO_ID')
            print(f"   {i+1}. {child_name} (Type: {child_type}, ID: {child_id})")

        # Look for existing module folder in direct children
        for child in children:
            child_name = child.get('fields', {}).get('name')
            child_type = child.get('itemType')

            print(f"Comparing: '{child_name}' == '{module_name}' AND {child_type} == 32")

            if (child_name == module_name and child_type == 32):  # FOLDER type
                print(f"FOUND: Module folder '{module_name}' already exists")
                print(f"   ID: {child['id']}")
                return child

        print(f"WILL CREATE: Module folder '{module_name}' under SmlPrep-SET-359")
        return {'id': 'NEW_FOLDER', 'fields': {'name': module_name}}  # Mock for analysis

    except Exception as e:
        print(f"Error checking module folder: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None


def _dry_run_analyze_test_case(jama_manager: JamaUTManager, test_name: str, covers_list: List[str],
                              source_info: str, module_folder: Optional[Dict], ut_id: str = None) -> Dict:
    """Analyze a single test case for dry-run without making changes. Accepts explicit ut_id if found."""
    covers_list = list(covers_list) if covers_list else []
    normalized_test_name = jama_manager.normalize_test_name(test_name)
    action = {
        'test_name': normalized_test_name,
        'original_test_name': test_name,
        'source_info': source_info,
        'covers_list': covers_list,
        'action': 'CREATE_TEST',
        'existing_id': None,
        'new_relationships': [],
        'existing_relationships': [],
        'invalid_requirements': []
    }
    if ut_id and hasattr(jama_manager, 'get_item_by_document_key'):
        from sw_ut_report.jama_common import ITEM_TYPES
        ut_item = jama_manager.get_item_by_document_key(ut_id, item_type=ITEM_TYPES['UNIT_TEST'])
        if ut_item:
            action['action'] = 'EXISTS_TEST'
            action['existing_id'] = ut_item['id']
        # else fallback to name-based search
    if not action['existing_id'] and module_folder and module_folder.get('id') != 'NEW_FOLDER':
        try:
            module_folder_id = module_folder['id']
            children = jama_manager.get_children_items(module_folder_id)
            if not children:
                children = jama_manager.get_children_items_by_location(module_folder_id)
            for child in children:
                if child.get('itemType') == 167:
                    existing_name = child.get('fields', {}).get('name', '').strip()
                    normalized_existing = jama_manager.normalize_test_name(existing_name)
                    print(f"DRY-RUN: Comparing '{normalized_existing}' == '{normalized_test_name}'")
                    if normalized_existing == normalized_test_name:
                        action['action'] = 'EXISTS_TEST'
                        action['existing_id'] = child['id']
                        print(f"DRY-RUN: Found existing test '{existing_name}' (ID: {child['id']})")
                        break
        except Exception as e:
            print(f"Error checking existing tests: {e}")
    if covers_list:
        for requirement_id in covers_list:
            try:
                req_item = jama_manager.get_item_by_document_key(requirement_id)
                if req_item:
                    action['new_relationships'].append(requirement_id)
                else:
                    action['invalid_requirements'].append(requirement_id)
            except JamaConnectionError:
                action['invalid_requirements'].append(requirement_id)
    return action


def create_unit_tests_in_jama(module_name: str, test_results: List[Dict]) -> bool:
    """
    Main function to create unit tests in Jama following the 4-step workflow.
    Logs errors and continues processing. Raises exception at the end if any errors occurred.

    Args:
        module_name: Name of the module (for folder creation)
        test_results: List of parsed test results from TXT/XML files

    Returns:
        bool: True if all operations succeeded

    Raises:
        JamaConnectionError: If any critical step fails or relationship creation errors occur
    """
    logging.info(f"=== Starting Jama UT Creation for Module: {module_name} ===")

    # Validate environment first
    if not validate_environment():
        raise JamaConnectionError("Jama environment not properly configured")

    try:
        # Initialize Jama manager
        jama_manager = JamaUTManager()
        logging.info("Jama UT Manager initialized successfully")

        # Step 1: Validate SmlPrep-SET-359 exists
        logging.info("=== Step 1: Validating SmlPrep-SET-359 ===")
        smlprep_set_359 = jama_manager.validate_smlprep_set_359_exists()

        # Step 2: Find or create module folder
        logging.info(f"=== Step 2: Finding/Creating Module Folder: {module_name} ===")
        module_folder = jama_manager.find_or_create_module_folder(module_name, smlprep_set_359)

        # Step 3 & 4: Process each test result
        logging.info("=== Step 3 & 4: Processing Test Cases ===")
        processed_count = 0
        total_scenarios = 0
        relationship_errors = []  # Track relationship creation failures
        status_change_errors = []  # Track status change failures
        name_based_ut_warnings = []  # Track UTs created/updated by name search (not by UT ID)
        ut_id_not_found_warnings = []  # Track UT IDs declared but not found

        # Helper function to check if a scenario or test result is empty

        def is_scenario_empty(scenario: dict) -> bool:
            """
            Returns True if the scenario has no steps, no raw_lines, and no xml_content.
            """
            if not scenario:
                return True
            if scenario.get('steps'):
                return False
            if scenario.get('raw_lines'):
                # Check if any raw line is non-empty and not just a covers line
                for line in scenario['raw_lines']:
                    clean_line = line.strip()
                    if clean_line and not clean_line.lower().startswith('covers:'):
                        return False
            if scenario.get('xml_content'):
                return False
            return True

        for test_result in test_results:
            if test_result.get('type') == 'txt':
                scenarios = test_result.get('content', [])
                filename = test_result.get('filename', 'Unknown')

                for idx, scenario in enumerate(scenarios):
                    if is_scenario_empty(scenario):
                        logging.warning(f"Skipping file '{filename}' scenario {idx+1} - no valid test content found.")
                        continue

                    total_scenarios += 1

                    if 'test_case' in scenario:
                        test_name = scenario['test_case']
                        covers_list = scenario.get('covers_list', [])
                        test_content = scenario
                    elif 'raw_lines' in scenario:
                        filename = test_result.get('filename', 'Unknown')
                        test_name = filename.replace('.txt', '') if filename.endswith('.txt') else filename
                        if scenario.get('raw_lines'):
                            for line in scenario['raw_lines']:
                                clean_line = line.strip()
                                if clean_line and not clean_line.lower().startswith('covers:'):
                                    import re
                                    clean_test_name = re.sub(r'\s+[🟢🔴⚪]\s+(PASS|FAIL|SKIP)\s*$', '', clean_line).strip()
                                    if clean_test_name:
                                        test_name = clean_test_name
                                        break
                        covers_list = scenario.get('covers_list', [])
                        test_content = scenario
                    else:
                        logging.warning(f"Skipping scenario with unknown format: {scenario}")
                        continue

                    # --- NEW LOGIC: Scan covers_list for UT IDs ---
                    from sw_ut_report.jama_common import is_jama_ut_id
                    ut_ids = [c for c in covers_list if is_jama_ut_id(c)]
                    covers_list_no_ut = [c for c in covers_list if not is_jama_ut_id(c)]
                    if len(ut_ids) > 1:
                        name_based_ut_warnings.append({
                            'document_keys': ut_ids,
                            'name': test_name,
                            'file_name': filename,
                            'error': 'Multiple UT IDs found in covers; only one is allowed.'
                        })
                        logging.error(f"Multiple UT IDs found in covers for test '{test_name}' in file '{filename}': {ut_ids}")
                        continue
                    elif len(ut_ids) == 1:
                        ut_id = ut_ids[0]
                        covers_list_for_relationships = covers_list_no_ut
                    else:
                        ut_id = None
                        covers_list_for_relationships = covers_list_no_ut
                    # --- END NEW LOGIC ---

                    logging.info(f"Creating UT: {clean_log_message(test_name)}, covers: {covers_list}")
                    from sw_ut_report.jama_common import is_jama_ut_id
                    try:
                        unit_test = jama_manager.find_or_create_unit_test(
                            test_name, module_folder, list(covers_list), test_content, ut_id=ut_id
                        )
                        if not ut_id:
                            doc_key = unit_test.get('documentKey', 'N/A')
                            ut_name = unit_test.get('fields', {}).get('name', 'N/A')
                            name_based_ut_warnings.append({
                                'document_key': doc_key,
                                'name': ut_name,
                                'file_name': filename
                            })
                    except JamaConnectionError as e:
                        logging.error(f"Failed to find or update UT by ID for {test_name}: {e}")
                        ut_id_val = ut_id if ut_id else (covers_list[0] if (covers_list and is_jama_ut_id(covers_list[0])) else 'N/A')
                        ut_id_not_found_warnings.append({
                            'ut_id': ut_id_val,
                            'test_name': clean_log_message(test_name),
                            'file_name': filename,
                            'error': str(e)
                        })
                        continue

                    if covers_list_for_relationships:
                        logging.info(f"Creating relationships for {len(covers_list_for_relationships)} requirements")
                        try:
                            jama_manager.create_verification_relationships(unit_test, covers_list_for_relationships)
                            logging.info(f"Successfully created all relationships for {clean_log_message(test_name)}")
                        except JamaConnectionError as e:
                            logging.error(f"Failed to create relationships for {clean_log_message(test_name)}: {e}")
                            relationship_errors.append({
                                'test_name': clean_log_message(test_name),
                                'covers_list': covers_list_for_relationships,
                                'error': str(e)
                            })
                    else:
                        logging.info("No covers requirements found - no relationships to create")

                    try:
                        logging.info(f"Changing workflow status to 'Accepted' for {clean_log_message(test_name)}")
                        jama_manager.change_item_status_to_accepted(unit_test['id'])
                        logging.info(f"Successfully changed workflow status to 'Accepted' for {clean_log_message(test_name)}")
                    except JamaConnectionError as e:
                        logging.error(f"Failed to change workflow status for {clean_log_message(test_name)}: {e}")
                        status_change_errors.append({
                            'test_name': clean_log_message(test_name),
                            'test_id': unit_test['id'],
                            'error': str(e)
                        })

                    processed_count += 1

            # Silently skip XML files
            # elif test_result.get('type') == 'xml':
            #     pass

            else:
                logging.warning(f"Skipping unknown test result type: {test_result.get('type')}")

        # Report final summary
        logging.info("=== UT Creation Summary ===")
        logging.info(f"Module: {module_name}")
        logging.info(f"Total scenarios processed: {total_scenarios}")
        logging.info(f"Successfully created/updated: {processed_count}")

        # Report name-based UT warnings
        if name_based_ut_warnings:
            print("\nWARNING: The following UTs were created or updated based on NAME search (not by UT ID):")
            print("Developers should reference all UT IDs in their tests for traceability.")
            print("| Document Key       | Name                        | File Name              |")
            print("|--------------------|-----------------------------|------------------------|")
            for ut in name_based_ut_warnings:
                print(f"| {ut['document_key']:<18} | {ut['name']:<27} | {ut['file_name']:<22} |")
            print()

        # Report UT ID not found warnings
        if ut_id_not_found_warnings:
            print("\nFAILED TEST SEARCH: The following UT IDs were declared in covers but not found in Jama:")
            print("| UT ID             | Test Name                   | File Name              | Error")
            print("|-------------------|----------------------------|------------------------|------------------------------")
            for ut in ut_id_not_found_warnings:
                print(f"| {ut['ut_id']:<17} | {ut['test_name']:<26} | {ut['file_name']:<22} | {ut['error']}")
            print()

        # Report relationship creation errors
        if relationship_errors:
            logging.error(f"Relationship creation failures: {len(relationship_errors)}")
            logging.error("Failed relationships details:")
            for error_info in relationship_errors:
                test_name = error_info['test_name']
                covers_count = len(error_info['covers_list'])
                error_msg = error_info['error']
                logging.error(f"  - {test_name}: Failed to create {covers_count} relationships")
                logging.error(f"    Error: {error_msg}")
        else:
            logging.info("All relationship operations completed successfully")

        # Report status change errors
        if status_change_errors:
            logging.error(f"Workflow status change failures: {len(status_change_errors)}")
            logging.error("Failed status changes details:")
            for error_info in status_change_errors:
                test_name = error_info['test_name']
                test_id = error_info['test_id']
                error_msg = error_info['error']
                logging.error(f"  - {test_name} (ID: {test_id}): Failed to change status to 'Accepted'")
                logging.error(f"    Error: {error_msg}")
        else:
            logging.info("All workflow status changes completed successfully")

        if processed_count > 0:
            total_errors = len(relationship_errors) + len(status_change_errors)
            if total_errors > 0:
                logging.warning(f"Processed {processed_count} unit tests but {total_errors} operations had failures")
                # Raise error to indicate partial failure
                failed_operations = []
                if relationship_errors:
                    failed_tests = [err['test_name'] for err in relationship_errors]
                    failed_operations.append(f"relationship creation failed for: {', '.join(failed_tests)}")
                if status_change_errors:
                    failed_tests = [err['test_name'] for err in status_change_errors]
                    failed_operations.append(f"status change failed for: {', '.join(failed_tests)}")
                raise JamaConnectionError(f"Unit tests processed but {'; '.join(failed_operations)}")
            else:
                logging.info(f"Successfully processed {processed_count} unit tests for module {module_name}")
                return True
        else:
            logging.warning("No unit tests were processed")
            return False

    except JamaConnectionError:
        # Re-raise Jama connection errors (these are expected and should stop execution)
        raise
    except Exception as e:
        logging.error(f"Unexpected error in UT creation workflow: {e}")
        raise JamaConnectionError(f"UT creation failed: {e}")


def extract_test_names_and_covers(test_results: List[Dict]) -> List[Dict]:
    """
    Extract test names and covers information from parsed test results.

    This function is useful for validation and preview purposes.

    Args:
        test_results: List of parsed test results

    Returns:
        List[Dict]: List of extracted test information
    """
    extracted_tests = []

    for test_result in test_results:
        if test_result.get('type') == 'txt':
            scenarios = test_result.get('content', [])

            for scenario in scenarios:
                if 'test_case' in scenario:
                    # Structured scenario
                    extracted_tests.append({
                        'test_name': scenario['test_case'],
                        'covers_list': scenario.get('covers_list', []),
                        'source_file': test_result.get('filename', 'Unknown'),
                        'type': 'structured_txt'
                    })
                elif 'raw_lines' in scenario:
                    # Unstructured scenario
                    filename = test_result.get('filename', 'Unknown')
                    test_name = filename.replace('.txt', '') if filename.endswith('.txt') else filename
                    extracted_tests.append({
                        'test_name': test_name,
                        'covers_list': scenario.get('covers_list', []),
                        'source_file': filename,
                        'type': 'unstructured_txt'
                    })

        elif test_result.get('type') == 'xml':
            content = test_result.get('content', {})
            filename = test_result.get('filename', 'Unknown')
            test_name = content.get('name', filename.replace('.xml', '') if filename.endswith('.xml') else filename)

            extracted_tests.append({
                'test_name': test_name,
                'covers_list': [],  # XML files don't have covers
                'source_file': filename,
                'type': 'xml'
            })

    return extracted_tests


def validate_jama_environment_for_ut_creation() -> bool:
    """
    Validate that the Jama environment is properly configured for UT creation.

    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        # Check environment variables
        if not validate_environment():
            return False

        # Try to initialize manager and validate SmlPrep-UT-1
        jama_manager = JamaUTManager()
        jama_manager.validate_smlprep_ut_1_exists()

        logging.info("Jama environment validation successful")
        return True

    except JamaConnectionError as e:
        logging.error(f"Jama environment validation failed: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during environment validation: {e}")
        return False