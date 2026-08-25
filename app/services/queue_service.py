import asyncio
import logging
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)

class JobManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False
        self._worker_task = None
        self.total_jobs = 0
        self.completed_jobs = 0
        self.mensagens = []
        
    def add_mensagem(self, msg: str):
        self.mensagens.append(msg)
        
    async def add_job(self, job_func: Callable, *args, **kwargs):
        if self.queue.qsize() == 0 and self.completed_jobs >= self.total_jobs:
            self.total_jobs = 0
            self.completed_jobs = 0
            self.mensagens = []
            
        await self.queue.put((job_func, args, kwargs))
        self.total_jobs += 1
        logger.info(f"Job adicionado à fila: {job_func.__name__}")
        
    async def _worker(self):
        while self.is_running:
            try:
                job_func, args, kwargs = await self.queue.get()
                logger.info(f"Processando job: {job_func.__name__}")
                try:
                    # Executa a função do job
                    if asyncio.iscoroutinefunction(job_func):
                        resultado = await job_func(*args, **kwargs)
                    else:
                        resultado = job_func(*args, **kwargs)
                        
                    if resultado and isinstance(resultado, str):
                        self.add_mensagem(resultado)
                    else:
                        self.add_mensagem(f"Arquivo processado e organizado com sucesso.")
                except Exception as e:
                    logger.error(f"Erro no job {job_func.__name__}: {e}", exc_info=True)
                    self.add_mensagem(f"❌ Erro ao processar arquivo: {str(e)[:50]}")
                finally:
                    self.completed_jobs += 1
                    self.queue.task_done()
                
                # Delay de 4.5s para evitar erro 429 do Gemini
                await asyncio.sleep(4.5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no worker da fila: {e}", exc_info=True)
                await asyncio.sleep(1)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("Worker da fila iniciado com sucesso.")
            
    def stop(self):
        self.is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            logger.info("Worker da fila parado.")
            
    def get_status(self) -> Dict[str, Any]:
        if self.total_jobs == 0:
            status_str = "vazio"
            progresso = 0
        elif self.completed_jobs >= self.total_jobs:
            status_str = "concluido"
            progresso = 100
        else:
            status_str = "processando"
            progresso = int((self.completed_jobs / self.total_jobs) * 100)
            
        mensagens = self.mensagens.copy()
        self.mensagens.clear()
        
        return {
            "status": status_str,
            "progresso": progresso,
            "processados": self.completed_jobs,
            "total": self.total_jobs,
            "mensagens": mensagens
        }

queue_manager = JobManager()
