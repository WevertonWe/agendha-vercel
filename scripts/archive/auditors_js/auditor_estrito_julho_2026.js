/**
 * ==============================================================================
 * 🔍 AUDITOR SIGATER v2 (ESTRITO 1-PARA-1): VISITAS AVALIATIVAS (JULHO/2026)
 * ==============================================================================
 * - Correspondência Estrita 1-para-1 (cada execução só pode validar 1 pessoa).
 * - Identifica falsos positivos por CPF compartilhado (ex: Rafaela/Maria Luzia).
 * - Identifica duplicidade no Coletum (ex: Josineide enviada 2x pelo Migson).
 * - Mostra a contagem real e localiza a 7ª pessoa faltante!
 * ==============================================================================
 */
(async function() {
    console.clear();
    console.log('%c🚀 AUDITORIA ESTRITA 1-PARA-1 - VISITAS AVALIATIVAS (JULHO/2026)...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');

    const rawData = [["Migson Brayne Pamponet da Silva","MARIANA GOMES DA SILVA","071.287.525-52","Sansaite","Macururé","31/07/2026","31657.165"],["Migson Brayne Pamponet da Silva","SIVANILDA GOMES DA SILVA","864.339.855-13","Serra do Tonan","Macururé","31/07/2026","31657.164"],["Migson Brayne Pamponet da Silva","JUNILSON SANTOS LIMA","034.581.415-02","Serra do Tonan","Macururé","31/07/2026","31657.163"],["Wandisson Santos de Jesus","GISLENE REIS DE MENEZES","063.221.125-38","Roçado","Chorrochó","31/07/2026","27309.447"],["Wandisson Santos de Jesus","ELIDA SUENIA CERQUEIRA DOS SANTOS","026.503.365-95","Roçado","Chorrochó","31/07/2026","27309.446"],["Wandisson Santos de Jesus","DÉBORA FERREIRA DA SILVA","058.118.435-18","Roçado","Chorrochó","31/07/2026","27309.445"],["Wandisson Santos de Jesus","JILSOMAR GOMES DA CRUZ","059.135.025-40","Roçado","Chorrochó","30/07/2026","27309.444"],["Wandisson Santos de Jesus","SALETE MARIA DOS SANTOS","285.342.788-90","Roçado","Chorrochó","30/07/2026","27309.443"],["Wandisson Santos de Jesus","MARIA JOSEANE FERREIRA DA SILVA","047.204.295-56","Roçado","Chorrochó","30/07/2026","27309.442"],["Wandisson Santos de Jesus","MARIA LUCIANA FERREIRA DA SILVA","066.303.415-97","Roçado","Chorrochó","30/07/2026","27309.441"],["Caroline Evangelista de Queiroz","EDENILSON GONÇALVES DA SILVA","066.558.795-31","ALTO VERMELHO","Abaré","31/07/2026","31616.126"],["Caroline Evangelista de Queiroz","TEREZA DO NASCIMENTO SOUZA","006.920.995-22","ALTO VERMELHO","Abaré","31/07/2026","31616.125"],["Caroline Evangelista de Queiroz","REGINA GONÇALVES DA SILVA","033.849.015-92","ALTO VERMELHO","Abaré","31/07/2026","31616.124"],["Caroline Evangelista de Queiroz","MARCELO DO NASCIMENTO SILVA","717.760.264-03","ALTO VERMELHO","Abaré","31/07/2026","31616.127"],["Estella Souza da Silva Pereira","LEIDE DAIANE SILVA MAIA","081.578.295-00","Riacho dos caldeirões","Macururé","31/07/2026","31648.161"],["Luiz Antoniel Paiva Galvão","CLESCINEIDE OLIVEIRA","028.213.355-04","Brejo do Burgo","Glória","31/07/2026","31646.120"],["Luiz Antoniel Paiva Galvão","SILVIA GOMES XAVIER CONCEIÇÃO","024.679.215-90","Pankarare","Glória","31/07/2026","31646.119"],["Luiz Antoniel Paiva Galvão","MARCILEIDE FAGUNDO DO NASCIMENTO","063.466.385-21","Brejo do Burgo","Glória","31/07/2026","31646.118"],["Luiz Antoniel Paiva Galvão","SINALIA MARIA OLIVEIRA DO NASCIMENTO","103.722.845-66","Brejo do Burgo","Glória","30/07/2026","31646.117"],["Luiz Antoniel Paiva Galvão","MARIA LUZIA OLIVEIRA DO NASCIMENTO","081.212.395-67","Brejo do Burgo","Glória","30/07/2026","31646.116"],["Luiz Antoniel Paiva Galvão","JOCIANE LUCAS DA SILVA","084.536.665-39","Brejo do Burgo","Glória","30/07/2026","31646.115"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MERIAN CALDAS BARROS","042.286.242-86","LAGOA GRANDE","Paulo Afonso","31/07/2026","26510.582"],["JOSEFA CRISTINA DE CARVALHO SANTOS","GISLANE BARBOSA XAVIER MACIEL NEVES","858.389.585-61","LAGOA GRANDE","Paulo Afonso","31/07/2026","26510.581"],["JOSEFA CRISTINA DE CARVALHO SANTOS","RANIELE SOARES MACIEL","858.312.875-80","LAGOA GRANDE","Paulo Afonso","31/07/2026","26510.583"],["JOSEFA CRISTINA DE CARVALHO SANTOS","QUELIANE MARQUES DA SILVA","067.743.865-63","CASA DE PEDRA","Paulo Afonso","30/07/2026","26510.579"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARIA JULIANA DA SILVA","858.316.555-63","CASA DE PEDRA","Paulo Afonso","30/07/2026","26510.577"],["JOSEFA CRISTINA DE CARVALHO SANTOS","GISELE MARIA DOS SANTOS  FELICIANO","863.819.585-02","CASA DE PEDRA","Paulo Afonso","30/07/2026","26510.578"],["JOSEFA CRISTINA DE CARVALHO SANTOS","LUCAS PEREIRA DE ALMEIDA","864.818.635-89","LAGOA GRANDE","Paulo Afonso","30/07/2026","26510.580"],["Estella Souza da Silva Pereira","ILDIVANIA MENDES DOS SANTOS","861.218.465-77","Riacho dos caldeirões","Macururé","30/07/2026","31648.156"],["Estella Souza da Silva Pereira","JOELSON DOS SANTOS","053.273.565-07","Minador","Macururé","31/07/2026","31648.160"],["Estella Souza da Silva Pereira","JANICE FÉLIX MACIEL","058.084.085-98","Minador","Macururé","31/07/2026","31648.159"],["Estella Souza da Silva Pereira","ROBERTA FÉLIX MAIA SANTOS","089.471.735-92","Riacho dos caldeirões","Macururé","30/07/2026","31648.158"],["Estella Souza da Silva Pereira","ROBÉRIA FÉLIX MAIA","860.538.045-41","Riacho dos caldeirões","Macururé","30/07/2026","31648.157"],["Caroline Evangelista de Queiroz","JESICA MACIEL SILVA SANTOS","056.647.685-17","ALTO VERMELHO","Abaré","30/07/2026","31616.123"],["Caroline Evangelista de Queiroz","MARIA DA SILVA BARBOSA","075.722.455-52","ALTO VERMELHO","Abaré","30/07/2026","31616.121"],["Caroline Evangelista de Queiroz","EDIVANIA SILVA BARBOSA","079.918.185-43","ALTO VERMELHO","Abaré","30/07/2026","31616.120"],["Caroline Evangelista de Queiroz","MARIA DE CARVALHO JESUS","070.683.095-42","ALTO VERMELHO","Abaré","30/07/2026","31616.122"],["Migson Brayne Pamponet da Silva","JENIVALDO SOARES DA SILVA","005.355.935-54","Sansaite","Macururé","30/07/2026","31657.159"],["Migson Brayne Pamponet da Silva","MARIA IZABEL PEREIRA DE ANDRADE","440.844.238-07","Sansaite","Macururé","30/07/2026","31657.160"],["Migson Brayne Pamponet da Silva","ROSIMEIRE RODRIGUES BARBOSA","010.850.055-18","Sansaite","Macururé","30/07/2026","31657.161"],["Migson Brayne Pamponet da Silva","JOSINEIDE DA CRUZ","027.981.885-80","Sansaite","Macururé","30/07/2026","31657.162"],["JOSEFA CRISTINA DE CARVALHO SANTOS","LILIANE DA CONCEIÇÃO","077.528.395-90","BAIXA FUNDA","Paulo Afonso","29/07/2026","26510.576"],["JOSEFA CRISTINA DE CARVALHO SANTOS","JAIANE DOS SANTOS BEZERRA","858.312.825-11","BAIXA FUNDA","Paulo Afonso","29/07/2026","26510.574"],["Estella Souza da Silva Pereira","VALDETE OLIVEIRA DA SILVA","024.863.985-46","Várzea da Ema","Chorrochó","29/07/2026","31648.155"],["Estella Souza da Silva Pereira","ALAYNE SILVA MENDES","056.301.215-37","Riacho dos caldeirões","Macururé","29/07/2026","31648.154"],["Estella Souza da Silva Pereira","JOSELIA MARIA MAIA","014.831.555-01","Riacho dos caldeirões","Macururé","29/07/2026","31648.153"],["Estella Souza da Silva Pereira","JOSIANE MARIA MAIA","048.065.195-70","Riacho dos caldeirões","Macururé","29/07/2026","31648.152"],["JOSEFA CRISTINA DE CARVALHO SANTOS","FABIANA FERREIRA DE SOUZA","056.622.665-06","BAIXA FUNDA","Paulo Afonso","29/07/2026","26510.575"],["Caroline Evangelista de Queiroz","LUANA SOUZA MAIA","105.928.095-79","ALTO VERMELHO","Abaré","29/07/2026","31616.119"],["Caroline Evangelista de Queiroz","ELENILDA SOUZA MAIA","100.796.665-31","ALTO VERMELHO","Abaré","29/07/2026","31616.117"],["Caroline Evangelista de Queiroz","ELIDIA BARBOSA DA SILVA","000.227.935-50","ALTO VERMELHO","Abaré","29/07/2026","31616.116"],["Caroline Evangelista de Queiroz","ELENILZA SOUZA MAIA","083.080.285-19","ALTO VERMELHO","Abaré","29/07/2026","31616.118"],["Luiz Antoniel Paiva Galvão","JAILDA VIEIRA DA CONCEIÇÃO","049.388.215-40","Brejo do Burgo","Glória","29/07/2026","31646.113"],["Luiz Antoniel Paiva Galvão","DERISSON SANTOS SILVA","063.645.335-90","Brejo do Burgo","Glória","29/07/2026","31646.112"],["Luiz Antoniel Paiva Galvão","GEOVANA GOMES XAVIER GAMA","098.775.225-19","Pankarare","Glória","29/07/2026","31646.111"],["Luiz Antoniel Paiva Galvão","RAFAELA MARIA OLIVEIRA DO NASCIMENTO","081.212.395-67","Brejo do Burgo","Glória","29/07/2026","31646.110"],["Migson Brayne Pamponet da Silva","ANTÔNIO RIBEIRO DA SILVA","006.139.625-75","Serra do Tonan","Macururé","29/07/2026","31657.158"],["Migson Brayne Pamponet da Silva","JULIO MARIA LIMA","039.800.195-27","Serra do Tonan","Macururé","29/07/2026","31657.157"],["Migson Brayne Pamponet da Silva","MARIA DA SOCORRO ARAÚJO DA SILVA","008.077.135-11","Serra do Tonan","Macururé","29/07/2026","31657.156"],["Migson Brayne Pamponet da Silva","JACIMARA FÉLIX DA SILVA","067.042.165-02","Serra do Tonan","Macururé","29/07/2026","31657.155"],["Estella Souza da Silva Pereira","AMANDA SUYLLA ALVES DE CARVALHO","071.500.385-22","Minador","Macururé","28/07/2026","31648.151"],["Estella Souza da Silva Pereira","EDIVANY DOS SANTOS SILVA","861.228.525-97","Minador","Macururé","28/07/2026","31648.150"],["Estella Souza da Silva Pereira","SÉRGIO OLIVEIRA MONTES","075.232.135-88","Várzea da Ema","Chorrochó","28/07/2026","31648.149"],["Estella Souza da Silva Pereira","NEIDINALVA DA CONCEIÇÃO MONTES","087.647.455-54","Várzea da Ema","Chorrochó","28/07/2026","31648.148"],["Estella Souza da Silva Pereira","JOCELMA MARIA DOS SANTOS","859.143.865-51","Minador","Macururé","27/07/2026","31648.147"],["Estella Souza da Silva Pereira","JOSE UILTON DOS SANTOS SILVA","084.206.715-92","Minador","Macururé","27/07/2026","31648.146"],["Estella Souza da Silva Pereira","JOSIVÂNIA DOS SANTOS SILVA","865.287.215-56","Minador","Macururé","27/07/2026","31648.145"],["Luiz Antoniel Paiva Galvão","MARISA SANTOS DO NASCIMENTO SILVA","005.412.075-63","Brejo do Burgo","Glória","28/07/2026","31646.109"],["Luiz Antoniel Paiva Galvão","MARIA JAQUELINE DA SILVA","360.846.068-30","Brejo do Burgo","Glória","28/07/2026","31646.108"],["Wandisson Santos de Jesus","EDIVA FERREIRA DA SILVA","006.161.055-09","Roçado","Chorrochó","28/07/2026","27309.440"],["Wandisson Santos de Jesus","MARIVALDO SILVA DE SOUZA","060.312.175-62","Roçado","Chorrochó","28/07/2026","27309.439"],["Wandisson Santos de Jesus","PASCOAL QUINTO DOS SANTOS","007.813.995-30","Roçado","Chorrochó","28/07/2026","27309.438"],["Wandisson Santos de jesus","HAGAMENON FRANÇA DO VALE","035.818.438-03","Roçado","Chorrochó","28/07/2026","27309.437"],["Caroline Evangelista de Queiroz","BENEDITA ALVES LOPES MAIA","002.980.955-05","ALTO VERMELHO","Abaré","28/07/2026","31616.115"],["Caroline Evangelista de Queiroz","ALAIDE BAHIA DA CRUZ","107.349.515-90","ALTO VERMELHO","Abaré","28/07/2026","31616.113"],["Caroline Evangelista de Queiroz","JOÃO ADRIANO SIMOES","015.691.025-03","LAGOA DO JOSE ALVES","Abaré","28/07/2026","31616.112"],["Caroline Evangelista de Queiroz","JILDENOR DIAS BARBOSA DOS SANTOS","040.336.255-50","LAGOA DO JOSE ALVES","Abaré","28/07/2026","31616.114"],["Migson Brayne Pamponet da Silva","RIVONILSON RAMOS DA CRUZ","291.849.058-08","Sansaite","Macururé","28/07/2026","31657.154"],["Migson Brayne Pamponet da Silva","ALEX SANDRO GOMES RAMOS","049.408.355-70","Sansaite","Macururé","28/07/2026","31657.153"],["Migson Brayne Pamponet da Silva","JOSEVAL RODRIGUES DA FONSECA","154.121.098-02","Sansaite","Macururé","28/07/2026","31657.152"],["Migson Brayne Pamponet da Silva","JOICE GOMES RAMOS","861.218.105-48","Sansaite","Macururé","28/07/2026","31657.151"],["Migson Brayne Pamponet da Silva","RAFAELA DA SILVA RAMOS","861.217.975-09","Sansaite","Macururé","27/07/2026","31657.150"],["Migson Brayne Pamponet da Silva","ELAINE JORGE DA SILVA RODRIGUES","135.479.428-10","Sansaite","Macururé","27/07/2026","31657.149"],["Migson Brayne Pamponet da Silva","RISAEL RAMOS DA CRUZ","057.513.425-93","Sansaite","Macururé","27/07/2026","31657.148"],["Migson Brayne Pamponet da Silva","JOSINEIDE DA CRUZ","027.981.885-80","Sansaite","Macururé","27/07/2026","31657.147"],["JOSEFA CRISTINA DE CARVALHO SANTOS","DAINE VICENTE BEZERRA","067.592.585-17","BAIXA FUNDA","Paulo Afonso","27/07/2026","26510.568"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ROSICLEIA TORQUATO DOS SANTOS","052.518.971-89","BAIXA FUNDA","Paulo Afonso","27/07/2026","26510.569"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ROSITELMA TORQUATO DOS SANTOS","052.207.601-73","BAIXA FUNDA","Paulo Afonso","27/07/2026","26510.570"],["JOSEFA CRISTINA DE CARVALHO SANTOS","VALDIRENE LIMA DE  JESUS","091.912.815-71","BAIXA FUNDA","Paulo Afonso","27/07/2026","26510.571"],["JOSEFA CRISTINA DE CARVALHO SANTOS","LUZIA TAVARES DA SILVA FERREIRA","082.913.275-99","LAGOA GRANDE","Paulo Afonso","24/07/2026","26510.573"],["Wandisson Santos de Jesus","SUELI SILVA DOS SANTOS","070.168.545-07","Roçado","Chorrochó","27/07/2026","27309.436"],["Wandisson Santos de Jesus","NAIR NOGUEIRA","020.194.595-90","Roçado","Chorrochó","27/07/2026","27309.435"],["Wandisson Santos de Jesus","GENILDA SILVA DOS SANTOS","087.611.655-14","Roçado","Chorrochó","27/07/2026","27309.434"],["Wandisson Santos de Jesus","FERNANDA REIS SANTOS COSTA","072.055.615-58","Roçado","Chorrochó","27/07/2026","27309.433"],["Caroline Evangelista de Queiroz","JIVALDO SIMOES","000.759.775-40","LAGOA DO JOSE ALVES","Abaré","27/07/2026","31616.110"],["Caroline Evangelista de Queiroz","AMILTON JOSÉ PAIVA DA SILVA","096.430.635-26","LAGOA DO JOSE ALVES","Abaré","27/07/2026","31616.109"],["Caroline Evangelista de Queiroz","CLAUDEANE SOUZA OLIVEIRA","075.827.175-11","LAGOA DO JOSE ALVES","Abaré","27/07/2026","31616.108"],["Caroline Evangelista de Queiroz","ADIMILSON SIMÕES DA SILVA","200.983.548-41","LAGOA DO JOSE ALVES","Abaré","27/07/2026","31616.111"],["Luiz Antoniel Paiva Galvão","ANA PATRÍCIA DO NASCIMENTO SILVA","864.300.025-60","Brejo do Burgo","Glória","27/07/2026","31646.107"],["Luiz Antoniel Paiva Galvão","SIMARA RIBEIRO DO NASCIMENTO","864.834.925-70","Brejo do Burgo","Glória","27/07/2026","31646.106"],["JOSEFA CRISTINA DE CARVALHO SANTOS","INIA SILVA NASCIMENTO","163.391.117-93","Baixa Funda","Paulo Afonso","24/07/2026","26510.564"],["JOSEFA CRISTINA DE CARVALHO SANTOS","PATRICIA DA SILVA DE JESUS","499.649.298-89","BAIXA FUNDA","Paulo Afonso","24/07/2026","26510.566"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ROBERLANIA BEZERRA DA SILVA","104.081.794-73","LAGOA GRANDE","Paulo Afonso","23/07/2026","26510.558"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARIA VIVIANE DOS SANTOS ANDRADE","047.351.335-85","LAGOA GRANDE","Paulo Afonso","23/07/2026","26510.559"],["JOSEFA CRISTINA DE CARVALHO SANTOS","JESSICA BARROS DE LIMA","099.244.865-44","LAGOA GRANDE","Paulo Afonso","23/07/2026","26510.560"],["Wandisson Santos de Jesus","AGMAR FONSECA COSTA","035.773.595-10","Roçado","Chorrochó","23/07/2026","27309.432"],["Wandisson Santos de Jesus","MARIZETE RODRIGUES DA SILVA","070.275.935-05","Roçado","Chorrochó","23/07/2026","27309.431"],["Wandisson Santos de Jesus","JOAO BISPO DE OLIVEIRA","469.588.605-78","Roçado","Chorrochó","23/07/2026","27309.430"],["Wandisson Santos de Jesus","FRANCISCO FONSECA DE ARAUJO","492.316.775-00","Roçado","Chorrochó","23/07/2026","27309.429"],["Estella Souza da Silva Pereira","CARMEN ANDREA RAMOS DA SILVA","009.724.565-89","Riacho dos caldeirões","Macururé","22/07/2026","31648.141"],["Estella Souza da Silva Pereira","MARIA JOSIANE LIMA SILVA","862.059.985-21","Riacho dos caldeirões","Macururé","22/07/2026","31648.140"],["Estella Souza da Silva Pereira","JOSAFÁ DA CRUZ","299.164.128-20","Riacho dos caldeirões","Macururé","22/07/2026","31648.139"],["Estella Souza da Silva Pereira","MARIA JOSÉ DOS SANTOS","039.262.175-45","Riacho dos caldeirões","Macururé","22/07/2026","31648.138"],["Wandisson Santos de Jesus","ANTONIO DO NASCIMENTO SANTOS","891.234.845-00","São José","Chorrochó","22/07/2026","27309.428"],["Wandisson Santos de Jesus","DANIELE RIBEIRO DA CRUZ","086.802.405-83","São José","Chorrochó","22/07/2026","27309.427"],["Wandisson Santos de Jesus","JUSTINO ALVES MOREIRA","107.609.228-45","São José","Chorrochó","22/07/2026","27309.426"],["JOSEFA CRISTINA DE CARVALHO SANTOS","VANESSA DA CONCEIÇÃO SA","030.732.375-77","LAGOA GRANDE","Paulo Afonso","22/07/2026","26510.554"],["JOSEFA CRISTINA DE CARVALHO SANTOS","PATRICIA FERREIRA DOS SANTOS","031.106.775-12","LAGOA GRANDE","Paulo Afonso","22/07/2026","26510.555"],["JOSEFA CRISTINA DE CARVALHO SANTOS","JOELMA PEREIRA MONTEIRO","026.321.565-21","LAGOA GRANDE","Paulo Afonso","22/07/2026","26510.556"],["Migson Brayne Pamponet da Silva","PEDRO HENRIQUE PESSOA SILVA","055.852.335-80","sansaite","Macururé","21/07/2026","31657.143"],["Migson Brayne Pamponet da Silva","TAMIRES GOMES E SILVA CRUZ","059.368.165-75","sansaite","Macururé","21/07/2026","31657.142"],["Migson Brayne Pamponet da Silva","IARA SOUZA LIMA","050.060.555-61","Sansaite","Macururé","20/07/2026","31657.141"],["Migson Brayne Pamponet da Silva","JOELSON DA CRUZ","040.557.755-98","Sansaite","Macururé","20/07/2026","31657.140"],["Migson Brayne Pamponet da Silva","MARICELIA GOMES DA CRUZ","001.225.945-41","Sansaite","Macururé","20/07/2026","31657.139"],["Migson Brayne Pamponet da Silva","KAROLAYNE DA CRUZ BARBOSA","859.143.945-70","Sansaite","Macururé","20/07/2026","31657.138"],["Migson Brayne Pamponet da Silva","JOSILMA DA CRUZ BARBOSA","283.904.098-01","Sansaite","Macururé","18/07/2026","31657.137"],["Migson Brayne Pamponet da Silva","DOJIVALDO GOMES DA SILVA","861.218.425-80","Sansaite","Macururé","18/07/2026","31657.136"],["Migson Brayne Pamponet da Silva","ADENILTON GOMES DA SILVA","261.937.818-46","Serra do Tonan","Macururé","17/07/2026","31657.134"],["Migson Brayne Pamponet da Silva","EDVALTO GOMES DE SILVA","808.126.275-04","Serra do Tonan","Macururé","17/07/2026","31657.133"],["Estella Souza da Silva Pereira","MARIA ZILDA DOS SANTOS SILVA","121.612.275-05","Minador","Macururé","21/07/2026","31648.137"],["Estella Souza da Silva Pereira","EDVÂNIA DOS SANTOS SILVA","860.764.785-78","Minador","Macururé","21/07/2026","31648.136"],["Estella Souza da Silva Pereira","JOSINEIDE MARIA DOS SANTOS","865.472.975-94","Minador","Macururé","21/07/2026","31648.135"],["Estella Souza da Silva Pereira","MARIA CARMELITA RAMOS DA SILVA","014.909.945-21","Riacho dos caldeirões","Macururé","21/07/2026","31648.134"],["Estella Souza da Silva Pereira","MARIA DOS SANTOS SILVA","867.340.795-89","Minador","Macururé","20/07/2026","31648.133"],["Estella Souza da Silva Pereira","RANIELE MARIA DOS SANTOS ALVES","867.346.295-97","Minador","Macururé","20/07/2026","31648.132"],["Estella Souza da Silva Pereira","MARIA FRANCIELE ALVES OLIVEIRA","121.840.155-98","Minador","Macururé","20/07/2026","31648.131"],["Luiz Antoniel Paiva Galvão","ANALICE ALVES DA SILVA SANTOS","063.677.665-45","Brejo do Burgo","Glória","21/07/2026","31646.104"],["Luiz Antoniel Paiva Galvão","RONALDO VIEIRA DA SILVA","078.079.925-90","Brejo do Burgo","Glória","21/07/2026","31646.103"],["Luiz Antoniel Paiva Galvão","MARCIA GRACIETE DA SILVA","071.724.085-19","Brejo do Burgo","Glória","21/07/2026","31646.102"],["Wandisson Santos de Jesus","MARTINHA FERREIRA DO NASCIMENTO","029.318.365-16","São José","Chorrochó","21/07/2026","27309.425"],["Wandisson Santos de Jesus","DANIEL DA SILVA CARVALHO","109.414.325-13","São José","Chorrochó","21/07/2026","27309.424"],["Wandisson Santos de Jesus","BRAZ CONCEIÇÃO DO NASCIMENTO","931.777.475-04","São José","Chorrochó","21/07/2026","27309.423"],["JOSEFA CRISTINA DE CARVALHO SANTOS","DAIANE CAETANO DA SILVA","084.309.295-50","CASA DE PEDRA","Paulo Afonso","21/07/2026","26510.553"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARCOS ANTONIO MONTEIRO DE SA","956.994.495-15","CASA DE PEDRA","Paulo Afonso","21/07/2026","26510.551"],["JOSEFA CRISTINA DE CARVALHO SANTOS","CLAUDIONOR PEREIRA DA SILVA","937.421.425-34","LAGOA GRANDE","Paulo Afonso","21/07/2026","26510.549"],["JOSEFA CRISTINA DE CARVALHO SANTOS","LARISSA DE SOUZA BARBOSA","858.385.965-54","CASA DE PEDRA","Paulo Afonso","21/07/2026","26510.548"],["Wandisson Santos de Jesus","MARINEIDE DE JESUS SANTOS","054.960.535-52","São José","Chorrochó","20/07/2026","27309.422"],["Wandisson Santos de Jesus","MILENA DE JESUS SANTOS","079.813.825-48","São José","Chorrochó","20/07/2026","27309.421"],["Wandisson Santos de Jesus","GLEUKA JÉSSIA ALVES DE ANDRADE","525.585.828-52","São José","Chorrochó","20/07/2026","27309.420"],["Wandisson Santos de Jesus","ALICE RIBEIRO DO NASCIMENTO OLIVEIRA","001.749.815-54","São José","Chorrochó","20/07/2026","27309.419"],["Luiz Antoniel Paiva Galvão","DANIELE BARROS DA SILVA","866.638.355-05","Brejo do Burgo","Glória","20/07/2026","31646.101"],["Luiz Antoniel Paiva Galvão","JOSIANE GOMES XAVIER SANTOS","048.231.185-10","Pankarare","Glória","20/07/2026","31646.99"],["Estella Souza da Silva Pereira","FRANCISCO DE PAULA BISPO DE ARAÚJO","278.287.005-04","Várzea da Ema","Chorrochó","18/07/2026","31648.129"],["Estella Souza da Silva Pereira","DURVAL FLORENCIO DOS SANTOS","233.386.605-53","Várzea da Ema","Chorrochó","17/07/2026","31648.128"],["Estella Souza da Silva Pereira","GEISIANE SANTOS OLIVEIRA","004.566.365-36","Várzea da Ema","Chorrochó","18/07/2026","31648.130"],["Estella Souza da Silva Pereira","EDIANE MARIA DE ARAÚJO LIMA","050.090.165-16","Várzea da Ema","Macururé","17/07/2026","31648.127"],["Estella Souza da Silva Pereira","ELISANGELA MARIA ARAÚJO LIMA","090.796.365-09","Várzea da Ema","Chorrochó","17/07/2026","31648.126"],["Wandisson Santos de Jesus","ANTÔNIA VITÓRIA DE JESUS MOREIRA","868.599.215-01","Golf","Chorrochó","17/07/2026","27309.418"],["Wandisson Santos de Jesus","VILMA PEREIRA DANTAS","016.261.435-79","São José","Chorrochó","17/07/2026","27309.417"],["Wandisson Santos de Jesus","MARIA JOSE DA SILVA","061.200.065-67","São José","Chorrochó","17/07/2026","27309.416"],["Wandisson Santos de Jesus","GABRIELA SOARES DOS SANTOS","486.843.408-09","Golf","Chorrochó","17/07/2026","27309.415"],["Caroline Evangelista de Queiroz","JEOVANIA MACIEL SILVA SANTOS","087.816.505-31","ALTO VERMELHO","Abaré","17/07/2026","31616.104"],["Caroline Evangelista de Queiroz","MAILANE CARVALHO DE JESUS","121.477.395-88","LAGOA DO JOSE ALVES","Abaré","17/07/2026","31616.107"],["Caroline Evangelista de Queiroz","ADRIANA DA SILVA SANTOS","085.410.415-14","ALTO VERMELHO","Abaré","17/07/2026","31616.105"],["Caroline Evangelista de Queiroz","MARIA APARECIDA DA SILVA NASCIMENTO","067.436.885-17","LAGOA DO JOSE ALVES","Abaré","17/07/2026","31616.106"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARIA DE LOURDES CAVALCANTE DE ARAUJO","009.644.425-82","CASA DE PEDRA","Paulo Afonso","17/07/2026","26510.545"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MANOEL MESSIAS PEREIRA MAIA","548.978.315-04","CASA DE PEDRA","Paulo Afonso","17/07/2026","26510.546"],["Luiz Antoniel Paiva Galvão","MARIA APARECIDA NASCIMENTO BARROS","002.966.065-37","Brejo do Burgo","Glória","17/07/2026","31646.98"],["Luiz Antoniel Paiva Galvão","GISLANE VIEIRA SILVA XAVIER","080.573.125-30","Brejo do Burgo","Glória","17/07/2026","31646.97"],["Luiz Antoniel Paiva Galvão","JOSILEIDE NASCIMENTO RIBEIRO","028.646.525-60","Brejo do Burgo","Glória","17/07/2026","31646.96"],["Luiz Antoniel Paiva Galvão","JEANE DO NASCIMENTO RIBEIRO","048.505.705-00","Brejo do Burgo","Glória","17/07/2026","31646.95"],["Caroline Evangelista de Queiroz","MARIA DO SOCORRO BARBOSA SANTOS","005.497.615-43","ALDEIA TUXI","Abaré","16/07/2026","31616.102"],["Caroline Evangelista de Queiroz","MARIA GOMES MOURA DO SOCORRO","007.779.715-93","ALDEIA TUXI","Abaré","16/07/2026","31616.101"],["Caroline Evangelista de Queiroz","RENATO DE JESUS SILVA","089.423.945-74","ALDEIA TUXI","Abaré","16/07/2026","31616.100"],["Caroline Evangelista de Queiroz","CEZAR ANTONIO DOS SANTOS","939.233.685-34","ALDEIA TUXI","Abaré","16/07/2026","31616.103"],["Estella Souza da Silva Pereira","EDLEUZA ALVES DOS SANTOS","069.508.605-79","Minador","Macururé","16/07/2026","31648.125"],["Estella Souza da Silva Pereira","EDINALVA ALVES DOS SANTOS","861.228.485-65","Minador","Macururé","16/07/2026","31648.124"],["Estella Souza da Silva Pereira","EDINAIDE ALVES DOS SANTOS","084.512.095-64","Minador","Macururé","16/07/2026","31648.123"],["JOSEFA CRISTINA DE CARVALHO SANTOS","SANDRA MARIA DA SILVA","041.195.795-30","CASA DE PEDRA","Paulo Afonso","16/07/2026","26510.542"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARIA NILZA DOS SANTOS NASCIMENTO","068.237.615-98","CASA DE PEDRA","Paulo Afonso","16/07/2026","26510.543"],["JOSEFA CRISTINA DE CARVALHO SANTOS","EDILENE MARTINS DA SILVA","083.696.975-85","CASA DE PEDRA","Paulo Afonso","16/07/2026","26510.544"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARINEIDE LIMA SANTOS","021.455.175-02","CASA DE PEDRA","Paulo Afonso","16/07/2026","26510.547"],["Wandisson Santos de Jesus","ANA CARLA SANTOS DA SILVA","067.389.725-71","São José","Chorrochó","16/07/2026","27309.414"],["Wandisson Santos de Jesus","AMÉRICO MARQUES RAMOS","469.361.815-20","São José","Chorrochó","16/07/2026","27309.413"],["Wandisson Santos de Jesus","MANOEL TEIXEIRA DOS SANTOS","639.034.234-91","Golf","Chorrochó","16/07/2026","27309.412"],["Migson Brayne Pamponet da Silva","ADENILSON GOMES DA SILVA","000.571.455-98","Serra do Tonan","Macururé","16/07/2026","31657.132"],["Migson Brayne Pamponet da Silva","ELIANE GOMES DA COSTA","063.846.795-07","Serra do Tonan","Macururé","16/07/2026","31657.131"],["Migson Brayne Pamponet da Silva","EDENICE MARIA DOS SANTOS FELIZ","961.287.805-63","Serra do Tonan","Macururé","16/07/2026","31657.130"],["Migson Brayne Pamponet da Silva","ALECIA MARIA BARBOSA LIMA","071.844.075-71","Serra do Tonan","Macururé","09/07/2026","31657.128"],["Migson Brayne Pamponet da Silva","DILMA MARINA ALVES DA SILVA GOMES","005.976.875-44","Serra do Tonan","Macururé","09/07/2026","31657.127"],["Estella Souza da Silva Pereira","MARIA JOVELINA DOS SANTOS","074.029.395-88","Riacho dos caldeirões","Macururé","13/07/2026","31648.122"],["Estella Souza da Silva Pereira","ELIETE ALVES DOS SANTOS","858.792.855-45","Minador","Macururé","13/07/2026","31648.121"],["Estella Souza da Silva Pereira","JAIANE RODRIGUES PEREIRA","125.243.885-06","Minador","Macururé","13/07/2026","31648.120"],["Wandisson Santos de Jesus","LUCIANO MENDES DE ARAUJO","804.428.625-04","São José","Chorrochó","13/07/2026","27309.411"],["Wandisson Santos de Jesus","GEANE MENDES DOS SANTOS","024.864.025-94","São José","Chorrochó","13/07/2026","27309.410"],["Wandisson Santos de Jesus","DEJANIRA DOS SANTOS DE OLIVEIRA","001.547.235-33","São José","Chorrochó","13/07/2026","27309.409"],["JOSEFA CRISTINA DE CARVALHO SANTOS","MARCIA MARIA PEREIRA DE SOUZA","858.387.715-77","LAGOA GRANDE","Paulo Afonso","13/07/2026","26510.541"],["Caroline Evangelista de Queiroz","JOSE FABIO FERREIRA FERNANDES","063.954.193-31","ALDEIA TUXI","Abaré","13/07/2026","31616.98"],["Caroline Evangelista de Queiroz","CARLEUZA DA CRUZ DOS SANTOS","050.062.535-25","ALDEIA TUXI","Abaré","13/07/2026","31616.97"],["Caroline Evangelista de Queiroz","DULCINEIA DO NASCIMENTO BARBALHO","136.258.828-84","ALDEIA TUXI","Abaré","13/07/2026","31616.99"],["Luiz Antoniel Paiva Galvão","MARIA SANTOS SILVA RIBEIRO","102.622.325-37","Pankarare","Glória","13/07/2026","31646.94"],["Luiz Antoniel Paiva Galvão","JAQUELINE RIBEIRO DE SOUZA","858.788.085-36","Pankarare","Glória","13/07/2026","31646.93"],["Luiz Antoniel Paiva Galvão","LUANA GOMES XAVIER VIEIRA","024.553.295-18","Pankarare","Glória","13/07/2026","31646.92"],["Luiz Antoniel Paiva Galvão","GERONIMO ANDRÉ SOBRINHO","017.296.555-13","Pankarare","Glória","13/07/2026","31646.91"],["Estella Souza da Silva Pereira","MARIA EDUARDA RODRIGUES SILVA GIMENES","859.165.615-63","Várzea da Ema","Chorrochó","11/07/2026","31648.119"],["Estella Souza da Silva Pereira","ADAILTON GOMES REIS","023.898.155-02","Várzea da Ema","Chorrochó","11/07/2026","31648.118"],["Estella Souza da Silva Pereira","JOSÉ RAIMUNDO ANTONIO DA SILVA","755.252.405-72","Várzea da Ema","Chorrochó","11/07/2026","31648.117"],["Estella Souza da Silva Pereira","RIGOBERTO RODRIGUES VARJÃO","050.090.155-44","Várzea da Ema","Chorrochó","11/07/2026","31648.116"],["Estella Souza da Silva Pereira","ANA PAULA MARIA DOS SANTOS","088.534.385-92","Minador","Macururé","10/07/2026","31648.115"],["Estella Souza da Silva Pereira","ANTONIO PEREIRA MAIA JUNIOR","865.417.585-06","Minador","Macururé","10/07/2026","31648.114"],["Estella Souza da Silva Pereira","TAMIRIS DOS SANTOS SILVA","126.110.805-18","Minador","Macururé","10/07/2026","31648.113"],["Wandisson Santos de Jesus","GILVANE ARAUJO DO NASCIMENTO","042.144.465-77","São José","Chorrochó","10/07/2026","27309.408"],["Wandisson Santos de Jesus","ALCIENE ARAUJO DE OLIVEIRA","024.100.045-98","São José","Chorrochó","10/07/2026","27309.407"],["Wandisson Santos de Jesus","ELIANE ALVES DE OLIVEIRA","030.039.095-50","São José","Chorrochó","10/07/2026","27309.406"],["Wandisson Santos de Jesus","BEATRIZ SOARES DAMASCENO","087.373.625-77","São José","Chorrochó","10/07/2026","27309.405"],["Caroline Evangelista de Queiroz","GILBERTO DIAS DOS SANTOS","007.919.225-45","LAGOA DO JOSE ALVES","Abaré","10/07/2026","31616.95"],["Caroline Evangelista de Queiroz","RENATA BARBOSA DA SILVA","084.365.185-78","ALTO VERMELHO","Abaré","10/07/2026","31616.96"],["JOSEFA CRISTINA DE CARVALHO SANTOS","IVETE LIMA DE SÁ","858.388.285-10","LAGOA GRANDE","Paulo Afonso","10/07/2026","26510.538"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ANA PAULA FERREIRA DOS SANTOS","099.652.175-56","CASA DE PEDRA","Paulo Afonso","10/07/2026","26510.539"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ROSEANE  SOARES DA SILVA","022.187.875-04","CASA DE PEDRA","Paulo Afonso","10/07/2026","26510.540"],["JOSEFA CRISTINA DE CARVALHO SANTOS","GIOVANA SOUZA IZIDIO","866.898.975-83","LAGOA GRANDE","Paulo Afonso","10/07/2026","26510.536"],["JOSEFA CRISTINA DE CARVALHO SANTOS","JOSEFA FERREIRA DA SILVA","074.248.425-44","LAGOA GRANDE","Paulo Afonso","09/07/2026","26510.537"],["Luiz Antoniel Paiva Galvão","ROBERTA RIBEIRO DA SILVA","103.628.365-82","Pankarare","Glória","10/07/2026","31646.90"],["Luiz Antoniel Paiva Galvão","MAIARA DE BARROS TEIXEIRA","100.082.235-48","Pankarare","Glória","10/07/2026","31646.89"],["Luiz Antoniel Paiva Galvão","ADEILMA MARIA DA SILVA","031.342.625-25","Pankarare","Glória","10/07/2026","31646.88"],["Estella Souza da Silva Pereira","RAFAELA DOS SANTOS MAIA","084.412.215-70","Minador","Macururé","09/07/2026","31648.112"],["Estella Souza da Silva Pereira","MEIRELAINE DE LIMA","110.664.555-38","Minador","Macururé","09/07/2026","31648.111"],["Estella Souza da Silva Pereira","LIEDSON ANDRADE MACIEL","096.067.305-90","Minador","Macururé","09/07/2026","31648.110"],["Caroline Evangelista de Queiroz","GILDEVANDRO BARBOSA DE SOUZA","072.056.395-06","ALTO VERMELHO","Abaré","09/07/2026","31616.94"],["Caroline Evangelista de Queiroz","JAINE MACIEL SILVA SANTOS","095.850.085-13","ALTO VERMELHO","Abaré","09/07/2026","31616.91"],["Caroline Evangelista de Queiroz","IONE BARBOSADE SOUZA","084.033.525-30","ALTO VERMELHO","Abaré","09/07/2026","31616.92"],["Caroline Evangelista de Queiroz","MARIA ANUNCIADA BARBOSA DE CARVALHO NETA","867.807.035-83","ALTO VERMELHO","Abaré","09/07/2026","31616.93"],["Luiz Antoniel Paiva Galvão","SILVANIA RIBEIRO DO NASCIMENTO","019.187.365-96","Pankarare","Glória","09/07/2026","31646.87"],["Luiz Antoniel Paiva Galvão","VANESSA RIBEIRO BARBOSA SILVA","045.565.765-39","Pankarare","Glória","09/07/2026","31646.86"],["Luiz Antoniel Paiva Galvão","LAIANE NASCIMENTO MOTA","084.820.065-92","Pankarare","Glória","09/07/2026","31646.85"],["Luiz Antoniel Paiva Galvão","DIVANEIDE RIBEIRO NASCIMENTO FEITIZA","054.959.295-43","Pankarare","Glória","09/07/2026","31646.84"],["Wandisson Santos de Jesus","VITOR PEREIRA DANTAS","002.520.365-73","Golf","Chorrochó","09/07/2026","27309.404"],["Wandisson Santos de Jesus","ROSEANE TEIXEIRA ALVES","053.178.235-28","Golf","Chorrochó","09/07/2026","27309.403"],["Wandisson Santos de Jesus","LUIZ TEIXEIRA ALVES","959.678.005-06","Golf","Chorrochó","09/07/2026","27309.402"],["Wandisson Santos de Jesus","MARIA DE LOURDES TEIXEIRA DOS SANTOS","078.537.665-80","Golf","Chorrochó","09/07/2026","27309.401"],["Estella Souza da Silva Pereira","LUCIANA OLIVEIRA ALVES SANTOS","043.730.485-09","Várzea da Ema","Chorrochó","08/07/2026","31648.109"],["Estella Souza da Silva Pereira","JOSE CASSIMIRO DE OLIVEIRA","512.887.375-72","Várzea da Ema","Chorrochó","08/07/2026","31648.108"],["Estella Souza da Silva Pereira","JOÃO ALVES DA SILVA","945.759.915-20","Várzea da Ema","Chorrochó","08/07/2026","31648.107"],["Estella Souza da Silva Pereira","ADRIANA CERQUEIRA DOS SANTOS","112.829.285-89","Várzea da Ema","Chorrochó","07/07/2026","31648.106"],["Estella Souza da Silva Pereira","ROSENILDE OLIVEIRA DA SILVA","015.134.575-94","Várzea da Ema","Chorrochó","07/07/2026","31648.105"],["Estella Souza da Silva Pereira","MARIA ANAILMA DE OLIVEIRA PIRES MARTINS","270.674.458-84","Várzea da Ema","Chorrochó","07/07/2026","31648.104"],["Wandisson Santos de Jesus","JADENICE TOLÊDO DOS SANTOS SIMÕES","003.133.995-65","Golf","Chorrochó","08/07/2026","27309.400"],["Wandisson Santos de Jesus","ELISANGELA ALVES DOS SANTOS","868.599.215-01","Golf","Chorrochó","08/07/2026","27309.399"],["Wandisson Santos de Jesus","JILSON GABRIEL ALVES DO NASCIMENTO","087.556.675-89","Golf","Chorrochó","08/07/2026","27309.398"],["Wandisson Santos de Jesus","JOSÉLIA PEREIRA DOS SANTOS","024.729.435-71","Golf","Chorrochó","08/07/2026","27309.397"],["JOSEFA CRISTINA DE CARVALHO SANTOS","SILEIDE IZIDORIO DE MELO","071.612.135-25","CASA DE PEDRA","Paulo Afonso","08/07/2026","26510.534"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ISMAILDE DE SOUZA SILVA","866.008.025-45","CASA DE PEDRA","Paulo Afonso","08/07/2026","26510.533"],["JOSEFA CRISTINA DE CARVALHO SANTOS","GLEISIANE BARROS DE LIMA","099.243.995-79","CASA DE PEDRA","Paulo Afonso","08/07/2026","26510.535"],["Caroline Evangelista de Queiroz","RIZADALVA ALVES DOS SANTOS","005.603.415-63","ALDEIA TUXI","Abaré","08/07/2026","31616.89"],["Caroline Evangelista de Queiroz","INACIO MARTINS DE MORAIS","045.175.515-47","ALDEIA TUXI","Abaré","08/07/2026","31616.88"],["Caroline Evangelista de Queiroz","EDILEIDE IRENE DOS SANTOS","031.279.895-47","ALDEIA TUXI","Abaré","08/07/2026","31616.87"],["Caroline Evangelista de Queiroz","FABIO JUNIOR DE MENEZES GOMES","035.897.835-16","ALDEIA TUXI","Abaré","08/07/2026","31616.90"],["Luiz Antoniel Paiva Galvão","LUCIVANIA ROSA DE MOTA","022.881.975-01","Pankarare","Glória","08/07/2026","31646.83"],["Migson Brayne Pamponet da Silva","MAIARA ARCANJA BERNARDO SILVA","070.700.825-50","Serra do Tonan","Macururé","08/07/2026","31657.124"],["Migson Brayne Pamponet da Silva","CLECIA APARECIDA GOMES DA SILVA","070.372.505-03","Serra do Tonan","Macururé","08/07/2026","31657.125"],["Migson Brayne Pamponet da Silva","ALDERIVA GOMES DA SILVA","033.081.025-10","Serra do Tonan","Macururé","08/07/2026","31657.126"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ROSIMAR SANTOS DA SILVA","083.440.364-10","CASA DE PEDRA","Paulo Afonso","07/07/2026","26510.532"],["JOSEFA CRISTINA DE CARVALHO SANTOS","ELAINE ANA DA SILVA","858.316.535-10","CASA DE PEDRA","Paulo Afonso","07/07/2026","26510.531"],["Caroline Evangelista de Queiroz","VANESSA DE CARVALHO SANTOS","069.302.825-45","ALDEIA TUXI","Abaré","07/07/2026","31616.85"],["Caroline Evangelista de Queiroz","JÉSSICA THAÍS SOARES DA SILVA","065.420.525-69","ALDEIA TUXI","Abaré","07/07/2026","31616.84"],["Caroline Evangelista de Queiroz","ADENILSA LAURINDA DA SILVA","006.122.325-57","ALDEIA TUXI","Abaré","07/07/2026","31616.86"],["Wandisson Santos de Jesus","JILAENE ALVES DOS SANTOS","030.777.355-80","Golf","Chorrochó","07/07/2026","27309.396"],["Wandisson Santos de Jesus","MARIA DE LOURDES ALVES DA SILVA","754.602.035-20","Golf","Chorrochó","07/07/2026","27309.395"],["Wandisson Santos de Jesus","SEBASTIANA ALVES BARBALHO","425.442.968-10","Golf","Chorrochó","07/07/2026","27309.394"],["Wandisson Santos de Jesus","LUCIVÂNIA ALVES DOS SANTOS","053.386.995-16","Golf","Chorrochó","07/07/2026","27309.393"],["Caroline Evangelista de Queiroz","ADRIANA DOS SANTOS DE JESUS","004.716.465-47","ALDEIA TUXI","Abaré","06/07/2026","31616.81"],["Caroline Evangelista de Queiroz","IANDRA DO NASCIMENTO SANTOS","045.487.375-10","ALDEIA TUXI","Abaré","06/07/2026","31616.82"],["Caroline Evangelista de Queiroz","MICHELLY DA SILVA CRUZ","111.572.465-75","ALDEIA TUXI","Abaré","06/07/2026","31616.83"],["Luiz Antoniel Paiva Galvão","ALECILDA RODRIGUES VIEIRA","050.084.785-16","Pankarare","Glória","06/07/2026","31646.82"],["Luiz Antoniel Paiva Galvão","LUCIMARA VIEIRA RIBEIRO","555.604.742-15","Pankarare","Glória","06/07/2026","31646.81"],["Luiz Antoniel Paiva Galvão","LUCIANA VIEIRA RIBEIRO BARBOSA","015.753.712-94","Pankarare","Glória","06/07/2026","31646.80"],["Luiz Antoniel Paiva Galvão","MAIARA RIBEIRO GAMA","112.392.505-41","Pankarare","Glória","03/07/2026","31646.79"],["Luiz Antoniel Paiva Galvão","MICHELE RIBEIRO GAMA","865.011.895-00","Pankarare","Glória","03/07/2026","31646.78"],["Luiz Antoniel Paiva Galvão","ADEZUILMA DA SILVA","002.977.505-18","Pankarare","Glória","03/07/2026","31646.77"],["Luiz Antoniel Paiva Galvão","THAYNARA SILVA BARROS","101.686.065-00","Pankarare","Glória","01/07/2026","31646.76"],["Luiz Antoniel Paiva Galvão","MAIRA MARIA DE BARROS TEIXEIRA","076.291.405-09","Pankarare","Glória","01/07/2026","31646.75"],["Luiz Antoniel Paiva Galvão","MÔNICA MARIA RIBEIRO GAMA","003.000.025-48","Pankarare","Glória","01/07/2026","31646.74"]];
    const coletumVisitas = rawData.map(r => ({
        tecnico: r[0],
        beneficiario: r[1],
        cpf: r[2],
        comunidade: r[3],
        municipio: r[4],
        data: r[5],
        id: r[6]
    }));

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

    // 1. Identifica linhas e links da tabela de execuções
    const trs = Array.from(document.querySelectorAll('table tbody tr')).filter(tr => tr.innerText.trim().length > 10);
    const linksLupa = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"]'));
    const urlsExecucoes = Array.from(new Set(linksLupa.map(a => a.href)));

    console.log(`📋 Linhas na tabela do SIGATER: ${trs.length} | Links /read/ únicos: ${urlsExecucoes.length}`);

    if (urlsExecucoes.length === 0) {
        alert('Abra a tela "LISTAGEM - EXECUÇÕES" da atividade no SIGATER.');
        return;
    }

    // Painel Visual Flutuante
    const antigo = document.getElementById('painelAuditoriaEstrita7');
    if (antigo) antigo.remove();

    const div = document.createElement('div');
    div.id = 'painelAuditoriaEstrita7';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;width:580px;max-height:85vh;overflow-y:auto;background:#181a20;color:#fff;padding:20px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:15px;"><i class="fas fa-search"></i> Auditoria Estrita 1-para-1 (Mês 7/2026)</strong>
            <button onclick="document.getElementById('painelAuditoriaEstrita7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:16px;">✖</button>
        </div>
        <p id="statusProgresso" style="margin:0;color:#ccc;">Lendo as ${urlsExecucoes.length} execuções no SIGATER...</p>
        <div style="width:100%;background:#2a2d36;height:12px;border-radius:6px;margin:12px 0;overflow:hidden;">
            <div id="barraProgresso" style="width:0%;height:100%;background:linear-gradient(90deg, #00bcd4, #00e676);transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    // 2. Leitura paralela das páginas
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

                    const codExec = url.match(/\/read\/(\d+)/) ? url.match(/\/read\/(\d+)/)[1] : url;

                    sigaterLancados.push({
                        codExec,
                        url,
                        nome: nomeBeneficiario.trim(),
                        cpf: cpfBeneficiario.trim(),
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

    // 3. Cruzamento Estrito 1-para-1 (Sem reutilizar execução!)
    const lancadosConfirmados = [];
    const pendentesNaoLancados = [];
    const execucoesUsadas = new Set();

    // Rodada 1: Match Exato por CPF e Nome Compatível
    coletumVisitas.forEach(col => {
        const cpfLimpoCol = cleanCpf(col.cpf);
        const nomeNormCol = normalizar(col.beneficiario);

        let matchSig = null;

        // Procura primeiro execução com mesmo CPF E nome compatível
        if (cpfLimpoCol.length >= 8) {
            matchSig = sigaterLancados.find(sig => {
                if (execucoesUsadas.has(sig.codExec)) return false;
                const sigCpf = cleanCpf(sig.cpf);
                if (sigCpf.includes(cpfLimpoCol) || cpfLimpoCol.includes(sigCpf)) {
                    // Só aceita se o nome também for parecido (para evitar validar 2 pessoas diferentes com mesmo CPF)
                    if (similaridade(col.beneficiario, sig.nome) >= 0.50 || sig.htmlBruto.includes(nomeNormCol)) {
                        return true;
                    }
                }
                return false;
            });
        }

        // Se não achou por CPF, procura por similaridade de nome alta
        if (!matchSig) {
            matchSig = sigaterLancados.find(sig => {
                if (execucoesUsadas.has(sig.codExec)) return false;
                if (similaridade(col.beneficiario, sig.nome) >= 0.75) return true;
                if (sig.htmlBruto.includes(nomeNormCol) && nomeNormCol.split(' ').length >= 2) return true;
                return false;
            });
        }

        if (matchSig) {
            execucoesUsadas.add(matchSig.codExec);
            lancadosConfirmados.push({
                coletum: col,
                sigater: matchSig
            });
        } else {
            pendentesNaoLancados.push(col);
        }
    });

    // 4. Diagnóstico de Linhas
    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 RESULTADO DA AUDITORIA ESTRITA (VISITAS AVALIATIVAS - MÊS 7/2026):
- Total de Fichas no Coletum: %c${coletumVisitas.length}%c
- Execuções lidas no SIGATER: %c${sigaterLancados.length}%c
- Execuções Únicas Confirmadas: %c${lancadosConfirmados.length}%c
- ⚠️ TOTAL QUE FALTA LANÇAR NO SIGATER: %c${pendentesNaoLancados.length}%c`,
        'font-weight: bold; font-size: 14px; color: #fff;',
        'color: #00e676; font-weight: bold;', 'color: #fff;',
        'color: #00bcd4; font-weight: bold;', 'color: #fff;',
        'color: #29b6f6; font-weight: bold;', 'color: #fff;',
        'color: #ff1744; font-weight: bold; font-size: 16px;', 'color: #fff;'
    );
    console.log('%c====================================================================', 'color: #888');

    // Agrupa por técnico
    const pendentesPorTecnico = {};
    pendentesNaoLancados.forEach(p => {
        const t = p.tecnico || 'Não Informado';
        if (!pendentesPorTecnico[t]) pendentesPorTecnico[t] = [];
        pendentesPorTecnico[t].push(p);
    });

    console.log(`%c⚠️ BENEFICIÁRIOS PENDENTES NO SIGATER (${pendentesNaoLancados.length}):`, 'color: #ff5252; font-size: 15px; font-weight: bold;');
    console.table(pendentesNaoLancados.map((p, i) => ({
        '#': i + 1,
        'Beneficiário': p.beneficiario,
        'CPF': p.cpf,
        'Técnico': p.tecnico,
        'Comunidade': p.comunidade,
        'Município': p.municipio,
        'Data': p.data,
        'ID Coletum': p.id
    })));

    // 5. Painel Flutuante Atualizado
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:${pendentesNaoLancados.length > 0 ? '#ff5252' : '#00e676'};font-size:15px;">
                ${pendentesNaoLancados.length > 0 ? `⚠️ Faltam ${pendentesNaoLancados.length} Visitas Avaliativas` : '✅ Todas as Visitas Lançadas!'}
            </strong>
            <button onclick="document.getElementById('painelAuditoriaEstrita7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:16px;">✖</button>
        </div>
        <p style="margin:0 0 10px 0;color:#ccc;">
            Meta Coletum: <strong>${coletumVisitas.length}</strong> | Lançados na tela: <strong style="color:#00bcd4;">${sigaterLancados.length}</strong> | Pendentes Reais: <strong style="color:#ff5252;font-size:15px;">${pendentesNaoLancados.length}</strong>
        </p>
        ${Object.keys(pendentesPorTecnico).length > 0 ? `
            <div style="background:#22252e;padding:10px;border-radius:8px;margin-bottom:12px;">
                <strong style="color:#ffd54f;display:block;margin-bottom:6px;">Pendências por Técnico:</strong>
                ${Object.keys(pendentesPorTecnico).map(t => `
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;">
                        <span>👤 ${t}</span>
                        <strong style="color:#ff5252;">${pendentesPorTecnico[t].length} pendentes</strong>
                    </div>
                `).join('')}
            </div>
        ` : ''}
        <div style="max-height:300px;overflow-y:auto;">
            ${pendentesNaoLancados.map((p, i) => `
                <div style="background:#22252e;padding:10px;border-radius:6px;margin-bottom:8px;border-left:4px solid #ff5252;">
                    <strong style="color:#fff;font-size:13px;">${i+1}. ${p.beneficiario}</strong><br>
                    <small style="color:#bbb;">CPF: ${p.cpf} | ${p.comunidade} (${p.municipio})</small><br>
                    <small style="color:#ffd54f;">👤 Técnico: ${p.tecnico} • 📅 Data: ${p.data} (ID: ${p.id})</small>
                </div>
            `).join('')}
        </div>
        <button id="btnCopiarPendentesEstrito" style="width:100%;margin-top:12px;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:13px;">
            📋 Copiar Lista dos ${pendentesNaoLancados.length} Pendentes
        </button>
        <button id="btnBaixarCsvPendentesEstrito" style="width:100%;margin-top:8px;padding:10px;background:#00e676;color:#000;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:13px;">
            📥 Baixar CSV dos Pendentes (Excel)
        </button>
    `;

    document.getElementById('btnCopiarPendentesEstrito').onclick = function() {
        const txt = pendentesNaoLancados.map((p, i) => `${i+1}. ${p.beneficiario} | CPF: ${p.cpf} | Técnico: ${p.tecnico} - ${p.comunidade} (${p.municipio}) - Data: ${p.data}`).join('\n');
        navigator.clipboard.writeText(txt).then(() => alert(`Lista dos ${pendentesNaoLancados.length} pendentes copiada!`));
    };

    document.getElementById('btnBaixarCsvPendentesEstrito').onclick = function() {
        let csvContent = '\uFEFF#;Técnico;Beneficiário;CPF;Comunidade;Município;Data Coletum;ID Coletum\n';
        pendentesNaoLancados.forEach((p, i) => {
            csvContent += `"${i+1}";"${p.tecnico}";"${p.beneficiario}";"${p.cpf}";"${p.comunidade}";"${p.municipio}";"${p.data}";"${p.id}"\n`;
        });
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Pendentes_Visitas_Avaliativas_Julho_2026_Estrito.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };
})();
