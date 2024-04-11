from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By  # Import By class for locating elements
import time

def getLocation():
    options = Options()
    options.add_argument("--use-fake-ui-for-media-stream")
    timeout = 20
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.gps-coordinates.net/my-location")
    wait = WebDriverWait(driver, timeout)
    time.sleep(3)
    
    # Find longitude and latitude elements
    longitude_element = driver.find_element(By.XPATH, '//*[@id="lng"]')
    latitude_element = driver.find_element(By.XPATH, '//*[@id="lat"]')
    my_address = driver.find_element(By.XPATH, '//*[@id="addr"]')
    
    
    # Get text from elements
    longitude = longitude_element.text
    latitude = latitude_element.text
    my_address = my_address.text
    
    driver.quit()
    return (latitude, longitude, my_address)

print(getLocation())
