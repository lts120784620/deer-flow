# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents import create_agent
from src.tools.search import LoggedTavilySearch
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output

from .types import State
from ..config import SELECTED_SEARCH_ENGINE, SearchEngine

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    task_title: Annotated[str, "The title of the task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


@tool
def handoff_to_image_generator(
    image_description: Annotated[str, "Detailed description of the image to be generated"],
    image_type: Annotated[str, "Type of generation: 'text_to_image', 'image_to_image', or 'image_to_video'"] = "text_to_image",
    style_prompt: Annotated[str, "Additional style or quality parameters for the image"] = "",
) -> str:
    """
    Hand off image/video generation tasks to the image generator agent.
    
    Use this tool when the user requests image generation, visualization, or when you need
    to create visual content to support your research findings.
    
    Args:
        image_description: Detailed description of what image to generate
        image_type: The type of generation (text_to_image, image_to_image, image_to_video)
        style_prompt: Additional style parameters (e.g., "high quality", "realistic", etc.)
    
    Returns:
        Instructions to hand off to image generator agent
    """
    return f"HANDOFF_TO_IMAGE_GENERATOR: {image_description} | Type: {image_type} | Style: {style_prompt}"


def background_investigation_node(state: State, config: RunnableConfig):
    logger.info("background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state["messages"][-1].content
    background_investigation_results = None
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results
        ).invoke(query)
        if isinstance(searched_content, list):
            background_investigation_results = [
                f"## {elem['title']}\n\n{elem['content']}" for elem in searched_content
            ]
            return {
                "background_investigation_results": "\n\n".join(
                    background_investigation_results
                )
            }
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results
        ).invoke(query)
    return {
        "background_investigation_results": json.dumps(
            background_investigation_results, ensure_ascii=False
        )
    }


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter", "image_generator"]]:
    """Planner node that create a plan for the research task."""
    logger.info("Planner creating a plan.")
    configurable = Configuration.from_runnable_config(config)
    messages = apply_prompt_template("planner", state)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0

    if AGENT_LLM_MAP["planner"] == "basic":
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"]).with_structured_output(
            Plan,
            method="json_mode",
        )
    else:
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"])

    # if the plan iterations is greater than the max plan iterations, return the reporter node
    if plan_iterations >= configurable.max_plan_iterations:
        return Command(goto="reporter")

    full_response = ""
    if AGENT_LLM_MAP["planner"] == "basic":
        response = llm.invoke(messages)
        full_response = response.model_dump_json(indent=4, exclude_none=True)
    else:
        response = llm.stream(messages)
        for chunk in response:
            full_response += chunk.content
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")
    
    try:
        curr_plan = json.loads(repair_json_output(full_response))
        
        # 检查是否是图片/视频生成请求
        if curr_plan.get("request_type") in ["image_generation", "video_generation"]:
            logger.info(f"检测到{curr_plan['request_type']}请求")
            logger.info(f"生成类型: {curr_plan['image_generation']['type']}")
            logger.info(f"提示词: {curr_plan['image_generation']['prompt']}")
            
            # 确保所有必需字段都存在
            if not all(key in curr_plan for key in ["locale", "thought", "title"]):
                curr_plan["locale"] = state.get("locale", "zh-CN")
                curr_plan["thought"] = f"生成{curr_plan['image_generation']['type']}类型的图片/视频"
                curr_plan["title"] = f"图片/视频生成任务 - {curr_plan['image_generation']['type']}"
            
            # 验证 Plan 模型
            new_plan = Plan.model_validate(curr_plan)
            
            # 调用 image_generator
            return Command(
                update={
                    "messages": [AIMessage(content=full_response, name="planner")],
                    "current_plan": new_plan,
                },
                goto="image_generator",
            )
            
        # 处理研究请求
        if curr_plan.get("has_enough_context"):
            logger.info("Planner response has enough context.")
            new_plan = Plan.model_validate(curr_plan)
            return Command(
                update={
                    "messages": [AIMessage(content=full_response, name="planner")],
                    "current_plan": new_plan,
                },
                goto="reporter",
            )
            
        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],
                "current_plan": full_response,
            },
            goto="human_feedback",
        )
            
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    # check if the plan is auto accepted
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        feedback = interrupt("Please Review the Plan.")

        # if the feedback is not accepted, return the planner node
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                },
                goto="planner",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")

    # if the plan is accepted, run the following node
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    try:
        current_plan = repair_json_output(current_plan)
        # increment the plan iterations
        plan_iterations += 1
        # parse the plan
        new_plan = json.loads(current_plan)
        if new_plan["has_enough_context"]:
            goto = "reporter"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),
            "plan_iterations": plan_iterations,
            "locale": new_plan["locale"],
        },
        goto=goto,
    )


def coordinator_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    configurable = Configuration.from_runnable_config(config)
    messages = apply_prompt_template("coordinator", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
        .bind_tools([handoff_to_planner])
        .invoke(messages)
    )
    logger.debug(f"Current state messages: {state['messages']}")

    goto = "__end__"
    locale = state.get("locale", "en-US")  # Default locale if not specified

    if len(response.tool_calls) > 0:
        goto = "planner"
        if state.get("enable_background_investigation"):
            # if the search_before_planning is True, add the web search tool to the planner agent
            goto = "background_investigator"
        try:
            for tool_call in response.tool_calls:
                if tool_call.get("name", "") != "handoff_to_planner":
                    continue
                if tool_locale := tool_call.get("args", {}).get("locale"):
                    locale = tool_locale
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")

    return Command(
        update={"locale": locale, "resources": configurable.resources},
        goto=goto,
    )


def reporter_node(state: State, config: RunnableConfig):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": state.get("locale", "en-US"),
    }
    invoke_messages = apply_prompt_template("reporter", input_, configurable)
    observations = state.get("observations", [])

    # Add a reminder about the new report format, citation style, and table usage
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Key Points - A bulleted list of the most important findings\n2. Overview - A brief introduction to the topic\n3. Detailed Analysis - Organized into logical sections\n4. Survey Note (optional) - For more comprehensive reports\n5. Key Citations - List all references at the end\n\nFor citations, DO NOT include inline citations in the text. Instead, place all citations in the 'Key Citations' section at the end using the format: `- [Source Title](URL)`. Include an empty line between each citation for better readability.\n\nPRIORITIZE USING MARKDOWN TABLES for data presentation and comparison. Use tables whenever presenting comparative data, statistics, features, or options. Structure tables with clear headers and aligned columns. Example table format:\n\n| Feature | Description | Pros | Cons |\n|---------|-------------|------|------|\n| Feature 1 | Description 1 | Pros 1 | Cons 1 |\n| Feature 2 | Description 2 | Pros 2 | Cons 2 |",
            name="system",
        )
    )

    for observation in observations:
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",
                name="observation",
            )
        )
    logger.debug(f"Current invoke messages: {invoke_messages}")
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)
    response_content = response.content
    logger.info(f"reporter response: {response_content}")

    return {"final_report": response_content}


def research_team_node(state: State):
    """Research team node that collaborates on tasks."""
    logger.info("Research team is collaborating on tasks.")
    
    # Check if the last step contains image generation handoff
    current_plan = state.get("current_plan")
    if current_plan and hasattr(current_plan, 'steps') and current_plan.steps:
        for step in current_plan.steps:
            if not step.execution_res:
                # Check if step description contains image generation handoff
                if step.execution_res and "HANDOFF_TO_IMAGE_GENERATOR:" in step.execution_res:
                    logger.info("Detected image generation handoff, routing to image_generator")
                    return "image_generator"
                break
    
    # Check messages for handoff signals
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1].content if messages[-1] else ""
        if "HANDOFF_TO_IMAGE_GENERATOR:" in last_message:
            logger.info("Detected image generation handoff in messages, routing to image_generator")
            return "image_generator"
    
    pass


async def _execute_agent_step(
    state: State, agent, agent_name: str
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    # Check if current_plan is a valid Plan object
    if not current_plan or isinstance(current_plan, str):
        logger.warning("No valid plan found or plan is a string")
        return Command(goto="research_team")
    
    # Ensure we have a proper Plan object with steps
    if not hasattr(current_plan, 'steps') or not current_plan.steps:
        logger.warning("No steps found in current plan")
        return Command(goto="research_team")

    # Find the first unexecuted step
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logger.warning("No unexecuted step found")
        return Command(goto="research_team")

    logger.info(f"Executing step: {current_step.title}, agent: {agent_name}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        if state.get("resources"):
            resources_info = "**The user mentioned the following resource files:**\n\n"
            for resource in state.get("resources"):
                resources_info += f"- {resource.title} ({resource.description})\n"

            agent_input["messages"].append(
                HumanMessage(
                    content=resources_info
                    + "\n\n"
                    + "You MUST use the **local_search_tool** to retrieve the information from the resource files.",
                )
            )

        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    logger.info(f"Agent input: {agent_input}")
    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit}
    )

    # Process the result
    response_content = result["messages"][-1].content
    logger.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logger.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name=agent_name,
                )
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    configurable = Configuration.from_runnable_config(config)
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for this agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        async with MultiServerMCPClient(mcp_servers) as client:
            loaded_tools = default_tools[:]
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
            agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)
    
    # Get the last message
    messages = state.get("messages", [])
    if not messages:
        return Command(goto="research_team")
    
    last_message = messages[-1].content if messages[-1] else ""
    logger.info(f"Researcher received message: {last_message}")
    
    # Create researcher agent with all necessary tools
    tools = [
        get_web_search_tool(configurable.max_search_results),
        crawl_tool,
        handoff_to_image_generator,  # Add image generation tool
    ]
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)
    
    logger.info(f"Researcher tools: {tools}")
    
    # Use the standard agent execution pattern
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        tools,
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    configurable = Configuration.from_runnable_config(config)
    tools = [python_repl_tool]
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        tools,
    )


async def image_generator_node(state: State, config: RunnableConfig) -> Command[Literal["reporter"]]:
    """处理图片/视频生成请求的节点"""
    logger.info("[image_generator_node] 进入 image_generator_node")
    
    # 获取当前计划
    current_plan = state.get("current_plan")
    logger.info(f"[image_generator_node] current_plan: {current_plan}")
    if not current_plan or not current_plan.image_generation:
        logger.error("[image_generator_node] 没有找到图片生成参数")
        return Command(goto="reporter")
    
    # 获取生成参数
    image_gen = current_plan.image_generation
    logger.info(f"生成类型: {image_gen.type}")
    logger.info(f"提示词: {image_gen.prompt}")
    
    # 创建 agent
    agent = create_agent(
        agent_name="image_generator",
        agent_type="image_generator",
        tools=[],  # 工具会在运行时动态加载
        prompt_template="image_generator"
    )
    
    config = {
        "configurable": {
            "thread_id": "default",
            "max_plan_iterations": 10,
            "max_step_num": 10,
            "mcp_settings": {
                "servers": {
                    "mcp-github-trending": {
                        "transport": "stdio",
                        "command": "uvx",
                        "args": ["mcp-github-trending"],
                        "enabled_tools": ["get_github_trending_repositories"],
                        "add_to_agents": ["researcher"],
                    },
                    "Wavespeed": {
                        "transport": "stdio",
                        "command": "wavespeed-mcp",
                        "args": [],
                        "env": {
                            "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
                        },
                        "enabled_tools": ["text_to_image", "image_to_image", "image_to_video"],
                        "add_to_agents": ["image_generator"],
                    }
                }
            },
        },
        "recursion_limit": 100,
    }
    
    # 执行 agent 步骤
    try:
        logger.info("[image_generator_node] 调用 _setup_and_execute_agent_step 开始")
        result = await _setup_and_execute_agent_step(
            state=state,
            config=config,
            agent_type="image_generator",
            default_tools=[]
        )
        logger.info(f"[image_generator_node] _setup_and_execute_agent_step 返回: {result}")
        
        # 构建生成结果消息
        generation_result = f"""
## 图片生成结果

### 生成参数
- 类型: {image_gen.type}
- 提示词: {image_gen.prompt}

### 生成结果
{result}
"""
        
        # 更新状态并返回
        return Command(
            update={
                "messages": [
                    AIMessage(content=generation_result, name="image_generator"),
                    AIMessage(content="图片生成完成，请查看结果。", name="reporter")
                ],
                "current_plan": current_plan,
                "observations": state.get("observations", []) + [generation_result]
            },
            goto="reporter"
        )
        
    except Exception as e:
        logger.error(f"[image_generator_node] 图片生成失败: {str(e)}", exc_info=True)
        error_message = f"""
## 图片生成失败

### 错误信息
{str(e)}

### 生成参数
- 类型: {image_gen.type}
- 提示词: {image_gen.prompt}
"""
        return Command(
            update={
                "messages": [
                    AIMessage(content=error_message, name="image_generator"),
                    AIMessage(content="图片生成失败，请查看错误信息。", name="reporter")
                ],
                "current_plan": current_plan,
                "observations": state.get("observations", []) + [error_message]
            },
            goto="reporter"
        )
