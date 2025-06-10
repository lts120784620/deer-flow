# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"
    IMAGE_GENERATION = "image_generation"


class Step(BaseModel):
    need_search: bool = Field(..., description="Must be explicitly set for each step")
    title: str
    description: str = Field(..., description="Specify exactly what data to collect")
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"
    )


class ImageGeneration(BaseModel):
    type: str = Field(..., description="Type of image generation (text_to_image, image_to_image, text_to_video)")
    prompt: str = Field(..., description="The prompt for image generation")


class Plan(BaseModel):
    request_type: Literal["research", "image_generation", "video_generation"] = Field(
        default="research",
        description="Type of request"
    )
    locale: Optional[str] = Field(
        default="zh-CN",
        description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    has_enough_context: bool = Field(
        default=True,
        description="Whether there is enough context to proceed"
    )
    thought: Optional[str] = Field(
        default=None,
        description="Analysis of the request"
    )
    title: Optional[str] = Field(
        default=None,
        description="Task title"
    )
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",
    )
    image_generation: Optional[ImageGeneration] = Field(
        default=None,
        description="Image generation parameters if applicable"
    )
    next_node: Optional[str] = Field(
        default=None,
        description="Next node to execute"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "request_type": "research",
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                    ),
                    "title": "AI Market Research Plan",
                    "steps": [
                        {
                            "need_search": True,
                            "title": "Current AI Market Analysis",
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                            ),
                            "step_type": "research",
                        }
                    ],
                },
                {
                    "request_type": "image_generation",
                    "has_enough_context": True,
                    "next_node": "image_generator",
                    "image_generation": {
                        "type": "text_to_image",
                        "prompt": "A cute kitten with big bright eyes, soft fluffy fur, sitting on a colorful blanket"
                    }
                }
            ]
        }
