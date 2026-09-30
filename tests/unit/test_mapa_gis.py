import io
import os
import sys
import json
import zipfile
from PIL import Image
import shapefile

sys.path.insert(0, os.path.abspath("."))

from app.modules.mapa.gis_utils import (
    extract_exif_gps,
    export_to_shapefile,
    export_to_geojson,
    export_to_kml,
    SIRGAS_2000_WKT
)

def test_export_to_shapefile():
    pontos = [
        {
            "id": 101,
            "nome": "Cisterna Calçadão Dona Lindinalva",
            "tipo": "Cisterna Calçadão (52.000L - 2ª Água)",
            "municipio": "Paulo Afonso",
            "comunidade": "Xingozinho",
            "status_obra": "Concluída / Em Uso",
            "beneficiario": "Lindinalva de Sá",
            "area_telhado": 200.0,
            "edital": "Água que Alimenta",
            "responsavel": "weverton",
            "data_coleta": "2026-09-28 10:00:00",
            "latitude": -9.382100,
            "longitude": -38.214500,
            "foto_url": "/static/uploads/mapa/foto1.jpg",
            "descricao": "Cisterna cheia e em pleno funcionamento"
        },
        {
            "id": 102,
            "nome": "Cisterna 1ª Água Seu Severino",
            "tipo": "Cisterna de Placa (16.000L - 1ª Água)",
            "municipio": "Glória",
            "comunidade": "Quixaba",
            "status_obra": "Em Construção",
            "beneficiario": "Severino dos Anjos",
            "area_telhado": 55.0,
            "edital": "BNDES / ASA",
            "responsavel": "weverton",
            "data_coleta": "2026-09-28 10:15:00",
            "latitude": -9.335000,
            "longitude": -38.258000,
            "foto_url": "",
            "descricao": "Fase de reboco e cobertura"
        }
    ]

    zip_bytes = export_to_shapefile(pontos)
    assert zip_bytes is not None
    assert len(zip_bytes) > 0

    # Validação do arquivo ZIP
    zip_buf = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_buf, 'r') as z:
        namelist = z.namelist()
        assert 'pontos_agendha.shp' in namelist
        assert 'pontos_agendha.shx' in namelist
        assert 'pontos_agendha.dbf' in namelist
        assert 'pontos_agendha.prj' in namelist
        assert 'pontos_agendha.cpg' in namelist
        assert 'LEIA-ME_QGIS.txt' in namelist

        # Validação do conteúdo da projeção SIRGAS 2000
        prj_content = z.read('pontos_agendha.prj').decode('utf-8')
        assert "SIRGAS 2000" in prj_content

        cpg_content = z.read('pontos_agendha.cpg').decode('utf-8')
        assert "UTF-8" in cpg_content

        # Validação da leitura do shapefile
        shp_data = io.BytesIO(z.read('pontos_agendha.shp'))
        shx_data = io.BytesIO(z.read('pontos_agendha.shx'))
        dbf_data = io.BytesIO(z.read('pontos_agendha.dbf'))

        with shapefile.Reader(shp=shp_data, shx=shx_data, dbf=dbf_data, encoding='utf-8') as sf:
            assert len(sf.shapes()) == 2
            records = sf.records()
            assert len(records) == 2
            # Verificar primeiro registro
            rec1 = records[0]
            assert rec1['ID'] == 101
            assert "Lindinalva" in rec1['NOME']
            assert rec1['MUNICIPIO'] == "Paulo Afonso"
            assert rec1['STATUS_OBR'] == "Concluída / Em Uso"


def test_export_to_geojson():
    pontos = [
        {
            "id": 1,
            "nome": "Cisterna Teste",
            "tipo": "Cisterna de Placa",
            "municipio": "Paulo Afonso",
            "comunidade": "Xingozinho",
            "status_obra": "Concluída",
            "beneficiario": "Maria",
            "area_telhado": 50,
            "edital": "P1MC",
            "responsavel": "admin",
            "data_coleta": "2026-09-28",
            "latitude": -9.4,
            "longitude": -38.2,
            "foto_url": "/static/foto.jpg",
            "descricao": "Nota técnica"
        }
    ]

    geo = export_to_geojson(pontos)
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) == 1
    feat = geo["features"][0]
    assert feat["geometry"]["type"] == "Point"
    assert feat["geometry"]["coordinates"] == [-38.2, -9.4]
    assert feat["properties"]["municipio"] == "Paulo Afonso"
    assert feat["properties"]["beneficiario"] == "Maria"


def test_export_to_kml():
    pontos = [
        {
            "id": 1,
            "nome": "Cisterna Calçadão",
            "tipo": "Cisterna Calçadão",
            "municipio": "Glória",
            "comunidade": "Brejo do Burgo",
            "status_obra": "Em Uso",
            "beneficiario": "José",
            "area_telhado": 200,
            "latitude": -9.3,
            "longitude": -38.1,
            "foto_url": "https://agendha.org/foto.jpg"
        }
    ]

    kml = export_to_kml(pontos)
    assert "<kml" in kml
    assert "<Placemark>" in kml
    assert "<coordinates>-38.1,-9.3,0</coordinates>" in kml
    assert "Cisterna Calçadão" in kml


def test_extract_exif_gps_without_gps():
    # Cria uma imagem temporária em memória sem GPS
    img = Image.new('RGB', (100, 100), color='blue')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)

    result = extract_exif_gps(buf)
    assert result["has_gps"] is False
    assert result["latitude"] is None
    assert result["longitude"] is None


if __name__ == "__main__":
    test_export_to_shapefile()
    test_export_to_geojson()
    test_export_to_kml()
    test_extract_exif_gps_without_gps()
    print("[SUCESSO] Todos os testes unitarios de SIG passaram com louvor!")
