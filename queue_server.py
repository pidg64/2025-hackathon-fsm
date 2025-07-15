import uvicorn

from queue import Queue
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
name_queue = Queue()

@app.post('/enqueue/{name}')
def enqueue_name(name: str):
    print(f'Encolando nombre: {name} en la cola {name_queue}')
    name_queue.put(name)
    return {'status': 'enqueued', 'name': name}

@app.get('/dequeue')
def dequeue_name():
    if name_queue.empty():
        return JSONResponse(content={}, status_code=200)
    
    name = name_queue.get()
    print(f'Nombre retirado de la cola: {name}')
    return {'name': name}

def get_queue():
    return name_queue

if __name__ == '__main__':
    uvicorn.run('queue_server:app', host='0.0.0.0', port=8081)