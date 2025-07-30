# public imports
import pandas as pd
from typing import List

from mystockutil.logging.logging_setup import CustomAdapter
from mystockutil.logging.logging_setup import logger as original_logger

# private imports
logger = CustomAdapter(original_logger, {'prefix': 'RDP'})

# essential imports
from mydataprovider.frame.odi.df_odi import odi
import mydataprovider.provider.rdp.flask.rdf_client as rdfc


class _RDP:
    pass

class RDP_fetch(_RDP):
    """
    rdfc의 기능만을 그대로 옮긴 클래스
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rdfc = rdfc  # rdf_client 모듈을 통해 서버와 통신
    
    def fetch_from_to(self, start_date:pd.Timestamp, end_date)->pd.DataFrame:
        """
        start_date부터 end_date까지의 주식데이터를 DataFrame으로 가져온다."""
        return self.rdfc.fetch_df(start_date=start_date, end_date=end_date)
    
    def add_acc(self, symbols: List[str]) -> List[str]:
        """
        정확한 종목 코드 리스트에 종목들을 추가합니다.
        새로 추가된 종목 코드리스트를 반환합니다.
        """
        return self.rdfc.add_acc(symbols=symbols)


class RealtimeDFProvider(RDP_fetch):
    """
    RealtimeDFProvider
    -------------------
    실시간 및 과거 주식 데이터를 RDF 서버를 통해 가져오는 클래스입니다.
    `RDP_core`와 `RDP_fetch`의 기능을 상속하여,
    특정 기간, 특정 날짜 기준으로 다양한 방식으로 데이터를 가져올 수 있습니다.

    Methods
    -------
    fetch_from_to(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame
        start_date부터 end_date까지의 주식 데이터를 DataFrame으로 가져옵니다.
    
    add_acc(symbols: List[str]) -> List[str]
        정확한 종목 코드 리스트(`acc`)에 새 종목들을 추가하고, 새로 추가된 종목 코드를 반환합니다.
    """
    pass


rdp = RealtimeDFProvider() # 기본 인스턴스 생성


if __name__ == '__main__':  
    from mydataprovider.test_api import myprint as print, dh
    
    symbols = ['298380']
    
    print("Finished")