import time
import numpy as np
from typing import Dict, Any, List
import gspread
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.colab import auth
from google.auth import default
from copy import copy



class SheetSimulator:
    """
    Simulador conectado a un Google Sheets que permite modificar inputs,
    leer outputs y automatizar simulaciones de escenarios financieros.
    """

    def __init__(self, spreadsheet, spreadsheet_id, sheets_api):
        self.spreadsheet = spreadsheet
        self.spreadsheet_id = spreadsheet_id
        self.sheets_api = sheets_api
        self.inputs = []
        self.outputs = []
        self.initial_inputs = {}

    @classmethod
    def _authorize(cls):
        """
        Maneja la autenticación estándar de Google Colab.
        """
        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)
        sheets_api = build("sheets", "v4", credentials=creds)
        return gc, sheets_api

    @classmethod
    def from_sheet_url(cls, spreadsheet_url: str):
        """
        Inicializa el simulador a partir de una URL de Google Sheets usando auth interactiva (Colab).
        """
        gc, sheets_api = cls._authorize()
        spreadsheet = gc.open_by_url(spreadsheet_url)
        spreadsheet_id = spreadsheet.id
        return cls(spreadsheet, spreadsheet_id, sheets_api)

    @classmethod
    def from_spreadsheet_id(cls, spreadsheet_id: str):
        """
        Inicializa el simulador a partir del ID del spreadsheet (sin .json).
        """
        gc, sheets_api = cls._authorize()
        spreadsheet = gc.open_by_key(spreadsheet_id)
        return cls(spreadsheet, spreadsheet_id, sheets_api)

    def set_inputs(self, inputs: List[Dict[str, str]]):
        self.inputs = inputs
        self.initial_inputs = self.read_cells(inputs)

    def set_outputs(self, outputs: List[Dict[str, str]]):
        self.outputs = outputs

    def read_inputs(self) -> Dict[str, Any]:
        """
        Devuelve los valores actuales de los inputs definidos.
        """
        return self.read_cells(self.inputs)

    def read_outputs(self) -> Dict[str, Any]:
        """
        Devuelve los valores actuales de los outputs definidos.
        """
        return self.read_cells(self.outputs)

    def restore_inputs(self):
        self.set_cells(self.inputs, self.initial_inputs)

    def run_simulation(self, new_inputs: Dict[str, Any], delay_seconds: float = 1.5, restore_inputs=True) -> Dict[str, Any]:
        """
        Corre una simulación: aplica nuevos inputs, lee outputs y restaura estado original.
        """

        new_inputs_ = copy(self.initial_inputs)
        new_inputs_.update(new_inputs)

        self.set_cells(self.inputs, new_inputs_)
        time.sleep(delay_seconds)
        outputs = self.read_cells(self.outputs)
        if restore_inputs:
          self.restore_inputs()
        return outputs

    def run_multiple_scenarios(
      self, scenarios: List[Dict[str, Any]],
      delay_seconds: float = 1.5,
      restore_inputs=True
    ) -> List[Dict[str, Any]]:
        """
        Corre múltiples simulaciones y retorna una lista de pares input/output.
        """
        results = []
        for scenario in scenarios:
            output = self.run_simulation(
              new_inputs=scenario,
              delay_seconds=delay_seconds,
              restore_inputs=restore_inputs
            )
            results.append({
                "input": scenario,
                "output": output
            })
        return results

    @staticmethod
    def read_cells_from_sheet(spreadsheet, spreadsheet_id, sheets_api, items):
        result = {}
        for item in items:
            range_str = f"{item['sheet']}!{item['range']}"
            response = sheets_api.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_str,
                valueRenderOption='UNFORMATTED_VALUE'
            ).execute()
            values = response.get("values", [])

            if ":" in item["range"]:
                cleaned = []
                for row in values:
                    cleaned_row = [float(cell) if cell not in ("", None) else 0.0 for cell in row]
                    cleaned.append(cleaned_row)
                result[item["name"]] = np.array(cleaned)
            else:
                val = values[0][0] if values and values[0] else 0.0
                result[item["name"]] = float(val)
        return result

    def read_cells(self, items: List[Dict[str, str]]) -> Dict[str, Any]:
        return self.read_cells_from_sheet(self.spreadsheet, self.spreadsheet_id, self.sheets_api, items)

    def set_cells(self, items: List[Dict[str, str]], values: Dict[str, Any]):
        for item in items:
            name = item["name"]
            sheet = self.spreadsheet.worksheet(item["sheet"])
            range_name = item["range"]
            value = values[name]

            if ":" in range_name:
                if isinstance(value, np.ndarray):
                    value = value.tolist()
                sheet.update(range_name=range_name, values=value)
            else:
                sheet.update(range_name=range_name, values=[[value]])



