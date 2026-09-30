/**
 * ==============================================================================
 * 🔍 AUDITOR SIGATER: VISITAS TÉCNICAS AVALIATIVAS (MÊS 7 / JULHO DE 2026)
 * ==============================================================================
 * Atividade: # 67119 (25º 7/2026 - Ano 3) - Visita Técnica Avaliativa (2 h)
 * Meta Coletum: 281 registros | Lançados no SIGATER: ~277 | Pendentes: ~4
 *
 * Instruções de Uso:
 * 1. No SIGATER, abra a tela "LISTAGEM - EXECUÇÕES" da atividade # 67119 (Julho/2026).
 *    (Basta clicar no botão [AE] da coluna 25º 7/2026 na tela de Planejamento).
 * 2. Abra o Console do navegador (pressione F12 e clique na aba "Console").
 * 3. Cole todo este código e aperte [ENTER].
 * 4. O auditor lerá todas as execuções e indicará exatamente quem são os 4 pendentes!
 * ==============================================================================
 */
(async function() {
    console.clear();
    console.log('%c🚀 AUDITANDO VISITAS TÉCNICAS AVALIATIVAS (JULHO/2026 - 281 REGISTROS COLETUM)...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');

    // 1. Base oficial de dados extraída diretamente do Coletum (Formulário 41981)
    const coletumVisitas = [
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Mariana Gomes da Silva",
    "cpf": "071.287.525-52",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "31/07/2026",
    "coletum_id": "31657.165"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Sivanilda Gomes da Silva",
    "cpf": "864.339.855-13",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "31/07/2026",
    "coletum_id": "31657.164"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Junilson Santos Lima",
    "cpf": "034.581.415-02",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "31/07/2026",
    "coletum_id": "31657.163"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gislene Reis de Menezes",
    "cpf": "063.221.125-38",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "31/07/2026",
    "coletum_id": "27309.447"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Elida Suenia Cerqueira dos Santos",
    "cpf": "026.503.365-95",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "31/07/2026",
    "coletum_id": "27309.446"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Débora Ferreira da Silva",
    "cpf": "058.118.435-18",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "31/07/2026",
    "coletum_id": "27309.445"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jilsomar Gomes da Cruz",
    "cpf": "059.135.025-40",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "30/07/2026",
    "coletum_id": "27309.444"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Salete Maria dos Santos",
    "cpf": "285.342.788-90",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "30/07/2026",
    "coletum_id": "27309.443"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Joseane Ferreira da Silva",
    "cpf": "047.204.295-56",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "30/07/2026",
    "coletum_id": "27309.442"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Luciana Ferreira da Silva",
    "cpf": "066.303.415-97",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "30/07/2026",
    "coletum_id": "27309.441"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "EDENILSON GONÇALVES DA SILVA",
    "cpf": "066.558.795-31",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "31/07/2026",
    "coletum_id": "31616.126"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "TEREZA DO NASCIMENTO SOUZA",
    "cpf": "006.920.995-22",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "31/07/2026",
    "coletum_id": "31616.125"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "REGINA GONÇALVES DA SILVA",
    "cpf": "033.849.015-92",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "31/07/2026",
    "coletum_id": "31616.124"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARCELO DO NASCIMENTO SILVA",
    "cpf": "717.760.264-03",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "31/07/2026",
    "coletum_id": "31616.127"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Leide Daiane Silva Maia",
    "cpf": "081.578.295-00",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "31/07/2026",
    "coletum_id": "31648.161"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Clescineide Oliveira",
    "cpf": "028.213.355-04",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "31/07/2026",
    "coletum_id": "31646.120"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Silvia Gomes Xavier Conceição",
    "cpf": "024.679.215-90",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "31/07/2026",
    "coletum_id": "31646.119"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Marcileide Fagundo do Nascimento",
    "cpf": "063.466.385-21",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "31/07/2026",
    "coletum_id": "31646.118"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Sinalia Maria Oliveira do Nascimento",
    "cpf": "103.722.845-66",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "30/07/2026",
    "coletum_id": "31646.117"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Luzia Oliveira do Nascimento",
    "cpf": "067.277.654-56",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "30/07/2026",
    "coletum_id": "31646.116"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Jociane Lucas da Silva",
    "cpf": "084.536.665-39",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "30/07/2026",
    "coletum_id": "31646.115"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MERIAN CALDAS BARROS",
    "cpf": "042.286.242-86",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "31/07/2026",
    "coletum_id": "26510.582"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "GISLANE BARBOSA XAVIER MACIEL NEVES",
    "cpf": "858.389.585-61",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "31/07/2026",
    "coletum_id": "26510.581"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "RANIELE SOARES MACIEL",
    "cpf": "858.312.875-80",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "31/07/2026",
    "coletum_id": "26510.583"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "QUELIANE MARQUES DA SILVA",
    "cpf": "067.743.865-63",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "30/07/2026",
    "coletum_id": "26510.579"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARIA JULIANA DA SILVA",
    "cpf": "858.316.555-63",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "30/07/2026",
    "coletum_id": "26510.577"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "GISELE MARIA DOS SANTOS  FELICIANO",
    "cpf": "863.819.585-02",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "30/07/2026",
    "coletum_id": "26510.578"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LUCAS PEREIRA DE ALMEIDA",
    "cpf": "864.818.635-89",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "30/07/2026",
    "coletum_id": "26510.580"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Ildivania Mendes dos Santos",
    "cpf": "861.218.465-77",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31648.156"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Joelson dos Santos",
    "cpf": "053.273.565-07",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "31/07/2026",
    "coletum_id": "31648.160"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Janice Félix Maciel",
    "cpf": "058.084.085-98",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "31/07/2026",
    "coletum_id": "31648.159"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Roberta Félix Maia Santos",
    "cpf": "089.471.735-92",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31648.158"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Robéria Félix Maia",
    "cpf": "860.538.045-41",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31648.157"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JESICA MACIEL SILVA SANTOS",
    "cpf": "056.647.685-17",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "30/07/2026",
    "coletum_id": "31616.123"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA DA SILVA BARBOSA",
    "cpf": "075.722.455-52",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "30/07/2026",
    "coletum_id": "31616.121"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "EDIVANIA SILVA BARBOSA",
    "cpf": "079.918.185-43",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "30/07/2026",
    "coletum_id": "31616.120"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA DE CARVALHO JESUS",
    "cpf": "070.683.095-42",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "30/07/2026",
    "coletum_id": "31616.122"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Jenivaldo Soares da Silva",
    "cpf": "005.355.935-54",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31657.159"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Maria Izabel Pereira de Andrade",
    "cpf": "440.844.238-07",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31657.160"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Rosimeire Rodrigues Barbosa",
    "cpf": "010.850.055-18",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31657.161"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Josineide da Cruz",
    "cpf": "027.981.885-80",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "30/07/2026",
    "coletum_id": "31657.162"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LILIANE DA CONCEIÇÃO",
    "cpf": "077.528.395-90",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "29/07/2026",
    "coletum_id": "26510.576"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JAIANE DOS SANTOS BEZERRA",
    "cpf": "858.312.825-11",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "29/07/2026",
    "coletum_id": "26510.574"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Valdete Oliveira da Silva",
    "cpf": "024.863.985-46",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "29/07/2026",
    "coletum_id": "31648.155"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Alayne Silva Mendes",
    "cpf": "056.301.215-37",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31648.154"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Joselia Maria Maia",
    "cpf": "014.831.555-01",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31648.153"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josiane Maria Maia",
    "cpf": "048.065.195-70",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31648.152"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "FABIANA FERREIRA DE SOUZA",
    "cpf": "056.622.665-06",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "29/07/2026",
    "coletum_id": "26510.575"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "LUANA SOUZA MAIA",
    "cpf": "105.928.095-79",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "29/07/2026",
    "coletum_id": "31616.119"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ELENILDA SOUZA MAIA",
    "cpf": "100.796.665-31",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "29/07/2026",
    "coletum_id": "31616.117"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ELIDIA BARBOSA DA SILVA",
    "cpf": "000.227.935-50",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "29/07/2026",
    "coletum_id": "31616.116"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ELENILZA SOUZA MAIA",
    "cpf": "083.080.285-19",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "29/07/2026",
    "coletum_id": "31616.118"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Jailda Vieira da Conceição",
    "cpf": "049.388.215-40",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "29/07/2026",
    "coletum_id": "31646.113"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Derisson Santos Silva",
    "cpf": "063.645.335-90",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "29/07/2026",
    "coletum_id": "31646.112"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Geovana Gomes Xavier Gama",
    "cpf": "098.775.225-19",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "29/07/2026",
    "coletum_id": "31646.111"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Rafaela Maria Oliveira do Nascimento",
    "cpf": "081.212.395-67",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "29/07/2026",
    "coletum_id": "31646.110"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Antônio Ribeiro da Silva",
    "cpf": "006.139.625-75",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31657.158"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Julio Maria Gomes Lima",
    "cpf": "039.800.195-27",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31657.157"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Maria da Socorro Araújo da Silva",
    "cpf": "008.077.135-11",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31657.156"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Jacimara Félix da Silva",
    "cpf": "067.042.165-02",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "29/07/2026",
    "coletum_id": "31657.155"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Amanda Suylla Alves de Carvalho",
    "cpf": "071.500.385-22",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "28/07/2026",
    "coletum_id": "31648.151"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edivany dos Santos Silva",
    "cpf": "861.228.525-97",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "28/07/2026",
    "coletum_id": "31648.150"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Sérgio Oliveira Montes",
    "cpf": "075.232.135-88",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "28/07/2026",
    "coletum_id": "31648.149"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Neidinalva da Conceição Montes",
    "cpf": "087.647.455-54",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "28/07/2026",
    "coletum_id": "31648.148"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Jocelma Maria dos Santos",
    "cpf": "859.143.865-51",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "27/07/2026",
    "coletum_id": "31648.147"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Jose Uilton dos Santos Silva",
    "cpf": "084.206.715-92",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "27/07/2026",
    "coletum_id": "31648.146"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josivânia dos Santos Silva",
    "cpf": "865.287.215-56",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "27/07/2026",
    "coletum_id": "31648.145"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Marisa Santos do Nascimento Silva",
    "cpf": "005.412.075-63",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "28/07/2026",
    "coletum_id": "31646.109"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Jaqueline da Silva",
    "cpf": "360.846.068-30",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "28/07/2026",
    "coletum_id": "31646.108"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Ediva Ferreira da Silva",
    "cpf": "006.161.055-09",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "28/07/2026",
    "coletum_id": "27309.440"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Marivaldo Silva de Souza",
    "cpf": "060.312.175-62",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "28/07/2026",
    "coletum_id": "27309.439"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Pascoal Quinto dos Santos",
    "cpf": "007.813.995-30",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "28/07/2026",
    "coletum_id": "27309.438"
  },
  {
    "tecnico": "Wandisson Santos de jesus",
    "beneficiario": "Hagamenon França do Vale",
    "cpf": "035.818.438-03",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "28/07/2026",
    "coletum_id": "27309.437"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "BENEDITA ALVES LOPES MAIA",
    "cpf": "002.980.955-05",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "28/07/2026",
    "coletum_id": "31616.115"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ALAIDE BAHIA DA CRUZ",
    "cpf": "107.349.515-90",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "28/07/2026",
    "coletum_id": "31616.113"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JOÃO ADRIANO SIMOES",
    "cpf": "015.691.025-03",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "28/07/2026",
    "coletum_id": "31616.112"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JILDENOR DIAS BARBOSA DOS SANTOS",
    "cpf": "040.336.255-50",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "28/07/2026",
    "coletum_id": "31616.114"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Rivonilson Ramos da Cruz",
    "cpf": "291.849.058-08",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "28/07/2026",
    "coletum_id": "31657.154"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Alex Sandro Gomes Ramos",
    "cpf": "049.408.355-70",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "28/07/2026",
    "coletum_id": "31657.153"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Joseval Rodrigues da Fonseca",
    "cpf": "154.121.098-02",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "28/07/2026",
    "coletum_id": "31657.152"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Joice Gomes Ramos",
    "cpf": "861.218.105-48",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "28/07/2026",
    "coletum_id": "31657.151"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Rafaela da Silva Ramos",
    "cpf": "861.217.975-09",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "27/07/2026",
    "coletum_id": "31657.150"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Elaine Jorge da Silva Rodrigues",
    "cpf": "135.479.428-10",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "27/07/2026",
    "coletum_id": "31657.149"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Risael Ramos da Cruz",
    "cpf": "057.513.425-93",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "27/07/2026",
    "coletum_id": "31657.148"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "DAINE VICENTE BEZERRA",
    "cpf": "067.592.585-17",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "27/07/2026",
    "coletum_id": "26510.568"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROSICLEIA TORQUATO DOS SANTOS",
    "cpf": "052.518.971-89",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "27/07/2026",
    "coletum_id": "26510.569"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROSITELMA TORQUATO DOS SANTOS",
    "cpf": "052.207.601-73",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "27/07/2026",
    "coletum_id": "26510.570"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "VALDIRENE LIMA DE  JESUS",
    "cpf": "091.912.815-71",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "27/07/2026",
    "coletum_id": "26510.571"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LUZIA TAVARES DA SILVA FERREIRA",
    "cpf": "082.913.275-99",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "24/07/2026",
    "coletum_id": "26510.573"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Sueli Silva dos Santos",
    "cpf": "070.168.545-07",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "27/07/2026",
    "coletum_id": "27309.436"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Nair Nogueira",
    "cpf": "020.194.595-90",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "27/07/2026",
    "coletum_id": "27309.435"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Genilda Silva dos Santos",
    "cpf": "087.611.655-14",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "27/07/2026",
    "coletum_id": "27309.434"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Fernanda Reis Santos Costa",
    "cpf": "072.055.615-58",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "27/07/2026",
    "coletum_id": "27309.433"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JIVALDO SIMOES",
    "cpf": "000.759.775-40",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "27/07/2026",
    "coletum_id": "31616.110"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "Amilton José Paiva da Silva",
    "cpf": "096.430.635-26",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "27/07/2026",
    "coletum_id": "31616.109"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "CLAUDEANE SOUZA OLIVEIRA",
    "cpf": "075.827.175-11",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "27/07/2026",
    "coletum_id": "31616.108"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADIMILSON SIMÕES DA SILVA",
    "cpf": "200.983.548-41",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "27/07/2026",
    "coletum_id": "31616.111"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Ana Patrícia do Nascimento Silva",
    "cpf": "864.300.025-60",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "27/07/2026",
    "coletum_id": "31646.107"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Simara Ribeiro do Nascimento",
    "cpf": "864.834.925-70",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "27/07/2026",
    "coletum_id": "31646.106"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "INIA SILVA NASCIMENTO",
    "cpf": "163.391.117-93",
    "comunidade": "Baixa Funda",
    "municipio": "Paulo Afonso",
    "data": "24/07/2026",
    "coletum_id": "26510.564"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "PATRICIA DA SILVA DE JESUS",
    "cpf": "499.649.298-89",
    "comunidade": "BAIXA FUNDA",
    "municipio": "Paulo Afonso",
    "data": "24/07/2026",
    "coletum_id": "26510.566"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROBERLANIA BEZERRA DA SILVA",
    "cpf": "104.081.794-73",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "23/07/2026",
    "coletum_id": "26510.558"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARIA VIVIANE DOS SANTOS ANDRADE",
    "cpf": "047.351.335-85",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "23/07/2026",
    "coletum_id": "26510.559"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JESSICA BARROS DE LIMA",
    "cpf": "099.244.865-44",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "23/07/2026",
    "coletum_id": "26510.560"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Agmar Fonseca Costa",
    "cpf": "035.773.595-10",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "23/07/2026",
    "coletum_id": "27309.432"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Marizete Rodrigues da Silva",
    "cpf": "070.275.935-05",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "23/07/2026",
    "coletum_id": "27309.431"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Joao Bispo de Oliveira",
    "cpf": "469.588.605-78",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "23/07/2026",
    "coletum_id": "27309.430"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Francisco Fonseca de Araujo",
    "cpf": "492.316.775-00",
    "comunidade": "Roçado",
    "municipio": "Chorrochó",
    "data": "23/07/2026",
    "coletum_id": "27309.429"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Carmen Andrea Ramos da Silva",
    "cpf": "009.724.565-89",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "22/07/2026",
    "coletum_id": "31648.141"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Josiane Lima Silva",
    "cpf": "862.059.985-21",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "22/07/2026",
    "coletum_id": "31648.140"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josafá da Cruz",
    "cpf": "299.164.128-20",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "22/07/2026",
    "coletum_id": "31648.139"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria José dos Santos",
    "cpf": "039.262.175-45",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "22/07/2026",
    "coletum_id": "31648.138"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Antonio do Nascimento Santos",
    "cpf": "891.234.845-00",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "22/07/2026",
    "coletum_id": "27309.428"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Daniele Ribeiro da Cruz",
    "cpf": "086.802.405-83",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "22/07/2026",
    "coletum_id": "27309.427"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Justino Alves Moreira",
    "cpf": "107.609.228-45",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "22/07/2026",
    "coletum_id": "27309.426"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "VANESSA DA CONCEIÇÃO SA",
    "cpf": "030.732.375-77",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "22/07/2026",
    "coletum_id": "26510.554"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "PATRICIA FERREIRA DOS SANTOS",
    "cpf": "031.106.775-12",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "22/07/2026",
    "coletum_id": "26510.555"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JOELMA PEREIRA MONTEIRO",
    "cpf": "026.321.565-21",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "22/07/2026",
    "coletum_id": "26510.556"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Pedro Henrique Pessoa Silva",
    "cpf": "055.852.335-80",
    "comunidade": "sansaite",
    "municipio": "Macururé",
    "data": "21/07/2026",
    "coletum_id": "31657.143"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Tamires Gomes e Silva Cruz",
    "cpf": "059.368.165-75",
    "comunidade": "sansaite",
    "municipio": "Macururé",
    "data": "21/07/2026",
    "coletum_id": "31657.142"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Iara Souza Lima",
    "cpf": "050.060.555-61",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31657.141"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Joelson da Cruz",
    "cpf": "040.557.755-98",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31657.140"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Maricelia Gomes da Cruz",
    "cpf": "001.225.945-41",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31657.139"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Karolayne da Cruz Barbosa",
    "cpf": "859.143.945-70",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31657.138"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Josilma da Cruz Barbosa",
    "cpf": "283.904.098-01",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "18/07/2026",
    "coletum_id": "31657.137"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Dojivaldo Gomes da Silva",
    "cpf": "861.218.425-80",
    "comunidade": "Sansaite",
    "municipio": "Macururé",
    "data": "18/07/2026",
    "coletum_id": "31657.136"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Adenilton Gomes da Silva",
    "cpf": "261.937.818-46",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "17/07/2026",
    "coletum_id": "31657.134"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Edvalto Gomes de Silva",
    "cpf": "808.126.275-04",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "17/07/2026",
    "coletum_id": "31657.133"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Zilda dos Santos Silva",
    "cpf": "121.612.275-05",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "21/07/2026",
    "coletum_id": "31648.137"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edvânia dos Santos Silva",
    "cpf": "860.764.785-78",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "21/07/2026",
    "coletum_id": "31648.136"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josineide Maria dos Santos",
    "cpf": "865.472.975-94",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "21/07/2026",
    "coletum_id": "31648.135"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Carmelita Ramos da Silva",
    "cpf": "014.909.945-21",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "21/07/2026",
    "coletum_id": "31648.134"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria dos Santos Silva",
    "cpf": "867.340.795-89",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31648.133"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Raniele Maria dos Santos Alves",
    "cpf": "867.346.295-97",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31648.132"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Franciele Alves Oliveira",
    "cpf": "121.840.155-98",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "20/07/2026",
    "coletum_id": "31648.131"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Analice Alves da Silva Santos",
    "cpf": "063.677.665-45",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "21/07/2026",
    "coletum_id": "31646.104"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Ronaldo Vieira da Silva",
    "cpf": "078.079.925-90",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "21/07/2026",
    "coletum_id": "31646.103"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Marcia Graciete da Silva",
    "cpf": "071.724.085-19",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "21/07/2026",
    "coletum_id": "31646.102"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Martinha Ferreira do Nascimento",
    "cpf": "029.318.365-16",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "21/07/2026",
    "coletum_id": "27309.425"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Daniel da Silva Carvalho",
    "cpf": "109.414.325-13",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "21/07/2026",
    "coletum_id": "27309.424"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Braz Conceição do Nascimento",
    "cpf": "931.777.475-04",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "21/07/2026",
    "coletum_id": "27309.423"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "DAIANE CAETANO DA SILVA",
    "cpf": "084.309.295-50",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "21/07/2026",
    "coletum_id": "26510.553"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARCOS ANTONIO MONTEIRO DE SA",
    "cpf": "956.994.495-15",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "21/07/2026",
    "coletum_id": "26510.551"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "CLAUDIONOR PEREIRA DA SILVA",
    "cpf": "937.421.425-34",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "21/07/2026",
    "coletum_id": "26510.549"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LARISSA DE SOUZA BARBOSA",
    "cpf": "858.385.965-54",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "21/07/2026",
    "coletum_id": "26510.548"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Marineide de Jesus Santos",
    "cpf": "054.960.535-52",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "20/07/2026",
    "coletum_id": "27309.422"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Milena de Jesus Santos",
    "cpf": "079.813.825-48",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "20/07/2026",
    "coletum_id": "27309.421"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gleuka Jéssia Alves de Andrade",
    "cpf": "525.585.828-52",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "20/07/2026",
    "coletum_id": "27309.420"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Alice Ribeiro do Nascimento Oliveira",
    "cpf": "001.749.815-54",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "20/07/2026",
    "coletum_id": "27309.419"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Daniele Barros da Silva",
    "cpf": "866.638.355-05",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "20/07/2026",
    "coletum_id": "31646.101"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Josiane Gomes Xavier Santos",
    "cpf": "048.231.185-10",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "20/07/2026",
    "coletum_id": "31646.99"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Francisco de Paula Bispo de Araújo",
    "cpf": "278.287.005-04",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "18/07/2026",
    "coletum_id": "31648.129"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Durval Florencio dos Santos",
    "cpf": "233.386.605-53",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "17/07/2026",
    "coletum_id": "31648.128"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Geisiane Santos Oliveira",
    "cpf": "004.566.365-36",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "18/07/2026",
    "coletum_id": "31648.130"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Ediane Maria de Araújo Lima",
    "cpf": "050.090.165-16",
    "comunidade": "Várzea da Ema",
    "municipio": "Macururé",
    "data": "17/07/2026",
    "coletum_id": "31648.127"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Elisangela Maria Araújo Lima",
    "cpf": "090.796.365-09",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "17/07/2026",
    "coletum_id": "31648.126"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Antônia vitória de jesus Moreira",
    "cpf": "868.599.215-01",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "17/07/2026",
    "coletum_id": "27309.418"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Vilma Pereira Dantas",
    "cpf": "016.261.435-79",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "17/07/2026",
    "coletum_id": "27309.417"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Jose da Silva",
    "cpf": "061.200.065-67",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "17/07/2026",
    "coletum_id": "27309.416"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gabriela Soares dos Santos",
    "cpf": "486.843.408-09",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "17/07/2026",
    "coletum_id": "27309.415"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JEOVANIA MACIEL SILVA SANTOS",
    "cpf": "087.816.505-31",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "17/07/2026",
    "coletum_id": "31616.104"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MAILANE CARVALHO DE JESUS",
    "cpf": "121.477.395-88",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "17/07/2026",
    "coletum_id": "31616.107"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADRIANA DA SILVA SANTOS",
    "cpf": "085.410.415-14",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "17/07/2026",
    "coletum_id": "31616.105"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA APARECIDA DA SILVA NASCIMENTO",
    "cpf": "067.436.885-17",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "17/07/2026",
    "coletum_id": "31616.106"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARIA DE LOURDES CAVALCANTE DE ARAUJO",
    "cpf": "009.644.425-82",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "17/07/2026",
    "coletum_id": "26510.545"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MANOEL MESSIAS PEREIRA MAIA",
    "cpf": "548.978.315-04",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "17/07/2026",
    "coletum_id": "26510.546"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Aparecida Nascimento Barros",
    "cpf": "002.966.065-37",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "17/07/2026",
    "coletum_id": "31646.98"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Gislane Vieira Silva Xavier",
    "cpf": "080.573.125-30",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "17/07/2026",
    "coletum_id": "31646.97"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Josileide Nascimento Ribeiro",
    "cpf": "028.646.525-60",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "17/07/2026",
    "coletum_id": "31646.96"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Jeane do Nascimento Ribeiro",
    "cpf": "048.505.705-00",
    "comunidade": "Brejo do Burgo",
    "municipio": "Glória",
    "data": "17/07/2026",
    "coletum_id": "31646.95"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA DO SOCORRO BARBOSA SANTOS",
    "cpf": "005.497.615-43",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "16/07/2026",
    "coletum_id": "31616.102"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA GOMES MOURA DO SOCORRO",
    "cpf": "007.779.715-93",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "16/07/2026",
    "coletum_id": "31616.101"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "RENATO DE JESUS SILVA",
    "cpf": "089.423.945-74",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "16/07/2026",
    "coletum_id": "31616.100"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "CEZAR ANTONIO DOS SANTOS",
    "cpf": "939.233.685-34",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "16/07/2026",
    "coletum_id": "31616.103"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edleuza Alves dos Santos",
    "cpf": "069.508.605-79",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "16/07/2026",
    "coletum_id": "31648.125"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edinalva Alves dos Santos",
    "cpf": "861.228.485-65",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "16/07/2026",
    "coletum_id": "31648.124"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edinaide Alves dos Santos",
    "cpf": "084.512.095-64",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "16/07/2026",
    "coletum_id": "31648.123"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "SANDRA MARIA DA SILVA",
    "cpf": "041.195.795-30",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "16/07/2026",
    "coletum_id": "26510.542"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARIA NILZA DOS SANTOS NASCIMENTO",
    "cpf": "068.237.615-98",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "16/07/2026",
    "coletum_id": "26510.543"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "EDILENE MARTINS DA SILVA",
    "cpf": "083.696.975-85",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "16/07/2026",
    "coletum_id": "26510.544"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARINEIDE LIMA SANTOS",
    "cpf": "021.455.175-02",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "16/07/2026",
    "coletum_id": "26510.547"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Ana Carla Santos da Silva",
    "cpf": "067.389.725-71",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "16/07/2026",
    "coletum_id": "27309.414"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Américo Marques Ramos",
    "cpf": "469.361.815-20",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "16/07/2026",
    "coletum_id": "27309.413"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Manoel Teixeira dos Santos",
    "cpf": "639.034.234-91",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "16/07/2026",
    "coletum_id": "27309.412"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Adenilson Gomes da Silva",
    "cpf": "000.571.455-98",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "16/07/2026",
    "coletum_id": "31657.132"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Eliane Gomes da Costa",
    "cpf": "063.846.795-07",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "16/07/2026",
    "coletum_id": "31657.131"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Edenice Maria dos Santos Feliz",
    "cpf": "961.287.805-63",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "16/07/2026",
    "coletum_id": "31657.130"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Alecia Maria Barbosa Lima",
    "cpf": "071.844.075-71",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "09/07/2026",
    "coletum_id": "31657.128"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Dilma Marina Alves da Silva Gomes",
    "cpf": "005.976.875-44",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "09/07/2026",
    "coletum_id": "31657.127"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Jovelina dos Santos",
    "cpf": "074.029.395-88",
    "comunidade": "Riacho dos caldeirões",
    "municipio": "Macururé",
    "data": "13/07/2026",
    "coletum_id": "31648.122"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Eliete Alves dos Santos",
    "cpf": "858.792.855-45",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "13/07/2026",
    "coletum_id": "31648.121"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Jaiane Rodrigues Pereira",
    "cpf": "125.243.885-06",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "13/07/2026",
    "coletum_id": "31648.120"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Luciano Mendes de Araujo",
    "cpf": "804.428.625-04",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "13/07/2026",
    "coletum_id": "27309.411"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Geane Mendes dos Santos",
    "cpf": "024.864.025-94",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "13/07/2026",
    "coletum_id": "27309.410"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Dejanira dos santos de Oliveira",
    "cpf": "001.547.235-33",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "13/07/2026",
    "coletum_id": "27309.409"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "MARCIA MARIA PEREIRA DE SOUZA",
    "cpf": "858.387.715-77",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "13/07/2026",
    "coletum_id": "26510.541"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JOSE FABIO FERREIRA FERNANDES",
    "cpf": "063.954.193-31",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "13/07/2026",
    "coletum_id": "31616.98"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "CARLEUZA DA CRUZ DOS SANTOS",
    "cpf": "050.062.535-25",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "13/07/2026",
    "coletum_id": "31616.97"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "DULCINEIA DO NASCIMENTO BARBALHO",
    "cpf": "136.258.828-84",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "13/07/2026",
    "coletum_id": "31616.99"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Santos Silva Ribeiro",
    "cpf": "102.622.325-37",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "13/07/2026",
    "coletum_id": "31646.94"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Jaqueline Ribeiro de Souza",
    "cpf": "858.788.085-36",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "13/07/2026",
    "coletum_id": "31646.93"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Luana Gomes Xavier Vieira",
    "cpf": "024.553.295-18",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "13/07/2026",
    "coletum_id": "31646.92"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Geronimo André Sobrinho",
    "cpf": "017.296.555-13",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "13/07/2026",
    "coletum_id": "31646.91"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Eduarda Rodrigues Silva Gimenes",
    "cpf": "859.165.615-63",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "11/07/2026",
    "coletum_id": "31648.119"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Adailton Gomes Reis",
    "cpf": "023.898.155-02",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "11/07/2026",
    "coletum_id": "31648.118"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "José Raimundo Antonio da Silva",
    "cpf": "755.252.405-72",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "11/07/2026",
    "coletum_id": "31648.117"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Rigoberto Rodrigues Varjão",
    "cpf": "050.090.155-44",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "11/07/2026",
    "coletum_id": "31648.116"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Ana Paula Maria dos Santos",
    "cpf": "088.534.385-92",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "10/07/2026",
    "coletum_id": "31648.115"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Antonio Pereira Maia Junior",
    "cpf": "865.417.585-06",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "10/07/2026",
    "coletum_id": "31648.114"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Tamiris dos Santos Silva",
    "cpf": "126.110.805-18",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "10/07/2026",
    "coletum_id": "31648.113"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gilvane Araujo do Nascimento",
    "cpf": "042.144.465-77",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "10/07/2026",
    "coletum_id": "27309.408"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Alciene Araujo de Oliveira",
    "cpf": "024.100.045-98",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "10/07/2026",
    "coletum_id": "27309.407"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Eliane Alves de Oliveira",
    "cpf": "030.039.095-50",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "10/07/2026",
    "coletum_id": "27309.406"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Beatriz Soares Damasceno",
    "cpf": "087.373.625-77",
    "comunidade": "São José",
    "municipio": "Chorrochó",
    "data": "10/07/2026",
    "coletum_id": "27309.405"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "GILBERTO DIAS DOS SANTOS",
    "cpf": "007.919.225-45",
    "comunidade": "LAGOA DO JOSE ALVES",
    "municipio": "Abaré",
    "data": "10/07/2026",
    "coletum_id": "31616.95"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "RENATA BARBOSA DA SILVA",
    "cpf": "084.365.185-78",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "10/07/2026",
    "coletum_id": "31616.96"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "IVETE LIMA DE SÁ",
    "cpf": "858.388.285-10",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "10/07/2026",
    "coletum_id": "26510.538"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ANA PAULA FERREIRA DOS SANTOS",
    "cpf": "099.652.175-56",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "10/07/2026",
    "coletum_id": "26510.539"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROSEANE  SOARES DA SILVA",
    "cpf": "022.187.875-04",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "10/07/2026",
    "coletum_id": "26510.540"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "GIOVANA SOUZA IZIDIO",
    "cpf": "866.898.975-83",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "10/07/2026",
    "coletum_id": "26510.536"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JOSEFA FERREIRA DA SILVA",
    "cpf": "074.248.425-44",
    "comunidade": "LAGOA GRANDE",
    "municipio": "Paulo Afonso",
    "data": "09/07/2026",
    "coletum_id": "26510.537"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Roberta Ribeiro da Silva",
    "cpf": "103.628.365-82",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "10/07/2026",
    "coletum_id": "31646.90"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maiara de Barros Teixeira",
    "cpf": "100.082.235-48",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "10/07/2026",
    "coletum_id": "31646.89"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Adeilma Maria da Silva",
    "cpf": "031.342.625-25",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "10/07/2026",
    "coletum_id": "31646.88"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Rafaela dos Santos Maia",
    "cpf": "084.412.215-70",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "09/07/2026",
    "coletum_id": "31648.112"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Meirelaine de Lima",
    "cpf": "110.664.555-38",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "09/07/2026",
    "coletum_id": "31648.111"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Liedson Andrade Maciel",
    "cpf": "096.067.305-90",
    "comunidade": "Minador",
    "municipio": "Macururé",
    "data": "09/07/2026",
    "coletum_id": "31648.110"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "GILDEVANDRO BARBOSA DE SOUZA",
    "cpf": "072.056.395-06",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "09/07/2026",
    "coletum_id": "31616.94"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JAINE MACIEL SILVA SANTOS",
    "cpf": "095.850.085-13",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "09/07/2026",
    "coletum_id": "31616.91"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "IONE BARBOSADE SOUZA",
    "cpf": "084.033.525-30",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "09/07/2026",
    "coletum_id": "31616.92"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA ANUNCIADA BARBOSA DE CARVALHO NETA",
    "cpf": "867.807.035-83",
    "comunidade": "ALTO VERMELHO",
    "municipio": "Abaré",
    "data": "09/07/2026",
    "coletum_id": "31616.93"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Silvania Ribeiro do Nascimento",
    "cpf": "019.187.365-96",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "09/07/2026",
    "coletum_id": "31646.87"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Vanessa Ribeiro Barbosa Silva",
    "cpf": "045.565.765-39",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "09/07/2026",
    "coletum_id": "31646.86"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Laiane Nascimento Mota",
    "cpf": "084.820.065-92",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "09/07/2026",
    "coletum_id": "31646.85"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Divaneide Ribeiro Nascimento Feitiza",
    "cpf": "054.959.295-43",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "09/07/2026",
    "coletum_id": "31646.84"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Vitor Pereira Dantas",
    "cpf": "002.520.365-73",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "09/07/2026",
    "coletum_id": "27309.404"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Roseane Teixeira Alves",
    "cpf": "053.178.235-28",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "09/07/2026",
    "coletum_id": "27309.403"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Luiz Teixeira Alves",
    "cpf": "959.678.005-06",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "09/07/2026",
    "coletum_id": "27309.402"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria de Lourdes Teixeira dos Santos",
    "cpf": "078.537.665-80",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "09/07/2026",
    "coletum_id": "27309.401"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Luciana Oliveira Alves Santos",
    "cpf": "043.730.485-09",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "31648.109"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Jose Cassimiro de Oliveira",
    "cpf": "512.887.375-72",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "31648.108"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "João Alves da Silva",
    "cpf": "945.759.915-20",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "31648.107"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Adriana Cerqueira dos Santos",
    "cpf": "112.829.285-89",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "31648.106"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Rosenilde Oliveira da Silva",
    "cpf": "015.134.575-94",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "31648.105"
  },
  {
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Anailma de Oliveira Pires Martins",
    "cpf": "270.674.458-84",
    "comunidade": "Várzea da Ema",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "31648.104"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jadenice Tolêdo dos Santos Simões",
    "cpf": "003.133.995-65",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "27309.400"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Elisangela Alves dos Santos",
    "cpf": "053.206.715-04",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "27309.399"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jilson Gabriel Alves do Nascimento",
    "cpf": "087.556.675-89",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "27309.398"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Josélia Pereira dos Santos",
    "cpf": "024.729.435-71",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "08/07/2026",
    "coletum_id": "27309.397"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "SILEIDE IZIDORIO DE MELO",
    "cpf": "071.612.135-25",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "08/07/2026",
    "coletum_id": "26510.534"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ISMAILDE DE SOUZA SILVA",
    "cpf": "866.008.025-45",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "08/07/2026",
    "coletum_id": "26510.533"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "GLEISIANE BARROS DE LIMA",
    "cpf": "099.243.995-79",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "08/07/2026",
    "coletum_id": "26510.535"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "RIZADALVA ALVES DOS SANTOS",
    "cpf": "005.603.415-63",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "08/07/2026",
    "coletum_id": "31616.89"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "INACIO MARTINS DE MORAIS",
    "cpf": "045.175.515-47",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "08/07/2026",
    "coletum_id": "31616.88"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "EDILEIDE IRENE DOS SANTOS",
    "cpf": "031.279.895-47",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "08/07/2026",
    "coletum_id": "31616.87"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "FABIO JUNIOR DE MENEZES GOMES",
    "cpf": "035.897.835-16",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "08/07/2026",
    "coletum_id": "31616.90"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Lucivania Rosa de Mota",
    "cpf": "022.881.975-01",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "08/07/2026",
    "coletum_id": "31646.83"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Maiara Arcanja Bernardo Silva",
    "cpf": "070.700.825-50",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "08/07/2026",
    "coletum_id": "31657.124"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Clecia Aparecida Gomes da Silva",
    "cpf": "070.372.505-03",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "08/07/2026",
    "coletum_id": "31657.125"
  },
  {
    "tecnico": "Migson Brayne Pamponet da Silva",
    "beneficiario": "Alderiva Gomes da Silva",
    "cpf": "033.081.025-10",
    "comunidade": "Serra do Tonan",
    "municipio": "Macururé",
    "data": "08/07/2026",
    "coletum_id": "31657.126"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROSIMAR SANTOS DA SILVA",
    "cpf": "083.440.364-10",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "07/07/2026",
    "coletum_id": "26510.532"
  },
  {
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ELAINE ANA DA SILVA",
    "cpf": "858.316.535-10",
    "comunidade": "CASA DE PEDRA",
    "municipio": "Paulo Afonso",
    "data": "07/07/2026",
    "coletum_id": "26510.531"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "VANESSA DE CARVALHO SANTOS",
    "cpf": "069.302.825-45",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "07/07/2026",
    "coletum_id": "31616.85"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JÉSSICA THAÍS SOARES DA SILVA",
    "cpf": "065.420.525-69",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "07/07/2026",
    "coletum_id": "31616.84"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADENILSA LAURINDA DA SILVA",
    "cpf": "006.122.325-57",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "07/07/2026",
    "coletum_id": "31616.86"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jilaene Alves dos Santos",
    "cpf": "030.777.355-80",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "27309.396"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria de Lourdes Alves da Silva",
    "cpf": "754.602.035-20",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "27309.395"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Sebastiana Alves Barbalho",
    "cpf": "425.442.968-10",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "27309.394"
  },
  {
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Lucivânia Alves dos Santos",
    "cpf": "053.386.995-16",
    "comunidade": "Golf",
    "municipio": "Chorrochó",
    "data": "07/07/2026",
    "coletum_id": "27309.393"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADRIANA DOS SANTOS DE JESUS",
    "cpf": "004.716.465-47",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "06/07/2026",
    "coletum_id": "31616.81"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "IANDRA DO NASCIMENTO SANTOS",
    "cpf": "045.487.375-10",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "06/07/2026",
    "coletum_id": "31616.82"
  },
  {
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MICHELLY DA SILVA CRUZ",
    "cpf": "111.572.465-75",
    "comunidade": "ALDEIA TUXI",
    "municipio": "Abaré",
    "data": "06/07/2026",
    "coletum_id": "31616.83"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Alecilda Rodrigues Vieira",
    "cpf": "050.084.785-16",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "06/07/2026",
    "coletum_id": "31646.82"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Lucimara Vieira Ribeiro",
    "cpf": "555.604.742-15",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "06/07/2026",
    "coletum_id": "31646.81"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Luciana Vieira Ribeiro Barbosa",
    "cpf": "015.753.712-94",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "06/07/2026",
    "coletum_id": "31646.80"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maiara Ribeiro Gama",
    "cpf": "112.392.505-41",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "03/07/2026",
    "coletum_id": "31646.79"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Michele Ribeiro Gama",
    "cpf": "865.011.895-00",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "03/07/2026",
    "coletum_id": "31646.78"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Adezuilma da Silva",
    "cpf": "002.977.505-18",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "03/07/2026",
    "coletum_id": "31646.77"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Thaynara Silva Barros",
    "cpf": "101.686.065-00",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "01/07/2026",
    "coletum_id": "31646.76"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maira Maria de Barros Teixeira",
    "cpf": "076.291.405-09",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "01/07/2026",
    "coletum_id": "31646.75"
  },
  {
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Mônica Maria Ribeiro Gama",
    "cpf": "003.000.025-48",
    "comunidade": "Pankarare",
    "municipio": "Glória",
    "data": "01/07/2026",
    "coletum_id": "31646.74"
  }
];

    function normalizar(txt) {
        if (!txt) return '';
        return String(txt).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().trim();
    }

    function cleanCpf(cpf) {
        if (!cpf) return '';
        return String(cpf).replace(/\D/g, '');
    }

    function similaridade(s1, s2) {
        const n1 = normalizar(s1);
        const n2 = normalizar(s2);
        if (n1 === n2) return 1.0;
        if (!n1 || !n2) return 0.0;
        if (n1.includes(n2) || n2.includes(n1)) return 0.92;
        const p1 = n1.split(' '), p2 = n2.split(' ');
        if (p1.length >= 2 && p2.length >= 2) {
            if (p1[0] === p2[0] && p1[p1.length - 1] === p2[p2.length - 1]) return 0.88;
        }
        const set1 = new Set(p1), set2 = new Set(p2);
        const inter = new Set([...set1].filter(x => set2.has(x)));
        return inter.size / new Set([...set1, ...set2]).size;
    }

    // Remove painel anterior se existir
    const antigo = document.getElementById('painelAuditoriaVisitas7');
    if (antigo) antigo.remove();

    // 2. Identificação das execuções na tela do SIGATER
    const linksLupa = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"], table tbody tr a'));
    const urlsExecucoes = Array.from(new Set(
        linksLupa.map(a => a.href).filter(h => h && (h.includes('/read/') || h.includes('cronograma_execucao/read')))
    ));

    // Se estiver na tela do Cronograma e não na tela de execuções
    if (urlsExecucoes.length === 0) {
        const divAviso = document.createElement('div');
        divAviso.id = 'painelAuditoriaVisitas7';
        divAviso.style.cssText = 'position:fixed;bottom:20px;right:20px;width:520px;background:#181a20;color:#fff;padding:22px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
        divAviso.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:14px;">
                <strong style="color:#00bcd4;font-size:16px;">📌 Tela de Cronograma Detectada</strong>
                <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
            </div>
            <p style="margin:0 0 12px 0;color:#ddd;line-height:1.5;">
                Você está na tela geral de planejamento.<br>
                Para auditar os lançamentos de <strong>Julho/2026 (25º - # 67119)</strong>:
            </p>
            <div style="background:#22252e;padding:12px;border-radius:8px;border-left:4px solid #00e676;margin-bottom:14px;">
                👉 <strong>Clique no botão [AE]</strong> ou no número <strong>277</strong> abaixo da coluna <strong>25º 7/2026</strong> para abrir a lista de execuções.
            </div>
            <p style="color:#aaa;font-size:12px;margin:0 0 14px 0;">
                Assim que a listagem abrir, cole este código novamente no Console (F12)!
            </p>
            <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="width:100%;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">
                Entendido!
            </button>
        `;
        document.body.appendChild(divAviso);
        return;
    }

    console.log(`📋 Total de execuções detectadas na página do SIGATER: ${urlsExecucoes.length}`);

    // 3. Painel Visual Flutuante de Progresso
    const div = document.createElement('div');
    div.id = 'painelAuditoriaVisitas7';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;width:600px;max-height:85vh;overflow-y:auto;background:#181a20;color:#fff;padding:22px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:16px;">🔍 Auditoria Visitas Avaliativas (Julho/2026)</strong>
            <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
        </div>
        <p id="statusProgresso" style="margin:0;color:#ccc;">Lendo as ${urlsExecucoes.length} execuções no SIGATER...</p>
        <div style="width:100%;background:#2a2d36;height:12px;border-radius:6px;margin:12px 0;overflow:hidden;">
            <div id="barraProgresso" style="width:0%;height:100%;background:linear-gradient(90deg, #00bcd4, #00e676);transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    // 4. Leitura paralela das páginas de execução
    const sigaterLancados = [];
    const BATCH_SIZE = 15;
    let concluidos = 0;

    for (let i = 0; i < urlsExecucoes.length; i += BATCH_SIZE) {
        const batch = urlsExecucoes.slice(i, i + BATCH_SIZE);
        await Promise.all(batch.map(async (url) => {
            try {
                const resp = await fetch(url);
                if (resp.ok) {
                    const html = await resp.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    
                    let nomeBeneficiario = '';
                    let cpfBeneficiario = '';

                    const trsPart = Array.from(doc.querySelectorAll('table tr'));
                    for (const tr of trsPart) {
                        const texto = tr.innerText || '';
                        if (texto.includes('Dados da DAP') || texto.includes('DAP_MDA') || /\d{3}\.\d{3}\.\d{3}-\d{2}/.test(texto)) {
                            const tds = Array.from(tr.querySelectorAll('td'));
                            tds.forEach(td => {
                                const t = td.innerText.trim();
                                if (/\d{3}\.\d{3}\.\d{3}-\d{2}/.test(t)) {
                                    cpfBeneficiario = t;
                                } else if (t.split(' ').length >= 2 && t.length >= 6 && !t.includes('DAP') && !t.includes('SIGATER') && !t.includes('MDA')) {
                                    nomeBeneficiario = t;
                                }
                            });
                        }
                    }

                    if (!nomeBeneficiario) {
                        const pdfLinks = Array.from(doc.querySelectorAll('a[href*=".pdf"], [title*=".pdf"]')).map(a => a.innerText || a.title || '');
                        for (const pdf of pdfLinks) {
                            const match = pdf.match(/([A-Z_]+)_-_(?:ATESTE|COLETUM)/i);
                            if (match) {
                                nomeBeneficiario = match[1].replace(/_/g, ' ');
                                break;
                            }
                        }
                    }

                    const codExec = url.match(/\/read\/(\d+)/) ? url.match(/\/read\/(\d+)/)[1] : '';

                    sigaterLancados.push({
                        codExec,
                        url,
                        nome: nomeBeneficiario || 'Não Identificado',
                        cpf: cpfBeneficiario || '-',
                        htmlBruto: normalizar(html)
                    });
                }
            } catch (err) {
            } finally {
                concluidos++;
                const perc = Math.round((concluidos / urlsExecucoes.length) * 100);
                const elStatus = document.getElementById('statusProgresso');
                const elBarra = document.getElementById('barraProgresso');
                if (elStatus) elStatus.innerText = `Processando: ${concluidos} de ${urlsExecucoes.length} (${perc}%)...`;
                if (elBarra) elBarra.style.width = `${perc}%`;
            }
        }));
    }

    // 5. Cruzamento Inteligente: Coletum vs SIGATER
    const lancadosConfirmados = [];
    const pendentesNaoLancados = [];

    coletumVisitas.forEach(col => {
        const nomeNormCol = normalizar(col.beneficiario);
        const cpfLimpoCol = cleanCpf(col.cpf);

        let achou = false;
        for (const sig of sigaterLancados) {
            const sigCpfLimpo = cleanCpf(sig.cpf);

            if ((cpfLimpoCol.length >= 8 && sigCpfLimpo.includes(cpfLimpoCol)) ||
                similaridade(col.beneficiario, sig.nome) >= 0.70 ||
                sig.htmlBruto.includes(nomeNormCol)) {
                achou = true;
                break;
            }
        }

        if (achou) {
            lancadosConfirmados.push(col);
        } else {
            pendentesNaoLancados.push(col);
        }
    });

    // 6. Agrupamento das pendências por Técnico
    const pendentesPorTecnico = {};
    pendentesNaoLancados.forEach(p => {
        const t = p.tecnico || 'Não Informado';
        if (!pendentesPorTecnico[t]) pendentesPorTecnico[t] = [];
        pendentesPorTecnico[t].push(p);
    });

    // 7. Exibição Detalhada no Console
    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 RESULTADO DA AUDITORIA (VISITAS AVALIATIVAS - JULHO/2026 - ATIVIDADE # 67119):
- Total no Coletum (Julho): %c${coletumVisitas.length}%c
- Lançados no SIGATER: %c${sigaterLancados.length}%c
- Confirmados: %c${lancadosConfirmados.length}%c
- ⚠️ PENDENTES DE LANÇAMENTO: %c${pendentesNaoLancados.length}%c`,
        'font-weight: bold; font-size: 14px; color: #fff;',
        'color: #00e676; font-weight: bold;', 'color: #fff;',
        'color: #00bcd4; font-weight: bold;', 'color: #fff;',
        'color: #29b6f6; font-weight: bold;', 'color: #fff;',
        'color: #ff1744; font-weight: bold; font-size: 16px;', 'color: #fff;'
    );
    console.log('%c====================================================================', 'color: #888');

    if (pendentesNaoLancados.length > 0) {
        console.log(`%c⚠️ LISTA DOS BENEFICIÁRIOS PENDENTES NO SIGATER (${pendentesNaoLancados.length}):`, 'color: #ff5252; font-size: 15px; font-weight: bold;');
        console.table(pendentesNaoLancados.map((p, i) => ({
            '#': i + 1,
            'Beneficiário': p.beneficiario,
            'CPF': p.cpf,
            'Técnico': p.tecnico,
            'Comunidade': p.comunidade,
            'Município': p.municipio,
            'Data': p.data,
            'ID Coletum': p.coletum_id
        })));
    } else {
        console.log('%c🎉 Parabéns! Todas as 281 visitas do Coletum constam como lançadas no SIGATER!', 'color: #00e676; font-size: 16px; font-weight: bold;');
    }

    // 8. Atualização do Painel Flutuante Final
    window._pendentesVisitasJulho = pendentesNaoLancados;

    div.style.border = pendentesNaoLancados.length > 0 ? '2px solid #ff5252' : '2px solid #00e676';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:12px;">
            <strong style="color:${pendentesNaoLancados.length > 0 ? '#ff5252' : '#00e676'};font-size:16px;">
                ${pendentesNaoLancados.length > 0 ? `⚠️ Faltam ${pendentesNaoLancados.length} Visitas Avaliativas no SIGATER` : '✅ 100% das Visitas Lançadas!'}
            </strong>
            <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
        </div>
        <p style="margin:0 0 10px 0;color:#ccc;">
            Meta Coletum: <strong>${coletumVisitas.length}</strong> | Lançados SIGATER: <strong style="color:#00bcd4;">${sigaterLancados.length}</strong> | Pendentes: <strong style="color:#ff5252;font-size:15px;">${pendentesNaoLancados.length}</strong>
        </p>

        ${Object.keys(pendentesPorTecnico).length > 0 ? `
            <div style="background:#22252e;padding:12px;border-radius:8px;margin-bottom:12px;">
                <strong style="color:#ffd54f;display:block;margin-bottom:8px;">👤 Pendências por Técnico:</strong>
                ${Object.keys(pendentesPorTecnico).map(t => `
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
                        <span>👤 ${t}</span>
                        <strong style="color:#ff5252;">${pendentesPorTecnico[t].length} pendente(s)</strong>
                    </div>
                `).join('')}
            </div>
        ` : ''}

        <div style="max-height:320px;overflow-y:auto;padding-right:4px;">
            ${pendentesNaoLancados.map((p, i) => `
                <div style="background:#22252e;padding:10px 12px;border-radius:6px;margin-bottom:8px;border-left:4px solid #ff5252;">
                    <strong style="color:#fff;font-size:13px;">${i+1}. ${p.beneficiario}</strong><br>
                    <small style="color:#bbb;">CPF: <span style="color:#00e676;">${p.cpf}</span> | ${p.comunidade} (${p.municipio})</small><br>
                    <small style="color:#ffd54f;">👤 Técnico: ${p.tecnico} • 📅 Data: ${p.data}</small>
                </div>
            `).join('')}
        </div>

        ${pendentesNaoLancados.length > 0 ? `
        <div style="display:flex;gap:10px;margin-top:14px;">
            <button id="btnCopiarPendentesVisitas" style="flex:1;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
                📋 Copiar Lista de Pendentes (${pendentesNaoLancados.length})
            </button>
            <button id="btnBaixarCsvPendentesVisitas" style="flex:1;padding:10px;background:#00e676;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
                📥 Baixar CSV
            </button>
        </div>` : ''}
    `;

    // Ações dos botões
    if (document.getElementById('btnCopiarPendentesVisitas')) {
        document.getElementById('btnCopiarPendentesVisitas').onclick = function() {
            const txt = pendentesNaoLancados.map((p, i) => 
                `${i+1}. ${p.beneficiario} | CPF: ${p.cpf} | Téc: ${p.tecnico} | ${p.comunidade} (${p.municipio}) | Data: ${p.data}`
            ).join('\n');
            navigator.clipboard.writeText(txt).then(() => alert(`Lista dos ${pendentesNaoLancados.length} pendentes copiada com sucesso!`));
        };
    }

    if (document.getElementById('btnBaixarCsvPendentesVisitas')) {
        document.getElementById('btnBaixarCsvPendentesVisitas').onclick = function() {
            let csv = '\uFEFFNº;Beneficiário;CPF;Técnico;Município;Comunidade;Data Realização;ID Coletum\n';
            pendentesNaoLancados.forEach((p, i) => {
                csv += `"${i+1}";"${p.beneficiario}";"${p.cpf}";"${p.tecnico}";"${p.municipio}";"${p.comunidade}";"${p.data}";"${p.coletum_id}"\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'Pendencias_Visitas_Avaliativas_Julho_2026.csv';
            link.click();
        };
    }
})();
