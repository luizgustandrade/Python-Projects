from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

completion = client.chat.completions.create(
  model="meta/llama3-8b-instruct",
  messages=[{"role":"user","content":"Tell me everything that you find about in internet this profile https://www.instagram.com/phcabral and can you also list youtube channels or other profiles that I can search and access ? "}],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")