import openrouterfreescanner

print("--- Testing get_all_models() ---")
all_models = openrouterfreescanner.get_all_models()
if all_models:
    print(f"Found {len(all_models)} models.")

print("\n--- Testing get_free_models() ---")
free_models = openrouterfreescanner.get_free_models()
if free_models:
    print(f"Found {len(free_models)} free models.")

print("\n--- Testing get_n_models(5) ---")
top_5_free_models = openrouterfreescanner.get_n_models(5)
if top_5_free_models:
    print(f"Found {len(top_5_free_models)} models.")
    for model in top_5_free_models:
        print(f"- {model['name']}")

print("\n--- Testing get_n_models(10, free_only=False) ---")
top_10_all_models = openrouterfreescanner.get_n_models(10, free_only=False)
if top_10_all_models:
    print(f"Found {len(top_10_all_models)} models.")
    for model in top_10_all_models:
        print(f"- {model['name']}")

print("\n--- Testing filter_models_by_name('gemma') ---")
gemma_models = openrouterfreescanner.filter_models_by_name("gemma")
if gemma_models:
    print(f"Found {len(gemma_models)} 'gemma' models.")
    for model in gemma_models:
        print(f"- {model['name']}")

print("\n--- Testing filter_models_by_name('gemma', free_only=False) ---")
all_gemma_models = openrouterfreescanner.filter_models_by_name("gemma", free_only=False)
if all_gemma_models:
    print(f"Found {len(all_gemma_models)} 'gemma' models (including paid)." )
    for model in all_gemma_models:
        print(f"- {model['name']}")