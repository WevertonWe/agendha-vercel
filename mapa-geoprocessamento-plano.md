# 🗺️ Plano Diretor: Modernização do SIG e Geoprocessamento Agendha

> **Objetivo:** Adequação profissional do mapa Agendha às demandas da Prefeitura e do trabalho de campo no **Território de Identidade Itaparica**, com foco em agricultura familiar, tecnologias de convivência com o Semiárido (Cisterna 16k L, Calçadão 52k L, Enxurrada, Barreiro) e integração plena com o **QGIS**.

---

## 🎯 Especificações Confirmadas pelo Usuário

1. **Formatos de Saída (Exportação Especializada):**
   - **Shapefile (.zip):** Pacote contendo `.shp`, `.shx`, `.dbf`, `.prj`, `.cpg` exigido pela Prefeitura e QGIS.
   - **GeoJSON (.geojson):** Para intercâmbio moderno com SIG web e QGIS sem truncamento de colunas.
   - **KML (.kml):** Para visualização rápida no Google Earth e GPS móvel.
   - **Excel (.xlsx):** Relatório tabular de acompanhamento.
   - **Interface:** Modal / Aba dedicada de Exportação para o usuário escolher o formato desejado.

2. **Ficha Técnica Agroecológica e Tecnologias de Água:**
   - **Tecnologia:** Cisterna de Placa (16.000 L - 1ª Água), Cisterna Calçadão (52.000 L - 2ª Água), Cisterna Enxurrada (52.000 L), Barreiro Trincheira, Barraginha, Poço Tubular, Quintal Agroecológico.
   - **Localização:** Coordenadas (Lat/Lng), Município e Comunidade Rural.
   - **Captação & Capacidade:** Área do telhado/calçadão de captação (m²) e volume em litros.
   - **Status da Obra:** *Diagnóstico*, *Escavação*, *Construção*, *Concluída/Em uso*, *Necessita Reforma*.
   - **Projeto / Edital:** Identificação do convênio/edital financiador (ex: Água que Alimenta, BNDES, MDS).
   - **Beneficiário:** Nome completo, documento (CPF/NIS).
   - **Mídia:** Fotos do local com leitura automática de metadados EXIF GPS (fotos tiradas no celular ou Timestamp Camera).
   - **Observações:** Anotações técnicas de campo.

3. **Camada Territorial Oficial:**
   - Delimitação vetorial oficial do **Território de Identidade Itaparica (Bahia)**: Paulo Afonso, Glória, Chorrochó, Macururé, Rodelas e Abaré (obtido via malha oficial IBGE).

---

## 🏗️ Tarefas de Implementação

### Tarefa 1: Modal e Motor de Exportação GIS (Shapefile .zip, GeoJSON, KML)
- Criar endpoint `/api/mapa/exportar` com suporte a query params (`formato=shapefile|geojson|kml|excel`).
- Gerador de Shapefile em Python (utilizando `pyshp` sem dependência de binários pesados C/C++, 100% compatível com Vercel).
- Inclusão de projeção `.prj` em **SIRGAS 2000 (EPSG:4674)** e **WGS 84 (EPSG:4326)** e `.cpg` com UTF-8 para manter acentuação correta no QGIS.
- Modal de exportação no frontend com opções claras de download.

### Tarefa 2: Formulário Especializado de Tecnologias de Água & Leitura EXIF de Fotos
- Atualizar o modal "Novo Ponto" com campos dedicados:
  - Tipo de Tecnologia hídrica (select dinâmico com cores e ícones específicos).
  - Município (lista dos municípios do Território Itaparica) e Comunidade.
  - Área de Captação (m² do telhado ou calçadão).
  - Status da Obra (badge visual: Diagnóstico, Construção, Concluída).
  - Projeto / Edital.
  - Leitor automático de EXIF GPS no JavaScript: ao selecionar a foto (Timestamp ou câmera), preencher Lat e Lng automaticamente se a imagem tiver geotagging.

### Tarefa 3: Camada Vetorial do Território Itaparica no Mapa
- Obtenção da malha municipal oficial IBGE dos 6 municípios do Território Itaparica.
- Adicionar camada no controle de camadas (`L.geoJSON`) com estilo cartográfico profissional (contornos bem definidos, preenchimento suave translúcido para não tampar estradas/açudes).
- Ferramenta de zoom automático para o território.

---

## 🔍 Critérios de Aceite e Verificação
1. **QGIS:** O `.zip` exportado deve ser descompactado e arrastado para dentro do QGIS sem nenhum aviso de projeção inválida ou erro na tabela de atributos DBF.
2. **Foto GPS:** Ao carregar uma foto com geolocalização, os campos de latitude e longitude devem ser preenchidos instantaneamente.
3. **Território Itaparica:** A malha dos municípios deve aparecer perfeitamente alinhada sobre a base do OpenStreetMap e Satélite.
