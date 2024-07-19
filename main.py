# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_option_menu import option_menu
from st_btn_select import st_btn_select
import extra_streamlit_components as stx
# from streamlit_cookies_manager import EncryptedCookieManager
# from cookies import Cookies, Cookie
# import http.cookies

import json
import sqlite3
import tempfile
import re
import time
import webbrowser
from datetime import datetime, timedelta
import random

import arabic_reshaper
from youtube_transcript_api import YouTubeTranscriptApi
from kivy.core.clipboard import Clipboard
import dns.resolver
import requests
import pygame
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import stripe

cookie_manager = stx.CookieManager()
# expiration_date = datetime.now() + timedelta(days=60)
# cookie_manager.set(cookie="user_id", val="another_cookie_try", expires_at=expiration_date)
# cookie_manager.delete(cookie="user_id")

conn = sqlite3.connect('text_areas.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS areas (youtube_content TEXT, pre_paraphrase_content TEXT, 
paraphrase_content TEXT, summary_content TEXT, email TEXT, password TEXT, customer_id TEXT, trial_start_date REAL)""")

# cursor.execute("DELETE FROM areas")
# cursor.execute("""INSERT INTO areas VALUES (?, ?, ?, ?)""", ("", "", "", ""))

if 'bullshit3' not in st.session_state:
    st.session_state['bullshit3'] = ""

st.session_state['bullshit3'] = cookie_manager.get(cookie="user_id")
st.write(st.session_state['bullshit3'])

try:
    cursor.execute("SELECT youtube_content FROM areas WHERE customer_id = ?", (str(cookie_manager.get(cookie="user_id")), ))
    youtube_text_area_value = cursor.fetchone()[0]
    # cursor.execute("SELECT pre_paraphrase_content FROM areas WHERE customer_id = ?", (cookie_manager.get(cookie="user_id"), ))
    pre_paraphrase_text_area_value = None
    # cursor.execute("SELECT paraphrase_content FROM areas")
    paraphrase_text_area_value = None
    # cursor.execute("SELECT summary_content FROM areas")
    summary_text_area_value = None
except:
    pass


conn.commit()
conn.close()


conn = sqlite3.connect('settings_save.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS settings (voice_gender TEXT, summary_type INTEGER, summary_mode INTEGER, verification_code INT, customer_id TEXT)""")
# cursor.execute("INSERT INTO settings VALUES (?, ?, ?)", ("Female", 0, 0))

conn.commit()
conn.close()


language_codes_youtube_api = ["en", "zh-CN", "zh", "zh-TW", "es", "fr", "pt", "hi", "ar", "ja", "bn", "ru", "id", "af", "sq", "am", "hy", "az", "bs", "bg", "my", "hr", "cs", "da", "nl", "et", "fil", "fi", "ka", "de", "el", "ht", "he", "hu", "is", "ga", "it", "kk", "rw", "km", "ko", "ku", "ky", "lv", "lt", "mk", "ms", "mt", "ne", "no", "fa", "pl", "ro", "sm", "sr", "si", "sk", "sl", "so", "sw", "sv", "te", "th", "ti", "tr", "tk", "uk", "ur", "uz", "vi", "cy"]



all_languages = [
    "", "English", "Chinese", "Spanish", "French", "Portuguese", "Hindi", "Arabic", "Japanese",
    "Bengali", "Russian", "Indonesian", "Afrikaans", "Albanian", "Amharic", "Arabic",
    "Armenian", "Azerbaijani", "Bengali", "Bosnian", "Bulgarian", "Burmese (Myanmar)",
    "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Filipinian",
    "Finnish", "French", "Georgian", "German", "Greek", "Haitian Creole", "Hebrew", "Hindi",
    "Hungarian", "Icelandic", "Indonesian", "Irish", "Italian", "Japanese", "Kazakh",
    "Kinyarwanda", "Khmer", "Korean", "Kurdish", "Kyrgyz", "Latvian", "Lithuanian",
    "Macedonian", "Malay", "Maltese", "Nepali", "Norwegian", "Persian", "Polish",
    "Portuguese", "Russian", "Romanian", "Samoan", "Serbian", "Sinhala", "Slovak",
    "Slovenian", "Somali", "Spanish", "Swahili", "Swedish", "Telugu", "Thai", "Tigrinya",
    "Turkish", "Turkmen", "Ukrainian", "Urdu", "Uzbek", "Vietnamese", "Welsh"
]


all_codes = [
    "", "en", "zh", "es", "fr", "pt", "hi", "ar", "ja",
    "bn", "ru", "id", "af", "sq", "am", "ar",
    "hy", "az", "bn", "bs", "bg", "my",
    "zh", "hr", "cs", "da", "nl", "en", "et", "fil",
    "fi", "fr", "ka", "de", "el", "ht", "he", "hi",
    "hu", "is", "id", "ga", "it", "ja", "kk",
    "rw", "km", "ko", "ku", "ky", "lv", "lt",
    "mk", "ms", "mt", "ne", "no", "fa", "pl",
    "pt", "ru", "ro", "sm", "sr", "si", "sk",
    "sl", "so", "es", "sw", "sv", "te", "th", "ti",
    "tr", "tk", "uk", "ur", "uz", "vi", "cy"
]

# Creating the dictionary
language_code_dict = dict(zip(all_languages, all_codes))

# ------------------------------------USER AUTHENTICATION AND REDIRECTION-----------------------------------------------
# 259200 (free trial righ amount of seconds
time.sleep(0.5)

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

    user_id_cookie = cookie_manager.get(cookie="user_id")
    # st.header(user_id_cookie)
    if user_id_cookie:
        st.subheader("cookie is present")

        try:
            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            st.header("STEP 1")
            subscriptions = stripe.Subscription.list(customer=user_id_cookie, status='all')
            st.header("STEP 2")

            if subscriptions.data:
                latest_subscription = subscriptions.data[0]
                subscription_status = latest_subscription.status
                if subscription_status == "active":
                    st.session_state.current_page = "Summary"

                elif subscription_status == "canceled":
                    st.session_state.current_page = "Subscribe"
                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.text = "Regain access"
                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.color = (0, 0, 0, 1)
                else:
                    st.session_state.current_page = "Subscribe"

            else:
                st.header("STEP 3")
                cursor.execute("SELECT trial_start_date FROM areas WHERE customer_id = ?", (user_id_cookie, ))
                start_date_of_trial = cursor.fetchone()[0]
                current_date = time.time()

                if start_date_of_trial is None:
                    st.header("STEP 4")
                    st.session_state.current_page = "Sign up"
                    st.subheader("No trial")
                elif current_date - start_date_of_trial > 60:
                    st.header("STEP 5")
                    st.session_state.current_page = "Subscribe"

                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.text = "Trial ended"
                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.color = (0.67, 0.33, 0, 1)
                elif current_date - start_date_of_trial < 60:
                    st.header("STEP 6")
                    st.session_state.current_page = "Summary"
                else:
                    st.header("STEP 7")
                    pass

        except Exception as e:
            st.header(e)
            st.header("STEP 8")
            cursor.execute("SELECT trial_start_date FROM areas WHERE customer_id = ?", (user_id_cookie,))

            start_date_of_trial = cursor.fetchone()[0]
            current_date = time.time()
            if start_date_of_trial is None:
                st.subheader("trial date is None")
                st.session_state.current_page = "Sign up"
            elif start_date_of_trial < 100:
                st.subheader("normally you don't enter this condition")
                st.session_state.current_page = "Sign up"
            elif current_date - start_date_of_trial > 60:
                st.subheader("right one")
                st.session_state.current_page = "Subscribe"
                # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.text = "Trial ended"
                # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.color = (0.67, 0.33, 0, 1)
            elif current_date - start_date_of_trial < 60:
                st.subheader("backup option")
                st.session_state.current_page = "Summary"

        conn.commit()
        conn.close()

    elif not user_id_cookie:
        st.subheader("No cookie")
        st.session_state.current_page = "Login"

    else:
        st.header("Else cookie")
        st.session_state.current_page = "Login"

# ---------------------------------------------------------------------------------------------------------------------------


# Initialize session states
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Sign up'

if 'language_switch' not in st.session_state:
    st.session_state['language_switch'] = 'English'

if 'audio_icon' not in st.session_state:
    st.session_state['audio_icon'] = '🔊 Listen'

if 'paraphrase_audio_icon' not in st.session_state:
    st.session_state['paraphrase_audio_icon'] = '🔊 Listen'

if 'channel' not in st.session_state:
    st.session_state['channel'] = None

if 'track' not in st.session_state:
    st.session_state['track'] = None

if 'voice_gender' not in st.session_state:
    try:
        conn = sqlite3.connect('settings_save.db')
        cursor = conn.cursor()
        cursor.execute("SELECT voice_gender FROM settings")
        the_gender = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if the_gender == "Female":
            st.session_state['voice_gender'] = "♀️ Female Voice"
        else:
            st.session_state['voice_gender'] = "♂️ Male Voice"
    except:
        pass

user_id = random.randint(0, 10)

if 'is_signup_disabled' not in st.session_state:
    st.session_state['is_signup_disabled'] = True

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = user_id


def callback(key):
    selection = st.session_state[key]
    if selection == "Youtube":
        st.session_state.current_page = "Youtube"
    elif selection == "Paraphrase":
        st.session_state.current_page = "Paraphrase"
    elif selection == "Summary":
        st.session_state.current_page = "Summary"


def go_settings():
    st.session_state.current_page = "Summary"


def go_contact_page():
    st.session_state.current_page = "Contact"


def go_home():
    st.session_state.current_page = "Summary"


if st.session_state.current_page == 'Youtube':
    top_navigation = option_menu(None, ["Youtube", "Summary", "Paraphrase"],
                                 icons=["📋", "📋", "📝"],
                                 orientation="horizontal",
                                 default_index=0,
                                 on_change=callback, key="youtube_menu")

    pygame.mixer.init()

    st.write("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        youtube_copy_but = st.button("📋 Copy", use_container_width=True)
    with col2:
        translator = st.button("🌐 Translate", use_container_width=True)
    with col3:
        youtube_audio_but = st.button(label=st.session_state['audio_icon'], use_container_width=True)
    with col4:
        erase_youtube = st.button("❌ Delete", use_container_width=True, help="Clear the text field")


    def translate():
        lang_name = st.session_state['language_switch']
        if lang_name == "- English":
            lang_name = "English"
        lang_code_to_translate_to = language_code_dict.get(lang_name, None)

        url1 = "https://google-translator9.p.rapidapi.com/v2/detect"
        payload1 = {"q": youtube_text_area[:2500]}
        headers1 = {
            "content-type": "application/json",
            "X-RapidAPI-Key": the_rapid_key,
            "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
        }
        response = requests.post(url1, json=payload1, headers=headers1)
        lang_code = response.json()["data"]["detections"][0][0]["language"]

        if len(youtube_text_area) > 10:

            if len(youtube_text_area) < 99000:

                if lang_code != lang_code_to_translate_to:

                    url = "https://google-translator9.p.rapidapi.com/v2"
                    payload = {
                        "q": youtube_text_area,
                        "source": lang_code,
                        "target": lang_code_to_translate_to,
                        "format": "text"
                    }
                    headers = {
                        "content-type": "application/json",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    translated_text = response.json()["data"]["translations"][0]["translatedText"]

                    arabic_languages = "arfaurkuhe"

                    if lang_code_to_translate_to not in arabic_languages:

                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?",
                                       (translated_text, youtube_text_area_value))
                        conn.commit()
                        conn.close()

                    else:

                        if lang_code_to_translate_to == "ar" or lang_code_to_translate_to == "fa" or lang_code_to_translate_to == "ur" or lang_code_to_translate_to == "ku" or lang_code_to_translate_to == "he":
                            full_arabic_text = ""
                            arabic_text = arabic_reshaper.reshape(translated_text)
                            lines = []
                            for i in range(0, len(arabic_text), 100):
                                lines.append(arabic_text[i:i + 100])

                            for line in lines:
                                # full_arabic_text += line[::-1] + "\n"
                                full_arabic_text += line[:-1:]

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?",
                                           (full_arabic_text, youtube_text_area_value))
                            conn.commit()
                            conn.close()

                else:
                    pass

            else:

                if lang_code != lang_code_to_translate_to:

                    MAX_CHUNK_SIZE = 94000

                    if len(youtube_text_area) > MAX_CHUNK_SIZE:
                        translated_chunks = []
                        full_translation = ""
                        start_index = 0
                        while start_index < len(youtube_text_area):
                            end_index = start_index + MAX_CHUNK_SIZE
                            chunk = youtube_text_area[start_index:end_index]
                            chunk = chunk[:MAX_CHUNK_SIZE]  # Ensure the chunk is within the limit
                            translated_chunks.append(chunk)
                            start_index = end_index

                        for chunk in translated_chunks:
                            url = "https://google-translator9.p.rapidapi.com/v2"

                            payload = {
                                "q": str(chunk),
                                "source": lang_code,
                                "target": lang_code_to_translate_to,
                                "format": "text"
                            }
                            headers = {
                                "content-type": "application/json",
                                "X-RapidAPI-Key": the_rapid_key,
                                "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                            }

                            response = requests.post(url, json=payload, headers=headers)
                            full_translation += response.json()["data"]["translations"][0]["translatedText"]

                        arabic_languages = "arfaurkuhe"

                        if lang_code_to_translate_to not in arabic_languages:

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?",
                                           (full_translation, youtube_text_area_value))
                            conn.commit()
                            conn.close()

                        else:

                            if lang_code_to_translate_to == "ar" or lang_code_to_translate_to == "fa" or lang_code_to_translate_to == "ur" or lang_code_to_translate_to == "ku" or lang_code_to_translate_to == "he":
                                full_arabic_text = ""
                                arabic_text = arabic_reshaper.reshape(full_translation)
                                lines = []
                                for i in range(0, len(arabic_text), 100):
                                    lines.append(arabic_text[i:i + 100])

                                for line in lines:
                                    # full_arabic_text += line[::-1] + "\n"
                                    full_arabic_text += line[:-1:]

                                conn = sqlite3.connect('text_areas.db')
                                cursor = conn.cursor()
                                cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?",
                                               (full_arabic_text, youtube_text_area_value))
                                conn.commit()
                                conn.close()


    if translator:
        youtube_language = st.selectbox("Select a language...", ("- English", "Chinese", "Spanish", "French", "Portuguese", "Hindi", "Arabic", "Japanese", "Bengali", "Russian", "Indonesian", "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani", "Bengali", "Bosnian", "Bulgarian", "Burmese (Myanmar)", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Filipinian", "Finnish", "French", "Georgian", "German", "Greek", "Haitian Creole", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Irish", "Italian", "Japanese", "Kazakh", "Kinyarwanda", "Khmer", "Korean", "Kurdish", "Kyrgyz", "Latvian", "Lithuanian", "Macedonian", "Malay", "Maltese", "Nepali", "Norwegian", "Persian", "Polish", "Portuguese", "Russian", "Romanian", "Samoan", "Serbian", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Swahili", "Swedish", "Telugu", "Thai", "Tigrinya", "Turkish", "Turkmen", "Ukrainian", "Urdu", "Uzbek", "Vietnamese", "Welsh"), key='language_switch', on_change=translate)

    youtube_message_placeholder = st.empty()

    youtube_text_area = st.text_area("Y", label_visibility="hidden", placeholder="Paste Youtube url...", height=300, value=youtube_text_area_value)

    transcribe_but = st.button("Transcribe", use_container_width=True, type="primary")

    st.write("")
    st.write("")

    bottom_col1, bottom_col2, bottom_col3 = st.columns(3)
    with bottom_col2:
        settings_but = st.button("⚙ Settings", use_container_width=True, on_click=go_settings)


    def play_audio():
        global audio_file

        if st.session_state['voice_gender'] == "♀️ Female Voice":
            gender = "Female"
        else:
            gender = "Male"

        if youtube_text_area == "":
            youtube_message_placeholder.error("Please provide some text to be read", icon="⚠")
            time.sleep(2.5)
            st.rerun()

        elif len(youtube_text_area) < 8:
            youtube_message_placeholder.error("Please provide a bit longer text", icon="⚠")
            time.sleep(2.5)
            st.rerun()

        else:

            try:
                if st.session_state['audio_icon'] == "▶ Resume":
                    # st.session_state['audio_icon'] = "⏸ Pause"
                    if st.session_state['channel'].get_busy() and st.session_state['channel'].get_sound() == st.session_state['track']:
                        st.session_state['channel'].unpause()

                elif st.session_state['audio_icon'] == "🔊 Listen":

                    text_to_be_read = youtube_text_area[:9300]

                    url = "https://ai-auto-text-to-speech.p.rapidapi.com/edgetts"
                    payload = {
                        "gender": gender,
                        "text": text_to_be_read
                    }
                    headers = {
                        "content-type": "application/json",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "ai-auto-text-to-speech.p.rapidapi.com"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    reformatted_response = json.loads(response.text)
                    audio_file_url = reformatted_response["audio_file_url"]

                    audio_file = download_audio(audio_file_url)
                    if audio_file:
                        play_audio_file()

                elif st.session_state['audio_icon'] == "⏸ Pause":
                    # st.session_state['audio_icon'] = "▶ Resume"
                    if st.session_state['channel'].get_busy():
                        st.session_state['channel'].pause()

            except Exception as e:
                pass
                # conn = sqlite3.connect('text_areas.db')
                # cursor = conn.cursor()
                # cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?",
                               # (str(e), youtube_text_area_value))
                # conn.commit()
                # conn.close()


    def download_audio(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    f.write(response.content)
                    return f.name
        except Exception:
            pass
        return None


    def play_audio_file():
        global audio_file

        pygame.mixer.init()
        st.session_state['track'] = pygame.mixer.Sound(audio_file)
        st.session_state['channel'] = pygame.mixer.Channel(0)
        st.session_state['channel'].play(st.session_state['track'])


    def check_audio_state():
        if st.session_state['audio_icon'] != "🔊 Listen":
            try:
                if not st.session_state['channel'].get_busy():
                    st.session_state['audio_icon'] = "🔊 Listen"
            except:
                pass

        if youtube_text_area == "":
            try:
                st.session_state['channel'].stop()
                st.session_state['audio_icon'] = "🔊 Listen"
            except:
                pass


    if youtube_audio_but:
        play_audio()

        if youtube_text_area == "":
            pass

        elif len(youtube_text_area) < 8:
            pass

        else:

            if st.session_state['audio_icon'] == "▶ Resume":
                st.session_state['audio_icon'] = "⏸ Pause"
            elif st.session_state['audio_icon'] == "🔊 Listen":
                st.session_state['audio_icon'] = "⏸ Pause"
            elif st.session_state['audio_icon'] == "⏸ Pause":
                st.session_state['audio_icon'] = "▶ Resume"
            st.rerun()


    def clear_text_area():
        conn = sqlite3.connect('text_areas.db')
        cursor = conn.cursor()

        if youtube_text_area_value != "":
            cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?", ("", youtube_text_area_value))

        elif youtube_text_area_value == "":
            cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?", (" ", youtube_text_area_value))

        conn.commit()
        conn.close()
        st.rerun()


    if erase_youtube:
        clear_text_area()

    if youtube_copy_but:
        Clipboard.copy(youtube_text_area)
        youtube_message_placeholder.success("Copied to clipboard", icon="✔")
        time.sleep(2)
        youtube_message_placeholder.empty()

    if transcribe_but:
        url = youtube_text_area
        pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.findall(pattern, url)
        video_id = None
        transcript = None
        continue_flag = True
        try:
            video_id = match[0]
        except:
            youtube_message_placeholder.error("Please provide a valid youtube URL", icon="⚠")
            time.sleep(3)
            youtube_message_placeholder.empty()
            continue_flag = False

        if continue_flag is True:

            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=language_codes_youtube_api)
            except:
                youtube_message_placeholder.info("There are no captions for this video", icon="⚠")
                time.sleep(3)
                youtube_message_placeholder.empty()
                continue_flag = False

            if continue_flag is True:

                try:
                    full_text = ""
                    for chunk in transcript:
                        full_text += str(chunk['text']) + " "

                    conn = sqlite3.connect('text_areas.db')
                    cursor = conn.cursor()
                    # cursor.execute("UPDATE areas SET youtube_content = ? WHERE youtube_content = ?", (str(full_text), youtube_text_area_value))
                    cursor.execute("UPDATE areas SET youtube_content = ? WHERE customer_id = ?",
                                   (str(full_text), cookie_manager.get("user_id")))
                    conn.commit()
                    conn.close()
                    # st.write(cookie_manager.get("user_id"))
                    st.rerun()
                except Exception as error:
                    st.write("Other error: ", error)

    while st.session_state['audio_icon'] != "🔊 Listen":
        time.sleep(4)
        check_audio_state()
        if st.session_state['audio_icon'] == "🔊 Listen":
            st.rerun()

if st.session_state.current_page == 'Paraphrase':
    top_navigation = option_menu(None, ["Youtube", "Summary", "Paraphrase"],
                                 icons=["📋", "📋", "📝"],
                                 orientation="horizontal",
                                 default_index=2,
                                 on_change=callback, key="paraphrase_menu")

    pre_paraphrase_text_area = st.text_area("P", label_visibility="hidden", placeholder="Enter text to paraphrase...", height=170, value=pre_paraphrase_text_area_value)

    paraphrase_col1, paraphrase_col2, paraphrase_col3, paraphrase_col4 = st.columns(4)

    with paraphrase_col1:
        paraphrase_copy_but = st.button("📋 Copy", use_container_width=True)
    with paraphrase_col2:
        paraphrase_translator = st.button("🌐 Translate", use_container_width=True)
    with paraphrase_col3:
        paraphrase_audio_but = st.button(label=st.session_state['audio_icon'], use_container_width=True)
    with paraphrase_col4:
        erase_pre_paraphrase = st.button("❌ Delete", use_container_width=True, help="Clear the text field")


    def translate():
        lang_name = st.session_state['language_switch']
        if lang_name == "- English":
            lang_name = "English"
        lang_code_to_translate_to = language_code_dict.get(lang_name, None)

        url1 = "https://google-translator9.p.rapidapi.com/v2/detect"
        payload1 = {"q": paraphrase_text_area[:2500]}
        headers1 = {
            "content-type": "application/json",
            "X-RapidAPI-Key": the_rapid_key,
            "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
        }
        response = requests.post(url1, json=payload1, headers=headers1)
        lang_code = response.json()["data"]["detections"][0][0]["language"]

        if len(paraphrase_text_area) > 10:

            if len(paraphrase_text_area) < 99000:

                if lang_code != lang_code_to_translate_to:

                    url = "https://google-translator9.p.rapidapi.com/v2"
                    payload = {
                        "q": paraphrase_text_area,
                        "source": lang_code,
                        "target": lang_code_to_translate_to,
                        "format": "text"
                    }
                    headers = {
                        "content-type": "application/json",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    translated_text = response.json()["data"]["translations"][0]["translatedText"]

                    arabic_languages = "arfaurkuhe"

                    if lang_code_to_translate_to not in arabic_languages:

                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                                       (translated_text, paraphrase_text_area_value))
                        conn.commit()
                        conn.close()

                    else:

                        if lang_code_to_translate_to == "ar" or lang_code_to_translate_to == "fa" or lang_code_to_translate_to == "ur" or lang_code_to_translate_to == "ku" or lang_code_to_translate_to == "he":
                            full_arabic_text = ""
                            arabic_text = arabic_reshaper.reshape(translated_text)
                            lines = []
                            for i in range(0, len(arabic_text), 100):
                                lines.append(arabic_text[i:i + 100])

                            for line in lines:
                                # full_arabic_text += line[::-1] + "\n"
                                full_arabic_text += line[:-1:]

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                                           (full_arabic_text, paraphrase_text_area_value))
                            conn.commit()
                            conn.close()

                else:
                    pass

            else:

                if lang_code != lang_code_to_translate_to:

                    MAX_CHUNK_SIZE = 94000

                    if len(paraphrase_text_area) > MAX_CHUNK_SIZE:
                        translated_chunks = []
                        full_translation = ""
                        start_index = 0
                        while start_index < len(paraphrase_text_area):
                            end_index = start_index + MAX_CHUNK_SIZE
                            chunk = paraphrase_text_area[start_index:end_index]
                            chunk = chunk[:MAX_CHUNK_SIZE]  # Ensure the chunk is within the limit
                            translated_chunks.append(chunk)
                            start_index = end_index

                        for chunk in translated_chunks:
                            url = "https://google-translator9.p.rapidapi.com/v2"

                            payload = {
                                "q": str(chunk),
                                "source": lang_code,
                                "target": lang_code_to_translate_to,
                                "format": "text"
                            }
                            headers = {
                                "content-type": "application/json",
                                "X-RapidAPI-Key": the_rapid_key,
                                "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                            }

                            response = requests.post(url, json=payload, headers=headers)
                            full_translation += response.json()["data"]["translations"][0]["translatedText"]

                        arabic_languages = "arfaurkuhe"

                        if lang_code_to_translate_to not in arabic_languages:

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                                           (full_translation, paraphrase_text_area_value))
                            conn.commit()
                            conn.close()

                        else:

                            if lang_code_to_translate_to == "ar" or lang_code_to_translate_to == "fa" or lang_code_to_translate_to == "ur" or lang_code_to_translate_to == "ku" or lang_code_to_translate_to == "he":
                                full_arabic_text = ""
                                arabic_text = arabic_reshaper.reshape(full_translation)
                                lines = []
                                for i in range(0, len(arabic_text), 100):
                                    lines.append(arabic_text[i:i + 100])

                                for line in lines:
                                    # full_arabic_text += line[::-1] + "\n"
                                    full_arabic_text += line[:-1:]

                                conn = sqlite3.connect('text_areas.db')
                                cursor = conn.cursor()
                                cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                                               (full_arabic_text, paraphrase_text_area_value))
                                conn.commit()
                                conn.close()


    if paraphrase_translator:
        paraphrase_language = st.selectbox("Select a language...", ("- English", "Chinese", "Spanish", "French", "Portuguese", "Hindi", "Arabic", "Japanese", "Bengali", "Russian", "Indonesian", "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani", "Bengali", "Bosnian", "Bulgarian", "Burmese (Myanmar)", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Filipinian", "Finnish", "French", "Georgian", "German", "Greek", "Haitian Creole", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Irish", "Italian", "Japanese", "Kazakh", "Kinyarwanda", "Khmer", "Korean", "Kurdish", "Kyrgyz", "Latvian", "Lithuanian", "Macedonian", "Malay", "Maltese", "Nepali", "Norwegian", "Persian", "Polish", "Portuguese", "Russian", "Romanian", "Samoan", "Serbian", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Swahili", "Swedish", "Telugu", "Thai", "Tigrinya", "Turkish", "Turkmen", "Ukrainian", "Urdu", "Uzbek", "Vietnamese", "Welsh"), key='language_switch', on_change=translate)

    paraphrase_message_placeholder = st.empty()

    paraphrase_text_area = st.text_area("P", label_visibility="hidden", placeholder="Paraphrased content will appear here...", height=170, value=paraphrase_text_area_value)

    paraphrase_sub_col1, paraphrase_sub_col2, paraphrase_sub_col3, paraphrase_sub_col4, paraphrase_sub_col5 = st.columns(5)
    with paraphrase_sub_col1:
        paraphrase_settings_but = st.button("⚙ Settings", use_container_width=True, on_click=go_settings)
    with paraphrase_sub_col3:
        paraphrase_but = st.button("Paraphrase", use_container_width=True, type="primary")
    with paraphrase_sub_col5:
        erase_paraphrase = st.button("❌ Delete", help="Clear the text field")

    st.write("")


    def play_audio():
        global audio_file

        if st.session_state['voice_gender'] == "♀️ Female Voice":
            gender = "Female"
        else:
            gender = "Male"

        if paraphrase_text_area == "":
            paraphrase_message_placeholder.error("Please paraphrase some text to be read", icon="⚠")
            time.sleep(2.5)
            st.rerun()

        elif len(paraphrase_text_area) < 8:
            paraphrase_message_placeholder.error("Please paraphrase a bit longer text", icon="⚠")
            time.sleep(2.5)
            st.rerun()

        else:

            try:
                if st.session_state['audio_icon'] == "▶ Resume":
                    # st.session_state['audio_icon'] = "⏸ Pause"
                    if st.session_state['channel'].get_busy() and st.session_state['channel'].get_sound() == st.session_state['track']:
                        st.session_state['channel'].unpause()

                elif st.session_state['audio_icon'] == "🔊 Listen":

                    # st.session_state['audio_icon'] = "⏸ Pause"

                    text_to_be_read = paraphrase_text_area[:9300]

                    url = "https://ai-auto-text-to-speech.p.rapidapi.com/edgetts"
                    payload = {
                        "gender": gender,
                        "text": text_to_be_read
                    }
                    headers = {
                        "content-type": "application/json",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "ai-auto-text-to-speech.p.rapidapi.com"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    reformatted_response = json.loads(response.text)
                    audio_file_url = reformatted_response["audio_file_url"]

                    audio_file = download_audio(audio_file_url)
                    if audio_file:
                        play_audio_file()

                elif st.session_state['audio_icon'] == "⏸ Pause":
                    # st.session_state['audio_icon'] = "▶ Resume"
                    if st.session_state['channel'].get_busy():
                        st.session_state['channel'].pause()

            except Exception as e:
                pass
                # conn = sqlite3.connect('text_areas.db')
                # cursor = conn.cursor()
                # cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                               # (str(e), paraphrase_text_area_value))
                # conn.commit()
                # conn.close()


    def download_audio(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    f.write(response.content)
                    return f.name
        except Exception:
            pass
        return None


    def play_audio_file():
        global audio_file

        pygame.mixer.init()
        st.session_state['track'] = pygame.mixer.Sound(audio_file)
        st.session_state['channel'] = pygame.mixer.Channel(0)
        st.session_state['channel'].play(st.session_state['track'])


    def check_audio_state():
        if st.session_state['audio_icon'] != "🔊 Listen":
            try:
                if not st.session_state['channel'].get_busy():
                    st.session_state['audio_icon'] = "🔊 Listen"
            except:
                pass

        if paraphrase_text_area == "":
            try:
                st.session_state['channel'].stop()
                st.session_state['audio_icon'] = "🔊 Listen"
            except:
                pass


    if paraphrase_audio_but:
        play_audio()

        if paraphrase_text_area == "":
            pass

        elif len(paraphrase_text_area) < 8:
            pass

        else:

            if st.session_state['audio_icon'] == "▶ Resume":
                st.session_state['audio_icon'] = "⏸ Pause"
            elif st.session_state['audio_icon'] == "🔊 Listen":
                st.session_state['audio_icon'] = "⏸ Pause"
            elif st.session_state['audio_icon'] == "⏸ Pause":
                st.session_state['audio_icon'] = "▶ Resume"
            st.rerun()


    def clear_text_area(widget):
        conn = sqlite3.connect('text_areas.db')
        cursor = conn.cursor()

        if widget == "pre_paraphrase":

            if pre_paraphrase_text_area_value != "":
                cursor.execute("UPDATE areas SET pre_paraphrase_content = ? WHERE pre_paraphrase_content = ?", ("", pre_paraphrase_text_area_value))

            elif pre_paraphrase_text_area_value == "":
                cursor.execute("UPDATE areas SET pre_paraphrase_content = ? WHERE pre_paraphrase_content = ?", (" ", pre_paraphrase_text_area_value))

        elif widget == "paraphrase":

            if paraphrase_text_area_value != "":
                cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?", ("", paraphrase_text_area_value))

            elif paraphrase_text_area_value == "":
                cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?", (" ", paraphrase_text_area_value))

        conn.commit()
        conn.close()
        st.rerun()


    if erase_pre_paraphrase:
        clear_text_area("pre_paraphrase")

    if erase_paraphrase:
        clear_text_area("paraphrase")

    if paraphrase_copy_but:
        Clipboard.copy(paraphrase_text_area)
        paraphrase_message_placeholder.success("Copied to clipboard", icon="✔")
        time.sleep(2)
        paraphrase_message_placeholder.empty()

    if paraphrase_but:
        url1 = "https://google-translator9.p.rapidapi.com/v2/detect"
        payload1 = {"q": pre_paraphrase_text_area[:2500]}
        headers1 = {
            "content-type": "application/json",
            "X-RapidAPI-Key": the_rapid_key,
            "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
        }
        response = requests.post(url1, json=payload1, headers=headers1)
        lang_code = response.json()["data"]["detections"][0][0]["language"]

        if len(pre_paraphrase_text_area) > 8 and len(pre_paraphrase_text_area) < 8500:

            url = "https://paraphrasing-and-rewriter-api.p.rapidapi.com/rewrite-light"

            payload = {
                "from": lang_code,
                "text": str(pre_paraphrase_text_area),
            }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": the_rapid_key,
                "X-RapidAPI-Host": "paraphrasing-and-rewriter-api.p.rapidapi.com"
            }

            response = requests.post(url, json=payload, headers=headers)

            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                           (response.text, paraphrase_text_area_value))
            conn.commit()
            conn.close()
            st.rerun()

        elif len(pre_paraphrase_text_area) > 8500:
            full_paraphrased_text = ""
            truncated_text = pre_paraphrase_text_area[:17000]
            first_chunk = truncated_text[:8500]
            second_chunk = truncated_text[8500:17000]
            chunks = [first_chunk, second_chunk]

            for chunk in chunks:
                url = "https://paraphrasing-and-rewriter-api.p.rapidapi.com/rewrite-light"
                payload = {
                    "from": lang_code,
                    "text": chunk
                }
                headers = {
                    "content-type": "application/json",
                    "X-RapidAPI-Key": the_rapid_key,
                    "X-RapidAPI-Host": "paraphrasing-and-rewriter-api.p.rapidapi.com"
                }
                response = requests.post(url, json=payload, headers=headers)
                full_paraphrased_text += response.text

            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE areas SET paraphrase_content = ? WHERE paraphrase_content = ?",
                           (full_paraphrased_text, paraphrase_text_area_value))
            conn.commit()
            conn.close()
            st.rerun()

        else:
            paraphrase_message_placeholder.error("Please give us a text to paraphrase", icon="⚠")
            time.sleep(3)
            paraphrase_message_placeholder.empty()

    while st.session_state['audio_icon'] != "🔊 Listen":
        time.sleep(4)
        check_audio_state()
        if st.session_state['audio_icon'] == "🔊 Listen":
            st.rerun()


if st.session_state.current_page == "Summary":
    top_navigation = option_menu(None, ["Youtube", "Summary", "Paraphrase"],
                                 icons=["📋", "📋", "📝"],
                                 orientation="horizontal",
                                 default_index=1,
                                 on_change=callback, key="summary_menu")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        summary_copy_but = st.button("📋 Copy", use_container_width=True)
    with summary_col2:
        summary_translator = st.button("🌐 Translate", use_container_width=True)
    with summary_col3:
        summary_audio_but = st.button(label=st.session_state['audio_icon'], use_container_width=True)
    with summary_col4:
        erase_summary = st.button("❌ Delete", use_container_width=True, help="Clear the text field")


    def translate():
        lang_name = st.session_state['language_switch']
        if lang_name == "- English":
            lang_name = "English"
        lang_code_to_translate_to = language_code_dict.get(lang_name, None)

        url1 = "https://google-translator9.p.rapidapi.com/v2/detect"
        payload1 = {"q": summary_text_area[:2500]}
        headers1 = {
            "content-type": "application/json",
            "X-RapidAPI-Key": the_rapid_key,
            "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
        }
        response = requests.post(url1, json=payload1, headers=headers1)
        lang_code = response.json()["data"]["detections"][0][0]["language"]

        if len(summary_text_area) > 10:

            if len(summary_text_area) < 99000:

                if lang_code != lang_code_to_translate_to:

                    url = "https://google-translator9.p.rapidapi.com/v2"
                    payload = {
                        "q": summary_text_area,
                        "source": lang_code,
                        "target": lang_code_to_translate_to,
                        "format": "text"
                    }
                    headers = {
                        "content-type": "application/json",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    translated_text = response.json()["data"]["translations"][0]["translatedText"]

                    arabic_languages = "arfaurkuhe"

                    if lang_code_to_translate_to not in arabic_languages:

                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                       (translated_text, summary_text_area_value))
                        conn.commit()
                        conn.close()

                    else:

                        if lang_code_to_translate_to == "ar" or lang_code_to_translate_to == "fa" or lang_code_to_translate_to == "ur" or lang_code_to_translate_to == "ku" or lang_code_to_translate_to == "he":
                            full_arabic_text = ""
                            arabic_text = arabic_reshaper.reshape(translated_text)
                            lines = []
                            for i in range(0, len(arabic_text), 100):
                                lines.append(arabic_text[i:i + 100])

                            for line in lines:
                                # full_arabic_text += line[::-1] + "\n"
                                full_arabic_text += line[:-1:]

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (full_arabic_text, summary_text_area_value))
                            conn.commit()
                            conn.close()

                else:
                    pass

            else:

                if lang_code != lang_code_to_translate_to:

                    MAX_CHUNK_SIZE = 94000

                    if len(summary_text_area) > MAX_CHUNK_SIZE:
                        translated_chunks = []
                        full_translation = ""
                        start_index = 0
                        while start_index < len(summary_text_area):
                            end_index = start_index + MAX_CHUNK_SIZE
                            chunk = summary_text_area[start_index:end_index]
                            chunk = chunk[:MAX_CHUNK_SIZE]  # Ensure the chunk is within the limit
                            translated_chunks.append(chunk)
                            start_index = end_index

                        for chunk in translated_chunks:
                            url = "https://google-translator9.p.rapidapi.com/v2"

                            payload = {
                                "q": str(chunk),
                                "source": lang_code,
                                "target": lang_code_to_translate_to,
                                "format": "text"
                            }
                            headers = {
                                "content-type": "application/json",
                                "X-RapidAPI-Key": the_rapid_key,
                                "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                            }

                            response = requests.post(url, json=payload, headers=headers)
                            full_translation += response.json()["data"]["translations"][0]["translatedText"]

                        arabic_languages = "arfaurkuhe"

                        if lang_code_to_translate_to not in arabic_languages:

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (full_translation, summary_text_area_value))
                            conn.commit()
                            conn.close()

                        else:

                            if lang_code_to_translate_to == "ar" or lang_code_to_translate_to == "fa" or lang_code_to_translate_to == "ur" or lang_code_to_translate_to == "ku" or lang_code_to_translate_to == "he":
                                full_arabic_text = ""
                                arabic_text = arabic_reshaper.reshape(full_translation)
                                lines = []
                                for i in range(0, len(arabic_text), 100):
                                    lines.append(arabic_text[i:i + 100])

                                for line in lines:
                                    # full_arabic_text += line[::-1] + "\n"
                                    full_arabic_text += line[:-1:]

                                conn = sqlite3.connect('text_areas.db')
                                cursor = conn.cursor()
                                cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                               (full_arabic_text, summary_text_area_value))
                                conn.commit()
                                conn.close()


    if summary_translator:
        summary_language = st.selectbox("Select a language...", ("- English", "Chinese", "Spanish", "French", "Portuguese", "Hindi", "Arabic", "Japanese", "Bengali", "Russian", "Indonesian", "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani", "Bengali", "Bosnian", "Bulgarian", "Burmese (Myanmar)", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Filipinian", "Finnish", "French", "Georgian", "German", "Greek", "Haitian Creole", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Irish", "Italian", "Japanese", "Kazakh", "Kinyarwanda", "Khmer", "Korean", "Kurdish", "Kyrgyz", "Latvian", "Lithuanian", "Macedonian", "Malay", "Maltese", "Nepali", "Norwegian", "Persian", "Polish", "Portuguese", "Russian", "Romanian", "Samoan", "Serbian", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Swahili", "Swedish", "Telugu", "Thai", "Tigrinya", "Turkish", "Turkmen", "Ukrainian", "Urdu", "Uzbek", "Vietnamese", "Welsh"), key='language_switch', on_change=translate)

    summary_message_placeholder = st.empty()

    summary_length_area = st.text_input("S", label_visibility="hidden", placeholder="                                                                              Summary length in sentences")

    summary_text_area = st.text_area("S", label_visibility="hidden", placeholder="Paste link or text to summarize...", height=300, value=summary_text_area_value)

    st.write()

    conn = sqlite3.connect('settings_save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT summary_type FROM settings")
    index_summary_type = cursor.fetchone()[0]
    cursor.execute("SELECT summary_mode FROM settings")
    index_summary_mode = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    summary_sub_col1, summary_sub_col2, summary_sub_col3 = st.columns(3)
    with summary_sub_col1:
        summary_type = st_btn_select(("Abstractive", "Extractive"), index=index_summary_type)
    with summary_sub_col2:
        summary_but = st.button("Summarize", use_container_width=True, type="primary")
    with summary_sub_col3:
        summary_mode = st_btn_select(("Bullet points", "Plain text"), index=index_summary_mode)

    summary_settings_but = st.button("⚙ Settings", use_container_width=True)
    if summary_settings_but:
        st.session_state.current_page = "Settings"
        st.rerun()

    if summary_type == "Abstractive":
        conn = sqlite3.connect('settings_save.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET summary_type = ?", (0, ))
        conn.commit()
        conn.close()

    elif summary_type == "Extractive":
        conn = sqlite3.connect('settings_save.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET summary_type = ?", (1, ))
        conn.commit()
        conn.close()

    if summary_mode == "Bullet points":
        conn = sqlite3.connect('settings_save.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET summary_mode = ?", (0, ))
        conn.commit()
        conn.close()

    elif summary_mode == "Plain text":
        conn = sqlite3.connect('settings_save.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET summary_mode = ?", (1, ))
        conn.commit()
        conn.close()


    def play_audio():
        global audio_file

        if st.session_state['voice_gender'] == "♀️ Female Voice":
            gender = "Female"
        else:
            gender = "Male"

        if summary_text_area == "":
            summary_message_placeholder.error("Please provide some text to be read", icon="⚠")
            time.sleep(2.5)
            st.rerun()

        elif len(summary_text_area) < 8:
            summary_message_placeholder.error("Please provide a bit longer text", icon="⚠")
            time.sleep(2.5)
            st.rerun()

        else:

            try:
                if st.session_state['audio_icon'] == "▶ Resume":
                    # st.session_state['audio_icon'] = "⏸ Pause"
                    if st.session_state['channel'].get_busy() and st.session_state['channel'].get_sound() == st.session_state['track']:
                        st.session_state['channel'].unpause()

                elif st.session_state['audio_icon'] == "🔊 Listen":

                    # st.session_state['audio_icon'] = "⏸ Pause"

                    text_to_be_read = summary_text_area[:9300]

                    url = "https://ai-auto-text-to-speech.p.rapidapi.com/edgetts"
                    payload = {
                        "gender": gender,
                        "text": text_to_be_read
                    }
                    headers = {
                        "content-type": "application/json",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "ai-auto-text-to-speech.p.rapidapi.com"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    reformatted_response = json.loads(response.text)
                    audio_file_url = reformatted_response["audio_file_url"]

                    audio_file = download_audio(audio_file_url)
                    if audio_file:
                        play_audio_file()

                elif st.session_state['audio_icon'] == "⏸ Pause":
                    # st.session_state['audio_icon'] = "▶ Resume"
                    if st.session_state['channel'].get_busy():
                        st.session_state['channel'].pause()

            except Exception as e:
                pass
                # conn = sqlite3.connect('text_areas.db')
                # cursor = conn.cursor()
                # cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                               # (str(e), summary_text_area_value))
                # conn.commit()
                # conn.close()


    def download_audio(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    f.write(response.content)
                    return f.name
        except Exception:
            pass
        return None


    def play_audio_file():
        global audio_file

        pygame.mixer.init()
        st.session_state['track'] = pygame.mixer.Sound(audio_file)
        st.session_state['channel'] = pygame.mixer.Channel(0)
        st.session_state['channel'].play(st.session_state['track'])


    def check_audio_state():
        if st.session_state['audio_icon'] != "🔊 Listen":
            try:
                if not st.session_state['channel'].get_busy():
                    st.session_state['audio_icon'] = "🔊 Listen"
            except:
                pass

        if summary_text_area == "":
            try:
                st.session_state['channel'].stop()
                st.session_state['audio_icon'] = "🔊 Listen"
            except:
                pass


    if summary_audio_but:
        play_audio()

        if summary_text_area == "":
            pass

        elif len(summary_text_area) < 8:
            pass

        else:

            if st.session_state['audio_icon'] == "▶ Resume":
                st.session_state['audio_icon'] = "⏸ Pause"
            elif st.session_state['audio_icon'] == "🔊 Listen":
                st.session_state['audio_icon'] = "⏸ Pause"
            elif st.session_state['audio_icon'] == "⏸ Pause":
                st.session_state['audio_icon'] = "▶ Resume"
            st.rerun()


    def clear_text_area():
        conn = sqlite3.connect('text_areas.db')
        cursor = conn.cursor()

        if summary_text_area_value != "":
            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?", ("", summary_text_area_value))

        elif summary_text_area_value == "":
            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?", (" ", summary_text_area_value))

        conn.commit()
        conn.close()
        st.rerun()

    if erase_summary:
        clear_text_area()

    if summary_copy_but:
        Clipboard.copy(summary_text_area)
        summary_message_placeholder.success("Copied to clipboard", icon="✔")
        time.sleep(2)
        summary_message_placeholder.empty()


    def summary_from_youtube():
        sentences = summary_length_area
        if sentences == "":
            sentences = "6"

        if len(str(summary_text_area)) > 52000:

            summary_sentences = []
            chunks = [summary_text_area[i:i + 52000] for i in range(0, len(summary_text_area), 52000)]

            for chunk in chunks:
                url = "https://extractoapi.p.rapidapi.com/summarize"
                payload = {
                    "styleArgs": {
                        "tone": "concise, professional and confident.",
                        "format": "bulleted list"
                    },
                    "text": chunk
                }
                headers = {
                    "content-type": "application/json",
                    "X-RapidAPI-Key": the_rapid_key,
                    "X-RapidAPI-Host": "extractoapi.p.rapidapi.com"
                }
                response = requests.post(url, json=payload, headers=headers)

                for summary_piece_sentence in response.json()["data"]:
                    summary_sentences.append(summary_piece_sentence)

            if summary_mode == "Bullet points":
                total_sentences = 0
                complete_sentence_list = []
                for sentence in summary_sentences:
                    complete_sentence_list.append(sentence)

                if len(complete_sentence_list) > int(sentences):
                    excess_sentences = len(complete_sentence_list) - int(sentences)
                    complete_sentence_list = complete_sentence_list[:-excess_sentences]

                complete_summary = "\n\n".join(complete_sentence_list)

                conn = sqlite3.connect('text_areas.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                               (complete_summary, summary_text_area_value))
                conn.commit()
                conn.close()
                st.rerun()

            elif summary_mode == "Plain text":
                full_summary = ""
                if len(summary_sentences) > int(sentences):
                    excess_sentences = len(summary_sentences) - int(sentences)
                    summary_sentences = summary_sentences[:-excess_sentences]

                for sentence in summary_sentences:
                    full_summary += f"{sentence} "

                conn = sqlite3.connect('text_areas.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                               (full_summary, summary_text_area_value))
                conn.commit()
                conn.close()
                st.rerun()

            # self.ids.field.foreground_color = (0, 0, 0, 1)

        else:
            url = "https://extractoapi.p.rapidapi.com/summarize"
            payload = {
                "styleArgs": {
                    "tone": "concise, professional and confident.",
                    "format": "bulleted list"
                },
                "text": str(summary_text_area)
            }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": the_rapid_key,
                "X-RapidAPI-Host": "extractoapi.p.rapidapi.com"
            }
            response = requests.post(url, json=payload, headers=headers)

            if summary_mode == "Bullet points":
                sentence_list = ""
                for sentence in response.json()["data"]:
                    sentence_list += f"{sentence}\n\n"

                sentence_split_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)'
                splitted_sentences = re.split(sentence_split_pattern, sentence_list)

                if int(sentences) < len(splitted_sentences):
                    sentence_list = ''.join(splitted_sentences[:int(sentences)])

                conn = sqlite3.connect('text_areas.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                               (sentence_list, summary_text_area_value))
                conn.commit()
                conn.close()
                st.rerun()

            elif summary_mode == "Plain text":
                all_sentences = ""
                for sentence in response.json()["data"]:
                    all_sentences += f"{sentence} "

                sentence_split_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)'
                splitted_sentences = re.split(sentence_split_pattern, all_sentences)

                if int(sentences) < len(splitted_sentences):
                    all_sentences = ' '.join(splitted_sentences[:int(sentences)])

                conn = sqlite3.connect('text_areas.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                               (all_sentences, summary_text_area_value))
                conn.commit()
                conn.close()
                st.rerun()

        if lang_code != "en":
            url = "https://google-translator9.p.rapidapi.com/v2"
            payload = {
                "q": str(summary_text_area),
                "source": "en",
                "target": lang_code,
                "format": "text"
            }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": the_rapid_key,
                "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
            }
            response = requests.post(url, json=payload, headers=headers)

            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                           (response.json()["data"]["translations"][0]["translatedText"], summary_text_area_value))
            conn.commit()
            conn.close()
            st.rerun()


    def backup_extractive_url_summary(url_to_be_summarized, num_of_sentences):
        url = "https://lexper.p.rapidapi.com/v1.1/extract"
        querystring = {
            "url": str(url_to_be_summarized),
            "js_timeout": "30", "media": "true"}
        headers = {
            "X-RapidAPI-Key": the_rapid_key,
            "X-RapidAPI-Host": "lexper.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)

        url_content = response.json()["article"]["text"]

        url1 = "https://textanalysis-text-summarization.p.rapidapi.com/text-summarizer-text"
        payload1 = {
            "text": url_content,
            "sentnum": str(num_of_sentences)
        }
        headers1 = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": the_rapid_key,
            "X-RapidAPI-Host": "textanalysis-text-summarization.p.rapidapi.com"
        }
        response1 = requests.post(url1, data=payload1, headers=headers1)

        if summary_mode == "Bullet points":
            sentence_list = ""
            for sentence in response1.json()["sentences"]:
                sentence_list += f"- {sentence}\n\n"

            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                           (sentence_list, summary_text_area_value))
            conn.commit()
            conn.close()
            st.rerun()

        elif summary_mode == "Plain text":
            all_sentences = ""
            for sentence in response1.json()["sentences"]:
                all_sentences += f"{sentence} "

            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                           (all_sentences, summary_text_area_value))
            conn.commit()
            conn.close()
            st.rerun()


    def summarize(summary_source, url_to_summarize=""):
        sentences = summary_length_area
        pattern = r'^-?\d*\.?\d+$'
        is_a_number = bool(re.match(pattern, sentences))

        if sentences == "" or sentences == "0":
            sentences = "6"

        elif not is_a_number:
            summary_message_placeholder.error("Please choose the number of sentences by providing a number or leave it empty for a default size summary", icon="⚠")
            time.sleep(5)
            summary_message_placeholder.empty()
            return

        if len(summary_text_area) > 10:

            if summary_source == "URL":

                if summary_type == "Abstractive":

                    url = "https://chatgpt4-api.p.rapidapi.com/gpt"
                    querystring = {
                        "content": f"Summarize this URL: {url_to_summarize} in {sentences} sentences. If there isn't that much sentences if the provided URL, just make a default size summary. But if the amount of sentences is reasonable, then please respect that amount. Please make the summary in the same language as the text from the URL, this is very important !"}
                    headers = {
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "chatgpt4-api.p.rapidapi.com"
                    }
                    response = requests.get(url, headers=headers, params=querystring)

                    if summary_mode == "Plain text":
                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                       (response.json()["content"] + " ", summary_text_area_value))
                        conn.commit()
                        conn.close()
                        st.rerun()

                    elif summary_mode == "Bullet points":
                        sentences = re.split(r'(?<=[.!?]) +', response.json()["content"])
                        sentences_with_dash = ['- ' + sentence for sentence in sentences]
                        bulleted_text = '\n\n'.join(sentences_with_dash)

                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                       (bulleted_text, summary_text_area_value))
                        conn.commit()
                        conn.close()
                        st.rerun()

                elif summary_type == "Extractive":

                    url = "https://textanalysis-text-summarization.p.rapidapi.com/text-summarizer-url"

                    payload = {
                        "url": url_to_summarize,
                        "sentnum": sentences,
                    }
                    headers = {
                        "content-type": "application/x-www-form-urlencoded",
                        "X-RapidAPI-Key": the_rapid_key,
                        "X-RapidAPI-Host": "textanalysis-text-summarization.p.rapidapi.com"
                    }
                    response = requests.post(url, data=payload, headers=headers)

                    if summary_mode == "Bullet points":
                        sentence_list = ""
                        try:
                            for sentence in response.json()["sentences"]:
                                sentence_list += f"- {sentence}\n\n"
                        except:
                            backup_extractive_url_summary(url_to_summarize, sentences)

                        if "N\n\no\n\nn\n\ne" in sentence_list and len(sentence_list) < 100:
                            backup_extractive_url_summary(url_to_summarize, sentences)
                        else:
                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (sentence_list, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

                    elif summary_mode == "Plain text":
                        all_sentences = ""
                        try:
                            for sentence in response.json()["sentences"]:
                                all_sentences += f"{sentence} "
                        except:
                            backup_extractive_url_summary(url_to_summarize, sentences)

                        if "N o n e" in all_sentences and len(all_sentences) < 100:
                            backup_extractive_url_summary(url_to_summarize, sentences)
                        else:
                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (all_sentences, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

            if summary_source == "Text":

                url = "https://google-translator9.p.rapidapi.com/v2/detect"
                payload = {"q": str(summary_text_area)[:2500]}
                headers = {
                    "content-type": "application/json",
                    "X-RapidAPI-Key": the_rapid_key,
                    "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                }
                response = requests.post(url, json=payload, headers=headers)

                lang_code = response.json()["data"]["detections"][0][0]["language"]

                if summary_type == "Abstractive":

                    if len(str(summary_text_area)) > 52000:

                        summary_sentences = []
                        chunks = [summary_text_area[i:i + 52000] for i in range(0, len(summary_text_area), 52000)]

                        for chunk in chunks:
                            url = "https://extractoapi.p.rapidapi.com/summarize"
                            payload = {
                                "styleArgs": {
                                    "tone": "concise, professional and confident.",
                                    "format": "bulleted list"
                                },
                                "text": chunk
                            }
                            headers = {
                                "content-type": "application/json",
                                "X-RapidAPI-Key": the_rapid_key,
                                "X-RapidAPI-Host": "extractoapi.p.rapidapi.com"
                            }
                            response = requests.post(url, json=payload, headers=headers)

                            for summary_piece_sentence in response.json()["data"]:
                                summary_sentences.append(summary_piece_sentence)

                        if summary_mode == "Bullet points":
                            total_sentences = 0
                            complete_sentence_list = []
                            for sentence in summary_sentences:
                                complete_sentence_list.append(sentence)

                            if len(complete_sentence_list) > int(sentences):
                                excess_sentences = len(complete_sentence_list) - int(sentences)
                                complete_sentence_list = complete_sentence_list[:-excess_sentences]

                            complete_summary = "\n\n".join(complete_sentence_list)

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (complete_summary, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

                        elif summary_mode == "Plain text":
                            full_summary = ""
                            if len(summary_sentences) > int(sentences):
                                excess_sentences = len(summary_sentences) - int(sentences)
                                summary_sentences = summary_sentences[:-excess_sentences]

                            for sentence in summary_sentences:
                                full_summary += f"{sentence} "

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (full_summary, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

                    else:
                        url = "https://extractoapi.p.rapidapi.com/summarize"
                        payload = {
                            "styleArgs": {
                                "tone": "concise, professional and confident.",
                                "format": "bulleted list"
                            },
                            "text": str(summary_text_area)
                        }
                        headers = {
                            "content-type": "application/json",
                            "X-RapidAPI-Key": the_rapid_key,
                            "X-RapidAPI-Host": "extractoapi.p.rapidapi.com"
                        }
                        response = requests.post(url, json=payload, headers=headers)

                        if summary_mode == "Bullet points":
                            sentence_list = ""
                            for sentence in response.json()["data"]:
                                sentence_list += f"- {sentence}\n\n"

                            sentence_split_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)'
                            splitted_sentences = re.split(sentence_split_pattern, sentence_list)

                            if int(sentences) < len(splitted_sentences):
                                sentence_list = ''.join(splitted_sentences[:int(sentences)])

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (sentence_list, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

                        elif summary_mode == "Plain text":
                            all_sentences = ""
                            for sentence in response.json()["data"]:
                                all_sentences += f"{sentence} "

                            sentence_split_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)'
                            splitted_sentences = re.split(sentence_split_pattern, all_sentences)

                            if int(sentences) < len(splitted_sentences):
                                all_sentences = ' '.join(splitted_sentences[:int(sentences)])

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (all_sentences, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

                    if lang_code != "en":
                        url = "https://google-translator9.p.rapidapi.com/v2"
                        payload = {
                            "q": str(summary_text_area),
                            "source": "en",
                            "target": lang_code,
                            "format": "text"
                        }
                        headers = {
                            "content-type": "application/json",
                            "X-RapidAPI-Key": the_rapid_key,
                            "X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
                        }
                        response = requests.post(url, json=payload, headers=headers)

                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                       (response.json()["data"]["translations"][0]["translatedText"], summary_text_area_value))
                        conn.commit()
                        conn.close()
                        st.rerun()

                elif summary_type == "Extractive":
                    from_youtube = any(char in summary_text_area for char in '.!?')
                    if from_youtube is False:
                        summary_from_youtube()
                    else:
                        url = "https://textanalysis-text-summarization.p.rapidapi.com/text-summarizer-text"
                        payload = {
                            "text": str(summary_text_area),
                            "sentnum": sentences
                        }
                        headers = {
                            "content-type": "application/x-www-form-urlencoded",
                            "X-RapidAPI-Key": the_rapid_key,
                            "X-RapidAPI-Host": "textanalysis-text-summarization.p.rapidapi.com"
                        }
                        response = requests.post(url, data=payload, headers=headers)

                        if summary_mode == "Bullet points":
                            sentence_list = ""
                            for sentence in response.json()["sentences"]:
                                sentence_list += f"- {sentence}\n\n"

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (sentence_list, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

                        elif summary_mode == "Plain text":
                            all_sentences = ""
                            for sentence in response.json()["sentences"]:
                                all_sentences += f"{sentence} "

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE areas SET summary_content = ? WHERE summary_content = ?",
                                           (all_sentences, summary_text_area_value))
                            conn.commit()
                            conn.close()
                            st.rerun()

        else:
            summary_message_placeholder.error("Please paste a URL or a long text", icon="⚠")
            time.sleep(3)
            summary_message_placeholder.empty()


    if summary_but:
        text = summary_text_area

        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)'

        try:
            urls = re.findall(url_pattern, text)

            if len(urls) != 1:
                summarize("Text")

            url_length = len(urls[0])
            text_length = len(text)
            if abs(url_length - text_length) < 100:
                summarize("URL", urls[0])
            else:
                summarize("Text")
        except IndexError:
            pass

    go_signup_but = st.button("Go Sign up")
    if go_signup_but:
        st.session_state.current_page = 'Sign up'
        st.rerun()

    while st.session_state['audio_icon'] != "🔊 Listen":
        time.sleep(4)
        check_audio_state()
        if st.session_state['audio_icon'] == "🔊 Listen":
            st.rerun()


if st.session_state.current_page == 'Settings':
    settings_col1, settings_col2, settings_col3 = st.columns(3)
    with settings_col2:
        st.title("⚙ Settings")

    subscription_container = st.container(border=True)
    with subscription_container:
        manage_sub_but = st.button("💳 Manage subscription", use_container_width=True, type="primary")

    if manage_sub_but:
        webbrowser.open("https://billing.stripe.com/p/login/test_fZecMXciia1B6Mo8ww")

    st.subheader("")

    tts_container = st.container(border=True)
    with tts_container:
        voice_gender_but = st.button(label=st.session_state['voice_gender'], use_container_width=True, type="primary")

    if voice_gender_but:
        if st.session_state['voice_gender'] == "♀️ Female Voice":

            st.session_state['voice_gender'] = "♂️ Male Voice"
            conn = sqlite3.connect('settings_save.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE settings SET voice_gender = ?", ("Male", ))
            conn.commit()
            conn.close()

        elif st.session_state['voice_gender'] == "♂️ Male Voice":

            st.session_state['voice_gender'] = "♀️ Female Voice"
            conn = sqlite3.connect('settings_save.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE settings SET voice_gender = ?", ("Female", ))
            conn.commit()
            conn.close()

        st.rerun()

    st.subheader("")

    faq_container = st.container(border=True)
    with faq_container:
        faq_but = st.button("💬 FAQ", use_container_width=True, type="primary")

    if faq_but:
        webbrowser.open("https://drive.google.com/file/d/1TkF4-JCcaAYbUVy5ayVvSSx-kaILP04K/view?usp=sharing")

    st.subheader("")

    contact_container = st.container(border=True)
    with contact_container:
        st.button("📞 Contact", use_container_width=True, type="primary", on_click=go_contact_page)

    st.subheader("")

    privacy_container = st.container(border=True)
    with privacy_container:
        privacy_but = st.button("🔒 Privacy Policy", use_container_width=True, type="primary")

    if privacy_but:
        webbrowser.open("https://drive.google.com/file/d/1xrmeVvYhzHer834o_TDiNwGp0rvrTrV_/view?usp=sharing")

    st.subheader("")

    terms_container = st.container(border=True)
    with terms_container:
        terms_but = st.button("📜 Terms and Conditions", use_container_width=True, type="primary")

    if terms_but:
        webbrowser.open("https://drive.google.com/file/d/1124X4IN1yQAvAYQVIebepBxeuNWJxTV5/view?usp=sharing")

    st.subheader("")

    settings_back_but = st.button("↩ Back")
    if settings_back_but:
        st.session_state.current_page = "Summary"
        st.rerun()

    st.header("")
    st.write("")

    settings_subcol1, settings_subcol2, settings_subcol3 = st.columns(3)
    with settings_subcol2:
        st.button("🏠 Home", use_container_width=True, on_click=go_home)


if st.session_state.current_page == 'Contact':
    contact_col1, contact_col2, contact_col3 = st.columns(3)
    with contact_col2:
        st.title("📞 Contact")


    st.divider()

    st.subheader("For questions and assistance:")

    mail_container = st.container(border=True)
    with mail_container:
        mail_but = st.button("📧 support@pickiepoint.com", use_container_width=True, type="primary")

    contact_message_placeholder = st.empty()

    if mail_but:
        Clipboard.copy("support@pickiepoint.com")
        contact_message_placeholder.success("Email copied", icon="✔")
        time.sleep(2)
        contact_message_placeholder.empty()

    st.write("")

    st.divider()

    st.subheader("Follow us on social media:")

    tiktok_container = st.container(border=True)
    with tiktok_container:
        tiktok_but = st.button("🎵 TikTok", use_container_width=True, type="primary")

    if tiktok_but:
        webbrowser.open("https://www.tiktok.com/@pickiepoint?is_from_webapp=1&sender_device=pc")

    st.subheader("")

    instagram_container = st.container(border=True)
    with instagram_container:
        instagram_but = st.button("📸 Instagram", use_container_width=True, type="primary")

    if instagram_but:
        webbrowser.open("https://www.instagram.com/pickiepoint?igsh=NHl2c3I2YnRqNmVt")

    st.subheader("")

    facebook_container = st.container(border=True)
    with facebook_container:
        facebook_but = st.button("📘 Facebook", use_container_width=True, type="primary")

    if facebook_but:
        webbrowser.open("https://www.facebook.com/profile.php?id=61559802255231")

    st.subheader("")

    snapchat_container = st.container(border=True)
    with snapchat_container:
        snapchat_but = st.button("👻 Snapchat", use_container_width=True, type="primary")

    if snapchat_but:
        webbrowser.open(
            "https://profile.snapchat.com/4b536818-4e44-409d-969f-e71ace4000a4/profiles/93b58548-a490-4204-af7a-ce93343552f9/details/public-stories?ref_aid=af78ba9a-96e9-48bd-85e1-2434facb2a6a")

    st.subheader("")

    twitter_container = st.container(border=True)
    with twitter_container:
        twitter_but = st.button("🐦 X (Twitter)", use_container_width=True, type="primary")

    if twitter_but:
        webbrowser.open("https://x.com/pickiepoint")

    st.subheader("")

    pinterest_container = st.container(border=True)
    with pinterest_container:
        pinterest_but = st.button("📌 Pinterest", use_container_width=True, type="primary")

    if pinterest_but:
        webbrowser.open("https://pin.it/3g7YfkVcU")

    st.subheader("")

    contact_back_but = st.button("↩ Back")
    if contact_back_but:
        st.session_state.current_page = "Settings"
        st.rerun()

    st.header("")
    st.write("")

    contact_sub_col1, contact_sub_col2 = st.columns(2)
    with contact_sub_col1:
        st.button("⚙ Settings", use_container_width=True, on_click=go_settings)
    with contact_sub_col2:
        st.button("🏠 Home", use_container_width=True, on_click=go_home)


if st.session_state.current_page == "Sign up":

    def create_account():
        user_email = email_placeholder
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, user_email):
            signup_message_placeholder.error("Please provide a valid email", icon="⚠")
            time.sleep(2.5)
            signup_message_placeholder.empty()

        else:
            domain = user_email.split('@')[1]
            try:
                dns.resolver.resolve(domain, 'MX')

                if len(password_placeholder) >= 8:

                    if privacy_policy_checkbox:

                        if terms_and_conditions_checkbox:

                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()
                            cursor.execute("SELECT email FROM areas WHERE email = ?", (user_email, ))

                            if cursor.fetchone():

                                conn.commit()
                                conn.close()

                                signup_message_placeholder.warning(
                                    "There is already an account associated with that email", icon="⚠")
                                time.sleep(2.5)
                                signup_message_placeholder.empty()

                            else:

                                signup_message_placeholder.success("Your account was created successfully", icon="✔")
                                time.sleep(2.5)
                                signup_message_placeholder.empty()

                                customer = stripe.Customer.create(email=user_email)
                                customer_id = customer["id"]

                                conn = sqlite3.connect('settings_save.db')
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?)", ("Female", 0, 0, 666666, customer_id))
                                conn.commit()
                                conn.close()

                                conn = sqlite3.connect('text_areas.db')
                                cursor = conn.cursor()
                                cursor.execute("""
                                INSERT INTO areas VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            ("", "", "", "", user_email, password_placeholder, customer_id, time.time()))
                                conn.commit()
                                conn.close()

                                cookie_expiration_date = datetime.now() + timedelta(days=60)
                                cookie_manager.set(cookie="user_id", val=customer_id, expires_at=cookie_expiration_date)

                                st.session_state.current_page = "Trial"
                                st.rerun()

                        else:
                            signup_message_placeholder.error("You must agree to our Terms and Conditions to use our service",
                                                             icon="⚠")
                            time.sleep(2.5)
                            signup_message_placeholder.empty()

                    else:
                        signup_message_placeholder.error("You must agree to our Privacy Policy to use our service",
                                                         icon="⚠")
                        time.sleep(2.5)
                        signup_message_placeholder.empty()

                else:
                    signup_message_placeholder.error("Minimum 8 characters for the password", icon="⚠")
                    time.sleep(2.5)
                    signup_message_placeholder.empty()

            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                signup_message_placeholder.error("Please provide a real email", icon="⚠")
                time.sleep(2.5)
                signup_message_placeholder.empty()


    with st.container(border=True):
        sign_title_col1, sign_title_col2, sign_title_col3 = st.columns(3)
        with sign_title_col2:
            st.title("Welcome")

        signup_message_placeholder = st.empty()

        email_placeholder = st.text_input(label="", placeholder="📧 Email")
        password_placeholder = st.text_input(label="", placeholder="🔒 Password", type="password")

        st.subheader("")

        sign_sub_col1, sign_sub_col2 = st.columns(2)
        with sign_sub_col1:
            privacy_policy_checkbox = st.checkbox("I read and agree to the")
            st.markdown("[Privacy Policy](https://drive.google.com/file/d/1xrmeVvYhzHer834o_TDiNwGp0rvrTrV_/view?usp=sharing)",
                        unsafe_allow_html=True)
        with sign_sub_col2:
            terms_and_conditions_checkbox = st.checkbox("I read and accept the")
            st.markdown("[Terms and Conditions](https://drive.google.com/file/d/1124X4IN1yQAvAYQVIebepBxeuNWJxTV5/view?usp=sharing)",
                        unsafe_allow_html=True)

        st.title("")

        sign_sub_col1, sign_sub_col2, sign_sub_col3 = st.columns(3)
        with sign_sub_col2:
            signup_but = st.button("Create account", type="primary", use_container_width=True)

        if signup_but:
            create_account()

        st.title("")

        sign_login_col1, sign_login_col2, sign_login_col3 = st.columns(3)
        with sign_login_col2:
            st.caption('<span style="font-size:19px; color:white;">Already have an account ?</span>', unsafe_allow_html=True)
            login_to_account_but = st.button("Log in", use_container_width=True)

        if login_to_account_but:
            st.session_state.current_page = "Login"
            st.rerun()

        st.title("")

        sign_img_col1, sign_img_col2, sign_img_col3 = st.columns(3)
        with sign_img_col2:
            # st.image("pickiepoint_logo_profile_picture.png", width=180)
            st.image("pickiepoint_logo_profile_picture.png", use_column_width=True)

        go_trial_but = st.button("Go Trial")
        if go_trial_but:
            st.session_state.current_page = "Trial"
            st.rerun()


if st.session_state.current_page == "Trial":

    trial_title_col1, trial_title_col2, trial_title_col3 = st.columns(3)
    with trial_title_col2:
        st.title("Get started")
        st.image("pickiepoint_logo_profile_picture.png")

        st.header("")

        st.caption('<span style="font-size:32px; font-weight:bold; color:green;">3 days free trial</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:22px; font-weight:bold; color:green;">No credit card required</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:26px; color:yellow;">Then 12.99$/month</span>', unsafe_allow_html=True)

        st.header("")

        st.caption('<span style="font-size:20px; color:white;">✅ Unlimited usage</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Zero ads</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Abstractive summary</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Extractive summary</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Summary from URL</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ 70 languages</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Auto detect language</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Audio support</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Creative paraphrasing</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Youtube captions</span>', unsafe_allow_html=True)

        st.title("")

        start_trial_but = st.button("Start trial", type="primary", use_container_width=True)
        if start_trial_but:
            st.session_state.current_page = "Trial confirmation"
            st.rerun()

        go_trial_confirmation = st.button("Go trial confirmation")
        if go_trial_confirmation:
            st.session_state.current_page = "Trial confirmation"
            st.rerun()


if st.session_state.current_page == "Trial confirmation":

    trial_conf_col1, trial_conf_col2, trial_conf_col3 = st.columns(3)
    st.image("pickiepoint_website_trial_confirmation.png", width=670)
    st.header("")

    trial_conf_sub_col1, trial_conf_sub_col2, trial_conf_sub_col3 = st.columns(3)
    with trial_conf_sub_col2:
        thanks_but = st.button("THANKS", type="primary", use_container_width=True)

    if thanks_but:
        st.session_state.current_page = "Summary"
        st.rerun()

    go_subscribe_but = st.button("Go subscribe")
    if go_subscribe_but:
        st.session_state.current_page = "Subscribe"
        st.rerun()


if st.session_state.current_page == "Subscribe":
    sub_title_col1, sub_title_col2, sub_title_col3 = st.columns(3)
    with sub_title_col2:
        st.title("Pickiepoint subscription")
        st.image("pickiepoint_logo_profile_picture.png")

        st.header("")

        st.caption('<span style="font-size:32px; font-weight:bold; color:orange;">Trial has ended</span>',
                   unsafe_allow_html=True)
        st.caption('<span style="font-size:24px; font-weight:bold; color:green;">Get unlimited access</span>',
                   unsafe_allow_html=True)
        st.caption('<span style="font-size:24px; color:yellow;">For just 12.99$/month</span>', unsafe_allow_html=True)

        st.header("")

        st.caption('<span style="font-size:20px; color:white;">✅ Unlimited usage</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Zero ads</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Abstractive summary</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Extractive summary</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Summary from URL</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ 70 languages</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Auto detect language</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Audio support</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Creative paraphrasing</span>', unsafe_allow_html=True)
        st.caption('<span style="font-size:20px; color:white;">✅ Youtube captions</span>', unsafe_allow_html=True)

        st.title("")

        subscribe_but = st.button("Continue", type="primary", use_container_width=True)
        if subscribe_but:
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price': 'price_1PGlyEGPF0oQ7Wr5oFxfZOvQ',
                    'quantity': 1,
                }],
                customer=cookie_manager.get("user_id"),
                mode='subscription',
                success_url='https://drive.google.com/file/d/1av794oc3eOxKWhdZQUmGI7ovNcDDTc1Y/view',
            )

            # Redirect user to the Stripe page where he can subscribe
            webbrowser.open(session.url)

        go_summary_but = st.button("Go summary")
        if go_summary_but:
            st.session_state.current_page = "Summary"
            st.rerun()


if st.session_state.current_page == "Login":

    with (st.container(border=True)):
        st.title("-\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0Welcome back\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0-")

        login_message_placeholder = st.empty()

        login_email_placeholder = st.text_input(label="", placeholder="📧 Email")
        login_password_placeholder = st.text_input(label="", placeholder="🔒 Password", type="password")

        st.text("")

        login_pass_col1, login_pass_col2, login_pass_col3 = st.columns(3)
        with login_pass_col3:
            forgot_password_but = st.button("Forgot password ?")

        if forgot_password_but:
            st.session_state.current_page = "Forgot password"
            st.rerun()

        st.title("")
        st.header("")

        login_sub_col1, login_sub_col2, login_sub_col3 = st.columns(3)
        with login_sub_col2:
            login_but = st.button("Login", type="primary", use_container_width=True)
            st.header("")
            st.caption('<span style="font-size:27px; color:white;">Need an account ?</span>', unsafe_allow_html=True)
            no_account_but = st.button("Create one", use_container_width=True)

        if no_account_but:
            st.session_state.current_page = "Sign up"
            st.rerun()

        st.title("")

        login_img_col1, login_img_col2, login_img_col3 = st.columns(3)
        with login_img_col2:
            st.image("pickiepoint_logo_profile_picture.png", use_column_width=True)

        if login_but:
            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()

            if login_email_placeholder == "":

                login_message_placeholder.error("Please enter your email", icon="⚠")
                time.sleep(2.5)
                login_message_placeholder.empty()

            else:

                cursor.execute("SELECT email FROM areas WHERE email = ?", (login_email_placeholder, ))

                if cursor.fetchone():

                    cursor.execute("SELECT password FROM areas WHERE email = ?", (login_email_placeholder, ))

                    if login_password_placeholder == cursor.fetchone()[0]:
                        conn = sqlite3.connect('text_areas.db')
                        cursor = conn.cursor()
                        cursor.execute("SELECT customer_id FROM areas WHERE email = ?", (login_email_placeholder, ))
                        customer_id = cursor.fetchone()[0]
                        conn.commit()
                        conn.close()

                        expiration_date_for_cookie = datetime.now() + timedelta(days=60)
                        cookie_manager.set(cookie="user_id", val=customer_id, expires_at=expiration_date_for_cookie)

                        try:
                            conn = sqlite3.connect('text_areas.db')
                            cursor = conn.cursor()

                            # the_subs = stripe.Subscription.list(customer=customer_id, status='all')

                            if subscriptions.data:
                                latest_subscription = subscriptions.data[0]
                                subscription_status = latest_subscription.status
                                if subscription_status == "active":
                                    st.session_state.current_page = "Summary"
                                    st.rerun()

                                elif subscription_status == "canceled":
                                    st.session_state.current_page = "Subscribe"
                                    st.rerun()
                                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.text = "Regain access"
                                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.color = (0, 0, 0, 1)
                                else:
                                    st.session_state.current_page = "Subscribe"
                                    st.rerun()

                            else:
                                st.header("BEYOND THE CRITICAL POINT")
                                cursor.execute("SELECT trial_start_date FROM areas WHERE customer_id = ?",
                                               (customer_id,))
                                start_date_of_trial = cursor.fetchone()[0]
                                current_date = time.time()

                                if start_date_of_trial is None:
                                    st.session_state.current_page = "Sign up"
                                    st.rerun()
                                elif current_date - start_date_of_trial > 259200:
                                    st.header(start_date_of_trial)
                                    st.header(current_date)
                                    st.header(current_date - start_date_of_trial)
                                    st.session_state.current_page = "Subscribe"
                                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.text = "Trial ended"
                                    # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.color = (0.67, 0.33, 0, 1)
                                    st.rerun()
                                elif current_date - start_date_of_trial < 259200:
                                    st.session_state.current_page = "Summary"
                                    st.rerun()
                                else:
                                    st.header("SOMETHING ELSE")
                                    pass

                        except:
                            st.subheader("ERROR")
                            cursor.execute("SELECT trial_start_date FROM areas WHERE customer_id = ?", (customer_id,))

                            start_date_of_trial = cursor.fetchone()[0]
                            current_date = time.time()
                            if start_date_of_trial is None:
                                st.session_state.current_page = "Sign up"
                                st.rerun()
                            elif start_date_of_trial < 100:
                                st.session_state.current_page = "Sign up"
                                st.rerun()
                            elif current_date - start_date_of_trial > 259200:
                                st.session_state.current_page = "Subscribe"
                                # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.text = "Trial ended"
                                # MDApp.get_running_app().root.get_screen("subscribe_screen").ids.trial_or_sub_renew_label.color = (0.67, 0.33, 0, 1)
                                st.rerun()
                            elif current_date - start_date_of_trial < 259200:
                                st.session_state.current_page = "Subscribe"
                                st.rerun()

                    else:

                        login_message_placeholder.error("Wrong password", icon="⚠")
                        time.sleep(2.5)
                        login_message_placeholder.empty()

                else:

                    login_message_placeholder.error("There is not any account associated with this email", icon="⚠")
                    time.sleep(2.5)
                    login_message_placeholder.empty()

            conn.commit()
            conn.close()


if st.session_state.current_page == "Forgot password":

    st.title("- \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0We got you covered\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 -")

    st.title("")
    st.write("")

    st.write("Just enter your email down below and we will send you a verification code that you can use to change your password")
    forgot_pass_message_placeholder = st.empty()
    forgot_pass_email_placeholder = st.text_input(label="", placeholder="📧 Email")

    st.header("")

    forgot_pass_col1, forgot_pass_col2, forgot_pass_col3 = st.columns(3)
    with forgot_pass_col2:
        send_code_but = st.button("Send code", type="primary", use_container_width=True)

    if send_code_but:
        user_email = forgot_pass_email_placeholder
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, user_email):
            forgot_pass_message_placeholder.error("Please provide a valid email", icon="⚠")
            time.sleep(2.5)
            forgot_pass_message_placeholder.empty()

        else:
            domain = user_email.split('@')[1]
            try:
                dns.resolver.resolve(domain, 'MX')

                conn = sqlite3.connect('text_areas.db')
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM areas WHERE email = ?", (user_email, ))
                if cursor.fetchone()[0]:

                    verification_code = random.randint(100000, 999999)
                    cursor.execute("SELECT customer_id FROM areas WHERE email = ?", (user_email,))
                    customer_id_for_pass_change = cursor.fetchone()[0]
                    conn.commit()
                    conn.close()

                    conn = sqlite3.connect('settings_save.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE settings SET verification_code = ? WHERE customer_id = ?",
                                   (verification_code, customer_id_for_pass_change))
                    conn.commit()
                    conn.close()

                    message = Mail(
                        from_email='support@pickiepoint.com',
                        to_emails=user_email,
                        subject='Your verification code',
                        html_content=f'<text>Your verification code that you can use to change your password: <bold>{verification_code}</bold></text>')


                    sg = SendGridAPIClient(SENGRID_API_KEY)
                    sg.send(message)

                    cookie_expiration_date = datetime.now() + timedelta(days=2)
                    cookie_manager.set(cookie="user_id_for_verification_code", val=customer_id_for_pass_change, expires_at=cookie_expiration_date)

                    st.session_state.current_page = "Verification code"
                    st.rerun()
                else:
                    forgot_pass_message_placeholder.error("There is no account associated with this email", icon="⚠")
                    time.sleep(2.5)
                    forgot_pass_message_placeholder.empty()

            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                forgot_pass_message_placeholder.error("Please provide a real email", icon="⚠")
                time.sleep(2.5)
                forgot_pass_message_placeholder.empty()

        st.rerun()


if st.session_state.current_page == "Verification code":

    ver_code_title_col1, ver_code_title_col2, ver_code_title_col3 = st.columns(3)
    with ver_code_title_col2:
        st.title("Enter code")

    st.title("")
    st.write("")

    st.write(
        "Enter the verification code we sent to your email inbox. Please consider checking your spam as well.")
    verification_code_message_placeholder = st.empty()
    verification_code_placeholder = st.text_input(label="", placeholder="🔐 Verification code")

    st.header("")

    ver_code_col1, ver_code_col2, ver_code_col3 = st.columns(3)
    with ver_code_col2:
        verify_code_but = st.button("Verify", type="primary", use_container_width=True)

    if verify_code_but:
        customer_id = cookie_manager.get("user_id_for_verification_code")

        conn = sqlite3.connect('settings_save.db')
        cursor = conn.cursor()
        cursor.execute("SELECT verification_code FROM settings WHERE customer_id = ?", (customer_id, ))
        correct_verification_code = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if verification_code_placeholder == correct_verification_code:
            st.session_state.current_page = "Password change"
            st.rerun()
        else:
            verification_code_message_placeholder.error("Wrong code", icon="⚠")
            time.sleep(2.5)
            verification_code_message_placeholder.empty()


if st.session_state.current_page == "Password change":
    st.title("- \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0Update your password\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 -")

    st.title("")
    st.write("")

    st.write(
        "You can now set up a new password for your account. Keep it somewhere safe as you will need it the next time you login. After you update it, you will be invited to login with this new password.")
    pass_change_message_placeholder = st.empty()
    pass_change_placeholder = st.text_input(label="", placeholder="🔒 New password", type="password")

    st.header("")

    pass_change_col1, pass_change_col2, pass_change_col3 = st.columns(3)
    with pass_change_col2:
        pass_change_but = st.button("Update password", type="primary", use_container_width=True)

    if pass_change_but:
        if len(pass_change_placeholder) < 8:
            pass_change_message_placeholder.error("Minimum 8 characters", icon="⚠")
            time.sleep(2.5)
            pass_change_message_placeholder.empty()
        else:
            pass_change_message_placeholder.error("Your password has been changed succesfully !", icon="✔")
            time.sleep(2)
            pass_change_message_placeholder.empty()

            targeted_customer_id = cookie_manager.get("user_id_for_verification_code")

            conn = sqlite3.connect('text_areas.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE areas SET password = ? WHERE customer_id = ?", (pass_change_placeholder, targeted_customer_id))
            conn.commit()
            conn.close()

            st.session_state.current_page = "Login"
            st.rerun()

    go_summary_screen_but = st.button("Go summary")

    if go_summary_screen_but:
        st.session_state.current_page = "Summary"
        st.rerun()
