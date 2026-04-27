import os
import platform
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Lógica para encontrar a Raiz do Projeto (garante que olhe para 'agendha/')
    # __file__ é app/config.py. parent é app/. parent.parent é a raiz do projeto.
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Define o caminho do banco TRAVADO na raiz
    DB_PATH: Path = BASE_DIR / "agendha.db"
    
    # Paths relativos ao BASE_DIR ou fixos dentro de app/
    # Como STATIC_FOLDER estava sendo definido como BASE_DIR / "static", mas config.py via "app" commo base dir,
    # agora que BASE_DIR é a raiz, precisamos ajustar se as pastas estão dentro de 'app' ou na raiz.
    # No list_dir anterior:
    # app/static existe -> BASE_DIR / "app" / "static"
    # app/templates existe -> BASE_DIR / "app" / "templates"
    # app/uploads existe -> BASE_DIR / "app" / "uploads"
    
    APP_DIR: Path = BASE_DIR / "app"
    
    STATIC_FOLDER: Path = APP_DIR / "static"
    TEMPLATES_FOLDER: Path = APP_DIR / "templates"
    UPLOAD_FOLDER: Path = APP_DIR / "uploads"
    PRINT_FOLDER: Path = APP_DIR / "prints_erros"
    
    DOCUMENTOS_FOLDER: Path = UPLOAD_FOLDER / "documentos"
    COTACOES_FOLDER: Path = UPLOAD_FOLDER / "cotacoes"
    GRH_FOLDER: Path = UPLOAD_FOLDER / "grh"
    BENEFICIARIOS_DOCS_FOLDER: Path = UPLOAD_FOLDER / "beneficiarios_docs"
    TEMP_FOLDER: Path = APP_DIR / "temp"

    # Files
    HISTORICO_PATH: Path = APP_DIR / "historico.json"
    TEMPLATE_ANALISE_PATH: Path = TEMPLATES_FOLDER / "excel" / "template_analise_cotacao.xlsx"
    # Favicon usually in static
    FAVICON_PATH: Path = STATIC_FOLDER / "favicon.ico"

    # External Tools Logic
    OFFICE_PATH: str | None = None
    POPPLER_PATH: str | None = None
    TESSERACT_CMD: str | None = None
    LIBREOFFICE_PATH: str | None = None
    
    # Credentials & Configs
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agendha System"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    SECRET_KEY: str = "sua_chave_secreta"
    ALGORITHM: str = "HS256"
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str | None = None
    AUTH_BEARER_PREFIX: str = "Bearer"
    
    # Automation Credentials
    MDS_USER: str | None = None
    MDS_PASSWORD: str | None = None

    class Config:
        env_file = ".env"
        # .env file location: root of project
        env_file_encoding = 'utf-8'
        extra = "ignore" 

    def __init__(self, **data):
        super().__init__(**data)
        self._setup_external_tools()
    
    def _setup_external_tools(self):
        # Fallback logic for external tools if not in env
        if not self.OFFICE_PATH:
             self.OFFICE_PATH = self._get_platform_default("office")
        if not self.LIBREOFFICE_PATH:
             self.LIBREOFFICE_PATH = self.OFFICE_PATH # Backwards compatibility
        
        if not self.POPPLER_PATH:
            self.POPPLER_PATH = self._get_platform_default("poppler")
            
        if not self.TESSERACT_CMD:
            self.TESSERACT_CMD = self._get_platform_default("tesseract")

    @staticmethod
    def _get_platform_default(tool_name):
        system = platform.system()
        
        if tool_name == "office":
            if system == "Windows":
                 # 1. Tentar Excel (Prioridade do Usuário)
                 excel_path = r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
                 if os.path.exists(excel_path):
                     return excel_path
                     
                 # 2. Tentar Excel em outro caminho comum (x86)
                 excel_path_x86 = r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE"
                 if os.path.exists(excel_path_x86):
                     return excel_path_x86

                 # 3. Tentar LibreOffice (Fallback)
                 libre_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
                 if os.path.exists(libre_path):
                     return libre_path
                 
                 return None

            return "soffice" # Linux/Mac

        if tool_name == "poppler":
            return None
            
        if tool_name == "tesseract":
            if system == "Windows":
                return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            return "/usr/bin/tesseract"
        return None

settings = Settings()
