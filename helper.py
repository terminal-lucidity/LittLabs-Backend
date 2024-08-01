from datetime import datetime

def generate_deadline_management_prompt(today, tasks):
    for task in tasks:
        task['dueDate'] = datetime.strptime(task['dueDate'], "%d-%m-%Y").date()


# Generate task string for the prompt
    task_str = ',\n  '.join([f'"{task["taskName"]}": ["{task["taskDescription"]}", "{task["dueDate"]}", "{task["taskType"]}", "{task["taskColor"]}"]' for task in tasks])

# Prompt template
    today = datetime.today().date()
    prompt_template = f"""
the following is a list of tasks and their deadlines, in the format {{"heading": ["description", "duedate", "type", "color"]}}, tasks: {{
  {task_str}
}}

Each task includes a heading, description, duedate, type, and color. Considering all these tasks, generate a detailed plan that helps the user complete them productively without missing any due dates. The plan should focus on:

Task Ordering: Determine the order in which tasks should be completed based on their type and due dates.
Methodology:
Prioritization: Prioritize tasks by their type (e.g., personal, work, study) and due dates.
Task Breakdown: Break down larger tasks into smaller, manageable sub-tasks if necessary.
Execution: Provide a step-by-step method for tackling each task, ensuring productivity and efficiency.
Provide the user with a clear and actionable plan that includes:

A prioritized list of tasks with an explanation for their order.
Specific steps for breaking down and completing each task.
Any additional tips for maintaining focus and managing time effectively.

Today's date: {today}


Give the answer in plain text instead of markdown format.
"""
    return prompt_template

def vidPrompt():
    prompt = """
Analyze the video interview and provide a detailed description of the interviewee's performance. 
The analysis should include the following parameters, each measured out of 10:

1. Vocabulary: Assess the range and appropriateness of terms used by the interviewee.
2. Confidence Level: Evaluate the interviewee's steadiness, tone, and lack of hesitation.
3. Engaging Ability: Determine how well the interviewee captures and maintains the audience's attention.
4. Speaking Style: Review the clarity, coherence, and expressiveness of the interviewee's speech.

Provide the output in the following JSON format with a text review summarizing the interviewee's performance:

{
  "video_analysis": {
    "vocabulary": 0,
    "confidence_level": 0,
    "engaging_ability": 0,
    "speaking_style": 0,
    "overall_average": 0,
    "review": ""
  }
}

Additionally, calculate an overall average score using a weighted average, where the weights are based on the importance of the four parameters being tested.
"""
    return prompt
