import os
import streamlit as st
from langchain import PromptTemplate, LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory

# =============================================================================
# 1) SETUP: Initialize OpenAI + LangChain
# =============================================================================
# Make sure you have your API key in an environment variable OR st.secrets
# e.g., export OPENAI_API_KEY="sk-XXXX"
api_key = "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"
if not api_key:
    st.warning("OpenAI API key not found. Add OPENAI_API_KEY as env variable or in Streamlit secrets.")
else:
    # The LLM we will use. By default, it might use GPT-3.5; set model_name="gpt-4" if you have access

    llm = ChatOpenAI(
        openai_api_key=api_key,
        model_name="gpt-4",
        temperature=0.7
    )



# =============================================================================
# 2) PLACEHOLDER CRM-INTEGRATION FUNCTIONS
#    In a real scenario, you'd replace these stubs with calls to HubSpot/Salesforce/Zoho, etc.
# =============================================================================
def get_crm_leads():
    """
    Placeholder: Fetch leads from your CRM.
    Return a list of dicts with lead info, e.g. [{"name": "...", "company": "...", ...}, ...]
    """
    # TODO: replace with actual CRM API calls
    return [
        {"id": 1, "name": "Alice Johnson", "company": "Acme Corp", "job_title": "CTO", "industry": "SaaS"},
        {"id": 2, "name": "Bob Smith", "company": "Beta Inc",  "job_title": "Head of Ops", "industry": "Logistics"},
    ]

def log_crm_activity(lead_id, activity_type, content):
    """
    Placeholder: Log an activity (e.g., 'Email Sent') to your CRM with relevant content.
    """
    # TODO: integrate CRM write-back
    st.write(f"CRM LOG: Lead {lead_id}, Activity: {activity_type}\nContent:\n{content}\n")


# =============================================================================
# 3) LANGCHAIN: TEMPLATES & CHAINS FOR DIFFERENT SALES TASKS
# =============================================================================
# --- A) Cold Email / LinkedIn Outreach
cold_email_template = PromptTemplate(
    input_variables=["prospect_name","company","job_title","industry","product_description"],
    template="""
You are a world-class B2B sales copywriter. 
Write a short, personalized outreach {medium} to {prospect_name}, who works at {company} as a {job_title} in the {industry} industry. 
Highlight how our offering can solve their pain points. 
Product/Service Description: {product_description}

Requirements:
1. Greet them by name.
2. Be concise (~100-150 words).
3. Use a friendly, professional tone.
4. End with a clear call to action.
""",
)

# --- B) Sales Call Assistance / Objection Handling
call_script_template = PromptTemplate(
    input_variables=["call_context","product_description"],
    template="""
You are an AI sales coach. The rep is on a call. Provide a script suggestion based on the context:

Call context: {call_context}
Product/Service: {product_description}

Give:
1) A structured call flow (Introduction, Discovery Questions, Value Proposition).
2) Possible objections and sample responses.
3) Closing statement.
Make it concise.
    """
)

# --- C) Newsletter / Survey Generation
newsletter_template = PromptTemplate(
    input_variables=["newsletter_topic","key_points"],
    template="""
You are an expert marketing copywriter. Draft a concise newsletter about "{newsletter_topic}" incorporating these key points:
{key_points}

Format:
1) Catchy headline (~5-8 words).
2) Brief body (2-3 short paragraphs).
3) Clear CTA at the end.

Tone: helpful and slightly promotional.
"""
)

# --- D) Webinar Follow-Up
webinar_followup_template = PromptTemplate(
    input_variables=["webinar_topic","recipient_type","key_highlights"],
    template="""
Write a follow-up email for someone who {recipient_type} our webinar on "{webinar_topic}".
Key highlights of the webinar: {key_highlights}
Guidelines:
- If they attended, thank them and offer next steps.
- If they missed it, provide a recap link.
- Keep it ~150 words, friendly, and professional.
- End with a clear CTA to continue the conversation.
"""
)

# --- E) Business Model Canvas (BMC) Analysis
bmc_template = PromptTemplate(
    input_variables=["known_info"],
    template="""
You are an AI analyst specializing in Business Model Canvas (BMC). 
Given the following known details about a business or prospect:

{known_info}

Fill in or analyze their model in terms of:
1) Customer Segments
2) Value Proposition
3) Channels
4) Customer Relationships
5) Revenue Streams
6) Key Resources
7) Key Activities
8) Key Partnerships
9) Cost Structure

Then suggest possible opportunities where our product/service could add value.
Output as a structured text summary.
"""
)

# Create LLMChains for each use-case
if api_key:
    cold_email_chain   = LLMChain(llm=llm, prompt=cold_email_template)
    call_script_chain  = LLMChain(llm=llm, prompt=call_script_template)
    newsletter_chain   = LLMChain(llm=llm, prompt=newsletter_template)
    webinar_chain      = LLMChain(llm=llm, prompt=webinar_followup_template)
    bmc_chain          = LLMChain(llm=llm, prompt=bmc_template)
else:
    cold_email_chain = call_script_chain = newsletter_chain = webinar_chain = bmc_chain = None


# =============================================================================
# 4) STREAMLIT UI
# =============================================================================
st.title("🚀 B2B Sales Automation AI Agent")

# For demonstration, let’s store a product description in session state or let user define it
if "product_desc" not in st.session_state:
    st.session_state["product_desc"] = "Our SaaS tool streamlines supply chain operations with AI-driven insights."

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to section:", (
    "1. Outreach Automation",
    "2. Sales Call Assistance",
    "3. Newsletter & Survey",
    "4. Webinar Follow-Up",
    "5. Business Model Canvas"
))


# -----------------------------------------------------------------------------
# PAGE 1: Outreach Automation
# -----------------------------------------------------------------------------
if page == "1. Outreach Automation":
    st.subheader("Cold Email / LinkedIn Outreach")
    st.write("Generate a personalized cold email or LinkedIn message for a lead.")
    
    leads = get_crm_leads()
    lead_names = [f"{lead['id']}: {lead['name']} @ {lead['company']}" for lead in leads]
    selected_lead = st.selectbox("Choose a lead from CRM", options=lead_names)
    medium = st.selectbox("Choose Medium:", ["email","LinkedIn message"])
    product_description = st.text_area("Product Description:", st.session_state["product_desc"], height=69)
    
    if st.button("Generate Outreach"):
        if not cold_email_chain:
            st.error("No OpenAI API key found. Please set it first.")
        else:
            lead_id = int(selected_lead.split(":")[0])
            lead_data = next((l for l in leads if l["id"] == lead_id), {})
            
            # Generate text using the chain
            outreach_text = cold_email_chain.run(
                prospect_name=lead_data["name"],
                company=lead_data["company"],
                job_title=lead_data["job_title"],
                industry=lead_data["industry"],
                product_description=product_description,
                medium=medium
            )
            
            st.success("Generated Outreach:")
            st.write(outreach_text)
            
            # Optional: Log in CRM
            if st.checkbox("Log this to CRM as 'Email Draft'?"):
                log_crm_activity(lead_id, f"{medium.capitalize()} Draft", outreach_text)


# -----------------------------------------------------------------------------
# PAGE 2: Sales Call Assistance
# -----------------------------------------------------------------------------
elif page == "2. Sales Call Assistance":
    st.subheader("Sales Call Script & Objection Handling")
    st.write("Enter current call context (brief notes) and let GPT-4 propose a structured script.")

    call_context = st.text_area("Call context / prospect notes:", height=120)
    product_description = st.text_area("Product Description:", st.session_state["product_desc"], height=69)

    if st.button("Generate Call Script"):
        if not call_script_chain:
            st.error("No OpenAI API key found.")
        else:
            call_script = call_script_chain.run(
                call_context=call_context,
                product_description=product_description
            )
            st.success("Suggested Call Script & Objections Handling:")
            st.write(call_script)


# -----------------------------------------------------------------------------
# PAGE 3: Newsletter & Survey
# -----------------------------------------------------------------------------
elif page == "3. Newsletter & Survey":
    st.subheader("Generate a Newsletter or Survey Content")
    st.write("Provide a topic and key points. GPT-4 will draft a concise newsletter.")

    newsletter_topic = st.text_input("Newsletter Topic:", "How AI is Revolutionizing Supply Chains")
    key_points = st.text_area("Key Points or Bullets:", "1) Efficiency gains\n2) Cost reduction\n3) Real-time analytics")

    if st.button("Generate Newsletter"):
        if not newsletter_chain:
            st.error("No OpenAI API key found.")
        else:
            newsletter_text = newsletter_chain.run(
                newsletter_topic=newsletter_topic, 
                key_points=key_points
            )
            st.success("Generated Newsletter:")
            st.write(newsletter_text)
            st.info("Copy/paste into your email marketing tool, or store in CRM as a marketing asset.")

    st.write("---")
    st.write("**Survey Generation** (simple example): You can adapt the same approach, e.g., prompt GPT-4 to create a short list of survey questions. Below is a minimal example.")

    if st.button("Generate Basic Survey Questions"):
        if not llm:
            st.error("No OpenAI API key found.")
        else:
            survey_prompt = f"Generate 5 short survey questions about {newsletter_topic} to gauge audience feedback."
            survey_questions = llm(survey_prompt)
            st.success("Survey Questions:")
            st.write(survey_questions)


# -----------------------------------------------------------------------------
# PAGE 4: Webinar Follow-Up
# -----------------------------------------------------------------------------
elif page == "4. Webinar Follow-Up":
    st.subheader("Automate Webinar Follow-Up Emails")
    st.write("GPT-4 can generate different follow-up messages depending on whether someone attended or missed your webinar.")

    webinar_topic = st.text_input("Webinar Topic:", "AI for B2B Sales Pipeline")
    recipient_type = st.selectbox("Recipient Type", ["attended", "missed"])
    key_highlights = st.text_area("Key Highlights:", "1) GPT-4 for cold outreach\n2) Live Q&A success\n3) Case study from ACME Corp")

    if st.button("Generate Follow-Up"):
        if not webinar_chain:
            st.error("No OpenAI API key found.")
        else:
            followup_text = webinar_chain.run(
                webinar_topic=webinar_topic,
                recipient_type=recipient_type,
                key_highlights=key_highlights
            )
            st.success("Generated Follow-Up Email:")
            st.write(followup_text)
            st.info("Copy/paste into your mailing platform or schedule via CRM.")


# -----------------------------------------------------------------------------
# PAGE 5: Business Model Canvas
# -----------------------------------------------------------------------------
elif page == "5. Business Model Canvas":
    st.subheader("Business Model Canvas (BMC) Analysis")
    st.write("Input known details about a prospect (or your own business), and GPT-4 will fill/analyze the BMC blocks + suggest opportunities.")

    known_info = st.text_area("Known Info About the Business:", 
        """Company: ACME Corp
Customer Segments: Mid-size manufacturing
Key Partnerships: ...
Value Proposition: ...
(Any partial BMC notes you have)
"""
    )

    if st.button("Analyze with BMC"):
        if not bmc_chain:
            st.error("No OpenAI API key found.")
        else:
            bmc_analysis = bmc_chain.run(known_info=known_info)
            st.success("BMC Analysis & Opportunity Recommendations:")
            st.write(bmc_analysis)
            st.info("Use this to discover how your solution fits into the prospect’s business model.")