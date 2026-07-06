import os
import sys
from pathlib import Path
import datetime

from dotenv import load_dotenv
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import agent_tool

load_dotenv()
MODEL = os.getenv("MODEL" , "gemini-flash-latest")


# sub agent - Planner
blog_planner = Agent(
    name="BlogPlanner",
    model=MODEL,
    description="Create a practical . skimable outline in Markdown",
    instruction="""
    You are a technical content strategist. Produce a clear Markdown outline wiht :
    - Title
    - Short Intro
    - 4-6 main section (each with 2-4 bullets)
    - Conclusion

    If `codebase_content` exists in state , weave in specific sections/snippets.
    Return only the outline in Markdown
    """,
    output_key="blog_outline"
)

class OutlineValidationChecker(Agent):
    def __init__(self):
        super().__init__(
            name="OutlineValidationChecker",
            model=MODEL,
            description="Validates that the outline is usable",
            instruction="""
            Check the outline in state `blog_outline` . If it has a title , intro , 4-6 section , and a conclusion , respond exactly "ok", otherwise respond exactly "retry" and list missing pieces.
        
            """,
            output_key="validation_result",
        )

robust_blog_planner = LoopAgent(
    name="RobustBlogPlanner",
    description="Retries planning if validation failes",
    sub_agents=[blog_planner, OutlineValidationChecker()],
    max_iterations=3
)

# Sub agent : wrtier
blog_writer = Agent(
    name="BlogWriter",
    model=MODEL,
    description="Writes a technical blog past from the outline",
    instruction="""
    Write a complete Markdown article fron the outline in `blog_outline`

    Guidelines : 
    - "Audience : software enginners : skip basics and focus on practical insight"
    - "Explain both the how and why"
    - "include concise code snippets when helpful"
    - "follow the outline's structure (H2/H3)"
    - "Output only the final artticle in Markdown (no fnece around the whole past)"
    """
    ,output_key="blog_post"
)

class BlogPostValidationChecker(Agent):
    def __init__(self):
        super().__init__(
            name="BlogPostValidationChecker",
            model=MODEL,
            description="Validates the final past.",
            instruction="""
            check `blog_post` for : intro , clear section matching the outline , conclsuion . and technical clarity.
            If passes , respond "OK" , else respond "retry" with the specific fixes.
            """
            , output_key="validation_result"
        )

robust_blog_writer = LoopAgent(
    name="RobustBlogWriter",
    description="Retries writing if validation fails",
    sub_agents=[blog_writer, BlogPostValidationChecker()],
    max_iterations=3
)

# Expose planner/ writer as tools so te root agent can call them explicitly
planner_tool = agent_tool.AgentTool(agent=robust_blog_planner)
writer_tool = agent_tool.AgentTool(agent=robust_blog_writer)

# Root agent 
root_agent = Agent(
    name="Blogger",
    model=MODEL,
    description="Minimal multi-agent blogger that plans and writes",
    instruction=f"""
    If the user gives a topic : 
    1) Call the planner tool to generate the outline.
    2) Call the writer tool to produce the full draft.
    3) End wiht 3 altenrate titles and 2 tweet-length hooks.
    If the trends tool fails or times out . continue wiht a sensible outline and draft anyway
    Date : {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools = [
        planner_tool,
        writer_tool
    ],
)