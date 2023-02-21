from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

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
    #might need to change this
    FFops.headless = True
    driver = webdriver.Firefox(options=FFops)

    # Open the main page
    driver.get(main_page)

    # Enter the password
    pass_input = driver.find_element(By.NAME,"password")
    pass_input.clear()
    pass_input.send_keys(adm_psw)
    pass_input.send_keys(Keys.RETURN)

    # find the technology field on the main page
    current_val = driver.find_element(By.ID,"technology")
    print(current_val.text)
    tech = current_val.text

    driver.close()
    return tech 

def set_mode(con_file: str, mode: str):

    if mode == '3G':
        new_val = 1
    elif mode == '4G':
        new_val = 2
    else:
        new_val = 3

    main_page, network_page, adm_psw = hotspot_config(con_file)
    FFops = Options()
    FFops.headless = True
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
    val = change_tech.get_attribute('value')
    
    driver.close()
    return

file_name = "orbic_config.txt"
tech = check_mode(file_name)
print(tech)



