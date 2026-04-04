import torch
from src.retrieval.retriever import retrieve
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype=torch.bfloat16,
    device_map="auto"
)

def generate_answer(context, query):
    user_content = f"Context:\n{context}\nQuestion:{query}"

    messages = [
        {
            "role": "system",
            "content": "You are a medical assistant. Use only provided context."
        },
        {
            "role": "user",
            "content": user_content
        }
    ]

    prompt = tokenizer.apply_chat_template(messages, tokenize=False)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    input_length = inputs["input_ids"].shape[1]

    output = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.3
    )

    return tokenizer.decode(output[0][input_length:], skip_special_tokens=True)

def main():
    while True:
        query = input("> ")
        results = retrieve(query)
        context = "\n\n".join(result["text"] for result in results)
        answer = generate_answer(context, query)
        print(answer)

if __name__ == "__main__":
    main()