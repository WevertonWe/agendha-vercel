/**
 * ==============================================================================
 * 🔍 AUDITOR SIGATER vs COLETUM - ACOMPANHAMENTO DO PLANO PRODUTIVO (JUNHO / 2026 - MÊS 6)
 * ==============================================================================
 * Formulário Coletum: 37226 (Acompanhamento Plano Produtivo - Bahia sem Fome)
 * Total no Coletum em Junho/2026: 164 registros (163 beneficiários únicos)
 *
 * Como usar:
 * 1. No SIGATER, abra a tela "LISTAGEM - EXECUÇÕES" da atividade de Acompanhamento / Visita Técnica.
 * 2. Abra o Console do navegador (F12 -> Console).
 * 3. Cole este código e pressione [ENTER].
 * ==============================================================================
 */
(async function() {
    console.clear();
    console.log('%c🚀 INICIANDO AUDITORIA ACOMPANHAMENTO PLANO PRODUTIVO (JUNHO/2026 - 164 REGISTROS)...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');

    const coletumRegistros = [
  {
    "coletum_id": "31648.103",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Fernando Santa Rosa dos Santos",
    "cpf": "00527782580",
    "cpf_formatado": "005.277.825-80",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "30/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31648.102",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josiane Maria Maia",
    "cpf": "04806519570",
    "cpf_formatado": "048.065.195-70",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "29/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.100",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Josiane Lima Silva",
    "cpf": "86205998521",
    "cpf_formatado": "862.059.985-21",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "29/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "26510.528",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JAINE DOS SANTOS MORAIS",
    "cpf": "05996482525",
    "cpf_formatado": "059.964.825-25",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "30/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.529",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ANA RUTH DOS SANTOS MAIA",
    "cpf": "07122119505",
    "cpf_formatado": "071.221.195-05",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "30/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31616.75",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA GOMES MAURO DO SOCORRO",
    "cpf": "00777971593",
    "cpf_formatado": "007.779.715-93",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "30/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.77",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ALAIDE BAHIA DA CRUZ",
    "cpf": "10734951590",
    "cpf_formatado": "107.349.515-90",
    "municipio": "Abaré",
    "comunidade": "ALTO VERMELHO",
    "data": "30/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.76",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JAINE MACIEL SILVA SANTOS",
    "cpf": "09585008513",
    "cpf_formatado": "095.850.085-13",
    "municipio": "Abaré",
    "comunidade": "ALTO VERMELHO",
    "data": "30/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.78",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "GILBERTO DIAS DOS SANTOS",
    "cpf": "00791922545",
    "cpf_formatado": "007.919.225-45",
    "municipio": "Abaré",
    "comunidade": "LAGOA DO JOSE ALVES",
    "data": "30/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.392",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Genilda Silva dos Santos",
    "cpf": "08761165514",
    "cpf_formatado": "087.611.655-14",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.391",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Salete Maria dos Santos",
    "cpf": "28534278890",
    "cpf_formatado": "285.342.788-90",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.390",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jilsomar Gomes da cruz",
    "cpf": "05913502540",
    "cpf_formatado": "059.135.025-40",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.73",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Jaqueline Ribeiro de Souza",
    "cpf": "85878808536",
    "cpf_formatado": "858.788.085-36",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.72",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Santos Silva Ribeiro",
    "cpf": "10262232537",
    "cpf_formatado": "102.622.325-37",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.71",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Lucivania Rosa de Mota",
    "cpf": "02288197501",
    "cpf_formatado": "022.881.975-01",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.70",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maiara de Barros Teixeira",
    "cpf": "10008223548",
    "cpf_formatado": "100.082.235-48",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "30/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.69",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Thaynara Silva Barros",
    "cpf": "10168606500",
    "cpf_formatado": "101.686.065-00",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "29/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.68",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maira Maria de Barros Teixeira",
    "cpf": "07629140509",
    "cpf_formatado": "076.291.405-09",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "29/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.67",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Mônica Maria Ribeiro Gama",
    "cpf": "00300002548",
    "cpf_formatado": "003.000.025-48",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "29/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.66",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Michele Ribeiro Gama",
    "cpf": "86501189500",
    "cpf_formatado": "865.011.895-00",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "29/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.99",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Joselia Maria Maia",
    "cpf": "01483155501",
    "cpf_formatado": "014.831.555-01",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "27/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.98",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Francineide Maria Conceição Maia",
    "cpf": "86697462558",
    "cpf_formatado": "866.974.625-58",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "27/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.97",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Alayne Silva Mendes",
    "cpf": "05630121537",
    "cpf_formatado": "056.301.215-37",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.96",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Leide Daiane Silva Maia",
    "cpf": "08157829500",
    "cpf_formatado": "081.578.295-00",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.95",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Carmelita Ramos da Silva",
    "cpf": "01490994521",
    "cpf_formatado": "014.909.945-21",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.94",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Ildivânia Mendes dos Santos",
    "cpf": "86121846577",
    "cpf_formatado": "861.218.465-77",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.93",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Robéria Félix Maia",
    "cpf": "86053804541",
    "cpf_formatado": "860.538.045-41",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "25/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.92",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Roberta Félix Maia Santos",
    "cpf": "08947173592",
    "cpf_formatado": "089.471.735-92",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "25/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31616.73",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JOSÉ JOÃO ANANIAS DA SILVA",
    "cpf": "01516323599",
    "cpf_formatado": "015.163.235-99",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "27/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.74",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "FABIO JUNIOR DE MENEZES GOMES",
    "cpf": "03589783516",
    "cpf_formatado": "035.897.835-16",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "27/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.69",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "CLAUDEANE SOUZA OLIVEIRA",
    "cpf": "07582717511",
    "cpf_formatado": "075.827.175-11",
    "municipio": "Abaré",
    "comunidade": "LAGOA DO JOSE ALVES",
    "data": "26/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.72",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JOÃO ADRIANO SIMÕES",
    "cpf": "01569102503",
    "cpf_formatado": "015.691.025-03",
    "municipio": "Abaré",
    "comunidade": "LAGOA DO JOSE ALVES",
    "data": "26/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.70",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "AMILTON JOSÉ PAIVA DA SILVA",
    "cpf": "09643063526",
    "cpf_formatado": "096.430.635-26",
    "municipio": "Abaré",
    "comunidade": "LAGOA DO JOSE ALVES",
    "data": "26/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.71",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADIMILSON SIMÕES DA SILVA",
    "cpf": "20098354841",
    "cpf_formatado": "200.983.548-41",
    "municipio": "Abaré",
    "comunidade": "LAGOA DO JOSE ALVES",
    "data": "26/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.65",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Clescineide Oliveira",
    "cpf": "02821335504",
    "cpf_formatado": "028.213.355-04",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.64",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Lucimara Vieira Ribeiro",
    "cpf": "55560474215",
    "cpf_formatado": "555.604.742-15",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.63",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Luciana Vieira Ribeiro Barbosa",
    "cpf": "01575371294",
    "cpf_formatado": "015.753.712-94",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.62",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Luana Gomes Xavier Vieira",
    "cpf": "02455329518",
    "cpf_formatado": "024.553.295-18",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.389",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Daniele Ribeiro da Cruz",
    "cpf": "08680240583",
    "cpf_formatado": "086.802.405-83",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.388",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "José Alves Moreira",
    "cpf": "68769121591",
    "cpf_formatado": "687.691.215-91",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "26/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31616.66",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "RIZADALVA ALVES DOS SANTOS",
    "cpf": "00560341563",
    "cpf_formatado": "005.603.415-63",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.67",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "INÁCIO MARTINS DE MORAIS",
    "cpf": "00543590585",
    "cpf_formatado": "005.435.905-85",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.68",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "EDILEIDE IRENE DOS SANTOS",
    "cpf": "03127989547",
    "cpf_formatado": "031.279.895-47",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.387",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Mirella da Silva Coelho Rocha",
    "cpf": "07224862517",
    "cpf_formatado": "072.248.625-17",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.386",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Pascoal Quinto dos Santos",
    "cpf": "00781399530",
    "cpf_formatado": "007.813.995-30",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.385",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Gislanea Almeida de Menezes",
    "cpf": "03736061501",
    "cpf_formatado": "037.360.615-01",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.384",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Luciana Ferreira da Silva",
    "cpf": "06630341597",
    "cpf_formatado": "066.303.415-97",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.61",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Jociane Lucas da Silva",
    "cpf": "08453666539",
    "cpf_formatado": "084.536.665-39",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "25/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.57",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Gislane Vieira Silva Xavier",
    "cpf": "08057312530",
    "cpf_formatado": "080.573.125-30",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.56",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Daniele Barros da Silva",
    "cpf": "86663835505",
    "cpf_formatado": "866.638.355-05",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.55",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Simara Ribeiro do Nascimento",
    "cpf": "86483492570",
    "cpf_formatado": "864.834.925-70",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.54",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Jaqueline da Silva",
    "cpf": "36084606830",
    "cpf_formatado": "360.846.068-30",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.91",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Carmen Andrea Ramos da Silva",
    "cpf": "00972456589",
    "cpf_formatado": "009.724.565-89",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "24/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.90",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria José dos Santos",
    "cpf": "03926217545",
    "cpf_formatado": "039.262.175-45",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "24/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.89",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Jovelina dos Santos",
    "cpf": "07402939588",
    "cpf_formatado": "074.029.395-88",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "24/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.88",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Tamiris dos Santos Silva",
    "cpf": "12611080518",
    "cpf_formatado": "126.110.805-18",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "23/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.87",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Jocelma Maria dos Santos",
    "cpf": "85914386551",
    "cpf_formatado": "859.143.865-51",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "23/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.86",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josineide Maria dos Santos",
    "cpf": "86547297594",
    "cpf_formatado": "865.472.975-94",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "23/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.85",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Joelson dos Santos",
    "cpf": "05327356507",
    "cpf_formatado": "053.273.565-07",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "23/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31616.65",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "IANDRA DO NASCIMENTO SANTOS",
    "cpf": "04548737510",
    "cpf_formatado": "045.487.375-10",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "23/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.63",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MARIA DO SOCORRO BARBOSA SANTOS",
    "cpf": "00549761543",
    "cpf_formatado": "005.497.615-43",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "23/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.64",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "CEZAR ANTÔNIO DOS SANTOS",
    "cpf": "93923368534",
    "cpf_formatado": "939.233.685-34",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "23/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.383",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Martinha Ferreira do Nascimento",
    "cpf": "02931836516",
    "cpf_formatado": "029.318.365-16",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "23/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.382",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Antonio do Nascimento Santos",
    "cpf": "89123484500",
    "cpf_formatado": "891.234.845-00",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "23/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.381",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria José da Silva",
    "cpf": "06120006567",
    "cpf_formatado": "061.200.065-67",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "23/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.60",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Sinalia Maria Oliveira do Nascimento",
    "cpf": "10372284566",
    "cpf_formatado": "103.722.845-66",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "23/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.59",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Rafaela Maria Oliveira do Nascimento",
    "cpf": "08121239567",
    "cpf_formatado": "081.212.395-67",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "23/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.58",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Luzia Oliveira do Nascimento",
    "cpf": "06727765456",
    "cpf_formatado": "067.277.654-56",
    "municipio": "Glória",
    "comunidade": "Brejo do burgo",
    "data": "23/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.59",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "RENATO DE JESUS SILVA",
    "cpf": "08942394574",
    "cpf_formatado": "089.423.945-74",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.60",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "CARLEUZA DA CRUZ DOS SANTOS",
    "cpf": "05006253525",
    "cpf_formatado": "050.062.535-25",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.61",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "MICHELLY DA SILVA CRUZ",
    "cpf": "11157246575",
    "cpf_formatado": "111.572.465-75",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.62",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADENILSA LAURINDA DA SILVA",
    "cpf": "00612232557",
    "cpf_formatado": "006.122.325-57",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "22/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "26510.527",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROGERIA BARBOSA DE SOUZA",
    "cpf": "05998184505",
    "cpf_formatado": "059.981.845-05",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "22/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.526",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "NUBIA FERREIRA DOS ANTOS",
    "cpf": "05996486512",
    "cpf_formatado": "059.964.865-12",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "22/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.525",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LUZIA TAVARES DA SILVA FERREIRA",
    "cpf": "08291327599",
    "cpf_formatado": "082.913.275-99",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "22/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.380",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Alaíde Ana do Nascimento",
    "cpf": "06195941522",
    "cpf_formatado": "061.959.415-22",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.379",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Américo Marques Ramos",
    "cpf": "46936181520",
    "cpf_formatado": "469.361.815-20",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.378",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Geane Mendes dos Santos",
    "cpf": "02486402594",
    "cpf_formatado": "024.864.025-94",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.377",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Justino Alves Moreira",
    "cpf": "10760922845",
    "cpf_formatado": "107.609.228-45",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.84",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "José Antônio Almeida dos Santos",
    "cpf": "07606422575",
    "cpf_formatado": "076.064.225-75",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.83",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Josivania dos Santos Silva",
    "cpf": "86528721556",
    "cpf_formatado": "865.287.215-56",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.82",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Janice Félix Maciel",
    "cpf": "05808408598",
    "cpf_formatado": "058.084.085-98",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "22/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.81",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Claudenice Vieira da Silva",
    "cpf": "11485616506",
    "cpf_formatado": "114.856.165-06",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "19/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.80",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Liedson Andrade Maciel",
    "cpf": "09606730590",
    "cpf_formatado": "096.067.305-90",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "19/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.79",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Rafaela dos Santos Maia",
    "cpf": "08441221570",
    "cpf_formatado": "084.412.215-70",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "19/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31616.57",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "DULCINEIA DO NASCIMENTO BARBALHO",
    "cpf": "13625882884",
    "cpf_formatado": "136.258.828-84",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "19/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.58",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JOSÉ FÁBIO FERREIRA FERNANDES",
    "cpf": "06395419331",
    "cpf_formatado": "063.954.193-31",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "19/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "26510.524",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JESSICA BARROS DE LIMA",
    "cpf": "09924486544",
    "cpf_formatado": "099.244.865-44",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "19/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.376",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Daniel da Silva Carvalho",
    "cpf": "10941432513",
    "cpf_formatado": "109.414.325-13",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "19/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.375",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gleuka Jéssica Alves de Adrade",
    "cpf": "52558582852",
    "cpf_formatado": "525.585.828-52",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "19/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.374",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Milena de Jesus Santos",
    "cpf": "07981382548",
    "cpf_formatado": "079.813.825-48",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "19/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.373",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Marineide de Jesus Santos",
    "cpf": "05496053552",
    "cpf_formatado": "054.960.535-52",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "19/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.78",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Zilda dos Santos Silva",
    "cpf": "12161227505",
    "cpf_formatado": "121.612.275-05",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "18/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.77",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edvânia dos Santos Silva",
    "cpf": "86076478578",
    "cpf_formatado": "860.764.785-78",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "18/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.76",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Jaiane Rodrigues Pereira",
    "cpf": "12524388506",
    "cpf_formatado": "125.243.885-06",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "18/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31616.55",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "JÉSSICA THAÍS SOARES DA SILVA",
    "cpf": "06542052569",
    "cpf_formatado": "065.420.525-69",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "18/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.54",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "ADRIANA DOS SANTOS JESUS",
    "cpf": "00471646547",
    "cpf_formatado": "004.716.465-47",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "18/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31616.56",
    "tecnico": "Caroline Evangelista de Queiroz",
    "beneficiario": "VANESSA DE CARVALHO SANTOS",
    "cpf": "06930282545",
    "cpf_formatado": "069.302.825-45",
    "municipio": "Abaré",
    "comunidade": "ALDEIA TUXI",
    "data": "18/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.48",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Analice Alves da Silva Santos",
    "cpf": "06367766545",
    "cpf_formatado": "063.677.665-45",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "17/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.49",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Marcia Graciete da Silva",
    "cpf": "07172408519",
    "cpf_formatado": "071.724.085-19",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "17/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.50",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Ronaldo Vieira da Silva",
    "cpf": "07807992590",
    "cpf_formatado": "078.079.925-90",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "17/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.53",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Eugênia Maria Batista",
    "cpf": "04055434502",
    "cpf_formatado": "040.554.345-02",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "18/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.52",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Derisson Santos Silva",
    "cpf": "06364533590",
    "cpf_formatado": "063.645.335-90",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "18/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.51",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Aparecida Nascimento Barros",
    "cpf": "00296606537",
    "cpf_formatado": "002.966.065-37",
    "municipio": "Glória",
    "comunidade": "Brejo do Burgo",
    "data": "18/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.75",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Amanda Suylla Alves de Carvalho",
    "cpf": "07150038522",
    "cpf_formatado": "071.500.385-22",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "18/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.74",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Meirelaine de Lima",
    "cpf": "11066455538",
    "cpf_formatado": "110.664.555-38",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "17/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.73",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Raniele Maria dos Santos Alves",
    "cpf": "86734629597",
    "cpf_formatado": "867.346.295-97",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "17/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.372",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Antônia vitória de Jesus Moreira",
    "cpf": "86859921501",
    "cpf_formatado": "868.599.215-01",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "17/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.371",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Dejanira dos Santos de Oliveira",
    "cpf": "00154723533",
    "cpf_formatado": "001.547.235-33",
    "municipio": "Chorrochó",
    "comunidade": "Róçado",
    "data": "17/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.370",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Vilma Pereira Dantas",
    "cpf": "01626143579",
    "cpf_formatado": "016.261.435-79",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "17/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.369",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gilvane Araujo do Nascimento",
    "cpf": "04214446577",
    "cpf_formatado": "042.144.465-77",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "17/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.72",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edivany dos Santos Silva",
    "cpf": "86122852597",
    "cpf_formatado": "861.228.525-97",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "16/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.71",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria dos Santos Silva",
    "cpf": "86734079589",
    "cpf_formatado": "867.340.795-89",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "16/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.70",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edleuza Alves dos Santos",
    "cpf": "06950860579",
    "cpf_formatado": "069.508.605-79",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "16/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "26510.518",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "ROSIVANIA BRAGA DA SILVA",
    "cpf": "06179066531",
    "cpf_formatado": "061.790.665-31",
    "municipio": "Paulo Afonso",
    "comunidade": "BAIXA FUNDA",
    "data": "16/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.517",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "INIA SILVA NASCIMENTO",
    "cpf": "16339111793",
    "cpf_formatado": "163.391.117-93",
    "municipio": "Paulo Afonso",
    "comunidade": "BAIXA FUNDA",
    "data": "16/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.516",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LUZIA TAVARES DA SILVA FERREIRA",
    "cpf": "08291327599",
    "cpf_formatado": "082.913.275-99",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "16/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.368",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Rosilda dos Santos",
    "cpf": "08761292540",
    "cpf_formatado": "087.612.925-40",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "16/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.367",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Hagamenon França do Vale",
    "cpf": "03581843803",
    "cpf_formatado": "035.818.438-03",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "16/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.366",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Fernanda Reis Santos Costa",
    "cpf": "07205561558",
    "cpf_formatado": "072.055.615-58",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "16/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.47",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Maria Maize Valério",
    "cpf": "05831950590",
    "cpf_formatado": "058.319.505-90",
    "municipio": "Glória",
    "comunidade": "Kantarure",
    "data": "16/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.45",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Janiel Olavo Coelho Silva",
    "cpf": "03249950599",
    "cpf_formatado": "032.499.505-99",
    "municipio": "Glória",
    "comunidade": "Kantarure",
    "data": "16/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.365",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria Joseane Ferreira da Silva",
    "cpf": "04720429556",
    "cpf_formatado": "047.204.295-56",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "15/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.364",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Débora Ferreira da Silva",
    "cpf": "05811843518",
    "cpf_formatado": "058.118.435-18",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "15/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.363",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gislene Reis de Menezes",
    "cpf": "06322112538",
    "cpf_formatado": "063.221.125-38",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "15/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.362",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Elida Suenia Cerqueira dos Santos",
    "cpf": "02650336595",
    "cpf_formatado": "026.503.365-95",
    "municipio": "Chorrochó",
    "comunidade": "Roçado",
    "data": "15/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.44",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Josiane Gomes Xavier Santos",
    "cpf": "04823118510",
    "cpf_formatado": "048.231.185-10",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "15/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.43",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Silvia Gomes Xavier Conceição",
    "cpf": "02467921590",
    "cpf_formatado": "024.679.215-90",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "15/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.361",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Mirelly da Silva Santos",
    "cpf": "85916964501",
    "cpf_formatado": "859.169.645-01",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "12/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.360",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Manoel Teixeira dos Santos",
    "cpf": "63903423491",
    "cpf_formatado": "639.034.234-91",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "12/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.359",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Fabiano Vagner Nascimento Souza",
    "cpf": "34068363803",
    "cpf_formatado": "340.683.638-03",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "12/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.42",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Silvania Ribeiro do Nascimento",
    "cpf": "01918736596",
    "cpf_formatado": "019.187.365-96",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "12/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31646.41",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Divaneide Ribeiro Nascimento Feitoza",
    "cpf": "05495929543",
    "cpf_formatado": "054.959.295-43",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "12/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31646.40",
    "tecnico": "Luiz Antoniel Paiva Galvão",
    "beneficiario": "Vanessa Ribeiro Barbosa Silva",
    "cpf": "04556576539",
    "cpf_formatado": "045.565.765-39",
    "municipio": "Glória",
    "comunidade": "Pankarare",
    "data": "12/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.69",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "José Uilton dos Santos Silva",
    "cpf": "08420671592",
    "cpf_formatado": "084.206.715-92",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "08/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31648.68",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Edinaide Alves dos Santos",
    "cpf": "08451209564",
    "cpf_formatado": "084.512.095-64",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "08/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.67",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Ednalva Alves dos Santos",
    "cpf": "86122848565",
    "cpf_formatado": "861.228.485-65",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "08/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "27309.358",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Alice Ribeiro do Nascimento Oliveira",
    "cpf": "00174981554",
    "cpf_formatado": "001.749.815-54",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "08/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.357",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Braz Conceição do Nascimento",
    "cpf": "93177747504",
    "cpf_formatado": "931.777.475-04",
    "municipio": "Chorrochó",
    "comunidade": "São José",
    "data": "08/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "27309.356",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Josélia Pereira dos Santos",
    "cpf": "02472943571",
    "cpf_formatado": "024.729.435-71",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "08/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31648.66",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Cintia Daniele Conceição Silva",
    "cpf": "06774378544",
    "cpf_formatado": "067.743.785-44",
    "municipio": "Macururé",
    "comunidade": "Riacho dos caldeirões",
    "data": "05/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.355",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Maria de Lourdes Alves da Silva",
    "cpf": "75460203520",
    "cpf_formatado": "754.602.035-20",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "05/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.354",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Roseane Teixeira Alves",
    "cpf": "05317823528",
    "cpf_formatado": "053.178.235-28",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "05/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.353",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Luiz Teixeira Alves",
    "cpf": "95967800506",
    "cpf_formatado": "959.678.005-06",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "05/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.352",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Elisangela Alves dos Santos",
    "cpf": "05320671504",
    "cpf_formatado": "053.206.715-04",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.351",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Gabriela Soares dos Santos",
    "cpf": "48684340809",
    "cpf_formatado": "486.843.408-09",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.350",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jadenice Tolêdo dos Santos Simões",
    "cpf": "00313399565",
    "cpf_formatado": "003.133.995-65",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.349",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Vitor Pereira Dantas",
    "cpf": "00252036573",
    "cpf_formatado": "002.520.365-73",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31648.65",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Franciele Alves Oliveira",
    "cpf": "12184015598",
    "cpf_formatado": "121.840.155-98",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "04/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.64",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Eliete Alves dos Santos",
    "cpf": "85879285545",
    "cpf_formatado": "858.792.855-45",
    "municipio": "Macururé",
    "comunidade": "Minador",
    "data": "04/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.63",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Maria Eduarda Rodrigues Silva Gimenes",
    "cpf": "85916561563",
    "cpf_formatado": "859.165.615-63",
    "municipio": "Chorrochó",
    "comunidade": "Várzea da Ema",
    "data": "04/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.62",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "José Cassimiro de Oliveira",
    "cpf": "51288737572",
    "cpf_formatado": "512.887.375-72",
    "municipio": "Chorrochó",
    "comunidade": "Várzea da Ema",
    "data": "03/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "26510.515",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "GLEISIANE BARROS DE LIMA",
    "cpf": "09924399579",
    "cpf_formatado": "099.243.995-79",
    "municipio": "Paulo Afonso",
    "comunidade": "CASA DE PEDRA",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.514",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "JOSEFA FERREIRA DA SILVA",
    "cpf": "07424842544",
    "cpf_formatado": "074.248.425-44",
    "municipio": "Paulo Afonso",
    "comunidade": "LAGOA GRANDE",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.512",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "FABIANA FERREIRA DE SOUZA",
    "cpf": "05662266506",
    "cpf_formatado": "056.622.665-06",
    "municipio": "Paulo Afonso",
    "comunidade": "BAIXA FUNDA",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "26510.513",
    "tecnico": "JOSEFA CRISTINA DE CARVALHO SANTOS",
    "beneficiario": "LUCINEIDE APARECIDA DE FREITAS",
    "cpf": "06759013590",
    "cpf_formatado": "067.590.135-90",
    "municipio": "Paulo Afonso",
    "comunidade": "BAIXA FUNDA",
    "data": "03/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.348",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jilson Gabriel Alves do Nascimento",
    "cpf": "08755667589",
    "cpf_formatado": "087.556.675-89",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "02/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.347",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Jilaene Alves dos Santos",
    "cpf": "03077735580",
    "cpf_formatado": "030.777.355-80",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "02/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.346",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Sebastina Alves Barbalho",
    "cpf": "42544296810",
    "cpf_formatado": "425.442.968-10",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "02/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "27309.345",
    "tecnico": "Wandisson Santos de Jesus",
    "beneficiario": "Lucivânia Alves dos Santos",
    "cpf": "05338699516",
    "cpf_formatado": "053.386.995-16",
    "municipio": "Chorrochó",
    "comunidade": "Golf",
    "data": "02/06/2026",
    "visita_n": 3
  },
  {
    "coletum_id": "31648.61",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Francisco de Paula Bispo de Araújo",
    "cpf": "27828700504",
    "cpf_formatado": "278.287.005-04",
    "municipio": "Chorrochó",
    "comunidade": "Várzea da Ema",
    "data": "02/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.60",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Caroline Soares de Jesus",
    "cpf": "05040705506",
    "cpf_formatado": "050.407.055-06",
    "municipio": "Chorrochó",
    "comunidade": "Várzea da Ema",
    "data": "02/06/2026",
    "visita_n": 1
  },
  {
    "coletum_id": "31648.59",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Rosenilde Oliveira da Silva",
    "cpf": "01513457594",
    "cpf_formatado": "015.134.575-94",
    "municipio": "Chorrochó",
    "comunidade": "Várzea da Ema",
    "data": "02/06/2026",
    "visita_n": 2
  },
  {
    "coletum_id": "31648.58",
    "tecnico": "Estella Souza da Silva Pereira",
    "beneficiario": "Patricia da Cruz Santos",
    "cpf": "39323124818",
    "cpf_formatado": "393.231.248-18",
    "municipio": "Chorrochó",
    "comunidade": "Várzea da Ema",
    "data": "02/06/2026",
    "visita_n": 1
  }
];

    function normalizar(txt) {
        if (!txt) return '';
        return String(txt).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().trim();
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

    // 1. Identifica links das execuções na tela do SIGATER
    const linksLupa = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"], table tbody tr a'));
    const urlsExecucoes = Array.from(new Set(
        linksLupa.map(a => a.href).filter(h => h && (h.includes('/read/') || h.includes('cronograma_execucao/read')))
    ));

    console.log(`📋 Total de execuções lidas na tela do SIGATER: ${urlsExecucoes.length}`);

    if (urlsExecucoes.length === 0) {
        alert('Por favor, abra a tela "LISTAGEM - EXECUÇÕES" da atividade no SIGATER.');
        return;
    }

    // Painel Visual Flutuante
    const antigo = document.getElementById('painelAuditoriaAcomp');
    if (antigo) antigo.remove();

    const div = document.createElement('div');
    div.id = 'painelAuditoriaAcomp';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;max-width:580px;max-height:85vh;overflow-y:auto;background:#1e1e2f;color:#fff;padding:20px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.8);z-index:999999;font-family:sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="border-bottom:1px solid #444;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:15px;">⏳ Lendo ${urlsExecucoes.length} Execuções no SIGATER...</strong>
        </div>
        <p id="statusProgresso" style="margin:0;color:#ccc;">Carregando dados dos beneficiários...</p>
        <div style="width:100%;background:#333;height:10px;border-radius:5px;margin-top:10px;overflow:hidden;">
            <div id="barraProgresso" style="width:0%;height:100%;background:#00bcd4;transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    // 2. Leitura paralela das páginas de execução
    const sigaterLancados = [];
    const BATCH_SIZE = 10;
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

    // 3. Cruzamento
    const lancadosConfirmados = [];
    const pendentesNaoLancados = [];

    coletumRegistros.forEach(col => {
        let achou = false;
        for (const sig of sigaterLancados) {
            const cpfLimpo = (col.cpf || '').replace(/\D/g, '');
            if (similaridade(col.beneficiario, sig.nome) >= 0.70 || sig.htmlBruto.includes(normalizar(col.beneficiario)) || (cpfLimpo.length >= 8 && sig.cpf.replace(/\D/g, '').includes(cpfLimpo))) {
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

    // 4. Exibição
    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 RESULTADO DA AUDITORIA (JUNHO/2026 - ACOMPANHAMENTO PLANO PRODUTIVO):
- Meta no Coletum (Junho/2026): %c${coletumRegistros.length}%c
- Lançados no SIGATER: %c${sigaterLancados.length}%c
- Confirmados: %c${lancadosConfirmados.length}%c
- ⚠️ PENDENTES: %c${pendentesNaoLancados.length}%c`,
        'font-weight: bold; font-size: 14px; color: #fff;',
        'color: #00e676; font-weight: bold;', 'color: #fff;',
        'color: #00bcd4; font-weight: bold;', 'color: #fff;',
        'color: #29b6f6; font-weight: bold;', 'color: #fff;',
        'color: #ff1744; font-weight: bold; font-size: 16px;', 'color: #fff;'
    );
    console.log('%c====================================================================', 'color: #888');

    if (pendentesNaoLancados.length > 0) {
        console.log(`%c⚠️ BENEFICIÁRIOS PENDENTES NO SIGATER:`, 'color: #ff5252; font-size: 15px; font-weight: bold;');
        console.table(pendentesNaoLancados.map((p, i) => ({
            '#': i + 1,
            'Beneficiário': p.beneficiario,
            'CPF': p.cpf_formatado,
            'Técnico': p.tecnico,
            'Comunidade': p.comunidade,
            'Município': p.municipio,
            'Data': p.data,
            'Visita Nº': p.visita_n
        })));
    } else {
        console.log('%c🎉 Todos os beneficiários constam como lançados no SIGATER!', 'color: #00e676; font-size: 16px; font-weight: bold;');
    }

    // 5. Painel Flutuante Final
    div.style.border = pendentesNaoLancados.length > 0 ? '2px solid #ff5252' : '2px solid #00e676';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #444;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:${pendentesNaoLancados.length > 0 ? '#ff5252' : '#00e676'};font-size:15px;">
                ${pendentesNaoLancados.length > 0 ? '⚠️ Pendências de Acompanhamento (Junho/2026)' : '✅ 100% Lançado no SIGATER'}
            </strong>
            <button onclick="document.getElementById('painelAuditoriaAcomp').remove()" style="background:none;border:none;color:#fff;cursor:pointer;font-size:16px;">✖</button>
        </div>
        <p style="margin:0 0 10px 0;color:#ccc;">
            Total Coletum: <strong>${coletumRegistros.length}</strong> | SIGATER: <strong style="color:#00e676;">${sigaterLancados.length}</strong> | Pendentes: <strong style="color:#ff5252;font-size:14px;">${pendentesNaoLancados.length}</strong>
        </p>
        <div style="max-height:360px;overflow-y:auto;">
            ${pendentesNaoLancados.map((p, i) => `
                <div style="background:#2a2b40;padding:10px;border-radius:6px;margin-bottom:8px;border-left:4px solid #ff5252;">
                    <strong style="color:#fff;font-size:13px;">${i+1}. ${p.beneficiario}</strong><br>
                    <small style="color:#bbb;">CPF: ${p.cpf_formatado} | ${p.comunidade} (${p.municipio})</small><br>
                    <small style="color:#ffd54f;">👤 Técnico: ${p.tecnico} • 📅 Data: ${p.data} (Visita Nº ${p.visita_n})</small>
                </div>
            `).join('')}
        </div>
        ${pendentesNaoLancados.length > 0 ? `
        <button id="btnCopiarPendentesAcomp" style="width:100%;margin-top:12px;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
            📋 Copiar Lista dos ${pendentesNaoLancados.length} Pendentes
        </button>` : ''}
    `;

    if (document.getElementById('btnCopiarPendentesAcomp')) {
        document.getElementById('btnCopiarPendentesAcomp').onclick = function() {
            const txt = pendentesNaoLancados.map((p, i) => `${i+1}. ${p.beneficiario} | CPF: ${p.cpf_formatado} | Téc: ${p.tecnico} - ${p.comunidade} (${p.municipio}) - Data: ${p.data} (Visita ${p.visita_n})`).join('\n');
            navigator.clipboard.writeText(txt).then(() => alert(`Lista dos ${pendentesNaoLancados.length} pendentes copiada!`));
        };
    }
})();
