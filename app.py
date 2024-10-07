from flask import Flask, jsonify, request
from database import init_db, db
from typing import List, Dict
import math

app = Flask(__name__)
init_db(app)

def calculate_match_score(user_profile: Dict, job: Dict) -> float:
    """Calculate the match score between a user profile and a job posting."""
    
    score = 0.0
    weights = {
        'skills': 5.5,
        'experience': 0.80,
        'location': 0.75,
        'role': 0.95,
        'job_type': 0.5
    }
    
    # Skills match
    user_skills = set(s.lower() for s in user_profile['skills'])
    job_skills = set(s.lower() for s in job.required_skills.split(','))
    if job_skills:
        skills_match = len(user_skills.intersection(job_skills)) / len(job_skills)
        score += skills_match * weights['skills']
    
    # Experience level match
    experience_levels = {'junior': 1, 'intermediate': 2, 'senior': 3}
    user_exp = experience_levels.get(user_profile['experience_level'].lower(), 0)
    job_exp = experience_levels.get(job.experience_level.lower(), 0)
    exp_diff = (user_exp - job_exp)
    if exp_diff == 0:
        score *= weights['experience']
    elif exp_diff == 1:
        score *= weights['experience'] * 0.5
    
    # Location match
    user_locations = [loc.lower() for loc in user_profile['preferences']['locations']]
    job_location = job.location.lower()
    if job_location in user_locations or (job_location == 'remote' and 'remote' in user_locations):
        score *= weights['location']
    
    # Desired role match
    if job.job_title.lower() in [role.lower() for role in user_profile['preferences']['desired_roles']]:
        score += weights['role']
    
    # Job type match
    if job.job_type.lower() == user_profile['preferences']['job_type'].lower():
        score *= weights['job_type']
    
    return score

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    experience_level = db.Column(db.String(50))
    preferences = db.Column(db.JSON)

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    job_id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    required_skills = db.Column(db.String(200))
    experience_level = db.Column(db.String(50))

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        if not all(k in data for k in ['name', 'skills', 'experience_level', 'preferences']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        new_user = UserProfile(**data)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_jobs():
    try:
        data = request.json
        if not all(k in data for k in ['job_title', 'company', 'required_skills', 'location', 'job_type', 'experience_level']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        new_job = JobPosting(**data)
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'id': new_job.job_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    try:
        user_profile = request.json
        if not all(k in user_profile for k in ['skills', 'experience_level', 'preferences']):
            return jsonify({'error': 'Invalid user profile format'}), 400
        
        # Get all jobs from database
        jobs = JobPosting.query.all()
        job_recommendations = []
        
        for job in jobs:
            match_score = calculate_match_score(user_profile, job)
            
            if match_score >= 0.45:  # Minimum match threshold
                recommendation = {
                    'job_title': job.job_title,
                    'company': job.company,
                    'location': job.location,
                    'job_type': job.job_type,
                    'required_skills': job.required_skills.split(','),
                    'experience_level': job.experience_level,
                    'match_score': round(match_score * 10, 2)
                }
                job_recommendations.append(recommendation)
        
        # Sort by match score
        job_recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify(job_recommendations[:3]), 200  # Return top 3 matches
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/")
def home():
    return "working"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)