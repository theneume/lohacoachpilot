import requests
import json
import os
from datetime import datetime
import random
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from natal_calculator import calculate_natal_type_from_dob

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # Enable CORS for all routes

# Load configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Load data files
with open('deepsyke_core_rag.json', 'r') as f:
    DEEPSYKE_CORE = json.load(f)

with open('dating_coach_rag.json', 'r') as f:
    DATING_COACH = json.load(f)

with open('gravitor_code_rag.json', 'r') as f:
    GRAVITOR_CODE = json.load(f)

# Load system prompt
with open('ai_system_prompt.txt', 'r') as f:
    SYSTEM_PROMPT_TEMPLATE = f.read()

# Store conversations in memory
conversations = {}

# Cultural avatars for dating coach (celebrities, socialites, fun people)
DATING_CAS = {
    'female': [
        'Taylor Swift', 'Beyoncé', 'Rihanna', 'Zendaya', 'Margot Robbie',
        'Emma Stone', 'Jennifer Lawrence', 'Priyanka Chopra', 'Gal Gadot',
        'Lupita Nyong\'o', 'Scarlett Johansson', 'Angelina Jolie', 'Megan Fox',
        'Kim Kardashian', 'Kylie Jenner', 'Kendall Jenner', 'Hailey Bieber',
        'Gigi Hadid', 'Bella Hadid', 'Dua Lipa', 'Ariana Grande', 'Billie Eilish',
        'Olivia Rodrigo', 'Selena Gomez', 'Miley Cyrus', 'Demi Lovato'
    ],
    'male': [
        'Ryan Reynolds', 'Leonardo DiCaprio', 'Brad Pitt', 'George Clooney',
        'Tom Hardy', 'Henry Cavill', 'Idris Elba', 'Chris Evans', 'Chris Hemsworth',
        'Chris Pratt', 'Robert Downey Jr.', 'Tom Cruise', 'Johnny Depp',
        'Justin Bieber', 'Shawn Mendes', 'Harry Styles', 'Zac Efron', 'Timothée Chalamet',
        'Michael B. Jordan', 'John Legend', 'Drake', 'Post Malone', 'Travis Scott',
        'Lewis Hamilton', 'David Beckham', 'Cristiano Ronaldo', 'Neymar'
    ]
}

# Cultural avatars rotation tracker
ca_rotation_tracker = {}

def get_archetype(natal_type, gender):
    """Map natal type and gender to archetype"""
    try:
        archetype_mapping = DATING_COACH['archetype_mappings'][natal_type][gender]
        archetype = archetype_mapping['primary']
        description = archetype_mapping['description']
        nicknames = DATING_COACH['archetype_nicknames'][archetype]
        return archetype, description, nicknames
    except KeyError:
        return 'Mystic', 'Soft, spiritual, and deeply feminine', ['the Dreamy One']

def get_archetype_advice(archetype, topic):
    """Get archetype-specific dating advice"""
    try:
        # Try new structure first
        if 'archetype_communication_styles' in DATING_COACH:
            if topic == 'communication':
                return DATING_COACH['archetype_communication_styles'][archetype]['approach']
            elif topic == 'dating_advice_focus':
                return DATING_COACH['archetype_communication_styles'][archetype]['dating_advice_focus']
        
        # Fall back to old structure
        advice = DATING_COACH['dating_topics'][topic]['archetype_specific_advice'][archetype]
        return advice
    except KeyError:
        return "Your unique energy is your superpower - embrace it fully."

def create_contextual_greeting(profile):
    """Create a contextual greeting based on user's archetype and input"""
    name = profile['name']
    gender = profile['gender']
    archetype, description, nicknames = get_archetype(profile['natal_type'], gender)
    nickname = nicknames[0] if nicknames else name
    
    goals = profile.get('goals', '').lower()
    challenges = profile.get('challenges', '').lower()
    
    # Contextual greeting templates based on archetype - positive, welcoming format
    greetings = {
        'Mystic': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Mystic. This means you're someone who values depth, intuition, and soulful connection in relationships. Your ability to see beneath the surface and connect on a profound level is your greatest strength in dating. Let's explore how to use this gift to attract the kind of meaningful connection you're looking for.",
            f"Welcome, {name}! Based on your profile, you're a Mystic—someone who brings emotional depth and spiritual awareness to relationships. This archetype is drawn to authentic, transformative connections rather than surface-level interactions. Your intuitive nature helps you understand people on a level most can't reach. Let's talk about how to channel this into creating the relationships you truly desire."
        ],
        'Maiden': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Maiden. This means you're authentic, warm-hearted, and naturally nurturing in relationships. Your genuine nature and emotional openness are incredibly attractive qualities that draw people to you. Let's explore how to protect this beautiful energy while attracting the right connections.",
            f"Welcome, {name}! Based on your profile, you're a Maiden—someone who brings warmth, authenticity, and natural charm to dating. This archetype is known for being emotionally honest and creating safe spaces for genuine connection. Your ability to be yourself without pretense is magnetic. Let's discuss how to use this strength to attract quality partners."
        ],
        'Queen': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Queen. This means you're sophisticated, discerning, and carry yourself with natural elegance. Your high standards and self-respect are attractive qualities that draw people who appreciate excellence. Let's explore how to maintain your standards while creating space for genuine connection.",
            f"Welcome, {name}! Based on your profile, you're a Queen—someone who brings grace, refinement, and clear boundaries to relationships. This archetype knows her worth and won't settle for less than she deserves. Your ability to command respect while remaining open to love is powerful. Let's talk about attracting partners who match your caliber."
        ],
        'Huntress': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Huntress. This means you're confident, independent, and know exactly what you want. Your directness and ambition are incredibly attractive qualities that create exciting relationship dynamics. Let's explore how to channel this powerful energy into creating the connections you desire.",
            f"Welcome, {name}! Based on your profile, you're a Huntress—someone who brings strength, clarity, and purpose to dating. This archetype goes after what she wants with confidence and doesn't play games. Your ability to be direct while maintaining your feminine power is magnetic. Let's discuss how to use this to attract quality partners."
        ],
        'Magician': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Magician. This means you're perceptive, transformative, and understand the deeper dynamics of attraction. Your ability to read people and situations gives you a unique advantage in dating. Let's explore how to use this insight to create the profound connections you're seeking.",
            f"Welcome, {name}! Based on your profile, you're a Magician—someone who brings wisdom, intuition, and transformative energy to relationships. This archetype sees patterns others miss and understands the psychology of attraction. Your depth of understanding is a powerful tool. Let's talk about channeling this into meaningful connections."
        ],
        'Knight': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Knight. This means you're romantic, protective, and value honor in relationships. Your desire to be a provider and protector is an attractive quality when expressed with respect and emotional awareness. Let's explore how to channel this chivalrous energy into creating healthy, passionate connections.",
            f"Welcome, {name}! Based on your profile, you're a Knight—someone who brings romance, loyalty, and a protective nature to dating. This archetype values commitment and wants to be the hero in his partner's story. Your romantic idealism, when balanced with emotional maturity, is incredibly appealing. Let's discuss how to pursue love in a way that honors both you and your future partner."
        ],
        'Warrior': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the Warrior. This means you're confident, accomplished, and approach dating with the same excellence you bring to other areas of life. Your drive and ambition are attractive qualities that draw quality partners. Let's explore how to balance your competitive edge with emotional depth to create powerful connections.",
            f"Welcome, {name}! Based on your profile, you're a Warrior—someone who brings strength, achievement, and determination to relationships. This archetype thrives on challenge and values excellence in all things, including love. Your confidence and success are magnetic. Let's talk about channeling this energy into creating the passionate, equal partnership you deserve."
        ],
        'King': [
            f"Hi {name}, welcome to Loha! I've determined from your profile that you embody the archetype of the King. This means you're a natural leader with vision, authority, and the ability to command respect. Your decisiveness and confidence are powerful attractive qualities. Let's explore how to lead in relationships while creating space for genuine emotional intimacy and partnership.",
            f"Welcome, {name}! Based on your profile, you're a King—someone who brings leadership, wisdom, and authority to dating. This archetype knows what he wants and has the confidence to pursue it. Your ability to take charge while remaining emotionally present is rare and valuable. Let's discuss how to build the kingdom of love you envision."
        ]
    }
    
    # Select a greeting based on archetype
    archetype_greetings = greetings.get(archetype, greetings['Mystic'])
    greeting = random.choice(archetype_greetings)
    
    # Add contextual element based on goals/challenges if provided
    if goals:
        if 'relationship' in goals or 'partner' in goals or 'love' in goals:
            greeting += f"\n\nI see you mentioned wanting {goals.strip()}. Perfect—let's work together on strategies to make that happen."
    
    return greeting

def build_dating_system_prompt(profile, conversation_history):
    """Build the complete dating coach system prompt with varied content rotation"""
    natal_type = profile['natal_type']
    gender = profile['gender']
    archetype, description, nicknames = get_archetype(natal_type, gender)
    
    # Get Deepsyke type details (for AI's knowledge, not for user-facing content)
    type_data = DEEPSYKE_CORE['affinity_zones'].get(natal_type, {})
    
    # Build user info section
    user_info = f"\n# USER INFORMATION\n"
    user_info += f"Name: {profile['name']}\n"
    user_info += f"Archetype: {archetype}\n"
    user_info += f"Archetype Description: {description}\n"
    user_info += f"Nickname Options: {', '.join(nicknames[:3])}\n"
    user_info += f"Gender: {gender}\n"
    
    if profile.get('goals'):
        user_info += f"\nDating Goals: {profile['goals']}\n"
    if profile.get('challenges'):
        user_info += f"Challenges: {profile['challenges']}\n"
    if profile.get('improvements'):
        user_info += f"Areas for Improvement: {profile['improvements']}\n"
    
    # Add relationships if provided
    relationships = profile.get('relationships', [])
    if relationships:
        user_info += f"\n# IMPORTANT RELATIONSHIPS\n"
        for rel in relationships:
            rel_type = rel.get('natal_type', 'Unknown')
            rel_archetype, _, rel_nicknames = get_archetype(rel_type, rel.get('gender', 'male'))
            user_info += f"- {rel['name']} ({rel.get('gender', '')}): {rel.get('type', 'unknown')} - {rel_archetype} archetype\n"
    
    # Add archetype-specific guidance
    user_info += f"\n# YOUR ARCHETYPE: {archetype.upper()}\n"
    user_info += f"{description}\n"
    
    # ROTATE CONTENT BASED ON CONVERSATION LENGTH TO PREVENT REPETITION
    message_count = len(conversation_history)
    
    # Different content sections for different conversation stages
    if message_count <= 3:
        # Early conversation: Focus on archetype and communication
        if 'archetype_communication_styles' in DATING_COACH:
            comm_style = DATING_COACH['archetype_communication_styles'].get(archetype, {})
            if comm_style:
                user_info += f"\n# COMMUNICATION STYLE\n"
                user_info += f"Approach: {comm_style.get('approach', '')}\n"
                user_info += f"Language: {comm_style.get('language', '')}\n"
                user_info += f"Dating Advice Focus: {comm_style.get('dating_advice_focus', '')}\n"
                user_info += f"Texting Style: {comm_style.get('texting_style', '')}\n"
        
        # Add tone protocol
        if 'tone_protocol' in DATING_COACH:
            tone = DATING_COACH['tone_protocol']
            if 'communication_rules' in tone:
                user_info += f"\n# COMMUNICATION GUIDELINES\n"
                user_info += f"Format: {tone['communication_rules'].get('format', '')}\n"
                user_info += f"Pacing: {tone['communication_rules'].get('pacing', '')}\n"
                user_info += f"Emotion: {tone['communication_rules'].get('emotion', '')}\n"
                user_info += f"Humor: {tone['communication_rules'].get('humor', '')}\n"
    
    elif message_count <= 6:
        # Mid conversation: Focus on chemistry and attraction
        if 'chemistry_building' in DATING_COACH:
            chem = DATING_COACH['chemistry_building']
            user_info += f"\n# CHEMISTRY BUILDING PRINCIPLES\n"
            for principle in chem.get('principles', [])[:4]:
                user_info += f"- {principle}\n"
        
        if 'attraction_principles' in DATING_COACH:
            attr = DATING_COACH['attraction_principles']
            user_info += f"\n# ATTRACTION PRINCIPLES\n"
            for principle in attr.get('principles', [])[:3]:
                user_info += f"- {principle}\n"
    
    elif message_count <= 9:
        # Later conversation: Focus on texting and communication strategies
        if 'texting_strategies' in DATING_COACH:
            texting = DATING_COACH['texting_strategies']
            user_info += f"\n# TEXTING STRATEGIES\n"
            for principle in texting.get('general_principles', [])[:4]:
                user_info += f"- {principle}\n"
            archetype_texting = texting.get('archetype_specific', {}).get(archetype, '')
            if archetype_texting:
                user_info += f"\nFor Your Archetype: {archetype_texting}\n"
        
        if 'conversation_starters' in DATING_COACH:
            starters = DATING_COACH['conversation_starters']
            user_info += f"\n# CONVERSATION STARTERS\n"
            for starter in starters.get('archetype_specific', {}).get(archetype, [])[:3]:
                user_info += f"- {starter}\n"
    
    else:
        # Deep conversation: Rotate through advanced topics including Gravitor Code
        topic_rotation = message_count % 6
        
        if topic_rotation == 0:
            # Gravitor Code insights
            if 'gravitor_types' in GRAVITOR_CODE:
                gravitor_types = GRAVITOR_CODE['gravitor_types']
                # Map archetype to Gravitor type
                gravitor_type = None
                if archetype in ['Mystic', 'Magician']:
                    gravitor_type = gravitor_types.get('SS', {})
                elif archetype in ['Maiden', 'Knight']:
                    gravitor_type = gravitor_types.get('SD', {})
                elif archetype in ['Queen', 'Warrior']:
                    gravitor_type = gravitor_types.get('DS', {})
                elif archetype in ['Huntress', 'King']:
                    gravitor_type = gravitor_types.get('DD', {})
                
                if gravitor_type:
                    user_info += f"\n# GRAVITOR CODE INSIGHTS\n"
                    user_info += f"Type: {gravitor_type.get('name', '')}\n"
                    user_info += f"Neurochemical Profile: {gravitor_type.get('neurochemical_profile', '')}\n"
                    
                    themes = gravitor_type.get('gravitor_themes', [])
                    if themes:
                        user_info += f"\nCore Themes:\n"
                        for theme in themes[:5]:
                            user_info += f"- {theme}\n"
                    
                    topics = gravitor_type.get('conversation_topics', [])
                    if topics:
                        user_info += f"\nConversation Topics:\n"
                        for topic in topics[:5]:
                            user_info += f"- {topic}\n"
        
        elif topic_rotation == 1:
            # Gravitor Code power statements
            if 'gravitor_types' in GRAVITOR_CODE:
                gravitor_types = GRAVITOR_CODE['gravitor_types']
                # Map archetype to Gravitor type
                gravitor_type = None
                if archetype in ['Mystic', 'Magician']:
                    gravitor_type = gravitor_types.get('SS', {})
                elif archetype in ['Maiden', 'Knight']:
                    gravitor_type = gravitor_types.get('SD', {})
                elif archetype in ['Queen', 'Warrior']:
                    gravitor_type = gravitor_types.get('DS', {})
                elif archetype in ['Huntress', 'King']:
                    gravitor_type = gravitor_types.get('DD', {})
                
                if gravitor_type:
                    power_statements = gravitor_type.get('power_statements', [])
                    if power_statements:
                        user_info += f"\n# POWER STATEMENTS & CONVERSATION FLOWS\n"
                        for ps in power_statements[:3]:
                            user_info += f"\nStatement: {ps.get('statement', '')}\n"
                            user_info += f"Why It Works: {ps.get('why_it_works', '')}\n"
                            user_info += f"Use these as inspiration for powerful, connecting statements.\n"
        
        elif topic_rotation == 2:
            # NLP and seduction patterns
            if 'nlp_techniques' in DATING_COACH:
                nlp = DATING_COACH['nlp_techniques']
                user_info += f"\n# ADVANCED COMMUNICATION TECHNIQUES\n"
                for technique in nlp.get('techniques', [])[:3]:
                    user_info += f"- {technique}\n"
            
            if 'seductive_language_patterns' in DATING_COACH:
                patterns = DATING_COACH['seductive_language_patterns']
                user_info += f"\n# SEDUCTIVE LANGUAGE PATTERNS\n"
                for pattern in patterns.get('archetype_specific', {}).get(archetype, [])[:2]:
                    user_info += f"- {pattern}\n"
        
        elif topic_rotation == 3:
            # Advanced seduction
            if 'advanced_seduction_techniques' in DATING_COACH:
                adv = DATING_COACH['advanced_seduction_techniques']
                user_info += f"\n# ADVANCED SEDUCTION TECHNIQUES\n"
                for technique in adv.get('techniques', [])[:3]:
                    user_info += f"- {technique}\n"
        
        elif topic_rotation == 4:
            # Gender-specific dating advice
            if 'dating_advice_by_gender' in DATING_COACH:
                gender_advice = DATING_COACH['dating_advice_by_gender']
                user_info += f"\n# DATING ADVICE FOR {gender.upper()}\n"
                advice_list = gender_advice.get(gender, [])
                for advice in advice_list[:4]:
                    user_info += f"- {advice}\n"
        
        else:
            # Cultural avatars and cultural context
            if 'cultural_avatar_guidelines' in DATING_COACH:
                cultural = DATING_COACH['cultural_avatar_guidelines']
                user_info += f"\n# CULTURAL REFERENCES\n"
                for guideline in cultural.get('guidelines', [])[:3]:
                    user_info += f"- {guideline}\n"
    
    # Build conversation history
    # Use all available history (already truncated in chat function)
    history_text = "\n# CONVERSATION HISTORY\n"
    for msg in conversation_history:
        role = "YOU" if msg['role'] == 'user' else "LOHA"
        history_text += f"{role}: {msg['content']}\n\n"
    
    # Replace placeholders in system prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace('{user_name}', profile['name'])
    system_prompt = system_prompt.replace('{archetype}', archetype)
    system_prompt = system_prompt.replace('{nickname}', nicknames[0])
    
    # Combine all parts
    full_prompt = system_prompt + "\n\n" + user_info + "\n\n" + history_text + "\n\n# USER'S MESSAGE:\n{user_message}"
    
    # Add variety reminder at the end
    full_prompt += "\n\n# IMPORTANT: BRING FRESH CONTENT\n"
    full_prompt += "This is message " + str(message_count) + " in the conversation. "
    full_prompt += "Do NOT repeat information you've already shared about their birth date, natal type, or archetype characteristics. "
    full_prompt += "Move the conversation forward with NEW insights, different topics, and fresh perspectives. "
    full_prompt += "Vary your responses between communication style, texting, attraction, chemistry building, seduction techniques, and relationship advice. "
    full_prompt += "Keep it interesting - no repetitive loops!"
    
    return full_prompt

def load_cultural_avatars(gender, session_id=None):
    """Load rotating selection of cultural avatars for dating coach"""
    try:
        all_names = DATING_CAS.get(gender, DATING_CAS['female'])
        
        if not all_names:
            return "", []
        
        # Initialize rotation tracker if not exists
        if gender not in ca_rotation_tracker:
            ca_rotation_tracker[gender] = 0
        
        # Get recently used avatars from session
        recently_used = []
        if session_id and session_id in conversations:
            recently_used = conversations[session_id].get('last_cas_mentioned', [])
        
        # Get rotation position
        rotation_pos = ca_rotation_tracker[gender]
        selected_cas = []
        
        # Select 2-3 avatars, skipping any used in this session
        max_candidates = random.randint(2, 3)
        
        for i in range(len(all_names)):
            pos = (rotation_pos + i) % len(all_names)
            ca = all_names[pos]
            
            if ca in recently_used:
                continue
            
            selected_cas.append(ca)
            
            if len(selected_cas) >= max_candidates:
                ca_rotation_tracker[gender] = (pos + 1) % len(all_names)
                break
        
        # Format for AI
        if selected_cas:
            ca_text = f"\n{'='*60}\n"
            ca_text += f"CULTURAL REFERENCES FOR THIS SESSION\n"
            ca_text += f"{'='*60}\n\n"
            ca_text += f"Selected: {', '.join(selected_cas)}\n\n"
            ca_text += f"Use these celebrities as examples when relevant to the conversation.\n"
            ca_text += f"Reference their dating history, quotes, or public persona when it helps illustrate a point.\n"
            ca_text += f"{'='*60}\n"
            return ca_text, selected_cas
        
        return "", []
    except Exception as e:
        print(f"Error loading cultural avatars: {e}")
        return "", []

def call_gemini_api(system_prompt, user_message, max_retries=2):
    """Call Gemini API with the complete system prompt and retry logic"""
    
    # User-friendly error messages
    error_messages = [
        "Hmm, having a momentary glitch. Let me try that again...",
        "Technical hiccup - give me one second to recover...",
        "Almost there, just a small delay on my end..."
    ]
    
    for attempt in range(max_retries + 1):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
            
            full_prompt = system_prompt.replace('{user_message}', user_message)
            
            # Truncate prompt if too long to avoid API errors
            if len(full_prompt) > 100000:
                # Keep the most recent parts of conversation
                parts = full_prompt.split('\n\n')
                full_prompt = '\n\n'.join(parts[-20:])  # Keep last 20 sections
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(url, json=data, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            
            # If we get here, we got a non-200 response
            if attempt < max_retries:
                print(f"API error, retry attempt {attempt + 1}/{max_retries}")
                import time
                time.sleep(1)  # Wait before retry
            else:
                print(f"API returned status {response.status_code}")
                return "I'm having some technical difficulties right now. Your message was saved though - just try sending it again in a moment."
                
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                print(f"Timeout, retry attempt {attempt + 1}/{max_retries}")
                import time
                time.sleep(2)  # Wait longer for timeout
            else:
                print("API timeout after retries")
                return "Taking a bit longer than usual to respond. Your message is safe - just give it another try."
                
        except Exception as e:
            print(f"Error calling Gemini API (attempt {attempt + 1}): {e}")
            if attempt < max_retries:
                import time
                time.sleep(1)
            else:
                # Give a more helpful error message
                return "I hit a snag processing that. Don't worry, our conversation is saved - just try rephrasing or sending it again."
    
    return "Something unexpected happened. Let's try once more - I'm right here with you."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Explicit routes for images
@app.route('/static/lologo8.png')
def serve_logo():
    return send_from_directory('static', 'lologo8.png')

@app.route('/static/lohafront1.png')
def serve_hero():
    return send_from_directory('static', 'lohafront1.png')

@app.route('/static/archtokens.png')
def serve_archetypes():
    return send_from_directory('static', 'archtokens.png')

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'LOHA Dating Coach'})

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize a new coaching session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        name = data.get('name', '')
        dob = data.get('dob', '')
        gender = data.get('gender', '')
        goals = data.get('goals', '')
        challenges = data.get('challenges', '')
        improvements = data.get('improvements', '')
        relationships = data.get('relationships', [])
        
        # Calculate natal type (silent, for AI's knowledge only)
        natal_type = calculate_natal_type_from_dob(dob, gender)
        
        # Build profile
        profile = {
            'name': name,
            'dob': dob,
            'gender': gender,
            'natal_type': natal_type,
            'goals': goals,
            'challenges': challenges,
            'improvements': improvements,
            'relationships': []
        }
        
        # Calculate natal types for relationships
        for rel in relationships:
            if rel.get('dob'):
                rel_natal_type = calculate_natal_type_from_dob(rel['dob'], rel.get('gender', 'male'))
                profile['relationships'].append({
                    'name': rel.get('name', ''),
                    'dob': rel.get('dob', ''),
                    'gender': rel.get('gender', ''),
                    'type': rel.get('type', ''),
                    'natal_type': rel_natal_type
                })
        
        # Get archetype
        archetype, _, nicknames = get_archetype(natal_type, gender)
        nickname = nicknames[0] if nicknames else "babe"
        
        # Create contextual greeting
        greeting = create_contextual_greeting(profile)
        
        # Store session
        conversations[session_id] = {
            'profile': profile,
            'history': [{'role': 'assistant', 'content': greeting}],
            'last_cas_mentioned': []
        }
        
        return jsonify({
            'success': True,
            'message': greeting
        })
    except Exception as e:
        print(f"Error initializing session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        user_message = data.get('message', '')
        
        if session_id not in conversations:
            return jsonify({
                'success': False, 
                'error': 'Session not found',
                'user_friendly': 'Our conversation got disconnected. Let me start fresh with you.'
            }), 400
        
        session = conversations[session_id]
        profile = session['profile']
        
        # Add user message to history
        session['history'].append({'role': 'user', 'content': user_message})
        
        # Build system prompt
        system_prompt = build_dating_system_prompt(profile, session['history'])
        
        # Call AI (now with retry logic)
        response = call_gemini_api(system_prompt, user_message)
        
        # Add response to history
        session['history'].append({'role': 'assistant', 'content': response})
        
        # TRUNCATE HISTORY: Keep only last 12 messages to prevent context overflow
        # This ensures we maintain conversation continuity without overwhelming the API
        if len(session['history']) > 12:
            # Keep the first greeting message and the most recent 11 messages
            # This preserves the initial context while limiting token usage
            session['history'] = [session['history'][0]] + session['history'][-11:]
        
        return jsonify({
            'success': True,
            'message': response
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        # Import traceback for better debugging
        import traceback
        traceback.print_exc()
        
        # Return a user-friendly error that explains what happened
        return jsonify({
            'success': False, 
            'error': str(e),
            'user_friendly': "I encountered an unexpected issue. Don't worry - I remember everything we've talked about. Just try sending your message again."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9024))
    print(f"Starting LOHA Dating Coach V2 on port {port}")
    print("Natural, helpful, and authentically human!")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        # Try alternative port
        for alt_port in [9021, 9022, 9023]:
            try:
                print(f"Trying alternative port {alt_port}")
                app.run(host='0.0.0.0', port=alt_port, debug=False)
                break
            except:
                continue