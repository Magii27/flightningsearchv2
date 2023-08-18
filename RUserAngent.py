import random


class RUserAgent:
    def __init__(self):
        self.__useragents = [
            """Mozilla/5.0 (Linux; Android 12; SM-N970F Build/SP1A.210812.016; wv) AppleWebKit/537.36 
            (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.60 Mobile Safari/537.36 
            [FB_IAB/FB4A;FBAV/419.0.0.37.71;]""",

            """Mozilla/5.0 (Linux; Android 10; BV6300Pro Build/QP1A.190711.020) AppleWebKit/537.36 
            (KHTML, like Gecko) Chrome/114.0.5735.61 Mobile Safari/537.36""",

            """Mozilla/5.0 (Linux; Android 11; LM-K410 Build/RKQ1.210420.001; wv) AppleWebKit/537.36 
            (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.60 Mobile Safari/537.36 
            [FB_IAB/FB4A;FBAV/371.0.0.24.109;]""",

            """Mozilla/5.0 (Linux; Android 11; moto g(9) plus Build/RPAS31.Q2-59-17-4-3-9; wv) AppleWebKit/537.36 
            (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.61 Mobile Safari/537.36 
            [FB_IAB/FB4A;FBAV/419.0.0.37.71;]""",

            """Mozilla/5.0 (Linux; Android 9; Redmi Note 8 Pro Build/PPR1.180610.011; wv) AppleWebKit/537.36 
            (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.60 Mobile Safari/537.36 
            YandexSearch/8.30 YandexSearchBrowser/8.30""",

            """Mozilla/5.0 (Linux; Android 11; Galaxy S20 Ultra) AppleWebKit/537.46 (KHTML, like Gecko) 
            Chrome/112.0.5615.47 Mobile Safari/537.44""",

            """Mozilla/5.0 (Linux; arm_64; Android 10; Redmi Note 8T) AppleWebKit/537.36 (KHTML, like Gecko) 
            Chrome/112.0.5615.100 Mobile Safari/537.36 YaApp_Android/10.51 YaSearchBrowser/10.51""",

            """Mozilla/5.0 (Linux; arm_64; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) 
            Chrome/105.0.5775.113 Mobile Safari/537.36""",

            """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 
            (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0""",

            """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
            Chrome/114.0.0.0 Safari/537.36"""
        ]

    def getRandomUserAgent(self):
        return self.__useragents[random.randint(0, len(self.__useragents) - 1)]
