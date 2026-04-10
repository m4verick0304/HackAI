import random
from faker import Faker

def generate_students(num_students=200):
    """
    Generates synthetic student data.
    Includes normal distributions and specific edge cases to test AI agents.
    """
    fake = Faker()
    students = []
    domains = ['web', 'ml', 'core', 'app', 'devops', 'cloud', 'data science', 'cybersecurity']

    for i in range(1, num_students + 1):
        name = fake.name()
        domain = random.choice(domains)
        
        # Determine case type to inject realistic edge cases
        case_type = random.random()
        
        # Edge Case 1: High CGPA, but completely inactive (about 5% of students)
        if case_type < 0.05:
            cgpa = round(random.uniform(8.5, 9.9), 2)
            dsa_score = random.randint(80, 100)
            activity_days = random.randint(0, 2)
            applications_sent = random.randint(0, 3)
            interviews_cleared = random.randint(0, applications_sent)
            
        # Edge Case 2: Low CGPA, but highly active & grinding (about 5% of students)
        elif case_type < 0.10:
            cgpa = round(random.uniform(5.0, 6.5), 2)
            dsa_score = random.randint(60, 95)
            activity_days = random.randint(25, 30)
            applications_sent = random.randint(30, 50)
            # They get interviews because they apply a lot!
            interviews_cleared = random.randint(2, min(10, applications_sent))
            
        # Normal Case: Standard distribution (90% of students)
        else:
            cgpa = round(random.uniform(6.0, 9.0), 2)
            dsa_score = random.randint(30, 85)
            activity_days = random.randint(5, 25)
            applications_sent = random.randint(5, 35)
            interviews_cleared = random.randint(0, min(5, applications_sent))

        student = {
            "id": i,
            "name": name,
            "cgpa": cgpa,
            "dsa_score": dsa_score,
            "activity_days": activity_days,
            "applications_sent": applications_sent,
            "interviews_cleared": interviews_cleared,
            "domain": domain
        }
        
        students.append(student)

    return students

if __name__ == "__main__":
    # Test generation of 200 students
    generated_data = generate_students(200)
    
    print(f"✅ Generated {len(generated_data)} synthetic students.")
    print("Example Edge Case (High CGPA, Inactive) / Normal:")
    print(generated_data[0])
    
    # Just a small sanity check on distributions
    active_low_gpa = [s for s in generated_data if s['cgpa'] <= 6.5 and s['activity_days'] >= 25]
    inactive_high_gpa = [s for s in generated_data if s['cgpa'] >= 8.5 and s['activity_days'] <= 2]
    
    print(f"🧪 Edge Case 1 (High CGPA/Inactive) Count: {len(inactive_high_gpa)}")
    print(f"🧪 Edge Case 2 (Low CGPA/Highly Active) Count: {len(active_low_gpa)}")