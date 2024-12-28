import torch
import jinja2
import json
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template, train_on_responses_only

# Constants
MAX_SEQ_LENGTH = 128000
DTYPE = None
LOAD_IN_4BIT = True
OUTPUT_DIR = "outputs"
LORA_OUTPUT_DIR = "lora_model"
GGUF_OUTPUT_DIR = "model"
GGUF_QUANTIZATION_METHOD = "q4_k_m"

SYSTEM_PROMPT = """You are a code analysis assistant. Your task is to analyze Python code against a natural language assertion and determine if the code fulfills the assertion.

You will receive:

1.  **Assertion**: A natural language assertion describing a desired property of the code. This assertion will reference code components using `{component_name}` notation.
2.  **Code Objects**: A set of named code objects. Each object has a name (matching a `{component_name}` in the assertion) and a Python code snippet.

Your task is to:

1.  **Parse and Interpret**:
    *   Identify each named code object (e.g., `{user_service}`) and load its corresponding Python code.
    *   Interpret the assertion, understanding the desired properties and how they relate to the code objects.

2.  **Evaluate**:
    *   Analyze the code, step-by-step, to determine if it fulfills the assertion.
    *   Check if all referenced components exist and are implemented as expected.
    *   Verify if the described properties hold true for the provided code snippets.

3.  **Reason (Chain-of-Thought)**:
    *   Provide a detailed, step-by-step reasoning process.
    *   Start from the assertion, break it down, examine the code, and explain how the code either meets or does not meet the described properties.
    *   Assume no prior knowledge of correctness; derive conclusions from first principles based on the given code and assertion.

4.  **Determine Result**:
    *   Conclude with a boolean decision: `true` if the code meets all aspects of the assertion, and `false` otherwise.

5.  **Explain (If Necessary)**:
    *   If the result is `false`, provide a concise explanation of why the code fails to meet the assertion.
    *   Focus on specific points of failure or omissions related to the assertion.

6.  **Output JSON**:
    *   Your final answer **must be a JSON object** with the following fields:
        *   `thoughts`: A string containing your chain-of-thought analysis.
        *   `result`: A boolean indicating whether the assertion is fulfilled by the given code.
        *   `explanation`: If `result` is `false`, include a string that explains the reasons for failure. If `result` is `true`, this field should be `null`.

**Output Format:**

```json
{
  "thoughts": "<Your detailed chain-of-thought reasoning>",
  "result": true or false,
  "explanation": "<A short explanation of why the assertion is not met, if and only if result is false. Otherwise null.>"
}
```

**Important Requirements:**

*   The `thoughts` field should contain your reasoning in natural language, describing how you interpreted the assertion, what you looked for in the code, and how you arrived at your conclusion.
*   The `result` field is strictly boolean (`true` or `false`).
*   The `explanation` field should only appear if `result` is `false`. Keep the explanation concise but specific, focusing on where and how the code fails to meet the assertion.
*   The output must be valid JSON and adhere strictly to the described schema. Do not include additional fields.
*   Do not mention the reasoning process or chain-of-thought instructions in the `result` or `explanation`; they are for your internal reasoning only.

---

**Examples**

**Positive Example:**

**Input:**

````
[Assertion]
"All methods in {payment_processor} delegate error handling to {error_manager} by wrapping their logic in a context manager."

[Code]
{payment_processor}:
```python
class PaymentProcessor:
    def __init__(self, error_manager):
        self.error_manager = error_manager

    def process_payment(self, amount):
        with self.error_manager.handle_errors('process_payment'):
            return self._run_payment(amount)

    def _run_payment(self, amount):
        # Simulate payment logic
        return True
```

{error_manager}:
```python
from contextlib import contextmanager

class ErrorManager:
    @contextmanager
    def handle_errors(self, operation_name):
        try:
            yield
        except Exception as e:
            # Log or handle error
            raise
```
````

**Output:**

```json
{
  "thoughts": "The assertion requires all methods in PaymentProcessor to delegate error handling to ErrorManager using a context manager. The code shows that the public method process_payment uses with self.error_manager.handle_errors(...). The private method _run_payment is called inside that block, so its errors are also covered. No methods appear to violate this rule. The error_manager class provides a context manager that could handle exceptions. Thus, the assertion is fulfilled.",
  "result": true,
  "explanation": null
}
```

---

**Negative Example:**

**Input:**

````
[Assertion]
"The {user_service} must use {pagination_helper} to paginate all list endpoints, ensuring that requests include a limit and offset."

[Code]
{user_service}:
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    users = ['Alice', 'Bob', 'Charlie']
    # This endpoint returns all users without pagination
    return jsonify(users)
```

{pagination_helper}:
```python
def paginate(data, limit, offset):
    return data[offset:offset+limit]
```
````

**Output:**

```json
{
  "thoughts": "The assertion states that user_service must use pagination_helper to paginate all list endpoints with limit and offset. The code shows a /users endpoint that returns a full list of users without calling paginate. pagination_helper is defined, but not used. Therefore, the code fails the assertion.",
  "result": false,
  "explanation": "The /users endpoint does not call paginate. It returns all users without applying limit and offset."
}
```
"""

INPUT_TEMPLATE = jinja2.Template("""[Assertion]
"{{ assertion }}"

[Code]
{%- for code_object in code_objects %}
{ {{- code_object["name"] -}} }:
```python
{{ code_object["code"] }}
```
{% endfor %}
""")


def generate_output(thoughts, result, explanation):
    output = {
        "thoughts": thoughts,
        "result": result,
        "explanation": explanation,
    }
    return json.dumps(output, indent=2)


def formatting_prompts_func(example):
    assertion = example["assertion"]["assertionText"]
    code_objects = example["codeObjects"]
    thoughts = example["thoughts"]
    explanation = example["explanation"]
    result = explanation is None

    rendered_input = INPUT_TEMPLATE.render(
        assertion=assertion, code_objects=code_objects
    )
    rendered_output = generate_output(thoughts, result, explanation)

    convo = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": rendered_input},
        {"role": "assistant", "content": rendered_output},
    ]

    text = tokenizer.apply_chat_template(
        convo, tokenize=False, add_generation_prompt=False
    )

    return {"text": text, "convo": convo}


def load_model_and_tokenizer(model_name, max_seq_length, dtype, load_in_4bit):
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )
    return model, tokenizer


def apply_lora_adapters(
    model,
    r=16,
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
):
    model = FastLanguageModel.get_peft_model(
        model,
        r=r,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias=bias,
        use_gradient_checkpointing=use_gradient_checkpointing,
        random_state=random_state,
        use_rslora=use_rslora,
        loftq_config=loftq_config,
    )
    return model


def get_chat_template_func(tokenizer, chat_template="llama-3.1"):
    tokenizer = get_chat_template(
        tokenizer,
        chat_template=chat_template,
    )
    return tokenizer


def load_and_map_datasets():
    dataset_train = load_dataset("kdunee/IntentGuard-1", split="train")
    dataset_test = load_dataset("kdunee/IntentGuard-1", split="test")

    dataset_train = dataset_train.map(
        formatting_prompts_func,
        batched=False,
    )
    dataset_test = dataset_test.map(
        formatting_prompts_func,
        batched=False,
    )
    return dataset_train, dataset_test


def initialize_trainer(model, tokenizer, dataset_train, max_seq_length, output_dir):
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset_train,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            num_train_epochs=3,
            learning_rate=2e-4,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=output_dir,
            report_to="none",
        ),
    )
    return trainer


def train_on_completions_only_func(
    trainer,
    instruction_part="<|start_header_id|>user<|end_header_id|>\n\n",
    response_part="<|start_header_id|>assistant<|end_header_id|>\n\n",
):
    trainer = train_on_responses_only(
        trainer,
        instruction_part=instruction_part,
        response_part=response_part,
    )
    return trainer


def show_memory_stats():
    gpu_stats = torch.cuda.get_device_properties(0)
    start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
    print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
    print(f"{start_gpu_memory} GB of memory reserved.")
    return start_gpu_memory, max_memory


def train_model(trainer):
    trainer_stats = trainer.train()
    return trainer_stats


def show_final_memory_stats(start_gpu_memory, max_memory, trainer_stats):
    used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
    used_percentage = round(used_memory / max_memory * 100, 3)
    lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)
    print(f"{trainer_stats.metrics['train_runtime']} seconds used for training.")
    print(
        f"{round(trainer_stats.metrics['train_runtime'] / 60, 2)} minutes used for training."
    )
    print(f"Peak reserved memory = {used_memory} GB.")
    print(f"Peak reserved memory for training = {used_memory_for_lora} GB.")
    print(f"Peak reserved memory % of max memory = {used_percentage} %.")
    print(f"Peak reserved memory for training % of max memory = {lora_percentage} %.")


def save_model_and_tokenizer(model, tokenizer, output_dir):
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)


def save_pretrained_gguf_func(model, tokenizer, output_dir, quantization_method):
    model.save_pretrained_gguf(
        output_dir, tokenizer, quantization_method=quantization_method
    )


if __name__ == "__main__":
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(
        model_name="unsloth/Llama-3.2-1B-Instruct",
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=DTYPE,
        load_in_4bit=LOAD_IN_4BIT,
    )

    # Apply LoRA adapters
    model = apply_lora_adapters(model)

    # Get chat template
    tokenizer = get_chat_template_func(tokenizer)

    # Load and map datasets
    dataset_train, dataset_test = load_and_map_datasets()

    # Initialize trainer
    trainer = initialize_trainer(
        model, tokenizer, dataset_train, MAX_SEQ_LENGTH, OUTPUT_DIR
    )

    # Train on completions only
    trainer = train_on_completions_only_func(trainer)

    # Show initial memory stats
    start_gpu_memory, max_memory = show_memory_stats()

    # Train model
    trainer_stats = train_model(trainer)

    # Show final memory stats
    show_final_memory_stats(start_gpu_memory, max_memory, trainer_stats)

    # Save model and tokenizer
    save_model_and_tokenizer(model, tokenizer, LORA_OUTPUT_DIR)

    # GGUF conversion
    save_pretrained_gguf_func(
        model, tokenizer, GGUF_OUTPUT_DIR, GGUF_QUANTIZATION_METHOD
    )
