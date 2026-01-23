# Loha Dating Coach - FAQ Integration Deployment Guide

## What's New

This version integrates the Loha FAQ content into the dating coach app with the following features:

### 1. FAQ Knowledge Base
- Comprehensive FAQ information stored in `loha_faq_rag.json`
- Covers all aspects of Loha dating site and coaching service
- AI can answer questions naturally using this knowledge

### 2. Subtle Loha Site Promotion
- Every 9 messages, the AI naturally mentions the Loha dating site
- Non-pushy, focused on user success and preparation
- Encourages users to imagine applying coaching insights on Loha

### 3. Balanced Approach
- Coaching remains the PRIMARY function
- FAQ info runs in background, never overshadows coaching
- Natural integration that feels conversational, not promotional

## Files Modified

1. **loha_faq_rag.json** (NEW)
   - Complete FAQ knowledge base
   - Structured for easy AI retrieval
   - Includes usage guidelines

2. **app.py**
   - Loads FAQ RAG file
   - Implements message counter (triggers every 9 messages)
   - Passes FAQ context and Loha mention flag to system prompt

3. **ai_system_prompt.txt**
   - Added FAQ integration instructions
   - Added Loha site mention guidelines
   - Maintains balance between coaching and promotion

## Deployment Steps

### Option 1: Render Deployment (Recommended)

1. **Update Environment Variable**
   ```
   GEMINI_API_KEY=AIzaSyARNl9LtYXqW-JM7wNuw1LbdtH7KMzYn90
   ```

2. **Deploy to Render**
   - Upload the entire `loha-dating-coach-v2` folder
   - Or connect to your GitHub repository
   - Render will automatically detect the Flask app

3. **Verify Deployment**
   - Test the chat functionality
   - Send 9 messages to verify Loha mention appears
   - Ask FAQ questions to verify knowledge integration

### Option 2: Local Testing

1. **Extract the archive**
   ```bash
   tar -xzf loha-dating-coach-faq-integrated.tar.gz
   cd loha-dating-coach-v2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variable**
   ```bash
   export GEMINI_API_KEY=AIzaSyARNl9LtYXqW-JM7wNuw1LbdtH7KMzYn90
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Access at**: http://localhost:9024

## Testing the Integration

### Test FAQ Integration
Ask questions like:
- "What makes Loha different from other dating apps?"
- "How does the matching system work?"
- "Is Loha free to use?"
- "What are the eight archetypes?"

### Test Loha Site Mentions
- Send 8-9 messages in a conversation
- On the 9th message, you should see a natural mention of Loha
- Example: "The insights you're gaining here are exactly what makes Loha members so successful"

### Test Coaching Function
- Regular dating advice should remain primary
- FAQ info should enhance, not overshadow coaching
- Tone should remain conversational and helpful

## Key Features

### Message Counter Logic
- Tracks messages per session
- Triggers Loha mention every 9 messages
- Resets when session ends

### FAQ Categories
- Getting Started
- Archetypes & Compatibility
- Deepsyke AI
- Membership & Pricing
- Safety & Privacy
- Relationship Success
- Technical Support
- Community & Events

### Loha Site Integration
- **Frequency**: Every 9 messages
- **Tone**: Encouraging, non-pushy
- **Focus**: User success and preparation
- **Examples**:
  - "Understanding your archetype now means you'll know exactly what to look for on Loha"
  - "When you're ready, Loha gives you a place to apply everything you're learning here"
  - "The combination of this coaching and Loha's matching system is incredibly powerful"

## Important Notes

1. **API Key**: Remember to set the new Gemini API key in your environment variables
2. **Primary Function**: Coaching is always primary, FAQ is background
3. **Natural Flow**: Loha mentions should feel organic, not forced
4. **User Choice**: Users can use the coach standalone or with Loha site

## Troubleshooting

### FAQ Not Working
- Verify `loha_faq_rag.json` is in the same directory as `app.py`
- Check server logs for loading errors

### Loha Mentions Not Appearing
- Verify message counter is incrementing
- Check that 9 messages have been sent in the session
- Look for the mention in the AI response (may be subtle)

### Coaching Quality Issues
- Ensure FAQ context isn't overwhelming the prompt
- Verify system prompt balance is maintained
- Check that coaching RAG files are loading correctly

## Support

For issues or questions:
- Check server logs for errors
- Verify all files are present
- Ensure environment variables are set correctly
- Test with a fresh session

## Version Info

- **Version**: FAQ Integration v2.0 (Improved)
- **Date**: January 2026
- **Compatibility**: Works with existing Loha Dating Coach V2
- **New Files**: loha_faq_rag.json
- **Modified Files**: app.py, ai_system_prompt.txt

## v2.0 Improvements

- Enhanced error handling for API failures
- Improved session stability with history limits (30 messages max)
- Better error recovery and user-friendly messages
- More robust data access patterns
- Improved reliability for extended conversations