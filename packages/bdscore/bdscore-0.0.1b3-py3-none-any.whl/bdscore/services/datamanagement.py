import time


class DataManagement:

    def getFamilies(
        self,
        FamilyId=None,
        Status=None,
        FilterId=None,
        SourceId=None,
        AttributeId=None,
        NotebookId=None,
        CadasterId=None,
        TableId=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Método para consultar famílias de dados

        @param FamilyId: ID da família de dados
        @param Status: Status da família de dados
        @param FilterId: ID do filtro
        @param SourceId: ID da fonte de dados
        @param AttributeId: ID do atributo
        @param NotebookId: ID do caderno
        @param CadasterId: ID do cadastro
        @param TableId: ID da tabela
        @param Lang: Idioma da resposta
        @param Page: Número da página
        @param Rows: Número de linhas por página
        @return: Resposta da API DataManagement
        """
        url = f"{self._core.datamanagement_url}/Family"
        params = {}
        if FamilyId is not None: params["FamilyId"] = FamilyId
        if Status is not None: params["Status"] = Status
        if FilterId is not None: params["FilterId"] = FilterId
        if SourceId is not None: params["SourceId"] = SourceId
        if AttributeId is not None: params["AttributeId"] = AttributeId
        if NotebookId is not None: params["NotebookId"] = NotebookId
        if CadasterId is not None: params["CadasterId"] = CadasterId
        if TableId is not None: params["TableId"] = TableId
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )
    def __init__(self, core):
        self._core = core

    
    
    def getValues(
        self,
        FamilyId,
        InitialDate,
        SeriesId=None,
        Interval=None,
        AttributesId=None,
        CadastersId=None,
        FinalDate=None,
        IsActive=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Consulta valores de séries temporais de acordo com os parâmetros da API DataManagement.
        Parâmetros obrigatórios: FamilyId, InitialDate
        """
        if not FamilyId or not InitialDate:
            raise ValueError("Os parâmetros 'FamilyId' e 'InitialDate' são obrigatórios.")

        url = f"{self._core.datamanagement_url}/getValues"
        params = {
            "FamilyId": FamilyId,
            "InitialDate": InitialDate,
        }
        if SeriesId is not None: params["SeriesId"] = SeriesId
        if Interval is not None: params["Interval"] = Interval
        if AttributesId is not None: params["AttributesId"] = AttributesId
        if CadastersId is not None: params["CadastersId"] = CadastersId
        if FinalDate is not None: params["FinalDate"] = FinalDate
        if IsActive is not None: params["IsActive"] = IsActive
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )