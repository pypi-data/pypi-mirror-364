from agents import Agent, Runner, trace
from agents.mcp.server import MCPServerStdio
from PointrAgent import SYSTEM_PROMPT
import os
from dotenv import load_dotenv

load_dotenv(override=True)


async def mcp_test():
    env = {"PC_API_URL": os.getenv("PC_API_URL"), "PC_CLIENT_ID": "this is a different client id", "PC_CLIENT_SECRET": os.getenv("PC_CLIENT_SECRET")}
    params = {"command": "uv", "args": ["run", "PointrAgent.py"], "env": env}
    model = "gpt-4.1-mini"
    history = []

    async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
        agent = Agent(name="PointrAgent", instructions=SYSTEM_PROMPT, model=model, mcp_servers=[mcp_server])
        print("Chatbot started. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            # Add user message to history
            history.append({"role": "user", "content": user_input})
            with trace("PointrAgent"):
                # Pass the history to the agent (adapt this if your agent expects a different format)
                result = await Runner.run(agent, history)
                print("Bot:", result.final_output)
                # Add bot response to history
                history.append({"role": "assistant", "content": result.final_output})


if __name__ == "__main__":
    import asyncio
    from agents import Runner

    # Run the main function in an asyncio event loop
    #asyncio.run(main())


    asyncio.run(mcp_test())
    