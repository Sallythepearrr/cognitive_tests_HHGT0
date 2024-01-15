from IPython.display import display, clear_output, HTML, Image
import random
random.seed(1)

import time
import ipywidgets as widgets
from jupyter_ui_poll import ui_events

import os
import re

import requests
from bs4 import BeautifulSoup
import json


# Pre-test questions
def consent_info():
    data_consent_info = """DATA CONSENT INFORMATION:
    
    Please read:
    
    we wish to record your response data to an anonymised public data repository.
    Your data will be used for educational teaching purposes 
    practising data analysis and visualisation.
    Please type yes in the box below if you consent to the upload."""
    
    print(data_consent_info)
    result = input("> ")
    
    if result == "yes":
        print("Thanks for your participation.")
        print("Please contact philip.lewis@ucl.ac.uk")
        print("If you have any questions or concerns")
        print("regarding the stored results.")
    
    else:
        # end code execution by raising an exception
        raise(Exception("User did not consent to continue test."))
    return


def id_instruction():
    id_instructions = """
    Please enter your anonymised ID
    
    To generate an anonymous 4-letter unique user identifier please enter:
    - two letters based on the initials (first and last name) of a childhood friend
    - two letters based on the initials (first and last name) of a favourite actor / actress
    
    e.g. if your friend was called Charlie Brown and film star was Tom Cruise
    then your unique identifer would be CBTC
    """
    
    print(id_instructions)
    user_id = input("> ")
    return user_id


def other_info():
    print("Please enter your age:")
    age = input("> ")
    
    print("Please indicate whether your major or occupation is more aligned with 'science' or 'art':")
    major = input("> ")
    return age, major



# Send to google
def send_to_google_form(data_dict, form_url):
    ''' Helper function to upload information to a corresponding google form 
        You are not expected to follow the code within this function!
    '''
    form_id = form_url[34:90]
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]
    form_dict = {}
    
    loaded_all = True
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]
    
    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok

# File dictionary for images that will display in the tests

# Read file name and create a dictionary that contains the image name as key and 
# the answer (Right or Left) as corresponding value
# Get the image file and the corresponding answers
def get_file_dict():
    
    current_directory = os.getcwd()


    # Specify the relative path to local files
    relative_path = ''
    
    # Combine the current directory and relative path to get the full path
    directory_path = os.path.join(current_directory, relative_path)
    
    file_dict = {}
    
    # Define a regular expression pattern to extract numbers from the file names
    pattern = re.compile(r'dots_image_(\d{1,2})x(\d{1,2})_same.png')
    
    # Iterate over files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a PNG file
        if filename.endswith('.png'):
            # Use regular expression to extract numbers from the file name
            match = pattern.match(filename)
            if match:
                left_side_num = int(match.group(1))
                right_side_num = int(match.group(2))
    
                # Compare left_side_num and right_side_num
                if left_side_num > right_side_num:
                    file_dict[filename] = 'Left'
                elif left_side_num < right_side_num:
                    file_dict[filename] = 'Right'
                else:
                    file_dict[filename] = 'Unknown'
    return file_dict


def create_shuffled_list():
    
    file_dict = get_file_dict()
    
    # Get the image files and answers from file_dict
    image_files = list(file_dict.keys())
    answers = list(file_dict.values())
    
    
    # Assume the test contained 64 trials that lasts around 4 mins
    # As there are 16 images in original files, we need to repeat 4 times
    total_image_in_block = image_files * 4
    total_answers_in_block = answers * 4

    # Combine image files and answers into pairs
    # file_pairs = list(zip(image_files, answers))
    pairs = list(zip(total_image_in_block, total_answers_in_block))

    # Shuffle the pairs
    random.shuffle(pairs)
    random.seed(1)

    # Unzip the pairs back into separate lists
    shuffled_image_files, shuffled_answers = zip(*pairs)

    # Convert the result back to lists
    shuffled_image_files = list(shuffled_image_files)
    shuffled_answers = list(shuffled_answers)

    return shuffled_image_files, shuffled_answers


# Functions for dislaying test images, buttons and time-out
def display_img(img_file):
    style_str = f'width: 500px;'
    html_out = HTML(f"<img style='{style_str}' src={img_file}></img>")
    display(html_out)

# Create Time-out
event_info = {
    'type': '',
    'description': '',
    'time': -1
}

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):    
    start_wait = time.time()

    # set event info to be empty
    # as this is dict we can change entries
    # directly without using
    # the global keyword
    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:
            # process UI events
            ui_poll(n_proc)

            # end loop if we have waited more than the timeout period
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False
                
            # end loop if event has occured
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False
                
            # add pause before looping
            # to check events again
            time.sleep(interval)
    
    # return event description after wait ends
    # will be set to empty string '' if no event occured
    return event_info

# this function lets buttons register events when clicked
def register_btn_event(btn):
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()
    return

# ANS Test Code

# Function that test ANS for one trial with button features
def ANS_test_single(img_file, blank_img, right_answer):

    top_area = widgets.Output(layout={"height":"60px"})
    main_area = widgets.Output(layout={"height":"350px"})
    bottom_area = widgets.Output(layout={"height":"60px"})

    btn1 = widgets.Button(description="Left")
    btn2 = widgets.Button(description="Right")

    btn1.on_click(register_btn_event)
    btn2.on_click(register_btn_event)

    panel = widgets.HBox([btn1, btn2])

    top_area.append_display_data( HTML("<h1>Which side has more dots?</h1>") )
    bottom_area.append_display_data(panel)

    display(top_area)
    display(main_area)
    display(bottom_area)

    with main_area: 
        display_img(img_file) # Display the image
        time.sleep(0.75) # Wait for 0.75 seconds

        clear_output(wait=True)
        display_img(blank_img)  # Display a blank image or placeholder imag

    score = 0
    
    start_time = time.time()
    result = wait_for_event(timeout=3)
    
    end_time = time.time()
    
    response_time =  end_time - start_time
    
    ans = "NA"
    if result['description'] == '':
        with main_area: 
            score = 0
            ans = "NA"
    elif result['description'] ==  right_answer:
        with main_area: 
            score = 1
            ans = result["description"]
    else:
        with main_area: 
            score = 0
            ans = result["description"]
    
    clear_output()
    wait_for_event(timeout=1.5)
        
    return score, ans, response_time


def ANS_test():
    total_score = 0
    input_answers = []
    response_times = []

    shuffled_image, shuffled_answers = create_shuffled_list()
    blank_img = "blank.png"

    for image, answer in zip(shuffled_image, shuffled_answers):
        score, input_ans, response_time = ANS_test_single(image, blank_img, answer)
        total_score += score
        
        input_answers.append(input_ans)
        response_times.append(response_time)
        
    print(f'You scored {total_score} out of {len(shuffled_image)}')
    return total_score, shuffled_image, shuffled_answers, input_answers, response_times


def run_ANS_test():
    consent_info()
    clear_output()
    
    user_id = id_instruction()
    clear_output()
    
    age, major = other_info()
    clear_output()
    
    total_score, shuffled_image, shuffled_answers, input_answers, response_times = ANS_test()

    # Send results to google form
    data_dict = {
        'user_id': user_id,
        'age': age,
        'subject': major,
        'score': total_score,
        'image names same': shuffled_image, 
        'image answers same': shuffled_answers,
        'input answers': input_answers,
        'reaction times': response_times
    }
    
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLScWXr-igXq9VC9caYLvd4v_vnf--KyrpeLZjAqiyJA0CzcSXg/viewform?usp=sf_link'
    send_to_google_form(data_dict, form_url)
    return

