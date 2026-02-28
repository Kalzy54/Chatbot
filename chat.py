import yaml
import logging
import argparse
from types import SimpleNamespace
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_config(config_path='config.yaml'):
    print('-> Loading config file ...')
    cfg = yaml.safe_load(
        open(config_path).read()
    )

    for k,v in cfg.items():
        if type(v) == dict:
            cfg[k] = SimpleNamespace(**v)
    cfg = SimpleNamespace(**cfg)
    return cfg

def get_prompt_template():
    # Import heavy library locally to avoid requiring it when running the server
    from llama_index.core import Prompt
    template = (
        "You are a helpful and intelligent virtual assistant designed to answer user questions based on relevant context information provided.\n"
        "Context information:\n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Based on the context information provided above, please answer the following question: {query_str}\n"
    )
    qa_template = Prompt(template)
    return qa_template

def reset_settings(cfg):
    # local import to avoid heavy deps at module import time
    from langchain_huggingface import HuggingFaceEmbeddings
    from llama_index.core import Settings
    embed_model = HuggingFaceEmbeddings(
        model_name=cfg.architecture.embedding_model
    )
    Settings.embed_model = embed_model
    Settings.llm = None

def get_retriever(cfg, prompt_template):
    import pandas as pd
    from llama_index.core.schema import TextNode
    from llama_index.core import VectorStoreIndex

    chunks = pd.read_pickle('processed_chunks.pickle')['chunk'].values.tolist()
    nodes = [TextNode(text=chunk) for chunk in chunks]
    index = VectorStoreIndex(nodes=nodes)
    retriever = index.as_query_engine(
        similarity_top_k=cfg.retrieve.top_k,
        text_qa_template=prompt_template
    )
    return retriever

def load_tokenizer(cfg):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        cfg.architecture.llm_model,
        token=cfg.architecture.hf_token
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer

def get_llm(cfg):
    # Local imports for heavy ML libs
    import torch
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    if cfg.architecture.llm_quantized:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
    else:
        bnb_config = None

    llm = AutoModelForCausalLM.from_pretrained(
        cfg.architecture.llm_model,
        torch_dtype=getattr(torch, 'bfloat16', None) or None,
        device_map=cfg.environment.device,
        token=cfg.architecture.hf_token,
        low_cpu_mem_usage=True,
        quantization_config=bnb_config,
    )

    return llm.eval()


def vistral_chat(cfg, retriever, tokenizer, language_model):
    while True:
        user_query = input('👨‍🦰 ')
        prompt = retriever.query(user_query).response
        prompt = tokenizer.bos_token + '[INST] ' + prompt + ' [/INST]'
        # local import to avoid top-level dependency
        from transformers import TextStreamer
        streamer = TextStreamer(tokenizer, skip_prompt=True)
        input_ids = tokenizer([prompt], return_tensors='pt').to(cfg.environment.device)

        _ = language_model.generate(
            **input_ids,
            streamer=streamer,
            pad_token_id=tokenizer.pad_token_id,
            max_new_tokens=cfg.generation.max_new_tokens,
            do_sample=cfg.generation.do_sample,
            temperature=cfg.generation.temperature,
        )

        print(20 * '---')


def main(config_path):
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        # Log the start of the process
        logger.info("Starting the process with config file: %s", config_path)
        
        # Load configuration from the file
        config = load_config(config_path)
        
        # Load necessary components
        prompt_template = get_prompt_template()
        
        # Replace OpenAI embed model and llm with custom ones
        reset_settings(config)
        
        # Get retriever
        retriever = get_retriever(config, prompt_template)
        
        # Load tokenizer and language model
        tokenizer = load_tokenizer(config)
        language_model = get_llm(config)
        
        # Start the command line interface
        vistral_chat(config, retriever, tokenizer, language_model)
        
        # Log successful completion
        logger.info("Process completed successfully.")
        
    except FileNotFoundError as e:
        logger.error("Configuration file not found: %s", e)
    except Exception as e:
        logger.exception("An error occurred: %s", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some configurations or run server.')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to the configuration file')
    parser.add_argument('--serve', action='store_true', help='Run the FastAPI server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host for server')
    parser.add_argument('--port', type=int, default=8000, help='Port for server')
    args = parser.parse_args()
    if args.serve:
        try:
            import uvicorn
            uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False)
        except Exception as e:
            print("Failed to start server:", e)
    else:
        main(args.config)