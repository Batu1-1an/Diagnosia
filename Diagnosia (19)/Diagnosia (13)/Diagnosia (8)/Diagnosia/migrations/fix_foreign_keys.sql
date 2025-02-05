-- Drop existing constraints (both old and new names)
ALTER TABLE diagnoses DROP CONSTRAINT IF EXISTS fk_user_profile;
ALTER TABLE diagnoses DROP CONSTRAINT IF EXISTS fk_doctor_profile;
ALTER TABLE diagnoses DROP CONSTRAINT IF EXISTS diagnoses_user_id_fkey;
ALTER TABLE diagnoses DROP CONSTRAINT IF EXISTS diagnoses_doctor_id_fkey;

-- Add properly named foreign key constraints for Supabase
ALTER TABLE diagnoses
ADD CONSTRAINT diagnoses_user_id_fkey
FOREIGN KEY (user_id) REFERENCES profiles(id)
ON DELETE CASCADE;

ALTER TABLE diagnoses
ADD CONSTRAINT diagnoses_doctor_id_fkey
FOREIGN KEY (doctor_id) REFERENCES profiles(id)
ON DELETE SET NULL; 