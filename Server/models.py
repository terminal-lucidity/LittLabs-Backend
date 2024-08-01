from pydantic import BaseModel
from typing import Optional
import typing_extensions as typing
class SignUpSchema(BaseModel):
    username:str
    email:str
    password:str

class LoginSchema(BaseModel):
    email:str
    password:str

class TaskTypeSchema(BaseModel):
    username:str
    taskTypeName:str
    taskTypeColor:str

class DeleteTaskTypeScheme(BaseModel):
    username:str
    taskTypeKey:str

class TodoSchema(BaseModel):
    username: str
    taskName: str
    taskDescription: str
    dueDate: str
    taskType: str
    taskColor: str
    isCompleted: bool

class DeleteTodoSchema(BaseModel):
    username: str
    taskKey: str

class CompleteTodoSchema(BaseModel):
    username: str
    taskKey: str
    isCompleted: bool

class NoteSchema(BaseModel):
    username:str
    noteTitle:str
    noteText:str
    creationDate:str

class DeleteNoteSchema(BaseModel):
    username:str
    noteKey:str

class UpdateNoteSchema(BaseModel):
    username: str
    noteKey: str
    noteTitle: str
    noteText: str

class ChatSchema(BaseModel):
    question: str
    username: str

class TextualQuestionSchema(BaseModel):
    question: Optional[str] = "Solve the questions in the image."

class VideoAnalysis(typing.TypedDict):
    vocabulary: int
    confidence_level: int
    engaging_ability: int
    speaking_style: int
    overall_average: int
    review: str