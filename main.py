# 1. Install openAI environment
#    pip install openai
# 2. Install fastAPI and uvcorn libraries
#    pip install fastapi uvicorn python-multipart
# 3. Install jinja2 library
#    pip install aiofiles jinja2

## -- Consejos para la libreria de OpenAI

# response.choices[0].message.content
# from openai import OpenAI
#
# openai = OpenAI(
#     api_key = "your key here"
# )
#
# response = openai.images.generate(
#   prompt=user_input,
#   n=1,
#   size="512x512"
# )
#
# image_url = response.data[0].url

# Virtual environment installation and verification
#
# python -m venv assistantenv
# pip list
# assistantenv\Scripts\activate.bat
# pip list
# pip install fastapi uvicorn python-multipart
#

#
# pip install websockets
#

#
# pip install python-dotenv
#

echo "# asistente-de-reclutamiento" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/alarconjr/asistente-de-reclutamiento.git
git push -u origin main


from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv


load_dotenv()

openai = OpenAI(
    api_key = os.getenv('OPENAI_API_SECRET_KEY')
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class = HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request, "home.html", {"chat_responses": chat_responses})
    # return templates.TemplateResponse( request,"home.html")

# chat_log = [{'role': 'system',
#              'content': 'Eres un tutor AI de python, dedicado completamente a enseñar al usuario como aprender \
#                          Python desde cero. Por favor provee de instrucciones claras de conceptos de python, \
#                          mejores practicas y syntaxis. Ayuda a crear un camino de aprendizaje para que los usuarios \
#                          puedan crear aplicaciones en python de la vida real y listas para produccion'}]

chat_log = [{'role': 'system',
             'content': 'Eres un asistente de reclutamiento, dedicado completamente a orientar al usuario acerca de \
                         las ofertas laborales ofrecidas por la empresa. Por favor provee de instrucciones claras de \
                         las ofertas laborales actuales. Estas ofertas son: Asistente de cocina, guardia de seguridad, \
                         ayudantes generales en planta de fabricacion, soldadores especializados y electricistas. \
                         Busca requerimientos generales para cada uno de estos puestos y pregunta cual de estos puestos \
                         le interesa al usuario, luego profundiza mas en los requerimientos generales de el puesto seleccionado'}]

chat_responses = []

@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()

    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = openai.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages = chat_log,
                temperature = 0.6,
                stream = True,
            )

            ai_response = ''

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    # await websocket.send_text(chunk.choices[0].delta.content)

            await websocket.send_text(ai_response)

            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f'Error {str(e)}')
            break


@app.post("/", response_class = HTMLResponse)
async def chat( request: Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = chat_log,
        temperature = 0.6,
    )

    bot_response = response.choices[0].message.content

    chat_log.append({'role': 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)

    return  templates.TemplateResponse( request, "home.html", {"chat_responses": chat_responses})
