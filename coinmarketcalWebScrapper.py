from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import pandas as pd

from .EventCardElement import EventCardElement


class coinmarketcalWebScrapper(object):

    def __init__(self, webdriver_path='G:\\Storage\\Repos\\TCC\\data\\loaders\\coinmarketcalScrapper\\chromedriver.exe'):
        self.driver = webdriver.Chrome(executable_path=webdriver_path)
        self.wait = WebDriverWait(self.driver, 6)

    def __del__(self):
        self.close()

    def close(self):
        self.driver.quit()

    def _extract_data_from_eventCards(self, data, eventCard_list_element) -> dict:
        for evento in eventCard_list_element:
            evento = EventCardElement(evento)
            data['added_date'].append(evento.added_date)
            data['event_date'].append(evento.event_date)
            data['title'].append(evento.title)
            data['votes'].append(evento.votes)
            data['confidence'].append(evento.confidence_percentage)

        return data

    def get_past_events(self, crypto='bitcoin') -> pd.DataFrame:
        url = 'https://coinmarketcal.com/en/coin/%s' % crypto
        self.driver.get(url)
        self.__safeClick((By.CSS_SELECTOR, "a[href=\#past]"))
        self.__show_all_eventCards()

        eventos_elem = self.driver.find_elements_by_css_selector("#past .row.list-card article")
        dados = {'added_date': [], 'event_date': [], 'title': [], 'votes': [], 'confidence': []}
        self._extract_data_from_eventCards(dados, eventos_elem)

        df = pd.DataFrame(dados, columns=['added_date', 'event_date', 'title', 'votes', 'confidence'])
        df['added_date'].astype('datetime64[ns]')
        df['event_date'].astype('datetime64[ns]')

        return df

    def get_upcoming_events(self, crypto='bitcoin') -> pd.DataFrame:
        url = 'https://coinmarketcal.com/en/coin/%s' % crypto
        self.driver.get(url)
        self.__safeClick((By.CSS_SELECTOR, "a[href=\#upcoming]"))
        self.__show_all_eventCards()

        eventos_elem = self.driver.find_elements_by_css_selector("#upcoming .row.list-card article")
        dados = {'added_date': [], 'event_date': [], 'title': [], 'votes': [], 'confidence': []}
        self._extract_data_from_eventCards(dados, eventos_elem)

        df = pd.DataFrame(dados, columns=['added_date', 'event_date', 'title', 'votes', 'confidence'])
        df['added_date'].astype('datetime64[ns]')
        df['event_date'].astype('datetime64[ns]')

        return df

    def __show_all_eventCards(self):
        while True:
            try:
                elem = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".active a.load-more:not(.d-none a):not([disabled=disabled])")))
                elem.click()
            except TimeoutException:
                break

        # scrool down, forcing the page to load all data
        page = self.driver.find_element_by_tag_name("body")
        page.send_keys(Keys.CONTROL, Keys.END)

    def __safeClick(self, locator):
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except TimeoutException as e:
            self.driver.quit()
            raise e
