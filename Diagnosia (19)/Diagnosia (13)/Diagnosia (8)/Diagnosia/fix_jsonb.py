from database import get_db
import json

def fix_jsonb_data():
    try:
        supabase = get_db()
        
        # Get all diagnoses that need fixing
        result = supabase.table('diagnoses').select('*').execute()
        
        for diagnosis in result.data:
            # Helper function to convert value to proper JSONB array
            def to_jsonb_array(value):
                if value is None or value == '[]':
                    return []
                if isinstance(value, str):
                    if value.startswith('[') and value.endswith(']'):
                        try:
                            return json.loads(value)
                        except:
                            return [value]
                    return [value]
                if isinstance(value, list):
                    return value
                return [str(value)]
            
            # Fix each field
            update_data = {
                'medications': to_jsonb_array(diagnosis.get('medications')),
                'diet': to_jsonb_array(diagnosis.get('diet')),
                'precautions': to_jsonb_array(diagnosis.get('precautions')),
                'symptoms': to_jsonb_array(diagnosis.get('symptoms'))
            }
            
            # Update the record
            supabase.table('diagnoses').update(update_data).eq('id', diagnosis['id']).execute()
            
        print("Successfully fixed JSONB data")
        
    except Exception as e:
        print(f"Error fixing JSONB data: {str(e)}")

if __name__ == '__main__':
    fix_jsonb_data() 