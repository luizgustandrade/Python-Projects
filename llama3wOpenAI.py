from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

completion = client.chat.completions.create(
  model="meta/llama3-8b-instruct",
  messages=[{"role":"user","content":"Tell me tips about Los Angeles."}],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")