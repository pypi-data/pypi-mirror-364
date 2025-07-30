from dash.testing.application_runners import import_app
from selenium.webdriver.common.action_chains import ActionChains
import time


# Basic test for the component rendering.
# The dash_duo pytest fixture is installed with dash (v1.0+)
def test_render_component(dash_duo):
    # Start a dash app contained as the variable `app` in `usage.py`
    app = import_app('usage')
    dash_duo.start_server(app)

    # Wait for the app to load
    dash_duo.wait_for_element('#tree-editor', timeout=10)

    # Check that the tree editor exists
    tree_editor = dash_duo.find_element('#tree-editor')
    assert tree_editor is not None

    # Check that the title is present
    title = dash_duo.find_element('h1')
    assert title.text == "Tree Editor with Labels"

    # Check initial state of selected item
    selected_item_div = dash_duo.find_element('#selected-item')
    assert selected_item_div.text == "No item selected"

    # Check that tree structure is displayed
    tree_structure_div = dash_duo.find_element('#tree-structure')
    assert "Home Page" in tree_structure_div.text
    assert "Products" in tree_structure_div.text
    assert "Electronics" in tree_structure_div.text

    # Test clicking on a tree item
    # Find a tree item (this selector might need adjustment based on actual rendered HTML)
    tree_items = dash_duo.find_elements('.tree-item')
    if tree_items:
        # Click on the first item
        tree_items[0].click()
        time.sleep(0.5)  # Wait for callback
        
        # Check if selected item is updated
        selected_text = dash_duo.find_element('#selected-item').text
        assert "Selected item ID:" in selected_text


def test_tree_structure(dash_duo):
    """Test that the tree structure is properly displayed"""
    app = import_app('usage')
    dash_duo.start_server(app)

    # Wait for the tree structure to load
    dash_duo.wait_for_element('#tree-structure', timeout=10)
    
    tree_structure = dash_duo.find_element('#tree-structure')
    structure_text = tree_structure.text
    
    # Verify parent-child relationships
    assert "ID: 3, Label: Electronics, Parent: 2" in structure_text
    assert "ID: 5, Label: Smartphones, Parent: 3" in structure_text
    assert "ID: 1, Label: Home Page, Parent: None" in structure_text
