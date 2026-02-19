import google.generativeai as genai
from config import Config

def _configure_gemini():
    try:
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY.strip())
            return True
        return False
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return False

def generate_chat_response(conversation_history, university_context=None, knowledge_context=None, department_context=None, model=None):
    """
    Generate a chat response using Google Gemini API
    
    Args:
        conversation_history: List of conversation messages
        university_context: Context about the user's university
        knowledge_context: Relevant knowledge from knowledge base
        department_context: Context about the user's department
        model: Model to use (optional)
    """

    # Check API key configuration
    if not Config.GEMINI_API_KEY:
        return "I apologize, but the AI service is currently not configured.", None

    # Configure Gemini
    if not _configure_gemini():
        return "I apologize, but I'm unable to connect to the AI service at the moment.", None

    model_name = model or Config.GEMINI_MODEL

    # Build system prompt with university, department, and knowledge context
    system_instruction = """You are an intelligent assistant for Algerian universities. 
You help students and staff with:
- Academic inquiries and course information
- Administrative procedures
- Campus facilities and services
- Department-specific guidance
- General university information

IMPORTANT INSTRUCTIONS:
1. Always respond in the SAME LANGUAGE the user uses (Arabic, English, or French)
2. Focus your answers on the specific university and department the user belongs to
3. Use the knowledge base information provided when available
4. When department information is available, provide department-specific guidance
5. Reference official department websites when appropriate
6. If you don't have specific information, provide general guidance and suggest contacting the university or department directly
7. Be helpful, professional, and concise
"""

    # Add university context if provided
    if university_context:
        system_instruction += f"\n\nCONTEXT ABOUT USER'S UNIVERSITY:\n{university_context}\n"
    
    # Add department context if provided
    if department_context:
        system_instruction += f"\n\nCONTEXT ABOUT USER'S DEPARTMENT:\n{department_context}\n"
    
    # Add knowledge context if provided
    if knowledge_context:
        system_instruction += f"\n\nRELEVANT INFORMATION FROM KNOWLEDGE BASE:\n{knowledge_context}\n"

    try:
        # ✅ Correct model initialization
        gemini_model = genai.GenerativeModel(model_name=model_name)

        # Convert conversation history
        gemini_history = []
        for msg in conversation_history[:-1]:
            role = 'model' if msg['role'] == 'assistant' else 'user'
            gemini_history.append({
                'role': role,
                'parts': [msg['content']]
            })

        # Start chat
        chat = gemini_model.start_chat(history=gemini_history)

        # Get last user message
        last_message = conversation_history[-1]['content'] if conversation_history else ""

        # ✅ Merge system prompt with user message
        full_prompt = system_instruction + "\n\nUser: " + last_message

        # Generate response
        response = chat.send_message(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )

        # ✅ Safe response extraction
        ai_message = getattr(response, "text", "I'm here to help you.")

        return ai_message, model_name

    except Exception as e:
        error_str = str(e)

        print("=" * 60)
        print("GEMINI API ERROR:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {error_str}")
        print(f"Model: {model_name}")
        print("=" * 60)

        return "I apologize, but I encountered an error while processing your request.", None


def count_tokens(text, model=None):
    """
    Count the number of tokens in a text string
    
    Note: Gemini API doesn't expose token counting in the same way as OpenAI.
    This is a rough estimate for tracking purposes.
    
    Args:
        text: The text to count tokens for
        model: The model to use (not used for Gemini, kept for compatibility)
    
    Returns:
        int: Estimated number of tokens
    """
    try:
        # For Gemini, we can use the count_tokens method if available
        # For now, use a simple estimation
        # Gemini roughly uses 1 token per 4 characters for English text
        return len(text) // 4
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4

def get_available_models():
    """Get list of available Gemini models"""
    try:
        available_models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        return available_models if available_models else ['models/gemini-pro', 'models/gemini-1.5-flash']
    except Exception:
        # Return default models if API call fails
        return ['models/gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']

def generate_chat_title(first_message, max_length=50):
    """
    Generate a concise, descriptive title for a chat based on the first message
    
    Args:
        first_message: The user's first message
        max_length: Maximum title length
    
    Returns:
        str: Generated title
    """
    # Fallback to simple title if no API key
    if not Config.GEMINI_API_KEY or not Config.GEMINI_API_KEY.startswith('AIza'):
        words = first_message.split()[:6]
        title = ' '.join(words)
        return title[:max_length] + ('...' if len(title) > max_length else '')
    
    try:
        # Configure Gemini
        _configure_gemini()
        
        # Use Gemini to generate a title
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Generate a very short, concise title (3-6 words max) that summarizes the topic of this question. 
Just output the title, nothing else.

Examples: 
- "Course Registration Help"
- "Library Hours Inquiry"
- "Tuition Payment Question"

Question: {first_message}

Title:"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=20,
            )
        )
        
        title = response.text.strip()
        # Remove quotes if present
        title = title.strip('"\'')
        
        # Ensure it's not too long
        if len(title) > max_length:
            title = title[:max_length] + '...'
        
        return title
        
    except Exception as e:
        print(f"Error generating title with Gemini: {e}")
        # Fallback: extract key words from the message
        words = first_message.split()[:6]
        title = ' '.join(words)
        if len(title) > max_length:
            title = title[:max_length] + '...'
        return title


