from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

def facebook(text,max_length,min_length):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)

def google(text, max_length, min_length):
    model_name = "google/long-t5-tglobal-base"  # or "google/long-t5-tglobal-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=16000)
    summary_ids = model.generate(inputs.input_ids, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

