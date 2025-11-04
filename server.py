from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    global active_graph

    # must be json file
    if not file.filename.endswith(".json"):
        return {"Upload Error": "Invalid file type"}

    # helpful to return something on failure
    try:
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Error": f"Failed to process file: {str(e)}"}

@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph

    # if no valid graph is uploaded return error
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    start_node = active_graph.nodes.get(start_node_id)
    end_node = active_graph.nodes.get(end_node_id)
    if start_node is None or end_node is None:
        return {"Solver Error": "Invalid start or end node ID."}

    try:
        dijkstra(active_graph, start_node)
        # Reconstruct path
        path = []
        current = end_node
        while current is not None:
            path.insert(0, current.id)
            current = current.prev
        
        if path[0] != start_node_id:
            return {"Error": "No path found."}

        return {
            "shortest_path": path,
            "total_distance": end_node.dist
        }

    except Exception as e:
        return {"Solver Error": f"{str(e)}"}

# # Adding for testing onrender no active graph failure
# @app.delete("/delete_graph_json/")
# async def create_upload_file():
#     global active_graph 
#     active_graph= None 

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    