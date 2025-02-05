import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_responsive_design(selenium_driver):
    """
    Test ID: TC007
    Test Type: System
    Test Case Category: User Interface
    Description: Test responsive design on mobile
    """
    # Set mobile viewport
    selenium_driver.set_window_size(375, 812)  # iPhone X dimensions
    
    # Navigate to homepage
    selenium_driver.get("http://localhost:5000")
    
    # Check responsive elements
    nav_menu = selenium_driver.find_element(By.ID, "nav-menu")
    assert nav_menu.is_displayed()
    
    # Check if elements stack properly on mobile
    content_width = selenium_driver.find_element(By.ID, "main-content").size['width']
    assert content_width <= 375  # Should not exceed viewport width

def test_form_validation(selenium_driver):
    """
    Test ID: TC008
    Test Type: Unit
    Test Case Category: User Interface
    Description: Test form submission validation
    """
    # Navigate to submission form
    selenium_driver.get("http://localhost:5000/submit")
    
    # Test empty form submission
    submit_button = selenium_driver.find_element(By.ID, "submit-btn")
    submit_button.click()
    
    # Check error messages
    error_messages = selenium_driver.find_elements(By.CLASS_NAME, "error-message")
    assert len(error_messages) > 0  # Should show validation errors
    
    # Fill form with valid data
    name_input = selenium_driver.find_element(By.ID, "name")
    name_input.send_keys("John Doe")
    
    email_input = selenium_driver.find_element(By.ID, "email")
    email_input.send_keys("john@example.com")
    
    # Submit valid form
    submit_button.click()
    
    # Check success message
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
    )
    success_message = selenium_driver.find_element(By.CLASS_NAME, "success-message")
    assert success_message.is_displayed()

@pytest.fixture
def selenium_driver():
    """
    Fixture for Selenium WebDriver
    Note: You'll need to have ChromeDriver installed and in PATH
    """
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit() 