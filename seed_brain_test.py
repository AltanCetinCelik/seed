from seed_brain import ask_seed


user_prompt = input("Talk to Seed: ")
answer = ask_seed(user_prompt)

print("\n=== SEED RESPONSE ===")
print(answer)