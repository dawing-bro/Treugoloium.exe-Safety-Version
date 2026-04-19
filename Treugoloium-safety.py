import pyaudio
import struct
import keyboard
import threading
import win32gui
import win32con
import win32api
import random
import time
import ctypes

# DPI Awareness для корректной работы на всем экране
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

START_TIME = time.time()
running = True

# Переменные для курсора
mouse_x, mouse_y = win32api.GetCursorPos()
dx, dy = 30, 30


def audio_logic():
    global running
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=8000, output=True)
    t = 0
    try:
        while running:
            elapsed = time.time() - START_TIME

            if elapsed < 15:
                # 1. Звук из начала
                output = (t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7)
            elif 15 <= elapsed < 35:
                # 2. Второй звук
                output = (t * (t >> 5 | t >> 35) & 53 & t >> 9) ^ (t & t >> 16 | t >> 8)
            elif 35 <= elapsed < 50:
                # 3. Возврат первого звука
                output = (t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7)
            else:
                running = False
                break

            stream.write(struct.pack('B', output & 0xFF))
            t += 1
            if keyboard.is_pressed('esc'):
                running = False
                break
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def visual_logic():
    global running, mouse_x, mouse_y, dx, dy
    hdc = win32gui.GetDC(0)
    sw = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    sh = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    try:
        while running:
            elapsed = time.time() - START_TIME

            if elapsed < 15:
                # Стадия 1: Полный перелив
                color = win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                brush = win32gui.CreateSolidBrush(color)
                win32gui.SelectObject(hdc, brush)
                win32gui.PatBlt(hdc, left, top, sw, sh, win32con.PATINVERT)
                win32gui.DeleteObject(brush)
                time.sleep(0.005)

            elif 15 <= elapsed < 35:
                # Стадия 2: Прямоугольники
                for _ in range(5):
                    color = win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    brush = win32gui.CreateSolidBrush(color)
                    win32gui.SelectObject(hdc, brush)
                    x, y = random.randint(left, left + sw), random.randint(top, top + sh)
                    w, h = random.randint(100, 500), random.randint(100, 500)
                    win32gui.PatBlt(hdc, x, y, w, h, win32con.PATINVERT)
                    win32gui.DeleteObject(brush)
                time.sleep(0.005)

            elif 35 <= elapsed < 50:
                # Стадия 3: Инверсия + Прыгающий курсор
                win32gui.InvertRect(hdc, (left, top, left + sw, top + sh))

                mouse_x += dx
                mouse_y += dy
                if mouse_x <= left or mouse_x >= left + sw: dx = -dx
                if mouse_y <= top or mouse_y >= top + sh: dy = -dy
                win32api.SetCursorPos((int(mouse_x), int(mouse_y)))
                time.sleep(0.001)

            else:
                running = False
                break

    finally:
        # Безопасный выход: очищаем экран
        win32gui.InvalidateRect(0, None, True)
        win32gui.ReleaseDC(0, hdc)
        print("Программа завершена безопасно.")


if __name__ == "__main__":
    t_audio = threading.Thread(target=audio_logic, daemon=True)
    t_audio.start()
    visual_logic()
