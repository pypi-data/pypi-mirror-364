#!/usr/bin/env python3
# /// script
# dependencies = [
#    "strands-agents",
#    "strands-agents-builder",
#    "strands-agents-tools",
# ]
# ///
from strands import Agent
from strands.models import BedrockModel

from strands import tool
from datetime import datetime


# tool の定義
@tool(name="get_time", description="現在の時間を返す")
def get_time() -> str:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"現在の時刻は {current_time} です"


bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    # model_id="us.amazon.nova-micro-v1:0",
    region_name='us-east-1',
)


def main():
    agent = Agent(model=bedrock_model, tools=[get_time])
    agent("こんにちは。今何時ですか? また AWS の Strands Agents について知っていることについて簡潔に教えてください。")


if __name__ == "__main__":
    main()
