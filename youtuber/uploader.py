import time
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .config import Config

class YouTubeUploader:
    def __init__(self, config: Config):
        self.config = config

    async def upload_to_youtube(self, subject: str):
        options = uc.ChromeOptions()
        options.add_argument(
            "--user-data-dir=/Users/manu/Library/Application\ Support/Google/Chrome/screen_ai"
        )
        driver = uc.Chrome(options=options)

        try:
            self._navigate_to_studio(driver)
            self._upload_video(driver, subject)
            self._fill_video_details(driver, subject)
            self._publish_video(driver)
        finally:
            driver.quit()

    def _navigate_to_studio(self, driver):
        driver.get(
            "https://studio.youtube.com/channel/UCS6J8BXoQOWqfcSY8rWZZ_g?c=UCS6J8BXoQOWqfcSY8rWZZ_g"
        )
        time.sleep(5)

    def _upload_video(self, driver, subject):
        upload_button = driver.find_element(By.XPATH, '//*[@id="upload-icon"]')
        upload_button.click()
        time.sleep(1)

        file_input = driver.find_element(By.XPATH, '//*[@id="content"]/input')
        abs_path = os.path.abspath(f"final_videos/{subject}.mp4")
        file_input.send_keys(abs_path)
        time.sleep(7)

    def _fill_video_details(self, driver, subject):
        with open(f"output/{subject}/script.json", "r") as f:
            data = json.load(f)

        title_text = data["youtube_title"]
        description_text = data["youtube_description"]

        title_input = driver.switch_to.active_element
        title_input.clear()
        title_input.send_keys(title_text)
        time.sleep(3)

        description_input = driver.find_element(
            By.XPATH,
            "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-video-description/div/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div",
        )
        time.sleep(1)
        description_input.send_keys(description_text)
        time.sleep(1)

    def _publish_video(self, driver):
        next_button = driver.find_element(By.XPATH, '//*[@id="next-button"]')
        for _ in range(3):
            next_button.click()
            time.sleep(1)

        private = driver.switch_to.active_element
        private.send_keys(Keys.DOWN)

        done_button = driver.find_element(By.XPATH, '//*[@id="done-button"]')
        done_button.click()
        time.sleep(20)
