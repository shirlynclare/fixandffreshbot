import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Set up the model
model = genai.GenerativeModel('gemini-pro')

def get_gemini_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def generate_service_chart(data_type, user_data=None):
    if data_type == "Popular Services":
        if user_data:
            df = pd.DataFrame(user_data)
        else:
            df = pd.DataFrame({
                "Service": ["Oil Change", "Tire Rotation", "Brake Service", "Engine Tune-up", "A/C Service"],
                "Percentage": [30, 25, 20, 15, 10]
            })
        fig = px.pie(df, values="Percentage", names="Service", title="Popular Garage Services")
    elif data_type == "Average Service Costs":
        if user_data:
            df = pd.DataFrame(user_data)
        else:
            df = pd.DataFrame({
                "Service": ["Oil Change", "Tire Rotation", "Brake Service", "Engine Tune-up", "A/C Service"],
                "Cost": [50, 30, 200, 150, 100]
            })
        fig = px.bar(df, x="Service", y="Cost", title="Average Service Costs")
    return fig

def get_daily_car_tip():
    tips = [
        "Check your tire pressure monthly for better fuel efficiency.",
        "Change your oil every 3,000-5,000 miles for optimal engine health.",
        "Rotate your tires every 6,000-8,000 miles for even wear.",
        "Keep your gas tank at least a quarter full to prevent fuel pump damage.",
        "Clean your headlights regularly for better visibility and safety."
    ]
    return random.choice(tips)

def main():
    st.set_page_config(page_title="Garagemate AI", page_icon=":car:", layout="wide")
    
    # Custom CSS for gray and black theme
    st.markdown("""
    <style>
    .big-font {
        font-size:36px !important;
        font-weight: bold;
        color: #FF4500;
        text-align: center;
    }
    .stApp {
        background-color: #2C2C2C;
        color: #E0E0E0 !important;
    }
    body {
        color: #E0E0E0;
    }
    p, .stMarkdown, .stText {
        color: #E0E0E0 !important;
    }
    .stButton>button {
        background-color: #FF4500;
        color: white;
    }
    .stSelectbox {
        background-color: #3C3C3C;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">Garagemate AI</p>', unsafe_allow_html=True)
    st.write("Your comprehensive car maintenance companion powered by advanced AI")

    # Daily car tip
    st.info(f"🚗 Daily Car Tip: {get_daily_car_tip()}")

    # Sidebar for different functionalities
    st.sidebar.title("Features")
    feature = st.sidebar.radio("Choose a feature:", ["Chat", "Service Charts", "Maintenance Guide", "Cost Estimator", "Part Finder", "Service Scheduler"])

    if feature == "Chat":
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("What car-related question do you have?"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            full_prompt = f"""You are an advanced garage AI assistant. Provide detailed information, advice, or insights on the following car-related query:

            {prompt}

            Consider various aspects such as car maintenance, repairs, costs, and best practices. Include relevant statistics or data if applicable.

            Remember to include a disclaimer that this information is for educational purposes only and not a substitute for professional mechanic advice or service."""

            response = get_gemini_response(full_prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

    elif feature == "Service Charts":
        st.subheader("Garage Service Visualization")
        chart_type = st.selectbox("Select chart type:", ["Popular Services", "Average Service Costs"])
        
        use_custom_data = st.checkbox("Use custom data")
        
        if use_custom_data:
            if chart_type == "Popular Services":
                st.write("Enter percentages for each service:")
                oil_change = st.number_input("Oil Change (%)", 0, 100, 30)
                tire_rotation = st.number_input("Tire Rotation (%)", 0, 100, 25)
                brake_service = st.number_input("Brake Service (%)", 0, 100, 20)
                engine_tuneup = st.number_input("Engine Tune-up (%)", 0, 100, 15)
                ac_service = st.number_input("A/C Service (%)", 0, 100, 10)
                
                user_data = {
                    "Service": ["Oil Change", "Tire Rotation", "Brake Service", "Engine Tune-up", "A/C Service"],
                    "Percentage": [oil_change, tire_rotation, brake_service, engine_tuneup, ac_service]
                }
            
            elif chart_type == "Average Service Costs":
                st.write("Enter average cost for each service:")
                services = ["Oil Change", "Tire Rotation", "Brake Service", "Engine Tune-up", "A/C Service"]
                user_data = {
                    "Service": services,
                    "Cost": []
                }
                for service in services:
                    cost = st.number_input(f"{service} ($)", 0, 1000, 100)
                    user_data["Cost"].append(cost)
            
            fig = generate_service_chart(chart_type, user_data)
        else:
            fig = generate_service_chart(chart_type)
        
        st.plotly_chart(fig)

    elif feature == "Maintenance Guide":
        st.subheader("Car Maintenance Guide")
        car_type = st.selectbox("Choose your car type:", ["Sedan", "SUV", "Truck", "Electric Vehicle"])
        mileage = st.number_input("Enter your car's mileage:", min_value=0, max_value=500000, value=50000)
        if st.button("Generate Maintenance Guide"):
            guide_prompt = f"Provide a maintenance guide for a {car_type} with {mileage} miles. Include recommended services, their frequency, and importance."
            response = get_gemini_response(guide_prompt)
            st.write(response)

    elif feature == "Cost Estimator":
        st.subheader("Service Cost Estimator")
        service = st.selectbox("Choose a service:", ["Oil Change", "Tire Rotation", "Brake Service", "Engine Tune-up", "A/C Service"])
        car_make = st.text_input("Enter your car make (e.g., Toyota, Ford):")
        car_model = st.text_input("Enter your car model:")
        car_year = st.number_input("Enter your car year:", min_value=1900, max_value=2024, value=2020)
        if st.button("Estimate Cost"):
            cost_prompt = f"Estimate the cost range for {service} for a {car_year} {car_make} {car_model}. Provide a low and high estimate and factors that might affect the cost."
            response = get_gemini_response(cost_prompt)
            st.write(response)

    elif feature == "Part Finder":
        st.subheader("Car Part Finder")
        part_name = st.text_input("Enter the name of the part you're looking for:")
        car_make = st.text_input("Enter your car make:")
        car_model = st.text_input("Enter your car model:")
        car_year = st.number_input("Enter your car year:", min_value=1900, max_value=2024, value=2020)
        if st.button("Find Part"):
            part_prompt = f"Provide information about {part_name} for a {car_year} {car_make} {car_model}. Include possible part numbers, estimated price range, and where to find it."
            response = get_gemini_response(part_prompt)
            st.write(response)

    elif feature == "Service Scheduler":
        st.subheader("Service Scheduler Assistant")
        service_type = st.selectbox("Choose a service type:", ["Oil Change", "Tire Rotation", "Brake Service", "Engine Tune-up", "A/C Service"])
        last_service_date = st.date_input("When was your last service?")
        mileage = st.number_input("Current mileage:", min_value=0, step=1000)
        if st.button("Get Next Service Recommendation"):
            schedule_prompt = f"Based on a {service_type} performed on {last_service_date} for a vehicle with {mileage} miles, when should the next service be scheduled? Provide a recommendation and explain the factors considered."
            response = get_gemini_response(schedule_prompt)
            st.write(response)

    # Footer
    st.markdown("---")
    st.markdown("*Disclaimer:* Garagemate AI is for informational purposes only. Always consult with a qualified mechanic for professional advice.")
    
    # Feedback
    st.sidebar.markdown("---")
    if st.sidebar.button("Give Feedback"):
        st.sidebar.text_area("We'd love to hear your thoughts!", key="feedback")
        if st.sidebar.button("Submit Feedback"):
            st.sidebar.success("Thank you for your feedback!")

if __name__== "__main__":
    main()