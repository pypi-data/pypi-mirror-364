
class DataPack:
    def __init__(self, core):
        self._core = core

    def getFX(
        self,
        Symbols,
        InitialDate,
        FinalDate,
        Fields=None,
        Interval=None,
        IgnDefault=None,
        Lang=None,
        Page=None,
        Rows=None,
        Format=None,
        IgnNull=None,
        isActive=None
    ):
        """
        Executa uma requisição GET para {base_url}/getFX com o header BDSKey e parâmetros na URL.
        """
        url = f"{self._core.base_url}/getFX"
        params = {
            "Symbols": Symbols,
            "InitialDate": InitialDate,
            "FinalDate": FinalDate,
        }
        if Fields is not None: params["Fields"] = Fields
        if Interval is not None: params["Interval"] = Interval
        if IgnDefault is not None: params["IgnDefault"] = IgnDefault
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows
        if Format is not None: params["Format"] = Format
        if IgnNull is not None: params["IgnNull"] = IgnNull
        if isActive is not None: params["isActive"] = isActive

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )

    def getEquitiesB3(
        self,
        Symbols,
        InitialDate,
        FinalDate,
        Fields=None,
        Interval=None,
        IgnDefault=None,
        Lang=None,
        Page=None,
        Rows=None,
        Format=None,
        IgnNull=None,
        isActive=None
    ):
        """
        Executa uma requisição GET para {base_url}/getEquitiesB3 com o header BDSKey e parâmetros na URL.
        """
        url = f"{self._core.base_url}/getEquitiesB3"
        params = {
            "Symbols": Symbols,
            "InitialDate": InitialDate,
            "FinalDate": FinalDate,
        }
        if Fields is not None: params["Fields"] = Fields
        if Interval is not None: params["Interval"] = Interval
        if IgnDefault is not None: params["IgnDefault"] = IgnDefault
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows
        if Format is not None: params["Format"] = Format
        if IgnNull is not None: params["IgnNull"] = IgnNull
        if isActive is not None: params["isActive"] = isActive

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )
