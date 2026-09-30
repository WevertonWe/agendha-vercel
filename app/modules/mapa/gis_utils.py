import io
import json
import zipfile
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ExifTags
import shapefile


# --- SIRGAS 2000 WKT PROJECTION (Official Brazil Standard / EPSG:4674) ---
SIRGAS_2000_WKT = (
    'GEOGCS["SIRGAS 2000",'
    'DATUM["Sistema_de_Referencia_Geocentrico_para_las_AmericaS_2000",'
    'SPHEROID["GRS 1980",6378137,298.257222101]],'
    'PRIMEM["Greenwich",0],'
    'UNIT["Degree",0.017453292519943295]]'
)


import math

def _convert_dms_to_dd(dms_values, ref: str) -> Optional[float]:
    """
    Converte coordenadas de Graus, Minutos e Segundos (DMS) do EXIF
    para Graus Decimais (DD), com proteção total contra divisão por zero e NaN.
    """
    try:
        def to_float(val):
            try:
                if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                    if val.denominator == 0:
                        return None
                    f = float(val.numerator) / float(val.denominator)
                    return None if math.isnan(f) else f
                if isinstance(val, (tuple, list)) and len(val) == 2:
                    if val[1] == 0:
                        return None
                    f = float(val[0]) / float(val[1])
                    return None if math.isnan(f) else f
                f = float(val)
                return None if math.isnan(f) else f
            except Exception:
                return None

        deg = to_float(dms_values[0])
        minute = to_float(dms_values[1])
        sec = to_float(dms_values[2])

        if deg is None or minute is None or sec is None:
            return None

        dd = deg + (minute / 60.0) + (sec / 3600.0)
        if math.isnan(dd) or dd == 0.0:
            return None

        if ref and str(ref).upper() in ['S', 'W']:
            dd = -dd
        return round(dd, 7)
    except Exception as e:
        print(f"Erro ao converter DMS para DD: {e}")
        return None


def extract_exif_gps(image_source) -> Dict[str, Any]:
    """
    Extrai coordenadas GPS (Latitude, Longitude), Altitude e Data/Hora
    de fotos tiradas com celulares ou aplicativos como Timestamp Camera.
    """
    result = {
        "has_gps": False,
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "data_coleta": None
    }

    try:
        img = Image.open(image_source)
        exif = None
        if hasattr(img, 'getexif'):
            exif = img.getexif()
        elif hasattr(img, '_getexif'):
            exif = img._getexif()

        if not exif:
            return result

        # 1. Obter IFD do GPS
        gps_info = None
        if hasattr(exif, 'get_ifd') and hasattr(ExifTags, 'IFD') and hasattr(ExifTags.IFD, 'GPSInfo'):
            try:
                gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
            except Exception:
                gps_info = None

        # Fallback para tags GPS padrão (tag 34853)
        if not gps_info:
            if hasattr(exif, 'get') and 34853 in exif:
                gps_info = exif[34853]
            elif isinstance(exif, dict) and 34853 in exif:
                gps_info = exif[34853]

        if not gps_info:
            return result

        # Mapear tags do GPSInfo
        gps_tags = {}
        for key, val in gps_info.items():
            sub_tag = ExifTags.GPSTAGS.get(key, key)
            gps_tags[sub_tag] = val

        lat_dms = gps_tags.get("GPSLatitude") or gps_info.get(2)
        lat_ref = gps_tags.get("GPSLatitudeRef") or gps_info.get(1) or "N"
        lng_dms = gps_tags.get("GPSLongitude") or gps_info.get(4)
        lng_ref = gps_tags.get("GPSLongitudeRef") or gps_info.get(3) or "E"

        if lat_dms and lng_dms:
            lat = _convert_dms_to_dd(lat_dms, lat_ref)
            lng = _convert_dms_to_dd(lng_dms, lng_ref)

            if lat is not None and lng is not None and not math.isnan(lat) and not math.isnan(lng):
                if -90 <= lat <= 90 and -180 <= lng <= 180 and not (lat == 0 and lng == 0):
                    result["latitude"] = lat
                    result["longitude"] = lng
                    result["has_gps"] = True

        # Altitude
        alt = gps_tags.get("GPSAltitude")
        if alt:
            try:
                if hasattr(alt, 'numerator'):
                    result["altitude"] = round(float(alt.numerator) / float(alt.denominator), 1)
                else:
                    result["altitude"] = round(float(alt), 1)
            except Exception:
                pass

        # Data e Hora da Captura
        date_str = None
        # Tenta DateTimeOriginal ou DateTime do EXIF
        for dt_tag in [36867, 306, 36868]: # DateTimeOriginal, DateTime, DateTimeDigitized
            val = exif.get(dt_tag)
            if val and isinstance(val, str):
                date_str = val
                break

        if not date_str and "GPSDateStamp" in gps_tags:
            date_part = gps_tags.get("GPSDateStamp")
            time_part = gps_tags.get("GPSTimeStamp")
            if date_part and time_part:
                try:
                    h = int(time_part[0])
                    m = int(time_part[1])
                    s = int(time_part[2])
                    date_str = f"{date_part} {h:02d}:{m:02d}:{s:02d}"
                except Exception:
                    date_str = str(date_part)

        if date_str:
            # Padroniza para YYYY-MM-DD HH:MM:SS
            try:
                clean_str = date_str.replace(":", "-", 2)
                dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
                result["data_coleta"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                result["data_coleta"] = str(date_str)

    except Exception as e:
        print(f"Erro ao processar EXIF GPS: {e}")

    return result


def export_to_shapefile(pontos: List[Dict[str, Any]]) -> bytes:
    """
    Gera um arquivo ZIP contendo o Shapefile oficial (.shp, .shx, .dbf, .prj, .cpg)
    projetado em SIRGAS 2000 (EPSG:4674), padronizado para Prefeituras e QGIS.
    """
    shp_buf = io.BytesIO()
    shx_buf = io.BytesIO()
    dbf_buf = io.BytesIO()

    with shapefile.Writer(shp=shp_buf, shx=shx_buf, dbf=dbf_buf, shapeType=shapefile.POINT, encoding='utf-8') as w:
        # Campos padronizados (DBF limite de 10 caracteres nos nomes)
        w.field('ID', 'N', 10, 0)
        w.field('NOME', 'C', 100)
        w.field('TIPO', 'C', 80)
        w.field('MUNICIPIO', 'C', 60)
        w.field('COMUNIDADE', 'C', 60)
        w.field('STATUS_OBR', 'C', 40)
        w.field('BENEFICIAR', 'C', 80)
        w.field('AREA_M2', 'N', 10, 2)
        w.field('EDITAL', 'C', 60)
        w.field('RESPONSAV', 'C', 40)
        w.field('DATA_COLET', 'C', 30)
        w.field('LATITUDE', 'N', 12, 6)
        w.field('LONGITUDE', 'N', 12, 6)

        for p in pontos:
            lat = p.get('latitude')
            lng = p.get('longitude')
            if lat is None or lng is None:
                continue

            try:
                lat_f = float(lat)
                lng_f = float(lng)
            except (ValueError, TypeError):
                continue

            # pyshp w.point(X, Y) -> (Longitude, Latitude)
            w.point(lng_f, lat_f)

            # Atributos limpos
            pid = int(p.get('id', 0) or 0)
            nome = str(p.get('nome') or '')[:100]
            tipo = str(p.get('tipo') or '')[:80]
            muni = str(p.get('municipio') or '')[:60]
            comu = str(p.get('comunidade') or '')[:60]
            st_obra = str(p.get('status_obra') or p.get('status_beneficiario') or '')[:40]
            benef = str(p.get('beneficiario') or '')[:80]
            
            try:
                area_m2 = float(p.get('area_telhado') or 0.0)
            except (ValueError, TypeError):
                area_m2 = 0.0

            edital = str(p.get('edital') or '')[:60]
            resp = str(p.get('responsavel') or '')[:40]
            dt_coleta = str(p.get('data_coleta') or '')[:30]

            w.record(
                pid,
                nome,
                tipo,
                muni,
                comu,
                st_obra,
                benef,
                area_m2,
                edital,
                resp,
                dt_coleta,
                lat_f,
                lng_f
            )

    # Empacotar em ZIP
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('pontos_agendha.shp', shp_buf.getvalue())
        z.writestr('pontos_agendha.shx', shx_buf.getvalue())
        z.writestr('pontos_agendha.dbf', dbf_buf.getvalue())
        z.writestr('pontos_agendha.cpg', 'UTF-8')
        z.writestr('pontos_agendha.prj', SIRGAS_2000_WKT)
        
        leia_me = (
            "===========================================================\n"
            "CAMADA ESPACIAL AGENDHA - PROJETOS DE ÁGUA E CONVIVÊNCIA\n"
            "===========================================================\n"
            "Formato: Shapefile (ESRI)\n"
            "Sistema de Coordenadas de Referência (CRS): SIRGAS 2000 (EPSG:4674)\n"
            "Compatibilidade: QGIS, ArcGIS, Google Earth, Prefeituras e Órgãos Públicos.\n"
            "Data da Extração: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n\n"
            "Campos da Tabela de Atributos:\n"
            "- ID: Código Identificador\n"
            "- NOME: Nome do Local / Beneficiário\n"
            "- TIPO: Tecnologia Social de Água (Cisterna 16k L, Calçadão 52k L, etc.)\n"
            "- MUNICIPIO: Município no Território Itaparica\n"
            "- COMUNIDADE: Comunidade Rural ou Assentamento\n"
            "- STATUS_OBR: Status da Obra / Implementação\n"
            "- BENEFICIAR: Agricultor(a) Familiar Beneficiário(a)\n"
            "- AREA_M2: Área de Captação (m² de Telhado ou Calçadão)\n"
            "- EDITAL: Projeto / Convênio Financiador\n"
            "- RESPONSAV: Técnico Responsável pela Coleta\n"
            "- DATA_COLET: Data da Foto / Coleta em Campo\n"
            "- LATITUDE / LONGITUDE: Coordenadas Geográficas\n"
        )
        z.writestr('LEIA-ME_QGIS.txt', leia_me)

    return zip_buf.getvalue()


def export_to_geojson(pontos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera um GeoJSON FeatureCollection completo com atributos ricos.
    """
    features = []

    for p in pontos:
        lat = p.get('latitude')
        lng = p.get('longitude')
        if lat is None or lng is None:
            continue

        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (ValueError, TypeError):
            continue

        # Se houver polígono salvo, podemos utilizá-lo como geometria
        geom = None
        if p.get('poligono'):
            try:
                poly_json = json.loads(p['poligono']) if isinstance(p['poligono'], str) else p['poligono']
                if 'geometry' in poly_json:
                    geom = poly_json['geometry']
                elif 'type' in poly_json and 'coordinates' in poly_json:
                    geom = poly_json
            except Exception:
                pass

        if not geom:
            geom = {
                "type": "Point",
                "coordinates": [lng_f, lat_f]
            }

        properties = {
            "id": p.get('id'),
            "nome": p.get('nome'),
            "tipo": p.get('tipo'),
            "municipio": p.get('municipio'),
            "comunidade": p.get('comunidade'),
            "status_obra": p.get('status_obra') or p.get('status_beneficiario'),
            "beneficiario": p.get('beneficiario'),
            "area_telhado_m2": p.get('area_telhado'),
            "edital": p.get('edital'),
            "responsavel": p.get('responsavel'),
            "descricao": p.get('descricao'),
            "foto_url": p.get('foto_url'),
            "data_coleta": p.get('data_coleta'),
            "latitude": lat_f,
            "longitude": lng_f
        }

        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": properties
        })

    return {
        "type": "FeatureCollection",
        "name": "Agendha_Tecnologias_Agua",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features
    }


def export_to_kml(pontos: List[Dict[str, Any]]) -> str:
    """
    Gera arquivo KML para visualização no Google Earth, Avenza Maps e GPS.
    """
    kml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        '  <name>Pontos Agendha - Tecnologias de Água</name>',
        '  <description>Projetos de Convivência com o Semiárido - Território Itaparica</description>',
        '  <Style id="pontoCisterna">',
        '    <IconStyle>',
        '      <scale>1.1</scale>',
        '      <Icon><href>http://maps.google.com/mapfiles/ms/icons/blue-dot.png</href></Icon>',
        '    </IconStyle>',
        '  </Style>'
    ]

    for p in pontos:
        lat = p.get('latitude')
        lng = p.get('longitude')
        if lat is None or lng is None:
            continue

        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (ValueError, TypeError):
            continue

        nome = str(p.get('nome') or 'Sem Nome')
        tipo = str(p.get('tipo') or 'Tecnologia Social')
        muni = str(p.get('municipio') or 'N/I')
        comu = str(p.get('comunidade') or 'N/I')
        st = str(p.get('status_obra') or p.get('status_beneficiario') or 'N/I')
        benef = str(p.get('beneficiario') or 'N/I')
        area = str(p.get('area_telhado') or '0')
        foto = str(p.get('foto_url') or '')

        img_tag = f'<br/><img src="{foto}" width="300"/><br/>' if foto else ''

        desc = (
            f"<![CDATA["
            f"<b>Tipo:</b> {tipo}<br/>"
            f"<b>Município:</b> {muni}<br/>"
            f"<b>Comunidade:</b> {comu}<br/>"
            f"<b>Status da Obra:</b> {st}<br/>"
            f"<b>Beneficiário:</b> {benef}<br/>"
            f"<b>Área de Captação:</b> {area} m²<br/>"
            f"{img_tag}"
            f"]]>"
        )

        kml_lines.extend([
            '  <Placemark>',
            f'    <name>{nome}</name>',
            f'    <description>{desc}</description>',
            '    <styleUrl>#pontoCisterna</styleUrl>',
            '    <Point>',
            f'      <coordinates>{lng_f},{lat_f},0</coordinates>',
            '    </Point>',
            '  </Placemark>'
        ])

    kml_lines.extend([
        '</Document>',
        '</kml>'
    ])

    return '\n'.join(kml_lines)
