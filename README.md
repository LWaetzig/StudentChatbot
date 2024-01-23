# STUDENTS GPT

## What is it
Repository for the PDF-Chatbot. Detailed report about the development process as well as some learnings can be found [here]().

### Project Scope

![Process.png](data/Process.png)


### Text Extraktion Model


### Semantic Chunking
In order to improve the way how the text is splitted, we implemented a different approach. This approach tries to identifies chunk points based in semantics. Further explanaition and code can be found [here]()

### Models
- we tested three models using a open source lecture set from MIT -> [Lecture Notes](data/test_lecture_set.pdf)
- The Models are:
  - [Falcon-7B-instruct](https://huggingface.co/tiiuae/falcon-7b-instruct)
  - [FLAN-T5-xxl](https://huggingface.co/google/flan-t5-xxl)
  - [DistilBERT finetuned on SQuAD](https://huggingface.co/distilbert-base-uncased-distilled-squad)
- Models are compaired and evaluated based on the following categories
- Evaluation and test results can be found [here]()

## Collaborators
+ Lars Kurschilgen
+ Nicholas Link
+ Alexander Paul
+ Adrian Setz
+ Lucas Wätzig
+ Jan Wolter


## Requirements

1. Clone Repository
2. Create a virtual python environment -> [Link](https://realpython.com/lessons/creating-virtual-environment/)
3. Install required packages listed in [requirements.txt](./requirements.txt)
4. The Application is build using streamlit. To run the app execute the following command in the projects directory ```streamlit run app.py```
5. The app will open in a new browser tab. If not follow the link displayed in your terminal

