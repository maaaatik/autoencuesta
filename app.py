import io
import os
import subprocess
import time
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

st.set_page_config(
    page_title="Encuestas automaticas by Matik",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ASCII_BANNER_1 = """⣿⣿⣿⣿⣿⣷⣿⣿⣿⡅⡹⢿⠆⠙⠋⠉⠻⠿⣿⣿⣿⣿⣿⣿⣮⠻⣦⡙⢷⡑⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣌⠡⠌⠂⣙⠻⣛⠻⠷⠐⠈⠛⢱⣮⣷⣽⣿
⣿⣿⣿⣿⡇⢿⢹⣿⣶⠐⠁⠀⣀⣠⣤⠄⠀⠀⠈⠙⠻⣿⣿⣿⣦⣵⣌⠻⣷⢝⠦⠚⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢟⣻⣿⣊⡃⠀⣙⠿⣿⣿⣿⣎⢮⡀⢮⣽⣿⣿
⢿⣿⣿⣿⣧⡸⡎⡛⡩⠖⠀⣴⣿⣿⣿⠀⠀⠀⠀⠸⠇⠀⠙⢿⣿⣿⣿⣷⣌⢷⣑⢷⣄⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣫⠶⠛⠉⠀⠁⠀⠈⠈⠀⠠⠜⠻⣿⣆⢿⣼⣿⣿⣿
⢐⣿⣿⣿⣿⣧⢧⣧⢻⣦⢀⣹⣿⣿⣿⣇⠀⠄⠀⠀⠀⡀⠀⠈⢻⣿⣿⣿⣿⣷⣝⢦⡹⠷⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⠈⠁⠀⠀⠀⠁⠀⠀⠀⠱⣶⣄⡀⠀⠈⠛⠜⣿⣿⣿⣿
⠀⠊⢫⣿⣏⣿⡌⣼⣄⢫⡌⣿⣿⣿⣿⣿⣦⡈⠲⣄⣤⣤⡡⢀⣠⣿⣿⣿⣿⣿⣿⣷⣼⣍⢬⣦⡙⣿⣿⣿⣿⣿⣯⢁⡄⠀⡀⡀⠀⠄⢈⣠⢪⠀⣿⣿⣿⣦⠀⢉⢂⠹⡿⣿⣿
⠀⠀⠄⢹⢃⢻⣟⠙⣿⣦⠱⢻⣿⣿⣿⣿⣿⣿⣷⣬⣍⣭⣥⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡙⢿⣼⡿⣿⣿⣿⣿⣿⣷⣄⠘⣱⢦⣤⡴⡿⢈⣼⣿⣿⣿⣇⣴⣶⣮⣅⢻⣿⡏
⠀⠀⠈⠹⣇⢡⢿⡆⠻⣿⣷⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣍⡻⣿⣟⣻⣿⣿⣿⣿⣷⣦⣥⣬⣤⣴⣾⣿⣿⣿⣿⣷⣿⣿⣿⣿⣷⡜⠃
⠀⠀⠀⢀⣘⠈⢂⠃⣧⡹⣿⣷⡄⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣮⣅⡙⢿⣟⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⡕⠂
⠀⠀⠀⠀⠀⠀⠛⢷⣜⢷⡌⠻⣿⣿⣦⣝⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⣹⣷⣦⣹⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠉⠃⠀"""

ASCII_GIRL_2 = """⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⡟⠀⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠀⢘⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⡇⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⡇⣿⠰⡀⠈⠄⠀⠀⠀⠀⠀⠀⠀⢳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣇⢻⡇⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠾⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⣿⣿⣄⢳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠈⠠⠀⠀⠀⠀⠀⠀⠡⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣄⠀⠀⠀⠀⠀⠘⠆⠀⠈⢿⣦⠀⠀⠠⠀⠀⠀⠀⠀⢰⣶⣶⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⡶⠀⠀⠀⠀⠀⠀⡀⠀⢀⣴⡄⠀⠀⠀⠀⠀⠀⠘⣦⣀⠀⠀⠀⢠⣀⠀⠀⠈⠳⠦⠀⠀⠀⠀⠀⠀⠐⠀⢻⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⣿⡿⠃⠜⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣇⠀⠀⠀⣷⣄⠀⠀⠈⠛⢷⣶⣤⡄⠙⠳⠦⣤⡀⠈⠀⠀⠀⡀⠸⣤⣄⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣿⠟⢠⠎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠈⠻⠷⠆⢰⣿⣿⣷⣤⡀⠈⠻⣷⣿⣿⣦⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠠⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⡿⢃⣴⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢶⣶⣄⠄⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠉⠀⢀⣠⣴⣶⣶⣶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⠋⣰⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣦⡀⢀⣾⣄⠠⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀
⣡⣿⣿⠃⠀⠀⠀⠀⠠⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⢋⣴⣿⣿⣿⣿⣦⣤⡹⣿⣿⣿⣿⣿⣿⣿⣿⣧⡁⠀⠈⠉⠛⠛⠿⣿⣷⣀⡐⠠⠷⣼⠂⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀
⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣉⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⡛⢿⣿⣿⣿⣿⣿⣿⣿⣷⣴⣆⣠⡀⠀⠀⠉⠛⠛⠛⠋⠉⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠀⠀⠀⠀⠀⠀⠀⠀
⣿⡡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⢌⡛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣦⣄⣀⣀⡠⠀⡤⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡻⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢿⣿⣿⣿⣿⣿⣿⣿⡿⠋⢀⣤⣄⣠⣴⠟⢁⡴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡛⢿⣿⣿⣿⣴⣿⣿⣿⠟⣁⠔⣫⣴⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡠⠀⠀⡐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡉⢿⡿⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣭⣀⡂⠉⢛⠻⠿⢋⠥⢊⣡⣾⣿⣷⡄⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⡔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣆⣻⣿⣷⣬⣹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣌⣒⠂⠭⠍⠛⠻⢿⠃⠀⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡜⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⣴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠘⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠙⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡾⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣦⣌⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣶⣄⡙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢠⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⡇⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⣶⣬⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠉⠀⠀⣀⣠⣴⣶⡶⠃⠐⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠟⠋⠉⣁⣠⣤⣶⣶⣿⣿⣿⣿⣿⡟⢡⡆⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠟⠛⠛⠉⠉⠀⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣿⡇⠀⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡆⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢻⡿⠛⢉⠤⠂⠁⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀
⣠⡆⠀⠗⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⡠⢊⣡⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣶⣿⣿⣿
⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠊⣴⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿
⠋⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⢺⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣠⡄⠀⢸⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⡇⠀⠀⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠢⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⢸⡇⠀⡆⢹⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠀⠀⠀⠀⠀⠀⠀⠀⡠⠀⠀⠀⠀⠀⠺⠃⠀⠀⠀⢀⡀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿"""

# --- ESTILO DARK MANGA ABIERTO (SIN CAJAS / A LA INTEMPERIE + ARTE BRAILLE ASCII) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+JP:wght@400;700;900&display=swap');

    :root {
        --bg-void: #050505;
        --text-pure: #FFFFFF;
        --text-muted: #999999;
        --line-dim: #262626;
    }

    /* Fondo negro puro sin cuadros */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
        background-color: var(--bg-void) !important;
        color: var(--text-pure) !important;
    }

    header[data-testid="stHeader"] {
        background-color: rgba(5, 5, 5, 0.85) !important;
        border-bottom: none !important;
    }

    .block-container {
        max-width: 1080px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }

    /* Eliminar bordes y fondos de contenedores para dejar todo a la intemperie */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0 1.8rem 0 !important;
        border-bottom: 1px solid #1F1F1F !important;
        border-radius: 0px !important;
    }

    /* Bloques ASCII Braille flotantes en negro y blanco */
    .ascii-art-banner {
        font-family: 'Courier New', 'JetBrains Mono', monospace;
        font-size: 7.4px;
        line-height: 7.6px;
        color: #E5E5E5;
        background: transparent;
        white-space: pre;
        overflow-x: hidden;
        letter-spacing: 0px;
        user-select: none;
        opacity: 0.92;
        margin-bottom: 1.2rem;
    }

    .ascii-art-side {
        font-family: 'Courier New', 'JetBrains Mono', monospace;
        font-size: 4.9px;
        line-height: 5.1px;
        color: #FFFFFF;
        background: transparent;
        white-space: pre;
        overflow-x: hidden;
        letter-spacing: 0px;
        user-select: none;
        opacity: 0.95;
    }

    .ascii-art-footer {
        font-family: 'Courier New', 'JetBrains Mono', monospace;
        font-size: 6.2px;
        line-height: 6.4px;
        color: #D4D4D4;
        background: transparent;
        white-space: pre;
        overflow-x: hidden;
        letter-spacing: 0px;
        user-select: none;
        opacity: 0.88;
    }

    /* Cabecera abierta */
    .open-hero {
        padding: 0.5rem 0 1rem 0;
    }

    .top-jp-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
        font-family: 'JetBrains Mono', 'Noto Sans JP', monospace;
        font-size: 0.76rem;
        color: #888888;
        letter-spacing: 0.14em;
    }

    .jp-pill {
        color: #FFFFFF;
        font-weight: 900;
        letter-spacing: 0.16em;
    }

    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        line-height: 1.05;
        margin: 0;
        text-transform: uppercase;
    }

    .hero-jp-sub {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: #8C8C8C;
        margin-top: 0.45rem;
        letter-spacing: 0.1em;
    }

    .hero-desc {
        font-size: 0.96rem;
        color: #BDBDBD;
        margin-top: 0.9rem;
        line-height: 1.6;
        max-width: 540px;
    }

    /* Títulos de sección abiertos */
    .section-open-head {
        display: flex;
        align-items: baseline;
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .sec-index {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 700;
        color: #FFFFFF;
        border-bottom: 2px solid #FFFFFF;
        padding-bottom: 2px;
    }

    .sec-name {
        font-size: 1.18rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        color: #FFFFFF;
    }

    .sec-jp {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 0.78rem;
        color: #737373;
        margin-left: auto;
        letter-spacing: 0.1em;
    }

    /* Textos generales */
    label, .stMarkdown p, .stCaption, [data-testid="stWidgetLabel"] p {
        color: #D4D4D4 !important;
    }

    /* Input abierto estilo línea inferior */
    .stTextInput input {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
        border-bottom: 1.5px solid #FFFFFF !important;
        border-radius: 0px !important;
        padding: 0.65rem 0.2rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input::placeholder {
        color: #525252 !important;
    }
    .stTextInput input:focus {
        box-shadow: none !important;
        border-bottom: 2.5px solid #FFFFFF !important;
    }

    /* Botones minimalistas sin cajas ni sombras */
    .stButton > button[kind="primary"], .stButton > button {
        background-color: #FFFFFF !important;
        color: #050505 !important;
        border: 1.5px solid #FFFFFF !important;
        border-radius: 0px !important;
        font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.84rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }

    /* Botones de descarga abiertos */
    .stDownloadButton > button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        padding: 0.55rem 1.1rem !important;
        width: 100%;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }
    .stDownloadButton > button:hover {
        background-color: #FFFFFF !important;
        color: #050505 !important;
    }

    /* File Uploader abierto */
    [data-testid="stFileUploader"] section {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed #666666 !important;
        border-radius: 0px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #FFFFFF !important;
        color: #050505 !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
    }

    /* Expander abierto */
    [data-testid="stExpander"] {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid #262626 !important;
        box-shadow: none !important;
    }
    [data-testid="stExpander"] summary {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        padding-left: 0 !important;
    }

    /* Alertas limpias sin caja cerrada */
    [data-testid="stAlert"] {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
        border-left: 3px solid #FFFFFF !important;
        border-radius: 0px !important;
        padding-left: 1rem !important;
    }

    /* Barra de progreso */
    .stProgress > div > div > div > div {
        background-color: #FFFFFF !important;
    }
    .stProgress > div > div {
        background-color: #1F1F1F !important;
    }

    /* Badges de tipo */
    .type-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 700;
        color: #050505;
        background-color: #FFFFFF;
        padding: 1px 6px;
        margin-left: 6px;
        vertical-align: middle;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def asegurar_chromium():
    """Instala el binario de Chromium en Streamlit Cloud si aún no está presente."""
    try:
        with sync_playwright() as p:
            exe = p.chromium.executable_path
            if os.path.exists(exe):
                return True
    except Exception:
        pass

    subprocess.run(["playwright", "install", "chromium"], check=True)
    return True


asegurar_chromium()


def detectar_plataforma(url: str) -> str:
    u = url.lower()
    if "forms.office.com" in u or "forms.cloud.microsoft" in u:
        return "microsoft"
    if "docs.google.com/forms" in u or "forms.gle" in u:
        return "google"
    return "desconocida"


def _extraer_opciones_ms(item, role_name: str) -> list[str]:
    opciones = []
    els = item.get_by_role(role_name)
    for i in range(els.count()):
        el = els.nth(i)
        label = el.get_attribute("aria-label") or el.get_attribute("value") or el.inner_text()
        if not label or not label.strip():
            parent_text = el.locator("xpath=..").inner_text()
            if parent_text:
                label = parent_text.splitlines()[0]
        if label:
            clean_lbl = label.strip()
            if clean_lbl and clean_lbl not in opciones:
                opciones.append(clean_lbl)
    return opciones


def inspeccionar_microsoft_forms(page) -> list[dict]:
    preguntas_map = {}

    for _ in range(15):
        items = page.locator("[data-automation-id='questionItem']")
        count = items.count()
        for idx in range(count):
            item = items.nth(idx)
            if not item.is_visible():
                continue

            title_el = item.locator("[data-automation-id='questionTitle']")
            if title_el.count() > 0:
                texto = title_el.first.inner_text().strip()
            else:
                lineas = [l.strip() for l in item.inner_text().splitlines() if l.strip()]
                texto = lineas[0] if lineas else f"Pregunta {len(preguntas_map) + 1}"

            texto_limpio = texto.lstrip("0123456789. ").rstrip("* ").strip()
            if not texto_limpio:
                texto_limpio = texto

            if texto_limpio in preguntas_map:
                continue

            radios = item.get_by_role("radio")
            checkboxes = item.get_by_role("checkbox")
            inputs = item.locator("input:not([type='radio']):not([type='checkbox']), textarea")

            if radios.count() > 0:
                opciones = _extraer_opciones_ms(item, "radio")
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "radio",
                    "opciones": opciones,
                }
            elif checkboxes.count() > 0:
                opciones = _extraer_opciones_ms(item, "checkbox")
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "checkbox",
                    "opciones": opciones,
                }
            elif inputs.count() > 0:
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "texto",
                    "opciones": [],
                }

        btn_siguiente = page.locator("button[data-automation-id='nextButton'], button:has-text('Siguiente'), button:has-text('Next')")
        if btn_siguiente.count() > 0 and btn_siguiente.first.is_visible():
            for idx in range(items.count()):
                item = items.nth(idx)
                if not item.is_visible():
                    continue
                radios = item.get_by_role("radio")
                if radios.count() > 0:
                    radios.first.click(force=True)
                checkboxes = item.get_by_role("checkbox")
                if checkboxes.count() > 0:
                    checkboxes.first.click(force=True)
                inputs = item.locator("input:not([type='radio']):not([type='checkbox']), textarea")
                if inputs.count() > 0:
                    inputs.first.fill("1")

            time.sleep(0.3)
            btn_siguiente.first.click(force=True)
            time.sleep(1.2)
        else:
            break

    return list(preguntas_map.values())


def inspeccionar_google_forms(page) -> list[dict]:
    preguntas_map = {}

    for _ in range(15):
        items = page.locator("div[role='listitem']")
        count = items.count()
        for idx in range(count):
            item = items.nth(idx)
            if not item.is_visible():
                continue

            heading = item.locator("[role='heading']")
            if heading.count() == 0:
                continue
            texto_limpio = heading.first.inner_text().replace("*", "").strip()
            if not texto_limpio or texto_limpio in preguntas_map:
                continue

            radios = item.locator("[role='radio']")
            checkboxes = item.locator("[role='checkbox']")
            inputs = item.locator("input[type='text'], input[type='number'], textarea")

            if radios.count() > 0:
                opciones = []
                for r_i in range(radios.count()):
                    val = radios.nth(r_i).get_attribute("data-value") or radios.nth(r_i).get_attribute("aria-label")
                    if val and val != "__other_option__":
                        opciones.append(val.strip())
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "radio",
                    "opciones": opciones,
                }
            elif checkboxes.count() > 0:
                opciones = []
                for c_i in range(checkboxes.count()):
                    val = checkboxes.nth(c_i).get_attribute("data-answer-value") or checkboxes.nth(c_i).get_attribute("aria-label")
                    if val and val != "__other_option__":
                        opciones.append(val.strip())
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "checkbox",
                    "opciones": opciones,
                }
            elif inputs.count() > 0:
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "texto",
                    "opciones": [],
                }

        btn_siguiente = page.locator("div[role='button']").filter(has_text="Siguiente")
        if btn_siguiente.count() > 0 and btn_siguiente.first.is_visible():
            for idx in range(items.count()):
                item = items.nth(idx)
                if not item.is_visible():
                    continue
                radios = item.locator("[role='radio']")
                if radios.count() > 0:
                    radios.first.click()
                inputs = item.locator("input[type='text'], input[type='number'], textarea")
                if inputs.count() > 0:
                    inputs.first.fill("1")
            btn_siguiente.first.click(force=True)
            time.sleep(1.0)
        else:
            break

    return list(preguntas_map.values())


def extraer_esquema(url: str) -> tuple[str, list[dict]]:
    plataforma = detectar_plataforma(url)
    if plataforma == "desconocida":
        raise ValueError("URL no reconocida. Usa un enlace de Microsoft Forms o Google Forms.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--font-render-hinting=none",
            ],
        )
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(1.5)

        if plataforma == "microsoft":
            page.wait_for_selector("[data-automation-id='questionItem']", timeout=20000)
            esquema = inspeccionar_microsoft_forms(page)
        else:
            page.wait_for_selector("div[role='listitem']", timeout=20000)
            esquema = inspeccionar_google_forms(page)

        browser.close()
    return plataforma, esquema


def _normalizar_valor_excel(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "nat"):
        return ""
    # Si Excel convirtió un rango tipo "18-24" o "1-5" en fecha "2026-04-18 00:00:00"
    if "00:00:00" in s:
        s = s.replace(" 00:00:00", "")
    return s


def llenar_pagina_microsoft(page, fila: dict, esquema: list[dict]):
    for q in esquema:
        preg = q["pregunta"]
        valor = _normalizar_valor_excel(fila.get(preg, ""))
        if not valor:
            continue

        item = page.locator("[data-automation-id='questionItem']").filter(has_text=preg)
        if item.count() == 0 or not item.first.is_visible():
            continue

        if q["tipo"] == "radio":
            radio = item.first.get_by_role("radio", name=valor, exact=True)
            if radio.count() == 0:
                radio = item.first.get_by_role("radio", name=valor, exact=False)
            if radio.count() > 0:
                radio.first.click(force=True)
        elif q["tipo"] == "checkbox":
            for opcion in [o.strip() for o in valor.split(";") if o.strip()]:
                chk = item.first.get_by_role("checkbox", name=opcion, exact=True)
                if chk.count() == 0:
                    chk = item.first.get_by_role("checkbox", name=opcion, exact=False)
                if chk.count() > 0:
                    chk.first.click(force=True)
        else:
            campo = item.first.locator("input:not([type='radio']):not([type='checkbox']), textarea").first
            if campo.count() > 0:
                campo.fill(valor)


def llenar_pagina_google(page, fila: dict, esquema: list[dict]):
    for q in esquema:
        preg = q["pregunta"]
        valor = _normalizar_valor_excel(fila.get(preg, ""))
        if not valor:
            continue

        item = page.locator("div[role='listitem']").filter(has_text=preg)
        if item.count() == 0 or not item.first.is_visible():
            continue

        if q["tipo"] == "radio":
            radio = item.first.locator(f"[role='radio'][data-value='{valor}'], [role='radio'][aria-label='{valor}']")
            if radio.count() > 0:
                radio.first.click(force=True)
        elif q["tipo"] == "checkbox":
            for opcion in [o.strip() for o in valor.split(";") if o.strip()]:
                chk = item.first.locator(f"[role='checkbox'][data-answer-value='{opcion}'], [role='checkbox'][aria-label='{opcion}']")
                if chk.count() > 0:
                    chk.first.click(force=True)
        else:
            campo = item.first.locator("input[type='text'], input[type='number'], textarea").first
            if campo.count() > 0:
                campo.fill(valor)


def ejecutar_envios(url: str, plataforma: str, esquema: list[dict], registros: list[dict], delay: float):
    enviadas = 0
    errores = []
    barra = st.progress(0)
    estado = st.empty()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--font-render-hinting=none",
            ],
        )
        page = browser.new_page()

        for i, fila in enumerate(registros, start=1):
            estado.info(f"Procesando envío {i} de {len(registros)}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if plataforma == "microsoft":
                    page.wait_for_selector("[data-automation-id='questionItem']", timeout=20000)
                    for _ in range(15):
                        llenar_pagina_microsoft(page, fila, esquema)
                        time.sleep(0.35)

                        btn_enviar = page.locator("button[data-automation-id='submitButton'], button:has-text('Enviar'), button:has-text('Submit')")
                        if btn_enviar.count() > 0 and btn_enviar.first.is_visible():
                            btn_enviar.first.click(force=True)
                            break

                        btn_sig = page.locator("button[data-automation-id='nextButton'], button:has-text('Siguiente'), button:has-text('Next')")
                        if btn_sig.count() > 0 and btn_sig.first.is_visible():
                            btn_sig.first.click(force=True)
                            time.sleep(0.9)
                        else:
                            break

                    # Espera confirmación en español o inglés
                    confirmacion = page.locator(
                        "text=/Enviar otra respuesta|Submit another response|Se ha enviado tu respuesta|Your response was submitted|Gracias|Thank you/i"
                    )
                    confirmacion.first.wait_for(state="visible", timeout=15000)

                else:
                    page.wait_for_selector("div[role='listitem']", timeout=20000)
                    for _ in range(15):
                        llenar_pagina_google(page, fila, esquema)
                        time.sleep(0.35)

                        btn_enviar = page.locator("div[role='button']").filter(has_text="Enviar")
                        if btn_enviar.count() == 0:
                            btn_enviar = page.locator("div[role='button']").filter(has_text="Submit")
                        if btn_enviar.count() > 0 and btn_enviar.first.is_visible():
                            btn_enviar.first.click(force=True)
                            break

                        btn_sig = page.locator("div[role='button']").filter(has_text="Siguiente")
                        if btn_sig.count() == 0:
                            btn_sig = page.locator("div[role='button']").filter(has_text="Next")
                        if btn_sig.count() > 0 and btn_sig.first.is_visible():
                            btn_sig.first.click(force=True)
                            time.sleep(0.9)
                        else:
                            break

                    confirmacion = page.locator(
                        "text=/Enviar otra respuesta|Submit another response|Se registró tu respuesta|Your response has been recorded/i"
                    )
                    confirmacion.first.wait_for(state="visible", timeout=15000)

                enviadas += 1
                time.sleep(delay)

            except PlaywrightTimeoutError:
                # Revisa si Microsoft Forms muestra mensaje de validación de campo obligatorio
                alerta_ms = page.locator("[data-automation-id='validationError'], [role='alert']")
                if alerta_ms.count() > 0 and alerta_ms.first.is_visible():
                    detalle = alerta_ms.first.inner_text().strip()
                    errores.append(f"Fila {i}: Formulario bloqueado por validación ({detalle}). Revisa columnas vacías u opciones mal escritas.")
                else:
                    errores.append(f"Fila {i}: Tiempo de espera agotado (revisa que todas las preguntas obligatorias tengan respuesta en el Excel).")
            except Exception as e:
                errores.append(f"Fila {i}: {e}")

            barra.progress(i / len(registros))

        browser.close()

    estado.empty()
    return enviadas, errores


# --- ENCABEZADO ABIERTO (A LA INTEMPERIE) CON TEXTO CENTRADO ---
st.markdown(f'<div class="ascii-art-banner">{ASCII_BANNER_1}</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="open-hero" style="text-align: center; max-width: 760px; margin: 0 auto 1.2rem auto;">
        <div class="top-jp-line" style="justify-content: center; gap: 1.5rem;">
            <span>FORMS AUTOMATION SYSTEM</span>
            <span class="jp-pill">自動アンケート // マティク</span>
        </div>
        <h1 class="hero-title" style="text-align: center;">Encuestas automaticas by Matik</h1>
        <div class="hero-jp-sub" style="text-align: center;">マティク・オートメーション</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<hr style="border:none; border-top:1px solid #262626; margin: 1rem 0 2rem 0;">', unsafe_allow_html=True)

if "esquema" not in st.session_state:
    st.session_state.esquema = None
    st.session_state.plataforma = None
    st.session_state.url = ""

# --- SECCIÓN 01 ---
with st.container():
    st.markdown(
        """
        <div class="section-open-head">
            <span class="sec-index">01</span>
            <span class="sec-name">Enlace del formulario</span>
            <span class="sec-jp">リンク入力</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    url_input = st.text_input(
        "URL pública de la encuesta",
        placeholder="https://forms.cloud.microsoft/... o https://docs.google.com/forms/...",
        label_visibility="collapsed",
    )

    if st.button("Extraer preguntas automáticamente", type="primary"):
        if not url_input.strip():
            st.warning("Ingresa un enlace válido primero.")
        else:
            with st.spinner("Escaneando secciones del formulario..."):
                try:
                    plat, esq = extraer_esquema(url_input.strip())
                    st.session_state.esquema = esq
                    st.session_state.plataforma = plat
                    st.session_state.url = url_input.strip()
                    st.success(f"Plataforma detectada: **{plat.upper()}** — **{len(esq)}** preguntas extraídas correctamente.")
                except Exception as e:
                    st.error(f"No se pudo inspeccionar el formulario: {e}")

if st.session_state.esquema:
    esquema = st.session_state.esquema

    with st.expander("Estructura y opciones detectadas // 質問リスト", expanded=True):
        for idx, q in enumerate(esquema, 1):
            opts = ", ".join(q["opciones"]) if q["opciones"] else "Campo abierto / numérico"
            st.markdown(
                f"**{idx:02d}. {q['pregunta']}** <span class='type-badge'>{q['tipo'].upper()}</span><br>"
                f"<span style='color:#8C8C8C; font-size:0.86rem;'>Opciones: {opts}</span>",
                unsafe_allow_html=True,
            )

    # --- SECCIÓN 02 ---
    with st.container():
        st.markdown(
            """
            <div class="section-open-head" style="margin-top:1.5rem;">
                <span class="sec-index">02</span>
                <span class="sec-name">Plantilla de datos</span>
                <span class="sec-jp">テンプレート</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Descarga el formato exacto con las columnas vinculadas a cada pregunta.")
        columnas = [q["pregunta"] for q in esquema]
        fila_ejemplo = {
            q["pregunta"]: (q["opciones"][0] if q["opciones"] else "Ejemplo")
            for q in esquema
        }
        df_plantilla = pd.DataFrame([fila_ejemplo], columns=columnas)

        buffer_xlsx = io.BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="openpyxl") as writer:
            df_plantilla.to_excel(writer, index=False, sheet_name="Respuestas")
            info_opciones = [
                {"Pregunta": q["pregunta"], "Tipo": q["tipo"], "Opciones válidas": " | ".join(q["opciones"])}
                for q in esquema
            ]
            pd.DataFrame(info_opciones).to_excel(writer, index=False, sheet_name="Opciones_Validas")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Descargar plantilla Excel (.xlsx)",
                data=buffer_xlsx.getvalue(),
                file_name="plantilla_encuesta_matik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with col2:
            st.download_button(
                label="Descargar plantilla CSV (.csv)",
                data=df_plantilla.to_csv(index=False).encode("utf-8-sig"),
                file_name="plantilla_encuesta_matik.csv",
                mime="text/csv",
            )

    # --- SECCIÓN 03 ---
    with st.container():
        st.markdown(
            """
            <div class="section-open-head" style="margin-top:1.5rem;">
                <span class="sec-index">03</span>
                <span class="sec-name">Carga y ejecución masiva</span>
                <span class="sec-jp">自動送信</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        archivo = st.file_uploader("Archivo de respuestas (.xlsx o .csv)", type=["xlsx", "csv"])
        delay = st.slider("Intervalo entre envíos (segundos)", min_value=0.5, max_value=5.0, value=1.2, step=0.1)

        if archivo is not None:
            if archivo.name.endswith(".csv"):
                df_resp = pd.read_csv(archivo, dtype=str)
            else:
                df_resp = pd.read_excel(archivo, sheet_name=0, dtype=str)

            st.caption(f"Vista previa — **{len(df_resp)}** registros listos para procesar:")
            st.dataframe(df_resp.head(10), use_container_width=True)

            if st.button("Iniciar envío masivo", type="primary"):
                registros = df_resp.to_dict(orient="records")
                enviadas, errores = ejecutar_envios(
                    st.session_state.url,
                    st.session_state.plataforma,
                    esquema,
                    registros,
                    delay,
                )
                st.success(f"Ejecución completada: **{enviadas}/{len(registros)}** respuestas enviadas.")
                if errores:
                    with st.expander("Registro de incidencias"):
                        for err in errores:
                            st.error(err)

# --- PIE DE PÁGINA ABIERTO CON EL SEGUNDO PERSONAJE ASCII ---
st.markdown('<hr style="border:none; border-top:1px solid #262626; margin: 2.5rem 0 1.5rem 0;">', unsafe_allow_html=True)
col_foot_art, col_foot_txt = st.columns([1.4, 1])

with col_foot_art:
    st.markdown(f'<div class="ascii-art-footer">{ASCII_GIRL_2}</div>', unsafe_allow_html=True)

with col_foot_txt:
    st.markdown(
        """
        <div style="text-align:right; padding-top: 2rem;">
            <div style="font-family:'Noto Sans JP', sans-serif; font-size:1.1rem; font-weight:900; color:#FFFFFF; letter-spacing:0.15em;">
                黒と白 // マティク
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#737373; margin-top:0.4rem; letter-spacing:0.12em;">
                ENCUESTAS AUTOMATICAS BY MATIK
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
