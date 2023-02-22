from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element

def hotspot_config(con_file: str):
    try:
        with open (con_file, 'r') as f:
            lines = f.readlines()
    except Exception:
        raise("Config File not found",Exception)

    main_page = lines[0]
    network_page = lines[1]
    adm_psw = lines[2]
    return main_page, network_page, adm_psw

def write_config(main_page: str, network_page: str, adm_psw: str, file_name: str):
    with open(file_name, 'w+') as f:
        f.write(main_page + "\n")
        f.write(network_page + "\n")
        f.write(adm_psw + "\n")
    return

# Returns the current technology as a string
# Args: con_file: str, name of the config file, if not in local folder must be an absolute path
# Return: tech: str. current network mode. expected 4G, 5G, or no signal
def check_mode(con_file: str) -> str:

    main_page, _, adm_psw = hotspot_config(con_file)
    FFops = Options()
    FFops.add_argument("-headless")
    driver = webdriver.Firefox(options=FFops)

    # Open the main page
    driver.get(main_page)
    
    # Enter the password
    pass_input = driver.find_element(By.NAME,"password")
    pass_input.clear()
    pass_input.send_keys(adm_psw)
    pass_input.send_keys(Keys.RETURN)

    # find the technology field on the main page
    #current_val = driver.find_element(By.ID,"technology")
    WebDriverWait(driver, timeout=30).until(text_to_be_present_in_element((By.ID,'technology'),'G'))
    current_val = driver.find_element(By.ID,"technology")
    tech = current_val.text
    
    if tech == "":
        print("Could not identify current network mode")
        tech = "unknown"

    driver.close()
    return tech 

def set_mode(con_file: str, new_mode: str):

    if new_mode == '3G':
        new_val = '2'
    elif new_mode == '4G':
        new_val = '1'
    elif new_mode == '5G':
        new_val = '0'
    else:
        raise Exception("Unknown network preference", new_mode)

    main_page, network_page, adm_psw = hotspot_config(con_file)
    FFops = Options()
    FFops.add_argument("-headless")
    driver = webdriver.Firefox(options=FFops)

    # Open the main page
    driver.get(main_page)

    # Enter the password
    pass_input = driver.find_element(By.NAME,"password")
    pass_input.clear()
    pass_input.send_keys(adm_psw)
    pass_input.send_keys(Keys.RETURN)

    # Switch to the config page
    driver.get(network_page)

    # Find the ok button and click it
    ok_but = driver.find_element(By.ID,'ok-btn')
    ok_but.click()

    # Find the value of the networkmode element, 0 is 5G, 1 is 4G, 2 is 3G (3G doesnt seem to be supported here)
    # The order of modes in the drop down is actuall 0,2,1 though so 5G to 4G is two downs
    change_tech = driver.find_element(By.ID,"networkmode")
    current_val = change_tech.get_attribute('value')
    
    # do a little confirmation printing
    if current_val == '0':
        current_mode = '5G'
    elif current_val == '1':
        current_mode = '4G'
    elif current_val == '2':
        current_mode = '3G'
    else:
        raise Exception("Current network technology unknown",current_mode)

    if current_val == new_val:
        print("Network mode already set")
        return

    # Currently 5G
    if current_val == '0':
        # Change to 4G
        if new_val == '1':
            change_tech.send_keys(Keys.ARROW_DOWN)
            change_tech.send_keys(Keys.ARROW_DOWN)
        # Change to 3G
        if new_val == '2':
            change_tech.send_keys(Keys.ARROW_DOWN)

    # Currently 4G
    if current_val == '1':
        # Change to 5G
        if new_val == '0':
            change_tech.send_keys(Keys.ARROW_UP)
            change_tech.send_keys(Keys.ARROW_UP)
        # Change to 3G
        if new_val == '2':
            change_tech.send_keys(Keys.ARROW_UP)
        
    # Currently 3G
    if current_val == '2':
        # Change to 5G
        if new_val == '0':
            change_tech.send_keys(Keys.ARROW_UP)
        # Change to 4G
        if new_val == '1':
            change_tech.send_keys(Keys.ARROW_DOWN)

    change_tech.send_keys(Keys.RETURN)
    submit_button = driver.find_element(By.ID,"manualSave")
    submit_button.click()
    
    print("Network mode changed from",current_mode,"to",new_mode)

    driver.close()
    return

hotspot_config_path = "configs/orbic_config.txt"



