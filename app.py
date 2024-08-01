import uvicorn
import pyrebase
import shutil
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, File, UploadFile,Form
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from models import *
from helper import *
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from datetime import date
import google.generativeai as genai
import time
import firebase_admin
from firebase_admin import credentials, firestore,auth
import json
load_dotenv()

api_key = os.getenv('GEMINI_API')
genai.configure(api_key=api_key)

app = FastAPI(docs_url="/")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def read_root():
    return {"message": "Hello World"}


if not firebase_admin._apps:
    cred = credentials.Certificate(r".\serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firestore.client()






@app.post('/signup')
async def create_an_account(user_data:SignUpSchema):
    email = user_data.email
    password = user_data.password
    username = user_data.username
    try:
        user = auth.create_user(
            display_name = username,   
            email = email,
            password = password
        )

        return JSONResponse(content={"username" : user.display_name},
                            status_code= 201
               )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail= f"Account already created for the email {email}"
        )

@app.post('/login')
async def create_access_token(user_data:LoginSchema):
    email = user_data.email
    password = user_data.password

    try:
        print("Inside try block")
        user = firebase.auth().sign_in_with_email_and_password(
            email = email,
            password = password
        )

        token = user['idToken']
        user_info = firebase.auth().get_account_info(token)
        display_name = user_info['users'][0].get('displayName', '')


        return JSONResponse(
            content={
                # "token":token
                "username":display_name
            },status_code=200
        )

    except:
        raise HTTPException(
            status_code=400,detail="Invalid Credentials"
        )

@app.post("/notes/create")
async def create_note(note:NoteSchema):    
    new_note = db.collection('Notes').document(note.username).collection('notes').document()
    new_note.set({
        "noteTitle":note.noteTitle,
        "noteText":note.noteText,
        "creationDate":note.creationDate,
        "noteKey": new_note.id
    })    
    return {"noteKey": new_note.id}

@app.get("/notes/read")
async def read_notes(username:str):
    notes = db.collection('Notes').document(username).collection('notes').get()
    notes=[notes[i].to_dict() for i in range(len(notes))]
    return notes



@app.put("/notes/update")
async def update_note(note: UpdateNoteSchema):
    note_ref = db.collection('Notes').document(note.username).collection('notes').document(note.noteKey)
    
    # Check if the document exists
    if not note_ref.get().exists:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update the note
    note_ref.update({
        "noteTitle": note.noteTitle,
        "noteText": note.noteText
    })
    
    return {"message": "Note updated successfully"}


@app.delete("/notes/delete")
async def delete_notes(note: DeleteNoteSchema):
    print("delete called")
    db.collection('Notes').document(note.username).collection('notes').document(note.noteKey).delete()
    return {"message":"Note deleted successfully"}


@app.post("/todo/create")
async def create_todo(todo_data: TodoSchema):
    print("\n\nFunction called!!!\n\n")
    new_todo_ref = db.collection('TodoList').document(todo_data.username).collection('Todos').document()
    new_todo_ref.set({
        "taskName": todo_data.taskName,
        "taskDescription": todo_data.taskDescription,
        "taskType": todo_data.taskType,
        "dueDate": todo_data.dueDate,
        "taskColor": todo_data.taskColor,
        "isCompleted": todo_data.isCompleted,
        "taskKey": new_todo_ref.id
    })
    
    return {"taskKey": new_todo_ref.id}

@app.get("/todo/read")
async def read_todos(username:str):
    tasks = db.collection('TodoList').document(username).collection('Todos').get()
    todos=[tasks[i].to_dict() for i in range(len(tasks))]
    return todos

@app.delete("/todo/delete")
async def delete_todo(delete_todo: DeleteTodoSchema):
    db.collection('TodoList').document(delete_todo.username).collection('Todos').document(delete_todo.taskKey).delete()
    return {"message":"Note deleted successfully"}

@app.put("/todo/complete")
async def update_todo_completed(complete_todo: CompleteTodoSchema):
    db.collection('TodoList').document(complete_todo.username).collection('Todos').document(complete_todo.taskKey).update({"isCompleted":complete_todo.isCompleted})
    return {"message":"Task completed successfully"}

@app.get("/taskType/read")
async def read_task_types(username:str):
    task_types = db.collection('TaskType').document(username).collection('taskType').get()
    task_types = [task_types[i].to_dict() for i in range(len(task_types))]
    return task_types

@app.post("/taskType/create")
async def create_task_type(taskType: TaskTypeSchema):    
    new_taskType = db.collection('TaskType').document(taskType.username).collection('taskType').document()
    new_taskType.set({
        "taskTypeName":taskType.taskTypeName,
        "taskTypeColor":taskType.taskTypeColor,
        "taskTypeKey": new_taskType.id
    })    
    x = db.collection('TaskType').document(taskType.username).collection('taskType').get()
    del x
    return {"taskTypeKey": new_taskType.id}

# @app.delete("/taskType/delete")
# async def delete_task_type(deleteTaskType: DeleteTaskTypeScheme):
#     db.collection('TaskType').document(deleteTaskType.username).collection('taskType').document(deleteTaskType.taskTypeKey).delete()
#     return {"message":"Task Type deleted successfully"}
@app.delete("/taskType/delete")
async def delete_task_type(deleteTaskType: DeleteTaskTypeScheme):
    doc_ref = db.collection('TaskType').document(deleteTaskType.username).collection('taskType').document(deleteTaskType.taskTypeKey)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return {"message": "Task Type deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Task Type not found")

@app.post('/chat')
async def chat(userPrompt:ChatSchema):
    tasks = db.collection('TodoList').document(userPrompt.username).collection('Todos').get()
    todos=[tasks[i].to_dict() for i in range(len(tasks))]
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])

    if "manage my deadlines" in userPrompt.question.lower():
        today = date.today()
        prompt = generate_deadline_management_prompt(today, todos)
        response = chat.send_message(prompt)
    else:
        response = chat.send_message(userPrompt.question)

    return {"response": response.text}




@app.post("/upload-video")
async def process_video(file: UploadFile = File(...)):
    model = genai.GenerativeModel('gemini-1.5-pro',
                              generation_config={"response_mime_type": "application/json",
                                                 "response_schema": VideoAnalysis})

    prompt= vidPrompt()

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Save the uploaded video file
        file_location = os.path.join(tmpdirname, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        print("File saved ")
        # Upload the video file to Google Generative AI
        video_file = genai.upload_file(path=file_location)

        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(10)
            video_file = genai.get_file(video_file.name)
    
        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)

        # Generate content using the uploaded video and the prompt
        print("Generating content...")
        response = model.generate_content([video_file, prompt], request_options={"timeout": 600})

    return json.loads(response.text)


@app.post("/flashcards")
async def generate_flashcards(file: UploadFile = File(...)):
    FlashCardSchema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "answer": {"type": "string"},
                "hint": {"type": "string"}
            },
            "required": ["question", "answer", "hint"]
        }
    }
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Save the uploaded file
        file_location = os.path.join(tmpdirname, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Load the PDF
        loader = PyPDFLoader(file_location)
        docs = loader.load()
        print("docs ready")
        # Split the content into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=2000)
        splits = text_splitter.split_documents(docs)
        print("split ready")
        # Combine the chunks into a single string
        content = []
        for split in splits:
            content.append(split.page_content)
        content = '\n\n\n\n'.join(content)
        print("content ready!")
        # Define the prompt template
        prompt_template = PromptTemplate(
            input_variables=['notes'],
            template='''Act as a teacher and consider the following text:
            {notes}
            Generate a list of question-answer pairs of varying difficulties.
            The questions should be of type fill-in-the-blank or True/False.
            The output should be a JSON array where each element contains "question", "answer", and "hint".
            
            For example:
            [
              {{
                "question": "What is the largest country in the world by land area?",
                "answer": "Russia",
                "hint": "It spans across two continents."
              }},
              {{
                "question": "True or False: The Pacific Ocean is the largest ocean on Earth.",
                "answer": "True",
                "hint": "It's bigger than the Atlantic Ocean."
              }}
            ]'''
        )
        model = genai.GenerativeModel('gemini-1.5-flash',
                              generation_config={"response_mime_type": "application/json",
                                                 "response_schema": FlashCardSchema})

        # Format the prompt
        prompt = prompt_template.format(notes=content)
        
        # Generate the flashcards
        response = model.generate_content(prompt)

        # Return the generated flashcards as JSON
        return json.loads(response.text)

@app.post("/imagesolver/")
async def generate_response(userPrompt:str = Form(default=""),file: UploadFile = File(...)):
    # Create a temporary directory
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Save the uploaded file
        file_location = os.path.join(tmpdirname, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Upload the image file to Google Generative AI
        sample_file = genai.upload_file(path=file_location, display_name=file.filename)
        if userPrompt=="":
            prompt = "Solve the questions in the image."
        # Generate content using the uploaded image and a prompt
        else:
            prompt = userPrompt
        print(prompt)
        response = model.generate_content([sample_file, prompt])

        # Return the generated response as JSON
        return JSONResponse(content={"response": response.text})

# if __name__ == "__main__":
#     uvicorn.run("app:app",reload=True,port=8000)