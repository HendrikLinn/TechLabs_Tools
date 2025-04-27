"""Configurations for the test cases."""

import os
import sys
import pytest  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error

sys.path.append("../modules/feature_engineering/")
sys.path.append("../modules/group_selection/")

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Assume your_script.py is in the parent directory
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.insert(0, project_root)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_session(request):  # pylint: disable=missing-function-docstring
    # Setup code (executed once before any test in the session)
    print("\nSetting up for the entire session")

    print("\nSetup for the test completed.")

    # The teardown code (executed once after all tests in the session)
    def teardown():
        print("\nTearing down after the entire session")

    # Register the teardown function
    request.addfinalizer(teardown)
