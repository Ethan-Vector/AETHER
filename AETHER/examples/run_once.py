from aether.agent import default_agent_from_env

if __name__ == "__main__":
    agent = default_agent_from_env()
    res = agent.run("calculate: (10+5)/3")
    print(res.final)
    print("trace:", res.trace_path)
