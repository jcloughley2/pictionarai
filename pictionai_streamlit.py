import streamlit as st
from openai import OpenAI
import os
import weave

# Configure OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define prompts as constants
RANDOM_OBJECT_SYSTEM_PROMPT = "You are an assistant that provides names of random objects."
RANDOM_OBJECT_USER_PROMPT = "Please provide the name of a random object, and I mean really random."

JUDGMENT_SYSTEM_PROMPT = "You are an assistant judging how close a guess is to an original prompt."
JUDGMENT_USER_PROMPT_TEMPLATE = "The original prompt was: '{original_prompt}'. The user guessed: '{user_guess}'. Please judge how close the guess is. Please provide a score from 1 to 10, with 1 being not even close and 10 being an exact match."

def get_random_object_name(system_prompt: str, user_prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def get_prompt_image(original_prompt: str):
    response = client.images.generate(
        model="dall-e-3",
        prompt=original_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

@weave.op()
def random_object_generation(system_prompt: str, user_prompt: str):
    original_prompt = get_random_object_name(system_prompt, user_prompt)
    image_url = get_prompt_image(original_prompt)
    return {"original_prompt": original_prompt, "image_url": image_url}

@weave.op()
def get_judgment(original_prompt: str, user_guess: str, system_prompt: str, user_prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

st.title("Pictionar(ai)")

if 'random_object' not in st.session_state:
    st.session_state.random_object = None
    st.session_state.image_url = None

if st.button("Let's Play"):
    with st.spinner("Generating random object and image..."):
        result = random_object_generation(RANDOM_OBJECT_SYSTEM_PROMPT, RANDOM_OBJECT_USER_PROMPT)
        st.session_state.random_object = result["original_prompt"]
        st.session_state.image_url = result["image_url"]

if st.session_state.image_url:
    st.image(st.session_state.image_url, caption="Generated Image", use_column_width=True)
    
    user_guess = st.text_input("Guess the Object!")
    
    if st.button("Submit Guess"):
        if user_guess:
            with st.spinner("Judging your guess..."):
                user_prompt = JUDGMENT_USER_PROMPT_TEMPLATE.format(original_prompt=st.session_state.random_object, user_guess=user_guess)
                judgment = get_judgment(
                    original_prompt=st.session_state.random_object,
                    user_guess=user_guess,
                    system_prompt=JUDGMENT_SYSTEM_PROMPT,
                    user_prompt=user_prompt
                )
            st.success("Thank you for your submission!")
            st.write(judgment)
            
            if st.button("Play Again"):
                st.session_state.random_object = None
                st.session_state.image_url = None
                st.experimental_rerun()
        else:
            st.warning("Please enter a guess before submitting.")

st.sidebar.title("About")
st.sidebar.info(
    "This is a Streamlit version of the Pictionar(ai) game. "
    "Try to guess the random object based on the generated image!"
)

# Initialize the weave project
weave.init('pictionai')
