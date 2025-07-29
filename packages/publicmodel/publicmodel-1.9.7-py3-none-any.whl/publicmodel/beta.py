import random
import re
import select
import string
import sys
import time

import colored
import cv2
import qrcode
import requests
from PIL import Image
from bs4 import BeautifulSoup
from colored import Fore

from publicmodel.abnormal.error_class import FormatError, MaxAttemptsExceededError, OptionError, LoadError


def log(func):
    def wrapper(*args, **kwargs):
        print(f"调用函数 {func.__name__} 前的普通参数: {args}, 字典参数: {kwargs}")
        start = time.time()
        ret = func(*args, **kwargs)
        cost = time.time() - start
        print(f"调用函数 {func.__name__} 后的普通参数: {args}, 字典参数: {kwargs}\n耗时: {cost:.5f}s")
        print(f"函数 {func.__name__} 的返回值: {ret}\n")
        return ret

    return wrapper


def tuichu(input_str, tishi='已退出', tuichu_str='q'):
    if input_str == tuichu_str:
        orange_print(tishi)
        sys.exit()


class TimeoutExpired(Exception):
    pass


def input_timeout(prompt, timeout=9):
    print(Fore.RGB(225, 255, 0) + prompt, end=" ", flush=True)
    fds = [sys.stdin]
    result = []
    r, _, _ = select.select(fds, [], [], timeout)
    if not r:
        raise TimeoutExpired()

    input_str = sys.stdin.readline().rstrip()
    result.append(input_str)
    return result[0]


def stop_thread(thread):
    thread.cancel()


def slow_print(text, delay=0.23):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # 换行


def slow_input(text, delay=0.23):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    return input()  # 换行


def tuichu2(input_str, tishi='已退出', tuichu_str='n'):
    if input_str == tuichu_str:
        print(tishi)
        sys.exit()


def slow_print2(text, delay=0.25):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def red_print(input_str):
    print(Fore.RGB(225, 0, 50) + input_str)


def red_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.RGB(225, 0, 50) + char, end='', flush=True)
        time.sleep(delay)
    print()


def orange_print(input_str):
    print(Fore.RGB(255, 170, 0) + input_str)


def orange_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.RGB(255, 170, 0) + char, end='', flush=True)
        time.sleep(delay)
    print()


def yellow_print(input_str):
    print(Fore.CYAN + Fore.GREEN + Fore.RED + Fore.GREEN + Fore.BLUE + Fore.YELLOW + input_str)


def yellow_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.CYAN + Fore.GREEN + Fore.RED + Fore.GREEN + Fore.BLUE + Fore.YELLOW + char, end='', flush=True)
        time.sleep(delay)
    print()


def yellow_print2(input_str):
    print(Fore.RGB(225, 255, 0) + input_str)


def yellow_slow_print2(input_str, delay=0.23):
    for char in input_str:
        print(Fore.RGB(225, 255, 0) + char, end='', flush=True)
        time.sleep(delay)
    print()


def green_print(input_str):
    print(Fore.RGB(125, 250, 85) + input_str)


def green_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.RGB(125, 250, 85) + char, end='', flush=True)
        time.sleep(delay)
    print()


def cyan_print(input_str):
    print(Fore.CYAN + input_str)


def cyan_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.CYAN + char, end='', flush=True)
        time.sleep(delay)
    print()


def blue_print(input_str):
    print(Fore.RGB(50, 150, 225) + input_str)


def blue_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.RGB(50, 150, 225) + char, end='', flush=True)
        time.sleep(delay)
    print()


def purple_print(input_str):
    print(Fore.RGB(171, 91, 187) + input_str)


def purple_slow_print(input_str, delay=0.23):
    for char in input_str:
        print(Fore.RGB(171, 91, 187) + char, end='', flush=True)
        time.sleep(delay)
    print()


def red_input(input_str):
    result = input(Fore.RGB(225, 0, 50) + input_str)
    return result


def red_slow_input(input_str, delay=0.23):
    for i, char in enumerate(input_str):
        print(Fore.RGB(225, 0, 50) + char, end='')
        time.sleep(delay)
    return input()


def orange_input(input_str):
    result = input(Fore.RGB(255, 170, 0) + input_str)
    return result


def orange_slow_input(input_str, delay=0.23):
    pass


def yellow_input(input_str):
    result = input(Fore.CYAN + Fore.GREEN + Fore.RED + Fore.GREEN + Fore.BLUE + Fore.YELLOW + input_str)
    return result


def yellow_slow_input(input_str, delay=0.23):
    pass


def yellow_input2(input_str):
    result = input(Fore.RGB(225, 255, 0) + input_str)
    return result


def yellow_slow_input(input_str, delay=0.23):
    pass


def green_input(input_str):
    result = input(Fore.RGB(125, 250, 85) + input_str)
    return result


def green_slow_input(input_str, delay=0.23):
    pass


def cyan_input(input_str):
    result = input(Fore.CYAN + input_str)
    return result


def cyan_slow_input(input_str, delay=0.23):
    pass


def blue_input(input_str):
    result = input(Fore.RGB(50, 150, 225) + input_str)
    return result


def blue_slow_input(input_str, delay=0.23):
    pass


def purple_input(input_str):
    result = input(Fore.RGB(171, 91, 187) + input_str)
    return result


def purple_slow_input(input_str, delay=0.23):
    pass


def is_chinese_start(s):
    return s and 0x4E00 <= ord(s[0]) <= 0x9FA0


def is_chinese_start(s):
    return s and 0x4E00 <= ord(s[0]) <= 0x9FA0


def hex_to_rgb(hex_value_print):
    hex_value = hex_value_print.upper()
    if '#' in hex_value:
        hex_value = hex_value.lstrip('#')
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    rgb = f"{r}, {g}, {b}"  # 将 r、g、b 组合成一个逗号分隔的字符串
    return rgb


def rgb_to_hex(rgb_print):
    rgb = rgb_print
    if isinstance(rgb, str):
        rgb = tuple(map(int, rgb.split(',')))  # 如果输入是字符串，则将其分割为整数值的元组

    r, g, b = rgb
    if r > 255 or g > 255 or b > 255:
        raise ValueError
    elif r < 0 or g < 0 or b < 0:
        raise TypeError
    hex_value = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    hex_value = hex_value.upper()
    return hex_value


def rainbow_print(text):
    colors = [colored.Fore.RGB(225, 0, 50), Fore.RGB(255, 170, 0), colored.Fore.RGB(225, 255, 0),
              colored.Fore.RGB(125, 250, 85), colored.Fore.CYAN, colored.Fore.RGB(50, 150, 225)]
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        print(color + char, end='')


def rainbow_slow_print(text, delay=0.23):
    colors = [colored.Fore.RGB(225, 0, 50), Fore.RGB(255, 170, 0), colored.Fore.RGB(225, 255, 0),
              colored.Fore.RGB(125, 250, 85), colored.Fore.CYAN, colored.Fore.RGB(50, 150, 225)]
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        print(color + char, end='')
        time.sleep(delay)


def rainbow_input(input_str):
    colors = [colored.Fore.RGB(225, 0, 50), Fore.RGB(255, 170, 0), colored.Fore.RGB(225, 255, 0),
              colored.Fore.RGB(125, 250, 85), colored.Fore.CYAN, colored.Fore.RGB(50, 150, 225)]
    for i, char in enumerate(input_str):
        color = colors[i % len(colors)]
        print(color + char, end='')
    return input()


def rainbow_slow_input(input_str, delay=0.23):
    colors = [colored.Fore.RGB(225, 0, 50), Fore.RGB(255, 170, 0), colored.Fore.RGB(225, 255, 0),
              colored.Fore.RGB(125, 250, 85), colored.Fore.CYAN, colored.Fore.RGB(50, 150, 225)]
    for i, char in enumerate(input_str):
        color = colors[i % len(colors)]
        print(color + char, end='')
        time.sleep(delay)
    return input()


def ord2(text):
    encrypted_text = ""
    for char in text:
        code = ord(char)
        encrypted_code = str(code)
        encrypted_text += encrypted_code + " "
    return encrypted_text[:-1]


def chr2(text):
    encrypted_codes = text.split(' ')
    decrypted_text = ''
    for encrypted_code in encrypted_codes:
        code = (int(encrypted_code))
        decrypted_text += chr(code)
    return decrypted_text


def list_start(list, symbol):
    for item in list:
        if isinstance(item, str) and item.startswith(symbol):
            return item
        else:
            raise ValueError


def weather():
    url = "http://www.weather.com.cn/weather/101280601.shtml"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"}
        response = requests.get(url, headers=headers)  # 发起请求
        data = response.content.decode("utf-8")  # 获得响应体并解码
        soup = BeautifulSoup(data, "lxml")
        lis = soup.select("ul[class='t clearfix'] li")
        x = 0
        for li in lis:
            try:
                date = li.select('h1')[0].text
                weather = li.select('p[class="wea"]')[0].text
                if x == 0:  # 为今天只有一个温度做判断 <i>14℃</i>
                    x += 1
                    temp = li.select('p[class="tem"] i')[0].text
                else:
                    temp = li.select('p[class="tem"] span')[0].text + " ~ " + li.select('p[class="tem"] i')[0].text
                print(date, weather, temp)
            except Exception as err:
                print(err)
    except Exception as err:
        print(err)


def lat_and_lon():
    # 使用ipinfo.io的API获取当前IP地址的地理位置信息
    url = 'https://ipinfo.io/json'
    response = requests.get(url)
    data = response.json()

    # 从返回的JSON数据中提取经纬度信息
    coordinates = data['loc'].split(',')
    latitude = coordinates[0]
    longitude = coordinates[1]

    # 返回经纬度
    return latitude, longitude


def trans(value):
    jieguo = None
    huoqu = value
    fanyi = huoqu
    url = f'https://cn.linguee.com/%E4%B8%AD%E6%96%87-%E8%8B%B1%E8%AF%AD/search?source=auto&query=/{fanyi}'
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    fruit_list = soup.find_all('a', class_='dictLink featured')
    for fruit in fruit_list:
        jieguo = fruit.text
    return jieguo


def value1(value):
    if isinstance(value, str):
        num = 'str'
    elif isinstance(value, int):
        num = 'int'
    elif isinstance(value, float):
        num = 'float'
    else:
        raise ValueError
    return num


def value2(value):
    global num
    if value.isdigit():
        num = int(value)
    elif re.match(r'^[-+]?(\d+(\.\d*)?|\.\d+)$', value):
        num = float(value)
    return num


def value3(value):
    if value.isdigit():
        num = 'int'
    elif re.match(r'^[-+]?(\d+(\.\d*)?|\.\d+)$', value):
        num = 'float'
    else:
        num = 'str'
    return num


def value4(value):
    ret = str(value)
    if '.' in ret and ret.count('.') == 1:
        temp_array = ret.split('.')
        one = temp_array[0]
        two = temp_array[1]
        if one.isdigit() and two.isdigit():
            xiao_shu = int(two)
            if xiao_shu == 0:
                ret = int(one)
            else:
                ret = float(value)
    elif ret.isdigit():
        ret = int(ret)
    return ret


def other(value, zifu):
    pattern = rf'[^0-9{zifu}]'  # 匹配非数字和非小数点的字符
    result = re.findall(pattern, value)
    return ''.join(result)


def other2(value, zifu):
    value = str(value)
    zifu = str(zifu)
    pattern = rf'[^{zifu}]'  # 匹配非数字和非小数点的字符
    result = re.findall(pattern, value)
    return ''.join(result)


def is_same_characters(string):
    unique_chars = set(string)  # 将字符串转换为集合，去除重复字符
    return len(unique_chars) == 1  # 如果集合中只有一个独特的字符，则返回 True，否则返回 False


def check_same_elements(lst):
    return len(set(lst)) == 1 and len(lst) == len(set(map(str, lst)))


def last(value):
    value = str(value)
    last = value[-1]
    return last


#  1. 如果结果的小数部分是一个循环的话，就在第一次循环的最后一个数字后打6个 '.' ，
#     比如小数部分是 '123123123' ，那就简化成 '123......'
#  2. 如果不是的话，就直接用eval()来算
def calculate(value):
    value = str(value)
    table1 = []
    table1.clear()
    if '/' not in value:
        outcome = str(value4(eval(value)))
        return outcome
    elif '/' in value:
        zifu = other(value, '.')
        if last(zifu) == '/':
            old_outcome = str(value4(eval(value)))
            print(f'old_outcome = {old_outcome}|v = {eval(value)}')
            if '.' not in old_outcome:
                return old_outcome
            else:
                if len(old_outcome) <= 4:
                    return old_outcome
                old_outcome2 = old_outcome[:-2]
                character = '.'
                index = old_outcome2.index(character)  # 获取字符在字符串中的索引位置
                decimal_part = old_outcome2[index + 1:]  # 使用切片操作符获取右边部分
                integer_part = old_outcome2[:index]
                zifu = '...'
                if is_same_characters(decimal_part):
                    outcome = str(integer_part + '.' + decimal_part[0] + zifu)
                    return outcome
                else:
                    return old_outcome


def delete_str(value, delete):
    value = str(value)
    wei_zhi1 = value.find(delete)
    wei_zhi2 = wei_zhi1 + len(delete)
    jieguo = value[:wei_zhi1] + value[wei_zhi2:]
    return jieguo


def MoveRight(string, char):
    string = str(string)
    char = str(char)

    # 找到字符在字符串中的位置
    index = string.find(char)

    # 如果字符不存在或在字符串末尾，则无需移动
    if index == -1 or index == len(string) - 1:
        return string

    # 将字符向右移动一个位置
    moved_string = string[:index] + string[index + 1] + string[index] + string[index + 2:]
    return moved_string


def MoveLeft(string, char):
    string = str(string)
    char = str(char)

    # 找到字符在字符串中的位置
    index = string.find(char)

    # 如果字符不存在或在字符串开头，则无需移动
    if index == -1 or index == 0:
        return string

    # 将字符向左移动一个位置
    moved_string = string[:index - 1] + string[index] + string[index - 1] + string[index + 1:]
    return moved_string


def erase(string, char):
    string = str(string)
    char = str(char)

    # 找到字符在字符串中的位置
    index = string.find(char)

    # 如果字符不存在或在字符串开头，则无需删除
    if index == -1 or index == 0:
        return string

    # 删除第二个参数左边的一个字符
    erased_string = string[:index - 1] + string[index:]
    return erased_string


def remove_character(string, char):
    # 从字符串中删除指定的字符
    return string.replace(char, "")


def anim_print(value, delay=0.25, loop=1, final=' '):
    value_list = [x for x in value]  # 将输入的文本转换为字符列表
    i = 1
    loop = value4(loop)
    while i <= loop:  # 循环指定的次数
        for char in value_list:
            print(f"\r{char}", end='', flush=True)  # 使用ANSI转义序列覆盖输出当前字符
            time.sleep(delay)  # 延时一段时间
        i += 1
    if final == ' ':
        print(f"\r{final}\b", end='', flush=True)  # 输出最终字符并退格
    else:
        print(f"\r{final}\n", end='', flush=True)  # 输出最终字符并换行


def rainbow_anim_print(value, delay=0.25, loop=1, final=' ', color='#BBBBBB'):
    value_list = [x for x in value]
    i = 1
    loop = value4(loop)

    # 创建颜色名称到colored.Fore属性的映射
    color_map = {
        "RED": colored.Fore.RED,
        "ORANGE": colored.Fore.RGB(255, 170, 0),
        "YELLOW": colored.Fore.RGB(255, 225, 0),
        "GREEN": colored.Fore.RGB(0, 170, 0),
        "BLUE": colored.Fore.BLUE,
        "CYAN": colored.Fore.CYAN,
        "PURPLE": colored.Fore.RGB(171, 91, 187)
    }

    while i <= loop:
        color = color.upper()
        if color == 'RAINBOW':
            color_list = [colored.Fore.RGB(225, 0, 50), colored.Fore.RGB(255, 170, 0), colored.Fore.RGB(225, 255, 0),
                          colored.Fore.RGB(125, 250, 85), colored.Fore.CYAN, colored.Fore.RGB(50, 150, 225)]
            for char in value_list:
                random_color = random.choice(color_list)
                print(random_color + f"\r{char}", end='', flush=True)
                time.sleep(delay)
            i += 1
        else:
            if color.startswith("#"):  # 十六进制码
                hex_code = color.lstrip("#")
                rgb = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
                selected_color = colored.Fore.RGB(*rgb)
            elif color.startswith("RGB(") and color.endswith(")"):  # RGB值
                rgb_str = color[4:-1]
                rgb = tuple(map(int, rgb_str.split(',')))
                selected_color = colored.Fore.RGB(*rgb)
            else:  # 颜色名称
                selected_color = color_map.get(color, colored.Fore.RGB(187, 187, 187))  # 获取指定颜色，如果未找到，则使用红色作为默认值
            for char in value_list:
                print(selected_color + f"\r{char}", end='', flush=True)
                time.sleep(delay)
            i += 1
    if final == ' ':
        print(colored.Fore.RGB(187, 187, 187) + f"\r{final}\b", end='', flush=True)
    else:
        print(colored.Fore.RGB(187, 187, 187) + f"\r{final}\n", end='', flush=True)


class VCG:  # Verification Code Generator
    def __init__(self, format_='111111', forbidden_characters=None, maximum_number_of_attempts=100000):
        if forbidden_characters is None:
            forbidden_characters = ['o', 'O', '0']
        self._format = format_
        self._forbidden_characters = forbidden_characters or []
        self.maximum_number_of_attempts = maximum_number_of_attempts

    def generate_code(self):
        i = 0
        while i <= self.maximum_number_of_attempts:
            code = []

            if len(self._format) == 0:
                raise FormatError("Format cannot be empty")

            for char in self._format:
                # Generate verification code
                if char == '1':
                    code.append(random.choice(string.digits))
                elif char == 'a':
                    code.append(random.choice(string.ascii_lowercase))
                elif char == 'A':
                    code.append(random.choice(string.ascii_uppercase))
                elif char == '*':
                    code.append(random.choice(string.punctuation))

                # Judgment of special characters
                elif char in ('x', 'X'):
                    random_format = random.choice(['1', 'a', 'A', '*'])
                    if random_format == '1':
                        code.append(random.choice(string.digits))
                    elif random_format == 'a':
                        code.append(random.choice(string.ascii_lowercase))
                    elif random_format == 'A':
                        code.append(random.choice(string.ascii_uppercase))
                    elif random_format == '*':
                        code.append(random.choice(string.punctuation))
                else:
                    raise FormatError(f"Invalid format character: \"{char}\"")

            generated_code = ''.join(code)

            # Check if the generated verification code contains any forbidden characters
            if not any(char in self._forbidden_characters for char in generated_code):
                return generated_code

            i += 1

        raise MaxAttemptsExceededError("The format you entered does not appear to be valid")


class QRCG:  # Quick Response Code Generator
    def __init__(self, data, img_size=(300, 300), qr_version=1, box_size=10, logo_path=None, save_path=None,
                 show=False, error_correct_levels="high", border=4, fill_color="black", back_color="white"):
        self.data = self._read_data(data)
        self.img_size = img_size
        self.qr_version = qr_version
        self.box_size = box_size
        self.logo_path = logo_path
        self.save_path = save_path
        self.show = show
        self.error_correct_levels = error_correct_levels
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color

    def _read_data(self, data):
        try:
            with open(data, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return data

    def generate_qr(self):
        if self.error_correct_levels == "low":
            error_correction = qrcode.constants.ERROR_CORRECT_L
        elif self.error_correct_levels == "default":
            error_correction = qrcode.constants.ERROR_CORRECT_M
        elif self.error_correct_levels == "medium":
            error_correction = qrcode.constants.ERROR_CORRECT_Q
        elif self.error_correct_levels == "high":
            error_correction = qrcode.constants.ERROR_CORRECT_H
        else:
            raise OptionError(f"Invalid error correction level: \"{self.error_correct_levels}\"")

        qr = qrcode.QRCode(
            version=self.qr_version,
            error_correction=error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color).convert('RGB')

        # Adjust the size of the QR code image
        img = img.resize(self.img_size, Image.NEAREST)  # Use nearest neighbor interpolation method

        if self.logo_path:
            self._add_logo(img)

        if self.save_path:
            img.save(self.save_path)

        if self.show:
            img.show()

    def _add_logo(self, img):
        logo = Image.open(self.logo_path)

        # The size of the logo is one-fifth of the minimum side length of the QR code image
        logo_size = min(self.img_size) // 5

        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo)


class QRCI:  # Quick Response Code Identification
    def __init__(self, image_path):
        self.image_path = image_path

    def decode_qr_code(self):
        # Read image
        image = cv2.imread(self.image_path)
        if image is None:
            raise ValueError("Unable to load image.")

        # Create a QR code detector
        qr_code_detector = cv2.QRCodeDetector()

        # Detect and decode QR codes
        data, vertices_array, _ = qr_code_detector.detectAndDecode(image)

        if vertices_array is not None:
            return data
        else:
            return None

    def get_qr_code_info(self):
        # Read image
        image = cv2.imread(self.image_path)
        if image is None:
            raise ValueError("Unable to load image.")

        # Create a QR code detector
        qr_code_detector = cv2.QRCodeDetector()

        # Detect and decode QR codes
        data, vertices_array, _ = qr_code_detector.detectAndDecode(image)

        if vertices_array is not None:
            # Get the bounding box of the QR code
            vertices = vertices_array[0]
            # Calculate the width and height of the QR code
            width = int(vertices[1][0] - vertices[0][0])
            height = int(vertices[2][1] - vertices[0][1])

            # Calculate the version number of the QR code
            version = (width - 21) // 4 + 1

            # Return to QR code information
            return {
                "data": data,
                "version": version,
                "width": width,
                "height": height,
                "vertices": vertices
            }
        else:
            return None


if __name__ == "__main__":
    try:
        print("Generating QR code...")
        qrcode_path = "img/qrcode2.png"
        qr_generator = QRCG(
            data="http://localhost:8000/comm/text/hello_world.html",
            img_size=(300, 300),
            qr_version=5,
            box_size=20,
            logo_path="img/logo.png",
            save_path=qrcode_path,
            show=True,
            error_correct_levels="high",
            fill_color="black",
            back_color="white"
        )
        qr_generator.generate_qr()

        print("Parsing QR code...")
        qrci = QRCI("img/qrcode2.png")
        qr_code_data = qrci.decode_qr_code()

        if qr_code_data:
            print("Decoded QR Code data:", qr_code_data)
        else:
            print("No QR Code found in the image.")
    except OptionError as e:
        print(f"[Error] {e}")
    except LoadError as e:
        print(f"[Error] {e}")
