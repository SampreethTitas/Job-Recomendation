# Job-Recommendation
Backend API Using Flask and PostgreSQL

Create DataBase to Store job details with necessary details

provide the DataBase details into the DATABASE_URL

Enter the new job deatils in the /api/jobs endpoint

To get the Job Recomendation :
Run the Flask 
enter the /api/recommendations endpoint using POST method providing the user profile as described object




# Recommendation Logic

Each criteria is assigned with a weighted score that is used to deteremine the match between the user profile and available jobs in the database.

weights = {
        'skills': 5.5,
        'experience': 0.80,
        'location': 0.75,
        'role': 0.95,
        'job_type': 0.5
    }
score += skills_match * weights['skills']
score *= weights['experience']
score *= weights['location']
score += weights['role']
score *= weights['job_type']


Later  0.45  Minimum match threshold is set to identify the best job that suite the user profile
