from database import get_db
import sys

def fix_doctor_assignments():
    try:
        supabase = get_db()
        
        # Get all diagnoses (we'll filter for null doctor_id in Python)
        all_diagnoses = supabase.table('diagnoses')\
            .select('id, disease, status, doctor_id')\
            .execute()
            
        # Filter for unassigned diagnoses
        unassigned = [d for d in all_diagnoses.data if d.get('doctor_id') is None]
            
        print(f"Found {len(unassigned)} diagnoses without doctors")
        
        if not unassigned:
            print("No unassigned diagnoses found.")
            return
            
        # Get available verified doctors
        doctors = supabase.table('profiles')\
            .select('id, name')\
            .eq('role', 'doctor')\
            .eq('is_verified', True)\
            .execute()
            
        if not doctors.data:
            print("No verified doctors found in the system.")
            return
            
        print(f"Found {len(doctors.data)} verified doctors")
            
        # Update each unassigned diagnosis with a doctor
        for diagnosis in unassigned:
            # Use the first available doctor (you might want to implement a more sophisticated assignment logic)
            doctor = doctors.data[0]
            
            # Update the diagnosis
            result = supabase.table('diagnoses')\
                .update({
                    'doctor_id': doctor['id'],
                    'status': 'pending_review',
                    'assigned_at': 'now()'
                })\
                .eq('id', diagnosis['id'])\
                .execute()
                
            if result.data:
                print(f"Assigned doctor {doctor['name']} to diagnosis {diagnosis['id']} ({diagnosis['disease']})")
            else:
                print(f"Failed to assign doctor to diagnosis {diagnosis['id']}")
                
        print("Doctor assignment process completed")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fix_doctor_assignments() 