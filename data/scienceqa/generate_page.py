

import os
import json

# def replace_holder(text, holder):
#     # normalize html code
#     text = text.replace("\n", "")
#     # replace holder
#     text = text.replace("[HOLDER]", holder)
#     text = text.replace("\u2014", " ")
#     text = text.replace("\n", " ")
#     text = text.strip()
#     return text


def capitalize_module(text):
    # capitalize text
    text = text.split("_")
    text = " ".join([word.capitalize() for word in text])
    return text

def normalize(html):
    # normalize html code
    html = html.replace("\n", " ")
    html = html.replace("\u2014", " ")
    html = html.strip()
    return html

def generate_message(result):
    message = ""
    
    # [1] question
    html = ""
    ques = result["question"]
    html = f"""
            <p><b>Question</b></p>
            <p class='question-txt'>{ques}</p>
    """
    question = normalize(html)

    # [2] context
    html = ""
    cont = result["context"]
    if cont != "":
        html = f"""
                <p><b>Context </b></p><p class='hint-txt'>{cont}</p>
        """
    context = normalize(html)

    # [3] image
    html = ""
    path = result["image"]
    if path:
        html = f"""
                <img src='{path}' alt='example image' class='question-img'/>
        """
    image = normalize(html)

    # [4] choices
    html = ""
    temp = ""
    cholen = 0
    options = result["choices"]
    if options:
        for option in options:
            temp += f"""
                <div class='choice-txt'>{option}</div>     
            """
            cholen += len(option)
        if cholen > 60:
            html = f"""
                <p><b>Choices </b></p><div class='choices'>{temp}</div>
            """
        else:
            html = f"""
                <p><b>Choices </b></p><div class='choices'>{temp}</div>
            """
    choices = normalize(html)

    # [5] modules
    html = ""
    modules = result["modules"]
    program = ", ".join([capitalize_module(module) for module in modules])
    html = f"""
                    <p><b>Program </b></p><p class='module-txt'>{program}</p>
            """
    program = normalize(html)

    # [6] responses
    html = ""
    modules = result["modules"]

    html = f"""
                    <p><b>Response </b></p>
            """
    for module in modules:
        response = str(result[module]["output"])
        response = response.replace("\n", "<br>")
        module = capitalize_module(module)
        html += f"""
                    <p class='module-txt'>{module}</p>
                    <p class='response-txt'>{response}</p>
                """
    
    responses = normalize(html)


    # [7] prediction
    html = ""
    prediction = result["prediction"]
    true_false = result["true_false"]
    if true_false:
        html = f"""
                    <p><b>Prediction:</b>
                        <a class='correct-txt'> {prediction}</a> (correct)
                    </p>
                """
    else:
        html = f"""
                    <p><b>Prediction:</b>
                        <a class='wrong-txt'> {prediction}</a> (wrong)
                    </p>
                """
    prediction = normalize(html)

    # [8] answer
    html = ""
    answer = result["answer"]
    html = f"""
                <p><b>Answer:</b>
                    <a class='answer-txt'> {answer}</a>
                </p>
            """
    answer = normalize(html)

    # build the message
    elements = [question, context, image, choices, program, prediction, answer]
    # elements = [question, context, image, choices, program, responses, prediction, answer]
    message = " ".join(elements)

    return message


def generate(result_file):
    results = {}

    for line in open(result_file):
        data = json.loads(line)
        result = {}

        # get data
        pid = data["pid"]

        # get module results
        modules = data["modules:output"]
        if "text_detector:output" in data:
            texts = data["text_detector:output"]
            texts = [(text[0][0], text[1]) for text in texts]
            texts = "\n".join([f"{text[0]}: {text[1]}" for text in texts])
            data["text_detector:output"] = texts

        module_result = {"modules": modules}
        for module in modules:
            module_result[module] = {"input": data[f"{module}:input"], "output": data[f"{module}:output"]}
        
        image_file = f"images/{pid}/image.png" if data["example"]["image"] else None
        
        # get example results
        result = {
                    "pid": pid, 
                    "question": data["example"]["question"],
                    "context": data["example"]["hint"],
                    "image": image_file,
                    "choices": data["example"]["choices"],
                    "answer": data["example"]["choices"][data["example"]["answer"]],
                    "prediction": data["prediction"],
                    "true_false": data["true_false"],
                }
        
        # save data
        result = {**result, **module_result}
        
        # generate message
        message = generate_message(result)
        result["message"] = message

        results[pid] = result

    return results


if __name__ == "__main__":

    labels = ["chameleon_gpt4", "chameleon_chatgpt"]

    for label in labels:
        input_file = f"raw_results/{label}_test_cache.jsonl"
        output_file = f"{label}.json"

        # generate results
        results = generate(input_file)

        # save  results
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

