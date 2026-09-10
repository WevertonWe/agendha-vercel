"""
Script de Automação Playwright para Download em Lote de Atestes no SIGATER (Bahia Sem Fome)
Compatível com o portal BahiaTer SIGATER (https://bahiater.sigater.ba.gov.br)

Como usar:
1. Execute: python scripts/sigater_downloader.py --atividade "CARACTERIZAÇÃO"
2. O navegador Chromium abrirá diretamente no portal BahiaTer SIGATER.
3. Faça o login normalmente.
4. Navegue até a tela onde os beneficiários / botões de ateste estão listados.
   (Se estiver na grade de números, clique no número do mês para abrir os beneficiários).
5. Volte no terminal e pressione [ENTER]. O script baixará e organizará todos os atestes!
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sigater_downloader")


def main():
    parser = argparse.ArgumentParser(description="Robô de Download e Organização Automática de Atestes do SIGATER")
    parser.add_argument("--url", default="https://bahiater.sigater.ba.gov.br", help="URL do portal BahiaTer SIGATER")
    parser.add_argument("--atividade", default="CARACTERIZAÇÃO", help="Nome ou código da atividade alvo")
    parser.add_argument("--headless", action="store_true", help="Executar sem interface gráfica")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright não está instalado. Execute: pip install playwright && playwright install chromium")
        sys.exit(1)

    from app.modules.bahia_sem_fome.services.sigater_service import (
        extrair_metadados_ateste_pdf,
        organizar_ateste_no_disco_local
    )
    from app.services.scanner_service import get_base_storage_path

    storage_base = get_base_storage_path()
    logger.info(f"📂 Diretório base de destino dos técnicos: {storage_base}")

    with sync_playwright() as p:
        logger.info("🚀 Iniciando navegador para conexão com o BahiaTer SIGATER...")
        
        user_data_dir = ROOT_DIR / "temp" / "sigater_browser_session"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=args.headless,
            accept_downloads=True,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )

        def setup_dialog_handler(pg):
            def _on_dialog(d):
                try:
                    d.accept()
                except Exception:
                    pass
            try:
                pg.on("dialog", _on_dialog)
            except Exception:
                pass

        context.on("page", setup_dialog_handler)
        for pg in context.pages:
            setup_dialog_handler(pg)

        page = context.pages[0] if context.pages else context.new_page()
        setup_dialog_handler(page)

        try:
            page.goto(args.url, timeout=20000)
            logger.info(f"🌐 Acessando: {args.url}")
        except Exception as e:
            logger.warning(f"⚠️ Aviso ao abrir URL inicial ({e}). O navegador permanecerá aberto.")

        while True:
            print("\n" + "=" * 65)
            print("📌 INSTRUÇÕES DE EXECUÇÃO:")
            print("1. No navegador aberto, faça login na sua conta do SIGATER.")
            print("2. Vá na tela onde os beneficiários estão listados (ou clique no número de execuções do mês).")
            print("3. Quando a tabela com os nomes ou botões de ateste estiver na tela:")
            print("   👉 Pressione [ENTER] para INICIAR a varredura e download.")
            print("   👉 Digite 'sair' + [ENTER] para encerrar o programa.")
            print("=" * 65 + "\n")

            opcao = input("👉 Pressione ENTER para varrer a tela atual (ou digite 'sair'): ").strip().lower()
            if opcao == "sair":
                break

            # Localiza a aba correta do SIGATER
            target_page = None
            for pg in reversed(context.pages):
                setup_dialog_handler(pg)
                url_lower = pg.url.lower()
                if "sigater" in url_lower or "bahiater" in url_lower or "cronograma" in url_lower:
                    target_page = pg
                    break

            if not target_page:
                target_page = context.pages[-1]

            try:
                target_page.bring_to_front()
            except Exception:
                pass

            logger.info(f"🔍 Analisando página ativa: {target_page.url}")

            temp_dl = ROOT_DIR / "temp" / "sigater_downloads"
            temp_dl.mkdir(parents=True, exist_ok=True)

            # Extração profunda de elementos na página
            logger.info("🔍 Inspecionando links, botões e tabelas da página...")
            
            dom_info = target_page.evaluate("""() => {
                const elementos = Array.from(document.querySelectorAll('a, button, input[type="button"], tr, td, i'));
                const resultados = [];
                
                elementos.forEach((el, idx) => {
                    const href = el.href || el.getAttribute('href') || '';
                    const onclick = el.getAttribute('onclick') || '';
                    const title = el.getAttribute('title') || '';
                    const text = (el.innerText || '').replace(/\\n+/g, ' ').trim();
                    const className = el.className || '';
                    const tag = el.tagName.toLowerCase();

                    // Identifica se é link de ateste, download ou PDF
                    const ehDownload = (
                        href.includes('.pdf') || href.includes('ateste') || href.includes('imprimir') || href.includes('download') ||
                        onclick.includes('ateste') || onclick.includes('imprimir') || onclick.includes('pdf') || onclick.includes('download') ||
                        title.toLowerCase().includes('ateste') || title.toLowerCase().includes('imprimir') || title.toLowerCase().includes('pdf') ||
                        title.toLowerCase().includes('download') || className.includes('pdf') || className.includes('print') || className.includes('download')
                    );

                    // Identifica se é célula com link de execução (ex: número com link)
                    const ehLinkExecucao = (
                        (tag === 'a' || tag === 'button' || onclick) &&
                        (href.includes('executar') || href.includes('beneficiario') || onclick.includes('executar') || onclick.includes('beneficiario'))
                    );

                    if (ehDownload || ehLinkExecucao || (href && tag === 'a' && text.length > 0 && text.length < 50)) {
                        resultados.push({
                            idx: idx,
                            tag: tag,
                            text: text,
                            href: href,
                            onclick: onclick,
                            title: title,
                            className: className,
                            ehDownload: ehDownload,
                            ehLinkExecucao: ehLinkExecucao
                        });
                    }
                });

                return {
                    url: window.location.href,
                    totalElementos: resultados.length,
                    elementos: resultados
                };
            }""")

            elementos_dl = [e for e in dom_info["elementos"] if e["ehDownload"]]
            logger.info(f"📊 Elementos detectados: {len(dom_info['elementos'])} links/botões ({len(elementos_dl)} marcados como Ateste/Download)")

            # Se não houver botões diretos de ateste, mas houver links de execução (ex: números clicáveis na grade)
            if not elementos_dl:
                logger.warning("⚠️ Nenhum botão direto de PDF/Ateste encontrado na tela atual.")
                links_exec = [e for e in dom_info["elementos"] if e["ehLinkExecucao"] or (e["tag"] == 'a' and e["text"].isdigit())]
                if links_exec:
                    logger.info(f"💡 Foram encontrados {len(links_exec)} links de meses/execuções na grade:")
                    for le in links_exec[:10]:
                        logger.info(f"   👉 Texto: '{le['text']}' | OnClick: {le['onclick'][:40]} | Href: {le['href'][:50]}")
                    print("\n💡 DICA: Clique em um dos números na grade do SIGATER (ex: 151) para abrir a lista dos beneficiários e aperte ENTER novamente!")
                continue

            # Processa os downloads
            baixados_sucesso = 0
            erros = 0

            for idx_dl, el in enumerate(elementos_dl, 1):
                logger.info(f"[{idx_dl}/{len(elementos_dl)}] Baixando: '{el['text']}' | Title: '{el['title']}'...")
                caminho_salvo = None

                href = el.get("href", "")
                if href and (href.startswith("http://") or href.startswith("https://")):
                    try:
                        resp = context.request.get(href)
                        if resp.status == 200 and (resp.headers.get("content-type", "").find("pdf") >= 0 or len(resp.body()) > 1000):
                            caminho_salvo = temp_dl / f"ateste_{idx_dl}_{int(time.time())}.pdf"
                            with open(caminho_salvo, "wb") as f_out:
                                f_out.write(resp.body())
                    except Exception as e_req:
                        logger.debug(f"Request direto: {e_req}")

                if not caminho_salvo or not caminho_salvo.exists():
                    try:
                        # Tenta clicar no elemento por title, href ou texto
                        loc = None
                        if el.get("title"):
                            loc = target_page.locator(f"[title='{el['title']}']").first
                        elif el.get("href"):
                            loc = target_page.locator(f"a[href='{el['href']}']").first
                        elif el.get("text"):
                            loc = target_page.locator(f"text='{el['text']}'").first

                        if loc and loc.count() > 0:
                            try:
                                with target_page.expect_download(timeout=8000) as dl_info:
                                    loc.click(force=True)
                                dl = dl_info.value
                                caminho_salvo = temp_dl / dl.suggested_filename
                                dl.save_as(str(caminho_salvo))
                            except Exception:
                                pass
                    except Exception as e_click:
                        logger.debug(f"Clique falhou: {e_click}")

                # Processa e organiza
                if caminho_salvo and caminho_salvo.exists() and caminho_salvo.stat().st_size > 500:
                    try:
                        with open(caminho_salvo, "rb") as f_pdf:
                            pdf_bytes = f_pdf.read()

                        meta = extrair_metadados_ateste_pdf(pdf_bytes, caminho_salvo.name)
                        res = organizar_ateste_no_disco_local(
                            pdf_bytes=pdf_bytes,
                            nome_beneficiario=meta["beneficiario"],
                            comunidade=meta["comunidade"],
                            tecnico=meta["tecnico"],
                            data_atividade=meta["data"],
                            atividade_nome=meta["atividade"] or args.atividade
                        )
                        logger.info(f"  ✅ Organizado: {res['caminho_relativo']}")
                        baixados_sucesso += 1
                    except Exception as e_org:
                        logger.error(f"  ❌ Erro ao organizar: {e_org}")
                        erros += 1
                else:
                    erros += 1

                time.sleep(0.3)

            print("\n" + "=" * 65)
            print(f"🎉 CONCLUÍDO! Total de Atestes Baixados nesta tela: {baixados_sucesso}")
            if erros > 0:
                print(f"⚠️ Itens pendentes: {erros}")
            print("=" * 65 + "\n")

        print("Navegador finalizado.")
        context.close()


if __name__ == "__main__":
    main()
