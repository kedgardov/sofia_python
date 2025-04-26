from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request

from extractor import Extractor
from matcher import Matcher
from predictor import Predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor = Predictor()
    matcher  = Matcher()
    extractor = Extractor()

    if not predictor.ensure_nltk_resources():
        raise Exception("Faltan recursos")
    
    if not predictor.load_models():
        raise Exception("Falta modelo ML")
    
    app.state.predictor = predictor
    app.state.matcher = matcher
    app.state.extractor = extractor

    yield

def get_predictor( request: Request ) -> Predictor:
    return request.app.state.predictor

def get_matcher( request: Request ) -> Matcher:
    return request.app.state.matcher

def get_extractor( request: Request ) -> Extractor:
    return request.app.state.extractor


app = FastAPI(lifespan=lifespan)

@app.post("/cargar_tesis")
async def cargar_tesis(file: UploadFile | None = None,
                       predictor: Predictor = Depends(get_predictor),
                       matcher: Matcher = Depends(get_matcher),
                       extractor: Extractor = Depends(get_extractor)):
    try:
        if file is None:
            raise Exception("El archivo no existe")
        
        if file.content_type != "application/pdf":
            raise Exception("Archivo no es pdf")
        
        fields = extractor.get_fields_from_pdf(file.file)
        prediction = predictor.predict_category(fields['abstract'])
        coordinacion = matcher.match_coordinacion(fields['coordinacion'])
        programa = matcher.match_programa(fields['programa'])
        fecha =  matcher.match_fecha(fields['fecha'])
        comite = matcher.match_comite(fields['comite'])
        
        fields['id_coordinacion'] = coordinacion
        fields['id_programa'] = programa
        fields['fecha'] = fecha
        fields['id_pronace'] = int(prediction)
        fields['id_opcion_terminal'] = None

        data = {'tesis': fields, 'comite': comite}


        return {
            "success": True,
            "message": "All good",
            "tesis_data": data
        }


    except Exception as e:
        raise HTTPException(status_code=500,detail = {
            "success": False,
            "message": str(e)
        })
    
