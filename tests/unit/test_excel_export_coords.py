import unittest
from unittest.mock import MagicMock, patch
import io
import openpyxl

from app.modules.agua_que_alimenta.routers.beneficiarios import RelatorioRequest, gerar_relatorio_excel


class TestExcelExportCoords(unittest.IsolatedAsyncioTestCase):
    @patch("app.modules.agua_que_alimenta.routers.beneficiarios.get_supabase")
    async def test_gerar_relatorio_excel_com_coordenadas(self, mock_get_supabase):
        # Mock Supabase
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_in = MagicMock()
        
        # Simulated database return with latitude and longitude
        fake_db_data = [
            {
                "nome_familiar": "Maria Silva",
                "cpf_familiar": "123.456.789-00",
                "municipio": "PAULO AFONSO",
                "comunidade": "Lagoa Grande",
                "latitude": "-9.65963",
                "longitude": "-38.31300",
                "status": "CADASTRADO",
                "nis": "12345678901",
                "tecnico_agua_que_alimenta": "HELDER",
                "doc_status": "uploads/doc1.pdf",
                "grh": "GRH 3"
            },
            {
                "nome_familiar": "João Santos",
                "cpf_familiar": "987.654.321-99",
                "municipio": "PAULO AFONSO",
                "comunidade": "Baixa da Onça",
                "latitude": "-9.64643",
                "longitude": "-38.29869",
                "status": "IMPORTADO",
                "nis": "98765432100",
                "tecnico_agua_que_alimenta": "HELDER",
                "doc_status": None,
                "grh": "GRH 2"
            }
        ]
        
        mock_execute_res = MagicMock()
        mock_execute_res.data = fake_db_data
        
        mock_in.execute.return_value = mock_execute_res
        mock_select.in_.return_value = mock_in
        mock_table.select.return_value = mock_select
        mock_supabase.table.return_value = mock_table
        mock_get_supabase.return_value = mock_supabase

        request_payload = RelatorioRequest(
            ids=[1, 2],
            colunas=[
                "numero_ordem",
                "nome_familiar",
                "cpf_familiar",
                "municipio",
                "comunidade",
                "latitude",
                "longitude",
                "status"
            ]
        )

        response = await gerar_relatorio_excel(request_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.media_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Ler o stream gerado no Excel
        excel_bytes = io.BytesIO()
        async for chunk in response.body_iterator:
            excel_bytes.write(chunk)
        excel_bytes.seek(0)

        wb = openpyxl.load_workbook(excel_bytes)
        self.assertIn("Beneficiários", wb.sheetnames)
        sheet = wb["Beneficiários"]

        headers = [cell.value for cell in sheet[1]]
        expected_headers = ["Nº", "Nome", "CPF", "Município", "Comunidade", "Latitude", "Longitude", "Status"]
        self.assertEqual(headers, expected_headers)

        # Validar dados da primeira linha
        row2 = [cell.value for cell in sheet[2]]
        self.assertEqual(row2[0], 1)
        self.assertEqual(row2[1], "Maria Silva")
        self.assertEqual(row2[5], "-9.65963")
        self.assertEqual(row2[6], "-38.31300")

        # Validar dados da segunda linha
        row3 = [cell.value for cell in sheet[3]]
        self.assertEqual(row3[0], 2)
        self.assertEqual(row3[1], "João Santos")
        self.assertEqual(row3[5], "-9.64643")
        self.assertEqual(row3[6], "-38.29869")


if __name__ == "__main__":
    unittest.main()
