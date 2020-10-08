import logging
import os
import shutil
from datetime import datetime, timedelta



import pandas as pd
import fastparquet
from oi_sud.cases.consts import *
from oi_sud.cases.parsers.moscow import MoscowParser
from oi_sud.cases.parsers.rf import FirstParser, SecondParser

logger = logging.getLogger(__name__)

#dask.config.set({'distributed.logging.distributed': 'info'})


class Scraper():
    __slots__ = ()

    @staticmethod
    def mkdirs(path):
        return os.makedirs(path, exist_ok=True)

    def save_cases_from_parquet(self, region, court, codex, stage, timestamp_from, filepath='/data/scraped/'):

        # читаем паркет и сохраняем дела в postgres

        if not timestamp_from:
            timestamp_from = datetime.now() - timedelta(hours=24)
            timestamp_from = timestamp_from.timestamp()

        court_title = court.title.split(' (')[0]

        df = pd.read_parquet(filepath,
                             filters=[('region', '==', region),
                                      ('court', '==', court_title),
                                      ('stage', '==', stage),
                                      ('codex', '==', codex),
                                      ('timestamp', '>', timestamp_from)])

        court_site_type = court.site_type

        if court_site_type == 1:
            parser = FirstParser(codex=codex, stage=stage, court=court)
        elif court_site_type == 2:
            parser = SecondParser(codex=codex, stage=stage, court=court)
        elif court_site_type == 3:
            parser = MoscowParser(codex=codex, stage=stage, court=court)

        parser.save_cases_from_df(df)

    def save_parquet_from_court_urls(self, urls_data, filepath='/data/scraped/'):

        # пишем в паркет сырой html карточек дел и тексты, если есть.
        # cоздаем древовидную структуру регион -> суд -> год -> кодекс -> инстанция

        stage = urls_data['stage']
        codex = urls_data['codex']
        court = urls_data['court_title'].split(' (')[0]
        region = urls_data['region']
        year = urls_data['year']

        if not urls_data.get('cases_urls'):
            return

        records = self.get_records_from_urls_data(urls_data)

        df_new = pd.DataFrame(records)




        try:

            df_old = pd.read_parquet(filepath,
                                     filters=[('codex', '==', codex), ('stage', '==', stage), ('region', '==', region),
                                              ('court', '==', court), ('year', '==', year)])
            df_concatenated = pd.concat([df_new, df_old])

            # убираем дупликаты
            new_df = df_concatenated.drop_duplicates(
                subset=['codex', 'stage', 'region', 'court', 'case_url', 'case_html', 'year'])  # .compute()

            # удаляем старый файл
            shutil.rmtree(f'{filepath}region={region}/court={court}/year={year}/codex={codex}/stage={stage}/')

            # пишем датасет без дупликатов в новый
            new_df.to_parquet(filepath, engine='pyarrow', compression='gzip',
                              partition_cols=['region', 'court', 'year', 'codex', 'stage'])

        except FileNotFoundError:
            df_new.to_parquet(filepath, engine='pyarrow', compression='gzip',
                              partition_cols=['region', 'court', 'year', 'codex', 'stage'])
