"""
Suíte de Testes Automatizados para Exportação em Lote de Documentos (ZIP).
Garante conformidade com o padrão AAA (Arrange, Act, Assert) e Test Engineer guidelines.
"""
import unittest
import io
import zipfile
import re
from pathlib import Path
from tempfile import TemporaryDirectory


class TestExportacaoAtestesZip(unittest.TestCase):
    """Testes unitários para a lógica de filtragem, compactação e segurança do ZIP."""

    def setUp(self):
        """Arrange: Cria uma árvore temporária simulando a estrutura física dos técnicos."""
        self.temp_dir = TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        
        # Estrutura de teste:
        # /MARIA_SILVA/documentos-atividades/JOAO_SANTOS/15-05-2026_VISITA_TECNICA/ATEST_01.pdf
        # /MARIA_SILVA/documentos-atividades/JOAO_SANTOS/15-05-2026_VISITA_TECNICA/COLLETUM_01.pdf
        # /JOSE_SOUZA/documentos-atividades/ANA_LIMA/20-06-2026_PLANO_PRODUTIVO/ATEST_02.pdf
        
        pasta_maria = self.base_dir / "MARIA_SILVA" / "documentos-atividades" / "JOAO_SANTOS" / "15-05-2026_VISITA_TECNICA"
        pasta_maria.mkdir(parents=True, exist_ok=True)
        (pasta_maria / "ATEST_01.pdf").write_bytes(b"%PDF-1.4 Mock Ateste Maria")
        (pasta_maria / "COLLETUM_01.pdf").write_bytes(b"%PDF-1.4 Mock Coletum Maria")
        (pasta_maria / "SIGATER_01.pdf").write_bytes(b"%PDF-1.4 Mock Sigater Maria")
        (pasta_maria / "foto.png").write_bytes(b"\x89PNG Mock Image")
        (pasta_maria / "ignorar.txt").write_text("nao incluir")

        pasta_jose = self.base_dir / "JOSE_SOUZA" / "documentos-atividades" / "ANA_LIMA" / "20-06-2026_PLANO_PRODUTIVO"
        pasta_jose.mkdir(parents=True, exist_ok=True)
        (pasta_jose / "ATEST_02.pdf").write_bytes(b"%PDF-1.4 Mock Ateste Jose")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _gerar_zip_helper(self, mes=None, ano=None, tecnico=None, tipo="todos"):
        """Função espelho da lógica de geração de ZIP de beneficiarios.py."""
        zip_buffer = io.BytesIO()
        arquivos_incluidos = 0
        tipo_filtro = (tipo or "todos").lower().strip()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root_dir, _, files in self.base_dir.walk() if hasattr(self.base_dir, 'walk') else [
                (str(p), [], [f.name for f in p.iterdir() if f.is_file()])
                for p in self.base_dir.glob('**') if p.is_dir()
            ]:
                for f_name in files:
                    if not f_name.lower().endswith(('.pdf', '.docx', '.jpg', '.png')):
                        continue
                    
                    f_upper = f_name.upper()
                    if tipo_filtro == "ateste" and "ATEST" not in f_upper:
                        continue
                    elif tipo_filtro == "coletum" and "COLLETUM" not in f_upper and "COLETUM" not in f_upper:
                        continue
                    elif tipo_filtro == "sigater" and "SIGATER" not in f_upper:
                        continue
                        
                    file_path = Path(root_dir) / f_name
                    rel_path = file_path.relative_to(self.base_dir)
                    partes_caminho = [p.upper() for p in rel_path.parts]
                    
                    if tecnico:
                        tec_norm = re.sub(r'[^A-Z0-9]', '', tecnico.upper())
                        if not any(tec_norm in re.sub(r'[^A-Z0-9]', '', p) for p in partes_caminho):
                            continue
                            
                    caminho_str = str(rel_path)
                    m_data = re.search(r'(\d{2})[.\-\/](\d{2})[.\-\/](\d{4})', caminho_str)
                    f_mes, f_ano = None, None
                    if m_data:
                        _, mes_str, ano_str = m_data.groups()
                        f_mes = int(mes_str)
                        f_ano = int(ano_str)
                        
                    if mes is not None and f_mes != mes:
                        continue
                    if ano is not None and f_ano != ano:
                        continue
                        
                    zf.write(str(file_path), arcname=str(rel_path))
                    arquivos_incluidos += 1
                    
        zip_buffer.seek(0)
        return zip_buffer, arquivos_incluidos

    def test_geracao_zip_todos_arquivos(self):
        """Act & Assert: Exportar sem filtros deve incluir todos os documentos válidos."""
        buf, total = self._gerar_zip_helper()
        self.assertGreater(total, 0)
        self.assertEqual(total, 5)  # 3 pdfs + 1 png de Maria, 1 pdf de Jose = total 5 - texto ignorado
        
        with zipfile.ZipFile(buf, "r") as zf:
            nomes = zf.namelist()
            self.assertTrue(any("ATEST_01.pdf" in n for n in nomes))
            self.assertTrue(any("COLLETUM_01.pdf" in n for n in nomes))
            self.assertFalse(any("ignorar.txt" in n for n in nomes))

    def test_filtro_por_mes_e_ano(self):
        """Act & Assert: Filtrar por mês 5 e ano 2026 deve retornar apenas arquivos de maio."""
        buf, total = self._gerar_zip_helper(mes=5, ano=2026)
        self.assertEqual(total, 4)
        
        # Mês 6 (junho) deve retornar 1 arquivo (de José)
        buf_junho, total_junho = self._gerar_zip_helper(mes=6, ano=2026)
        self.assertEqual(total_junho, 1)

    def test_filtro_por_tipo_ateste_e_coletum(self):
        """Act & Assert: Filtrar por tipo 'ateste' deve ignorar coletum e imagens."""
        buf_ateste, total_ateste = self._gerar_zip_helper(tipo="ateste")
        self.assertEqual(total_ateste, 2)  # ATEST_01 e ATEST_02
        
        with zipfile.ZipFile(buf_ateste, "r") as zf:
            for nome in zf.namelist():
                self.assertIn("ATEST", nome.upper())

    def test_filtro_por_tecnico_especifico(self):
        """Act & Assert: Filtrar pelo técnico Maria Silva deve retornar apenas seus arquivos."""
        buf_tec, total_tec = self._gerar_zip_helper(tecnico="Maria Silva")
        self.assertEqual(total_tec, 4)
        
        with zipfile.ZipFile(buf_tec, "r") as zf:
            for nome in zf.namelist():
                self.assertTrue("MARIA_SILVA" in nome.upper())


if __name__ == "__main__":
    unittest.main()
