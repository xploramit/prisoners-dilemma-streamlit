# Prisoner's Dilemma Dynamic Classroom Game

This version is multi-user. All students can open the same Streamlit link on different laptops/phones.

## How it works
- Shared game state is stored in Supabase.
- Each student selects their own name.
- Only the student whose turn it is sees the voting buttons.
- After a vote, every device refreshes automatically.
- Pair members vote one after another.
- Choices remain hidden until all five matches in a round are complete.
- The teacher starts each new round.
- Scores and leaderboard are shared for everyone.

## Files
- app.py
- requirements.txt
- supabase_schema.sql

## Setup
1. Create a free Supabase project.
2. Open SQL Editor in Supabase.
3. Run the contents of `supabase_schema.sql`.
4. In Supabase, copy:
   - Project URL
   - anon/public key
5. Upload these files to a GitHub repository.
6. Go to Streamlit Community Cloud and deploy `app.py`.
7. In Streamlit app settings → Secrets, add:

SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"

8. Restart the Streamlit app.

## Important
The GitHub Pages HTML version cannot synchronize votes between devices because each browser keeps its own local state. This Streamlit + Supabase version uses one shared database, so all devices see the same turn and score.
