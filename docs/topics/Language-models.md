# How a large language model works guide

*What is inside a chatbot, from the words it reads to how it was trained. Four parts: stop at the one you need.*

[In one minute](#in-one-minute) · [Do it](#do-it) · [Expert](#expert) · [Now and next](#now-and-next)

## In one minute

A large language model plays one game, over and over: **guess the next piece of text**. Shown "The cat sat on the", it gives a score to every possible next piece, "mat" high and "volcano" low. It picks one, adds it to the text, and guesses again. A whole answer is built this way, one piece at a time.

It got good at the game by reading a huge amount of text and adjusting billions of numbers inside it, a little after each wrong guess. Afterwards it was trained more on examples of helpful answers, and on people's ratings of which answer was better.

So it does not look facts up in a database. It produces text that **sounds right** given what it read. Most of the time that is also correct; sometimes it is confidently wrong. Check anything that matters.

<figure class="sketch"><span class="ai-tag">AI-created</span><svg viewBox="0 0 640 400" role="img" aria-labelledby="sk-cs-nextword-t"><title id="sk-cs-nextword-t">A language model scores every possible next word after "The cat sat on the": mat high, volcano low; it picks one, adds it, and guesses again</title><defs><filter id="sk-cs-nextword-pen"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter><filter id="sk-cs-nextword-paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="7"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.35  0 0 0 0 0.25  0 0 0 .10 0"/></filter><pattern id="sk-cs-nextword-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="#8a4a2a" stroke-width="1.1" opacity=".55"/></pattern><pattern id="sk-cs-nextword-dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1" fill="#8a4a2a" opacity=".5"/><circle cx="6.5" cy="7" r=".8" fill="#8a4a2a" opacity=".4"/></pattern><marker id="sk-cs-nextword-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#3a2a1e" stroke-width="1.6" stroke-linecap="round"/></marker></defs><rect width="640" height="400" filter="url(#sk-cs-nextword-paper)"/><g filter="url(#sk-cs-nextword-pen)"><text x="30" y="44" class="h">Guess the next piece</text><text x="40" y="110" class="l">The cat sat on the …</text><text x="120" y="166" text-anchor="end" class="l">mat</text><path class="p gold" d="M132 150 L380.0 150 L380.0 172 L132 172Z"/><text x="120" y="202" text-anchor="end" class="l">floor</text><path class="p room" d="M132 186 L212.0 186 L212.0 208 L132 208Z"/><text x="120" y="238" text-anchor="end" class="l">sofa</text><path class="p room" d="M132 222 L180.0 222 L180.0 244 L132 244Z"/><text x="120" y="274" text-anchor="end" class="l">roof</text><path class="p room" d="M132 258 L152.0 258 L152.0 280 L132 280Z"/><text x="120" y="310" text-anchor="end" class="l">volcano</text><path class="p room" d="M132 294 L136.0 294 L136.0 316 L132 316Z"/><path class="p" d="M420 156 C470 130 500 110 520 108" marker-end="url(#sk-cs-nextword-ah)"/><text x="440" y="74" class="s">pick one, add it,</text><text x="440" y="96" class="s">then guess again</text><text x="30" y="356" class="s">Scores for every possible next piece, learnt from a huge amount of text.</text><text x="30" y="378" class="s">It sounds right; it is usually right; check anything that matters.</text></g></svg><figcaption>Sketched for this page. The scores are made up to show the idea.</figcaption></figure>

## Do it

**Run a small model on your own computer** (Python, `pip install transformers torch`)

```python
from transformers import pipeline

generate = pipeline("text-generation", model="gpt2")    # a small 2019 model, about 500 MB
print(generate("Mars is", max_new_tokens=20)[0]["generated_text"])
```

**See the pieces it reads** (tokens)

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2")
tok.tokenize("Unbelievable sandstorms on Mars")         # words are split into common pieces
tok("Mars")["input_ids"]                                # each piece is a number
```

**Bigger open models on a laptop:** llama.cpp or Ollama (`ollama run <model name>`) run quantized open-weight models on an ordinary CPU or GPU.

**Build one from scratch:** the [ML book, chapter 19](../books/machine-learning/19-Transformers.md) writes a transformer in NumPy, step by step; [chapter 15](../books/machine-learning/15-Neural-Networks-and-Backpropagation.md) builds the neural-network parts it rests on.

## Expert

### The pieces, and where each came from

| Piece | What it does | Key paper |
|---|---|---|
| Tokenizer (byte-pair encoding) | splits text into pieces from a fixed vocabulary of tens of thousands | Sennrich, Haddow and Birch, 2016 |
| Embeddings | turns each token into a vector of numbers | Mikolov and others (word2vec), 2013 |
| Transformer, self-attention | lets every position look at every earlier one and weigh what matters | Vaswani and others, "Attention Is All You Need", 2017 |
| Pretraining on next-token prediction | learns language and a great deal of knowledge from raw text | Radford and others (GPT), 2018; Brown and others (GPT-3), 2020 |
| Scaling laws | loss falls predictably with more parameters, data and compute | Kaplan and others, 2020; Hoffmann and others ("Chinchilla"), 2022 |
| Instruction tuning, learning from human feedback | turns a text predictor into an assistant | Ouyang and others (InstructGPT), 2022; Rafailov and others (DPO), 2023 |
| Retrieval-augmented generation | looks up documents and puts them in the prompt | Lewis and others, 2020 |
| Sampling | temperature, top-k, nucleus sampling choose the next token | Holtzman and others, 2019 |
| Efficient attention and serving | FlashAttention (2022), paged KV-cache (vLLM, 2023), quantization, LoRA fine-tuning (2021) | |

Cost: generating each token runs the whole network once; attention over $n$ tokens costs $O(n^2)$ in time for a full pass, which is why long contexts are expensive.

### Implementations

| Tool | Use |
|---|---|
| **PyTorch**, **JAX** | training and research |
| **Hugging Face Transformers** | thousands of open models behind one API |
| **vLLM**, **TensorRT-LLM**, **SGLang** | serving many users fast |
| **llama.cpp**, **Ollama**, **MLX** (Apple) | running models on a laptop or phone |
| **nanoGPT** and similar teaching code | a whole GPT in a few hundred lines |

### Common mistakes

| Mistake | What happened |
|---|---|
| **Treating output as fact** | In 2023 a New York lawyer filed a brief citing court cases a chatbot had invented; the court fined the lawyers (Mata v. Avianca). Ask for sources and check them. |
| **Prompt injection** | Text inside a web page, email or file can carry instructions the model follows, because it can't reliably tell data from orders (Greshake and others, 2023). Never give a model tools and untrusted input without limits. |
| **Pasting secrets into a hosted chatbot** | Company code and data have leaked this way; what you type may be stored. Follow your organisation's rules, or run a local model. |
| **Benchmarks the model has already seen** | Test questions found on the web end up in training data ("contamination"), so scores look better than real ability. Test on fresh, private examples. |
| **Judging by a few good answers** | Outputs vary from run to run. Measure on a fixed set of cases, many times. |
| **Expecting arithmetic and exact counting** | The model sees tokens, not letters or digits; give it a calculator or code tool instead. |

### Best practices

- Ground answers in documents you supply (retrieval), and show the sources.
- Keep a person in the loop for anything with consequences.
- Give tools only the permissions the task needs; treat every external text as untrusted.
- Build an evaluation set from your real task before choosing or tuning a model.
- Start small: a smaller model with good retrieval often beats a larger one without it.

### Learn it properly

- [ML book](../books/machine-learning/index.md): [chapter 15](../books/machine-learning/15-Neural-Networks-and-Backpropagation.md) neural networks, [chapter 18](../books/machine-learning/18-Sequence-Models.md) sequence models, [chapter 19](../books/machine-learning/19-Transformers.md) transformers, [chapter 20](../books/machine-learning/20-Generative-Models.md) generative models
- [AI book, chapter 17](../books/ai/17-Large-Language-Models.md): pretraining, sampling, feedback training, retrieval, tools, evaluation and limits

## Now and next

*Last checked: 4 November 2026.*

- **Thinking longer at answer time.** Models trained with reinforcement learning to work through problems step by step before answering do much better on math and code; spending more compute at answer time is now a second way to scale, beside bigger training.
- **Agents.** Models that call tools, browse and write code over many steps; reliability and security (prompt injection) are the open problems.
- **Small and local.** Distilled and quantized models run on phones and laptops, which helps privacy and cost.
- **Looking inside.** Mechanistic interpretability (for example sparse autoencoders that find readable "features" in a model) tries to explain what the numbers do; see the [ML book, chapter 23](../books/machine-learning/23-Where-Machine-Learning-Goes.md).
- **Open questions:** how far scaling continues, how to measure real reasoning, how to make models reliably say "I don't know".
