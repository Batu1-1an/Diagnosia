-- Add foreign key relationships between diagnoses and profiles tables
ALTER TABLE diagnoses
ADD CONSTRAINT fk_user_profile
FOREIGN KEY (user_id) REFERENCES profiles(id);

ALTER TABLE diagnoses
ADD CONSTRAINT fk_doctor_profile
FOREIGN KEY (doctor_id) REFERENCES profiles(id);

-- Make sure the columns exist and are of the correct type
ALTER TABLE diagnoses
ALTER COLUMN user_id TYPE uuid USING user_id::uuid,
ALTER COLUMN doctor_id TYPE uuid USING doctor_id::uuid; 