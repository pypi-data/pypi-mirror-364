from transformers import AutoTokenizer, pipeline
import torch
import fasthug


MODEL_ID = 'facebook/opt-125m'
PROMPT = "Once upon a time"
MAX_NEW_TOKENS = 5


def test_generate_manual():
    torch.manual_seed(0)
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = fasthug.from_pretrained(MODEL_ID).cuda()

    input_ids = tokenizer.encode(PROMPT, return_tensors="pt").cuda()
    output_ids = model.generate(input_ids, max_new_tokens=MAX_NEW_TOKENS)
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    assert output_text == "Once upon a time, I was a student"


def test_generate_pipeline():
    torch.manual_seed(0)
    
    model = fasthug.from_pretrained(MODEL_ID)
    generator = pipeline("text-generation", model=model, tokenizer=MODEL_ID)
    output = generator(PROMPT, max_new_tokens=MAX_NEW_TOKENS)

    assert output[0]["generated_text"] == "Once upon a time, my daughter was in"