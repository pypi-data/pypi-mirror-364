from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from io import BytesIO
import base64
from PIL import Image
from escpos.escpos import EscposIO
from escpos.printer import Network

class PrintRequest(BaseModel):
    printer_ip: str
    port: int = 9100
    data: str

class PrinterAPI:
    def __init__(self, printer_ip: str, port: int, data: str):
        self.printer_ip = printer_ip
        self.port = port
        self.data = data

    def process_image_and_print(self):
        try:
            image_io = BytesIO(base64.b64decode(self.data))
            image = Image.open(image_io)

            # Convert and resize
            image = image.convert("L")
            image = image.resize((384, int(image.height * (384 / image.width))))
            image = image.convert("1")

            printer = Network(self.printer_ip, port=self.port)
            
            printer.set()  # reset trạng thái
            printer.image(image)
            printer.cut()
            printer.close()

            return JSONResponse({"status": "success"}, status_code=status.HTTP_200_OK)
        except Exception as e:
            try:
                printer.close()
            except:
                pass
            return JSONResponse(
                {"status": "error", "message": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def create_app():
    app = FastAPI()
    
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post('/print')
    async def print_receipt(print_request: PrintRequest):
        try:
            printer_api = PrinterAPI(print_request.printer_ip, print_request.port, print_request.data)
            return printer_api.process_image_and_print()
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing parameter: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app