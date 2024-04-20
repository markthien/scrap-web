import json
from scrapy.selector import Selector

def export_json():
    # Initialize the JSON object
    data = {}

    # Add the 'average_eps_growth' key
    data['average_eps_growth'] = {}

    # Add the 'stock' key
    data['average_eps_growth']['stock'] = "META"

    # Add the 'from_site' key
    data['average_eps_growth']['from_site'] = []

    # Add the 'average' key
    data['average_eps_growth']['average'] = "20%"

    # Dynamically add data to the 'from_site' list
    # for i in range(3):
    site_data = {
        "domain_name": "zack",
        "eps": "19%"
    }
    data['average_eps_growth']['from_site'].append(site_data)
    site_data = {
        "domain_name": "finviz",
        "eps": "21%"
    }
    data['average_eps_growth']['from_site'].append(site_data)    
    
    with open("output_stock_analysis.json", "w") as write_file:
        json.dump(data, write_file, indent=4)

def chatgpt_prompt_eng():

    text = f"""
    You should express what you want a model to do by \ 
    providing instructions that are as clear and \ 
    specific as you can possibly make them. \ 
    This will guide the model towards the desired output, \ 
    and reduce the chances of receiving irrelevant \ 
    or incorrect responses. Don't confuse writing a \ 
    clear prompt with writing a short prompt. \ 
    In many cases, longer prompts provide more clarity \ 
    and context for the model, which can lead to \ 
    more detailed and relevant outputs.
    """
    prompt = f"""
    Summarize the text delimited by triple backticks \ 
    into a single sentence.
    ```{text}```
    """
    print(prompt)

def test_scrapy():
    body = "<html><body> \
                <table> \
                    <tr> \
                        <td class=\"haha1\"> \
                            <span>Awesome 1</span> \
                        </td> \
                        <td> \
                            <span>Awesome 2</span> \
                        </td> \
                    </tr> \
                   <tr> \
                        <td class=\"haha2\"> \
                            <span>Awesome 3</span> \
                        </td> \
                    </tr> \
                </table> \
            </body></html>"
    result = Selector(text=body).xpath("//td/span[text()=\"Awesome 1\"]/following::td/span/text()").get()
    print(f'result = {result}')

test_scrapy()        